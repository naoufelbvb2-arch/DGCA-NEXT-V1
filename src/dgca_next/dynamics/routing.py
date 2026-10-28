"""Freeze post-event source μ; directed μ excludes legitimate gated targets."""

from collections.abc import Mapping

from dgca_next.dynamics.context_gate import ContextBindingFixture, structural_diagnostic
from dgca_next.dynamics.provenance import RuntimeSupport, SourceKind
from dgca_next.dynamics.state import GraphSnapshot


def contextual_targets(
    graph: GraphSnapshot, bindings: Mapping[int, ContextBindingFixture]
) -> frozenset[int]:
    return frozenset(
        z
        for z, binding in bindings.items()
        if structural_diagnostic(binding, graph, bindings) is None
    )


def source_mask(
    graph: GraphSnapshot,
    bindings: Mapping[int, ContextBindingFixture],
    gates: Mapping[int, bool],
    frontier: frozenset[int],
    witnesses: Mapping[int, RuntimeSupport],
) -> tuple[dict[int, float], tuple[str, ...]]:
    owners: dict[int, list[int]] = {}
    for z, binding in sorted(bindings.items()):
        if not binding.complete or not gates.get(z, False) or z not in frontier:
            continue
        if structural_diagnostic(binding, graph, bindings):
            continue
        for anchor in binding.anchor_sources:
            witness = witnesses.get(anchor)
            if (
                anchor in frontier
                and anchor not in bindings
                and witness
                and witness.kind is SourceKind.READ_ONLY_OBSERVED
            ):
                owners.setdefault(anchor, []).append(z)
    mu = {i: float(len(zs) == 1) for i, zs in sorted(owners.items())}
    diagnostics = tuple(
        f"AMBIGUOUS_CONTEXT_OWNER:{i}" for i, zs in sorted(owners.items()) if len(zs) > 1
    )
    return mu, diagnostics
