"""Immutable native laboratory capability: Schema 5, fresh databases only."""

from dgca_next.graph.network import SparseNetwork
from dgca_next.learning.native_form import _form_at_end, decode_native_close, encode_native_close
from dgca_next.learning.novelty import RecyclingDecision
from dgca_next.learning.proposals import decode_proposals
from dgca_next.learning.settlement import CloseResult
from dgca_next.persistence.form_inspection import FormEligibilityDiagnostic, _inspect_completed_root
from dgca_next.persistence.native_codec import (
    decode_native_graph,
    empty_native_graph,
    encode_native_graph,
)
from dgca_next.persistence.production_store import ProductionRootStore


class NativeRootStore(ProductionRootStore):
    _schema_version = 5
    _schema_label = "I4_NATIVE_FORM_V1"
    _encode_graph = staticmethod(encode_native_graph)
    _decode_graph = staticmethod(decode_native_graph)
    _encode_close = staticmethod(encode_native_close)
    _decode_close = staticmethod(decode_native_close)
    _empty_graph = staticmethod(empty_native_graph)

    def _validate(self) -> None:
        if self._connection.execute("SELECT COUNT(*) FROM p04_requests").fetchone()[0]:
            raise ValueError("I4_REWIRING_CONFLICT")
        super()._validate()

    def request_recycling(
        self, exposure_id: int, event_order: int, owner_id: int, slot_index: int
    ) -> None:
        raise ValueError("I4_REWIRING_CONFLICT")

    def inspect_recycling(
        self, exposure_id: int, order: int, receiver_id: int, owner_id: int, slot_index: int
    ) -> RecyclingDecision:
        raise ValueError("I4_REWIRING_CONFLICT")

    def _finalize_close(
        self, graph: SparseNetwork, result: CloseResult, *, replay: bool
    ) -> tuple[SparseNetwork, CloseResult]:
        return _form_at_end(self._connection, graph, result, replay=replay)

    def inspect_form_eligibility(self, exposure_id: int) -> FormEligibilityDiagnostic:
        """Historical pre-FORM diagnostic, never a publication authority."""
        with self._read_snapshot():
            try:
                self._id(exposure_id)
                self._validate()
                row = self._connection.execute(
                    "SELECT status,close_record FROM p01_roots WHERE exposure_id=?", (exposure_id,)
                ).fetchone()
                if row is None or row[0] != "COMPLETED":
                    raise ValueError("ROOT_NOT_COMPLETED")
                close = self._decode_close(row[1])
                last = self._connection.execute(
                    "SELECT w_after FROM p01_events WHERE exposure_id=? "
                    "ORDER BY event_order DESC LIMIT 1",
                    (exposure_id,),
                ).fetchone()
                rows = self._connection.execute(
                    "SELECT proposals FROM p01_events WHERE exposure_id=? ORDER BY event_order",
                    (exposure_id,),
                ).fetchall()
                proposals = tuple(p for r in rows for p in decode_proposals(r[0]))
                graph, _ = self._settle_graph(
                    self._decode_graph(last[0]),
                    exposure_id,
                    close.close_serial,
                    proposals,
                    event_clock=close.event_clock,
                )
                return _inspect_completed_root(
                    self._connection,
                    exposure_id,
                    graph_decoder=self._decode_graph,
                    graph_encoder=self._encode_graph,
                    post_evidence_graph=graph,
                )
            except ValueError as exc:
                raise ValueError(f"UNVERIFIED_FORM_EVENT: {exc}") from exc
