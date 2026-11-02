"""Explicit proof-gated operator capability; all earlier versions stay exact."""

import hashlib
from dataclasses import replace

from dgca_next.graph.network import SparseNetwork
from dgca_next.learning.completed_event_clock import CooldownDecision, _verified_completed_prefix
from dgca_next.learning.native_multi import _multi_end
from dgca_next.learning.native_operators import (
    OperatorCloseResult,
    decode_operator_close,
    encode_operator_close,
)
from dgca_next.learning.proposals import LinkProposal
from dgca_next.learning.settlement import CloseResult
from dgca_next.persistence.multi_store import NativeMultiRootStore
from dgca_next.persistence.native_codec import _encode_native_shadow
from dgca_next.persistence.operator_codec import decode_operator_graph


class NativeOperatorRootStore(NativeMultiRootStore):
    _schema_label = "I4_NATIVE_OPERATORS_V1"
    _operators_enabled = True
    _decode_graph = staticmethod(decode_operator_graph)
    _encode_close = staticmethod(encode_operator_close)
    _decode_close = staticmethod(decode_operator_close)

    def _settle_graph(
        self,
        graph: SparseNetwork,
        exposure_id: int,
        serial: int,
        proposals: tuple[LinkProposal, ...],
        *,
        event_clock: int,
    ) -> tuple[SparseNetwork, CloseResult]:
        after, result = super()._settle_graph(
            graph, exposure_id, serial, proposals, event_clock=event_clock
        )
        if not graph._state.native_operator_log:
            return after, result
        # Synaptic settlement owns only physical evidence. Restore the extra
        # immutable operator lineage over its private physical shadow.
        after._state = replace(after._state, native_operator_log=graph._state.native_operator_log)
        return after, replace(
            result, graph_hash=hashlib.sha256(_encode_native_shadow(after)).hexdigest()
        )

    def _finalize_close(
        self, graph: SparseNetwork, result: CloseResult, *, replay: bool
    ) -> tuple[SparseNetwork, CloseResult]:
        if replay:
            row = self._connection.execute(
                "SELECT close_record FROM p01_roots WHERE exposure_id=?", (result.exposure_id,)
            ).fetchone()
            if row is None:
                raise ValueError("MISSING_NATIVE_CLOSE")
            if type(decode_operator_close(row[0])) is not OperatorCloseResult:
                return super()._finalize_close(graph, result, replay=True)
        return _multi_end(
            self._connection,
            graph,
            result,
            replay=replay,
            graph_decoder=self._decode_graph,
            operators=True,
        )

    def inspect_native_cooldown(self, assembly_id: int) -> CooldownDecision:
        """Actual live identity and completed history only; no mutation permit."""
        with self._read_snapshot():
            self._id(assembly_id)
            self._validate()
            record = self.graph()._state.native_assemblies.get(assembly_id)
            if record is None or record.status != "LIVE":
                raise ValueError("ACTUAL_LIVE_NATIVE_ID_REQUIRED")
            row = self._connection.execute(
                "SELECT close_record FROM p01_roots WHERE status='COMPLETED' "
                "ORDER BY close_serial DESC LIMIT 1"
            ).fetchone()
            if row is None:
                raise ValueError("COMPLETED_CLOCK_HISTORY_REQUIRED")
            close = self._decode_close(row[0])
            prefix = _verified_completed_prefix(
                self._connection, close, self._decode_close, replay=True
            )
            touched = (
                frozenset({assembly_id})
                if record.last_merge_split_close_serial == close.close_serial
                else frozenset()
            )
            return prefix.cooldown(
                assembly_id, record.last_merge_split_close_serial, edited_this_end=touched
            )
