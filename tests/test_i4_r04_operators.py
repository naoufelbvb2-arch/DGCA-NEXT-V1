"""Operator-capability plumbing and authority refusal; no fixture learning."""

import sqlite3
from contextlib import closing
from dataclasses import replace

import pytest
from test_i4_r04_autonomous import ROOT

from dgca_next.learning.native_operators import (
    OperatorCloseResult,
    decode_operator_close,
    encode_operator_close,
)
from dgca_next.persistence.production_store import _checkpoint_digest
from dgca_next.persistence.store import RootStore

MODE = "I4_NATIVE_OPERATORS_V1"


def operator_store(path):
    return RootStore(path, repository_root=ROOT, code_revision="a" * 40, execution_mode=MODE)


def test_explicit_operator_mode_produces_no_spurious_mutation(tmp_path):
    path = tmp_path / "operator.sqlite"
    s = operator_store(path)
    s.begin(1)
    s.event(1, 0, (("a", "1"),))
    before, h = s.view(), s.h_bytes()
    pending = s.inspect_pending_native(1)
    assert type(pending.close) is OperatorCloseResult and not pending.committed
    assert not pending.close.operator_ordinals
    assert s.view() == before and s.h_bytes() == h
    close = s.end(1)
    assert type(close) is OperatorCloseResult and not close.operator_ordinals
    assert close == pending.close == decode_operator_close(encode_operator_close(close))
    assert not s.graph().native_operator_log()
    with pytest.raises(ValueError, match="ACTUAL_LIVE_NATIVE_ID_REQUIRED"):
        s.inspect_native_cooldown(0)
    before = s.view()
    assert s.end(1) == close and s.view() == before
    s.close()
    data = path.read_bytes()
    s = operator_store(path)
    assert s.view() == before and s.h_bytes() == h and path.read_bytes() == data
    s.close()
    with pytest.raises(ValueError):
        RootStore(
            path, repository_root=ROOT, code_revision="a" * 40, execution_mode="I4_NATIVE_MULTI_V1"
        )


def test_forged_operator_ordinal_is_rejected_after_repaired_hashes(tmp_path):
    path = tmp_path / "forgery.sqlite"
    s = operator_store(path)
    s.begin(1)
    s.event(1, 0, ())
    close = s.end(1)
    s.close()
    forged = encode_operator_close(replace(close, operator_ordinals=(99,)))
    with closing(sqlite3.connect(path)) as db:
        w, h = db.execute("SELECT w_end,h_end FROM p01_roots WHERE exposure_id=1").fetchone()
        with db:
            db.execute(
                "UPDATE p01_roots SET close_record=?,close_hash=? WHERE exposure_id=1",
                (forged, _checkpoint_digest(forged, h, w)),
            )
    with pytest.raises(ValueError):
        operator_store(path)


def test_real_form_grow_and_all_operator_close_versions_replay(tmp_path):
    path = tmp_path / "lifecycle.sqlite"
    s = operator_store(path)
    for root in range(1, 6):
        s.begin(root)
        for order in range(2 if 2 <= root <= 4 else 1):
            s.event(root, order, (("a", "1"),))
        close = s.end(root)
        assert type(close) is OperatorCloseResult and not close.operator_ordinals
    assert s.graph().native_assemblies()[0].member_cell_ids == (8606, 9345, 11795, 12181)
    assert s.graph().native_assemblies()[0].structural_generation == 2
    before, h = s.view(), s.h_bytes()
    s.close()
    s = operator_store(path)
    assert s.view() == before and s.h_bytes() == h
    s.close()
