"""Sparse logical network. Only explicit fixture construction may commit cells."""

from collections.abc import Iterable, Iterator, Mapping
from types import MappingProxyType

from dgca_next.contracts import CellAddress
from dgca_next.graph.cell import Cell
from dgca_next.graph.latent import LatentSlot, empty_slots, require_latent_policy


class SparseNetwork:
    __slots__ = ("_cells",)

    def __init__(self) -> None:
        self._cells: Mapping[int, Cell] = MappingProxyType({})

    @property
    def stored_cell_count(self) -> int:
        return len(self._cells)

    def cell(self, cell_id: int) -> Cell:
        address = CellAddress.from_cell_id(cell_id)
        return self._cells.get(cell_id, Cell(address))

    def iter_cell_ids(self) -> Iterator[int]:
        return iter(range(12288))

    def iter_cells(self) -> Iterator[Cell]:
        return (self.cell(cell_id) for cell_id in self.iter_cell_ids())

    def stored_cells(self) -> tuple[Cell, ...]:
        return tuple(self._cells[key] for key in sorted(self._cells))

    def latent_slots(self, cell_id: int) -> tuple[LatentSlot, ...]:
        return empty_slots(self.cell(cell_id).address.region)

    def initialize_latent_neighborhoods(self) -> None:
        require_latent_policy()


class FixtureBuilder:
    """Isolated synthetic graph construction, never a LEARN/exposure interface."""

    def __init__(self, network: SparseNetwork) -> None:
        if type(network) is not SparseNetwork:
            raise ValueError("network must be SparseNetwork")
        self._network = network

    def commit_cells(self, cell_ids: Iterable[int], *, committed_event: int) -> None:
        shadow = dict(self._network._cells)
        for cell_id in cell_ids:
            cell = Cell(CellAddress.from_cell_id(cell_id), True, committed_event, True)
            if cell_id in shadow and shadow[cell_id] != cell:
                raise ValueError("CONFLICTING_DUPLICATE_CELL")
            shadow[cell_id] = cell
        self._network._cells = MappingProxyType(shadow)
