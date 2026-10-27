"""Verify raw bytes against pinned manifest values. No newline normalization."""

import hashlib
import re
from pathlib import Path
from typing import Final

EXPECTED_SPECS: Final = (
    (
        "docs/specs/DGCA_CORE_RC4_1.md",
        "f9d57129b773a93cf8603cdf2df0f6530364200ddea7ce7a070101491800a92d",
        "6c4b163b2c7fa519da462c17f8a9002dc979ebc9",
    ),
    (
        "docs/specs/DGCA_LLA_RC4_1.md",
        "67d98d3e34aa0edeac2c77b955c0a0e489d3b6aac89f86959a8b626c4b4d2b69",
        "c43cb5944e537fc5894560790f1095b9b9e1c825",
    ),
)


class SpecIntegrityError(ValueError):
    """Missing, malformed, or altered scientific source/manifest."""


def verify_specs(repository_root: Path) -> tuple[str, ...]:
    """Verify both manifest rows and both files; return SHA-256 result lines."""
    try:
        manifest = (repository_root / "docs/specs/SOURCE-MANIFEST.md").read_text("utf-8")
        rows = re.findall(
            r"^\| `([^`]+)` \| `([0-9a-f]{64})` \| `([0-9a-f]{40})` \|$",
            manifest,
            re.MULTILINE,
        )
        if sorted(rows) != sorted(EXPECTED_SPECS):
            raise SpecIntegrityError("source manifest does not match the pinned I0 sources")
        results = []
        for path, expected, blob_sha in EXPECTED_SPECS:
            data = (repository_root / path).read_bytes()
            digest = hashlib.sha256(data).hexdigest()
            blob = b"blob " + str(len(data)).encode("ascii") + b"\0" + data
            if digest != expected or hashlib.sha1(blob).hexdigest() != blob_sha:
                raise SpecIntegrityError(f"specification bytes changed: {path}; SHA-256={digest}")
            results.append(f"PASS {path} SHA-256={digest}")
        return tuple(results)
    except (OSError, UnicodeError) as exc:
        raise SpecIntegrityError(str(exc)) from exc
