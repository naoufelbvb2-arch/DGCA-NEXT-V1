from dataclasses import FrozenInstanceError, replace

import pytest
from neural_fixtures import context_fixture, fixture_graph

from dgca_next.contracts import EventOrigin, SynapseScope
from dgca_next.dynamics.provenance import Lane, RuntimeSupport, SourceKind
from dgca_next.dynamics.session import (
    FeatureEvent,
    RuntimeState,
    cold_reset,
    cold_state,
    read_only_episode,
    read_only_step,
)


def test_T13_T14_residual_prediction_spatial_not_fresh():
    graph, _, frozen, h = fixture_graph(
        ((9345, 8200, SynapseScope.ASSOCIATIVE), (9345, 8208, SynapseScope.LOCAL)),
        cells=(8606, 11795, 12181),
    )
    before = graph.debug_dump()
    first, second = read_only_episode(
        frozen, h, (FeatureEvent((("a", "1"),)), FeatureEvent(())), session_id=71
    )
    assert 9345 in first.state.frontiers.step
    assert 8208 not in first.state.frontiers.step
    assert second.temporal[8200] > 0
    assert second.state.activity[9345] > 0
    assert second.state.frontiers.step == frozenset()
    assert second.state.witnesses == {}
    assert graph.debug_dump() == before


@pytest.mark.parametrize("support,emits", [("0.1", False), ("1", True)])
def test_T15_observed_committed_actual_emission(support, emits):
    _, _, frozen, h = fixture_graph(cells=(9345,))
    trace = read_only_episode(frozen, h, (FeatureEvent((("a", support),)),), session_id=4)[0]
    assert (9345 in trace.state.frontiers.step) is emits
    assert trace.observation.X_fixed
    assert set(trace.state.activity) == {9345}
    assert len(trace.contributions) == 4  # Direct reception is retained even on uncommitted IDs.


def test_T16_prior_frozen_final_activity_not_current_residual():
    _, _, frozen, h = fixture_graph(((9345, 8200, SynapseScope.ASSOCIATIVE),))
    first, second, third = read_only_episode(
        frozen, h, (FeatureEvent((("a", "1"),)), FeatureEvent(()), FeatureEvent(())), session_id=4
    )
    a = first.state.activity[9345]
    assert second.temporal[8200] == pytest.approx(a)
    assert second.state.activity[9345] == pytest.approx(0.8 * a)
    assert third.temporal == {}


def test_T17_cold_and_hard_boundary_remove_eligibility():
    _, _, frozen, h = fixture_graph(((9345, 8200, SynapseScope.ASSOCIATIVE),))
    initial = cold_state(frozen, h, session_id=4)
    first = read_only_step(frozen, initial, FeatureEvent((("a", "1"),)))
    reset = cold_reset(first.state)
    assert not reset.activity and not reset.history and not reset.witnesses
    assert not reset.mu and not reset.frontiers.step and not reset.emitters
    assert reset.homeostasis is h
    boundary = read_only_step(frozen, first.state, FeatureEvent((), boundary=True))
    assert not boundary.temporal
    assert set(boundary.state.activity.values()) == {0.0}
    independent = read_only_episode(frozen, h, (FeatureEvent(()),), session_id=5)[0]
    assert independent.temporal == {}


def test_T18_multiple_lanes_without_direct_overwrite():
    _, _, frozen, h = fixture_graph(
        ((9345, 8606, SynapseScope.ASSOCIATIVE), (9345, 8606, SynapseScope.LOCAL))
    )
    first, second = read_only_episode(
        frozen, h, (FeatureEvent((("a", "1"),)), FeatureEvent((("a", "1"),))), session_id=71
    )
    lanes = {c.lane for c in second.contributions if c.target_id == 8606}
    assert {Lane.DIRECT_OBSERVED, Lane.PREDICTED, Lane.SPATIALLY_COMPLETED, Lane.RESIDUAL} <= lanes
    assert second.state.witnesses[8606].kind is SourceKind.READ_ONLY_OBSERVED
    assert second.state.witnesses[8606].value == 1.0
    assert first.state.next_order == 1 and second.state.next_order == 2


def test_T19_forbidden_provenance_inputs_fail_closed():
    _, _, frozen, h = fixture_graph(cells=(9345,))
    with pytest.raises(ValueError, match="UNVERIFIED_RUNTIME"):
        RuntimeState(1, 0, frozen.structural_hash, h)
    for kind in (
        SourceKind.EXTERNAL_DIRECT,
        SourceKind.INTERNAL_SELECTED,
        SourceKind.DERIVED_EXTERNAL_CONTEXT,
    ):
        with pytest.raises(ValueError, match="NO_EXTERNAL"):
            RuntimeSupport(9345, 1.0, kind, 1, 0, "digest")
    with pytest.raises(ValueError, match="UNVERIFIED_EVENT"):
        read_only_step(frozen, cold_state(frozen, h, session_id=1), {"X": {9345: 1.0}})


def test_T30_replay_is_features_in_new_session_never_a_root():
    _, _, frozen, h = fixture_graph(cells=(9345,))
    first = FeatureEvent((("a", "1"),))
    trace = read_only_episode(frozen, h, (first,), session_id=10)[0]
    sealed = FeatureEvent(first.features, sealed_digest=trace.observation.digest)
    replay = read_only_episode(frozen, h, (sealed,), session_id=11)[0]
    assert replay.provenance.origin is EventOrigin.READ_ONLY_OBSERVED
    assert replay.provenance.exposure_id is None
    assert replay.state.activity == trace.state.activity
    with pytest.raises(ValueError, match="SEALED_FEATURE"):
        FeatureEvent(first.features, sealed_digest="wrong")


def test_runtime_nested_immutability_and_bounded_history():
    _, _, frozen, h = fixture_graph(cells=(9345,))
    traces = read_only_episode(
        frozen, h, tuple(FeatureEvent((("a", "1"),)) for _ in range(8)), session_id=1
    )
    state = traces[-1].state
    assert len(state.history) == 5
    assert state.A_prev == traces[-2].state.activity
    with pytest.raises(TypeError):
        state.history[-1][9345] = 0.0
    with pytest.raises(FrozenInstanceError):
        state.witnesses[9345].kind = SourceKind.INTERNAL_SELECTED


def test_T19_forged_predecessor_cannot_be_installed_on_copied_state():
    _, _, graph, h, bindings = context_fixture()
    cold = cold_state(graph, h, session_id=1, bindings=bindings)
    blank = read_only_step(graph, cold, FeatureEvent(())).state
    forged = {
        i: RuntimeSupport(i, 1.0, SourceKind.READ_ONLY_OBSERVED, 1, 0, "forged")
        for i in bindings[0].predecessor
    }
    with pytest.raises(ValueError, match="UNVERIFIED_RUNTIME_PROVENANCE"):
        replace(blank, witnesses=forged)
    actual = read_only_step(graph, blank, FeatureEvent((("ab", "1"),)))
    assert not actual.gates[bindings[0].z]
    assert actual.state.activity[bindings[0].z] == 0.0


def test_sealed_replay_rejects_same_X_from_different_canonical_input():
    _, _, graph, h = fixture_graph(cells=(9345,))
    event = FeatureEvent((("a", "1"),), salience="0.5")
    trace = read_only_step(graph, cold_state(graph, h, session_id=1), event)
    with pytest.raises(ValueError, match="SEALED_FEATURE_DIGEST_MISMATCH"):
        FeatureEvent((("a", "0.5"),), sealed_digest=trace.observation.digest)


def test_receiver_collision_diagnostic_is_visible_in_event_trace():
    _, _, graph, h = fixture_graph(cells=(8606,))
    trace = read_only_step(
        graph, cold_state(graph, h, session_id=1), FeatureEvent((("a", "0.5"), ("f617", "0.25")))
    )
    assert "CELL_FEATURE_ALIAS:8606" in trace.diagnostics
