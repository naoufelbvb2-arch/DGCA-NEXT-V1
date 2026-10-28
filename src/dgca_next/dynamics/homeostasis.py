"""Pure fixture homeostasis from an audited pre-event graph (Core RC4.3 §5)."""

from collections.abc import Mapping
from dataclasses import dataclass

from dgca_next.contracts import CellAddress, Region
from dgca_next.dynamics.numeric import SpecBlocked, clip, parameter, support
from dgca_next.dynamics.state import GraphSnapshot, Homeostasis


@dataclass(frozen=True, slots=True)
class RegionalFiring:
    """Synthetic measurement; neither an external event nor production authority."""

    region: Region
    graph_hash: str
    committed_before: tuple[int, ...]
    active: tuple[int, ...]
    threshold_before: float | None
    rho: float | None
    fixture_only: bool = True


def _validate_inputs(graph: GraphSnapshot, activity: Mapping[int, float]) -> None:
    if type(graph) is not GraphSnapshot:
        raise ValueError("UNVERIFIED_PRE_EVENT_POPULATION")
    graph.validate()
    for cell_id, value in activity.items():
        CellAddress.from_cell_id(cell_id)
        support(value)


def _regional_firing(
    graph: GraphSnapshot,
    homeostasis: Homeostasis,
    activity: Mapping[int, float],
    region: Region,
) -> RegionalFiring:
    if type(region) is not Region:
        raise ValueError("INVALID_HOMEOSTATIC_REGION")
    if region is not Region.LANGUAGE:
        raise SpecBlocked(f"UNRESOLVED_INITIAL_THRESHOLD: {region.name}")
    committed = tuple(
        sorted(i for i in graph.committed_ids if CellAddress.from_cell_id(i).region is region)
    )
    if not committed:
        return RegionalFiring(region, graph.structural_hash, (), (), None, None)
    threshold = homeostasis.threshold(committed[0])
    active = tuple(i for i in committed if activity.get(i, 0.0) >= threshold)
    return RegionalFiring(
        region, graph.structural_hash, committed, active, threshold, len(active) / len(committed)
    )


def regional_firing(
    graph: GraphSnapshot,
    homeostasis: Homeostasis,
    activity: Mapping[int, float],
    *,
    region: Region = Region.LANGUAGE,
) -> RegionalFiring:
    """Derive the exact K_r from audited frozen W; no caller-supplied population/rho.

    The caller must capture W before the fixture event. I2 cannot certify an
    external event, open root, checkpoint or durable H update; I3 owns them.
    """
    _validate_inputs(graph, activity)
    return _regional_firing(graph, homeostasis, activity, region)


def adapt(
    homeostasis: Homeostasis,
    activity: Mapping[int, float],
    *,
    graph: GraphSnapshot,
    regions: tuple[Region, ...] = (Region.LANGUAGE,),
) -> Homeostasis:
    """Return synthetic post-event H from frozen W; no in-place or durable write."""
    if type(regions) is not tuple or len(set(regions)) != len(regions):
        raise ValueError("INVALID_ACTIVE_REGIONS")
    _validate_inputs(graph, activity)
    gains, rates = dict(homeostasis.gains), dict(homeostasis.rates)
    thresholds, region_rates = dict(homeostasis.thresholds), dict(homeostasis.region_rates)
    for region in regions:
        measurement = _regional_firing(graph, homeostasis, activity, region)
        if measurement.rho is None:
            continue
        if region not in region_rates or region not in thresholds:
            raise ValueError("MISSING_EXPLICIT_HOMEOSTASIS_STATE")
        active_ids = frozenset(measurement.active)
        for i in measurement.committed_before:
            if i not in gains or i not in rates:
                raise ValueError("MISSING_EXPLICIT_HOMEOSTASIS_STATE")
            active = int(i in active_ids)
            rates[i] = (1.0 - parameter("beta_I")) * rates[i] + parameter("beta_I") * active
            gains[i] = clip(
                gains[i] + parameter("eta_I") * (parameter("rho_cell") - rates[i]),
                parameter("g_min"),
                parameter("g_max"),
            )
        rho = measurement.rho
        region_rates[region] = (1.0 - parameter("beta_H")) * region_rates[region] + parameter(
            "beta_H"
        ) * rho
        difference = region_rates[region] - parameter(f"rho_target_{region.name}")
        direction = (1 if difference > 0 else -1) if abs(difference) > parameter("eps_dead") else 0
        thresholds[region] = clip(
            thresholds[region] + parameter("eta_H") * direction,
            parameter("theta_min"),
            parameter("theta_max"),
        )
    return Homeostasis(gains, rates, thresholds, region_rates)
