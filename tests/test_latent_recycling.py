from dataclasses import FrozenInstanceError, replace

import pytest

from dgca_next.contracts import EventMode, EventOrigin, SynapseScope
from dgca_next.graph import (
    FixtureBuilder,
    FixtureEventSnapshot,
    FixtureFrontier,
    FixtureLocalNovelty,
    FixtureReceiver,
    InjectedFailure,
    MutationStage,
    SparseNetwork,
    SynapseState,
)
from dgca_next.graph.recycling import completed_close_credit


@pytest.fixture
def recycling_fixture():
    graph = SparseNetwork()
    builder = FixtureBuilder(graph)
    builder.commit_cells([10000, 11000, *range(4096, 4136)], committed_event=0)
    birth = FixtureEventSnapshot(
        1,
        1,
        0,
        0,
        direct_receivers=(FixtureReceiver(8192, 500000), FixtureReceiver(9000, 500000)),
        birth_ids=frozenset({8192, 9000}),
    )
    builder.initialize_cohort(birth)
    event = FixtureEventSnapshot(
        2,
        4,
        0,
        100,
        frontier=(FixtureFrontier(10000, 0.8), FixtureFrontier(11000, 0.6)),
        direct_receivers=(FixtureReceiver(8192, 500000), FixtureReceiver(9000, 500000)),
    )
    return graph, builder, event, FixtureLocalNovelty(event, 8192, 0.0)


@pytest.mark.parametrize("closes", [0, 99, 100, 101])
def test_l01_t06_exact_completed_close_boundary(recycling_fixture, closes):
    graph, builder, event, _ = recycling_fixture
    event = replace(event, completed_external_closes=closes)
    novelty = FixtureLocalNovelty(event, 8192, 0.0)
    before = graph.structural_hash
    if closes < 100:
        with pytest.raises(ValueError, match="CONFIRMATION_WINDOW_NOT_ELAPSED"):
            builder.recycle_slot(8192, 0, event=event, novelty=novelty)
        assert graph.structural_hash == before
    else:
        builder.recycle_slot(8192, 0, event=event, novelty=novelty)
        assert graph.latent_slots(8192)[0].target_id == 10000
        assert graph.latent_slots(9000)[0].target_id == 10000
    graph.validate_graph()


@pytest.mark.parametrize(
    "mode,origin,completed,credit",
    [
        (EventMode.LEARN, EventOrigin.EXTERNAL_DIRECT, True, 1),
        (EventMode.LEARN, EventOrigin.EXTERNAL_DIRECT, False, 0),  # OPEN/ABORT add no credit.
        (EventMode.REPLAY, EventOrigin.REPLAY_RECALLED, True, 0),
        (EventMode.RETRIEVE, EventOrigin.READ_ONLY_OBSERVED, True, 0),
        (EventMode.GENERATE, EventOrigin.INTERNAL_SELECTED, True, 0),
        (EventMode.GENERATE, EventOrigin.READ_ONLY_OBSERVED, True, 0),
    ],
)
def test_l01_t05_t06_nonexternal_or_incomplete_activity_does_not_age(
    mode, origin, completed, credit
):
    assert completed_close_credit(mode, origin, completed=completed) == credit


def test_l01_t05_rejected_trigger_retains_permitted_physical_birth_without_evidence(
    recycling_fixture,
):
    graph, builder, event, _ = recycling_fixture
    before = graph.structural_hash
    with pytest.raises(ValueError, match="UNVERIFIED_NOVELTY"):
        builder.recycle_slot(8192, 0, event=event)
    assert graph.structural_hash == before
    assert graph.cell(8192).committed
    assert graph.latent_slots(8192)[0].assignment.pending_birth is True
    assert graph.synapses() == graph.reserved_keys() == ()
    assert graph.recycling_log() == ()


@pytest.mark.parametrize("proof", [None, 0.9, 1, {"verified": True}])
def test_l01_t06_arbitrary_novelty_never_authorizes_physical_recycling(recycling_fixture, proof):
    graph, builder, event, _ = recycling_fixture
    before = graph.structural_hash
    with pytest.raises(ValueError, match="UNVERIFIED_NOVELTY"):
        builder.recycle_slot(8192, 0, event=event, novelty=proof)
    assert graph.structural_hash == before


def test_l01_t06_fixture_or_protocol_shaped_proof_cannot_enable_production(recycling_fixture):
    graph, _, event, novelty = recycling_fixture
    before = graph.structural_hash

    class CallerClaim:
        fixture_only = False
        receiver_id = 8192
        novelty = 1.0

    claim = CallerClaim()
    claim.event = event
    for proof in (novelty, claim):
        with pytest.raises(ValueError, match="UNVERIFIED_NOVELTY"):
            graph.recycle_slot(8192, 0, novelty=proof)
    assert graph.automatic_recycling_enabled is False
    with pytest.raises(AttributeError):
        graph.automatic_recycling_enabled = True
    assert graph.structural_hash == before


@pytest.mark.parametrize(
    "prediction,passes", [(0.0, True), (0.35, True), (0.3500003, False), (0.5, False), (1.0, False)]
)
def test_l01_t06_fixture_residual_threshold_is_not_branch_novelty(
    recycling_fixture, prediction, passes
):
    graph, builder, event, _ = recycling_fixture
    novelty = FixtureLocalNovelty(event, 8192, prediction)
    if passes:
        builder.recycle_slot(8192, 0, event=event, novelty=novelty)
        assert len(graph.recycling_log()) == 1
    else:
        before = graph.structural_hash
        with pytest.raises(ValueError, match="UNVERIFIED_NOVELTY"):
            builder.recycle_slot(8192, 0, event=event, novelty=novelty)
        assert graph.structural_hash == before


@pytest.mark.parametrize(
    "changes",
    [{"exposure_id": 3}, {"event_id": 5}, {"event_order": 1}, {"completed_external_closes": 101}],
)
def test_l01_t06_novelty_must_match_the_exact_event(recycling_fixture, changes):
    graph, builder, event, novelty = recycling_fixture
    before = graph.structural_hash
    with pytest.raises(ValueError, match="UNVERIFIED_NOVELTY"):
        builder.recycle_slot(8192, 0, event=replace(event, **changes), novelty=novelty)
    assert graph.structural_hash == before


def test_l01_t06_trigger_at_reverse_endpoint_is_legal(recycling_fixture):
    graph, builder, event, _ = recycling_fixture
    builder.recycle_slot(8192, 0, event=event, novelty=FixtureLocalNovelty(event, 9000, 0.0))
    assert len(graph.recycling_log()[0].changes) == 2


@pytest.mark.parametrize("reverse", [False, True])
@pytest.mark.parametrize("state", SynapseState)
def test_l01_t07_every_live_state_in_either_direction_blocks(
    recycling_fixture, record_factory, key_factory, reverse, state
):
    graph, builder, event, novelty = recycling_fixture
    source, target = (9000, 8192) if reverse else (8192, 9000)
    builder.add_synapse(
        record_factory(
            key_factory(source, target),
            state=state,
            E_ext=3.0 if state is SynapseState.CONSOLIDATED else 1.0,
            external_root_count=2 if state is SynapseState.CONSOLIDATED else 1,
        )
    )
    before = graph.structural_hash
    with pytest.raises(ValueError, match="RECYCLE_BLOCKED_LIVE_OR_PROTECTED"):
        builder.recycle_slot(8192, 0, event=event, novelty=novelty)
    assert graph.structural_hash == before


@pytest.mark.parametrize("scope", [SynapseScope.LOCAL, SynapseScope.ASSOCIATIVE])
@pytest.mark.parametrize("reverse", [False, True])
def test_l01_t07_any_scope_reservation_in_either_direction_blocks(
    recycling_fixture, key_factory, scope, reverse
):
    graph, builder, event, novelty = recycling_fixture
    key = key_factory(9000, 8192, scope) if reverse else key_factory(8192, 9000, scope)
    builder.reserve(key, 8192)
    before = graph.structural_hash
    with pytest.raises(ValueError, match="RECYCLE_BLOCKED_LIVE_OR_PROTECTED"):
        builder.recycle_slot(8192, 0, event=event, novelty=novelty)
    assert graph.structural_hash == before


@pytest.mark.parametrize("reverse", [False, True])
@pytest.mark.parametrize(
    "kind,reason",
    [("pin", "RECYCLE_BLOCKED_CANDIDATE"), ("protected", "RECYCLE_BLOCKED_LIVE_OR_PROTECTED")],
)
def test_l01_t07_opposite_slot_protection_cannot_be_ignored(
    recycling_fixture, reverse, kind, reason
):
    graph, builder, event, novelty = recycling_fixture
    owner = 9000 if reverse else 8192
    if kind == "pin":
        builder.pin_slot(owner, 0, 8192)
    else:
        builder.protect_slot(owner, 0)
    before = graph.structural_hash
    with pytest.raises(ValueError, match=reason):
        builder.recycle_slot(8192, 0, event=event, novelty=novelty)
    assert graph.structural_hash == before


def test_l01_t07_opposite_fixed_copy_blocks_bilateral_operation(graph_pair):
    graph, builder = graph_pair
    builder.inject_slot(8193, 6, 8192)
    before = graph.structural_hash
    with pytest.raises(ValueError, match="RECYCLE_BLOCKED_FIXED"):
        builder.recycle_slot(8192, 0)
    assert graph.structural_hash == before


def test_l01_t06_both_assignment_ages_must_have_elapsed(recycling_fixture):
    graph, builder, event, _ = recycling_fixture
    builder.remove_fixture_slot(9000, 0)
    builder.fill_coactive(
        9000, FixtureEventSnapshot(2, 2, 0, 50, frontier=(FixtureFrontier(8192, 0.5),))
    )
    before = graph.structural_hash
    with pytest.raises(ValueError, match="CONFIRMATION_WINDOW_NOT_ELAPSED"):
        builder.recycle_slot(8192, 0, event=event, novelty=FixtureLocalNovelty(event, 8192, 0.0))
    assert graph.structural_hash == before
    mature = replace(event, completed_external_closes=150)
    builder.recycle_slot(8192, 0, event=mature, novelty=FixtureLocalNovelty(mature, 8192, 0.0))
    graph.validate_graph()


def test_l01_t08_success_rebuilds_both_indices_ages_and_ordered_log(recycling_fixture):
    graph, builder, event, novelty = recycling_fixture
    fixed = {i: graph.latent_slots(i)[6:12] + graph.latent_slots(i)[18:24] for i in (8192, 9000)}
    builder.recycle_slot(8192, 0, event=event, novelty=novelty)
    assert graph.reverse_latent(8192) == graph.reverse_latent(9000) == ()
    assert graph.reverse_latent(10000) == ((8192, 0), (9000, 0))
    for owner in (8192, 9000):
        slot = graph.latent_slots(owner)[0]
        assert slot.target_id == 10000 and slot.assigned_at_completed_close_serial == 100
        assert slot.assignment.pending_birth is False
        assert fixed[owner] == graph.latent_slots(owner)[6:12] + graph.latent_slots(owner)[18:24]
        assert graph.outgoing_usage(owner).total == 0
    assert graph.recycling_log()[0].reason == "RECYCLED"
    assert graph.recycling_log()[0].changes == ((8192, 0, 9000, 10000), (9000, 0, 8192, 10000))
    assert graph.synapses() == graph.reserved_keys() == ()
    graph.validate_graph()
    before = graph.structural_hash
    builder.recycle_slot(8192, 0, event=event, novelty=novelty)
    assert graph.structural_hash == before
    with pytest.raises(ValueError, match="CONFLICTING_RECYCLING_RETRY"):
        builder.recycle_slot(8192, 0, event=event, novelty=FixtureLocalNovelty(event, 8192, 0.1))


def test_l01_t08_one_sided_occurrence_is_supported(recycling_fixture):
    graph, builder, event, novelty = recycling_fixture
    builder.remove_fixture_slot(9000, 0)
    builder.recycle_slot(8192, 0, event=event, novelty=novelty)
    assert graph.reverse_latent(10000) == ((8192, 0),)
    assert len(graph.recycling_log()[0].changes) == 1
    graph.validate_graph()


@pytest.mark.parametrize("second_side_only", [False, True])
def test_l01_t08_no_replacement_never_deletes_either_side(recycling_fixture, second_side_only):
    graph, builder, event, _ = recycling_fixture
    if second_side_only:
        target = graph.latent_slots(9000)[6].target_id
        builder.commit_cells([target], committed_event=0)
        event = replace(event, frontier=(FixtureFrontier(target, 0.8),))
    else:
        event = replace(event, frontier=())
    before = graph.structural_hash
    with pytest.raises(ValueError, match="NO_RECYCLING_REPLACEMENT"):
        builder.recycle_slot(8192, 0, event=event, novelty=FixtureLocalNovelty(event, 8192, 0.0))
    assert graph.structural_hash == before


@pytest.mark.parametrize(
    "stage",
    [MutationStage.SLOT, MutationStage.REVERSE_INDEX, MutationStage.BUDGET, MutationStage.PUBLISH],
)
def test_l01_t07_t08_injected_failure_rolls_back_both_sides_and_metadata(recycling_fixture, stage):
    graph, builder, event, novelty = recycling_fixture
    before = graph.structural_hash
    with pytest.raises(InjectedFailure), builder.transaction(fail_at=stage) as tx:
        tx.recycle_slot(8192, 0, event=event, novelty=novelty)
    assert graph.structural_hash == before
    assert graph.recycling_log() == ()
    graph.validate_graph()


def test_l01_t07_failure_after_first_side_is_still_atomic(recycling_fixture):
    graph, builder, event, novelty = recycling_fixture
    before = graph.structural_hash
    tx = builder.transaction()
    updates = 0

    def interrupt_second_index(stage):
        nonlocal updates
        assert graph.structural_hash == before
        if stage is MutationStage.REVERSE_INDEX:
            updates += 1
            if updates == 2:
                raise InjectedFailure("torn bilateral index update")

    tx._shadow.hook = interrupt_second_index
    with pytest.raises(InjectedFailure), tx:
        tx.recycle_slot(8192, 0, event=event, novelty=novelty)
    assert updates == 2 and graph.structural_hash == before


@pytest.mark.parametrize("prediction", [float("nan"), float("inf"), -0.1, 1.1, True, "0.5"])
def test_l01_t10_invalid_or_semantic_proof_payloads(prediction, recycling_fixture):
    _, _, event, _ = recycling_fixture
    with pytest.raises(ValueError):
        FixtureLocalNovelty(event, 8192, prediction)
    with pytest.raises(ValueError, match="UNVERIFIED_NOVELTY"):
        FixtureLocalNovelty(event, 11000, 0.0)
    with pytest.raises(FrozenInstanceError):
        FixtureLocalNovelty(event, 8192, 0.0).pre_input_prediction = 0.8


def test_l01_t07_cross_region_scope_protection_and_compatible_replacements(
    key_factory, record_factory
):
    graph = SparseNetwork()
    builder = FixtureBuilder(graph)
    builder.commit_cells([2000, 3000, 10000, 11000], committed_event=0)
    birth = FixtureEventSnapshot(
        1,
        1,
        0,
        0,
        direct_receivers=(FixtureReceiver(8192, 500000), FixtureReceiver(0, 500000)),
        birth_ids=frozenset({8192, 0}),
    )
    builder.initialize_cohort(birth)
    assert graph.latent_slots(8192)[12].target_id == 0
    assert graph.latent_slots(0)[15].target_id == 8192
    event = FixtureEventSnapshot(
        2,
        4,
        0,
        100,
        frontier=(FixtureFrontier(2000, 0.8), FixtureFrontier(10000, 0.8)),
        direct_receivers=(FixtureReceiver(8192, 500000),),
    )
    novelty = FixtureLocalNovelty(event, 8192, 0.0)
    cross = key_factory(0, 8192, SynapseScope.CROSS_TERRITORY)
    builder.reserve(cross, 8192)
    before = graph.structural_hash
    with pytest.raises(ValueError, match="RECYCLE_BLOCKED_LIVE_OR_PROTECTED"):
        builder.recycle_slot(8192, 12, event=event, novelty=novelty)
    assert graph.structural_hash == before
    builder.release(cross, 8192)
    builder.add_synapse(record_factory(cross))
    before = graph.structural_hash
    with pytest.raises(ValueError, match="RECYCLE_BLOCKED_LIVE_OR_PROTECTED"):
        builder.recycle_slot(8192, 12, event=event, novelty=novelty)
    assert graph.structural_hash == before
    builder.remove_synapse(cross)
    builder.recycle_slot(8192, 12, event=event, novelty=novelty)
    assert graph.latent_slots(8192)[12].target_id == 2000
    assert graph.latent_slots(0)[15].target_id == 10000
    graph.validate_graph()


def test_l01_t06_missing_assignment_age_is_never_assumed_zero(graph_pair):
    graph, builder = graph_pair
    builder.commit_cells([10000], committed_event=0)
    event = FixtureEventSnapshot(
        2,
        2,
        0,
        100,
        frontier=(FixtureFrontier(10000, 0.8),),
        direct_receivers=(FixtureReceiver(8192, 500000),),
    )
    before = graph.structural_hash
    with pytest.raises(ValueError, match="CONFIRMATION_WINDOW_NOT_ELAPSED"):
        builder.recycle_slot(8192, 0, event=event, novelty=FixtureLocalNovelty(event, 8192, 0.0))
    assert graph.structural_hash == before


def test_l01_t10_independent_audit_detects_recycling_log_or_age_corruption(recycling_fixture):
    from dgca_next.graph import GraphInvariantError

    graph, builder, event, novelty = recycling_fixture
    builder.recycle_slot(8192, 0, event=event, novelty=novelty)
    original = graph._state
    graph._state = replace(original, recycling_log=())
    with pytest.raises(GraphInvariantError, match="RECYCLING_LOG_MISMATCH"):
        graph.validate_graph()
    graph._state = original
    tx = builder.transaction()
    slots = tx._shadow.slots[8192]
    tx._shadow.slots[8192] = (
        replace(slots[0], assignment=replace(slots[0].assignment, completed_close_serial=0)),
    ) + slots[1:]
    before = graph.structural_hash
    with pytest.raises(GraphInvariantError, match="ASSIGNMENT_AGE_RESET"):
        tx.commit()
    assert graph.structural_hash == before


def test_l01_t08_old_target_and_self_cannot_be_replacement_candidates(recycling_fixture):
    graph, builder, event, _ = recycling_fixture
    event = replace(
        event,
        frontier=(
            FixtureFrontier(8192, 1.0),
            FixtureFrontier(9000, 1.0),
            FixtureFrontier(10000, 0.8),
        ),
    )
    builder.recycle_slot(8192, 0, event=event, novelty=FixtureLocalNovelty(event, 8192, 0.0))
    assert graph.latent_slots(8192)[0].target_id == graph.latent_slots(9000)[0].target_id == 10000


def test_new_record_metadata_cannot_expose_mutable_aliases(recycling_fixture):
    graph, builder, event, novelty = recycling_fixture
    assert novelty.digest == FixtureLocalNovelty(event, 8192, -0.0).digest
    builder.recycle_slot(8192, 0, event=event, novelty=novelty)
    record = graph.recycling_log()[0]
    with pytest.raises(ValueError, match="INVALID_BILATERAL_CHANGES"):
        replace(record, changes=tuple(list(change) for change in record.changes))
    with pytest.raises(ValueError, match="INVALID_SNAPSHOT_DIGEST"):
        replace(record, novelty_digest=list(record.novelty_digest))
