"""Production experiment is genuine, distinct from numerical component cases."""

from i4_r03_native_lifecycle_trace import run_trial


def test_real_six_root_lifecycle_and_independent_process(tmp_path):
    result = run_trial(tmp_path / "native-lifecycle.sqlite")
    assert result["assembly_after"]["structural_generation"] == 2
    assert result["assembly_after"]["member_cell_ids"] == (8606, 9345, 11795, 12181)
    assert result["root6"]["accepted_count"] == 0
    assert result["production_removal_archive"] == "NOT_RUN"
    assert result["read_only_state_unchanged"]
