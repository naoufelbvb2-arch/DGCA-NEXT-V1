"""Fresh experimental W schema 5; legacy W and databases are not migrated."""

from dataclasses import asdict, replace
from types import MappingProxyType

from dgca_next.contracts import Region
from dgca_next.graph.native_assembly import _assembly_record, _form_record
from dgca_next.graph.network import SparseNetwork
from dgca_next.persistence.binary_records import decode_record, encode_record
from dgca_next.persistence.graph_codec import decode_production_graph, encode_production_graph

_TAG = 0x57
_VERSION = 5


def empty_native_graph() -> SparseNetwork:
    graph = SparseNetwork()
    graph._state = replace(
        graph._state, assembly_high_watermarks=MappingProxyType({Region.LANGUAGE: -1})
    )
    return graph


def _base_graph(graph: SparseNetwork) -> SparseNetwork:
    result = SparseNetwork()
    result._state = replace(
        graph._state,
        cells=MappingProxyType(
            {i: replace(c, assembly_ids=frozenset()) for i, c in graph._state.cells.items()}
        ),
        native_assemblies=MappingProxyType({}),
        assembly_high_watermarks=MappingProxyType({}),
        member_assemblies=MappingProxyType({}),
        native_form_log=(),
    )
    return result


def encode_native_graph(network: SparseNetwork) -> bytes:
    graph = network
    if type(graph) is not SparseNetwork or not graph._state.assembly_high_watermarks:
        raise ValueError("NATIVE_GRAPH_SCHEMA_REQUIRED")
    graph.validate_graph()
    state = graph._state
    forms = [asdict(r) for r in state.native_form_log]
    doc = {
        "base": encode_production_graph(_base_graph(graph)),
        "assemblies": [
            [
                r.assembly_id,
                r.region.value,
                list(r.member_cell_ids),
                r.structural_generation,
                r.birth_close_serial,
                r.last_mutation_close_serial,
                r.last_merge_split_close_serial,
                r.status,
            ]
            for r in graph.native_assemblies()
        ],
        "high_watermarks": [
            [r.value, n]
            for r, n in sorted(state.assembly_high_watermarks.items(), key=lambda v: v[0].value)
        ],
        "cells_memberships": [[i, sorted(c.assembly_ids)] for i, c in sorted(state.cells.items())],
        "membership_reverse": [
            [i, sorted(ids)] for i, ids in sorted(state.member_assemblies.items())
        ],
        "forms": forms,
    }
    # Tuples are not canonical binary-record values.
    for record in forms:
        record["members"] = list(record["members"])
        record["witnesses"] = [list(w) for w in record["witnesses"]]
    return encode_record(_TAG, _VERSION, doc)


def decode_native_graph(data: bytes) -> SparseNetwork:
    try:
        doc = decode_record(data, _TAG, _VERSION)
        if type(doc) is not dict or set(doc) != {
            "base",
            "assemblies",
            "high_watermarks",
            "cells_memberships",
            "membership_reverse",
            "forms",
        }:
            raise ValueError("INVALID_NATIVE_W")
        graph = decode_production_graph(doc["base"])
        assemblies = {}
        for row in doc["assemblies"]:
            if type(row) is not list or len(row) != 8 or row[0] in assemblies:
                raise ValueError("INVALID_NATIVE_ASSEMBLY_RECORD")
            record = _assembly_record(row[0], Region(row[1]), tuple(row[2]), *row[3:])
            assemblies[record.assembly_id] = record
        highs = {}
        for region, high in doc["high_watermarks"]:
            if Region(region) in highs:
                raise ValueError("DUPLICATE_NATIVE_HIGH_WATERMARK")
            highs[Region(region)] = high
        memberships = {}
        for cell, ids in doc["cells_memberships"]:
            if cell in memberships or cell not in graph._state.cells:
                raise ValueError("INVALID_NATIVE_MEMBERSHIP_CELL")
            memberships[cell] = frozenset(ids)
        if set(memberships) != set(graph._state.cells):
            raise ValueError("MISSING_NATIVE_CELL_MEMBERSHIPS")
        reverse = {}
        for cell, ids in doc["membership_reverse"]:
            if cell in reverse:
                raise ValueError("DUPLICATE_NATIVE_MEMBER_REVERSE")
            reverse[cell] = frozenset(ids)
        forms = []
        for row in doc["forms"]:
            if type(row) is not dict:
                raise ValueError("INVALID_NATIVE_FORM_RECORD")
            item = dict(row)
            item["members"] = tuple(item["members"])
            item["witnesses"] = tuple(tuple(w) for w in item["witnesses"])
            forms.append(_form_record(**item))
        graph._state = replace(
            graph._state,
            cells=MappingProxyType(
                {i: replace(c, assembly_ids=memberships[i]) for i, c in graph._state.cells.items()}
            ),
            native_assemblies=MappingProxyType(assemblies),
            assembly_high_watermarks=MappingProxyType(highs),
            member_assemblies=MappingProxyType(reverse),
            native_form_log=tuple(forms),
        )
        if encode_native_graph(graph) != data:
            raise ValueError("NONCANONICAL_NATIVE_W")
        return graph
    except (KeyError, TypeError, IndexError, OverflowError, AttributeError) as exc:
        raise ValueError("INVALID_NATIVE_W") from exc
