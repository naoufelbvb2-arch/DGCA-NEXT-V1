"""Declared genuine SIC curricula and pure P00 feasibility; no R04 writer."""

import argparse
import hashlib
import json
import sqlite3
import subprocess
import sys
import time
import tracemalloc
from contextlib import closing
from dataclasses import asdict
from pathlib import Path
from tempfile import TemporaryDirectory

from i3_final_integration import _allocated_bytes, _peak_rss_bytes

from dgca_next.dynamics.session import FeatureEvent, read_only_episode
from dgca_next.dynamics.state import GraphSnapshot
from dgca_next.graph.merge_split_analysis import analyze_merge, analyze_split
from dgca_next.learning.homeostasis_profile import LanguageHomeostasis
from dgca_next.persistence.reachability_inspection import (
    cooldown_alternatives,
    inspect_reachability,
)
from dgca_next.persistence.store import RootStore

ROOT = Path(__file__).resolve().parents[2]
MODE = "I4_NATIVE_MAINTAIN_GROW_V1"
A = (("a", "1"),)
MIX = (("a", "1"), ("f617", "1"))


def sha(data):
    return hashlib.sha256(data).hexdigest()


def _archive(path):
    with closing(sqlite3.connect(path)) as connection:
        return sha("\n".join(connection.iterdump()).encode())


def _checkpoint(store, path):
    before, h, file_bytes = store.view(), store.h_bytes(), path.read_bytes()
    archive = _archive(path)
    result = inspect_reachability(store)
    assert store.view() == before and store.h_bytes() == h
    assert _archive(path) == archive and path.read_bytes() == file_bytes
    assert not result.mutation_authorized
    return dict(
        inspection=asdict(result),
        archive_sha256=archive,
        file_sha256=sha(file_bytes),
        inspection_state_unchanged=True,
    )


def _root(store, identity, features, repeats):
    store.begin(identity)
    observations = []
    for order in range(repeats):
        e = store.event(identity, order, features)
        observations.append(
            dict(
                event_id=e.event_id,
                order=e.event_order,
                digest=e.digest,
                X_fixed=e.X_fixed,
                pass1_emitters=e.emitters,
                F_step=e.frontier,
                final=e.final,
                born=e.born,
            )
        )
    before, h = store.view(), store.h_bytes()
    try:
        close = store.end(identity)
        outcome = dict(
            status="COMPLETED",
            close_serial=close.close_serial,
            event_clock=close.event_clock,
            accepted_count=len(close.accepted),
            accepted=[
                dict(
                    source=p.key.source.cell_id,
                    target=p.key.target.cell_id,
                    scope=p.key.scope.value,
                    q=p.credit.q,
                    y=p.credit.y,
                )
                for p in close.accepted
            ],
        )
    except ValueError as exc:
        # A refusal is measured, never bypassed or converted into success.
        assert store.view() == before and store.h_bytes() == h
        assert store.root(identity).status == "OPEN"
        outcome = dict(
            status="OPEN",
            refusal=str(exc),
            end_rollback_exact=True,
            pending=[
                dict(
                    source=p.key.source.cell_id,
                    target=p.key.target.cell_id,
                    scope=p.key.scope.value,
                    q=p.credit.q,
                    y=p.credit.y,
                )
                for p in store.pending_proposals(identity)
            ],
        )
    return dict(root_id=identity, features=features, observations=observations, **outcome)


def _reopen(path, revision, expected):
    script = """
import json,sys
from dataclasses import asdict
from pathlib import Path
from dgca_next.persistence.store import RootStore
from dgca_next.persistence.reachability_inspection import inspect_reachability
s=RootStore(Path(sys.argv[1]),repository_root=Path(sys.argv[2]),code_revision=sys.argv[3],execution_mode='I4_NATIVE_MAINTAIN_GROW_V1')
print(json.dumps(asdict(inspect_reachability(s)),sort_keys=True))
s.close()
"""
    actual = json.loads(
        subprocess.check_output(
            [sys.executable, "-c", script, str(path), str(ROOT), revision], text=True
        )
    )
    assert actual == json.loads(json.dumps(expected["inspection"]))
    assert _archive(path) == expected["archive_sha256"]
    assert sha(path.read_bytes()) == expected["file_sha256"]
    return dict(
        independent_reopen_exact=True,
        W=actual["W_sha256"],
        H=actual["H_sha256"],
        R=actual["R_sha256"],
        completed_closes=actual["completed_closes"],
    )


def _curriculum(path, revision, name):
    store = RootStore(path, repository_root=ROOT, code_revision=revision, execution_mode=MODE)
    assert not store.graph().stored_cells() and not store.graph().synapses()
    assert not store.graph().native_assemblies()
    rows = []
    snapshots = []
    # A: accepted single cohort, reinforced beyond Q=.4, then passive root.
    # B: accepted cohort then witnessed admission of the overlapping f617 cohort.
    # C: simultaneous seven-receiver cohort from its first real EVENT.
    initial = MIX if name == "C_SIMULTANEOUS" else A
    for root in range(1, 5):
        row = _root(store, root, initial, 1 if root == 1 else 2)
        rows.append(row)
        snapshots.append(_checkpoint(store, path))
        if row["status"] != "COMPLETED":
            break
    if name != "C_SIMULTANEOUS":
        rows.append(_root(store, 5, A, 1))
        snapshots.append(_checkpoint(store, path))
        if name == "A_REINFORCED":
            rows.append(_root(store, 6, A, 2))
            snapshots.append(_checkpoint(store, path))
            w_before = store.view().W
            rows.append(_root(store, 7, (), 1))
            assert store.view().W == w_before
        else:
            rows.append(_root(store, 6, MIX, 1))
            snapshots.append(_checkpoint(store, path))
            for root in (7, 8, 9):
                row = _root(store, root, MIX, 2)
                rows.append(row)
                snapshots.append(_checkpoint(store, path))
                if row["status"] != "COMPLETED":
                    break
    final = _checkpoint(store, path)
    before, h = store.view(), store.h_bytes()
    snapshot = GraphSnapshot.capture(store.graph())
    profile = LanguageHomeostasis.decode(h).materialize(snapshot.committed_ids)
    read_only_episode(snapshot, profile, (FeatureEvent(A),), session_id=41)
    assert store.view() == before and store.h_bytes() == h
    result = dict(
        name=name,
        roots=rows,
        snapshots=snapshots,
        final=final,
        read_only_state_unchanged=True,
        database_bytes=path.stat().st_size,
        allocated_bytes=_allocated_bytes(path),
        automatic_recycling=store.graph().automatic_recycling_enabled,
        terminal_reason=rows[-1].get("refusal", "CURRENT_LAB_SINGLE_FOUR_MEMBER_ASSEMBLY"),
    )
    store.close()
    result["recovery"] = _reopen(path, revision, final)
    return result


def _clock_trial(path, revision):
    store = RootStore(path, repository_root=ROOT, code_revision=revision, execution_mode=MODE)
    completed = [_root(store, 1, A, 1), _root(store, 2, A, 5)]
    store.begin(3)
    for order in range(3):
        store.event(3, order, A)
    open_snapshot = _checkpoint(store, path)
    h_begin = store._backend._connection.execute(
        "SELECT h_begin FROM p01_roots WHERE exposure_id=3"
    ).fetchone()[0]
    store.abort(3)
    assert store.h_bytes() == h_begin
    final = _checkpoint(store, path)
    inspection = inspect_reachability(store)
    assert len(inspection.clock_history) == 2
    assert inspection.clock_history[-1].cumulative_completed_events == 6
    assert inspection.aborted_event_count == 3
    snapshot = GraphSnapshot.capture(store.graph())
    profile = LanguageHomeostasis.decode(store.h_bytes()).materialize(snapshot.committed_ids)
    before, h = store.view(), store.h_bytes()
    read_only_episode(snapshot, profile, (FeatureEvent(A),), session_id=42)
    assert store.view() == before and store.h_bytes() == h
    assert _checkpoint(store, path) == final
    # Reference zero is a numeric start-of-history comparison, NOT a real edit.
    alternatives = cooldown_alternatives(inspection.clock_history, 0)
    result = dict(
        completed_roots=completed,
        open_before_abort=open_snapshot,
        final=final,
        diagnostic_start_reference=asdict(alternatives),
        actual_merge_split_edits=0,
        read_only_created_roots=0,
        abort_H_BEGIN_exact=True,
    )
    store.close()
    result["recovery"] = _reopen(path, revision, final)
    return result


def component_benchmark():
    """Scalar-only examples, with no AssemblyID or NativeAssemblyRecord."""
    first = tuple(range(8192, 8198))
    second = (*first[:5], 8198)
    union = tuple(sorted(set(first) | set(second)))
    complete = {i: {j: 0.5 for j in union if i != j} for i in union}
    merge = analyze_merge(first, second, complete)
    members = tuple(range(8192, 8208))
    supports = {
        i: {j: 0.5 for j in members if i != j and (i < 8200) == (j < 8200)} for i in members
    }
    tracemalloc.start()
    started = time.perf_counter()
    split = analyze_split(members, supports)
    seconds = time.perf_counter() - started
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    assert split.examined == 32631 and split.best is not None
    assert not split.mutation_authorized and not merge.mutation_authorized
    return dict(
        evidence_kind="NUMERIC_ONLY",
        merge=asdict(merge),
        split16=asdict(split),
        seconds=seconds,
        peak_tracemalloc_bytes=peak,
        bound_members=16,
    )


def run_trial(directory):
    revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    started = time.perf_counter()
    curricula = [
        _curriculum(directory / f"{name}.sqlite", revision, name)
        for name in ("A_REINFORCED", "B_SEQUENTIAL_OVERLAP", "C_SIMULTANEOUS")
    ]
    clock = _clock_trial(directory / "clock.sqlite", revision)
    component = component_benchmark()
    return dict(
        code_revision=revision,
        curricula=curricula,
        clock=clock,
        component=component,
        seconds=time.perf_counter() - started,
        peak_parent_rss_bytes=_peak_rss_bytes(),
        native_merge_split_mutations=0,
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    with TemporaryDirectory() as directory:
        result = run_trial(Path(directory))
    if args.output:
        args.output.write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n"
        )
        print(
            json.dumps(
                dict(
                    output=str(args.output),
                    revision=result["code_revision"],
                    terminal_reasons=[c["terminal_reason"] for c in result["curricula"]],
                    seconds=result["seconds"],
                )
            )
        )
    else:
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
