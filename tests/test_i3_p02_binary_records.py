"""P02 canonical records encode finite numeric fields in binary64 big-endian."""

import math
import struct

import pytest

from dgca_next.persistence.binary_records import decode_record, encode_record


def test_binary64_and_fixed_width_numeric_golden():
    raw = encode_record(0x51, 2, [1.5, 7, -1, 0.0])
    expected = (
        b"\x07"
        + struct.pack(">I", 4)
        + b"\x04"
        + struct.pack(">d", 1.5)
        + b"\x03"
        + struct.pack(">q", 7)
        + b"\x03"
        + struct.pack(">q", -1)
        + b"\x04"
        + struct.pack(">d", 0.0)
    )
    assert raw == b"\x51\x02" + struct.pack(">I", len(expected)) + expected
    assert decode_record(raw, 0x51, 2) == [1.5, 7, -1, 0.0]


@pytest.mark.parametrize("number", [math.nan, math.inf, -math.inf])
def test_nonfinite_numbers_rejected(number):
    with pytest.raises(ValueError, match="INVALID_RECORD_BINARY64"):
        encode_record(0x51, 2, [number])


def test_negative_zero_normalized_and_noncanonical_bytes_rejected():
    raw = encode_record(0x51, 2, [-0.0])
    assert raw.endswith(struct.pack(">d", 0.0))
    damaged = raw[:-8] + struct.pack(">d", -0.0)
    with pytest.raises(ValueError, match="INVALID_RECORD_BINARY64"):
        decode_record(damaged, 0x51, 2)
    with pytest.raises(ValueError):
        decode_record(raw[:-1], 0x51, 2)
