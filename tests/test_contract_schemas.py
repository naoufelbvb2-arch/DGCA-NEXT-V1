from dataclasses import FrozenInstanceError, fields
from itertools import product

import pytest

from dgca_next.contracts import (
    CellAddress,
    EventMode,
    EventOrigin,
    EventProvenance,
    HSlow,
    R,
    ReadOnlyState,
    Region,
    StatePartition,
    SynapseKey,
    SynapseScope,
    W,
)


def test_entire_address_space_is_bijective():
    ids = set()
    for region, row, col, slot in product(Region, range(32), range(16), range(8)):
        address = CellAddress(region, row, col, slot)
        assert CellAddress.from_cell_id(address.cell_id) == address
        assert CellAddress.from_bytes(address.to_bytes()) == address
        ids.add(address.cell_id)
    assert ids == set(range(12288))


@pytest.mark.parametrize("field,limit", [("mc_row", 32), ("mc_col", 16), ("slot", 8)])
@pytest.mark.parametrize("bad", [-1, True, 0.0, "0", None])
def test_invalid_coordinate_types_and_lower_bounds(field, limit, bad):
    coordinates = {"mc_row": 0, "mc_col": 0, "slot": 0}
    coordinates[field] = bad
    with pytest.raises(ValueError):
        CellAddress(Region.LANGUAGE, **coordinates)


@pytest.mark.parametrize("row,col,slot", [(32, 0, 0), (0, 16, 0), (0, 0, 8)])
def test_address_upper_bounds(row, col, slot):
    with pytest.raises(ValueError):
        CellAddress(Region.LANGUAGE, row, col, slot)


@pytest.mark.parametrize("region", ["LANGUAGE", "language", 2, True, None])
def test_regions_are_not_coerced(region):
    with pytest.raises(ValueError):
        CellAddress(region, 0, 0, 0)


@pytest.mark.parametrize("cell_id", [-1, 12288, True, 1.0, "1", None])
def test_invalid_global_ids(cell_id):
    with pytest.raises(ValueError):
        CellAddress.from_cell_id(cell_id)


def test_serialized_address_fixture():
    address = CellAddress(Region.LANGUAGE, 3, 3, 6)
    assert address.cell_id == 8606  # Core §3.1's shared receiver example.
    assert address.to_bytes().hex() == "01010000000402030306"
    assert {field.name for field in fields(address)} == {"region", "mc_row", "mc_col", "slot"}
    with pytest.raises((AttributeError, TypeError)):
        address.word_id = "forbidden"


@pytest.mark.parametrize(
    "record",
    [
        b"",
        bytes.fromhex("02010000000402030306"),  # wrong tag
        bytes.fromhex("01020000000402030306"),  # unsupported version
        bytes.fromhex("01010000000502030306"),  # wrong length
        bytes.fromhex("01010000000403030306"),  # invalid region
        bytes.fromhex("01010000000402200306"),  # invalid row
        bytes.fromhex("0101000000040203030600"),  # trailing data
        bytearray.fromhex("01010000000402030306"),
    ],
)
def test_malformed_address_records(record):
    with pytest.raises(ValueError):
        CellAddress.from_bytes(record)


@pytest.mark.parametrize("scope", SynapseScope)
@pytest.mark.parametrize("same_region", [True, False])
def test_scope_region_matrix(scope, same_region):
    source = CellAddress(Region.LANGUAGE, 0, 0, 0)
    target = CellAddress(Region.LANGUAGE if same_region else Region.AUDIO, 0, 0, 1)
    valid = scope is SynapseScope.ASSOCIATIVE or (same_region == (scope is SynapseScope.LOCAL))
    if not valid:
        with pytest.raises(ValueError):
            SynapseKey(source, target, scope)
        return
    key = SynapseKey(source, target, scope)
    assert key != SynapseKey(target, source, scope)
    expected = 1 if scope is SynapseScope.ASSOCIATIVE else 0
    key.validate_delta(expected)
    for delta in (-1, 1 - expected, 2, 5, True, 0.0):
        with pytest.raises(ValueError):
            key.validate_delta(delta)


@pytest.mark.parametrize("scope", SynapseScope)
def test_self_links_forbidden(scope):
    cell = CellAddress(Region.LANGUAGE, 0, 0, 0)
    with pytest.raises(ValueError):
        SynapseKey(cell, cell, scope)


def test_scope_and_endpoint_types():
    a = CellAddress.from_cell_id(0)
    b = CellAddress.from_cell_id(1)
    with pytest.raises(ValueError):
        SynapseKey(a, b, "LOCAL")
    with pytest.raises(ValueError):
        SynapseKey(0, b, SynapseScope.LOCAL)
    assert [s.value for s in SynapseScope] == ["LOCAL", "CROSS_TERRITORY", "ASSOCIATIVE"]


@pytest.mark.parametrize("mode", EventMode)
@pytest.mark.parametrize("origin", EventOrigin)
def test_mode_origin_matrix(mode, origin):
    ids = (
        {"exposure_id": 1}
        if mode is EventMode.LEARN
        else {"replay_source_exposure_id": 1}
        if mode is EventMode.REPLAY
        else {"session_id": 1}
    )
    valid = (mode, origin) in {
        (EventMode.LEARN, EventOrigin.EXTERNAL_DIRECT),
        (EventMode.REPLAY, EventOrigin.REPLAY_RECALLED),
        (EventMode.RETRIEVE, EventOrigin.READ_ONLY_OBSERVED),
        (EventMode.GENERATE, EventOrigin.READ_ONLY_OBSERVED),
        (EventMode.GENERATE, EventOrigin.INTERNAL_SELECTED),
    }
    if valid:
        assert EventProvenance(mode, origin, 0, **ids).mode is mode
    else:
        with pytest.raises(ValueError):
            EventProvenance(mode, origin, 0, **ids)


@pytest.mark.parametrize("mode", ["LEARN", "learn", 0, True, None])
def test_invalid_modes_are_rejected(mode):
    with pytest.raises(ValueError):
        EventProvenance(mode, EventOrigin.EXTERNAL_DIRECT, 0, exposure_id=1)


@pytest.mark.parametrize("origin", ["EXTERNAL_DIRECT", "DIRECT_OBSERVED", 0, None])
def test_invalid_event_origins(origin):
    with pytest.raises(ValueError):
        EventProvenance(EventMode.LEARN, origin, 0, exposure_id=1)


@pytest.mark.parametrize("field", ["event_order", "exposure_id"])
@pytest.mark.parametrize("bad", [-1, True, 0.0, "1"])
def test_invalid_event_identifiers(field, bad):
    kwargs = {"event_order": 0, "exposure_id": 1}
    kwargs[field] = bad
    with pytest.raises(ValueError):
        EventProvenance(EventMode.LEARN, EventOrigin.EXTERNAL_DIRECT, **kwargs)


@pytest.mark.parametrize(
    "mode,origin,ids",
    [
        (EventMode.LEARN, EventOrigin.EXTERNAL_DIRECT, {}),
        (EventMode.LEARN, EventOrigin.EXTERNAL_DIRECT, {"exposure_id": 1, "session_id": 1}),
        (EventMode.REPLAY, EventOrigin.REPLAY_RECALLED, {}),
        (
            EventMode.REPLAY,
            EventOrigin.REPLAY_RECALLED,
            {"replay_source_exposure_id": 1, "exposure_id": 1},
        ),
        (EventMode.RETRIEVE, EventOrigin.READ_ONLY_OBSERVED, {}),
        (
            EventMode.RETRIEVE,
            EventOrigin.READ_ONLY_OBSERVED,
            {"session_id": 1, "exposure_id": 1},
        ),
        (
            EventMode.GENERATE,
            EventOrigin.INTERNAL_SELECTED,
            {"session_id": 1, "replay_source_exposure_id": 1},
        ),
    ],
)
def test_invalid_provenance_combinations(mode, origin, ids):
    with pytest.raises(ValueError):
        EventProvenance(mode, origin, 0, **ids)


def test_state_ownership_and_readonly_boundary():
    w, r, h = W(b"graph fixture"), R(b"ephemeral fixture"), HSlow(b"slow fixture")
    view = ReadOnlyState(w, h)
    assert [w.partition, r.partition, h.partition] == list(StatePartition)
    assert {f.name for f in fields(view)} == {"w", "h_slow"}
    for envelope in (w, r, h):
        with pytest.raises(FrozenInstanceError):
            envelope.snapshot = b"changed"
        with pytest.raises(TypeError):
            envelope.snapshot[0] = 0
    with pytest.raises(FrozenInstanceError):
        view.w = W(b"replacement")
    assert w.snapshot == b"graph fixture"
    assert r.snapshot == b"ephemeral fixture"
    assert h.snapshot == b"slow fixture"


@pytest.mark.parametrize("envelope", [W, R, HSlow])
@pytest.mark.parametrize("payload", [bytearray(b"mutable"), {}, [], "text", None])
def test_state_envelopes_reject_mutable_or_untyped_references(envelope, payload):
    with pytest.raises(ValueError):
        envelope(payload)


@pytest.mark.parametrize("w,h", [(R(b""), HSlow(b"")), (W(b""), W(b"")), ({}, HSlow(b""))])
def test_state_partitions_cannot_be_interchanged(w, h):
    with pytest.raises(ValueError):
        ReadOnlyState(w, h)
