"""Explicit R05 capability; authentic R replay precedes native END authority."""

from collections.abc import Callable
from typing import Any

from dgca_next.contracts import EventMode
from dgca_next.dynamics.activation import TwoPassResult
from dgca_next.dynamics.drive import aggregate
from dgca_next.dynamics.frontier import Frontiers
from dgca_next.dynamics.native_attractor import (
    NativeFeatureEvent,
    NativeRuntime,
    NativeTrace,
    NativeView,
    ObservationScope,
    _capture_native_view,
    _cold_native,
    _native_step,
    _restore_validated_state,
)
from dgca_next.dynamics.session import FeatureEvent
from dgca_next.dynamics.state import GraphSnapshot, Homeostasis
from dgca_next.graph.cell import ProductionAdmission
from dgca_next.graph.native_assembly import NativeAssemblyRecord
from dgca_next.graph.network import SparseNetwork
from dgca_next.graph.production import _admit_sensory_cohort
from dgca_next.learning.homeostasis_profile import (
    LanguageHomeostasis,
    preview_pre_event_adaptation,
)
from dgca_next.learning.native_multi import _multi_end
from dgca_next.learning.novelty import VerifiedLocalNovelty, _verified_novelty
from dgca_next.learning.observation import preflight
from dgca_next.learning.production_event import ExternalEventObservation, decode_event
from dgca_next.learning.settlement import CloseResult
from dgca_next.peripheral.sic import SICProjection
from dgca_next.persistence.binary_records import decode_record
from dgca_next.persistence.native_runtime_codec import encode_native_runtime, runtime_document
from dgca_next.persistence.native_store import NativeRootStore
from dgca_next.persistence.operator_store import NativeOperatorRootStore
from dgca_next.persistence.production_store import Hook
from dgca_next.persistence.store import R_COLD, RootStore


def _feature_event(p: SICProjection, boundary: bool) -> FeatureEvent:
    def decimal(value: int) -> str:
        return f"{value // 1_000_000}.{value % 1_000_000:06d}"

    return FeatureEvent(
        tuple((feature.decode("utf-8"), decimal(value)) for feature, value in p.input_features),
        decimal(p.salience_fixed),
        boundary,
        p.digest,
    )


def _event_features(raw: bytes) -> FeatureEvent:
    value: Any = decode_record(raw, 0x45, 2)

    def decimal(v: int) -> str:
        return f"{v // 1_000_000}.{v % 1_000_000:06d}"

    return FeatureEvent(
        tuple((bytes.fromhex(f).decode("utf-8"), decimal(v)) for f, v in value["features"]),
        decimal(value["salience"]),
        value["boundary"],
        value["digest"],
    )


class NativeAttractorRootStore(NativeOperatorRootStore):
    """Fresh Schema5 + R2 table; old capabilities refuse its table set."""

    _schema_label = "I4_NATIVE_ATTRACTOR_V1"
    _required_tables = NativeOperatorRootStore._required_tables | {"p05_runtime"}
    _scope = ObservationScope.UNSPECIFIED

    def _initialize_runtime_tables(self) -> None:
        self._connection.execute(
            "CREATE TABLE p05_runtime (event_id INTEGER PRIMARY KEY "
            "REFERENCES p01_events(event_id), record BLOB NOT NULL)"
        )

    def _runtime_observation(self, raw: bytes) -> ExternalEventObservation:
        return decode_event(runtime_document(raw)["event"])

    def _event_passes(
        self,
        snapshot: GraphSnapshot,
        h: Homeostasis,
        projection: SICProjection,
        previous: ExternalEventObservation | None,
        *,
        runtime: bytes,
        boundary: bool,
        exposure_id: int,
        before_w: bytes,
        before_h: bytes,
    ) -> tuple[TwoPassResult, dict[int, float], Frontiers, object]:
        view = _capture_native_view(self._decode_graph(before_w), before_w, before_h)
        state = (
            _cold_native(view, exposure_id, EventMode.LEARN)
            if runtime == R_COLD
            else (_restore_validated_state(runtime_document(runtime)["state"]))
        )
        trace = _native_step(
            view, state, NativeFeatureEvent(_feature_event(projection, boundary), self._scope)
        )
        return trace.passes, dict(trace.temporal), trace.state.frontiers, trace

    def _checkpoint_runtime(
        self,
        observation: ExternalEventObservation,
        native: object,
        before_r: bytes,
        after_w: bytes,
        after_h: bytes,
    ) -> bytes:
        if type(native) is not NativeTrace:
            raise ValueError("MISSING_NATIVE_EVENT_COMPUTATION")
        raw = encode_native_runtime(native, observation, before_r, after_w, after_h)
        self._connection.execute(
            "INSERT INTO p05_runtime VALUES (?,?)", (observation.event_id, raw)
        )
        return raw

    def event(
        self,
        exposure_id: int,
        order: int,
        features: tuple[tuple[str, str], ...],
        *,
        salience: str = "1.000000",
        boundary: bool = False,
        hook: Hook | None = None,
        observation_scope: ObservationScope = ObservationScope.UNSPECIFIED,
    ) -> ExternalEventObservation:
        if type(observation_scope) is not ObservationScope:
            raise ValueError("INVALID_EXTERNAL_OBSERVATION_SCOPE")
        self._scope = observation_scope
        try:
            return super().event(
                exposure_id, order, features, salience=salience, boundary=boundary, hook=hook
            )
        finally:
            self._scope = ObservationScope.UNSPECIFIED

    def _audit_native_events(self) -> dict[int, ExternalEventObservation]:
        rows = self._connection.execute(
            "SELECT e.event_id,e.exposure_id,e.event_order,e.record,e.w_before,e.w_after,"
            "e.h_before,e.h_after,r.record FROM p01_events e LEFT JOIN p05_runtime r "
            "ON r.event_id=e.event_id ORDER BY e.event_id"
        ).fetchall()
        if len(rows) != self._connection.execute("SELECT COUNT(*) FROM p05_runtime").fetchone()[0]:
            raise ValueError("NATIVE_R_JOURNAL_CARDINALITY")
        states: dict[int, bytes] = {}
        verified = {}
        for eid, exposure, order, raw, w, after_w, h, after_h, native in rows:
            if type(native) is not bytes:
                raise ValueError("MISSING_NATIVE_R_CHECKPOINT")
            doc = runtime_document(native)
            observation = decode_event(raw)
            view = _capture_native_view(self._decode_graph(w), w, h)
            before_r = states.get(exposure, R_COLD)
            state = (
                _cold_native(view, exposure, EventMode.LEARN)
                if before_r == R_COLD
                else (_restore_validated_state(runtime_document(before_r)["state"]))
            )
            if (
                state.next_order != order
                or state.scope_id != exposure
                or state.mode is not EventMode.LEARN
            ):
                raise ValueError("NATIVE_R_EVENT_SEQUENCE")
            trace = _native_step(
                view,
                state,
                NativeFeatureEvent(_event_features(raw), ObservationScope(doc["scope"])),
            )
            first, second = trace.passes.first, trace.passes.second
            expected = (
                tuple(sorted(first.raw.items())),
                tuple(sorted(first.normalized.items())),
                tuple(sorted(first.activity.items())),
                tuple(sorted(second.raw.items())),
                tuple(sorted(second.normalized.items())),
                tuple(sorted(second.activity.items())),
                tuple(sorted(trace.temporal.items())),
                tuple(sorted(aggregate(trace.passes.synchronous).items())),
                tuple(sorted(trace.passes.emitters)),
                tuple(sorted(trace.state.frontiers.learning)),
                tuple(sorted(trace.state.frontiers.step)),
            )
            actual = (
                observation.pass1_raw,
                observation.pass1_normalized,
                observation.pass1,
                observation.final_raw,
                observation.final_normalized,
                observation.final,
                observation.temporal,
                observation.synchronous,
                observation.emitters,
                observation.learning_frontier,
                observation.frontier,
            )
            if actual != expected:
                raise ValueError("NATIVE_EVENT_NEURAL_TRACE_MISMATCH")
            profile = LanguageHomeostasis.decode(h)
            features = _event_features(raw)
            draft = preflight(
                view.graph, view.homeostasis, features.features, salience=features.salience
            )
            serial = self._connection.execute(
                "SELECT COUNT(*) FROM p01_roots WHERE status='COMPLETED' AND exposure_id<?",
                (exposure,),
            ).fetchone()[0]
            after = _admit_sensory_cohort(
                self._decode_graph(w),
                admission=ProductionAdmission(exposure, eid, order, observation.digest),
                born=draft.accepted,
                frontier={i: second.activity[i] for i in trace.state.frontiers.learning},
                completed_closes=serial,
            )
            if (
                self._encode_graph(after) != after_w
                or preview_pre_event_adaptation(profile, view.graph, second.activity).encode()
                != after_h
            ):
                raise ValueError("NATIVE_EVENT_WH_CHECKPOINT_MISMATCH")
            if encode_native_runtime(trace, observation, before_r, after_w, after_h) != native:
                raise ValueError("NATIVE_R_REDERIVATION_MISMATCH")
            states[exposure] = native
            verified[eid] = observation
        row = self._metadata()
        opened = row[9]
        if opened is not None and type(opened) is not int:
            raise ValueError("INVALID_NATIVE_OPEN_ROOT")
        expected_runtime = states.get(opened, R_COLD) if opened is not None else R_COLD
        if row[7] != expected_runtime:
            raise ValueError("NATIVE_R_METADATA_MISMATCH")
        return verified

    def _validate(self) -> None:
        row = self._metadata()
        if self._validated == (row, self._data_version()):
            return
        self._audit_native_events()
        super()._validate()

    def _event_verifier(self) -> Callable[[ExternalEventObservation], None]:
        verified = self._audit_native_events()

        def verify(event: ExternalEventObservation) -> None:
            if verified.get(event.event_id) != event:
                raise ValueError("UNVERIFIED_NATIVE_FORM_WITNESS")

        return verify

    def _finalize_close(
        self, graph: SparseNetwork, result: CloseResult, *, replay: bool
    ) -> tuple[SparseNetwork, CloseResult]:
        return _multi_end(
            self._connection,
            graph,
            result,
            replay=replay,
            graph_decoder=self._decode_graph,
            operators=True,
            event_verifier=self._event_verifier(),
        )

    def verified_local_novelty(
        self, exposure_id: int, order: int, receiver_id: int
    ) -> VerifiedLocalNovelty:
        with self._read_snapshot():
            self._validate()
            return _verified_novelty(
                self._connection,
                exposure_id,
                order,
                receiver_id,
                graph_decoder=self._decode_graph,
                verify_activation=False,
            )[0]


def _read_view(store: RootStore) -> NativeView:
    if type(store) is not RootStore or not isinstance(store._backend, NativeRootStore):
        raise ValueError("AUTHENTICATED_NATIVE_ROOTSTORE_REQUIRED")
    backend = store._backend
    backend._validate()
    backend.assert_read_only_allowed()
    row = backend._metadata()
    w, h = row[8], row[6]
    if not isinstance(w, bytes) or not isinstance(h, bytes):
        raise ValueError("CORRUPT_NATIVE_SOURCE")
    return _capture_native_view(backend._decode_graph(w), w, h)


def start_native_session(store: RootStore, *, session_id: int) -> NativeRuntime:
    if type(store) is not RootStore:
        raise ValueError("AUTHENTICATED_NATIVE_ROOTSTORE_REQUIRED")
    with store._backend._read_snapshot():
        return _cold_native(_read_view(store), session_id, EventMode.RETRIEVE)


def inspect_native_subject(
    store: RootStore,
    assembly_id: int,
    *,
    generation: int | None = None,
) -> NativeAssemblyRecord:
    if type(store) is not RootStore:
        raise ValueError("AUTHENTICATED_NATIVE_ROOTSTORE_REQUIRED")
    with store._backend._read_snapshot():
        return _read_view(store).subject(assembly_id, generation)


def native_session_step(
    store: RootStore,
    state: NativeRuntime,
    event: NativeFeatureEvent,
    *,
    context_sigma: bool = True,
) -> NativeTrace:
    if (
        type(store) is not RootStore
        or type(state) is not NativeRuntime
        or state.mode is not EventMode.RETRIEVE
    ):
        raise ValueError("AUTHENTICATED_READ_ONLY_NATIVE_SESSION_REQUIRED")
    with store._backend._read_snapshot():
        return _native_step(_read_view(store), state, event, context_sigma=context_sigma)
