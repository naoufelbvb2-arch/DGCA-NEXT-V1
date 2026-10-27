from collections import Counter

import pytest

from dgca_next.contracts import Region
from dgca_next.graph import (
    FixtureBuilder,
    FixtureEventSnapshot,
    FixtureReceiver,
    SlotCategory,
    SparseNetwork,
)


@pytest.mark.parametrize("region", Region)
def test_i1_t04_slot_schema(region):
    slots = SparseNetwork().latent_slots(4096 * region.value)
    assert tuple(s.index for s in slots) == tuple(range(24))
    assert Counter(s.category for s in slots) == dict.fromkeys(SlotCategory, 6)
    assert all(s.target_id is None and not s.protected and not s.pinned for s in slots)
    assert all(s.permitted_region is region for s in slots[:12])
    for category in (SlotCategory.COACTIVE_INTER, SlotCategory.TOPOGRAPHIC):
        counts = Counter(s.permitted_region for s in slots if s.category is category)
        assert counts == {other: 3 for other in Region if other is not region}
    assert [s.recyclable_category for s in slots] == [True] * 6 + [False] * 6 + [True] * 6 + [
        False
    ] * 6


def test_i1_t26_unverified_event_fails_closed_without_mutation():
    graph = SparseNetwork()
    with pytest.raises(ValueError, match="UNVERIFIED_EVENT_SNAPSHOT"):
        graph.initialize_latent_neighborhoods()
    assert graph.stored_cell_count == 0


@pytest.mark.parametrize("direction", ["neither", "forward", "reverse", "both"])
def test_i1_t06_either_endpoint_eligibility(direction):
    graph = SparseNetwork()
    builder = FixtureBuilder(graph)
    builder.commit_cells([8192, 8193], committed_event=0)
    if direction in ("forward", "both"):
        builder.inject_slot(8192, 0, 8193)
    if direction in ("reverse", "both"):
        builder.inject_slot(8193, 0, 8192)
    assert graph.structurally_eligible(8192, 8193) == (direction != "neither")
    assert graph.structurally_eligible(8193, 8192) == (direction != "neither")
    assert not graph.structurally_eligible(8192, 8192)


def test_i1_t05_forward_reverse_primitive_and_failed_edit(graph_pair):
    graph, builder = graph_pair
    assert graph.reverse_latent(8193) == ((8192, 0),)
    before = graph.structural_hash
    builder.inject_slot(8192, 0, 8193)
    assert graph.structural_hash == before
    with pytest.raises(ValueError, match="DUPLICATE_LATENT_TARGET"):
        builder.inject_slot(8192, 1, 8193)
    with pytest.raises(ValueError, match="CONFLICTING_DUPLICATE_SLOT"):
        builder.inject_slot(8192, 0, 8194)
    assert graph.structural_hash == before
    builder.remove_fixture_slot(8192, 0)
    assert graph.reverse_latent(8193) == ()
    assert graph.latent_slots(8192)[0].target_id is None


@pytest.mark.parametrize("index,target", [(6, 8193), (18, 0)])
def test_i1_t07_fixed_slot_cannot_recycle(index, target):
    graph = SparseNetwork()
    builder = FixtureBuilder(graph)
    builder.commit_cells([8192, target], committed_event=0)
    builder.inject_slot(8192, index, target)
    before = graph.structural_hash
    with pytest.raises(ValueError, match="RECYCLE_BLOCKED_FIXED"):
        builder.recycle_slot(8192, index)
    with pytest.raises(ValueError, match="RECYCLE_BLOCKED_FIXED"):
        builder.remove_fixture_slot(8192, index)
    assert graph.structural_hash == before


@pytest.mark.parametrize("protection", ["live", "reverse_live", "pin", "protected"])
def test_i1_t08_protection_blocks_recycling(graph_pair, protection, key_factory, record_factory):
    graph, builder = graph_pair
    if protection in ("live", "reverse_live"):
        key = key_factory() if protection == "live" else key_factory(8193, 8192)
        builder.add_synapse(record_factory(key))
    elif protection == "pin":
        builder.pin_slot(8192, 0, 8192)
    else:
        builder.protect_slot(8192, 0)
    before = graph.structural_hash
    diagnostic = (
        "RECYCLE_BLOCKED_CANDIDATE" if protection == "pin" else "RECYCLE_BLOCKED_LIVE_OR_PROTECTED"
    )
    with pytest.raises(ValueError, match=diagnostic):
        builder.recycle_slot(8192, 0)
    assert graph.structural_hash == before


def test_i1_t09_no_recycling_without_novelty_authority(graph_pair):
    graph, builder = graph_pair
    before = graph.structural_hash
    with pytest.raises(ValueError, match="UNVERIFIED_NOVELTY"):
        builder.recycle_slot(8192, 0)
    assert graph.structural_hash == before


def test_i1_t09_production_recycling_policy_execution(graph_pair):
    graph, _ = graph_pair
    before = graph.structural_hash
    assert graph.automatic_recycling_enabled is False
    with pytest.raises(ValueError, match="UNVERIFIED_NOVELTY"):
        graph.recycle_slot(8192, 0)
    assert graph.structural_hash == before


def test_i1_t26_production_initializer_policy_execution():
    graph = SparseNetwork()
    event = FixtureEventSnapshot(
        1, 1, 0, 0, direct_receivers=(FixtureReceiver(8192, 500000),), birth_ids=frozenset({8192})
    )
    FixtureBuilder(graph).initialize_cohort(event)
    assert graph.stored_cell_count == 1
    assert graph.occupied_slot_count == 12
    assert graph.initialization(8192) is not None
    assert all(
        s.target_id is not None for s in graph.latent_slots(8192) if not s.recyclable_category
    )
    graph.validate_graph()


@pytest.mark.parametrize(
    "index,target,reason",
    [
        (0, 0, "slot region"),
        (12, 4096, "slot region"),
        (0, 8192, "LATENT_SELF_TARGET"),
        (6, 8500, "LOCAL_SLOT_OUTSIDE_VICINITY"),
        (24, 8193, "INVALID_SLOT_INDEX"),
        (True, 8193, "INVALID_SLOT_INDEX"),
    ],
)
def test_slot_injection_rejects_illegal_targets(index, target, reason):
    graph = SparseNetwork()
    builder = FixtureBuilder(graph)
    builder.commit_cells([0, 4096, 8192, 8193, 8500], committed_event=0)
    before = graph.structural_hash
    with pytest.raises(ValueError, match=reason):
        builder.inject_slot(8192, index, target)
    assert graph.structural_hash == before


def test_i1_t17_full_source_latent_uses_target_side_eligibility(key_factory, record_factory):
    graph = SparseNetwork()
    builder = FixtureBuilder(graph)
    targets = [*range(8193, 8205), *range(3), *range(4096, 4099), *range(3, 6), *range(4099, 4102)]
    builder.commit_cells([8192, 8300, *targets], committed_event=0)
    for index, target in enumerate(targets):
        builder.inject_slot(8192, index, target)
    builder.inject_slot(8300, 0, 8192)
    key = key_factory(8192, 8300)
    builder.add_synapse(record_factory(key))
    assert all(slot.target_id is not None for slot in graph.latent_slots(8192))
    assert graph.structurally_eligible(8192, 8300)
    assert graph.outgoing_usage(8192).total == 1


def test_i1_t18_overlapping_physical_role_fixture(key_factory):
    graph = SparseNetwork()
    builder = FixtureBuilder(graph)
    builder.commit_cells(range(8192, 8197), committed_event=0)
    # Two P, two C, two Y positions, with physical overlap. No role on Cell.
    p, c, y = (8193, 8194), (8193, 8195), (8194, 8196)
    for index, target in enumerate(sorted(set(p + c + y))):
        builder.inject_slot(8192, index, target)
        builder.pin_slot(8192, index, 8192)
    from dgca_next.contracts import SynapseScope

    keys = [
        *(key_factory(i, 8192, SynapseScope.ASSOCIATIVE) for i in p),
        *(key_factory(i, 8192) for i in c),
        *(key_factory(8192, i, SynapseScope.ASSOCIATIVE) for i in y),
    ]
    for key in keys + keys:
        builder.reserve(key, 8192)
    assert graph.occupied_slot_count == 4
    assert len(graph.reserved_keys()) == 6
    assert graph.outgoing_usage(8193).total == 2
    assert graph.outgoing_usage(8192).total == 2
