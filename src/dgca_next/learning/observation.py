"""Non-authoritative external-ingress preflight; no witnessed EVENT is minted."""

from dataclasses import dataclass

from dgca_next.config import load_lab_config
from dgca_next.dynamics.numeric import SpecBlocked
from dgca_next.dynamics.state import GraphSnapshot, Homeostasis
from dgca_next.peripheral.sic import SICProjection, project


@dataclass(frozen=True, slots=True)
class IngressDraft:
    """Uncommitted diagnostic data, never an external witness or root proof."""

    projection: SICProjection
    eligible_uncommitted: tuple[tuple[int, int], ...]
    previously_committed: tuple[tuple[int, int], ...]


def preflight(
    graph: GraphSnapshot,
    homeostasis: Homeostasis,
    features: tuple[tuple[str, str], ...],
    *,
    salience: str = "1.000000",
) -> IngressDraft:
    """Validate inputs and determine whether explicit unresolved rules apply.

    Returns possible receivers only; it does not choose or commit a cohort.
    I3 has no actual EVENT authority or persisted observation witness yet.
    """
    if type(graph) is not GraphSnapshot:
        raise ValueError("UNVERIFIED_PRE_EVENT_GRAPH")
    if type(homeostasis) is not Homeostasis or type(features) is not tuple:
        raise ValueError("INVALID_EXTERNAL_INGRESS")
    graph.validate()
    projection = project(features, salience=salience)
    committed = graph.committed_ids
    epsilon = float(load_lab_config().parameter("eps_p").value)
    newborn = tuple(
        (cell, support)
        for cell, support in projection.X_fixed
        if cell not in committed and support / 1_000_000 > epsilon
    )
    observed = tuple((cell, support) for cell, support in projection.X_fixed if cell in committed)
    if len(newborn) > int(load_lab_config().parameter("K_R").value):
        raise SpecBlocked("I3-S01: sensory cohort selection is undefined above K_R")
    if newborn and (
        any(cell not in homeostasis.gains or cell not in homeostasis.rates for cell, _ in newborn)
        or projection.region not in homeostasis.thresholds
        or projection.region not in homeostasis.region_rates
    ):
        raise SpecBlocked("I3-S02: cold/newborn homeostatic initialization is unspecified")
    return IngressDraft(projection, newborn, observed)
