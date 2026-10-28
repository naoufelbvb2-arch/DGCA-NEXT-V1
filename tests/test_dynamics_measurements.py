"""Measurements are synthetic fixtures; no runtime or learning threshold is asserted."""

import json
import sys
import time
import tracemalloc
from pathlib import Path

from dgca_next.dynamics.session import FeatureEvent, read_only_episode
from dgca_next.dynamics.state import GraphSnapshot, Homeostasis
from dgca_next.graph import FixtureBuilder, SparseNetwork


def test_sparse_event_measurement_and_repeatable_activity():
    graph = SparseNetwork()
    FixtureBuilder(graph).commit_cells(range(8192, 8704), committed_event=0)
    frozen = GraphSnapshot.capture(graph)
    h = Homeostasis.uniform_language(frozen.committed_ids)
    events = tuple(FeatureEvent((("a", "0.5"), ("ab", "0.25"))) for _ in range(4))
    tracemalloc.start()
    started = time.perf_counter()
    traces = read_only_episode(frozen, h, events, session_id=99)
    elapsed = time.perf_counter() - started
    retained, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    repeated = read_only_episode(frozen, h, events, session_id=99)
    assert traces == repeated
    assert len(traces[-1].state.activity) == 512
    assert len(graph.synapses()) == 0 and graph.stored_cell_count == 512
    assert graph.automatic_recycling_enabled is False
    metrics = {
        "fixture_only": True,
        "platform": sys.platform,
        "python": sys.version.split()[0],
        "logical_cells": 12288,
        "committed_fixture_cells": graph.stored_cell_count,
        "live_synapses": len(graph.synapses()),
        "event_count": len(events),
        "elapsed_seconds": elapsed,
        "retained_traced_bytes": retained,
        "peak_traced_bytes": peak,
        "final_frontier": sorted(traces[-1].state.frontiers.step),
        "no_learning_or_admission": True,
    }
    path = Path(".pytest_cache/i2-dynamics-metrics.json")
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(metrics, indent=2, sort_keys=True) + "\n", encoding="utf-8")
