"""Native R05 numerical runtime. Public authority is issued by RootStore only.

No fixture Assembly, expected output, evidence update, owner or W mutation.
Private capture/restore helpers are used only inside authenticated store paths.
"""

import hashlib
from collections.abc import Mapping
from dataclasses import InitVar, dataclass, field
from enum import Enum
from typing import Any

from dgca_next.contracts import CellAddress, EventMode, Region, SynapseKey, SynapseScope
from dgca_next.dynamics.activation import TwoPassResult, two_pass
from dgca_next.dynamics.drive import aggregate, temporal_drives
from dgca_next.dynamics.frontier import Frontiers, final_frontiers
from dgca_next.dynamics.numeric import finite, parameter, q6, support
from dgca_next.dynamics.session import FeatureEvent
from dgca_next.dynamics.state import GraphSnapshot, Homeostasis, frozen_numbers
from dgca_next.graph.native_assembly import NativeAssemblyRecord
from dgca_next.graph.native_lifecycle import quantized_sum
from dgca_next.graph.network import SparseNetwork
from dgca_next.graph.synapse import SynapseState, quality
from dgca_next.learning.homeostasis_profile import LanguageHomeostasis
from dgca_next.peripheral.sic import SICProjection, project
from dgca_next.persistence.native_codec import encode_native_graph

_VIEW = object()
_RUNTIME = object()


class ObservationScope(Enum):
    """The existing LLA2.1 ingress coverage declaration, never an expected Y."""

    COMPLETE_NEXT_EVENT = "COMPLETE_NEXT_EVENT"
    PARTIAL = "PARTIAL"
    UNSPECIFIED = "UNSPECIFIED"


@dataclass(frozen=True, slots=True)
class NativeFeatureEvent:
    event: FeatureEvent
    scope: ObservationScope = ObservationScope.UNSPECIFIED

    def __post_init__(self) -> None:
        if type(self.event) is not FeatureEvent or type(self.scope) is not ObservationScope:
            raise ValueError("INVALID_NATIVE_EXTERNAL_INPUT")


@dataclass(frozen=True, slots=True)
class NativeView:
    graph: GraphSnapshot
    homeostasis: Homeostasis
    w_hash: str
    h_hash: str
    records: tuple[NativeAssemblyRecord, ...]
    _authority: InitVar[object] = None

    def __post_init__(self, _authority: object) -> None:
        if _authority is not _VIEW:
            raise ValueError("UNAUTHENTICATED_NATIVE_VIEW")

    def subject(self, identity: int, generation: int | None = None) -> NativeAssemblyRecord:
        if type(identity) is not int or identity < 0:
            raise ValueError("INVALID_NATIVE_SUBJECT_ID")
        record = next((r for r in self.records if r.assembly_id == identity), None)
        if record is None:
            raise ValueError("UNKNOWN_NATIVE_SUBJECT")
        if record.status != "LIVE":
            raise ValueError("ARCHIVED_NATIVE_SUBJECT")
        if generation is not None and (
            type(generation) is not int or generation != record.structural_generation
        ):
            raise ValueError("STALE_NATIVE_GENERATION")
        return record


def _capture_native_view(graph: SparseNetwork, w: bytes, h: bytes) -> NativeView:
    """Store-private bridge; caller must first authenticate the whole journal."""
    if type(graph) is not SparseNetwork or encode_native_graph(graph) != w:
        raise ValueError("NATIVE_VIEW_W_MISMATCH")
    if any(c.fixture_only for c in graph.stored_cells()) or any(
        s.fixture_only for s in graph.synapses()
    ):
        raise ValueError("FIXTURE_HAS_NO_NATIVE_AUTHORITY")
    frozen = GraphSnapshot.capture(graph)
    records = graph.native_assemblies()
    for record in records:
        if type(record) is not NativeAssemblyRecord or record.fixture_only:
            raise ValueError("UNAUTHENTICATED_NATIVE_SUBJECT")
        if record.status == "LIVE":
            if record.region is not Region.LANGUAGE:
                raise ValueError("UNSUPPORTED_NATIVE_REGION")
            for cell in record.member_cell_ids:
                if (
                    cell not in frozen.committed_ids
                    or record.assembly_id not in graph.cell(cell).assembly_ids
                    or record.assembly_id not in graph.member_assemblies(cell)
                ):
                    raise ValueError("NATIVE_MEMBERSHIP_MISMATCH")
    profile = LanguageHomeostasis.decode(h).materialize(frozen.committed_ids)
    return NativeView(
        frozen,
        profile,
        hashlib.sha256(w).hexdigest(),
        hashlib.sha256(h).hexdigest(),
        records,
        _authority=_VIEW,
    )


@dataclass(frozen=True, slots=True)
class NativeAttractor:
    assembly_id: int
    generation: int
    members: tuple[int, ...]
    strength: float
    age: int
    error: float

    def __post_init__(self) -> None:
        if (
            type(self.assembly_id) is not int
            or self.assembly_id < 0
            or type(self.generation) is not int
            or self.generation < 1
            or type(self.members) is not tuple
            or self.members != tuple(sorted(set(self.members)))
            or not int(parameter("K_min")) <= len(self.members) <= int(parameter("K_max"))
            or any(CellAddress.from_cell_id(i).region is not Region.LANGUAGE for i in self.members)
            or type(self.age) is not int
            or not 0 <= self.age < int(parameter("T_max"))
            or not 0 <= finite(self.error) <= parameter("Theta_err")
        ):
            raise ValueError("INVALID_NATIVE_ATTRACTOR")
        support(self.strength)


@dataclass(frozen=True, slots=True)
class NativeRuntime:
    scope_id: int
    next_order: int
    mode: EventMode
    w_hash: str
    h_hash: str
    activity: Mapping[int, float] = field(default_factory=dict)
    previous: Mapping[int, float] = field(default_factory=dict)
    history: tuple[Mapping[int, float], ...] = ()
    frontiers: Frontiers = Frontiers(frozenset(), frozenset(), frozenset())
    attractors: tuple[NativeAttractor, ...] = ()
    _authority: InitVar[object] = None

    def __post_init__(self, _authority: object) -> None:
        if _authority is not _RUNTIME:
            raise ValueError("UNVERIFIED_NATIVE_RUNTIME")
        if (
            type(self.scope_id) is not int
            or self.scope_id < 0
            or type(self.next_order) is not int
            or self.next_order < 0
            or self.mode not in (EventMode.LEARN, EventMode.RETRIEVE)
        ):
            raise ValueError("INVALID_NATIVE_RUNTIME")
        for name in ("w_hash", "h_hash"):
            value = getattr(self, name)
            if (
                type(value) is not str
                or len(value) != 64
                or any(c not in "0123456789abcdef" for c in value)
            ):
                raise ValueError("INVALID_NATIVE_RUNTIME_HASH")
        for name in ("activity", "previous"):
            object.__setattr__(self, name, frozen_numbers(getattr(self, name)))
        object.__setattr__(self, "history", tuple(frozen_numbers(a) for a in self.history))
        if len(self.history) > int(parameter("H_context")):
            raise ValueError("NATIVE_HISTORY_CAPACITY")
        ids = tuple(a.assembly_id for a in self.attractors)
        if ids != tuple(sorted(set(ids))) or any(
            type(a) is not NativeAttractor for a in self.attractors
        ):
            raise ValueError("INVALID_NATIVE_ATTRACTOR_ORDER")


def _cold_native(view: NativeView, scope_id: int, mode: EventMode) -> NativeRuntime:
    return NativeRuntime(scope_id, 0, mode, view.w_hash, view.h_hash, _authority=_RUNTIME)


def _key(i: int, j: int) -> SynapseKey:
    return SynapseKey(CellAddress.from_cell_id(i), CellAddress.from_cell_id(j), SynapseScope.LOCAL)


def _fresh_scores(
    graph: GraphSnapshot, members: tuple[int, ...], fresh: Mapping[int, float]
) -> tuple[float, float, tuple[tuple[int, int, float], ...]]:
    """Pure physical arithmetic; these numbers alone grant no admission."""
    total = 0.0
    for cell in members:
        total += support(fresh.get(cell, 0.0))
    numerator, denominator = 0.0, 0.0
    pairs = []
    for position, i in enumerate(members):
        for j in members[position + 1 :]:
            a, b = graph.synapse(_key(i, j)), graph.synapse(_key(j, i))
            if (
                a is None
                or b is None
                or a.state is not SynapseState.CONSOLIDATED
                or b.state is not SynapseState.CONSOLIDATED
            ):
                continue
            weight = min(quality(a), quality(b))
            if q6(weight) < q6(parameter("theta_A")):
                continue
            numerator += weight * min(support(fresh.get(i, 0.0)), support(fresh.get(j, 0.0)))
            denominator += weight
            pairs.append((i, j, weight))
    if not members or denominator <= 0.0:
        raise ValueError("INVALID_NATIVE_RECIPROCAL_COHESION")
    return support(total / len(members)), support(numerator / denominator), tuple(pairs)


def _advance(
    subject: NativeAssemblyRecord,
    previous: NativeAttractor | None,
    fresh_mean: float,
    cohesion: float,
    comparable: tuple[tuple[int, float, float], ...],
    boundary: bool,
) -> tuple[NativeAttractor | None, str | None, float]:
    """Private transition arithmetic. Production inputs are computed by native_step."""
    if boundary:
        return None, "ATTRACTOR_BOUNDARY_COLLAPSE", 0.0
    if previous is None:
        if q6(fresh_mean) < q6(parameter("theta_in")):
            return None, "ATTRACTOR_INSUFFICIENT_FRESH_MEAN", 0.0
        if q6(cohesion) < q6(parameter("theta_ctx_form")):
            return None, "ATTRACTOR_INSUFFICIENT_COHESION", 0.0
        return (
            NativeAttractor(
                subject.assembly_id,
                subject.structural_generation,
                subject.member_cell_ids,
                fresh_mean,
                0,
                0.0,
            ),
            None,
            0.0,
        )
    age = previous.age + 1
    if age >= int(parameter("T_max")):
        return None, "ATTRACTOR_AGE_COLLAPSE", 0.0
    missed = 0.0
    for _, predicted, observed in comparable:
        missed += support(predicted) * (1.0 - support(observed))
    miss = missed / len(comparable) if comparable else 0.0
    error = min(parameter("Theta_err") + 1.0, previous.error + miss)
    if quantized_sum(error) > quantized_sum(parameter("Theta_err")):
        return None, "ATTRACTOR_ERROR_COLLAPSE", miss
    return (
        NativeAttractor(
            subject.assembly_id,
            subject.structural_generation,
            subject.member_cell_ids,
            max(parameter("rho_s") * previous.strength, fresh_mean),
            age,
            error,
        ),
        None,
        miss,
    )


@dataclass(frozen=True, slots=True)
class NativeTrace:
    observation: SICProjection
    scope: ObservationScope
    boundary: bool
    temporal: Mapping[int, float]
    sigma: Mapping[int, float]
    passes: TwoPassResult
    fresh: TwoPassResult
    evaluations: tuple[dict[str, Any], ...]
    state: NativeRuntime
    context_sigma_enabled: bool

    def __post_init__(self) -> None:
        for name in ("temporal", "sigma"):
            object.__setattr__(self, name, frozen_numbers(getattr(self, name)))


def _native_step(
    view: NativeView,
    state: NativeRuntime,
    event: NativeFeatureEvent,
    *,
    context_sigma: bool = True,
) -> NativeTrace:
    if (
        type(view) is not NativeView
        or type(state) is not NativeRuntime
        or type(event) is not NativeFeatureEvent
    ):
        raise ValueError("UNVERIFIED_NATIVE_RUNTIME_INPUT")
    if (state.w_hash, state.h_hash) != (view.w_hash, view.h_hash):
        raise ValueError("STALE_NATIVE_RUNTIME_SNAPSHOT")
    if type(context_sigma) is not bool or (state.mode is EventMode.LEARN and not context_sigma):
        raise ValueError("NATIVE_ABLATION_IS_READ_ONLY")
    prior = state
    for old in prior.attractors:
        subject = view.subject(old.assembly_id, old.generation)
        if old.members != subject.member_cell_ids:
            raise ValueError("STALE_NATIVE_ATTRACTOR_MEMBERS")
    if event.event.boundary:
        prior = _cold_native(view, state.scope_id, state.mode)
    projection = project(event.event.features, salience=event.event.salience)
    if event.event.sealed_digest is not None and event.event.sealed_digest != projection.digest:
        raise ValueError("SEALED_FEATURE_DIGEST_MISMATCH")
    temporal = aggregate(temporal_drives(view.graph, prior.activity, prior.frontiers.step, {}))
    old_by_id = {a.assembly_id: a for a in prior.attractors}
    sigma: dict[int, float] = {}
    if context_sigma:
        for old in prior.attractors:
            for cell in view.subject(old.assembly_id, old.generation).member_cell_ids:
                sigma[cell] = max(sigma.get(cell, 0.0), parameter("rho_s") * old.strength)
    X = dict(projection.X)
    passes = two_pass(view.graph, view.homeostasis, prior.activity, X, temporal, sigma)
    fresh = two_pass(view.graph, view.homeostasis, {}, X, {}, {})
    direct = frozenset(i for i, _ in projection.X_fixed if i in view.graph.committed_ids)
    frontiers = final_frontiers(passes.second.activity, view.homeostasis, direct)
    active, evaluations = [], []
    for subject in view.records:
        if subject.status != "LIVE":
            continue
        mean, cohesion, pairs = _fresh_scores(
            view.graph, subject.member_cell_ids, fresh.second.activity
        )
        previous = old_by_id.get(subject.assembly_id)
        predictions = (
            aggregate(
                temporal_drives(
                    view.graph,
                    prior.activity,
                    prior.frontiers.step & frozenset(subject.member_cell_ids),
                    {},
                )
            )
            if previous
            else {}
        )
        predicted = tuple(
            (j, p) for j, p in sorted(predictions.items()) if q6(p) >= q6(parameter("theta_pred"))
        )
        comparable = (
            tuple((j, p, X[j]) for j, p in predicted if j in direct)
            if event.scope is ObservationScope.COMPLETE_NEXT_EVENT
            else ()
        )
        after, diagnostic, miss = _advance(
            subject, previous, mean, cohesion, comparable, event.event.boundary
        )
        if after:
            active.append(after)
        evaluations.append(
            dict(
                assembly_id=subject.assembly_id,
                generation=subject.structural_generation,
                members=list(subject.member_cell_ids),
                fresh_mean=mean,
                fresh_cohesion=cohesion,
                reciprocal_pairs=[list(p) for p in pairs],
                mean_pass=q6(mean) >= q6(parameter("theta_in")),
                cohesion_pass=q6(cohesion) >= q6(parameter("theta_ctx_form")),
                predictions=[list(p) for p in predicted],
                comparables=[list(c) for c in comparable],
                miss=miss,
                diagnostic=diagnostic,
                error_status="EXTERNALLY_COMPARABLE"
                if comparable
                else "NO_EXTERNALLY_COMPARABLE_OUTCOME",
                before=None if previous is None else _attractor_row(previous),
                after=None if after is None else _attractor_row(after),
            )
        )
    after_state = NativeRuntime(
        state.scope_id,
        state.next_order + 1,
        state.mode,
        view.w_hash,
        view.h_hash,
        passes.second.activity,
        prior.activity,
        (prior.history + (passes.second.activity,))[-int(parameter("H_context")) :],
        frontiers,
        tuple(active),
        _authority=_RUNTIME,
    )
    return NativeTrace(
        projection,
        event.scope,
        event.event.boundary,
        temporal,
        sigma,
        passes,
        fresh,
        tuple(evaluations),
        after_state,
        context_sigma,
    )


def _attractor_row(a: NativeAttractor) -> list[Any]:
    return [a.assembly_id, a.generation, list(a.members), a.strength, a.age, a.error]


def _state_document(state: NativeRuntime) -> dict[str, Any]:
    return dict(
        scope_id=state.scope_id,
        next_order=state.next_order,
        mode=state.mode.value,
        w_hash=state.w_hash,
        h_hash=state.h_hash,
        activity=[[i, a] for i, a in state.activity.items()],
        previous=[[i, a] for i, a in state.previous.items()],
        history=[[[i, a] for i, a in h.items()] for h in state.history],
        learning=sorted(state.frontiers.learning),
        cross=sorted(state.frontiers.cross),
        step=sorted(state.frontiers.step),
        attractors=[_attractor_row(a) for a in state.attractors],
    )


def _restore_validated_state(doc: dict[str, Any]) -> NativeRuntime:
    """Store-private restore AFTER journal validation, not a public decoder credential."""
    state = NativeRuntime(
        doc["scope_id"],
        doc["next_order"],
        EventMode(doc["mode"]),
        doc["w_hash"],
        doc["h_hash"],
        dict(doc["activity"]),
        dict(doc["previous"]),
        tuple(dict(h) for h in doc["history"]),
        Frontiers(frozenset(doc["learning"]), frozenset(doc["cross"]), frozenset(doc["step"])),
        tuple(
            NativeAttractor(a[0], a[1], tuple(a[2]), a[3], a[4], a[5]) for a in doc["attractors"]
        ),
        _authority=_RUNTIME,
    )
    if _state_document(state) != doc:
        raise ValueError("NONCANONICAL_NATIVE_RUNTIME")
    return state
