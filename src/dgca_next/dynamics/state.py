"""Immutable snapshots over existing I1 records. Not a persistence/root executor."""

from collections.abc import Mapping
from dataclasses import dataclass, field
from types import MappingProxyType

from dgca_next.contracts import CellAddress, Region, SynapseKey
from dgca_next.dynamics.numeric import finite, parameter, support
from dgca_next.graph import SparseNetwork, Synapse
from dgca_next.graph.cell import Cell
from dgca_next.graph.latent import LatentSlot
from dgca_next.graph.network import _eligible, _slots, _State


def frozen_numbers(values: Mapping[int, float]) -> Mapping[int, float]:
    result = {}
    for cell_id, value in sorted(values.items()):
        CellAddress.from_cell_id(cell_id)
        result[cell_id] = support(value)
    return MappingProxyType(result)


@dataclass(frozen=True, slots=True)
class GraphSnapshot:
    """One immutable I1 state pointer, never a duplicate graph/cell representation."""

    _state: _State
    structural_hash: str

    @classmethod
    def capture(cls, network: SparseNetwork) -> GraphSnapshot:
        if type(network) is not SparseNetwork:
            raise ValueError("INVALID_GRAPH")
        network.validate_graph()
        return cls(network._state, network.structural_hash)

    @property
    def committed_ids(self) -> frozenset[int]:
        return frozenset(self._state.cells)

    def cells(self) -> tuple[Cell, ...]:
        return tuple(self._state.cells[i] for i in sorted(self._state.cells))

    def synapses(self) -> tuple[Synapse, ...]:
        return tuple(self._state.synapses.values())

    def synapse(self, key: SynapseKey) -> Synapse | None:
        return self._state.synapses.get(key)

    def eligible(self, source: int, target: int) -> bool:
        return _eligible(self._state, source, target)

    def slots(self, owner: int) -> tuple[LatentSlot, ...]:
        return _slots(self._state, owner)

    def claimants(self, key: SynapseKey) -> frozenset[int]:
        return self._state.reservations.get(key, frozenset())

    def validate(self) -> None:
        """Independently audit the frozen I1 state and its diagnostic identity."""
        network = SparseNetwork()
        network._state = self._state
        network.validate_graph()
        if network.structural_hash != self.structural_hash:
            raise ValueError("UNVERIFIED_GRAPH_SNAPSHOT")


@dataclass(frozen=True, slots=True)
class Homeostasis:
    """Sparse explicit H; missing gains and adaptive thresholds fail closed.

    This snapshot requires explicit values. RC4.4 production defaults must be
    materialized through the separate versioned sparse LANGUAGE profile.
    uniform_language() remains a synthetic I2 comparator, not that profile.
    """

    gains: Mapping[int, float]
    rates: Mapping[int, float] = field(default_factory=dict)
    thresholds: Mapping[Region, float] = field(default_factory=dict)
    region_rates: Mapping[Region, float] = field(default_factory=dict)

    def __post_init__(self) -> None:
        gains = {}
        for cell_id, value in sorted(self.gains.items()):
            CellAddress.from_cell_id(cell_id)
            if not parameter("g_min") <= finite(value) <= parameter("g_max"):
                raise ValueError("INVALID_HOMEOSTATIC_GAIN")
            gains[cell_id] = value
        object.__setattr__(self, "gains", MappingProxyType(gains))
        object.__setattr__(self, "rates", frozen_numbers(self.rates))
        for name in ("thresholds", "region_rates"):
            values = dict(getattr(self, name))
            for region, value in values.items():
                if type(region) is not Region:
                    raise ValueError("INVALID_HOMEOSTATIC_REGION")
                support(value)
                if name == "thresholds" and not parameter("theta_min") <= value <= parameter(
                    "theta_max"
                ):
                    raise ValueError("INVALID_THRESHOLD")
            object.__setattr__(self, name, MappingProxyType(values))

    @classmethod
    def uniform_language(cls, cell_ids: frozenset[int]) -> Homeostasis:
        """Explicit synthetic fixture, not invented scientific H initialization."""
        return cls(
            {i: 1.0 for i in cell_ids},
            {i: 0.0 for i in cell_ids},
            {Region.LANGUAGE: parameter("theta_active_init_LANGUAGE")},
            {Region.LANGUAGE: 0.0},
        )

    def threshold(self, cell_id: int, factor: str | None = None) -> float:
        region = CellAddress.from_cell_id(cell_id).region
        if region is not Region.LANGUAGE:
            from dgca_next.dynamics.numeric import SpecBlocked

            raise SpecBlocked(f"UNRESOLVED_INITIAL_THRESHOLD: {region.name}")
        if region not in self.thresholds:
            raise ValueError("MISSING_ADAPTIVE_THRESHOLD")
        return self.thresholds[region] * (parameter(factor) if factor else 1.0)
