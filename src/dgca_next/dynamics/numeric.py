"""Finite binary64 operations, stable fold order and exact Q6 (Core §3.1)."""

import math
import struct
from collections.abc import Iterable

from dgca_next.config import load_lab_config
from dgca_next.graph.policy import q6 as q6

_CONFIG = load_lab_config()


class SpecBlocked(RuntimeError):
    """An executable rule conflicts or is absent; no fallback computation."""


def parameter(name: str) -> float:
    return float(_CONFIG.parameter(name).value)


def finite(value: float) -> float:
    if type(value) is not float or not math.isfinite(value):
        raise ValueError("INVALID_FINITE_BINARY64")
    return 0.0 if value == 0 else value


def support(value: float) -> float:
    value = finite(value)
    if not 0 <= value <= 1:
        raise ValueError("SUPPORT_OUT_OF_BOUNDS")
    return value


def clip(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
    value = finite(value)
    return max(lower, min(value, upper))


def noisy_or(values: Iterable[float]) -> float:
    """Caller supplies canonical contributor order; literal complement-product fold."""
    complement = 1.0
    for value in values:
        complement *= 1.0 - support(value)
    return support(1.0 - complement)


def binary64_bytes(value: float) -> bytes:
    return struct.pack(">d", finite(value))
