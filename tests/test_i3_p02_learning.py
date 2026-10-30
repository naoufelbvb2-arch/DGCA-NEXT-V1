"""Actual RootStore learning: no fixture graph, injected synapse or oracle."""

import sqlite3
import subprocess
import sys
from contextlib import closing
from pathlib import Path

import pytest

from dgca_next.contracts import SynapseScope
from dgca_next.dynamics.session import FeatureEvent, read_only_episode
from dgca_next.dynamics.state import GraphSnapshot
from dgca_next.graph.synapse import SynapseState, quality
from dgca_next.learning.homeostasis_profile import LanguageHomeostasis
from dgca_next.persistence.graph_codec import decode_production_graph
from dgca_next.persistence.store import RootStore

ROOT = Path(__file__).resolve().parents[1]


def store(path):
    return RootStore(path, repository_root=ROOT, code_revision="a" * 40)


def test_cold_real_root_learning_persistence_and_causal_effect(tmp_path):
    path = tmp_path / "learn.sqlite"
    engine = store(path)
    assert engine.graph().synapses() == ()
    engine.begin(1)
    birth = engine.event(1, 0, (("a", "1"),))
    assert birth.born == (8606, 9345, 11795, 12181)
    assert not engine.pending_proposals(1)
    assert not engine.end(1).accepted
    zero_link_w = engine.view().W
    assert engine.view().completed_closes == 1 and not engine.graph().synapses()

    engine.begin(2)
    source = engine.event(2, 0, (("a", "1"),))
    target = engine.event(2, 1, (("a", "1"),))
    assert engine.graph().synapses() == ()
    pending = engine.pending_proposals(2)
    assert {p.key.scope for p in pending} == {SynapseScope.LOCAL, SynapseScope.ASSOCIATIVE}
    close = engine.end(2)
    assert close.close_serial == 2 and {p.key.scope for p in close.accepted} == {
        SynapseScope.LOCAL,
        SynapseScope.ASSOCIATIVE,
    }
    graph = engine.graph()
    assert graph.synapses() and all(not synapse.fixture_only for synapse in graph.synapses())
    assert all(s.external_root_count == 1 and s.credits[0].root_id == 2 for s in graph.synapses())
    assert any(
        p.credit.source_event_id == source.event_id and p.credit.event_id == target.event_id
        for p in close.accepted
        if p.key.scope is SynapseScope.ASSOCIATIVE
    )
    for accepted in close.accepted:
        candidates = [p for p in pending if p.key == accepted.key]
        winner = min(
            candidates, key=lambda p: (-p.credit.q, p.credit.event_order, p.credit.ordinal)
        )
        assert accepted == winner
        assert graph.synapse(accepted.key).credits == (winner.credit,)
    before_retry = engine.view()
    assert engine.end(2) == close and engine.view() == before_retry
    first_links = {s.key: s for s in graph.synapses()}

    engine.begin(3)
    engine.event(3, 0, (("a", "1"),))
    engine.event(3, 1, (("a", "1"),))
    engine.end(3)
    graph = engine.graph()
    reinforced = {s.key: s for s in graph.synapses()}
    assert all(reinforced[k].external_root_count == 2 for k in first_links)
    assert all(reinforced[k].E_ext > first_links[k].E_ext for k in first_links)
    assert all(tuple(c.root_id for c in reinforced[k].credits) == (2, 3) for k in first_links)
    learned_w, learned_h = engine.view().W, engine.h_bytes()
    engine.close()
    engine = store(path)
    assert engine.view().W == learned_w and engine.h_bytes() == learned_h
    assert engine.graph().synapses() == graph.synapses()
    assert engine.view().completed_closes == 3

    actual = GraphSnapshot.capture(engine.graph())
    zero = GraphSnapshot.capture(decode_production_graph(zero_link_w))
    homeostasis = LanguageHomeostasis.decode(learned_h).materialize(actual.committed_ids)
    inputs = (FeatureEvent((("a", "1"),)), FeatureEvent((("a", "1"),)))
    before = engine.view()
    trained = read_only_episode(actual, homeostasis, inputs, session_id=3)
    comparator = read_only_episode(zero, homeostasis, inputs, session_id=4)
    assert any(s.key.scope is SynapseScope.LOCAL for s in graph.synapses())
    assert all(quality(s) > 0 for s in graph.synapses())
    assert trained[0].synchronous and not comparator[0].synchronous
    assert trained[1].temporal and not comparator[1].temporal
    assert engine.view() == before

    engine.begin(4)
    engine.event(4, 0, (("a", "1"),))
    engine.event(4, 1, (("a", "1"),))
    engine.end(4)
    consolidated_graph = engine.graph()
    local = [s for s in consolidated_graph.synapses() if s.key.scope is SynapseScope.LOCAL]
    associative = [
        s for s in consolidated_graph.synapses() if s.key.scope is SynapseScope.ASSOCIATIVE
    ]
    assert local and all(s.E_ext >= 3.0 and s.state is SynapseState.CONSOLIDATED for s in local)
    assert associative and all(
        s.E_ext < 3.0 and s.state is SynapseState.CANDIDATE for s in associative
    )
    completed_h = engine.h_bytes()
    engine.begin(5)
    later = engine.event(5, 0, (("ab", "1"),))
    assert later.born and engine.graph().synapses() == consolidated_graph.synapses()
    for cell_id in later.born:
        assert engine.graph().initialization(cell_id).assignment.completed_close_serial == 4
    engine.abort(5)
    assert (
        engine.h_bytes() == completed_h
        and engine.graph().synapses() == consolidated_graph.synapses()
    )
    assert engine.view().completed_closes == 4
    engine.close()


@pytest.mark.parametrize("stage", ["BEFORE_COMMIT", "AFTER_COMMIT"])
def test_end_process_crash_recovers_whole_close_without_double_credit(tmp_path, stage):
    path = tmp_path / "crash.sqlite"
    engine = store(path)
    engine.begin(1)
    engine.event(1, 0, (("a", "1"),))
    engine.end(1)
    engine.begin(2)
    engine.event(2, 0, (("a", "1"),))
    engine.event(2, 1, (("a", "1"),))
    before = engine.view()
    proposals = engine.pending_proposals(2)
    assert proposals and not engine.graph().synapses()
    engine.close()
    script = """
import os, sys
from pathlib import Path
from dgca_next.persistence.store import RootStore
s=RootStore(Path(sys.argv[1]), repository_root=Path(sys.argv[2]), code_revision='a'*40)
def crash(stage):
    if stage == sys.argv[3]: os._exit(71)
s.end(2, hook=crash)
"""
    process = subprocess.run(
        [sys.executable, "-c", script, str(path), str(ROOT), stage], check=False
    )
    assert process.returncode == 71
    engine = store(path)
    if stage == "BEFORE_COMMIT":
        assert engine.view() == before and engine.root(2).status == "OPEN"
        assert engine.pending_proposals(2) == proposals and not engine.graph().synapses()
        result = engine.end(2)
    else:
        assert engine.root(2).status == "COMPLETED" and engine.view().completed_closes == 2
        result = engine.end(2)
    after = engine.view()
    assert result.close_serial == 2 and result.accepted
    assert all(s.external_root_count == 1 for s in engine.graph().synapses())
    assert engine.end(2) == result and engine.view() == after
    engine.close()


@pytest.mark.parametrize("stage", ["BEFORE_COMMIT", "AFTER_COMMIT"])
def test_event_crash_with_previously_learned_links_is_atomic(tmp_path, stage):
    path = tmp_path / "event-crash.sqlite"
    engine = store(path)
    engine.begin(1)
    engine.event(1, 0, (("a", "1"),))
    engine.end(1)
    engine.begin(2)
    engine.event(2, 0, (("a", "1"),))
    engine.event(2, 1, (("a", "1"),))
    engine.end(2)
    existing_links = engine.graph().synapses()
    engine.begin(3)
    before, begin_h = engine.view(), engine.h_bytes()
    engine.close()
    script = """
import os, sys
from pathlib import Path
from dgca_next.persistence.store import RootStore
s=RootStore(Path(sys.argv[1]), repository_root=Path(sys.argv[2]), code_revision='a'*40)
def crash(stage):
    if stage == sys.argv[3]: os._exit(71)
s.event(3, 0, (('ab','1'),), hook=crash)
"""
    process = subprocess.run(
        [sys.executable, "-c", script, str(path), str(ROOT), stage], check=False
    )
    assert process.returncode == 71
    engine = store(path)
    assert engine.graph().synapses() == existing_links
    if stage == "BEFORE_COMMIT":
        assert engine.view() == before and engine.observation(3, 0) is None
    else:
        assert engine.root(3).next_order == 1 and engine.observation(3, 0).born
    engine.abort(3)
    assert engine.h_bytes() == begin_h and engine.graph().synapses() == existing_links
    assert engine.view().completed_closes == 2
    engine.close()


def test_p01_production_schema_is_explicitly_rejected(tmp_path):
    path = tmp_path / "old-p01.sqlite"
    with closing(sqlite3.connect(path)) as connection:
        with connection:
            connection.execute("CREATE TABLE p01_metadata (id INTEGER, schema_version INTEGER)")
            connection.execute("INSERT INTO p01_metadata VALUES (1,2)")
            connection.execute("CREATE TABLE p01_roots (id INTEGER)")
            connection.execute("CREATE TABLE p01_events (id INTEGER)")
    with pytest.raises(ValueError, match="UNSUPPORTED_PRODUCTION_SCHEMA"):
        store(path)
