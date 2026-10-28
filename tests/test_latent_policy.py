import itertools
import json
from dataclasses import FrozenInstanceError, fields, replace
from pathlib import Path

import pytest

from dgca_next.contracts import CellAddress, EventMode, EventOrigin, Region
from dgca_next.graph import (
    FixtureBuilder,
    FixtureEventSnapshot,
    FixtureFrontier,
    FixtureReceiver,
    InjectedFailure,
    MutationStage,
    SparseNetwork,
    initialize_layout,
    local_targets,
    topographic_targets,
)
from dgca_next.graph.latent import LATENT_POLICY_VERSION, empty_slots
from dgca_next.graph.policy import TOPOGRAPHIC_SALT, q6, ranked_candidates, topographic_base


def birth_event(ids, *, closes=0, event_id=1, frontier=()):
    return FixtureEventSnapshot(
        1,
        event_id,
        0,
        closes,
        frontier=tuple(frontier),
        direct_receivers=tuple(FixtureReceiver(i, 500000) for i in ids),
        birth_ids=frozenset(ids),
    )


def test_l01_t01_simultaneous_cobirth_is_topology_only():
    graph = SparseNetwork()
    event = birth_event((8192, 9000, 10000))
    builder = FixtureBuilder(graph)
    builder.initialize_cohort(event)
    assert graph.stored_cell_count == 3
    assert graph.synapses() == graph.reserved_keys() == ()
    for owner in event.birth_ids:
        targets = {s.target_id for s in graph.latent_slots(owner)[:6]}
        assert event.birth_ids - {owner} <= targets
        assert all(graph.structurally_eligible(owner, peer) for peer in event.birth_ids - {owner})
        assert graph.initialization(owner).assignment.pending_birth is True
    graph.validate_graph()
    before = graph.structural_hash
    builder.initialize_cohort(event)
    assert graph.structural_hash == before


@pytest.mark.parametrize(
    "owner,expected",
    [
        (0, (1, 8, 128, 2, 9, 129)),
        (8192, (8193, 8200, 8320, 8194, 8201, 8321)),
        (9539, (9536, 9408, 9528, 9544, 9664, 9537)),
        (12287, (12280, 12152, 12272, 12281, 12153, 12273)),
    ],
)
def test_l01_t02_round_robin_local_goldens(owner, expected):
    assert local_targets(owner) == expected
    assert len(set(expected)) == 6 and owner not in expected


@pytest.mark.parametrize(
    "owner,expected",
    [
        (0, (7459, 7937, 6283, 10074, 10352, 9754)),
        (4096, (3618, 2002, 1859, 10120, 9766, 10285)),
        (8192, (2387, 2113, 1452, 5693, 4810, 4808)),
        (12287, (3963, 3137, 3151, 4285, 6203, 5857)),
        (1309, (4730, 5681, 5682, 10312, 8715, 10394)),
    ],
)
def test_l01_t03_independent_spec_topographic_goldens(owner, expected):
    # Frozen vectors computed from the approved byte preimage using a standalone
    # hashlib/struct reference, without importing the implementation selectors.
    assert topographic_targets(owner) == expected
    assert TOPOGRAPHIC_SALT == b"DGCA-LATENT-TOP1"
    assert len(TOPOGRAPHIC_SALT) == 16
    assert LATENT_POLICY_VERSION == "DGCA-LATENT-TOPO-V1"
    region = CellAddress.from_cell_id(owner).region
    assert all(CellAddress.from_cell_id(i).region is not region for i in expected)


def test_topographic_collision_and_explicit_exclusion_probe():
    assert tuple(topographic_base(1309, Region.AUDIO, k) for k in range(3)) == (634, 1585, 1585)
    assert topographic_targets(8192, frozenset({2387}))[0] == 2388
    with pytest.raises(ValueError, match="NO_TOPOGRAPHIC_TARGET"):
        topographic_targets(8192, frozenset(range(4096)))


def test_l01_t04_quantized_rank_ties_and_empty_categories():
    event = birth_event(
        (8192,),
        frontier=(
            FixtureFrontier(9500, 0.5000004),
            FixtureFrontier(9300, 0.5),
            FixtureFrontier(9400, 0.8),
        ),
    )
    assert ranked_candidates(event, Region.LANGUAGE) == (9400, 8192, 9300, 9500)
    layout = initialize_layout(8192, event)
    assert tuple(s.target_id for s in layout[:6]) == (9400, 9300, 9500, None, None, None)
    assert all(s.target_id is None for s in layout[12:18])
    # Binary64-rational ties-even: these binary fractions give exact half-micro ties.
    assert q6(1 / 128) == 7812
    assert q6(3 / 128) == 23438


def test_l01_t04_reordered_inputs_and_births_have_same_dump():
    hashes = []
    ids = (8192, 9000, 10000)
    for order in itertools.permutations(ids):
        graph = SparseNetwork()
        event = birth_event(order)
        FixtureBuilder(graph).initialize_cohort(event)
        hashes.append(graph.structural_hash)
    assert len(set(hashes)) == 1


def test_fixed_targets_remain_uncommitted_and_unmaterialized():
    graph = SparseNetwork()
    FixtureBuilder(graph).initialize_cohort(birth_event((8192,)))
    assert graph.stored_cell_count == 1
    for slot in graph.latent_slots(8192):
        if slot.target_id is not None:
            assert not graph.cell(slot.target_id).committed
            assert graph.reverse_latent(slot.target_id) == ((8192, slot.index),)
    graph.validate_graph()


def test_later_fill_uses_new_snapshot_without_rotating_fixed_or_populated_slots():
    graph = SparseNetwork()
    builder = FixtureBuilder(graph)
    builder.commit_cells([9000, 10000, 11000], committed_event=0)
    builder.initialize_cohort(birth_event((8192,)))
    fixed = graph.latent_slots(8192)[6:12] + graph.latent_slots(8192)[18:24]
    later = FixtureEventSnapshot(2, 2, 0, 7, frontier=(FixtureFrontier(9000, 0.5),))
    builder.fill_coactive(8192, later)
    first = graph.latent_slots(8192)[0]
    assert first.target_id == 9000 and first.assigned_at_completed_close_serial == 7
    builder.fill_coactive(
        8192,
        replace(
            later, event_id=3, frontier=(FixtureFrontier(10000, 0.9), FixtureFrontier(11000, 0.6))
        ),
    )
    assert graph.latent_slots(8192)[0] == first
    assert graph.latent_slots(8192)[6:12] + graph.latent_slots(8192)[18:24] == fixed
    assert tuple(s.target_id for s in graph.latent_slots(8192)[:3]) == (9000, 10000, 11000)
    assert graph.synapses() == ()
    graph.validate_graph()


def test_context_end_birth_preserves_pins_without_fabricating_sensory_score():
    graph = SparseNetwork()
    builder = FixtureBuilder(graph)
    targets = (8193, 8194, 9000, 10000)
    builder.commit_cells(targets, committed_event=0)
    slots = list(empty_slots(Region.LANGUAGE))
    for index, target in enumerate(targets):
        slots[index] = replace(
            slots[index], target_id=target, protected=True, pin_owners=frozenset({8192})
        )
    event = FixtureEventSnapshot(1, 1, 0, 1, frontier=(FixtureFrontier(9000, 0.5),))
    assert 8192 not in ranked_candidates(event, Region.LANGUAGE)
    builder.initialize_context_cell(8192, event, tuple(slots))
    assert graph.initialization(8192).contextual is True
    assert graph.initialization(8192).assignment.pending_birth is False
    assert all(s.pinned for s in graph.latent_slots(8192)[:4])
    assert tuple(s.target_id for s in graph.latent_slots(8192)[6:12]) == (
        8195,
        8200,
        8320,
        8196,
        8201,
        8321,
    )
    assert graph.synapses() == graph.reserved_keys() == ()
    assert len({s.target_id for s in graph.latent_slots(8192) if s.target_id is not None}) == 16
    graph.validate_graph()


def test_l01_t05_no_retroactive_fixture_link_at_birth_event(key_factory, record_factory):
    graph = SparseNetwork()
    builder = FixtureBuilder(graph)
    builder.initialize_cohort(birth_event((8192, 9000)))
    before = graph.structural_hash
    with pytest.raises(ValueError, match="COMMITMENT_TIMING"):
        builder.add_synapse(record_factory(key_factory(8192, 9000), created_event=1))
    assert graph.structural_hash == before
    assert graph.synapses() == ()


@pytest.mark.parametrize(
    "stage",
    [
        MutationStage.CELL,
        MutationStage.SLOT,
        MutationStage.REVERSE_INDEX,
        MutationStage.BUDGET,
        MutationStage.PUBLISH,
    ],
)
def test_l01_t10_initialization_is_one_atomic_publication(stage):
    graph = SparseNetwork()
    before = graph.structural_hash
    with pytest.raises(InjectedFailure), FixtureBuilder(graph).transaction(fail_at=stage) as tx:
        tx.initialize_cohort(birth_event((8192, 9000, 10000)))
    assert graph.structural_hash == before
    assert graph.stored_cell_count == 0
    graph.validate_graph()


@pytest.mark.parametrize(
    "changes",
    [
        {"mode": EventMode.RETRIEVE},
        {"mode": EventMode.REPLAY},
        {"origin": EventOrigin.INTERNAL_SELECTED},
        {"fixture_only": False},
        {"birth_ids": frozenset({9000})},
        {"frontier": [FixtureFrontier(9000, 0.5)]},
        {"frontier": (FixtureFrontier(8192, 0.5),)},
    ],
)
def test_l01_t10_invalid_provenance_is_rejected(changes):
    with pytest.raises(ValueError):
        replace(birth_event((8192,)), **changes)


def test_l01_t10_snapshot_immutability_and_no_semantic_fields():
    event = birth_event((8192,))
    with pytest.raises(FrozenInstanceError):
        event.event_order = 2
    with pytest.raises(ValueError, match="FORBIDDEN_CANDIDATE_PROVENANCE"):
        FixtureFrontier(9000, 0.5, origin="PREDICTED_ONLY")
    for cls in (FixtureEventSnapshot, FixtureReceiver, FixtureFrontier):
        assert not {"label", "word", "raw_surface", "expected", "novelty"} & {
            f.name for f in fields(cls)
        }
    with pytest.raises(TypeError):
        FixtureReceiver(8192, 500000, word="oracle")


def test_l01_t09_published_sic_footprint_fixture_eligibility_measurement():
    # Core §3.1 published physical vectors, not a new SIC encoder or word input.
    cohorts = (
        (9345, 12181, 8606, 11795),
        (11641, 10513, 8694, 10273),
        (9330, 9412, 11818, 9195),
        (8606, 8200, 10035, 10926),
    )
    rows = []
    for cohort in cohorts:
        graph = SparseNetwork()
        FixtureBuilder(graph).initialize_cohort(birth_event(cohort))
        eligible = sum(
            all(graph.structurally_eligible(a, b) for a, b in itertools.combinations(triangle, 2))
            for triangle in itertools.combinations(cohort, 3)
        )
        rows.append(dict(physical_cohort=cohort, eligible_triangles=eligible))
        assert graph.synapses() == ()
        graph.validate_graph()
    metrics = dict(
        fixture_only=True,
        cohort_count=len(rows),
        eligible_cohort_count=sum(row["eligible_triangles"] > 0 for row in rows),
        rows=rows,
        learning_claim=False,
    )
    metrics["eligible_cohort_percent"] = 100 * metrics["eligible_cohort_count"] / len(rows)
    output = Path(__file__).resolve().parents[1] / ".pytest_cache/i1-l01-feasibility.json"
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")


def test_conflicting_reinitialization_and_missing_frontier_commitment_are_atomic():
    graph = SparseNetwork()
    builder = FixtureBuilder(graph)
    event = birth_event((8192,))
    builder.initialize_cohort(event)
    before = graph.structural_hash
    with pytest.raises(ValueError, match="CONFLICTING_BIRTH_COHORT"):
        builder.initialize_cohort(replace(event, event_id=2))
    with pytest.raises(ValueError, match="UNVERIFIED_FRONTIER_COMMITMENT"):
        builder.fill_coactive(
            8192,
            replace(
                event, event_id=2, birth_ids=frozenset(), frontier=(FixtureFrontier(9000, 0.5),)
            ),
        )
    assert graph.structural_hash == before


def test_cobirth_cannot_be_partitioned_or_rescored_after_publication():
    graph = SparseNetwork()
    builder = FixtureBuilder(graph)
    first = birth_event((8192,))
    builder.initialize_cohort(first)
    before = graph.structural_hash
    with pytest.raises(ValueError, match="CONFLICTING_COBIRTH_SNAPSHOT"):
        builder.initialize_cohort(birth_event((9000,)))
    assert graph.structural_hash == before
    assert not graph.cell(9000).committed


def test_empty_fill_cannot_retroactively_change_a_birth_snapshot():
    graph = SparseNetwork()
    builder = FixtureBuilder(graph)
    builder.commit_cells([9000], committed_event=0)
    event = birth_event((8192,))
    builder.initialize_cohort(event)
    before = graph.structural_hash
    with pytest.raises(ValueError, match="RETROACTIVE_FILL"):
        builder.fill_coactive(
            8192, replace(event, birth_ids=frozenset(), frontier=(FixtureFrontier(9000, 0.5),))
        )
    assert graph.structural_hash == before


def test_policy_version_is_explicit_and_mismatch_rejected_by_audit():
    import dataclasses

    from dgca_next.graph import GraphInvariantError
    from dgca_next.graph.policy import InitializationRecord

    graph = SparseNetwork()
    FixtureBuilder(graph).initialize_cohort(birth_event((8192,)))
    record = graph.initialization(8192)
    args = {f.name: getattr(record, f.name) for f in dataclasses.fields(record)}
    del args["policy_version"]
    with pytest.raises(TypeError):
        InitializationRecord(**args)
    with pytest.raises(ValueError, match="UNSUPPORTED_LATENT_POLICY_VERSION"):
        replace(record, policy_version="DGCA-LATENT-TOPO-V0")
    # Deliberately corrupt internal fixture metadata to exercise the independent audit.
    object.__setattr__(record, "policy_version", "unversioned")
    with pytest.raises(GraphInvariantError, match="UNSUPPORTED_LATENT_POLICY_VERSION"):
        graph.validate_graph()


def test_canonical_snapshot_digest_normalizes_signed_zero():
    event = birth_event((8192,), frontier=(FixtureFrontier(9000, 0.0),))
    negative_zero = replace(event, frontier=(FixtureFrontier(9000, -0.0),))
    assert event.digest == negative_zero.digest
