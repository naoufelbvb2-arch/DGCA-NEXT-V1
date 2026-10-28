from collections import Counter

import pytest

from dgca_next.contracts import CellAddress, Region
from dgca_next.graph import (
    SparseNetwork,
    microcolumn_neighborhood,
    microcolumn_of,
    same_microcolumn,
)


def test_i1_t01_full_logical_bijection():
    graph = SparseNetwork()
    ids = tuple(graph.iter_cell_ids())
    assert ids == tuple(range(12288))
    assert len(set(ids)) == 12288
    assert Counter(graph.cell(i).address.region for i in ids) == dict.fromkeys(Region, 4096)
    assert all(CellAddress.from_cell_id(i).cell_id == i for i in ids)
    assert graph.stored_cell_count == 0


@pytest.mark.parametrize(
    "row,col,counts",
    [(0, 0, (1, 3, 6)), (0, 8, (1, 4, 9)), (8, 8, (1, 5, 13)), (31, 15, (1, 3, 6))],
)
@pytest.mark.parametrize("region", Region)
def test_i1_t03_geometry(row, col, counts, region):
    anchor = CellAddress(region, row, col, 7).cell_id
    for radius, count in enumerate(counts):
        result = microcolumn_neighborhood(anchor, radius)
        assert len(result) == count
        assert [(m.row, m.col) for m in result] == sorted((m.row, m.col) for m in result)
        for column in result:
            assert column.region is region
            assert abs(column.row - row) + abs(column.col - col) <= radius
            assert len(column.cell_ids()) == 8
            assert all(microcolumn_of(i) == column for i in column.cell_ids())
    assert same_microcolumn(anchor, anchor - 7)
    assert not same_microcolumn(anchor, (anchor + 8) % 12288)


@pytest.mark.parametrize("radius", [-1, 3, True, 1.0])
def test_geometry_rejects_unsupported_radius(radius):
    with pytest.raises(ValueError):
        microcolumn_neighborhood(0, radius)
