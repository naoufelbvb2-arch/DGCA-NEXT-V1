"""I3-R03/R04 pure numeric fixtures; these functions cannot authorize evidence.

Real external validation, root journals and graph publication are intentionally
absent. A `SyntheticEvidence` is a calculation aid, never a production Synapse.
"""

import math
from dataclasses import dataclass

from dgca_next.contracts import SynapseKey, SynapseScope
from dgca_next.dynamics.numeric import clip, parameter, q6, support
from dgca_next.graph.cell import nonnegative_integer
from dgca_next.graph.synapse import SynapseState


@dataclass(frozen=True, slots=True)
class PositiveNumbers:
    coactivity: float
    q: float
    y: float
    threshold_passed: bool
    target_active: bool


def preview_positive_numbers(
    scope: SynapseScope, source_final: float, target_final: float, target_threshold: float
) -> PositiveNumbers:
    """Compute numerical laws only; no V_ext, topology, frontier or root proof."""
    if type(scope) is not SynapseScope:
        raise ValueError("INVALID_SYNAPSE_SCOPE")
    a_source, a_target, theta = (
        support(source_final),
        support(target_final),
        support(target_threshold),
    )
    if not parameter("theta_min") <= theta <= parameter("theta_max"):
        raise ValueError("INVALID_ACTIVE_THRESHOLD")
    coactivity = a_source * a_target
    factor = parameter(f"k_evidence_{scope.value}")
    q = coactivity * factor
    theta_s = parameter("theta_S")
    y = clip(theta_s + (1.0 - theta_s) * ((a_target - theta) / (1.0 - theta)), theta_s, 1.0)
    create = parameter(
        "theta_create_x" if scope is SynapseScope.CROSS_TERRITORY else "theta_create"
    )
    return PositiveNumbers(
        coactivity, q, y, q6(coactivity) >= q6(create), q6(a_target) >= q6(theta)
    )


@dataclass(frozen=True, slots=True)
class SyntheticProposal:
    """One untrusted numerical proposal, never a witness or production command."""

    key: SynapseKey
    root_id: int
    event_order: int
    ordinal: int
    q: float
    y: float
    fixture_only: bool = True

    def __post_init__(self) -> None:
        if type(self.key) is not SynapseKey or self.fixture_only is not True:
            raise ValueError("SYNTHETIC_PROPOSAL_ONLY")
        for name in ("root_id", "event_order", "ordinal"):
            nonnegative_integer(getattr(self, name), name)
        if support(self.q) <= 0.0 or support(self.y) < parameter("theta_S"):
            raise ValueError("INVALID_POSITIVE_PROPOSAL")


def root_max(proposals: tuple[SyntheticProposal, ...]) -> SyntheticProposal:
    """Select one paired q/y using full binary64 q and deterministic ties."""
    if type(proposals) is not tuple or not proposals:
        raise ValueError("NO_POSITIVE_PROPOSALS")
    if any(type(p) is not SyntheticProposal for p in proposals):
        raise ValueError("SYNTHETIC_PROPOSAL_ONLY")
    first = proposals[0]
    if any((p.key, p.root_id) != (first.key, first.root_id) for p in proposals):
        raise ValueError("MIXED_KEY_OR_ROOT")
    if len({(p.event_order, p.ordinal) for p in proposals}) != len(proposals):
        raise ValueError("DUPLICATE_PROPOSAL_ORDINAL")
    return min(proposals, key=lambda p: (-p.q, p.event_order, p.ordinal))


@dataclass(frozen=True, slots=True)
class SyntheticEvidence:
    key: SynapseKey
    S: float
    E_ext: float
    E_int: float
    roots: tuple[int, ...]
    state: SynapseState
    fixture_only: bool = True

    def __post_init__(self) -> None:
        if type(self.key) is not SynapseKey or type(self.state) is not SynapseState:
            raise ValueError("INVALID_SYNTHETIC_EVIDENCE")
        if self.fixture_only is not True or type(self.roots) is not tuple:
            raise ValueError("SYNTHETIC_EVIDENCE_ONLY")
        support(self.S)
        for name in ("E_ext", "E_int"):
            value = getattr(self, name)
            if (
                type(value) is not float
                or not math.isfinite(value)
                or value < 0.0
                or value > parameter("E_max")
            ):
                raise ValueError("INVALID_EVIDENCE_MASS")
        if self.E_ext + self.E_int > parameter("E_max") or self.E_int > parameter(
            "phi"
        ) * parameter("E_max"):
            raise ValueError("INVALID_EVIDENCE_MASS")
        if self.E_ext <= 0 or not self.roots or tuple(sorted(set(self.roots))) != self.roots:
            raise ValueError("INVALID_SYNTHETIC_ROOTS")
        for root in self.roots:
            nonnegative_integer(root, "root_id")
        if self.state is SynapseState.CONSOLIDATED and (
            len(self.roots) < 2
            or q6(self.S) < q6(parameter("theta_S"))
            or q6((self.E_ext + self.E_int) / parameter("E_max")) < q6(parameter("theta_E"))
        ):
            raise ValueError("INVALID_CONSOLIDATED_RECORD")


def apply_fixture_proposal(
    current: SyntheticEvidence | None, proposal: SyntheticProposal
) -> SyntheticEvidence:
    """Apply one selected positive q in an isolated synthetic calculation."""
    if type(proposal) is not SyntheticProposal:
        raise ValueError("SYNTHETIC_PROPOSAL_ONLY")
    limit = parameter("E_max")
    if current is None:
        return SyntheticEvidence(
            proposal.key,
            proposal.y,
            min(limit, proposal.q),
            0.0,
            (proposal.root_id,),
            SynapseState.CANDIDATE,
        )
    if type(current) is not SyntheticEvidence or current.key != proposal.key:
        raise ValueError("SYNTHETIC_EVIDENCE_ONLY")
    if proposal.root_id <= current.roots[-1]:
        raise ValueError("ROOT_ID_REUSED")
    old_mass = current.E_ext + current.E_int
    S = (old_mass * current.S + proposal.q * proposal.y) / (old_mass + proposal.q)
    external = min(limit, current.E_ext + proposal.q)
    internal = min(current.E_int, parameter("phi") * limit, limit - external)
    roots = (*current.roots, proposal.root_id)
    eligible = (
        len(roots) >= 2
        and q6(S) >= q6(parameter("theta_S"))
        and q6((external + internal) / limit) >= q6(parameter("theta_E"))
    )
    state = SynapseState.CONSOLIDATED if eligible else current.state
    return SyntheticEvidence(current.key, S, external, internal, roots, state)
