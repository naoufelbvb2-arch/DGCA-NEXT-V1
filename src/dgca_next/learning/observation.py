"""Non-authoritative external-ingress preflight; no witnessed EVENT is minted."""

from dataclasses import dataclass
from fractions import Fraction

from dgca_next.config import load_lab_config
from dgca_next.dynamics.state import GraphSnapshot, Homeostasis
from dgca_next.peripheral.sic import SICProjection, project


@dataclass(frozen=True, slots=True)
class IngressDraft:
    """Uncommitted diagnostic data, never an external witness or root proof."""

    projection: SICProjection
    eligible_uncommitted: tuple[tuple[int, int], ...]
    previously_committed: tuple[tuple[int, int], ...]
    accepted: tuple[tuple[int, int], ...]
    deferred: tuple[tuple[int, int], ...]

    @property
    def diagnostics(self) -> tuple[tuple[str, int], ...]:
        return tuple(("SENSORY_BIRTH_CAPACITY_DEFERRED", cell) for cell, _ in self.deferred)


def preflight(
    graph: GraphSnapshot,
    homeostasis: Homeostasis,
    features: tuple[tuple[str, str], ...],
    *,
    salience: str = "1.000000",
) -> IngressDraft:
    """Compute an unauthoritative RC4.4 cohort draft over an audited snapshot.

    This is a diagnostic selection, not a committed cohort or a witness. The
    legacy store does not load durable W and must not use this as an EVENT.
    """
    if type(graph) is not GraphSnapshot:
        raise ValueError("UNVERIFIED_PRE_EVENT_GRAPH")
    if type(homeostasis) is not Homeostasis or type(features) is not tuple:
        raise ValueError("INVALID_EXTERNAL_INGRESS")
    graph.validate()
    projection = project(features, salience=salience)
    committed = graph.committed_ids
    epsilon = Fraction(str(load_lab_config().parameter("eps_p").value))
    newborn = tuple(
        (cell, support)
        for cell, support in projection.X_fixed
        if cell not in committed and Fraction(support, 1_000_000) > epsilon
    )
    observed = tuple((cell, support) for cell, support in projection.X_fixed if cell in committed)
    ranked = tuple(sorted(newborn, key=lambda item: (-item[1], item[0])))
    capacity = int(load_lab_config().parameter("K_R").value)
    return IngressDraft(projection, newborn, observed, ranked[:capacity], ranked[capacity:])
