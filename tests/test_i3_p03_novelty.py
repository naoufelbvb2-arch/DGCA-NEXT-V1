"""Actual production-journal novelty; numerical fixtures confer no authority."""

import sqlite3
from contextlib import closing
from dataclasses import replace
from pathlib import Path

import pytest

from dgca_next.graph.policy import q6
from dgca_next.learning.novelty import local_residual_novelty
from dgca_next.persistence.store import RootStore

ROOT = Path(__file__).resolve().parents[1]


def store(path):
    return RootStore(path, repository_root=ROOT, code_revision="a" * 40)


def _dynamic_slot(graph, owner, target):
    return next(s.index for s in graph.latent_slots(owner) if s.target_id == target)


def test_novelty_numerics_are_pure_and_not_authority():
    assert local_residual_novelty(0, 0.5) == 0.0
    assert local_residual_novelty(600_000, 0.5) == pytest.approx(1 / 6)
    assert local_residual_novelty(600_000, 0.1) == pytest.approx(5 / 6)
    assert q6(local_residual_novelty(600_000, 0.5)) < q6(0.3)
    assert q6(local_residual_novelty(600_000, 0.1)) > q6(0.3)
    with pytest.raises(ValueError):
        local_residual_novelty(600_000, float("nan"))


def test_provisional_completed_and_aborted_witnesses(tmp_path):
    engine = store(tmp_path / "novelty.sqlite")
    engine.begin(1)
    birth = engine.event(1, 0, (("a", "1"),))
    owner = birth.born[0]
    with pytest.raises(ValueError, match="NEWBORN_RECEIVER"):
        engine.verified_local_novelty(1, 0, owner)
    engine.end(1)
    with pytest.raises(ValueError, match="NEWBORN_RECEIVER"):
        engine.verified_local_novelty(1, 0, owner)
    engine.begin(2)
    event = engine.event(2, 0, (("a", "1"),))
    before = engine.view()
    provisional = engine.verified_local_novelty(2, 0, owner)
    assert provisional.status == "PROVISIONAL" and provisional.close_serial is None
    assert provisional.event_id == event.event_id and provisional.novelty == 1.0
    assert provisional.x_fixed == 1_000_000 and provisional.pre_input_prediction == 0.0
    with pytest.raises(ValueError, match="UNVERIFIED_NOVELTY_CONSTRUCTION"):
        replace(provisional, novelty=0.0)
    assert engine.view() == before
    engine.abort(2)
    with pytest.raises(ValueError, match="ABORTED_ROOT"):
        engine.verified_local_novelty(2, 0, owner)
    engine.begin(3)
    engine.event(3, 0, (("a", "1"),))
    close = engine.end(3)
    witness = engine.verified_local_novelty(3, 0, owner)
    assert witness.status == "COMPLETED" and witness.close_serial == close.close_serial == 2
    assert witness.novelty == 1.0 and witness.novelty_q6 == 1_000_000
    assert engine.end(3) == close and engine.view().completed_closes == 2
    with pytest.raises(ValueError, match="UNKNOWN_EVENT"):
        engine.verified_local_novelty(3, 1, owner)
    with pytest.raises(ValueError, match="UNKNOWN_ROOT"):
        engine.verified_local_novelty(999, 0, owner)
    engine.close()


def test_real_temporal_lane_from_prior_frontier_and_historical_pre_w(tmp_path):
    path = tmp_path / "trained.sqlite"
    engine = store(path)
    engine.begin(1)
    birth = engine.event(1, 0, (("a", "1"),))
    engine.end(1)
    owner = birth.born[0]
    engine.begin(2)
    engine.event(2, 0, (("a", "1"),))
    engine.event(2, 1, (("a", "1"),))
    engine.end(2)
    assert engine.graph().synapses()
    engine.begin(3)
    cold = engine.event(3, 0, (("a", "1"),))
    predicted = engine.event(3, 1, (("a", "1"),))
    assert not cold.temporal and dict(predicted.temporal)[owner] > 0
    provisional = engine.verified_local_novelty(3, 1, owner)
    assert provisional.pre_input_prediction == dict(predicted.temporal)[owner]
    assert provisional.novelty == pytest.approx(1 - provisional.pre_input_prediction)
    assert provisional.status == "PROVISIONAL"
    prediction_only = engine.event(3, 2, ())
    assert dict(prediction_only.temporal)[owner] > 0
    with pytest.raises(ValueError, match="NO_DIRECT_INPUT"):
        engine.verified_local_novelty(3, 2, owner)
    engine.end(3)
    before = engine.view()
    completed = engine.verified_local_novelty(3, 1, owner)
    assert completed.status == "COMPLETED" and completed.pre_w_hash == predicted.pre_w_hash
    assert completed.pre_input_prediction == dict(predicted.temporal)[owner]
    assert engine.verified_local_novelty(3, 0, owner).pre_input_prediction == 0.0
    assert engine.view() == before
    engine.close()
    engine = store(path)
    assert engine.verified_local_novelty(3, 1, owner) == completed
    engine.begin(4)
    blank = engine.event(4, 0, ())
    assert not blank.temporal
    with pytest.raises(ValueError, match="NO_DIRECT_INPUT"):
        engine.verified_local_novelty(4, 0, owner)
    engine.abort(4)
    engine.close()


def test_real_learned_pair_is_protected_and_inspection_is_read_only(tmp_path):
    engine = store(tmp_path / "protected.sqlite")
    engine.begin(1)
    born = engine.event(1, 0, (("a", "1"),)).born
    engine.end(1)
    engine.begin(2)
    engine.event(2, 0, (("a", "1"),))
    engine.event(2, 1, (("a", "1"),))
    engine.end(2)
    graph = engine.graph()
    owner, target = born[:2]
    slot = _dynamic_slot(graph, owner, target)
    before, h = engine.view(), engine.h_bytes()
    links = graph.synapses()
    decision = engine.inspect_recycling(2, 1, owner, owner, slot)
    assert not decision.allowed and decision.reason == "RECYCLE_BLOCKED_LIVE_OR_PROTECTED"
    assert decision.live_keys and len(decision.occurrences) == 2
    assert engine.view() == before and engine.h_bytes() == h and engine.graph().synapses() == links
    fixed = engine.inspect_recycling(2, 1, owner, owner, 6)
    assert fixed.reason == "RECYCLE_BLOCKED_FIXED"
    assert engine.view() == before and not engine.graph().automatic_recycling_enabled
    engine.close()


def test_validation_cache_detects_external_journal_tampering(tmp_path):
    path = tmp_path / "tamper.sqlite"
    engine = store(path)
    engine.begin(1)
    engine.event(1, 0, (("a", "1"),))
    engine.end(1)
    assert engine.view().completed_closes == 1
    with closing(sqlite3.connect(path)) as connection:
        with connection:
            connection.execute("UPDATE p01_events SET checkpoint_hash=?", ("0" * 64,))
    with pytest.raises(ValueError, match="EVENT_CHECKPOINT_HASH_MISMATCH"):
        engine.view()
    engine.close()
