"""Evaluator-only PredScore and scratch FULL/CONTROL (Core §9). No readout/generation."""

from collections.abc import Mapping
from dataclasses import dataclass

from dgca_next.contracts import CellAddress
from dgca_next.dynamics.activation import TwoPassResult, two_pass
from dgca_next.dynamics.drive import aggregate
from dgca_next.dynamics.session import RuntimeState, _context_operators, next_drives
from dgca_next.dynamics.state import GraphSnapshot, frozen_numbers


@dataclass(frozen=True, slots=True)
class EvaluationFootprint:
    cell_ids: tuple[int, ...]
    comparable: bool = True
    aliased: bool = False

    def __post_init__(self) -> None:
        if type(self.cell_ids) is not tuple or self.cell_ids != tuple(sorted(set(self.cell_ids))):
            raise ValueError("NONCANONICAL_EVALUATOR_FOOTPRINT")
        for i in self.cell_ids:
            CellAddress.from_cell_id(i)
        if type(self.comparable) is not bool or type(self.aliased) is not bool:
            raise ValueError("INVALID_EVALUATOR_STATUS")


def pred_score(
    graph: GraphSnapshot, state: RuntimeState, outcome: EvaluationFootprint
) -> tuple[str, float | None]:
    if type(outcome) is not EvaluationFootprint:
        raise ValueError("UNRESOLVED_EVALUATOR_FOOTPRINT")
    if not outcome.cell_ids or not outcome.comparable or outcome.aliased:
        return "UNRESOLVED", None
    predictions = aggregate(next_drives(graph, state))
    return "RESOLVED", sum(predictions.get(i, 0.0) for i in outcome.cell_ids) / len(
        outcome.cell_ids
    )


@dataclass(frozen=True, slots=True)
class FullControl:
    full: TwoPassResult
    control: TwoPassResult
    temporal: Mapping[int, float]
    gain: Mapping[int, float]
    eligible_neural_next: frozenset[int]

    def __post_init__(self) -> None:
        object.__setattr__(self, "temporal", frozen_numbers(self.temporal))
        object.__setattr__(self, "gain", frozen_numbers(self.gain))


def full_control(graph: GraphSnapshot, state: RuntimeState) -> FullControl:
    temporal = aggregate(next_drives(graph, state))
    gates, sigma, _ = _context_operators(graph, state, {}, False)
    # Both calls start from exactly the same frozen R/H/W. They run identical
    # normalizer/P_S laws; their derived outputs may differ causally with P_T.
    full = two_pass(graph, state.homeostasis, state.activity, {}, temporal, sigma, gates=gates)
    control = two_pass(graph, state.homeostasis, state.activity, {}, {}, sigma, gates=gates)
    gain = {
        i: max(full.second.activity[i] - control.second.activity[i], 0.0)
        for i in full.second.activity
    }
    eligible = frozenset(i for i, value in gain.items() if value > 0 and temporal.get(i, 0.0) > 0)
    return FullControl(full, control, temporal, gain, eligible)
