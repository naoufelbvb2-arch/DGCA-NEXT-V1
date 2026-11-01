"""Experimental multi-FORM/MG; eligible unproven MERGE/SPLIT fail closed."""

import hashlib
import sqlite3
from dataclasses import asdict, dataclass, replace
from itertools import combinations
from types import MappingProxyType
from typing import Any

from dgca_next.contracts import Region
from dgca_next.graph.assembly_support import inspect_structure
from dgca_next.graph.merge_split_analysis import analyze_merge, analyze_split
from dgca_next.graph.native_assembly import _assembly_record, _form_record, _next_native_id
from dgca_next.graph.native_lifecycle import StructuralEdit, parameter, plan_maintain_grow
from dgca_next.graph.native_mutation import _mutation_record
from dgca_next.graph.network import SparseNetwork
from dgca_next.graph.policy import q6
from dgca_next.learning.completed_event_clock import _verified_completed_prefix
from dgca_next.learning.native_form import NativeCloseResult
from dgca_next.learning.native_lifecycle import (
    NativeLifecycleCloseResult,
    decode_lifecycle_close,
    encode_lifecycle_close,
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


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _plain(value: Any) -> Any:
    if type(value) in (tuple, list):
        return [_plain(v) for v in value]
    if type(value) is dict:
        return {k: _plain(v) for k, v in value.items()}
    return value


@dataclass(frozen=True, slots=True)
class MultiAssemblyCloseResult(NativeLifecycleCloseResult):
    operator_checks: tuple[bytes, ...]
    close_version: int = 2


def _parent(close: MultiAssemblyCloseResult) -> NativeLifecycleCloseResult:
    return NativeLifecycleCloseResult(
        close.exposure_id,
        close.close_serial,
        close.event_clock,
        close.accepted,
        close.refused,
        close.graph_hash,
        close.form_reason,
        close.formed_ids,
        close.mutation_ordinals,
        close.evaluations,
        close.coverage,
    )


def decode_operator_check(data: bytes) -> dict[str, Any]:
    doc = decode_record(data, 0x4F, 1)
    if (
        type(doc) is not dict
        or set(doc) != {"operator", "subjects", "cooldown", "numbers", "eligible"}
        or doc["operator"] not in ("MERGE", "SPLIT")
        or type(doc["eligible"]) is not bool
        or encode_record(0x4F, 1, doc) != data
    ):
        raise ValueError("INVALID_NATIVE_OPERATOR_CHECK")
    return doc


def encode_multi_close(close: CloseResult) -> bytes:
    if type(close) is not MultiAssemblyCloseResult:
        return encode_lifecycle_close(close)
    if type(close.close_version) is not int or close.close_version not in (1, 2):
        raise ValueError("UNSUPPORTED_NATIVE_MULTI_CLOSE")
    for record in close.operator_checks:
        decode_operator_check(record)
    return encode_record(
        0x43,
        5,
        {
            "r04_multi_version": close.close_version,
            "base_lifecycle": encode_lifecycle_close(_parent(close)),
            "operator_checks": list(close.operator_checks),
        },
    )


def decode_multi_close(data: bytes) -> NativeCloseResult:
    doc = decode_record(data, 0x43, 5)
    if type(doc) is not dict or "r04_multi_version" not in doc:
        return decode_lifecycle_close(data)
    try:
        if (
            set(doc) != {"r04_multi_version", "base_lifecycle", "operator_checks"}
            or type(doc["r04_multi_version"]) is not int
            or doc["r04_multi_version"] not in (1, 2)
        ):
            raise ValueError("UNSUPPORTED_NATIVE_MULTI_CLOSE")
        base = decode_lifecycle_close(doc["base_lifecycle"])
        if type(base) is not NativeLifecycleCloseResult:
            raise ValueError("INVALID_NATIVE_MULTI_PARENT")
        checks = tuple(doc["operator_checks"])
        result = MultiAssemblyCloseResult(
            base.exposure_id,
            base.close_serial,
            base.event_clock,
            base.accepted,
            base.refused,
            base.graph_hash,
            base.form_reason,
            base.formed_ids,
            base.mutation_ordinals,
            base.evaluations,
            base.coverage,
            checks,
            doc["r04_multi_version"],
        )
        if encode_multi_close(result) != data:
            raise ValueError("NONCANONICAL_NATIVE_MULTI_CLOSE")
        return result
    except (TypeError, KeyError, IndexError) as exc:
        raise ValueError("INVALID_NATIVE_MULTI_CLOSE") from exc


class UnprovenNativeOperator(ValueError):
    """Real pending eligibility evidence, never a committed mutation result."""

    def __init__(self, operator: str, close: MultiAssemblyCloseResult, shadow: bytes):
        super().__init__(f"I4_R04_{operator}_WRITER_NOT_PROVEN")
        self.operator = operator
        self.provisional_close = close
        self.provisional_W = shadow


def _apply_edits(
    graph: SparseNetwork,
    edits: tuple[StructuralEdit, ...],
    result: CloseResult,
    event: Any,
    physical_hash: str,
) -> SparseNetwork:
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
        change = _mutation_record(
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
            after_status=status,
            observation_digest=event.observation_digest,
            event_pre_w_hash=event.pre_w_hash,
            event_pre_h_hash=event.pre_h_hash,
            witness_graph_hash=physical_hash,
            before_w_hash=before_hash,
            after_w_hash=_sha(_encode_native_shadow(after)),
            scores=edit.evaluation.scores,
            rank_support=edit.evaluation.rank_support,
            inverse_removed=edit.before
            if status == "ARCHIVED"
            else tuple(i for i in edit.before if i not in edit.after),
            inverse_added=tuple(i for i in edit.after if i not in edit.before),
        )
        after._state = replace(
            after._state, native_mutation_log=(*graph._state.native_mutation_log, change)
        )
        graph = after
    return graph


def _multi_end(
    connection: sqlite3.Connection,
    graph: SparseNetwork,
    result: CloseResult,
    *,
    replay: bool,
    probe: bool = False,
    close_version: int = 2,
) -> tuple[SparseNetwork, MultiAssemblyCloseResult]:
    physical = _base_graph(graph)
    structure = inspect_structure(physical)
    prefix = _verified_completed_prefix(connection, result, decode_multi_close, replay=replay)
    root = connection.execute(
        "SELECT next_order FROM p01_roots WHERE exposure_id=?", (result.exposure_id,)
    ).fetchone()
    assert root is not None
    events = _qualified_events(
        connection,
        result.exposure_id,
        structure.committed,
        root[0],
        graph_decoder=decode_native_graph,
        replay=replay,
    )
    supports: dict[int, dict[int, float]] = {}
    for pair in structure.pairs:
        if pair.forward.reason == pair.reverse.reason == "QUALIFIED":
            supports.setdefault(pair.first, {})[pair.second] = pair.support
            supports.setdefault(pair.second, {})[pair.first] = pair.support
    edits, evaluations = plan_maintain_grow(
        {r.assembly_id: r.member_cell_ids for r in graph.native_assemblies() if r.status == "LIVE"},
        supports,
        graph._state.member_assemblies,
        frozenset(structure.committed),
    )
    start = len(graph._state.native_mutation_log)
    graph = _apply_edits(graph, edits, result, events[-1], _sha(encode_production_graph(physical)))
    graph.validate_graph()
    live_before_form = tuple(a for a in graph.native_assemblies() if a.status == "LIVE")
    coverage = []
    filtered = []
    for original in events:
        witnesses = {w.cell_id: w for w in original.witnesses}
        covered: set[int] = set()
        for assembly in live_before_form:
            count = 0
            for cell in assembly.member_cell_ids:
                w = witnesses[cell]
                if (
                    w.committed_before
                    and w.final_activity is not None
                    and w.theta_emit is not None
                    and q6(w.final_activity) >= q6(w.theta_emit)
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
    seeds = tuple(c for c in _project_candidates(structure, tuple(filtered)) if c.selected)
    # Batch authority is frozen after MG and before any new birth, never
    # recomputed from a partially inserted newborn or a caller diagnostic.
    authorizing_hash = _sha(encode_native_graph(graph))
    formed = []
    for seed in seeds:
        event = next(e for e in events if e.event_id == seed.event_id)
        witnesses = {w.cell_id: w for w in event.witnesses}
        sampled = []
        for cell in seed.triangle.members:
            w = witnesses[cell]
            if (
                not w.qualified
                or w.committed_event is None
                or w.final_activity is None
                or w.theta_emit is None
            ):
                raise ValueError("UNVERIFIED_NATIVE_FORM_WITNESS")
            sampled.append(
                (cell, w.direct_x_fixed, w.committed_event, w.final_activity, w.theta_emit)
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
        birth = _form_record(
            identity,
            result.exposure_id,
            event.event_id,
            event.event_order,
            result.close_serial,
            seed.triangle.members,
            event.observation_digest,
            event.pre_w_hash,
            event.pre_h_hash,
            authorizing_hash,
            tuple(sampled),
        )
        cells, reverse = dict(graph._state.cells), dict(graph._state.member_assemblies)
        for cell in assembly.member_cell_ids:
            cells[cell] = replace(cells[cell], assembly_ids=cells[cell].assembly_ids | {identity})
            reverse[cell] = reverse.get(cell, frozenset()) | {identity}
        after = SparseNetwork()
        after._state = replace(
            graph._state,
            cells=MappingProxyType(cells),
            member_assemblies=MappingProxyType(reverse),
            native_assemblies=MappingProxyType(
                {**graph._state.native_assemblies, identity: assembly}
            ),
            assembly_high_watermarks=MappingProxyType({Region.LANGUAGE: identity}),
            native_form_log=(*graph._state.native_form_log, birth),
        )
        graph = after
        formed.append(identity)
    graph.validate_graph()
    live = tuple(a for a in graph.native_assemblies() if a.status == "LIVE")
    counts = {c.cell_id: len(c.assembly_ids) for c in graph.stored_cells()}
    checks = []
    positive = None
    for a, b in combinations(live, 2):
        timers = (
            prefix.cooldown(a.assembly_id, a.last_merge_split_close_serial),
            prefix.cooldown(b.assembly_id, b.last_merge_split_close_serial),
        )
        numbers = analyze_merge(
            a.member_cell_ids, b.member_cell_ids, supports, membership_counts=counts
        )
        eligible = numbers.mathematical_eligible and all(t.eligible for t in timers)
        checks.append(
            encode_record(
                0x4F,
                1,
                _plain(
                    dict(
                        operator="MERGE",
                        subjects=[
                            (a.assembly_id, a.structural_generation),
                            (b.assembly_id, b.structural_generation),
                        ],
                        cooldown=[asdict(t) for t in timers],
                        numbers=asdict(numbers),
                        eligible=eligible,
                    )
                ),
            )
        )
        if eligible and positive is None:
            positive = "MERGE"
    # With no implemented merge writer an eligible MERGE already stops END;
    # subsequent split calculations are provisional diagnostics, never a skip.
    for a in live:
        timer = prefix.cooldown(a.assembly_id, a.last_merge_split_close_serial)
        numbers_split = analyze_split(a.member_cell_ids, supports, membership_counts=counts)
        eligible = numbers_split.mathematical_eligible and timer.eligible
        checks.append(
            encode_record(
                0x4F,
                1,
                _plain(
                    dict(
                        operator="SPLIT",
                        subjects=[(a.assembly_id, a.structural_generation)],
                        cooldown=[asdict(timer)],
                        numbers=asdict(numbers_split),
                        eligible=eligible,
                    )
                ),
            )
        )
        if eligible and positive is None:
            positive = "SPLIT"
    if encode_production_graph(_base_graph(graph)) != encode_production_graph(physical):
        raise ValueError("NATIVE_OPERATORS_CHANGED_PHYSICAL_KNOWLEDGE")
    encoded = encode_native_graph(graph)
    closed = MultiAssemblyCloseResult(
        result.exposure_id,
        result.close_serial,
        result.event_clock,
        result.accepted,
        result.refused,
        _sha(encoded),
        "FORMED"
        if formed
        else (
            "NO_RECIPROCAL_TRIANGLE"
            if close_version >= 2 and not any(t.eligible for t in structure.triangles)
            else "NO_QUALIFIED_FORM_EVENT"
        ),
        tuple(formed),
        tuple(range(start, len(graph._state.native_mutation_log))),
        evaluations,
        tuple(coverage),
        tuple(checks),
        close_version,
    )
    if positive is not None and not probe:
        raise UnprovenNativeOperator(positive, closed, encoded)
    return graph, closed
