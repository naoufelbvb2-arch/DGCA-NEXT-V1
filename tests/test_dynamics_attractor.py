from dataclasses import replace

import pytest
from neural_fixtures import assembly_fixture, fixture_graph

from dgca_next.contracts import Region, SynapseScope
from dgca_next.dynamics.attractor import (
    AssemblyFixture,
    AttractorState,
    transition,
    validate_assembly,
)
from dgca_next.dynamics.homeostasis import adapt
from dgca_next.dynamics.numeric import SpecBlocked
from dgca_next.dynamics.session import FeatureEvent, cold_reset, read_only_episode
from dgca_next.dynamics.state import GraphSnapshot, Homeostasis


def test_T25_fresh_zero_without_input_even_with_residual_and_attractor():
    _, _, graph, h, assembly = assembly_fixture()
    first, second = read_only_episode(
        graph,
        h,
        (FeatureEvent((("a", "1"),)), FeatureEvent(())),
        session_id=1,
        assemblies=(assembly,),
        fixture_cohesion={7: 0.8},
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
        fixture_cohesion={7: 0.8},
    )
    assert first.sigma == {}
    strength = first.state.attractors[0].strength
    assert second.sigma == {i: 0.9 * strength for i in assembly.members}
    assert second.state.attractors[0].strength == 0.9 * strength
    assert second.state.attractors[0].age == 1
    assert second.state.attractors[0].error == 0.0


def test_T26_error_and_collapse_precedence():
    old = AttractorState(7, 0.7, 29, 1.5)
    assert (
        transition(old, assembly_id=7, fresh_mean=1.0, boundary=True, comparable=((1.0, 0.0),))[1]
        == "ATTRACTOR_BOUNDARY_COLLAPSE"
    )
    assert (
        transition(old, assembly_id=7, fresh_mean=1.0, comparable=((1.0, 0.0),))[1]
        == "ATTRACTOR_AGE_COLLAPSE"
    )
    assert (
        transition(replace(old, age=0), assembly_id=7, fresh_mean=1.0, comparable=((1.0, 0.0),))[1]
        == "ATTRACTOR_ERROR_COLLAPSE"
    )
    unchanged, _ = transition(replace(old, age=0), assembly_id=7, fresh_mean=0.8)
    assert unchanged.error == 1.5
    assert unchanged.strength == 0.8
    updated, _ = transition(
        AttractorState(7, 0.7, 0, 0.2),
        assembly_id=7,
        fresh_mean=1.0,
        comparable=((0.5, 0.0), (0.8, 1.0), (0.24, 0.0)),
    )
    assert updated.error == 0.45  # Two eligible comparables; no error reset on fresh.


def test_T26_admission_thresholds_explicit_synthetic_cohesion():
    assert transition(None, assembly_id=7, fresh_mean=0.399999) == (None, None)
    assert transition(None, assembly_id=7, fresh_mean=0.4, cohesion=0.499999)[0] is None
    admitted, _ = transition(None, assembly_id=7, fresh_mean=0.4, cohesion=0.5)
    assert admitted == AttractorState(7, 0.4, 0, 0.0)


def test_SPEC_BLOCKED_S02_missing_cohesion_definition():
    with pytest.raises(SpecBlocked, match="I2-S02"):
        transition(None, assembly_id=7, fresh_mean=0.4)
    _, _, graph, h, assembly = assembly_fixture()
    with pytest.raises(SpecBlocked, match="I2-S02"):
        read_only_episode(
            graph, h, (FeatureEvent((("a", "1"),)),), session_id=1, assemblies=(assembly,)
        )


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


def test_T27_pure_homeostasis_independent_golden():
    h = Homeostasis(
        {8192: 1.0, 8193: 0.7},
        {8192: 0.1, 8193: 1.0},
        {Region.LANGUAGE: 0.2},
        {Region.LANGUAGE: 0.1},
    )
    adapted = adapt(h, {8192: 0.8})
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
    updated = adapt(h, {})
    assert updated.rates[8192] == 0.95 * 0.5
    assert updated.thresholds[Region.LANGUAGE] == 0.195
