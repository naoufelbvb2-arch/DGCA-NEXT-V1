from dataclasses import replace

import pytest
from neural_fixtures import assembly_fixture, context_fixture, fixture_graph, physical_key

from dgca_next.contracts import Region, SynapseScope
from dgca_next.dynamics.attractor import (
    AssemblyFixture,
    AttractorState,
    transition,
    validate_assembly,
)
from dgca_next.dynamics.context_gate import link_fingerprint, structural_diagnostic
from dgca_next.dynamics.homeostasis import adapt
from dgca_next.dynamics.numeric import SpecBlocked
from dgca_next.dynamics.session import FeatureEvent, cold_reset, read_only_episode
from dgca_next.dynamics.state import GraphSnapshot, Homeostasis
from dgca_next.graph import Synapse, SynapseState


def test_T25_fresh_zero_without_input_even_with_residual_and_attractor():
    _, _, graph, h, assembly = assembly_fixture()
    first, second = read_only_episode(
        graph,
        h,
        (FeatureEvent((("a", "1"),)), FeatureEvent(())),
        session_id=1,
        assemblies=(assembly,),
    )
    assert first.fresh is not None and second.fresh is not None
    assert first.state.attractors
    assert set(second.fresh.second.activity.values()) == {0.0}
    assert all(a > 0 for a in second.state.activity.values())
    assert not second.state.frontiers.step
    assert not cold_reset(second.state).attractors


def test_T26_previous_only_sigma_and_decay():
    _, _, graph, h, assembly = assembly_fixture()
    first, second = read_only_episode(
        graph,
        h,
        (FeatureEvent((("a", "1"),)), FeatureEvent(())),
        session_id=1,
        assemblies=(assembly,),
    )
    assert first.sigma == {}
    strength = first.state.attractors[0].strength
    assert second.sigma == {i: 0.9 * strength for i in assembly.members}
    assert second.state.attractors[0].strength == 0.9 * strength
    assert second.state.attractors[0].age == 1
    assert second.state.attractors[0].error == 0.0


def test_T26_error_and_collapse_precedence():
    _, _, graph, _, assembly = assembly_fixture()
    fresh = dict.fromkeys(assembly.members, 1.0)
    old = AttractorState(7, 0.7, 29, 1.5)
    assert (
        transition(
            old,
            graph=graph,
            assembly=assembly,
            fresh=fresh,
            boundary=True,
            comparable=((1.0, 0.0),),
        )[1]
        == "ATTRACTOR_BOUNDARY_COLLAPSE"
    )
    assert (
        transition(old, graph=graph, assembly=assembly, fresh=fresh, comparable=((1.0, 0.0),))[1]
        == "ATTRACTOR_AGE_COLLAPSE"
    )
    assert (
        transition(
            replace(old, age=0),
            graph=graph,
            assembly=assembly,
            fresh=fresh,
            comparable=((1.0, 0.0),),
        )[1]
        == "ATTRACTOR_ERROR_COLLAPSE"
    )
    unchanged, _ = transition(
        replace(old, age=0),
        graph=graph,
        assembly=assembly,
        fresh=dict.fromkeys(assembly.members, 0.8),
    )
    assert unchanged.error == 1.5
    assert unchanged.strength == pytest.approx(0.8)
    updated, _ = transition(
        AttractorState(7, 0.7, 0, 0.2),
        graph=graph,
        assembly=assembly,
        fresh=fresh,
        comparable=((0.5, 0.0), (0.8, 1.0), (0.24, 0.0)),
    )
    assert updated.error == 0.45  # Two eligible comparables; no error reset on fresh.


def test_T26_admission_thresholds_derived_from_physical_fresh_activity():
    _, _, graph, _, assembly = assembly_fixture()
    assert transition(
        None, graph=graph, assembly=assembly, fresh=dict.fromkeys(assembly.members, 0.399999)
    ) == (None, None)
    partial = dict(zip(assembly.members, (1.0, 1.0, 0.0), strict=True))
    assert transition(None, graph=graph, assembly=assembly, fresh=partial)[0] is None
    admitted, _ = transition(
        None, graph=graph, assembly=assembly, fresh=dict.fromkeys(assembly.members, 0.5)
    )
    assert admitted == AttractorState(7, 0.5, 0, 0.0)


def test_S02_real_fresh_cohesion_admission_with_read_only_input():
    _, _, graph, h, assembly = assembly_fixture()
    trace = read_only_episode(
        graph, h, (FeatureEvent((("a", "1"),)),), session_id=1, assemblies=(assembly,)
    )[0]
    assert trace.state.attractors and trace.state.attractors[0].strength >= 0.5


def test_assembly_requires_actual_reciprocity_and_membership():
    graph, builder, _, _ = fixture_graph(
        ((8192, 8200, SynapseScope.LOCAL), (8200, 8208, SynapseScope.LOCAL))
    )
    assembly = AssemblyFixture(7, (8192, 8200, 8208))
    with pytest.raises(ValueError, match="MEMBERSHIP"):
        validate_assembly(GraphSnapshot.capture(graph), assembly)
    for i in assembly.members:
        builder.set_memberships(i, frozenset({7}))
    with pytest.raises(ValueError, match="UNQUALIFIED"):
        validate_assembly(GraphSnapshot.capture(graph), assembly)


def test_assembly_rejects_incomplete_or_stale_context_even_with_valid_triangle():
    graph, builder, _, _, bindings = context_fixture()
    original = bindings[0]
    z = original.z
    members = (z, 8200, 8208)
    # A physically pinned 2/2/2 candidate; no owner discovery is simulated.
    for target in set((*original.predecessor, *original.current, *original.outcome)):
        existing = next((s for s in graph.latent_slots(z) if s.target_id == target), None)
        if existing is None:
            existing = next(s for s in graph.latent_slots(z) if s.index < 6 and s.target_id is None)
            builder.inject_slot(z, existing.index, target)
        builder.pin_slot(z, existing.index, z)
    for source in members:
        for target in members:
            if source == target:
                continue
            if not graph.structurally_eligible(source, target):
                slot = next(
                    s for s in graph.latent_slots(source) if s.index < 6 and s.target_id is None
                )
                builder.inject_slot(source, slot.index, target)
            key = physical_key(source, target, SynapseScope.LOCAL)
            builder.add_synapse(
                Synapse(key, 0, SynapseState.CONSOLIDATED, 1.0, 10.0, 0.0, 2, 2, True, True)
            )
        builder.set_memberships(source, frozenset({7}))
    frozen = GraphSnapshot.capture(graph)
    binding = replace(original, link_fingerprint=link_fingerprint(frozen, original.keys))
    candidate = replace(binding, complete=False)
    assert structural_diagnostic(candidate, frozen, {z: candidate}) is None
    assembly = AssemblyFixture(7, members)
    with pytest.raises(ValueError, match="UNQUALIFIED_CONTEXT_ASSEMBLY_MEMBER"):
        validate_assembly(frozen, assembly, {z: candidate})
    with pytest.raises(ValueError, match="UNQUALIFIED_CONTEXT_ASSEMBLY_MEMBER"):
        validate_assembly(frozen, assembly, {z: replace(binding, active=False)})
    validate_assembly(frozen, assembly, {z: binding})


def test_T27_pure_homeostasis_independent_golden():
    h = Homeostasis(
        {8192: 1.0, 8193: 0.7},
        {8192: 0.1, 8193: 1.0},
        {Region.LANGUAGE: 0.2},
        {Region.LANGUAGE: 0.1},
    )
    adapted = adapt(h, {8192: 0.8}, fixture_region_firing={Region.LANGUAGE: 1 / 4096})
    expected_rate = 0.95 * 0.1 + 0.05
    assert adapted.rates[8192] == expected_rate
    assert adapted.gains[8192] == 1.0 + 0.002 * (0.05 - expected_rate)
    assert adapted.rates[8193] == 0.95
    assert adapted.gains[8193] == 0.7
    assert adapted.region_rates[Region.LANGUAGE] == 0.95 * 0.1 + 0.05 * (1 / 4096)
    assert adapted.thresholds[Region.LANGUAGE] == 0.20500000000000002
    assert h.gains[8192] == 1.0 and h.thresholds[Region.LANGUAGE] == 0.2


def test_T27_no_activity_still_updates_ema_pure_only():
    h = Homeostasis({8192: 1.0}, {8192: 0.5}, {Region.LANGUAGE: 0.2}, {Region.LANGUAGE: 0.0})
    updated = adapt(h, {}, fixture_region_firing={Region.LANGUAGE: 0.0})
    assert updated.rates[8192] == 0.95 * 0.5
    assert updated.thresholds[Region.LANGUAGE] == 0.195


def test_SPEC_BLOCKED_S03_region_firing_denominator_is_unspecified():
    h = Homeostasis(
        {8192: 1.0, 8193: 1.0},
        {8192: 0.0, 8193: 0.0},
        {Region.LANGUAGE: 0.2},
        {Region.LANGUAGE: 0.03},
    )
    with pytest.raises(SpecBlocked, match="I2-S03"):
        adapt(h, {8192: 1.0})
    logical = adapt(h, {8192: 1.0}, fixture_region_firing={Region.LANGUAGE: 1 / 4096})
    committed = adapt(h, {8192: 1.0}, fixture_region_firing={Region.LANGUAGE: 1 / 2})
    assert logical.thresholds[Region.LANGUAGE] == 0.2
    assert committed.thresholds[Region.LANGUAGE] == 0.20500000000000002
