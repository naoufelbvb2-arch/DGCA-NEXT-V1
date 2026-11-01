"""Predeclared bounded RootStore trials; no fixture or hand-built connection."""

import argparse
import hashlib
import json
import sqlite3
import subprocess
import sys
import time
from contextlib import closing
from dataclasses import asdict
from pathlib import Path

from dgca_next.dynamics.session import FeatureEvent, read_only_episode
from dgca_next.dynamics.state import GraphSnapshot
from dgca_next.graph.assembly_support import inspect_structure
from dgca_next.graph.synapse import quality
from dgca_next.learning.completed_event_clock import _verified_completed_prefix
from dgca_next.learning.homeostasis_profile import LanguageHomeostasis
from dgca_next.learning.native_multi import (
    UnprovenNativeOperator,
    decode_multi_close,
    decode_operator_check,
)
from dgca_next.peripheral.sic import receiver_ids
from dgca_next.persistence.native_codec import _base_graph
from dgca_next.persistence.store import RootStore

ROOT = Path(__file__).resolve().parents[2]
MODE = "I4_NATIVE_MULTI_V1"
A = (("a", "1"),)
MIX = (*A, ("f617", "1"))


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def open_store(path, revision):
    return RootStore(path, repository_root=ROOT, code_revision=revision, execution_mode=MODE)


def archive_hash(path):
    with closing(sqlite3.connect(path)) as db:
        return sha("\n".join(db.iterdump()).encode())


def checkpoint(s):
    v = s.view()
    return dict(
        W_sha256=sha(v.W),
        H_sha256=sha(s.h_bytes()),
        R_sha256=sha(v.runtime),
        completed_closes=v.completed_closes,
        open_root=v.open_root,
        assemblies=[asdict(a) for a in s.graph().native_assemblies()],
    )


def run_root(s, identity, events):
    s.begin(identity)
    observations = []
    for order, (features, boundary) in enumerate(events):
        e = s.event(identity, order, tuple(features), boundary=boundary)
        observations.append(
            dict(
                event_id=e.event_id,
                order=e.event_order,
                digest=e.digest,
                features=features,
                boundary=boundary,
                X_fixed=e.X_fixed,
                pass1_emitters=e.emitters,
                final=e.final,
                F_step=e.frontier,
                born=e.born,
            )
        )
    before, h = s.view(), s.h_bytes()
    try:
        close = s.end(identity)
        outcome = dict(
            status="COMPLETED",
            close_serial=close.close_serial,
            event_clock=close.event_clock,
            formed_ids=close.formed_ids,
            mutation_ordinals=close.mutation_ordinals,
            evaluations=[asdict(e) for e in close.evaluations],
            operator_checks=[decode_operator_check(b) for b in close.operator_checks],
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
            refused_count=len(close.refused),
        )
    except ValueError as exc:
        assert s.view() == before and s.h_bytes() == h and s.root(identity).status == "OPEN"
        outcome = dict(status="OPEN", refusal=str(exc), END_rollback_exact=True)
        if isinstance(exc, UnprovenNativeOperator):
            p = s.inspect_pending_native(identity)
            assert p.W == exc.provisional_W and p.close == exc.provisional_close
            outcome["provisional_only"] = dict(
                committed=False,
                W_sha256=sha(p.W),
                operator_checks=[decode_operator_check(b) for b in p.close.operator_checks],
                evaluations=[asdict(e) for e in p.close.evaluations],
            )
    return dict(root_id=identity, observations=observations, state=checkpoint(s), **outcome)


def events(features, count):
    return [(features, False)] * count


def final_evidence(s):
    g = s.graph()
    before, h = s.view(), s.h_bytes()
    structure = inspect_structure(_base_graph(g))
    profile = LanguageHomeostasis.decode(h).materialize(tuple(c.cell_id for c in g.stored_cells()))
    # In an OPEN-root refusal, readonly runtime is deliberately unavailable.
    if before.open_root is None:
        read_only_episode(GraphSnapshot.capture(g), profile, (FeatureEvent(A),), session_id=41)
    assert s.view() == before and s.h_bytes() == h
    return dict(
        state=checkpoint(s),
        committed_cells=[c.cell_id for c in g.stored_cells()],
        forms=[asdict(b) for b in g.native_form_log()],
        mutations=[asdict(b) for b in g.native_mutation_log()],
        reciprocal_pairs=[asdict(p) for p in structure.pairs],
        synapses=[
            dict(
                source=v.key.source.cell_id,
                target=v.key.target.cell_id,
                scope=v.key.scope.value,
                state=v.state.value,
                Q=quality(v),
                S=v.S,
                E_ext=v.E_ext,
                E_int=v.E_int,
                external_root_count=v.external_root_count,
                credits=[asdict(c) for c in v.credits],
            )
            for v in g.synapses()
        ],
        read_only_unchanged=True,
        automatic_recycling=g.automatic_recycling_enabled,
    )


def recover(path, revision, expected):
    script = """
import sys,json,hashlib
from pathlib import Path
from dgca_next.persistence.store import RootStore
s=RootStore(Path(sys.argv[1]),repository_root=Path(sys.argv[2]),code_revision=sys.argv[3],execution_mode='I4_NATIVE_MULTI_V1')
v=s.view()
print(json.dumps([hashlib.sha256(v.W).hexdigest(),hashlib.sha256(s.h_bytes()).hexdigest(),v.completed_closes,v.open_root]))
s.close()
"""
    before, archive = path.read_bytes(), archive_hash(path)
    actual = json.loads(
        subprocess.check_output(
            [sys.executable, "-c", script, str(path), str(ROOT), revision], text=True
        )
    )
    assert actual == [
        expected["W_sha256"],
        expected["H_sha256"],
        expected["completed_closes"],
        expected["open_root"],
    ]
    assert path.read_bytes() == before and archive_hash(path) == archive
    return dict(
        cold_process_replay_exact=True,
        file_sha256=sha(before),
        archive_sha256=archive,
        database_bytes=len(before),
    )


def disjoint_features():
    chosen, used = [], set()
    for n in range(64):
        feature = f"r04-cap-{n}"
        cells = set(receiver_ids(feature))
        if len(cells) == 4 and not cells & used:
            chosen.append(feature)
            used.update(cells)
        if len(chosen) == 13:
            break
    assert len(chosen) == 13, "DECLARED_FEATURE_SCREEN_EXHAUSTED"
    return chosen


def curriculum(path, revision, family):
    s = open_store(path, revision)
    assert not s.graph().synapses() and not s.graph().stored_cells()
    rows = []
    selected = disjoint_features() if family == "F04" else []
    inputs = dict(selected_features=[dict(feature=f, receivers=receiver_ids(f)) for f in selected])
    # This file is written BEFORE the first external EVENT is presented.
    path.with_suffix(".declaration.json").write_text(
        json.dumps(inputs, sort_keys=True), encoding="utf8"
    )
    if family == "F04":
        for r in range(1, 6):
            features = selected[-1:] if r == 5 else selected
            submitted = []
            for f in features:
                submitted += [(((f, "1"),), n == 0) for n in range(1 if r == 1 else 2)]
            rows.append(run_root(s, r, submitted))
            if rows[-1]["status"] != "COMPLETED":
                break
    else:
        initial = MIX if family == "F02" else A
        for r in range(1, 5):
            rows.append(run_root(s, r, events(initial, 1 if r == 1 else 2)))
            if rows[-1]["status"] != "COMPLETED":
                break
        if rows[-1]["status"] == "COMPLETED":
            tail = (
                [(A, 1), (A, 2), ((), 1)]
                if family == "F01"
                else [(MIX, 1), (MIX, 2), (MIX, 2), (MIX, 2)]
                if family == "F02"
                else [(A, 1), (MIX, 1), (MIX, 2), (MIX, 2), (MIX, 2), (MIX, 2)]
            )
            for r, (f, count) in enumerate(tail, 5):
                rows.append(run_root(s, r, events(f, count)))
                if rows[-1]["status"] != "COMPLETED":
                    break
    result = dict(
        family=family,
        revision=1,
        evidence_kind="GENUINE_ROOTSTORE_EXTERNAL_EVENTS",
        **inputs,
        roots=rows,
        final=final_evidence(s),
    )
    s.close()
    result["recovery"] = recover(path, revision, result["final"]["state"])
    return result


def clock_trial(path, revision):
    s = open_store(path, revision)
    rows = [run_root(s, 1, events((), 1)), run_root(s, 2, events((), 5))]
    prefix = _verified_completed_prefix(
        s._backend._connection, s.end(2), decode_multi_close, replay=True
    )
    five = asdict(prefix.cooldown(0, 1))
    s.begin(3)
    h = s.h_bytes()
    for n in range(3):
        s.event(3, n, ())
    s.abort(3)
    assert s.h_bytes() == h
    rows.append(run_root(s, 4, events((), 194)))
    prefix = _verified_completed_prefix(
        s._backend._connection, s.end(4), decode_multi_close, replay=True
    )
    at199 = asdict(prefix.cooldown(0, 1))
    rows.append(run_root(s, 5, events((), 1)))
    prefix = _verified_completed_prefix(
        s._backend._connection, s.end(5), decode_multi_close, replay=True
    )
    at200 = asdict(prefix.cooldown(0, 1))
    same = asdict(prefix.cooldown(0, None, edited_this_end=frozenset({0})))
    result = dict(
        evidence_kind="GENUINE_COMPLETED_EVENT_REFERENCE_CLOCK_NOT_REAL_EDIT",
        roots=rows,
        after_five=five,
        at199=at199,
        at200=at200,
        same_end_component=same,
        aborted_events=3,
        abort_H_BEGIN_exact=True,
        actual_merge_split_edits=0,
        final=final_evidence(s),
    )
    s.close()
    result["recovery"] = recover(path, revision, result["final"]["state"])
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--family", choices=("F01", "F02", "F03", "F04", "clock"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.directory.mkdir(parents=True, exist_ok=True)
    path = args.directory / f"{args.family}.sqlite"
    assert not path.exists(), "FRESH_PRODUCTION_DATABASE_REQUIRED"
    revision = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    started = time.perf_counter()
    result = (
        clock_trial(path, revision)
        if args.family == "clock"
        else curriculum(path, revision, args.family)
    )
    result.update(code_revision=revision, seconds=time.perf_counter() - started)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf8", newline="\n"
    )
    print(
        json.dumps(
            dict(
                family=args.family,
                revision=revision,
                seconds=result["seconds"],
                output=str(args.output),
                final=result["final"]["state"],
            )
        )
    )


if __name__ == "__main__":
    main()
