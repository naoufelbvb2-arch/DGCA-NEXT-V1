"""RC4.2 bilateral physical guards; genuine novelty verification is deferred."""

import hashlib
import math
from dataclasses import dataclass, replace
from typing import TYPE_CHECKING, Protocol

from dgca_next.config import load_lab_config
from dgca_next.contracts import CellAddress, EventMode, EventOrigin
from dgca_next.graph.latent import LATENT_POLICY_VERSION, LatentSlot
from dgca_next.graph.policy import (
    FixtureEventSnapshot,
    q6,
    ranked_candidates,
    validate_fixture_event,
)

if TYPE_CHECKING:
    from dgca_next.graph.network import _State

_CONFIG = load_lab_config()


class VerifiedLocalNovelty(Protocol):
    """Future executor authority, not an I1 factory or scalar authorization."""

    @property
    def receiver_id(self) -> int: ...

    @property
    def event(self) -> object: ...

    @property
    def novelty(self) -> float: ...

    @property
    def fixture_only(self) -> bool: ...


@dataclass(frozen=True, slots=True)
class FixtureLocalNovelty:
    """Explicit synthetic arithmetic input. Never accepted by production."""

    event: FixtureEventSnapshot
    receiver_id: int
    pre_input_prediction: float
    fixture_only: bool = True

    def __post_init__(self) -> None:
        if (
            type(self.event) is not FixtureEventSnapshot
            or self.fixture_only is not True
            or type(self.fixture_only) is not bool
        ):
            raise ValueError("I1_FIXTURE_ONLY")
        CellAddress.from_cell_id(self.receiver_id)
        if (
            type(self.pre_input_prediction) is not float
            or not math.isfinite(self.pre_input_prediction)
            or not 0 <= self.pre_input_prediction <= 1
        ):
            raise ValueError("INVALID_PRE_INPUT_PREDICTION")
        if not any(r.cell_id == self.receiver_id for r in self.event.direct_receivers):
            raise ValueError("UNVERIFIED_NOVELTY")

    @property
    def novelty(self) -> float:
        support = next(
            r.direct_support_millionths
            for r in self.event.direct_receivers
            if r.cell_id == self.receiver_id
        )
        x = support / 1_000_000
        return max(0.0, x - min(x, self.pre_input_prediction)) / max(
            x, float(_CONFIG.parameter("eps_p").value)
        )

    @property
    def digest(self) -> str:
        prediction = 0.0 if self.pre_input_prediction == 0 else self.pre_input_prediction
        payload = f"{self.event.digest}:{self.receiver_id}:{prediction.hex()}"
        return hashlib.sha256(payload.encode("ascii")).hexdigest()


@dataclass(frozen=True, slots=True)
class RecyclingRecord:
    exposure_id: int
    event_id: int
    event_order: int
    completed_close_serial: int
    changes: tuple[tuple[int, int, int, int], ...]
    snapshot_digest: str
    novelty_digest: str
    policy_version: str
    reason: str = "RECYCLED"
    fixture_only: bool = True

    def __post_init__(self) -> None:
        from dgca_next.graph.cell import nonnegative_integer

        for name in ("exposure_id", "event_id", "event_order", "completed_close_serial"):
            nonnegative_integer(getattr(self, name), name)
        if (
            type(self.policy_version) is not str
            or self.policy_version != LATENT_POLICY_VERSION
            or self.reason != "RECYCLED"
            or self.fixture_only is not True
        ):
            raise ValueError("INVALID_RECYCLING_RECORD")
        if (
            type(self.changes) is not tuple
            or not 1 <= len(self.changes) <= 2
            or any(type(change) is not tuple or len(change) != 4 for change in self.changes)
            or tuple(sorted(self.changes)) != self.changes
        ):
            raise ValueError("INVALID_BILATERAL_CHANGES")
        for owner, index, old, new in self.changes:
            for cell_id in (owner, old, new):
                CellAddress.from_cell_id(cell_id)
            if type(index) is not int or not 0 <= index < 24 or owner in (old, new) or old == new:
                raise ValueError("INVALID_BILATERAL_CHANGES")
        for digest in (self.snapshot_digest, self.novelty_digest):
            if (
                type(digest) is not str
                or len(digest) != 64
                or any(c not in "0123456789abcdef" for c in digest)
            ):
                raise ValueError("INVALID_SNAPSHOT_DIGEST")


@dataclass(frozen=True, slots=True)
class ProductionRecyclingRecord:
    """Auditable physical replacement; journal replay supplies its authority."""

    exposure_id: int
    event_id: int
    event_order: int
    completed_close_serial: int
    changes: tuple[tuple[int, int, int, int], ...]
    snapshot_digest: str
    novelty_digest: str
    policy_version: str
    receiver_id: int
    x_fixed: int
    prediction: float
    novelty_q6: int
    reason: str = "RECYCLED"
    fixture_only: bool = False

    def __post_init__(self) -> None:
        # Reuse the fixture record's structural checks, not its authority.
        RecyclingRecord(
            self.exposure_id,
            self.event_id,
            self.event_order,
            self.completed_close_serial,
            self.changes,
            self.snapshot_digest,
            self.novelty_digest,
            self.policy_version,
        )
        CellAddress.from_cell_id(self.receiver_id)
        if (
            self.fixture_only is not False
            or self.reason != "RECYCLED"
            or type(self.x_fixed) is not int
            or not 0 < self.x_fixed <= 1_000_000
            or type(self.prediction) is not float
            or not math.isfinite(self.prediction)
            or not 0 <= self.prediction <= 1
            or type(self.novelty_q6) is not int
            or not 0 <= self.novelty_q6 <= 1_000_000
            or self.receiver_id not in {self.changes[0][0], self.changes[0][2]}
        ):
            raise ValueError("INVALID_PRODUCTION_RECYCLING_RECORD")


def completed_close_credit(mode: EventMode, origin: EventOrigin, *, completed: bool) -> int:
    """Pure clock-credit rule, not a root executor or mutable counter."""
    if (
        type(mode) is not EventMode
        or type(origin) is not EventOrigin
        or type(completed) is not bool
    ):
        raise ValueError("INVALID_CLOSE_PROVENANCE")
    return int(completed and mode is EventMode.LEARN and origin is EventOrigin.EXTERNAL_DIRECT)


def bilateral_occurrences(
    state: _State, owner_id: int, slot_index: int
) -> tuple[tuple[int, LatentSlot], ...]:
    CellAddress.from_cell_id(owner_id)
    if type(slot_index) is not int or not 0 <= slot_index < 24:
        raise ValueError("INVALID_SLOT_INDEX")
    slots = state.slots.get(owner_id)
    if slots is None or slots[slot_index].target_id is None:
        raise ValueError("EMPTY_SLOT")
    target = slots[slot_index].target_id
    assert target is not None
    pair = frozenset((owner_id, target))
    occurrences = tuple(
        sorted(
            (
                (source, slot)
                for source, other in ((owner_id, target), (target, owner_id))
                for slot in state.slots.get(source, ())
                if slot.target_id == other
            ),
            key=lambda item: (item[0], item[1].index),
        )
    )
    if any(not slot.recyclable_category for _, slot in occurrences):
        raise ValueError("RECYCLE_BLOCKED_FIXED")
    if any(slot.protected for _, slot in occurrences) or any(
        frozenset((k.source.cell_id, k.target.cell_id)) == pair
        for k in (*state.synapses, *state.reservations)
    ):
        raise ValueError("RECYCLE_BLOCKED_LIVE_OR_PROTECTED")
    if any(slot.pinned for _, slot in occurrences):
        raise ValueError("RECYCLE_BLOCKED_CANDIDATE")
    return occurrences


def plan_fixture_recycling(
    state: _State,
    owner_id: int,
    slot_index: int,
    event: FixtureEventSnapshot | None,
    novelty: FixtureLocalNovelty | None,
) -> tuple[tuple[int, LatentSlot], ...]:
    occurrences = bilateral_occurrences(state, owner_id, slot_index)
    if type(event) is not FixtureEventSnapshot or type(novelty) is not FixtureLocalNovelty:
        raise ValueError("UNVERIFIED_NOVELTY")
    if novelty.event.digest != event.digest or novelty.receiver_id not in {
        owner for owner, _ in occurrences
    } | {slot.target_id for _, slot in occurrences}:
        raise ValueError("UNVERIFIED_NOVELTY")
    if q6(novelty.novelty) < q6(float(_CONFIG.parameter("theta_R").value)):
        raise ValueError("UNVERIFIED_NOVELTY: BELOW_THRESHOLD")
    validate_fixture_event(event, state.cells)
    receiver = state.cells.get(novelty.receiver_id)
    if (
        receiver is None
        or receiver.committed_event is None
        or receiver.committed_event >= event.event_id
    ):
        raise ValueError("UNVERIFIED_NOVELTY: COMMITMENT_TIMING")
    for _, slot in occurrences:
        assigned = slot.assigned_at_completed_close_serial
        if assigned is None or event.completed_external_closes - assigned < int(
            _CONFIG.parameter("W_conf").value
        ):
            raise ValueError("CONFIRMATION_WINDOW_NOT_ELAPSED")
        assert slot.assignment is not None
        if slot.assignment.event_id >= event.event_id:
            raise ValueError("UNVERIFIED_NOVELTY: EVENT_ORDER")
    replacements = []
    for owner, slot in occurrences:
        selected = {owner, slot.target_id} | {
            s.target_id
            for s in state.slots[owner]
            if s.index != slot.index and s.target_id is not None
        }
        target = next(
            (i for i in ranked_candidates(event, slot.permitted_region) if i not in selected), None
        )
        if target is None:
            raise ValueError("NO_RECYCLING_REPLACEMENT")
        replacements.append(
            (
                owner,
                replace(slot, target_id=target, assignment=event.assignment(pending_birth=False)),
            )
        )
    return tuple(replacements)
