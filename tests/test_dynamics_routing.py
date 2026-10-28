from neural_fixtures import context_fixture

from dgca_next.dynamics.drive import aggregate
from dgca_next.dynamics.session import FeatureEvent, next_drives, read_only_episode


def test_T22_masked_ordinary_and_preserved_depth2_target():
    graph, _, frozen, h, bindings = context_fixture(nested=True)
    before = graph.debug_dump()
    traces = read_only_episode(
        frozen,
        h,
        (FeatureEvent((("a", "1"),)), FeatureEvent((("ab", "1"),)), FeatureEvent((("é", "1"),))),
        session_id=4,
        bindings=bindings,
    )
    post_B = traces[1].state
    assert post_B.mu[8694] == 1.0
    directed = {(d.source_id, d.target_id): d.value for d in next_drives(frozen, post_B)}
    assert (8694, 8216) not in directed
    assert directed[8694, 8194] > 0
    assert traces[2].gates[8194]
    assert 8194 in traces[2].state.frontiers.step
    assert traces[2].state.witnesses[8194].depth == 2
    lineage = traces[2].state.witnesses[8194].parents[0]
    assert lineage.cell_id == 8192 and lineage.depth == 1
    assert len(lineage.parents) >= 3
    assert graph.debug_dump() == before


def test_T23_ambiguous_owners_keep_generic_routing():
    _, _, frozen, h, bindings = context_fixture(ambiguous=True)
    traces = read_only_episode(
        frozen,
        h,
        (FeatureEvent((("a", "1"),)), FeatureEvent((("ab", "1"),))),
        session_id=4,
        bindings=bindings,
    )
    state = traces[-1].state
    assert 8192 in state.frontiers.step and 8193 in state.frontiers.step
    assert state.mu[8694] == 0.0
    assert any(d == "AMBIGUOUS_CONTEXT_OWNER:8694" for d in traces[-1].diagnostics)
    assert aggregate(next_drives(frozen, state))[8216] > 0


def test_T24_mask_frozen_no_future_input_and_one_step_only():
    _, _, frozen, h, bindings = context_fixture()
    traces = read_only_episode(
        frozen,
        h,
        (FeatureEvent((("a", "1"),)), FeatureEvent((("ab", "1"),)), FeatureEvent(())),
        session_id=4,
        bindings=bindings,
    )
    before = traces[1].state
    assert aggregate(next_drives(frozen, before)).get(8216, 0.0) == 0.0
    assert dict(before.mu) == dict(traces[1].state.mu)
    assert not traces[-1].state.mu
    assert not traces[-1].state.frontiers.step
