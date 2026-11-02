"""Actual operator continuation/crash controls of genuine RootStore lineages."""

import argparse
import base64
import json
import shutil
import sqlite3
import subprocess
import sys
import time
from contextlib import closing
from dataclasses import asdict
from pathlib import Path

from i4_r04_autonomous_forensics import file_sha
from i4_r04_autonomous_trial import json_default, sha

from dgca_next.dynamics.session import FeatureEvent, read_only_episode
from dgca_next.dynamics.state import GraphSnapshot
from dgca_next.graph.native_operator import read_operator
from dgca_next.learning.homeostasis_profile import LanguageHomeostasis
from dgca_next.learning.native_multi import decode_operator_check
from dgca_next.learning.native_operators import encode_operator_close
from dgca_next.persistence.graph_codec import encode_production_graph
from dgca_next.persistence.native_codec import _base_graph
from dgca_next.persistence.store import RootStore

ROOT = Path(__file__).resolve().parents[2]
MODE = "I4_NATIVE_OPERATORS_V1"


def open_store(path, revision):
    return RootStore(path, repository_root=ROOT, code_revision=revision, execution_mode=MODE)


def state(s):
    v = s.view()
    return dict(
        W_sha256=sha(v.W),
        H_sha256=sha(s.h_bytes()),
        R_sha256=sha(v.runtime),
        completed_closes=v.completed_closes,
        open_root=v.open_root,
    )


def copied_source(source, target, trace):
    assert not target.exists(), "FRESH_CONTROL_COPY_REQUIRED"
    assert file_sha(source) == trace["recovery"]["file_sha256"]
    shutil.copy2(source, target)
    assert file_sha(source) == file_sha(target)


def reopen(path, revision, expected):
    script = """
import hashlib,json,sys
from pathlib import Path
from dgca_next.persistence.store import RootStore
s=RootStore(Path(sys.argv[1]),repository_root=Path(sys.argv[2]),code_revision=sys.argv[3],execution_mode='I4_NATIVE_OPERATORS_V1')
v=s.view()
print(json.dumps(dict(W_sha256=hashlib.sha256(v.W).hexdigest(),H_sha256=hashlib.sha256(s.h_bytes()).hexdigest(),R_sha256=hashlib.sha256(v.runtime).hexdigest(),completed_closes=v.completed_closes,open_root=v.open_root)))
s.close()
"""
    before = file_sha(path)
    actual = json.loads(
        subprocess.check_output(
            [sys.executable, "-c", script, str(path), str(ROOT), revision], text=True
        )
    )
    assert actual == expected and file_sha(path) == before
    return dict(
        cold_process_replay_exact=True, file_sha256=before, database_bytes=path.stat().st_size
    )


def publish(path, initial_revision, root):
    s = open_store(path, initial_revision)
    before, h = s.view(), s.h_bytes()
    births = s.graph().native_form_log()
    oldlinks = {v.key: v for v in s.graph().synapses()}
    pending = s.inspect_pending_native(root)
    assert pending.close.operator_ordinals and not pending.committed
    assert s.view() == before and s.h_bytes() == h

    def fail(stage):
        if stage == "BEFORE_COMMIT":
            raise RuntimeError("CONTROLLED_OPERATOR_ROLLBACK")

    try:
        s.end(root, hook=fail)
        raise AssertionError("FAILURE_INJECTION_NOT_REACHED")
    except RuntimeError as exc:
        assert str(exc) == "CONTROLLED_OPERATOR_ROLLBACK"
    assert s.view() == before and s.h_bytes() == h and s.root(root).status == "OPEN"
    close = s.end(root)
    assert close == pending.close and s.h_bytes() == h
    graph = s.graph()
    assert graph.native_form_log()[: len(births)] == births
    assert all(
        graph.synapse(k) is not None and graph.synapse(k).credits[: len(v.credits)] == v.credits
        for k, v in oldlinks.items()
    )
    physical = sha(encode_production_graph(_base_graph(graph)))
    records = []
    for raw in graph.native_operator_log():
        doc = read_operator(raw)
        assert doc["physical_w_hash"] == physical
        doc["check"] = decode_operator_check(doc["check"])
        records.append(doc)
    assert not graph.automatic_recycling_enabled
    after, h = s.view(), s.h_bytes()
    assert s.end(root) == close and s.view() == after and s.h_bytes() == h
    frozen = GraphSnapshot.capture(graph)
    profile = LanguageHomeostasis.decode(h).materialize(frozen.committed_ids)
    neural = read_only_episode(frozen, profile, (FeatureEvent((("a", "1"),)),), session_id=71)[0]
    assert s.view() == after and s.h_bytes() == h
    timers = [
        asdict(s.inspect_native_cooldown(a.assembly_id))
        for a in graph.native_assemblies()
        if a.status == "LIVE" and a.last_merge_split_close_serial == close.close_serial
    ]
    result = dict(
        status="COMPLETED",
        root_id=root,
        event_clock=close.event_clock,
        operator_ordinals=close.operator_ordinals,
        operator_records=records,
        before=dict(W_sha256=sha(before.W), H_sha256=sha(h)),
        final=dict(
            state=state(s),
            assemblies=[asdict(a) for a in graph.native_assemblies()],
            forms=[asdict(b) for b in graph.native_form_log()],
            mutations=[asdict(m) for m in graph.native_mutation_log()],
        ),
        W_base64=base64.b64encode(after.W).decode(),
        H_base64=base64.b64encode(h).decode(),
        close_base64=base64.b64encode(encode_operator_close(close)).decode(),
        physical_post_synapse_sha256=physical,
        original_births_preserved=True,
        all_previous_learned_links_and_credits_preserved=True,
        H_at_END_unchanged=True,
        exception_rollback_exact=True,
        duplicate_END_idempotent=True,
        read_only_state_unchanged=True,
        read_only_activity=sorted(neural.state.activity.items()),
        actual_same_close_cooldowns=timers,
    )
    s.close()
    result["recovery"] = reopen(path, initial_revision, result["final"]["state"])
    return result


def crash(path, initial_revision, root, stage, expected_before):
    script = """
import os,sys
from pathlib import Path
from dgca_next.persistence.store import RootStore
s=RootStore(Path(sys.argv[1]),repository_root=Path(sys.argv[2]),code_revision=sys.argv[3],execution_mode='I4_NATIVE_OPERATORS_V1')
def stop(stage):
    if stage==sys.argv[5]: os._exit(73)
s.end(int(sys.argv[4]),hook=stop)
"""
    proc = subprocess.run(
        [sys.executable, "-c", script, str(path), str(ROOT), initial_revision, str(root), stage]
    )
    assert proc.returncode == 73
    s = open_store(path, initial_revision)
    actual = state(s)
    if stage == "BEFORE_COMMIT":
        assert actual == expected_before
        assert actual["open_root"] == root and s.root(root).status == "OPEN"
        assert not s.graph().native_operator_log()
    else:
        assert actual["open_root"] is None and s.root(root).status == "COMPLETED"
        close = s.end(root)
        assert close.operator_ordinals and s.graph().native_operator_log()
        records = [read_operator(r) for r in s.graph().native_operator_log()]
        assert all(r["close_serial"] == close.close_serial for r in records)
    s.close()
    return dict(
        process_exit=73,
        stage=stage,
        final=dict(state=actual),
        cold_recovery=True,
        file_sha256=file_sha(path),
    )


def abort(path, initial_revision, root):
    s = open_store(path, initial_revision)
    before = s.view()
    with closing(sqlite3.connect(path)) as db:
        h_begin = db.execute(
            "SELECT h_begin FROM p01_roots WHERE exposure_id=?", (root,)
        ).fetchone()[0]
    s.abort(root)
    assert s.h_bytes() == h_begin and s.view().W == before.W
    assert (
        not s.graph().native_operator_log() and s.view().completed_closes == before.completed_closes
    )
    expected = state(s)
    s.close()
    return dict(
        H_BEGIN_restored_exact=True,
        no_operator_or_evidence_published=True,
        final=dict(state=expected),
        recovery=reopen(path, initial_revision, expected),
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--family", choices=("F05-r3", "F06-r2"), required=True)
    parser.add_argument(
        "--case", choices=("publish", "BEFORE_COMMIT", "AFTER_COMMIT", "abort"), required=True
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    revision = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    trace = json.loads((args.evidence / (args.family + ".json")).read_text(encoding="utf8"))
    root = trace["roots"][-1]["root_id"]
    args.directory.mkdir(parents=True, exist_ok=True)
    target = args.directory / (args.family + "-" + args.case + ".sqlite")
    copied_source(args.source / (args.family + ".sqlite"), target, trace)
    started = time.perf_counter()
    if args.case == "publish":
        result = publish(target, trace["code_revision"], root)
    elif args.case == "abort":
        result = abort(target, trace["code_revision"], root)
    else:
        result = crash(target, trace["code_revision"], root, args.case, trace["final"]["state"])
    result.update(
        family=args.family,
        case=args.case,
        writer_verification_revision=revision,
        database_initial_revision=trace["code_revision"],
        source_kind="CONTINUATION_OF_GENUINE_EXTERNAL_ROOTSTORE_LINEAGE",
        controls_are_not_independent_learning_roots=True,
        seconds=time.perf_counter() - started,
    )
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True, default=json_default) + "\n",
        encoding="utf8",
        newline="\n",
    )
    print(
        json.dumps(
            dict(
                family=args.family,
                case=args.case,
                seconds=result["seconds"],
                output=str(args.output),
            )
        )
    )


if __name__ == "__main__":
    main()
