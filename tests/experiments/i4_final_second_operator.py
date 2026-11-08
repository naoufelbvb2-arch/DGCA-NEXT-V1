"""B01: genuine post-SPLIT growth/removal and exact completed-event re-edit."""

import argparse
import json
import shutil
import subprocess
import time
from dataclasses import asdict
from pathlib import Path

from i4_final_lifecycle_closeout import physics, write
from i4_r04_autonomous_forensics import file_sha
from i4_r04_autonomous_trial import checkpoint, json_default
from i4_r04_operator_execution import open_store, reopen, state

from dgca_next.graph.native_operator import read_operator
from dgca_next.learning.native_multi import decode_operator_check

FEATURES = (
    "r04-merge-149",
    "r04-merge-293",
    "r04-merge-5965",
    "r04-merge-6364",
    "r04-merge-820",
    "r04-merge-1746",
    "r04-merge-2233",
    "r04-merge-2430",
)


def curriculum():
    bundles = [(("f617", "1"), (f, "1")) for f in FEATURES]
    return (
        [(b, 1) for b in bundles]
        + [(b, 3) for b in bundles[:2] for _ in range(3)]
        + [(b, 3) for b in bundles[2:] for _ in range(9)]
    )


def observe(e):
    doc = asdict(e)
    doc.pop("raw")
    return doc


def target_checks(close):
    selected = []
    for raw in close.operator_checks:
        doc = decode_operator_check(raw)
        if any(subject[0] == 0 for subject in doc["subjects"]):
            selected.append(doc)
    return selected


def completed_root(s, root, features, count):
    s.begin(root)
    events = [observe(s.event(root, i, features, boundary=i == 0)) for i in range(count)]
    before = state(s)
    original = s.graph()
    pending = s.inspect_pending_native(root)
    assert state(s) == before and not pending.committed
    checks = target_checks(pending.close)
    close = s.end(root)
    assert close == pending.close
    after = state(s)
    assert s.end(root) == close and state(s) == after
    graph = s.graph()
    assert graph.native_form_log()[: len(original.native_form_log())] == original.native_form_log()
    assert (
        graph.native_operator_log()[: len(original.native_operator_log())]
        == original.native_operator_log()
    )
    for old in original.synapses():
        new = graph.synapse(old.key)
        assert new is not None and new.credits[: len(old.credits)] == old.credits
    row = dict(
        root_id=root,
        features=features,
        events=events,
        before_END=before,
        after_END=checkpoint(s),
        event_clock=close.event_clock,
        close_serial=close.close_serial,
        accepted=[asdict(p) for p in close.accepted],
        refused=[asdict(p) for p in close.refused],
        evaluations=[asdict(e) for e in close.evaluations],
        pending_target_checks=checks,
        operator_checks=[decode_operator_check(raw) for raw in close.operator_checks],
        operator_ordinals=close.operator_ordinals,
        mutations=[asdict(m) for m in graph.native_mutation_log() if m.exposure_id == root],
        physical_graph_unchanged=before["W_sha256"] == after["W_sha256"],
    )
    return row


def run(args):
    receipt = json.loads(args.source_receipt.read_text(encoding="utf8"))
    expected = receipt["recovery"]["file_sha256"]
    assert file_sha(args.source) == expected and not args.database.exists()
    shutil.copy2(args.source, args.database)
    revision = receipt["database_initial_revision"]
    driver = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    started = time.perf_counter()
    s = open_store(args.database, revision)
    original = s.graph()
    original_ops = original.native_operator_log()
    first = asdict(s.inspect_native_cooldown(0))
    assert first["age_completed_events"] == 0 and first["last_close_reference"] == 59
    result = dict(
        family="B01-r1",
        lineage="CONTINUATION_OF_ORIGINAL_R04_F05_R3_NOT_A01_OR_INDEPENDENT",
        database_initial_revision=revision,
        verification_revision=driver,
        source_sha256=expected,
        original_cooldown=first,
        initial=physics(s),
        roots=[],
        gate="EMPIRICAL_NOT_PROVEN",
    )
    write(args.output, result)
    root = s.view().high_watermark + 1
    try:
        for features, count in curriculum():
            row = completed_root(s, root, features, count)
            result["roots"].append(row)
            write(args.output, result)
            print(
                json.dumps(
                    dict(
                        root=root,
                        age=row["event_clock"] - 161,
                        assemblies=row["after_END"]["assemblies"],
                    ),
                    default=json_default,
                ),
                flush=True,
            )
            subject = s.graph()._state.native_assemblies[0]
            if subject.status != "LIVE":
                result["blocker"] = "PREVIOUSLY_EDITED_SUBJECT_ARCHIVED_DURING_CURRICULUM"
                break
            assert subject.last_merge_split_close_serial == 59
            root += 1
        else:
            before_abort = state(s)
            clock = asdict(s.inspect_native_cooldown(0))
            assert clock["age_completed_events"] == 188
            s.begin(root)
            h_begin = s.h_bytes()
            events = [observe(s.event(root, i, ())) for i in range(3)]
            s.abort(root)
            assert s.h_bytes() == h_begin
            assert state(s)["W_sha256"] == before_abort["W_sha256"]
            assert asdict(s.inspect_native_cooldown(0)) == clock
            result["aborted_root"] = dict(
                root_id=root,
                events=events,
                before=before_abort,
                after=state(s),
                clock=clock,
                H_BEGIN_exact=True,
                no_completed_event_age=True,
            )
            root += 1
            row199 = completed_root(s, root, (), 11)
            result["at199"] = row199
            result["completed_timer199"] = asdict(s.inspect_native_cooldown(0))
            assert result["completed_timer199"]["age_completed_events"] == 199
            write(args.output, result)
            root += 1
            s.begin(root)
            event = s.event(root, 0, ())
            before = state(s)
            pending = s.inspect_pending_native(root)
            assert state(s) == before and not pending.committed
            checks200 = target_checks(pending.close)
            path = args.database.with_suffix(".before-second.sqlite")
            assert not path.exists()
            shutil.copy2(args.database, path)
            result["pre_second_source"] = dict(path=str(path), sha256=file_sha(path), root=root)
            close = s.end(root)
            assert close == pending.close and s.end(root) == close
            graph = s.graph()
            second = [
                read_operator(raw)
                for raw in graph.native_operator_log()[len(original_ops) :]
                if any(row[0] == 0 for row in read_operator(raw)["before"])
            ]
            checks199 = row199["pending_target_checks"]
            physical199 = any(
                not c["numbers"]["reasons"]
                if c["operator"] == "MERGE"
                else not c["numbers"]["reasons"] and c["numbers"]["best"] is not None
                for c in checks199
            )
            blocked199 = physical199 and all(not c["eligible"] for c in checks199)
            eligible200 = any(c["eligible"] for c in checks200)
            result["at200"] = dict(
                root_id=root,
                event=observe(event),
                before_END=before,
                after_END=checkpoint(s),
                checks=checks200,
                operator_ordinals=close.operator_ordinals,
                new_target_records=[
                    dict(r, check=decode_operator_check(r["check"])) for r in second
                ],
            )
            if blocked199 and row199["physical_graph_unchanged"] and eligible200 and second:
                assert all(r["close_serial"] == close.close_serial for r in second)
                assert graph.native_operator_log()[: len(original_ops)] == original_ops
                assert graph._state.native_assemblies[0].birth_close_serial == 4
                result["gate"] = "PRODUCTION_SECOND_OBSERVED_CONTROLS_PENDING"
            else:
                result["blocker"] = "SAME_ID_SECOND_ELIGIBILITY_OR_PUBLICATION_NOT_REACHED"
            result["final_timer"] = asdict(s.inspect_native_cooldown(0))
    except Exception as exc:
        result["failure"] = dict(type=type(exc).__name__, reason=str(exc), state=state(s))
        write(args.output, result)
        s.close()
        raise
    result["final"] = physics(s)
    final = state(s)
    s.close()
    result["recovery"] = reopen(args.database, revision, final)
    assert file_sha(args.source) == expected
    result["seconds"] = time.perf_counter() - started
    write(args.output, result)
    print(json.dumps(dict(gate=result["gate"], seconds=result["seconds"])), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--source-receipt", type=Path, required=True)
    parser.add_argument("--database", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    run(parser.parse_args())
