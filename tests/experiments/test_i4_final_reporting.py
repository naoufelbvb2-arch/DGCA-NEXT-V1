"""Experiment interpreter and real serialized-proof reporting regressions."""

import base64
import json
import subprocess
import sys
from pathlib import Path

from i4_final_second_operator import target_checks

from dgca_next.learning.native_operators import decode_operator_close

ROOT = Path(__file__).resolve().parents[2]


def test_final_trial_cli_is_valid_in_the_actual_python_interpreter():
    result = subprocess.run(
        [sys.executable, str(ROOT / "tests/experiments/i4_final_second_operator.py"), "--help"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert "--source-receipt" in result.stdout and not result.stderr


def test_target_report_keeps_actual_id_zero_and_serialized_physics_distinct():
    receipt = json.loads(
        (ROOT / "docs/implementation/evidence/i4-r04-autonomous/F05-r3-publish.json").read_text(
            encoding="utf8"
        )
    )
    close = decode_operator_close(base64.b64decode(receipt["close_base64"], validate=True))
    checks = target_checks(close)
    split = next(c for c in checks if c["operator"] == "SPLIT")
    assert split["subjects"] == [[0, 12]] and split["eligible"]
    assert split["numbers"]["best"]["cross_mean"] == 0.0
    assert not split["numbers"]["reasons"]
    assert all(c["subjects"] != [[1, 12]] for c in checks)
    merge = next(c for c in checks if c["operator"] == "MERGE")
    assert not merge["eligible"] and "EMPTY_EXCLUSIVE_SET" in merge["numbers"]["reasons"]
