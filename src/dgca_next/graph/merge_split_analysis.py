"""Core 2.0 numerical eligibility only; never identity or mutation authority."""

import math
from collections.abc import Iterator, Mapping
from dataclasses import dataclass
from itertools import combinations

from dgca_next.contracts import CellAddress, Region
from dgca_next.graph.native_lifecycle import StructuralScore, parameter, quantized_sum, score
from dgca_next.graph.policy import q6

Supports = Mapping[int, Mapping[int, float]]


def _keep(value: StructuralScore) -> bool:
    # Core's ratio can exceed one in scalar-only sub-threshold R examples;
    # preserve the written equation, without clipping it or inventing a rule.
    return (
        value.degree >= int(parameter("d_min"))
        and quantized_sum(value.density) >= q6(parameter("rho_keep"))
        and quantized_sum(value.specificity) >= q6(parameter("sigma_keep"))
    )


def _members(values: tuple[int, ...]) -> None:
    if (
        type(values) is not tuple
        or values != tuple(sorted(set(values)))
        or not int(parameter("K_min")) <= len(values) <= int(parameter("K_max"))
        or any(CellAddress.from_cell_id(i).region is not Region.LANGUAGE for i in values)
    ):
        raise ValueError("INVALID_NUMERIC_ASSEMBLY_MEMBERS")


def _supports(values: Supports) -> None:
    for i, neighbors in values.items():
        if CellAddress.from_cell_id(i).region is not Region.LANGUAGE:
            raise ValueError("UNSUPPORTED_STRUCTURAL_REGION")
        for j, value in neighbors.items():
            if (
                i == j
                or CellAddress.from_cell_id(j).region is not Region.LANGUAGE
                or type(value) is not float
                or not math.isfinite(value)
                or not 0 <= value <= 1
                or values.get(j, {}).get(i) != value
            ):
                raise ValueError("INVALID_RECIPROCAL_NUMBERS")


def _counts(
    members: tuple[int, ...], counts: Mapping[int, int], minimum: Mapping[int, int]
) -> None:
    for i in members:
        value = counts.get(i, minimum[i])
        if type(value) is not int or not minimum[i] <= value <= int(parameter("M_max")):
            raise ValueError("INVALID_NUMERIC_MEMBERSHIP_COUNT")


@dataclass(frozen=True, slots=True)
class MergeMath:
    first: tuple[int, ...]
    second: tuple[int, ...]
    intersection: tuple[int, ...]
    first_exclusive: tuple[int, ...]
    second_exclusive: tuple[int, ...]
    union: tuple[int, ...]
    jaccard: float
    between_strength: float
    cross_pair_count: int
    source_scores: tuple[tuple[StructuralScore, ...], ...]
    union_scores: tuple[StructuralScore, ...]
    memberships_after: tuple[tuple[int, int], ...]
    reasons: tuple[str, ...]
    evidence_kind: str = "NUMERIC_ONLY"

    @property
    def mathematical_eligible(self) -> bool:
        return not self.reasons

    @property
    def mutation_authorized(self) -> bool:
        return False


def analyze_merge(
    first: tuple[int, ...],
    second: tuple[int, ...],
    supports: Supports,
    *,
    membership_counts: Mapping[int, int] | None = None,
) -> MergeMath:
    """Counts coalesce two owners; they never charge a fictitious third ID."""
    _members(first)
    _members(second)
    _supports(supports)
    a, b = set(first), set(second)
    union = tuple(sorted(a | b))
    common, only_a, only_b = tuple(sorted(a & b)), tuple(sorted(a - b)), tuple(sorted(b - a))
    minimum = {i: int(i in a) + int(i in b) for i in union}
    counts = {} if membership_counts is None else membership_counts
    _counts(union, counts, minimum)
    after = tuple((i, counts.get(i, minimum[i]) - minimum[i] + 1) for i in union)
    jaccard = len(common) / len(union)
    cross = tuple(supports.get(i, {}).get(j, 0.0) for i in only_a for j in only_b)
    between = sum(cross) / len(cross) if cross else 0.0
    original = tuple(tuple(score(i, group, supports) for i in group) for group in (first, second))
    proposed = tuple(score(i, union, supports) for i in union)
    reasons = []
    if not only_a or not only_b:
        reasons.append("EMPTY_EXCLUSIVE_SET")
    if q6(jaccard) < q6(parameter("theta_merge")):
        reasons.append("INSUFFICIENT_JACCARD")
    if q6(between) < q6(parameter("theta_ob")):
        reasons.append("INSUFFICIENT_BETWEEN_STRENGTH")
    if len(union) > int(parameter("K_max")):
        reasons.append("UNION_SIZE_LIMIT")
    if any(not _keep(v) for group in original for v in group):
        reasons.append("INVALID_SOURCE_KEEP")
    if any(not _keep(v) for v in proposed):
        reasons.append("UNION_KEEP_FAILED")
    if any(n > int(parameter("M_max")) for _, n in after):
        reasons.append("MEMBERSHIP_CAPACITY")
    return MergeMath(
        first,
        second,
        common,
        only_a,
        only_b,
        union,
        jaccard,
        between,
        len(cross),
        original,
        proposed,
        after,
        tuple(reasons),
    )


def bipartitions(members: tuple[int, ...]) -> Iterator[tuple[tuple[int, ...], tuple[int, ...]]]:
    """Bounded streaming enumeration, anchor in L; no region-wide subsets."""
    _members(members)
    for size in range(int(parameter("K_min")), len(members) - int(parameter("K_min")) + 1):
        for tail in combinations(members[1:], size - 1):
            left = (members[0], *tail)
            chosen = set(left)
            yield left, tuple(i for i in members if i not in chosen)


@dataclass(frozen=True, slots=True)
class SplitPartition:
    left: tuple[int, ...]
    right: tuple[int, ...]
    cross_max: float
    cross_mean: float
    scores: tuple[tuple[StructuralScore, ...], ...]


@dataclass(frozen=True, slots=True)
class SplitMath:
    members: tuple[int, ...]
    examined: int
    cross_refused: int
    mean_refused: int
    keep_refused: int
    eligible_partitions: int
    best: SplitPartition | None
    reasons: tuple[str, ...]
    evidence_kind: str = "NUMERIC_ONLY"

    @property
    def mathematical_eligible(self) -> bool:
        return not self.reasons and self.best is not None

    @property
    def mutation_authorized(self) -> bool:
        return False


def analyze_split(
    members: tuple[int, ...],
    supports: Supports,
    *,
    membership_counts: Mapping[int, int] | None = None,
) -> SplitMath:
    _members(members)
    _supports(supports)
    _counts(
        members, {} if membership_counts is None else membership_counts, {i: 1 for i in members}
    )
    if len(members) < int(parameter("N_min")):
        return SplitMath(members, 0, 0, 0, 0, 0, None, ("SPLIT_NOT_APPLICABLE",))
    if any(not _keep(score(i, members, supports)) for i in members):
        return SplitMath(members, 0, 0, 0, 0, 0, None, ("INVALID_SOURCE_KEEP",))
    examined = cross_refused = mean_refused = keep_refused = eligible = 0
    best = None
    best_key = None
    weak_q6 = q6(parameter("theta_weak"))
    separation_q6 = q6(parameter("theta_sep"))
    for left, right in bipartitions(members):
        examined += 1
        # Reject on the first strong cross edge before computing side scores.
        cross = []
        refused = False
        for i in left:
            for j in right:
                value = supports.get(i, {}).get(j, 0.0)
                if q6(value) > weak_q6:
                    refused = True
                    break
                cross.append(value)
            if refused:
                break
        if refused:
            cross_refused += 1
            continue
        mean = sum(cross) / len(cross)
        if q6(mean) >= separation_q6:
            mean_refused += 1
            continue
        scores = tuple(tuple(score(i, side, supports) for i in side) for side in (left, right))
        if any(not _keep(v) for group in scores for v in group):
            keep_refused += 1
            continue
        eligible += 1
        key = (q6(mean), left, right)
        if best_key is None or key < best_key:
            best_key = key
            best = SplitPartition(left, right, max(cross), mean, scores)
    return SplitMath(
        members,
        examined,
        cross_refused,
        mean_refused,
        keep_refused,
        eligible,
        best,
        () if best is not None else ("NO_LEGAL_BIPARTITION",),
    )
