from dataclasses import replace

import pytest
from neural_fixtures import context_fixture

from dgca_next.dynamics.context_gate import structural_diagnostic
from dgca_next.dynamics.provenance import Lane, SourceKind
from dgca_next.dynamics.session import FeatureEvent, read_only_episode
from dgca_next.peripheral.sic import receiver_ids


def episode(frozen, h, bindings, supports=("1", "1"), boundary=False):
    return read_only_episode(
        frozen,
        h,
        (
            FeatureEvent((("a", supports[0]),)),
            FeatureEvent((("ab", supports[1]),), boundary=boundary),
        ),
        session_id=5,
        bindings=bindings,
    )


@pytest.mark.parametrize(
    "changes,diagnostic",
    [
        ({"tau_ctx_q6": None}, "INVALID_CONTEXT_THRESHOLD"),
        ({"owned_lower_q6": 220000}, "INVALID_CONTEXT_THRESHOLD"),
        ({"schema_version": 1}, "UNSUPPORTED_BINDING_SCHEMA"),
        ({"active": False}, "STALE_CONTEXT_BINDING"),
        ({"link_fingerprint": "stale"}, "STALE_CONTEXT_BINDING"),
    ],
)
def test_T20_invalid_binding_fails_closed(changes, diagnostic):
    _, _, frozen, h, bindings = context_fixture()
    binding = replace(bindings[0], **changes)
    trace = episode(frozen, h, (binding,))[-1]
    assert trace.passes.first.activity[binding.z] == trace.state.activity[binding.z] == 0.0
    assert any(diagnostic in d for d in trace.diagnostics)


@pytest.mark.parametrize("supports", [("0.2", "1"), ("1", "0")])
def test_T20_missing_or_below_P_C(supports):
    _, _, frozen, h, bindings = context_fixture()
    trace = episode(frozen, h, bindings, supports)[-1]
    assert trace.passes.first.activity[8192] == trace.state.activity[8192] == 0.0
    assert 8192 not in trace.state.frontiers.step
    assert not trace.state.mu


def test_T20_B_only_and_boundary_cannot_match():
    _, _, frozen, h, bindings = context_fixture()
    trace = read_only_episode(
        frozen, h, (FeatureEvent((("ab", "1"),)),), session_id=4, bindings=bindings
    )[0]
    assert trace.state.activity[8192] == 0.0
    assert episode(frozen, h, bindings, boundary=True)[-1].state.activity[8192] == 0.0


def test_T20_direct_SIC_collision_cannot_bypass_context_gate():
    _, _, frozen, h, bindings = context_fixture()
    # Real SHA mapping, found once and pinned below; no forged X.
    text = next(f"gate{n}" for n in range(100000) if 8192 in receiver_ids(f"gate{n}"))
    trace = read_only_episode(
        frozen, h, (FeatureEvent(((text, "1"), ("ab", "1"))),), session_id=4, bindings=bindings
    )[0]
    assert dict(trace.observation.X)[8192] == 1.0
    assert trace.passes.first.raw[8192] == trace.passes.second.raw[8192] == 0.0
    assert trace.state.activity[8192] == 0.0
    assert any(c.target_id == 8192 and c.lane is Lane.DIRECT_OBSERVED for c in trace.contributions)


def test_T21_gate_adds_zero_excitation_actual_weights_decide():
    _, _, frozen, h, bindings = context_fixture()
    trace = episode(frozen, h, bindings)[-1]
    assert trace.gates[8192]
    assert 8192 in trace.state.frontiers.step
    assert trace.state.witnesses[8192].kind is SourceKind.DERIVED_RUNTIME_CONTEXT
    assert trace.state.witnesses[8192].depth == 1
    assert all(c.value == 0.0 for c in trace.contributions if c.lane is Lane.CONTEXT_MATCHED)
    _, _, frozen, h, bindings = context_fixture(strength=0.6)
    # Minimum legal S/E records; small P/C support opens gate, but no probe is added.
    trace = episode(frozen, h, bindings, ("0.25", "0.000001"))[-1]
    assert trace.gates[8192]
    assert trace.state.activity[8192] < h.threshold(8192, "theta_emit_factor")
    assert 8192 not in trace.state.frontiers.step


def test_T21_exact_calibrated_boundary_not_generic_positive():
    _, _, frozen, h, bindings = context_fixture()
    assert episode(frozen, h, bindings, ("0.25", "1"))[-1].gates[8192]
    assert not episode(frozen, h, bindings, ("0.249999", "1"))[-1].gates[8192]
    assert bindings[0].tau_ctx_q6 == 250000


def test_context_fixture_stale_parent_generation_fails_closed():
    _, _, frozen, h, bindings = context_fixture(nested=True)
    parent, child = bindings
    stale = replace(parent, generation=2)
    assert (
        structural_diagnostic(child, frozen, {stale.z: stale, child.z: child})
        == "PARENT_BINDING_STALE"
    )
    traces = read_only_episode(
        frozen,
        h,
        (FeatureEvent((("a", "1"),)), FeatureEvent((("ab", "1"),)), FeatureEvent((("é", "1"),))),
        session_id=4,
        bindings=(stale, child),
    )
    assert traces[-1].state.activity[child.z] == 0.0
