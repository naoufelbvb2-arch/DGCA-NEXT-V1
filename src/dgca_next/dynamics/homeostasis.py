"""Pure H_slow arithmetic (Core §5); never called by a read-only event."""

from collections.abc import Mapping

from dgca_next.contracts import CellAddress, Region
from dgca_next.dynamics.numeric import SpecBlocked, clip, parameter, support
from dgca_next.dynamics.state import Homeostasis


def adapt(
    homeostasis: Homeostasis,
    activity: Mapping[int, float],
    *,
    fixture_region_firing: Mapping[Region, float] | None = None,
) -> Homeostasis:
    """Pure formula with explicit synthetic rho_r(t); never certify a real rate.

    Core gives the regional EMA in terms of rho_r(t), but gives no executable
    population/denominator definition. I2 does not choose one implicitly.
    """
    gains, rates = dict(homeostasis.gains), dict(homeostasis.rates)
    thresholds, region_rates = dict(homeostasis.thresholds), dict(homeostasis.region_rates)
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
        rates[i] = (1.0 - parameter("beta_I")) * rates[i] + parameter("beta_I") * active
        gains[i] = clip(
            gains[i] + parameter("eta_I") * (parameter("rho_cell") - rates[i]),
            parameter("g_min"),
            parameter("g_max"),
        )
    for region in sorted(thresholds, key=lambda r: r.value):
        if region not in region_rates:
            raise ValueError("MISSING_EXPLICIT_HOMEOSTASIS_STATE")
        if fixture_region_firing is None or region not in fixture_region_firing:
            raise SpecBlocked(
                "I2-S03: Core §5 rho_r(t) lacks a region population/denominator "
                f"definition: {region.name}"
            )
        rho = support(fixture_region_firing[region])
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
