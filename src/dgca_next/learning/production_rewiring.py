"""Root-journal-scoped physical replacement after ordinary evidence settlement."""

import hashlib
import sqlite3
from dataclasses import replace
from types import MappingProxyType

from dgca_next.graph.audit import validate_state, validate_transition
from dgca_next.graph.cell import ProductionAdmission
from dgca_next.graph.latent import LATENT_POLICY_VERSION, SlotAssignment
from dgca_next.graph.network import SparseNetwork
from dgca_next.graph.recycling import ProductionRecyclingRecord
from dgca_next.learning.novelty import _inspect_recycling, _verified_novelty


def _rewire_at_end(
    connection: sqlite3.Connection,
    graph: SparseNetwork,
    exposure: int,
    last_order: int,
    requested_order: int,
    owner: int,
    index: int,
    serial: int,
    *,
    replay: bool = False,
) -> tuple[SparseNetwork, str]:
    """Recompute authority and guards; caller owns the atomic END transaction."""
    if requested_order != last_order:
        return graph, "STALE_TRIGGER_EVENT"
    target = graph.latent_slots(owner)[index].target_id
    if target is None:
        return graph, "EMPTY_SLOT"
    novelty = event = None
    decision = None
    for receiver in sorted((owner, target)):
        try:
            candidate, candidate_event = _verified_novelty(
                connection, exposure, last_order, receiver, verify_activation=not replay
            )
        except ValueError:
            continue
        candidate_decision = _inspect_recycling(
            graph,
            serial,
            owner,
            index,
            candidate,
            candidate_event,
            candidate_event.event_id,
            staged_at_end=True,
        )
        novelty, event, decision = candidate, candidate_event, candidate_decision
        if candidate_decision.reason != "UNVERIFIED_NOVELTY":
            break
    if decision is None:
        decision = _inspect_recycling(
            graph, serial, owner, index, None, None, -1, staged_at_end=True
        )
    if not decision.allowed:
        return graph, decision.reason
    assert novelty is not None and event is not None
    admission = ProductionAdmission(exposure, event.event_id, last_order, event.digest)
    assignment = SlotAssignment(
        serial, exposure, event.event_id, last_order, False, LATENT_POLICY_VERSION, False, admission
    )
    slots = dict(graph._state.slots)
    changes = []
    for source, slot_index, new_target in decision.replacements:
        layout = slots[source]
        old = layout[slot_index]
        assert old.target_id is not None
        changes.append((source, slot_index, old.target_id, new_target))
        slots[source] = (
            *layout[:slot_index],
            replace(old, target_id=new_target, assignment=assignment),
            *layout[slot_index + 1 :],
        )
    reverse: dict[int, frozenset[tuple[int, int]]] = {}
    for source, layout in slots.items():
        for slot in layout:
            if slot.target_id is not None:
                reverse[slot.target_id] = reverse.get(slot.target_id, frozenset()) | {
                    (source, slot.index)
                }
    ordered_changes = tuple(sorted(changes))
    proof = hashlib.sha256(
        f"{event.digest}:{novelty.receiver_id}:{novelty.pre_input_prediction.hex()}:"
        f"{novelty.novelty_q6}".encode("ascii")
    ).hexdigest()
    record = ProductionRecyclingRecord(
        exposure,
        event.event_id,
        last_order,
        serial,
        ordered_changes,
        event.digest,
        proof,
        LATENT_POLICY_VERSION,
        novelty.receiver_id,
        novelty.x_fixed,
        novelty.pre_input_prediction,
        novelty.novelty_q6,
    )
    state = replace(
        graph._state,
        slots=MappingProxyType(slots),
        reverse=MappingProxyType(reverse),
        wiring_log=(*graph._state.wiring_log, *ordered_changes),
        recycling_log=(*graph._state.recycling_log, record),
    )
    validate_state(state)
    validate_transition(graph._state, state)
    result = SparseNetwork()
    result._state = state
    return result, "RECYCLED"
