"""Actual six-root native continuation, process crashes and independent reload."""

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
from dgca_next.graph.synapse import quality
from dgca_next.learning.homeostasis_profile import LanguageHomeostasis
from dgca_next.persistence.store import RootStore

ROOT = Path(__file__).resolve().parents[2]
MODE = "I4_NATIVE_MAINTAIN_GROW_V1"


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
    assert not store.graph().stored_cells() and not store.graph().synapses()
    assert not store.graph().native_assemblies()
    progression = []
    for root in range(1, 5):
        store.begin(root)
        for order in range(1 if root == 1 else 2):
            store.event(root, order, (("a", "1"),))
        close = store.end(root)
        graph = store.graph()
        progression.append(
            dict(
                root=root,
                completed_serial=close.close_serial,
                W=sha(store.view().W),
                H=sha(store.h_bytes()),
                formed_ids=close.formed_ids,
                local_count=sum(s.key.scope is SynapseScope.LOCAL for s in graph.synapses()),
                assemblies=[
                    asdict(a) | {"region": a.region.value} for a in graph.native_assemblies()
                ],
            )
        )
    birth_log = store.graph().native_form_log()
    before_assembly = store.graph().native_assemblies()[0]
    before_links = {s.key: s for s in store.graph().synapses()}
    before_topology = store.graph()._state.slots, store.graph()._state.reverse
    before_root5 = store.view()
    store.begin(5)
    event = store.event(5, 0, (("a", "1"),))
    before_end = store.view()
    assert store.graph().native_assemblies() == (before_assembly,)
    store.close()
    crash_script = """
import os,sys
from pathlib import Path
from dgca_next.persistence.store import RootStore
s=RootStore(Path(sys.argv[1]),repository_root=Path(sys.argv[2]),code_revision=sys.argv[3],execution_mode='I4_NATIVE_MAINTAIN_GROW_V1')
def crash(stage):
    if stage==sys.argv[4]: os._exit(31)
s.end(5,hook=crash)
"""
    crashes = []
    for phase in ("BEFORE_COMMIT", "AFTER_COMMIT"):
        completed = subprocess.run(
            [sys.executable, "-c", crash_script, str(path), str(ROOT), revision, phase]
        )
        assert completed.returncode == 31
        store = open_store()
        if phase == "BEFORE_COMMIT":
            assert store.view() == before_end and store.graph().native_assemblies() == (
                before_assembly,
            )
        else:
            assert store.root(5).status == "COMPLETED"
        crashes.append(
            dict(
                phase=phase,
                exit_code=completed.returncode,
                root_status=store.root(5).status,
                completed_serial=store.view().completed_closes,
                W=sha(store.view().W),
                H=sha(store.h_bytes()),
                generation=store.graph().native_assemblies()[0].structural_generation,
                mutation_count=len(store.graph().native_mutation_log()),
            )
        )
        store.close()
    store = open_store()
    close5 = store.end(5)
    graph = store.graph()
    (assembly,) = graph.native_assemblies()
    (mutation,) = graph.native_mutation_log()
    assert assembly.assembly_id == 0 and assembly.structural_generation == 2
    assert assembly.member_cell_ids == (8606, 9345, 11795, 12181)
    assert graph.native_form_log() == birth_log and mutation.exposure_id == 5
    assert set(before_links) == {s.key for s in graph.synapses()}
    assert (graph._state.slots, graph._state.reverse) == before_topology
    learned = []
    for link in graph.synapses():
        old = before_links[link.key]
        if link.key.scope is SynapseScope.LOCAL:
            learned.append(
                dict(
                    source=link.key.source.cell_id,
                    target=link.key.target.cell_id,
                    state=link.state.value,
                    before_Q=quality(old),
                    Q=quality(link),
                    S=link.S,
                    E_ext=link.E_ext,
                    E_int=link.E_int,
                    external_count=link.external_root_count,
                    roots=[c.root_id for c in link.credits],
                    latest_credit=asdict(link.credits[-1]),
                )
            )
    after5 = store.view()
    assert store.end(5) == close5 and store.view() == after5
    store.begin(6)
    empty = store.event(6, 0, ())
    close6 = store.end(6)
    assert not close6.accepted and not close6.mutation_ordinals
    assert store.graph().native_assemblies() == (assembly,)
    assert store.graph().native_form_log() == birth_log
    assert store.graph().native_mutation_log() == (mutation,)
    final = store.view()
    assert final.W == after5.W
    h = store.h_bytes()
    snapshot = GraphSnapshot.capture(store.graph())
    homeostasis = LanguageHomeostasis.decode(h).materialize(snapshot.committed_ids)
    activity = read_only_episode(
        snapshot, homeostasis, (FeatureEvent((("a", "1"),)),), session_id=10
    )[0]
    assert store.inspect_native_lifecycle(5) == close5 and store.view() == final
    assert store.graph().native_mutation_log() == (mutation,)
    with closing(sqlite3.connect(path)) as connection:
        archive = sha("\n".join(connection.iterdump()).encode())
        schema = connection.execute("SELECT schema_version FROM p01_metadata").fetchone()[0]
    result = dict(
        code_revision=revision,
        execution_mode=MODE,
        schema=schema,
        input_features=[["a", "1"]],
        roots1_to_4=progression,
        immutable_birth=[asdict(f) for f in birth_log],
        assembly_before=asdict(before_assembly) | {"region": before_assembly.region.value},
        assembly_after=asdict(assembly) | {"region": assembly.region.value},
        root5_event=dict(
            root=event.exposure_id,
            event=event.event_id,
            order=event.event_order,
            observation_digest=event.digest,
            X_fixed=event.X_fixed,
            final=event.final,
            frozen_pass1_emitters=event.emitters,
            F_step=event.frontier,
            pre_w_hash=event.pre_w_hash,
            pre_h_hash=event.pre_h_hash,
            born=event.born,
            origin=event.origin.value,
            mode=event.mode.value,
        ),
        root5_evaluations=[asdict(e) for e in close5.evaluations],
        root5_coverage=close5.coverage,
        mutation=asdict(mutation),
        root5_accepted=[
            dict(
                source=p.key.source.cell_id,
                target=p.key.target.cell_id,
                scope=p.key.scope.value,
                q=p.credit.q,
                y=p.credit.y,
            )
            for p in close5.accepted
        ],
        local_links=learned,
        W_before_root5=sha(before_root5.W),
        W_before_END5=sha(before_end.W),
        W_after_END5=sha(after5.W),
        H_after_END5=sha(
            store._backend._connection.execute(
                "SELECT h_end FROM p01_roots WHERE exposure_id=5"
            ).fetchone()[0]
        ),
        W_after_END6=sha(final.W),
        H_after_END6=sha(h),
        R_after_END6=sha(final.runtime),
        root6=dict(
            event_id=empty.event_id,
            close_serial=close6.close_serial,
            accepted_count=len(close6.accepted),
            mutation_ordinals=close6.mutation_ordinals,
            evaluations=[asdict(e) for e in close6.evaluations],
            coverage=close6.coverage,
        ),
        member_reverse=[
            [i, sorted(store.graph().member_assemblies(i))] for i in assembly.member_cell_ids
        ],
        high_watermark=store.graph()._state.assembly_high_watermarks[Region.LANGUAGE],
        process_crashes=crashes,
        archive_sha256=archive,
        max_read_only_synchronous=max(activity.synchronous.values()),
        read_only_state_unchanged=True,
        database_bytes=path.stat().st_size,
        database_allocated_bytes=_allocated_bytes(path),
        automatic_recycling_enabled=store.graph().automatic_recycling_enabled,
        production_removal_archive="NOT_RUN",
        component_removal_archive="tested separately",
    )
    store.close()
    load_script = """
import hashlib,json,sys
from pathlib import Path
from dataclasses import asdict
from dgca_next.persistence.store import RootStore
s=RootStore(Path(sys.argv[1]),repository_root=Path(sys.argv[2]),code_revision=sys.argv[3],execution_mode='I4_NATIVE_MAINTAIN_GROW_V1')
a,=s.graph().native_assemblies()
print(json.dumps({'W':hashlib.sha256(s.view().W).hexdigest(),'H':hashlib.sha256(s.h_bytes()).hexdigest(),
'id':a.assembly_id,'generation':a.structural_generation,'members':a.member_cell_ids,'serial':s.view().completed_closes,
'mutation':asdict(s.graph().native_mutation_log()[0]),'birth':asdict(s.graph().native_form_log()[0]),
'reverse':[[i,sorted(s.graph().member_assemblies(i))] for i in a.member_cell_ids]}))
s.close()
"""
    independent = json.loads(
        subprocess.check_output(
            [sys.executable, "-c", load_script, str(path), str(ROOT), revision], text=True
        )
    )
    assert independent["W"] == result["W_after_END6"] and independent["H"] == result["H_after_END6"]
    assert independent["id"] == 0 and independent["generation"] == 2 and independent["serial"] == 6
    assert independent["members"] == list(assembly.member_cell_ids)
    assert independent["mutation"] == json.loads(json.dumps(result["mutation"]))
    assert independent["birth"] == json.loads(json.dumps(result["immutable_birth"][0]))
    assert independent["reverse"] == result["member_reverse"]
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
        result = run_trial(Path(directory) / "lifecycle.sqlite", measure_memory=True)
    data = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(data, encoding="utf-8", newline="\n")
        print(
            json.dumps(
                dict(
                    output=str(args.output),
                    revision=result["code_revision"],
                    assembly=result["assembly_after"],
                    seconds=result["seconds"],
                    database_bytes=result["database_bytes"],
                )
            )
        )
    else:
        print(data, end="")


if __name__ == "__main__":
    main()
