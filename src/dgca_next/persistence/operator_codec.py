"""Optional W5 lineage extension; accepted old W/close bytes stay unchanged."""

from dataclasses import replace
from types import MappingProxyType

from dgca_next.contracts import Region
from dgca_next.graph.native_assembly import _form_record
from dgca_next.graph.native_mutation import _mutation_record
from dgca_next.graph.native_operator import read_assembly_row
from dgca_next.graph.network import SparseNetwork
from dgca_next.persistence.binary_records import decode_record
from dgca_next.persistence.graph_codec import decode_production_graph
from dgca_next.persistence.native_codec import decode_native_graph, encode_native_graph


def decode_operator_graph(data: bytes) -> SparseNetwork:
    doc = decode_record(data, 0x57, 5)
    if type(doc) is not dict or "operator_journal_version" not in doc:
        return decode_native_graph(data)
    try:
        fields = {
            "base",
            "assemblies",
            "high_watermarks",
            "cells_memberships",
            "membership_reverse",
            "forms",
            "operator_journal_version",
            "operators",
        }
        if (
            set(doc) not in (fields, fields | {"structural_journal_version", "mutations"})
            or type(doc["operator_journal_version"]) is not int
            or doc["operator_journal_version"] != 1
            or not doc["operators"]
            or (
                "mutations" in doc
                and (
                    type(doc["structural_journal_version"]) is not int
                    or doc["structural_journal_version"] != 1
                )
            )
        ):
            raise ValueError("INVALID_OPERATOR_W_VERSION")
        graph = decode_production_graph(doc["base"])
        registry = {}
        for row in doc["assemblies"]:
            record = read_assembly_row(row)
            if record.assembly_id in registry:
                raise ValueError("DUPLICATE_NATIVE_ASSEMBLY")
            registry[record.assembly_id] = record
        cells = dict(graph._state.cells)
        memberships = {}
        for cell, ids in doc["cells_memberships"]:
            if cell not in cells or cell in memberships:
                raise ValueError("INVALID_NATIVE_MEMBERSHIP_CELL")
            memberships[cell] = frozenset(ids)
        if set(memberships) != set(cells):
            raise ValueError("MISSING_NATIVE_CELL_MEMBERSHIPS")
        reverse = {}
        for cell, ids in doc["membership_reverse"]:
            if cell in reverse:
                raise ValueError("DUPLICATE_NATIVE_MEMBER_REVERSE")
            reverse[cell] = frozenset(ids)
        forms = []
        for row in doc["forms"]:
            forms.append(
                _form_record(
                    **(
                        row
                        | {
                            "members": tuple(row["members"]),
                            "witnesses": tuple(tuple(w) for w in row["witnesses"]),
                        }
                    )
                )
            )
        graph._state = replace(
            graph._state,
            cells=MappingProxyType(
                {i: replace(c, assembly_ids=memberships[i]) for i, c in cells.items()}
            ),
            native_assemblies=MappingProxyType(registry),
            assembly_high_watermarks=MappingProxyType(
                {Region(r): n for r, n in doc["high_watermarks"]}
            ),
            member_assemblies=MappingProxyType(reverse),
            native_form_log=tuple(forms),
            native_mutation_log=tuple(_mutation_record(**r) for r in doc.get("mutations", [])),
            native_operator_log=tuple(doc["operators"]),
        )
        if encode_native_graph(graph) != data:
            raise ValueError("NONCANONICAL_OPERATOR_W")
        return graph
    except (TypeError, KeyError, IndexError) as exc:
        raise ValueError("INVALID_OPERATOR_W") from exc
