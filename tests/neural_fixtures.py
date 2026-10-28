"""Explicit synthetic I1 physical graphs. These are never learned structures."""

from dataclasses import replace

from dgca_next.contracts import CellAddress, SynapseKey, SynapseScope
from dgca_next.dynamics.context_gate import ContextBindingFixture, ParentFixture, link_fingerprint
from dgca_next.dynamics.state import GraphSnapshot, Homeostasis
from dgca_next.graph import FixtureBuilder, SparseNetwork, Synapse, SynapseState
from dgca_next.peripheral.sic import project


def physical_key(source, target, scope):
    return SynapseKey(CellAddress.from_cell_id(source), CellAddress.from_cell_id(target), scope)


def fixture_graph(edges=(), cells=()):
    """edge=(source,target,scope[,S,E_ext,E_int,state]); all numbers synthetic."""
    graph = SparseNetwork()
    builder = FixtureBuilder(graph)
    ids = set(cells)
    ids.update(i for edge in edges for i in edge[:2])
    builder.commit_cells(sorted(ids), committed_event=0)
    for edge in edges:
        source, target, scope = edge[:3]
        if not graph.structurally_eligible(source, target):
            for owner, other in ((source, target), (target, source)):
                region = CellAddress.from_cell_id(other).region
                slots = [
                    s
                    for s in graph.latent_slots(owner)
                    if s.target_id is None and s.permitted_region is region
                ]
                if slots:
                    builder.inject_slot(owner, slots[0].index, other)
                    break
            else:
                raise AssertionError("fixture cannot satisfy actual latent quota")
        S, E_ext, E_int, state = edge[3:] or (1.0, 10.0, 0.0, SynapseState.CONSOLIDATED)
        builder.add_synapse(
            Synapse(
                physical_key(source, target, scope),
                1 if scope is SynapseScope.ASSOCIATIVE else 0,
                state,
                S,
                E_ext,
                E_int,
                2,
                2,
                True,
                True,
            )
        )
    snapshot = GraphSnapshot.capture(graph)
    return graph, builder, snapshot, Homeostasis.uniform_language(snapshot.committed_ids)


def context_fixture(*, ambiguous=False, nested=False, strength=1.0):
    """Artificial P=a, C=ab paths. Feature names stay exclusively in the test."""
    a = tuple(i for i, _ in project((("a", "1"),)).X_fixed)
    b = tuple(i for i, _ in project((("ab", "1"),)).X_fixed)
    c = tuple(i for i, _ in project((("é", "1"),)).X_fixed)
    p, current, outcomes = (a[1], a[2]), b[:2], (8200, 8208)
    z_ids = (8192, 8193) if ambiguous else (8192,)
    edges = []
    for z in z_ids:
        edges.extend(
            (i, z, SynapseScope.ASSOCIATIVE, strength, 10.0, 0.0, SynapseState.CONSOLIDATED)
            for i in p
        )
        edges.extend(
            (i, z, SynapseScope.LOCAL, strength, 10.0, 0.0, SynapseState.CONSOLIDATED)
            for i in current
        )
        edges.extend((z, y, SynapseScope.ASSOCIATIVE) for y in outcomes)
    edges.append((b[0], 8216, SynapseScope.ASSOCIATIVE))
    if nested:
        edges.extend((i, 8194, SynapseScope.ASSOCIATIVE) for i in (8192, b[0]))
        edges.extend((i, 8194, SynapseScope.LOCAL) for i in c[:2])
        edges.extend((8194, y, SynapseScope.ASSOCIATIVE) for y in (8224, 8232))
    graph, builder, frozen, h = fixture_graph(tuple(edges), cells=(*a, *b, *c))
    bindings = []
    for seq, z in enumerate(z_ids, 1):
        binding = ContextBindingFixture(
            z, p, current, outcomes, b, 800000, 200000, 250000, "", b[0], seq
        )
        bindings.append(replace(binding, link_fingerprint=link_fingerprint(frozen, binding.keys)))
    if nested:
        parent = bindings[0]
        ref = ParentFixture(
            parent.z,
            parent.owner_anchor,
            parent.owner_sequence,
            parent.generation,
            parent.digest,
            parent.depth,
        )
        binding = ContextBindingFixture(
            8194,
            (8192, b[0]),
            c[:2],
            (8224, 8232),
            c,
            800000,
            200000,
            250000,
            "",
            c[0],
            1,
            depth=2,
            parents=(ref,),
            schema_version=3,
        )
        bindings.append(replace(binding, link_fingerprint=link_fingerprint(frozen, binding.keys)))
    return graph, builder, frozen, h, tuple(bindings)


def assembly_fixture():
    from dgca_next.dynamics.attractor import AssemblyFixture

    members = tuple(i for i, _ in project((("a", "1"),)).X_fixed)[:3]
    edges = tuple((i, j, SynapseScope.LOCAL) for i in members for j in members if i != j)
    graph, builder, _, _ = fixture_graph(edges)
    for i in members:
        builder.set_memberships(i, frozenset({7}))
    frozen = GraphSnapshot.capture(graph)
    return (
        graph,
        builder,
        frozen,
        Homeostasis.uniform_language(frozen.committed_ids),
        AssemblyFixture(7, members).bind(frozen),
    )
