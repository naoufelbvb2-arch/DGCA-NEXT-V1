from dataclasses import FrozenInstanceError, fields

import pytest

from dgca_next.contracts import CellAddress
from dgca_next.graph import Cell, FixtureBuilder, SparseNetwork


def test_i1_t02_lazy_reads_never_materialize_or_commit():
    graph = SparseNetwork()
    assert len(tuple(graph.iter_cells())) == 12288
    for cell_id in graph.iter_cell_ids():
        assert not graph.cell(cell_id).committed
        assert graph.cell(cell_id).committed_event is None
        assert len(graph.latent_slots(cell_id)) == 24
    assert graph.stored_cells() == ()
    assert graph.stored_cell_count == 0


def test_fixture_commitment_is_explicit_and_immutable():
    graph = SparseNetwork()
    builder = FixtureBuilder(graph)
    builder.commit_cells([8193, 8192], committed_event=0)
    assert [cell.cell_id for cell in graph.stored_cells()] == [8192, 8193]
    assert all(c.committed and c.fixture_only for c in graph.stored_cells())
    before = graph.stored_cells()
    builder.commit_cells([8193, 8192], committed_event=0)
    assert graph.stored_cells() == before
    with pytest.raises(ValueError, match="CONFLICTING_DUPLICATE_CELL"):
        builder.commit_cells([8194, 8192], committed_event=1)
    assert graph.stored_cells() == before
    with pytest.raises(FrozenInstanceError):
        graph.cell(8192).committed = False


@pytest.mark.parametrize(
    "kwargs",
    [
        {"committed": True},
        {"committed_event": 0},
        {"committed": True, "committed_event": 0},
        {"committed": True, "committed_event": -1, "fixture_only": True},
        {"committed": True, "committed_event": True, "fixture_only": True},
        {"committed": 1},
        {"assembly_ids": {1}},
    ],
)
def test_invalid_cell_metadata(kwargs):
    with pytest.raises(ValueError):
        Cell(CellAddress.from_cell_id(0), **kwargs)


def test_no_semantic_or_runtime_fields():
    assert {f.name for f in fields(Cell)} == {
        "address",
        "committed",
        "committed_event",
        "fixture_only",
        "assembly_ids",
        "admission",
    }
