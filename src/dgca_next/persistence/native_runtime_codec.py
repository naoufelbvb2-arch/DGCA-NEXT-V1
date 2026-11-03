"""R05 tagged R2 checkpoints. Decoding is diagnostic, never authentication."""

from dataclasses import replace
from typing import Any

from dgca_next.dynamics.native_attractor import (
    _RUNTIME,
    NativeTrace,
    ObservationScope,
    _state_document,
)
from dgca_next.learning.production_event import ExternalEventObservation, decode_event
from dgca_next.persistence.binary_records import decode_record, encode_record
from dgca_next.persistence.production_store import _sha


def runtime_document(raw: bytes) -> dict[str, Any]:
    value = decode_record(raw, 0x52, 2)
    if type(value) is not dict or set(value) != {
        "event",
        "scope",
        "before_r",
        "pre_w",
        "pre_h",
        "after_w",
        "after_h",
        "fresh_first",
        "fresh_second",
        "sigma",
        "evaluations",
        "state",
    }:
        raise ValueError("INVALID_NATIVE_R_FIELDS")
    ObservationScope(value["scope"])
    decode_event(value["event"])
    if encode_record(0x52, 2, value) != raw:
        raise ValueError("NONCANONICAL_NATIVE_R")
    return value


def encode_native_runtime(
    trace: NativeTrace,
    event: ExternalEventObservation,
    before_r: bytes,
    after_w: bytes,
    after_h: bytes,
) -> bytes:
    state = replace(trace.state, w_hash=_sha(after_w), h_hash=_sha(after_h), _authority=_RUNTIME)

    def numbers(values: Any) -> list[list[Any]]:
        return [[i, a] for i, a in sorted(values.items())]

    def one_pass(value: Any) -> dict[str, Any]:
        return {k: numbers(getattr(value, k)) for k in ("raw", "normalized", "activity")}

    return encode_record(
        0x52,
        2,
        dict(
            event=event.raw,
            scope=trace.scope.value,
            before_r=_sha(before_r),
            pre_w=trace.state.w_hash,
            pre_h=trace.state.h_hash,
            after_w=_sha(after_w),
            after_h=_sha(after_h),
            fresh_first=one_pass(trace.fresh.first),
            fresh_second=one_pass(trace.fresh.second),
            sigma=numbers(trace.sigma),
            evaluations=list(trace.evaluations),
            state=_state_document(state),
        ),
    )
