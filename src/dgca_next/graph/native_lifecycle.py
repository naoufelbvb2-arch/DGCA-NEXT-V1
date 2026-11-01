"""Pure Core 2.0 MAINTAIN/GROW arithmetic; plans confer no write authority."""

import math
from collections.abc import Mapping
from dataclasses import dataclass

from dgca_next.config import load_lab_config
from dgca_next.contracts import CellAddress, Region
from dgca_next.graph.policy import q6

_CONFIG = load_lab_config()


def parameter(name: str) -> float:
    return float(_CONFIG.parameter(name).value)


def quantized_sum(value: float) -> int:
    """Core 3.1 Q6 on a sum (unlike a support, it may exceed one)."""
    if type(value) is not float or not math.isfinite(value) or value < 0:
        raise ValueError("INVALID_STRUCTURAL_SUM")
    numerator, denominator = value.as_integer_ratio()
    result, remainder = divmod(numerator * 1_000_000, denominator)
    return result + int(
        2 * remainder > denominator or (2 * remainder == denominator and result % 2)
    )


@dataclass(frozen=True, slots=True)
class StructuralScore:
    cell_id: int
    degree: int
    density: float
    numerator: float
    denominator: float
    specificity: float


def score(
    cell: int, members: tuple[int, ...], supports: Mapping[int, Mapping[int, float]]
) -> StructuralScore:
    neighbors = supports.get(cell, {})
    own = tuple(i for i in members if i != cell)
    degree = sum(q6(neighbors.get(i, 0.0)) >= q6(parameter("theta_A")) for i in own)
    numerator = sum(neighbors.get(i, 0.0) for i in own)
    denominator = sum(
        (v for _, v in sorted(neighbors.items()) if q6(v) >= q6(parameter("theta_A"))), 0.0
    )
    return StructuralScore(
        cell,
        degree,
        degree / len(own) if own else 0.0,
        numerator,
        denominator,
        numerator / denominator if denominator else 0.0,
    )


def passes(value: StructuralScore, density: str, specificity: str) -> bool:
    return (
        value.degree >= int(parameter("d_min"))
        and q6(value.density) >= q6(parameter(density))
        and q6(value.specificity) >= q6(parameter(specificity))
    )


@dataclass(frozen=True, slots=True)
class StructuralEvaluation:
    assembly_id: int
    stage: str
    cell_id: int | None
    members: tuple[int, ...]
    rank_support: float
    scores: tuple[StructuralScore, ...]
    reason: str


@dataclass(frozen=True, slots=True)
class StructuralEdit:
    assembly_id: int
    stage: str
    before: tuple[int, ...]
    after: tuple[int, ...]
    evaluation: StructuralEvaluation


def plan_maintain_grow(
    live: Mapping[int, tuple[int, ...]],
    supports: Mapping[int, Mapping[int, float]],
    memberships: Mapping[int, frozenset[int]],
    committed: frozenset[int],
) -> tuple[tuple[StructuralEdit, ...], tuple[StructuralEvaluation, ...]]:
    """One ranked pass, finite reciprocal neighborhoods, lowest-ID removal."""
    current = dict(live)
    counts = {i: len(ids) for i, ids in memberships.items()}
    edits: list[StructuralEdit] = []
    evaluations = []
    for identity in sorted(current):
        members = current[identity]
        while len(members) >= int(parameter("K_min")):
            values = tuple(score(i, members, supports) for i in members)
            failing = tuple(v.cell_id for v in values if not passes(v, "rho_keep", "sigma_keep"))
            cell = min(failing) if failing else None
            evaluation = StructuralEvaluation(
                identity, "MAINTAIN", cell, members, 0.0, values, "REMOVE" if failing else "KEEP"
            )
            evaluations.append(evaluation)
            if cell is None:
                break
            after = tuple(i for i in members if i != cell)
            edits.append(
                StructuralEdit(
                    identity,
                    "ARCHIVE" if len(after) < int(parameter("K_min")) else "MAINTAIN_REMOVE",
                    members,
                    after,
                    evaluation,
                )
            )
            counts[cell] = counts.get(cell, 0) - 1
            members = after
        current[identity] = members
        if len(members) < int(parameter("K_min")):
            for cell in members:
                counts[cell] = counts.get(cell, 0) - 1
    for identity in sorted(current):
        members = current[identity]
        if len(members) < int(parameter("K_min")):
            continue
        candidates = {
            i
            for j in members
            for i, v in supports.get(j, {}).items()
            if i in committed
            and i not in members
            and CellAddress.from_cell_id(i).region is Region.LANGUAGE
            and q6(v) >= q6(parameter("theta_A"))
        }
        ranked = sorted(
            ((sum(supports.get(i, {}).get(j, 0.0) for j in members), i) for i in candidates),
            key=lambda item: (-quantized_sum(item[0]), item[1]),
        )
        for rank_support, cell in ranked:
            if len(members) >= int(parameter("K_max")):
                break
            prospective = tuple(sorted((*members, cell)))
            values = tuple(score(i, prospective, supports) for i in prospective)
            candidate = next(v for v in values if v.cell_id == cell)
            reason = (
                "MEMBERSHIP_CAPACITY"
                if counts.get(cell, 0) >= int(parameter("M_max"))
                else "CANDIDATE_GROW_FAILED"
                if not passes(candidate, "rho_G", "sigma_G")
                else "EXISTING_MEMBER_KEEP_FAILED"
                if any(not passes(v, "rho_keep", "sigma_keep") for v in values if v.cell_id != cell)
                else "ADD"
            )
            evaluation = StructuralEvaluation(
                identity, "GROW", cell, members, rank_support, values, reason
            )
            evaluations.append(evaluation)
            if reason == "ADD":
                edits.append(StructuralEdit(identity, "GROW_ADD", members, prospective, evaluation))
                members = prospective
                counts[cell] = counts.get(cell, 0) + 1
        current[identity] = members
    return tuple(edits), tuple(evaluations)


def guard_deferred(live: tuple[tuple[int, ...], ...]) -> None:
    """Conservative approved containment, not an implementation of R04."""
    if len(live) > 1 or any(len(members) >= int(parameter("N_min")) for members in live):
        raise ValueError("I4_UNIMPLEMENTED_MERGE_SPLIT")
