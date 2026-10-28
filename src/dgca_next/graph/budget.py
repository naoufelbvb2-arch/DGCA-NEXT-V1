"""Structural unique-key capacity; no proposal ranking or eviction policy."""

from collections.abc import Iterable
from dataclasses import dataclass

from dgca_next.config import load_lab_config
from dgca_next.contracts import SynapseKey

_CONFIG = load_lab_config()


@dataclass(frozen=True, slots=True)
class OutgoingUsage:
    total: int
    cross: int
    episodic: int


def outgoing_usage(
    keys: Iterable[SynapseKey], episodic_keys: Iterable[SynapseKey]
) -> OutgoingUsage:
    """Cross outgoing means distinct endpoint regions, including ASSOCIATIVE."""
    distinct = frozenset(keys)
    return OutgoingUsage(
        len(distinct),
        sum(key.source.region is not key.target.region for key in distinct),
        len(frozenset(episodic_keys)),
    )


def validate_usage(usage: OutgoingUsage) -> None:
    if usage.total > int(_CONFIG.parameter("B_i").value):
        raise ValueError("SOURCE_OUTGOING_CAPACITY")
    if usage.cross > int(_CONFIG.parameter("B_i_cross").value):
        raise ValueError("CROSS_OUTGOING_CAPACITY")
    if usage.episodic > int(_CONFIG.parameter("E_cap").value):
        raise ValueError("EPISODIC_OUTGOING_CAPACITY")
