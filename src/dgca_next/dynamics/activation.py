"""Exactly two frozen-state passes (Core §5). Pure numeric kernel, not an EVENT."""

from collections.abc import Mapping
from dataclasses import dataclass

from dgca_next.contracts import CellAddress
from dgca_next.dynamics.drive import Drive, aggregate, synchronous_drives
from dgca_next.dynamics.numeric import clip, noisy_or, parameter, support
from dgca_next.dynamics.state import GraphSnapshot, Homeostasis, frozen_numbers


@dataclass(frozen=True, slots=True)
class PassResult:
    raw: Mapping[int, float]
    normalized: Mapping[int, float]
    activity: Mapping[int, float]

    def __post_init__(self) -> None:
        for name in ("raw", "normalized", "activity"):
            object.__setattr__(self, name, frozen_numbers(getattr(self, name)))


@dataclass(frozen=True, slots=True)
class TwoPassResult:
    first: PassResult
    second: PassResult
    emitters: frozenset[int]
    synchronous: tuple[Drive, ...]


def _pass(
    graph: GraphSnapshot,
    homeostasis: Homeostasis,
    previous: Mapping[int, float],
    lanes: tuple[Mapping[int, float], ...],
    gates: Mapping[int, bool],
) -> PassResult:
    ids = graph.committed_ids
    raw = {
        i: noisy_or(lane.get(i, 0.0) for lane in lanes) if gates.get(i, True) else 0.0
        for i in sorted(ids)
    }
    sums: dict[int, float] = {}
    for i, value in raw.items():
        sums[i // 8] = sums.get(i // 8, 0.0) + value
    normalized, activity = {}, {}
    for i in sorted(ids):
        region = CellAddress.from_cell_id(i).region.name
        # All eight logical positions contribute, including uncommitted zeros.
        normalized[i] = raw[i] / (1.0 + parameter(f"beta_{region}") * (sums[i // 8] / 8))
        if i not in homeostasis.gains:
            raise ValueError(f"MISSING_HOMEOSTATIC_GAIN: {i}")
        activity[i] = (
            clip(
                (1.0 - parameter(f"delta_A_{region}")) * support(previous.get(i, 0.0))
                + parameter(f"gamma_A_{region}") * homeostasis.gains[i] * normalized[i]
            )
            if gates.get(i, True)
            else 0.0
        )
    return PassResult(raw, normalized, activity)


def two_pass(
    graph: GraphSnapshot,
    homeostasis: Homeostasis,
    previous: Mapping[int, float],
    X: Mapping[int, float],
    temporal: Mapping[int, float],
    sigma: Mapping[int, float],
    *,
    gates: Mapping[int, bool] | None = None,
) -> TwoPassResult:
    gates = {} if gates is None else gates
    for cell_id, allowed in gates.items():
        CellAddress.from_cell_id(cell_id)
        if type(allowed) is not bool:
            raise ValueError("INVALID_CONTEXT_GATE")
    for lane in (previous, X, temporal, sigma):
        frozen_numbers(lane)
    first = _pass(graph, homeostasis, previous, (X, temporal, sigma), gates)
    emitters = frozenset(
        i for i, a in first.activity.items() if a >= homeostasis.threshold(i, "theta_emit_factor")
    )
    synchronous = synchronous_drives(graph, first.activity, emitters)
    second = _pass(
        graph, homeostasis, previous, (X, temporal, aggregate(synchronous), sigma), gates
    )
    return TwoPassResult(first, second, emitters, synchronous)
