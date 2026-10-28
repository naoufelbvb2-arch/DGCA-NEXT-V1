"""Canonical I3-R01 H record, Core §3.1; no pickle or implicit defaults.

H record tag 0x48, schema 1, unsigned u32 payload length. The payload fields
are four count-prefixed, sorted maps in order: gains and rates as (u32 cell ID,
binary64), thresholds and regional EMAs as (u8 region, binary64). Counts use
u32. Binary64 is big-endian, finite, and canonicalizes negative zero.
"""

import math
import struct
from collections.abc import Mapping

from dgca_next.contracts import Region
from dgca_next.dynamics.state import Homeostasis

_HEADER = b"\x48\x01"


def _pack_value(value: float) -> bytes:
    if type(value) is not float or not math.isfinite(value):
        raise ValueError("INVALID_BINARY64")
    return struct.pack(">d", 0.0 if value == 0.0 else value)


def _encode_cells(values: Mapping[int, float]) -> bytes:
    return struct.pack(">I", len(values)) + b"".join(
        struct.pack(">I", key) + _pack_value(value) for key, value in sorted(values.items())
    )


def _encode_regions(values: Mapping[Region, float]) -> bytes:
    return struct.pack(">I", len(values)) + b"".join(
        bytes((key.value,)) + _pack_value(value)
        for key, value in sorted(values.items(), key=lambda item: item[0].value)
    )


def encode_homeostasis(state: Homeostasis) -> bytes:
    if type(state) is not Homeostasis:
        raise ValueError("INVALID_HOMEOSTASIS")
    payload = (
        _encode_cells(state.gains)
        + _encode_cells(state.rates)
        + _encode_regions(state.thresholds)
        + _encode_regions(state.region_rates)
    )
    return _HEADER + struct.pack(">I", len(payload)) + payload


def decode_homeostasis(record: bytes) -> Homeostasis:
    if type(record) is not bytes or len(record) < 6 or record[:2] != _HEADER:
        raise ValueError("UNSUPPORTED_H_SCHEMA")
    if struct.unpack(">I", record[2:6])[0] != len(record) - 6:
        raise ValueError("MALFORMED_H_RECORD")
    offset = 6

    def read(size: int) -> bytes:
        nonlocal offset
        if offset + size > len(record):
            raise ValueError("MALFORMED_H_RECORD")
        result = record[offset : offset + size]
        offset += size
        return result

    def entries(width: int, maximum: int) -> dict[int, float]:
        count = struct.unpack(">I", read(4))[0]
        if count > maximum:
            raise ValueError("INVALID_H_COUNT")
        result: dict[int, float] = {}
        previous = -1
        for _ in range(count):
            key = int.from_bytes(read(width), "big")
            raw = read(8)
            value = struct.unpack(">d", raw)[0]
            if key <= previous or not math.isfinite(value) or raw != _pack_value(value):
                raise ValueError("NONCANONICAL_H_RECORD")
            result[key] = value
            previous = key
        return result

    gains = entries(4, 12288)
    rates = entries(4, 12288)
    thresholds = {Region(k): v for k, v in entries(1, 3).items()}
    region_rates = {Region(k): v for k, v in entries(1, 3).items()}
    if offset != len(record):
        raise ValueError("MALFORMED_H_RECORD")
    return Homeostasis(gains, rates, thresholds, region_rates)
