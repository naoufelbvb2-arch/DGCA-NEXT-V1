"""Read-only stale runtime refusal between actual F01 root4/root5 snapshots."""

import argparse
import hashlib
import json
from dataclasses import asdict
from pathlib import Path

from dgca_next.dynamics.native_attractor import NativeFeatureEvent
from dgca_next.dynamics.session import FeatureEvent
from dgca_next.persistence.attractor_store import (
    inspect_native_subject,
    native_session_step,
    start_native_session,
)
from dgca_next.persistence.store import RootStore

ROOT = Path(__file__).resolve().parents[2]


def run(old_path, current_path, revision, out):
    options = dict(
        repository_root=ROOT, code_revision=revision, execution_mode="I4_NATIVE_ATTRACTOR_V1"
    )
    old = RootStore(old_path, **options)
    current = RootStore(current_path, **options)
    old_before, current_before = old.view(), current.view()
    event = NativeFeatureEvent(FeatureEvent((("a", "1"),)))
    prior = native_session_step(old, start_native_session(old, session_id=201), event)
    assert prior.state.attractors and prior.state.attractors[0].generation == 1
    reasons = []
    for function in (
        lambda: native_session_step(current, prior.state, event),
        lambda: inspect_native_subject(current, 0, generation=1),
    ):
        try:
            function()
        except ValueError as exc:
            reasons.append(str(exc))
        else:
            raise AssertionError("STALE_NATIVE_REFERENCE_ACCEPTED")
    assert reasons == ["STALE_NATIVE_RUNTIME_SNAPSHOT", "STALE_NATIVE_GENERATION"]
    assert old.view() == old_before and current.view() == current_before
    subject = inspect_native_subject(current, 0, generation=2)
    result = dict(
        classification="AUTHENTICATED_HISTORICAL_READ_ONLY_CONTROL_NOT_NEW_LEARNING",
        original_family="F01-r2",
        original_revision=revision,
        before_subject=asdict(prior.state.attractors[0]),
        current_subject=dict(
            id=subject.assembly_id,
            generation=subject.structural_generation,
            members=list(subject.member_cell_ids),
        ),
        old_W=hashlib.sha256(old_before.W).hexdigest(),
        current_W=hashlib.sha256(current_before.W).hexdigest(),
        refusals=reasons,
        W_H_R_unchanged=True,
    )
    old.close()
    current.close()
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("old", type=Path)
    parser.add_argument("current", type=Path)
    parser.add_argument("revision")
    parser.add_argument("out", type=Path)
    args = parser.parse_args()
    run(args.old, args.current, args.revision, args.out)
