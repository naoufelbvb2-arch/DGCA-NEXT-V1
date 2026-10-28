"""Pure fixture Attractor transitions (Core §2.1); no Assembly formation."""

from collections.abc import Mapping
from dataclasses import dataclass, replace

from dgca_next.contracts import SynapseScope
from dgca_next.dynamics.context_gate import ContextBindingFixture, _key, structural_diagnostic
from dgca_next.dynamics.numeric import finite, parameter, support
from dgca_next.dynamics.state import GraphSnapshot
from dgca_next.graph import SynapseState
from dgca_next.graph.synapse import quality


@dataclass(frozen=True, slots=True)
class AssemblyFixture:
    assembly_id: int
    members: tuple[int, ...]
    fixture_only: bool = True
    generation: int = 1
    bound_graph_hash: str | None = None
    bound_identity: tuple[int, int, tuple[int, ...]] | None = None

    def __post_init__(self) -> None:
        if (
            type(self.assembly_id) is not int
            or self.assembly_id < 0
            or type(self.generation) is not int
            or self.generation < 1
            or self.fixture_only is not True
        ):
            raise ValueError("I2_ASSEMBLY_FIXTURE_ONLY")
        if (
            type(self.members) is not tuple
            or self.members != tuple(sorted(set(self.members)))
            or not 3 <= len(self.members) <= 16
        ):
            raise ValueError("INVALID_ASSEMBLY_FIXTURE")

    def bind(
        self,
        graph: GraphSnapshot,
        bindings: Mapping[int, ContextBindingFixture] | None = None,
    ) -> AssemblyFixture:
        """Freeze a synthetic Assembly identity and generation against one I1 W."""
        validate_assembly(graph, self, bindings)
        return replace(
            self,
            bound_graph_hash=graph.structural_hash,
            bound_identity=(self.assembly_id, self.generation, self.members),
        )


def validate_assembly(
    graph: GraphSnapshot,
    assembly: AssemblyFixture,
    bindings: Mapping[int, ContextBindingFixture] | None = None,
) -> None:
    if assembly.bound_identity is not None and (
        assembly.bound_identity != (assembly.assembly_id, assembly.generation, assembly.members)
        or assembly.bound_graph_hash != graph.structural_hash
    ):
        raise ValueError("STALE_ASSEMBLY_FIXTURE")
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


def cohesion_from_graph_and_fresh(
    graph: GraphSnapshot,
    assembly: AssemblyFixture,
    fresh: Mapping[int, float],
    bindings: Mapping[int, ContextBindingFixture] | None = None,
) -> float:
    """Core §2.1 ordered reciprocal fresh weighting on a frozen fixture W."""
    if assembly.bound_identity is None or assembly.bound_graph_hash is None:
        raise ValueError("UNVERIFIED_ASSEMBLY_GENERATION")
    validate_assembly(graph, assembly, bindings)
    numerator, denominator = 0.0, 0.0
    for position, i in enumerate(assembly.members):
        first = support(fresh.get(i, 0.0))
        for j in assembly.members[position + 1 :]:
            forward = graph.synapse(_key(i, j, SynapseScope.LOCAL))
            reverse = graph.synapse(_key(j, i, SynapseScope.LOCAL))
            if (
                forward is None
                or reverse is None
                or forward.state is not SynapseState.CONSOLIDATED
                or reverse.state is not SynapseState.CONSOLIDATED
            ):
                continue
            weight = min(quality(forward), quality(reverse))
            if weight < parameter("theta_A"):
                continue
            numerator += weight * min(first, support(fresh.get(j, 0.0)))
            denominator += weight
    if denominator <= 0.0:
        raise ValueError("INVALID_ASSEMBLY_RECIPROCAL_STRUCTURE")
    return support(numerator / denominator)


@dataclass(frozen=True, slots=True)
class AttractorState:
    assembly_id: int
    strength: float
    age: int
    error: float
    generation: int = 1

    def __post_init__(self) -> None:
        if (
            type(self.assembly_id) is not int
            or self.assembly_id < 0
            or type(self.generation) is not int
            or self.generation < 1
        ):
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
    graph: GraphSnapshot,
    assembly: AssemblyFixture,
    fresh: Mapping[int, float],
    bindings: Mapping[int, ContextBindingFixture] | None = None,
    boundary: bool = False,
    comparable: tuple[tuple[float, float], ...] = (),
) -> tuple[AttractorState | None, str | None]:
    """Fixture-only Attractor calculation; no scalar can authorize cohesion.

    Comparable outcome pairs are synthetic fixture data, not real external proof.
    """
    if type(boundary) is not bool or type(comparable) is not tuple:
        raise ValueError("INVALID_ATTRACTOR_INPUT")
    if previous and (previous.assembly_id, previous.generation) != (
        assembly.assembly_id,
        assembly.generation,
    ):
        raise ValueError("ATTRACTOR_ID_MISMATCH")
    cohesion = cohesion_from_graph_and_fresh(graph, assembly, fresh, bindings)
    fresh_total = 0.0
    for member in assembly.members:
        fresh_total += support(fresh.get(member, 0.0))
    fresh_mean = fresh_total / len(assembly.members)
    if boundary:
        return None, "ATTRACTOR_BOUNDARY_COLLAPSE"
    if previous is None:
        if fresh_mean < parameter("theta_in"):
            return None, None
        if cohesion < parameter("theta_ctx_form"):
            return None, "ATTRACTOR_INSUFFICIENT_COHESION"
        return AttractorState(assembly.assembly_id, fresh_mean, 0, 0.0, assembly.generation), None
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
    return AttractorState(assembly.assembly_id, strength, age, error, assembly.generation), None
