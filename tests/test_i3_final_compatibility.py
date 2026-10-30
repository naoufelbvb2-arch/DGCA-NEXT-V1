"""Legacy production schema remains explicitly unsupported, never reinterpreted."""

import sqlite3
from contextlib import closing
from pathlib import Path

import pytest

from dgca_next.persistence.store import RootStore

ROOT = Path(__file__).resolve().parents[1]


def test_schema3_journal_is_rejected_without_modification(tmp_path):
    path = tmp_path / "schema3.sqlite"
    store = RootStore(path, repository_root=ROOT, code_revision="a" * 40)
    store.begin(1)
    store.event(1, 0, (("a", "1"),))
    store.end(1)
    store.close()
    with closing(sqlite3.connect(path)) as connection:
        with connection:
            connection.execute("DROP TABLE p04_requests")
            connection.execute("UPDATE p01_metadata SET schema_version=3")
    before = path.read_bytes()
    with pytest.raises(ValueError, match="UNSUPPORTED_PRODUCTION_SCHEMA"):
        RootStore(path, repository_root=ROOT, code_revision="a" * 40)
    assert path.read_bytes() == before
