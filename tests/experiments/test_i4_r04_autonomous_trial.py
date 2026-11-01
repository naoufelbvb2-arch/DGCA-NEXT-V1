"""Production trace/report regressions, including true twelve-seed deferral."""

import json

from i4_r04_autonomous_trial import curriculum, json_default


def test_two_live_report_is_serializable_and_cold_replayable(tmp_path):
    trace = curriculum(tmp_path / "multi.sqlite", "a" * 40, "F02")
    document = json.loads(json.dumps(trace, default=json_default))
    assert document["roots"][3]["formed_ids"] == [0, 1]
    assert document["recovery"]["cold_process_replay_exact"]
    assert len(document["final"]["state"]["assemblies"]) == 2
    assert not document["final"]["automatic_recycling"]


def test_real_twelve_seed_cap_and_next_root_deferral(tmp_path):
    trace = curriculum(tmp_path / "cap.sqlite", "a" * 40, "F04")
    assert trace["roots"][3]["formed_ids"] == tuple(range(12))
    assert trace["roots"][4]["formed_ids"] == (12,)
    assert len(trace["selected_features"]) == 13
    forms = trace["final"]["forms"]
    assert forms[-1]["exposure_id"] == 5 and forms[-1]["completed_close_serial"] == 5
    assert all(f["exposure_id"] == 4 for f in forms[:-1])
    assert len(trace["final"]["state"]["assemblies"]) == 13
    assert trace["recovery"]["cold_process_replay_exact"]
