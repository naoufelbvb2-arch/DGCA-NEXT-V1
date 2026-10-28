"""Reproduce P02's external RootStore learning trace without fixture mutation."""

import hashlib
import json
import sqlite3
from contextlib import closing
from pathlib import Path
from tempfile import TemporaryDirectory

from dgca_next.contracts import SynapseScope
from dgca_next.dynamics.session import FeatureEvent, read_only_episode
from dgca_next.dynamics.state import GraphSnapshot
from dgca_next.graph.synapse import quality
from dgca_next.learning.homeostasis_profile import LanguageHomeostasis
from dgca_next.persistence.graph_codec import decode_production_graph
from dgca_next.persistence.store import RootStore

ROOT = Path(__file__).resolve().parents[2]
FEATURE_A = (("a", "1"),)


def _key(synapse):
    return [synapse.key.source.cell_id, synapse.key.target.cell_id, synapse.key.scope.value]


def _info(synapse, event_eligible):
    credit = synapse.credits[-1]
    return {
        "key": _key(synapse),
        "state": synapse.state.value,
        "S": synapse.S,
        "E_ext": synapse.E_ext,
        "root_count": synapse.external_root_count,
        "Q": quality(synapse),
        "roots": [c.root_id for c in synapse.credits],
        "q": credit.q,
        "y": credit.y,
        "source_activity": credit.source_activity,
        "target_activity": credit.target_activity,
        "target_threshold": credit.target_threshold,
        "source_event_id": credit.source_event_id,
        "event_id": credit.event_id,
        "event_order": credit.event_order,
        "source_digest": credit.source_digest,
        "target_digest": credit.target_digest,
        "D_event": event_eligible,
    }


def _event_eligible(path, credit, key):
    with closing(sqlite3.connect(path)) as connection:
        row = connection.execute(
            "SELECT w_before FROM p01_events WHERE event_id=?", (credit.event_id,)
        ).fetchone()
    assert row is not None
    graph = decode_production_graph(row[0])
    return graph.structurally_eligible(key.source.cell_id, key.target.cell_id)


def main():
    with TemporaryDirectory() as directory:
        path = Path(directory) / "trace.sqlite"
        engine = RootStore(path, repository_root=ROOT, code_revision="a" * 40)
        assert engine.graph().synapses() == ()
        engine.begin(1)
        birth = engine.event(1, 0, FEATURE_A)
        assert not engine.end(1).accepted
        zero_w = engine.view().W

        engine.begin(2)
        source_event = engine.event(2, 0, FEATURE_A)
        target_event = engine.event(2, 1, FEATURE_A)
        staged = engine.pending_proposals(2)
        close = engine.end(2)
        links = engine.graph().synapses()
        local = next(s for s in links if s.key.scope is SynapseScope.LOCAL)
        assoc = next(s for s in links if s.key.scope is SynapseScope.ASSOCIATIVE)
        first = [_info(s, _event_eligible(path, s.credits[-1], s.key)) for s in (local, assoc)]

        engine.begin(3)
        engine.event(3, 0, FEATURE_A)
        engine.event(3, 1, FEATURE_A)
        engine.end(3)
        graph = engine.graph()
        second_links = (graph.synapse(local.key), graph.synapse(assoc.key))
        assert all(link is not None for link in second_links)
        second = [_info(s, _event_eligible(path, s.credits[-1], s.key)) for s in second_links]
        w, h_bytes = engine.view().W, engine.h_bytes()
        snapshot = GraphSnapshot.capture(graph)
        h = LanguageHomeostasis.decode(h_bytes).materialize(snapshot.committed_ids)
        inputs = (FeatureEvent(FEATURE_A), FeatureEvent(FEATURE_A))
        actual = read_only_episode(snapshot, h, inputs, session_id=1)
        baseline = read_only_episode(
            GraphSnapshot.capture(decode_production_graph(zero_w)), h, inputs, session_id=2
        )
        result = {
            "birth": birth.born,
            "root2_events": [source_event.event_id, target_event.event_id],
            "source_emitters": source_event.emitters,
            "source_F_step": source_event.frontier,
            "staged_count": len(staged),
            "root2_accepted_count": len(close.accepted),
            "link_count": len(links),
            "root2": first,
            "root3": second,
            "D_close": [
                graph.structurally_eligible(s.key.source.cell_id, s.key.target.cell_id)
                for s in second_links
            ],
            "W_sha256": hashlib.sha256(w).hexdigest(),
            "H_sha256": hashlib.sha256(h_bytes).hexdigest(),
            "P_S": dict(actual[0].synchronous),
            "P_S_zero_link": dict(baseline[0].synchronous),
            "P_T": dict(actual[1].temporal),
            "P_T_zero_link": dict(baseline[1].temporal),
        }
        engine.close()
        engine = RootStore(path, repository_root=ROOT, code_revision="a" * 40)
        result["recovered"] = {
            "same_W": engine.view().W == w,
            "same_H": engine.h_bytes() == h_bytes,
            "completed_roots": engine.view().completed_closes,
        }
        engine.begin(4)
        engine.event(4, 0, FEATURE_A)
        engine.event(4, 1, FEATURE_A)
        engine.end(4)
        after_four = engine.graph()
        fourth_links = (after_four.synapse(local.key), after_four.synapse(assoc.key))
        assert all(link is not None for link in fourth_links)
        result["root4"] = [
            _info(s, _event_eligible(path, s.credits[-1], s.key)) for s in fourth_links
        ]
        completed_h = engine.h_bytes()
        engine.begin(5)
        later = engine.event(5, 0, (("ab", "1"),))
        engine.abort(5)
        result["abort5"] = {
            "born": later.born,
            "H_restored": engine.h_bytes() == completed_h,
            "links_unchanged": engine.graph().synapses() == after_four.synapses(),
        }
        engine.close()
        print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
