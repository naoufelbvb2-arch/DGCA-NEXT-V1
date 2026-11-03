"""Predeclared F01/F02 actual external curricula, not graph fixtures.

python tests/experiments/i4_r05_native_attractor_trace.py --family F01 --out DIR
Do not reuse output directories: independent trials start with an empty DB.
"""

import argparse
import base64
import hashlib
import json
import sqlite3
import subprocess
import sys
import time
from contextlib import closing
from dataclasses import asdict
from pathlib import Path

from dgca_next.dynamics.native_attractor import NativeFeatureEvent, ObservationScope
from dgca_next.dynamics.session import FeatureEvent
from dgca_next.graph.synapse import quality
from dgca_next.persistence.attractor_store import native_session_step, start_native_session
from dgca_next.persistence.native_runtime_codec import runtime_document
from dgca_next.persistence.store import RootStore

ROOT = Path(__file__).resolve().parents[2]
MODE = "I4_NATIVE_ATTRACTOR_V1"


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def opened(path, revision):
    return RootStore(path, repository_root=ROOT, code_revision=revision, execution_mode=MODE)


def summary(store):
    view = store.view()
    graph = store.graph()
    return dict(
        W=digest(view.W),
        H=digest(store.h_bytes()),
        R=digest(view.runtime),
        completed=view.completed_closes,
        high=view.high_watermark,
        open=view.open_root,
        cells=[c.cell_id for c in graph.stored_cells()],
        assemblies=[
            dict(
                id=a.assembly_id,
                generation=a.structural_generation,
                members=a.member_cell_ids,
                status=a.status,
            )
            for a in graph.native_assemblies()
        ],
    )


def copy_database(source, target):
    with closing(sqlite3.connect(source)) as src, closing(sqlite3.connect(target)) as dst:
        src.backup(dst)


def trace_document(trace):
    def values(m):
        return dict(m)

    def passes(p):
        return {k: values(getattr(p, k)) for k in ("raw", "normalized", "activity")}

    return dict(
        sigma=values(trace.sigma),
        temporal=values(trace.temporal),
        boundary=trace.boundary,
        fresh_first=passes(trace.fresh.first),
        fresh_second=passes(trace.fresh.second),
        normal_first=passes(trace.passes.first),
        normal_second=passes(trace.passes.second),
        evaluations=list(trace.evaluations),
        attractors=[asdict(a) for a in trace.state.attractors],
        scope=trace.scope.value,
    )


def readonly_controls(store, feature):
    before = summary(store)
    caller = store.view().runtime
    cold = start_native_session(store, session_id=100)
    result = {}
    for value in ("1", "0.4", "0.2"):
        trace = native_session_step(
            store, cold, NativeFeatureEvent(FeatureEvent(((feature, value),)))
        )
        result[value] = trace_document(trace)
    initial = native_session_step(store, cold, NativeFeatureEvent(FeatureEvent(((feature, "1"),))))
    state = initial.state
    result["age"] = [trace_document(initial)]
    for _ in range(30):
        trace = native_session_step(
            store, state, NativeFeatureEvent(FeatureEvent(((feature, "1"),)))
        )
        result["age"].append(trace_document(trace))
        state = trace.state
    result["empty"] = trace_document(
        native_session_step(store, initial.state, NativeFeatureEvent(FeatureEvent(())))
    )
    result["boundary"] = trace_document(
        native_session_step(
            store, initial.state, NativeFeatureEvent(FeatureEvent(((feature, "1"),), boundary=True))
        )
    )
    event = NativeFeatureEvent(FeatureEvent(((feature, "0.2"),)))
    on = native_session_step(store, initial.state, event)
    off = native_session_step(store, initial.state, event, context_sigma=False)
    result["ablation"] = dict(
        source=before,
        on=trace_document(on),
        off=trace_document(off),
        fresh_equal=on.fresh == off.fresh,
        final_l1=sum(
            abs(on.passes.second.activity[i] - off.passes.second.activity[i])
            for i in on.passes.second.activity
        ),
        raw_l1=sum(
            abs(on.passes.first.raw[i] - off.passes.first.raw[i]) for i in on.passes.first.raw
        ),
    )
    result["invariance"] = before == summary(store) and caller == store.view().runtime
    return result


def run(family, out):
    if out.exists():
        raise ValueError("FRESH_TRIAL_DIRECTORY_REQUIRED")
    out.mkdir(parents=True)
    revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    path = out / "production.sqlite"
    started = time.perf_counter()
    store = opened(path, revision)
    result = dict(family=family, revision=revision, zero_state=summary(store), roots=[], events=[])
    assert not store.graph().stored_cells() and not store.graph().synapses()
    feature = "a" if family == "F01" else "ab"
    last_training = 5 if family == "F01" else 12
    for root in range(1, last_training + 1):
        store.begin(root)
        for order in range(1 if root == 1 or (family == "F01" and root == 5) else 2):
            store.event(root, order, ((feature, "1"),))
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
        if root == 4 or root == last_training:
            copy_database(path, out / f"root-{root}.sqlite")
    result["learned_links"] = [
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
    result["readonly"] = readonly_controls(store, feature)
    if family == "F01":
        store.begin(6)
        for order in range(33):
            store.event(6, order, () if order == 2 else ((feature, "1"),), boundary=order == 32)
            result["events"].append(runtime_document(store.view().runtime))
        store.end(6)
        result["roots"].append(dict(root=6, state=summary(store)))
    error_root = 7 if family == "F01" else 13
    store.begin(error_root)
    for order in range(10):
        value = "1" if order in (0, 1, 3) else "0.1"
        store.event(
            error_root,
            order,
            ((feature, value),),
            observation_scope=ObservationScope.COMPLETE_NEXT_EVENT,
        )
        result["events"].append(runtime_document(store.view().runtime))
    store.end(error_root)
    result["roots"].append(dict(root=error_root, state=summary(store)))
    result["final"] = summary(store)
    result["final_W_base64"] = base64.b64encode(store.view().W).decode("ascii")
    result["final_H_base64"] = base64.b64encode(store.h_bytes()).decode("ascii")
    store.close()
    child = subprocess.run(
        [
            sys.executable,
            str(Path(__file__).resolve()),
            "--verify",
            str(path),
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
    print(json.dumps(dict(family=family, seconds=result["seconds"], final=result["final"])))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--family", choices=("F01", "F02"))
    parser.add_argument("--out", type=Path)
    parser.add_argument("--verify", type=Path)
    parser.add_argument("--revision")
    args = parser.parse_args()
    if args.verify:
        store = opened(args.verify, args.revision)
        print(json.dumps(summary(store), sort_keys=True))
        store.close()
    else:
        run(args.family, args.out)
