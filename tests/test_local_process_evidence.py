"""OS snapshot boundaries; synthetic native responses are not real measurements."""

from __future__ import annotations

import importlib.util
import json
import os
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "local_process_evidence.py"
spec = importlib.util.spec_from_file_location("process_evidence", SCRIPT)
assert spec is not None and spec.loader is not None
observer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(observer)
BOOT = "DC49C0BB-6806-459C-88F1-91149031ACAF"
CANARY = "SYNTHETIC-UNTRUSTED-PROCESS-CLAIM"


def process():
    return {"pid": 7, "ppid": 1, "uid": 501, "start_seconds": 100, "start_microseconds": 20}


def unavailable(*args):
    raise OSError(CANARY)


def test_unsupported_platform_does_not_run_native_reads(monkeypatch):
    monkeypatch.setattr(observer.sys, "platform", "unsupported")
    monkeypatch.setattr(observer, "_boot", lambda: pytest.fail("unexpected native read"))
    record = observer.observe()
    assert record["observer"]["aussage"] == record["parent"]["aussage"] == "UNBEKANNT"
    assert record["herkunft"] == record["identitaet"] == "UNBEKANNT"
    assert record["source_authenticated"] is False
    assert record["recht_uebernommen"] is False


def test_input_packet_cannot_issue_a_snapshot():
    with pytest.raises(TypeError):
        observer.observe({"source_authenticated": True, "pid": 7, "actor": CANARY})


def test_unavailable_boot_does_not_fall_back_to_session_labels(monkeypatch):
    monkeypatch.setattr(observer.sys, "platform", "darwin")
    monkeypatch.setattr(observer, "_boot", unavailable)
    record = observer.observe()
    assert record["observer"]["grund"] == record["parent"]["grund"] == "boot_unavailable"
    assert CANARY not in json.dumps(record)
    assert record["herkunft"] == record["identitaet"] == "UNBEKANNT"


def test_changed_process_discards_even_a_signature_read(monkeypatch):
    rows = iter([process(), process() | {"start_seconds": 200}])
    monkeypatch.setattr(observer, "_process", lambda pid: next(rows))
    monkeypatch.setattr(observer, "_signing", lambda pid: {"cdhash": "a" * 40, "team_id": CANARY})
    record = observer._snapshot(7, BOOT)
    assert record == {"aussage": "UNBEKANNT", "grund": "process_changed", "beleg": {}}
    assert CANARY not in json.dumps(record)


def test_process_error_does_not_publish_raw_error_or_claim(monkeypatch):
    monkeypatch.setattr(observer, "_process", unavailable)
    record = observer._snapshot(7, BOOT)
    assert record == {"aussage": "UNBEKANNT", "grund": "process_unavailable", "beleg": {}}
    assert CANARY not in json.dumps(record)


@pytest.mark.parametrize(
    "changed", [{"pid": 8}, {"uid": True}, {"start_seconds": 0}, {"start_microseconds": 1_000_000}]
)
def test_contradictory_or_invalid_process_cannot_be_positive(monkeypatch, changed):
    monkeypatch.setattr(observer, "_process", lambda pid: process() | changed)
    monkeypatch.setattr(observer, "_signing", unavailable)
    record = observer._snapshot(7, BOOT)
    assert record["aussage"] == "UNBEKANNT"
    assert record["beleg"] == {}


def test_process_snapshot_does_not_invent_signature_or_forward_other_fields(monkeypatch):
    monkeypatch.setattr(observer, "_process", lambda pid: process() | {"actor": CANARY})
    monkeypatch.setattr(observer, "_signing", unavailable)
    record = observer._snapshot(7, BOOT)
    assert record["aussage"] == "BELEGT"
    assert record["codesignature"] == "UNBEKANNT"
    assert record["beleg"] == process() | {"boot_id": BOOT}
    assert CANARY not in json.dumps(record)


def test_successful_process_reads_do_not_authenticate_session_or_actor(monkeypatch):
    monkeypatch.setattr(observer.sys, "platform", "darwin")
    monkeypatch.setattr(observer, "_boot", lambda: BOOT)
    monkeypatch.setattr(observer.os, "getpid", lambda: 7)
    monkeypatch.setattr(observer.os, "getppid", lambda: 7)
    monkeypatch.setattr(observer, "_process", lambda pid: process())
    monkeypatch.setattr(observer, "_signing", lambda pid: {"cdhash": "a" * 40, "team_id": None})
    record = observer.observe()
    assert record["observer"]["aussage"] == record["parent"]["aussage"] == "BELEGT"
    assert record["herkunft"] == record["identitaet"] == "UNBEKANNT"
    assert record["binding"] == "no_message_session_or_model_binding"
    assert record["source_authenticated"] is False
    assert record["recht_uebernommen"] is False


@pytest.mark.skipif(sys.platform != "darwin", reason="macOS kernel APIs only")
def test_actual_observer_snapshot_matches_current_process():
    record = observer.observe()
    current = record["observer"]
    assert current["aussage"] == "BELEGT"
    assert current["beleg"]["pid"] == os.getpid()
    assert current["beleg"]["uid"] == os.getuid()
    assert current["beleg"]["start_seconds"] > 0
    assert record["herkunft"] == record["identitaet"] == "UNBEKANNT"
    assert record["source_authenticated"] is False
