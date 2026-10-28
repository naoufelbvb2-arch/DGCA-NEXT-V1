import pytest

from dgca_next.contracts import CellAddress, SynapseKey, SynapseScope
from dgca_next.graph import FixtureBuilder, SparseNetwork, Synapse, SynapseState


@pytest.fixture
def key_factory():
    def make(source=8192, target=8193, scope=SynapseScope.LOCAL):
        return SynapseKey(CellAddress.from_cell_id(source), CellAddress.from_cell_id(target), scope)

    return make


@pytest.fixture
def record_factory(key_factory):
    def make(key=None, **changes):
        key = key_factory() if key is None else key
        values = dict(
            key=key,
            delta=1 if key.scope is SynapseScope.ASSOCIATIVE else 0,
            state=SynapseState.CANDIDATE,
            S=0.6,
            E_ext=1.0,
            E_int=0.0,
            external_root_count=1,
            created_event=2,
            fixture_only=True,
        )
        values.update(changes)
        return Synapse(**values)

    return make


@pytest.fixture
def graph_pair():
    graph = SparseNetwork()
    builder = FixtureBuilder(graph)
    builder.commit_cells([8192, 8193, 8194], committed_event=0)
    builder.inject_slot(8192, 0, 8193)
    return graph, builder
