"""Genuine external roots and one controlled atomic physical replacement."""

import copy
import hashlib
import json
import subprocess
import sys
import time
import tracemalloc
from pathlib import Path
from tempfile import TemporaryDirectory

from dgca_next.dynamics.session import FeatureEvent, read_only_episode
from dgca_next.dynamics.state import GraphSnapshot
from dgca_next.learning.homeostasis_profile import LanguageHomeostasis
from dgca_next.learning.settlement import _settle
from dgca_next.persistence.binary_records import decode_record, encode_record
from dgca_next.persistence.graph_codec import decode_production_graph
from dgca_next.persistence.store import RootStore

ROOT = Path(__file__).resolve().parents[2]


def run_trial(path, *, measure_memory=False):
    start = time.perf_counter()
    if measure_memory:
        tracemalloc.start()
    store = RootStore(path, repository_root=ROOT, code_revision="a" * 40)
    store.begin(1)
    birth = store.event(1, 0, (("a", "1"),))
    store.end(1)
    owner, target = birth.born[:2]
    index = next(s.index for s in store.graph().latent_slots(owner) if s.target_id == target)
    store.begin(2)
    store.event(2, 0, (("a", "0.000001"),))
    store.abort(2)
    assert store.view().completed_closes == 1
    frozen = GraphSnapshot.capture(store.graph())
    h = LanguageHomeostasis.decode(store.h_bytes()).materialize(frozen.committed_ids)
    before_read_only = store.view()
    read_only_episode(frozen, h, (FeatureEvent((("a", "0.000001"),)),), session_id=3)
    assert store.view() == before_read_only and store.view().completed_closes == 1
    for root in range(3, 100):
        store.begin(root)
        store.event(root, 0, (("a", "0.000001"),))
        store.end(root)
    assert store.view().completed_closes == 98
    features = (("a", "0.2"), ("ab", "1"))
    store.begin(100)
    store.event(100, 0, features)
    store.event(100, 1, features)
    store.request_recycling(100, 1, owner, index)
    store.end(100)
    refusal99 = store.recycling_request(100)
    assert refusal99[-1] == "CONFIRMATION_WINDOW_NOT_ELAPSED"
    before = store.view()
    before_graph = store.graph()
    assert before_graph.synapses()
    old_slots = [(owner, index, target)]
    old_slots.extend(
        (target, s.index, owner) for s in before_graph.latent_slots(target) if s.target_id == owner
    )
    store.begin(101)
    event = store.event(101, 0, features)
    store.request_recycling(101, 0, owner, index)
    provisional = store.verified_local_novelty(101, 0, owner)
    w_before_end = store.view().W
    post_evidence, _ = _settle(
        store.graph(), 101, 100, store.pending_proposals(101), event_clock=101
    )

    store.close()
    crash_script = """
import os, sys
from pathlib import Path
from dgca_next.persistence.store import RootStore
s = RootStore(Path(sys.argv[1]), repository_root=Path(sys.argv[2]), code_revision='a' * 40)
def crash(stage):
    if stage == sys.argv[3]:
        os._exit(31)
s.end(101, hook=crash)
"""
    crashed = subprocess.run(
        [sys.executable, "-c", crash_script, str(path), str(ROOT), "BEFORE_COMMIT"],
        check=False,
    )
    assert crashed.returncode == 31
    store = RootStore(path, repository_root=ROOT, code_revision="a" * 40)
    assert store.view().W == w_before_end and store.recycling_request(101)[-1] is None
    store.close()
    crashed = subprocess.run(
        [sys.executable, "-c", crash_script, str(path), str(ROOT), "AFTER_COMMIT"],
        check=False,
    )
    assert crashed.returncode == 31
    store = RootStore(path, repository_root=ROOT, code_revision="a" * 40)
    request = store.recycling_request(101)
    assert request[-1] == "RECYCLED"
    after = store.view()
    graph = store.graph()
    record = graph.recycling_log()[-1]
    assert store.end(101).close_serial == 100
    assert store.view() == after
    for source, slot_index, old, new in record.changes:
        assert graph.latent_slots(source)[slot_index].target_id == new
        assert (source, slot_index) not in graph.reverse_latent(old)
        assert (source, slot_index) in graph.reverse_latent(new)
        assert graph.latent_slots(source)[slot_index].assigned_at_completed_close_serial == 100
    assert [(s, i, old) for s, i, old, _ in record.changes] == old_slots
    assert graph.synapses() == post_evidence.synapses()
    assert all(graph.synapse(link.key) is not None for link in before_graph.synapses())
    after_snapshot = GraphSnapshot.capture(graph)
    post_snapshot = GraphSnapshot.capture(post_evidence)
    h = LanguageHomeostasis.decode(store.h_bytes()).materialize(after_snapshot.committed_ids)
    probe = (FeatureEvent((("ab", "1"),)),)
    post_trace = read_only_episode(post_snapshot, h, probe, session_id=200)[0]
    after_trace = read_only_episode(after_snapshot, h, probe, session_id=200)[0]
    assert post_trace.synchronous == after_trace.synchronous
    assert post_trace.passes.second.activity == after_trace.passes.second.activity
    assert any(value > 0 for value in after_trace.synchronous.values())
    assert store.view() == after
    document = decode_record(after.W, 0x57, 3)
    for corruption in ("reverse", "old_target"):
        damaged = copy.deepcopy(document)
        if corruption == "reverse":
            damaged["reverse"][0][1].pop()
        else:
            damaged["recycling"][0][4][0][2] = 0
        try:
            decode_production_graph(encode_record(0x57, 3, damaged))
        except ValueError:
            pass
        else:
            raise AssertionError(f"undetected {corruption} corruption")
    result = {
        "owner": owner,
        "target": target,
        "slot": index,
        "root": 101,
        "event_id": event.event_id,
        "X_fixed": provisional.x_fixed,
        "P_T": provisional.pre_input_prediction,
        "novelty": provisional.novelty,
        "novelty_q6": provisional.novelty_q6,
        "serial": 100,
        "old_occurrences": old_slots,
        "changes": record.changes,
        "W_before": hashlib.sha256(w_before_end).hexdigest(),
        "W_after": hashlib.sha256(after.W).hexdigest(),
        "H_after": hashlib.sha256(store.h_bytes()).hexdigest(),
        "disposition99": refusal99[-1],
        "database_bytes": path.stat().st_size,
        "pre_trial_serial": before.completed_closes,
        "read_only_nonzero_synchronous": max(after_trace.synchronous.values()),
    }
    store.close()
    store = RootStore(path, repository_root=ROOT, code_revision="a" * 40)
    assert store.view() == after and store.graph().recycling_log()[-1] == record
    assert store.recycling_request(101) == request
    store.begin(102)
    store.event(102, 0, (("a", "0.000001"),))
    store.request_recycling(102, 0, owner, index)
    store.end(102)
    # The replacement pair already has live links, which take precedence over
    # its new age of one completed root.
    assert store.recycling_request(102)[-1] == "RECYCLE_BLOCKED_LIVE_OR_PROTECTED"
    assert store.graph().latent_slots(owner)[index].assigned_at_completed_close_serial == 100
    another = birth.born[2]
    another_index = next(
        s.index for s in store.graph().latent_slots(owner) if s.target_id == another
    )
    store.begin(103)
    store.event(103, 0, (("a", "0.2"),))
    store.request_recycling(103, 0, owner, another_index)
    before_no_candidate = store.graph().latent_slots(owner)
    store.end(103)
    assert store.recycling_request(103)[-1] == "NO_RECYCLING_REPLACEMENT"
    assert store.graph().latent_slots(owner) == before_no_candidate
    store.begin(104)
    store.event(104, 0, (("a", "1"),))
    before_evidence = store.graph()
    assert not any(
        {link.key.source.cell_id, link.key.target.cell_id} == {owner, another}
        for link in before_evidence.synapses()
    )
    store.request_recycling(104, 0, owner, another_index)
    store.end(104)
    assert store.recycling_request(104)[-1] == "RECYCLE_BLOCKED_LIVE_OR_PROTECTED"
    assert any(
        {link.key.source.cell_id, link.key.target.cell_id} == {owner, another}
        for link in store.graph().synapses()
    )
    result["same_end_disposition"] = store.recycling_request(104)[-1]
    result["no_candidate_disposition"] = store.recycling_request(103)[-1]
    store.close()
    result["seconds"] = time.perf_counter() - start
    if measure_memory:
        _, result["peak_python_bytes"] = tracemalloc.get_traced_memory()
        tracemalloc.stop()
    return result


def main():
    with TemporaryDirectory() as directory:
        print(
            json.dumps(
                run_trial(Path(directory) / "rewire.sqlite", measure_memory=True),
                indent=2,
                sort_keys=True,
            )
        )


if __name__ == "__main__":
    main()
