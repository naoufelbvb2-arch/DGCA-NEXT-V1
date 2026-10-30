"""Production request staging and transaction controls; no fixture graph."""

import sqlite3
import subprocess
import sys
from contextlib import closing
from pathlib import Path

import pytest

from dgca_next.persistence.store import RootStore

ROOT = Path(__file__).resolve().parents[1]


def _store(path):
    return RootStore(path, repository_root=ROOT, code_revision="a" * 40)


def _prepare(path):
    store = _store(path)
    store.begin(1)
    born = store.event(1, 0, (("a", "1"),)).born
    store.end(1)
    owner, target = born[:2]
    slot = next(s.index for s in store.graph().latent_slots(owner) if s.target_id == target)
    return store, owner, slot


def test_request_is_restricted_durable_and_abort_has_no_rewire(tmp_path):
    path = tmp_path / "requests.sqlite"
    store, owner, slot = _prepare(path)
    with pytest.raises(ValueError, match="EXPOSURE_NOT_OPEN"):
        store.request_recycling(1, 0, owner, slot)
    store.begin(2)
    h_begin = store.h_bytes()
    with pytest.raises(ValueError, match="STALE_TRIGGER_EVENT"):
        store.request_recycling(2, 0, owner, slot)
    store.event(2, 0, (("a", "0.2"),))
    before = store.view()
    store.request_recycling(2, 0, owner, slot)
    store.request_recycling(2, 0, owner, slot)
    assert store.view() == before
    with pytest.raises(ValueError, match="CONFLICTING_RECYCLING_REQUEST"):
        store.request_recycling(2, 0, owner, 6)
    store.close()
    store = _store(path)
    assert store.recycling_request(2) == (0, owner, slot, None)
    assert store.view() == before
    store.abort(2)
    assert store.recycling_request(2)[-1] == "ABORTED"
    assert store.view().W == before.W and store.h_bytes() == h_begin
    assert not store.graph().recycling_log()
    store.close()


@pytest.mark.parametrize("stage", ["BEFORE_COMMIT", "AFTER_COMMIT"])
def test_end_failure_is_atomic_and_retry_idempotent(tmp_path, stage):
    path = tmp_path / "failure.sqlite"
    store, owner, slot = _prepare(path)
    store.begin(2)
    store.event(2, 0, (("a", "0.2"),))
    store.request_recycling(2, 0, owner, slot)
    before = store.view()

    def fail(name):
        if name == stage:
            raise RuntimeError(name)

    with pytest.raises(RuntimeError, match=stage):
        store.end(2, hook=fail)
    store.close()
    store = _store(path)
    if stage == "BEFORE_COMMIT":
        assert store.view() == before
        assert store.recycling_request(2)[-1] is None
    else:
        assert store.root(2).status == "COMPLETED"
    result = store.end(2)
    assert result.close_serial == 2
    assert store.end(2) == result and store.view().completed_closes == 2
    assert store.recycling_request(2)[-1] == "CONFIRMATION_WINDOW_NOT_ELAPSED"
    assert not store.graph().recycling_log()
    store.close()


def test_fixed_and_stale_requests_refuse_without_rewiring(tmp_path):
    store, owner, slot = _prepare(tmp_path / "refusals.sqlite")
    store.begin(2)
    store.event(2, 0, (("a", "0.2"),))
    store.request_recycling(2, 0, owner, 6)
    fixed_before = store.graph().latent_slots(owner)
    store.end(2)
    assert store.recycling_request(2)[-1] == "RECYCLE_BLOCKED_FIXED"
    assert store.graph().latent_slots(owner) == fixed_before
    store.begin(3)
    store.event(3, 0, (("a", "0.2"),))
    store.request_recycling(3, 0, owner, slot)
    store.event(3, 1, (("a", "0.2"),))
    stale_before = store.graph().latent_slots(owner)
    store.end(3)
    assert store.recycling_request(3)[-1] == "STALE_TRIGGER_EVENT"
    assert store.graph().latent_slots(owner) == stale_before
    store.close()


def test_altered_close_disposition_is_rejected_on_reopen(tmp_path):
    path = tmp_path / "tampered.sqlite"
    store, owner, slot = _prepare(path)
    store.begin(2)
    store.event(2, 0, (("a", "0.2"),))
    store.request_recycling(2, 0, owner, slot)
    store.end(2)
    store.close()
    with closing(sqlite3.connect(path)) as connection:
        with connection:
            connection.execute("UPDATE p04_requests SET disposition='RECYCLED' WHERE exposure_id=2")
    with pytest.raises(ValueError, match="RECYCLING_DISPOSITION_MISMATCH"):
        _store(path)


@pytest.mark.parametrize("stage", ["BEFORE_COMMIT", "AFTER_COMMIT"])
def test_abort_process_crash_preserves_request_and_h_atomicity(tmp_path, stage):
    path = tmp_path / "abort-crash.sqlite"
    store, owner, slot = _prepare(path)
    store.begin(2)
    h_begin = store.h_bytes()
    store.event(2, 0, (("a", "0.2"),))
    store.request_recycling(2, 0, owner, slot)
    before = store.view()
    store.close()
    script = """
import os, sys
from pathlib import Path
from dgca_next.persistence.store import RootStore
s = RootStore(Path(sys.argv[1]), repository_root=Path(sys.argv[2]), code_revision='a' * 40)
def crash(stage):
    if stage == sys.argv[3]:
        os._exit(31)
s.abort(2, hook=crash)
"""
    process = subprocess.run(
        [sys.executable, "-c", script, str(path), str(ROOT), stage], check=False
    )
    assert process.returncode == 31
    store = _store(path)
    if stage == "BEFORE_COMMIT":
        assert store.view() == before and store.recycling_request(2)[-1] is None
        store.abort(2)
    else:
        assert store.root(2).status == "ABORTED"
    assert store.recycling_request(2)[-1] == "ABORTED"
    assert store.h_bytes() == h_begin and store.view().W == before.W
    assert store.view().completed_closes == 1 and not store.graph().recycling_log()
    store.close()
