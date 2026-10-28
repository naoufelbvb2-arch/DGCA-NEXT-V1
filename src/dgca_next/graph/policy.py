"""Approved RC4.2 §1.3 pure selectors and explicitly synthetic event snapshots.

No real event admission, activation or evidence verification happens here.
"""

import hashlib
import json
import math
import struct
from collections.abc import Mapping
from dataclasses import dataclass, replace
from enum import Enum

from dgca_next.contracts import CellAddress, EventMode, EventOrigin, Region
from dgca_next.graph.cell import Cell, nonnegative_integer
from dgca_next.graph.geometry import microcolumn_neighborhood, microcolumn_of
from dgca_next.graph.latent import LATENT_POLICY_VERSION, LatentSlot, SlotAssignment, empty_slots

TOPOGRAPHIC_SALT = b"DGCA-LATENT-TOP1"
TOPOGRAPHIC_TAG = LATENT_POLICY_VERSION.encode("ascii")


def q6(value: float) -> int:
    """Core §3.1 exact binary64 rational, millionths, ties to even."""
    if type(value) is not float or not math.isfinite(value) or not 0 <= value <= 1:
        raise ValueError("INVALID_FINITE_BINARY64_SUPPORT")
    numerator, denominator = value.as_integer_ratio()
    result, remainder = divmod(numerator * 1_000_000, denominator)
    return result + int(
        2 * remainder > denominator or (2 * remainder == denominator and result % 2)
    )


class CandidateOrigin(Enum):
    EXTERNAL_FRONTIER = "EXTERNAL_FRONTIER"
    DERIVED_EXTERNAL_CONTEXT = "DERIVED_EXTERNAL_CONTEXT"


@dataclass(frozen=True, slots=True)
class FixtureFrontier:
    cell_id: int
    final_activity: float
    origin: CandidateOrigin = CandidateOrigin.EXTERNAL_FRONTIER
    fixture_only: bool = True

    def __post_init__(self) -> None:
        CellAddress.from_cell_id(self.cell_id)
        q6(self.final_activity)
        if type(self.origin) is not CandidateOrigin:
            raise ValueError("FORBIDDEN_CANDIDATE_PROVENANCE")
        if self.fixture_only is not True or type(self.fixture_only) is not bool:
            raise ValueError("I1_FIXTURE_ONLY")


@dataclass(frozen=True, slots=True)
class FixtureReceiver:
    cell_id: int
    direct_support_millionths: int
    fixture_only: bool = True

    def __post_init__(self) -> None:
        CellAddress.from_cell_id(self.cell_id)
        if (
            type(self.direct_support_millionths) is not int
            or not 0 < self.direct_support_millionths <= 1_000_000
        ):
            raise ValueError("INVALID_DIRECT_SUPPORT")
        if self.fixture_only is not True or type(self.fixture_only) is not bool:
            raise ValueError("I1_FIXTURE_ONLY")


@dataclass(frozen=True, slots=True)
class FixtureEventSnapshot:
    exposure_id: int
    event_id: int
    event_order: int
    completed_external_closes: int
    frontier: tuple[FixtureFrontier, ...] = ()
    direct_receivers: tuple[FixtureReceiver, ...] = ()
    birth_ids: frozenset[int] = frozenset()
    mode: EventMode = EventMode.LEARN
    origin: EventOrigin = EventOrigin.EXTERNAL_DIRECT
    fixture_only: bool = True

    def __post_init__(self) -> None:
        for name in ("exposure_id", "event_id", "event_order", "completed_external_closes"):
            nonnegative_integer(getattr(self, name), name)
        if self.fixture_only is not True or type(self.fixture_only) is not bool:
            raise ValueError("I1_FIXTURE_ONLY")
        if self.mode is not EventMode.LEARN or self.origin is not EventOrigin.EXTERNAL_DIRECT:
            raise ValueError("FORBIDDEN_EVENT_PROVENANCE")
        for sequence, cls in (
            (self.frontier, FixtureFrontier),
            (self.direct_receivers, FixtureReceiver),
        ):
            if type(sequence) is not tuple or any(type(item) is not cls for item in sequence):
                raise ValueError("IMMUTABLE_TYPED_CANDIDATES_REQUIRED")
            if len({item.cell_id for item in sequence}) != len(sequence):
                raise ValueError("DUPLICATE_CANDIDATE_ID")
        if type(self.birth_ids) is not frozenset:
            raise ValueError("IMMUTABLE_BIRTH_COHORT_REQUIRED")
        for cell_id in self.birth_ids:
            CellAddress.from_cell_id(cell_id)
        receivers = {r.cell_id for r in self.direct_receivers}
        if not self.birth_ids <= receivers or self.birth_ids & {r.cell_id for r in self.frontier}:
            raise ValueError("INVALID_COBIRTH_PROVENANCE")

    @property
    def digest(self) -> str:
        payload = {
            "exposure": self.exposure_id,
            "event": self.event_id,
            "order": self.event_order,
            "closes": self.completed_external_closes,
            "births": sorted(self.birth_ids),
            "frontier": sorted(
                (
                    r.cell_id,
                    (0.0 if r.final_activity == 0 else r.final_activity).hex(),
                    r.origin.value,
                )
                for r in self.frontier
            ),
            "receivers": sorted(
                (r.cell_id, r.direct_support_millionths) for r in self.direct_receivers
            ),
            "fixture_only": True,
        }
        return hashlib.sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()

    def assignment(self, *, pending_birth: bool) -> SlotAssignment:
        return SlotAssignment(
            self.completed_external_closes,
            self.exposure_id,
            self.event_id,
            self.event_order,
            pending_birth,
            LATENT_POLICY_VERSION,
        )


@dataclass(frozen=True, slots=True)
class InitializationRecord:
    owner_id: int
    snapshot_digest: str
    contextual: bool
    seed_targets: tuple[int, ...]
    assignment: SlotAssignment
    policy_version: str

    def __post_init__(self) -> None:
        CellAddress.from_cell_id(self.owner_id)
        if type(self.policy_version) is not str or self.policy_version != LATENT_POLICY_VERSION:
            raise ValueError("UNSUPPORTED_LATENT_POLICY_VERSION")
        if type(self.contextual) is not bool or type(self.seed_targets) is not tuple:
            raise ValueError("INVALID_INITIALIZATION_RECORD")
        if (
            type(self.snapshot_digest) is not str
            or len(self.snapshot_digest) != 64
            or any(c not in "0123456789abcdef" for c in self.snapshot_digest)
        ):
            raise ValueError("INVALID_SNAPSHOT_DIGEST")
        if type(self.assignment) is not SlotAssignment:
            raise ValueError("INVALID_ASSIGNMENT_METADATA")
        if len(set(self.seed_targets)) != len(self.seed_targets):
            raise ValueError("DUPLICATE_LATENT_TARGET")
        for cell_id in self.seed_targets:
            CellAddress.from_cell_id(cell_id)


def validate_fixture_event(
    event: FixtureEventSnapshot, cells: Mapping[int, Cell], *, births_pending: bool = False
) -> None:
    if type(event) is not FixtureEventSnapshot:
        raise ValueError("UNVERIFIED_EVENT_SNAPSHOT")
    for candidate in event.frontier:
        cell = cells.get(candidate.cell_id)
        if cell is None or cell.committed_event is None or cell.committed_event >= event.event_id:
            raise ValueError("UNVERIFIED_FRONTIER_COMMITMENT")
    if not births_pending:
        for cell_id in event.birth_ids:
            cell = cells.get(cell_id)
            if cell is None or cell.committed_event != event.event_id:
                raise ValueError("UNVERIFIED_BIRTH_COHORT")


def _check_excluded(excluded: frozenset[int]) -> None:
    if type(excluded) is not frozenset:
        raise ValueError("IMMUTABLE_PHYSICAL_EXCLUSIONS_REQUIRED")
    for cell_id in excluded:
        CellAddress.from_cell_id(cell_id)


def local_targets(owner_id: int, excluded: frozenset[int] = frozenset()) -> tuple[int, ...]:
    _check_excluded(excluded)
    own = microcolumn_of(owner_id)
    columns = (own,) + tuple(c for c in microcolumn_neighborhood(owner_id, 1) if c != own)
    selected = set(excluded) | {owner_id}
    result: list[int] = []
    while len(result) < 6:
        advanced = False
        for column in columns:
            target = next((i for i in column.cell_ids() if i not in selected), None)
            if target is not None:
                selected.add(target)
                result.append(target)
                advanced = True
                if len(result) == 6:
                    break
        if not advanced:
            raise ValueError("NO_LOCAL_TARGET")
    return tuple(result)


def topographic_base(owner_id: int, region: Region, ordinal: int) -> int:
    address = CellAddress.from_cell_id(owner_id)
    if (
        type(region) is not Region
        or region is address.region
        or type(ordinal) is not int
        or ordinal not in (0, 1, 2)
    ):
        raise ValueError("INVALID_TOPOGRAPHIC_ADDRESS")
    payload = (
        TOPOGRAPHIC_TAG
        + b"\0"
        + TOPOGRAPHIC_SALT
        + struct.pack(">IBB", owner_id, region.value, ordinal)
    )
    return int.from_bytes(hashlib.sha256(payload).digest()[:8], "big") % 4096


def topographic_targets(owner_id: int, excluded: frozenset[int] = frozenset()) -> tuple[int, ...]:
    _check_excluded(excluded)
    owner = CellAddress.from_cell_id(owner_id)
    selected = set(excluded) | {owner_id}
    result: list[int] = []
    for region in Region:
        if region is owner.region:
            continue
        for ordinal in range(3):
            base = topographic_base(owner_id, region, ordinal)
            target = next(
                (
                    4096 * region.value + (base + probe) % 4096
                    for probe in range(4096)
                    if 4096 * region.value + (base + probe) % 4096 not in selected
                ),
                None,
            )
            if target is None:
                raise ValueError("NO_TOPOGRAPHIC_TARGET")
            selected.add(target)
            result.append(target)
    return tuple(result)


def ranked_candidates(event: FixtureEventSnapshot, region: Region) -> tuple[int, ...]:
    if type(event) is not FixtureEventSnapshot or type(region) is not Region:
        raise ValueError("UNVERIFIED_EVENT_SNAPSHOT")
    scores = {candidate.cell_id: q6(candidate.final_activity) for candidate in event.frontier}
    scores.update(
        {
            r.cell_id: q6(r.direct_support_millionths / 1_000_000)
            for r in event.direct_receivers
            if r.cell_id in event.birth_ids
        }
    )
    return tuple(
        sorted(
            (i for i in scores if CellAddress.from_cell_id(i).region is region),
            key=lambda i: (-scores[i], i),
        )
    )


def fill_coactive(
    owner_id: int,
    slots: tuple[LatentSlot, ...],
    event: FixtureEventSnapshot,
    *,
    pending_birth: bool,
) -> tuple[LatentSlot, ...]:
    selected = {owner_id} | {s.target_id for s in slots if s.target_id is not None}
    result = list(slots)
    for slot in slots:
        if not slot.recyclable_category or slot.target_id is not None:
            continue
        target = next(
            (i for i in ranked_candidates(event, slot.permitted_region) if i not in selected), None
        )
        if target is not None:
            selected.add(target)
            result[slot.index] = replace(
                slot, target_id=target, assignment=event.assignment(pending_birth=pending_birth)
            )
    return tuple(result)


def initialize_layout(
    owner_id: int,
    event: FixtureEventSnapshot,
    *,
    pinned_slots: tuple[LatentSlot, ...] | None = None,
    contextual: bool = False,
) -> tuple[LatentSlot, ...]:
    owner = CellAddress.from_cell_id(owner_id)
    if type(event) is not FixtureEventSnapshot or (
        not contextual and owner_id not in event.birth_ids
    ):
        raise ValueError("UNVERIFIED_BIRTH_COHORT")
    if contextual and owner_id in event.birth_ids:
        raise ValueError("CONTEXT_IS_NOT_SENSORY_BIRTH")
    slots = empty_slots(owner.region) if pinned_slots is None else pinned_slots
    if type(slots) is not tuple or len(slots) != 24:
        raise ValueError("INVALID_SLOT_COUNT")
    selected = {owner_id}
    for slot, schema in zip(slots, empty_slots(owner.region), strict=True):
        if (slot.index, slot.category, slot.permitted_region) != (
            schema.index,
            schema.category,
            schema.permitted_region,
        ):
            raise ValueError("INVALID_SLOT_CATEGORY_REGION")
        if slot.target_id is not None:
            if (
                not contextual
                or not slot.recyclable_category
                or not slot.pinned
                or slot.target_id in selected
            ):
                raise ValueError("INVALID_CONTEXT_PIN")
            selected.add(slot.target_id)
    if contextual and not 2 <= len(selected) - 1 <= 6:
        raise ValueError("INVALID_CONTEXT_PIN_COUNT")
    fixed_local = local_targets(owner_id, frozenset(selected))
    selected.update(fixed_local)
    fixed_topographic = topographic_targets(owner_id, frozenset(selected))
    result = list(slots)
    assignment = event.assignment(pending_birth=not contextual)
    for slot in slots:
        if slot.target_id is not None:
            result[slot.index] = replace(slot, assignment=assignment)
    for index, target in zip(
        (*range(6, 12), *range(18, 24)), fixed_local + fixed_topographic, strict=True
    ):
        result[index] = replace(result[index], target_id=target, assignment=assignment)
    return fill_coactive(owner_id, tuple(result), event, pending_birth=not contextual)
