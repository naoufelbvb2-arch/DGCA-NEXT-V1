"""Predeclared F07: genuine completed events after an actual SPLIT stamp."""

import argparse
import json
import shutil
import subprocess
import time
from dataclasses import asdict
from pathlib import Path

from i4_r04_autonomous_forensics import file_sha
from i4_r04_autonomous_trial import json_default
from i4_r04_operator_execution import open_store, reopen, state

from dgca_next.dynamics.session import FeatureEvent, read_only_episode
from dgca_next.dynamics.state import GraphSnapshot
from dgca_next.learning.homeostasis_profile import LanguageHomeostasis


def run(path, initial_revision):
    s = open_store(path, initial_revision)
    before = s.view()
    graph = s.graph()
    identity = 0
    assert graph.native_assemblies()[0].last_merge_split_close_serial is not None
    baseline = asdict(s.inspect_native_cooldown(identity))
    assert baseline["age_completed_events"] == 0
    first = before.high_watermark + 1
    rows = []
    for offset, count, abort_root in (
        (0, 1, False),
        (1, 5, False),
        (2, 3, True),
        (3, 193, False),
        (4, 1, False),
    ):
        root = first + offset
        s.begin(root)
        h_begin = s.h_bytes()
        for order in range(count):
            event = s.event(root, order, ())
            assert not event.X_fixed and not event.born
        during = asdict(s.inspect_native_cooldown(identity))
        if abort_root:
            s.abort(root)
            assert s.h_bytes() == h_begin
            after = asdict(s.inspect_native_cooldown(identity))
            assert after == during and after["age_completed_events"] == 6
            close = None
        else:
            close = s.end(root)
            after = asdict(s.inspect_native_cooldown(identity))
            expected = {0: 1, 1: 6, 3: 199, 4: 200}[offset]
            assert after["age_completed_events"] == expected
            assert s.end(root) == close
        assert s.view().W == before.W and s.graph().native_assemblies() == graph.native_assemblies()
        frozen = GraphSnapshot.capture(s.graph())
        current, h = s.view(), s.h_bytes()
        profile = LanguageHomeostasis.decode(h).materialize(frozen.committed_ids)
        read_only_episode(frozen, profile, (FeatureEvent((("a", "1"),)),), session_id=root)
        assert s.view() == current and s.h_bytes() == h
        assert asdict(s.inspect_native_cooldown(identity)) == after
        rows.append(
            dict(
                root_id=root,
                event_ids=list(range(event.event_id - count + 1, event.event_id + 1)),
                event_count=count,
                status="ABORTED" if abort_root else "COMPLETED",
                close_serial=None if close is None else close.close_serial,
                completed_event_clock=None if close is None else close.event_clock,
                during_OPEN=during,
                after_close=after,
                readonly_unchanged=True,
            )
        )
    assert not rows[-2]["after_close"]["status"] == "COOLDOWN_ELAPSED"
    assert rows[-1]["after_close"]["status"] == "COOLDOWN_ELAPSED"
    result = dict(
        family="F07",
        baseline=baseline,
        actual_assembly_id=identity,
        actual_merge_split_close_reference=baseline["last_close_reference"],
        roots=rows,
        completed_external_events=200,
        aborted_external_events=3,
        W_and_generations_unchanged=True,
        H_BEGIN_restored_on_ABORT=True,
        final=dict(state=state(s)),
        actual_second_edit_attempted=False,
    )
    s.close()
    result["recovery"] = reopen(path, initial_revision, result["final"]["state"])
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--source-receipt", type=Path, required=True)
    parser.add_argument("--database", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    receipt = json.loads(args.source_receipt.read_text(encoding="utf8"))
    assert file_sha(args.source) == receipt["recovery"]["file_sha256"]
    assert not args.database.exists()
    shutil.copy2(args.source, args.database)
    started = time.perf_counter()
    result = run(args.database, receipt["database_initial_revision"])
    result.update(
        verification_revision=subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True
        ).strip(),
        seconds=time.perf_counter() - started,
    )
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True, default=json_default) + "\n",
        encoding="utf8",
        newline="\n",
    )
    print(json.dumps(dict(output=str(args.output), seconds=result["seconds"])))


if __name__ == "__main__":
    main()
