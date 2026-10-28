import json
import platform
import sys
import tracemalloc
from pathlib import Path
from time import perf_counter

from dgca_next.contracts import Region
from dgca_next.graph import FixtureBuilder, SparseNetwork, validate_graph


def test_i1_t24_full_logical_network_sparse_storage(record_factory, key_factory):
    tracemalloc.start()
    started = perf_counter()
    graph = SparseNetwork()
    builder = FixtureBuilder(graph)
    with builder.transaction() as tx:
        tx.commit_cells(graph.iter_cell_ids(), committed_event=0)
        for region in Region:
            for offset in range(256):
                source = 4096 * region.value + 2 * offset
                target = source + 1
                tx.inject_slot(source, 0, target)
                key = key_factory(source, target)
                if offset % 4 == 0:
                    tx.reserve(key, source)
                else:
                    tx.add_synapse(record_factory(key))
    build_seconds = perf_counter() - started
    audit_started = perf_counter()
    report = validate_graph(graph)
    audit_seconds = perf_counter() - audit_started
    assert sum(cell.committed for cell in graph.iter_cells()) == 12288
    assert report.stored_cells == 12288
    assert report.occupied_slots == 768
    assert report.synapses == 576
    assert report.reserved_keys == 192
    # Inspect actual sparse containers, without a platform-specific memory/time threshold.
    assert len(graph._state.slots) == len(graph._state.outgoing) == 768
    assert len(graph._state.reverse) == 768
    assert sum(len(slots) for slots in graph._state.slots.values()) == 768 * 24
    digest = graph.structural_hash
    assert digest == "160a96789166570bd8337c04f55044687c2dae8df62f690832d0164afb0f58b9"
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    metrics = dict(
        fixture_only=True,
        python=platform.python_version(),
        platform=sys.platform,
        logical_cells=12288,
        materialized_cells=12288,
        slot_owner_records=768,
        occupied_slots=768,
        live_synapses=576,
        reserved_keys=192,
        build_seconds=build_seconds,
        independent_audit_seconds=audit_seconds,
        retained_traced_bytes=current,
        peak_traced_bytes=peak,
        structural_sha256=digest,
    )
    output = Path(__file__).resolve().parents[1] / ".pytest_cache/i1-stress-metrics.json"
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(metrics, sort_keys=True, indent=2) + "\n", encoding="utf-8")
