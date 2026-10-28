"""Typed physical contributions, distinct from training/evidence authority."""

from dataclasses import dataclass
from enum import Enum

from dgca_next.contracts import CellAddress
from dgca_next.dynamics.numeric import support


class SourceKind(Enum):
    EXTERNAL_DIRECT = "EXTERNAL_DIRECT"
    READ_ONLY_OBSERVED = "READ_ONLY_OBSERVED"
    INTERNAL_SELECTED = "INTERNAL_SELECTED"
    DERIVED_EXTERNAL_CONTEXT = "DERIVED_EXTERNAL_CONTEXT"
    DERIVED_RUNTIME_CONTEXT = "DERIVED_RUNTIME_CONTEXT"


class Lane(Enum):
    DIRECT_OBSERVED = "DIRECT_OBSERVED"
    SPATIALLY_COMPLETED = "SPATIALLY_COMPLETED"
    PREDICTED = "PREDICTED"
    RESIDUAL = "RESIDUAL"
    ATTRACTOR = "ATTRACTOR"
    CONTEXT_MATCHED = "CONTEXT_MATCHED"


@dataclass(frozen=True, slots=True)
class Contribution:
    target_id: int
    source_id: int | None
    event_order: int
    lane: Lane
    value: float
    session_id: int
    origin: SourceKind

    def __post_init__(self) -> None:
        CellAddress.from_cell_id(self.target_id)
        if self.source_id is not None:
            CellAddress.from_cell_id(self.source_id)
        if type(self.event_order) is not int or self.event_order < 0:
            raise ValueError("INVALID_EVENT_ORDER")
        if type(self.session_id) is not int or self.session_id < 0:
            raise ValueError("INVALID_SESSION_ID")
        if type(self.lane) is not Lane or type(self.origin) is not SourceKind:
            raise ValueError("UNVERIFIED_PROVENANCE")
        support(self.value)


@dataclass(frozen=True, slots=True)
class RuntimeSupport:
    cell_id: int
    value: float
    kind: SourceKind
    session_id: int
    event_order: int
    bundle_digest: str
    depth: int = 0
    binding_digest: str | None = None
    parents: tuple[tuple[int, int, str], ...] = ()

    def __post_init__(self) -> None:
        CellAddress.from_cell_id(self.cell_id)
        support(self.value)
        if type(self.kind) is not SourceKind or self.kind not in (
            SourceKind.READ_ONLY_OBSERVED,
            SourceKind.DERIVED_RUNTIME_CONTEXT,
        ):
            raise ValueError("I2_HAS_NO_EXTERNAL_OR_INTERNAL_WITNESS_PRODUCER")
        if (
            type(self.parents) is not tuple
            or type(self.depth) is not int
            or not 0 <= self.depth <= 8
        ):
            raise ValueError("DERIVED_PROVENANCE_UNVERIFIED")
        if self.kind is SourceKind.READ_ONLY_OBSERVED and (
            self.depth or self.parents or self.binding_digest
        ):
            raise ValueError("DIRECT_SOURCE_HAS_CONTEXT_METADATA")
        if self.kind is SourceKind.DERIVED_RUNTIME_CONTEXT and (
            not self.parents or not self.binding_digest or not self.depth
        ):
            raise ValueError("DERIVED_PROVENANCE_UNVERIFIED")
