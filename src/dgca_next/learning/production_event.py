"""Immutable, serialized production event observations, not evidence updates."""

import hashlib
import math
from dataclasses import InitVar, dataclass

from dgca_next.config import load_lab_config
from dgca_next.contracts import EventMode, EventOrigin, EventProvenance
from dgca_next.graph.latent import LATENT_POLICY_VERSION
from dgca_next.integrity import EXPECTED_SPECS
from dgca_next.learning.homeostasis_profile import PROFILE_VERSION
from dgca_next.peripheral.sic import SICProjection, project
from dgca_next.persistence.binary_records import decode_record, encode_record

_TAG = 0x45
_VERSION = 2
_NUMERIC_FIELDS = (
    "previous",
    "pass1_raw",
    "pass1_normalized",
    "pass1",
    "final_raw",
    "final_normalized",
    "final",
    "temporal",
    "synchronous",
)
_PERMIT = object()
SALT_HASH = hashlib.sha256(
    b"".join(
        bytes.fromhex(str(load_lab_config().parameter(f"sic_salt_{i}").value)) for i in range(4)
    )
).hexdigest()


def _numbers(values: dict[int, float]) -> list[list[object]]:
    result: list[list[object]] = []
    for key, value in sorted(values.items()):
        if (
            type(key) is not int
            or not 0 <= key < 12288
            or type(value) is not float
            or not math.isfinite(value)
            or not 0 <= value <= 1
        ):
            raise ValueError("INVALID_EVENT_NUMERIC_TRACE")
        result.append([key, (0.0 if value == 0.0 else value).hex()])
    return result


@dataclass(frozen=True, slots=True)
class ExternalEventObservation:
    exposure_id: int
    event_id: int
    event_order: int
    digest: str
    X_fixed: tuple[tuple[int, int], ...]
    pre_committed: tuple[int, ...]
    pre_w_hash: str
    pre_h_hash: str
    previous: tuple[tuple[int, float], ...]
    pass1_raw: tuple[tuple[int, float], ...]
    pass1_normalized: tuple[tuple[int, float], ...]
    pass1: tuple[tuple[int, float], ...]
    final_raw: tuple[tuple[int, float], ...]
    final_normalized: tuple[tuple[int, float], ...]
    final: tuple[tuple[int, float], ...]
    temporal: tuple[tuple[int, float], ...]
    synchronous: tuple[tuple[int, float], ...]
    emitters: tuple[int, ...]
    learning_frontier: tuple[int, ...]
    frontier: tuple[int, ...]
    born: tuple[int, ...]
    deferred: tuple[int, ...]
    boundary: bool
    raw: bytes
    config_hash: str
    core_hash: str
    lla_hash: str
    salt_hash: str
    h_profile_version: str
    origin: EventOrigin = EventOrigin.EXTERNAL_DIRECT
    mode: EventMode = EventMode.LEARN
    fixture_only: bool = False
    _authority: InitVar[object] = None

    def __post_init__(self, _authority: object) -> None:
        if _authority is not _PERMIT:
            raise ValueError("UNVERIFIED_EVENT_CONSTRUCTION")

    @property
    def provenance(self) -> EventProvenance:
        return EventProvenance(
            self.mode, self.origin, self.event_order, exposure_id=self.exposure_id
        )


def encode_event(payload: dict[str, object]) -> bytes:
    packed = dict(payload)
    for name in _NUMERIC_FIELDS:
        rows = payload[name]
        if type(rows) is not list:
            raise ValueError("INVALID_EVENT_NUMERIC_TRACE")
        values: dict[int, float] = {}
        for row in rows:
            if (
                type(row) is not list
                or len(row) != 2
                or type(row[0]) is not int
                or type(row[1]) is not str
            ):
                raise ValueError("INVALID_EVENT_NUMERIC_TRACE")
            values[row[0]] = float.fromhex(row[1])
        if _numbers(values) != rows:
            raise ValueError("NONCANONICAL_EVENT_NUMBERS")
        packed[name] = [[key, value] for key, value in sorted(values.items())]
    return encode_record(_TAG, _VERSION, packed)


def decode_event(
    raw: bytes, *, _verified_projection: SICProjection | None = None
) -> ExternalEventObservation:
    try:
        doc = decode_record(raw, _TAG, _VERSION)
        expected = {
            "exposure",
            "event",
            "order",
            "digest",
            "features",
            "salience",
            "x",
            "pre",
            "pre_w",
            "pre_h",
            "previous",
            "pass1_raw",
            "pass1_normalized",
            "pass1",
            "final_raw",
            "final_normalized",
            "final",
            "temporal",
            "synchronous",
            "emitters",
            "learning_frontier",
            "frontier",
            "born",
            "deferred",
            "boundary",
            "origin",
            "mode",
            "config",
            "core",
            "lla",
            "latent",
            "salt_hash",
            "h_profile",
        }
        if type(doc) is not dict or set(doc) != expected:
            raise ValueError("NONCANONICAL_EVENT")
        for name in _NUMERIC_FIELDS:
            rows = doc[name]
            if type(rows) is not list:
                raise ValueError("INVALID_EVENT_NUMERIC_TRACE")
            converted = []
            for row in rows:
                if (
                    type(row) is not list
                    or len(row) != 2
                    or type(row[0]) is not int
                    or type(row[1]) is not float
                ):
                    raise ValueError("INVALID_EVENT_NUMERIC_TRACE")
                converted.append([row[0], row[1].hex()])
            doc[name] = converted
        if encode_event(doc) != raw:
            raise ValueError("NONCANONICAL_EVENT")
        for name in ("exposure", "event", "order", "salience"):
            if type(doc[name]) is not int or doc[name] < 0:
                raise ValueError("INVALID_EVENT_ID")
        if (
            type(doc["boundary"]) is not bool
            or doc["origin"] != "EXTERNAL_DIRECT"
            or doc["mode"] != "LEARN"
        ):
            raise ValueError("INVALID_EVENT_ORIGIN")
        if (
            doc["config"],
            doc["core"],
            doc["lla"],
            doc["latent"],
            doc["salt_hash"],
            doc["h_profile"],
        ) != (
            load_lab_config().sha256,
            EXPECTED_SPECS[0][1],
            EXPECTED_SPECS[1][1],
            LATENT_POLICY_VERSION,
            SALT_HASH,
            PROFILE_VERSION,
        ):
            raise ValueError("EVENT_SOURCE_IDENTITY_MISMATCH")
        features = []
        for row in doc["features"]:
            if (
                type(row) is not list
                or len(row) != 2
                or type(row[0]) is not str
                or type(row[1]) is not int
                or not 0 <= row[1] <= 1_000_000
            ):
                raise ValueError("INVALID_EVENT_FEATURE")
            features.append(
                (
                    bytes.fromhex(row[0]).decode("utf-8"),
                    f"{row[1] // 1_000_000}.{row[1] % 1_000_000:06d}",
                )
            )
        sal = doc["salience"]
        projection = (
            project(tuple(features), salience=f"{sal // 1_000_000}.{sal % 1_000_000:06d}")
            if _verified_projection is None
            else _verified_projection
        )
        if (
            type(projection) is not SICProjection
            or [[feature.hex(), value] for feature, value in projection.input_features]
            != doc["features"]
            or projection.salience_fixed != sal
        ):
            raise ValueError("EVENT_PROJECTION_MISMATCH")
        if projection.digest != doc["digest"] or [list(x) for x in projection.X_fixed] != doc["x"]:
            raise ValueError("EVENT_PROJECTION_MISMATCH")
        for name in ("pre_w", "pre_h"):
            if (
                type(doc[name]) is not str
                or len(doc[name]) != 64
                or any(c not in "0123456789abcdef" for c in doc[name])
            ):
                raise ValueError("INVALID_EVENT_HASH")

        def ids(name: str) -> tuple[int, ...]:
            values = doc[name]
            if (
                type(values) is not list
                or any(type(i) is not int or not 0 <= i < 12288 for i in values)
                or values != sorted(set(values))
            ):
                raise ValueError("INVALID_EVENT_IDS")
            return tuple(values)

        def numeric(name: str) -> tuple[tuple[int, float], ...]:
            rows = doc[name]
            if type(rows) is not list:
                raise ValueError("INVALID_EVENT_NUMERIC_TRACE")
            values = {}
            for row in rows:
                if (
                    type(row) is not list
                    or len(row) != 2
                    or type(row[0]) is not int
                    or type(row[1]) is not str
                ):
                    raise ValueError("INVALID_EVENT_NUMERIC_TRACE")
                values[row[0]] = float.fromhex(row[1])
            if _numbers(values) != rows:
                raise ValueError("NONCANONICAL_EVENT_NUMBERS")
            return tuple(values.items())

        return ExternalEventObservation(
            doc["exposure"],
            doc["event"],
            doc["order"],
            doc["digest"],
            projection.X_fixed,
            ids("pre"),
            doc["pre_w"],
            doc["pre_h"],
            numeric("previous"),
            numeric("pass1_raw"),
            numeric("pass1_normalized"),
            numeric("pass1"),
            numeric("final_raw"),
            numeric("final_normalized"),
            numeric("final"),
            numeric("temporal"),
            numeric("synchronous"),
            ids("emitters"),
            ids("learning_frontier"),
            ids("frontier"),
            ids("born"),
            ids("deferred"),
            doc["boundary"],
            raw,
            doc["config"],
            doc["core"],
            doc["lla"],
            doc["salt_hash"],
            doc["h_profile"],
            _authority=_PERMIT,
        )
    except (KeyError, TypeError, UnicodeError, OverflowError) as exc:
        raise ValueError("INVALID_EVENT_RECORD") from exc
