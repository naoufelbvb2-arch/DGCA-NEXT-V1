"""Typed slot schema; no inherited initialization/recycling heuristic (Core §1.3)."""

from dataclasses import dataclass
from enum import Enum

from dgca_next.contracts import CellAddress, Region


class UnresolvedLatentPolicy(RuntimeError):
    """Production target selection/confirmation window is not specified."""


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

    def __post_init__(self) -> None:
        if type(self.index) is not int or not 0 <= self.index < 24:
            raise ValueError("slot index must be in [0,24)")
        if type(self.category) is not SlotCategory or type(self.permitted_region) is not Region:
            raise ValueError("typed category and region required")
        if type(self.protected) is not bool or type(self.pin_owners) is not frozenset:
            raise ValueError("invalid immutable protection metadata")
        if self.target_id is None:
            if self.protected or self.pin_owners:
                raise ValueError("empty slots cannot be protected or pinned")
        elif CellAddress.from_cell_id(self.target_id).region is not self.permitted_region:
            raise ValueError("target violates slot region")
        for owner in self.pin_owners:
            CellAddress.from_cell_id(owner)

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


def require_latent_policy() -> None:
    raise UnresolvedLatentPolicy(
        "UNRESOLVED_LATENT_POLICY: Core §1.3 names inherited selection and an original "
        "confirmation window; neither RC4.1 spec supplies their complete executable rule"
    )
