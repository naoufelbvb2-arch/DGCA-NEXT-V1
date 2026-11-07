"""Bounded genuine FORM after terminal archive; source is an authenticated copy."""

import argparse
import json
import shutil
import subprocess
import time
from dataclasses import asdict
from pathlib import Path

from i4_final_lifecycle_closeout import write
from i4_r04_autonomous_forensics import file_sha
from i4_r04_autonomous_trial import run_root
from i4_r04_operator_execution import open_store, reopen, state


def run(args):
    receipt = json.loads(args.receipt.read_text(encoding="utf8"))
    expected = receipt["recovery"]["file_sha256"]
    assert file_sha(args.source) == expected and not args.database.exists()
    shutil.copy2(args.source, args.database)
    revision = receipt["database_initial_revision"]
    started = time.perf_counter()
    driver = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    s = open_store(args.database, revision)
    initial = s.graph()
    archived = tuple(a for a in initial.native_assemblies() if a.status == "ARCHIVED")
    assert {a.assembly_id for a in archived} == {0, 1}
    high = max(a.assembly_id for a in initial.native_assemblies())
    births = initial.native_form_log()
    rows = []
    first = s.view().high_watermark + 1
    formed = []
    for root in range(first, first + 9):
        row = run_root(s, root, [((("r04-merge-1746", "1"),), i == 0) for i in range(3)])
        rows.append(row)
        assert row["status"] == "COMPLETED"
        graph = s.graph()
        assert graph.native_form_log()[: len(births)] == births
        for old in archived:
            assert graph._state.native_assemblies[old.assembly_id] == old
            assert all(old.assembly_id not in c.assembly_ids for c in graph.stored_cells())
        formed = row["formed_ids"]
        print(json.dumps(dict(root=root, formed=formed)), flush=True)
        if formed:
            assert min(formed) > high
            break
    result = dict(
        classification="GENUINE_POST_ARCHIVE_FORM_SAME_LINEAGE_IDENTITY_CONTROL",
        database_initial_revision=revision,
        verification_revision=driver,
        source_sha256=expected,
        previous_high_watermark=high,
        original_archived_records=[asdict(a) for a in archived],
        roots=rows,
        formed_ids=formed,
        new_form_after_archive=bool(formed),
        archived_records_and_births_unchanged=True,
        after=state(s),
    )
    s.close()
    result["recovery"] = reopen(args.database, revision, result["after"])
    assert file_sha(args.source) == expected
    result["seconds"] = time.perf_counter() - started
    write(args.output, result)
    print(json.dumps(dict(formed=formed, seconds=result["seconds"])), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--database", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    run(parser.parse_args())
