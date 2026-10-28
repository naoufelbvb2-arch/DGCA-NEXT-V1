import math
import struct
from fractions import Fraction

import pytest

from dgca_next.dynamics.numeric import binary64_bytes, clip, noisy_or, q6


@pytest.mark.parametrize(
    "values,expected",
    [((), 0.0), ((0.0,), 0.0), ((1.0,), 1.0), ((0.5, 0.25), 0.625), ((0.0, 1.0, 0.3), 1.0)],
)
def test_T08_literal_complement_product(values, expected):
    assert noisy_or(values) == expected


def test_T08_stable_fold_and_quantization():
    values = (0.1, 0.2, 0.3, 0.000001, 0.999999)
    complement = 1.0
    for v in values:
        complement = complement * (1.0 - v)
    assert binary64_bytes(noisy_or(values)) == struct.pack(">d", 1.0 - complement)
    for v in (0.0000005, math.nextafter(0.5, 1), 0.1234565, 0.9999995):
        assert q6(v) == round(Fraction.from_float(v) * 1000000)
    assert binary64_bytes(-0.0) == b"\0" * 8
    assert clip(-0.1) == 0.0
    assert clip(1.1) == 1.0


@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf"), -0.1, 1.1, True, 1])
def test_T08_invalid_support(value):
    with pytest.raises(ValueError):
        noisy_or((value,))
