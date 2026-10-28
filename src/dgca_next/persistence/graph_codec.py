"""Canonical P01 production W encoding; fixtures and synapses are forbidden."""

import json
from dataclasses import replace
from types import MappingProxyType

from dgca_next.contracts import CellAddress
from dgca_next.graph.cell import Cell, ProductionAdmission
from dgca_next.graph.latent import LATENT_POLICY_VERSION, SlotAssignment, empty_slots
from dgca_next.graph.network import SparseNetwork, _State
from dgca_next.graph.policy import InitializationRecord

_TAG = b"DGCA-P01-W\x01\0"


def encode_production_graph(network: SparseNetwork) -> bytes:
    if type(network) is not SparseNetwork:
        raise ValueError("INVALID_PRODUCTION_GRAPH")
    network.validate_graph()
    state = network._state
    if (
        state.synapses
        or state.reservations
        or state.outgoing
        or state.recycling_log
        or set(state.cells) != set(state.slots)
        or set(state.cells) != set(state.initializations)
    ):
        raise ValueError("UNSUPPORTED_PRODUCTION_W")
    rows = []
    for cell in network.stored_cells():
        a = cell.admission
        record = state.initializations[cell.cell_id]
        assignment = record.assignment
        if cell.fixture_only or type(a) is not ProductionAdmission or record.contextual:
            raise ValueError("FIXTURE_GRAPH_FORBIDDEN")
        if record.seed_targets or assignment.admission != a or assignment.fixture_only:
            raise ValueError("INVALID_PRODUCTION_INITIALIZATION")
        layout = state.slots[cell.cell_id]
        if any(s.target_id is not None and s.assignment != assignment for s in layout):
            raise ValueError("INVALID_PRODUCTION_SLOT_ASSIGNMENT")
        if any(s.protected or s.pin_owners for s in layout):
            raise ValueError("UNSUPPORTED_PRODUCTION_SLOT")
        rows.append(
            [
                cell.cell_id,
                a.exposure_id,
                a.event_id,
                a.event_order,
                a.observation_digest,
                assignment.completed_close_serial,
                [slot.target_id for slot in layout],
            ]
        )
    payload = {
        "cells": rows,
        "reverse": [
            [i, [list(ref) for ref in sorted(refs)]] for i, refs in sorted(state.reverse.items())
        ],
        "wiring": [list(row) for row in state.wiring_log],
    }
    return (
        _TAG
        + json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()
    )


def decode_production_graph(data: bytes) -> SparseNetwork:
    if type(data) is not bytes or not data.startswith(_TAG):
        raise ValueError("UNSUPPORTED_PRODUCTION_W_SCHEMA")
    try:
        doc = json.loads(data[len(_TAG) :].decode("ascii"))
        if type(doc) is not dict or set(doc) != {"cells", "reverse", "wiring"}:
            raise ValueError("INVALID_PRODUCTION_W")
        if any(type(doc[k]) is not list for k in doc):
            raise ValueError("INVALID_PRODUCTION_W")
        cells, slots, initializations = {}, {}, {}
        last = -1
        for row in doc["cells"]:
            if type(row) is not list or len(row) != 7:
                raise ValueError("INVALID_PRODUCTION_CELL")
            owner, exposure, event, order, digest, closes, targets = row
            if (
                type(owner) is not int
                or owner <= last
                or type(targets) is not list
                or len(targets) != 24
            ):
                raise ValueError("INVALID_PRODUCTION_CELL")
            last = owner
            admission = ProductionAdmission(exposure, event, order, digest)
            assignment = SlotAssignment(
                closes, exposure, event, order, True, LATENT_POLICY_VERSION, False, admission
            )
            cells[owner] = Cell(
                CellAddress.from_cell_id(owner), True, event, False, frozenset(), admission
            )
            layout = empty_slots(cells[owner].address.region)
            slots[owner] = tuple(
                replace(
                    slot, target_id=target, assignment=assignment if target is not None else None
                )
                for slot, target in zip(layout, targets, strict=True)
            )
            initializations[owner] = InitializationRecord(
                owner, digest, False, (), assignment, LATENT_POLICY_VERSION
            )
        reverse = {}
        for row in doc["reverse"]:
            if (
                type(row) is not list
                or len(row) != 2
                or type(row[0]) is not int
                or type(row[1]) is not list
            ):
                raise ValueError("INVALID_PRODUCTION_REVERSE")
            target, refs = row
            if target in reverse:
                raise ValueError("INVALID_PRODUCTION_REVERSE")
            reverse[target] = frozenset(tuple(ref) for ref in refs)
        wiring = tuple(tuple(row) for row in doc["wiring"])
        state = _State(
            cells=MappingProxyType(cells),
            slots=MappingProxyType(slots),
            reverse=MappingProxyType(reverse),
            wiring_log=wiring,
            initializations=MappingProxyType(initializations),
        )
        network = SparseNetwork()
        network._state = state
        if encode_production_graph(network) != data:
            raise ValueError("NONCANONICAL_PRODUCTION_W")
        return network
    except (UnicodeError, json.JSONDecodeError, KeyError, TypeError, IndexError) as exc:
        raise ValueError("INVALID_PRODUCTION_W") from exc
