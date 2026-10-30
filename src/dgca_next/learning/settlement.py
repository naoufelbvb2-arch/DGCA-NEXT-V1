"""Deterministic witnessed root settlement on one production graph shadow."""

import hashlib
from dataclasses import dataclass, replace
from types import MappingProxyType

from dgca_next.config import load_lab_config
from dgca_next.contracts import SynapseKey, SynapseScope
from dgca_next.graph.audit import validate_state
from dgca_next.graph.network import SparseNetwork, _eligible
from dgca_next.graph.synapse import Synapse, SynapseState
from dgca_next.learning.evidence import _positive_external_update
from dgca_next.learning.proposals import LinkProposal, decode_proposals, encode_proposals
from dgca_next.persistence.binary_records import decode_record, encode_record
from dgca_next.persistence.graph_codec import _key, _read_key, encode_production_graph

_CONFIG = load_lab_config()
_TAG = 0x43
_VERSION = 2


@dataclass(frozen=True, slots=True)
class Refusal:
    key: SynapseKey
    reason: str


@dataclass(frozen=True, slots=True)
class CloseResult:
    exposure_id: int
    close_serial: int
    event_clock: int
    accepted: tuple[LinkProposal, ...]
    refused: tuple[Refusal, ...]
    graph_hash: str


def _select_root_max(
    proposals: tuple[LinkProposal, ...], exposure_id: int
) -> dict[SynapseKey, LinkProposal]:
    """Select paired q/y by full binary64 q; this alone publishes nothing."""
    selected: dict[SynapseKey, LinkProposal] = {}
    for proposal in proposals:
        if type(proposal) is not LinkProposal or proposal.credit.root_id != exposure_id:
            raise ValueError("UNVERIFIED_ROOT_PROPOSAL")
        prior_winner = selected.get(proposal.key)
        if prior_winner is None or (
            -proposal.credit.q,
            proposal.credit.event_order,
            proposal.credit.ordinal,
        ) < (-prior_winner.credit.q, prior_winner.credit.event_order, prior_winner.credit.ordinal):
            selected[proposal.key] = proposal
    return selected


def _settle(
    graph: SparseNetwork,
    exposure_id: int,
    close_serial: int,
    proposals: tuple[LinkProposal, ...],
    *,
    event_clock: int,
) -> tuple[SparseNetwork, CloseResult]:
    """Reduce, check and apply in a shadow; caller owns atomic root authority."""
    if (
        type(graph) is not SparseNetwork
        or type(proposals) is not tuple
        or type(event_clock) is not int
        or event_clock < 0
    ):
        raise ValueError("INVALID_CLOSE_INPUT")
    graph.validate_graph()
    if any(c.fixture_only for c in graph.stored_cells()) or any(
        s.fixture_only for s in graph.synapses()
    ):
        raise ValueError("FIXTURE_GRAPH_FORBIDDEN")
    selected = _select_root_max(proposals, exposure_id)
    winners = sorted(
        selected.values(),
        key=lambda p: (
            1,
            -p.coactivity,
            -p.credit.q,
            p.key.source.cell_id,
            p.key.target.cell_id,
            tuple(SynapseScope).index(p.key.scope),
        ),
    )
    base = graph._state
    links = dict(base.synapses)
    outgoing = dict(base.outgoing)
    reservations = dict(base.reservations)
    accepted, refused = [], []
    limit = float(_CONFIG.parameter("E_max").value)
    for p in winners:
        key, c = p.key, p.credit
        source, target = key.source.cell_id, key.target.cell_id
        if (
            source not in base.cells
            or target not in base.cells
            or not _eligible(base, source, target)
        ):
            refused.append(Refusal(key, "STALE_LATENT_ELIGIBILITY"))
            continue
        src_event, dst_event = (
            base.cells[source].committed_event,
            base.cells[target].committed_event,
        )
        if (
            src_event is None
            or dst_event is None
            or src_event >= c.source_event_id
            or dst_event >= c.event_id
        ):
            refused.append(Refusal(key, "COMMITMENT_TIMING"))
            continue
        old = links.get(key)
        if old is not None and (
            old.fixture_only or any(credit.root_id == exposure_id for credit in old.credits)
        ):
            refused.append(Refusal(key, "ROOT_ALREADY_CREDITED"))
            continue
        if (
            old is not None
            and old.state is SynapseState.CANDIDATE
            and old.candidate_deadline is not None
            and event_clock > old.candidate_deadline
        ):
            refused.append(Refusal(key, "CANDIDATE_CONFIRMATION_EXPIRED"))
            continue
        current_keys = outgoing.get(source, frozenset())
        if key not in current_keys and len(current_keys) >= int(_CONFIG.parameter("B_i").value):
            refused.append(Refusal(key, "SOURCE_OUTGOING_CAPACITY"))
            continue
        if (
            key not in current_keys
            and key.source.region is not key.target.region
            and sum(k.source.region is not k.target.region for k in current_keys)
            >= int(_CONFIG.parameter("B_i_cross").value)
        ):
            refused.append(Refusal(key, "CROSS_OUTGOING_CAPACITY"))
            continue
        if old is None:
            updated = Synapse(
                key,
                1 if key.scope is SynapseScope.ASSOCIATIVE else 0,
                SynapseState.CANDIDATE,
                c.y,
                min(limit, c.q),
                0.0,
                1,
                c.event_id,
                False,
                False,
                (c,),
                event_clock + int(_CONFIG.parameter("W_conf").value),
            )
        else:
            strength, external, internal = _positive_external_update(
                old.S, old.E_ext, old.E_int, c.q, c.y
            )
            credits = (*old.credits, c)
            state = old.state
            if (
                len(credits) >= 2
                and strength >= float(_CONFIG.parameter("theta_S").value)
                and external >= limit * float(_CONFIG.parameter("theta_E").value)
            ):
                state = SynapseState.CONSOLIDATED
            updated = replace(
                old,
                S=strength,
                E_ext=external,
                E_int=internal,
                external_root_count=len(credits),
                credits=credits,
                state=state,
            )
        links[key] = updated
        reservations.pop(key, None)
        outgoing[source] = current_keys | {key}
        accepted.append(p)
    shadow_state = replace(
        base,
        synapses=MappingProxyType(links),
        reservations=MappingProxyType(reservations),
        outgoing=MappingProxyType(outgoing),
    )
    validate_state(shadow_state)
    result_graph = SparseNetwork()
    result_graph._state = shadow_state
    graph_hash = hashlib.sha256(encode_production_graph(result_graph)).hexdigest()
    return result_graph, CloseResult(
        exposure_id, close_serial, event_clock, tuple(accepted), tuple(refused), graph_hash
    )


def encode_close(close: CloseResult) -> bytes:
    doc = {
        "root": close.exposure_id,
        "serial": close.close_serial,
        "event_clock": close.event_clock,
        "accepted": encode_proposals(close.accepted),
        "refused": [[_key(r.key), r.reason] for r in close.refused],
        "W": close.graph_hash,
    }
    return encode_record(_TAG, _VERSION, doc)


def decode_close(data: bytes) -> CloseResult:
    try:
        doc = decode_record(data, _TAG, _VERSION)
        if type(doc) is not dict or set(doc) != {
            "root",
            "serial",
            "event_clock",
            "accepted",
            "refused",
            "W",
        }:
            raise ValueError("INVALID_CLOSE_RECORD")
        if (
            type(doc["root"]) is not int
            or doc["root"] < 0
            or type(doc["serial"]) is not int
            or doc["serial"] < 1
            or type(doc["event_clock"]) is not int
            or doc["event_clock"] < 1
        ):
            raise ValueError("INVALID_CLOSE_RECORD")
        if (
            type(doc["W"]) is not str
            or len(doc["W"]) != 64
            or any(c not in "0123456789abcdef" for c in doc["W"])
        ):
            raise ValueError("INVALID_CLOSE_RECORD")
        refused = tuple(Refusal(_read_key(row[0]), row[1]) for row in doc["refused"])
        result = CloseResult(
            doc["root"],
            doc["serial"],
            doc["event_clock"],
            decode_proposals(doc["accepted"]),
            refused,
            doc["W"],
        )
        if encode_close(result) != data:
            raise ValueError("NONCANONICAL_CLOSE_RECORD")
        return result
    except (TypeError, IndexError, KeyError, UnicodeError) as exc:
        raise ValueError("INVALID_CLOSE_RECORD") from exc
