"""One fixed RC4.1 lab profile, with source origins on every value.

I0 validates declarations only; registry entries do not enable any engine.
External TOML is a complete [lab] snapshot, never an implicit partial override.
Changing a scientific value requires a separately reviewed/versioned profile.
"""

import hashlib
import json
import math
import tomllib
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Final

Scalar = bool | int | float | str
CORE: Final = "docs/specs/DGCA_CORE_RC4_1.md"
LLA: Final = "docs/specs/DGCA_LLA_RC4_1.md"


class ConfigurationError(ValueError):
    """Invalid, incomplete or contradictory fixed-profile configuration."""


class UnresolvedParameter(ConfigurationError):
    """No default is defined in the I0 registry; no value has been guessed."""


@dataclass(frozen=True, slots=True)
class Parameter:
    value: Scalar
    origins: tuple[str, ...]


def _core(value: Scalar, section: str) -> Parameter:
    return Parameter(value, (f"{CORE} §{section}",))


def _lla(value: Scalar, section: str) -> Parameter:
    return Parameter(value, (f"{LLA} §{section}",))


# Literal source values, not computed dynamics or experimentally tuned constants.
_DEFAULTS: Final[Mapping[str, Parameter]] = MappingProxyType(
    {
        "N": _core(12288, "1.1"),
        "N_r": _core(4096, "1.1"),
        "mc_rows": _core(32, "1.1"),
        "mc_cols": _core(16, "1.1"),
        "cells_per_microcolumn": _core(8, "1.1"),
        "delta_A_VISION": _core(0.50, "1.1"),
        "delta_A_AUDIO": _core(0.35, "1.1"),
        "delta_A_LANGUAGE": _core(0.20, "1.1"),
        "gamma_A_VISION": _core(0.90, "1.1"),
        "gamma_A_AUDIO": _core(0.85, "1.1"),
        "gamma_A_LANGUAGE": _core(0.80, "1.1"),
        "beta_VISION": _core(1.00, "1.1"),
        "beta_AUDIO": _core(1.00, "1.1"),
        "beta_LANGUAGE": _core(0.80, "1.1"),
        "rho_target_VISION": _core(0.020, "1.1"),
        "rho_target_AUDIO": _core(0.025, "1.1"),
        "rho_target_LANGUAGE": _core(0.030, "1.1"),
        "g_min": _core(0.70, "1.2"),
        "g_max": _core(1.40, "1.2"),
        "B_i": _core(64, "1.2"),
        "B_i_cross": _core(12, "1.2"),
        "E_cap": _core(4, "1.2"),
        "M_max": _core(12, "1.2"),
        "latent_slots": _core(24, "1.3"),
        "latent_coactive_intra": _core(6, "1.3"),
        "latent_local": _core(6, "1.3"),
        "latent_coactive_inter": _core(6, "1.3"),
        "latent_topographic": _core(6, "1.3"),
        "theta_active_init_LANGUAGE": _core(0.20, "12"),
        "theta_min": _core(0.05, "12"),
        "theta_max": _core(0.60, "12"),
        "theta_emit_factor": _core(1.15, "5"),
        "theta_bind_factor": _core(1.20, "5"),
        "beta_I": _core(0.05, "12"),
        "eta_I": _core(0.002, "12"),
        "rho_cell": _core(0.05, "12"),
        "beta_H": _core(0.05, "12"),
        "eta_H": _core(0.005, "12"),
        "eps_dead": _core(0.002, "12"),
        "K_R": _core(12, "12"),
        "K_sensory": _core(8, "12"),
        "K_context": _core(4, "12"),
        "H_context": _core(5, "12"),
        "eps_p": _lla(1e-6, "9"),
        "theta_R": _lla(0.30, "9"),
        "E_max": _lla(10.0, "9"),
        "theta_S": _lla(0.60, "4.4"),
        "theta_E": _lla(0.30, "4.4"),
        "lambda_demote": _lla(0.80, "4.4"),
        "theta_demote": _lla(0.48, "4.4"),
        "theta_create": _lla(0.20, "5"),
        "theta_create_x": _lla(0.39, "5"),
        "theta_pred": _lla(0.25, "9"),
        "W_conf": _lla(100, "4.4"),
        "W_conf_context": _lla(240, "4.4"),
        "W_episodic": _lla(2000, "4.4"),
        "G_cap_fraction": _lla(0.10, "4.4"),
        "REPLAY_ENABLED": _lla(False, "4.1"),
        "R_max_effective": _lla(0, "4.1"),
        "N_ext": _lla(10, "4.4"),
        "R_max": _lla(3, "4.4"),
        "alpha_rec": _lla(0.05, "4.4"),
        "omega_P": _lla(0.50, "4.1"),
        "omega_R": _lla(0.50, "4.1"),
        "omega_root_external": _lla(1.0, "4.1"),
        "omega_root_replay": _lla(0.25, "4.1"),
        "phi": _lla(0.50, "4.3"),
        "gamma_int": _lla(0.75, "4.3"),
        "NEGATIVE_UPDATES_ENABLED": _lla(False, "0"),
        "k_neural_LOCAL": _lla(1.0, "4.1"),
        "k_neural_CROSS_TERRITORY": _lla(1.0, "4.1"),
        "k_neural_ASSOCIATIVE": _lla(1.0, "4.1"),
        "k_evidence_LOCAL": _lla(1.0, "4.1"),
        "k_evidence_CROSS_TERRITORY": _lla(1.0, "4.1"),
        "k_evidence_ASSOCIATIVE": _lla(0.7408182206817179, "4.1"),
        "n_branch_min": _lla(2, "9"),
        "predecessor_witness_count": _lla(2, "9"),
        "dP_min": _core(0.40, "7.1"),
        "dY_min": _core(0.40, "7.1"),
        "nu_ctx_min": _core(0.30, "7.1"),
        "m_reuse": _core(0.05, "7.1"),
        "m_P": _lla(0.05, "6.2"),
        "m_P_q6": _core(50000, "5.1"),
        "contrast_capacity": _core(16, "7.1"),
        "contrast_TTL": _core(2000, "7.1"),
        "role_pool_size": _core(8, "7.3"),
        "selected_role_count": _core(2, "7.4"),
        "context_search_radius": _core(2, "7.3"),
        "ANCHOR_SOURCE_MAX": _core(64, "7.3"),
        "eta_b": _core(1.0, "7.5"),
        "probe_matches_max": _core(8, "7.4"),
        "consolidation_matches_max": _core(32, "7.4"),
        "candidate_age_max": _core(240, "7.4"),
        "rho_s": _core(0.90, "2.1"),
        "T_max": _core(30, "2.1"),
        "Theta_err": _core(1.50, "2.1"),
        "theta_ctx_form": _core(0.50, "2.1"),
        "theta_in": _core(0.40, "2.1"),
        "omega_X": _core(0.85, "2"),
        "theta_A": _core(0.10, "2.0"),
        "K_min": _core(3, "2.0"),
        "K_max": _core(16, "2.0"),
        "d_min": _core(2, "2.0"),
        "rho_core": _core(0.70, "2.0"),
        "rho_G": _core(0.50, "2.0"),
        "sigma_G": _core(0.30, "2.0"),
        "rho_keep": _core(0.35, "2.0"),
        "sigma_keep": _core(0.20, "2.0"),
        "theta_merge": _core(0.70, "2.0"),
        "theta_ob": _core(0.40, "2.0"),
        "theta_weak": _core(0.15, "2.0"),
        "theta_sep": _core(0.10, "2.0"),
        "N_min": _core(6, "2.0"),
        "T_c": _core(200, "2.0"),
        "K_FORM_PER_END": _core(12, "2.0"),
        "theta_read": _core(0.08, "9.2"),
        "m_read": _core(0.04, "9.2"),
        "MAX_CHAIN_DEPTH": _core(8, "6.1"),
        "T_gen_max": _core(32, "9.3"),
        "ledger_attestation_roots": _core(2, "9.4"),
        "salience": _core("1.000000", "3.1"),
        "sic_salt_0": _core("000102030405060708090a0b0c0d0e0f", "3.1"),
        "sic_salt_1": _core("101112131415161718191a1b1c1d1e1f", "3.1"),
        "sic_salt_2": _core("202122232425262728292a2b2c2d2e2f", "3.1"),
        "sic_salt_3": _core("303132333435363738393a3b3c3d3e3f", "3.1"),
    }
)


@dataclass(frozen=True, slots=True)
class LabConfig:
    """Validated immutable fixed-profile snapshot; no writable mapping exposed."""

    parameters: tuple[tuple[str, Parameter], ...]

    def __post_init__(self) -> None:
        expected = tuple(sorted(_DEFAULTS.items()))
        if type(self.parameters) is not tuple or len(self.parameters) != len(expected):
            raise ConfigurationError("incomplete or malformed lab profile")
        for actual, (key, parameter) in zip(self.parameters, expected, strict=True):
            if (
                type(actual) is not tuple
                or len(actual) != 2
                or actual[0] != key
                or type(actual[1]) is not Parameter
                or type(actual[1].value) is not type(parameter.value)
                or actual[1] != parameter
                or type(actual[1].origins) is not tuple
            ):
                raise ConfigurationError(f"invalid or contradictory lab parameter: {key}")

    def parameter(self, name: str) -> Parameter:
        for key, parameter in self.parameters:
            if key == name:
                return parameter
        raise UnresolvedParameter(f"UNRESOLVED_PARAMETER: {name}")

    def to_json(self) -> str:
        """Deterministic configuration manifest, not neural state persistence."""
        return json.dumps(
            {
                key: {"value": parameter.value, "origins": parameter.origins}
                for key, parameter in self.parameters
            },
            sort_keys=True,
            ensure_ascii=True,
            allow_nan=False,
            separators=(",", ":"),
        )

    @property
    def sha256(self) -> str:
        return hashlib.sha256(self.to_json().encode("utf-8")).hexdigest()


def load_lab_config(path: Path | None = None) -> LabConfig:
    """Read defaults, or require a complete exact [lab] TOML copy of them.

    Absent files, duplicate keys, unknown keys, missing values, type coercion,
    nonfinite values and altered defaults fail closed. No partial overrides.
    """
    if path is not None:
        with path.open("rb") as stream:
            document = tomllib.load(stream)
        if set(document) != {"lab"} or type(document["lab"]) is not dict:
            raise ConfigurationError("expected exactly one [lab] table")
        values = document["lab"]
        unknown = set(values) - set(_DEFAULTS)
        if unknown:
            raise UnresolvedParameter(f"UNRESOLVED_PARAMETER: {sorted(unknown)}")
        missing = set(_DEFAULTS) - set(values)
        if missing:
            raise ConfigurationError(f"missing lab values: {sorted(missing)}")
        for key, parameter in _DEFAULTS.items():
            value = values[key]
            if (
                type(value) is not type(parameter.value)
                or (type(value) is float and not math.isfinite(value))
                or value != parameter.value
                or (type(value) is float and value == 0 and math.copysign(1, value) < 0)
            ):
                raise ConfigurationError(f"invalid or contradictory lab value: {key}")
    return LabConfig(tuple(sorted(_DEFAULTS.items())))
