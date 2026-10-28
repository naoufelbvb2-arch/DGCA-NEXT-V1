"""Physical role/owner encodings from Core §3.1; no exposure identity."""

import hashlib
from enum import IntEnum

from dgca_next.contracts import CellAddress
from dgca_next.peripheral.sic import SCALE


class Role(IntEnum):
    P = 0
    C = 1
    Y = 2


def role_bytes(role: Role, items: tuple[tuple[int, int], ...]) -> bytes:
    if type(role) is not Role or type(items) is not tuple:
        raise ValueError("INVALID_ROLE_RECORD")
    payload = b"DGCA-ROLE-V1\0" + bytes((role,)) + len(items).to_bytes(4, "big")
    previous = -1
    for item in items:
        if type(item) is not tuple or len(item) != 2:
            raise ValueError("INVALID_ROLE_RECORD")
        cell_id, support = item
        CellAddress.from_cell_id(cell_id)
        if cell_id <= previous or type(support) is not int or not 0 < support <= SCALE:
            raise ValueError("NONCANONICAL_ROLE_RECORD")
        payload += cell_id.to_bytes(4, "big") + support.to_bytes(4, "big")
        previous = cell_id
    return payload


def role_digest(role: Role, items: tuple[tuple[int, int], ...]) -> str:
    return hashlib.sha256(role_bytes(role, items)).hexdigest()


def owner_profile_bytes(
    predecessor: tuple[tuple[int, int], ...],
    current: tuple[tuple[int, int], ...],
    outcome: tuple[tuple[int, int], ...],
) -> bytes:
    result = b"DGCA-OWNER-PROFILE-V1\0"
    for role, items in zip(Role, (predecessor, current, outcome), strict=True):
        record = role_bytes(role, items)
        result += len(record).to_bytes(4, "big") + record
    return result


def owner_profile_digest(
    predecessor: tuple[tuple[int, int], ...],
    current: tuple[tuple[int, int], ...],
    outcome: tuple[tuple[int, int], ...],
) -> str:
    return hashlib.sha256(owner_profile_bytes(predecessor, current, outcome)).hexdigest()
