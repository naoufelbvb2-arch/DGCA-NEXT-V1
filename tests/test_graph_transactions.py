import copy
import os
import subprocess
import sys
from dataclasses import replace
from types import MappingProxyType

import pytest

from dgca_next.graph import (
    FixtureBuilder,
    GraphInvariantError,
    InjectedFailure,
    MutationStage,
    SparseNetwork,
    validate_graph,
)


@pytest.mark.parametrize("stage", MutationStage)
def test_i1_t22_injected_shadow_failure_at_every_resource(
    graph_pair, stage, key_factory, record_factory
):
    graph, builder = graph_pair
    before = graph.structural_hash
    tx = builder.transaction(fail_at=stage)
    with pytest.raises(InjectedFailure, match=stage.value), tx:
        tx.commit_cells([8195], committed_event=0)
        tx.inject_slot(8193, 0, 8195)
        key = key_factory(8193, 8195)
        tx.reserve(key, 8192)
        tx.add_synapse(record_factory(key))
        assert graph.structural_hash == before  # No intermediate publication.
    assert stage in tx.visited_stages
    assert graph.structural_hash == before
    assert validate_graph(graph).synapses == 0
    with pytest.raises(ValueError, match="CLOSED_FIXTURE_TRANSACTION"):
        tx.commit()


@pytest.mark.parametrize(
    "stage",
    [MutationStage.LINK, MutationStage.RESERVATION, MutationStage.BUDGET, MutationStage.PUBLISH],
)
def test_i1_t16_transfer_failure_restores_claims_and_budgets(graph_pair, record_factory, stage):
    graph, builder = graph_pair
    link = record_factory()
    builder.reserve(link.key, 8192)
    builder.reserve(link.key, 8193)
    before = graph.structural_hash
    with pytest.raises(InjectedFailure), builder.transaction(fail_at=stage) as tx:
        tx.add_synapse(link)
    assert graph.structural_hash == before
    assert graph.synapse(link.key) is None
    assert graph.reservation_claimants(link.key) == frozenset({8192, 8193})
    assert graph.outgoing_usage(8192).total == 1
    validate_graph(graph)


@pytest.mark.parametrize(
    "stage", [MutationStage.SLOT, MutationStage.REVERSE_INDEX, MutationStage.PUBLISH]
)
def test_i1_t05_fixture_teardown_rollback_restores_both_views(graph_pair, stage):
    graph, builder = graph_pair
    before = graph.structural_hash
    with pytest.raises(InjectedFailure), builder.transaction(fail_at=stage) as tx:
        tx.remove_fixture_slot(8192, 0)
    assert graph.structural_hash == before
    assert graph.reverse_latent(8193) == ((8192, 0),)
    validate_graph(graph)


def test_i1_t21_audit_after_each_accepted_mutation(graph_pair, key_factory, record_factory):
    graph, builder = graph_pair
    operations = [
        lambda: builder.inject_slot(8193, 0, 8194),
        lambda: builder.reserve(key_factory(), 8192),
        lambda: builder.reserve(key_factory(), 8193),
        lambda: builder.release(key_factory(), 8192),
        lambda: builder.add_synapse(record_factory()),
        lambda: builder.set_memberships(8192, frozenset(range(12))),
        lambda: builder.remove_synapse(key_factory()),
        lambda: builder.pin_slot(8193, 0, 8192),
        lambda: builder.protect_slot(8193, 0),
    ]
    for operation in operations:
        operation()
        before = graph.structural_hash
        report = validate_graph(graph)
        assert report.logical_cells == 12288
        assert graph.structural_hash == before


@pytest.mark.parametrize(
    "damage,reason",
    [
        ("reverse", "REVERSE_LATENT_INDEX_MISMATCH"),
        ("outgoing", "OUTGOING_INDEX_MISMATCH"),
        ("slot_count", "INVALID_SLOT_COUNT"),
        ("slot_category", "INVALID_SLOT_CATEGORY_REGION"),
        ("cell_identity", "CELL_ID_ADDRESS_MISMATCH"),
        ("eligibility", "MISSING_LATENT_ELIGIBILITY"),
        ("wiring_log", "WIRING_LOG_MISMATCH"),
        ("reservation", "LIVE_KEY_RESERVATION_NOT_TRANSFERRED"),
        ("numeric_state", "INVALID_GRAPH_SCHEMA"),
    ],
)
def test_independent_audit_detects_internal_corruption(graph_pair, record_factory, damage, reason):
    graph, builder = graph_pair
    link = record_factory()
    builder.add_synapse(link)
    state = graph._state  # Deliberate internal corruption; never a public write API.
    if damage == "reverse":
        graph._state = replace(state, reverse=MappingProxyType({}))
    elif damage == "outgoing":
        graph._state = replace(state, outgoing=MappingProxyType({}))
    elif damage == "slot_count":
        graph._state = replace(state, slots=MappingProxyType({8192: state.slots[8192][:-1]}))
    elif damage == "slot_category":
        slots = state.slots[8192]
        altered = (replace(slots[0], index=1),) + slots[1:]
        graph._state = replace(state, slots=MappingProxyType({8192: altered}))
    elif damage == "cell_identity":
        cells = dict(state.cells)
        cells[8192] = cells[8193]
        graph._state = replace(state, cells=MappingProxyType(cells))
    elif damage == "eligibility":
        graph._state = replace(state, slots=MappingProxyType({}), reverse=MappingProxyType({}))
    elif damage == "wiring_log":
        graph._state = replace(state, wiring_log=())
    elif damage == "reservation":
        graph._state = replace(state, reservations=MappingProxyType({link.key: frozenset({8192})}))
    else:
        malformed = copy.copy(link)
        object.__setattr__(malformed, "S", float("nan"))
        graph._state = replace(state, synapses=MappingProxyType({link.key: malformed}))
    corrupted = graph._state
    with pytest.raises(GraphInvariantError, match=reason):
        validate_graph(graph)
    assert graph._state is corrupted  # Audit never repairs or mutates its input.


def test_bad_mutation_aborts_whole_batch_even_if_error_is_caught(graph_pair):
    graph, builder = graph_pair
    before = graph.structural_hash
    tx = builder.transaction()
    tx.commit_cells([8195], committed_event=0)
    with pytest.raises(ValueError):
        tx.inject_slot(8192, 0, 8194)
    with pytest.raises(ValueError, match="CLOSED_FIXTURE_TRANSACTION"):
        tx.commit()
    assert graph.structural_hash == before


def test_rollback_and_single_use(graph_pair):
    graph, builder = graph_pair
    before = graph.structural_hash
    tx = builder.transaction()
    tx.commit_cells([8195], committed_event=0)
    tx.rollback()
    tx.rollback()
    with pytest.raises(ValueError, match="CLOSED_FIXTURE_TRANSACTION"):
        tx.inject_slot(8193, 0, 8194)
    assert graph.structural_hash == before
    with pytest.raises(RuntimeError), builder.transaction() as tx:
        tx.commit_cells([8195], committed_event=0)
        raise RuntimeError("fixture body failed")
    assert graph.structural_hash == before


def test_stale_shadow_cannot_overwrite_newer_commit(graph_pair):
    graph, builder = graph_pair
    first, second = builder.transaction(), builder.transaction()
    first.commit_cells([8195], committed_event=0)
    second.commit_cells([8196], committed_event=0)
    first.commit()
    before = graph.structural_hash
    with pytest.raises(ValueError, match="STALE_SHADOW_TRANSACTION"):
        second.commit()
    assert graph.structural_hash == before
    assert graph.cell(8195).committed and not graph.cell(8196).committed


def test_exact_retry_does_not_invalidate_existing_shadow(graph_pair):
    graph, builder = graph_pair
    tx = builder.transaction()
    builder.commit_cells([8192], committed_event=0)
    tx.commit_cells([8195], committed_event=0)
    tx.commit()
    assert graph.cell(8195).committed


def test_failed_independent_prepublication_audit_never_publishes(graph_pair):
    graph, builder = graph_pair
    before = graph.structural_hash
    tx = builder.transaction()
    tx._shadow.reverse.clear()  # Simulate a writer bug for the independent audit.
    with pytest.raises(GraphInvariantError, match="REVERSE_LATENT_INDEX_MISMATCH"):
        tx.commit()
    assert graph.structural_hash == before


def test_i1_t23_reordered_fixture_insertions_are_canonical(key_factory, record_factory):
    hashes = []
    for reverse in (False, True):
        graph = SparseNetwork()
        builder = FixtureBuilder(graph)
        targets = list(range(8193, 8199))
        with builder.transaction() as tx:
            tx.commit_cells([8192, *targets][:: -1 if reverse else 1], committed_event=0)
            for target in targets[:: -1 if reverse else 1]:
                tx.inject_slot(target, 0, 8192)
                key = key_factory(8192, target)
                tx.reserve(key, target)
                tx.add_synapse(record_factory(key))
        validate_graph(graph)
        hashes.append(graph.structural_hash)
    assert len(set(hashes)) == 1


def test_i1_t23_debug_hash_independent_of_process_hash_seed(tmp_path):
    script = """from dgca_next.contracts import CellAddress, SynapseKey, SynapseScope
from dgca_next.graph import FixtureBuilder, SparseNetwork, Synapse, SynapseState
g = SparseNetwork()
b = FixtureBuilder(g)
with b.transaction() as t:
    t.commit_cells(range(8192, 8198), committed_event=0)
    keys = {
        SynapseKey(CellAddress.from_cell_id(8192),
                   CellAddress.from_cell_id(i), SynapseScope.LOCAL)
        for i in range(8193, 8198)
    }
    for k in keys:
        t.inject_slot(k.target.cell_id, 0, 8192)
        t.add_synapse(Synapse(k, 0, SynapseState.CANDIDATE, .6, 1., 0., 1, 2, True))
g.validate_graph()
print(g.structural_hash)
"""
    outputs = []
    for hash_seed in ("7", "91"):
        result = subprocess.run(
            [sys.executable, "-c", script],
            cwd=tmp_path,
            env={**os.environ, "PYTHONHASHSEED": hash_seed},
            check=True,
            text=True,
            capture_output=True,
        )
        outputs.append(result.stdout.strip())
    assert outputs[0] == outputs[1]


def test_mutable_aliases_not_exposed(graph_pair, key_factory):
    graph, builder = graph_pair
    builder.reserve(key_factory(), 8192)
    for value in (
        graph.latent_slots(8192),
        graph.reverse_latent(8193),
        graph.outgoing_keys(8192),
        graph.reserved_keys(),
        graph.stored_cells(),
    ):
        assert type(value) is tuple
    assert type(graph.reservation_claimants(key_factory())) is frozenset
    with pytest.raises(TypeError):
        graph._state.cells[8192] = graph.cell(8193)


def test_nested_transactions_and_invalid_injection_stage_rejected(graph_pair):
    _, builder = graph_pair
    tx = builder.transaction()
    with pytest.raises(ValueError, match="NESTED"):
        tx.transaction()
    tx.rollback()
    with pytest.raises(ValueError, match="MutationStage"):
        builder.transaction(fail_at="SLOT")


def test_publication_hooks_never_observe_half_state(graph_pair, key_factory, record_factory):
    graph, builder = graph_pair
    before = graph.structural_hash
    tx = builder.transaction()
    visited = []

    def observe(stage):
        visited.append(stage)
        assert graph.structural_hash == before
        validate_graph(graph)

    tx._shadow.hook = observe
    with tx:
        tx.commit_cells([8195], committed_event=0)
        tx.inject_slot(8193, 0, 8195)
        key = key_factory(8193, 8195)
        tx.reserve(key, 8192)
        tx.add_synapse(record_factory(key))
    assert set(visited) == set(MutationStage)
    assert graph.structural_hash != before
    # Even the closed mutable shadow cannot mutate published mapping containers.
    tx._shadow.cells.clear()
    tx._shadow.reverse.clear()
    assert graph.cell(8195).committed
    validate_graph(graph)


def test_before_image_audit_prevents_pin_removal(graph_pair):
    graph, builder = graph_pair
    builder.pin_slot(8192, 0, 8192)
    before = graph.structural_hash
    tx = builder.transaction()
    slots = tx._shadow.slots[8192]
    tx._shadow.slots[8192] = (replace(slots[0], pin_owners=frozenset()),) + slots[1:]
    with pytest.raises(GraphInvariantError, match="CANDIDATE_PIN_REMOVED"):
        tx.commit()
    assert graph.structural_hash == before


def test_before_image_audit_prevents_consolidated_removal(graph_pair, record_factory):
    from dgca_next.graph import SynapseState

    graph, builder = graph_pair
    link = record_factory(state=SynapseState.CONSOLIDATED, E_ext=3.0, external_root_count=2)
    builder.add_synapse(link)
    before = graph.structural_hash
    tx = builder.transaction()
    tx._shadow.synapses.clear()
    tx._shadow.outgoing.clear()
    with pytest.raises(GraphInvariantError, match="PROTECTED_SYNAPSE_CHANGED"):
        tx.commit()
    assert graph.structural_hash == before


def test_audit_rejects_uncommitted_pin_owner(graph_pair):
    graph, _ = graph_pair
    slots = graph._state.slots[8192]
    altered = (replace(slots[0], pin_owners=frozenset({9000})),) + slots[1:]
    graph._state = replace(graph._state, slots=MappingProxyType({8192: altered}))
    with pytest.raises(GraphInvariantError, match="UNCOMMITTED_PIN_OWNER"):
        validate_graph(graph)
