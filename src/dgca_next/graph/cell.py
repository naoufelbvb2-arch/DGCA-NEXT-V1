"""Persistent physical metadata only (Core §§1.1–1.2, 4).

Activity and homeostasis remain in R/H_slow. Fixture commitments remain
distinct from production sensory admissions backed by a root event journal.
"""

from dataclasses import dataclass

from dgca_next.contracts import CellAddress


def nonnegative_integer(value: int, name: str) -> None:
    if type(value) is not int or value < 0:
        raise ValueError(f"invalid {name}: {value!r}")


@dataclass(frozen=True, slots=True)
class ProductionAdmission:
    """Physical birth provenance; the root journal validates its authority."""

    exposure_id: int
    event_id: int
    event_order: int
    observation_digest: str

    def __post_init__(self) -> None:
        for name in ("exposure_id", "event_id", "event_order"):
            nonnegative_integer(getattr(self, name), name)
        if (
            type(self.observation_digest) is not str
            or len(self.observation_digest) != 64
            or any(c not in "0123456789abcdef" for c in self.observation_digest)
        ):
            raise ValueError("INVALID_ADMISSION_DIGEST")


@dataclass(frozen=True, slots=True)
class Cell:
    address: CellAddress
    committed: bool = False
    committed_event: int | None = None
    fixture_only: bool = False
    assembly_ids: frozenset[int] = frozenset()
    admission: ProductionAdmission | None = None

    def __post_init__(self) -> None:
        if type(self.address) is not CellAddress:
            raise ValueError("address must be CellAddress")
        if type(self.committed) is not bool or type(self.fixture_only) is not bool:
            raise ValueError("commitment and fixture markers must be bool")
        if self.committed:
            if self.committed_event is None:
                raise ValueError("COMMITMENT_EVENT_REQUIRED")
            nonnegative_integer(self.committed_event, "committed_event")
            if self.fixture_only:
                if self.admission is not None:
                    raise ValueError("FIXTURE_ADMISSION_FORBIDDEN")
            elif (
                type(self.admission) is not ProductionAdmission
                or self.admission.event_id != self.committed_event
            ):
                raise ValueError("PRODUCTION_ADMISSION_REQUIRED")
        elif self.committed_event is not None or self.assembly_ids or self.admission is not None:
            raise ValueError("uncommitted cell cannot have commitment metadata or memberships")
        if type(self.assembly_ids) is not frozenset or len(self.assembly_ids) > 12:
            raise ValueError("invalid memberships: Core §1.2 M_max=12")
        for assembly_id in self.assembly_ids:
            nonnegative_integer(assembly_id, "assembly_id")

    @property
    def cell_id(self) -> int:
        return self.address.cell_id
