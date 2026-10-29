"""Production EVENT witness staging; OPEN/ABORT cannot publish evidence."""

from dataclasses import asdict, replace
from pathlib import Path
from types import MappingProxyType

import pytest

from dgca_next.contracts import SynapseScope
from dgca_next.graph import FixtureBuilder, SparseNetwork
from dgca_next.graph.synapse import ProductionCredit, _production_credit
from dgca_next.learning.settlement import _select_root_max, _settle
from dgca_next.persistence.graph_codec import encode_production_graph
from dgca_next.persistence.store import RootStore

ROOT = Path(__file__).resolve().parents[1]


def open_store(path):
    return RootStore(path, repository_root=ROOT, code_revision="a" * 40)


def test_real_observations_stage_local_and_prior_step_without_live_synapses(tmp_path):
    path = tmp_path / "learn.sqlite"
    store = open_store(path)
    store.begin(1)
    birth = store.event(1, 0, (("a", "1"),))
    assert not store.pending_proposals(1)
    second = store.event(1, 1, (("a", "1"),))
    local = store.pending_proposals(1)
    assert local and all(p.key.scope is SynapseScope.LOCAL for p in local)
    assert all(
        p.credit.event_id == second.event_id and p.credit.source_event_id == second.event_id
        for p in local
    )
    assert all(
        p.key.source.cell_id in second.emitters and p.key.target.cell_id in second.pre_committed
        for p in local
    )
    third = store.event(1, 2, (("a", "1"),))
    staged = store.pending_proposals(1)
    associative = [p for p in staged if p.key.scope is SynapseScope.ASSOCIATIVE]
    assert associative and all(p.credit.source_event_id == second.event_id for p in associative)
    assert all(p.credit.event_id == third.event_id for p in associative)
    assert all(
        p.credit.source_activity == dict(second.final)[p.key.source.cell_id] for p in associative
    )
    assert all(
        p.key.source.cell_id in birth.born and p.key.target.cell_id in birth.born for p in staged
    )
    assert store.graph().synapses() == () and store.view().completed_closes == 0
    store.close()
    store = open_store(path)
    assert store.pending_proposals(1) == staged
    assert store.graph().synapses() == ()
    store.abort(1)
    with pytest.raises(ValueError, match="EXPOSURE_NOT_OPEN"):
        store.pending_proposals(1)
    assert store.graph().synapses() == () and store.view().completed_closes == 0
    store.close()


def test_empty_or_boundary_event_does_not_mint_temporal_witness(tmp_path):
    store = open_store(tmp_path / "learn.sqlite")
    store.begin(1)
    store.event(1, 0, (("a", "1"),))
    store.event(1, 1, (("a", "1"),))
    blank = store.event(1, 2, ())
    assert not any(p.credit.event_id == blank.event_id for p in store.pending_proposals(1))
    bounded = store.event(1, 3, (("a", "1"),), boundary=True)
    assert not any(
        p.credit.event_id == bounded.event_id and p.key.scope is SynapseScope.ASSOCIATIVE
        for p in store.pending_proposals(1)
    )
    store.abort(1)
    store.close()


def test_full_binary64_near_tie_keeps_the_larger_q_and_its_paired_y(tmp_path):
    """Synthetic numbers exercise the comparator only, never publication."""
    engine = open_store(tmp_path / "root.sqlite")
    engine.begin(1)
    engine.event(1, 0, (("a", "1"),))
    engine.event(1, 1, (("a", "1"),))
    genuine = engine.pending_proposals(1)[0]
    values = asdict(genuine.credit)
    with pytest.raises(ValueError, match="UNVERIFIED_PRODUCTION_CREDIT"):
        ProductionCredit(**values)
    earlier = replace(
        genuine, credit=_production_credit(**(values | {"q": 0.5, "y": 0.8, "ordinal": 0}))
    )
    later = replace(
        genuine, credit=_production_credit(**(values | {"q": 0.5000001, "y": 0.7, "ordinal": 1}))
    )
    assert _select_root_max((earlier, later), 1)[genuine.key] == later
    assert _select_root_max((earlier, later), 1)[genuine.key].credit.y == 0.7
    with pytest.raises(TypeError):
        engine.end(1, proposals=(later,))
    assert engine.graph().synapses() == ()
    engine.abort(1)
    engine.close()


def test_close_refuses_a_physically_stale_pair_in_an_isolated_shadow(tmp_path):
    """Synthetic deletion exercises a refusal; it is never published to RootStore."""
    engine = open_store(tmp_path / "stale.sqlite")
    engine.begin(1)
    engine.event(1, 0, (("a", "1"),))
    engine.event(1, 1, (("a", "1"),))
    proposal = engine.pending_proposals(1)[0]
    graph = engine.graph()
    base = graph._state
    slots, reverse, wiring = dict(base.slots), dict(base.reverse), list(base.wiring_log)
    source, target = proposal.key.source.cell_id, proposal.key.target.cell_id
    for owner, other in ((source, target), (target, source)):
        layout = list(slots[owner])
        for slot in layout:
            if slot.target_id != other:
                continue
            assert slot.recyclable_category
            layout[slot.index] = replace(slot, target_id=None, assignment=None)
            remaining = reverse[other] - {(owner, slot.index)}
            if remaining:
                reverse[other] = remaining
            else:
                del reverse[other]
            wiring.append((owner, slot.index, other, -1))
        slots[owner] = tuple(layout)
    isolated = SparseNetwork()
    isolated._state = replace(
        base,
        slots=MappingProxyType(slots),
        reverse=MappingProxyType(reverse),
        wiring_log=tuple(wiring),
    )
    isolated.validate_graph()
    assert not isolated.structurally_eligible(source, target)
    after, close = _settle(isolated, 1, 1, (proposal,), event_clock=2)
    assert not close.accepted and close.refused[0].reason == "STALE_LATENT_ELIGIBILITY"
    assert after.synapses() == () and engine.graph().synapses() == ()
    engine.abort(1)
    engine.close()


def test_fixture_writer_cannot_publish_a_real_production_synapse(tmp_path):
    engine = open_store(tmp_path / "separation.sqlite")
    engine.begin(1)
    engine.event(1, 0, (("a", "1"),))
    engine.event(1, 1, (("a", "1"),))
    engine.end(1)
    link = engine.graph().synapses()[0]
    fixture = SparseNetwork()
    builder = FixtureBuilder(fixture)
    builder.commit_cells((link.key.source.cell_id, link.key.target.cell_id), committed_event=0)
    with pytest.raises(ValueError, match="FIXTURE_EDITOR_REJECTS_PRODUCTION_SYNAPSE"):
        builder.add_synapse(link)
    with pytest.raises(ValueError):
        encode_production_graph(fixture)
    assert fixture.synapses() == ()
    engine.close()


def test_empty_root_cannot_fabricate_a_completed_external_observation(tmp_path):
    engine = open_store(tmp_path / "empty.sqlite")
    engine.begin(1)
    before = engine.view()
    with pytest.raises(ValueError, match="EMPTY_EXTERNAL_EXPOSURE"):
        engine.end(1)
    assert engine.view() == before and engine.view().completed_closes == 0
    engine.abort(1)
    engine.close()


def test_completed_event_clock_ignores_aborted_events_and_guards_expired_candidates(tmp_path):
    engine = open_store(tmp_path / "clock.sqlite")
    engine.begin(1)
    engine.event(1, 0, (("a", "1"),))
    engine.event(1, 1, ())
    engine.event(1, 2, ())
    engine.abort(1)
    engine.begin(2)
    actual = engine.event(2, 0, (("a", "1"),))
    close = engine.end(2)
    assert actual.event_id == 3 and close.event_clock == 1
    graph = engine.graph()
    assert graph.synapses() and all(s.candidate_deadline == 101 for s in graph.synapses())
    engine.begin(3)
    engine.event(3, 0, (("a", "1"),))
    proposals = engine.pending_proposals(3)
    assert proposals
    # Synthetic future clock is used only to exercise the refusal, never to publish evidence.
    shadow, simulated = _settle(graph, 3, 2, proposals, event_clock=102)
    assert not simulated.accepted
    assert all(r.reason == "CANDIDATE_CONFIRMATION_EXPIRED" for r in simulated.refused)
    assert shadow.synapses() == graph.synapses()
    engine.abort(3)
    engine.close()
