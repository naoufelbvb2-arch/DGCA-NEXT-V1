import pytest
from neural_fixtures import fixture_graph

from dgca_next.contracts import Region, SynapseScope
from dgca_next.dynamics.activation import two_pass
from dgca_next.dynamics.drive import aggregate, synchronous_drives, temporal_drives
from dgca_next.dynamics.numeric import SpecBlocked
from dgca_next.dynamics.state import GraphSnapshot
from dgca_next.graph import SynapseState
from dgca_next.peripheral.sic import project


def test_T06_uncommitted_X_no_activity_or_commitment():
    graph, _, frozen, h = fixture_graph()
    before = graph.debug_dump()
    result = two_pass(frozen, h, {}, dict(project((("a", "1"),)).X), {}, {})
    assert not result.second.activity
    assert graph.debug_dump() == before
    assert graph.stored_cell_count == 0


def test_T06_uncommitted_direct_raw_still_participates_in_column_mean():
    graph, _, frozen, h = fixture_graph(cells=(9345,))
    inputs = dict(project((("a", "1"), ("x12", "1"))).X)
    assert inputs[9344] == inputs[9345] == 1.0
    result = two_pass(frozen, h, {}, inputs, {}, {})
    assert result.first.raw[9344] == 1.0
    assert result.first.activity[9345] == 0.8 / 1.2
    assert 9344 not in result.first.activity and 9344 not in result.emitters
    assert not graph.cell(9344).committed


def test_T09_associative_no_evidence_factor_and_quality():
    _, _, frozen, _ = fixture_graph(
        ((8192, 8200, SynapseScope.ASSOCIATIVE, 1.0, 3.0, 0.0, SynapseState.CONSOLIDATED),)
    )
    drive = aggregate(temporal_drives(frozen, {8192: 0.8}, frozenset({8192}), {}))
    assert drive[8200] == pytest.approx(0.24, abs=1e-15)
    assert temporal_drives(frozen, {8192: 0.8}, frozenset(), {}) == ()


def test_T09_internal_evidence_discount_exactly_once():
    _, _, frozen, _ = fixture_graph(
        ((8192, 8200, SynapseScope.ASSOCIATIVE, 0.8, 2.0, 4.0, SynapseState.CANDIDATE),)
    )
    drives = temporal_drives(frozen, {8192: 0.8}, frozenset({8192}), {})
    assert drives[0].value == 0.8 * (0.75 * 0.8 * (6.0 / 10.0))


def test_T10_T11_two_pass_frozen_source_and_no_third_iteration():
    _, _, frozen, h = fixture_graph(
        ((8192, 8200, SynapseScope.LOCAL), (8200, 8208, SynapseScope.LOCAL))
    )
    result = two_pass(frozen, h, {}, {8192: 1.0}, {}, {})
    first = 0.8 / (1 + 0.8 / 8)
    assert result.first.activity[8192] == first
    assert result.emitters == frozenset({8192})
    assert result.second.raw[8200] == pytest.approx(first)
    assert result.second.activity[8200] == pytest.approx(0.8 * first / (1 + 0.8 * first / 8))
    assert result.second.activity[8208] == 0.0
    assert result.first.activity[8200] == 0.0


def test_T12_gate_precedes_column_mean_and_residual():
    _, _, frozen, h = fixture_graph(cells=(8192, 8193))
    result = two_pass(frozen, h, {8193: 1.0}, {8192: 1.0, 8193: 1.0}, {}, {}, gates={8193: False})
    assert result.first.activity[8193] == result.second.activity[8193] == 0.0
    assert result.first.activity[8192] == 0.8 / 1.1
    assert result.second.normalized[8192] == 1.0 / 1.1


def test_T12_eight_logical_slots_and_frozen_previous_on_both_passes():
    _, _, frozen, h = fixture_graph(cells=(8192, 8193))
    result = two_pass(frozen, h, {8192: 0.2}, {8192: 0.5, 8193: 0.5}, {}, {})
    assert result.second.activity[8192] == 0.8 * 0.2 + 0.8 * (0.5 / 1.1)
    assert result.first == result.second


def test_T31_same_state_bit_identical_and_immutable():
    graph, builder, frozen, h = fixture_graph(cells=(8192,))
    a = two_pass(frozen, h, {}, {8192: 1.0}, {}, {})
    assert a == two_pass(frozen, h, {}, {8192: 1.0}, {}, {})
    with pytest.raises(TypeError):
        a.second.activity[8192] = 0.0
    builder.commit_cells((8193,), committed_event=0)
    assert frozen.committed_ids == frozenset({8192})
    assert GraphSnapshot.capture(graph).committed_ids == frozenset({8192, 8193})


@pytest.mark.parametrize("state", [SynapseState.CANDIDATE, SynapseState.EPISODIC_INDEXED])
def test_S01_live_nonconsolidated_pass2_propagates_own_quality(state):
    graph, _, frozen, h = fixture_graph(
        ((8192, 8200, SynapseScope.LOCAL, 0.6, 1.0, 0.0, state),), cells=tuple(range(8192, 8202))
    )
    before = graph.debug_dump()
    result = two_pass(frozen, h, {}, {8192: 1.0}, {}, {})
    assert result.synchronous[0].value == result.first.activity[8192] * 0.06
    assert result.second.activity[8200] > 0
    assert graph.debug_dump() == before


def test_vision_threshold_not_invented():
    _, _, frozen, h = fixture_graph(cells=(0,))
    assert Region.VISION not in h.thresholds
    with pytest.raises(SpecBlocked, match="UNRESOLVED_INITIAL_THRESHOLD"):
        two_pass(frozen, h, {}, {0: 1.0}, {}, {})


def test_cross_scope_directed_synchronous_quality_on_physical_fixture():
    _, _, frozen, _ = fixture_graph(((8192, 0, SynapseScope.CROSS_TERRITORY),))
    drives = synchronous_drives(frozen, {8192: 0.7}, frozenset({8192}))
    assert len(drives) == 1
    assert drives[0].source_id == 8192 and drives[0].target_id == 0
    assert drives[0].scope is SynapseScope.CROSS_TERRITORY and drives[0].value == 0.7


def test_stable_contributor_order_under_reversed_graph_construction():
    edges = tuple((i, 8216, SynapseScope.LOCAL) for i in (8192, 8200, 8208))
    _, _, first, h1 = fixture_graph(edges)
    _, _, second, h2 = fixture_graph(tuple(reversed(edges)))
    X = {8192: 1.0, 8200: 0.7, 8208: 0.5}
    a = two_pass(first, h1, {}, X, {}, {})
    b = two_pass(second, h2, {}, X, {}, {})
    assert a == b
    assert tuple(d.source_id for d in a.synchronous) == (8192, 8200, 8208)
    complement = 1.0
    for d in a.synchronous:
        complement *= 1.0 - d.value
    assert a.second.raw[8216] == 1.0 - complement
