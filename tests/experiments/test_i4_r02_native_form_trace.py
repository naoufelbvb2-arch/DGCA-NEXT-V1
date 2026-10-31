"""Full native first-FORM production and independent-process recovery trial."""

from i4_r02_native_form_trace import run_trial


def test_first_native_assembly_from_zero_and_independent_cold_restore(tmp_path):
    result = run_trial(tmp_path / "schema5.sqlite")
    assert result["schema"] == 5
    assert result["assembly"]["member_cell_ids"] == (8606, 9345, 11795)
    assert (
        result["assembly"]["status"] == "LIVE" and result["assembly"]["structural_generation"] == 1
    )
    assert [r["form_reason"] for r in result["roots"]] == [
        "NO_RECIPROCAL_TRIANGLE",
        "NO_RECIPROCAL_TRIANGLE",
        "NO_RECIPROCAL_TRIANGLE",
        "FORMED",
    ]
    assert result["independent_process"]["serial"] == 4
    assert not result["automatic_recycling_enabled"]
