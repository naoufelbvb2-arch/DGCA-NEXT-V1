import pytest

from dgca_next.contracts import SynapseScope
from dgca_next.graph import FixtureBuilder, SparseNetwork, SynapseState


@pytest.mark.parametrize("reservation", [False, True])
def test_i1_t13_outgoing_cap_real_distinct_eligible_pairs(reservation, key_factory, record_factory):
    graph = SparseNetwork()
    builder = FixtureBuilder(graph)
    builder.commit_cells(range(8192, 8258), committed_event=0)
    for target in range(8193, 8258):
        builder.inject_slot(target, 0, 8192)
    for target in range(8193, 8257):
        key = key_factory(8192, target)
        builder.reserve(key, 8192) if reservation else builder.add_synapse(record_factory(key))
    assert graph.outgoing_usage(8192).total == 64
    assert graph.outgoing_usage(8193).total == 0  # Incoming does not debit target.
    before = graph.structural_hash
    key = key_factory(8192, 8257)
    with pytest.raises(ValueError, match="SOURCE_OUTGOING_CAPACITY"):
        builder.reserve(key, 8192) if reservation else builder.add_synapse(record_factory(key))
    assert graph.structural_hash == before


@pytest.mark.parametrize("scope", [SynapseScope.CROSS_TERRITORY, SynapseScope.ASSOCIATIVE])
def test_i1_t14_cross_outgoing_cap(key_factory, record_factory, scope):
    graph = SparseNetwork()
    builder = FixtureBuilder(graph)
    builder.commit_cells([8192, *range(13)], committed_event=0)
    for target in range(13):
        builder.inject_slot(target, 15, 8192)  # VISION inter group for LANGUAGE.
    for target in range(12):
        builder.add_synapse(record_factory(key_factory(8192, target, scope)))
    assert graph.outgoing_usage(8192).cross == 12
    before = graph.structural_hash
    with pytest.raises(ValueError, match="CROSS_OUTGOING_CAPACITY"):
        builder.add_synapse(record_factory(key_factory(8192, 12, scope)))
    assert graph.structural_hash == before


def test_i1_t15_unique_key_claimants_and_idempotent_release(graph_pair, key_factory):
    graph, builder = graph_pair
    key = key_factory()
    builder.reserve(key, 8192)
    builder.reserve(key, 8193)
    before = graph.structural_hash
    builder.reserve(key, 8193)
    assert graph.structural_hash == before
    assert graph.outgoing_usage(8192).total == 1
    assert graph.reservation_claimants(key) == frozenset({8192, 8193})
    builder.release(key, 8192)
    assert graph.outgoing_usage(8192).total == 1
    builder.release(key, 8193)
    builder.release(key, 8193)
    assert graph.reserved_keys() == ()
    assert graph.outgoing_usage(8192).total == 0


def test_i1_t16_reservation_to_live_no_double_debit(graph_pair, record_factory):
    graph, builder = graph_pair
    record = record_factory()
    builder.reserve(record.key, 8192)
    builder.reserve(record.key, 8193)
    builder.add_synapse(record)
    assert graph.outgoing_usage(8192).total == 1
    assert graph.reserved_keys() == ()
    builder.reserve(record.key, 8192)
    builder.release(record.key, 8193)
    assert graph.outgoing_usage(8192).total == 1
    builder.remove_synapse(record.key)
    builder.remove_synapse(record.key)
    assert graph.outgoing_usage(8192).total == 0


def test_episodic_cap_and_membership_cap(key_factory, record_factory):
    graph = SparseNetwork()
    builder = FixtureBuilder(graph)
    builder.commit_cells(range(8192, 8242), committed_event=0)
    for target in range(8193, 8198):
        builder.inject_slot(target, 0, 8192)
    for target in range(8193, 8197):
        builder.add_synapse(
            record_factory(key_factory(8192, target), state=SynapseState.EPISODIC_INDEXED)
        )
    assert graph.outgoing_usage(8192).episodic == 4
    before = graph.structural_hash
    with pytest.raises(ValueError, match="EPISODIC_OUTGOING_CAPACITY"):
        builder.add_synapse(
            record_factory(key_factory(8192, 8197), state=SynapseState.EPISODIC_INDEXED)
        )
    assert graph.structural_hash == before
    builder.set_memberships(8192, frozenset(range(12)))
    before = graph.structural_hash
    with pytest.raises(ValueError, match="M_max=12"):
        builder.set_memberships(8192, frozenset(range(13)))
    assert graph.structural_hash == before


def test_network_episodic_cap(graph_pair, record_factory):
    graph, builder = graph_pair
    before = graph.structural_hash
    with pytest.raises(ValueError, match="NETWORK_EPISODIC_CAPACITY"):
        builder.add_synapse(record_factory(state=SynapseState.EPISODIC_INDEXED))
    assert graph.structural_hash == before


@pytest.mark.parametrize("reverse", [False, True])
def test_combined_live_and_prospective_keys_use_one_shadow(reverse, key_factory, record_factory):
    graph = SparseNetwork()
    builder = FixtureBuilder(graph)
    with builder.transaction() as tx:
        tx.commit_cells(range(8192, 8258), committed_event=0)
        for target in range(8193, 8258):
            tx.inject_slot(target, 0, 8192)
        for target in range(8193, 8256):
            tx.add_synapse(record_factory(key_factory(8192, target)))
    assert graph.outgoing_usage(8192).total == 63
    before = graph.structural_hash
    with pytest.raises(ValueError, match="SOURCE_OUTGOING_CAPACITY"), builder.transaction() as tx:
        for target in [8257, 8256] if reverse else [8256, 8257]:
            tx.reserve(key_factory(8192, target), 8192)
    assert graph.structural_hash == before
    assert graph.reserved_keys() == ()
    graph.validate_graph()


@pytest.mark.parametrize("case", ["outgoing", "cross", "episodic"])
def test_independent_audit_recomputes_caps(case, key_factory, record_factory):
    from dataclasses import replace
    from types import MappingProxyType

    from dgca_next.graph import GraphInvariantError

    graph = SparseNetwork()
    builder = FixtureBuilder(graph)
    targets = list(range(13)) if case == "cross" else list(range(8193, 8258))
    scope = SynapseScope.ASSOCIATIVE if case == "cross" else SynapseScope.LOCAL
    with builder.transaction() as tx:
        tx.commit_cells([8192, *targets], committed_event=0)
        for target in targets:
            tx.inject_slot(target, 15 if case == "cross" else 0, 8192)
    chosen = targets[:5] if case == "episodic" else targets
    state = SynapseState.EPISODIC_INDEXED if case == "episodic" else SynapseState.CANDIDATE
    records = {
        key_factory(8192, target, scope): record_factory(
            key_factory(8192, target, scope), state=state
        )
        for target in chosen
    }
    # Corrupt only internal bookkeeping, with otherwise legal endpoints/D/records.
    graph._state = replace(
        graph._state,
        synapses=MappingProxyType(records),
        outgoing=MappingProxyType({8192: frozenset(records)}),
    )
    diagnostic = {
        "outgoing": "SOURCE_OUTGOING_CAPACITY",
        "cross": "CROSS_OUTGOING_CAPACITY",
        "episodic": "EPISODIC_OUTGOING_CAPACITY",
    }[case]
    with pytest.raises(GraphInvariantError, match=diagnostic):
        graph.validate_graph()
