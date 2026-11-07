"""Actual pre-ARCHIVE lineage copies; no extra independent learning evidence."""

import argparse
import base64
import json
import math
import shutil
import sqlite3
import subprocess
import sys
import time
from contextlib import closing
from dataclasses import asdict, replace

from i4_final_lifecycle_closeout import write
from i4_r04_autonomous_forensics import file_sha
from i4_r04_autonomous_trial import sha
from i4_r04_operator_execution import ROOT, open_store, reopen, state

from dgca_next.learning.native_operators import decode_operator_close, encode_operator_close
from dgca_next.persistence.production_store import _checkpoint_digest


def metadata(path):
    with closing(sqlite3.connect(path)) as db:
        w, h, r, count, root = db.execute(
            "SELECT w_state,h_state,r_state,completed_closes,open_root FROM p01_metadata"
        ).fetchone()
    return dict(
        W_sha256=sha(w), H_sha256=sha(h), R_sha256=sha(r), completed_closes=count, open_root=root
    )


def run(args):
    receipt = json.loads(args.receipt.read_text(encoding="utf8"))
    source = args.source
    assert file_sha(source) == receipt["pre_archive_source"]["sha256"]
    assert not args.database.exists(), "FRESH_CONTROL_COPY_REQUIRED"
    shutil.copy2(source, args.database)
    revision = receipt["database_initial_revision"]
    root = receipt["pre_archive_source"]["root"]
    started = time.perf_counter()
    before = metadata(args.database)
    result = dict(
        classification="ACTUAL_LINEAGE_TRANSACTION_CONTROL_NOT_INDEPENDENT_LEARNING",
        case=args.case,
        root_id=root,
        source_sha256=file_sha(source),
        database_initial_revision=revision,
        verification_revision=subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True
        ).strip(),
        before=before,
    )
    if args.case in ("BEFORE_COMMIT", "AFTER_COMMIT"):
        code = """
import os,sys
from pathlib import Path
from dgca_next.persistence.store import RootStore
s=RootStore(Path(sys.argv[1]),repository_root=Path(sys.argv[2]),code_revision=sys.argv[3],execution_mode='I4_NATIVE_OPERATORS_V1')
def crash(phase):
    if phase==sys.argv[5]: os._exit(73)
s.end(int(sys.argv[4]),hook=crash)
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
        else:
            assert s.root(root).status == "COMPLETED"
            assert any(
                m.stage == "ARCHIVE" and m.exposure_id == root
                for m in s.graph().native_mutation_log()
            )
            assert s.end(root) == s.end(root) and state(s) == after
        result.update(process_exit=73, after=after, cold_recovery_exact=True)
        s.close()
    else:
        s = open_store(args.database, revision)
        original = s.graph()
        initial_births = original.native_form_log()
        original_links = {v.key: v for v in original.synapses()}
        original_ops = original.native_operator_log()
        if args.case == "abort":
            with closing(sqlite3.connect(args.database)) as db:
                h_begin = db.execute(
                    "SELECT h_begin FROM p01_roots WHERE exposure_id=?", (root,)
                ).fetchone()[0]
            s.abort(root)
            assert s.h_bytes() == h_begin and state(s)["W_sha256"] == before["W_sha256"]
            assert s.view().completed_closes == before["completed_closes"]
            assert s.graph().native_operator_log() == original_ops
            assert s.graph().native_form_log() == initial_births
            assert not any(m.stage == "ARCHIVE" for m in s.graph().native_mutation_log())
            final = state(s)
            s.close()
            result.update(H_BEGIN_exact=True, no_archive_or_evidence=True, after=final)
            result["recovery"] = reopen(args.database, revision, final)
        else:
            pending = s.inspect_pending_native(root)
            assert not pending.committed

            def fail(phase):
                if phase == "BEFORE_COMMIT":
                    raise RuntimeError("ARCHIVE_ROLLBACK_CONTROL")

            if args.case == "publish":
                try:
                    s.end(root, hook=fail)
                    raise AssertionError("HOOK_NOT_REACHED")
                except RuntimeError as exc:
                    assert str(exc) == "ARCHIVE_ROLLBACK_CONTROL"
                assert state(s) == before and s.root(root).status == "OPEN"
            close = s.end(root)
            assert close == pending.close
            graph = s.graph()
            changes = [m for m in graph.native_mutation_log() if m.exposure_id == root]
            terminal = [m for m in changes if m.stage == "ARCHIVE"]
            assert terminal
            assert graph.native_form_log()[: len(initial_births)] == initial_births
            assert graph.native_operator_log()[: len(original_ops)] == original_ops
            for key, old in original_links.items():
                new = graph.synapse(key)
                assert new is not None and new.credits[: len(old.credits)] == old.credits
            for mutation in terminal:
                archived = graph._state.native_assemblies[mutation.assembly_id]
                assert archived.status == "ARCHIVED" and len(archived.member_cell_ids) == 2
                assert archived.structural_generation == mutation.before_generation + 1
                assert all(mutation.assembly_id not in c.assembly_ids for c in graph.stored_cells())
                assert all(
                    mutation.assembly_id not in graph.member_assemblies(c.cell_id)
                    for c in graph.stored_cells()
                )
            final = state(s)
            assert s.end(root) == close and state(s) == final
            result.update(
                after=final,
                mutations=[asdict(m) for m in changes],
                W_base64=base64.b64encode(s.view().W).decode(),
                immutable_births_and_prior_credits_preserved=True,
                duplicate_END_exact=True,
                exception_rollback_exact=args.case == "publish",
            )
            s.close()
            if args.case == "publish":
                result["recovery"] = reopen(args.database, revision, final)
            else:
                with closing(sqlite3.connect(args.database)) as db:
                    raw, w, h = db.execute(
                        "SELECT close_record,w_end,h_end FROM p01_roots WHERE exposure_id=?",
                        (root,),
                    ).fetchone()
                    close = decode_operator_close(raw)
                    if args.case == "forged_score":
                        rows = list(close.evaluations)
                        at = next(
                            i
                            for i, e in enumerate(rows)
                            if e.stage == "MAINTAIN" and e.reason == "REMOVE"
                        )
                        scores = list(rows[at].scores)
                        scores[0] = replace(
                            scores[0], denominator=math.nextafter(scores[0].denominator, math.inf)
                        )
                        rows[at] = replace(rows[at], scores=tuple(scores))
                        forged = encode_operator_close(replace(close, evaluations=tuple(rows)))
                    elif args.case == "forged_lineage":
                        forged = encode_operator_close(replace(close, mutation_ordinals=()))
                    else:
                        raise ValueError("UNDECLARED_CONTROL")
                    assert forged != raw
                    with db:
                        db.execute(
                            "UPDATE p01_roots SET close_record=?,close_hash=? WHERE exposure_id=?",
                            (forged, _checkpoint_digest(forged, h, w), root),
                        )
                    repaired = db.execute(
                        "SELECT close_record,close_hash FROM p01_roots WHERE exposure_id=?", (root,)
                    ).fetchone()
                    assert repaired[1] == _checkpoint_digest(repaired[0], h, w)
                try:
                    reopened = open_store(args.database, revision)
                except ValueError as exc:
                    result.update(
                        repaired_checksum_verified=True, historical_forgery_refused=str(exc)
                    )
                else:
                    reopened.close()
                    raise AssertionError("FORGED_ARCHIVE_HISTORY_ACCEPTED")
                result.pop("W_base64")
    assert file_sha(source) == result["source_sha256"]
    result.update(
        seconds=time.perf_counter() - started, database_bytes=args.database.stat().st_size
    )
    write(args.output, result)
    print(json.dumps(dict(case=args.case, passed=True, seconds=result["seconds"])), flush=True)


if __name__ == "__main__":
    from pathlib import Path

    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--database", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--case",
        choices=(
            "publish",
            "abort",
            "BEFORE_COMMIT",
            "AFTER_COMMIT",
            "forged_score",
            "forged_lineage",
        ),
        required=True,
    )
    run(parser.parse_args())
