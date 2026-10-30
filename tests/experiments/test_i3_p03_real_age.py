"""P03's 99/100 age boundary uses only real completed RootStore exposures."""

from i3_p03_age_trace import run_age_trial


def test_100_actual_completed_roots_and_read_only_feasibility(tmp_path):
    result = run_age_trial(tmp_path / "production-age.sqlite", measure_memory=False)
    assert result["serial99"] == 99 and result["ages99"] == [99, 99]
    assert result["reason99"] == "CONFIRMATION_WINDOW_NOT_ELAPSED"
    assert result["serial100"] == 100 and result["ages100"] == [100, 100]
    assert result["assigned_serials"] == [0, 0]
    assert result["x_fixed"] == 200_000 and result["P_T"] == 0.0
    assert result["novelty"] == 1.0 and result["novelty_q6"] == 1_000_000
    assert result["reason100"] == "ALLOWED" and len(result["replacements"]) == 2
    assert result["provisional_reason"] == "UNVERIFIED_NOVELTY"
    assert result["no_candidate_reason"] == "NO_RECYCLING_REPLACEMENT"
    assert result["protected_reason"] == "RECYCLE_BLOCKED_LIVE_OR_PROTECTED"
    assert result["protected_live_keys"] and all(age >= 100 for age in result["protected_ages"])
    assert result["final_serial"] == 102
