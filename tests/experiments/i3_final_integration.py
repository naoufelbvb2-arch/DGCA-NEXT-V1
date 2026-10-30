"""One genuine production chain from cold sensory input to controlled rewiring."""

import hashlib
import json
import sqlite3
import subprocess
import sys
import time
import tracemalloc
from contextlib import closing
from pathlib import Path
from tempfile import TemporaryDirectory

from dgca_next.contracts import Region, SynapseScope
from dgca_next.dynamics.session import FeatureEvent, read_only_episode
from dgca_next.dynamics.state import GraphSnapshot
from dgca_next.graph.synapse import SynapseState, quality
from dgca_next.learning.homeostasis_profile import LanguageHomeostasis
from dgca_next.persistence.graph_codec import decode_production_graph
from dgca_next.persistence.store import RootStore

ROOT = Path(__file__).resolve().parents[2]
A = (("a", "1"),)


def _allocated_bytes(path):
    if sys.platform != "win32":
        return path.stat().st_blocks * 512
    import ctypes
    import msvcrt

    class FileStandardInfo(ctypes.Structure):
        _fields_ = [
            ("allocation", ctypes.c_longlong),
            ("end", ctypes.c_longlong),
            ("links", ctypes.c_uint32),
            ("delete_pending", ctypes.c_bool),
            ("directory", ctypes.c_bool),
        ]

    info = FileStandardInfo()
    with path.open("rb") as handle:
        fn = ctypes.windll.kernel32.GetFileInformationByHandleEx
        fn.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_void_p, ctypes.c_uint32]
        fn.restype = ctypes.c_int
        if not fn(
            msvcrt.get_osfhandle(handle.fileno()), 1, ctypes.byref(info), ctypes.sizeof(info)
        ):
            raise OSError("GetFileInformationByHandleEx failed")
    return info.allocation


def _peak_rss_bytes():
    if sys.platform != "win32":
        import resource

        value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        return value if sys.platform == "darwin" else value * 1024
    import ctypes

    class Counters(ctypes.Structure):
        _fields_ = [("cb", ctypes.c_uint32), ("faults", ctypes.c_uint32)] + [
            (name, ctypes.c_size_t)
            for name in ("peak", "current", "pq", "q", "npq", "nq", "pagefile", "peakfile")
        ]

    counters = Counters()
    counters.cb = ctypes.sizeof(counters)
    kernel = ctypes.windll.kernel32
    kernel.GetCurrentProcess.restype = ctypes.c_void_p
    fn = ctypes.windll.psapi.GetProcessMemoryInfo
    fn.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint32]
    fn.restype = ctypes.c_int
    if not fn(kernel.GetCurrentProcess(), ctypes.byref(counters), counters.cb):
        raise OSError("GetProcessMemoryInfo failed")
    return counters.peak


def digest(data):
    return hashlib.sha256(data).hexdigest()


def link_info(link):
    return {
        "source": link.key.source.cell_id,
        "target": link.key.target.cell_id,
        "scope": link.key.scope.value,
        "state": link.state.value,
        "S": link.S,
        "E_ext": link.E_ext,
        "count": link.external_root_count,
        "Q": quality(link),
        "roots": [credit.root_id for credit in link.credits],
        "q": link.credits[-1].q,
        "y": link.credits[-1].y,
        "source_event": link.credits[-1].source_event_id,
        "target_event": link.credits[-1].event_id,
    }


def run_chain(path, *, measure_memory=False):
    start = time.perf_counter()
    if measure_memory:
        tracemalloc.start()
    store = RootStore(path, repository_root=ROOT, code_revision="a" * 40)
    assert not store.graph().stored_cells() and not store.graph().synapses()
    birth_started = time.perf_counter()
    store.begin(1)
    birth = store.event(1, 0, A)
    assert not birth.pre_committed and not store.pending_proposals(1)
    assert not store.end(1).accepted
    initial_w = store.view().W
    assert not store.graph().synapses()
    initial_h = store.h_bytes()
    profile = LanguageHomeostasis.decode(initial_h)
    h0 = profile.materialize(frozenset(birth.born))
    assert all(len(store.graph().latent_slots(i)) == 24 for i in birth.born)
    metrics = {}

    def measure(label, last_append):
        nonlocal store
        view = store.view()
        store.close()
        began = time.perf_counter()
        store = RootStore(path, repository_root=ROOT, code_revision="a" * 40)
        reopen = time.perf_counter() - began
        assert store.view() == view
        with closing(sqlite3.connect(path)) as connection:
            snapshots = connection.execute("SELECT COUNT(*) FROM p01_events").fetchone()[0]
            pages = connection.execute("PRAGMA page_count").fetchone()[0]
            page_size = connection.execute("PRAGMA page_size").fetchone()[0]
        metrics[label] = {
            "completed_serial": view.completed_closes,
            "events": snapshots,
            "W_bytes": len(view.W),
            "db_file_bytes": path.stat().st_size,
            "db_allocated_bytes": _allocated_bytes(path),
            "sqlite_logical_bytes": pages * page_size,
            "reopen_full_audit_seconds": reopen,
            "last_root_append_seconds": last_append,
        }

    measure("1", time.perf_counter() - birth_started)
    first_close = None
    for root in (2, 3, 4):
        store.begin(root)
        source = store.event(root, 0, A)
        if root == 4:
            assert store.verified_local_novelty(4, 0, birth.born[0]).pre_input_prediction == 0
        store.event(root, 1, A)
        if root == 3:
            novelty = store.verified_local_novelty(3, 1, birth.born[0])
            assert novelty.pre_input_prediction > 0
            empty = store.event(3, 2, ())
            assert dict(empty.temporal).get(birth.born[0], 0) > 0
            try:
                store.verified_local_novelty(3, 2, birth.born[0])
            except ValueError as exc:
                assert "NO_DIRECT_INPUT" in str(exc)
            else:
                raise AssertionError("prediction-only novelty was authorized")
        pending = store.pending_proposals(root)
        closed = store.end(root)
        if root == 2:
            first_close = closed
            assert {p.key.scope for p in closed.accepted} == {
                SynapseScope.LOCAL,
                SynapseScope.ASSOCIATIVE,
            }
            assert source.frontier and source.emitters and pending
            for proposal in closed.accepted:
                candidates = [item for item in pending if item.key == proposal.key]
                assert proposal == min(
                    candidates,
                    key=lambda item: (-item.credit.q, item.credit.event_order, item.credit.ordinal),
                )
        if root == 3:
            assert novelty.status == "PROVISIONAL"
            assert store.verified_local_novelty(3, 1, birth.born[0]).status == "COMPLETED"
    assert first_close is not None
    graph = store.graph()
    local = next(s for s in graph.synapses() if s.key.scope is SynapseScope.LOCAL)
    assoc = next(s for s in graph.synapses() if s.key.scope is SynapseScope.ASSOCIATIVE)
    assert local.state is SynapseState.CONSOLIDATED and local.E_ext >= 3 and local.S >= 0.6
    assert local.external_root_count >= 2 and assoc.external_root_count >= 2
    learned_w, learned_h = store.view().W, store.h_bytes()
    store.close()
    store = RootStore(path, repository_root=ROOT, code_revision="a" * 40)
    assert store.view().W == learned_w and store.h_bytes() == learned_h
    actual = GraphSnapshot.capture(store.graph())
    baseline = GraphSnapshot.capture(decode_production_graph(initial_w))
    assert actual.committed_ids == baseline.committed_ids
    h = LanguageHomeostasis.decode(learned_h).materialize(actual.committed_ids)
    probe = (FeatureEvent(A), FeatureEvent(A))
    before_read = store.view()
    trained = read_only_episode(actual, h, probe, session_id=1)
    zero = read_only_episode(baseline, h, probe, session_id=2)
    assert trained[0].synchronous and not zero[0].synchronous
    assert trained[1].temporal and not zero[1].temporal and store.view() == before_read

    store.begin(5)
    abort_h = store.h_bytes()
    store.event(5, 0, A)
    assert store.pending_proposals(5)
    second_birth = store.event(5, 1, (("ab", "1"),))
    before_abort_links = store.graph().synapses()
    store.abort(5)
    assert store.h_bytes() == abort_h and store.graph().synapses() == before_abort_links
    assert store.view().completed_closes == 4 and second_birth.born
    try:
        store.verified_local_novelty(5, 0, birth.born[0])
    except ValueError as exc:
        assert "ABORTED_ROOT" in str(exc)
    else:
        raise AssertionError("aborted novelty was authorized")
    owner, target = second_birth.born[:2]
    slot = next(s.index for s in store.graph().latent_slots(owner) if s.target_id == target)
    assert store.graph().latent_slots(owner)[slot].assigned_at_completed_close_serial == 4
    assert not any(
        {s.key.source.cell_id, s.key.target.cell_id} == {owner, target}
        for s in store.graph().synapses()
    )
    controls = (("ab", "0.2"), ("ac", "1"))
    for root in range(6, 105):
        began = time.perf_counter()
        store.begin(root)
        event = store.event(root, 0, controls if root == 104 else (("a", "0.000001"),))
        if root == 104:
            store.request_recycling(root, 0, owner, slot)
        store.end(root)
        elapsed = time.perf_counter() - began
        if store.view().completed_closes in (10, 100):
            measure(str(store.view().completed_closes), elapsed)
    assert store.view().completed_closes == 103
    assert store.recycling_request(104)[-1] == "CONFIRMATION_WINDOW_NOT_ELAPSED"
    store.begin(105)
    event = store.event(105, 0, controls)
    n = store.verified_local_novelty(105, 0, owner)
    store.request_recycling(105, 0, owner, slot)
    before_end = store.view()
    before_snapshot = GraphSnapshot.capture(store.graph())
    old_pair = tuple(store.graph().latent_slots(owner))
    preserved = (store.graph().synapse(local.key), store.graph().synapse(assoc.key))
    store.close()
    script = """
import os, sys
from pathlib import Path
from dgca_next.persistence.store import RootStore
s = RootStore(Path(sys.argv[1]), repository_root=Path(sys.argv[2]), code_revision='a'*40)
def crash(stage):
    if stage == sys.argv[3]: os._exit(31)
s.end(105, hook=crash)
"""
    for phase in ("BEFORE_COMMIT", "AFTER_COMMIT"):
        process = subprocess.run([sys.executable, "-c", script, str(path), str(ROOT), phase])
        assert process.returncode == 31
        store = RootStore(path, repository_root=ROOT, code_revision="a" * 40)
        if phase == "BEFORE_COMMIT":
            assert store.view() == before_end and store.recycling_request(105)[-1] is None
        else:
            assert store.recycling_request(105)[-1] == "RECYCLED"
        store.close()
    store = RootStore(path, repository_root=ROOT, code_revision="a" * 40)
    assert store.view().completed_closes == 104
    close = store.end(105)
    assert store.end(105) == close and store.view().completed_closes == 104
    rewired = store.graph()
    record = rewired.recycling_log()[-1]
    assert record.exposure_id == 105 and record.event_id == event.event_id
    assert rewired.synapse(local.key) == preserved[0] and rewired.synapse(assoc.key) == preserved[1]
    for source_id, index, old, new in record.changes:
        assert (source_id, index) not in rewired.reverse_latent(old)
        assert (source_id, index) in rewired.reverse_latent(new)
        assert rewired.latent_slots(source_id)[index].assigned_at_completed_close_serial == 104
    assert old_pair[slot].target_id == target
    final_view, final_h = store.view(), store.h_bytes()
    read_h = LanguageHomeostasis.decode(final_h).materialize(before_snapshot.committed_ids)
    prior_read = read_only_episode(before_snapshot, read_h, probe, session_id=11)
    after_read = read_only_episode(GraphSnapshot.capture(rewired), read_h, probe, session_id=12)
    for prior_trace, after_trace in zip(prior_read, after_read, strict=True):
        assert all(
            prior_trace.passes.second.activity[i] == after_trace.passes.second.activity[i]
            for i in birth.born
        )
    assert store.view() == final_view
    assert not rewired.automatic_recycling_enabled
    result = {
        "birth": birth.born,
        "deferred": birth.deferred,
        "birth_event": birth.event_id,
        "pre_committed": birth.pre_committed,
        "h0_gain": h0.gains[birth.born[0]],
        "h0_threshold": h0.thresholds[Region.LANGUAGE],
        "source_F_step": source.frontier,
        "source_emitters": source.emitters,
        "local": link_info(local),
        "associative": link_info(assoc),
        "novelty_root3": {
            "event": novelty.event_id,
            "X_fixed": novelty.x_fixed,
            "P_T": novelty.pre_input_prediction,
            "nu": novelty.novelty,
        },
        "baseline_PS": dict(zero[0].synchronous),
        "trained_PS": dict(trained[0].synchronous),
        "baseline_PT": dict(zero[1].temporal),
        "trained_PT": dict(trained[1].temporal),
        "birth_aborted_root": 5,
        "birth_aborted": second_birth.born,
        "recycle_root": 105,
        "recycle_event": event.event_id,
        "serial": 104,
        "age": 100,
        "novelty_X_fixed": n.x_fixed,
        "novelty_PT": n.pre_input_prediction,
        "novelty_q6": n.novelty_q6,
        "changes": record.changes,
        "W_before": digest(before_end.W),
        "W_after": digest(final_view.W),
        "H_after": digest(final_h),
        "metrics": metrics,
        "seconds": time.perf_counter() - start,
    }
    store.close()
    store = RootStore(path, repository_root=ROOT, code_revision="a" * 40)
    assert store.view() == final_view and store.h_bytes() == final_h
    assert store.graph().recycling_log()[-1] == record
    store.close()
    if measure_memory:
        _, result["peak_tracemalloc_bytes"] = tracemalloc.get_traced_memory()
        tracemalloc.stop()
    result["peak_rss_bytes"] = _peak_rss_bytes()
    return result


def main():
    with TemporaryDirectory() as directory:
        print(
            json.dumps(
                run_chain(Path(directory) / "chain.sqlite", measure_memory=True),
                indent=2,
                sort_keys=True,
                default=str,
            )
        )


if __name__ == "__main__":
    main()
