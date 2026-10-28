"""Immutable synapse records; production credits are checked against root journals."""

import math
from dataclasses import dataclass
from enum import Enum

from dgca_next.config import load_lab_config
from dgca_next.contracts import SynapseKey, SynapseScope
from dgca_next.graph.cell import nonnegative_integer

_CONFIG = load_lab_config()
E_MAX = float(_CONFIG.parameter("E_max").value)


class SynapseState(Enum):
    CANDIDATE = "CANDIDATE"
    EPISODIC_INDEXED = "EPISODIC_INDEXED"
    CONSOLIDATED = "CONSOLIDATED"


def key_order(key: SynapseKey) -> tuple[int, int, int]:
    return (key.source.cell_id, key.target.cell_id, tuple(SynapseScope).index(key.scope))


@dataclass(frozen=True, slots=True)
class ProductionCredit:
    """One selected root-local positive proposal; not standalone authorization."""

    root_id: int
    event_id: int
    event_order: int
    ordinal: int
    source_event_id: int
    source_digest: str
    target_digest: str
    source_activity: float
    target_activity: float
    target_threshold: float
    q: float
    y: float

    def __post_init__(self) -> None:
        for name in ("root_id", "event_id", "event_order", "ordinal", "source_event_id"):
            nonnegative_integer(getattr(self, name), name)
        for name in ("source_digest", "target_digest"):
            digest = getattr(self, name)
            if (
                type(digest) is not str
                or len(digest) != 64
                or any(c not in "0123456789abcdef" for c in digest)
            ):
                raise ValueError("INVALID_CREDIT_DIGEST")
        for name in ("source_activity", "target_activity", "target_threshold", "q", "y"):
            value = getattr(self, name)
            if type(value) is not float or not math.isfinite(value) or not 0 <= value <= 1:
                raise ValueError("INVALID_CREDIT_VALUE")
        if self.q <= 0 or self.y < float(_CONFIG.parameter("theta_S").value):
            raise ValueError("INVALID_POSITIVE_CREDIT")


@dataclass(frozen=True, slots=True)
class Synapse:
    key: SynapseKey
    delta: int
    state: SynapseState
    S: float
    E_ext: float
    E_int: float
    external_root_count: int
    created_event: int
    fixture_only: bool
    protected: bool = False
    credits: tuple[ProductionCredit, ...] = ()
    candidate_deadline: int | None = None

    def __post_init__(self) -> None:
        if type(self.key) is not SynapseKey or type(self.state) is not SynapseState:
            raise ValueError("INVALID_SYNAPSE_SCHEMA")
        self.key.validate_delta(self.delta)
        for name in ("S", "E_ext", "E_int"):
            value = getattr(self, name)
            if type(value) is not float or not math.isfinite(value) or value < 0:
                raise ValueError(f"INVALID_SYNAPSE_NUMBER: {name}")
        if self.S > 1 or self.E_ext + self.E_int > E_MAX:
            raise ValueError("INVALID_SYNAPSE_BOUNDS")
        if self.E_int > float(_CONFIG.parameter("phi").value) * E_MAX:
            raise ValueError("INTERNAL_EVIDENCE_CAP")
        nonnegative_integer(self.external_root_count, "external_root_count")
        nonnegative_integer(self.created_event, "created_event")
        if self.external_root_count < 1 or self.E_ext <= 0:
            raise ValueError("EXTERNAL_ROOT_REQUIRED")
        if type(self.fixture_only) is not bool or type(self.credits) is not tuple:
            raise ValueError("INVALID_SYNAPSE_ORIGIN")
        if self.fixture_only:
            if self.credits or self.candidate_deadline is not None:
                raise ValueError("FIXTURE_CREDIT_FORBIDDEN")
        else:
            if (
                not self.credits
                or any(type(c) is not ProductionCredit for c in self.credits)
                or len(self.credits) != self.external_root_count
                or tuple(c.root_id for c in self.credits)
                != tuple(sorted({c.root_id for c in self.credits}))
                or self.created_event != self.credits[0].event_id
                or self.E_int != 0.0
                or self.candidate_deadline
                != self.created_event + int(_CONFIG.parameter("W_conf").value)
            ):
                raise ValueError("INVALID_PRODUCTION_CREDITS")
            strength = self.credits[0].y
            mass = min(E_MAX, self.credits[0].q)
            for credit in self.credits[1:]:
                strength = (mass * strength + credit.q * credit.y) / (mass + credit.q)
                mass = min(E_MAX, mass + credit.q)
            if (self.S, self.E_ext) != (strength, mass):
                raise ValueError("PRODUCTION_EVIDENCE_MISMATCH")
        if type(self.protected) is not bool:
            raise ValueError("INVALID_PROTECTION_MARKER")
        if self.state is SynapseState.CONSOLIDATED and (
            self.S < float(_CONFIG.parameter("theta_S").value)
            or (self.E_ext + self.E_int) / E_MAX < float(_CONFIG.parameter("theta_E").value)
            or self.external_root_count < 2
        ):
            raise ValueError("INVALID_CONSOLIDATED_RECORD")


def quality(synapse: Synapse | None) -> float:
    """Pure Q from stored fixture data; no k_evidence, propagation or learning."""
    if synapse is None:
        return 0.0
    if type(synapse) is not Synapse:
        raise ValueError("synapse must be Synapse or None")
    discount = float(_CONFIG.parameter("gamma_int").value) if synapse.E_int > synapse.E_ext else 1.0
    return discount * synapse.S * ((synapse.E_ext + synapse.E_int) / E_MAX)
