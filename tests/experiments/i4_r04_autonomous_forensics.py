"""Export exact authenticated trial snapshots; never a RootStore authority."""

import argparse
import base64
import hashlib
import json
import sqlite3
from contextlib import closing
from dataclasses import asdict
from pathlib import Path

from dgca_next.contracts import Region
from dgca_next.graph.assembly_support import inspect_structure
from dgca_next.graph.native_lifecycle import score
from dgca_next.learning.homeostasis_profile import LanguageHomeostasis
from dgca_next.learning.production_event import decode_event
from dgca_next.persistence.native_codec import _base_graph, decode_native_graph, encode_native_graph


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def file_sha(path):
    digest = hashlib.sha256()
    with path.open("rb") as source:
        while block := source.read(1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def snapshot(path, trace_path):
    """Bind exported bytes to an already cold-replayed, unchanged DB receipt."""
    trace = json.loads(trace_path.read_text(encoding="utf8"))
    before = file_sha(path)
    assert before == trace["recovery"]["file_sha256"], "DATABASE_CHANGED_AFTER_COLD_REPLAY"
    with closing(sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True)) as db:
        w, h, r, closes = db.execute(
            "SELECT w_state,h_state,r_state,completed_closes FROM p01_metadata"
        ).fetchone()
        births = []
        for raw, pre_h in db.execute("SELECT record,h_before FROM p01_events ORDER BY event_id"):
            event = decode_event(raw)
            if not event.born:
                continue
            frozen = LanguageHomeostasis.decode(pre_h).materialize(frozenset(event.pre_committed))
            births.append(
                dict(
                    exposure_id=event.exposure_id,
                    event_id=event.event_id,
                    order=event.event_order,
                    digest=event.digest,
                    born=event.born,
                    origin=event.origin.value,
                    mode=event.mode.value,
                    X_fixed=event.X_fixed,
                    final=event.final,
                    pass1_emitters=event.emitters,
                    learning_frontier=event.learning_frontier,
                    pre_event_gains=sorted(frozen.gains.items()),
                    theta_active=frozen.thresholds[Region.LANGUAGE],
                    H_before_base64=base64.b64encode(pre_h).decode(),
                    pre_W_sha256=event.pre_w_hash,
                    pre_H_sha256=event.pre_h_hash,
                )
            )
    state = trace["final"]["state"]
    assert [sha(w), sha(h), sha(r), closes] == [
        state["W_sha256"],
        state["H_sha256"],
        state["R_sha256"],
        state["completed_closes"],
    ]
    graph = decode_native_graph(w)
    assert encode_native_graph(graph) == w
    structure = inspect_structure(_base_graph(graph))
    supports = {}
    for pair in structure.pairs:
        if pair.edge:
            supports.setdefault(pair.first, {})[pair.second] = pair.support
            supports.setdefault(pair.second, {})[pair.first] = pair.support
    scores = [
        dict(
            assembly_id=a.assembly_id,
            generation=a.structural_generation,
            scores=[asdict(score(i, a.member_cell_ids, supports)) for i in a.member_cell_ids],
        )
        for a in graph.native_assemblies()
        if a.status == "LIVE"
    ]
    initializations = []
    for cell in graph.stored_cells():
        birth = graph.initialization(cell.cell_id)
        assert birth is not None
        initializations.append(
            dict(
                owner=cell.cell_id,
                event_id=birth.assignment.event_id,
                seed_targets=birth.seed_targets,
                dynamic_targets=[
                    v.target_id for v in graph.latent_slots(cell.cell_id) if v.recyclable_category
                ],
            )
        )
    assert file_sha(path) == before
    return dict(
        source_kind="EXACT_COPY_OF_COLD_REPLAYED_PRODUCTION_CHECKPOINT",
        publication_authority=False,
        trace=trace_path.name,
        trace_sha256=file_sha(trace_path),
        database_sha256=before,
        W_sha256=sha(w),
        H_sha256=sha(h),
        R_sha256=sha(r),
        W_base64=base64.b64encode(w).decode(),
        H_base64=base64.b64encode(h).decode(),
        R_base64=base64.b64encode(r).decode(),
        current_scores=scores,
        committed_cells=len(graph.stored_cells()),
        learned_keys=len(graph.synapses()),
        physical_initializations=initializations,
        genuine_birth_events=births,
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    trials = (
        "F01-r1",
        "F02-r1",
        "F03-r1",
        "F04-r1",
        "F05-r1",
        "F05-r2",
        "F05-r3",
        "F06-r1",
        "F06-r2",
        "clock-r1",
    )
    records = []
    for trial in trials:
        # Revision1 retained the original family-only DB filename.
        name = trial.removesuffix("-r1")
        records.append(
            snapshot(args.directory / (name + ".sqlite"), args.evidence / (trial + ".json"))
        )
    args.output.write_text(
        json.dumps(records, indent=2, sort_keys=True) + "\n", encoding="utf8", newline="\n"
    )
    print(
        json.dumps(
            dict(snapshots=len(records), output=str(args.output), bytes=args.output.stat().st_size)
        )
    )


if __name__ == "__main__":
    main()
