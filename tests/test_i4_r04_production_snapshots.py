"""Codec/lineage components on real saved states, NOT a learning experiment."""

import base64
import json
from pathlib import Path

import pytest

from dgca_next.graph.native_operator import read_operator
from dgca_next.persistence.binary_records import decode_record, encode_record
from dgca_next.persistence.native_codec import decode_native_graph, encode_native_graph
from dgca_next.persistence.operator_codec import decode_operator_graph

EVIDENCE = Path(__file__).resolve().parents[1] / "docs/implementation/evidence/i4-r04-autonomous"


@pytest.fixture(params=("F05-r3", "F06-r2"), scope="module")
def saved(request):
    trace = json.loads((EVIDENCE / (request.param + "-publish.json")).read_text(encoding="utf8"))
    assert trace["recovery"]["cold_process_replay_exact"]
    return trace, base64.b64decode(trace["W_base64"])


def test_actual_saved_operator_state_roundtrips_but_old_reader_refuses(saved):
    trace, raw = saved
    graph = decode_operator_graph(raw)
    assert encode_native_graph(graph) == raw
    assert len(graph.native_operator_log()) == len(trace["operator_records"])
    assert all(
        read_operator(op)["exposure_id"] == trace["root_id"] for op in graph.native_operator_log()
    )
    assert not graph.automatic_recycling_enabled
    with pytest.raises(ValueError):
        decode_native_graph(raw)


@pytest.mark.parametrize(
    "damage",
    [
        "generation",
        "birth",
        "subjects",
        "clock_reference",
        "ordinal",
        "reverse",
        "form_child",
        "members",
        "partition",
    ],
)
def test_saved_lineage_refuses_structural_forgery_components(saved, damage):
    _, raw = saved
    doc = decode_record(raw, 0x57, 5)
    op = read_operator(doc["operators"][0])
    if damage == "generation":
        op["after"][0][3] += 1
    elif damage == "birth":
        op["after"][1][4] += 1
    elif damage == "subjects":
        op["before"][0][0] = 999
    elif damage == "clock_reference":
        op["after"][0][6] -= 1
    elif damage == "ordinal":
        op["ordinal"] = 999
    elif damage == "reverse":
        doc["membership_reverse"][0][1] = []
    elif damage == "members":
        op["after"][0][2] = op["after"][0][2][1:]
    elif damage == "partition":
        op["after"][0][2], op["after"][1][2] = op["after"][1][2], op["after"][0][2]
    else:
        fake = dict(doc["forms"][0])
        fake["assembly_id"] = op["after"][1][0]
        doc["forms"].append(fake)
    doc["operators"][0] = encode_record(0x4D, 1, op)
    with pytest.raises(ValueError):
        decode_operator_graph(encode_record(0x57, 5, doc))


def test_bare_w_does_not_authenticate_historical_event_clock(saved):
    _, raw = saved
    doc = decode_record(raw, 0x57, 5)
    changed = []
    for record in doc["operators"]:
        op = read_operator(record)
        op["event_clock"] += 1
        changed.append(encode_record(0x4D, 1, op))
    doc["operators"] = changed
    forged = encode_record(0x57, 5, doc)
    # Explicit trust boundary: a structural codec is not RootStore authority.
    # Genuine cold RootStore forgery controls must reject the repaired journal.
    assert encode_native_graph(decode_operator_graph(forged)) == forged
