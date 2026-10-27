import json
import re
import subprocess
import sys
import tomllib
from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from dgca_next.config import (
    ConfigurationError,
    LabConfig,
    Parameter,
    UnresolvedParameter,
    load_lab_config,
)

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests/fixtures/i0-contract-v1.json"


def config_toml(values):
    def literal(value):
        if isinstance(value, float) and value != value:
            return "nan"
        return str(value).lower() if type(value) is bool else repr(value)

    return "[lab]\n" + "\n".join(f"{key} = {literal(value)}" for key, value in values.items())


@pytest.fixture
def values():
    return {key: parameter.value for key, parameter in load_lab_config().parameters}


def test_defaults_and_origins_are_deterministic_and_immutable():
    first, second = load_lab_config(), load_lab_config()
    assert first == second
    assert first.to_json() == second.to_json()
    assert first.sha256 == json.loads(FIXTURE.read_text("utf-8"))["config_sha256"]
    with pytest.raises(FrozenInstanceError):
        first.parameters = ()
    with pytest.raises(FrozenInstanceError):
        first.parameter("N").value = 1


def test_configuration_hash_matches_in_a_fresh_interpreter(tmp_path):
    result = subprocess.run(
        [
            sys.executable,
            "-I",
            "-c",
            "from dgca_next.config import load_lab_config; print(load_lab_config().sha256)",
        ],
        cwd=tmp_path,
        text=True,
        capture_output=True,
        check=True,
    )
    assert result.stdout.strip() == load_lab_config().sha256


def test_each_default_cites_an_existing_exact_source_section():
    for _, parameter in load_lab_config().parameters:
        assert parameter.origins
        for origin in parameter.origins:
            path, section = origin.split(" §")
            source = (ROOT / path).read_text("utf-8")
            assert re.search(r"^#{1,4} " + re.escape(section) + r"(?:[. ]|$)", source, re.MULTILINE)


def test_critical_spec_values_and_no_conflation():
    config = load_lab_config()
    expected = {
        "N": 12288,
        "N_r": 4096,
        "B_i": 64,
        "B_i_cross": 12,
        "theta_active_init_LANGUAGE": 0.20,
        "k_neural_ASSOCIATIVE": 1.0,
        "k_evidence_ASSOCIATIVE": 0.7408182206817179,
        "omega_root_replay": 0.25,
        "REPLAY_ENABLED": False,
        "R_max_effective": 0,
        "NEGATIVE_UPDATES_ENABLED": False,
        "W_conf": 100,
        "W_conf_context": 240,
        "probe_matches_max": 8,
        "consolidation_matches_max": 32,
        "candidate_age_max": 240,
        "MAX_CHAIN_DEPTH": 8,
        "T_gen_max": 32,
        "m_P_q6": 50000,
    }
    for name, value in expected.items():
        assert config.parameter(name).value == value
        assert type(config.parameter(name).value) is type(value)


def test_full_snapshot_is_independent_of_toml_key_order(tmp_path, values):
    a, b = tmp_path / "a.toml", tmp_path / "b.toml"
    a.write_text(config_toml(values), "utf-8")
    b.write_text(config_toml(dict(reversed(list(values.items())))), "utf-8")
    assert load_lab_config(a) == load_lab_config(b) == load_lab_config()


@pytest.mark.parametrize("value", [32, 128, 64.0, True, "64", None, [], {}])
def test_invalid_or_contradictory_parameter_is_an_error(tmp_path, values, value):
    values["B_i"] = value
    path = tmp_path / "lab.toml"
    # None/dicts/lists are tested using legal TOML representations where possible.
    if value is None:
        content = config_toml(values).replace("B_i = None", "B_i = 'None'")
    else:
        content = config_toml(values)
    path.write_text(content, "utf-8")
    with pytest.raises((ConfigurationError, tomllib.TOMLDecodeError)):
        load_lab_config(path)


@pytest.mark.parametrize("value", ["nan", "inf", "-inf", "'0.20'", "true"])
def test_nonfinite_and_wrong_float_types_fail(tmp_path, values, value):
    content = config_toml(values).replace(
        "theta_active_init_LANGUAGE = 0.2", f"theta_active_init_LANGUAGE = {value}"
    )
    path = tmp_path / "lab.toml"
    path.write_text(content, "utf-8")
    with pytest.raises(ConfigurationError):
        load_lab_config(path)


@pytest.mark.parametrize("name", ["random_seed", "tau_ctx_q6", "theta_active_init_VISION", "typo"])
def test_absent_or_instance_calibrated_defaults_are_unresolved(name):
    with pytest.raises(UnresolvedParameter, match="UNRESOLVED_PARAMETER"):
        load_lab_config().parameter(name)


def test_unknown_input_parameter_is_unresolved(tmp_path, values):
    values["unknown"] = 1
    path = tmp_path / "lab.toml"
    path.write_text(config_toml(values), "utf-8")
    with pytest.raises(UnresolvedParameter):
        load_lab_config(path)


@pytest.mark.parametrize("key", ["N", "REPLAY_ENABLED", "k_evidence_ASSOCIATIVE"])
def test_missing_value_never_falls_back(tmp_path, values, key):
    del values[key]
    path = tmp_path / "lab.toml"
    path.write_text(config_toml(values), "utf-8")
    with pytest.raises(ConfigurationError, match="missing lab values"):
        load_lab_config(path)


@pytest.mark.parametrize("content", ["", "[other]\nN=1", "lab=1", "[lab]\nB_i=64\nB_i=32"])
def test_invalid_documents_are_errors(tmp_path, content):
    path = tmp_path / "lab.toml"
    path.write_text(content, "utf-8")
    with pytest.raises((ConfigurationError, tomllib.TOMLDecodeError)):
        load_lab_config(path)


def test_missing_file_is_an_error(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_lab_config(tmp_path / "missing.toml")


def test_direct_construction_cannot_bypass_validation():
    with pytest.raises(ConfigurationError):
        LabConfig(())
    defaults = load_lab_config().parameters
    for replacement in (
        Parameter(32, defaults[0][1].origins),
        Parameter(defaults[0][1].value, ("invented source",)),
    ):
        altered = ((defaults[0][0], replacement), *defaults[1:])
        with pytest.raises(ConfigurationError):
            LabConfig(altered)
