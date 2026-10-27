import hashlib
import shutil
import subprocess
from pathlib import Path

import pytest

from dgca_next.__main__ import main
from dgca_next.integrity import (
    ARCHIVAL_SPECS,
    EXPECTED_SPECS,
    HISTORICAL_I0_COMMIT,
    SpecIntegrityError,
    verify_specs,
)

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def source_copy(tmp_path):
    shutil.copytree(ROOT / "docs/specs", tmp_path / "docs/specs")
    return tmp_path


def test_spec_and_manifest_integrity():
    assert len(verify_specs(ROOT)) == 2


@pytest.mark.parametrize("path,digest,blob_sha", ARCHIVAL_SPECS)
def test_default_branch_contains_identical_sources(path, digest, blob_sha):
    # Immutable accepted I0 commit, not a movable main path after a later merge.
    data = subprocess.check_output(["git", "show", f"{HISTORICAL_I0_COMMIT}:{path}"], cwd=ROOT)
    assert hashlib.sha256(data).hexdigest() == digest
    assert hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest() == blob_sha


def test_exactly_two_current_scientific_artifacts():
    assert sorted(p.name for p in (ROOT / "docs/specs").glob("DGCA_*_RC*.md")) == [
        "DGCA_CORE_RC4_2.md",
        "DGCA_LLA_RC4_2.md",
    ]


@pytest.mark.parametrize("path,digest,blob_sha", EXPECTED_SPECS)
def test_specs_match_committed_source_bytes(path, digest, blob_sha):
    data = (ROOT / path).read_bytes()
    assert hashlib.sha256(data).hexdigest() == digest
    assert hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest() == blob_sha


@pytest.mark.parametrize("path,digest,blob_sha", EXPECTED_SPECS)
@pytest.mark.parametrize("damage", ["edit", "crlf", "missing"])
def test_changed_scientific_bytes_fail(source_copy, path, digest, blob_sha, damage):
    target = source_copy / path
    if damage == "missing":
        target.unlink()
    elif damage == "crlf":
        target.write_bytes(target.read_bytes().replace(b"\n", b"\r\n"))
    else:
        target.write_bytes(target.read_bytes() + b"unapproved scientific change\n")
    with pytest.raises(SpecIntegrityError):
        verify_specs(source_copy)


@pytest.mark.parametrize("damage", ["hash", "duplicate", "missing", "invalid_utf8"])
def test_manifest_tampering_fails(source_copy, damage):
    target = source_copy / "docs/specs/SOURCE-MANIFEST.md"
    content = target.read_bytes()
    if damage == "hash":
        target.write_bytes(content.replace(EXPECTED_SPECS[0][1].encode(), b"0" * 64))
    elif damage == "duplicate":
        row = next(line for line in content.splitlines() if EXPECTED_SPECS[0][1].encode() in line)
        target.write_bytes(content + b"\n" + row + b"\n")
    elif damage == "invalid_utf8":
        target.write_bytes(b"\xff")
    else:
        target.unlink()
    with pytest.raises(SpecIntegrityError):
        verify_specs(source_copy)


def test_integrity_cli_success(capsys):
    assert main(["verify-specs", "--repo-root", str(ROOT)]) == 0
    output = capsys.readouterr()
    assert output.out.count("PASS docs/specs/") == 2
    assert output.err == ""


def test_integrity_cli_failure(tmp_path, capsys):
    assert main(["verify-specs", "--repo-root", str(tmp_path)]) == 1
    output = capsys.readouterr()
    assert output.out == ""
    assert output.err.startswith("FAIL ")


@pytest.mark.parametrize("command", ["learn", "generate", "retrieve"])
def test_no_engine_cli(command):
    with pytest.raises(SystemExit) as exc:
        main([command])
    assert exc.value.code == 2
