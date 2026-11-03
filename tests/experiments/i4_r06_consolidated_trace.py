"""Declared F03-r1 integrated production verification, after the R05 local gate."""

import argparse
import base64
import json
import subprocess
import sys
import time
from dataclasses import asdict
from pathlib import Path

from i4_r05_native_attractor_trace import copy_database, opened, readonly_controls, summary

from dgca_next.dynamics.native_attractor import ObservationScope
from dgca_next.graph.assembly_support import inspect_structure
from dgca_next.graph.merge_split_analysis import analyze_split
from dgca_next.graph.synapse import quality
from dgca_next.persistence.native_codec import _base_graph
from dgca_next.persistence.native_runtime_codec import runtime_document
from dgca_next.persistence.store import R_COLD

ROOT = Path(__file__).resolve().parents[2]


def run(out):
    gate = json.loads(
        (ROOT / "docs/implementation/evidence/i4-r05-r06/R05-LOCAL-GATE.json").read_text()
    )
    if gate["status"] != "LOCAL_R05_PASS" or not all(v["passed"] for v in gate["gates"].values()):
        raise ValueError("R05_LOCAL_GATE_REQUIRED_BEFORE_R06")
    if out.exists():
        raise ValueError("FRESH_R06_TRIAL_DIRECTORY_REQUIRED")
    out.mkdir(parents=True)
    revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    started = time.perf_counter()
    path = out / "production.sqlite"
    store = opened(path, revision)
    result = dict(
        family="F03-r1",
        revision=revision,
        local_gate=gate["source_head"],
        zero=summary(store),
        roots=[],
        events=[],
    )
    assert not store.graph().stored_cells() and not store.graph().synapses()
    for root in range(1, 6):
        store.begin(root)
        for order in range(1 if root in (1, 5) else 2):
            store.event(root, order, (("a", "1"),))
            result["events"].append(runtime_document(store.view().runtime))
        close = store.end(root)
        result["roots"].append(
            dict(
                root=root,
                state=summary(store),
                formed=close.formed_ids,
                mutations=close.mutation_ordinals,
            )
        )
    copy_database(path, out / "root-5.sqlite")
    before = summary(store)
    store.begin(6)
    w_before = store.view().W
    for order in range(10):
        value = "1" if order in (0, 1, 3) else "0.1"
        store.event(
            6, order, (("a", value),), observation_scope=ObservationScope.COMPLETE_NEXT_EVENT
        )
        result["events"].append(runtime_document(store.view().runtime))
        assert store.view().W == w_before
    receiver = store.observation(6, 2).X_fixed[0][0]
    pre_inspection = store.view()
    result["provisional_novelty"] = asdict(store.verified_local_novelty(6, 2, receiver))
    assert pre_inspection == store.view()
    store.end(6)
    result["completed_novelty"] = asdict(store.verified_local_novelty(6, 2, receiver))
    assert result["completed_novelty"]["status"] == "COMPLETED"
    result["roots"].append(dict(root=6, state=summary(store), pre_root=before))
    result["links"] = [
        dict(
            source=s.key.source.cell_id,
            target=s.key.target.cell_id,
            scope=s.key.scope.name,
            state=s.state.name,
            Q=quality(s),
            S=s.S,
            E_ext=s.E_ext,
            E_int=s.E_int,
            count=s.external_root_count,
            credits=[asdict(c) for c in s.credits],
        )
        for s in store.graph().synapses()
    ]
    h_begin, w_begin = store.h_bytes(), store.view().W
    store.begin(7)
    for order in range(2):
        store.event(7, order, (("a", "1"),))
        result["events"].append(runtime_document(store.view().runtime))
    store.abort(7)
    assert store.h_bytes() == h_begin and store.view().W == w_begin
    assert store.view().runtime == R_COLD and store.view().completed_closes == 6
    assert all(c.root_id != 7 for s in store.graph().synapses() for c in s.credits)
    result["abort"] = dict(
        root=7,
        H_BEGIN_base64=base64.b64encode(h_begin).decode("ascii"),
        H_restored_exact=True,
        W_and_evidence_unchanged=True,
    )
    result["readonly"] = readonly_controls(store, "a")
    graph = store.graph()
    physical = inspect_structure(_base_graph(graph))
    supports = {}
    for pair in physical.pairs:
        if pair.forward.reason == pair.reverse.reason == "QUALIFIED":
            supports.setdefault(pair.first, {})[pair.second] = pair.support
            supports.setdefault(pair.second, {})[pair.first] = pair.support
    live = [a for a in graph.native_assemblies() if a.status == "LIVE"]
    result["structural_limit"] = dict(
        live_assemblies=len(live),
        merge_pair_available=len(live) >= 2,
        split_reasons=[
            list(
                analyze_split(
                    a.member_cell_ids,
                    supports,
                    membership_counts={
                        c.cell_id: len(c.assembly_ids) for c in graph.stored_cells()
                    },
                ).reasons
            )
            for a in live
        ],
        no_operator_executed=True,
        automatic_recycling=graph.automatic_recycling_enabled,
    )
    result["final"] = summary(store)
    result["W_base64"] = base64.b64encode(store.view().W).decode("ascii")
    result["H_base64"] = base64.b64encode(store.h_bytes()).decode("ascii")
    store.close()
    child = subprocess.run(
        [
            sys.executable,
            str(ROOT / "tests/experiments/i4_r05_native_attractor_trace.py"),
            "--verify",
            str(path.resolve()),
            "--revision",
            revision,
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    result["cold_process"] = json.loads(child.stdout)
    assert result["cold_process"] == result["final"]
    result["seconds"] = time.perf_counter() - started
    result["database_bytes"] = path.stat().st_size

    def default(value):
        if type(value) is bytes:
            return {"base64": base64.b64encode(value).decode("ascii")}
        raise TypeError(type(value).__name__)

    (out / "receipt.json").write_text(
        json.dumps(result, default=default, sort_keys=True, indent=2) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(dict(family=result["family"], seconds=result["seconds"], final=result["final"]))
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("out", type=Path)
    args = parser.parse_args()
    run(args.out)
