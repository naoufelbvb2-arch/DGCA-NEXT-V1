"""Production EVENT witness staging; OPEN/ABORT cannot publish evidence."""

from pathlib import Path

import pytest

from dgca_next.contracts import SynapseScope
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
