"""Explicit numerical/component counterexamples, never production learning."""

from dataclasses import replace
from itertools import combinations
from types import MappingProxyType

import pytest

from dgca_next.contracts import CellAddress, SynapseKey, SynapseScope
from dgca_next.graph import FixtureBuilder, SparseNetwork, Synapse, SynapseState
from dgca_next.graph.assembly_support import inspect_component_structure
from dgca_next.graph.native_lifecycle import (
    guard_deferred,
    passes,
    plan_maintain_grow,
    quantized_sum,
    score,
)

A = (8192, 8193, 8194)


def supports(edges):
    result = {}
    for row in edges:
        i, j = row[:2]
        weight = row[2] if len(row) == 3 else 0.3
        result.setdefault(i, {})[j] = weight
        result.setdefault(j, {})[i] = weight
    return result


def plan(members, values, *, committed=None, memberships=None):
    return plan_maintain_grow(
        {0: members},
        values,
        memberships or {},
        frozenset(values) if committed is None else committed,
    )


def test_keep_is_distinct_from_form_density_and_specificity():
    cycle = tuple(range(8192, 8197))
    values = supports([(cycle[i], cycle[(i + 1) % 5]) for i in range(5)])
    assert all(passes(score(i, cycle, values), "rho_keep", "sigma_keep") for i in cycle)
    assert all(not passes(score(i, cycle, values), "rho_core", "sigma_G") for i in cycle)
    edits, evaluations = plan(cycle, values)
    assert not edits and evaluations[0].reason == "KEEP"
    values = supports(
        [
            *combinations(A, 2),
            *((i, 8200 + 3 * n + k, 0.8) for n, i in enumerate(A) for k in range(3)),
        ]
    )
    assert all(score(i, A, values).specificity == pytest.approx(0.2) for i in A)
    assert all(passes(score(i, A, values), "rho_keep", "sigma_keep") for i in A)
    assert all(not passes(score(i, A, values), "rho_core", "sigma_G") for i in A)
    assert not plan(A, values)[0]


def test_maintain_removes_lowest_failing_id_then_recomputes():
    members = tuple(range(8192, 8197))
    values = supports([(8192, 8193), (8193, 8194), *combinations(members[2:], 2)])
    edits, evaluations = plan(members, values)
    assert [(e.stage, e.before, e.after) for e in edits] == [
        ("MAINTAIN_REMOVE", members, members[1:]),
        ("MAINTAIN_REMOVE", members[1:], members[2:]),
    ]
    first = {v.cell_id: v.degree for v in evaluations[0].scores}
    second = {v.cell_id: v.degree for v in evaluations[1].scores}
    assert first[8193] == 2 and second[8193] == 1
    assert evaluations[2].reason == "KEEP"


def test_archive_is_terminal_removal_without_fake_live_memberships():
    edits, _ = plan(A, supports([(8192, 8193)]))
    assert len(edits) == 1 and edits[0].stage == "ARCHIVE"
    assert edits[0].before == A and edits[0].after == A[1:]
    assert not any(e.stage == "GROW_ADD" for e in edits)


def test_grow_ranks_actual_sum_then_physical_id_without_resort():
    values = supports([*combinations(A, 2), *((i, 8196) for i in A[:2]), *((i, 8195) for i in A)])
    edits, evaluations = plan(A, values)
    growth = [e for e in evaluations if e.stage == "GROW"]
    assert [e.cell_id for e in growth] == [8195, 8196]
    assert growth[0].rank_support == pytest.approx(0.9)
    assert growth[1].rank_support == pytest.approx(0.6)
    assert [e.after[-1] for e in edits] == [8195, 8196]


def test_rank_tie_is_q6_then_id_and_sums_are_not_clamped_to_one():
    assert quantized_sum(1.0355871969083743) == 1035587
    values = supports(
        [
            *combinations(A, 2),
            *((i, 8195, 0.30000011) for i in A),
            *((i, 8196, 0.30000012) for i in A),
        ]
    )
    _, evaluations = plan(A, values)
    assert [e.cell_id for e in evaluations if e.stage == "GROW"] == [8195, 8196]


def test_candidate_is_not_revisited_after_later_addition():
    values = supports(
        [*combinations(A, 2), (8192, 8195, 0.9), (8192, 8196), (8193, 8196), (8195, 8196)]
    )
    edits, evaluations = plan(A, values)
    assert [e.cell_id for e in evaluations if e.stage == "GROW"] == [8195, 8196]
    assert len(edits) == 1 and edits[0].after == (*A, 8196)
    assert passes(score(8195, (*A, 8195, 8196), values), "rho_G", "sigma_G")


def test_existing_members_keep_guards_are_rechecked_prospectively():
    members = tuple(range(8192, 8198))
    values = supports(
        [(members[i], members[(i + 1) % 6]) for i in range(6)] + [(i, 8200) for i in members[:3]]
    )
    edits, evaluations = plan(members, values)
    grow = next(e for e in evaluations if e.stage == "GROW")
    assert not edits and grow.reason == "EXISTING_MEMBER_KEEP_FAILED"
    assert passes(next(s for s in grow.scores if s.cell_id == 8200), "rho_G", "sigma_G")


@pytest.mark.parametrize(
    "invalid", ["uncommitted", "region", "capacity", "one_neighbor", "specificity"]
)
def test_grow_refuses_unqualified_candidates(invalid):
    candidate = 7 if invalid == "region" else 8195
    values = supports([*combinations(A, 2), *((i, candidate) for i in A)])
    committed = frozenset(values) - {candidate} if invalid == "uncommitted" else frozenset(values)
    memberships = {candidate: frozenset(range(12))} if invalid == "capacity" else {}
    if invalid == "one_neighbor":
        values = supports([*combinations(A, 2), (A[0], candidate)])
    if invalid == "specificity":
        values = supports(
            [
                *combinations(A, 2),
                *((i, candidate) for i in A),
                *((candidate, i, 0.9) for i in range(8200, 8204)),
            ]
        )
        committed = frozenset(values)
    assert not plan(A, values, committed=committed, memberships=memberships)[0]


def test_max_size_and_finite_neighborhood_enumeration():
    class NoIteration(frozenset):
        def __iter__(self):
            raise AssertionError("whole committed population scan")

    values = supports([*combinations(A, 2), *((i, 8195) for i in A)])
    assert plan(A, values, committed=NoIteration(values))[0][0].stage == "GROW_ADD"
    members = tuple(range(8192, 8208))
    values = supports(combinations((*members, 8208), 2))
    assert not plan(members, values)[0]


@pytest.mark.parametrize("defect", ["one_way", "candidate", "episodic", "associative", "latent"])
def test_physical_defects_never_supply_grow_support(defect):
    graph = SparseNetwork()
    builder = FixtureBuilder(graph)
    # Six episodic keys require the inherited floor(.10 * committed) cap.
    builder.commit_cells(range(8192, 8252), committed_event=0)
    used = {}
    for i, j in combinations((*A, 8195), 2):
        index = used.get(i, 0)
        builder.inject_slot(i, index, j)
        used[i] = index + 1
        for source, target in ((i, j), (j, i)):
            candidate = 8195 in (source, target)
            if candidate and defect == "one_way" and source == 8195:
                continue
            scope = (
                SynapseScope.ASSOCIATIVE
                if candidate and defect == "associative"
                else SynapseScope.LOCAL
            )
            state = (
                (
                    SynapseState.CANDIDATE
                    if defect == "candidate"
                    else SynapseState.EPISODIC_INDEXED
                    if defect == "episodic"
                    else SynapseState.CONSOLIDATED
                )
                if candidate
                else SynapseState.CONSOLIDATED
            )
            builder.add_synapse(
                Synapse(
                    SynapseKey(
                        CellAddress.from_cell_id(source), CellAddress.from_cell_id(target), scope
                    ),
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
    if defect == "latent":
        graph._state = replace(
            graph._state, slots=MappingProxyType({}), reverse=MappingProxyType({})
        )
        with pytest.raises(ValueError):
            inspect_component_structure(graph)
        return
    structure = inspect_component_structure(graph)
    values = supports((p.first, p.second, p.support) for p in structure.pairs if p.edge)
    assert not plan(A, values, committed=frozenset((*A, 8195)))[0]


@pytest.mark.parametrize(
    "members", [((8192, 8193, 8194), (8195, 8196, 8197)), (tuple(range(8192, 8198)),)]
)
def test_deferred_operators_fail_closed_conservatively(members):
    with pytest.raises(ValueError, match="I4_UNIMPLEMENTED_MERGE_SPLIT"):
        guard_deferred(members)
    guard_deferred(((*A, 8195),))
