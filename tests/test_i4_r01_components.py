"""COMPONENT falsification only: no fixture is production FORM evidence."""

from dataclasses import FrozenInstanceError, replace
from types import MappingProxyType

import pytest

from dgca_next.contracts import CellAddress, SynapseKey, SynapseScope
from dgca_next.graph import FixtureBuilder, SparseNetwork, Synapse, SynapseState
from dgca_next.graph.assembly_support import (
    inspect_component_structure,
    inspect_pair,
    inspect_structure,
    reciprocal_quality,
)
from dgca_next.persistence.form_inspection import (
    FormEventDiagnostic,
    FormMemberWitnessDiagnostic,
    _project_candidates,
)


def component_graph(
    pairs, *, state=SynapseState.CONSOLIDATED, reverse=True, count=30, scope=SynapseScope.LOCAL
):
    graph = SparseNetwork()
    builder = FixtureBuilder(graph)
    builder.commit_cells(range(8192, 8192 + count), committed_event=0)
    indexes = {}
    for i, j in pairs:
        index = indexes.get(i, 0)
        builder.inject_slot(i, index, j)
        indexes[i] = index + 1
        for source, target in ((i, j), (j, i)) if reverse else ((i, j),):
            key = SynapseKey(
                CellAddress.from_cell_id(source), CellAddress.from_cell_id(target), scope
            )
            builder.add_synapse(
                Synapse(
                    key,
                    1 if scope is SynapseScope.ASSOCIATIVE else 0,
                    state,
                    1.0,
                    3.0,
                    0.0,
                    3,
                    2,
                    True,
                )
            )
    return graph


@pytest.mark.parametrize(
    "reverse,state",
    [
        (False, SynapseState.CONSOLIDATED),
        (True, SynapseState.CANDIDATE),
        (True, SynapseState.EPISODIC_INDEXED),
    ],
)
def test_only_reciprocal_consolidated_local_counts(reverse, state):
    graph = component_graph([(8192, 8193)], reverse=reverse)
    if state is not SynapseState.CONSOLIDATED:
        links = dict(graph._state.synapses)
        reverse_key = next(k for k in links if k.source.cell_id == 8193)
        links[reverse_key] = replace(links[reverse_key], state=state)
        graph._state = replace(graph._state, synapses=MappingProxyType(links))
    result = inspect_component_structure(graph)
    assert result.component_only and result.pairs[0].support == 0.0
    assert not result.pairs[0].edge and result.triangles == ()
    with pytest.raises(ValueError, match="FIXTURE_FORM_STRUCTURE_FORBIDDEN"):
        inspect_structure(graph)


@pytest.mark.parametrize(
    "reverse,edge",
    [(0.099999, False), (0.0999994, False), (0.0999996, True), (0.1, True), (0.100001, True)],
)
def test_numeric_only_quality_threshold(reverse, edge):
    # Legal consolidated records currently have a higher minimum Q; these
    # scalar boundary examples are strictly mathematical component checks.
    support, actual = reciprocal_quality(0.3, reverse)
    assert support == reverse and actual is edge


@pytest.mark.parametrize("invalid", [float("nan"), float("inf"), -0.1, 1.1, True])
def test_invalid_scalar_quality_fails_closed(invalid):
    with pytest.raises(ValueError, match="INVALID_RECIPROCAL_QUALITY"):
        reciprocal_quality(invalid, 0.3)


def test_associative_links_never_construct_reciprocal_structure():
    graph = component_graph(
        [(8192, 8193), (8192, 8194), (8193, 8194)], scope=SynapseScope.ASSOCIATIVE
    )
    result = inspect_component_structure(graph)
    assert result.pairs == result.triangles == ()


def test_specificity_uses_all_actual_reciprocal_neighbors_and_is_immutable():
    graph = component_graph([(8192, i) for i in range(8193, 8201)] + [(8193, 8194)])
    result = inspect_component_structure(graph)
    triangle = next(t for t in result.triangles if t.members == (8192, 8193, 8194))
    cell = triangle.cells[0]
    assert cell.degree == 2 and cell.density == 1.0
    assert len(cell.reciprocal_neighbors) == 8
    assert cell.specificity == pytest.approx(0.25)
    assert not triangle.eligible and "INSUFFICIENT_SPECIFICITY:8192" in triangle.reasons
    with pytest.raises(FrozenInstanceError):
        cell.degree = 0
    before = graph.structural_hash
    graph._state = replace(
        graph._state, synapses=MappingProxyType(dict(reversed(list(graph._state.synapses.items()))))
    )
    assert inspect_component_structure(graph) == result and graph.structural_hash == before


def test_empty_self_uncommitted_and_broken_physical_graph_fail_closed():
    empty = SparseNetwork()
    assert inspect_structure(empty).triangles == ()
    with pytest.raises(ValueError, match="INVALID_RECIPROCAL_PAIR"):
        inspect_pair(empty, 8192, 8192)
    pair = inspect_pair(empty, 8192, 8193)
    assert pair.support == 0 and pair.forward.reason == "UNCOMMITTED_ENDPOINT"
    graph = component_graph([(8192, 8193)])
    graph._state = replace(graph._state, reverse=MappingProxyType({}))
    with pytest.raises(ValueError, match="REVERSE_LATENT_INDEX_MISMATCH"):
        inspect_component_structure(graph)


def test_projected_seeds_are_event_ordered_disjoint_and_limited_to_twelve():
    pairs = []
    for first in range(8192, 8192 + 39, 3):
        pairs.extend([(first, first + 1), (first, first + 2), (first + 1, first + 2)])
    structure = inspect_component_structure(component_graph(pairs, count=39))
    witnesses = tuple(
        FormMemberWitnessDiagnostic(
            i, 1_000_000, True, 0, 1.0, 0.23, True, True, "OBS_ELIGIBLE_EMISSION"
        )
        for i in structure.committed
    )
    event = FormEventDiagnostic(1, 0, "a" * 64, "b" * 64, "c" * 64, witnesses)
    later = replace(event, event_id=2, event_order=1)
    candidates = _project_candidates(structure, (later, event))
    seeds = tuple(c for c in candidates if c.selected)
    assert len(seeds) == 12 and all(c.event_order == 0 for c in seeds)
    assert len({i for c in seeds for i in c.triangle.members}) == 36
    assert seeds[0].triangle.members == (8192, 8193, 8194)
    assert any("K_FORM_PER_END_REACHED" in c.reasons for c in candidates)
