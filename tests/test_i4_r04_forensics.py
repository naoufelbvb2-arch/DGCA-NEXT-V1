"""Real protected-parent compatibility and crash-safe completed-event time."""

import io
import os
import subprocess
import sys
import tarfile

import pytest
from test_i4_r04_autonomous import MODE, ROOT, root, store_at

from dgca_next.learning.completed_event_clock import _verified_completed_prefix
from dgca_next.learning.native_multi import decode_multi_close
from dgca_next.persistence.store import RootStore


@pytest.mark.parametrize("experimental", [False, True])
def test_actual_protected_source_history_loads_without_rewriting(tmp_path, experimental):
    parent = (
        "5fca02cdaabf882837556b704c4e9f391a6ea711"
        if experimental
        else "1af7dab4e82be826380d787e16cfecd8a2224f0f"
    )
    source = tmp_path / "protected-source"
    source.mkdir()
    archive = subprocess.check_output(
        ["git", "archive", "--format=tar", parent, "src", "docs/specs"], cwd=ROOT
    )
    with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
        tar.extractall(source, filter="data")
    path = tmp_path / "protected.sqlite"
    script = """
import sys
from pathlib import Path
from dgca_next.persistence.store import RootStore
s=RootStore(Path(sys.argv[1]),repository_root=Path.cwd(),code_revision=sys.argv[2],execution_mode=sys.argv[3])
features=(("a","1"),("f617","1")) if sys.argv[3]=='I4_NATIVE_MULTI_V1' else (("a","1"),)
for r in range(1,6):
    s.begin(r)
    for o in range(2 if 2<=r<=4 else 1): s.event(r,o,features)
    s.end(r)
s.close()
"""
    subprocess.check_call(
        [
            sys.executable,
            "-c",
            script,
            str(path),
            parent,
            MODE if experimental else "I4_NATIVE_MAINTAIN_GROW_V1",
        ],
        cwd=source,
        env=os.environ | {"PYTHONPATH": str(source / "src")},
    )
    data = path.read_bytes()
    s = RootStore(path, repository_root=ROOT, code_revision=parent, execution_mode=MODE)
    assert path.read_bytes() == data
    assert s.graph().native_assemblies()[0].structural_generation == (5 if experimental else 2)
    if experimental:
        assert s.end(1).close_version == 1
        assert s.end(1).form_reason == "NO_QUALIFIED_FORM_EVENT"
    assert root(s, 6, (), 1).close_version == 2
    s.close()
    s = RootStore(path, repository_root=ROOT, code_revision=parent, execution_mode=MODE)
    assert s.view().completed_closes == 6
    s.close()


@pytest.mark.parametrize("stage", ["BEFORE_COMMIT", "AFTER_COMMIT"])
def test_completed_event_clock_survives_real_end_process_crash(tmp_path, stage):
    path = tmp_path / "clock-crash.sqlite"
    s = store_at(path)
    root(s, 1, (), 1)
    s.begin(2)
    for order in range(5):
        s.event(2, order, ())
    before = s.view()
    s.close()
    script = """
import os,sys
from pathlib import Path
from dgca_next.persistence.store import RootStore
s=RootStore(Path(sys.argv[1]),repository_root=Path.cwd(),code_revision='a'*40,execution_mode='I4_NATIVE_MULTI_V1')
def stop(stage):
    if stage==sys.argv[2]: os._exit(47)
s.end(2,hook=stop)
"""
    p = subprocess.run([sys.executable, "-c", script, str(path), stage], cwd=ROOT)
    assert p.returncode == 47
    s = store_at(path)
    if stage == "BEFORE_COMMIT":
        assert s.view() == before and s.view().completed_closes == 1
    else:
        assert s.root(2).status == "COMPLETED"
    close = s.end(2)
    prefix = _verified_completed_prefix(
        s._backend._connection, close, decode_multi_close, replay=True
    )
    assert close.event_clock == 6 and prefix.cooldown(0, 1).age_completed_events == 5
    assert s.end(2) == close
    s.close()
