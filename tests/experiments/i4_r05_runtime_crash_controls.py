"""Bounded process exits on copies of the actual F01 root5 lineage.

Copies are transaction controls, never additional independent learning roots.
"""

import argparse
import hashlib
import json
import sqlite3
import subprocess
import sys
import time
from contextlib import closing
from pathlib import Path

from dgca_next.persistence.native_runtime_codec import runtime_document
from dgca_next.persistence.store import R_COLD, RootStore

ROOT = Path(__file__).resolve().parents[2]
MODE = "I4_NATIVE_ATTRACTOR_V1"


def open_store(path, revision):
    return RootStore(path, repository_root=ROOT, code_revision=revision, execution_mode=MODE)


def hashes(store):
    view = store.view()
    return {
        k: hashlib.sha256(v).hexdigest()
        for k, v in (("W", view.W), ("H", store.h_bytes()), ("R", view.runtime))
    }


def run(source, revision, out):
    if out.exists():
        raise ValueError("FRESH_CONTROL_DIRECTORY_REQUIRED")
    out.mkdir(parents=True)
    started = time.perf_counter()
    cases = []
    for operation in ("event", "end", "abort"):
        for phase in ("BEFORE_COMMIT", "AFTER_COMMIT"):
            path = out / f"{operation}-{phase}.sqlite"
            with closing(sqlite3.connect(source)) as src, closing(sqlite3.connect(path)) as dst:
                src.backup(dst)
            store = open_store(path, revision)
            source_hashes = hashes(store)
            assert store.view().completed_closes == 5
            h_begin = store.h_bytes()
            store.begin(6)
            store.event(6, 0, (("a", "1"),))
            store.event(6, 1, (("a", "1"),))
            before = hashes(store)
            before_r = runtime_document(store.view().runtime)
            store.close()
            action = (
                "s.event(6,2,(('a','0.1'),),observation_scope=ObservationScope.COMPLETE_NEXT_EVENT,hook=hook)"
                if operation == "event"
                else f"s.{operation}(6,hook=hook)"
            )
            code = (
                "import os; from pathlib import Path; "
                "from dgca_next.persistence.store import RootStore; "
                "from dgca_next.dynamics.native_attractor import ObservationScope; "
                f"s=RootStore(Path({str(path.resolve())!r}),repository_root=Path({str(ROOT)!r}),"
                f"code_revision={revision!r},execution_mode={MODE!r}); "
                f"hook=lambda p: os._exit(41) if p=={phase!r} else None; " + action
            )
            child = subprocess.run(
                [sys.executable, "-c", code], cwd=ROOT, capture_output=True, text=True
            )
            assert child.returncode == 41, child.stderr
            recovered = open_store(path, revision)
            after = hashes(recovered)
            root = recovered.root(6)
            case = dict(
                operation=operation,
                phase=phase,
                before=before,
                after=after,
                source=source_hashes,
                status=root.status,
                order=root.next_order,
                process_exit=child.returncode,
            )
            if phase == "BEFORE_COMMIT":
                assert before == after and root.status == "OPEN" and root.next_order == 2
                assert runtime_document(recovered.view().runtime) == before_r
                case["exact_previous_checkpoint"] = True
            elif operation == "event":
                native = runtime_document(recovered.view().runtime)
                assert root.next_order == 3 and native["state"]["attractors"][0][4] == 1
                evaluation = native["evaluations"][0]
                assert evaluation["comparables"] and evaluation["miss"] > 0
                assert native["state"]["attractors"][0][-1] == evaluation["miss"]
                assert after["W"] == before["W"]
                case["runtime"] = dict(state=native["state"], evaluations=native["evaluations"])
            elif operation == "end":
                assert root.status == "COMPLETED" and recovered.view().runtime == R_COLD
                close = recovered.end(6)
                assert close == recovered.end(6) and after == hashes(recovered)
                case["idempotent_END"] = True
            else:
                assert root.status == "ABORTED" and recovered.view().runtime == R_COLD
                assert recovered.h_bytes() == h_begin
                assert after["W"] == before["W"]
                case["exact_H_BEGIN"] = True
            case["database_bytes"] = path.stat().st_size
            recovered.close()
            cases.append(case)
    result = dict(
        classification="GENUINE_LINEAGE_FAILURE_CONTROLS_NOT_INDEPENDENT_LEARNING_EVIDENCE",
        original_family="F01-r2",
        original_revision=revision,
        driver_revision=subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        original_completed_roots=[1, 2, 3, 4, 5],
        cases=cases,
        seconds=time.perf_counter() - started,
    )
    (out / "receipt.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(dict(cases=len(cases), seconds=result["seconds"], passed=True)))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("revision")
    parser.add_argument("out", type=Path)
    args = parser.parse_args()
    run(args.source, args.revision, args.out)
