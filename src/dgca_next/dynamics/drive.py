"""Qualified directed neural contributions (Core §1.4/§5, LLA §4.1)."""

from collections.abc import Mapping
from dataclasses import dataclass

from dgca_next.contracts import SynapseScope
from dgca_next.dynamics.numeric import SpecBlocked, noisy_or, support
from dgca_next.dynamics.state import GraphSnapshot
from dgca_next.graph import Synapse, SynapseState
from dgca_next.graph.synapse import quality


@dataclass(frozen=True, slots=True)
class Drive:
    source_id: int
    target_id: int
    scope: SynapseScope
    value: float


def contributor_order(synapse: Synapse) -> tuple[int, int, int]:
    key = synapse.key
    return key.source.cell_id, tuple(SynapseScope).index(key.scope), key.target.cell_id


def aggregate(drives: tuple[Drive, ...]) -> dict[int, float]:
    grouped: dict[int, list[float]] = {}
    for drive in drives:
        grouped.setdefault(drive.target_id, []).append(drive.value)
    return {i: noisy_or(values) for i, values in sorted(grouped.items())}


def temporal_drives(
    graph: GraphSnapshot,
    activity: Mapping[int, float],
    frontier: frozenset[int],
    mu: Mapping[int, float],
    contextual_targets: frozenset[int] = frozenset(),
) -> tuple[Drive, ...]:
    drives = []
    for synapse in sorted(graph.synapses(), key=contributor_order):
        key = synapse.key
        source, target = key.source.cell_id, key.target.cell_id
        if key.scope is SynapseScope.ASSOCIATIVE and source in frontier:
            mask = 0.0 if target in contextual_targets else support(mu.get(source, 0.0))
            value = (1.0 - mask) * support(activity.get(source, 0.0)) * quality(synapse)
            if value:
                drives.append(Drive(source, target, key.scope, value))
    return tuple(drives)


def synchronous_drives(
    graph: GraphSnapshot, activity: Mapping[int, float], emitters: frozenset[int]
) -> tuple[Drive, ...]:
    drives = []
    for synapse in sorted(graph.synapses(), key=contributor_order):
        key = synapse.key
        source, target = key.source.cell_id, key.target.cell_id
        if key.scope is not SynapseScope.ASSOCIATIVE and source in emitters:
            if synapse.state is not SynapseState.CONSOLIDATED:
                raise SpecBlocked(
                    "I2-S01: Core §1.4/§5 and LLA §4.1 use live Q; "
                    "I2 contract §3 requires consolidated pass-2 Q: "
                    f"{source}->{target}/{key.scope.value}/{synapse.state.value}"
                )
            value = support(activity[source]) * quality(synapse)
            if value:
                drives.append(Drive(source, target, key.scope, value))
    return tuple(drives)
