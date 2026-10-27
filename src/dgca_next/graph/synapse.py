"""Immutable fixture records, not evidence updates (Core §1.4, LLA §§4.1–4.4)."""

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
        if type(self.fixture_only) is not bool or not self.fixture_only:
            raise ValueError("I1_FIXTURE_ONLY")
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
