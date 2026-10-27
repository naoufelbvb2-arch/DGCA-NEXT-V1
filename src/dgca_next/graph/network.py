"""One sparse graph with immutable public values and explicit fixture-only writes.

Exact mutation retries are no-ops; conflicting duplicates are rejected.
Internal shadows publish once. No production learning or wiring entry point.
"""

import hashlib
import json
import struct
from collections.abc import Callable, Iterable, Iterator, Mapping
from dataclasses import asdict, dataclass, field, replace
from enum import Enum
from types import MappingProxyType
from typing import TYPE_CHECKING

from dgca_next.contracts import CellAddress, SynapseKey
from dgca_next.graph.budget import OutgoingUsage, outgoing_usage, validate_usage
from dgca_next.graph.cell import Cell
from dgca_next.graph.geometry import microcolumn_neighborhood, microcolumn_of
from dgca_next.graph.latent import LATENT_POLICY_VERSION, LatentSlot, SlotCategory, empty_slots
from dgca_next.graph.policy import (
    FixtureEventSnapshot,
    InitializationRecord,
    fill_coactive,
    initialize_layout,
    validate_fixture_event,
)
from dgca_next.graph.recycling import (
    FixtureLocalNovelty,
    RecyclingRecord,
    VerifiedLocalNovelty,
    bilateral_occurrences,
    plan_fixture_recycling,
)
from dgca_next.graph.synapse import Synapse, SynapseState, key_order, quality

if TYPE_CHECKING:
    from dgca_next.graph.audit import AuditReport
    from dgca_next.graph.transaction import FixtureTransaction

SlotRef = tuple[int, int]


class MutationStage(Enum):
    CELL = "CELL"
    SLOT = "SLOT"
    REVERSE_INDEX = "REVERSE_INDEX"
    LINK = "LINK"
    RESERVATION = "RESERVATION"
    BUDGET = "BUDGET"
    PUBLISH = "PUBLISH"


def _empty_mapping[K, V]() -> Mapping[K, V]:
    return MappingProxyType({})


@dataclass(frozen=True, slots=True)
class _State:
    cells: Mapping[int, Cell] = field(default_factory=_empty_mapping)
    slots: Mapping[int, tuple[LatentSlot, ...]] = field(default_factory=_empty_mapping)
    reverse: Mapping[int, frozenset[SlotRef]] = field(default_factory=_empty_mapping)
    synapses: Mapping[SynapseKey, Synapse] = field(default_factory=_empty_mapping)
    reservations: Mapping[SynapseKey, frozenset[int]] = field(default_factory=_empty_mapping)
    outgoing: Mapping[int, frozenset[SynapseKey]] = field(default_factory=_empty_mapping)
    # Wiring audit tuples: (owner_id, slot_index, old_target, new_target).
    # -1 denotes empty only in this administrative log, never a physical ID.
    wiring_log: tuple[tuple[int, int, int, int], ...] = ()
    initializations: Mapping[int, InitializationRecord] = field(default_factory=_empty_mapping)
    recycling_log: tuple[RecyclingRecord, ...] = ()


def _slots(state: _State, cell_id: int) -> tuple[LatentSlot, ...]:
    address = CellAddress.from_cell_id(cell_id)
    return state.slots.get(cell_id, empty_slots(address.region))


def _eligible(state: _State, first: int, second: int) -> bool:
    CellAddress.from_cell_id(first)
    CellAddress.from_cell_id(second)
    return first != second and (
        any(slot.target_id == second for slot in _slots(state, first))
        or any(slot.target_id == first for slot in _slots(state, second))
    )


class SparseNetwork:
    __slots__ = ("_state",)

    def __init__(self) -> None:
        self._state = _State()

    @property
    def stored_cell_count(self) -> int:
        return len(self._state.cells)

    @property
    def occupied_slot_count(self) -> int:
        return sum(s.target_id is not None for slots in self._state.slots.values() for s in slots)

    def cell(self, cell_id: int) -> Cell:
        address = CellAddress.from_cell_id(cell_id)
        return self._state.cells.get(cell_id, Cell(address))

    def iter_cell_ids(self) -> Iterator[int]:
        return iter(range(12288))

    def iter_cells(self) -> Iterator[Cell]:
        return (self.cell(cell_id) for cell_id in self.iter_cell_ids())

    def stored_cells(self) -> tuple[Cell, ...]:
        return tuple(self._state.cells[key] for key in sorted(self._state.cells))

    def latent_slots(self, cell_id: int) -> tuple[LatentSlot, ...]:
        return _slots(self._state, cell_id)

    def reverse_latent(self, target_id: int) -> tuple[SlotRef, ...]:
        CellAddress.from_cell_id(target_id)
        return tuple(sorted(self._state.reverse.get(target_id, ())))

    def structurally_eligible(self, first: int, second: int) -> bool:
        return _eligible(self._state, first, second)

    def synapse(self, key: SynapseKey) -> Synapse | None:
        if type(key) is not SynapseKey:
            raise ValueError("key must be SynapseKey")
        return self._state.synapses.get(key)

    def synapses(self) -> tuple[Synapse, ...]:
        return tuple(
            self._state.synapses[key] for key in sorted(self._state.synapses, key=key_order)
        )

    def reserved_keys(self) -> tuple[SynapseKey, ...]:
        return tuple(sorted(self._state.reservations, key=key_order))

    def reservation_claimants(self, key: SynapseKey) -> frozenset[int]:
        if type(key) is not SynapseKey:
            raise ValueError("key must be SynapseKey")
        return self._state.reservations.get(key, frozenset())

    def outgoing_keys(self, source_id: int) -> tuple[SynapseKey, ...]:
        CellAddress.from_cell_id(source_id)
        return tuple(sorted(self._state.outgoing.get(source_id, ()), key=key_order))

    def outgoing_usage(self, source_id: int) -> OutgoingUsage:
        keys = self.outgoing_keys(source_id)
        return outgoing_usage(
            keys,
            (
                key
                for key in keys
                if (s := self.synapse(key)) and s.state is SynapseState.EPISODIC_INDEXED
            ),
        )

    def quality(self, key: SynapseKey) -> float:
        return quality(self.synapse(key))

    def initialize_latent_neighborhoods(self) -> None:
        raise ValueError("UNVERIFIED_EVENT_SNAPSHOT: use pure selectors or explicit FixtureBuilder")

    @property
    def automatic_recycling_enabled(self) -> bool:
        return False

    def recycle_slot(
        self, owner_id: int, slot_index: int, *, novelty: VerifiedLocalNovelty | None = None
    ) -> None:
        # Protection diagnostics remain useful, but no caller can enable production.
        bilateral_occurrences(self._state, owner_id, slot_index)
        raise ValueError("UNVERIFIED_NOVELTY: production automatic recycling is disabled")

    def initialization(self, owner_id: int) -> InitializationRecord | None:
        CellAddress.from_cell_id(owner_id)
        return self._state.initializations.get(owner_id)

    def recycling_log(self) -> tuple[RecyclingRecord, ...]:
        return self._state.recycling_log

    def validate_graph(self) -> AuditReport:
        from dgca_next.graph.audit import validate_graph

        return validate_graph(self)

    def debug_dump(self) -> str:
        """Canonical diagnostic, not a durable checkpoint. Includes all indices.

        Binary64 fields use big-endian hex. Wiring history is an administrative
        sorted multiset, not a root/event execution journal.
        """

        def number(value: float) -> str:
            return struct.pack(">d", 0.0 if value == 0 else value).hex()

        state = self._state
        return json.dumps(
            {
                "fixture_only": True,
                "cells": [
                    [
                        c.cell_id,
                        c.committed,
                        c.committed_event,
                        c.fixture_only,
                        sorted(c.assembly_ids),
                    ]
                    for c in self.stored_cells()
                ],
                "slots": [
                    [
                        owner,
                        s.index,
                        s.category.value,
                        s.permitted_region.value,
                        s.target_id,
                        s.protected,
                        sorted(s.pin_owners),
                    ]
                    for owner in sorted(state.slots)
                    for s in state.slots[owner]
                ],
                "reverse": [
                    [target, sorted(refs)] for target, refs in sorted(state.reverse.items())
                ],
                "synapses": [
                    [
                        key_order(s.key),
                        s.delta,
                        s.state.value,
                        number(s.S),
                        number(s.E_ext),
                        number(s.E_int),
                        s.external_root_count,
                        s.created_event,
                        s.fixture_only,
                        s.protected,
                    ]
                    for s in self.synapses()
                ],
                "reservations": [
                    [key_order(key), sorted(state.reservations[key])]
                    for key in self.reserved_keys()
                ],
                "outgoing": [
                    [source, [key_order(k) for k in self.outgoing_keys(source)]]
                    for source in sorted(state.outgoing)
                ],
                "wiring_log": sorted(state.wiring_log),
                **(
                    {
                        "slot_assignments": [
                            [owner, s.index, asdict(s.assignment)]
                            for owner in sorted(state.slots)
                            for s in state.slots[owner]
                            if s.assignment is not None
                        ]
                    }
                    if any(
                        s.assignment is not None for slots in state.slots.values() for s in slots
                    )
                    else {}
                ),
                **(
                    {
                        "latent_initializations": [
                            asdict(state.initializations[owner])
                            for owner in sorted(state.initializations)
                        ]
                    }
                    if state.initializations
                    else {}
                ),
                **(
                    {"recycling_log": [asdict(record) for record in state.recycling_log]}
                    if state.recycling_log
                    else {}
                ),
            },
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )

    @property
    def structural_hash(self) -> str:
        return hashlib.sha256(self.debug_dump().encode("utf-8")).hexdigest()


class _Editor:
    """Private mutable fixture shadow; published by one pointer assignment."""

    def __init__(
        self, network: SparseNetwork, hook: Callable[[MutationStage], None] | None = None
    ) -> None:
        self.network = network
        self.hook = hook
        self.base = network._state
        self.cells = dict(self.base.cells)
        self.slots = dict(self.base.slots)
        self.reverse = dict(self.base.reverse)
        self.synapses = dict(self.base.synapses)
        self.reservations = dict(self.base.reservations)
        self.outgoing = dict(self.base.outgoing)
        self.wiring_log = list(self.base.wiring_log)
        self.initializations = dict(self.base.initializations)
        self.recycling_log = list(self.base.recycling_log)

    def checkpoint(self, stage: MutationStage) -> None:
        if self.hook is not None:
            self.hook(stage)

    def state(self) -> _State:
        return _State(
            cells=MappingProxyType(dict(self.cells)),
            slots=MappingProxyType(dict(self.slots)),
            reverse=MappingProxyType(dict(self.reverse)),
            synapses=MappingProxyType(dict(self.synapses)),
            reservations=MappingProxyType(dict(self.reservations)),
            outgoing=MappingProxyType(dict(self.outgoing)),
            wiring_log=tuple(self.wiring_log),
            initializations=MappingProxyType(dict(self.initializations)),
            recycling_log=tuple(self.recycling_log),
        )

    def require_committed(self, cell_id: int) -> Cell:
        CellAddress.from_cell_id(cell_id)
        cell = self.cells.get(cell_id)
        if cell is None or not cell.committed:
            raise ValueError("UNCOMMITTED_ENDPOINT")
        return cell

    def commit_cells(self, cell_ids: Iterable[int], *, committed_event: int) -> None:
        for cell_id in cell_ids:
            cell = Cell(CellAddress.from_cell_id(cell_id), True, committed_event, True)
            if cell_id in self.cells and self.cells[cell_id] != cell:
                raise ValueError("CONFLICTING_DUPLICATE_CELL")
            self.cells[cell_id] = cell
            self.checkpoint(MutationStage.CELL)

    def _store_layout(self, owner_id: int, layout: tuple[LatentSlot, ...]) -> None:
        old_slots = self.slots.get(
            owner_id, empty_slots(self.require_committed(owner_id).address.region)
        )
        self.slots.setdefault(owner_id, old_slots)
        for old, new in zip(old_slots, layout, strict=True):
            if old == new:
                continue
            self._replace_slot(owner_id, new)
            if old.target_id is not None:
                refs = self.reverse[old.target_id] - {(owner_id, old.index)}
                if refs:
                    self.reverse[old.target_id] = refs
                else:
                    del self.reverse[old.target_id]
            if new.target_id is not None:
                self.reverse[new.target_id] = self.reverse.get(new.target_id, frozenset()) | {
                    (owner_id, new.index)
                }
            self.checkpoint(MutationStage.REVERSE_INDEX)
            if old.target_id != new.target_id:
                self.wiring_log.append(
                    (
                        owner_id,
                        old.index,
                        old.target_id if old.target_id is not None else -1,
                        new.target_id if new.target_id is not None else -1,
                    )
                )

    def initialize_cohort(self, event: FixtureEventSnapshot) -> None:
        validate_fixture_event(event, self.cells, births_pending=True)
        for record in self.initializations.values():
            prior = record.assignment
            if (prior.exposure_id, prior.event_id, prior.event_order) == (
                event.exposure_id,
                event.event_id,
                event.event_order,
            ) and record.snapshot_digest != event.digest:
                raise ValueError("CONFLICTING_COBIRTH_SNAPSHOT")
        # Retry only the exact whole-cohort snapshot; never retroactively initialize.
        if any(owner in self.cells for owner in event.birth_ids):
            if all(
                owner in self.initializations
                and not self.initializations[owner].contextual
                and self.initializations[owner].snapshot_digest == event.digest
                for owner in event.birth_ids
            ):
                return
            raise ValueError("CONFLICTING_BIRTH_COHORT")
        layouts = {owner: initialize_layout(owner, event) for owner in sorted(event.birth_ids)}
        self.commit_cells(sorted(event.birth_ids), committed_event=event.event_id)
        for owner, layout in layouts.items():
            self._store_layout(owner, layout)
            self.initializations[owner] = InitializationRecord(
                owner,
                event.digest,
                False,
                (),
                event.assignment(pending_birth=True),
                LATENT_POLICY_VERSION,
            )
            self._update_budget(owner)
            self.checkpoint(MutationStage.BUDGET)

    def initialize_context_cell(
        self, owner_id: int, event: FixtureEventSnapshot, pinned_slots: tuple[LatentSlot, ...]
    ) -> None:
        validate_fixture_event(event, self.cells)
        layout = initialize_layout(owner_id, event, pinned_slots=pinned_slots, contextual=True)
        seeds = tuple(sorted(s.target_id for s in pinned_slots if s.target_id is not None))
        for target in seeds:
            self.require_committed(target)
        record = InitializationRecord(
            owner_id,
            event.digest,
            True,
            seeds,
            event.assignment(pending_birth=False),
            LATENT_POLICY_VERSION,
        )
        if owner_id in self.cells:
            if self.initializations.get(owner_id) == record:
                return
            raise ValueError("CONFLICTING_BIRTH_COHORT")
        self.commit_cells([owner_id], committed_event=event.event_id)
        self._store_layout(owner_id, layout)
        self.initializations[owner_id] = record
        self._update_budget(owner_id)
        self.checkpoint(MutationStage.BUDGET)

    def fill_coactive(self, owner_id: int, event: FixtureEventSnapshot) -> None:
        validate_fixture_event(event, self.cells)
        if owner_id not in self.initializations:
            raise ValueError("UNINITIALIZED_LATENT_POLICY")
        previous = self.slots[owner_id]
        layout = fill_coactive(owner_id, previous, event, pending_birth=False)
        if layout != previous:
            assignments = [s.assignment for s in previous if s.assignment is not None]
            if any(
                a.event_id >= event.event_id
                or a.completed_close_serial > event.completed_external_closes
                for a in assignments
            ):
                raise ValueError("UNVERIFIED_EVENT_SNAPSHOT: RETROACTIVE_FILL")
        self._store_layout(owner_id, layout)
        self._update_budget(owner_id)
        self.checkpoint(MutationStage.BUDGET)

    def inject_slot(self, owner_id: int, slot_index: int, target_id: int) -> None:
        self.require_committed(owner_id)
        self.require_committed(target_id)
        if owner_id == target_id:
            raise ValueError("LATENT_SELF_TARGET")
        if type(slot_index) is not int or not 0 <= slot_index < 24:
            raise ValueError("INVALID_SLOT_INDEX")
        slots = self.slots.get(owner_id, empty_slots(CellAddress.from_cell_id(owner_id).region))
        slot = slots[slot_index]
        if slot.target_id == target_id:
            return
        if slot.target_id is not None:
            raise ValueError("CONFLICTING_DUPLICATE_SLOT")
        if any(s.target_id == target_id for s in slots):
            raise ValueError("DUPLICATE_LATENT_TARGET")
        replacement = replace(slot, target_id=target_id)
        if slot.category is SlotCategory.LOCAL and microcolumn_of(target_id) not in (
            microcolumn_neighborhood(owner_id, 1)
        ):
            raise ValueError("LOCAL_SLOT_OUTSIDE_VICINITY")
        self.slots[owner_id] = slots[:slot_index] + (replacement,) + slots[slot_index + 1 :]
        self.checkpoint(MutationStage.SLOT)
        self.reverse[target_id] = self.reverse.get(target_id, frozenset()) | {
            (owner_id, slot_index)
        }
        self.checkpoint(MutationStage.REVERSE_INDEX)
        self.wiring_log.append((owner_id, slot_index, -1, target_id))

    def pin_slot(self, owner_id: int, slot_index: int, claimant_id: int) -> None:
        self.require_committed(claimant_id)
        slot = self._occupied_slot(owner_id, slot_index)
        self._replace_slot(owner_id, replace(slot, pin_owners=slot.pin_owners | {claimant_id}))

    def protect_slot(self, owner_id: int, slot_index: int) -> None:
        slot = self._occupied_slot(owner_id, slot_index)
        self._replace_slot(owner_id, replace(slot, protected=True))

    def _occupied_slot(self, owner_id: int, slot_index: int) -> LatentSlot:
        self.require_committed(owner_id)
        if type(slot_index) is not int or not 0 <= slot_index < 24:
            raise ValueError("INVALID_SLOT_INDEX")
        slot = self.slots.get(owner_id, empty_slots(CellAddress.from_cell_id(owner_id).region))[
            slot_index
        ]
        if slot.target_id is None:
            raise ValueError("EMPTY_SLOT")
        return slot

    def _replace_slot(self, owner_id: int, slot: LatentSlot) -> None:
        slots = self.slots[owner_id]
        self.slots[owner_id] = slots[: slot.index] + (slot,) + slots[slot.index + 1 :]
        self.checkpoint(MutationStage.SLOT)

    def check_slot_removal(self, owner_id: int, slot_index: int) -> LatentSlot:
        slot = self._occupied_slot(owner_id, slot_index)
        if not slot.recyclable_category:
            raise ValueError("RECYCLE_BLOCKED_FIXED")
        # Live protection has priority over candidate pins (Core §1.3).
        if slot.protected or any(
            {key.source.cell_id, key.target.cell_id} == {owner_id, slot.target_id}
            for key in self.synapses
        ):
            raise ValueError("RECYCLE_BLOCKED_LIVE_OR_PROTECTED")
        if slot.pinned:
            raise ValueError("RECYCLE_BLOCKED_CANDIDATE")
        return slot

    def remove_fixture_slot(self, owner_id: int, slot_index: int) -> None:
        """Explicit synthetic teardown only; never production recycling."""
        slot = self.check_slot_removal(owner_id, slot_index)
        assert slot.target_id is not None
        # Retain structural validity of any pending intended keys as well.
        if any(
            {k.source.cell_id, k.target.cell_id} == {owner_id, slot.target_id}
            for k in self.reservations
        ):
            raise ValueError("RELEASE_FIXTURE_RESERVATION_FIRST")
        self._replace_slot(owner_id, replace(slot, target_id=None, assignment=None))
        refs = self.reverse[slot.target_id] - {(owner_id, slot_index)}
        if refs:
            self.reverse[slot.target_id] = refs
        else:
            del self.reverse[slot.target_id]
        self.checkpoint(MutationStage.REVERSE_INDEX)
        self.wiring_log.append((owner_id, slot_index, slot.target_id, -1))

    def recycle_slot(
        self,
        owner_id: int,
        slot_index: int,
        *,
        event: FixtureEventSnapshot | None = None,
        novelty: FixtureLocalNovelty | None = None,
    ) -> None:
        if type(event) is FixtureEventSnapshot and type(novelty) is FixtureLocalNovelty:
            for record in reversed(self.recycling_log):
                if record.snapshot_digest == event.digest and any(
                    change[:2] == (owner_id, slot_index) for change in record.changes
                ):
                    if record.novelty_digest == novelty.digest and all(
                        self.slots[owner][index].target_id == new
                        for owner, index, _, new in record.changes
                    ):
                        return
                    raise ValueError("CONFLICTING_RECYCLING_RETRY")
        replacements = plan_fixture_recycling(self.state(), owner_id, slot_index, event, novelty)
        assert event is not None and novelty is not None
        changes = []
        for owner, new in replacements:
            old = self.slots[owner][new.index]
            assert old.target_id is not None and new.target_id is not None
            changes.append((owner, new.index, old.target_id, new.target_id))
            layout = self.slots[owner]
            self._store_layout(owner, layout[: new.index] + (new,) + layout[new.index + 1 :])
        self.recycling_log.append(
            RecyclingRecord(
                event.exposure_id,
                event.event_id,
                event.event_order,
                event.completed_external_closes,
                tuple(changes),
                event.digest,
                novelty.digest,
                LATENT_POLICY_VERSION,
            )
        )
        for owner, _ in replacements:
            self._update_budget(owner)
            self.checkpoint(MutationStage.BUDGET)

    def _require_key(self, key: SynapseKey) -> None:
        if type(key) is not SynapseKey:
            raise ValueError("INVALID_SYNAPSE_KEY")
        self.require_committed(key.source.cell_id)
        self.require_committed(key.target.cell_id)
        first, second = key.source.cell_id, key.target.cell_id
        if not any(s.target_id == second for s in self.slots.get(first, ())) and not any(
            s.target_id == first for s in self.slots.get(second, ())
        ):
            raise ValueError("MISSING_LATENT_ELIGIBILITY")

    def _update_budget(self, source_id: int) -> None:
        keys = self.outgoing.get(source_id, frozenset())
        validate_usage(
            outgoing_usage(
                keys,
                (
                    k
                    for k in keys
                    if k in self.synapses
                    and self.synapses[k].state is SynapseState.EPISODIC_INDEXED
                ),
            )
        )
        episodic_count = sum(
            s.state is SynapseState.EPISODIC_INDEXED for s in self.synapses.values()
        )
        # LLA §4.4 floor(.10 * committedCells), exact for this fixed decimal.
        if episodic_count > len(self.cells) // 10:
            raise ValueError("NETWORK_EPISODIC_CAPACITY")

    def reserve(self, key: SynapseKey, claimant_id: int) -> None:
        self._require_key(key)
        self.require_committed(claimant_id)
        if key in self.synapses:
            return
        self.reservations[key] = self.reservations.get(key, frozenset()) | {claimant_id}
        self.checkpoint(MutationStage.RESERVATION)
        source_id = key.source.cell_id
        self.outgoing[source_id] = self.outgoing.get(source_id, frozenset()) | {key}
        self.checkpoint(MutationStage.BUDGET)
        self._update_budget(source_id)

    def release(self, key: SynapseKey, claimant_id: int) -> None:
        if type(key) is not SynapseKey:
            raise ValueError("INVALID_SYNAPSE_KEY")
        CellAddress.from_cell_id(claimant_id)
        remaining = self.reservations.get(key, frozenset()) - {claimant_id}
        if remaining:
            self.reservations[key] = remaining
            self.checkpoint(MutationStage.RESERVATION)
        elif key in self.reservations:
            del self.reservations[key]
            self.checkpoint(MutationStage.RESERVATION)
            self._uncharge_if_unused(key)

    def _uncharge_if_unused(self, key: SynapseKey) -> None:
        if key not in self.synapses and key not in self.reservations:
            source = key.source.cell_id
            keys = self.outgoing[source] - {key}
            if keys:
                self.outgoing[source] = keys
            else:
                del self.outgoing[source]
            self.checkpoint(MutationStage.BUDGET)

    def add_synapse(self, synapse: Synapse) -> None:
        if type(synapse) is not Synapse:
            raise ValueError("INVALID_SYNAPSE_SCHEMA")
        self._require_key(synapse.key)
        key = synapse.key
        if key in self.synapses:
            if self.synapses[key] != synapse:
                raise ValueError("CONFLICTING_DUPLICATE_SYNAPSE")
            return
        source = self.cells[key.source.cell_id]
        target = self.cells[key.target.cell_id]
        assert source.committed_event is not None and target.committed_event is not None
        if source.committed_event >= synapse.created_event - synapse.delta or (
            target.committed_event >= synapse.created_event
        ):
            raise ValueError("COMMITMENT_TIMING")
        self.synapses[key] = synapse
        self.checkpoint(MutationStage.LINK)
        self.reservations.pop(key, None)
        self.checkpoint(MutationStage.RESERVATION)
        self.outgoing[source.cell_id] = self.outgoing.get(source.cell_id, frozenset()) | {key}
        self.checkpoint(MutationStage.BUDGET)
        self._update_budget(source.cell_id)

    def remove_synapse(self, key: SynapseKey) -> None:
        if type(key) is not SynapseKey:
            raise ValueError("INVALID_SYNAPSE_KEY")
        existing = self.synapses.get(key)
        if existing is None:
            return
        if existing.state is SynapseState.CONSOLIDATED or existing.protected:
            raise ValueError("PROTECTED_SYNAPSE")
        if any(
            slot.pinned and slot.target_id in (key.source.cell_id, key.target.cell_id)
            for owner in (key.source.cell_id, key.target.cell_id)
            for slot in self.slots.get(owner, ())
        ):
            raise ValueError("PINNED_SYNAPSE")
        del self.synapses[key]
        self.checkpoint(MutationStage.LINK)
        self._uncharge_if_unused(key)

    def set_memberships(self, cell_id: int, assembly_ids: frozenset[int]) -> None:
        cell = self.require_committed(cell_id)
        self.cells[cell_id] = replace(cell, assembly_ids=assembly_ids)
        self.checkpoint(MutationStage.CELL)

    def publish(self) -> None:
        from dgca_next.graph.audit import validate_state, validate_transition

        if self.network._state is not self.base:
            raise ValueError("STALE_SHADOW_TRANSACTION")
        candidate = self.state()
        validate_state(candidate)
        validate_transition(self.base, candidate)
        self.checkpoint(MutationStage.PUBLISH)
        if self.network._state is not self.base:
            raise ValueError("STALE_SHADOW_TRANSACTION")
        if candidate != self.base:
            self.network._state = candidate


class FixtureBuilder:
    """Explicit isolated fixture API. No production commitment or LLA interface."""

    def __init__(self, network: SparseNetwork) -> None:
        if type(network) is not SparseNetwork:
            raise ValueError("network must be SparseNetwork")
        self._network = network

    def _apply(self, operation: Callable[[_Editor], None]) -> None:
        shadow = _Editor(self._network)
        operation(shadow)
        shadow.publish()

    def commit_cells(self, cell_ids: Iterable[int], *, committed_event: int) -> None:
        self._apply(lambda shadow: shadow.commit_cells(cell_ids, committed_event=committed_event))

    def transaction(self, *, fail_at: MutationStage | None = None) -> FixtureTransaction:
        from dgca_next.graph.transaction import FixtureTransaction

        return FixtureTransaction(self._network, fail_at=fail_at)

    def inject_slot(self, owner_id: int, slot_index: int, target_id: int) -> None:
        self._apply(lambda shadow: shadow.inject_slot(owner_id, slot_index, target_id))

    def pin_slot(self, owner_id: int, slot_index: int, claimant_id: int) -> None:
        self._apply(lambda shadow: shadow.pin_slot(owner_id, slot_index, claimant_id))

    def protect_slot(self, owner_id: int, slot_index: int) -> None:
        self._apply(lambda shadow: shadow.protect_slot(owner_id, slot_index))

    def remove_fixture_slot(self, owner_id: int, slot_index: int) -> None:
        self._apply(lambda shadow: shadow.remove_fixture_slot(owner_id, slot_index))

    def initialize_cohort(self, event: FixtureEventSnapshot) -> None:
        self._apply(lambda shadow: shadow.initialize_cohort(event))

    def initialize_context_cell(
        self, owner_id: int, event: FixtureEventSnapshot, pinned_slots: tuple[LatentSlot, ...]
    ) -> None:
        self._apply(lambda shadow: shadow.initialize_context_cell(owner_id, event, pinned_slots))

    def fill_coactive(self, owner_id: int, event: FixtureEventSnapshot) -> None:
        self._apply(lambda shadow: shadow.fill_coactive(owner_id, event))

    def recycle_slot(
        self,
        owner_id: int,
        slot_index: int,
        *,
        event: FixtureEventSnapshot | None = None,
        novelty: FixtureLocalNovelty | None = None,
    ) -> None:
        self._apply(
            lambda shadow: shadow.recycle_slot(owner_id, slot_index, event=event, novelty=novelty)
        )

    def add_synapse(self, synapse: Synapse) -> None:
        self._apply(lambda shadow: shadow.add_synapse(synapse))

    def remove_synapse(self, key: SynapseKey) -> None:
        self._apply(lambda shadow: shadow.remove_synapse(key))

    def reserve(self, key: SynapseKey, claimant_id: int) -> None:
        self._apply(lambda shadow: shadow.reserve(key, claimant_id))

    def release(self, key: SynapseKey, claimant_id: int) -> None:
        self._apply(lambda shadow: shadow.release(key, claimant_id))

    def set_memberships(self, cell_id: int, assembly_ids: frozenset[int]) -> None:
        self._apply(lambda shadow: shadow.set_memberships(cell_id, assembly_ids))
