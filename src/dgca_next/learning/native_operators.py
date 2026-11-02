"""Conditionally authorized real native operators; RootStore owns publication."""

import hashlib
from dataclasses import asdict, dataclass, replace
from itertools import combinations
from types import MappingProxyType
from typing import Any

from dgca_next.contracts import Region
from dgca_next.graph.merge_split_analysis import analyze_merge, analyze_split
from dgca_next.graph.native_assembly import _assembly_record, _next_native_id
from dgca_next.graph.native_operator import assembly_row, read_operator
from dgca_next.graph.network import SparseNetwork
from dgca_next.learning.completed_event_clock import VerifiedCompletedPrefix
from dgca_next.learning.native_form import NativeCloseResult
from dgca_next.learning.native_multi import (
    MultiAssemblyCloseResult,
    _plain,
    decode_multi_close,
    encode_multi_close,
)
from dgca_next.learning.settlement import CloseResult
from dgca_next.persistence.binary_records import decode_record, encode_record
from dgca_next.persistence.native_codec import _encode_native_shadow


@dataclass(frozen=True, slots=True)
class OperatorCloseResult(MultiAssemblyCloseResult):
    operator_ordinals: tuple[int, ...] = ()


def operator_close(
    base: MultiAssemblyCloseResult, ordinals: tuple[int, ...]
) -> OperatorCloseResult:
    return OperatorCloseResult(
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
        base.operator_checks,
        base.close_version,
        ordinals,
    )


def encode_operator_close(close: CloseResult) -> bytes:
    if type(close) is not OperatorCloseResult:
        return encode_multi_close(close)
    base = MultiAssemblyCloseResult(
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
        close.operator_checks,
        close.close_version,
    )
    if base.close_version != 2:
        raise ValueError("INVALID_OPERATOR_CLOSE_PARENT")
    return encode_record(
        0x43,
        5,
        dict(
            r04_operator_close_version=1,
            base_multi=encode_multi_close(base),
            operator_ordinals=list(close.operator_ordinals),
        ),
    )


def decode_operator_close(data: bytes) -> NativeCloseResult:
    doc = decode_record(data, 0x43, 5)
    if type(doc) is not dict or "r04_operator_close_version" not in doc:
        return decode_multi_close(data)
    try:
        if (
            set(doc) != {"r04_operator_close_version", "base_multi", "operator_ordinals"}
            or type(doc["r04_operator_close_version"]) is not int
            or doc["r04_operator_close_version"] != 1
        ):
            raise ValueError("INVALID_OPERATOR_CLOSE")
        base = decode_multi_close(doc["base_multi"])
        if type(base) is not MultiAssemblyCloseResult:
            raise ValueError("INVALID_OPERATOR_CLOSE_PARENT")
        result = operator_close(base, tuple(doc["operator_ordinals"]))
        if (
            any(type(i) is not int or i < 0 for i in result.operator_ordinals)
            or result.operator_ordinals != tuple(sorted(set(result.operator_ordinals)))
            or encode_operator_close(result) != data
        ):
            raise ValueError("NONCANONICAL_OPERATOR_CLOSE")
        return result
    except (TypeError, KeyError, IndexError) as exc:
        raise ValueError("INVALID_OPERATOR_CLOSE") from exc


def _apply(
    graph: SparseNetwork,
    before: tuple[Any, ...],
    after: tuple[Any, ...],
    result: CloseResult,
    event: Any,
    physical_hash: str,
    check: bytes,
) -> SparseNetwork:
    before_hash = hashlib.sha256(_encode_native_shadow(graph)).hexdigest()
    registry = {**graph._state.native_assemblies, **{r.assembly_id: r for r in after}}
    inverse: dict[int, frozenset[int]] = {}
    for r in registry.values():
        if r.status == "LIVE":
            for cell in r.member_cell_ids:
                inverse[cell] = inverse.get(cell, frozenset()) | {r.assembly_id}
    shadow = SparseNetwork()
    shadow._state = replace(
        graph._state,
        native_assemblies=MappingProxyType(registry),
        cells=MappingProxyType(
            {
                i: replace(c, assembly_ids=inverse.get(i, frozenset()))
                for i, c in graph._state.cells.items()
            }
        ),
        member_assemblies=MappingProxyType(inverse),
        assembly_high_watermarks=MappingProxyType({Region.LANGUAGE: len(registry) - 1}),
    )
    proof = decode_record(check, 0x4F, 1)
    assert isinstance(proof, dict)
    operator = proof["operator"]
    raw = encode_record(
        0x4D,
        1,
        dict(
            version=1,
            ordinal=len(graph._state.native_operator_log),
            operator=operator,
            exposure_id=result.exposure_id,
            event_id=event.event_id,
            event_order=event.event_order,
            close_serial=result.close_serial,
            event_clock=result.event_clock,
            observation_digest=event.observation_digest,
            event_pre_w_hash=event.pre_w_hash,
            event_pre_h_hash=event.pre_h_hash,
            physical_w_hash=physical_hash,
            before_w_hash=before_hash,
            after_w_hash=hashlib.sha256(_encode_native_shadow(shadow)).hexdigest(),
            before=[assembly_row(r) for r in before],
            after=[assembly_row(r) for r in after],
            check=check,
        ),
    )
    read_operator(raw)
    shadow._state = replace(
        shadow._state, native_operator_log=(*graph._state.native_operator_log, raw)
    )
    shadow.validate_graph()
    return shadow


def settle_native_operators(
    graph: SparseNetwork,
    result: CloseResult,
    prefix: VerifiedCompletedPrefix,
    event: Any,
    supports: dict[int, dict[int, float]],
    physical_hash: str,
) -> tuple[SparseNetwork, tuple[bytes, ...], tuple[int, ...]]:
    start = len(graph._state.native_operator_log)
    initial_ids = tuple(a.assembly_id for a in graph.native_assemblies() if a.status == "LIVE")
    initial_pairs = tuple(combinations(initial_ids, 2))
    available = set(initial_pairs)
    recomputed = False
    touched: set[int] = set()
    checks = []
    for first, second in initial_pairs:
        if (first, second) not in available:
            continue
        a, b = graph._state.native_assemblies[first], graph._state.native_assemblies[second]
        if a.status != "LIVE" or b.status != "LIVE":
            continue
        timers = tuple(
            prefix.cooldown(
                r.assembly_id, r.last_merge_split_close_serial, edited_this_end=frozenset(touched)
            )
            for r in (a, b)
        )
        counts = {i: len(v) for i, v in graph._state.member_assemblies.items()}
        numbers = analyze_merge(
            a.member_cell_ids, b.member_cell_ids, supports, membership_counts=counts
        )
        eligible = numbers.mathematical_eligible and all(t.eligible for t in timers)
        check = encode_record(
            0x4F,
            1,
            _plain(
                dict(
                    operator="MERGE",
                    subjects=[(r.assembly_id, r.structural_generation) for r in (a, b)],
                    cooldown=[asdict(t) for t in timers],
                    numbers=asdict(numbers),
                    eligible=eligible,
                )
            ),
        )
        checks.append(check)
        if eligible:
            survivor = _assembly_record(
                first,
                Region.LANGUAGE,
                numbers.union,
                a.structural_generation + 1,
                a.birth_close_serial,
                result.close_serial,
                result.close_serial,
                "LIVE",
            )
            archived = _assembly_record(
                second,
                Region.LANGUAGE,
                b.member_cell_ids,
                b.structural_generation,
                b.birth_close_serial,
                result.close_serial,
                result.close_serial,
                "ARCHIVED",
            )
            graph = _apply(graph, (a, b), (survivor, archived), result, event, physical_hash, check)
            touched.update((first, second))
            if not recomputed:
                available = set(
                    combinations(
                        tuple(
                            r.assembly_id for r in graph.native_assemblies() if r.status == "LIVE"
                        ),
                        2,
                    )
                )
                recomputed = True
    # Fixed surviving-original list; no derived child is revisited in this END.
    originals = tuple(r.assembly_id for r in graph.native_assemblies() if r.status == "LIVE")
    for identity in originals:
        a = graph._state.native_assemblies[identity]
        timer = prefix.cooldown(
            identity, a.last_merge_split_close_serial, edited_this_end=frozenset(touched)
        )
        counts = {i: len(v) for i, v in graph._state.member_assemblies.items()}
        split = analyze_split(a.member_cell_ids, supports, membership_counts=counts)
        eligible = split.mathematical_eligible and timer.eligible
        check = encode_record(
            0x4F,
            1,
            _plain(
                dict(
                    operator="SPLIT",
                    subjects=[(identity, a.structural_generation)],
                    cooldown=[asdict(timer)],
                    numbers=asdict(split),
                    eligible=eligible,
                )
            ),
        )
        checks.append(check)
        if eligible:
            assert split.best is not None
            child_id = _next_native_id(
                graph._state.assembly_high_watermarks[Region.LANGUAGE],
                graph._state.native_assemblies,
            )
            parent = _assembly_record(
                identity,
                Region.LANGUAGE,
                split.best.left,
                a.structural_generation + 1,
                a.birth_close_serial,
                result.close_serial,
                result.close_serial,
                "LIVE",
            )
            child = _assembly_record(
                child_id,
                Region.LANGUAGE,
                split.best.right,
                1,
                result.close_serial,
                result.close_serial,
                result.close_serial,
                "LIVE",
            )
            graph = _apply(graph, (a,), (parent, child), result, event, physical_hash, check)
            touched.update((identity, child_id))
    return graph, tuple(checks), tuple(range(start, len(graph._state.native_operator_log)))
