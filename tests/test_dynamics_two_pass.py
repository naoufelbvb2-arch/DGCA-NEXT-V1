import pytest
from neural_fixtures import fixture_graph

from dgca_next.contracts import Region, SynapseScope
from dgca_next.dynamics.activation import two_pass
from dgca_next.dynamics.drive import aggregate, temporal_drives
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
def test_SPEC_BLOCKED_S01_live_versus_consolidated_pass2(state):
    graph, _, frozen, h = fixture_graph(
        ((8192, 8200, SynapseScope.LOCAL, 0.6, 1.0, 0.0, state),), cells=tuple(range(8192, 8202))
    )
    before = graph.debug_dump()
    with pytest.raises(SpecBlocked, match="I2-S01"):
        two_pass(frozen, h, {}, {8192: 1.0}, {}, {})
    assert graph.debug_dump() == before


def test_vision_threshold_not_invented():
    _, _, frozen, h = fixture_graph(cells=(0,))
    assert Region.VISION not in h.thresholds
    with pytest.raises(SpecBlocked, match="UNRESOLVED_INITIAL_THRESHOLD"):
        two_pass(frozen, h, {}, {0: 1.0}, {}, {})
