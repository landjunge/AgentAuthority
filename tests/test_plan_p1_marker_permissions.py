"""Actual filesystem checks of the reviewed PR26 marker; synthetic data only."""

import importlib.util
import os
import stat
from pathlib import Path
from types import SimpleNamespace

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "p1_controlled_run.py"


def load_observer(monkeypatch):
    spec = importlib.util.spec_from_file_location("reviewed_marker", SCRIPT)
    observer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(observer)
    monkeypatch.setattr(
        observer,
        "time",
        SimpleNamespace(
            monotonic_ns=lambda: 20,
            monotonic=lambda: 2.0,
            sleep=lambda _: None,
        ),
    )
    return observer


@pytest.mark.parametrize("mask", [0o000, 0o022, 0o077])
def test_new_marker_is_private_regular_empty_file(tmp_path, monkeypatch, mask):
    observer = load_observer(monkeypatch)
    events = [{"run": 7, "kind": "cli_end", "t_ns": 1}]
    previous = os.umask(mask)
    try:
        observer.watch_after(tmp_path, 7, events, True, 0.0)
    finally:
        os.umask(previous)
    marker = tmp_path / "post.observe"
    metadata = marker.lstat()
    assert stat.S_ISREG(metadata.st_mode)
    assert stat.S_IMODE(metadata.st_mode) == 0o600
    assert marker.read_bytes() == b""
    assert events[-1]["kind"] == "target_absent"
    assert events[-1]["value"] is False


def test_existing_marker_is_not_overwritten_or_repaired(tmp_path, monkeypatch):
    observer = load_observer(monkeypatch)
    marker = tmp_path / "post.observe"
    marker.write_bytes(b"SYNTHETIC-MARKER")
    marker.chmod(0o644)
    before = marker.lstat()
    observer.watch_after(tmp_path, 7, [{"run": 7, "kind": "cli_end", "t_ns": 1}], True, 0.0)
    after = marker.lstat()
    assert (after.st_dev, after.st_ino) == (before.st_dev, before.st_ino)
    assert marker.read_bytes() == b"SYNTHETIC-MARKER"
    assert stat.S_IMODE(after.st_mode) == 0o644


@pytest.mark.parametrize("guard", ["recording_not_valid", "target_present", "missing_cli_end"])
def test_invalid_precondition_creates_no_marker(tmp_path, monkeypatch, guard):
    observer = load_observer(monkeypatch)
    events = [] if guard == "missing_cli_end" else [{"run": 7, "kind": "cli_end", "t_ns": 1}]
    if guard == "target_present":
        (tmp_path / "target").write_bytes(b"SYNTHETIC-TARGET")
    observer.watch_after(tmp_path, 7, events, guard != "recording_not_valid", 0.0)
    assert not (tmp_path / "post.observe").exists()
