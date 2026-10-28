"""Final event frontiers; high residual activity does not mint a new event."""

from collections.abc import Mapping
from dataclasses import dataclass

from dgca_next.dynamics.provenance import RuntimeSupport
from dgca_next.dynamics.state import Homeostasis


@dataclass(frozen=True, slots=True)
class Frontiers:
    learning: frozenset[int]
    cross: frozenset[int]
    step: frozenset[int]


def final_frontiers(
    activity: Mapping[int, float],
    homeostasis: Homeostasis,
    direct: frozenset[int],
    context_matches: frozenset[int] = frozenset(),
) -> Frontiers:
    learning = frozenset(i for i, a in activity.items() if a >= homeostasis.threshold(i))
    cross = frozenset(
        i for i in learning if activity[i] >= homeostasis.threshold(i, "theta_bind_factor")
    )
    step = frozenset(
        i
        for i in direct | context_matches
        if i in activity and activity[i] >= homeostasis.threshold(i, "theta_emit_factor")
    )
    return Frontiers(learning, cross, step)


def support_is_current(witness: RuntimeSupport, session_id: int, order: int) -> bool:
    return (
        type(witness) is RuntimeSupport
        and witness.session_id == session_id
        and witness.event_order == order
        and witness.value > 0
    )
