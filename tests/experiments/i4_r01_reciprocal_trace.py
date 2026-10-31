"""Reproduce R01 using only cold production RootStore external events."""

import argparse
import hashlib
import json
import sqlite3
import subprocess
import time
import tracemalloc
from contextlib import closing
from dataclasses import asdict
from pathlib import Path
from tempfile import TemporaryDirectory

from i3_final_integration import _allocated_bytes, _peak_rss_bytes

from dgca_next.graph import SparseNetwork
from dgca_next.graph.assembly_support import inspect_structure
from dgca_next.persistence.store import RootStore

ROOT = Path(__file__).resolve().parents[2]


def _sha(value):
    return hashlib.sha256(value).hexdigest()


def _archive(path):
    with closing(sqlite3.connect(path)) as connection:
        return _sha("\n".join(connection.iterdump()).encode("utf-8"))


def run_trial(path, *, measure_memory=False):
    started = time.perf_counter()
    revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    if measure_memory:
        tracemalloc.start()
    empty_started = time.perf_counter()
    assert inspect_structure(SparseNetwork()).triangles == ()
    empty_seconds = time.perf_counter() - empty_started
    store = RootStore(path, repository_root=ROOT, code_revision=revision)
    assert not store.graph().synapses() and not store.graph().stored_cells()
    roots = []
    for root in range(1, 5):
        store.begin(root)
        observations = []
        for order in range(1 if root == 1 else 2):
            event = store.event(root, order, (("a", "1"),))
            observations.append(
                {
                    "id": event.event_id,
                    "order": order,
                    "born": event.born,
                    "deferred": event.deferred,
                    "origin": event.origin.value,
                    "mode": event.mode.value,
                    "observation_digest": event.digest,
                }
            )
        close = store.end(root)
        before, h_before = store.view(), store.h_bytes()
        archive_before, file_before = _archive(path), _sha(path.read_bytes())
        structural_before = store.graph().structural_hash
        inspection_started = time.perf_counter()
        result = store.inspect_form_eligibility(root)
        inspect_seconds = time.perf_counter() - inspection_started
        assert store.view() == before and store.h_bytes() == h_before
        assert _archive(path) == archive_before and _sha(path.read_bytes()) == file_before
        assert store.graph().structural_hash == structural_before
        assert all(not cell.assembly_ids for cell in store.graph().stored_cells())
        roots.append(
            {
                "exposure_id": root,
                "close_serial": close.close_serial,
                "observations": observations,
                "reason": result.reason,
                "W_sha256": result.source_w_hash,
                "H_sha256": result.source_h_hash,
                "current_W_sha256": _sha(before.W),
                "current_H_sha256": _sha(h_before),
                "R_sha256": _sha(before.runtime),
                "graph_hash": structural_before,
                "archive_sha256": archive_before,
                "database_sha256": file_before,
                "read_only_identical": True,
                "inspect_seconds": inspect_seconds,
                "reciprocal_pairs": [asdict(pair) for pair in result.structure.pairs],
                "triangles": [
                    {
                        "members": triangle.members,
                        "cells": [asdict(c) for c in triangle.cells],
                        "reasons": triangle.reasons,
                    }
                    for triangle in result.structure.triangles
                ],
                "events": [asdict(event) for event in result.events],
                "candidates": [
                    {
                        "event_id": c.event_id,
                        "event_order": c.event_order,
                        "members": c.triangle.members,
                        "reasons": c.reasons,
                        "selected": c.selected,
                    }
                    for c in result.candidates
                ],
            }
        )
    before = store.view()
    final_h = store.h_bytes()
    store.close()
    reopen_started = time.perf_counter()
    store = RootStore(path, repository_root=ROOT, code_revision=revision)
    cold_result = store.inspect_form_eligibility(4)
    cold_seconds = time.perf_counter() - reopen_started
    assert cold_result == result and store.view() == before and store.h_bytes() == final_h
    assert _archive(path) == archive_before and _sha(path.read_bytes()) == file_before
    assert not store.graph().automatic_recycling_enabled
    store.close()
    output = {
        "code_revision": revision,
        "input_features": [["a", "1"]],
        "config_hash": result.config_hash,
        "core_hash": result.core_hash,
        "lla_hash": result.lla_hash,
        "roots": roots,
        "cold_inspection_identical": True,
        "cold_reopen_inspect_seconds": cold_seconds,
        "empty_inspect_seconds": empty_seconds,
        "database_bytes": path.stat().st_size,
        "database_allocated_bytes": _allocated_bytes(path),
        "seconds": time.perf_counter() - started,
        "peak_rss_bytes": _peak_rss_bytes(),
    }
    if measure_memory:
        _, output["peak_tracemalloc_bytes"] = tracemalloc.get_traced_memory()
        tracemalloc.stop()
    return output


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    with TemporaryDirectory() as directory:
        result = run_trial(Path(directory) / "r01.sqlite", measure_memory=True)
    data = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output is not None:
        args.output.write_text(data, encoding="utf-8", newline="\n")
        print(
            json.dumps(
                {
                    "output": str(args.output),
                    "revision": result["code_revision"],
                    "reason": result["roots"][-1]["reason"],
                    "seconds": result["seconds"],
                    "database_bytes": result["database_bytes"],
                    "peak_tracemalloc_bytes": result["peak_tracemalloc_bytes"],
                    "peak_rss_bytes": result["peak_rss_bytes"],
                },
                sort_keys=True,
            )
        )
    else:
        print(data, end="")


if __name__ == "__main__":
    main()
