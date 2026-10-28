"""Pure bounded geometry, never latent target selection (Core §§1.1, 7.3)."""

from dataclasses import dataclass

from dgca_next.contracts import CellAddress, Region


@dataclass(frozen=True, slots=True)
class Microcolumn:
    region: Region
    row: int
    col: int

    def __post_init__(self) -> None:
        CellAddress(self.region, self.row, self.col, 0)

    def cell_ids(self) -> tuple[int, ...]:
        return tuple(
            CellAddress(self.region, self.row, self.col, slot).cell_id for slot in range(8)
        )


def microcolumn_of(cell_id: int) -> Microcolumn:
    address = CellAddress.from_cell_id(cell_id)
    return Microcolumn(address.region, address.mc_row, address.mc_col)


def same_microcolumn(first: int, second: int) -> bool:
    return microcolumn_of(first) == microcolumn_of(second)


def microcolumn_neighborhood(anchor_id: int, radius: int) -> tuple[Microcolumn, ...]:
    """Inclusive Manhattan ball, row/column order, clipped within the same region."""
    if type(radius) is not int or radius not in (0, 1, 2):
        raise ValueError("I1 geometry supports integer radius 0, 1 or 2")
    anchor = microcolumn_of(anchor_id)
    return tuple(
        Microcolumn(anchor.region, row, col)
        for row in range(max(0, anchor.row - radius), min(32, anchor.row + radius + 1))
        for col in range(max(0, anchor.col - radius), min(16, anchor.col + radius + 1))
        if abs(row - anchor.row) + abs(col - anchor.col) <= radius
    )
