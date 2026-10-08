"""Regression: the frozen collector helper must be started as a module.

This invokes only argparse --help, NEVER a C1-C7 experiment.
"""
from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys


def test_collector_run02_module_entrypoint_imports_without_capture():
    repo = Path(__file__).resolve().parents[1]
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    completed = subprocess.run(
        [
            sys.executable, "-m",
            "probes.collector_manipulation_c1_c7_run02",
            "--help",
        ],
        cwd=repo,
        env=env,
        capture_output=True,
        text=True,
        timeout=20,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    assert "--out OUT" in completed.stdout
    assert "--wait-seconds" in completed.stdout
