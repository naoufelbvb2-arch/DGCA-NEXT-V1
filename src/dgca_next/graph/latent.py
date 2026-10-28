"""Typed slot schema and assignment metadata (Core RC4.2 §1.3)."""

from dataclasses import dataclass
from enum import Enum

from dgca_next.contracts import CellAddress, Region
from dgca_next.graph.cell import ProductionAdmission, nonnegative_integer

LATENT_POLICY_VERSION = "DGCA-LATENT-TOPO-V1"


class UnresolvedLatentPolicy(RuntimeError):
    """Legacy exception retained for callers of the historical RC4.1 API."""


@dataclass(frozen=True, slots=True)
class SlotAssignment:
    completed_close_serial: int
    exposure_id: int
    event_id: int
    event_order: int
    pending_birth: bool
    policy_version: str
    fixture_only: bool = True
    admission: ProductionAdmission | None = None

    def __post_init__(self) -> None:
        for name in ("completed_close_serial", "exposure_id", "event_id", "event_order"):
            nonnegative_integer(getattr(self, name), name)
        if type(self.pending_birth) is not bool or type(self.fixture_only) is not bool:
            raise ValueError("INVALID_FIXTURE_ASSIGNMENT")
        if self.fixture_only and self.admission is not None:
            raise ValueError("FIXTURE_ADMISSION_FORBIDDEN")
        if not self.fixture_only and (
            type(self.admission) is not ProductionAdmission
            or (self.exposure_id, self.event_id, self.event_order)
            != (self.admission.exposure_id, self.admission.event_id, self.admission.event_order)
        ):
            raise ValueError("PRODUCTION_ADMISSION_REQUIRED")
        if type(self.policy_version) is not str or self.policy_version != LATENT_POLICY_VERSION:
            raise ValueError("UNSUPPORTED_LATENT_POLICY_VERSION")


class SlotCategory(Enum):
    COACTIVE_INTRA = "COACTIVE_INTRA"
    LOCAL = "LOCAL"
    COACTIVE_INTER = "COACTIVE_INTER"
    TOPOGRAPHIC = "TOPOGRAPHIC"


@dataclass(frozen=True, slots=True)
class LatentSlot:
    """Administrative index layout; target region quotas follow Core §1.3.

    0–5 intra, 6–11 local, 12–17 inter, 18–23 topographic. Cross groups
    allocate 3 positions per other region in region-byte order. This numbering
    selects no target and introduces no wiring policy.
    """

    index: int
    category: SlotCategory
    permitted_region: Region
    target_id: int | None = None
    protected: bool = False
    pin_owners: frozenset[int] = frozenset()
    assignment: SlotAssignment | None = None

    def __post_init__(self) -> None:
        if type(self.index) is not int or not 0 <= self.index < 24:
            raise ValueError("slot index must be in [0,24)")
        if type(self.category) is not SlotCategory or type(self.permitted_region) is not Region:
            raise ValueError("typed category and region required")
        if type(self.protected) is not bool or type(self.pin_owners) is not frozenset:
            raise ValueError("invalid immutable protection metadata")
        if self.target_id is None:
            if self.protected or self.pin_owners or self.assignment is not None:
                raise ValueError("empty slots cannot have protection or assignment metadata")
        elif CellAddress.from_cell_id(self.target_id).region is not self.permitted_region:
            raise ValueError("target violates slot region")
        for owner in self.pin_owners:
            CellAddress.from_cell_id(owner)
        if self.assignment is not None and type(self.assignment) is not SlotAssignment:
            raise ValueError("INVALID_ASSIGNMENT_METADATA")

    @property
    def assigned_at_completed_close_serial(self) -> int | None:
        return self.assignment.completed_close_serial if self.assignment is not None else None

    @property
    def recyclable_category(self) -> bool:
        return self.category in (SlotCategory.COACTIVE_INTRA, SlotCategory.COACTIVE_INTER)

    @property
    def pinned(self) -> bool:
        return bool(self.pin_owners)


def empty_slots(region: Region) -> tuple[LatentSlot, ...]:
    if type(region) is not Region:
        raise ValueError("region must be Region")
    other = tuple(r for r in Region if r is not region)
    return tuple(
        LatentSlot(
            index,
            SlotCategory.COACTIVE_INTRA
            if index < 6
            else SlotCategory.LOCAL
            if index < 12
            else SlotCategory.COACTIVE_INTER
            if index < 18
            else SlotCategory.TOPOGRAPHIC,
            region if index < 12 else other[((index - 12) % 6) // 3],
        )
        for index in range(24)
    )
