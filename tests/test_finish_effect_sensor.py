"""Source-sensor boundaries, distinct invocation identity and capture failure."""
from __future__ import annotations

import sys

from lab.fake_adapter import FakeAdapter
from research.finish_effect_observation import FinishEffectSensor


def traced(sensor, call):
    old = sys.gettrace()
    def callback(frame, event, arg):
        sensor.trace(frame, event, arg)
        return callback
    sys.settrace(callback)
    try:
        return call()
    finally:
        sys.settrace(old)
        sensor.close()


def test_real_write_observation_has_no_contents_or_extra_fields(monkeypatch):
    monkeypatch.setenv("LAB_AUTHORITY_EVENTS", "0")
    adapter, sensor = FakeAdapter(), FinishEffectSensor()
    def call():
        d = adapter.write("inert_actor_marker", "ordinary.py", "inert_workflow_marker", "inert_content_marker")
        assert d.allow
        assert adapter.lab.finish("inert_workflow_marker") is True
    traced(sensor, call)
    assert sensor.errors == 0
    assert [r['kind'] for r in sensor.events] == ['write_started', 'write_effect_before', 'write_effect', 'finish_return_before', 'finish_return']
    assert all(set(r) == {'run','kind','value','t_ns'} for r in sensor.events)
    assert sensor.events[1]['value'] is False and sensor.events[2]['value'] is True
    assert "marker" not in str(sensor.events)


def test_deny_is_never_an_effect_observation(monkeypatch):
    monkeypatch.setenv("LAB_AUTHORITY_EVENTS", "0")
    adapter, sensor = FakeAdapter(), FinishEffectSensor()
    traced(sensor, lambda: adapter.write("a", "config/security-policy.json", "wf", "inert"))
    assert not any(r['kind'].startswith('write_effect') for r in sensor.events)


def test_new_invocations_are_not_workflow_or_resource_identity(monkeypatch):
    monkeypatch.setenv("LAB_AUTHORITY_EVENTS", "0")
    adapter, sensor = FakeAdapter(), FinishEffectSensor()
    def call():
        adapter.write("a", "same.py", "same_workflow")
        adapter.lab.finish("same_workflow")
        adapter.write("a", "same.py", "same_workflow")
        adapter.lab.finish("same_workflow")
    traced(sensor, call)
    starts = [r['run'] for r in sensor.events if r['kind']=='write_started']
    finishes = [r['run'] for r in sensor.events if r['kind']=='finish_return']
    assert starts == [1,2] and finishes == [1,2]
    assert sensor.errors == 0


def test_recorder_failure_does_not_prevent_original_write_or_finish(monkeypatch):
    monkeypatch.setenv("LAB_AUTHORITY_EVENTS", "0")
    adapter, sensor = FakeAdapter(), FinishEffectSensor()
    def broken(*args):
        raise OSError("inert sensor error")
    monkeypatch.setattr(sensor, '_add', broken)
    def call():
        assert adapter.write("a", "ordinary.py", "wf", "inert").allow
        assert adapter.lab.finish("wf")
    traced(sensor, call)
    assert "ordinary.py" in adapter.repo.files
    assert sensor.errors > 0
