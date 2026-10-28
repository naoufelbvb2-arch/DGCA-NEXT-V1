"""R01 transaction skeleton tests. No test claims production EVENT or learning."""

import sqlite3
import struct
import subprocess
import sys
from contextlib import closing
from pathlib import Path

import pytest

from dgca_next.contracts import Region
from dgca_next.dynamics.numeric import SpecBlocked
from dgca_next.dynamics.state import Homeostasis
from dgca_next.persistence.codec import decode_homeostasis, encode_homeostasis
from dgca_next.persistence.store import EMPTY_W, R_COLD, RootStore

ROOT = Path(__file__).resolve().parents[1]
REVISION = "a" * 40  # Declared test identifier, not a claimed Git commit.


def h_fixture():
    # Explicit synthetic state for exercising storage only, not an initial policy.
    return Homeostasis({8192: 1.0}, {8192: 0.25}, {Region.LANGUAGE: 0.2}, {Region.LANGUAGE: 0.03})


def store(path, *, initial=None, revision=REVISION):
    return RootStore(
        path, repository_root=ROOT, code_revision=revision, initial_homeostasis=initial
    )


def test_versioned_binary_codec_independent_golden():
    source = h_fixture()
    items = (
        struct.pack(">II", 1, 8192)
        + struct.pack(">d", 1.0)
        + struct.pack(">II", 1, 8192)
        + struct.pack(">d", 0.25)
        + struct.pack(">IBd", 1, 2, 0.2)
        + struct.pack(">IBd", 1, 2, 0.03)
    )
    expected = b"\x48\x01" + struct.pack(">I", len(items)) + items
    assert encode_homeostasis(source) == expected
    assert decode_homeostasis(expected) == source
    assert encode_homeostasis(decode_homeostasis(expected)) == expected


@pytest.mark.parametrize(
    "damage", ["version", "truncate", "length", "trailing", "nonfinite", "negative_zero"]
)
def test_codec_rejects_corrupted_or_noncanonical_records(damage):
    record = bytearray(encode_homeostasis(h_fixture()))
    if damage == "version":
        record[1] = 2
    elif damage == "truncate":
        del record[-1:]
    elif damage == "length":
        record[5] ^= 1
    elif damage == "trailing":
        record.extend(b"x")
    elif damage == "nonfinite":
        record[14:22] = struct.pack(">d", float("nan"))
    else:
        record[14:22] = struct.pack(">d", -0.0)
    with pytest.raises(ValueError):
        decode_homeostasis(bytes(record))


def test_begin_abort_cold_exclusive_monotonic_and_retry(tmp_path):
    db = tmp_path / "roots.sqlite"
    initial = h_fixture()
    engine = store(db, initial=initial)
    assert engine.view().high_watermark == -1
    assert engine.view().runtime == R_COLD and engine.view().W == EMPTY_W
    first = engine.begin(4)
    assert first.status == "OPEN" and first.next_order == 0 and first.H_begin == initial
    assert engine.begin(4) == first
    with pytest.raises(ValueError, match="EXPOSURE_ALREADY_OPEN"):
        engine.begin(5)
    with pytest.raises(ValueError, match="READ_ONLY_FORBIDDEN"):
        engine.assert_read_only_allowed()
    assert engine.abort(4).status == "ABORTED"
    engine.assert_read_only_allowed()
    with pytest.raises(ValueError, match="ROOT_ID_REUSED"):
        engine.begin(4)
    second = engine.begin(9)
    assert engine.abort(4).status == "ABORTED"  # Cannot disturb the later root.
    assert engine.view().open_root == 9 and engine.root(9) == second
    assert engine.view().homeostasis == initial and engine.view().completed_closes == 0
    engine.close()
    restored = store(db)
    assert restored.view().open_root == 9 and restored.view().high_watermark == 9
    assert restored.root(4).status == "ABORTED"
    restored.close()


def test_two_connections_share_the_same_persisted_open_lock(tmp_path):
    db = tmp_path / "roots.sqlite"
    first = store(db, initial=h_fixture())
    second = store(db)
    first.begin(3)
    with pytest.raises(ValueError, match="EXPOSURE_ALREADY_OPEN"):
        second.begin(4)
    assert second.view().open_root == 3
    first.abort(3)
    second.begin(4)
    assert first.view().open_root == 4
    second.abort(4)
    first.close()
    second.close()


def test_event_and_end_are_fail_closed_without_changing_checkpoint(tmp_path):
    engine = store(tmp_path / "roots.sqlite", initial=h_fixture())
    engine.begin(7)
    before, root = engine.view(), engine.root(7)
    with pytest.raises(SpecBlocked, match="I3-S01"):
        engine.event(7, 0, tuple((f, "1") for f in ("a", "ab", "c", "d")))
    with pytest.raises(SpecBlocked, match="I3-S02"):
        engine.event(7, 0, (("a", "1"),))
    with pytest.raises(SpecBlocked, match="I3-R02"):
        engine.event(7, 0, ())
    with pytest.raises(ValueError, match="EVENT_ORDER_MISMATCH"):
        engine.event(7, 1, (("a", "1"),))
    with pytest.raises(ValueError):
        engine.event(7, 0, (("a", "NaN"),))
    with pytest.raises(SpecBlocked, match="I3-R03"):
        engine.end(7)
    assert engine.view() == before and engine.root(7) == root
    engine.close()


@pytest.mark.parametrize("operation", ["begin", "abort"])
def test_exception_before_commit_rolls_back_entire_transition(tmp_path, operation):
    engine = store(tmp_path / "roots.sqlite", initial=h_fixture())
    if operation == "abort":
        engine.begin(10)
    before = engine.view()

    def fail(stage):
        if stage == "BEFORE_COMMIT":
            raise RuntimeError("injected")

    with pytest.raises(RuntimeError, match="injected"):
        getattr(engine, operation)(10, hook=fail)
    assert engine.view() == before
    assert engine.root(10) is None if operation == "begin" else engine.root(10).status == "OPEN"
    engine.close()


@pytest.mark.parametrize("operation", ["begin", "abort"])
@pytest.mark.parametrize("stage", ["BEFORE_COMMIT", "AFTER_COMMIT"])
def test_process_crash_recovers_only_pre_or_post_transition(tmp_path, operation, stage):
    db = tmp_path / "roots.sqlite"
    engine = store(db, initial=h_fixture())
    if operation == "abort":
        engine.begin(10)
    engine.close()
    script = """
import os, sys
from pathlib import Path
from dgca_next.persistence.store import RootStore
s=RootStore(Path(sys.argv[1]), repository_root=Path(sys.argv[2]), code_revision='a'*40)
def crash(stage):
    if stage == sys.argv[4]: os._exit(71)
getattr(s,sys.argv[3])(10,hook=crash)
"""
    result = subprocess.run(
        [sys.executable, "-c", script, str(db), str(ROOT), operation, stage], check=False
    )
    assert result.returncode == 71
    recovered = store(db)
    status = recovered.root(10)
    if operation == "begin" and stage == "BEFORE_COMMIT":
        assert status is None and recovered.view().high_watermark == -1
    elif operation == "begin" or stage == "BEFORE_COMMIT":
        assert status.status == "OPEN" and recovered.view().open_root == 10
    else:
        assert status.status == "ABORTED" and recovered.view().open_root is None
    assert recovered.view().homeostasis == h_fixture()
    assert recovered.view().runtime == R_COLD and recovered.view().completed_closes == 0
    recovered.close()


@pytest.mark.parametrize(
    "column,value",
    [
        ("schema_version", 2),
        ("config_hash", "bad"),
        ("core_hash", "bad"),
        ("lla_hash", "bad"),
        ("code_revision", "bad"),
        ("latent_version", "bad"),
        ("graph_hash", "bad"),
        ("r_state", b"bad"),
        ("h_state", b"bad"),
    ],
)
def test_restore_rejects_corrupted_metadata(tmp_path, column, value):
    db = tmp_path / "roots.sqlite"
    engine = store(db, initial=h_fixture())
    engine.close()
    with closing(sqlite3.connect(db)) as connection:
        with connection:
            connection.execute(f"UPDATE metadata SET {column}=? WHERE id=1", (value,))
    with pytest.raises(ValueError):
        store(db)


def test_explicit_initial_H_and_code_identity_required(tmp_path):
    db = tmp_path / "roots.sqlite"
    with pytest.raises(ValueError, match="EXPLICIT_INITIAL_H_REQUIRED"):
        store(db)
    with pytest.raises(ValueError, match="INVALID_CODE_REVISION"):
        store(db, initial=h_fixture(), revision="unversioned")
    engine = store(db, initial=h_fixture())
    engine.close()
    with pytest.raises(ValueError, match="STORE_IDENTITY_MISMATCH"):
        store(db, revision="b" * 40)
