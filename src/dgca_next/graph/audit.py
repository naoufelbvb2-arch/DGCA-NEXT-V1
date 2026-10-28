"""Independent read-only audit reconstructed from physical records, not counters."""

from collections import Counter, defaultdict
from dataclasses import dataclass, replace

from dgca_next.contracts import CellAddress, SynapseKey
from dgca_next.graph.cell import Cell
from dgca_next.graph.geometry import microcolumn_neighborhood, microcolumn_of
from dgca_next.graph.latent import LatentSlot, SlotAssignment, SlotCategory, empty_slots
from dgca_next.graph.network import SlotRef, SparseNetwork, _State
from dgca_next.graph.policy import InitializationRecord, local_targets, topographic_targets
from dgca_next.graph.recycling import RecyclingRecord
from dgca_next.graph.synapse import Synapse, SynapseState, key_order


class GraphInvariantError(ValueError):
    """Physical schema and redundant graph bookkeeping disagree."""


@dataclass(frozen=True, slots=True)
class AuditReport:
    logical_cells: int
    stored_cells: int
    occupied_slots: int
    synapses: int
    reserved_keys: int


def _require(condition: bool, diagnostic: str) -> None:
    if not condition:
        raise GraphInvariantError(diagnostic)


def validate_state(state: _State) -> AuditReport:
    try:
        return _validate(state)
    except GraphInvariantError:
        raise
    except (ValueError, TypeError, AttributeError, KeyError, IndexError) as exc:
        raise GraphInvariantError(f"INVALID_GRAPH_SCHEMA: {exc}") from exc


def _validate(state: _State) -> AuditReport:
    for cell_id in sorted(state.cells):
        cell = state.cells[cell_id]
        _require(type(cell) is Cell, "INVALID_CELL_TYPE")
        replace(cell)
        _require(CellAddress.from_cell_id(cell_id) == cell.address, "CELL_ID_ADDRESS_MISMATCH")
        _require(cell.committed, "INVALID_STORED_COMMITMENT")

    expected_reverse: dict[int, set[SlotRef]] = defaultdict(set)
    pairs: set[tuple[int, int]] = set()
    for owner in sorted(state.slots):
        slots = state.slots[owner]
        _require(owner in state.cells, "UNCOMMITTED_LATENT_OWNER")
        _require(type(slots) is tuple and len(slots) == 24, "INVALID_SLOT_COUNT")
        schema = empty_slots(CellAddress.from_cell_id(owner).region)
        targets: set[int] = set()
        for index, slot in enumerate(slots):
            _require(type(slot) is LatentSlot, "INVALID_SLOT_TYPE")
            replace(slot)
            expected = schema[index]
            _require(
                (slot.index, slot.category, slot.permitted_region)
                == (expected.index, expected.category, expected.permitted_region),
                "INVALID_SLOT_CATEGORY_REGION",
            )
            if slot.target_id is None:
                continue
            target = slot.target_id
            _require(
                not slot.recyclable_category or target in state.cells, "UNCOMMITTED_LATENT_TARGET"
            )
            _require(target != owner, "LATENT_SELF_TARGET")
            _require(target not in targets, "DUPLICATE_LATENT_TARGET")
            targets.add(target)
            _require(all(pin in state.cells for pin in slot.pin_owners), "UNCOMMITTED_PIN_OWNER")
            if slot.category is SlotCategory.LOCAL:
                _require(
                    microcolumn_of(target) in microcolumn_neighborhood(owner, 1),
                    "LOCAL_SLOT_OUTSIDE_VICINITY",
                )
            expected_reverse[target].add((owner, index))
            pairs.add((owner, target))
            if slot.assignment is not None:
                _require(type(slot.assignment) is SlotAssignment, "INVALID_ASSIGNMENT_METADATA")
                replace(slot.assignment)
    for owner in sorted(state.initializations):
        record = state.initializations[owner]
        _require(type(record) is InitializationRecord, "INVALID_INITIALIZATION_RECORD")
        replace(record)
        _require(record.owner_id == owner and owner in state.cells, "INVALID_INITIALIZATION_OWNER")
        _require(
            state.cells[owner].committed_event == record.assignment.event_id,
            "INITIALIZATION_COMMITMENT_TIMING",
        )
        _require(
            state.cells[owner].fixture_only == record.assignment.fixture_only
            and state.cells[owner].admission == record.assignment.admission,
            "INITIALIZATION_ORIGIN_MISMATCH",
        )
        initialized_slots = state.slots.get(owner)
        _require(initialized_slots is not None, "MISSING_INITIALIZED_SLOTS")
        assert initialized_slots is not None
        local = local_targets(owner, frozenset(record.seed_targets))
        topo = topographic_targets(owner, frozenset((*record.seed_targets, *local)))
        _require(
            tuple(initialized_slots[i].target_id for i in (*range(6, 12), *range(18, 24)))
            == local + topo,
            "FIXED_POLICY_TARGET_MISMATCH",
        )
        _require(
            all(
                slot.assignment is not None
                for slot in initialized_slots
                if slot.target_id is not None
            ),
            "MISSING_ASSIGNMENT_METADATA",
        )
    _require(
        all(type(refs) is frozenset for refs in state.reverse.values()), "MUTABLE_REVERSE_INDEX"
    )
    _require(
        dict(state.reverse) == {k: frozenset(v) for k, v in expected_reverse.items()},
        "REVERSE_LATENT_INDEX_MISMATCH",
    )

    expected_outgoing: dict[int, set[SynapseKey]] = defaultdict(set)
    episodic: Counter[int] = Counter()

    def check_key(key: SynapseKey) -> None:
        _require(type(key) is SynapseKey, "INVALID_SYNAPSE_KEY")
        replace(key)
        source, target = key.source.cell_id, key.target.cell_id
        _require(
            CellAddress.from_cell_id(source) == key.source
            and CellAddress.from_cell_id(target) == key.target,
            "INVALID_KEY_ADDRESS",
        )
        _require(source in state.cells and target in state.cells, "UNCOMMITTED_ENDPOINT")
        _require(
            (source, target) in pairs or (target, source) in pairs, "MISSING_LATENT_ELIGIBILITY"
        )
        expected_outgoing[source].add(key)

    for key in sorted(state.synapses, key=key_order):
        synapse = state.synapses[key]
        _require(type(synapse) is Synapse, "INVALID_SYNAPSE_TYPE")
        replace(synapse)
        _require(key == synapse.key, "SYNAPSE_KEY_RECORD_MISMATCH")
        check_key(key)
        source_event = state.cells[key.source.cell_id].committed_event
        target_event = state.cells[key.target.cell_id].committed_event
        _require(source_event is not None and target_event is not None, "MISSING_COMMITMENT_EVENT")
        assert source_event is not None and target_event is not None
        _require(
            source_event < synapse.created_event - synapse.delta
            and target_event < synapse.created_event,
            "COMMITMENT_TIMING",
        )
        if synapse.state is SynapseState.EPISODIC_INDEXED:
            episodic[key.source.cell_id] += 1

    for key in sorted(state.reservations, key=key_order):
        claimants = state.reservations[key]
        check_key(key)
        _require(type(claimants) is frozenset and bool(claimants), "INVALID_RESERVATION_CLAIMANTS")
        _require(key not in state.synapses, "LIVE_KEY_RESERVATION_NOT_TRANSFERRED")
        for claimant in claimants:
            CellAddress.from_cell_id(claimant)
            _require(claimant in state.cells, "UNCOMMITTED_RESERVATION_OWNER")
    _require(
        all(type(keys) is frozenset for keys in state.outgoing.values()), "MUTABLE_BUDGET_INDEX"
    )
    _require(
        dict(state.outgoing) == {k: frozenset(v) for k, v in expected_outgoing.items()},
        "OUTGOING_INDEX_MISMATCH",
    )
    # Core §1.2, LLA §4.4. Deliberately independent of mutation-side budget helpers.
    for source in sorted(expected_outgoing):
        keys = expected_outgoing[source]
        _require(len(keys) <= 64, "SOURCE_OUTGOING_CAPACITY")
        _require(
            sum(k.source.region is not k.target.region for k in keys) <= 12,
            "CROSS_OUTGOING_CAPACITY",
        )
        _require(episodic[source] <= 4, "EPISODIC_OUTGOING_CAPACITY")
    _require(sum(episodic.values()) <= len(state.cells) // 10, "NETWORK_EPISODIC_CAPACITY")

    # Fixture insertion/removal accounting, not a production confirmation window.
    balance: Counter[tuple[int, int, int]] = Counter()
    _require(type(state.wiring_log) is tuple, "MUTABLE_WIRING_LOG")
    for owner, index, old, new in sorted(state.wiring_log):
        CellAddress.from_cell_id(owner)
        _require(type(index) is int and 0 <= index < 24, "INVALID_WIRING_LOG_INDEX")
        _require(old != new, "INVALID_WIRING_LOG_CHANGE")
        for target, amount in ((old, -1), (new, 1)):
            if target != -1:
                CellAddress.from_cell_id(target)
                balance[owner, index, target] += amount
    expected_balance = Counter(
        (owner, slot.index, slot.target_id)
        for owner, slots in state.slots.items()
        for slot in slots
        if slot.target_id is not None
    )
    _require(
        {k: v for k, v in balance.items() if v} == dict(expected_balance), "WIRING_LOG_MISMATCH"
    )
    _require(type(state.recycling_log) is tuple, "MUTABLE_RECYCLING_LOG")
    recorded: Counter[tuple[int, int, int, int]] = Counter()
    for recycling_entry in state.recycling_log:
        _require(type(recycling_entry) is RecyclingRecord, "INVALID_RECYCLING_RECORD")
        replace(recycling_entry)
        recorded.update(recycling_entry.changes)
    actual_replacements = Counter(
        change for change in state.wiring_log if change[2] != -1 and change[3] != -1
    )
    _require(recorded == actual_replacements, "RECYCLING_LOG_MISMATCH")
    return AuditReport(
        12288, len(state.cells), len(pairs), len(state.synapses), len(state.reservations)
    )


def validate_graph(network: SparseNetwork) -> AuditReport:
    if type(network) is not SparseNetwork:
        raise ValueError("network must be SparseNetwork")
    return validate_state(network._state)


def validate_transition(base: _State, candidate: _State) -> None:
    """Check retention rules requiring a before-image, independently of writers."""
    pinned_pairs: set[frozenset[int]] = set()
    _require(
        candidate.recycling_log[: len(base.recycling_log)] == base.recycling_log,
        "RECYCLING_HISTORY_CHANGED",
    )
    for owner in sorted(base.slots):
        for slot in base.slots[owner]:
            if slot.target_id is None:
                continue
            after_slots = candidate.slots.get(owner)
            after = after_slots[slot.index] if after_slots is not None else None
            if (
                after is not None
                and after.target_id == slot.target_id
                and slot.assignment is not None
            ):
                _require(after.assignment == slot.assignment, "ASSIGNMENT_AGE_RESET")
            if not slot.recyclable_category or slot.protected or slot.pinned:
                _require(
                    after is not None and after.target_id == slot.target_id,
                    "PROTECTED_SLOT_CHANGED",
                )
                assert after is not None
                _require(not slot.protected or after.protected, "SLOT_PROTECTION_REMOVED")
                _require(slot.pin_owners <= after.pin_owners, "CANDIDATE_PIN_REMOVED")
            if slot.pinned:
                pinned_pairs.add(frozenset((owner, slot.target_id)))
    for key in sorted(base.synapses, key=key_order):
        before = base.synapses[key]
        after_link = candidate.synapses.get(key)
        pair = frozenset((key.source.cell_id, key.target.cell_id))
        if before.protected or before.state is SynapseState.CONSOLIDATED or pair in pinned_pairs:
            _require(after_link == before, "PROTECTED_SYNAPSE_CHANGED")
        elif after_link is not None:
            _require(after_link == before, "I1_SYNAPSE_UPDATE_UNSUPPORTED")
    for cell_id in sorted(base.cells):
        before_cell = base.cells[cell_id]
        after_cell = candidate.cells.get(cell_id)
        _require(
            after_cell is not None
            and (
                after_cell.address,
                after_cell.committed,
                after_cell.committed_event,
                after_cell.fixture_only,
            )
            == (
                before_cell.address,
                before_cell.committed,
                before_cell.committed_event,
                before_cell.fixture_only,
            ),
            "COMMITTED_CELL_CHANGED",
        )
    for owner in base.initializations:
        _require(
            candidate.initializations.get(owner) == base.initializations[owner],
            "INITIALIZATION_HISTORY_CHANGED",
        )
    for record in candidate.recycling_log[len(base.recycling_log) :]:
        for owner, index, old_target, new_target in record.changes:
            if owner not in base.slots or base.slots[owner][index].target_id != old_target:
                # New assignments in this fixture batch have no published before-image.
                continue
            before_slot = base.slots[owner][index]
            assigned = before_slot.assigned_at_completed_close_serial
            _require(
                assigned is not None and record.completed_close_serial - assigned >= 100,
                "CONFIRMATION_WINDOW_NOT_ELAPSED",
            )
            pair = frozenset((owner, old_target))
            _require(
                not any(
                    frozenset((k.source.cell_id, k.target.cell_id)) == pair
                    for k in (*base.synapses, *base.reservations)
                ),
                "RECYCLE_BLOCKED_LIVE_OR_PROTECTED",
            )
            for source, other in ((owner, old_target), (old_target, owner)):
                for old_slot in base.slots.get(source, ()):
                    if old_slot.target_id == other:
                        _require(
                            old_slot.recyclable_category
                            and not old_slot.protected
                            and not old_slot.pinned,
                            "PROTECTED_BILATERAL_REPLACEMENT",
                        )
                        _require(
                            any(
                                change[:3] == (source, old_slot.index, other)
                                for change in record.changes
                            ),
                            "INCOMPLETE_BILATERAL_REPLACEMENT",
                        )
            after_slot = candidate.slots[owner][index]
            _require(
                after_slot.target_id == new_target and after_slot.assignment is not None,
                "RECYCLE_ASSIGNMENT_MISMATCH",
            )
            assert after_slot.assignment is not None
            _require(
                (
                    after_slot.assignment.exposure_id,
                    after_slot.assignment.event_id,
                    after_slot.assignment.event_order,
                    after_slot.assignment.completed_close_serial,
                )
                == (
                    record.exposure_id,
                    record.event_id,
                    record.event_order,
                    record.completed_close_serial,
                ),
                "RECYCLE_ASSIGNMENT_MISMATCH",
            )
