"""Run 03 pre-capture smoke check; does not invoke C1-C7 or ground truth."""
from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys


def test_run03_module_entrypoint_and_frozen_copy():
    repo = Path(__file__).resolve().parents[1]
    previous = (repo / "probes/collector_manipulation_c1_c7_run02.py").read_text()
    current = (repo / "probes/collector_manipulation_c1_c7_run03.py").read_text()
    assert current == previous.replace(
        "Frozen C1-C7 Run-02 capture", "Independent C1-C7 Run-03 capture"
    ).replace(
        "/tmp/aa-collector-manipulation-c1-c7-run02-20261008",
        "/tmp/aa-collector-manipulation-c1-c7-run03-20261008",
    )
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    completed = subprocess.run(
        [sys.executable, "-m", "probes.collector_manipulation_c1_c7_run03", "--help"],
        cwd=repo, env=env, capture_output=True, text=True, timeout=20, check=False
    )
    assert completed.returncode == 0, completed.stderr
    assert "--out OUT" in completed.stdout
    assert "--wait-seconds" in completed.stdout
