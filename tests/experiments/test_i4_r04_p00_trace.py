"""Genuine production feasibility and read-only/cold recovery evidence."""

from i4_r04_p00_trace import run_trial


def test_declared_production_curricula_and_clock(tmp_path):
    result = run_trial(tmp_path)
    a, b, c = result["curricula"]
    actual = a["final"]["inspection"]
    assert actual["identities"][0]["members"] == (8606, 9345, 11795, 12181)
    assert actual["merge_status"] == "MERGE_NOT_APPLICABLE"
    assert actual["split_status"] == "SPLIT_NOT_APPLICABLE"
    assert all(p["support"] >= 0.4 for p in actual["pairs"])
    assert b["terminal_reason"] == "I4_UNIMPLEMENTED_MERGE_SPLIT"
    assert c["terminal_reason"] == "I4_FIRST_FORM_LAB_SCOPE_EXCEEDED"
    assert len(b["final"]["inspection"]["identities"]) == 1
    assert not c["final"]["inspection"]["identities"]
    assert all(x["recovery"]["independent_reopen_exact"] for x in result["curricula"])
    assert result["clock"]["diagnostic_start_reference"]["elapsed_roots"] == 2
    assert result["clock"]["diagnostic_start_reference"]["elapsed_events"] == 6
    assert result["clock"]["final"]["inspection"]["aborted_event_count"] == 3
    assert result["component"]["split16"]["examined"] == 32631
    assert result["native_merge_split_mutations"] == 0
