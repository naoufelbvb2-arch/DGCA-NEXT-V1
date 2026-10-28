"""Isolated READ_ONLY_EPISODE (Core §9.1), never an exposure or evidence root."""

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from types import MappingProxyType

from dgca_next.contracts import EventMode, EventOrigin, EventProvenance, Region
from dgca_next.dynamics.activation import TwoPassResult, two_pass
from dgca_next.dynamics.attractor import (
    AssemblyFixture,
    AttractorState,
    transition,
    validate_assembly,
)
from dgca_next.dynamics.context_gate import ContextBindingFixture, gate
from dgca_next.dynamics.drive import Drive, aggregate, temporal_drives
from dgca_next.dynamics.frontier import Frontiers, final_frontiers
from dgca_next.dynamics.numeric import parameter, q6, support
from dgca_next.dynamics.provenance import Contribution, Lane, RuntimeSupport, SourceKind
from dgca_next.dynamics.routing import contextual_targets, source_mask
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
    bindings: tuple[ContextBindingFixture, ...] = ()
    assemblies: tuple[AssemblyFixture, ...] = ()
    attractors: tuple[AttractorState, ...] = ()
    fixture_cohesion: Mapping[int, float] = field(default_factory=dict)
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
        for name, expected in (
            ("bindings", ContextBindingFixture),
            ("assemblies", AssemblyFixture),
            ("attractors", AttractorState),
        ):
            values = getattr(self, name)
            if type(values) is not tuple or any(type(v) is not expected for v in values):
                raise ValueError("INVALID_RUNTIME_FIXTURE")
        if len({b.z for b in self.bindings}) != len(self.bindings):
            raise ValueError("DUPLICATE_CONTEXT_DESCRIPTOR")
        if len({a.assembly_id for a in self.assemblies}) != len(self.assemblies):
            raise ValueError("DUPLICATE_ASSEMBLY_FIXTURE")
        object.__setattr__(
            self,
            "fixture_cohesion",
            MappingProxyType({i: support(v) for i, v in sorted(self.fixture_cohesion.items())}),
        )


def cold_state(
    graph: GraphSnapshot,
    homeostasis: Homeostasis,
    *,
    session_id: int,
    bindings: tuple[ContextBindingFixture, ...] = (),
    assemblies: tuple[AssemblyFixture, ...] = (),
    fixture_cohesion: Mapping[int, float] | None = None,
) -> RuntimeState:
    for assembly in assemblies:
        validate_assembly(graph, assembly)
    return RuntimeState(
        session_id,
        0,
        graph.structural_hash,
        homeostasis,
        bindings=bindings,
        assemblies=assemblies,
        fixture_cohesion={} if fixture_cohesion is None else fixture_cohesion,
        _authority=_AUTHORITY,
    )


def cold_reset(state: RuntimeState) -> RuntimeState:
    """Clear every ephemeral lane/frontier/timeline; retain only W/H/session envelope."""
    return RuntimeState(
        state.session_id,
        state.next_order,
        state.graph_hash,
        state.homeostasis,
        bindings=state.bindings,
        assemblies=state.assemblies,
        fixture_cohesion=state.fixture_cohesion,
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
    fresh: TwoPassResult | None = None
    gates: Mapping[int, bool] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in ("temporal", "synchronous", "sigma"):
            object.__setattr__(self, name, frozen_numbers(getattr(self, name)))
        object.__setattr__(self, "gates", MappingProxyType(dict(self.gates)))


def _context_operators(
    graph: GraphSnapshot, previous: RuntimeState, X: Mapping[int, float], boundary: bool
) -> tuple[dict[int, bool], dict[int, float], list[str]]:
    bindings = {b.z: b for b in previous.bindings}
    gates, diagnostics = {}, []
    for z, binding in sorted(bindings.items()):
        allowed, diagnostic = gate(
            binding,
            graph,
            bindings,
            previous.witnesses,
            X,
            session_id=previous.session_id,
            order=previous.next_order,
            boundary=boundary,
        )
        gates[z] = allowed
        if diagnostic:
            diagnostics.append(f"{diagnostic}:{z}")
    assemblies = {a.assembly_id: a for a in previous.assemblies}
    sigma: dict[int, float] = {}
    for attractor in previous.attractors:
        assembly = assemblies.get(attractor.assembly_id)
        if assembly is None:
            raise ValueError("UNVERIFIED_ATTRACTOR_ASSEMBLY")
        validate_assembly(graph, assembly)
        for i in assembly.members:
            sigma[i] = max(sigma.get(i, 0.0), parameter("rho_s") * attractor.strength)
    return gates, sigma, diagnostics


def next_drives(graph: GraphSnapshot, state: RuntimeState) -> tuple[Drive, ...]:
    if (
        type(state) is not RuntimeState
        or state._authority is not _AUTHORITY
        or state.graph_hash != graph.structural_hash
    ):
        raise ValueError("UNVERIFIED_RUNTIME_PROVENANCE")
    targets = contextual_targets(graph, {b.z: b for b in state.bindings})
    return temporal_drives(graph, state.activity, state.frontiers.step, state.mu, targets)


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
    drives = next_drives(graph, previous)
    temporal = aggregate(drives)
    X = dict(observation.X)
    gates, sigma, diagnostics = _context_operators(graph, previous, X, event.boundary)
    passes = two_pass(graph, state.homeostasis, previous.activity, X, temporal, sigma, gates=gates)
    if fail_hook:
        fail_hook("PASS2")
    order = state.next_order
    direct = frozenset(i for i, _ in observation.X_fixed if i in graph.committed_ids)
    matches = frozenset(z for z, allowed in gates.items() if allowed)
    frontiers = final_frontiers(passes.second.activity, state.homeostasis, direct, matches)
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
    for binding in state.bindings:
        z = binding.z
        if gates.get(z, False):
            contributions.append(
                Contribution(
                    z,
                    None,
                    order,
                    Lane.CONTEXT_MATCHED,
                    0.0,
                    state.session_id,
                    SourceKind.DERIVED_RUNTIME_CONTEXT,
                )
            )
        if binding.complete and gates.get(z, False) and z in frontiers.step:
            parents = tuple(
                (p, order - 1, previous.witnesses[p].bundle_digest) for p in binding.predecessor
            )
            parents += tuple(
                (c, order, observation.digest) for c in binding.current if X.get(c, 0.0) > 0
            )
            witnesses[z] = RuntimeSupport(
                z,
                q6(passes.second.activity[z]) / 1_000_000,
                SourceKind.DERIVED_RUNTIME_CONTEXT,
                state.session_id,
                order,
                observation.digest,
                binding.depth,
                binding.digest,
                parents,
            )
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
        if residual and gates.get(i, True):
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
    for i, value in sigma.items():
        if value:
            contributions.append(
                Contribution(
                    i,
                    None,
                    order,
                    Lane.ATTRACTOR,
                    value,
                    state.session_id,
                    SourceKind.READ_ONLY_OBSERVED,
                )
            )
    mu, route_diagnostics = source_mask(
        graph, {b.z: b for b in state.bindings}, gates, frontiers.step, witnesses
    )
    diagnostics.extend(route_diagnostics)
    fresh = (
        two_pass(graph, state.homeostasis, {}, X, {}, {}, gates=gates) if state.assemblies else None
    )
    attractors = []
    prior_attractors = {a.assembly_id: a for a in previous.attractors}
    for assembly in state.assemblies:
        assert fresh is not None
        mean = sum(fresh.second.activity[i] for i in assembly.members) / len(assembly.members)
        attractor, diagnostic = transition(
            prior_attractors.get(assembly.assembly_id),
            assembly_id=assembly.assembly_id,
            fresh_mean=mean,
            boundary=event.boundary,
            cohesion=state.fixture_cohesion.get(assembly.assembly_id),
        )
        if attractor:
            attractors.append(attractor)
        if diagnostic:
            diagnostics.append(diagnostic)
    history = (previous.history + (passes.second.activity,))[-int(parameter("H_context")) :]
    after = RuntimeState(
        state.session_id,
        order + 1,
        graph.structural_hash,
        state.homeostasis,
        activity=passes.second.activity,
        A_prev=previous.activity,
        history=history,
        frontiers=frontiers,
        emitters=passes.emitters,
        witnesses=witnesses,
        mu=mu,
        bindings=state.bindings,
        assemblies=state.assemblies,
        attractors=tuple(attractors),
        fixture_cohesion=state.fixture_cohesion,
        _authority=_AUTHORITY,
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
        sigma,
        passes,
        tuple(contributions),
        after,
        tuple(diagnostics),
        fresh,
        gates,
    )


def read_only_episode(
    graph: GraphSnapshot,
    homeostasis: Homeostasis,
    events: tuple[FeatureEvent, ...],
    *,
    session_id: int,
    bindings: tuple[ContextBindingFixture, ...] = (),
    assemblies: tuple[AssemblyFixture, ...] = (),
    fixture_cohesion: Mapping[int, float] | None = None,
) -> tuple[EventTrace, ...]:
    state = cold_state(
        graph,
        homeostasis,
        session_id=session_id,
        bindings=bindings,
        assemblies=assemblies,
        fixture_cohesion=fixture_cohesion,
    )
    traces = []
    for event in events:
        trace = read_only_step(graph, state, event)
        traces.append(trace)
        state = trace.state
    return tuple(traces)
