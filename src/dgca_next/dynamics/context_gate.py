"""Fixture-only physical context operators (Core §§5.1,6.1). No owner discovery."""

import hashlib
from collections.abc import Mapping
from dataclasses import dataclass

from dgca_next.contracts import CellAddress, SynapseKey, SynapseScope
from dgca_next.dynamics.frontier import support_is_current
from dgca_next.dynamics.numeric import q6
from dgca_next.dynamics.provenance import RuntimeSupport, SourceKind
from dgca_next.dynamics.state import GraphSnapshot
from dgca_next.graph import SynapseState


def _key(source: int, target: int, scope: SynapseScope) -> SynapseKey:
    return SynapseKey(CellAddress.from_cell_id(source), CellAddress.from_cell_id(target), scope)


@dataclass(frozen=True, slots=True)
class ParentFixture:
    cell_id: int
    owner_anchor: int
    owner_sequence: int
    generation: int
    binding_digest: str
    depth: int


@dataclass(frozen=True, slots=True)
class ContextBindingFixture:
    """Explicit synthetic retained descriptor, not StableBinding or a learned OwnerID.

    P/C/Y are physical role keys. Y is used only for structural durability and
    routing qualification, never to decide the P/current-C runtime match.
    """

    z: int
    predecessor: tuple[int, int]
    current: tuple[int, ...]
    outcome: tuple[int, ...]
    anchor_sources: tuple[int, ...]
    owned_lower_q6: int | None
    rival_upper_q6: int | None
    tau_ctx_q6: int | None
    link_fingerprint: str
    owner_anchor: int
    owner_sequence: int
    generation: int = 1
    depth: int = 1
    parents: tuple[ParentFixture, ...] = ()
    complete: bool = True
    active: bool = True
    schema_version: int = 2
    fixture_only: bool = True

    def __post_init__(self) -> None:
        for name in ("predecessor", "current", "outcome", "anchor_sources", "parents"):
            if type(getattr(self, name)) is not tuple:
                raise ValueError("MUTABLE_CONTEXT_FIXTURE")
        for i in (
            self.z,
            self.owner_anchor,
            *self.predecessor,
            *self.current,
            *self.outcome,
            *self.anchor_sources,
        ):
            CellAddress.from_cell_id(i)
        if len(set(self.predecessor)) != 2 or len(self.predecessor) != 2:
            raise ValueError("TWO_DISTINCT_P_REQUIRED")
        for role in (self.current, self.outcome):
            if not 1 <= len(role) <= 2 or len(set(role)) != len(role):
                raise ValueError("INVALID_RETAINED_ROLE")
        if self.z in (*self.predecessor, *self.current, *self.outcome):
            raise ValueError("CONTEXT_SELF_ROLE")
        if (
            self.anchor_sources != tuple(sorted(set(self.anchor_sources)))
            or len(self.anchor_sources) > 64
        ):
            raise ValueError("INVALID_ANCHOR_SOURCE_SET")
        for value in (self.owner_sequence, self.generation, self.depth):
            if type(value) is not int or value < 1:
                raise ValueError("INVALID_CONTEXT_FIXTURE_ID")
        if (
            type(self.complete) is not bool
            or type(self.active) is not bool
            or self.fixture_only is not True
        ):
            raise ValueError("I2_CONTEXT_FIXTURE_ONLY")
        if any(type(p) is not ParentFixture for p in self.parents):
            raise ValueError("INVALID_PARENT_FIXTURE")

    @property
    def keys(self) -> tuple[SynapseKey, ...]:
        return tuple(
            [_key(p, self.z, SynapseScope.ASSOCIATIVE) for p in self.predecessor]
            + [_key(c, self.z, SynapseScope.LOCAL) for c in self.current]
            + [_key(self.z, y, SynapseScope.ASSOCIATIVE) for y in self.outcome]
        )

    @property
    def digest(self) -> str:
        # Diagnostic fixture identity, not a normative StableBinding serializer.
        return hashlib.sha256(repr(self).encode("utf-8")).hexdigest()


def link_fingerprint(graph: GraphSnapshot, keys: tuple[SynapseKey, ...]) -> str:
    result = bytearray(b"DGCA-I2-FIXTURE-KEYS-V1\0")
    for key in keys:
        result.extend(key.source.cell_id.to_bytes(4, "big"))
        result.extend(key.target.cell_id.to_bytes(4, "big"))
        result.extend(bytes((tuple(SynapseScope).index(key.scope),)))
        synapse = graph.synapse(key)
        result.extend(bytes((int(graph.eligible(key.source.cell_id, key.target.cell_id)),)))
        if synapse:
            result.extend(synapse.state.value.encode("ascii") + b"\0")
        else:
            result.extend(b"ABSENT\0")
        for claimant in sorted(graph.claimants(key)):
            result.extend(claimant.to_bytes(4, "big"))
        result.extend(b"\xff\xff\xff\xff")
    return hashlib.sha256(result).hexdigest()


def structural_diagnostic(
    binding: ContextBindingFixture,
    graph: GraphSnapshot,
    bindings: Mapping[int, ContextBindingFixture],
    ancestors: frozenset[int] = frozenset(),
) -> str | None:
    if binding.z in ancestors:
        return "CONTEXT_CHAIN_CYCLE"
    if binding.schema_version != (3 if binding.parents else 2):
        return "UNSUPPORTED_BINDING_SCHEMA"
    L, U, tau = binding.owned_lower_q6, binding.rival_upper_q6, binding.tau_ctx_q6
    if any(type(v) is not int or not 0 <= v <= 1_000_000 for v in (L, U, tau)):
        return "INVALID_CONTEXT_THRESHOLD"
    assert L is not None and U is not None and tau is not None
    if L - U < 50_000 or tau != U + 50_000 or tau > L:
        return "INVALID_CONTEXT_THRESHOLD"
    if (
        not binding.active
        or not set((binding.z, *binding.predecessor, *binding.current, *binding.outcome))
        <= graph.committed_ids
    ):
        return "STALE_CONTEXT_BINDING"
    if binding.depth > 8:
        return "CONTEXT_CHAIN_DEPTH_EXCEEDED"
    if any(i < 8192 for i in (binding.z, *binding.predecessor, *binding.current, *binding.outcome)):
        return "UNSUPPORTED_CONTEXT_REGION"
    if link_fingerprint(graph, binding.keys) != binding.link_fingerprint:
        return "STALE_CONTEXT_BINDING"
    for key in binding.keys:
        live = graph.synapse(key)
        if not graph.eligible(key.source.cell_id, key.target.cell_id):
            return "STALE_CONTEXT_BINDING"
        if binding.complete:
            if live is None or live.state is not SynapseState.CONSOLIDATED:
                return "STALE_CONTEXT_BINDING"
        elif live is None and binding.z not in graph.claimants(key):
            return "MISSING_CONTEXT_SOURCE"
    if not binding.complete:
        if len(binding.current) != 2 or len(binding.outcome) != 2:
            return "MISSING_CONTEXT_SOURCE"
        for i in set((*binding.predecessor, *binding.current, *binding.outcome)):
            if not any(
                s.target_id == i and binding.z in s.pin_owners for s in graph.slots(binding.z)
            ):
                return "MISSING_CONTEXT_SOURCE"
    parent_ids = {p.cell_id for p in binding.parents}
    if len(parent_ids) != len(binding.parents) or not parent_ids <= set(binding.predecessor):
        return "DERIVED_PROVENANCE_UNVERIFIED"
    actual_context_p = set(binding.predecessor) & set(bindings)
    if actual_context_p != parent_ids:
        return "DERIVED_PROVENANCE_UNVERIFIED"
    expected_depth = 1 + max((p.depth for p in binding.parents), default=0)
    if binding.depth != expected_depth:
        return "DERIVED_PROVENANCE_UNVERIFIED"
    for ref in binding.parents:
        parent = bindings.get(ref.cell_id)
        if parent is None or not parent.complete:
            return "PARENT_NOT_COMPLETE"
        if (
            parent.owner_anchor,
            parent.owner_sequence,
            parent.generation,
            parent.digest,
            parent.depth,
        ) != (ref.owner_anchor, ref.owner_sequence, ref.generation, ref.binding_digest, ref.depth):
            return "PARENT_BINDING_STALE"
        if structural_diagnostic(parent, graph, bindings, ancestors | {binding.z}):
            return "PARENT_BINDING_STALE"
    return None


def gate(
    binding: ContextBindingFixture,
    graph: GraphSnapshot,
    bindings: Mapping[int, ContextBindingFixture],
    prior: Mapping[int, RuntimeSupport],
    direct: Mapping[int, float],
    *,
    session_id: int,
    order: int,
    boundary: bool,
) -> tuple[bool, str | None]:
    diagnostic = structural_diagnostic(binding, graph, bindings)
    if diagnostic:
        return False, diagnostic
    if boundary:
        return False, "CONTEXT_HARD_BOUNDARY"
    values = []
    for p in binding.predecessor:
        witness = prior.get(p)
        if witness is None or not support_is_current(witness, session_id, order - 1):
            return False, "MISSING_CONTEXT_SOURCE"
        ref = next((r for r in binding.parents if r.cell_id == p), None)
        if ref is not None:
            if (
                witness.kind is not SourceKind.DERIVED_RUNTIME_CONTEXT
                or witness.binding_digest != ref.binding_digest
            ):
                return False, "DERIVED_PROVENANCE_UNVERIFIED"
        elif witness.kind is not SourceKind.READ_ONLY_OBSERVED:
            return False, "DERIVED_PROVENANCE_UNVERIFIED"
        values.append(witness.value)
    assert binding.tau_ctx_q6 is not None
    if q6(min(values)) < binding.tau_ctx_q6:
        return False, "CONTEXT_BELOW_THRESHOLD"
    if not any(direct.get(c, 0.0) > 0 for c in binding.current):
        return False, "MISSING_CONTEXT_SOURCE"
    return True, None
