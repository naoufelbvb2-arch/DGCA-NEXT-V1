"""Bounded experimental authority; genuine roots versus labeled components."""

import hashlib
import sqlite3
import subprocess
import sys
from contextlib import closing
from dataclasses import replace
from pathlib import Path

import pytest

from dgca_next.graph.merge_split_analysis import SplitPartition
from dgca_next.learning.completed_event_clock import (
    VerifiedCompletedPrefix,
    _verified_completed_prefix,
)
from dgca_next.learning.native_multi import (
    UnprovenNativeOperator,
    decode_multi_close,
    decode_operator_check,
    encode_multi_close,
)
from dgca_next.persistence.binary_records import decode_record, encode_record
from dgca_next.persistence.native_codec import encode_native_graph
from dgca_next.persistence.production_store import _checkpoint_digest
from dgca_next.persistence.store import RootStore

ROOT = Path(__file__).resolve().parents[1]
MODE = "I4_NATIVE_MULTI_V1"
MIX = (("a", "1"), ("f617", "1"))


def store_at(path, mode=MODE):
    return RootStore(path, repository_root=ROOT, code_revision="a" * 40, execution_mode=mode)


def root(store, identity, features=MIX, repeats=2):
    store.begin(identity)
    for order in range(repeats):
        store.event(identity, order, features)
    return store.end(identity)


def two_births(store):
    for r in range(1, 5):
        close = root(store, r, repeats=1 if r == 1 else 2)
    return close


def test_actual_two_form_batch_and_shared_grow_replay(tmp_path):
    path = tmp_path / "multi.sqlite"
    s = store_at(path)
    assert not s.graph().stored_cells() and not s.graph().synapses()
    result = two_births(s)
    assert result.formed_ids == (0, 1)
    first, second = s.graph().native_assemblies()
    assert first.member_cell_ids == (8200, 8606, 9345)
    assert second.member_cell_ids == (10035, 10926, 11795)
    births = s.graph().native_form_log()
    assert births[0].post_evidence_w_hash == births[1].post_evidence_w_hash
    assert len({b.event_id for b in births}) == 1
    assert result == decode_multi_close(encode_multi_close(result))
    assert s.end(4) == result  # Idempotence, no duplicate IDs/evidence.
    c = root(s, 5, repeats=1)
    assert len(c.mutation_ordinals) == 8
    graph = s.graph()
    for a in graph.native_assemblies():
        assert a.member_cell_ids == (8200, 8606, 9345, 10035, 10926, 11795, 12181)
        assert a.structural_generation == 5 and a.assembly_id in (0, 1)
        for cell in a.member_cell_ids:
            assert graph.member_assemblies(cell) == graph.cell(cell).assembly_ids == {0, 1}
    assert graph.native_form_log() == births
    checks = [decode_operator_check(b) for b in c.operator_checks]
    assert [b["operator"] for b in checks] == ["MERGE", "SPLIT", "SPLIT"]
    assert all(not b["eligible"] for b in checks)
    assert "EMPTY_EXCLUSIVE_SET" in checks[0]["numbers"]["reasons"]
    view, h = s.view(), s.h_bytes()
    s.close()
    raw = path.read_bytes()
    s = store_at(path)
    assert s.view() == view and s.h_bytes() == h and path.read_bytes() == raw
    assert s.inspect_native_lifecycle(5) == c
    assert encode_native_graph(s.graph()) == view.W
    c = root(s, 6, (), 1)
    assert not c.mutation_ordinals and not c.formed_ids
    assert s.view().W == view.W
    s.close()


def test_no_triangle_diagnostic_and_close_version_are_exact(tmp_path):
    s = store_at(tmp_path / "diagnostic.sqlite")
    close = root(s, 1, (), 1)
    assert close.form_reason == "NO_RECIPROCAL_TRIANGLE" and close.close_version == 2
    with pytest.raises(ValueError, match="UNSUPPORTED_NATIVE_MULTI_CLOSE"):
        encode_multi_close(replace(close, close_version=999))
    s.close()


def test_pending_inspection_never_publishes_and_abort_has_no_ids(tmp_path):
    s = store_at(tmp_path / "abort.sqlite")
    for r in (1, 2, 3):
        root(s, r, repeats=1 if r == 1 else 2)
    s.begin(4)
    h_begin = s.h_bytes()
    for order in (0, 1):
        s.event(4, order, MIX)
    before, h = s.view(), s.h_bytes()
    p = s.inspect_pending_native(4)
    assert not p.committed and p.source_kind == "PROVISIONAL_TRUSTED_END_SHADOW"
    assert p.close.formed_ids == (0, 1)
    assert s.inspect_pending_native(4) == p
    assert s.view() == before and s.h_bytes() == h
    assert not s.graph().native_assemblies()
    s.abort(4)
    assert s.h_bytes() == h_begin and not s.graph().native_assemblies()
    assert s.view().completed_closes == 3
    with pytest.raises(ValueError, match="NONEMPTY_OPEN_ROOT_REQUIRED"):
        s.inspect_pending_native(4)
    s.close()


@pytest.mark.parametrize("old_mode", ["I4_NATIVE_FORM_V1", "I4_NATIVE_MAINTAIN_GROW_V1"])
def test_old_schema5_history_keeps_exact_bytes_and_old_replay(tmp_path, old_mode):
    path = tmp_path / "old.sqlite"
    old = store_at(path, old_mode)
    for r in range(1, 5):
        root(old, r, (("a", "1"),), 1 if r == 1 else 2)
    if old_mode == "I4_NATIVE_MAINTAIN_GROW_V1":
        root(old, 5, (("a", "1"),), 1)
    before = old.view()
    history = old._backend._connection.execute(
        "SELECT close_record,w_end FROM p01_roots ORDER BY exposure_id"
    ).fetchall()
    old.close()
    data = path.read_bytes()
    s = store_at(path)
    assert s.view() == before and path.read_bytes() == data
    assert (
        s._backend._connection.execute(
            "SELECT close_record,w_end FROM p01_roots ORDER BY exposure_id"
        ).fetchall()
        == history
    )
    root(s, 6, (("a", "1"),), 1)
    s.close()
    s = store_at(path)
    assert s.view().completed_closes == before.completed_closes + 1
    s.close()
    # Old readers reject the NEW close format; no silent downgrade/rewrite.
    with pytest.raises(ValueError):
        store_at(path, old_mode)


@pytest.mark.parametrize("damage", ["subject", "eligible", "clock", "root", "witness", "birth"])
def test_repaired_checksums_do_not_authorize_forged_multi_close(tmp_path, damage):
    path = tmp_path / "forge.sqlite"
    s = store_at(path)
    two_births(s)
    s.close()
    with closing(sqlite3.connect(path)) as db:
        raw, w, h = db.execute(
            "SELECT close_record,w_end,h_end FROM p01_roots WHERE exposure_id=4"
        ).fetchone()
        c = decode_multi_close(raw)
        if damage in ("subject", "eligible", "clock"):
            checks = list(c.operator_checks)
            doc = decode_operator_check(checks[0])
            if damage == "subject":
                doc["subjects"][0][0] = 99
            elif damage == "eligible":
                doc["eligible"] = True
            else:
                doc["cooldown"][0]["age_completed_events"] = 200
            checks[0] = encode_record(0x4F, 1, doc)
            raw = encode_multi_close(replace(c, operator_checks=tuple(checks)))
        else:
            doc = decode_record(w, 0x57, 5)
            form = doc["forms"][1]
            form[
                {"root": "exposure_id", "witness": "event_id", "birth": "post_evidence_w_hash"}[
                    damage
                ]
            ] = "0" * 64 if damage == "birth" else 99
            w = encode_record(0x57, 5, doc)
            raw = encode_multi_close(replace(c, graph_hash=hashlib.sha256(w).hexdigest()))
        with db:
            db.execute("UPDATE p01_metadata SET w_state=?", (w,))
            db.execute(
                "UPDATE p01_roots SET close_record=?,w_end=?,close_hash=? WHERE exposure_id=4",
                (raw, w, _checkpoint_digest(raw, h, w)),
            )
    with pytest.raises(ValueError):
        store_at(path)


@pytest.mark.parametrize("stage", ["BEFORE_COMMIT", "AFTER_COMMIT"])
def test_real_multi_form_process_exit_is_atomic(tmp_path, stage):
    path = tmp_path / "crash.sqlite"
    s = store_at(path)
    for r in (1, 2, 3):
        root(s, r, repeats=1 if r == 1 else 2)
    s.begin(4)
    for order in (0, 1):
        s.event(4, order, MIX)
    before, h = s.view(), s.h_bytes()
    s.close()
    script = """
import os,sys
from pathlib import Path
from dgca_next.persistence.store import RootStore
s=RootStore(Path(sys.argv[1]),repository_root=Path.cwd(),code_revision='a'*40,execution_mode='I4_NATIVE_MULTI_V1')
def stop(stage):
    if stage==sys.argv[2]: os._exit(47)
s.end(4,hook=stop)
"""
    proc = subprocess.run([sys.executable, "-c", script, str(path), stage], cwd=ROOT)
    assert proc.returncode == 47
    s = store_at(path)
    assert s.h_bytes() == h
    if stage == "BEFORE_COMMIT":
        assert s.view() == before and s.root(4).status == "OPEN"
        assert not s.graph().native_assemblies()
    else:
        assert s.root(4).status == "COMPLETED"
        assert s.end(4).formed_ids == (0, 1)
    s.close()


def test_end_exception_rolls_back_all_multi_evidence_and_ids(tmp_path):
    s = store_at(tmp_path / "exception.sqlite")
    for r in (1, 2, 3):
        root(s, r, repeats=1 if r == 1 else 2)
    s.begin(4)
    for order in (0, 1):
        s.event(4, order, MIX)
    before, h = s.view(), s.h_bytes()

    def fail(stage):
        if stage == "BEFORE_COMMIT":
            raise RuntimeError("injected transaction exception")

    with pytest.raises(RuntimeError, match="injected transaction exception"):
        s.end(4, hook=fail)
    assert s.view() == before and s.h_bytes() == h
    assert s.end(4).formed_ids == (0, 1)
    s.close()


def test_real_completed_event_prefix_199_200_not_root_count(tmp_path):
    s = store_at(tmp_path / "clock.sqlite")
    root(s, 1, (), 1)
    c = root(s, 2, (), 5)
    assert c.event_clock == 6
    prefix = _verified_completed_prefix(s._backend._connection, c, decode_multi_close, replay=True)
    assert prefix.cooldown(0, 1).age_completed_events == 5
    s.begin(3)
    h = s.h_bytes()
    for n in range(3):
        s.event(3, n, ())
    s.abort(3)
    assert s.h_bytes() == h
    c = root(s, 4, (), 194)
    p = _verified_completed_prefix(s._backend._connection, c, decode_multi_close, replay=True)
    assert c.event_clock == 200 and c.close_serial == 3
    assert p.cooldown(0, 1).age_completed_events == 199 and not p.cooldown(0, 1).eligible
    c = root(s, 5, (), 1)
    p = _verified_completed_prefix(s._backend._connection, c, decode_multi_close, replay=True)
    assert c.event_clock == 201 and c.close_serial == 4
    assert p.cooldown(0, 1).age_completed_events == 200 and p.cooldown(0, 1).eligible
    assert p.cooldown(0, None).status == "NEVER_EDITED"
    assert p.cooldown(0, None, edited_this_end=frozenset({0})).status == "SAME_END_EDIT_BLOCKED"
    with pytest.raises(ValueError, match="MISSING_COOLDOWN_CLOCK_PROVENANCE"):
        p.cooldown(0, 999)
    with pytest.raises(ValueError, match="UNVERIFIED_COMPLETED_EVENT_PREFIX"):
        VerifiedCompletedPrefix(5, 4, 201, ((1, 1),))
    before = s.view()
    assert s.end(5) == c and s.view() == before
    s.close()
    s = store_at(tmp_path / "clock.sqlite")
    assert s.view() == before
    s.close()
    # Reference close 1 is genuine; no Assembly edit is claimed in this test.


@pytest.mark.parametrize("operator", ["MERGE", "SPLIT"])
def test_component_injected_positive_operator_never_silently_publishes(
    tmp_path, monkeypatch, operator
):
    # Negative fault injection only. Genuine roots supply the identities;
    # the patched scalar predicate is explicitly NOT production eligibility.
    import dgca_next.learning.native_multi as module

    s = store_at(tmp_path / "refuse.sqlite")
    two_births(s)
    s.begin(5)
    s.event(5, 0, MIX)
    before, h = s.view(), s.h_bytes()
    if operator == "MERGE":
        original = module.analyze_merge
        monkeypatch.setattr(
            module, "analyze_merge", lambda *a, **k: replace(original(*a, **k), reasons=())
        )
    else:
        original = module.analyze_split
        monkeypatch.setattr(
            module,
            "analyze_split",
            lambda *a, **k: replace(
                original(*a, **k),
                reasons=(),
                best=SplitPartition(a[0][:3], a[0][3:], 0.0, 0.0, ((), ())),
            ),
        )
    with pytest.raises(UnprovenNativeOperator, match=f"{operator}_WRITER_NOT_PROVEN"):
        s.end(5)
    assert s.view() == before and s.h_bytes() == h and s.root(5).status == "OPEN"
    s.abort(5)
    s.close()
