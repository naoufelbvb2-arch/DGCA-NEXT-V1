"""Byte-exact SIC-V1 (Core §3.1). Integer/Fraction arithmetic until X conversion."""

import hashlib
import re
import unicodedata
from collections.abc import Iterable
from dataclasses import dataclass
from fractions import Fraction

from dgca_next.config import load_lab_config
from dgca_next.contracts import Region

SCALE = 1_000_000
_GRAMMAR = re.compile(r"(?:0|1|0\.[0-9]{1,6}|1\.0{1,6})", re.ASCII)
_CONFIG = load_lab_config()
_SALTS = tuple(bytes.fromhex(str(_CONFIG.parameter(f"sic_salt_{k}").value)) for k in range(4))


def decimal_fixed(value: str) -> int:
    if type(value) is not str or _GRAMMAR.fullmatch(value) is None:
        raise ValueError("INVALID_DECIMAL_SUPPORT")
    whole, _, fraction = value.partition(".")
    return int(whole) * SCALE + int(fraction.ljust(6, "0"))


def feature_bytes(value: str) -> bytes:
    if type(value) is not str:
        raise ValueError("INVALID_FEATURE_ENCODING")
    try:
        result = unicodedata.normalize("NFC", value).encode("utf-8", errors="strict")
    except UnicodeError as error:
        raise ValueError("INVALID_FEATURE_ENCODING") from error
    if not 1 <= len(result) <= 4096:
        raise ValueError("INVALID_FEATURE_LENGTH")
    return result


def receiver_ids(feature: str, region: Region = Region.LANGUAGE) -> tuple[int, ...]:
    return _receiver_bytes(feature_bytes(feature), region)


def _receiver_bytes(feature: bytes, region: Region) -> tuple[int, ...]:
    if type(region) is not Region:
        raise ValueError("INVALID_SIC_REGION")
    return tuple(
        4096 * region.value
        + int.from_bytes(
            hashlib.sha256(
                b"DGCA-SIC-V1\0"
                + bytes((region.value, k))
                + salt
                + len(feature).to_bytes(4, "big")
                + feature
            ).digest()[:8],
            "big",
        )
        % 4096
        for k, salt in enumerate(_SALTS)
    )


def exact_or(values: Iterable[int]) -> int:
    complement = Fraction(1)
    for value in values:
        if type(value) is not int or not 0 <= value <= SCALE:
            raise ValueError("INVALID_FIXED_SUPPORT")
        complement *= Fraction(SCALE - value, SCALE)
    return round((1 - complement) * SCALE)


def _receivers(
    features: tuple[tuple[bytes, int], ...], region: Region
) -> tuple[tuple[int, int], ...]:
    supports: dict[int, list[int]] = {}
    for feature, support in features:
        if support:
            for cell_id in sorted(set(_receiver_bytes(feature, region))):
                supports.setdefault(cell_id, []).append(support)
    return tuple((cell_id, exact_or(values)) for cell_id, values in sorted(supports.items()))


@dataclass(frozen=True, slots=True)
class SICProjection:
    """Canonical effective features and exact direct supports, never a witness root."""

    region: Region
    features: tuple[tuple[bytes, int], ...]
    X_fixed: tuple[tuple[int, int], ...]
    input_features: tuple[tuple[bytes, int], ...] = ()
    salience_fixed: int = SCALE

    def __post_init__(self) -> None:
        if (
            type(self.region) is not Region
            or type(self.features) is not tuple
            or type(self.input_features) is not tuple
            or type(self.salience_fixed) is not int
            or not 0 <= self.salience_fixed <= SCALE
        ):
            raise ValueError("INVALID_PROJECTION")
        previous = b""
        for item in self.input_features:
            if type(item) is not tuple or len(item) != 2:
                raise ValueError("INVALID_PROJECTION")
            feature, support = item
            if type(feature) is not bytes or feature <= previous:
                raise ValueError("NONCANONICAL_FEATURES")
            try:
                if feature_bytes(feature.decode("utf-8", "strict")) != feature:
                    raise ValueError("NONCANONICAL_FEATURES")
            except UnicodeError as error:
                raise ValueError("INVALID_FEATURE_ENCODING") from error
            if type(support) is not int or not 0 <= support <= SCALE:
                raise ValueError("INVALID_FIXED_SUPPORT")
            previous = feature
        expected_features = tuple(
            (feature, effective)
            for feature, original in self.input_features
            if (effective := round(Fraction(original * self.salience_fixed, SCALE))) > 0
        )
        if (
            any(
                type(item) is not tuple
                or len(item) != 2
                or type(item[0]) is not bytes
                or type(item[1]) is not int
                for item in self.features
            )
            or self.features != expected_features
        ):
            raise ValueError("UNVERIFIED_SIC_PROJECTION")
        if (
            type(self.X_fixed) is not tuple
            or any(
                type(item) is not tuple
                or len(item) != 2
                or type(item[0]) is not int
                or type(item[1]) is not int
                for item in self.X_fixed
            )
            or self.X_fixed != _receivers(self.features, self.region)
        ):
            raise ValueError("UNVERIFIED_SIC_PROJECTION")

    @property
    def X(self) -> tuple[tuple[int, float], ...]:
        return tuple((cell_id, support / SCALE) for cell_id, support in self.X_fixed)

    @property
    def digest(self) -> str:
        """Diagnostic schema 2: canonical original supports and separate salience."""
        payload = b"DGCA-I2-SIC-BUNDLE-V2\0" + bytes((self.region.value,))
        payload += self.salience_fixed.to_bytes(4, "big")
        payload += len(self.input_features).to_bytes(4, "big")
        for feature, support in self.input_features:
            payload += len(feature).to_bytes(4, "big") + feature + support.to_bytes(4, "big")
        return hashlib.sha256(payload).hexdigest()

    @property
    def aliased_receivers(self) -> tuple[int, ...]:
        """IDs receiving more than one distinct positive effective feature."""
        counts: dict[int, int] = {}
        for feature, _ in self.features:
            for cell_id in set(_receiver_bytes(feature, self.region)):
                counts[cell_id] = counts.get(cell_id, 0) + 1
        return tuple(sorted(i for i, count in counts.items() if count > 1))


def project(
    features: Iterable[tuple[str, str]],
    *,
    region: Region = Region.LANGUAGE,
    salience: str = "1.000000",
) -> SICProjection:
    sal = decimal_fixed(salience)
    if type(region) is not Region:
        raise ValueError("INVALID_SIC_REGION")
    grouped: dict[bytes, list[int]] = {}
    for item in features:
        if type(item) is not tuple or len(item) != 2:
            raise ValueError("INVALID_FEATURE_PAIR")
        text, support = item
        grouped.setdefault(feature_bytes(text), []).append(decimal_fixed(support))
    original = tuple((feature, exact_or(supports)) for feature, supports in sorted(grouped.items()))
    effective = tuple(
        (feature, merged)
        for feature, initial in original
        if (merged := round(Fraction(initial * sal, SCALE))) > 0
    )
    return SICProjection(region, effective, _receivers(effective, region), original, sal)
