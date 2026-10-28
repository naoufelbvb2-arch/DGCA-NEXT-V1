from dataclasses import FrozenInstanceError, replace

import pytest

from dgca_next.contracts import SynapseScope
from dgca_next.graph import FixtureBuilder, SparseNetwork, SynapseState, quality


@pytest.mark.parametrize("scope,same_region", [(s, r) for s in SynapseScope for r in (True, False)])
def test_i1_t10_scope_delta_and_direction(scope, same_region, key_factory, record_factory):
    target = 8193 if same_region else 0
    legal = scope is SynapseScope.ASSOCIATIVE or same_region == (scope is SynapseScope.LOCAL)
    if not legal:
        with pytest.raises(ValueError):
            key_factory(8192, target, scope)
        return
    graph = SparseNetwork()
    builder = FixtureBuilder(graph)
    builder.commit_cells([8192, target], committed_event=0)
    builder.inject_slot(8192, 0 if same_region else 12, target)
    key = key_factory(8192, target, scope)
    link = record_factory(key)
    builder.add_synapse(link)
    reverse = key_factory(target, 8192, scope)
    assert graph.synapse(reverse) is None
    builder.add_synapse(record_factory(reverse))
    assert len(graph.synapses()) == 2
    for delta in (-1, 1 - link.delta, 2, 5, True):
        with pytest.raises(ValueError):
            record_factory(key, delta=delta)


def test_i1_t11_exact_duplicate_noop_conflicting_duplicate_reject(graph_pair, record_factory):
    graph, builder = graph_pair
    record = record_factory()
    builder.add_synapse(record)
    before = graph.structural_hash
    builder.add_synapse(record)
    assert graph.structural_hash == before
    with pytest.raises(ValueError, match="CONFLICTING_DUPLICATE_SYNAPSE"):
        builder.add_synapse(replace(record, S=0.7))
    assert graph.structural_hash == before
    with pytest.raises(FrozenInstanceError):
        graph.synapses()[0].S = 0.9


def test_i1_t11_self_link(key_factory):
    with pytest.raises(ValueError, match="self-links"):
        key_factory(8192, 8192)


@pytest.mark.parametrize("committed", [False, True])
def test_i1_t12_uncommitted_or_missing_latent(committed, record_factory):
    graph = SparseNetwork()
    builder = FixtureBuilder(graph)
    if committed:
        builder.commit_cells([8192, 8193], committed_event=0)
    before = graph.structural_hash
    with pytest.raises(
        ValueError, match="MISSING_LATENT_ELIGIBILITY" if committed else "UNCOMMITTED_ENDPOINT"
    ):
        builder.add_synapse(record_factory())
    assert graph.structural_hash == before


@pytest.mark.parametrize(
    "S,ext,internal,expected", [(0.8, 3.0, 0.0, 0.24), (0.8, 1.0, 2.0, 0.18), (0.8, 2.0, 2.0, 0.32)]
)
def test_i1_t19_fixture_quality(S, ext, internal, expected, graph_pair, record_factory):
    graph, builder = graph_pair
    link = record_factory(S=S, E_ext=ext, E_int=internal)
    builder.add_synapse(link)
    assert quality(link) == pytest.approx(expected, rel=0, abs=1e-15)
    assert graph.quality(link.key) == quality(link)
    assert quality(None) == 0.0


@pytest.mark.parametrize(
    "field,bad",
    [
        (field, value)
        for field in ("S", "E_ext", "E_int")
        for value in (float("nan"), float("inf"), -float("inf"), -0.1, True, 1, "0.5")
    ]
    + [
        ("S", 1.1),
        ("E_ext", 11.0),
        ("E_ext", 0.0),
        ("E_int", 5.1),
        ("external_root_count", 0),
        ("external_root_count", True),
        ("created_event", -1),
        ("fixture_only", False),
        ("fixture_only", 1),
        ("state", "CANDIDATE"),
    ],
)
def test_i1_t20_invalid_numeric_state(field, bad, record_factory):
    with pytest.raises(ValueError):
        record_factory(**{field: bad})


def test_total_mass_and_consolidation_bounds(record_factory):
    with pytest.raises(ValueError):
        record_factory(E_ext=9.0, E_int=2.0)
    for changes in ({"S": 0.59}, {"E_ext": 2.99}, {"external_root_count": 1}):
        args = dict(state=SynapseState.CONSOLIDATED, S=0.8, E_ext=3.0, external_root_count=2)
        args.update(changes)
        with pytest.raises(ValueError, match="INVALID_CONSOLIDATED_RECORD"):
            record_factory(**args)


def test_protected_consolidated_link_cannot_be_removed(graph_pair, record_factory):
    graph, builder = graph_pair
    link = record_factory(state=SynapseState.CONSOLIDATED, S=0.8, E_ext=3.0, external_root_count=2)
    builder.add_synapse(link)
    before = graph.structural_hash
    with pytest.raises(ValueError, match="PROTECTED_SYNAPSE"):
        builder.remove_synapse(link.key)
    assert graph.structural_hash == before


def test_commitment_timing_is_checked(graph_pair, record_factory):
    graph, builder = graph_pair
    before = graph.structural_hash
    with pytest.raises(ValueError, match="COMMITMENT_TIMING"):
        builder.add_synapse(record_factory(created_event=0))
    assert graph.structural_hash == before


def test_absent_link_quality_is_zero(graph_pair, key_factory):
    graph, _ = graph_pair
    assert graph.quality(key_factory()) == 0.0


def test_pinned_link_cannot_be_removed(graph_pair, record_factory):
    graph, builder = graph_pair
    link = record_factory()
    builder.add_synapse(link)
    builder.pin_slot(8192, 0, 8192)
    before = graph.structural_hash
    with pytest.raises(ValueError, match="PINNED_SYNAPSE"):
        builder.remove_synapse(link.key)
    assert graph.structural_hash == before
