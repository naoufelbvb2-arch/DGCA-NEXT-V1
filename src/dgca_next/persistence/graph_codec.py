"""Canonical P02 production W encoding; fixture graph records are forbidden."""

import math
from dataclasses import replace
from types import MappingProxyType

from dgca_next.contracts import CellAddress, SynapseKey, SynapseScope
from dgca_next.graph.cell import Cell, ProductionAdmission
from dgca_next.graph.latent import LATENT_POLICY_VERSION, SlotAssignment, empty_slots
from dgca_next.graph.network import SparseNetwork, _State
from dgca_next.graph.policy import InitializationRecord
from dgca_next.graph.synapse import ProductionCredit, Synapse, SynapseState
from dgca_next.persistence.binary_records import decode_record, encode_record

_TAG = 0x57
_VERSION = 2


def _key(key: SynapseKey) -> list[object]:
    return [key.source.cell_id, key.target.cell_id, key.scope.value]


def _read_key(row: list[object]) -> SynapseKey:
    if type(row) is not list or len(row) != 3:
        raise ValueError("INVALID_PRODUCTION_KEY")
    source, target, scope = row
    if type(source) is not int or type(target) is not int or type(scope) is not str:
        raise ValueError("INVALID_PRODUCTION_KEY")
    return SynapseKey(
        CellAddress.from_cell_id(source), CellAddress.from_cell_id(target), SynapseScope(scope)
    )


def _float(value: object) -> float:
    if type(value) is not float:
        raise ValueError("INVALID_PRODUCTION_NUMBER")
    if not math.isfinite(value) or value < 0:
        raise ValueError("NONCANONICAL_PRODUCTION_NUMBER")
    return value


def encode_production_graph(network: SparseNetwork) -> bytes:
    if type(network) is not SparseNetwork:
        raise ValueError("INVALID_PRODUCTION_GRAPH")
    network.validate_graph()
    state = network._state
    if (
        state.recycling_log
        or set(state.cells) != set(state.slots)
        or set(state.cells) != set(state.initializations)
    ):
        raise ValueError("UNSUPPORTED_PRODUCTION_W")
    rows = []
    for cell in network.stored_cells():
        a = cell.admission
        record = state.initializations[cell.cell_id]
        assignment = record.assignment
        if (
            cell.fixture_only
            or type(a) is not ProductionAdmission
            or record.contextual
            or cell.assembly_ids
        ):
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
        "links": [
            [
                _key(s.key),
                s.delta,
                s.state.value,
                s.S,
                s.E_ext,
                s.E_int,
                s.external_root_count,
                s.created_event,
                s.protected,
                s.candidate_deadline,
                [
                    [
                        c.root_id,
                        c.event_id,
                        c.event_order,
                        c.ordinal,
                        c.source_event_id,
                        c.source_digest,
                        c.target_digest,
                        c.source_activity,
                        c.target_activity,
                        c.target_threshold,
                        c.q,
                        c.y,
                    ]
                    for c in s.credits
                ],
            ]
            for s in network.synapses()
            if not s.fixture_only
        ],
        "reservations": [
            [_key(key), sorted(state.reservations[key])] for key in network.reserved_keys()
        ],
        "outgoing": [
            [i, [_key(key) for key in network.outgoing_keys(i)]] for i in sorted(state.outgoing)
        ],
    }
    if any(s.fixture_only for s in network.synapses()):
        raise ValueError("FIXTURE_GRAPH_FORBIDDEN")
    return encode_record(_TAG, _VERSION, payload)


def decode_production_graph(data: bytes) -> SparseNetwork:
    try:
        doc = decode_record(data, _TAG, _VERSION)
        if type(doc) is not dict or set(doc) != {
            "cells",
            "reverse",
            "wiring",
            "links",
            "reservations",
            "outgoing",
        }:
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
        synapses = {}
        for row in doc["links"]:
            if type(row) is not list or len(row) != 11 or type(row[10]) is not list:
                raise ValueError("INVALID_PRODUCTION_SYNAPSE")
            key = _read_key(row[0])
            if key in synapses:
                raise ValueError("DUPLICATE_PRODUCTION_SYNAPSE")
            credits = []
            for credit in row[10]:
                if type(credit) is not list or len(credit) != 12:
                    raise ValueError("INVALID_PRODUCTION_CREDIT")
                credits.append(
                    ProductionCredit(*credit[:7], *(_float(value) for value in credit[7:]))
                )
            synapses[key] = Synapse(
                key,
                row[1],
                SynapseState(row[2]),
                _float(row[3]),
                _float(row[4]),
                _float(row[5]),
                row[6],
                row[7],
                False,
                row[8],
                tuple(credits),
                row[9],
            )
        reservations = {}
        for row in doc["reservations"]:
            key = _read_key(row[0])
            if key in reservations:
                raise ValueError("DUPLICATE_RESERVATION")
            reservations[key] = frozenset(row[1])
        outgoing = {}
        for owner, keys in doc["outgoing"]:
            if type(owner) is not int or owner in outgoing:
                raise ValueError("INVALID_PRODUCTION_OUTGOING")
            outgoing[owner] = frozenset(_read_key(key) for key in keys)
        state = _State(
            cells=MappingProxyType(cells),
            slots=MappingProxyType(slots),
            reverse=MappingProxyType(reverse),
            synapses=MappingProxyType(synapses),
            reservations=MappingProxyType(reservations),
            outgoing=MappingProxyType(outgoing),
            wiring_log=wiring,
            initializations=MappingProxyType(initializations),
        )
        network = SparseNetwork()
        network._state = state
        if encode_production_graph(network) != data:
            raise ValueError("NONCANONICAL_PRODUCTION_W")
        return network
    except (UnicodeError, KeyError, TypeError, IndexError) as exc:
        raise ValueError("INVALID_PRODUCTION_W") from exc
