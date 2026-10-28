"""Isolated READ_ONLY_EPISODE (Core §9.1), never an exposure or evidence root."""

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from types import MappingProxyType

from dgca_next.contracts import EventMode, EventOrigin, EventProvenance, Region
from dgca_next.dynamics.activation import TwoPassResult, two_pass
from dgca_next.dynamics.drive import aggregate, temporal_drives
from dgca_next.dynamics.frontier import Frontiers, final_frontiers
from dgca_next.dynamics.numeric import parameter
from dgca_next.dynamics.provenance import Contribution, Lane, RuntimeSupport, SourceKind
from dgca_next.dynamics.state import GraphSnapshot, Homeostasis, frozen_numbers
from dgca_next.peripheral.sic import SICProjection, project

_AUTHORITY = object()  # In-process scratch provenance, not a persisted/evidence credential.


@dataclass(frozen=True, slots=True)
class FeatureEvent:
    features: tuple[tuple[str, str], ...]
    salience: str = "1.000000"
    boundary: bool = False
    sealed_digest: str | None = None

    def __post_init__(self) -> None:
        if type(self.features) is not tuple or type(self.boundary) is not bool:
            raise ValueError("INVALID_FEATURE_EVENT")
        bundle = project(self.features, salience=self.salience)
        if self.sealed_digest is not None and self.sealed_digest != bundle.digest:
            raise ValueError("SEALED_FEATURE_DIGEST_MISMATCH")


@dataclass(frozen=True, slots=True)
class RuntimeState:
    session_id: int
    next_order: int
    graph_hash: str
    homeostasis: Homeostasis
    activity: Mapping[int, float] = field(default_factory=dict)
    A_prev: Mapping[int, float] = field(default_factory=dict)
    history: tuple[Mapping[int, float], ...] = ()
    frontiers: Frontiers = Frontiers(frozenset(), frozenset(), frozenset())
    emitters: frozenset[int] = frozenset()
    witnesses: Mapping[int, RuntimeSupport] = field(default_factory=dict)
    mu: Mapping[int, float] = field(default_factory=dict)
    _authority: object = field(default=None, repr=False, compare=False)

    def __post_init__(self) -> None:
        if self._authority is not _AUTHORITY:
            raise ValueError("UNVERIFIED_RUNTIME_PROVENANCE")
        if type(self.session_id) is not int or self.session_id < 0:
            raise ValueError("INVALID_SESSION_ID")
        if type(self.next_order) is not int or self.next_order < 0:
            raise ValueError("INVALID_EVENT_ORDER")
        for name in ("activity", "A_prev", "mu"):
            object.__setattr__(self, name, frozen_numbers(getattr(self, name)))
        object.__setattr__(self, "history", tuple(frozen_numbers(a) for a in self.history))
        object.__setattr__(
            self, "witnesses", MappingProxyType(dict(sorted(self.witnesses.items())))
        )


def cold_state(graph: GraphSnapshot, homeostasis: Homeostasis, *, session_id: int) -> RuntimeState:
    return RuntimeState(session_id, 0, graph.structural_hash, homeostasis, _authority=_AUTHORITY)


def cold_reset(state: RuntimeState) -> RuntimeState:
    """Clear every ephemeral lane/frontier/timeline; retain only W/H/session envelope."""
    return RuntimeState(
        state.session_id,
        state.next_order,
        state.graph_hash,
        state.homeostasis,
        _authority=_AUTHORITY,
    )


@dataclass(frozen=True, slots=True)
class EventTrace:
    provenance: EventProvenance
    boundary: bool
    observation: SICProjection
    temporal: Mapping[int, float]
    synchronous: Mapping[int, float]
    sigma: Mapping[int, float]
    passes: TwoPassResult
    contributions: tuple[Contribution, ...]
    state: RuntimeState
    diagnostics: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        for name in ("temporal", "synchronous", "sigma"):
            object.__setattr__(self, name, frozen_numbers(getattr(self, name)))


def read_only_step(
    graph: GraphSnapshot,
    state: RuntimeState,
    event: FeatureEvent,
    *,
    fail_hook: Callable[[str], None] | None = None,
) -> EventTrace:
    if type(state) is not RuntimeState or state._authority is not _AUTHORITY:
        raise ValueError("UNVERIFIED_RUNTIME_PROVENANCE")
    if state.graph_hash != graph.structural_hash:
        raise ValueError("STALE_RUNTIME_GRAPH")
    if type(event) is not FeatureEvent:
        raise ValueError("UNVERIFIED_EVENT_PROVENANCE")
    observation = project(event.features, salience=event.salience)
    if event.sealed_digest is not None and event.sealed_digest != observation.digest:
        raise ValueError("SEALED_FEATURE_DIGEST_MISMATCH")
    if observation.region is not Region.LANGUAGE:
        raise ValueError("I2_LANGUAGE_ONLY")
    previous = cold_reset(state) if event.boundary else state
    if fail_hook:
        fail_hook("CANONICAL_INPUT")
    drives = temporal_drives(graph, previous.activity, previous.frontiers.step, previous.mu)
    temporal = aggregate(drives)
    passes = two_pass(
        graph, state.homeostasis, previous.activity, dict(observation.X), temporal, {}
    )
    if fail_hook:
        fail_hook("PASS2")
    order = state.next_order
    direct = frozenset(i for i, _ in observation.X_fixed if i in graph.committed_ids)
    frontiers = final_frontiers(passes.second.activity, state.homeostasis, direct)
    witnesses = {
        i: RuntimeSupport(
            i,
            u / 1_000_000,
            SourceKind.READ_ONLY_OBSERVED,
            state.session_id,
            order,
            observation.digest,
        )
        for i, u in observation.X_fixed
        if i in direct
    }
    contributions = [
        Contribution(
            i, None, order, Lane.DIRECT_OBSERVED, x, state.session_id, SourceKind.READ_ONLY_OBSERVED
        )
        for i, x in observation.X
    ]
    for drive in drives + passes.synchronous:
        contributions.append(
            Contribution(
                drive.target_id,
                drive.source_id,
                order,
                Lane.PREDICTED if drive in drives else Lane.SPATIALLY_COMPLETED,
                drive.value,
                state.session_id,
                SourceKind.READ_ONLY_OBSERVED,
            )
        )
    for i, a in previous.activity.items():
        residual = (1.0 - parameter("delta_A_LANGUAGE")) * a
        if residual:
            contributions.append(
                Contribution(
                    i,
                    i,
                    order,
                    Lane.RESIDUAL,
                    residual,
                    state.session_id,
                    SourceKind.READ_ONLY_OBSERVED,
                )
            )
    history = (previous.history + (passes.second.activity,))[-int(parameter("H_context")) :]
    after = RuntimeState(
        state.session_id,
        order + 1,
        graph.structural_hash,
        state.homeostasis,
        passes.second.activity,
        previous.activity,
        history,
        frontiers,
        passes.emitters,
        witnesses,
        {},
        _AUTHORITY,
    )
    if fail_hook:
        fail_hook("RESULT")
    return EventTrace(
        EventProvenance(
            EventMode.RETRIEVE, EventOrigin.READ_ONLY_OBSERVED, order, session_id=state.session_id
        ),
        event.boundary,
        observation,
        temporal,
        aggregate(passes.synchronous),
        {},
        passes,
        tuple(contributions),
        after,
    )


def read_only_episode(
    graph: GraphSnapshot,
    homeostasis: Homeostasis,
    events: tuple[FeatureEvent, ...],
    *,
    session_id: int,
) -> tuple[EventTrace, ...]:
    state = cold_state(graph, homeostasis, session_id=session_id)
    traces = []
    for event in events:
        trace = read_only_step(graph, state, event)
        traces.append(trace)
        state = trace.state
    return tuple(traces)
