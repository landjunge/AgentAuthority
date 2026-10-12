"""Test-only two-window observer. No p1/P6 changes or writer attribution."""

from __future__ import annotations

import json
import subprocess
import sys
import time

import pytest


def classify_interval(last_absent, first_present, boundary, end, *, failed=False):
    if failed or first_present is None:
        return "UNBEKANNT", "observation_failed" if failed else "not_observed_in_windows"
    if last_absent is None or first_present > end:
        return "UNBEKANNT", "unbounded_interval"
    if first_present <= boundary:
        return "NACH", "first_window"
    if last_absent >= boundary:
        return "SPAETER", "second_window"
    return "UNBEKANNT", "window_boundary_overlap"


def probe_windows(parent, delay):
    target = parent / "target"
    # Writer's schedule and oracle are not inputs to the observation loop.
    code = (
        "import pathlib,sys,time,json; print('READY',flush=True); sys.stdin.readline(); "
        "time.sleep(float(sys.argv[2])); before=time.monotonic_ns(); "
        "pathlib.Path(sys.argv[1]).touch(); after=time.monotonic_ns(); "
        "print(json.dumps({'write_begin':before,'write_end':after}),flush=True)"
    )
    child = subprocess.Popen(
        [sys.executable, "-B", "-c", code, str(target), str(delay)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True,
    )
    assert child.stdout.readline().strip() == "READY"
    started = time.monotonic_ns()
    boundary, end = started + 200_000_000, started + 800_000_000
    child.stdin.write("start\n")
    child.stdin.flush()
    last_absent = first_present = None
    failed = False
    while time.monotonic_ns() <= end:
        before = time.monotonic_ns()
        try:
            target.lstat()
        except FileNotFoundError:
            last_absent = before  # conservative lower bound, not stat completion
        except OSError:
            failed = True
            break
        else:
            first_present = time.monotonic_ns()  # conservative upper bound
            break
        time.sleep(0.01)
    # Read the separate oracle only after the observation has been classified.
    verdict, reason = classify_interval(last_absent, first_present, boundary, end, failed=failed)
    output, _ = child.communicate(timeout=3)
    assert child.returncode == 0
    oracle = json.loads(output)
    return {
        "verdict": verdict,
        "reason": reason,
        "start": started,
        "boundary": boundary,
        "end": end,
        "last_absent": last_absent,
        "first_present": first_present,
        "oracle": oracle,
        "writer_identity": "UNBEKANNT",
        "logical_agent_identity": "UNBEKANNT",
    }


@pytest.mark.parametrize("delay,expected", [(0.08, "NACH"), (0.35, "SPAETER"), (0.9, "UNBEKANNT")])
def test_actual_writer_and_independent_window_observation(tmp_path, delay, expected):
    result = probe_windows(tmp_path, delay)
    assert result["verdict"] == expected
    oracle = result["oracle"]
    if expected == "NACH":
        assert oracle["write_end"] <= result["boundary"]
    elif expected == "SPAETER":
        assert result["boundary"] < oracle["write_begin"] <= oracle["write_end"] <= result["end"]
    else:
        assert oracle["write_begin"] > result["end"]
    assert result["writer_identity"] == result["logical_agent_identity"] == "UNBEKANNT"


@pytest.mark.parametrize(
    "last,first,expected,reason",
    [
        (9, 10, "NACH", "first_window"),
        (10, 11, "SPAETER", "second_window"),
        (9, 11, "UNBEKANNT", "window_boundary_overlap"),
        (None, 11, "UNBEKANNT", "unbounded_interval"),
        (11, 21, "UNBEKANNT", "unbounded_interval"),
    ],
)
def test_boundary_precision_is_not_invented(last, first, expected, reason):
    assert classify_interval(last, first, 10, 20) == (expected, reason)


def test_observation_failure_is_not_absence():
    assert classify_interval(11, 12, 10, 20, failed=True) == ("UNBEKANNT", "observation_failed")


# Foreign capture is deliberately not simulated: no admissible live-append
# entrypoint/source signal exists. Its research hypothesis remains unjudged.
