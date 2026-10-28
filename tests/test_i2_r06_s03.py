"""RC4.3 S03: frozen committed population, no real LEARN transaction."""

from dataclasses import replace

import pytest
from neural_fixtures import fixture_graph

from dgca_next.contracts import Region
from dgca_next.dynamics.homeostasis import adapt, regional_firing
from dgca_next.dynamics.measurement import full_control
from dgca_next.dynamics.numeric import SpecBlocked
from dgca_next.dynamics.session import FeatureEvent, read_only_episode
from dgca_next.dynamics.state import GraphSnapshot, Homeostasis


def homeostasis(ids, *, language_rate=0.03):
    return Homeostasis(
        {i: 1.0 for i in ids},
        {i: 0.0 for i in ids},
        {Region.LANGUAGE: 0.2},
        {Region.LANGUAGE: language_rate},
    )


def test_committed_fraction_not_logical_capacity_and_known_ema():
    graph, _, frozen, _ = fixture_graph(cells=(8192, 8193))
    h = homeostasis((8192, 8193))
    measurement = regional_firing(frozen, h, {8192: 1.0, 8193: 0.0})
    assert measurement.committed_before == (8192, 8193)
    assert measurement.active == (8192,)
    assert measurement.rho == 0.5 and measurement.rho != 1 / 4096
    updated = adapt(h, {8192: 1.0, 8193: 0.0}, graph=frozen)
    assert updated.region_rates[Region.LANGUAGE] == 0.0535
    assert updated.thresholds[Region.LANGUAGE] == 0.20500000000000002
    assert h.region_rates[Region.LANGUAGE] == 0.03
    assert graph.structural_hash == frozen.structural_hash


def test_dormant_committed_included_and_same_activity_different_population():
    _, _, one, _ = fixture_graph(cells=(8192,))
    _, _, four, _ = fixture_graph(cells=(8192, 8193, 8194, 8195))
    h = homeostasis((8192, 8193, 8194, 8195))
    activity = {8192: 0.7, 8193: 0.1}
    assert regional_firing(one, h, activity).rho == 1.0
    result = regional_firing(four, h, activity)
    assert result.committed_before == (8192, 8193, 8194, 8195)
    assert result.active == (8192,) and result.rho == 0.25
    adapted = adapt(h, activity, graph=one)
    assert adapted.rates[8193] == 0.0  # H entries are not the population authority.


def test_pre_event_threshold_is_used_at_exact_boundary():
    _, _, graph, _ = fixture_graph(cells=(8192,))
    h = homeostasis((8192,))
    result = regional_firing(graph, h, {8192: 0.2})
    assert result.threshold_before == 0.2 and result.active == (8192,)
    assert adapt(h, {8192: 0.2}, graph=graph).thresholds[Region.LANGUAGE] > 0.2


def test_newborn_excluded_from_pre_event_snapshot_and_included_next_event():
    graph, builder, pre_event, _ = fixture_graph(cells=(8192,))
    h = homeostasis((8192, 8193))
    builder.commit_cells((8193,), committed_event=1)
    next_event = GraphSnapshot.capture(graph)
    final_activity = {8192: 0.0, 8193: 1.0}
    before = regional_firing(pre_event, h, final_activity)
    after = regional_firing(next_event, h, final_activity)
    assert before.committed_before == (8192,) and before.rho == 0.0
    assert after.committed_before == (8192, 8193) and after.rho == 0.5


def test_residual_active_counts_in_rate_not_in_fresh_event_frontier():
    _, _, graph, _ = fixture_graph(cells=(9345,))
    h = homeostasis((9345,))
    _, residual = read_only_episode(
        graph, h, (FeatureEvent((("a", "1"),)), FeatureEvent(())), session_id=4
    )
    assert residual.state.activity[9345] >= 0.2
    assert not residual.state.frontiers.step
    assert regional_firing(graph, h, residual.state.activity).rho == 1.0


def test_empty_population_skips_region_and_does_not_modify_other_H():
    _, _, empty, _ = fixture_graph(cells=(0,))
    h = Homeostasis(
        {0: 1.0},
        {0: 0.3},
        {Region.LANGUAGE: 0.2, Region.VISION: 0.4},
        {Region.LANGUAGE: 0.03, Region.VISION: 0.12},
    )
    result = regional_firing(empty, h, {0: 1.0})
    assert result.rho is None and result.threshold_before is None
    assert result.committed_before == result.active == ()
    updated = adapt(h, {0: 1.0}, graph=empty)
    assert updated == h
    with pytest.raises(SpecBlocked, match="UNRESOLVED_INITIAL_THRESHOLD"):
        regional_firing(empty, h, {0: 1.0}, region=Region.VISION)


def test_language_only_updates_neither_vision_fixture_nor_extra_gains():
    _, _, graph, _ = fixture_graph(cells=(0, 8192))
    h = Homeostasis(
        {0: 1.0, 8192: 1.0, 8193: 1.0},
        {0: 0.3, 8192: 0.0, 8193: 0.4},
        {Region.LANGUAGE: 0.2, Region.VISION: 0.4},
        {Region.LANGUAGE: 0.03, Region.VISION: 0.12},
    )
    after = adapt(h, {0: 1.0, 8192: 1.0}, graph=graph)
    assert after.gains[0] == h.gains[0] and after.rates[0] == h.rates[0]
    assert after.gains[8193] == h.gains[8193] and after.rates[8193] == h.rates[8193]
    assert after.thresholds[Region.VISION] == h.thresholds[Region.VISION]
    assert after.region_rates[Region.VISION] == h.region_rates[Region.VISION]


def test_no_fabricated_population_or_caller_asserted_rho():
    _, _, graph, _ = fixture_graph(cells=(8192, 8193))
    h = homeostasis((8192, 8193))
    with pytest.raises(ValueError, match="UNVERIFIED_PRE_EVENT_POPULATION"):
        regional_firing(None, h, {8192: 1.0})
    with pytest.raises(ValueError, match="UNVERIFIED_GRAPH_SNAPSHOT"):
        regional_firing(replace(graph, structural_hash="fabricated"), h, {8192: 1.0})
    with pytest.raises(TypeError):
        adapt(h, {8192: 1.0}, graph=graph, fixture_region_firing={Region.LANGUAGE: 1.0})
    with pytest.raises(ValueError):
        regional_firing(graph, h, {8192: float("nan")})


def test_read_only_full_control_H_graph_and_caller_R_unchanged():
    network, _, graph, _ = fixture_graph(cells=(9345,))
    h = homeostasis((9345,))
    trace = read_only_episode(graph, h, (FeatureEvent((("a", "1"),)),), session_id=8)[0]
    state, before = trace.state, network.debug_dump()
    full_control(graph, state)
    assert state.homeostasis is h and state.next_order == 1
    assert network.debug_dump() == before
