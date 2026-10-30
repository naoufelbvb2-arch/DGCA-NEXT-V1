"""Cold-start ingress attempt: fail-closed guards, not evidence of learning."""

import json
from pathlib import Path

import pytest

from dgca_next.dynamics.numeric import SpecBlocked
from dgca_next.graph import SparseNetwork
from dgca_next.learning.homeostasis_profile import LanguageHomeostasis
from dgca_next.peripheral.sic import project
from dgca_next.persistence.store import EMPTY_W, RootStore

ROOT = Path(__file__).resolve().parents[2]


def test_cold_start_ingress_reports_blockers_without_fabricating_learning(tmp_path):
    h = LanguageHomeostasis.initial().overrides
    network = SparseNetwork()
    assert network.stored_cell_count == 0 and network.synapses() == ()
    engine = RootStore(
        tmp_path / "cold.sqlite",
        repository_root=ROOT,
        code_revision="a" * 40,
        initial_homeostasis=h,
    )
    before = engine.view()
    assert before.W == EMPTY_W and before.completed_closes == 0
    engine.begin(1)
    first = (("a", "1"),)
    with pytest.raises(SpecBlocked, match="I3-R02") as initial:
        engine.event(1, 0, first)
    first_state = engine.view()
    assert engine.root(1).next_order == 0 and first_state.W == before.W
    assert first_state.completed_closes == 0
    engine.abort(1)
    engine.begin(2)
    overflow = tuple((f, "1") for f in ("a", "ab", "c", "d"))
    with pytest.raises(SpecBlocked, match="I3-R02") as selection:
        engine.event(2, 0, overflow)
    second_state = engine.view()
    assert engine.root(2).next_order == 0 and second_state.W == before.W
    assert second_state.completed_closes == 0
    engine.abort(2)
    final = engine.view()
    engine.close()
    report = {
        "status": "PARTIAL: production EVENT unavailable",
        "attempt_type": "uncommitted synthetic test ingress; no validated external EVENT",
        "initial_W": "EMPTY_W",
        "initial_committed_cells": 0,
        "initial_synapses": 0,
        "first_projected_X_fixed": list(project(first).X_fixed),
        "first_rejection": str(initial.value),
        "overflow_projected_X_fixed": list(project(overflow).X_fixed),
        "overflow_count": len(project(overflow).X_fixed),
        "overflow_rejection": str(selection.value),
        "completed_external_roots": final.completed_closes,
        "high_watermark": final.high_watermark,
        "learned_links": 0,
        "experiment_status": "NOT_RUN: no production EVENT, END, evidence, or learning",
    }
    path = ROOT / ".pytest_cache/i3-cold-attempt.json"
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(report, sort_keys=True, indent=2) + "\n", encoding="utf-8")
