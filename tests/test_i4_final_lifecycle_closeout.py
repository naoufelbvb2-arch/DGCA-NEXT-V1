"""Saved genuine archive evidence components; long RootStore controls run separately."""

import base64
import hashlib
import json
from dataclasses import asdict
from pathlib import Path

import pytest

from dgca_next.graph.assembly_support import inspect_structure
from dgca_next.graph.native_lifecycle import passes, score
from dgca_next.graph.native_operator import read_operator
from dgca_next.persistence.binary_records import decode_record, encode_record
from dgca_next.persistence.native_codec import _base_graph, encode_native_graph
from dgca_next.persistence.operator_codec import decode_operator_graph

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs/implementation/evidence/i4-final-closeout"
OLD_EVIDENCE = ROOT / "docs/implementation/evidence/i4-r04-autonomous"


@pytest.fixture(scope="module")
def archive():
    document = json.loads((EVIDENCE / "A01-publish.json").read_text(encoding="utf8"))
    raw = base64.b64decode(document["W_base64"], validate=True)
    assert hashlib.sha256(raw).hexdigest() == document["after"]["W_sha256"]
    return document, raw, decode_operator_graph(raw)


def test_genuine_archive_checkpoint_roundtrips_and_has_no_fixture_authority(archive):
    _, raw, graph = archive
    assert encode_native_graph(graph) == raw
    assert all(not c.fixture_only for c in graph.stored_cells())
    assert all(not s.fixture_only for s in graph.synapses())
    assert not graph.automatic_recycling_enabled


def test_terminal_maintain_is_distinct_from_original_split_and_merge_archive(archive):
    doc, _, graph = archive
    mutations = [m for m in graph.native_mutation_log() if m.exposure_id == doc["root_id"]]
    terminal = [m for m in mutations if m.stage == "ARCHIVE"]
    assert terminal and {m.assembly_id for m in terminal} == {0, 1}
    assert all(len(m.before_members) == 3 and len(m.after_members) == 2 for m in terminal)
    assert all(m.before_status == "LIVE" and m.after_status == "ARCHIVED" for m in terminal)
    assert all(m.after_generation == m.before_generation + 1 for m in terminal)
    operators = [read_operator(r) for r in graph.native_operator_log()]
    assert operators and all(
        o["close_serial"] == 59 and o["operator"] == "SPLIT" for o in operators
    )


def test_archived_ids_have_no_live_inverse_and_are_not_reused(archive):
    doc, _, graph = archive
    for identity in (0, 1):
        record = graph._state.native_assemblies[identity]
        assert record.status == "ARCHIVED"
        assert record.birth_close_serial == 4 and record.last_merge_split_close_serial == 59
        assert len(record.member_cell_ids) == 2
        assert all(identity not in c.assembly_ids for c in graph.stored_cells())
        assert all(identity not in graph.member_assemblies(c.cell_id) for c in graph.stored_cells())
    records = graph.native_assemblies()
    assert [r.assembly_id for r in records] == list(range(len(records)))
    assert doc["immutable_births_and_prior_credits_preserved"]


def test_saved_archive_scores_recompute_from_actual_learned_physical_graph(archive):
    doc, _, graph = archive
    supports = {}
    for pair in inspect_structure(_base_graph(graph)).pairs:
        if pair.edge:
            supports.setdefault(pair.first, {})[pair.second] = pair.support
            supports.setdefault(pair.second, {})[pair.first] = pair.support
    for mutation in graph.native_mutation_log():
        if mutation.exposure_id != doc["root_id"] or mutation.stage != "ARCHIVE":
            continue
        actual = tuple(score(i, mutation.before_members, supports) for i in mutation.before_members)
        assert actual == mutation.scores
        failing = [v.cell_id for v in actual if not passes(v, "rho_keep", "sigma_keep")]
        erased = set(mutation.before_members) - set(mutation.after_members)
        assert erased == {min(failing)} == {8200}
        assert all(v.degree == 2 and v.density == 1.0 for v in actual)
        assert next(v for v in actual if v.cell_id == 8200).specificity < 0.20


def test_original_physical_links_and_births_survive_terminal_archive(archive):
    _, _, graph = archive
    original_doc = json.loads((OLD_EVIDENCE / "F05-r3-publish.json").read_text(encoding="utf8"))
    original = decode_operator_graph(base64.b64decode(original_doc["W_base64"], validate=True))
    assert graph.native_form_log()[: len(original.native_form_log())] == original.native_form_log()
    assert graph.native_operator_log() == original.native_operator_log()
    for old in original.synapses():
        new = graph.synapse(old.key)
        assert new is not None and new.credits[: len(old.credits)] == old.credits
        assert new.E_ext >= old.E_ext and new.E_int == old.E_int == 0.0
    assert all(asdict(c)["root_id"] >= 0 for s in graph.synapses() for c in s.credits)


@pytest.mark.parametrize("damage", ["generation", "inverse", "removal_order"])
def test_repaired_structural_archive_forgeries_are_not_valid_checkpoints(archive, damage):
    _, raw, _ = archive
    doc = decode_record(raw, 0x57, 5)
    mutation = next(m for m in doc["mutations"] if m["stage"] == "ARCHIVE")
    if damage == "generation":
        mutation["after_generation"] += 1
    elif damage == "inverse":
        mutation["inverse_removed"] = mutation["after_members"]
    else:
        mutation["after_members"] = mutation["before_members"][:2]
    forged = encode_record(0x57, 5, doc)
    assert forged != raw
    with pytest.raises(ValueError):
        decode_operator_graph(forged)


def test_actual_archive_process_and_falsification_receipts_are_explicit():
    # Receipt verification is component coverage, not another run of the long histories.
    trajectory = json.loads((EVIDENCE / "A01-r1.json").read_text(encoding="utf8"))
    published = json.loads((EVIDENCE / "A01-publish.json").read_text(encoding="utf8"))
    final = trajectory["roots"][-1]
    for key in ("W_sha256", "H_sha256", "R_sha256", "completed_closes", "open_root"):
        assert published["before"][key] == final["before_END"][key]
        assert published["after"][key] == final["after_END"][key]
    for case in (
        "publish",
        "abort",
        "BEFORE_COMMIT",
        "AFTER_COMMIT",
        "forged_score",
        "forged_lineage",
    ):
        doc = json.loads((EVIDENCE / f"A01-{case}.json").read_text(encoding="utf8"))
        assert (
            doc["classification"] == "ACTUAL_LINEAGE_TRANSACTION_CONTROL_NOT_INDEPENDENT_LEARNING"
        )
        if case.startswith("forged"):
            assert doc["repaired_checksum_verified"] and doc["historical_forgery_refused"]
        elif case.endswith("COMMIT"):
            assert doc["process_exit"] == 73 and doc["cold_recovery_exact"]
            assert doc["after"] == published["after" if case == "AFTER_COMMIT" else "before"]
        elif case == "abort":
            assert doc["H_BEGIN_exact"] and doc["no_archive_or_evidence"]
            assert doc["after"]["H_sha256"] == final["events"][0]["pre_h_hash"]
            assert doc["after"]["W_sha256"] == published["before"]["W_sha256"]
        else:
            assert doc["exception_rollback_exact"] and doc["duplicate_END_exact"]
            assert doc["recovery"]["cold_process_replay_exact"]


def test_actual_post_archive_form_allocates_past_retained_archived_identities():
    document = json.loads((EVIDENCE / "A01-identity.json").read_text(encoding="utf8"))
    assert document["classification"] == "GENUINE_POST_ARCHIVE_FORM_SAME_LINEAGE_IDENTITY_CONTROL"
    assert document["new_form_after_archive"] and document["formed_ids"]
    assert min(document["formed_ids"]) > document["previous_high_watermark"] == 4
    assert document["archived_records_and_births_unchanged"]
    assert document["recovery"]["cold_process_replay_exact"]
    archived = document["original_archived_records"]
    assert {a["assembly_id"] for a in archived} == {0, 1}
    assert all(a["status"] == "ARCHIVED" and a["structural_generation"] == 14 for a in archived)
