"""Official R01 production curriculum and persisted inspection, no fixtures."""

from i4_r01_reciprocal_trace import run_trial


def test_cold_real_curriculum_produces_a_repeatable_eligible_triangle(tmp_path):
    trace = run_trial(tmp_path / "r01.sqlite")
    assert trace["cold_inspection_identical"]
    assert [r["reason"] for r in trace["roots"]] == [
        "NO_RECIPROCAL_TRIANGLE",
        "NO_RECIPROCAL_TRIANGLE",
        "NO_RECIPROCAL_TRIANGLE",
        "FORM_ELIGIBLE",
    ]
    final = trace["roots"][-1]
    selected = [c for c in final["candidates"] if c["selected"]]
    assert len(selected) == 1 and selected[0]["members"] == (8606, 9345, 11795)
    assert selected[0]["event_id"] == 5 and selected[0]["event_order"] == 0
    assert all(r["read_only_identical"] for r in trace["roots"])
