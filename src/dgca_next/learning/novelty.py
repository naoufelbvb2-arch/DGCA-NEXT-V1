"""Journal-bound local novelty and read-only bilateral feasibility."""

import math
import sqlite3
from collections.abc import Iterable
from dataclasses import InitVar, dataclass

from dgca_next.config import load_lab_config
from dgca_next.contracts import CellAddress, Region, SynapseKey
from dgca_next.dynamics.activation import two_pass
from dgca_next.dynamics.drive import aggregate, temporal_drives
from dgca_next.dynamics.frontier import final_frontiers
from dgca_next.dynamics.state import GraphSnapshot
from dgca_next.graph.network import SparseNetwork
from dgca_next.graph.policy import q6
from dgca_next.integrity import EXPECTED_SPECS
from dgca_next.learning.homeostasis_profile import LanguageHomeostasis
from dgca_next.learning.production_event import ExternalEventObservation, decode_event
from dgca_next.persistence.graph_codec import decode_production_graph

_CONFIG = load_lab_config()
_PERMIT = object()


def local_residual_novelty(x_fixed: int, prediction: float) -> float:
    """Pure numerical operator; inputs alone never authorize a recycling action."""
    if type(x_fixed) is not int or not 0 <= x_fixed <= 1_000_000:
        raise ValueError("INVALID_DIRECT_SUPPORT")
    if type(prediction) is not float or not math.isfinite(prediction) or not 0 <= prediction <= 1:
        raise ValueError("INVALID_PRE_INPUT_PREDICTION")
    if x_fixed == 0:
        return 0.0
    x = x_fixed / 1_000_000
    return max(0.0, x - min(x, prediction)) / max(x, float(_CONFIG.parameter("eps_p").value))


@dataclass(frozen=True, slots=True)
class VerifiedLocalNovelty:
    receiver_id: int
    exposure_id: int
    event_id: int
    event_order: int
    x_fixed: int
    pre_input_prediction: float
    novelty: float
    novelty_q6: int
    observation_digest: str
    pre_w_hash: str
    config_hash: str
    core_hash: str
    lla_hash: str
    status: str
    close_serial: int | None
    _authority: InitVar[object] = None

    def __post_init__(self, _authority: object) -> None:
        if _authority is not _PERMIT:
            raise ValueError("UNVERIFIED_NOVELTY_CONSTRUCTION")

    @property
    def fixture_only(self) -> bool:
        return False


@dataclass(frozen=True, slots=True)
class SlotOccurrence:
    owner_id: int
    slot_index: int
    target_id: int
    category: str
    assigned_serial: int | None
    age: int | None
    fixed: bool
    protected: bool
    pinned: bool


@dataclass(frozen=True, slots=True)
class RecyclingDecision:
    owner_id: int
    target_id: int
    slot_index: int
    reason: str
    graph_hash: str
    completed_close_serial: int
    occurrences: tuple[SlotOccurrence, ...]
    live_keys: tuple[tuple[int, int, str], ...]
    reserved_keys: tuple[tuple[int, int, str], ...]
    replacements: tuple[tuple[int, int, int], ...]
    novelty: VerifiedLocalNovelty | None

    @property
    def allowed(self) -> bool:
        return self.reason == "ALLOWED"


def _verified_novelty(
    connection: sqlite3.Connection, exposure_id: int, order: int, receiver_id: int
) -> tuple[VerifiedLocalNovelty, ExternalEventObservation]:
    """Verify the stored event and frozen prediction, never caller-provided scalars."""
    for value in (exposure_id, order, receiver_id):
        if type(value) is not int or value < 0:
            raise ValueError("INVALID_NOVELTY_IDENTITY")
    if CellAddress.from_cell_id(receiver_id).region is not Region.LANGUAGE:
        raise ValueError("UNSUPPORTED_NOVELTY_REGION")
    root = connection.execute(
        "SELECT status,close_serial FROM p01_roots WHERE exposure_id=?", (exposure_id,)
    ).fetchone()
    if root is None:
        raise ValueError("UNVERIFIED_NOVELTY: UNKNOWN_ROOT")
    if root[0] not in ("OPEN", "COMPLETED"):
        raise ValueError("UNVERIFIED_NOVELTY: ABORTED_ROOT")
    row = connection.execute(
        "SELECT record,w_before,h_before FROM p01_events WHERE exposure_id=? AND event_order=?",
        (exposure_id, order),
    ).fetchone()
    if row is None:
        raise ValueError("UNVERIFIED_NOVELTY: UNKNOWN_EVENT")
    event = decode_event(row[0])
    pre_graph = GraphSnapshot.capture(decode_production_graph(row[1]))
    if event.pre_committed != tuple(sorted(pre_graph.committed_ids)):
        raise ValueError("UNVERIFIED_NOVELTY: PRESTATE_MISMATCH")
    x_fixed = dict(event.X_fixed).get(receiver_id, 0)
    if not x_fixed:
        raise ValueError("UNVERIFIED_NOVELTY: NO_DIRECT_INPUT")
    if receiver_id not in pre_graph.committed_ids:
        raise ValueError("UNVERIFIED_NOVELTY: NEWBORN_RECEIVER")
    previous = None
    if order and not event.boundary:
        prior = connection.execute(
            "SELECT record,w_before,h_before FROM p01_events WHERE exposure_id=? AND event_order=?",
            (exposure_id, order - 1),
        ).fetchone()
        if prior is None:
            raise ValueError("UNVERIFIED_NOVELTY: MISSING_PREVIOUS_EVENT")
        previous = decode_event(prior[0])
        previous_graph = GraphSnapshot.capture(decode_production_graph(prior[1]))
        previous_h = LanguageHomeostasis.decode(prior[2]).materialize(previous_graph.committed_ids)
        previous_direct = frozenset(
            i for i, _ in previous.X_fixed if i in previous_graph.committed_ids
        )
        previous_frontiers = final_frontiers(dict(previous.final), previous_h, previous_direct)
        if previous.frontier != tuple(sorted(previous_frontiers.step)):
            raise ValueError("UNVERIFIED_NOVELTY: PREVIOUS_FRONTIER_MISMATCH")
    prior_activity = {} if previous is None else dict(previous.final)
    prior_frontier = frozenset() if previous is None else frozenset(previous.frontier)
    temporal = aggregate(temporal_drives(pre_graph, prior_activity, prior_frontier, {}))
    if tuple(sorted(temporal.items())) != event.temporal or event.previous != tuple(
        sorted(prior_activity.items())
    ):
        raise ValueError("UNVERIFIED_NOVELTY: TEMPORAL_LANE_MISMATCH")
    profile = LanguageHomeostasis.decode(row[2])
    homeostasis = profile.materialize(pre_graph.committed_ids)
    projection = dict((i, value / 1_000_000) for i, value in event.X_fixed)
    passes = two_pass(pre_graph, homeostasis, prior_activity, projection, temporal, {})
    direct = frozenset(i for i, _ in event.X_fixed if i in pre_graph.committed_ids)
    frontiers = final_frontiers(passes.second.activity, homeostasis, direct)
    if (
        tuple(sorted(passes.first.raw.items())) != event.pass1_raw
        or tuple(sorted(passes.first.normalized.items())) != event.pass1_normalized
        or tuple(sorted(passes.first.activity.items())) != event.pass1
        or tuple(sorted(passes.second.raw.items())) != event.final_raw
        or tuple(sorted(passes.second.normalized.items())) != event.final_normalized
        or tuple(sorted(passes.second.activity.items())) != event.final
        or tuple(sorted(aggregate(passes.synchronous).items())) != event.synchronous
        or tuple(sorted(passes.emitters)) != event.emitters
        or tuple(sorted(frontiers.learning)) != event.learning_frontier
        or tuple(sorted(frontiers.step)) != event.frontier
    ):
        raise ValueError("UNVERIFIED_NOVELTY: NEURAL_LANE_MISMATCH")
    prediction = temporal.get(receiver_id, 0.0)
    residual = local_residual_novelty(x_fixed, prediction)
    status = "COMPLETED" if root[0] == "COMPLETED" else "PROVISIONAL"
    novelty = VerifiedLocalNovelty(
        receiver_id,
        exposure_id,
        event.event_id,
        order,
        x_fixed,
        prediction,
        residual,
        q6(residual),
        event.digest,
        event.pre_w_hash,
        _CONFIG.sha256,
        EXPECTED_SPECS[0][1],
        EXPECTED_SPECS[1][1],
        status,
        root[1] if status == "COMPLETED" else None,
        _authority=_PERMIT,
    )
    return novelty, event


def _inspect_recycling(
    graph: SparseNetwork,
    completed_serial: int,
    owner_id: int,
    slot_index: int,
    novelty: VerifiedLocalNovelty | None,
    event: ExternalEventObservation | None,
    latest_event_id: int,
) -> RecyclingDecision:
    """Inspect physical topology and ranked replacements without publishing a shadow."""
    if (
        type(graph) is not SparseNetwork
        or type(completed_serial) is not int
        or completed_serial < 0
    ):
        raise ValueError("INVALID_RECYCLING_STATE")
    CellAddress.from_cell_id(owner_id)
    if type(slot_index) is not int or not 0 <= slot_index < 24:
        raise ValueError("INVALID_SLOT_INDEX")
    graph.validate_graph()
    state = graph._state
    owner_slots = state.slots.get(owner_id)
    if owner_slots is None or owner_slots[slot_index].target_id is None:
        raise ValueError("EMPTY_SLOT")
    target = owner_slots[slot_index].target_id
    assert target is not None
    pair = frozenset((owner_id, target))
    affected = tuple(
        sorted(
            (
                (source, slot)
                for source, other in ((owner_id, target), (target, owner_id))
                for slot in state.slots.get(source, ())
                if slot.target_id == other
            ),
            key=lambda item: (item[0], item[1].index),
        )
    )
    occurrences = tuple(
        SlotOccurrence(
            source,
            slot.index,
            slot.target_id,
            slot.category.value,
            slot.assigned_at_completed_close_serial,
            None
            if slot.assigned_at_completed_close_serial is None
            else completed_serial - slot.assigned_at_completed_close_serial,
            not slot.recyclable_category,
            slot.protected,
            slot.pinned,
        )
        for source, slot in affected
        if slot.target_id is not None
    )

    def keys(values: Iterable[SynapseKey]) -> tuple[tuple[int, int, str], ...]:
        return tuple(
            sorted(
                (k.source.cell_id, k.target.cell_id, k.scope.value)
                for k in values
                if frozenset((k.source.cell_id, k.target.cell_id)) == pair
            )
        )

    live, reserved = keys(state.synapses), keys(state.reservations)
    reason = "ALLOWED"
    if any(item.fixed for item in occurrences):
        reason = "RECYCLE_BLOCKED_FIXED"
    elif live or reserved or any(item.protected for item in occurrences):
        reason = "RECYCLE_BLOCKED_LIVE_OR_PROTECTED"
    elif any(item.pinned for item in occurrences):
        reason = "RECYCLE_BLOCKED_CANDIDATE"
    elif any(
        item.age is None or item.age < int(_CONFIG.parameter("W_conf").value)
        for item in occurrences
    ):
        reason = "CONFIRMATION_WINDOW_NOT_ELAPSED"
    elif (
        type(novelty) is not VerifiedLocalNovelty
        or event is None
        or novelty.status != "COMPLETED"
        or novelty.close_serial is None
        or novelty.close_serial > completed_serial
        or novelty.exposure_id != event.exposure_id
        or novelty.event_id != event.event_id
        or novelty.event_order != event.event_order
        or novelty.observation_digest != event.digest
        or novelty.pre_w_hash != event.pre_w_hash
        or novelty.receiver_id not in pair
        or novelty.novelty_q6 < q6(float(_CONFIG.parameter("theta_R").value))
    ):
        reason = "UNVERIFIED_NOVELTY"
    elif event.event_id != latest_event_id:
        reason = "STALE_TRIGGER_EVENT"
    elif any(
        slot.assignment is None or slot.assignment.event_id >= event.event_id
        for _, slot in affected
    ):
        reason = "UNVERIFIED_NOVELTY: EVENT_ORDER"
    replacements: list[tuple[int, int, int]] = []
    if reason == "ALLOWED" and event is not None:
        scores = {i: q6(value) for i, value in event.final if i in event.learning_frontier}
        scores.update({i: q6(value / 1_000_000) for i, value in event.X_fixed if i in event.born})
        for source, slot in affected:
            selected = {source, slot.target_id} | {
                current.target_id
                for current in state.slots[source]
                if current.index != slot.index and current.target_id is not None
            }
            candidates = sorted(
                (
                    i
                    for i in scores
                    if CellAddress.from_cell_id(i).region is slot.permitted_region
                    and i in state.cells
                    and i not in selected
                ),
                key=lambda i: (-scores[i], i),
            )
            if not candidates:
                reason = "NO_RECYCLING_REPLACEMENT"
                replacements.clear()
                break
            replacements.append((source, slot.index, candidates[0]))
    return RecyclingDecision(
        owner_id,
        target,
        slot_index,
        reason,
        graph.structural_hash,
        completed_serial,
        occurrences,
        live,
        reserved,
        tuple(replacements),
        novelty,
    )
