"""NUMERIC_ONLY Core geometry; no native identity or production mutation."""

import copy
from dataclasses import FrozenInstanceError

import pytest

from dgca_next.graph.merge_split_analysis import analyze_merge, analyze_split, bipartitions
from dgca_next.learning.evidence import _positive_external_update
from dgca_next.persistence.reachability_inspection import (
    COOLDOWN_DECISION,
    CompletedRootClock,
    cooldown_alternatives,
    inspect_reachability,
)


def complete(cells, value=0.5):
    return {i: {j: value for j in cells if j != i} for i in cells}


def two_cliques(cross=0.05):
    cells = tuple(range(8192, 8198))
    return cells, {
        i: {j: 0.5 if (i < 8195) == (j < 8195) else cross for j in cells if j != i} for i in cells
    }


@pytest.mark.parametrize(
    "case,expected",
    [
        ("disjoint", 0.0),
        ("identical", 1.0),
        ("nested", 0.75),
        ("five_overlap_four", 4 / 6),
        ("six_overlap_five", 5 / 7),
        ("exact", 0.7),
    ],
)
def test_jaccard_and_nonempty_exclusives(case, expected):
    first = tuple(range(8192, 8198))
    second = (*first[:5], 8198)
    if case == "disjoint":
        first, second = tuple(range(8192, 8195)), tuple(range(8195, 8198))
    elif case == "identical":
        second = first
    elif case == "nested":
        first, second = tuple(range(8192, 8195)), tuple(range(8192, 8196))
    elif case == "five_overlap_four":
        first, second = tuple(range(8192, 8197)), (*range(8192, 8196), 8197)
    elif case == "exact":
        first, second = tuple(range(8192, 8200)), (*range(8192, 8199), 8200, 8201)
    result = analyze_merge(first, second, complete(tuple(sorted(set(first) | set(second)))))
    assert result.jaccard == expected
    assert result.mathematical_eligible == (case in ("six_overlap_five", "exact"))
    assert result.between_strength == (0.0 if case in ("identical", "nested") else 0.5)
    assert result.evidence_kind == "NUMERIC_ONLY" and not result.mutation_authorized


@pytest.mark.parametrize("value,eligible", [(0.3999994, False), (0.3999996, True), (0.4, True)])
def test_between_strength_uses_core_q6(value, eligible):
    first, second = tuple(range(8192, 8198)), (*range(8192, 8197), 8198)
    values = complete(tuple(range(8192, 8199)))
    values[8197][8198] = values[8198][8197] = value
    assert analyze_merge(first, second, values).mathematical_eligible is eligible


def test_merge_capacity_coalesces_owners_and_union_size_is_bounded():
    first, second = tuple(range(8192, 8198)), (*range(8192, 8197), 8198)
    values = complete(tuple(range(8192, 8199)))
    result = analyze_merge(first, second, values, membership_counts={i: 12 for i in values})
    assert result.mathematical_eligible
    assert dict(result.memberships_after)[8192] == 11
    assert dict(result.memberships_after)[8197] == dict(result.memberships_after)[8198] == 12
    with pytest.raises(ValueError, match="MEMBERSHIP_COUNT"):
        analyze_merge(first, second, values, membership_counts={8192: 13})
    first, second = tuple(range(8192, 8208)), tuple(range(8194, 8210))
    result = analyze_merge(first, second, complete(tuple(range(8192, 8210))))
    assert result.jaccard >= 0.7 and "UNION_SIZE_LIMIT" in result.reasons


def test_merge_union_keep_uses_actual_density_and_full_region_specificity():
    first, second = tuple(range(8192, 8198)), (*range(8192, 8197), 8198)
    values = complete(tuple(range(8192, 8199)))
    for j in (8195, 8196, 8197, 8198):
        del values[8192][j]
        del values[j][8192]
    result = analyze_merge(first, second, values)
    assert "UNION_KEEP_FAILED" in result.reasons and "INVALID_SOURCE_KEEP" not in result.reasons
    values = complete(tuple(range(8192, 8199)))
    for outside in range(8220, 8236):
        values[outside] = {i: 1.0 for i in range(8192, 8199)}
        for i in range(8192, 8199):
            values[i][outside] = 1.0
    result = analyze_merge(first, second, values)
    assert "UNION_KEEP_FAILED" in result.reasons
    assert result.union_scores[0].denominator > result.union_scores[0].numerator


@pytest.mark.parametrize(
    "cross,eligible",
    [(0.0, True), (0.05, True), (0.0999994, True), (0.0999996, False), (0.1, False), (0.15, False)],
)
def test_split_cliques_and_strict_mean_boundary(cross, eligible):
    cells, values = two_cliques(cross)
    result = analyze_split(cells, values)
    assert result.examined == 10
    assert result.mathematical_eligible is eligible
    if eligible:
        assert result.best.left == cells[:3] and result.best.right == cells[3:]
    assert result.evidence_kind == "NUMERIC_ONLY" and not result.mutation_authorized


def test_one_strong_cross_edge_refuses_even_when_mean_is_small():
    cells, values = two_cliques(0.0)
    values[8192][8195] = values[8195][8192] = 0.150001
    result = analyze_split(cells, values)
    assert not result.mathematical_eligible and result.cross_refused == 10


def test_side_keep_is_required_even_if_cross_thresholds_pass():
    cells, values = two_cliques(0.0)
    values[8192][8193] = values[8193][8192] = 0.0
    values[8192][8195] = values[8195][8192] = 0.1
    values[8193][8196] = values[8196][8193] = 0.1
    result = analyze_split(cells, values)
    assert not result.mathematical_eligible and result.keep_refused > 0
    assert result.examined == 10


def test_partition_ranking_is_deterministic_for_equal_mean_cuts():
    cells = tuple(range(8192, 8201))
    values = {
        i: {j: 0.5 if (i - 8192) // 3 == (j - 8192) // 3 else 0.0 for j in cells if j != i}
        for i in cells
    }
    for i in cells:
        j = 8192 + (i - 8192 + 3) % 9
        values[i][j] = values[j][i] = 0.11
    result = analyze_split(cells, values)
    assert result.eligible_partitions == 3 and result.best.left == cells[:3]
    reversed_values = {
        i: dict(reversed(list(v.items()))) for i, v in reversed(list(values.items()))
    }
    assert analyze_split(cells, reversed_values) == result


def test_small_source_and_streaming_bound_are_explicit():
    cells = tuple(range(8192, 8208))
    assert sum(1 for _ in bipartitions(cells)) == 32631
    assert all(
        cells[0] in left and 3 <= len(left) <= 13 and len(right) >= 3
        for left, right in bipartitions(cells)
    )
    result = analyze_split(cells[:4], complete(cells[:4]))
    assert result.reasons == ("SPLIT_NOT_APPLICABLE",) and result.examined == 0
    with pytest.raises(ValueError, match="MEMBERS"):
        tuple(bipartitions((*cells, 8208)))


@pytest.mark.parametrize("damage", ["nan", "asymmetric", "self", "wrong_region"])
def test_invalid_numerical_support_fails_closed(damage):
    cells, values = two_cliques()
    if damage == "nan":
        values[8192][8193] = float("nan")
    elif damage == "asymmetric":
        values[8192][8193] = 0.8
    elif damage == "self":
        values[8192][8192] = 0.2
    else:
        values[1] = {}
    with pytest.raises(ValueError):
        analyze_split(cells, values)


def test_analysis_is_immutable_and_cannot_authorize_production():
    cells, values = two_cliques()
    saved = copy.deepcopy(values)
    result = analyze_split(cells, values)
    assert values == saved
    with pytest.raises(FrozenInstanceError):
        result.examined = 0
    with pytest.raises(ValueError, match="NATIVE_ROOTSTORE_REQUIRED"):
        inspect_reachability(result)


def test_positive_only_consolidated_floor_and_saturation_are_not_passive_decay():
    # Formula-only; not external evidence or a learned synapse.
    for strength, mass, q, y in ((0.6, 3.0, 0.2, 0.6), (1.0, 10.0, 0.5, 0.6)):
        updated_s, updated_e, internal = _positive_external_update(strength, mass, 0.0, q, y)
        assert internal == 0.0 and updated_s * updated_e / 10 >= 0.18
    assert updated_s < 1.0  # Q can decrease at saturation, but not to weak-cross range.


def test_completed_clock_unit_alternatives_and_199_200_are_numeric_only():
    # Scalar history examples. They are NOT claimed as 200 genuine root trials.
    one_five = (CompletedRootClock(1, 1, 1, 1), CompletedRootClock(2, 2, 5, 6))
    result = cooldown_alternatives(one_five, 0)
    assert result.elapsed_roots == 2 and result.elapsed_events == 6
    assert result.status == COOLDOWN_DECISION
    boundary = (CompletedRootClock(1, 1, 199, 199),)
    assert not cooldown_alternatives(boundary, 0).events_interpretation_passes
    boundary += (CompletedRootClock(2, 2, 1, 200),)
    assert cooldown_alternatives(boundary, 0).events_interpretation_passes
    assert not cooldown_alternatives(boundary, 0).roots_interpretation_passes
    roots = tuple(CompletedRootClock(i, i, 1, i) for i in range(1, 201))
    assert not cooldown_alternatives(roots[:199], 0).roots_interpretation_passes
    assert cooldown_alternatives(roots, 0).roots_interpretation_passes
    assert cooldown_alternatives(one_five, 1).elapsed_events == 5
    assert cooldown_alternatives(one_five, None).status == "NOT_PREVIOUSLY_EDITED"
    with pytest.raises(ValueError, match="UNKNOWN_COMPLETED_CLOSE"):
        cooldown_alternatives(one_five, 3)
