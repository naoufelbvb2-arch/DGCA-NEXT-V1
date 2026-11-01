"""Actual native subjects only; inspection never updates a store."""

from pathlib import Path

import pytest

from dgca_next.persistence.reachability_inspection import inspect_reachability
from dgca_next.persistence.store import RootStore

ROOT = Path(__file__).resolve().parents[1]


def test_only_actual_live_ids_are_production_inputs_and_queries_do_not_write(tmp_path):
    path = tmp_path / "subjects.sqlite"
    store = RootStore(
        path,
        repository_root=ROOT,
        code_revision="a" * 40,
        execution_mode="I4_NATIVE_MAINTAIN_GROW_V1",
    )
    for root in range(1, 6):
        store.begin(root)
        for order in range(2 if 2 <= root <= 4 else 1):
            store.event(root, order, (("a", "1"),))
        store.end(root)
    before, h, data = store.view(), store.h_bytes(), path.read_bytes()
    result = inspect_reachability(store, split_id=0)
    assert result.source_kind == "PRODUCTION_ROOTSTORE_SNAPSHOT"
    assert result.identities[0].generation == 2
    assert not result.mutation_authorized
    for kwargs in (
        dict(merge_ids=(0, 1)),
        dict(merge_ids=(0, 0)),
        dict(merge_ids=(result.identities[0], result.identities[0])),
        dict(split_id=1),
        dict(split_id=True),
        dict(split_id=result.identities[0]),
    ):
        with pytest.raises(ValueError, match="ACTUAL_.*LIVE_ID"):
            inspect_reachability(store, **kwargs)
    assert store.view() == before and store.h_bytes() == h and path.read_bytes() == data
    assert inspect_reachability(store) == result
    store.close()


def test_legacy_store_cannot_be_used_to_supply_native_identity_authority(tmp_path):
    path = tmp_path / "schema4.sqlite"
    store = RootStore(path, repository_root=ROOT, code_revision="a" * 40)
    before = path.read_bytes()
    with pytest.raises(ValueError, match="NATIVE_ROOTSTORE_REQUIRED"):
        inspect_reachability(store)
    assert path.read_bytes() == before
    store.close()
