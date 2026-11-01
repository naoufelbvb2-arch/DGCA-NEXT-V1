"""Real Schema-5 roots and lifecycle recovery; no fixture learning authority."""

import hashlib
import io
import json
import os
import sqlite3
import subprocess
import sys
import tarfile
from contextlib import closing
from dataclasses import FrozenInstanceError, asdict, replace
from pathlib import Path
from types import MappingProxyType

import pytest

from dgca_next.dynamics.session import FeatureEvent, read_only_episode
from dgca_next.dynamics.state import GraphSnapshot
from dgca_next.graph.native_assembly import _next_native_id
from dgca_next.graph.native_mutation import NativeStructuralMutationRecord
from dgca_next.graph.network import SparseNetwork
from dgca_next.learning.homeostasis_profile import LanguageHomeostasis
from dgca_next.learning.native_lifecycle import (
    _native_end,
    decode_lifecycle_close,
    encode_lifecycle_close,
)
from dgca_next.persistence.binary_records import decode_record, encode_record
from dgca_next.persistence.native_codec import decode_native_graph, encode_native_graph
from dgca_next.persistence.production_store import _checkpoint_digest
from dgca_next.persistence.store import RootStore

ROOT = Path(__file__).resolve().parents[1]
MODE = "I4_NATIVE_MAINTAIN_GROW_V1"


def store_at(path, *, mode=MODE, revision="a" * 40):
    return RootStore(path, repository_root=ROOT, code_revision=revision, execution_mode=mode)


def birth(store):
    for root in range(1, 5):
        store.begin(root)
        for order in range(1 if root == 1 else 2):
            store.event(root, order, (("a", "1"),))
        store.end(root)
    return store.graph().native_form_log()


def test_root5_real_grow_and_root6_stable_cold_replay(tmp_path):
    path = tmp_path / "grow.sqlite"
    store = store_at(path)
    origin = birth(store)
    initial = store.graph().native_assemblies()[0]
    assert initial.member_cell_ids == (8606, 9345, 11795)
    assert initial.structural_generation == 1
    before = store.graph()
    store.begin(5)
    event = store.event(5, 0, (("a", "1"),))
    assert store.graph().native_assemblies() == (initial,)
    result = store.end(5)
    graph = store.graph()
    (assembly,) = graph.native_assemblies()
    assert assembly.member_cell_ids == (8606, 9345, 11795, 12181)
    assert assembly.assembly_id == 0 and assembly.structural_generation == 2
    assert assembly.birth_close_serial == 4 and assembly.last_mutation_close_serial == 5
    assert graph.native_form_log() == origin
    assert {s.key for s in graph.synapses()} == {s.key for s in before.synapses()}
    (edit,) = graph.native_mutation_log()
    assert edit.stage == "GROW_ADD" and edit.inverse_added == (12181,)
    assert edit.exposure_id == 5 and edit.event_id == event.event_id
    assert edit.before_generation == 1 and edit.after_generation == 2
    assert (
        edit.before_members == initial.member_cell_ids
        and edit.after_members == assembly.member_cell_ids
    )
    assert all(s.degree == 3 and s.density == 1 and s.specificity == 1 for s in edit.scores)
    assert result.mutation_ordinals == (0,)
    with pytest.raises(FrozenInstanceError):
        edit.ordinal = 2
    with pytest.raises(ValueError, match="UNVERIFIED_NATIVE_MUTATION_CONSTRUCTION"):
        NativeStructuralMutationRecord(**asdict(edit))
    for cell in assembly.member_cell_ids:
        assert graph.cell(cell).assembly_ids == graph.member_assemblies(cell) == frozenset({0})
    assert store.end(5) == result
    store.begin(6)
    store.event(6, 0, ())
    stable = store.end(6)
    assert not stable.mutation_ordinals
    assert store.graph().native_assemblies() == (assembly,)
    assert store.graph().native_mutation_log() == (edit,)
    final, h = store.view(), store.h_bytes()
    assert store.inspect_native_lifecycle(5) == result and store.view() == final
    snapshot = GraphSnapshot.capture(store.graph())
    homeostasis = LanguageHomeostasis.decode(h).materialize(snapshot.committed_ids)
    assert read_only_episode(snapshot, homeostasis, (FeatureEvent((("a", "1"),)),), session_id=9)
    assert store.view() == final and store.graph().native_mutation_log() == (edit,)
    store.close()
    store = store_at(path)
    assert store.view() == final and store.h_bytes() == h
    assert store.graph().native_form_log() == origin and store.graph().native_mutation_log() == (
        edit,
    )
    assert store.end(5) == result and store.end(6) == stable
    store.close()


@pytest.mark.parametrize("operation", ["end", "abort"])
@pytest.mark.parametrize("phase", ["BEFORE_COMMIT", "AFTER_COMMIT"])
def test_root5_real_process_crashes_are_atomic(tmp_path, operation, phase):
    path = tmp_path / "crash.sqlite"
    store = store_at(path)
    birth_log = birth(store)
    store.begin(5)
    h_begin = store.h_bytes()
    store.event(5, 0, (("a", "1"),))
    before = store.view()
    store.close()
    script = """
import os,sys
from pathlib import Path
from dgca_next.persistence.store import RootStore
s=RootStore(Path(sys.argv[1]),repository_root=Path(sys.argv[2]),code_revision='a'*40,execution_mode='I4_NATIVE_MAINTAIN_GROW_V1')
def crash(stage):
    if stage==sys.argv[4]: os._exit(31)
getattr(s,sys.argv[3])(5,hook=crash)
"""
    assert (
        subprocess.run(
            [sys.executable, "-c", script, str(path), str(ROOT), operation, phase]
        ).returncode
        == 31
    )
    store = store_at(path)
    if phase == "BEFORE_COMMIT":
        assert store.view() == before and store.root(5).status == "OPEN"
    if operation == "end":
        close = store.end(5)
        assert store.end(5) == close and store.view().completed_closes == 5
    else:
        store.abort(5)
        assert store.h_bytes() == h_begin and store.view().completed_closes == 4
        assert store.graph().native_assemblies()[0].structural_generation == 1
        assert not store.graph().native_mutation_log()
        store.begin(6)
        store.event(6, 0, (("a", "1"),))
        store.end(6)
    assert store.graph().native_form_log() == birth_log
    assert store.graph().native_assemblies()[0].structural_generation == 2
    assert len(store.graph().native_mutation_log()) == 1
    store.close()


def test_exception_rollback_and_p04_mode_containment(tmp_path):
    store = store_at(tmp_path / "rollback.sqlite")
    birth(store)
    store.begin(5)
    store.event(5, 0, (("a", "1"),))
    before = store.view()
    with pytest.raises(ValueError, match="I4_REWIRING_CONFLICT"):
        store.request_recycling(5, 0, 8606, 0)

    def reject(stage):
        if stage == "BEFORE_COMMIT":
            raise RuntimeError("injected rollback")

    with pytest.raises(RuntimeError, match="injected rollback"):
        store.end(5, hook=reject)
    assert store.view() == before and store.root(5).status == "OPEN"
    assert store.graph().native_assemblies()[0].structural_generation == 1
    assert not store.graph().native_mutation_log()
    assert store.end(5).mutation_ordinals == (0,)
    store.close()


def test_required_additional_form_fails_without_publishing_evidence(tmp_path):
    store = store_at(tmp_path / "extra-form.sqlite")
    birth(store)
    store.begin(5)
    store.event(5, 0, (("ab", "1"),))
    store.end(5)
    for root in (6, 7):
        store.begin(root)
        store.event(root, 0, (("ab", "1"),))
        store.event(root, 1, (("ab", "1"),))
        store.end(root)
    store.begin(8)
    store.event(8, 0, (("ab", "1"),))
    store.event(8, 1, (("ab", "1"),))
    before = store.view()
    with pytest.raises(ValueError, match="I4_FIRST_FORM_LAB_SCOPE_EXCEEDED"):
        store.end(8)
    assert store.view() == before and store.root(8).status == "OPEN"
    assert store.view().completed_closes == 7
    assert len(store.graph().native_assemblies()) == 1
    store.abort(8)
    store.close()


@pytest.mark.parametrize(
    "damage",
    [
        "member",
        "generation",
        "order",
        "root",
        "serial",
        "before_w",
        "after_w",
        "event",
        "reverse",
        "birth",
        "archive",
    ],
)
def test_cold_replay_rejects_structural_forgery_with_repaired_hashes(tmp_path, damage):
    path = tmp_path / "forged.sqlite"
    store = store_at(path)
    birth(store)
    store.begin(5)
    store.event(5, 0, (("a", "1"),))
    store.end(5)
    store.close()
    with closing(sqlite3.connect(path)) as connection:
        raw_close, h, raw = connection.execute(
            "SELECT close_record,h_end,w_end FROM p01_roots WHERE exposure_id=5"
        ).fetchone()
        document = decode_record(raw, 0x57, 5)
        edit = document["mutations"][0]
        if damage == "member":
            edit["after_members"][-1] = 12182
        elif damage == "generation":
            edit["after_generation"] = 4
            document["assemblies"][0][3] = 4
        elif damage == "order":
            edit["ordinal"] = 1
        elif damage == "root":
            edit["exposure_id"] = 99
        elif damage == "serial":
            edit["completed_close_serial"] = 6
            document["assemblies"][0][5] = 6
        elif damage in ("before_w", "after_w"):
            edit[damage + "_hash"] = "0" * 64
        elif damage == "event":
            edit["event_id"] = 99
        elif damage == "reverse":
            document["membership_reverse"][-1][1] = []
        elif damage == "birth":
            document["forms"][0]["exposure_id"] = 99
        else:
            # COMPONENT forged archive representation, not production loss.
            edit["stage"] = "ARCHIVE"
            edit["after_members"] = edit["before_members"][1:]
            edit["after_status"] = "ARCHIVED"
            edit["inverse_removed"] = edit["before_members"]
            edit["inverse_added"] = []
            edit["scores"] = [
                dict(
                    cell_id=i,
                    degree=0,
                    density=0.0,
                    numerator=0.0,
                    denominator=1.0,
                    specificity=0.0,
                )
                for i in edit["before_members"]
            ]
            row = document["assemblies"][0]
            row[2], row[7] = edit["after_members"], "ARCHIVED"
            document["membership_reverse"] = []
            for row in document["cells_memberships"]:
                row[1] = []
        damaged = encode_record(0x57, 5, document)
        # A forged birth may already violate the origin-before-mutation
        # lineage guard. The other cases require independent root replay.
        if damage in ("root", "serial", "before_w", "after_w", "event", "archive"):
            assert encode_native_graph(decode_native_graph(damaged)) == damaged
            if damage == "archive":
                archived = decode_native_graph(damaged)
                assert _next_native_id(0, archived._state.native_assemblies) == 1
        close = replace(
            decode_lifecycle_close(raw_close), graph_hash=hashlib.sha256(damaged).hexdigest()
        )
        encoded = encode_lifecycle_close(close)
        with connection:
            connection.execute("UPDATE p01_metadata SET w_state=?", (damaged,))
            connection.execute(
                "UPDATE p01_roots SET w_end=?,close_record=?,close_hash=? WHERE exposure_id=5",
                (damaged, encoded, _checkpoint_digest(encoded, h, damaged)),
            )
    with pytest.raises(ValueError):
        store_at(path)


def test_accepted_r02_database_is_loaded_byte_exact_then_continued(tmp_path):
    old_root = tmp_path / "accepted-source"
    old_root.mkdir()
    accepted = "c66eb570b03e7653d9fa1f16c1805d52ad5f9072"
    archive = subprocess.check_output(
        ["git", "archive", "--format=tar", accepted, "src", "docs/specs"], cwd=ROOT
    )
    with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
        tar.extractall(old_root, filter="data")
    path = tmp_path / "accepted.sqlite"
    script = """
import hashlib,json,sys
from pathlib import Path
from dgca_next.persistence.store import RootStore
s=RootStore(Path(sys.argv[1]),repository_root=Path.cwd(),code_revision=sys.argv[2],execution_mode='I4_NATIVE_FORM_V1')
for r in range(1,5):
    s.begin(r)
    for o in range(1 if r==1 else 2): s.event(r,o,(("a","1"),))
    s.end(r)
print(json.dumps({'W':hashlib.sha256(s.view().W).hexdigest(),'H':hashlib.sha256(s.h_bytes()).hexdigest()}))
s.close()
"""
    env = os.environ | {"PYTHONPATH": str(old_root / "src")}
    baseline = json.loads(
        subprocess.check_output(
            [sys.executable, "-c", script, str(path), accepted], cwd=old_root, env=env, text=True
        )
    )
    before_bytes = path.read_bytes()
    store = store_at(path, revision=accepted)
    assert path.read_bytes() == before_bytes
    assert hashlib.sha256(store.view().W).hexdigest() == baseline["W"]
    assert hashlib.sha256(store.h_bytes()).hexdigest() == baseline["H"]
    assert baseline["W"] == "3b124aeb978bfa5e080b2d5ba9656fc78f1dbaae52ec0b3da9e56bedd1f9cd40"
    store.begin(5)
    store.event(5, 0, (("a", "1"),))
    assert store.end(5).mutation_ordinals == (0,)
    store.close()


def test_component_only_faulted_shadow_repairs_then_codec_archives(tmp_path):
    """Fault injection on a private copy: NOT production removal or evidence."""
    store = store_at(tmp_path / "component-repair.sqlite")
    birth(store)
    origin = store.graph().native_form_log()
    store.begin(5)
    store.event(5, 0, ())
    before = store.view()
    graph = store.graph()
    links = {
        k: v
        for k, v in graph._state.synapses.items()
        if not (k.scope.value == "LOCAL" and {k.source.cell_id, k.target.cell_id} == {8606, 9345})
    }
    fault = SparseNetwork()
    fault._state = replace(
        graph._state,
        synapses=MappingProxyType(links),
        outgoing=MappingProxyType(
            {
                i: frozenset(k for k in keys if k in links)
                for i, keys in graph._state.outgoing.items()
            }
        ),
    )
    with pytest.raises(ValueError, match="INVALID_NATIVE_RECIPROCAL_STRUCTURE"):
        encode_native_graph(fault)
    # The private repair boundary accepts physical-only temporary shadows;
    # no faulted graph is ever supplied to the public RootStore END API.
    shadow, close = store._backend._settle_graph(graph, 5, 5, (), event_clock=8)
    repaired, _ = _native_end(store._backend._connection, fault, close, replay=False)
    restored = decode_native_graph(encode_native_graph(repaired))
    (archived,) = restored.native_assemblies()
    assert archived.status == "ARCHIVED" and archived.member_cell_ids == (9345, 11795)
    assert archived.structural_generation == 2 and archived.assembly_id == 0
    assert restored.native_form_log() == origin
    assert restored.native_mutation_log()[0].stage == "ARCHIVE"
    assert all(not c.assembly_ids for c in restored.stored_cells())
    assert not restored._state.member_assemblies
    assert _next_native_id(0, restored._state.native_assemblies) == 1
    assert store.view() == before and len(shadow.synapses()) == len(graph.synapses())
    # Actual production close still uses the intact learned graph and GROW.
    store.end(5)
    assert store.graph().native_assemblies()[0].status == "LIVE"
    assert store.graph().native_assemblies()[0].member_cell_ids == (8606, 9345, 11795, 12181)
    store.close()


@pytest.mark.parametrize("schema", [3, 4])
def test_lifecycle_loader_rejects_legacy_database_without_touching_bytes(tmp_path, schema):
    path = tmp_path / "legacy.sqlite"
    old = RootStore(path, repository_root=ROOT, code_revision="a" * 40)
    old.begin(1)
    old.event(1, 0, (("a", "1"),))
    old.end(1)
    old.close()
    if schema == 3:
        with closing(sqlite3.connect(path)) as connection:
            with connection:
                connection.execute("DROP TABLE p04_requests")
                connection.execute("UPDATE p01_metadata SET schema_version=3")
    before = path.read_bytes()
    with pytest.raises(ValueError, match="UNSUPPORTED_PRODUCTION_SCHEMA"):
        store_at(path)
    assert path.read_bytes() == before
