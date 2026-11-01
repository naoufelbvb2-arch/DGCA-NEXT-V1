"""Root-authenticated MAINTAIN -> GROW -> guarded FORM/MERGE/SPLIT END."""

import hashlib
import sqlite3
from dataclasses import asdict, dataclass, replace
from types import MappingProxyType

from dgca_next.graph.assembly_support import inspect_structure
from dgca_next.graph.native_assembly import _assembly_record
from dgca_next.graph.native_lifecycle import (
    StructuralEvaluation,
    StructuralScore,
    guard_deferred,
    parameter,
    plan_maintain_grow,
)
from dgca_next.graph.native_mutation import _mutation_record
from dgca_next.graph.network import SparseNetwork
from dgca_next.graph.policy import q6
from dgca_next.learning.native_form import (
    NativeCloseResult,
    _form_at_end,
    decode_native_close,
    encode_native_close,
)
from dgca_next.learning.settlement import CloseResult
from dgca_next.persistence.binary_records import decode_record, encode_record
from dgca_next.persistence.form_inspection import _project_candidates, _qualified_events
from dgca_next.persistence.graph_codec import encode_production_graph
from dgca_next.persistence.native_codec import (
    _base_graph,
    _encode_native_shadow,
    decode_native_graph,
    encode_native_graph,
)


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


@dataclass(frozen=True, slots=True)
class NativeLifecycleCloseResult(NativeCloseResult):
    mutation_ordinals: tuple[int, ...]
    evaluations: tuple[StructuralEvaluation, ...]
    # Event, Assembly, emitted committed-before count, current size, covered.
    coverage: tuple[tuple[int, int, int, int, bool], ...]


def _native_end(
    connection: sqlite3.Connection, graph: SparseNetwork, result: CloseResult, *, replay: bool
) -> tuple[SparseNetwork, CloseResult]:
    if not graph._state.native_assemblies:
        return _form_at_end(connection, graph, result, replay=replay)
    # Only physical state is required to be valid before lifecycle repair.
    # No public codec accepts this potentially temporary non-KEEP shadow.
    physical = _base_graph(graph)
    physical.validate_graph()
    structure = inspect_structure(physical)
    supports: dict[int, dict[int, float]] = {}
    for pair in structure.pairs:
        if pair.forward.reason == pair.reverse.reason == "QUALIFIED":
            supports.setdefault(pair.first, {})[pair.second] = pair.support
            supports.setdefault(pair.second, {})[pair.first] = pair.support
    row = connection.execute(
        "SELECT status,next_order FROM p01_roots WHERE exposure_id=?", (result.exposure_id,)
    ).fetchone()
    if row is None or row[0] != ("COMPLETED" if replay else "OPEN"):
        raise ValueError("UNVERIFIED_NATIVE_LIFECYCLE_ROOT")
    events = _qualified_events(
        connection,
        result.exposure_id,
        structure.committed,
        row[1],
        graph_decoder=decode_native_graph,
        replay=replay,
    )
    event = events[-1]  # Close authority, not additional coactivity/evidence.
    edits, evaluations = plan_maintain_grow(
        {r.assembly_id: r.member_cell_ids for r in graph.native_assemblies() if r.status == "LIVE"},
        supports,
        graph._state.member_assemblies,
        frozenset(structure.committed),
    )
    physical_hash = _sha(encode_production_graph(physical))
    start_ordinal = len(graph._state.native_mutation_log)
    for edit in edits:
        before = graph._state.native_assemblies[edit.assembly_id]
        if before.member_cell_ids != edit.before or before.status != "LIVE":
            raise ValueError("NATIVE_PLAN_PRESTATE_MISMATCH")
        status = "ARCHIVED" if edit.stage == "ARCHIVE" else "LIVE"
        record = _assembly_record(
            before.assembly_id,
            before.region,
            edit.after,
            before.structural_generation + 1,
            before.birth_close_serial,
            result.close_serial,
            before.last_merge_split_close_serial,
            status,
        )
        before_hash = _sha(_encode_native_shadow(graph))
        registry = {**graph._state.native_assemblies, record.assembly_id: record}
        inverse: dict[int, frozenset[int]] = {}
        for assembly in registry.values():
            if assembly.status == "LIVE":
                for cell in assembly.member_cell_ids:
                    inverse[cell] = inverse.get(cell, frozenset()) | {assembly.assembly_id}
        after = SparseNetwork()
        after._state = replace(
            graph._state,
            native_assemblies=MappingProxyType(registry),
            member_assemblies=MappingProxyType(inverse),
            cells=MappingProxyType(
                {
                    i: replace(c, assembly_ids=inverse.get(i, frozenset()))
                    for i, c in graph._state.cells.items()
                }
            ),
        )
        # This hash deliberately excludes this record itself (no circular hash).
        after_hash = _sha(_encode_native_shadow(after))
        removed = (
            tuple(i for i in edit.before if i not in edit.after)
            if status == "LIVE"
            else edit.before
        )
        added = tuple(i for i in edit.after if i not in edit.before)
        mutation = _mutation_record(
            schema_version=1,
            ordinal=len(graph._state.native_mutation_log),
            assembly_id=record.assembly_id,
            exposure_id=result.exposure_id,
            event_id=event.event_id,
            event_order=event.event_order,
            completed_close_serial=result.close_serial,
            stage=edit.stage,
            before_members=edit.before,
            after_members=edit.after,
            before_generation=before.structural_generation,
            after_generation=record.structural_generation,
            before_status=before.status,
            after_status=record.status,
            observation_digest=event.observation_digest,
            event_pre_w_hash=event.pre_w_hash,
            event_pre_h_hash=event.pre_h_hash,
            witness_graph_hash=physical_hash,
            before_w_hash=before_hash,
            after_w_hash=after_hash,
            scores=edit.evaluation.scores,
            rank_support=edit.evaluation.rank_support,
            inverse_removed=removed,
            inverse_added=added,
        )
        after._state = replace(
            after._state, native_mutation_log=(*graph._state.native_mutation_log, mutation)
        )
        graph = after
    graph.validate_graph()
    live = tuple(r for r in graph.native_assemblies() if r.status == "LIVE")
    guard_deferred(tuple(r.member_cell_ids for r in live))
    coverage = []
    filtered = []
    for original in events:
        witnesses = {w.cell_id: w for w in original.witnesses}
        covered: set[int] = set()
        for assembly in live:
            count = 0
            for cell in assembly.member_cell_ids:
                witness = witnesses[cell]
                if (
                    witness.committed_before
                    and witness.final_activity is not None
                    and witness.theta_emit is not None
                    and q6(witness.final_activity) >= q6(witness.theta_emit)
                ):
                    count += 1
            qualifies = q6(count / len(assembly.member_cell_ids)) >= q6(parameter("rho_core"))
            coverage.append(
                (
                    original.event_id,
                    assembly.assembly_id,
                    count,
                    len(assembly.member_cell_ids),
                    qualifies,
                )
            )
            if qualifies:
                covered.update(assembly.member_cell_ids)
        filtered.append(
            replace(
                original,
                witnesses=tuple(
                    replace(w, reason="COVERED_BY_LIVE_ASSEMBLY") if w.cell_id in covered else w
                    for w in original.witnesses
                ),
            )
        )
    structure = replace(
        structure,
        triangles=tuple(
            replace(
                t,
                reasons=(
                    *t.reasons,
                    *(
                        f"MEMBERSHIP_CAPACITY:{i}"
                        for i in t.members
                        if len(graph.member_assemblies(i)) >= int(parameter("M_max"))
                    ),
                ),
                cells=tuple(
                    replace(v, memberships=len(graph.member_assemblies(v.cell_id))) for v in t.cells
                ),
            )
            for t in structure.triangles
        ),
    )
    if any(c.selected for c in _project_candidates(structure, tuple(filtered))):
        raise ValueError("I4_FIRST_FORM_LAB_SCOPE_EXCEEDED")
    if encode_production_graph(_base_graph(graph)) != encode_production_graph(physical):
        raise ValueError("NATIVE_LIFECYCLE_CHANGED_PHYSICAL_KNOWLEDGE")
    return graph, NativeLifecycleCloseResult(
        result.exposure_id,
        result.close_serial,
        result.event_clock,
        result.accepted,
        result.refused,
        _sha(encode_native_graph(graph)),
        "NO_QUALIFIED_FORM_EVENT",
        (),
        tuple(range(start_ordinal, len(graph._state.native_mutation_log))),
        tuple(evaluations),
        tuple(coverage),
    )


def encode_lifecycle_close(close: CloseResult) -> bytes:
    result = close
    if type(result) is not NativeLifecycleCloseResult:
        return encode_native_close(result)
    base = NativeCloseResult(
        result.exposure_id,
        result.close_serial,
        result.event_clock,
        result.accepted,
        result.refused,
        result.graph_hash,
        result.form_reason,
        result.formed_ids,
    )
    evaluations = []
    for value in result.evaluations:
        row = asdict(value)
        row["members"] = list(value.members)
        row["scores"] = [asdict(s) for s in value.scores]
        evaluations.append(row)
    return encode_record(
        0x43,
        5,
        {
            "lifecycle_version": 1,
            "base_native": encode_native_close(base),
            "mutation_ordinals": list(result.mutation_ordinals),
            "evaluations": evaluations,
            "coverage": [list(v) for v in result.coverage],
        },
    )


def decode_lifecycle_close(data: bytes) -> NativeCloseResult:
    doc = decode_record(data, 0x43, 5)
    if type(doc) is not dict or "lifecycle_version" not in doc:
        return decode_native_close(data)
    try:
        if (
            set(doc)
            != {"lifecycle_version", "base_native", "mutation_ordinals", "evaluations", "coverage"}
            or type(doc["lifecycle_version"]) is not int
            or doc["lifecycle_version"] != 1
        ):
            raise ValueError("INVALID_NATIVE_LIFECYCLE_CLOSE")
        base = decode_native_close(doc["base_native"])
        evaluations = tuple(
            StructuralEvaluation(
                **(
                    r
                    | {
                        "members": tuple(r["members"]),
                        "scores": tuple(StructuralScore(**s) for s in r["scores"]),
                    }
                )
            )
            for r in doc["evaluations"]
        )
        result = NativeLifecycleCloseResult(
            base.exposure_id,
            base.close_serial,
            base.event_clock,
            base.accepted,
            base.refused,
            base.graph_hash,
            base.form_reason,
            base.formed_ids,
            tuple(doc["mutation_ordinals"]),
            evaluations,
            tuple(tuple(v) for v in doc["coverage"]),
        )
        if encode_lifecycle_close(result) != data:
            raise ValueError("NONCANONICAL_NATIVE_LIFECYCLE_CLOSE")
        return result
    except (TypeError, KeyError, IndexError) as exc:
        raise ValueError("INVALID_NATIVE_LIFECYCLE_CLOSE") from exc
