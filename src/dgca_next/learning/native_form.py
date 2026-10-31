"""Trusted first-FORM shadow, invoked only by Schema-5 atomic END/replay."""

import hashlib
import sqlite3
from dataclasses import dataclass, replace
from types import MappingProxyType

from dgca_next.contracts import Region
from dgca_next.graph.assembly_support import inspect_structure
from dgca_next.graph.native_assembly import _assembly_record, _form_record, _next_native_id
from dgca_next.graph.network import SparseNetwork
from dgca_next.learning.settlement import CloseResult, decode_close, encode_close
from dgca_next.persistence.binary_records import decode_record, encode_record
from dgca_next.persistence.form_inspection import _project_candidates, _qualified_events
from dgca_next.persistence.native_codec import decode_native_graph, encode_native_graph


@dataclass(frozen=True, slots=True)
class NativeCloseResult(CloseResult):
    form_reason: str
    formed_ids: tuple[int, ...]


def _form_at_end(
    connection: sqlite3.Connection, graph: SparseNetwork, result: CloseResult, *, replay: bool
) -> tuple[SparseNetwork, NativeCloseResult]:
    graph.validate_graph()
    if graph._state.native_assemblies:
        raise ValueError("I4_UNIMPLEMENTED_MAINTAIN_GROW")
    if graph._state.reservations or graph._state.recycling_log:
        raise ValueError("I4_REWIRING_CONFLICT")
    row = connection.execute(
        "SELECT status,next_order FROM p01_roots WHERE exposure_id=?", (result.exposure_id,)
    ).fetchone()
    if row is None or row[0] != ("COMPLETED" if replay else "OPEN"):
        raise ValueError("UNVERIFIED_NATIVE_FORM_ROOT")
    structure = inspect_structure(graph)
    events = _qualified_events(
        connection,
        result.exposure_id,
        structure.committed,
        row[1],
        graph_decoder=decode_native_graph,
        replay=replay,
    )
    candidates = _project_candidates(structure, events)
    seeds = tuple(c for c in candidates if c.selected)
    # This approved vertical slice may publish one first Assembly. Do not
    # silently redefine the scientific 12-seed limit for a larger experiment.
    if len(seeds) > 1:
        raise ValueError("I4_FIRST_FORM_LAB_SCOPE_EXCEEDED")
    if not seeds:
        reason = (
            "NO_RECIPROCAL_TRIANGLE"
            if not any(t.eligible for t in structure.triangles)
            else "NO_QUALIFIED_FORM_EVENT"
        )
        return graph, NativeCloseResult(
            result.exposure_id,
            result.close_serial,
            result.event_clock,
            result.accepted,
            result.refused,
            result.graph_hash,
            reason,
            (),
        )
    seed = seeds[0]
    event = next(e for e in events if e.event_id == seed.event_id)
    witnesses = {w.cell_id: w for w in event.witnesses}
    sampled = []
    for member in seed.triangle.members:
        w = witnesses[member]
        if (
            not w.qualified
            or w.committed_event is None
            or w.final_activity is None
            or w.theta_emit is None
        ):
            raise ValueError("UNVERIFIED_NATIVE_FORM_WITNESS")
        sampled.append(
            (member, w.direct_x_fixed, w.committed_event, w.final_activity, w.theta_emit)
        )
    high = graph._state.assembly_high_watermarks[Region.LANGUAGE]
    identity = _next_native_id(high, graph._state.native_assemblies)
    assembly = _assembly_record(
        identity,
        Region.LANGUAGE,
        seed.triangle.members,
        1,
        result.close_serial,
        result.close_serial,
        None,
        "LIVE",
    )
    record = _form_record(
        identity,
        result.exposure_id,
        event.event_id,
        event.event_order,
        result.close_serial,
        seed.triangle.members,
        event.observation_digest,
        event.pre_w_hash,
        event.pre_h_hash,
        hashlib.sha256(encode_native_graph(graph)).hexdigest(),
        tuple(sampled),
    )
    cells = dict(graph._state.cells)
    reverse = dict(graph._state.member_assemblies)
    for member in assembly.member_cell_ids:
        cells[member] = replace(cells[member], assembly_ids=cells[member].assembly_ids | {identity})
        reverse[member] = reverse.get(member, frozenset()) | {identity}
    state = replace(
        graph._state,
        cells=MappingProxyType(cells),
        native_assemblies=MappingProxyType({**graph._state.native_assemblies, identity: assembly}),
        assembly_high_watermarks=MappingProxyType({Region.LANGUAGE: identity}),
        member_assemblies=MappingProxyType(reverse),
        native_form_log=(*graph._state.native_form_log, record),
    )
    after = SparseNetwork()
    after._state = state
    after.validate_graph()
    if after.synapses() != graph.synapses() or after._state.slots != graph._state.slots:
        raise ValueError("FORM_CHANGED_PHYSICAL_KNOWLEDGE")
    final_hash = hashlib.sha256(encode_native_graph(after)).hexdigest()
    return after, NativeCloseResult(
        result.exposure_id,
        result.close_serial,
        result.event_clock,
        result.accepted,
        result.refused,
        final_hash,
        "FORMED",
        (identity,),
    )


def encode_native_close(close: CloseResult) -> bytes:
    result = close
    if (
        type(result) is not NativeCloseResult
        or result.form_reason not in ("FORMED", "NO_RECIPROCAL_TRIANGLE", "NO_QUALIFIED_FORM_EVENT")
        or (result.form_reason == "FORMED") != bool(result.formed_ids)
    ):
        raise ValueError("INVALID_NATIVE_CLOSE_RESULT")
    base = CloseResult(
        result.exposure_id,
        result.close_serial,
        result.event_clock,
        result.accepted,
        result.refused,
        result.graph_hash,
    )
    return encode_record(
        0x43,
        5,
        {
            "base": encode_close(base),
            "form_reason": result.form_reason,
            "formed_ids": list(result.formed_ids),
        },
    )


def decode_native_close(data: bytes) -> NativeCloseResult:
    try:
        doc = decode_record(data, 0x43, 5)
        if type(doc) is not dict or set(doc) != {"base", "form_reason", "formed_ids"}:
            raise ValueError("INVALID_NATIVE_CLOSE_RECORD")
        base = decode_close(doc["base"])
        ids = tuple(doc["formed_ids"])
        if any(type(i) is not int or i < 0 for i in ids) or ids != tuple(sorted(set(ids))):
            raise ValueError("INVALID_NATIVE_CLOSE_IDENTITIES")
        result = NativeCloseResult(
            base.exposure_id,
            base.close_serial,
            base.event_clock,
            base.accepted,
            base.refused,
            base.graph_hash,
            doc["form_reason"],
            ids,
        )
        if encode_native_close(result) != data:
            raise ValueError("NONCANONICAL_NATIVE_CLOSE_RECORD")
        return result
    except (KeyError, TypeError, IndexError) as exc:
        raise ValueError("INVALID_NATIVE_CLOSE_RECORD") from exc
