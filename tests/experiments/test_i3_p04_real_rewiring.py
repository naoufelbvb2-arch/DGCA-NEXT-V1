"""Positive P04 experiment uses actual production external roots."""

from i3_p04_real_rewiring import run_trial


def test_actual_hundred_root_atomic_bilateral_rewiring(tmp_path):
    trace = run_trial(tmp_path / "p04.sqlite")
    assert trace["pre_trial_serial"] == 99
    assert trace["disposition99"] == "CONFIRMATION_WINDOW_NOT_ELAPSED"
    assert trace["serial"] == 100 and trace["novelty_q6"] == 1_000_000
    assert len(trace["changes"]) == 2
    assert trace["W_before"] != trace["W_after"]
