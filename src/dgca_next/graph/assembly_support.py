"""Read-only LANGUAGE reciprocal structure; no Assembly identity or publication."""

import math
from dataclasses import dataclass
from itertools import combinations

from dgca_next.config import load_lab_config
from dgca_next.contracts import CellAddress, Region, SynapseKey, SynapseScope
from dgca_next.graph.network import SparseNetwork
from dgca_next.graph.policy import q6
from dgca_next.graph.synapse import ProductionCredit, SynapseState, quality

_CONFIG = load_lab_config()


def _parameter(name: str) -> float:
    return float(_CONFIG.parameter(name).value)


def reciprocal_quality(forward: float, reverse: float) -> tuple[float, bool]:
    """Numerical component only; scalars supply no physical/event authority."""
    if any(
        type(v) is not float or not math.isfinite(v) or not 0 <= v <= 1 for v in (forward, reverse)
    ):
        raise ValueError("INVALID_RECIPROCAL_QUALITY")
    value = min(forward, reverse)
    return value, q6(value) >= q6(_parameter("theta_A"))


@dataclass(frozen=True, slots=True)
class DirectedLocalDiagnostic:
    source: int
    target: int
    state: str | None
    strength: float
    external: float
    internal: float
    external_count: int
    quality: float
    structurally_eligible: bool
    credits: tuple[ProductionCredit, ...]
    reason: str


@dataclass(frozen=True, slots=True)
class ReciprocalPairDiagnostic:
    first: int
    second: int
    forward: DirectedLocalDiagnostic
    reverse: DirectedLocalDiagnostic
    support: float
    edge: bool


@dataclass(frozen=True, slots=True)
class MemberStructuralDiagnostic:
    cell_id: int
    degree: int
    density: float
    reciprocal_neighbors: tuple[tuple[int, float], ...]
    numerator: float
    denominator: float
    specificity: float
    memberships: int


@dataclass(frozen=True, slots=True)
class TriangleDiagnostic:
    members: tuple[int, int, int]
    pairs: tuple[ReciprocalPairDiagnostic, ...]
    cells: tuple[MemberStructuralDiagnostic, ...]
    reasons: tuple[str, ...]

    @property
    def eligible(self) -> bool:
        return not self.reasons


@dataclass(frozen=True, slots=True)
class ReciprocalStructureDiagnostic:
    graph_hash: str
    committed: tuple[int, ...]
    pairs: tuple[ReciprocalPairDiagnostic, ...]
    triangles: tuple[TriangleDiagnostic, ...]
    component_only: bool


def _check_graph(graph: SparseNetwork, component_only: bool) -> None:
    if type(graph) is not SparseNetwork:
        raise ValueError("INVALID_STRUCTURAL_GRAPH")
    graph.validate_graph()
    if not component_only and (
        any(c.fixture_only for c in graph.stored_cells())
        or any(s.fixture_only for s in graph.synapses())
    ):
        raise ValueError("FIXTURE_FORM_STRUCTURE_FORBIDDEN")
    if not component_only and any(c.assembly_ids for c in graph.stored_cells()):
        raise ValueError("UNSUPPORTED_NATIVE_MEMBERSHIPS")


def _directed(
    graph: SparseNetwork, source: int, target: int, component: bool
) -> DirectedLocalDiagnostic:
    key = SynapseKey(
        CellAddress.from_cell_id(source), CellAddress.from_cell_id(target), SynapseScope.LOCAL
    )
    link = graph.synapse(key)
    eligible = graph.structurally_eligible(source, target)
    reason = "QUALIFIED"
    if not graph.cell(source).committed or not graph.cell(target).committed:
        reason = "UNCOMMITTED_ENDPOINT"
    elif key.source.region is not Region.LANGUAGE or key.target.region is not Region.LANGUAGE:
        reason = "UNSUPPORTED_FORM_REGION"
    elif link is None:
        reason = "MISSING_LOCAL_KEY"
    elif link.fixture_only and not component:
        reason = "FIXTURE_LOCAL_KEY"
    elif not eligible:
        reason = "MISSING_LATENT_ELIGIBILITY"
    elif link.state is not SynapseState.CONSOLIDATED:
        reason = "NONCONSOLIDATED_LOCAL_KEY"
    elif quality(link) <= 0:
        reason = "ZERO_QUALITY"
    return DirectedLocalDiagnostic(
        source,
        target,
        None if link is None else link.state.value,
        0.0 if link is None else link.S,
        0.0 if link is None else link.E_ext,
        0.0 if link is None else link.E_int,
        0 if link is None else link.external_root_count,
        0.0 if link is None else quality(link),
        eligible,
        () if link is None else link.credits,
        reason,
    )


def _pair(
    graph: SparseNetwork, first: int, second: int, component: bool
) -> ReciprocalPairDiagnostic:
    if type(first) is not int or type(second) is not int or first >= second:
        raise ValueError("INVALID_RECIPROCAL_PAIR")
    forward, reverse = (
        _directed(graph, first, second, component),
        _directed(graph, second, first, component),
    )
    support = (
        min(forward.quality, reverse.quality)
        if forward.reason == reverse.reason == "QUALIFIED"
        else 0.0
    )
    _, edge = reciprocal_quality(support, support)
    return ReciprocalPairDiagnostic(first, second, forward, reverse, support, edge)


def inspect_pair(graph: SparseNetwork, first: int, second: int) -> ReciprocalPairDiagnostic:
    """Pure production structure only; this supplies no event or mutation authority."""
    _check_graph(graph, False)
    return _pair(graph, first, second, False)


def _triangle(
    graph: SparseNetwork,
    members: tuple[int, int, int],
    pairs: dict[tuple[int, int], ReciprocalPairDiagnostic],
    adjacency: dict[int, dict[int, float]],
    component: bool,
) -> TriangleDiagnostic:
    own_pairs = tuple(
        pairs.get((i, j)) or _pair(graph, i, j, component) for i, j in combinations(members, 2)
    )
    reasons = []
    if not all(pair.edge for pair in own_pairs):
        reasons.append("NO_RECIPROCAL_TRIANGLE")
    cells = []
    for cell in members:
        neighbors = adjacency.get(cell, {})
        degree = sum(other in neighbors for other in members if other != cell)
        density = degree / 2
        numerator = sum(pair.support for pair in own_pairs if cell in (pair.first, pair.second))
        denominator = sum(value for _, value in sorted(neighbors.items()))
        specificity = numerator / denominator if denominator else 0.0
        count = len(graph.cell(cell).assembly_ids)
        cells.append(
            MemberStructuralDiagnostic(
                cell,
                degree,
                density,
                tuple(sorted(neighbors.items())),
                numerator,
                denominator,
                specificity,
                count,
            )
        )
        if degree < _parameter("d_min") or q6(density) < q6(_parameter("rho_core")):
            reasons.append(f"INSUFFICIENT_DENSITY:{cell}")
        if q6(specificity) < q6(_parameter("sigma_G")):
            reasons.append(f"INSUFFICIENT_SPECIFICITY:{cell}")
        if count >= int(_parameter("M_max")):
            reasons.append(f"MEMBERSHIP_CAPACITY:{cell}")
    return TriangleDiagnostic(members, own_pairs, tuple(cells), tuple(reasons))


def _analyze(graph: SparseNetwork, component: bool) -> ReciprocalStructureDiagnostic:
    _check_graph(graph, component)
    keys = sorted(
        {
            tuple(sorted((link.key.source.cell_id, link.key.target.cell_id)))
            for link in graph.synapses()
            if link.key.scope is SynapseScope.LOCAL
            and link.key.source.region is Region.LANGUAGE
            and link.key.target.region is Region.LANGUAGE
        }
    )
    pairs = {(i, j): _pair(graph, i, j, component) for i, j in keys}
    adjacency: dict[int, dict[int, float]] = {}
    for (i, j), pair in pairs.items():
        if pair.edge:
            adjacency.setdefault(i, {})[j] = pair.support
            adjacency.setdefault(j, {})[i] = pair.support
    # Intersect only actual reciprocal neighborhoods; no whole-region triples.
    triangles = []
    for i in sorted(adjacency):
        for j in sorted(k for k in adjacency[i] if k > i):
            for k in sorted(set(adjacency[i]) & set(adjacency[j])):
                if k > j:
                    triangles.append(_triangle(graph, (i, j, k), pairs, adjacency, component))
    return ReciprocalStructureDiagnostic(
        graph.structural_hash,
        tuple(c.cell_id for c in graph.stored_cells() if c.address.region is Region.LANGUAGE),
        tuple(pairs.values()),
        tuple(triangles),
        component,
    )


def inspect_structure(graph: SparseNetwork) -> ReciprocalStructureDiagnostic:
    return _analyze(graph, False)


def inspect_component_structure(graph: SparseNetwork) -> ReciprocalStructureDiagnostic:
    """Explicit fixture arithmetic only; never a trusted FORM event or birth."""
    return _analyze(graph, True)
