"""Bounded final lifecycle continuations; only RootStore mutates production W."""

import argparse
import json
import shutil
import subprocess
import time
from dataclasses import asdict
from pathlib import Path

from i4_r04_autonomous_forensics import file_sha
from i4_r04_autonomous_trial import checkpoint, json_default
from i4_r04_operator_execution import open_store, reopen, state

from dgca_next.graph.assembly_support import inspect_structure
from dgca_next.graph.native_lifecycle import score
from dgca_next.graph.native_operator import read_operator
from dgca_next.graph.synapse import quality
from dgca_next.learning.native_multi import decode_operator_check
from dgca_next.persistence.native_codec import _base_graph

A01_FEATURES = (
    "r04-merge-820",
    "r04-merge-1746",
    "r04-merge-2233",
    "r04-merge-2430",
)


def schedule_a01():
    births = [(((f, "1"),), 1) for f in A01_FEATURES]
    learning = [(((f, "1"),), 3) for f in A01_FEATURES for _ in range(9)]
    return births + learning


def physics(s):
    graph = s.graph()
    supports = {}
    for pair in inspect_structure(_base_graph(graph)).pairs:
        if pair.edge:
            supports.setdefault(pair.first, {})[pair.second] = pair.support
            supports.setdefault(pair.second, {})[pair.first] = pair.support
    return dict(
        checkpoint=checkpoint(s),
        scores=[
            dict(
                assembly_id=a.assembly_id,
                generation=a.structural_generation,
                members=a.member_cell_ids,
                values=[asdict(score(i, a.member_cell_ids, supports)) for i in a.member_cell_ids],
            )
            for a in graph.native_assemblies()
            if a.status == "LIVE"
        ],
        physical_links=[
            dict(
                source=v.key.source.cell_id,
                target=v.key.target.cell_id,
                scope=v.key.scope.value,
                Q=quality(v),
                S=v.S,
                E_ext=v.E_ext,
                E_int=v.E_int,
                state=v.state.value,
                credits=[asdict(c) for c in v.credits],
            )
            for v in graph.synapses()
        ],
    )


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True, default=json_default) + "\n",
        encoding="utf8",
        newline="\n",
    )


def run_a01(args):
    receipt = json.loads(args.source_receipt.read_text(encoding="utf8"))
    expected_sha = receipt["recovery"]["file_sha256"]
    assert file_sha(args.source) == expected_sha
    assert not args.database.exists(), "FRESH_CONTINUATION_PATH_REQUIRED"
    args.database.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(args.source, args.database)
    revision = receipt["database_initial_revision"]
    started = time.perf_counter()
    s = open_store(args.database, revision)
    original = s.graph()
    old_links = {v.key: v for v in original.synapses()}
    births = original.native_form_log()
    result = dict(
        family="A01-r1",
        source_sha256=expected_sha,
        source_receipt=str(args.source_receipt),
        database_initial_revision=revision,
        verification_revision=subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True
        ).strip(),
        lineage="CONTINUATION_OF_ORIGINAL_R04_F05_R3_NOT_INDEPENDENT",
        initial=physics(s),
        roots=[],
        gate="EMPIRICAL_NOT_PROVEN",
    )
    write(args.output, result)
    first = s.view().high_watermark + 1
    for offset, (features, count) in enumerate(schedule_a01()):
        root = first + offset
        s.begin(root)
        events = []
        for order in range(count):
            e = s.event(root, order, features, boundary=order == 0)
            observed = asdict(e)
            observed.pop("raw")
            events.append(observed)
        before = state(s)
        pending = s.inspect_pending_native(root)
        archived = [
            e for e in pending.close.evaluations if e.stage == "MAINTAIN" and e.reason == "REMOVE"
        ]
        # A genuine OPEN checkpoint, not a caller-supplied graph or publication.
        if any(len(e.members) == 3 for e in archived):
            target = args.database.with_suffix(".before-archive.sqlite")
            assert not target.exists()
            shutil.copy2(args.database, target)
            result["pre_archive_source"] = dict(
                path=str(target), sha256=file_sha(target), root=root
            )
        close = s.end(root)
        assert s.h_bytes() and s.end(root) == close
        graph = s.graph()
        assert graph.native_form_log()[: len(births)] == births
        assert all(
            graph.synapse(k) is not None and graph.synapse(k).credits[: len(v.credits)] == v.credits
            for k, v in old_links.items()
        )
        mutations = [asdict(m) for m in graph.native_mutation_log() if m.exposure_id == root]
        row = dict(
            root_id=root,
            features=features,
            events=events,
            before_END=before,
            after_END=checkpoint(s),
            event_clock=close.event_clock,
            accepted=[asdict(p) for p in close.accepted],
            refused=[asdict(p) for p in close.refused],
            evaluations=[asdict(e) for e in close.evaluations],
            mutations=mutations,
            operator_checks=[decode_operator_check(c) for c in close.operator_checks],
            operators=[read_operator(r) for r in graph.native_operator_log()],
        )
        # Raw operator bytes are not needed; the immutable original log is hashed in W.
        row.pop("operators")
        result["roots"].append(row)
        terminal = any(m["stage"] == "ARCHIVE" for m in mutations)
        if terminal:
            result["gate"] = "PRODUCTION_ARCHIVE_OBSERVED_CONTROLS_PENDING"
        write(args.output, result)
        print(
            json.dumps(
                dict(
                    root=root, terminal_archive=terminal, assemblies=row["after_END"]["assemblies"]
                ),
                default=json_default,
            ),
            flush=True,
        )
        if terminal:
            break
    result["final"] = physics(s)
    final = state(s)
    s.close()
    result["recovery"] = reopen(args.database, revision, final)
    assert file_sha(args.source) == expected_sha
    result["original_source_unchanged"] = True
    result["seconds"] = time.perf_counter() - started
    write(args.output, result)
    print(json.dumps(dict(gate=result["gate"], seconds=result["seconds"])), flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--source-receipt", type=Path, required=True)
    parser.add_argument("--database", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    run_a01(parser.parse_args())


if __name__ == "__main__":
    main()
