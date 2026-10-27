import importlib.metadata
import subprocess
import sys
import tomllib
from pathlib import Path

from dgca_next import __version__

ROOT = Path(__file__).resolve().parents[1]


def test_installed_version_matches_source_and_metadata():
    project = tomllib.loads((ROOT / "pyproject.toml").read_text("utf-8"))["project"]
    assert __version__ == project["version"] == importlib.metadata.version("dgca-next")
    assert project["dependencies"] == []


def test_import_from_outside_repository(tmp_path):
    result = subprocess.run(
        [sys.executable, "-I", "-c", "import dgca_next; print(dgca_next.__version__)"],
        cwd=tmp_path,
        text=True,
        capture_output=True,
        check=True,
    )
    assert result.stdout == f"{__version__}\n"
    assert result.stderr == ""


def test_module_version():
    result = subprocess.run(
        [sys.executable, "-m", "dgca_next", "--version"],
        text=True,
        capture_output=True,
        check=True,
    )
    assert result.stdout == f"dgca-next {__version__}\n"
    assert result.stderr == ""
