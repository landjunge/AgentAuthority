from __future__ import annotations

import os
import subprocess
import sys

import pytest

from lab.observation_completeness import measure_target


@pytest.mark.parametrize(
    "target,sibling", [(True, False), (False, True), (True, True), (False, False)]
)
def test_separate_writer_does_not_leak_sibling_or_identity(tmp_path, target, sibling):
    # Scenario/oracle data goes only to the writer, never to measure_target.
    names = (["target"] if target else []) + (["sibling"] if sibling else [])
    subprocess.run(
        [
            sys.executable,
            "-B",
            "-c",
            "import pathlib,sys; [pathlib.Path(p).touch() for p in sys.argv[1:]]",
            *[str(tmp_path / name) for name in names],
        ],
        check=True,
    )
    result = measure_target(tmp_path / "target")
    assert result["target_present"] is target
    assert result["target_effect"] == ("BELEGT" if target else "ABWESEND")
    assert result["coverage"] == "UNVOLLSTAENDIG"
    assert result["all_effects_seen"] is False
    assert result["writer_identity"] == result["logical_agent_identity"] == "UNBEKANNT"
    assert result["source_authenticated"] is result["rights_inherited"] is False
    assert "sibling" not in str(result) and str(tmp_path) not in str(result)


def test_unavailable_directory_is_not_absence(tmp_path):
    assert measure_target(tmp_path / "missing" / "target")["target_effect"] == "UNBEKANNT"


def test_symlink_is_not_a_regular_target_effect(tmp_path):
    (tmp_path / "other").touch()
    (tmp_path / "target").symlink_to(tmp_path / "other")
    assert measure_target(tmp_path / "target")["target_effect"] == "UNBEKANNT"


@pytest.mark.skipif(os.geteuid() == 0, reason="root bypasses permission probe")
def test_unreadable_directory_is_not_absence(tmp_path):
    hidden = tmp_path / "hidden"
    hidden.mkdir()
    hidden.chmod(0)
    try:
        assert measure_target(hidden / "target")["target_effect"] == "UNBEKANNT"
    finally:
        hidden.chmod(0o700)
