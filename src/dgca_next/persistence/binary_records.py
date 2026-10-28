"""Canonical tagged P02 records: fixed-width integers and big-endian binary64.

Every record is tag:u8, version:u8, payload_length:u32be, payload. Values
carry a one-byte type tag; integers use signed i64be, floating-point numbers
use canonical finite binary64be, and text/bytes and containers use u32be
lengths. Object fields are serialized in ascending UTF-8 key order. Each
record consumer validates its exact field set and canonical re-encoding.
"""

import math
import struct


def _u32(value: int) -> bytes:
    if not 0 <= value <= 0xFFFFFFFF:
        raise ValueError("RECORD_SIZE_OUT_OF_RANGE")
    return struct.pack(">I", value)


def _value(value: object) -> bytes:
    if value is None:
        return b"\x00"
    if type(value) is bool:
        return b"\x02" if value else b"\x01"
    if type(value) is int:
        if not -(2**63) <= value < 2**63:
            raise ValueError("RECORD_INTEGER_OUT_OF_RANGE")
        return b"\x03" + struct.pack(">q", value)
    if type(value) is float:
        if not math.isfinite(value):
            raise ValueError("INVALID_RECORD_BINARY64")
        return b"\x04" + struct.pack(">d", 0.0 if value == 0.0 else value)
    if type(value) is str:
        encoded = value.encode("utf-8", "strict")
        return b"\x05" + _u32(len(encoded)) + encoded
    if type(value) is bytes:
        return b"\x06" + _u32(len(value)) + value
    if type(value) is list:
        return b"\x07" + _u32(len(value)) + b"".join(_value(item) for item in value)
    if type(value) is dict:
        if any(type(key) is not str for key in value):
            raise ValueError("INVALID_RECORD_FIELD")
        keys = sorted(value, key=lambda key: key.encode("utf-8"))
        return (
            b"\x08" + _u32(len(keys)) + b"".join(_value(key) + _value(value[key]) for key in keys)
        )
    raise ValueError("INVALID_RECORD_VALUE")


def encode_record(tag: int, version: int, value: object) -> bytes:
    if (
        type(tag) is not int
        or type(version) is not int
        or not 0 <= tag < 256
        or not 0 <= version < 256
    ):
        raise ValueError("INVALID_RECORD_SCHEMA")
    payload = _value(value)
    return bytes((tag, version)) + _u32(len(payload)) + payload


def decode_record(data: bytes, tag: int, version: int) -> object:
    if type(data) is not bytes or len(data) < 6 or data[:2] != bytes((tag, version)):
        raise ValueError("UNSUPPORTED_RECORD_SCHEMA")
    if struct.unpack(">I", data[2:6])[0] != len(data) - 6:
        raise ValueError("INVALID_RECORD_LENGTH")
    offset = 6

    def read(size: int) -> bytes:
        nonlocal offset
        if size < 0 or offset + size > len(data):
            raise ValueError("TRUNCATED_RECORD")
        result = data[offset : offset + size]
        offset += size
        return result

    def parse(depth: int) -> object:
        if depth > 64:
            raise ValueError("RECORD_NESTING_LIMIT")
        kind = read(1)[0]
        if kind == 0:
            return None
        if kind in (1, 2):
            return kind == 2
        if kind == 3:
            return struct.unpack(">q", read(8))[0]
        if kind == 4:
            raw = read(8)
            number = struct.unpack(">d", raw)[0]
            if not math.isfinite(number) or (number == 0.0 and raw != struct.pack(">d", 0.0)):
                raise ValueError("INVALID_RECORD_BINARY64")
            return number
        if kind in (5, 6):
            size = struct.unpack(">I", read(4))[0]
            raw = read(size)
            return raw.decode("utf-8", "strict") if kind == 5 else raw
        if kind == 7:
            size = struct.unpack(">I", read(4))[0]
            if size > len(data) - offset:
                raise ValueError("INVALID_RECORD_COUNT")
            return [parse(depth + 1) for _ in range(size)]
        if kind == 8:
            size = struct.unpack(">I", read(4))[0]
            if size > (len(data) - offset) // 2:
                raise ValueError("INVALID_RECORD_COUNT")
            result: dict[str, object] = {}
            for _ in range(size):
                key = parse(depth + 1)
                if type(key) is not str or key in result:
                    raise ValueError("INVALID_RECORD_FIELD")
                result[key] = parse(depth + 1)
            return result
        raise ValueError("INVALID_RECORD_TYPE")

    try:
        result = parse(0)
        if offset != len(data) or encode_record(tag, version, result) != data:
            raise ValueError("NONCANONICAL_RECORD")
        return result
    except (UnicodeError, struct.error, OverflowError) as exc:
        raise ValueError("INVALID_RECORD") from exc
