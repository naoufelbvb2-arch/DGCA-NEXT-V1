"""Schema-5 physical Assembly identity and independent membership audit."""

from collections.abc import Mapping
from dataclasses import InitVar, asdict, dataclass
from typing import TYPE_CHECKING

from dgca_next.config import load_lab_config
from dgca_next.contracts import CellAddress, Region, SynapseScope
from dgca_next.graph.cell import nonnegative_integer
from dgca_next.graph.native_lifecycle import passes, score
from dgca_next.graph.native_mutation import NativeStructuralMutationRecord, _mutation_record
from dgca_next.graph.policy import q6
from dgca_next.graph.synapse import SynapseState, quality

if TYPE_CHECKING:
    from dgca_next.graph.network import _State

_PERMIT = object()
_CONFIG = load_lab_config()


def _next_native_id(high_watermark: int, registry: Mapping[int, NativeAssemblyRecord]) -> int:
    """Administrative identity allocation includes archived IDs, never only LIVE."""
    if (
        type(high_watermark) is not int
        or high_watermark != len(registry) - 1
        or tuple(sorted(registry)) != tuple(range(len(registry)))
    ):
        raise ValueError("NATIVE_ASSEMBLY_HIGH_WATERMARK_MISMATCH")
    return high_watermark + 1


@dataclass(frozen=True, slots=True)
class NativeAssemblyRecord:
    assembly_id: int
    region: Region
    member_cell_ids: tuple[int, ...]
    structural_generation: int
    birth_close_serial: int
    last_mutation_close_serial: int
    last_merge_split_close_serial: int | None
    status: str
    _authority: InitVar[object] = None

    @property
    def fixture_only(self) -> bool:
        return False

    def __post_init__(self, _authority: object) -> None:
        if _authority is not _PERMIT:
            raise ValueError("UNVERIFIED_NATIVE_ASSEMBLY_CONSTRUCTION")
        nonnegative_integer(self.assembly_id, "assembly_id")
        for name in ("structural_generation", "birth_close_serial", "last_mutation_close_serial"):
            value = getattr(self, name)
            nonnegative_integer(value, name)
            if value < 1:
                raise ValueError("INVALID_NATIVE_ASSEMBLY_CLOCK")
        if self.last_merge_split_close_serial is not None:
            nonnegative_integer(self.last_merge_split_close_serial, "last_merge_split_close_serial")
            if (
                not self.birth_close_serial
                <= self.last_merge_split_close_serial
                <= self.last_mutation_close_serial
            ):
                raise ValueError("INVALID_NATIVE_ASSEMBLY_CLOCK")
        if self.last_mutation_close_serial < self.birth_close_serial:
            raise ValueError("INVALID_NATIVE_ASSEMBLY_CLOCK")
        if (
            self.region is not Region.LANGUAGE
            or self.status not in ("LIVE", "ARCHIVED")
            or type(self.member_cell_ids) is not tuple
            or self.member_cell_ids != tuple(sorted(set(self.member_cell_ids)))
            or not (3 if self.status == "LIVE" else 0) <= len(self.member_cell_ids) <= 16
            or any(
                CellAddress.from_cell_id(i).region is not self.region for i in self.member_cell_ids
            )
        ):
            raise ValueError("INVALID_NATIVE_ASSEMBLY_MEMBERS")


def _assembly_record(
    assembly_id: int,
    region: Region,
    members: tuple[int, ...],
    generation: int,
    birth: int,
    mutation: int,
    merge_split: int | None,
    status: str,
) -> NativeAssemblyRecord:
    return NativeAssemblyRecord(
        assembly_id,
        region,
        members,
        generation,
        birth,
        mutation,
        merge_split,
        status,
        _authority=_PERMIT,
    )


@dataclass(frozen=True, slots=True)
class NativeFormRecord:
    assembly_id: int
    exposure_id: int
    event_id: int
    event_order: int
    completed_close_serial: int
    members: tuple[int, ...]
    observation_digest: str
    pre_w_hash: str
    pre_h_hash: str
    post_evidence_w_hash: str
    # Physical receiver, direct SIC millionths, committed event, final A, theta_emit.
    witnesses: tuple[tuple[int, int, int, float, float], ...]
    _authority: InitVar[object] = None

    @property
    def fixture_only(self) -> bool:
        return False

    def __post_init__(self, _authority: object) -> None:
        if _authority is not _PERMIT:
            raise ValueError("UNVERIFIED_NATIVE_FORM_CONSTRUCTION")
        for name in (
            "assembly_id",
            "exposure_id",
            "event_id",
            "event_order",
            "completed_close_serial",
        ):
            nonnegative_integer(getattr(self, name), name)
        if (
            self.completed_close_serial < 1
            or type(self.members) is not tuple
            or len(self.members) != 3
        ):
            raise ValueError("INVALID_NATIVE_FORM_MEMBERS")
        if self.members != tuple(sorted(set(self.members))):
            raise ValueError("INVALID_NATIVE_FORM_MEMBERS")
        if type(self.witnesses) is not tuple or len(self.witnesses) != 3:
            raise ValueError("INVALID_NATIVE_FORM_WITNESSES")
        if tuple(w[0] for w in self.witnesses) != self.members:
            raise ValueError("INVALID_NATIVE_FORM_WITNESSES")
        for cell, x, committed, final, threshold in self.witnesses:
            if (
                CellAddress.from_cell_id(cell).region is not Region.LANGUAGE
                or type(x) is not int
                or not 0 < x <= 1_000_000
                or type(committed) is not int
                or not 0 <= committed < self.event_id
                or type(final) is not float
                or type(threshold) is not float
                or not 0 <= final <= 1
                or not 0 < threshold <= 1
                or q6(final) < q6(threshold)
            ):
                raise ValueError("INVALID_NATIVE_FORM_WITNESSES")
        for value in (
            self.observation_digest,
            self.pre_w_hash,
            self.pre_h_hash,
            self.post_evidence_w_hash,
        ):
            if (
                type(value) is not str
                or len(value) != 64
                or any(c not in "0123456789abcdef" for c in value)
            ):
                raise ValueError("INVALID_NATIVE_FORM_HASH")


def _form_record(
    assembly_id: int,
    exposure_id: int,
    event_id: int,
    event_order: int,
    completed_close_serial: int,
    members: tuple[int, ...],
    observation_digest: str,
    pre_w_hash: str,
    pre_h_hash: str,
    post_evidence_w_hash: str,
    witnesses: tuple[tuple[int, int, int, float, float], ...],
) -> NativeFormRecord:
    return NativeFormRecord(
        assembly_id,
        exposure_id,
        event_id,
        event_order,
        completed_close_serial,
        members,
        observation_digest,
        pre_w_hash,
        pre_h_hash,
        post_evidence_w_hash,
        witnesses,
        _authority=_PERMIT,
    )


def validate_native_state(state: _State) -> None:
    if type(state.native_operator_log) is not tuple:
        raise ValueError("INVALID_NATIVE_OPERATOR_LOG")
    native = bool(state.assembly_high_watermarks)
    if not native:
        if (
            state.native_assemblies
            or state.member_assemblies
            or state.native_form_log
            or state.native_mutation_log
            or state.native_operator_log
        ):
            raise ValueError("NATIVE_ASSEMBLY_MODE_REQUIRED")
        return
    if set(state.assembly_high_watermarks) != {Region.LANGUAGE}:
        raise ValueError("UNSUPPORTED_NATIVE_REGION")
    high = state.assembly_high_watermarks[Region.LANGUAGE]
    _next_native_id(high, state.native_assemblies)
    if (
        state.recycling_log
        or state.reservations
        or any(slot.protected or slot.pinned for layout in state.slots.values() for slot in layout)
    ):
        raise ValueError("I4_UNSUPPORTED_PROTECTED_OR_RECYCLING_STATE")
    if any(c.fixture_only for c in state.cells.values()) or any(
        s.fixture_only for s in state.synapses.values()
    ):
        raise ValueError("FIXTURE_NATIVE_ASSEMBLY_FORBIDDEN")
    if state.native_operator_log:
        from dgca_next.graph.native_operator import validate_operator_state

        validate_operator_state(state)
        return
    provenance = {}
    for form_entry in state.native_form_log:
        if type(form_entry) is not NativeFormRecord or form_entry.assembly_id in provenance:
            raise ValueError("INVALID_NATIVE_FORM_HISTORY")
        _form_record(
            form_entry.assembly_id,
            form_entry.exposure_id,
            form_entry.event_id,
            form_entry.event_order,
            form_entry.completed_close_serial,
            form_entry.members,
            form_entry.observation_digest,
            form_entry.pre_w_hash,
            form_entry.pre_h_hash,
            form_entry.post_evidence_w_hash,
            form_entry.witnesses,
        )
        provenance[form_entry.assembly_id] = form_entry
    if set(provenance) != set(state.native_assemblies):
        raise ValueError("NATIVE_FORM_HISTORY_MISSING")
    histories = {i: (r.members, 1, "LIVE", r.completed_close_serial) for i, r in provenance.items()}
    last_order = (-1, -1, -1, -1)
    for ordinal, edit in enumerate(state.native_mutation_log):
        if type(edit) is not NativeStructuralMutationRecord:
            raise ValueError("INVALID_NATIVE_MUTATION_HISTORY")
        _mutation_record(**asdict(edit))
        order = (
            edit.completed_close_serial,
            1 if edit.stage == "GROW_ADD" else 0,
            edit.assembly_id,
            ordinal,
        )
        if edit.ordinal != ordinal or order <= last_order or edit.assembly_id not in histories:
            raise ValueError("INVALID_NATIVE_MUTATION_ORDER")
        previous = histories[edit.assembly_id]
        if (
            previous[:3] != (edit.before_members, edit.before_generation, edit.before_status)
            or edit.completed_close_serial < previous[3]
            or edit.completed_close_serial <= provenance[edit.assembly_id].completed_close_serial
            or edit.exposure_id <= provenance[edit.assembly_id].exposure_id
            or edit.event_id <= provenance[edit.assembly_id].event_id
        ):
            raise ValueError("NATIVE_MUTATION_CHAIN_MISMATCH")
        histories[edit.assembly_id] = (
            edit.after_members,
            edit.after_generation,
            edit.after_status,
            edit.completed_close_serial,
        )
        last_order = order
    adjacency: dict[int, dict[int, float]] = {}
    directed = {
        (k.source.cell_id, k.target.cell_id): link
        for k, link in state.synapses.items()
        if k.scope is SynapseScope.LOCAL
        and link.state is SynapseState.CONSOLIDATED
        and k.source.region is k.target.region is Region.LANGUAGE
    }
    for (i, j), link in sorted(directed.items()):
        reverse = directed.get((j, i))
        if reverse is not None:
            support = min(quality(link), quality(reverse))
            if q6(support) >= q6(float(_CONFIG.parameter("theta_A").value)):
                adjacency.setdefault(i, {})[j] = support
    expected: dict[int, frozenset[int]] = {}
    for identity, record in sorted(state.native_assemblies.items()):
        if type(record) is not NativeAssemblyRecord or identity != record.assembly_id:
            raise ValueError("INVALID_NATIVE_ASSEMBLY_IDENTITY")
        _assembly_record(
            record.assembly_id,
            record.region,
            record.member_cell_ids,
            record.structural_generation,
            record.birth_close_serial,
            record.last_mutation_close_serial,
            record.last_merge_split_close_serial,
            record.status,
        )
        origin = provenance[identity]
        if origin.completed_close_serial != record.birth_close_serial:
            raise ValueError("NATIVE_ASSEMBLY_BIRTH_MISMATCH")
        if record.last_merge_split_close_serial is not None:
            raise ValueError("I4_UNIMPLEMENTED_MERGE_SPLIT")
        if histories[identity] != (
            record.member_cell_ids,
            record.structural_generation,
            record.status,
            record.last_mutation_close_serial,
        ):
            raise ValueError("NATIVE_MUTATION_REGISTRY_MISMATCH")
        if any(i not in state.cells for i in record.member_cell_ids):
            raise ValueError("UNCOMMITTED_NATIVE_MEMBER")
        if any(state.cells[w[0]].committed_event != w[2] for w in origin.witnesses):
            raise ValueError("NATIVE_MEMBER_COMMITMENT_MISMATCH")
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
        ) > int(_CONFIG.parameter("M_max").value):
            raise ValueError("NATIVE_CELL_MEMBERSHIP_MISMATCH")


def native_hash_payload(state: _State) -> dict[str, object]:
    if not state.assembly_high_watermarks:
        return {}
    return {
        "native_assemblies": [
            asdict(record) | {"region": record.region.value}
            for _, record in sorted(state.native_assemblies.items())
        ],
        "assembly_high_watermarks": [
            [r.value, h]
            for r, h in sorted(
                state.assembly_high_watermarks.items(), key=lambda item: item[0].value
            )
        ],
        "member_assemblies": [
            [i, sorted(ids)] for i, ids in sorted(state.member_assemblies.items())
        ],
        "native_form_log": [asdict(record) for record in state.native_form_log],
        **(
            {"native_operator_log": [raw.hex() for raw in state.native_operator_log]}
            if state.native_operator_log
            else {}
        ),
        **(
            {"native_mutation_log": [asdict(record) for record in state.native_mutation_log]}
            if state.native_mutation_log
            else {}
        ),
    }
