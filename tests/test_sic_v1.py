import hashlib
import struct
from fractions import Fraction

import pytest

from dgca_next.contracts import Region
from dgca_next.peripheral.fingerprint import (
    Role,
    owner_profile_bytes,
    owner_profile_digest,
    role_bytes,
    role_digest,
)
from dgca_next.peripheral.sic import SICProjection, decimal_fixed, exact_or, project, receiver_ids


@pytest.mark.parametrize(
    "feature,local",
    [
        ("a", (1153, 3989, 414, 3603)),
        ("ab", (3449, 2321, 502, 2081)),
        ("é", (1138, 1220, 3626, 1003)),
        ("f617", (414, 8, 1843, 2734)),
    ],
)
def test_T01_published_salt_vectors(feature, local):
    assert receiver_ids(feature) == tuple(8192 + i for i in local)


@pytest.mark.parametrize("region", list(Region))
def test_T01_independent_payload(region):
    expected = []
    for k in range(4):
        salt = bytes(range(16 * k, 16 * (k + 1)))
        payload = b"DGCA-SIC-V1\0" + bytes((region.value, k)) + salt + struct.pack(">I", 2) + b"ab"
        expected.append(
            region.value * 4096 + int.from_bytes(hashlib.sha256(payload).digest()[:8], "big") % 4096
        )
    assert receiver_ids("ab", region) == tuple(expected)


def test_T02_nfc_and_unsigned_order():
    assert project((("é", "0.5"),)) == project((("e\u0301", "0.5"),))
    bundle = project((("é", "0.5"), ("a", "0.5"), ("e\u0301", "0.25")))
    assert bundle.features == ((b"a", 500000), ("é".encode(), 625000))
    assert project((("x" * 4096, "1"),)).X


@pytest.mark.parametrize("feature", ["", "x" * 4097, "é" * 2049, "\ud800", b"\xff", b"a", 1, None])
def test_T02_invalid_features(feature):
    with pytest.raises(ValueError):
        project(((feature, "1"),))


@pytest.mark.parametrize(
    "value",
    [
        "-0",
        "-0.000000",
        "+1",
        "1e0",
        "NaN",
        "Inf",
        "0.",
        ".5",
        "00",
        "1.000001",
        "0.0000001",
        "0.5\n",
        " 0.5",
        "0.٥",
        0.5,
        True,
        None,
    ],
)
def test_T03_strict_decimal_grammar(value):
    with pytest.raises(ValueError):
        decimal_fixed(value)


@pytest.mark.parametrize(
    "value,expected",
    [("0", 0), ("1", 1000000), ("0.1", 100000), ("1.00", 1000000), ("0.000001", 1)],
)
def test_T03_decimal_fixed(value, expected):
    assert decimal_fixed(value) == expected


def test_T03_half_even_each_stage():
    # Exact .000001 * .5 rounds to even zero, .000003 * .5 to even two.
    assert project((("a", "0.000001"),), salience="0.5").X_fixed == ()
    assert {v for _, v in project((("a", "0.000003"),), salience="0.5").X_fixed} == {2}
    for supports in ((1, 500000), (3, 500000), (123456, 654321, 222222)):
        complement = Fraction(1)
        for v in supports:
            complement *= 1 - Fraction(v, 1000000)
        assert exact_or(supports) == round((1 - complement) * 1000000)
    assert exact_or((1, 500000)) == 500000
    assert exact_or((3, 500000)) == 500002


def test_T04_duplicates_and_shared_receiver():
    assert dict(project((("a", "0.5"), ("f617", "0.25"))).X_fixed)[8606] == 625000
    repeated = project((("a", "0.5"), ("a", "0.25")))
    assert repeated.X_fixed == tuple((i, 625000) for i in (8606, 9345, 11795, 12181))
    assert project((("a", "0"),)).features == ()
    assert project((("a", "0.5"), ("a", "0.25"))) == project((("a", "0.25"), ("a", "0.5")))


def test_T04_one_feature_salt_collision_counted_once():
    # Fixed physical collision found by enumeration, not a probabilistic test.
    assert receiver_ids("collision4375") == (10751, 10953, 10953, 11601)
    assert project((("collision4375", "0.5"),)).X_fixed == (
        (10751, 500000),
        (10953, 500000),
        (11601, 500000),
    )


def test_T05_role_and_owner_vectors():
    items = project((("a", "0.5"),)).X_fixed
    assert (
        role_digest(Role.P, items)
        == "6cce77c3fc8da8bed4973ec695b267c3430807001563606989f40a3fe383b337"
    )
    records = [
        b"DGCA-ROLE-V1\0"
        + bytes((r,))
        + struct.pack(">I", 4)
        + b"".join(struct.pack(">II", i, u) for i, u in items)
        for r in range(3)
    ]
    expected = b"DGCA-OWNER-PROFILE-V1\0" + b"".join(struct.pack(">I", len(r)) + r for r in records)
    assert owner_profile_bytes(items, items, items) == expected
    assert owner_profile_digest(items, items, items) == hashlib.sha256(expected).hexdigest()
    assert role_bytes(Role.C, items) != role_bytes(Role.P, items)


@pytest.mark.parametrize(
    "items",
    [((2, 1), (1, 1)), ((1, 0),), ((1, 1), (1, 1)), ((12288, 1),), ((True, 1),), ((1, 1000001),)],
)
def test_T05_noncanonical_fingerprints_rejected(items):
    with pytest.raises(ValueError):
        role_bytes(Role.P, items)


def test_T07_projection_cannot_assert_arbitrary_X():
    with pytest.raises(ValueError, match="UNVERIFIED_SIC"):
        SICProjection(Region.LANGUAGE, ((b"a", 500000),), ((8192, 1000000),))
    with pytest.raises(ValueError):
        project((("a", "1"), ("b", "nan")))


def test_projection_rejects_boolean_and_float_numeric_aliases():
    good = project((("a", "0.000001"),))
    bad_fixed = tuple((float(i), True) for i, _ in good.X_fixed)
    with pytest.raises(ValueError, match="UNVERIFIED_SIC"):
        SICProjection(
            good.region, good.features, bad_fixed, good.input_features, good.salience_fixed
        )
    with pytest.raises(ValueError, match="UNVERIFIED_SIC"):
        SICProjection(
            good.region, ((b"a", True),), good.X_fixed, good.input_features, good.salience_fixed
        )


def test_sealed_bundle_identity_preserves_original_features_and_salience():
    first = project((("a", "1"),), salience="0.5")
    second = project((("a", "0.5"),))
    assert first.X_fixed == second.X_fixed
    assert first.digest != second.digest
    assert project((("a", "0"),)).digest != project(()).digest
    assert project((("a", "0.5"), ("a", "0.25"))).digest == project((("a", "0.625"),)).digest


def test_receiver_alias_diagnostic_is_feature_based_not_salt_based():
    assert project((("a", "0.5"), ("f617", "0.25"))).aliased_receivers == (8606,)
    assert project((("a", "0.5"), ("a", "0.25"))).aliased_receivers == ()
    assert project((("collision4375", "0.5"),)).aliased_receivers == ()
    assert project((("a", "0.5"), ("f617", "0"))).aliased_receivers == ()
