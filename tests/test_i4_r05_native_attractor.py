"""R05 actual RootStore learning and read-only/runtime falsification tests."""

import hashlib
import sqlite3
import subprocess
import sys
from contextlib import closing
from dataclasses import replace
from pathlib import Path

import pytest

from dgca_next.dynamics.activation import two_pass
from dgca_next.dynamics.native_attractor import (
    NativeFeatureEvent,
    ObservationScope,
    _advance,
)
from dgca_next.dynamics.session import FeatureEvent
from dgca_next.dynamics.state import GraphSnapshot
from dgca_next.learning.homeostasis_profile import LanguageHomeostasis
from dgca_next.persistence.attractor_store import (
    inspect_native_subject,
    native_session_step,
    start_native_session,
)
from dgca_next.persistence.binary_records import encode_record
from dgca_next.persistence.native_runtime_codec import runtime_document
from dgca_next.persistence.store import R_COLD, RootStore

ROOT = Path(__file__).resolve().parents[1]
BASE = "b4549d2f9c38d665f19a87848ae22b4b950c8fac"
MODE = "I4_NATIVE_ATTRACTOR_V1"


def open_store(path, mode=MODE):
    return RootStore(path, repository_root=ROOT, code_revision=BASE, execution_mode=mode)


def feature(support="1", *, boundary=False, scope=ObservationScope.UNSPECIFIED):
    return NativeFeatureEvent(FeatureEvent((("a", support),), boundary=boundary), scope)


def train(store, start=1, stop=5):
    for root in range(start, stop + 1):
        store.begin(root)
        for order in range(1 if root in (1, 5) else 2):
            store.event(root, order, (("a", "1"),))
        store.end(root)


@pytest.fixture(scope="module")
def learned(tmp_path_factory):
    path = tmp_path_factory.mktemp("r05-learned") / "native.sqlite"
    store = open_store(path)
    assert not store.graph().synapses()
    train(store, stop=4)
    prior = native_session_step(store, start_native_session(store, session_id=1), feature()).state
    train(store, start=5)
    yield store, path, prior
    store.close()


def test_real_native_generation_and_stale_previous_subject(learned):
    store, _, stale = learned
    native = inspect_native_subject(store, 0, generation=2)
    assert native.member_cell_ids == (8606, 9345, 11795, 12181)
    with pytest.raises(ValueError, match="STALE_NATIVE_GENERATION"):
        inspect_native_subject(store, 0, generation=1)
    with pytest.raises(ValueError, match="UNKNOWN_NATIVE_SUBJECT"):
        inspect_native_subject(store, 999)
    with pytest.raises(ValueError, match="STALE_NATIVE_RUNTIME_SNAPSHOT"):
        native_session_step(store, stale, feature())
    with pytest.raises(ValueError, match="AUTHENTICATED_NATIVE_ROOTSTORE_REQUIRED"):
        start_native_session(store.graph(), session_id=1)


def test_real_admission_sigma_independent_fresh_and_read_only(learned):
    store, _, _ = learned
    before = store.view()
    original = start_native_session(store, session_id=2)
    first = native_session_step(store, original, feature())
    assert len(first.state.attractors) == 1 and not first.sigma
    assert first.evaluations[0]["mean_pass"] and first.evaluations[0]["cohesion_pass"]
    normal = native_session_step(store, first.state, feature("0.2"))
    ablated = native_session_step(store, first.state, feature("0.2"), context_sigma=False)
    assert normal.fresh == ablated.fresh and normal.sigma and not ablated.sigma
    assert set(normal.sigma.values()) == {0.9 * first.state.attractors[0].strength}
    assert normal.state.attractors[0].age == 1 and original.next_order == 0
    empty = native_session_step(store, first.state, NativeFeatureEvent(FeatureEvent(())))
    assert not any(empty.fresh.second.activity.values())
    assert empty.state.attractors[0].strength == 0.9 * first.state.attractors[0].strength
    assert store.view() == before
    assert all(not x.fixture_only for x in store.graph().synapses())
    with pytest.raises(ValueError, match="UNVERIFIED_NATIVE_RUNTIME"):
        replace(first.state, attractors=())


def test_real_one_threshold_negative_and_no_input(learned):
    store, _, _ = learned
    cold = start_native_session(store, session_id=3)
    trace = native_session_step(store, cold, feature("0.4"))
    assert trace.evaluations[0]["mean_pass"]
    assert not trace.evaluations[0]["cohesion_pass"] and not trace.state.attractors
    empty = native_session_step(store, cold, NativeFeatureEvent(FeatureEvent(())))
    assert not empty.state.attractors and not any(empty.fresh.second.activity.values())


def test_fresh_is_frozen_zero_scratch_and_real_weighted_reciprocal_fold(learned):
    store, _, _ = learned
    cold = start_native_session(store, session_id=30)
    first = native_session_step(store, cold, feature())
    observed = native_session_step(store, first.state, feature("0.4"))
    graph = GraphSnapshot.capture(store.graph())
    h = LanguageHomeostasis.decode(store.h_bytes()).materialize(graph.committed_ids)
    expected = two_pass(graph, h, {}, dict(observed.observation.X), {}, {})
    assert expected == observed.fresh
    row = observed.evaluations[0]
    numerator, denominator = 0.0, 0.0
    for i, j, weight in row["reciprocal_pairs"]:
        numerator += weight * min(expected.second.activity[i], expected.second.activity[j])
        denominator += weight
    assert row["fresh_cohesion"] == numerator / denominator
    assert row["fresh_mean"] == sum(expected.second.activity.values()) / 4


def test_cross_platform_actual_learned_physical_and_homeostasis_fingerprints(learned):
    store, _, _ = learned
    # Actual F01 root5 witnesses, never a manufactured learned connection.
    assert hashlib.sha256(store.view().W).hexdigest() == (
        "240aa43d90731aeadc2b2f862da0f7e6f2093c6f87afa2d6680cec0595bce66b"
    )
    assert hashlib.sha256(store.h_bytes()).hexdigest() == (
        "b3eca03ad5c1f9eae079ea82766c0ff64a567780421215354bb9b55603377810"
    )


def test_real_full_age_horizon_and_boundary_precedence(learned):
    store, _, _ = learned
    current = native_session_step(store, start_native_session(store, session_id=4), feature())
    for age in range(1, 30):
        current = native_session_step(store, current.state, feature())
        assert current.state.attractors[0].age == age
    at_limit = native_session_step(store, current.state, feature())
    assert not at_limit.state.attractors and at_limit.sigma
    assert at_limit.evaluations[0]["diagnostic"] == "ATTRACTOR_AGE_COLLAPSE"
    boundary = native_session_step(store, current.state, feature(boundary=True))
    assert not boundary.state.attractors and not boundary.sigma
    assert boundary.evaluations[0]["diagnostic"] == "ATTRACTOR_BOUNDARY_COLLAPSE"


def test_numeric_reverse_threshold_and_error_precedence_are_components(learned):
    store, _, _ = learned
    subject = inspect_native_subject(store, 0)
    # Explicit mathematical controls; these supplied numbers are never ingress.
    state, diagnostic, _ = _advance(subject, None, 0.39, 0.6, (), False)
    assert state is None and diagnostic == "ATTRACTOR_INSUFFICIENT_FRESH_MEAN"
    initial, _, _ = _advance(subject, None, 0.8, 0.8, (), False)
    for _ in range(2):
        initial, _, miss = _advance(subject, initial, 0.8, 0.8, ((8606, 0.8, 0.0),), False)
    assert initial is None and miss == 0.8


def copy_learned(source, target):
    with closing(sqlite3.connect(source)) as src, closing(sqlite3.connect(target)) as dst:
        src.backup(dst)


def test_genuine_external_comparable_error_and_no_event_evidence(tmp_path, learned):
    _, source, _ = learned
    path = tmp_path / "external-error.sqlite"
    copy_learned(source, path)
    store = open_store(path)
    store.begin(6)
    w_begin = store.view().W
    rows = []
    for order in range(10):
        value = "1" if order in (0, 1, 3) else "0.1"
        store.event(
            6, order, (("a", value),), observation_scope=ObservationScope.COMPLETE_NEXT_EVENT
        )
        rows.append(runtime_document(store.view().runtime)["evaluations"][0])
        assert store.view().W == w_begin
    assert rows[2]["comparables"] and rows[2]["miss"] > 0
    assert rows[3]["after"][-1] >= rows[2]["after"][-1]
    assert any(r["diagnostic"] == "ATTRACTOR_ERROR_COLLAPSE" for r in rows)
    store.end(6)
    assert store.view().runtime == R_COLD
    assert all(
        len({c.root_id for c in s.credits}) == s.external_root_count
        for s in store.graph().synapses()
    )
    store.close()
    reopened = open_store(path)
    assert reopened.root(6).status == "COMPLETED"
    reopened.close()


@pytest.mark.parametrize("scope", [ObservationScope.UNSPECIFIED, ObservationScope.PARTIAL])
def test_actual_unqualified_outcomes_never_accumulate_error(tmp_path, learned, scope):
    _, source, _ = learned
    path = tmp_path / "no-error-authority.sqlite"
    copy_learned(source, path)
    store = open_store(path)
    store.begin(6)
    for order, value in enumerate(("1", "1", "0.1", "0.1")):
        store.event(6, order, (("a", value),), observation_scope=scope)
    row = runtime_document(store.view().runtime)["evaluations"][0]
    assert row["predictions"] and not row["comparables"] and row["after"][-1] == 0.0
    store.abort(6)
    store.close()


@pytest.mark.parametrize("operation", ["event", "end", "abort"])
@pytest.mark.parametrize("phase", ["BEFORE_COMMIT", "AFTER_COMMIT"])
def test_native_process_crash_atomicity(tmp_path, learned, operation, phase):
    _, source, _ = learned
    path = tmp_path / "crash.sqlite"
    copy_learned(source, path)
    store = open_store(path)
    store.begin(6)
    store.event(6, 0, (("a", "1"),))
    store.event(6, 1, (("a", "1"),))
    before = store.view()
    h_begin = store.root(6).H_begin
    store.close()
    statement = (
        "s.event(6,2,(('a','1'),),hook=hook)"
        if operation == "event"
        else f"s.{operation}(6,hook=hook)"
    )
    code = (
        "import os; from pathlib import Path; from dgca_next.persistence.store import RootStore; "
        f"s=RootStore(Path({str(path)!r}),repository_root=Path({str(ROOT)!r}),"
        f"code_revision={BASE!r},execution_mode={MODE!r}); "
        f"hook=lambda p: os._exit(27) if p=={phase!r} else None; " + statement
    )
    child = subprocess.run([sys.executable, "-c", code], cwd=ROOT, capture_output=True, text=True)
    assert child.returncode == 27, child.stderr
    recovered = open_store(path)
    if phase == "BEFORE_COMMIT":
        assert recovered.view() == before and recovered.root(6).next_order == 2
    elif operation == "event":
        assert recovered.root(6).next_order == 3
        state = runtime_document(recovered.view().runtime)["state"]
        assert state["attractors"][0][4] == 1 and state["next_order"] == 3
    elif operation == "end":
        assert recovered.root(6).status == "COMPLETED" and recovered.view().runtime == R_COLD
        closed = recovered.end(6)
        assert closed == recovered.end(6)
    else:
        assert recovered.root(6).status == "ABORTED" and recovered.view().runtime == R_COLD
        assert recovered.view().homeostasis == h_begin
    recovered.close()


def test_actual_event_checkpoint_abort_cold_reset_and_scope(tmp_path):
    path = tmp_path / "runtime.sqlite"
    store = open_store(path)
    empty = store.view()
    scratch = native_session_step(store, start_native_session(store, session_id=90), feature())
    assert not scratch.state.attractors and not scratch.passes.second.activity
    assert store.view() == empty
    train(store)
    h_begin = store.h_bytes()
    store.begin(6)
    store.event(6, 0, (("a", "1"),))
    first = runtime_document(store.view().runtime)
    assert not first["state"]["attractors"]
    store.event(6, 1, (("a", "1"),))
    second = runtime_document(store.view().runtime)
    assert second["state"]["attractors"][0][4:] == [0, 0.0]
    checkpoint = store.view()
    with pytest.raises(ValueError, match="EVENT_ORDER_MISMATCH"):
        store.event(6, 1, (("a", "1"),))
    with pytest.raises(ValueError, match="INVALID_EXTERNAL_OBSERVATION_SCOPE"):
        store.event(6, 2, (("a", "1"),), observation_scope="COMPLETE_NEXT_EVENT")
    assert store.view() == checkpoint
    store.close()
    store = open_store(path)
    assert store.view() == checkpoint
    assert store.observation(6, 1).event_order == 1
    store.abort(6)
    assert store.h_bytes() == h_begin and store.view().runtime == R_COLD
    store.begin(7)
    store.event(7, 0, (("a", "1"),))
    assert not runtime_document(store.view().runtime)["state"]["attractors"]
    store.abort(7)
    store.close()
    with pytest.raises(ValueError, match="UNSUPPORTED_STORE_SCHEMA"):
        open_store(path, "I4_NATIVE_OPERATORS_V1")


def test_cold_sensory_abort_retains_lawful_births_and_exact_initial_H(tmp_path):
    path = tmp_path / "cold-abort.sqlite"
    store = open_store(path)
    initial_h = store.h_bytes()
    store.begin(1)
    store.event(1, 0, (("a", "1"),))
    store.event(1, 1, (("a", "1"),))
    assert store.h_bytes() != initial_h
    lawful_w = store.view().W
    store.abort(1)
    assert store.view().W == lawful_w and store.h_bytes() == initial_h
    assert store.view().runtime == R_COLD and not store.graph().synapses()
    store.close()
    recovered = open_store(path)
    assert tuple(c.cell_id for c in recovered.graph().stored_cells()) == (8606, 9345, 11795, 12181)
    assert recovered.h_bytes() == initial_h and recovered.root(1).status == "ABORTED"
    recovered.begin(2)
    recovered.event(2, 0, (("a", "1"),))
    recovered.abort(2)
    recovered.close()


def test_active_generation_one_is_not_backdated_to_generation_two_at_END(tmp_path):
    path = tmp_path / "active-before-grow.sqlite"
    store = open_store(path)
    train(store, stop=4)
    store.begin(5)
    store.event(5, 0, (("a", "1"),))
    store.event(5, 1, (("a", "1"),))
    saved = runtime_document(store.view().runtime)
    assert saved["state"]["attractors"][0][1] == 1
    assert saved["state"]["attractors"][0][2] == [8606, 9345, 11795]
    store.end(5)
    assert inspect_native_subject(store, 0).structural_generation == 2
    assert store.view().runtime == R_COLD
    store.close()
    recovered = open_store(path)
    # Cold history must authenticate old event-start GEN1, not the final GEN2.
    assert inspect_native_subject(recovered, 0).member_cell_ids == (8606, 9345, 11795, 12181)
    recovered.begin(6)
    recovered.event(6, 0, (("a", "1"),))
    assert not runtime_document(recovered.view().runtime)["state"]["attractors"]
    recovered.abort(6)
    recovered.close()


@pytest.mark.parametrize("damage", ["age", "generation", "fresh", "scope", "version", "missing"])
def test_repaired_runtime_forgery_is_rederived_and_refused(tmp_path, learned, damage):
    _, source, _ = learned
    path = tmp_path / "forged.sqlite"
    with closing(sqlite3.connect(source)) as source_db, closing(sqlite3.connect(path)) as target:
        source_db.backup(target)
    store = open_store(path)
    store.begin(6)
    store.event(6, 0, (("a", "1"),))
    store.event(6, 1, (("a", "1"),))
    raw = store.view().runtime
    doc = runtime_document(raw)
    store.close()
    if damage == "age":
        doc["state"]["attractors"][0][4] = 8
    elif damage == "generation":
        doc["state"]["attractors"][0][1] += 1
    elif damage == "fresh":
        doc["fresh_second"]["activity"][0][1] = 0.0
    elif damage == "scope":
        doc["scope"] = "FORGED_EXPECTED_Y"
    forged = encode_record(0x52, 3 if damage == "version" else 2, doc)
    with closing(sqlite3.connect(path)) as db, db:
        if damage == "missing":
            db.execute(
                "DELETE FROM p05_runtime WHERE event_id=(SELECT MAX(event_id) FROM p05_runtime)"
            )
        else:
            db.execute(
                "UPDATE p05_runtime SET record=? "
                "WHERE event_id=(SELECT MAX(event_id) FROM p05_runtime)",
                (forged,),
            )
            db.execute("UPDATE p01_metadata SET r_state=?", (forged,))
    assert hashlib.sha256(forged).digest() != hashlib.sha256(raw).digest() or damage == "missing"
    with pytest.raises(ValueError):
        open_store(path)
