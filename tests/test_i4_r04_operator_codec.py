"""Representation refusal components; these tests claim no real operator."""

from dataclasses import replace

import pytest
from test_i4_r04_autonomous import store_at

from dgca_next.graph.native_operator import read_operator
from dgca_next.graph.network import SparseNetwork
from dgca_next.persistence.binary_records import decode_record, encode_record
from dgca_next.persistence.native_codec import encode_native_graph
from dgca_next.persistence.operator_codec import decode_operator_graph


def test_empty_extension_keeps_accepted_w_bytes(tmp_path):
    s = store_at(tmp_path / "old.sqlite")
    s.begin(1)
    s.event(1, 0, (("a", "1"),))
    s.end(1)
    raw = s.view().W
    graph = decode_operator_graph(raw)
    assert encode_native_graph(graph) == raw and not graph.native_operator_log()
    assert "operators" not in decode_record(raw, 0x57, 5)
    s.close()


@pytest.mark.parametrize("damage", ["empty", "version", "malformed", "extra"])
def test_no_lineage_can_be_smuggled_into_an_old_w(tmp_path, damage):
    s = store_at(tmp_path / "old.sqlite")
    doc = decode_record(s.view().W, 0x57, 5)
    doc.update(operator_journal_version=1, operators=[])
    if damage == "version":
        doc["operator_journal_version"] = 99
    elif damage == "malformed":
        doc["operators"] = [b"unverified"]
    elif damage == "extra":
        doc["future_alias"] = 0
    with pytest.raises(ValueError):
        decode_operator_graph(encode_record(0x57, 5, doc))
    s.close()


def test_operator_records_cannot_exist_in_a_non_native_graph():
    graph = SparseNetwork()
    graph._state = replace(graph._state, native_operator_log=(b"unverified",))
    with pytest.raises(ValueError, match="NATIVE_ASSEMBLY_MODE_REQUIRED"):
        graph.validate_graph()
    with pytest.raises(ValueError):
        read_operator(encode_record(0x4D, 1, {"version": 1, "operator": "SPLIT"}))
