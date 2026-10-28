"""Mechanical peripheral input; no tokenizer or semantic interpretation."""

from dgca_next.peripheral.fingerprint import Role, owner_profile_bytes, role_bytes, role_digest
from dgca_next.peripheral.sic import SICProjection, project, receiver_ids

__all__ = [
    "Role",
    "SICProjection",
    "owner_profile_bytes",
    "project",
    "receiver_ids",
    "role_bytes",
    "role_digest",
]
