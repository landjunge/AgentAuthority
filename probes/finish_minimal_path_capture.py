"""One unchanged original probe, two separate passive observation channels."""
from __future__ import annotations

import json
import sys
import threading

import pytest

from probes import finish_observer_case_capture as oracle
from research.finish_effect_observation import FinishEffectSensor

sensor: FinishEffectSensor


def pytest_configure(config):
    global sensor
    oracle.pytest_configure(config)
    sensor = FinishEffectSensor()


def combined_trace(frame, event, arg):
    oracle.trace(frame, event, arg)
    sensor.trace(frame, event, arg)
    return combined_trace


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_call(item):
    if str(item.path) != oracle.PROBE or item.name != oracle.NODE:
        raise RuntimeError("only_the_frozen_original_probe_is_authorized")
    old_main, old_thread = sys.gettrace(), threading.gettrace()
    sys.settrace(combined_trace)
    threading.settrace(combined_trace)
    try:
        yield
    finally:
        sys.settrace(old_main)
        threading.settrace(old_thread)
        sensor.close()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    yield from oracle.pytest_runtest_makereport(item, call)


def pytest_sessionfinish(session, exitstatus):
    oracle.pytest_sessionfinish(session, exitstatus)
    path = oracle.output / "original/observations.jsonl"
    with path.open("x") as handle:
        for row in sensor.events:
            handle.write(json.dumps(row, separators=(",", ":")) + "\n")
    path.chmod(0o444)
    oracle.save(oracle.output / "original/capture.json",
                {"recording_errors": sensor.errors, "test_invocations": 1,
                 "pytest_exit_code": int(exitstatus)})
