"""Explicit experimental multi-Assembly capability, with historical dispatch."""

from dataclasses import dataclass

from dgca_next.graph.network import SparseNetwork
from dgca_next.learning.native_form import _form_at_end
from dgca_next.learning.native_lifecycle import NativeLifecycleCloseResult, _native_end
from dgca_next.learning.native_multi import (
    MultiAssemblyCloseResult,
    _multi_end,
    decode_multi_close,
    encode_multi_close,
)
from dgca_next.learning.proposals import decode_proposals
from dgca_next.learning.settlement import CloseResult
from dgca_next.persistence.native_codec import encode_native_graph
from dgca_next.persistence.native_store import NativeLifecycleRootStore


@dataclass(frozen=True, slots=True)
class PendingNativeInspection:
    """Uncommitted trusted END shadow; never a completed-root attestation."""

    close: MultiAssemblyCloseResult
    W: bytes
    committed: bool = False
    source_kind: str = "PROVISIONAL_TRUSTED_END_SHADOW"


class NativeMultiRootStore(NativeLifecycleRootStore):
    _operators_enabled = False
    _schema_label = "I4_NATIVE_MULTI_V1"
    _encode_close = staticmethod(encode_multi_close)
    _decode_close = staticmethod(decode_multi_close)

    def _finalize_close(
        self, graph: SparseNetwork, result: CloseResult, *, replay: bool
    ) -> tuple[SparseNetwork, CloseResult]:
        if replay:
            saved = self._connection.execute(
                "SELECT close_record FROM p01_roots WHERE exposure_id=?", (result.exposure_id,)
            ).fetchone()
            if saved is None:
                raise ValueError("MISSING_NATIVE_CLOSE")
            original = decode_multi_close(saved[0])
            # Reconstruct each accepted historical operator version exactly.
            # Selecting this capability never rewrites old close/W bytes.
            if type(original) is NativeLifecycleCloseResult:
                return _native_end(self._connection, graph, result, replay=True)
            if type(original) is not MultiAssemblyCloseResult:
                return _form_at_end(self._connection, graph, result, replay=True)
            return _multi_end(
                self._connection, graph, result, replay=True, close_version=original.close_version
            )
        return _multi_end(self._connection, graph, result, replay=replay)

    def inspect_pending_native(self, exposure_id: int) -> PendingNativeInspection:
        with self._read_snapshot():
            self._id(exposure_id)
            self._validate()
            root = self.root(exposure_id)
            if root is None or root.status != "OPEN" or root.next_order < 1:
                raise ValueError("NONEMPTY_OPEN_ROOT_REQUIRED")
            if self.view().open_root != exposure_id:
                raise ValueError("EXPOSURE_NOT_OPEN")
            serial, events = self._connection.execute(
                "SELECT COUNT(*),COALESCE(SUM(next_order),0) FROM p01_roots "
                "WHERE status='COMPLETED'"
            ).fetchone()
            rows = self._connection.execute(
                "SELECT proposals FROM p01_events WHERE exposure_id=? ORDER BY event_order",
                (exposure_id,),
            ).fetchall()
            proposals = tuple(p for row in rows for p in decode_proposals(row[0]))
            graph, close = self._settle_graph(
                self.graph(),
                exposure_id,
                serial + 1,
                proposals,
                event_clock=events + root.next_order,
            )
            graph, closed = _multi_end(
                self._connection,
                graph,
                close,
                replay=False,
                probe=True,
                graph_decoder=self._decode_graph,
                operators=self._operators_enabled,
                event_verifier=self._event_verifier(),
            )
            return PendingNativeInspection(closed, encode_native_graph(graph))
