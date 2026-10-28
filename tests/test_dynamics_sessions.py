import pytest
from neural_fixtures import assembly_fixture, context_fixture, fixture_graph

from dgca_next.contracts import SynapseScope
from dgca_next.dynamics.measurement import EvaluationFootprint, full_control, pred_score
from dgca_next.dynamics.session import FeatureEvent, cold_state, read_only_episode, read_only_step


def test_T28_FULL_CONTROL_from_same_snapshot_no_new_event():
    graph, _, frozen, h = fixture_graph(
        ((9345, 8200, SynapseScope.ASSOCIATIVE), (8200, 8208, SynapseScope.LOCAL))
    )
    trace = read_only_episode(frozen, h, (FeatureEvent((("a", "1"),)),), session_id=1)[0]
    state, before = trace.state, graph.debug_dump()
    result = full_control(frozen, state)
    assert result.temporal[8200] > 0
    assert result.control.second.activity[8200] == 0.0
    assert result.full.second.activity[8200] > 0
    assert result.gain[8200] == result.full.second.activity[8200]
    assert result.gain[9345] == 0.0
    assert 8200 in result.eligible_neural_next
    # P_S follows the same law and causally changes when FULL makes 8200 emit.
    assert result.full.second.activity[8208] > result.control.second.activity[8208]
    assert 8208 not in result.eligible_neural_next  # No direct temporal drive to 8208.
    assert state is trace.state and state.next_order == 1
    assert graph.debug_dump() == before
    assert full_control(frozen, state) == result


def test_T28_preserve_attractor_residual_and_homeostasis():
    graph, _, frozen, h, assembly = assembly_fixture()
    trace = read_only_episode(
        frozen,
        h,
        (FeatureEvent((("a", "1"),)),),
        session_id=1,
        assemblies=(assembly,),
        fixture_cohesion={7: 0.8},
    )[0]
    before = graph.structural_hash
    result = full_control(frozen, trace.state)
    assert result.full == result.control
    assert all(v > 0 for v in result.control.second.activity.values())
    assert trace.state.homeostasis is h
    assert trace.state.attractors[0].age == 0
    assert graph.structural_hash == before


def test_T29_evaluator_footprints_cannot_feed_neural_runtime():
    _, _, frozen, h, bindings = context_fixture()
    trace = read_only_episode(
        frozen,
        h,
        (FeatureEvent((("a", "1"),)), FeatureEvent((("ab", "1"),))),
        session_id=1,
        bindings=bindings,
    )[-1]
    before = full_control(frozen, trace.state)
    correct = pred_score(frozen, trace.state, EvaluationFootprint((8200, 8208)))
    other = pred_score(frozen, trace.state, EvaluationFootprint((8216,)))
    assert correct[0] == other[0] == "RESOLVED"
    assert correct[1] > 0 and other[1] == 0.0
    assert full_control(frozen, trace.state) == before
    for outcome in (
        EvaluationFootprint(()),
        EvaluationFootprint((8200,), aliased=True),
        EvaluationFootprint((8200,), comparable=False),
    ):
        assert pred_score(frozen, trace.state, outcome) == ("UNRESOLVED", None)


@pytest.mark.parametrize("stage", ["CANONICAL_INPUT", "PASS2", "RESULT"])
def test_T32_fault_injection_no_graph_R_H_mutation(stage):
    graph, _, frozen, h = fixture_graph(cells=(9345,))
    state = cold_state(frozen, h, session_id=1)
    before = graph.debug_dump()

    def interrupt(checkpoint):
        assert state.activity == {}
        assert graph.debug_dump() == before
        if checkpoint == stage:
            raise RuntimeError("injected")

    with pytest.raises(RuntimeError, match="injected"):
        read_only_step(frozen, state, FeatureEvent((("a", "1"),)), fail_hook=interrupt)
    assert state.activity == {} and state.next_order == 0
    assert state.homeostasis is h and graph.debug_dump() == before
    assert read_only_step(frozen, state, FeatureEvent((("a", "1"),))).state.next_order == 1


@pytest.mark.parametrize("feature,support", [("a", "NaN"), ("\ud800", "1"), ("a", "0.0000001")])
def test_T07_malformed_feature_event_leaves_graph_and_caller_R_unchanged(feature, support):
    graph, _, frozen, h = fixture_graph(cells=(9345,))
    state = read_only_step(
        frozen, cold_state(frozen, h, session_id=1), FeatureEvent((("a", "1"),))
    ).state
    before = graph.debug_dump()
    before_activity = dict(state.activity)
    with pytest.raises(ValueError):
        read_only_step(frozen, state, FeatureEvent(((feature, support),)))
    assert graph.debug_dump() == before
    assert dict(state.activity) == before_activity and state.next_order == 1
    assert state.homeostasis is h
