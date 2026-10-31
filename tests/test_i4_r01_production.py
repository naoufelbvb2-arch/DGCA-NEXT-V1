"""Authentic production root inspection; no fixture graph or Assembly birth."""

import hashlib
import sqlite3
from contextlib import closing
from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from dgca_next.persistence.binary_records import decode_record, encode_record
from dgca_next.persistence.store import RootStore

ROOT = Path(__file__).resolve().parents[1]


def engine(path):
    return RootStore(path, repository_root=ROOT, code_revision="a" * 40)


def train(store):
    results = []
    for root in range(1, 5):
        store.begin(root)
        for order in range(1 if root == 1 else 2):
            store.event(root, order, (("a", "1"),))
        store.end(root)
        results.append(store.inspect_form_eligibility(root))
    return results


def archive(path):
    with closing(sqlite3.connect(path)) as connection:
        return hashlib.sha256("\n".join(connection.iterdump()).encode()).hexdigest()


def test_real_triangle_and_event_qualification_round_trip_without_mutation(tmp_path):
    path = tmp_path / "real.sqlite"
    store = engine(path)
    progression = train(store)
    assert [p.reason for p in progression[:3]] == ["NO_RECIPROCAL_TRIANGLE"] * 3
    assert all(not w.committed_before for w in progression[0].events[0].witnesses)
    before, before_h, before_archive = store.view(), store.h_bytes(), archive(path)
    before_file = path.read_bytes()
    result = store.inspect_form_eligibility(4)
    assert result == progression[3] and result.reason == "FORM_ELIGIBLE"
    assert not result.structure.component_only and len(result.structure.triangles) == 4
    seed = result.projected_seeds[0]
    assert (seed.event_id, seed.event_order, seed.triangle.members) == (5, 0, (8606, 9345, 11795))
    assert len(result.projected_seeds) == 1
    for pair in seed.triangle.pairs:
        assert pair.edge and pair.support == 0.3
        for link in (pair.forward, pair.reverse):
            assert link.state == "CONSOLIDATED" and link.quality == 0.3
            assert link.external_count == 3 and [c.root_id for c in link.credits] == [2, 3, 4]
            assert link.structurally_eligible
    for cell in seed.triangle.cells:
        assert cell.degree == 2 and cell.density == 1
        assert len(cell.reciprocal_neighbors) == 3 and cell.specificity == pytest.approx(2 / 3)
    for witness in result.events[0].witnesses:
        assert witness.qualified and witness.direct_x_fixed == 1_000_000
        assert witness.committed_event == 0 and witness.final_activity >= witness.theta_emit
        assert witness.theta_emit == 0.253 and witness.pass1_emitter and witness.in_f_step
    assert store.view() == before and store.h_bytes() == before_h
    assert archive(path) == before_archive and path.read_bytes() == before_file
    assert all(not c.assembly_ids for c in store.graph().stored_cells())
    with pytest.raises(FrozenInstanceError):
        result.reason = "changed"
    store.close()
    store = engine(path)
    assert store.inspect_form_eligibility(4) == result
    assert store.view() == before and archive(path) == before_archive
    store.begin(5)
    store.event(5, 0, (("a", "1"),))
    store.end(5)
    assert store.view().W != before.W
    assert store.inspect_form_eligibility(4) == result  # historical W and H, not latest W
    assert store.inspect_form_eligibility(5).source_w_hash != result.source_w_hash
    store.close()


def test_no_direct_or_below_threshold_event_never_qualifies(tmp_path):
    store = engine(tmp_path / "negative.sqlite")
    train(store)
    store.begin(5)
    store.event(5, 0, ())
    store.end(5)
    result = store.inspect_form_eligibility(5)
    assert result.reason == "NO_QUALIFIED_FORM_EVENT" and not result.projected_seeds
    assert all(w.reason == "NO_DIRECT_EXTERNAL_WITNESS" for w in result.events[0].witnesses)
    store.begin(6)
    store.event(6, 0, (("a", "0.01"),))
    store.end(6)
    result = store.inspect_form_eligibility(6)
    assert result.reason == "NO_QUALIFIED_FORM_EVENT"
    assert all(w.reason == "BELOW_EVENT_THETA_EMIT" for w in result.events[0].witnesses)
    store.begin(7)
    store.event(7, 0, (("a", "1"),))
    predicted_only = store.event(7, 1, ())
    assert predicted_only.temporal and not predicted_only.X_fixed
    store.end(7)
    result = store.inspect_form_eligibility(7)
    assert all(w.reason == "NO_DIRECT_EXTERNAL_WITNESS" for w in result.events[1].witnesses)
    assert not any(c.selected and c.event_order == 1 for c in result.candidates)
    store.close()


def test_open_aborted_unknown_or_caller_objects_cannot_authorize_form(tmp_path):
    store = engine(tmp_path / "origins.sqlite")
    store.begin(1)
    event = store.event(1, 0, (("a", "1"),))
    for identity in (1, 99, event, True):
        with pytest.raises(ValueError, match="UNVERIFIED_FORM_EVENT"):
            store.inspect_form_eligibility(identity)
    store.abort(1)
    with pytest.raises(ValueError, match="ROOT_NOT_COMPLETED"):
        store.inspect_form_eligibility(1)
    store.close()


@pytest.mark.parametrize(
    "damage", ["truncated", "READ_ONLY_OBSERVED", "REPLAY_RECALLED", "INTERNAL_SELECTED"]
)
def test_missing_or_untrusted_event_record_is_unverified(tmp_path, damage):
    path = tmp_path / "corrupt.sqlite"
    store = engine(path)
    train(store)
    with closing(sqlite3.connect(path)) as connection:
        raw = connection.execute("SELECT record FROM p01_events WHERE event_id=5").fetchone()[0]
        if damage == "truncated":
            raw = raw[:10]
        else:
            document = decode_record(raw, 0x45, 2)
            document["origin"] = damage
            raw = encode_record(0x45, 2, document)
        with connection:
            connection.execute("UPDATE p01_events SET record=? WHERE event_id=5", (raw,))
    with pytest.raises(ValueError, match="UNVERIFIED_FORM_EVENT"):
        store.inspect_form_eligibility(4)
    store.close()
