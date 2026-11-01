"""Versioned structural lineage; bare records never authorize RootStore END."""

from dataclasses import asdict
from typing import TYPE_CHECKING, Any

from dgca_next.contracts import Region, SynapseScope
from dgca_next.graph.cell import nonnegative_integer
from dgca_next.graph.native_lifecycle import parameter, passes, score
from dgca_next.graph.native_mutation import _mutation_record
from dgca_next.graph.policy import q6
from dgca_next.graph.synapse import SynapseState, quality
from dgca_next.persistence.binary_records import decode_record, encode_record

if TYPE_CHECKING:
    from dgca_next.graph.native_assembly import NativeAssemblyRecord
    from dgca_next.graph.network import _State


def assembly_row(record: NativeAssemblyRecord) -> list[Any]:
    return [
        record.assembly_id,
        record.region.value,
        list(record.member_cell_ids),
        record.structural_generation,
        record.birth_close_serial,
        record.last_mutation_close_serial,
        record.last_merge_split_close_serial,
        record.status,
    ]


def read_assembly_row(row: Any) -> NativeAssemblyRecord:
    from dgca_next.graph.native_assembly import _assembly_record

    if type(row) is not list or len(row) != 8:
        raise ValueError("INVALID_OPERATOR_ASSEMBLY_ROW")
    return _assembly_record(row[0], Region(row[1]), tuple(row[2]), *row[3:])


def read_operator(data: bytes) -> dict[str, Any]:
    """Canonical representation/lineage checks; history authenticates physics."""
    try:
        doc = decode_record(data, 0x4D, 1)
        names = {
            "version",
            "ordinal",
            "operator",
            "exposure_id",
            "event_id",
            "event_order",
            "close_serial",
            "event_clock",
            "observation_digest",
            "event_pre_w_hash",
            "event_pre_h_hash",
            "physical_w_hash",
            "before_w_hash",
            "after_w_hash",
            "before",
            "after",
            "check",
        }
        if (
            type(doc) is not dict
            or set(doc) != names
            or type(doc["version"]) is not int
            or doc["version"] != 1
        ):
            raise ValueError("INVALID_NATIVE_OPERATOR_RECORD")
        for name in (
            "ordinal",
            "exposure_id",
            "event_id",
            "event_order",
            "close_serial",
            "event_clock",
        ):
            nonnegative_integer(doc[name], name)
        if min(doc["close_serial"], doc["event_clock"]) < 1:
            raise ValueError("INVALID_OPERATOR_CLOCK")
        for name in (
            "observation_digest",
            "event_pre_w_hash",
            "event_pre_h_hash",
            "physical_w_hash",
            "before_w_hash",
            "after_w_hash",
        ):
            value = doc[name]
            if (
                type(value) is not str
                or len(value) != 64
                or any(c not in "0123456789abcdef" for c in value)
            ):
                raise ValueError("INVALID_OPERATOR_HASH")
        before = tuple(read_assembly_row(r) for r in doc["before"])
        after = tuple(read_assembly_row(r) for r in doc["after"])
        if len(after) != 2 or any(r.status != "LIVE" for r in before):
            raise ValueError("INVALID_OPERATOR_SUBJECTS")
        check = decode_record(doc["check"], 0x4F, 1)
        if (
            type(check) is not dict
            or set(check) != {"operator", "subjects", "cooldown", "numbers", "eligible"}
            or check["operator"] != doc["operator"]
            or check["eligible"] is not True
            or check["subjects"] != [[r.assembly_id, r.structural_generation] for r in before]
            or len(check["cooldown"]) != len(before)
        ):
            raise ValueError("INVALID_OPERATOR_ELIGIBILITY_PROOF")
        close = doc["close_serial"]
        for r, timer in zip(before, check["cooldown"], strict=True):
            if (
                timer["assembly_id"] != r.assembly_id
                or timer["last_close_reference"] != r.last_merge_split_close_serial
                or close < r.last_mutation_close_serial
                or r.last_merge_split_close_serial == close
            ):
                raise ValueError("INVALID_OPERATOR_COOLDOWN_SOURCE")
            if r.last_merge_split_close_serial is None:
                valid = timer["status"] == "NEVER_EDITED" and timer["age_completed_events"] is None
            else:
                age = timer["age_completed_events"]
                valid = (
                    timer["status"] == "COOLDOWN_ELAPSED"
                    and type(age) is int
                    and int(parameter("T_c")) <= age <= doc["event_clock"]
                )
            if not valid:
                raise ValueError("INVALID_OPERATOR_COOLDOWN_SOURCE")
        first, second = after
        original = before[0]
        if (
            first.assembly_id != original.assembly_id
            or first.status != "LIVE"
            or first.birth_close_serial != original.birth_close_serial
            or first.structural_generation != original.structural_generation + 1
            or any(
                r.last_mutation_close_serial != close or r.last_merge_split_close_serial != close
                for r in after
            )
        ):
            raise ValueError("INVALID_OPERATOR_SURVIVOR")
        if doc["operator"] == "MERGE":
            if len(before) != 2 or before[0].assembly_id >= before[1].assembly_id:
                raise ValueError("INVALID_MERGE_IDENTITIES")
            higher = before[1]
            if (
                first.member_cell_ids
                != tuple(sorted(set(original.member_cell_ids) | set(higher.member_cell_ids)))
                or second.assembly_id != higher.assembly_id
                or second.status != "ARCHIVED"
                or second.member_cell_ids != higher.member_cell_ids
                or second.structural_generation != higher.structural_generation
                or second.birth_close_serial != higher.birth_close_serial
                or check["numbers"]["reasons"]
            ):
                raise ValueError("INVALID_MERGE_LINEAGE")
        elif doc["operator"] == "SPLIT":
            best = check["numbers"]["best"]
            if (
                len(before) != 1
                or len(original.member_cell_ids) < int(parameter("N_min"))
                or second.assembly_id <= original.assembly_id
                or second.status != "LIVE"
                or second.structural_generation != 1
                or second.birth_close_serial != close
                or set(first.member_cell_ids) & set(second.member_cell_ids)
                or tuple(sorted((*first.member_cell_ids, *second.member_cell_ids)))
                != original.member_cell_ids
                or first.member_cell_ids[0] != original.member_cell_ids[0]
                or best is None
                or check["numbers"]["reasons"]
                or [list(first.member_cell_ids), list(second.member_cell_ids)]
                != [best["left"], best["right"]]
            ):
                raise ValueError("INVALID_DERIVED_SPLIT_LINEAGE")
        else:
            raise ValueError("UNSUPPORTED_NATIVE_OPERATOR")
        if encode_record(0x4D, 1, doc) != data:
            raise ValueError("NONCANONICAL_NATIVE_OPERATOR")
        return doc
    except (TypeError, KeyError, IndexError) as exc:
        raise ValueError("INVALID_NATIVE_OPERATOR_RECORD") from exc


def validate_operator_state(state: _State) -> None:
    """Replay real FORM, v1 MG and derived/multi-object lineage together."""
    from dgca_next.graph.native_assembly import (
        NativeFormRecord,
        _assembly_record,
        _form_record,
    )

    actions: list[tuple[tuple[int, int, int, int], str, Any]] = []
    for index, birth in enumerate(state.native_form_log):
        if type(birth) is not NativeFormRecord:
            raise ValueError("INVALID_NATIVE_FORM_HISTORY")
        _form_record(**asdict(birth))
        if any(
            i not in state.cells or state.cells[i].committed_event != committed
            for i, _, committed, _, _ in birth.witnesses
        ):
            raise ValueError("NATIVE_MEMBER_COMMITMENT_MISMATCH")
        actions.append(((birth.completed_close_serial, 2, index, 0), "FORM", birth))
    for index, edit in enumerate(state.native_mutation_log):
        _mutation_record(**asdict(edit))
        if edit.ordinal != index:
            raise ValueError("INVALID_NATIVE_MUTATION_ORDER")
        actions.append(
            (
                (
                    edit.completed_close_serial,
                    int(edit.stage == "GROW_ADD"),
                    edit.assembly_id,
                    index,
                ),
                "MG",
                edit,
            )
        )
    last_operator_key = (-1, -1, -1, -1)
    for index, raw in enumerate(state.native_operator_log):
        doc = read_operator(raw)
        stage = 3 if doc["operator"] == "MERGE" else 4
        ids = [row[0] for row in doc["before"]]
        key = (doc["close_serial"], stage, ids[0], ids[-1])
        if doc["ordinal"] != index or key <= last_operator_key:
            raise ValueError("INVALID_NATIVE_OPERATOR_ORDER")
        last_operator_key = key
        actions.append((key, "OP", doc))
    histories: dict[int, NativeAssemblyRecord] = {}
    born_at: dict[int, tuple[int, int, int]] = {}
    for _, kind, item in sorted(actions, key=lambda a: a[0]):
        if kind == "FORM":
            if item.assembly_id != len(histories):
                raise ValueError("INVALID_NATIVE_BIRTH_ALLOCATION")
            histories[item.assembly_id] = _assembly_record(
                item.assembly_id,
                Region.LANGUAGE,
                item.members,
                1,
                item.completed_close_serial,
                item.completed_close_serial,
                None,
                "LIVE",
            )
            born_at[item.assembly_id] = (
                item.exposure_id,
                item.event_id,
                item.completed_close_serial,
            )
        elif kind == "MG":
            before = histories.get(item.assembly_id)
            if before is None or (
                before.member_cell_ids,
                before.structural_generation,
                before.status,
            ) != (item.before_members, item.before_generation, item.before_status):
                raise ValueError("NATIVE_MUTATION_CHAIN_MISMATCH")
            origin = born_at[item.assembly_id]
            if (
                item.exposure_id <= origin[0]
                or item.event_id <= origin[1]
                or item.completed_close_serial <= origin[2]
                or item.completed_close_serial < before.last_mutation_close_serial
            ):
                raise ValueError("NATIVE_MUTATION_CHAIN_MISMATCH")
            histories[item.assembly_id] = _assembly_record(
                item.assembly_id,
                Region.LANGUAGE,
                item.after_members,
                item.after_generation,
                before.birth_close_serial,
                item.completed_close_serial,
                before.last_merge_split_close_serial,
                item.after_status,
            )
        else:
            before_rows = [read_assembly_row(r) for r in item["before"]]
            after_rows = [read_assembly_row(r) for r in item["after"]]
            if any(histories.get(r.assembly_id) != r for r in before_rows):
                raise ValueError("NATIVE_OPERATOR_CHAIN_MISMATCH")
            if item["operator"] == "SPLIT":
                child = after_rows[1]
                if child.assembly_id != len(histories):
                    raise ValueError("INVALID_DERIVED_SPLIT_ALLOCATION")
                born_at[child.assembly_id] = (
                    item["exposure_id"],
                    item["event_id"],
                    item["close_serial"],
                )
            for r in after_rows:
                histories[r.assembly_id] = r
    if histories != dict(state.native_assemblies):
        raise ValueError("NATIVE_OPERATOR_REGISTRY_MISMATCH")
    adjacency: dict[int, dict[int, float]] = {}
    directed = {
        (k.source.cell_id, k.target.cell_id): v
        for k, v in state.synapses.items()
        if k.scope is SynapseScope.LOCAL and v.state is SynapseState.CONSOLIDATED
    }
    for (i, j), link in sorted(directed.items()):
        other = directed.get((j, i))
        if other is not None:
            support = min(quality(link), quality(other))
            if q6(support) >= q6(parameter("theta_A")):
                adjacency.setdefault(i, {})[j] = support
    expected: dict[int, frozenset[int]] = {}
    for identity, record in histories.items():
        if any(i not in state.cells for i in record.member_cell_ids):
            raise ValueError("UNCOMMITTED_NATIVE_MEMBER")
        if record.status == "LIVE":
            for cell in record.member_cell_ids:
                if not passes(
                    score(cell, record.member_cell_ids, adjacency), "rho_keep", "sigma_keep"
                ):
                    raise ValueError("INVALID_NATIVE_RECIPROCAL_STRUCTURE")
                expected[cell] = expected.get(cell, frozenset()) | {identity}
    if dict(state.member_assemblies) != expected:
        raise ValueError("NATIVE_MEMBERSHIP_REVERSE_MISMATCH")
    for cell, cell_record in state.cells.items():
        if cell_record.assembly_ids != expected.get(cell, frozenset()) or len(
            cell_record.assembly_ids
        ) > int(parameter("M_max")):
            raise ValueError("NATIVE_CELL_MEMBERSHIP_MISMATCH")
