"""RC4.4 LANGUAGE sparse H profile; no EVENT or publication authority."""

from __future__ import annotations

import hashlib
import struct
from collections.abc import Mapping
from dataclasses import dataclass

from dgca_next.config import load_lab_config
from dgca_next.contracts import CellAddress, Region
from dgca_next.dynamics.homeostasis import adapt
from dgca_next.dynamics.state import GraphSnapshot, Homeostasis
from dgca_next.persistence.codec import decode_homeostasis, encode_homeostasis

_CONFIG = load_lab_config()
PROFILE_VERSION = str(_CONFIG.parameter("h_profile_version").value)
_PROFILE = (
    PROFILE_VERSION.encode("ascii")
    + b"\0"
    + struct.pack(
        ">dddd",
        float(_CONFIG.parameter("g_initial_LANGUAGE").value),
        float(_CONFIG.parameter("r_bar_initial_LANGUAGE").value),
        float(_CONFIG.parameter("rho_bar_initial_LANGUAGE").value),
        float(_CONFIG.parameter("theta_active_init_LANGUAGE").value),
    )
)
PROFILE_HASH = hashlib.sha256(_PROFILE).digest()
_MAGIC = b"DGCA-H4\x01"


@dataclass(frozen=True, slots=True)
class LanguageHomeostasis:
    """Sparse adaptations and shared region state pinned to immutable defaults.

    This numeric value alone cannot authorize an adaptation or a graph birth.
    """

    overrides: Homeostasis

    def __post_init__(self) -> None:
        h = self.overrides
        if type(h) is not Homeostasis:
            raise ValueError("INVALID_PROFILE_STATE")
        if set(h.gains) != set(h.rates):
            raise ValueError("INCOMPLETE_H_OVERRIDE")
        if set(h.thresholds) != {Region.LANGUAGE} or set(h.region_rates) != {Region.LANGUAGE}:
            raise ValueError("UNSUPPORTED_H_REGION")
        if any(CellAddress.from_cell_id(i).region is not Region.LANGUAGE for i in h.gains):
            raise ValueError("UNSUPPORTED_H_REGION")

    @classmethod
    def initial(cls) -> LanguageHomeostasis:
        return cls(
            Homeostasis(
                {},
                {},
                {Region.LANGUAGE: float(_CONFIG.parameter("theta_active_init_LANGUAGE").value)},
                {Region.LANGUAGE: float(_CONFIG.parameter("rho_bar_initial_LANGUAGE").value)},
            )
        )

    def materialize(self, committed: frozenset[int]) -> Homeostasis:
        if type(committed) is not frozenset:
            raise ValueError("INVALID_COMMITTED_POPULATION")
        for cell in committed:
            if CellAddress.from_cell_id(cell).region is not Region.LANGUAGE:
                raise ValueError("UNSUPPORTED_H_REGION")
        h = self.overrides
        if not set(h.gains).issubset(committed):
            raise ValueError("H_OVERRIDE_NOT_COMMITTED")
        default_gain = float(_CONFIG.parameter("g_initial_LANGUAGE").value)
        default_rate = float(_CONFIG.parameter("r_bar_initial_LANGUAGE").value)
        return Homeostasis(
            {i: h.gains.get(i, default_gain) for i in committed},
            {i: h.rates.get(i, default_rate) for i in committed},
            h.thresholds,
            h.region_rates,
        )

    def encode(self) -> bytes:
        return _MAGIC + PROFILE_HASH + encode_homeostasis(self.overrides)

    @classmethod
    def decode(cls, payload: bytes) -> LanguageHomeostasis:
        if type(payload) is not bytes or not payload.startswith(_MAGIC + PROFILE_HASH):
            raise ValueError("UNSUPPORTED_H_PROFILE")
        state = cls(decode_homeostasis(payload[len(_MAGIC) + len(PROFILE_HASH) :]))
        if state.encode() != payload:
            raise ValueError("NONCANONICAL_H_PROFILE")
        return state


def preview_pre_event_adaptation(
    profile: LanguageHomeostasis, graph: GraphSnapshot, activity: Mapping[int, float]
) -> LanguageHomeostasis:
    """Compute a frozen-population H preview, without authorization or mutation.

    A production EVENT must separately verify provenance, use its own actual
    durable pre-event W, and atomically checkpoint its adaptation. Calling this
    pure helper cannot establish those conditions or publish an H override.
    """
    if type(profile) is not LanguageHomeostasis or type(graph) is not GraphSnapshot:
        raise ValueError("INVALID_PRE_EVENT_PROFILE")
    graph.validate()
    expanded = profile.materialize(graph.committed_ids)
    after = adapt(expanded, activity, graph=graph)
    return LanguageHomeostasis(after)
