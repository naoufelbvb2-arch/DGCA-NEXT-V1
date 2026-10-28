"""I3-R01 SQLite root skeleton. EVENT/END explicitly fail closed.

This persists an explicit caller H image and root administration, but does not
mint external witnesses, commit sensory cells, or create learned graph records.
The code revision is a caller-declared identifier, not remote authentication.
"""

import re
import sqlite3
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path

from dgca_next.config import load_lab_config
from dgca_next.dynamics.numeric import SpecBlocked
from dgca_next.dynamics.state import Homeostasis
from dgca_next.graph import SparseNetwork
from dgca_next.graph.latent import LATENT_POLICY_VERSION
from dgca_next.integrity import EXPECTED_SPECS, verify_specs
from dgca_next.peripheral.sic import project
from dgca_next.persistence.codec import decode_homeostasis, encode_homeostasis

SCHEMA_VERSION = 1
R_COLD = b"\x52\x01\x00\x00\x00\x00"
EMPTY_W = b"\x57\x01\x00\x00\x00\x00"
Hook = Callable[[str], None]


@dataclass(frozen=True, slots=True)
class RootView:
    exposure_id: int
    status: str
    next_order: int
    H_begin: Homeostasis


@dataclass(frozen=True, slots=True)
class StoreView:
    high_watermark: int
    open_root: int | None
    completed_closes: int
    homeostasis: Homeostasis
    runtime: bytes
    W: bytes


class RootStore:
    """SQLite-backed exclusive root marker; only BEGIN and ABORT are enabled."""

    def __init__(
        self,
        path: Path,
        *,
        repository_root: Path,
        code_revision: str,
        initial_homeostasis: Homeostasis | None = None,
    ) -> None:
        if type(path) is not Path and not isinstance(path, Path):
            raise ValueError("INVALID_STORE_PATH")
        if type(code_revision) is not str or not re.fullmatch(r"[0-9a-f]{40}", code_revision):
            raise ValueError("INVALID_CODE_REVISION")
        verify_specs(repository_root)
        self._connection = sqlite3.connect(str(path), isolation_level=None)
        self._connection.execute("PRAGMA foreign_keys=ON")
        self._connection.execute("PRAGMA synchronous=FULL")
        self._code_revision = code_revision
        try:
            tables = {
                row[0]
                for row in self._connection.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
                )
            }
            if not tables:
                if initial_homeostasis is None:
                    raise ValueError("EXPLICIT_INITIAL_H_REQUIRED")
                self._initialize(initial_homeostasis)
            elif tables != {"metadata", "roots"}:
                raise ValueError("UNSUPPORTED_STORE_SCHEMA")
            self._validate_store()
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

    def _initialize(self, initial: Homeostasis) -> None:
        h_bytes = encode_homeostasis(initial)
        with self._transaction():
            self._connection.execute(
                "CREATE TABLE metadata (id INTEGER PRIMARY KEY CHECK(id=1), "
                "schema_version INTEGER NOT NULL, "
                "config_hash TEXT NOT NULL, core_hash TEXT NOT NULL, lla_hash TEXT NOT NULL, "
                "code_revision TEXT NOT NULL, latent_version TEXT NOT NULL, "
                "h_state BLOB NOT NULL, r_state BLOB NOT NULL, w_state BLOB NOT NULL, "
                "graph_hash TEXT NOT NULL, open_root INTEGER, high_watermark INTEGER NOT NULL, "
                "completed_closes INTEGER NOT NULL)"
            )
            self._connection.execute(
                "CREATE TABLE roots (exposure_id INTEGER PRIMARY KEY, status TEXT NOT NULL, "
                "next_order INTEGER NOT NULL, h_begin BLOB NOT NULL)"
            )
            self._connection.execute(
                "INSERT INTO metadata VALUES (1,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (
                    SCHEMA_VERSION,
                    load_lab_config().sha256,
                    EXPECTED_SPECS[0][1],
                    EXPECTED_SPECS[1][1],
                    self._code_revision,
                    LATENT_POLICY_VERSION,
                    h_bytes,
                    R_COLD,
                    EMPTY_W,
                    SparseNetwork().structural_hash,
                    None,
                    -1,
                    0,
                ),
            )

    def _metadata(self) -> tuple[object, ...]:
        row = self._connection.execute(
            "SELECT schema_version,config_hash,core_hash,lla_hash,code_revision,latent_version,"
            "h_state,r_state,w_state,graph_hash,open_root,high_watermark,completed_closes "
            "FROM metadata WHERE id=1"
        ).fetchone()
        if row is None or len(row) != 13:
            raise ValueError("CORRUPT_STORE_METADATA")
        return tuple(row)

    def _validate_store(self) -> None:
        row = self._metadata()
        expected = (
            SCHEMA_VERSION,
            load_lab_config().sha256,
            EXPECTED_SPECS[0][1],
            EXPECTED_SPECS[1][1],
            self._code_revision,
            LATENT_POLICY_VERSION,
        )
        if row[:6] != expected:
            raise ValueError("STORE_IDENTITY_MISMATCH")
        if type(row[6]) is not bytes:
            raise ValueError("MALFORMED_H_RECORD")
        decode_homeostasis(row[6])
        if row[7] != R_COLD or row[8] != EMPTY_W or row[9] != SparseNetwork().structural_hash:
            raise ValueError("UNSUPPORTED_W_OR_R_CHECKPOINT")
        roots = self._connection.execute(
            "SELECT exposure_id,status,next_order,h_begin FROM roots ORDER BY exposure_id"
        ).fetchall()
        if type(row[11]) is not int or row[11] != (roots[-1][0] if roots else -1):
            raise ValueError("INVALID_ROOT_HIGH_WATERMARK")
        if row[12] != 0:
            raise ValueError("UNSUPPORTED_COMPLETED_ROOT")
        opened = []
        for root_id, status, order, h_begin in roots:
            if (
                type(root_id) is not int
                or root_id < 0
                or status not in ("OPEN", "ABORTED")
                or order != 0
            ):
                raise ValueError("INVALID_ROOT_JOURNAL")
            decode_homeostasis(h_begin)
            if status == "OPEN":
                opened.append(root_id)
        if len(opened) > 1 or row[10] != (opened[0] if opened else None):
            raise ValueError("INVALID_OPEN_ROOT_JOURNAL")

    @staticmethod
    def _id(exposure_id: int) -> None:
        if type(exposure_id) is not int or not 0 <= exposure_id <= 2**63 - 1:
            raise ValueError("INVALID_EXPOSURE_ID")

    def view(self) -> StoreView:
        self._validate_store()
        row = self._metadata()
        assert isinstance(row[6], bytes) and isinstance(row[7], bytes) and isinstance(row[8], bytes)
        assert isinstance(row[11], int) and isinstance(row[12], int)
        assert row[10] is None or isinstance(row[10], int)
        return StoreView(row[11], row[10], row[12], decode_homeostasis(row[6]), row[7], row[8])

    def root(self, exposure_id: int) -> RootView | None:
        self._id(exposure_id)
        row = self._connection.execute(
            "SELECT status,next_order,h_begin FROM roots WHERE exposure_id=?", (exposure_id,)
        ).fetchone()
        return (
            None
            if row is None
            else RootView(exposure_id, row[0], row[1], decode_homeostasis(row[2]))
        )

    def begin(self, exposure_id: int, *, hook: Hook | None = None) -> RootView:
        self._id(exposure_id)
        with self._transaction():
            self._validate_store()
            row = self._metadata()
            current, high = row[10], row[11]
            assert isinstance(high, int)
            if current == exposure_id:
                existing = self.root(exposure_id)
                assert existing is not None
                return existing
            if current is not None:
                raise ValueError("EXPOSURE_ALREADY_OPEN")
            if exposure_id <= high:
                raise ValueError("ROOT_ID_REUSED")
            self._connection.execute(
                "INSERT INTO roots VALUES (?,'OPEN',0,?)", (exposure_id, row[6])
            )
            self._connection.execute(
                "UPDATE metadata SET open_root=?,high_watermark=?,r_state=? WHERE id=1",
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
            self._validate_store()
            root = self.root(exposure_id)
            if root is None:
                raise ValueError("UNKNOWN_EXPOSURE")
            if root.status == "ABORTED":
                return root
            if self._metadata()[10] != exposure_id:
                raise ValueError("EXPOSURE_NOT_OPEN")
            self._connection.execute(
                "UPDATE roots SET status='ABORTED' WHERE exposure_id=?", (exposure_id,)
            )
            self._connection.execute(
                "UPDATE metadata SET h_state=?,r_state=?,open_root=NULL WHERE id=1",
                (encode_homeostasis(root.H_begin), R_COLD),
            )
            if hook:
                hook("BEFORE_COMMIT")
        if hook:
            hook("AFTER_COMMIT")
        result = self.root(exposure_id)
        assert result is not None
        return result

    def event(self, exposure_id: int, order: int, features: tuple[tuple[str, str], ...]) -> None:
        """Validate ingress but never publish an EVENT until R02 is complete."""
        self._id(exposure_id)
        if type(order) is not int or order < 0:
            raise ValueError("INVALID_EVENT_ORDER")
        state = self.view()
        root = self.root(exposure_id)
        if root is None or root.status != "OPEN" or state.open_root != exposure_id:
            raise ValueError("EXPOSURE_NOT_OPEN")
        if order != root.next_order:
            raise ValueError("EVENT_ORDER_MISMATCH")
        if type(features) is not tuple:
            raise ValueError("INVALID_FEATURE_EVENT")
        observation = project(features)
        if len(observation.X_fixed) > int(load_lab_config().parameter("K_R").value):
            raise SpecBlocked("I3-S01: sensory cohort selection is undefined above K_R")
        if observation.X_fixed:
            raise SpecBlocked("I3-S02: cold/newborn homeostatic initialization is unspecified")
        raise SpecBlocked("I3-R02: EVENT production graph authority is not implemented")

    def end(self, exposure_id: int) -> None:
        self._id(exposure_id)
        state = self.view()
        if state.open_root != exposure_id:
            raise ValueError("EXPOSURE_NOT_OPEN")
        raise SpecBlocked("I3-R03: END evidence publication is not implemented")

    def assert_read_only_allowed(self) -> None:
        if self.view().open_root is not None:
            raise ValueError("READ_ONLY_FORBIDDEN_WHILE_EXPOSURE_OPEN")

    def close(self) -> None:
        self._connection.close()
