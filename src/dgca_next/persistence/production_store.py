"""P02 production roots, witnessed EVENT staging and atomic END settlement."""

import hashlib
import sqlite3
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from pathlib import Path

from dgca_next.config import load_lab_config
from dgca_next.contracts import Region
from dgca_next.dynamics.activation import two_pass
from dgca_next.dynamics.drive import aggregate, temporal_drives
from dgca_next.dynamics.frontier import final_frontiers
from dgca_next.dynamics.state import GraphSnapshot
from dgca_next.graph import SparseNetwork
from dgca_next.graph.cell import ProductionAdmission
from dgca_next.graph.latent import LATENT_POLICY_VERSION
from dgca_next.graph.production import _admit_sensory_cohort
from dgca_next.integrity import EXPECTED_SPECS, verify_specs
from dgca_next.learning.homeostasis_profile import (
    PROFILE_VERSION,
    LanguageHomeostasis,
    preview_pre_event_adaptation,
)
from dgca_next.learning.observation import preflight
from dgca_next.learning.production_event import (
    SALT_HASH,
    ExternalEventObservation,
    _numbers,
    decode_event,
    encode_event,
)
from dgca_next.learning.proposals import (
    LinkProposal,
    _derive_proposals,
    decode_proposals,
    encode_proposals,
)
from dgca_next.learning.settlement import CloseResult, _settle, decode_close, encode_close
from dgca_next.persistence.graph_codec import decode_production_graph, encode_production_graph
from dgca_next.persistence.store import R_COLD, RootView, StoreView

Hook = Callable[[str], None]


def _sha(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _checkpoint_digest(*parts: bytes) -> str:
    digest = hashlib.sha256(b"DGCA-P01-CHECKPOINT\0")
    for part in parts:
        digest.update(len(part).to_bytes(8, "big"))
        digest.update(part)
    return digest.hexdigest()


class ProductionRootStore:
    """Exclusive external LEARN root and atomic sensory EVENT checkpoint."""

    def __init__(self, path: Path, *, repository_root: Path, code_revision: str) -> None:
        import re

        if not isinstance(path, Path):
            raise ValueError("INVALID_STORE_PATH")
        if type(code_revision) is not str or not re.fullmatch(r"[0-9a-f]{40}", code_revision):
            raise ValueError("INVALID_CODE_REVISION")
        verify_specs(repository_root)
        self._revision = code_revision
        self._connection = sqlite3.connect(str(path), isolation_level=None)
        self._connection.execute("PRAGMA foreign_keys=ON")
        self._connection.execute("PRAGMA synchronous=FULL")
        try:
            tables = {
                r[0]
                for r in self._connection.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
                )
            }
            if not tables:
                self._initialize()
            elif tables != {"p01_metadata", "p01_roots", "p01_events"}:
                raise ValueError("UNSUPPORTED_STORE_SCHEMA")
            else:
                version = self._connection.execute(
                    "SELECT schema_version FROM p01_metadata WHERE id=1"
                ).fetchone()
                if version is None or version[0] != 3:
                    raise ValueError("UNSUPPORTED_PRODUCTION_SCHEMA: P02 requires version 3")
            with self._read_snapshot():
                self._validate()
        except BaseException:
            self._connection.close()
            raise

    @contextmanager
    def _transaction(self) -> Iterator[None]:
        self._connection.execute("BEGIN IMMEDIATE")
        try:
            yield
            self._connection.execute("COMMIT")
        except BaseException:
            if self._connection.in_transaction:
                self._connection.execute("ROLLBACK")
            raise

    @contextmanager
    def _read_snapshot(self) -> Iterator[None]:
        """Bind all validation and view reads to one SQLite snapshot."""
        started = not self._connection.in_transaction
        if started:
            self._connection.execute("BEGIN")
        try:
            yield
            if started:
                self._connection.execute("COMMIT")
        except BaseException:
            if started and self._connection.in_transaction:
                self._connection.execute("ROLLBACK")
            raise

    def _initialize(self) -> None:
        with self._transaction():
            self._connection.execute(
                "CREATE TABLE p01_metadata (id INTEGER PRIMARY KEY CHECK(id=1), "
                "schema_version INTEGER NOT NULL, config_hash TEXT NOT NULL, "
                "core_hash TEXT NOT NULL, lla_hash TEXT NOT NULL, code_revision TEXT NOT NULL, "
                "latent_version TEXT NOT NULL, h_state BLOB NOT NULL, r_state BLOB NOT NULL, "
                "w_state BLOB NOT NULL, open_root INTEGER, high_watermark INTEGER NOT NULL, "
                "event_high INTEGER NOT NULL, completed_closes INTEGER NOT NULL)"
            )
            self._connection.execute(
                "CREATE TABLE p01_roots (exposure_id INTEGER PRIMARY KEY, status TEXT NOT NULL, "
                "next_order INTEGER NOT NULL, h_begin BLOB NOT NULL, w_begin BLOB NOT NULL, "
                "h_end BLOB, w_end BLOB, close_serial INTEGER, close_record BLOB, close_hash TEXT)"
            )
            self._connection.execute(
                "CREATE TABLE p01_events (event_id INTEGER PRIMARY KEY, "
                "exposure_id INTEGER NOT NULL REFERENCES p01_roots(exposure_id), "
                "event_order INTEGER NOT NULL, record BLOB NOT NULL, w_before BLOB NOT NULL, "
                "w_after BLOB NOT NULL, h_before BLOB NOT NULL, h_after BLOB NOT NULL, "
                "proposals BLOB NOT NULL, "
                "checkpoint_hash TEXT NOT NULL, "
                "UNIQUE(exposure_id,event_order))"
            )
            self._connection.execute(
                "INSERT INTO p01_metadata VALUES (1,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (
                    3,
                    load_lab_config().sha256,
                    EXPECTED_SPECS[0][1],
                    EXPECTED_SPECS[1][1],
                    self._revision,
                    LATENT_POLICY_VERSION,
                    LanguageHomeostasis.initial().encode(),
                    R_COLD,
                    encode_production_graph(SparseNetwork()),
                    None,
                    -1,
                    -1,
                    0,
                ),
            )

    def _metadata(self) -> tuple[object, ...]:
        row = self._connection.execute(
            "SELECT schema_version,config_hash,core_hash,lla_hash,code_revision,latent_version,"
            "h_state,r_state,w_state,open_root,high_watermark,event_high,completed_closes "
            "FROM p01_metadata WHERE id=1"
        ).fetchone()
        if row is None:
            raise ValueError("CORRUPT_STORE_METADATA")
        return tuple(row)

    @staticmethod
    def _id(exposure_id: int) -> None:
        if type(exposure_id) is not int or not 0 <= exposure_id <= 2**63 - 1:
            raise ValueError("INVALID_EXPOSURE_ID")

    def _validate(self) -> None:
        row = self._metadata()
        identity = (
            3,
            load_lab_config().sha256,
            EXPECTED_SPECS[0][1],
            EXPECTED_SPECS[1][1],
            self._revision,
            LATENT_POLICY_VERSION,
        )
        if row[:6] != identity:
            raise ValueError("STORE_IDENTITY_MISMATCH")
        h, runtime, w = row[6:9]
        if type(h) is not bytes or type(runtime) is not bytes or type(w) is not bytes:
            raise ValueError("CORRUPT_STORE_METADATA")
        profile = LanguageHomeostasis.decode(h)
        graph = decode_production_graph(w)
        profile.materialize(frozenset(c.cell_id for c in graph.stored_cells()))
        roots = self._connection.execute(
            "SELECT exposure_id,status,next_order,h_begin,w_begin,h_end,w_end,close_serial,"
            "close_record,close_hash FROM p01_roots ORDER BY exposure_id"
        ).fetchall()
        events = self._connection.execute(
            "SELECT event_id,exposure_id,event_order,record,w_before,w_after,h_before,h_after,"
            "proposals,checkpoint_hash "
            "FROM p01_events ORDER BY event_id"
        ).fetchall()
        if row[10] != (roots[-1][0] if roots else -1) or row[11] != (
            events[-1][0] if events else -1
        ):
            raise ValueError("INVALID_HIGH_WATERMARK")
        event_map: dict[tuple[int, int], ExternalEventObservation] = {}
        counts: dict[int, int] = {}
        root_begins = {root[0]: root[3] for root in roots}
        root_graphs = {root[0]: root[4] for root in roots}
        last_h: dict[int, bytes] = {}
        last_w: dict[int, bytes] = {}
        staged_by_root: dict[int, list[LinkProposal]] = {}
        previous_id = -1
        previous_exposure = -1
        for (
            event_id,
            exposure,
            order,
            raw,
            before_w,
            after_w,
            before_h,
            after_h,
            proposal_data,
            checksum,
        ) in events:
            if (
                event_id != previous_id + 1
                or order != counts.get(exposure, 0)
                or exposure < previous_exposure
                or exposure not in root_begins
                or before_w != last_w.get(exposure, root_graphs.get(exposure))
                or before_h != last_h.get(exposure, root_begins.get(exposure))
            ):
                raise ValueError("INVALID_EVENT_JOURNAL_ORDER")
            previous_id = event_id
            previous_exposure = exposure
            last_w[exposure] = after_w
            last_h[exposure] = after_h
            counts[exposure] = order + 1
            if checksum != _checkpoint_digest(
                raw, before_w, after_w, before_h, after_h, proposal_data
            ):
                raise ValueError("EVENT_CHECKPOINT_HASH_MISMATCH")
            observation = decode_event(raw)
            if (observation.event_id, observation.exposure_id, observation.event_order) != (
                event_id,
                exposure,
                order,
            ):
                raise ValueError("EVENT_IDENTITY_MISMATCH")
            before = decode_production_graph(before_w)
            after = decode_production_graph(after_w)
            before_profile = LanguageHomeostasis.decode(before_h)
            LanguageHomeostasis.decode(after_h)
            if observation.pre_w_hash != _sha(before_w) or observation.pre_h_hash != _sha(before_h):
                raise ValueError("EVENT_PRESTATE_MISMATCH")
            pre = frozenset(c.cell_id for c in before.stored_cells())
            post = frozenset(c.cell_id for c in after.stored_cells())
            if observation.pre_committed != tuple(sorted(pre)) or post - pre != frozenset(
                observation.born
            ):
                raise ValueError("EVENT_BIRTH_MISMATCH")
            x = dict(observation.X_fixed)
            previous = (
                event_map.get((exposure, order - 1)) if order and not observation.boundary else None
            )
            if (
                observation.previous != (() if previous is None else previous.final)
                or {i for i, _ in observation.pass1} != set(pre)
                or {i for i, _ in observation.final} != set(pre)
                or not set(observation.emitters) <= set(pre)
                or not set(observation.learning_frontier) <= set(pre)
                or not set(observation.frontier) <= (set(pre) & set(x))
            ):
                raise ValueError("INVALID_EVENT_CAUSAL_TRACE")
            threshold = before_profile.overrides.thresholds[Region.LANGUAGE]
            staged = _derive_proposals(
                GraphSnapshot.capture(before), observation, previous, threshold
            )
            if (
                encode_proposals(staged) != proposal_data
                or decode_proposals(proposal_data) != staged
            ):
                raise ValueError("EVENT_PROPOSAL_MISMATCH")
            staged_by_root.setdefault(exposure, []).extend(staged)
            eligible = sorted(
                ((i, u) for i, u in x.items() if i not in pre and u > 1),
                key=lambda p: (-p[1], p[0]),
            )
            if set(observation.born) != {i for i, _ in eligible[:12]} or set(
                observation.deferred
            ) != {i for i, _ in eligible[12:]}:
                raise ValueError("EVENT_COHORT_MISMATCH")
            admission = ProductionAdmission(exposure, event_id, order, observation.digest)
            if (
                any(
                    before.cell(i) != after.cell(i)
                    or before.latent_slots(i) != after.latent_slots(i)
                    for i in pre
                )
                or any(after.cell(i).admission != admission for i in observation.born)
                or (
                    before._state.synapses != after._state.synapses
                    or before._state.reservations != after._state.reservations
                    or before._state.outgoing != after._state.outgoing
                )
            ):
                raise ValueError("EVENT_GRAPH_MISMATCH")
            event_map[(exposure, order)] = observation
        opened = []
        expected_root_h = LanguageHomeostasis.initial().encode()
        expected_root_w = encode_production_graph(SparseNetwork())
        completed_closes = 0
        completed_event_clock = 0
        for (
            exposure,
            status,
            order,
            h_begin,
            w_begin,
            h_end,
            w_end,
            close_serial,
            close_record,
            close_hash,
        ) in roots:
            self._id(exposure)
            LanguageHomeostasis.decode(h_begin)
            if (
                status not in ("OPEN", "ABORTED", "COMPLETED")
                or type(order) is not int
                or order != counts.get(exposure, 0)
                or h_begin != expected_root_h
                or w_begin != expected_root_w
            ):
                raise ValueError("INVALID_ROOT_JOURNAL")
            if status == "OPEN":
                opened.append(exposure)
                if any(
                    v is not None for v in (h_end, w_end, close_serial, close_record, close_hash)
                ):
                    raise ValueError("INVALID_OPEN_ROOT_JOURNAL")
                expected_root_w = last_w.get(exposure, w_begin)
                expected_root_h = last_h.get(exposure, h_begin)
            elif status == "ABORTED":
                if (
                    h_end != h_begin
                    or w_end != last_w.get(exposure, w_begin)
                    or close_serial is not None
                    or close_record is not None
                    or close_hash != _checkpoint_digest(h_end, w_end)
                ):
                    raise ValueError("INVALID_ABORT_CHECKPOINT")
                expected_root_w, expected_root_h = w_end, h_end
            else:
                completed_closes += 1
                completed_event_clock += order
                if not order or close_serial != completed_closes or h_end != last_h.get(exposure):
                    raise ValueError("INVALID_COMPLETED_ROOT")
                before_close = decode_production_graph(last_w[exposure])
                after_close, result = _settle(
                    before_close,
                    exposure,
                    completed_closes,
                    tuple(staged_by_root.get(exposure, [])),
                    event_clock=completed_event_clock,
                )
                if (
                    w_end != encode_production_graph(after_close)
                    or close_record != encode_close(result)
                    or decode_close(close_record) != result
                    or close_hash != _checkpoint_digest(close_record, h_end, w_end)
                ):
                    raise ValueError("INVALID_CLOSE_CHECKPOINT")
                expected_root_w, expected_root_h = w_end, h_end
        if row[12] != completed_closes:
            raise ValueError("INVALID_COMPLETED_CLOSE_SERIAL")
        if (
            len(opened) > 1
            or row[9] != (opened[0] if opened else None)
            or (opened and roots[-1][0] != opened[0])
        ):
            raise ValueError("INVALID_OPEN_ROOT_JOURNAL")
        if runtime != R_COLD:
            last = decode_event(runtime)
            if (
                row[9] != last.exposure_id
                or last.event_order != counts.get(last.exposure_id, 0) - 1
                or event_map.get((last.exposure_id, last.event_order)) != last
            ):
                raise ValueError("INVALID_RUNTIME_CHECKPOINT")
        elif opened and counts.get(opened[0], 0):
            raise ValueError("MISSING_RUNTIME_CHECKPOINT")
        if w != expected_root_w:
            raise ValueError("DURABLE_GRAPH_JOURNAL_MISMATCH")
        if h != expected_root_h:
            raise ValueError("DURABLE_H_JOURNAL_MISMATCH")

    def view(self) -> StoreView:
        with self._read_snapshot():
            self._validate()
            row = self._metadata()
            assert (
                isinstance(row[6], bytes)
                and isinstance(row[7], bytes)
                and isinstance(row[8], bytes)
            )
            assert row[9] is None or isinstance(row[9], int)
            assert isinstance(row[10], int)
            assert isinstance(row[12], int)
            return StoreView(
                row[10],
                row[9],
                row[12],
                LanguageHomeostasis.decode(row[6]).overrides,
                row[7],
                row[8],
            )

    def graph(self) -> SparseNetwork:
        with self._read_snapshot():
            self._validate()
            value = self._metadata()[8]
            assert isinstance(value, bytes)
            return decode_production_graph(value)

    def h_bytes(self) -> bytes:
        with self._read_snapshot():
            self._validate()
            value = self._metadata()[6]
            assert isinstance(value, bytes)
            return value

    def root(self, exposure_id: int) -> RootView | None:
        self._id(exposure_id)
        row = self._connection.execute(
            "SELECT status,next_order,h_begin FROM p01_roots WHERE exposure_id=?", (exposure_id,)
        ).fetchone()
        return (
            None
            if row is None
            else RootView(exposure_id, row[0], row[1], LanguageHomeostasis.decode(row[2]).overrides)
        )

    def observation(self, exposure_id: int, order: int) -> ExternalEventObservation | None:
        self._id(exposure_id)
        if type(order) is not int or order < 0:
            raise ValueError("INVALID_EVENT_ORDER")
        with self._read_snapshot():
            self._validate()
            row = self._connection.execute(
                "SELECT record FROM p01_events WHERE exposure_id=? AND event_order=?",
                (exposure_id, order),
            ).fetchone()
            return None if row is None else decode_event(row[0])

    def pending_proposals(self, exposure_id: int) -> tuple[LinkProposal, ...]:
        """Read staged proposals; their values alone cannot publish evidence."""
        self._id(exposure_id)
        with self._read_snapshot():
            self._validate()
            root = self.root(exposure_id)
            if root is None or root.status != "OPEN":
                raise ValueError("EXPOSURE_NOT_OPEN")
            rows = self._connection.execute(
                "SELECT proposals FROM p01_events WHERE exposure_id=? ORDER BY event_order",
                (exposure_id,),
            ).fetchall()
            return tuple(proposal for row in rows for proposal in decode_proposals(row[0]))

    def begin(self, exposure_id: int, *, hook: Hook | None = None) -> RootView:
        self._id(exposure_id)
        with self._transaction():
            self._validate()
            row = self._metadata()
            if row[9] == exposure_id:
                result = self.root(exposure_id)
                assert result is not None
                return result
            if row[9] is not None:
                raise ValueError("EXPOSURE_ALREADY_OPEN")
            assert isinstance(row[10], int)
            if exposure_id <= row[10]:
                raise ValueError("ROOT_ID_REUSED")
            self._connection.execute(
                "INSERT INTO p01_roots VALUES (?,'OPEN',0,?,?,NULL,NULL,NULL,NULL,NULL)",
                (exposure_id, row[6], row[8]),
            )
            self._connection.execute(
                "UPDATE p01_metadata SET open_root=?,high_watermark=?,r_state=? WHERE id=1",
                (exposure_id, exposure_id, R_COLD),
            )
            if hook:
                hook("BEFORE_COMMIT")
        if hook:
            hook("AFTER_COMMIT")
        result = self.root(exposure_id)
        assert result is not None
        return result

    def abort(self, exposure_id: int, *, hook: Hook | None = None) -> RootView:
        self._id(exposure_id)
        with self._transaction():
            self._validate()
            root = self.root(exposure_id)
            if root is None:
                raise ValueError("UNKNOWN_EXPOSURE")
            if root.status == "ABORTED":
                return root
            if self._metadata()[9] != exposure_id:
                raise ValueError("EXPOSURE_NOT_OPEN")
            begin_h = self._connection.execute(
                "SELECT h_begin FROM p01_roots WHERE exposure_id=?", (exposure_id,)
            ).fetchone()[0]
            current_w = self._metadata()[8]
            assert isinstance(current_w, bytes) and isinstance(begin_h, bytes)
            self._connection.execute(
                "UPDATE p01_roots SET status='ABORTED',h_end=?,w_end=?,close_hash=? "
                "WHERE exposure_id=?",
                (begin_h, current_w, _checkpoint_digest(begin_h, current_w), exposure_id),
            )
            self._connection.execute(
                "UPDATE p01_metadata SET h_state=?,r_state=?,open_root=NULL WHERE id=1",
                (begin_h, R_COLD),
            )
            if hook:
                hook("BEFORE_COMMIT")
        if hook:
            hook("AFTER_COMMIT")
        result = self.root(exposure_id)
        assert result is not None
        return result

    def event(
        self,
        exposure_id: int,
        order: int,
        features: tuple[tuple[str, str], ...],
        *,
        salience: str = "1.000000",
        boundary: bool = False,
        hook: Hook | None = None,
    ) -> ExternalEventObservation:
        self._id(exposure_id)
        if type(order) is not int or order < 0:
            raise ValueError("INVALID_EVENT_ORDER")
        if type(features) is not tuple or type(boundary) is not bool:
            raise ValueError("INVALID_FEATURE_EVENT")
        with self._transaction():
            self._validate()
            row = self._metadata()
            root = self.root(exposure_id)
            if root is None or root.status != "OPEN" or row[9] != exposure_id:
                raise ValueError("EXPOSURE_NOT_OPEN")
            if order != root.next_order:
                raise ValueError("EVENT_ORDER_MISMATCH")
            before_h, runtime, before_w = row[6:9]
            assert (
                isinstance(before_h, bytes)
                and isinstance(runtime, bytes)
                and isinstance(before_w, bytes)
            )
            graph = decode_production_graph(before_w)
            snapshot = GraphSnapshot.capture(graph)
            profile = LanguageHomeostasis.decode(before_h)
            h = profile.materialize(snapshot.committed_ids)
            draft = preflight(snapshot, h, features, salience=salience)
            effective_boundary = boundary or order == 0
            previous = None if runtime == R_COLD or effective_boundary else decode_event(runtime)
            prior_activity = {} if previous is None else dict(previous.final)
            prior_frontier = frozenset() if previous is None else frozenset(previous.frontier)
            temporal = aggregate(temporal_drives(snapshot, prior_activity, prior_frontier, {}))
            passes = two_pass(snapshot, h, prior_activity, dict(draft.projection.X), temporal, {})
            direct = frozenset(i for i, _ in draft.previously_committed)
            frontiers = final_frontiers(passes.second.activity, h, direct)
            assert isinstance(row[11], int)
            event_id = row[11] + 1
            admission = ProductionAdmission(exposure_id, event_id, order, draft.projection.digest)
            frontier = {i: passes.second.activity[i] for i in frontiers.learning}
            assert isinstance(row[12], int)
            after_graph = _admit_sensory_cohort(
                graph,
                admission=admission,
                born=draft.accepted,
                frontier=frontier,
                completed_closes=row[12],
            )
            after_w = encode_production_graph(after_graph)
            after_h = preview_pre_event_adaptation(
                profile, snapshot, passes.second.activity
            ).encode()
            p = draft.projection
            payload: dict[str, object] = {
                "exposure": exposure_id,
                "event": event_id,
                "order": order,
                "digest": p.digest,
                "features": [[feature.hex(), value] for feature, value in p.input_features],
                "salience": p.salience_fixed,
                "x": [list(x) for x in p.X_fixed],
                "pre": sorted(snapshot.committed_ids),
                "pre_w": _sha(before_w),
                "pre_h": _sha(before_h),
                "previous": _numbers(prior_activity),
                "pass1_raw": _numbers(dict(passes.first.raw)),
                "pass1_normalized": _numbers(dict(passes.first.normalized)),
                "pass1": _numbers(dict(passes.first.activity)),
                "final_raw": _numbers(dict(passes.second.raw)),
                "final_normalized": _numbers(dict(passes.second.normalized)),
                "final": _numbers(dict(passes.second.activity)),
                "temporal": _numbers(temporal),
                "synchronous": _numbers(aggregate(passes.synchronous)),
                "emitters": sorted(passes.emitters),
                "learning_frontier": sorted(frontiers.learning),
                "frontier": sorted(frontiers.step),
                "born": sorted(i for i, _ in draft.accepted),
                "deferred": sorted(i for i, _ in draft.deferred),
                "boundary": effective_boundary,
                "origin": "EXTERNAL_DIRECT",
                "mode": "LEARN",
                "config": load_lab_config().sha256,
                "core": EXPECTED_SPECS[0][1],
                "lla": EXPECTED_SPECS[1][1],
                "latent": LATENT_POLICY_VERSION,
                "salt_hash": SALT_HASH,
                "h_profile": PROFILE_VERSION,
            }
            raw = encode_event(payload)
            observation = decode_event(raw, _verified_projection=p)
            staged = _derive_proposals(
                snapshot, observation, previous, h.thresholds[Region.LANGUAGE]
            )
            proposal_data = encode_proposals(staged)
            self._connection.execute(
                "INSERT INTO p01_events VALUES (?,?,?,?,?,?,?,?,?,?)",
                (
                    event_id,
                    exposure_id,
                    order,
                    raw,
                    before_w,
                    after_w,
                    before_h,
                    after_h,
                    proposal_data,
                    _checkpoint_digest(raw, before_w, after_w, before_h, after_h, proposal_data),
                ),
            )
            self._connection.execute(
                "UPDATE p01_roots SET next_order=? WHERE exposure_id=?", (order + 1, exposure_id)
            )
            self._connection.execute(
                "UPDATE p01_metadata SET h_state=?,r_state=?,w_state=?,event_high=? WHERE id=1",
                (after_h, raw, after_w, event_id),
            )
            if hook:
                hook("BEFORE_COMMIT")
        if hook:
            hook("AFTER_COMMIT")
        return observation

    def end(self, exposure_id: int, *, hook: Hook | None = None) -> CloseResult:
        """Publish one verified root's winning evidence in one SQLite transaction."""
        self._id(exposure_id)
        with self._transaction():
            self._validate()
            root = self.root(exposure_id)
            if root is None:
                raise ValueError("UNKNOWN_EXPOSURE")
            if root.status == "COMPLETED":
                stored = self._connection.execute(
                    "SELECT close_record FROM p01_roots WHERE exposure_id=?", (exposure_id,)
                ).fetchone()
                return decode_close(stored[0])
            row = self._metadata()
            if root.status != "OPEN" or row[9] != exposure_id:
                raise ValueError("EXPOSURE_NOT_OPEN")
            if root.next_order == 0:
                raise ValueError("EMPTY_EXTERNAL_EXPOSURE")
            before_w, h_end = row[8], row[6]
            assert isinstance(before_w, bytes) and isinstance(h_end, bytes)
            assert isinstance(row[12], int)
            serial = row[12] + 1
            completed_events = self._connection.execute(
                "SELECT COALESCE(SUM(next_order),0) FROM p01_roots WHERE status='COMPLETED'"
            ).fetchone()[0]
            assert isinstance(completed_events, int)
            event_clock = completed_events + root.next_order
            rows = self._connection.execute(
                "SELECT proposals FROM p01_events WHERE exposure_id=? ORDER BY event_order",
                (exposure_id,),
            ).fetchall()
            proposals = tuple(proposal for item in rows for proposal in decode_proposals(item[0]))
            after, result = _settle(
                decode_production_graph(before_w),
                exposure_id,
                serial,
                proposals,
                event_clock=event_clock,
            )
            w_end = encode_production_graph(after)
            close_record = encode_close(result)
            self._connection.execute(
                "UPDATE p01_roots SET status='COMPLETED',h_end=?,w_end=?,close_serial=?,"
                "close_record=?,close_hash=? WHERE exposure_id=?",
                (
                    h_end,
                    w_end,
                    serial,
                    close_record,
                    _checkpoint_digest(close_record, h_end, w_end),
                    exposure_id,
                ),
            )
            self._connection.execute(
                "UPDATE p01_metadata SET w_state=?,r_state=?,open_root=NULL,completed_closes=? "
                "WHERE id=1",
                (w_end, R_COLD, serial),
            )
            if hook:
                hook("BEFORE_COMMIT")
        if hook:
            hook("AFTER_COMMIT")
        return result

    def assert_read_only_allowed(self) -> None:
        if self.view().open_root is not None:
            raise ValueError("READ_ONLY_FORBIDDEN_WHILE_EXPOSURE_OPEN")

    def close(self) -> None:
        self._connection.close()
