"""Read-only R05 identity negatives on authenticated original R04 databases.

No operator is executed here. Historical R04 runtime did not contain native
Attractors; these checks do not claim an active Attractor survived an edit.
"""

import argparse
import hashlib
import json
from pathlib import Path

from dgca_next.graph.native_operator import read_operator
from dgca_next.persistence.attractor_store import inspect_native_subject, start_native_session
from dgca_next.persistence.store import RootStore

ROOT = Path(__file__).resolve().parents[2]


def run(path, receipt_path, out):
    reference = json.loads(receipt_path.read_text(encoding="utf-8"))
    store = RootStore(
        path,
        repository_root=ROOT,
        code_revision=reference["database_initial_revision"],
        execution_mode="I4_NATIVE_OPERATORS_V1",
    )
    before = store.view()
    h = store.h_bytes()
    graph = store.graph()
    records = [read_operator(op) for op in graph.native_operator_log()]
    assert records and before.completed_closes == reference["root_id"]
    session = start_native_session(store, session_id=200)
    assert not session.attractors
    refusals = []
    for op in records:
        for row in op["before"]:
            identity, generation = row[0], row[3]
            try:
                inspect_native_subject(store, identity, generation=generation)
            except ValueError as exc:
                refusals.append(
                    dict(
                        operator=op["operator"],
                        id=identity,
                        historical_generation=generation,
                        reason=str(exc),
                    )
                )
            else:
                raise AssertionError("STALE_OPERATOR_SUBJECT_ACCEPTED")
    assert all(
        r["reason"] in ("ARCHIVED_NATIVE_SUBJECT", "STALE_NATIVE_GENERATION") for r in refusals
    )
    assert store.view() == before and store.h_bytes() == h
    summary = dict(
        reference=str(receipt_path.resolve().relative_to(ROOT)),
        source=reference["database_initial_revision"],
        completed=before.completed_closes,
        W=hashlib.sha256(before.W).hexdigest(),
        H=hashlib.sha256(h).hexdigest(),
        R=hashlib.sha256(before.runtime).hexdigest(),
        refusals=refusals,
        unchanged=True,
        classification="AUTHENTICATED_HISTORICAL_IDENTITY_NEGATIVE_NOT_NEW_OPERATOR_EXECUTION",
    )
    store.close()
    out.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("database", type=Path)
    parser.add_argument("reference", type=Path)
    parser.add_argument("out", type=Path)
    args = parser.parse_args()
    run(args.database, args.reference, args.out)
