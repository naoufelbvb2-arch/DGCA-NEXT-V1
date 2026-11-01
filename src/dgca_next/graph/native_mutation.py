"""Version-1 structural history; only trusted END/recovery may construct it."""

import math
from dataclasses import InitVar, dataclass
from typing import Any

from dgca_next.contracts import CellAddress, Region
from dgca_next.graph.cell import nonnegative_integer
from dgca_next.graph.native_lifecycle import StructuralScore, passes

_PERMIT = object()


@dataclass(frozen=True, slots=True)
class NativeStructuralMutationRecord:
    schema_version: int
    ordinal: int
    assembly_id: int
    exposure_id: int
    event_id: int
    event_order: int
    completed_close_serial: int
    stage: str
    before_members: tuple[int, ...]
    after_members: tuple[int, ...]
    before_generation: int
    after_generation: int
    before_status: str
    after_status: str
    observation_digest: str
    event_pre_w_hash: str
    event_pre_h_hash: str
    witness_graph_hash: str
    before_w_hash: str
    after_w_hash: str
    scores: tuple[StructuralScore, ...]
    rank_support: float
    inverse_removed: tuple[int, ...]
    inverse_added: tuple[int, ...]
    _authority: InitVar[object] = None

    def __post_init__(self, _authority: object) -> None:
        if _authority is not _PERMIT:
            raise ValueError("UNVERIFIED_NATIVE_MUTATION_CONSTRUCTION")
        if type(self.schema_version) is not int or self.schema_version != 1:
            raise ValueError("UNSUPPORTED_NATIVE_MUTATION_VERSION")
        for name in (
            "ordinal",
            "assembly_id",
            "exposure_id",
            "event_id",
            "event_order",
            "completed_close_serial",
            "before_generation",
            "after_generation",
        ):
            nonnegative_integer(getattr(self, name), name)
        if min(self.completed_close_serial, self.before_generation, self.after_generation) < 1:
            raise ValueError("INVALID_NATIVE_MUTATION_CLOCK")
        for members in (
            self.before_members,
            self.after_members,
            self.inverse_removed,
            self.inverse_added,
        ):
            if (
                type(members) is not tuple
                or members != tuple(sorted(set(members)))
                or len(members) > 16
                or any(CellAddress.from_cell_id(i).region is not Region.LANGUAGE for i in members)
            ):
                raise ValueError("INVALID_NATIVE_MUTATION_MEMBERS")
        removed = tuple(i for i in self.before_members if i not in self.after_members)
        added = tuple(i for i in self.after_members if i not in self.before_members)
        if self.before_status != "LIVE":
            raise ValueError("NATIVE_ARCHIVED_MUTATION_FORBIDDEN")
        if self.stage == "MAINTAIN_REMOVE":
            valid = len(removed) == 1 and not added and self.after_status == "LIVE"
        elif self.stage == "GROW_ADD":
            valid = len(added) == 1 and not removed and self.after_status == "LIVE"
        elif self.stage == "ARCHIVE":
            valid = (
                len(removed) == 1
                and not added
                and len(self.before_members) == 3
                and len(self.after_members) == 2
                and self.after_status == "ARCHIVED"
            )
            removed = self.before_members
        else:
            raise ValueError("UNSUPPORTED_NATIVE_MUTATION_STAGE")
        if (
            not valid
            or self.after_generation != self.before_generation + 1
            or self.inverse_removed != removed
            or self.inverse_added != added
        ):
            raise ValueError("INVALID_NATIVE_MUTATION_DELTA")
        for value in (
            self.observation_digest,
            self.event_pre_w_hash,
            self.event_pre_h_hash,
            self.witness_graph_hash,
            self.before_w_hash,
            self.after_w_hash,
        ):
            if (
                type(value) is not str
                or len(value) != 64
                or any(c not in "0123456789abcdef" for c in value)
            ):
                raise ValueError("INVALID_NATIVE_MUTATION_HASH")
        if (
            type(self.rank_support) is not float
            or not math.isfinite(self.rank_support)
            or self.rank_support < 0
        ):
            raise ValueError("INVALID_NATIVE_MUTATION_RANK")
        if type(self.scores) is not tuple or tuple(v.cell_id for v in self.scores) != (
            self.after_members if self.stage == "GROW_ADD" else self.before_members
        ):
            raise ValueError("INVALID_NATIVE_MUTATION_SCORES")
        for sample in self.scores:
            if (
                type(sample) is not StructuralScore
                or type(sample.degree) is not int
                or sample.degree < 0
                or any(
                    type(x) is not float or not math.isfinite(x) or x < 0
                    for x in (
                        sample.density,
                        sample.numerator,
                        sample.denominator,
                        sample.specificity,
                    )
                )
            ):
                raise ValueError("INVALID_NATIVE_MUTATION_SCORES")
        if self.stage in ("MAINTAIN_REMOVE", "ARCHIVE"):
            failing = [v.cell_id for v in self.scores if not passes(v, "rho_keep", "sigma_keep")]
            erased = tuple(i for i in self.before_members if i not in self.after_members)
            if not failing or min(failing) != erased[0]:
                raise ValueError("INVALID_NATIVE_REMOVAL_ORDER")
        if self.stage == "GROW_ADD" and any(
            not passes(
                v,
                "rho_G" if v.cell_id == added[0] else "rho_keep",
                "sigma_G" if v.cell_id == added[0] else "sigma_keep",
            )
            for v in self.scores
        ):
            raise ValueError("INVALID_NATIVE_GROW_SCORES")


def _mutation_record(**fields: Any) -> NativeStructuralMutationRecord:
    for name in ("before_members", "after_members", "inverse_removed", "inverse_added"):
        fields[name] = tuple(fields[name])
    fields["scores"] = tuple(
        StructuralScore(**v) if type(v) is dict else v for v in fields["scores"]
    )
    return NativeStructuralMutationRecord(**fields, _authority=_PERMIT)
