"""S01 physical link fixtures: neural propagation is not Assembly formation."""

import pytest
from neural_fixtures import fixture_graph, physical_key

from dgca_next.contracts import SynapseScope
from dgca_next.dynamics.drive import synchronous_drives, temporal_drives
from dgca_next.dynamics.state import GraphSnapshot
from dgca_next.graph import SynapseState


@pytest.mark.parametrize(
    "scope,target", [(SynapseScope.LOCAL, 8200), (SynapseScope.CROSS_TERRITORY, 0)]
)
@pytest.mark.parametrize(
    "state,S,E",
    [
        (SynapseState.CANDIDATE, 0.6, 1.0),
        (SynapseState.EPISODIC_INDEXED, 0.6, 1.0),
        (SynapseState.CONSOLIDATED, 0.6, 3.0),
    ],
)
def test_live_states_and_scopes_use_actual_quality(scope, target, state, S, E):
    graph, _, snapshot, _ = fixture_graph(
        ((8192, target, scope, S, E, 0.0, state),), cells=tuple(range(8192, 8202))
    )
    before = graph.debug_dump()
    drives = synchronous_drives(snapshot, {8192: 0.8}, frozenset({8192}))
    assert len(drives) == 1
    assert drives[0].value == 0.8 * (S * (E / 10.0))
    if state is not SynapseState.CONSOLIDATED:
        assert drives[0].value == 0.048
    assert graph.debug_dump() == before


def test_unmaterialized_reserved_key_and_missing_emitters_give_zero():
    graph, builder, snapshot, _ = fixture_graph(cells=(8192, 8200))
    builder.inject_slot(8192, 0, 8200)
    builder.reserve(physical_key(8192, 8200, SynapseScope.LOCAL), 8192)
    snapshot = GraphSnapshot.capture(graph)
    assert synchronous_drives(snapshot, {8192: 0.8}, frozenset({8192})) == ()
    graph2, _, snapshot2, _ = fixture_graph(((8192, 8200, SynapseScope.LOCAL),))
    assert synchronous_drives(snapshot2, {8192: 0.8}, frozenset()) == ()
    assert synchronous_drives(snapshot2, {8192: 0.8}, frozenset({8200})) == ()
    assert graph2.synapses()


def test_zero_quality_contributes_zero_and_assoc_remains_temporal_only():
    _, _, graph, _ = fixture_graph(
        (
            (8192, 8200, SynapseScope.LOCAL, 0.0, 1.0, 0.0, SynapseState.CANDIDATE),
            (8192, 8208, SynapseScope.ASSOCIATIVE, 1.0, 3.0, 0.0, SynapseState.CONSOLIDATED),
        )
    )
    assert synchronous_drives(graph, {8192: 0.8}, frozenset({8192})) == ()
    assert temporal_drives(graph, {8192: 0.8}, frozenset(), {}) == ()
    assert temporal_drives(graph, {8192: 0.8}, frozenset({8192}), {})[0].value == 0.24


def test_candidate_reciprocity_never_creates_qualified_assembly():
    from dgca_next.dynamics.attractor import AssemblyFixture, validate_assembly

    members = (8192, 8200, 8208)
    edges = tuple(
        (i, j, SynapseScope.LOCAL, 0.6, 1.0, 0.0, SynapseState.CANDIDATE)
        for i in members
        for j in members
        if i != j
    )
    network, builder, _, _ = fixture_graph(edges)
    for i in members:
        builder.set_memberships(i, frozenset({7}))
    snapshot = GraphSnapshot.capture(network)
    assert synchronous_drives(snapshot, {8192: 0.8}, frozenset({8192}))
    with pytest.raises(ValueError, match="UNQUALIFIED_ASSEMBLY_FIXTURE"):
        validate_assembly(snapshot, AssemblyFixture(7, members))
