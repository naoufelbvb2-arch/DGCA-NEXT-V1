"""Minimal physical schemas and ownership boundaries (Core §§1, 3.1, 4, 6.1, 9–11).

The opaque state envelopes declare ownership only. They do not define a graph,
runtime, adaptation implementation, checkpoint format, or evidence validator.
"""

from dataclasses import dataclass
from enum import Enum
from typing import ClassVar


def _integer(value: int, name: str, lower: int, upper: int | None = None) -> None:
    if type(value) is not int or value < lower or (upper is not None and value > upper):
        raise ValueError(f"invalid {name}: {value!r}")


class Region(Enum):
    """Core §3.1 region bytes; Core §1.1 shape."""

    VISION = 0
    AUDIO = 1
    LANGUAGE = 2


@dataclass(frozen=True, slots=True)
class CellAddress:
    """Physical identity only; Core §§1.1, 3.1."""

    region: Region
    mc_row: int
    mc_col: int
    slot: int

    def __post_init__(self) -> None:
        if type(self.region) is not Region:
            raise ValueError("region must be a Region")
        _integer(self.mc_row, "mc_row", 0, 31)
        _integer(self.mc_col, "mc_col", 0, 15)
        _integer(self.slot, "slot", 0, 7)

    @property
    def cell_id(self) -> int:
        return 4096 * self.region.value + (self.mc_row * 16 + self.mc_col) * 8 + self.slot

    @classmethod
    def from_cell_id(cls, cell_id: int) -> CellAddress:
        _integer(cell_id, "cell_id", 0, 12287)
        region, local = divmod(cell_id, 4096)
        column, slot = divmod(local, 8)
        row, col = divmod(column, 16)
        return cls(Region(region), row, col, slot)

    def to_bytes(self) -> bytes:
        """I0 address record: tag=1, version=1, u32-BE length, four u8 fields.

        Field order: region, mc_row, mc_col, slot. Administrative tag/version;
        not a scientific parameter or a future W/R/H serialization schema.
        Envelope follows Core §3.1.
        """
        return b"\x01\x01\x00\x00\x00\x04" + bytes(
            (self.region.value, self.mc_row, self.mc_col, self.slot)
        )

    @classmethod
    def from_bytes(cls, record: bytes) -> CellAddress:
        if type(record) is not bytes or len(record) != 10 or record[:6] != b"\1\1\0\0\0\4":
            raise ValueError("unsupported or malformed I0 address record")
        return cls(Region(record[6]), record[7], record[8], record[9])


class SynapseScope(Enum):
    """Declaration order is the canonical scope order (Core §§1.4, 3.1)."""

    LOCAL = "LOCAL"
    CROSS_TERRITORY = "CROSS_TERRITORY"
    ASSOCIATIVE = "ASSOCIATIVE"


@dataclass(frozen=True, slots=True)
class SynapseKey:
    """Directed structural key, without strengths, evidence, or learning laws."""

    source: CellAddress
    target: CellAddress
    scope: SynapseScope

    def __post_init__(self) -> None:
        if type(self.source) is not CellAddress or type(self.target) is not CellAddress:
            raise ValueError("synapse endpoints must be CellAddress values")
        if type(self.scope) is not SynapseScope:
            raise ValueError("scope must be a SynapseScope")
        if self.source == self.target:
            raise ValueError("self-links are forbidden")
        same_region = self.source.region is self.target.region
        if self.scope is SynapseScope.LOCAL and not same_region:
            raise ValueError("LOCAL requires the same region")
        if self.scope is SynapseScope.CROSS_TERRITORY and same_region:
            raise ValueError("CROSS_TERRITORY requires distinct regions")

    def validate_delta(self, delta: int) -> None:
        """Reject illegal scope/time pairs; never clamp (Core §1.4, LLA §4.1)."""
        expected = 1 if self.scope is SynapseScope.ASSOCIATIVE else 0
        _integer(delta, "delta", expected, expected)


class EventMode(Enum):
    LEARN = "LEARN"
    REPLAY = "REPLAY"
    RETRIEVE = "RETRIEVE"
    GENERATE = "GENERATE"


class EventOrigin(Enum):
    """Event origins, distinct from per-cell contribution lanes (Core §6.1).

    REPLAY_RECALLED names LLA §4.1's internally recalled prior-root event.
    It is an I0 administrative spelling, not an additional scientific mode.
    """

    EXTERNAL_DIRECT = "EXTERNAL_DIRECT"
    REPLAY_RECALLED = "REPLAY_RECALLED"
    READ_ONLY_OBSERVED = "READ_ONLY_OBSERVED"
    INTERNAL_SELECTED = "INTERNAL_SELECTED"


@dataclass(frozen=True, slots=True)
class EventProvenance:
    """Input shape only: no claim of verified witnesses or root lifecycle.

    LEARN represents the genuine external exposure interface (LLA §7).
    Replay identifies its source root without opening an exposure. Read-only
    observations/selected events identify a session, never a training root.
    Cross-event continuity, monotonic roots and causality need a future engine.
    """

    mode: EventMode
    origin: EventOrigin
    event_order: int
    exposure_id: int | None = None
    session_id: int | None = None
    replay_source_exposure_id: int | None = None

    def __post_init__(self) -> None:
        if type(self.mode) is not EventMode or type(self.origin) is not EventOrigin:
            raise ValueError("mode and origin must be typed enum values")
        _integer(self.event_order, "event_order", 0)
        # The specs require ordered nonrecycled IDs, but prescribe no initial ID.
        for name in ("exposure_id", "session_id", "replay_source_exposure_id"):
            value = getattr(self, name)
            if value is not None:
                _integer(value, name, 0)
        match self.mode:
            case EventMode.LEARN:
                valid = (
                    self.origin is EventOrigin.EXTERNAL_DIRECT
                    and self.exposure_id is not None
                    and self.session_id is None
                    and self.replay_source_exposure_id is None
                )
            case EventMode.REPLAY:
                valid = (
                    self.origin is EventOrigin.REPLAY_RECALLED
                    and self.replay_source_exposure_id is not None
                    and self.exposure_id is None
                    and self.session_id is None
                )
            case EventMode.RETRIEVE | EventMode.GENERATE:
                origins = {EventOrigin.READ_ONLY_OBSERVED}
                if self.mode is EventMode.GENERATE:
                    origins.add(EventOrigin.INTERNAL_SELECTED)
                valid = (
                    self.origin in origins
                    and self.session_id is not None
                    and self.exposure_id is None
                    and self.replay_source_exposure_id is None
                )
        if not valid:
            raise ValueError("invalid mode/origin/root/session combination")


class StatePartition(Enum):
    W = "W"
    R = "R"
    H_SLOW = "H_slow"


@dataclass(frozen=True, slots=True)
class W:
    """Owned immutable snapshot of persistent graph/governance data; Core §4."""

    snapshot: bytes
    partition: ClassVar[StatePartition] = StatePartition.W

    def __post_init__(self) -> None:
        if type(self.snapshot) is not bytes:
            raise ValueError("W requires immutable snapshot bytes")


@dataclass(frozen=True, slots=True)
class R:
    """Owned snapshot of ephemeral activity/witness/staging data; Core §§4, 11."""

    snapshot: bytes
    partition: ClassVar[StatePartition] = StatePartition.R

    def __post_init__(self) -> None:
        if type(self.snapshot) is not bytes:
            raise ValueError("R requires immutable snapshot bytes")


@dataclass(frozen=True, slots=True)
class HSlow:
    """Owned snapshot of g/r_bar/threshold/region EMA data; Core §4."""

    snapshot: bytes
    partition: ClassVar[StatePartition] = StatePartition.H_SLOW

    def __post_init__(self) -> None:
        if type(self.snapshot) is not bytes:
            raise ValueError("H_slow requires immutable snapshot bytes")


@dataclass(frozen=True, slots=True)
class ReadOnlyState:
    """Read-only boundary: exposes no writable W/H_slow or caller R reference.

    Immutable opaque snapshots prevent container aliasing. No operation that
    advances scratch R is supplied by I0; no arbitrary mutable payload accepted.
    """

    w: W
    h_slow: HSlow

    def __post_init__(self) -> None:
        if type(self.w) is not W or type(self.h_slow) is not HSlow:
            raise ValueError("read-only state requires distinct W and HSlow envelopes")
