"""Pure synthetic I3 maths tests; never actual external-root evidence."""

import pytest

from dgca_next.contracts import CellAddress, SynapseKey, SynapseScope
from dgca_next.graph import SynapseState
from dgca_next.learning.evidence import (
    SyntheticEvidence,
    SyntheticProposal,
    apply_fixture_proposal,
    preview_positive_numbers,
    root_max,
)


def key(scope=SynapseScope.LOCAL):
    return SynapseKey(CellAddress.from_cell_id(8192), CellAddress.from_cell_id(8200), scope)


def proposal(root, order, ordinal, q, y, scope=SynapseScope.LOCAL):
    return SyntheticProposal(key(scope), root, order, ordinal, q, y)


def test_q_goldens_and_creation_gate_distinct_from_q():
    local = preview_positive_numbers(SynapseScope.LOCAL, 0.8, 0.6, 0.2)
    temporal = preview_positive_numbers(SynapseScope.ASSOCIATIVE, 0.8, 0.6, 0.2)
    assert local.coactivity == local.q == 0.48
    assert temporal.coactivity == 0.48 and temporal.q == 0.8 * 0.6 * 0.7408182206817179
    assert local.y == temporal.y == 0.6 + (1.0 - 0.6) * ((0.6 - 0.2) / (1.0 - 0.2))
    borderline = preview_positive_numbers(SynapseScope.ASSOCIATIVE, 0.5, 0.5, 0.2)
    assert borderline.coactivity == 0.25 and borderline.threshold_passed
    assert borderline.q == 0.5 * 0.5 * 0.7408182206817179
    assert not preview_positive_numbers(SynapseScope.LOCAL, 0.4, 0.4, 0.2).threshold_passed
    assert not preview_positive_numbers(SynapseScope.LOCAL, 1.0, 0.1, 0.2).target_active


def test_same_event_final_source_arithmetic_not_pass1_value():
    final = preview_positive_numbers(SynapseScope.LOCAL, 0.8, 0.5, 0.2)
    assert final.coactivity == 0.4
    assert final.coactivity != 0.4 * 0.5  # Pass-1 activity is a separate emitter gate.


def test_same_root_max_q_keeps_paired_y_and_counts_once():
    proposals = (proposal(1, 0, 0, 0.2, 0.9), proposal(1, 1, 0, 0.5, 0.7))
    winner = root_max(proposals)
    assert winner.q == 0.5 and winner.y == 0.7
    created = apply_fixture_proposal(None, winner)
    assert created.S == 0.7 and created.E_ext == 0.5
    assert created.roots == (1,) and created.state is SynapseState.CANDIDATE
    with pytest.raises(ValueError, match="ROOT_ID_REUSED"):
        apply_fixture_proposal(created, winner)


def test_max_q6_tie_uses_event_and_ordinal_and_rejects_mixed_key():
    later = proposal(1, 1, 1, 0.5000001, 0.6)
    earlier = proposal(1, 0, 2, 0.5, 0.8)
    assert root_max((later, earlier)) is earlier
    with pytest.raises(ValueError, match="MIXED_KEY_OR_ROOT"):
        root_max((later, proposal(2, 1, 1, 0.5, 0.6)))
    with pytest.raises(ValueError, match="DUPLICATE_PROPOSAL"):
        root_max((later, later))


def test_weighted_strength_consolidation_and_distinct_roots():
    current = apply_fixture_proposal(None, proposal(1, 0, 0, 1.0, 0.8))
    next_ = apply_fixture_proposal(current, proposal(2, 0, 0, 1.0, 0.6))
    assert next_.S == 0.7 and next_.E_ext == 2.0
    assert next_.roots == (1, 2) and next_.state is SynapseState.CANDIDATE
    next_ = apply_fixture_proposal(next_, proposal(3, 0, 0, 1.0, 0.6))
    assert next_.E_ext == 3.0 and next_.state is SynapseState.CONSOLIDATED
    assert next_.S == (2.0 * 0.7 + 1.0 * 0.6) / 3.0


def test_bounded_dual_ledger_external_priority_and_saturation():
    previous = SyntheticEvidence(key(), 0.8, 8.5, 1.5, (1, 2), SynapseState.CONSOLIDATED)
    result = apply_fixture_proposal(previous, proposal(3, 0, 0, 1.0, 0.6))
    assert result.E_ext == 9.5 and result.E_int == 0.5
    assert result.E_ext + result.E_int == 10.0
    assert result.S == (10.0 * 0.8 + 1.0 * 0.6) / 11.0
    later = apply_fixture_proposal(result, proposal(4, 0, 0, 1.0, 0.6))
    assert later.E_ext == 10.0 and later.E_int == 0.0
    assert later.S != result.S and later.roots == (1, 2, 3, 4)


def test_17_root_illustration_is_only_synthetic_arithmetic():
    numbers = preview_positive_numbers(SynapseScope.ASSOCIATIVE, 0.5, 0.5, 0.2)
    current = None
    for root in range(1, 18):
        current = apply_fixture_proposal(
            current, proposal(root, 0, 0, numbers.q, numbers.y, SynapseScope.ASSOCIATIVE)
        )
        if root == 16:
            assert current.state is SynapseState.CANDIDATE
    assert current.E_ext >= 3.0 and current.state is SynapseState.CONSOLIDATED
    assert len(current.roots) == 17 and current.fixture_only


@pytest.mark.parametrize("mass", [float("nan"), float("inf"), -0.1, 10.1])
def test_invalid_evidence_never_accepted(mass):
    with pytest.raises(ValueError):
        SyntheticEvidence(key(), 0.8, mass, 0.0, (1,), SynapseState.CANDIDATE)
