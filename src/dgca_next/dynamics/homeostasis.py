"""Pure H_slow arithmetic (Core §5); never called by a read-only event."""

from collections.abc import Mapping

from dgca_next.contracts import CellAddress, Region
from dgca_next.dynamics.numeric import clip, parameter, support
from dgca_next.dynamics.state import Homeostasis


def adapt(homeostasis: Homeostasis, activity: Mapping[int, float]) -> Homeostasis:
    """Explicit synthetic active-event fixture; no durable write or root status."""
    gains, rates = dict(homeostasis.gains), dict(homeostasis.rates)
    thresholds, region_rates = dict(homeostasis.thresholds), dict(homeostasis.region_rates)
    active_by_region: dict[Region, int] = {}
    for i, a in sorted(activity.items()):
        support(a)
        if i not in gains:
            raise ValueError("MISSING_EXPLICIT_HOMEOSTASIS_STATE")
    for i in sorted(gains):
        a = activity.get(i, 0.0)
        region = CellAddress.from_cell_id(i).region
        if (
            i not in gains
            or i not in rates
            or region not in thresholds
            or region not in region_rates
        ):
            raise ValueError("MISSING_EXPLICIT_HOMEOSTASIS_STATE")
        active = int(a >= thresholds[region])
        active_by_region[region] = active_by_region.get(region, 0) + active
        rates[i] = (1.0 - parameter("beta_I")) * rates[i] + parameter("beta_I") * active
        gains[i] = clip(
            gains[i] + parameter("eta_I") * (parameter("rho_cell") - rates[i]),
            parameter("g_min"),
            parameter("g_max"),
        )
    for region in sorted(thresholds, key=lambda r: r.value):
        if region not in region_rates:
            raise ValueError("MISSING_EXPLICIT_HOMEOSTASIS_STATE")
        count = active_by_region.get(region, 0)
        rho = count / 4096
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
