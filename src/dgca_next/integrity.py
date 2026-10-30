"""Verify raw bytes against pinned manifest values. No newline normalization."""

import hashlib
import re
from pathlib import Path
from typing import Final

HISTORICAL_I0_COMMIT: Final = "fdcd3ea3c85b9c7484e89d043188a59d49907b71"
RC4_2_MIGRATION_PARENT: Final = "673451ca905911931c60e3bece47e37e0e3d1e7a"
RC4_3_MIGRATION_PARENT: Final = "ba36cab417574c7ee416e358f448bec54d0006f2"
RC4_4_MIGRATION_PARENT: Final = "c0c860a1a00b24c5e796a512c5b77beb022a079a"
ARCHIVAL_RC43_SPECS: Final = (
    (
        "docs/specs/DGCA_CORE_RC4_3.md",
        "41764eea3ddccdbd692325ecf7f03c243bf259bb46cc2b1820f7648125f3a53a",
        "37a226f5d81b3c72685015ae7125f9d5d24af9f4",
    ),
    (
        "docs/specs/DGCA_LLA_RC4_3.md",
        "4c70fd84a8356e7871e6ac5bd14eeb800bf2347342512c4901e1e2191a89e958",
        "4fbaef7f3922d41604bd649b1217fe2741d58b3e",
    ),
)
ARCHIVAL_SPECS: Final = (
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

ARCHIVAL_RC42_SPECS: Final = (
    (
        "docs/specs/DGCA_CORE_RC4_2.md",
        "570570a2a57c3b859ed3745c8812711cf36de89a47be50bdbf5f415a1b8dbc59",
        "5422a212abe21773a48c82b7f2ceaa34a9cd0a63",
    ),
    (
        "docs/specs/DGCA_LLA_RC4_2.md",
        "47ad994cbda467ae1ce0ffd6c2868522f5502897f6c4d2d1f3ab68b69ac1df30",
        "889025d76d70167de3070ffd8945878d37bf3dde",
    ),
)

# Updated together with both RC4.4 scientific sources.
EXPECTED_SPECS: Final = (
    (
        "docs/specs/DGCA_CORE_RC4_4.md",
        "3829494e85b85c1421379324a1702013bed3c970e353ad3b71c08da1901eb93c",
        "1207be632b6f8aa5839a30c0570ce844724faf0f",
    ),
    (
        "docs/specs/DGCA_LLA_RC4_4.md",
        "ba38b7916add57090f088460adb0baa351111cc1757c4a062c89a9d35ca6f2e0",
        "7c81d4dd6ea98650856cb87cf02ddce3bce5048d",
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
            raise SpecIntegrityError(
                "source manifest does not match the pinned current RC4.4 sources"
            )
        if (
            HISTORICAL_I0_COMMIT not in manifest
            or RC4_2_MIGRATION_PARENT not in manifest
            or RC4_3_MIGRATION_PARENT not in manifest
            or RC4_4_MIGRATION_PARENT not in manifest
            or any(
                sha not in manifest or blob not in manifest
                for _, sha, blob in (*ARCHIVAL_SPECS, *ARCHIVAL_RC42_SPECS, *ARCHIVAL_RC43_SPECS)
            )
        ):
            raise SpecIntegrityError("source manifest archival provenance changed")
        current = sorted(
            p.relative_to(repository_root).as_posix()
            for p in (repository_root / "docs/specs").glob("DGCA_*_RC*.md")
        )
        if current != sorted(path for path, _, _ in EXPECTED_SPECS):
            raise SpecIntegrityError("expected exactly two current scientific artifacts")
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
