"""Real production RootStore EVENT tests; no fixture graph or witness injection."""

import json
import sqlite3
import subprocess
import sys
from contextlib import closing
from dataclasses import replace
from pathlib import Path

import pytest

from dgca_next.contracts import EventMode, EventOrigin
from dgca_next.dynamics.numeric import SpecBlocked
from dgca_next.dynamics.session import FeatureEvent, read_only_episode
from dgca_next.dynamics.state import GraphSnapshot
from dgca_next.graph import FixtureBuilder, SlotCategory
from dgca_next.learning.homeostasis_profile import LanguageHomeostasis
from dgca_next.persistence.graph_codec import decode_production_graph, encode_production_graph
from dgca_next.persistence.store import R_COLD, RootStore

ROOT = Path(__file__).resolve().parents[1]
REVISION = "a" * 40


def open_store(path):
    return RootStore(path, repository_root=ROOT, code_revision=REVISION)


def test_real_cold_event_restart_and_abort(tmp_path):
    path = tmp_path / "production.sqlite"
    store = open_store(path)
    before_h = store.h_bytes()
    assert before_h == LanguageHomeostasis.initial().encode()
    assert store.graph().stored_cell_count == 0 and store.graph().synapses() == ()
    store.begin(1)
    event = store.event(1, 0, (("a", "1"),))
    ids = (8606, 9345, 11795, 12181)
    assert event.born == ids and event.event_id == event.event_order == 0
    assert event.origin is EventOrigin.EXTERNAL_DIRECT and event.mode is EventMode.LEARN
    assert event.provenance.exposure_id == 1 and event.fixture_only is False
    assert event.boundary is True
    with pytest.raises(ValueError, match="UNVERIFIED_EVENT_CONSTRUCTION"):
        replace(event, born=())
    assert event.pre_committed == () and event.pass1 == event.final == ()
    assert event.X_fixed == tuple((i, 1_000_000) for i in ids)
    assert event.pass1_raw == tuple((i, 1.0) for i in ids)
    assert all(value == pytest.approx(1 / 1.1) for _, value in event.pass1_normalized)
    assert store.root(1).next_order == 1
    before_end = store.view()
    assert before_end.completed_closes == 0
    with pytest.raises(SpecBlocked, match="I3-R03"):
        store.end(1)
    assert store.view() == before_end
    graph = store.graph()
    assert tuple(c.cell_id for c in graph.stored_cells()) == ids
    assert all(c.committed and not c.fixture_only for c in graph.stored_cells())
    assert all(len(graph.latent_slots(i)) == 24 for i in ids)
    assert graph.synapses() == () and graph.validate_graph().stored_cells == 4
    assert all(graph.reverse_latent(i) for i in ids)
    saved_w, saved_r, saved_h = store.view().W, store.view().runtime, store.h_bytes()
    assert saved_h == before_h
    store.close()
    restored = open_store(path)
    assert restored.view().W == saved_w and restored.view().runtime == saved_r
    assert restored.h_bytes() == saved_h and restored.root(1).next_order == 1
    assert restored.observation(1, 0) == event
    assert encode_production_graph(restored.graph()) == saved_w
    assert encode_production_graph(decode_production_graph(saved_w)) == saved_w
    restored.abort(1)
    assert restored.h_bytes() == before_h and restored.view().runtime == R_COLD
    assert restored.view().W == saved_w
    effective = LanguageHomeostasis.decode(restored.h_bytes()).materialize(frozenset(ids))
    assert all(effective.gains[i] == 1.0 and effective.rates[i] == 0.05 for i in ids)
    restored.close()


def test_fixture_builder_rejects_production_graph(tmp_path):
    store = open_store(tmp_path / "production.sqlite")
    store.begin(1)
    store.event(1, 0, (("a", "1"),))
    graph = store.graph()
    with pytest.raises(ValueError, match="FIXTURE_EDITOR_REJECTS_PRODUCTION_GRAPH"):
        FixtureBuilder(graph).commit_cells([8192], committed_event=3)
    store.abort(1)
    store.close()


def test_oversubscribed_cohort_and_later_retry(tmp_path):
    store = open_store(tmp_path / "production.sqlite")
    features = tuple((f, "1") for f in ("a", "ab", "c", "d"))
    store.begin(1)
    event = store.event(1, 0, features)
    assert event.born == (8286, 8465, 8606, 8649, 8694, 9227, 9345, 9902, 9912, 10128, 10273, 10513)
    assert event.deferred == (11524, 11641, 11795, 12181)
    assert store.graph().stored_cell_count == 12
    store.abort(1)
    store.begin(2)
    second = store.event(2, 0, features)
    assert second.event_id == 1 and second.born == event.deferred and not second.deferred
    assert len(second.pre_committed) == 12 and store.graph().stored_cell_count == 16
    assert store.graph().synapses() == ()
    store.abort(2)
    store.close()


def test_reject_invalid_events_atomically(tmp_path):
    store = open_store(tmp_path / "production.sqlite")
    store.begin(1)
    before = store.view()
    with pytest.raises(ValueError):
        store.event(1, 0, (("a", "NaN"),))
    with pytest.raises(ValueError, match="EVENT_ORDER_MISMATCH"):
        store.event(1, 1, (("a", "1"),))
    assert store.view() == before and store.root(1).next_order == 0
    store.event(1, 0, (("a", "1"),))
    after = store.view()
    with pytest.raises(ValueError, match="EVENT_ORDER_MISMATCH"):
        store.event(1, 0, (("a", "1"),))
    assert store.view() == after
    with pytest.raises(ValueError, match="INVALID_FEATURE_EVENT"):
        store.event(1, 1, after)
    assert store.view() == after
    store.abort(1)
    with pytest.raises(ValueError, match="ROOT_ID_REUSED"):
        store.begin(1)
    store.close()


def test_second_event_adapts_committed_population_and_abort_restores_exact_h(tmp_path):
    path = tmp_path / "production.sqlite"
    store = open_store(path)
    initial_h = store.h_bytes()
    store.begin(1)
    first = store.event(1, 0, (("a", "1"),))
    assert store.h_bytes() == initial_h and not first.pre_committed
    second = store.event(1, 1, (("a", "1"),))
    assert second.pre_committed == first.born
    assert second.previous == ()
    assert second.born == () and second.deferred == ()
    assert second.emitters == first.born and second.frontier == first.born
    assert all(value == pytest.approx(0.8 / 1.1) for _, value in second.final)
    adapted = LanguageHomeostasis.decode(store.h_bytes()).overrides
    assert all(adapted.rates[i] == pytest.approx(0.0975) for i in first.born)
    assert all(adapted.gains[i] == pytest.approx(0.999905) for i in first.born)
    assert list(adapted.region_rates.values()) == pytest.approx([0.0785])
    assert store.h_bytes() != initial_h
    event2 = store.event(1, 2, (), boundary=True)
    assert event2.boundary and event2.previous == () and event2.temporal == ()
    assert all(value == 0.0 for _, value in event2.final)
    store.close()
    store = open_store(path)
    assert store.root(1).next_order == 3 and store.observation(1, 1) == second
    store.abort(1)
    assert store.h_bytes() == initial_h
    assert tuple(c.cell_id for c in store.graph().stored_cells()) == first.born
    store.abort(1)
    assert store.h_bytes() == initial_h
    store.close()


def test_births_use_frozen_learning_frontier_without_fabricating_step_frontier(tmp_path):
    store = open_store(tmp_path / "production.sqlite")
    store.begin(1)
    first = store.event(1, 0, (("a", "1"),))
    store.event(1, 1, (("a", "1"),))
    third = store.event(1, 2, (("distinct_feature", "1"),))
    assert third.learning_frontier == first.born
    assert third.frontier == ()
    assert third.born and set(third.born).isdisjoint(first.born)
    graph = store.graph()
    assert any(
        slot.category is SlotCategory.COACTIVE_INTRA and slot.target_id in first.born
        for owner in third.born
        for slot in graph.latent_slots(owner)
    )
    assert graph.synapses() == ()
    store.abort(1)
    store.close()


@pytest.mark.parametrize("stage", ["BEFORE_COMMIT", "AFTER_COMMIT"])
def test_adaptation_event_crash_keeps_whole_checkpoint(tmp_path, stage):
    path = tmp_path / "production.sqlite"
    store = open_store(path)
    store.begin(1)
    store.event(1, 0, (("a", "1"),))
    initial_h, initial_w, initial_r = store.h_bytes(), store.view().W, store.view().runtime
    store.close()
    script = """
import os, sys
from pathlib import Path
from dgca_next.persistence.store import RootStore
s = RootStore(Path(sys.argv[1]), repository_root=Path(sys.argv[2]), code_revision='a'*40)
def crash(stage):
    if stage == sys.argv[3]: os._exit(71)
s.event(1, 1, (('a','1'),), hook=crash)
"""
    result = subprocess.run(
        [sys.executable, "-c", script, str(path), str(ROOT), stage], check=False
    )
    assert result.returncode == 71
    store = open_store(path)
    assert store.view().W == initial_w
    if stage == "BEFORE_COMMIT":
        assert store.root(1).next_order == 1 and store.h_bytes() == initial_h
        assert store.view().runtime == initial_r and store.observation(1, 1) is None
    else:
        assert store.root(1).next_order == 2 and store.h_bytes() != initial_h
        assert store.view().runtime != initial_r and store.observation(1, 1).event_id == 1
    store.abort(1)
    assert store.h_bytes() == initial_h and store.view().W == initial_w
    store.close()


def test_event_journal_tampering_fails_without_replaying_event(tmp_path):
    path = tmp_path / "production.sqlite"
    store = open_store(path)
    store.begin(1)
    store.event(1, 0, (("a", "1"),))
    store.close()
    with closing(sqlite3.connect(path)) as connection:
        with connection:
            connection.execute("UPDATE p01_events SET checkpoint_hash=?", ("0" * 64,))
    with pytest.raises(ValueError, match="EVENT_CHECKPOINT_HASH_MISMATCH"):
        open_store(path)


def test_cold_read_only_after_abort_is_isolated(tmp_path):
    store = open_store(tmp_path / "production.sqlite")
    store.begin(1)
    store.event(1, 0, (("a", "1"),))
    with pytest.raises(ValueError, match="READ_ONLY_FORBIDDEN"):
        store.assert_read_only_allowed()
    store.abort(1)
    store.assert_read_only_allowed()
    graph = store.graph()
    frozen = GraphSnapshot.capture(graph)
    h = LanguageHomeostasis.decode(store.h_bytes()).materialize(frozen.committed_ids)
    before = store.view()
    traces = read_only_episode(frozen, h, (FeatureEvent((("a", "1"),)),), session_id=1)
    assert len(traces) == 1 and all(a > 0 for a in traces[0].passes.second.activity.values())
    assert store.view() == before and not graph.synapses()
    store.close()


def test_empty_event_advances_witness_without_birth(tmp_path):
    store = open_store(tmp_path / "production.sqlite")
    store.begin(1)
    before = store.view().W
    trace = store.event(1, 0, ())
    assert trace.born == trace.X_fixed == () and trace.boundary is True
    assert store.view().W == before and store.root(1).next_order == 1
    assert store.observation(1, 0) == trace
    store.abort(1)
    store.close()


def test_production_connections_share_open_lock(tmp_path):
    path = tmp_path / "production.sqlite"
    first, second = open_store(path), open_store(path)
    first.begin(1)
    with pytest.raises(ValueError, match="EXPOSURE_ALREADY_OPEN"):
        second.begin(2)
    event = first.event(1, 0, (("a", "1"),))
    assert second.observation(1, 0) == event and second.root(1).next_order == 1
    first.abort(1)
    second.begin(2)
    assert first.view().open_root == 2
    second.abort(2)
    first.close()
    second.close()


@pytest.mark.parametrize("operation", ["begin", "abort"])
@pytest.mark.parametrize("stage", ["BEFORE_COMMIT", "AFTER_COMMIT"])
def test_production_begin_abort_crash_recovery(tmp_path, operation, stage):
    path = tmp_path / "production.sqlite"
    store = open_store(path)
    initial_h = store.h_bytes()
    if operation == "abort":
        store.begin(1)
        store.event(1, 0, (("a", "1"),))
        store.event(1, 1, (("a", "1"),))
    store.close()
    script = """
import os, sys
from pathlib import Path
from dgca_next.persistence.store import RootStore
s=RootStore(Path(sys.argv[1]), repository_root=Path(sys.argv[2]), code_revision='a'*40)
def crash(stage):
    if stage == sys.argv[4]: os._exit(71)
getattr(s,sys.argv[3])(1, hook=crash)
"""
    result = subprocess.run(
        [sys.executable, "-c", script, str(path), str(ROOT), operation, stage], check=False
    )
    assert result.returncode == 71
    store = open_store(path)
    root = store.root(1)
    if operation == "begin" and stage == "BEFORE_COMMIT":
        assert root is None and store.view().open_root is None
    elif operation == "begin" or stage == "BEFORE_COMMIT":
        assert root.status == "OPEN" and store.view().open_root == 1
        if operation == "abort":
            assert store.h_bytes() != initial_h and store.root(1).next_order == 2
    else:
        assert root.status == "ABORTED" and store.view().open_root is None
        assert store.h_bytes() == initial_h
    if operation == "abort":
        assert store.graph().stored_cell_count == 4
    store.close()


@pytest.mark.parametrize("stage", ["BEFORE_COMMIT", "AFTER_COMMIT"])
def test_event_process_crash_atomicity(tmp_path, stage):
    path = tmp_path / "production.sqlite"
    store = open_store(path)
    store.begin(1)
    before_h = store.h_bytes()
    store.close()
    script = """
import os, sys
from pathlib import Path
from dgca_next.persistence.store import RootStore
s = RootStore(Path(sys.argv[1]), repository_root=Path(sys.argv[2]), code_revision='a'*40)
def crash(stage):
    if stage == sys.argv[3]: os._exit(71)
s.event(1, 0, (('a','1'),), hook=crash)
"""
    result = subprocess.run(
        [sys.executable, "-c", script, str(path), str(ROOT), stage], check=False
    )
    assert result.returncode == 71
    store = open_store(path)
    if stage == "BEFORE_COMMIT":
        assert store.root(1).next_order == 0 and store.graph().stored_cell_count == 0
        assert store.observation(1, 0) is None and store.view().runtime == R_COLD
    else:
        assert store.root(1).next_order == 1 and store.graph().stored_cell_count == 4
        assert store.observation(1, 0).born == (8606, 9345, 11795, 12181)
        assert store.graph().validate_graph().stored_cells == 4
        assert all(store.graph().reverse_latent(i) for i in store.observation(1, 0).born)
    recovered_w = store.view().W
    store.abort(1)
    assert store.h_bytes() == before_h and store.view().W == recovered_w
    store.close()


@pytest.mark.parametrize(
    "column", ["schema_version", "config_hash", "w_state", "h_state", "r_state"]
)
def test_corrupt_production_checkpoint_fails_closed(tmp_path, column):
    path = tmp_path / "production.sqlite"
    store = open_store(path)
    store.begin(1)
    store.event(1, 0, (("a", "1"),))
    store.close()
    with closing(sqlite3.connect(path)) as connection:
        with connection:
            connection.execute(f"UPDATE p01_metadata SET {column}=?", ("bad",))
    with pytest.raises(ValueError):
        open_store(path)


def test_reverse_index_tampering_fails_graph_decode(tmp_path):
    store = open_store(tmp_path / "production.sqlite")
    store.begin(1)
    store.event(1, 0, (("a", "1"),))
    encoded = store.view().W
    tag = b"DGCA-P01-W\x01\0"
    doc = json.loads(encoded[len(tag) :])
    doc["reverse"][0][1] = []
    damaged = tag + json.dumps(doc, sort_keys=True, separators=(",", ":")).encode("ascii")
    with pytest.raises(ValueError):
        decode_production_graph(damaged)
    store.abort(1)
    store.close()
