"""Pure fixture Attractor transitions (Core §2.1); no Assembly formation."""

from collections.abc import Mapping
from dataclasses import dataclass

from dgca_next.contracts import SynapseScope
from dgca_next.dynamics.context_gate import ContextBindingFixture, _key, structural_diagnostic
from dgca_next.dynamics.numeric import SpecBlocked, finite, parameter, support
from dgca_next.dynamics.state import GraphSnapshot
from dgca_next.graph import SynapseState
from dgca_next.graph.synapse import quality


@dataclass(frozen=True, slots=True)
class AssemblyFixture:
    assembly_id: int
    members: tuple[int, ...]
    fixture_only: bool = True

    def __post_init__(self) -> None:
        if (
            type(self.assembly_id) is not int
            or self.assembly_id < 0
            or self.fixture_only is not True
        ):
            raise ValueError("I2_ASSEMBLY_FIXTURE_ONLY")
        if (
            type(self.members) is not tuple
            or self.members != tuple(sorted(set(self.members)))
            or not 3 <= len(self.members) <= 16
        ):
            raise ValueError("INVALID_ASSEMBLY_FIXTURE")


def validate_assembly(
    graph: GraphSnapshot,
    assembly: AssemblyFixture,
    bindings: Mapping[int, ContextBindingFixture] | None = None,
) -> None:
    members = assembly.members
    if not set(members) <= graph.committed_ids or any(i < 8192 for i in members):
        raise ValueError("INVALID_ASSEMBLY_MEMBERS")
    cells = {c.cell_id: c for c in graph.cells()}
    if any(assembly.assembly_id not in cells[i].assembly_ids for i in members):
        raise ValueError("MISSING_ASSEMBLY_FIXTURE_MEMBERSHIP")
    contexts = {} if bindings is None else bindings
    for i in members:
        binding = contexts.get(i)
        if binding and (not binding.complete or structural_diagnostic(binding, graph, contexts)):
            raise ValueError("UNQUALIFIED_CONTEXT_ASSEMBLY_MEMBER")
    reciprocal: dict[int, dict[int, float]] = {}
    for synapse in graph.synapses():
        key = synapse.key
        if key.scope is not SynapseScope.LOCAL or synapse.state is not SynapseState.CONSOLIDATED:
            continue
        reverse = graph.synapse(_key(key.target.cell_id, key.source.cell_id, SynapseScope.LOCAL))
        if reverse and reverse.state is SynapseState.CONSOLIDATED:
            value = min(quality(synapse), quality(reverse))
            if value >= parameter("theta_A"):
                reciprocal.setdefault(key.source.cell_id, {})[key.target.cell_id] = value
    for i in members:
        neighbors = reciprocal.get(i, {})
        own = {j: v for j, v in neighbors.items() if j in members}
        density = len(own) / (len(members) - 1)
        total = sum(v for _, v in sorted(neighbors.items()))
        specificity = sum(v for _, v in sorted(own.items())) / total if total else 0.0
        if (
            len(own) < parameter("d_min")
            or density < parameter("rho_keep")
            or specificity < parameter("sigma_keep")
        ):
            raise ValueError("UNQUALIFIED_ASSEMBLY_FIXTURE")


@dataclass(frozen=True, slots=True)
class AttractorState:
    assembly_id: int
    strength: float
    age: int
    error: float

    def __post_init__(self) -> None:
        if type(self.assembly_id) is not int or self.assembly_id < 0:
            raise ValueError("INVALID_ATTRACTOR_ID")
        support(self.strength)
        if (
            type(self.age) is not int
            or self.age < 0
            or not 0 <= finite(self.error) <= parameter("Theta_err") + 1.0
        ):
            raise ValueError("INVALID_ATTRACTOR_STATE")


def transition(
    previous: AttractorState | None,
    *,
    assembly_id: int,
    fresh_mean: float,
    boundary: bool = False,
    cohesion: float | None = None,
    comparable: tuple[tuple[float, float], ...] = (),
) -> tuple[AttractorState | None, str | None]:
    """Cohesion, if supplied, is an explicit synthetic scalar; not inferred.

    RC4.2 names a cohesion threshold but gives no cohesion formula. Automatic
    admission requiring that score therefore raises I2-S02 instead of choosing
    mean pair quality/density/specificity. Existing qualified states can decay.
    Comparable pairs are explicit externally comparable (prediction,observation)
    fixture measurements, not an I2 certificate for external outcomes.
    """
    support(fresh_mean)
    if type(boundary) is not bool or type(comparable) is not tuple:
        raise ValueError("INVALID_ATTRACTOR_INPUT")
    if previous and previous.assembly_id != assembly_id:
        raise ValueError("ATTRACTOR_ID_MISMATCH")
    if boundary:
        return None, "ATTRACTOR_BOUNDARY_COLLAPSE"
    if previous is None:
        if fresh_mean < parameter("theta_in"):
            return None, None
        if cohesion is None:
            raise SpecBlocked(
                "I2-S02: Core §2.1 cohesion>=theta_ctx_form has no executable cohesion definition"
            )
        if support(cohesion) < parameter("theta_ctx_form"):
            return None, "ATTRACTOR_INSUFFICIENT_COHESION"
        return AttractorState(assembly_id, fresh_mean, 0, 0.0), None
    age = previous.age + 1
    if age >= int(parameter("T_max")):
        return None, "ATTRACTOR_AGE_COLLAPSE"
    valid = []
    for prediction, observed in comparable:
        support(prediction)
        support(observed)
        if prediction >= parameter("theta_pred"):
            valid.append(prediction * (1.0 - observed))
    miss = sum(valid) / len(valid) if valid else 0.0
    error = min(parameter("Theta_err") + 1.0, previous.error + miss)
    if error > parameter("Theta_err"):
        return None, "ATTRACTOR_ERROR_COLLAPSE"
    strength = max(parameter("rho_s") * previous.strength, fresh_mean)
    return AttractorState(assembly_id, strength, age, error), None
