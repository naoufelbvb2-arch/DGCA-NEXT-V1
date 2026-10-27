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
