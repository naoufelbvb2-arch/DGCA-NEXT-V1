"""RC4.3 S02: computed fresh cohesion on legal synthetic graph fixtures."""

from dataclasses import replace

import pytest
from neural_fixtures import assembly_fixture, fixture_graph

from dgca_next.contracts import SynapseScope
from dgca_next.dynamics.attractor import AssemblyFixture, cohesion_from_graph_and_fresh, transition
from dgca_next.dynamics.session import FeatureEvent, read_only_episode
from dgca_next.dynamics.state import GraphSnapshot, Homeostasis
from dgca_next.graph import SynapseState


def test_equal_triangle_partial_reject_and_equal_half_admit():
    _, _, graph, _, assembly = assembly_fixture()
    partial = dict(zip(assembly.members, (1.0, 1.0, 0.0), strict=True))
    assert sum(partial.values()) / 3 == 2 / 3
    assert cohesion_from_graph_and_fresh(graph, assembly, partial) == 1 / 3
    result, reason = transition(None, graph=graph, assembly=assembly, fresh=partial)
    assert result is None and reason == "ATTRACTOR_INSUFFICIENT_COHESION"
    uniform = dict.fromkeys(assembly.members, 0.5)
    assert cohesion_from_graph_and_fresh(graph, assembly, uniform) == 0.5
    result, reason = transition(None, graph=graph, assembly=assembly, fresh=uniform)
    assert result is not None and result.strength == 0.5 and reason is None


def test_unequal_weights_sorted_pair_golden_quotient():
    members = (8192, 8200, 8208)
    weights = {(8192, 8200): 3.0, (8192, 8208): 5.0, (8200, 8208): 10.0}
    edges = tuple(
        (source, target, SynapseScope.LOCAL, 1.0, mass, 0.0, SynapseState.CONSOLIDATED)
        for (i, j), mass in weights.items()
        for source, target in ((i, j), (j, i))
    )
    graph, builder, _, _ = fixture_graph(edges)
    for member in members:
        builder.set_memberships(member, frozenset({7}))
    snapshot = GraphSnapshot.capture(graph)
    assembly = AssemblyFixture(7, members).bind(snapshot)
    fresh = dict(zip(members, (0.8, 0.4, 0.2), strict=True))
    expected = ((0.3 * 0.4 + 0.5 * 0.2) + 1.0 * 0.2) / ((0.3 + 0.5) + 1.0)
    assert cohesion_from_graph_and_fresh(snapshot, assembly, fresh) == expected
    assert len(graph.synapses()) == 6  # Three unordered pairs, not six directed weights.


@pytest.mark.parametrize("kind", ["candidate", "one_sided"])
def test_nonconsolidated_or_one_sided_pair_excluded(kind):
    members = (8192, 8200, 8208, 8216)
    edges = []
    for i in members:
        for j in members:
            if i == j or (kind == "one_sided" and (i, j) == (8200, 8192)):
                continue
            if kind == "candidate" and (i, j) == (8200, 8192):
                edges.append((i, j, SynapseScope.LOCAL, 0.6, 1.0, 0.0, SynapseState.CANDIDATE))
            else:
                edges.append((i, j, SynapseScope.LOCAL))
    graph, builder, _, _ = fixture_graph(tuple(edges))
    for member in members:
        builder.set_memberships(member, frozenset({7}))
    snapshot = GraphSnapshot.capture(graph)
    assembly = AssemblyFixture(7, members).bind(snapshot)
    fresh = dict(zip(members, (1.0, 1.0, 0.0, 0.0), strict=True))
    assert cohesion_from_graph_and_fresh(snapshot, assembly, fresh) == 0.0
    assert transition(None, graph=snapshot, assembly=assembly, fresh=fresh)[0] is None


def test_empty_fresh_is_zero_no_admission_and_no_current_sigma():
    _, _, graph, h, assembly = assembly_fixture()
    assert cohesion_from_graph_and_fresh(graph, assembly, {}) == 0.0
    assert transition(None, graph=graph, assembly=assembly, fresh={}) == (None, None)
    empty = read_only_episode(graph, h, (FeatureEvent(()),), session_id=4, assemblies=(assembly,))[
        0
    ]
    assert not empty.state.attractors and not empty.sigma
    active, later = read_only_episode(
        graph,
        h,
        (FeatureEvent((("a", "1"),)), FeatureEvent(())),
        session_id=4,
        assemblies=(assembly,),
    )
    assert not active.sigma and active.state.attractors
    assert later.sigma and not later.state.frontiers.step


def test_invalid_or_stale_generation_rejected_and_no_scalar_override():
    graph, builder, snapshot, h, assembly = assembly_fixture()
    fresh = dict.fromkeys(assembly.members, 0.5)
    with pytest.raises(ValueError, match="STALE_ASSEMBLY_FIXTURE"):
        cohesion_from_graph_and_fresh(snapshot, replace(assembly, generation=2), fresh)
    with pytest.raises(ValueError, match="UNVERIFIED_ASSEMBLY_GENERATION"):
        cohesion_from_graph_and_fresh(snapshot, AssemblyFixture(7, assembly.members), fresh)
    with pytest.raises(TypeError):
        read_only_episode(
            snapshot, h, (), session_id=1, assemblies=(assembly,), fixture_cohesion={7: 1.0}
        )
    builder.set_memberships(assembly.members[0], frozenset({7, 8}))
    updated = GraphSnapshot.capture(graph)
    with pytest.raises(ValueError, match="STALE_ASSEMBLY_FIXTURE"):
        cohesion_from_graph_and_fresh(updated, assembly, fresh)
    assert h == Homeostasis.uniform_language(snapshot.committed_ids)
