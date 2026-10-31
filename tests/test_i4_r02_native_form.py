"""Production schema-5 FORM, durability and mode separation; no fixture births."""

import hashlib
import sqlite3
import subprocess
import sys
from contextlib import closing
from dataclasses import FrozenInstanceError, replace
from pathlib import Path

import pytest

from dgca_next.contracts import Region, SynapseScope
from dgca_next.dynamics.session import FeatureEvent, read_only_episode
from dgca_next.dynamics.state import GraphSnapshot
from dgca_next.graph.native_assembly import NativeAssemblyRecord, _assembly_record, _next_native_id
from dgca_next.graph.synapse import SynapseState
from dgca_next.learning.native_form import decode_native_close, encode_native_close
from dgca_next.persistence.binary_records import decode_record, encode_record
from dgca_next.persistence.native_codec import decode_native_graph, encode_native_graph
from dgca_next.persistence.production_store import _checkpoint_digest
from dgca_next.persistence.store import RootStore

ROOT = Path(__file__).resolve().parents[1]
MODE = "I4_NATIVE_FORM_V1"


def native(path):
    return RootStore(path, repository_root=ROOT, code_revision="a" * 40, execution_mode=MODE)


def roots(store, end=4):
    closes = []
    for root in range(1, end + 1):
        store.begin(root)
        for order in range(1 if root == 1 else 2):
            store.event(root, order, (("a", "1"),))
        closes.append(store.end(root))
    return closes


def test_first_native_form_is_real_same_end_evidence_and_persistent(tmp_path):
    path = tmp_path / "native.sqlite"
    store = native(path)
    assert not store.graph().stored_cells() and not store.graph().synapses()
    assert not store.graph().native_assemblies()
    closes = roots(store, 3)
    assert all(not c.formed_ids and c.form_reason == "NO_RECIPROCAL_TRIANGLE" for c in closes)
    assert all(s.state is SynapseState.CANDIDATE for s in store.graph().synapses())
    store.begin(4)
    first = store.event(4, 0, (("a", "1"),))
    store.event(4, 1, (("a", "1"),))
    assert not store.graph().native_assemblies()
    assert all(s.state is SynapseState.CANDIDATE for s in store.graph().synapses())
    result = store.end(4)
    assert result.form_reason == "FORMED" and result.formed_ids == (0,)
    graph = store.graph()
    (assembly,) = graph.native_assemblies()
    assert assembly.assembly_id == 0 and assembly.region is Region.LANGUAGE
    assert assembly.member_cell_ids == (8606, 9345, 11795) and assembly.status == "LIVE"
    assert assembly.structural_generation == 1 and assembly.birth_close_serial == 4
    assert (
        assembly.last_mutation_close_serial == 4 and assembly.last_merge_split_close_serial is None
    )
    assert not assembly.fixture_only and graph._state.assembly_high_watermarks[Region.LANGUAGE] == 0
    for member in assembly.member_cell_ids:
        assert graph.cell(member).assembly_ids == graph.member_assemblies(member) == frozenset({0})
    assert not graph.cell(12181).assembly_ids
    local = [s for s in graph.synapses() if s.key.scope is SynapseScope.LOCAL]
    assert len(local) == 12 and all(s.state is SynapseState.CONSOLIDATED for s in local)
    assert all(s.E_ext == 3 and s.external_root_count == 3 for s in local)
    (proof,) = graph.native_form_log()
    assert (proof.exposure_id, proof.event_id, proof.event_order) == (4, first.event_id, 0)
    assert proof.completed_close_serial == 4 and proof.observation_digest == first.digest
    assert all(w[1] == 1_000_000 and w[2] == 0 and w[3] >= w[4] for w in proof.witnesses)
    before, h = store.view(), store.h_bytes()
    assert store.end(4) == result and store.view() == before
    diagnostic = store.inspect_form_eligibility(4)
    assert diagnostic.reason == "FORM_ELIGIBLE"
    assert diagnostic.source_w_hash == proof.post_evidence_w_hash
    assert store.view() == before
    snapshot = GraphSnapshot.capture(graph)
    from dgca_next.learning.homeostasis_profile import LanguageHomeostasis

    homeostasis = LanguageHomeostasis.decode(h).materialize(snapshot.committed_ids)
    traces = read_only_episode(snapshot, homeostasis, (FeatureEvent((("a", "1"),)),), session_id=7)
    assert traces[0].synchronous and store.view() == before
    with pytest.raises(FrozenInstanceError):
        assembly.status = "ARCHIVED"
    store.close()
    store = native(path)
    assert store.view() == before and store.h_bytes() == h
    assert store.graph().native_assemblies() == (assembly,)
    assert store.graph().native_form_log() == (proof,)
    assert store.end(4) == result
    store.close()


def test_no_qualified_root_or_abort_publishes_an_assembly(tmp_path):
    store = native(tmp_path / "abort.sqlite")
    roots(store, 3)
    before = store.view()
    store.begin(4)
    store.event(4, 0, (("a", "1"),))
    store.event(4, 1, (("a", "1"),))
    assert store.pending_proposals(4) and not store.graph().native_assemblies()
    store.abort(4)
    assert store.view().W == before.W and store.view().homeostasis == before.homeostasis
    assert store.view().completed_closes == 3 and not store.graph().native_assemblies()
    store.begin(5)
    store.event(5, 0, ())
    result = store.end(5)
    assert not result.formed_ids and not store.graph().native_assemblies()
    assert store.graph()._state.assembly_high_watermarks[Region.LANGUAGE] == -1
    store.close()


def test_native_mode_blocks_recycling_and_later_unimplemented_end_atomically(tmp_path):
    store = native(tmp_path / "containment.sqlite")
    roots(store, 4)
    before = store.view()
    with pytest.raises(ValueError, match="I4_REWIRING_CONFLICT"):
        store.request_recycling(4, 1, 8606, 0)
    assert store.view() == before
    store.begin(5)
    store.event(5, 0, (("a", "1"),))
    pre_end, h = store.view(), store.h_bytes()
    with pytest.raises(ValueError, match="I4_UNIMPLEMENTED_MAINTAIN_GROW"):
        store.end(5)
    assert store.view() == pre_end and store.h_bytes() == h
    assert store.root(5).status == "OPEN" and store.view().completed_closes == 4
    store.abort(5)
    assert (
        store.view().W == before.W
        and store.h_bytes()
        == store._backend._connection.execute(
            "SELECT h_begin FROM p01_roots WHERE exposure_id=5"
        ).fetchone()[0]
    )
    assert store.end(4).formed_ids == (0,)
    store.close()


@pytest.mark.parametrize("version", [3, 4])
def test_native_loader_rejects_old_database_without_modification(tmp_path, version):
    path = tmp_path / "old.sqlite"
    store = RootStore(path, repository_root=ROOT, code_revision="a" * 40)
    roots(store, 1)
    before_view = store.view()
    store.close()
    if version == 3:
        with closing(sqlite3.connect(path)) as connection:
            with connection:
                connection.execute("DROP TABLE p04_requests")
                connection.execute("UPDATE p01_metadata SET schema_version=3")
    before = path.read_bytes()
    with pytest.raises(ValueError, match="UNSUPPORTED_PRODUCTION_SCHEMA"):
        native(path)
    assert path.read_bytes() == before
    if version == 4:
        store = RootStore(path, repository_root=ROOT, code_revision="a" * 40)
        assert store.view() == before_view
        store.close()


def test_legacy_loader_does_not_silently_open_schema5(tmp_path):
    path = tmp_path / "schema5.sqlite"
    store = native(path)
    roots(store, 1)
    store.close()
    before = path.read_bytes()
    with pytest.raises(ValueError, match="UNSUPPORTED_PRODUCTION_SCHEMA"):
        RootStore(path, repository_root=ROOT, code_revision="a" * 40)
    assert path.read_bytes() == before


@pytest.mark.parametrize("phase", ["BEFORE_COMMIT", "AFTER_COMMIT"])
def test_native_form_process_crash_recovers_whole_root_once(tmp_path, phase):
    path = tmp_path / "crash.sqlite"
    store = native(path)
    roots(store, 3)
    store.begin(4)
    store.event(4, 0, (("a", "1"),))
    store.event(4, 1, (("a", "1"),))
    before = store.view()
    store.close()

    script = """
import os, sys
from pathlib import Path
from dgca_next.persistence.store import RootStore
s=RootStore(Path(sys.argv[1]),repository_root=Path(sys.argv[2]),code_revision='a'*40,execution_mode='I4_NATIVE_FORM_V1')
def crash(stage):
    if stage == sys.argv[3]: os._exit(31)
s.end(4,hook=crash)
"""
    result = subprocess.run([sys.executable, "-c", script, str(path), str(ROOT), phase])
    assert result.returncode == 31
    store = native(path)
    if phase == "BEFORE_COMMIT":
        assert store.view() == before and not store.graph().native_assemblies()
    else:
        assert store.root(4).status == "COMPLETED" and len(store.graph().native_assemblies()) == 1
    result = store.end(4)
    assert store.end(4) == result and result.formed_ids == (0,)
    assert store.view().completed_closes == 4 and len(store.graph().native_form_log()) == 1
    store.close()


@pytest.mark.parametrize("phase", ["BEFORE_COMMIT", "AFTER_COMMIT"])
def test_native_abort_process_crash_never_consumes_identity(tmp_path, phase):
    path = tmp_path / "abort-crash.sqlite"
    store = native(path)
    roots(store, 3)
    store.begin(4)
    h_begin = store.h_bytes()
    store.event(4, 0, (("a", "1"),))
    store.event(4, 1, (("a", "1"),))
    before = store.view()
    store.close()
    script = """
import os, sys
from pathlib import Path
from dgca_next.persistence.store import RootStore
s=RootStore(Path(sys.argv[1]),repository_root=Path(sys.argv[2]),code_revision='a'*40,execution_mode='I4_NATIVE_FORM_V1')
def crash(stage):
    if stage == sys.argv[3]: os._exit(31)
s.abort(4,hook=crash)
"""
    process = subprocess.run([sys.executable, "-c", script, str(path), str(ROOT), phase])
    assert process.returncode == 31
    store = native(path)
    if phase == "BEFORE_COMMIT":
        assert store.view() == before
        store.abort(4)
    assert store.h_bytes() == h_begin and store.view().completed_closes == 3
    assert not store.graph().native_assemblies()
    assert store.graph()._state.assembly_high_watermarks[Region.LANGUAGE] == -1
    store.begin(5)
    store.event(5, 0, (("a", "1"),))
    store.event(5, 1, (("a", "1"),))
    assert store.end(5).formed_ids == (0,)
    assert store.graph().native_assemblies()[0].birth_close_serial == 4
    store.close()


@pytest.mark.parametrize(
    "damage",
    ["members", "reverse", "generation", "watermark", "missing_form", "candidate", "one_way"],
)
def test_native_codec_rejects_corrupt_structural_records(tmp_path, damage):
    store = native(tmp_path / "codec.sqlite")
    roots(store, 4)
    raw = store.view().W
    store.close()
    document = decode_record(raw, 0x57, 5)
    if damage == "members":
        document["cells_memberships"][0][1] = []
    elif damage == "reverse":
        document["membership_reverse"] = []
    elif damage == "generation":
        document["assemblies"][0][3] = 2
    elif damage == "watermark":
        document["high_watermarks"][0][1] = -1
    elif damage == "missing_form":
        document["forms"] = []
    else:
        base = decode_record(document["base"], 0x57, 2)
        row = next(r for r in base["links"] if r[0] == [8606, 9345, "LOCAL"])
        if damage == "candidate":
            row[2] = "CANDIDATE"
        else:
            base["links"].remove(row)
            next(r for r in base["outgoing"] if r[0] == 8606)[1].remove(row[0])
        document["base"] = encode_record(0x57, 2, base)
    with pytest.raises(ValueError):
        decode_native_graph(encode_record(0x57, 5, document))


def test_cold_replay_rejects_forged_birth_even_with_repaired_checksums(tmp_path):
    path = tmp_path / "journal.sqlite"
    store = native(path)
    roots(store, 4)
    store.close()
    with closing(sqlite3.connect(path)) as connection:
        old_close, h, raw = connection.execute(
            "SELECT close_record,h_end,w_end FROM p01_roots WHERE exposure_id=4"
        ).fetchone()
        document = decode_record(raw, 0x57, 5)
        document["forms"][0]["exposure_id"] = 99
        damaged = encode_record(0x57, 5, document)
        # The physical codec alone cannot authenticate a root journal. Repair
        # checksums here to require independent historical FORM re-derivation.
        assert encode_native_graph(decode_native_graph(damaged)) == damaged
        close = replace(
            decode_native_close(old_close), graph_hash=hashlib.sha256(damaged).hexdigest()
        )
        encoded = encode_native_close(close)
        with connection:
            connection.execute("UPDATE p01_metadata SET w_state=?", (damaged,))
            connection.execute(
                "UPDATE p01_roots SET w_end=?,close_record=?,close_hash=? WHERE exposure_id=4",
                (damaged, encoded, _checkpoint_digest(encoded, h, damaged)),
            )
    with pytest.raises(ValueError, match="INVALID_CLOSE_CHECKPOINT"):
        native(path)


def test_public_native_record_constructor_cannot_mint_authority():
    with pytest.raises(ValueError, match="UNVERIFIED_NATIVE_ASSEMBLY_CONSTRUCTION"):
        NativeAssemblyRecord(0, Region.LANGUAGE, (8606, 9345, 11795), 1, 4, 4, None, "LIVE")


def test_multiple_real_disjoint_seeds_fail_closed_at_lab_boundary(tmp_path):
    store = native(tmp_path / "two-cohorts.sqlite")
    store.begin(1)
    store.event(1, 0, (("a", "1"),))
    store.event(1, 1, (("ab", "1"),), boundary=True)
    store.end(1)
    for root in (2, 3, 4):
        store.begin(root)
        store.event(root, 0, (("a", "1"),))
        store.event(root, 1, (("a", "1"),))
        store.event(root, 2, (("ab", "1"),), boundary=True)
        store.event(root, 3, (("ab", "1"),))
        if root < 4:
            store.end(root)
    before = store.view()
    with pytest.raises(ValueError, match="I4_FIRST_FORM_LAB_SCOPE_EXCEEDED"):
        store.end(4)
    assert store.view() == before and not store.graph().native_assemblies()
    assert store.view().completed_closes == 3
    store.abort(4)
    store.close()


def test_component_archived_identity_is_never_reused():
    # Administrative simulation only; no production archive operation exists.
    archived = _assembly_record(0, Region.LANGUAGE, (8606, 9345, 11795), 2, 4, 5, None, "ARCHIVED")
    assert _next_native_id(0, {0: archived}) == 1
    with pytest.raises(ValueError, match="HIGH_WATERMARK"):
        _next_native_id(-1, {0: archived})


@pytest.mark.parametrize("damage", ["witness", "competing_recycling"])
def test_untrusted_open_root_cannot_publish_native_form(tmp_path, damage):
    path = tmp_path / "untrusted.sqlite"
    store = native(path)
    roots(store, 3)
    store.begin(4)
    store.event(4, 0, (("a", "1"),))
    store.event(4, 1, (("a", "1"),))
    before = store.view()
    with closing(sqlite3.connect(path)) as connection:
        with connection:
            if damage == "witness":
                connection.execute("UPDATE p01_events SET record=? WHERE event_id=5", (b"invalid",))
            else:
                connection.execute("INSERT INTO p04_requests VALUES (4,1,8606,0,NULL)")
    with pytest.raises(ValueError, match="EVENT_CHECKPOINT_HASH_MISMATCH|I4_REWIRING_CONFLICT"):
        store.end(4)
    with closing(sqlite3.connect(path)) as connection:
        after_w, serial, opened = connection.execute(
            "SELECT w_state,completed_closes,open_root FROM p01_metadata"
        ).fetchone()
    assert after_w == before.W and serial == 3 and opened == 4
    assert not decode_native_graph(after_w).native_assemblies()
    store.close()
