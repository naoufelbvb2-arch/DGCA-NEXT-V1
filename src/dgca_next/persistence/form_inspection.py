"""Read-only projection of FORM prerequisites from an authenticated root close."""

import hashlib
import sqlite3
from dataclasses import dataclass

from dgca_next.config import load_lab_config
from dgca_next.graph.assembly_support import (
    ReciprocalStructureDiagnostic,
    TriangleDiagnostic,
    inspect_structure,
)
from dgca_next.graph.policy import q6
from dgca_next.integrity import EXPECTED_SPECS
from dgca_next.learning.homeostasis_profile import LanguageHomeostasis
from dgca_next.learning.novelty import _verified_novelty
from dgca_next.learning.production_event import decode_event
from dgca_next.persistence.graph_codec import decode_production_graph

_CONFIG = load_lab_config()


@dataclass(frozen=True, slots=True)
class FormMemberWitnessDiagnostic:
    cell_id: int
    direct_x_fixed: int
    committed_before: bool
    committed_event: int | None
    final_activity: float | None
    theta_emit: float | None
    pass1_emitter: bool
    in_f_step: bool
    reason: str

    @property
    def qualified(self) -> bool:
        return self.reason == "OBS_ELIGIBLE_EMISSION"


@dataclass(frozen=True, slots=True)
class FormEventDiagnostic:
    event_id: int
    event_order: int
    observation_digest: str
    pre_w_hash: str
    pre_h_hash: str
    witnesses: tuple[FormMemberWitnessDiagnostic, ...]


@dataclass(frozen=True, slots=True)
class FormCandidateDiagnostic:
    event_id: int
    event_order: int
    triangle: TriangleDiagnostic
    reasons: tuple[str, ...]

    @property
    def selected(self) -> bool:
        return not self.reasons


@dataclass(frozen=True, slots=True)
class FormEligibilityDiagnostic:
    exposure_id: int
    close_serial: int
    source_w_hash: str
    source_h_hash: str
    config_hash: str
    core_hash: str
    lla_hash: str
    structure: ReciprocalStructureDiagnostic
    events: tuple[FormEventDiagnostic, ...]
    candidates: tuple[FormCandidateDiagnostic, ...]
    reason: str

    @property
    def projected_seeds(self) -> tuple[FormCandidateDiagnostic, ...]:
        return tuple(candidate for candidate in self.candidates if candidate.selected)


def _project_candidates(
    structure: ReciprocalStructureDiagnostic, events: tuple[FormEventDiagnostic, ...]
) -> tuple[FormCandidateDiagnostic, ...]:
    """Pure hypothetical selection. No result is a publication capability."""
    selected = 0
    assigned: set[int] = set()
    candidates = []
    limit = int(_CONFIG.parameter("K_FORM_PER_END").value)
    for event in sorted(events, key=lambda e: e.event_order):
        qualified = {w.cell_id for w in event.witnesses if w.qualified}
        for triangle in sorted(structure.triangles, key=lambda t: t.members):
            reasons = list(triangle.reasons)
            reasons.extend(
                f"UNQUALIFIED_FORM_MEMBER:{i}" for i in triangle.members if i not in qualified
            )
            if assigned.intersection(triangle.members):
                reasons.append("FORM_VERTEX_ALREADY_ASSIGNED")
            if selected >= limit:
                reasons.append("K_FORM_PER_END_REACHED")
            candidate = FormCandidateDiagnostic(
                event.event_id, event.event_order, triangle, tuple(reasons)
            )
            candidates.append(candidate)
            if candidate.selected:
                selected += 1
                assigned.update(triangle.members)
    return tuple(candidates)


def _inspect_completed_root(
    connection: sqlite3.Connection, exposure_id: int
) -> FormEligibilityDiagnostic:
    if type(exposure_id) is not int or exposure_id < 0:
        raise ValueError("INVALID_EXPOSURE_ID")
    root = connection.execute(
        "SELECT status,next_order,w_end,h_end,close_serial FROM p01_roots WHERE exposure_id=?",
        (exposure_id,),
    ).fetchone()
    if root is None or root[0] != "COMPLETED":
        raise ValueError("ROOT_NOT_COMPLETED")
    rewired = connection.execute(
        "SELECT disposition FROM p04_requests WHERE exposure_id=?", (exposure_id,)
    ).fetchone()
    if rewired is not None and rewired[0] == "RECYCLED":
        raise ValueError("POST_EVIDENCE_SNAPSHOT_REWIRED: I4_D01_UNRESOLVED")
    graph = decode_production_graph(root[2])
    structure = inspect_structure(graph)
    rows = connection.execute(
        "SELECT event_id,event_order,record,w_before,h_before FROM p01_events "
        "WHERE exposure_id=? ORDER BY event_order",
        (exposure_id,),
    ).fetchall()
    if len(rows) != root[1] or not rows:
        raise ValueError("MISSING_EVENT_SNAPSHOT")
    events = []
    for event_id, order, raw, pre_w, pre_h in rows:
        event = decode_event(raw)
        if (event.exposure_id, event.event_id, event.event_order) != (exposure_id, event_id, order):
            raise ValueError("FORM_EVENT_IDENTITY_MISMATCH")
        before = decode_production_graph(pre_w)
        if event.pre_committed != tuple(c.cell_id for c in before.stored_cells()):
            raise ValueError("FORM_COMMITMENT_SNAPSHOT_MISMATCH")
        if (event.pre_w_hash, event.pre_h_hash) != (
            hashlib.sha256(pre_w).hexdigest(),
            hashlib.sha256(pre_h).hexdigest(),
        ):
            raise ValueError("FORM_PRESTATE_HASH_MISMATCH")
        direct, activity = dict(event.X_fixed), dict(event.final)
        # One genuine committed direct receiver verifies the entire saved
        # neural trace against that EVENT's historical W/H, never current W.
        verifier = next((i for i in event.pre_committed if direct.get(i, 0) > 0), None)
        if verifier is not None:
            _, verified_event = _verified_novelty(connection, exposure_id, order, verifier)
            if verified_event != event:
                raise ValueError("FORM_WITNESS_EVENT_MISMATCH")
        h = LanguageHomeostasis.decode(pre_h).materialize(frozenset(event.pre_committed))
        witnesses = []
        for i in structure.committed:
            cell = before.cell(i)
            committed = (
                i in event.pre_committed
                and cell.committed_event is not None
                and cell.committed_event < event_id
            )
            value = activity.get(i)
            threshold = h.threshold(i, "theta_emit_factor") if committed else None
            if not committed:
                reason = "NOT_COMMITTED_BEFORE_EVENT"
            elif direct.get(i, 0) <= 0:
                reason = "NO_DIRECT_EXTERNAL_WITNESS"
            elif value is None or threshold is None:
                raise ValueError("MISSING_EVENT_ACTIVITY_OR_THRESHOLD")
            elif q6(value) < q6(threshold):
                reason = "BELOW_EVENT_THETA_EMIT"
            else:
                reason = "OBS_ELIGIBLE_EMISSION"
            witnesses.append(
                FormMemberWitnessDiagnostic(
                    i,
                    direct.get(i, 0),
                    committed,
                    cell.committed_event,
                    value,
                    threshold,
                    i in event.emitters,
                    i in event.frontier,
                    reason,
                )
            )
        events.append(
            FormEventDiagnostic(
                event_id, order, event.digest, event.pre_w_hash, event.pre_h_hash, tuple(witnesses)
            )
        )
    event_tuple = tuple(events)
    candidates = _project_candidates(structure, event_tuple)
    reason = (
        "FORM_ELIGIBLE"
        if any(c.selected for c in candidates)
        else "NO_RECIPROCAL_TRIANGLE"
        if not any(t.eligible for t in structure.triangles)
        else "NO_QUALIFIED_FORM_EVENT"
    )
    return FormEligibilityDiagnostic(
        exposure_id,
        root[4],
        hashlib.sha256(root[2]).hexdigest(),
        hashlib.sha256(root[3]).hexdigest(),
        _CONFIG.sha256,
        EXPECTED_SPECS[0][1],
        EXPECTED_SPECS[1][1],
        structure,
        event_tuple,
        candidates,
        reason,
    )
