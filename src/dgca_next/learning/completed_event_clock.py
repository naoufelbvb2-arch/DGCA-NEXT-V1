"""Approved C01: immutable close references into the existing event prefix."""

import sqlite3
from collections.abc import Callable
from dataclasses import InitVar, dataclass

from dgca_next.graph.cell import nonnegative_integer
from dgca_next.graph.native_lifecycle import parameter
from dgca_next.learning.settlement import CloseResult

_PERMIT = object()


@dataclass(frozen=True, slots=True)
class CooldownDecision:
    assembly_id: int
    last_close_reference: int | None
    age_completed_events: int | None
    status: str

    @property
    def eligible(self) -> bool:
        return self.status in ("NEVER_EDITED", "COOLDOWN_ELAPSED")


@dataclass(frozen=True, slots=True)
class VerifiedCompletedPrefix:
    exposure_id: int
    prospective_close_serial: int
    prospective_event_clock: int
    historical_prefixes: tuple[tuple[int, int], ...]
    _authority: InitVar[object] = None

    def __post_init__(self, _authority: object) -> None:
        if _authority is not _PERMIT:
            raise ValueError("UNVERIFIED_COMPLETED_EVENT_PREFIX")

    def cooldown(
        self,
        assembly_id: int,
        last_close: int | None,
        *,
        edited_this_end: frozenset[int] = frozenset(),
    ) -> CooldownDecision:
        nonnegative_integer(assembly_id, "assembly_id")
        if assembly_id in edited_this_end:
            return CooldownDecision(assembly_id, last_close, 0, "SAME_END_EDIT_BLOCKED")
        if last_close is None:
            return CooldownDecision(assembly_id, None, None, "NEVER_EDITED")
        nonnegative_integer(last_close, "last_close")
        previous = dict(self.historical_prefixes).get(last_close)
        if previous is None:
            raise ValueError("MISSING_COOLDOWN_CLOCK_PROVENANCE")
        age = self.prospective_event_clock - previous
        if age < 0:
            raise ValueError("INCONSISTENT_COOLDOWN_CLOCK_PROVENANCE")
        return CooldownDecision(
            assembly_id,
            last_close,
            age,
            "COOLDOWN_ELAPSED" if age >= int(parameter("T_c")) else "COOLDOWN_NOT_ELAPSED",
        )


def _verified_completed_prefix(
    connection: sqlite3.Connection,
    result: CloseResult,
    decoder: Callable[[bytes], CloseResult],
    *,
    replay: bool,
) -> VerifiedCompletedPrefix:
    current = connection.execute(
        "SELECT status,next_order,close_serial FROM p01_roots WHERE exposure_id=?",
        (result.exposure_id,),
    ).fetchone()
    if (
        current is None
        or current[0] != ("COMPLETED" if replay else "OPEN")
        or (replay and current[2] != result.close_serial)
        or current[1] < 1
    ):
        raise ValueError("UNVERIFIED_CLOCK_ROOT")
    rows = connection.execute(
        "SELECT exposure_id,close_serial,next_order,close_record FROM p01_roots "
        "WHERE status='COMPLETED' AND close_serial<? ORDER BY close_serial",
        (result.close_serial,),
    ).fetchall()
    prefixes = []
    total = 0
    last_root = -1
    for serial, (root, saved_serial, count, raw) in enumerate(rows, 1):
        close = decoder(raw)
        total += count
        if (
            saved_serial != serial
            or root <= last_root
            or root >= result.exposure_id
            or close.exposure_id != root
            or close.close_serial != serial
            or close.event_clock != total
        ):
            raise ValueError("INCONSISTENT_COOLDOWN_CLOCK_PROVENANCE")
        prefixes.append((serial, total))
        last_root = root
    if len(prefixes) + 1 != result.close_serial or total + current[1] != result.event_clock:
        raise ValueError("INCONSISTENT_PROSPECTIVE_EVENT_PREFIX")
    return VerifiedCompletedPrefix(
        result.exposure_id,
        result.close_serial,
        result.event_clock,
        tuple(prefixes),
        _authority=_PERMIT,
    )
