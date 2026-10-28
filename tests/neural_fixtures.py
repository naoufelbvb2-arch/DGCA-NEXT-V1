"""Explicit synthetic I1 physical graphs. These are never learned structures."""

from dgca_next.contracts import CellAddress, SynapseKey, SynapseScope
from dgca_next.dynamics.state import GraphSnapshot, Homeostasis
from dgca_next.graph import FixtureBuilder, SparseNetwork, Synapse, SynapseState


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
