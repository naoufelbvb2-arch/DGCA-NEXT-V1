"""Genuine same-ID second-operator rollback, crash and historical falsification."""

import argparse
import base64
import json
import shutil
import sqlite3
import subprocess
import sys
import time
from contextlib import closing
from dataclasses import asdict, replace
from pathlib import Path

from i4_final_archive_controls import metadata
from i4_final_lifecycle_closeout import write
from i4_r04_autonomous_forensics import file_sha
from i4_r04_autonomous_trial import sha
from i4_r04_operator_execution import ROOT, open_store, reopen, state

from dgca_next.graph.native_operator import read_operator
from dgca_next.learning.native_multi import decode_operator_check
from dgca_next.learning.native_operators import decode_operator_close, encode_operator_close
from dgca_next.persistence.binary_records import decode_record, encode_record
from dgca_next.persistence.graph_codec import encode_production_graph
from dgca_next.persistence.native_codec import _base_graph
from dgca_next.persistence.operator_codec import decode_operator_graph
from dgca_next.persistence.production_store import _checkpoint_digest

CASES = (
    "publish",
    "abort",
    "BEFORE_COMMIT",
    "AFTER_COMMIT",
    "second_clock",
    "missing_history_clock",
    "repaired_history_clock",
    "identity_proof",
    "partition_proof",
)


def damage(path, root, case):
    with closing(sqlite3.connect(path)) as db:
        target = 59 if case in ("missing_history_clock", "repaired_history_clock") else root
        raw, w, h = db.execute(
            "SELECT close_record,w_end,h_end FROM p01_roots WHERE exposure_id=?", (target,)
        ).fetchone()
        close = decode_operator_close(raw)
        well_formed_w = True
        if case == "missing_history_clock":
            with db:
                db.execute("UPDATE p01_roots SET close_serial=NULL WHERE exposure_id=59")
            return dict(missing_original_close_reference=True, original_close=59)
        if case == "repaired_history_clock":
            forged = encode_operator_close(replace(close, event_clock=close.event_clock + 1))
        elif case == "second_clock":
            doc = decode_record(w, 0x57, 5)
            changed = []
            for value in doc["operators"]:
                op = read_operator(value)
                if op["exposure_id"] == root:
                    op["event_clock"] += 1
                    value = encode_record(0x4D, 1, op)
                changed.append(value)
            doc["operators"] = changed
            w = encode_record(0x57, 5, doc)
            decode_operator_graph(w)
            forged = encode_operator_close(
                replace(close, event_clock=close.event_clock + 1, graph_hash=sha(w))
            )
        else:
            checks = []
            changed = False
            for value in close.operator_checks:
                check = decode_operator_check(value)
                if check["eligible"] and any(row[0] == 0 for row in check["subjects"]):
                    if case == "identity_proof":
                        check["subjects"][0][1] += 1
                    elif case == "partition_proof":
                        if check["operator"] == "SPLIT":
                            check["numbers"]["best"]["left"].reverse()
                        else:
                            check["numbers"]["union"].reverse()
                    else:
                        raise ValueError("UNDECLARED_FALSIFICATION")
                    changed = True
                    value = encode_record(0x4F, 1, check)
                checks.append(value)
            assert changed
            forged = encode_operator_close(replace(close, operator_checks=tuple(checks)))
        assert forged != raw
        decode_operator_close(forged)
        decode_operator_graph(w)
        with db:
            db.execute(
                "UPDATE p01_roots SET close_record=?,w_end=?,close_hash=? WHERE exposure_id=?",
                (forged, w, _checkpoint_digest(forged, h, w), target),
            )
            if case == "second_clock":
                db.execute("UPDATE p01_metadata SET w_state=? WHERE id=1", (w,))
        row = db.execute(
            "SELECT close_record,w_end,h_end,close_hash FROM p01_roots WHERE exposure_id=?",
            (target,),
        ).fetchone()
        assert row[3] == _checkpoint_digest(row[0], row[2], row[1])
        return dict(
            repaired_checkpoint_verified=True,
            canonical_close_decodes=True,
            canonical_W_decodes=well_formed_w,
            damaged_root=target,
        )


def run(args):
    receipt = json.loads(args.receipt.read_text(encoding="utf8"))
    source_info = receipt["pre_second_source"]
    assert receipt["gate"] == "PRODUCTION_SECOND_OBSERVED_CONTROLS_PENDING"
    assert file_sha(args.source) == source_info["sha256"] and not args.database.exists()
    shutil.copy2(args.source, args.database)
    revision = receipt["database_initial_revision"]
    root = source_info["root"]
    started = time.perf_counter()
    before = metadata(args.database)
    result = dict(
        classification="GENUINE_SECOND_OPERATOR_LINEAGE_CONTROL_NOT_INDEPENDENT_EVIDENCE",
        case=args.case,
        root_id=root,
        before=before,
        source_sha256=source_info["sha256"],
        database_initial_revision=revision,
        verification_revision=subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True
        ).strip(),
    )
    if args.case in ("BEFORE_COMMIT", "AFTER_COMMIT"):
        code = """
import os,sys
from pathlib import Path
from dgca_next.persistence.store import RootStore
s=RootStore(Path(sys.argv[1]),repository_root=Path(sys.argv[2]),code_revision=sys.argv[3],execution_mode='I4_NATIVE_OPERATORS_V1')
def hook(stage):
    if stage==sys.argv[5]: os._exit(73)
s.end(int(sys.argv[4]),hook=hook)
"""
        proc = subprocess.run(
            [
                sys.executable,
                "-c",
                code,
                str(args.database),
                str(ROOT),
                revision,
                str(root),
                args.case,
            ]
        )
        assert proc.returncode == 73
        s = open_store(args.database, revision)
        after = state(s)
        if args.case == "BEFORE_COMMIT":
            assert after == before and s.root(root).status == "OPEN"
            assert s.graph()._state.native_assemblies[0].last_merge_split_close_serial == 59
        else:
            assert s.root(root).status == "COMPLETED"
            close = s.end(root)
            assert s.end(root) == close and state(s) == after
            assert (
                s.graph()._state.native_assemblies[0].last_merge_split_close_serial
                == close.close_serial
            )
        result.update(after=after, process_exit=73, full_cold_recovery=True)
        s.close()
    else:
        s = open_store(args.database, revision)
        graph = s.graph()
        old_ops = graph.native_operator_log()
        old_births = graph.native_form_log()
        old_subject = graph._state.native_assemblies[0]
        physical = encode_production_graph(_base_graph(graph))
        assert old_subject.last_merge_split_close_serial == 59
        if args.case == "abort":
            with closing(sqlite3.connect(args.database)) as db:
                h_begin = db.execute(
                    "SELECT h_begin FROM p01_roots WHERE exposure_id=?", (root,)
                ).fetchone()[0]
            s.abort(root)
            assert s.h_bytes() == h_begin and state(s)["W_sha256"] == before["W_sha256"]
            assert s.graph().native_operator_log() == old_ops
            assert s.graph()._state.native_assemblies[0] == old_subject
            assert s.view().completed_closes == before["completed_closes"]
            final = state(s)
            s.close()
            result.update(after=final, H_BEGIN_exact=True, no_second_operator_or_age=True)
            result["recovery"] = reopen(args.database, revision, final)
        else:
            pending = s.inspect_pending_native(root)
            target = [decode_operator_check(v) for v in pending.close.operator_checks]
            assert any(c["eligible"] and any(r[0] == 0 for r in c["subjects"]) for c in target)
            assert not pending.close.accepted and state(s) == before

            def fail(stage):
                if stage == "BEFORE_COMMIT":
                    raise RuntimeError("SECOND_OPERATOR_ROLLBACK")

            if args.case == "publish":
                try:
                    s.end(root, hook=fail)
                    raise AssertionError("HOOK_NOT_REACHED")
                except RuntimeError as exc:
                    assert str(exc) == "SECOND_OPERATOR_ROLLBACK"
                assert state(s) == before and s.root(root).status == "OPEN"
            close = s.end(root)
            assert close == pending.close
            graph = s.graph()
            assert encode_production_graph(_base_graph(graph)) == physical
            assert graph.native_operator_log()[: len(old_ops)] == old_ops
            assert graph.native_form_log() == old_births
            new_subject = graph._state.native_assemblies[0]
            assert new_subject.birth_close_serial == old_subject.birth_close_serial == 4
            assert new_subject.structural_generation == old_subject.structural_generation + 1
            assert new_subject.last_merge_split_close_serial == close.close_serial
            final = state(s)
            assert s.end(root) == close and state(s) == final
            result.update(
                after=final,
                before_subject=asdict(old_subject),
                after_subject=asdict(new_subject),
                physical_links_and_evidence_unchanged=True,
                original_history_unchanged=True,
                duplicate_END_exact=True,
                exception_rollback_exact=args.case == "publish",
                new_records=[
                    dict(
                        read_operator(raw), check=decode_operator_check(read_operator(raw)["check"])
                    )
                    for raw in graph.native_operator_log()[len(old_ops) :]
                ],
            )
            if args.case == "publish":
                result["W_base64"] = base64.b64encode(s.view().W).decode()
            s.close()
            if args.case == "publish":
                result["recovery"] = reopen(args.database, revision, final)
            else:
                result["corruption"] = damage(args.database, root, args.case)
                try:
                    reopened = open_store(args.database, revision)
                except ValueError as exc:
                    result["forgery_refused"] = str(exc)
                else:
                    reopened.close()
                    raise AssertionError("FALSE_SECOND_OPERATOR_HISTORY_ACCEPTED")
    assert file_sha(args.source) == source_info["sha256"]
    result.update(
        seconds=time.perf_counter() - started, database_bytes=args.database.stat().st_size
    )
    write(args.output, result)
    print(json.dumps(dict(case=args.case, passed=True, seconds=result["seconds"])), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--database", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--case", choices=CASES, required=True)
    run(parser.parse_args())
