"""Run 100 genuine completed RootStore exposures and inspect actual slots."""

import hashlib
import json
import time
import tracemalloc
from pathlib import Path
from tempfile import TemporaryDirectory

from dgca_next.dynamics.session import FeatureEvent, read_only_episode
from dgca_next.dynamics.state import GraphSnapshot
from dgca_next.learning.homeostasis_profile import LanguageHomeostasis
from dgca_next.persistence.store import RootStore

ROOT = Path(__file__).resolve().parents[2]


def _sha(data):
    return hashlib.sha256(data).hexdigest()


def run_age_trial(path, *, measure_memory=True):
    started = time.perf_counter()
    if measure_memory:
        tracemalloc.start()
    engine = RootStore(path, repository_root=ROOT, code_revision="a" * 40)
    engine.begin(1)
    birth = engine.event(1, 0, (("a", "1"),))
    first = engine.end(1)
    assert engine.end(1) == first and engine.view().completed_closes == 1
    owner, target = birth.born[:2]
    slot = next(s.index for s in engine.graph().latent_slots(owner) if s.target_id == target)

    engine.begin(2)
    engine.event(2, 0, (("a", "0.000001"),))
    engine.event(2, 1, (("a", "0.000001"),))
    assert engine.view().completed_closes == 1
    engine.abort(2)
    assert engine.view().completed_closes == 1
    frozen = GraphSnapshot.capture(engine.graph())
    h = LanguageHomeostasis.decode(engine.h_bytes()).materialize(frozen.committed_ids)
    before = engine.view()
    read_only_episode(frozen, h, (FeatureEvent((("a", "0.000001"),)),), session_id=3)
    assert engine.view() == before and engine.view().completed_closes == 1

    for root_id in range(3, 100):
        engine.begin(root_id)
        engine.event(root_id, 0, (("a", "0.000001"),))
        engine.end(root_id)
    assert engine.view().completed_closes == 98
    before_w = len(engine.view().W)
    features = (("a", "0.2"), ("ab", "1"))
    engine.begin(100)
    event99 = engine.event(100, 0, features)
    engine.end(100)
    before99, h99 = engine.view(), engine.h_bytes()
    novelty99 = engine.verified_local_novelty(100, 0, owner)
    decision99 = engine.inspect_recycling(100, 0, owner, owner, slot)
    assert engine.view() == before99 and engine.h_bytes() == h99

    engine.begin(101)
    event100 = engine.event(101, 0, features)
    engine.end(101)
    before100, h100 = engine.view(), engine.h_bytes()
    graph100 = engine.graph()
    novelty100 = engine.verified_local_novelty(101, 0, owner)
    decision100 = engine.inspect_recycling(101, 0, owner, owner, slot)
    assert engine.view() == before100 and engine.h_bytes() == h100
    assert engine.graph().synapses() == graph100.synapses()
    assert engine.graph().structural_hash == graph100.structural_hash
    assert not engine.graph().automatic_recycling_enabled

    result = {
        "owner": owner,
        "target": target,
        "slot": slot,
        "root99": 100,
        "event99": event99.event_id,
        "serial99": before99.completed_closes,
        "reason99": decision99.reason,
        "ages99": [x.age for x in decision99.occurrences],
        "root100": 101,
        "event100": event100.event_id,
        "serial100": before100.completed_closes,
        "reason100": decision100.reason,
        "ages100": [x.age for x in decision100.occurrences],
        "assigned_serials": [x.assigned_serial for x in decision100.occurrences],
        "replacements": decision100.replacements,
        "x_fixed": novelty100.x_fixed,
        "P_T": novelty100.pre_input_prediction,
        "novelty": novelty100.novelty,
        "novelty_q6": novelty100.novelty_q6,
        "novelty99": novelty99.novelty,
        "W_sha256": _sha(before100.W),
        "H_sha256": _sha(h100),
        "W_bytes_at_98": before_w,
        "W_bytes_at_100": len(before100.W),
        "database_bytes": path.stat().st_size,
        "synapse_count": len(graph100.synapses()),
        "abort_and_read_only_serial": 1,
    }
    engine.close()
    engine = RootStore(path, repository_root=ROOT, code_revision="a" * 40)
    assert engine.view().completed_closes == 100
    assert engine.verified_local_novelty(101, 0, owner) == novelty100
    assert engine.inspect_recycling(101, 0, owner, owner, slot) == decision100
    assert engine.view().W == before100.W and engine.h_bytes() == h100
    engine.begin(102)
    engine.event(102, 0, (("a", "0.2"),))
    before_provisional = engine.view()
    provisional = engine.verified_local_novelty(102, 0, owner)
    provisional_decision = engine.inspect_recycling(102, 0, owner, owner, slot)
    assert provisional.status == "PROVISIONAL"
    assert provisional_decision.reason == "UNVERIFIED_NOVELTY"
    assert engine.view() == before_provisional and before_provisional.completed_closes == 100
    engine.end(102)
    before_no_candidate = engine.view()
    no_candidate = engine.inspect_recycling(102, 0, owner, owner, slot)
    assert engine.view() == before_no_candidate
    engine.begin(103)
    engine.event(103, 0, (("a", "1"),))
    engine.end(103)
    before_protected, protected_h = engine.view(), engine.h_bytes()
    protected_links = engine.graph().synapses()
    protected = engine.inspect_recycling(103, 0, owner, owner, slot)
    assert engine.view() == before_protected and engine.h_bytes() == protected_h
    assert engine.graph().synapses() == protected_links
    result["provisional_reason"] = provisional_decision.reason
    result["no_candidate_reason"] = no_candidate.reason
    result["protected_reason"] = protected.reason
    result["protected_ages"] = [item.age for item in protected.occurrences]
    result["protected_live_keys"] = protected.live_keys
    result["final_serial"] = before_protected.completed_closes
    result["database_bytes_final"] = path.stat().st_size
    engine.close()
    result["seconds"] = time.perf_counter() - started
    if measure_memory:
        _, result["peak_python_bytes"] = tracemalloc.get_traced_memory()
        tracemalloc.stop()
    return result


def main():
    with TemporaryDirectory() as directory:
        print(json.dumps(run_age_trial(Path(directory) / "age.sqlite"), sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
