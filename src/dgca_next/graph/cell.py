"""Persistent physical metadata only (Core §§1.1–1.2, 4).

Activity and homeostasis remain in R/H_slow; no values or laws are invented here.
All committed cells in this milestone are explicitly synthetic fixtures.
"""

from dataclasses import dataclass

from dgca_next.contracts import CellAddress


def nonnegative_integer(value: int, name: str) -> None:
    if type(value) is not int or value < 0:
        raise ValueError(f"invalid {name}: {value!r}")


@dataclass(frozen=True, slots=True)
class Cell:
    address: CellAddress
    committed: bool = False
    committed_event: int | None = None
    fixture_only: bool = False
    assembly_ids: frozenset[int] = frozenset()

    def __post_init__(self) -> None:
        if type(self.address) is not CellAddress:
            raise ValueError("address must be CellAddress")
        if type(self.committed) is not bool or type(self.fixture_only) is not bool:
            raise ValueError("commitment and fixture markers must be bool")
        if self.committed:
            if self.committed_event is None or not self.fixture_only:
                raise ValueError("I1 commitment requires an event and fixture_only=True")
            nonnegative_integer(self.committed_event, "committed_event")
        elif self.committed_event is not None or self.assembly_ids:
            raise ValueError("uncommitted cell cannot have commitment metadata or memberships")
        if type(self.assembly_ids) is not frozenset or len(self.assembly_ids) > 12:
            raise ValueError("invalid memberships: Core §1.2 M_max=12")
        for assembly_id in self.assembly_ids:
            nonnegative_integer(assembly_id, "assembly_id")

    @property
    def cell_id(self) -> int:
        return self.address.cell_id
