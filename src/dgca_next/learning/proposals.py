"""Witnessed P02 proposal derivation from frozen production EVENT records."""

import json
from dataclasses import dataclass

from dgca_next.contracts import CellAddress, Region, SynapseKey, SynapseScope
from dgca_next.dynamics.state import GraphSnapshot
from dgca_next.graph.synapse import ProductionCredit
from dgca_next.learning.evidence import preview_positive_numbers
from dgca_next.learning.production_event import ExternalEventObservation
from dgca_next.persistence.graph_codec import _float, _key, _read_key

_TAG = b"DGCA-P02-P\x01\0"


@dataclass(frozen=True, slots=True)
class LinkProposal:
    key: SynapseKey
    credit: ProductionCredit
    coactivity: float
    event_graph_hash: str
    source_x_fixed: int
    target_x_fixed: int


def _derive_proposals(
    graph: GraphSnapshot,
    event: ExternalEventObservation,
    previous: ExternalEventObservation | None,
    threshold: float,
) -> tuple[LinkProposal, ...]:
    """Derive records only from RootStore's frozen W and external event journal."""
    if type(graph) is not GraphSnapshot or type(event) is not ExternalEventObservation:
        raise ValueError("UNVERIFIED_PROPOSAL_EVENT")
    graph.validate()
    if event.pre_committed != tuple(sorted(graph.committed_ids)):
        raise ValueError("PROPOSAL_PRESTATE_MISMATCH")
    x, final = dict(event.X_fixed), dict(event.final)
    eligible = tuple(
        sorted(i for i in graph.committed_ids if x.get(i, 0) > 0 and final[i] >= threshold)
    )
    sources = tuple(
        sorted(i for i in event.emitters if i in graph.committed_ids and x.get(i, 0) > 0)
    )
    candidates: list[tuple[SynapseKey, ExternalEventObservation, float, float, int, int]] = []
    for source in sources:
        for target in eligible:
            if source != target and graph.eligible(source, target):
                candidates.append(
                    (
                        SynapseKey(
                            CellAddress.from_cell_id(source),
                            CellAddress.from_cell_id(target),
                            SynapseScope.LOCAL,
                        ),
                        event,
                        final[source],
                        final[target],
                        x[source],
                        x[target],
                    )
                )
    if previous is not None and not event.boundary:
        if (
            previous.exposure_id != event.exposure_id
            or previous.event_order + 1 != event.event_order
        ):
            raise ValueError("INVALID_TEMPORAL_PROVENANCE")
        px, pf = dict(previous.X_fixed), dict(previous.final)
        for source in previous.frontier:
            if source not in previous.pre_committed or px.get(source, 0) <= 0:
                continue
            for target in eligible:
                if source != target and graph.eligible(source, target):
                    candidates.append(
                        (
                            SynapseKey(
                                CellAddress.from_cell_id(source),
                                CellAddress.from_cell_id(target),
                                SynapseScope.ASSOCIATIVE,
                            ),
                            previous,
                            pf[source],
                            final[target],
                            px[source],
                            x[target],
                        )
                    )
    result: list[LinkProposal] = []
    for key, source_event, source_a, target_a, source_x, target_x in candidates:
        if key.source.region is not Region.LANGUAGE or key.target.region is not Region.LANGUAGE:
            raise ValueError("UNSUPPORTED_PRODUCTION_REGION")
        numbers = preview_positive_numbers(key.scope, source_a, target_a, threshold)
        if not numbers.threshold_passed or numbers.q <= 0:
            continue
        credit = ProductionCredit(
            event.exposure_id,
            event.event_id,
            event.event_order,
            len(result),
            source_event.event_id,
            source_event.digest,
            event.digest,
            source_a,
            target_a,
            threshold,
            numbers.q,
            numbers.y,
        )
        result.append(
            LinkProposal(key, credit, numbers.coactivity, event.pre_w_hash, source_x, target_x)
        )
    return tuple(result)


def encode_proposals(proposals: tuple[LinkProposal, ...]) -> bytes:
    rows = []
    for p in proposals:
        c = p.credit
        rows.append(
            [
                _key(p.key),
                c.root_id,
                c.event_id,
                c.event_order,
                c.ordinal,
                c.source_event_id,
                c.source_digest,
                c.target_digest,
                c.source_activity.hex(),
                c.target_activity.hex(),
                c.target_threshold.hex(),
                c.q.hex(),
                c.y.hex(),
                p.coactivity.hex(),
                p.event_graph_hash,
                p.source_x_fixed,
                p.target_x_fixed,
            ]
        )
    return _TAG + json.dumps(rows, separators=(",", ":"), ensure_ascii=True).encode("ascii")


def decode_proposals(data: bytes) -> tuple[LinkProposal, ...]:
    if type(data) is not bytes or not data.startswith(_TAG):
        raise ValueError("UNSUPPORTED_PROPOSAL_SCHEMA")
    try:
        rows = json.loads(data[len(_TAG) :].decode("ascii"))
        if type(rows) is not list:
            raise ValueError("INVALID_PROPOSAL_JOURNAL")
        result = []
        for row in rows:
            if type(row) is not list or len(row) != 17:
                raise ValueError("INVALID_PROPOSAL_JOURNAL")
            credit = ProductionCredit(*row[1:8], *(_float(x) for x in row[8:13]))
            result.append(
                LinkProposal(_read_key(row[0]), credit, _float(row[13]), row[14], row[15], row[16])
            )
        proposals = tuple(result)
        if encode_proposals(proposals) != data:
            raise ValueError("NONCANONICAL_PROPOSAL_JOURNAL")
        return proposals
    except (KeyError, TypeError, IndexError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("INVALID_PROPOSAL_JOURNAL") from exc
