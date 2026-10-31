"""Cold Schema-5 production FORM and independent-process recovery trace."""

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

from dgca_next.contracts import Region, SynapseScope
from dgca_next.dynamics.session import FeatureEvent, read_only_episode
from dgca_next.dynamics.state import GraphSnapshot
from dgca_next.learning.homeostasis_profile import LanguageHomeostasis
from dgca_next.persistence.store import RootStore

ROOT = Path(__file__).resolve().parents[2]
MODE = "I4_NATIVE_FORM_V1"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def run_trial(path, *, measure_memory=False):
    revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    started = time.perf_counter()
    if measure_memory:
        tracemalloc.start()

    def open_store():
        return RootStore(path, repository_root=ROOT, code_revision=revision, execution_mode=MODE)

    store = open_store()
    assert not store.graph().stored_cells() and not store.graph().native_assemblies()
    assert not store.graph().synapses()
    progression = []
    for root in range(1, 5):
        store.begin(root)
        for order in range(1 if root == 1 else 2):
            store.event(root, order, (("a", "1"),))
        before = store.view()
        assert not store.graph().native_assemblies()
        if root == 4:
            pre_end_w = before.W
            pre_end_h = store.h_bytes()
            store.close()
            crash_script = """
import os, sys
from pathlib import Path
from dgca_next.persistence.store import RootStore
s=RootStore(Path(sys.argv[1]),repository_root=Path(sys.argv[2]),code_revision=sys.argv[3],execution_mode='I4_NATIVE_FORM_V1')
def crash(stage):
    if stage == sys.argv[4]: os._exit(31)
s.end(4,hook=crash)
"""
            for phase in ("BEFORE_COMMIT", "AFTER_COMMIT"):
                process = subprocess.run(
                    [sys.executable, "-c", crash_script, str(path), str(ROOT), revision, phase]
                )
                assert process.returncode == 31
                store = open_store()
                if phase == "BEFORE_COMMIT":
                    assert store.view() == before and not store.graph().native_assemblies()
                else:
                    assert len(store.graph().native_assemblies()) == 1
                store.close()
            store = open_store()
        close = store.end(root)
        graph = store.graph()
        local = [s for s in graph.synapses() if s.key.scope is SynapseScope.LOCAL]
        progression.append(
            {
                "root": root,
                "serial": close.close_serial,
                "form_reason": close.form_reason,
                "formed_ids": close.formed_ids,
                "W_sha256": sha(store.view().W),
                "H_sha256": sha(store.h_bytes()),
                "local_count": len(local),
                "local_states": sorted({s.state.value for s in local}),
                "local_mass": sorted({s.E_ext for s in local}),
            }
        )
    assert close.formed_ids == (0,)
    graph = store.graph()
    (assembly,) = graph.native_assemblies()
    (proof,) = graph.native_form_log()
    assert assembly.member_cell_ids == (8606, 9345, 11795)
    final = store.view()
    h = store.h_bytes()
    assert pre_end_h == h and sha(pre_end_w) != sha(final.W)
    assert store.end(4) == close and store.view() == final
    diagnostic = store.inspect_form_eligibility(4)
    selected = diagnostic.projected_seeds[0]
    assert selected.triangle.members == assembly.member_cell_ids
    assert diagnostic.source_w_hash == proof.post_evidence_w_hash
    snapshot = GraphSnapshot.capture(graph)
    homeostasis = LanguageHomeostasis.decode(h).materialize(snapshot.committed_ids)
    read = read_only_episode(snapshot, homeostasis, (FeatureEvent((("a", "1"),)),), session_id=9)[0]
    assert read.synchronous and store.view() == final
    with closing(sqlite3.connect(path)) as connection:
        archive = sha("\n".join(connection.iterdump()).encode())
        schema = connection.execute("SELECT schema_version FROM p01_metadata").fetchone()[0]
    result = {
        "code_revision": revision,
        "execution_mode": MODE,
        "schema": schema,
        "input_features": [["a", "1"]],
        "roots": progression,
        "assembly": asdict(assembly) | {"region": assembly.region.value},
        "form_provenance": asdict(proof),
        "structural_triangle": asdict(selected.triangle),
        "event_witnesses": [asdict(e) for e in diagnostic.events],
        "member_reverse": [
            [i, sorted(graph.member_assemblies(i))] for i in assembly.member_cell_ids
        ],
        "high_watermark": graph._state.assembly_high_watermarks[Region.LANGUAGE],
        "W_before_END": sha(pre_end_w),
        "W_after_END": sha(final.W),
        "H_after_END": sha(h),
        "R_after_END": sha(final.runtime),
        "archive_sha256": archive,
        "max_read_only_synchronous": max(read.synchronous.values()),
        "automatic_recycling_enabled": graph.automatic_recycling_enabled,
        "database_bytes": path.stat().st_size,
        "database_allocated_bytes": _allocated_bytes(path),
    }
    store.close()
    load_script = """
import json, hashlib, sys
from pathlib import Path
from dgca_next.persistence.store import RootStore
s=RootStore(Path(sys.argv[1]),repository_root=Path(sys.argv[2]),code_revision=sys.argv[3],execution_mode='I4_NATIVE_FORM_V1')
a,=s.graph().native_assemblies()
print(json.dumps({'id':a.assembly_id,'generation':a.structural_generation,'members':a.member_cell_ids,'serial':s.view().completed_closes,'W':hashlib.sha256(s.view().W).hexdigest(),'H':hashlib.sha256(s.h_bytes()).hexdigest()}))
s.close()
"""
    independent = json.loads(
        subprocess.check_output(
            [sys.executable, "-c", load_script, str(path), str(ROOT), revision], text=True
        )
    )
    assert independent["id"] == 0 and independent["generation"] == 1
    assert independent["members"] == list(assembly.member_cell_ids) and independent["serial"] == 4
    assert independent["W"] == result["W_after_END"] and independent["H"] == result["H_after_END"]
    result["independent_process"] = independent
    result["seconds"] = time.perf_counter() - started
    if measure_memory:
        _, result["peak_tracemalloc_bytes"] = tracemalloc.get_traced_memory()
        tracemalloc.stop()
    result["peak_rss_bytes"] = _peak_rss_bytes()
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    with TemporaryDirectory() as directory:
        result = run_trial(Path(directory) / "native.sqlite", measure_memory=True)
    data = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(data, encoding="utf-8", newline="\n")
        print(
            json.dumps(
                {
                    "output": str(args.output),
                    "revision": result["code_revision"],
                    "assembly": result["assembly"],
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
