"""Checkpoint reporter accepts extra descriptive data, never changed state."""

import pytest
from i4_r04_operator_execution import assert_checkpoint


def test_checkpoint_comparison_preserves_all_five_authoritative_fields():
    actual = dict(W_sha256="w", H_sha256="h", R_sha256="r", completed_closes=3, open_root=4)
    expected = actual | {"assemblies": ["descriptive-only-in-this-component"]}
    assert_checkpoint(actual, expected)
    for key, bad in (
        ("W_sha256", "changed"),
        ("H_sha256", "changed"),
        ("R_sha256", "changed"),
        ("completed_closes", 4),
        ("open_root", None),
    ):
        with pytest.raises(AssertionError):
            assert_checkpoint(actual | {key: bad}, expected)
