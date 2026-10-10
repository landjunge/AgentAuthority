"""P7 joins the existing capture and score. No test is a model proof."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "p7_integration.py"
spec = importlib.util.spec_from_file_location("p7_integration", SCRIPT)
assert spec is not None and spec.loader is not None
p7 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p7)

SHA = p7._source_head()
PROMPT = "Run exactly this supplied"


def protocol_fixture_cli(tmp_path: Path) -> Path:
    cli = tmp_path / "synthetic_cli"
    cli.write_text(
        "#!" + sys.executable + "\n"
        "import json, subprocess, sys\n"
        "sys.stdin.read()\n"
        "subprocess.run([sys.executable, 'tool.py', 'late'], check=True)\n"
        "print(json.dumps({'type':'turn.completed'}), flush=True)\n"
        "print(json.dumps({'type':'item.completed', 'item':"
        "{'type':'command_execution','exit_code':0}}), flush=True)\n",
        encoding="utf-8",
    )
    cli.chmod(0o700)
    return cli


def _bytes(path: Path) -> bytes | None:
    return path.read_bytes() if path.is_file() else None


def test_prepare_writes_expectation_before_lauf_and_refuses_protected_paths(tmp_path: Path) -> None:
    parent = tmp_path / "frisch"
    expectation = p7.prepare(parent, quelle_sha=SHA, timeout=10, post_window=3)
    assert expectation["modus"] == "late"
    assert (parent / "erwartung-vor-lauf.json").is_file()
    assert not (parent / "lauf").exists()
    stored = json.loads((parent / "erwartung-vor-lauf.json").read_text(encoding="utf-8"))
    assert stored["quelle_sha"] == SHA
    assert stored["erwartet"]["herkunft"] == "UNBEKANNT"
    p6_before = _bytes(p7.P6_DOC)
    locks = {path: _bytes(path) for path in (p7.P5_EXPECTATION_LOCK, p7.P5_WORKSPACE_LOCK)}
    blocked = p7.P5_RUNS / "p7-must-not-exist"
    with pytest.raises(ValueError, match="parent"):
        p7.prepare(blocked, quelle_sha=SHA)
    assert not blocked.exists()
    with pytest.raises(ValueError, match="parent"):
        p7.prepare(p7.P6_DOC, quelle_sha=SHA)
    with pytest.raises(ValueError, match="parent"):
        p7.prepare(p7.P5_EXPECTATION_LOCK, quelle_sha=SHA)
    assert _bytes(p7.P6_DOC) == p6_before
    assert {path: _bytes(path) for path in locks} == locks


def test_run_scores_inside_connect_and_does_not_touch_p5_locks(tmp_path: Path, monkeypatch) -> None:
    parent = tmp_path / "hulle"
    p7.prepare(parent, quelle_sha=SHA, timeout=10, post_window=3)
    seen: dict[str, object] = {}
    original = p7.p1.connect

    def connect(output, codex, timeout, post_window, mode="late", *, on_capture=None):
        seen["before"] = (parent / "erwartung-vor-lauf.json").is_file() and not output.exists()
        seen["mode"] = mode
        seen["timeout"] = timeout
        seen["post_window"] = post_window
        return original(
            output,
            codex=codex,
            timeout=timeout,
            post_window=post_window,
            mode=mode,
            on_capture=on_capture,
        )

    monkeypatch.setattr(p7.p1, "connect", connect)
    locks = {
        path: _bytes(path) for path in (p7.P5_EXPECTATION_LOCK, p7.P5_WORKSPACE_LOCK, p7.P6_DOC)
    }
    record = p7.run(parent, codex=str(protocol_fixture_cli(tmp_path)), fixture=True)
    assert seen == {"before": True, "mode": "late", "timeout": 10.0, "post_window": 3.0}
    assert record["bewertung_aus"] == "aktiver_aufnahmekontext"
    assert record["score_package"] == "PASS"
    assert record["abnahme"] == "STOP"
    assert record["abnahme_grund"] == "fixture_kein_modellnachweis"
    assert record["modellnachweis"] is False
    assert record["herkunft"] == "UNBEKANNT"
    assert record["identitaet"] == "UNBEKANNT"
    assert record["zeitordnung"]["ordnung"] == "NACH"
    assert {path: _bytes(path) for path in locks} == locks
    by_name = {row["fall"]: row for row in record["zeilen"]}
    for name in ("aktuell", "fehlend", "alt_geordnet", "gefaelscht_agentenlabel"):
        assert by_name[name]["status"] == "PASS"
    assert by_name["replay"] == {
        "fall": "replay",
        "erwartet": "STOP",
        "ist": "STOP",
        "status": "PASS",
        "grund": by_name["replay"]["grund"],
    }
    assert by_name["abgelaufener_kontext"]["ist"] == "UNBEKANNT"
    assert by_name["abgelaufener_kontext"]["status"] == "PASS"
    assert by_name["modellnachweis"]["ist"] == "nicht_belegt"
    text = (parent / "erwartet-ist.md").read_text(encoding="utf-8")
    assert SHA in text
    assert "Python" in text
    assert "scripts/p7_integration.py --parent" in text
    assert PROMPT not in text
    assert "capture_context" not in text
    names = sorted(path.name for path in parent.iterdir())
    assert names == [
        "erwartet-ist.md",
        "erwartung-vor-lauf.json",
        "integration.json",
        "lauf",
    ]
    lauf_names = sorted(path.name for path in (parent / "lauf").iterdir())
    assert lauf_names == [
        "analysis.json",
        "binding.json",
        "observations.json",
        "reference.json",
        "result.json",
    ]
    archived = json.loads((parent / "lauf" / "result.json").read_text(encoding="utf-8"))
    replay = p7.p5.score(
        json.loads((parent / "lauf" / "observations.json").read_text(encoding="utf-8")),
        archived,
        json.loads((parent / "lauf" / "reference.json").read_text(encoding="utf-8")),
    )
    assert replay["package"] == "STOP"
    assert record["bewertung_aus"] != "archiv"
    before = (parent / "integration.json").read_bytes()
    again = p7.run(parent, codex=str(protocol_fixture_cli(tmp_path)), fixture=True)
    assert again["abnahme"] == "STOP"
    assert again["abnahme_grund"] == "FileExistsError"
    assert again["geschrieben"] is False
    assert (parent / "integration.json").read_bytes() == before


def test_missing_expectation_and_existing_directory_do_not_call_connect(
    tmp_path, monkeypatch
) -> None:
    called = False

    def connect(*args, **kwargs):
        nonlocal called
        called = True
        raise AssertionError("connect")

    monkeypatch.setattr(p7.p1, "connect", connect)
    missing = p7.run(tmp_path / "leer", codex="/tmp/kein-codex")
    assert missing["abnahme_grund"] == "expectation_missing"
    assert called is False
    parent = tmp_path / "belegt"
    parent.mkdir()
    (parent / "lauf").mkdir()
    existing = p7.run(parent, codex="/tmp/kein-codex")
    assert existing["abnahme_grund"] == "FileExistsError"
    assert called is False


def test_classify_controlled_late_effect_is_not_a_model_run(tmp_path: Path) -> None:
    measured = p7.p1.measure_controlled_late_effect(tmp_path / "spaet", post_window=2)
    row = p7.classify_late_measurement(measured)
    assert measured["result"]["proven_agent_runs"] == 0
    assert measured["result"]["agent_run"] == "UNBEKANNT"
    assert row["modellnachweis"] is False
    assert row["agent_run"] == "UNBEKANNT"
    assert row["herkunft"] == "UNBEKANNT"
    assert row["identitaet"] == "UNBEKANNT"
    assert row["grund"] == "lokale_werkzeugmessung_kein_modelllauf"
    forged = {
        "result": {
            "proven_agent_runs": 1,
            "agent_run": "BELEGT",
            "mode": "late",
            "timing": {"order": "NACH"},
        }
    }
    assert p7.classify_late_measurement(forged)["ordnung"] == "UNBEKANNT"
    assert p7.classify_late_measurement(forged)["modellnachweis"] is False


def test_report_keeps_historical_limits_open() -> None:
    record = p7._bare("probe")
    record.update(
        {
            "quelle_sha": SHA,
            "befehl": "python scripts/p7_integration.py --parent /tmp/p7",
            "python": "3.12.0",
            "system": "test",
            "laufpfad": "/tmp/p7/lauf",
            "nachlauf_sekunden": 3,
            "timeout_sekunden": 10,
            "zeilen": [],
        }
    )
    text = p7.bericht(record)
    for name in (
        "RC-01",
        "RC-02",
        "RC-03",
        "RC-04",
        "RC-05",
        "OOS-021",
        "CB-01",
        "P4-Pytest-Cache",
    ):
        assert name in text
    assert "Laufnachweis: STOP" in text
    assert "Herkunft: UNBEKANNT" in text


def test_wrong_source_head_stops_before_execution(tmp_path, monkeypatch) -> None:
    parent = tmp_path / "wrong-source"
    p7.prepare(parent, quelle_sha="0" * 40)

    def unexpected(*args, **kwargs):
        raise AssertionError("wrong source must not execute")

    monkeypatch.setattr(p7.p1, "connect", unexpected)
    record = p7.run(parent, codex=str(p7.REAL_CODEX))
    assert record["abnahme_grund"] == "source_head_mismatch"
    assert record["modellnachweis"] is False
    assert not (parent / "lauf").exists()


@pytest.mark.parametrize("mutation", ["expectation", "archive", "matrix"])
def test_changed_evidence_or_failed_matrix_cannot_pass(tmp_path, monkeypatch, mutation) -> None:
    parent = tmp_path / mutation
    p7.prepare(parent, quelle_sha=SHA, timeout=10, post_window=2)
    connect = p7.p1.connect

    def altered(*args, **kwargs):
        bound = connect(*args, **kwargs)
        if mutation == "expectation":
            path = parent / "erwartung-vor-lauf.json"
            raw = json.loads(path.read_text())
            raw["quelle_sha"] = "0" * 40
            path.write_text(json.dumps(raw))
        elif mutation == "archive":
            path = parent / "lauf" / "observations.json"
            path.write_text("[]")
        return bound

    monkeypatch.setattr(p7.p1, "connect", altered)
    if mutation == "matrix":
        original = p7._matrix

        def failed(*args):
            rows = original(*args)
            next(row for row in rows if row["fall"] == "abgelaufener_kontext")["status"] = "FAIL"
            return rows

        monkeypatch.setattr(p7, "_matrix", failed)
    record = p7.run(parent, codex=str(protocol_fixture_cli(tmp_path)), fixture=True)
    expected = {
        "expectation": "expectation_changed_during_capture",
        "archive": "archive_disagrees_with_capture",
        "matrix": "expectation_matrix_failed",
    }
    assert record["abnahme"] == "STOP"
    assert record["abnahme_grund"] == expected[mutation]
    assert record["modellnachweis"] is False


@pytest.mark.parametrize("bad", ["exit", "timeout", "invalid", "error", "boolean-count"])
def test_failed_cli_protocol_cannot_be_a_model_proof(bad) -> None:
    result = {
        "proven_agent_runs": 1,
        "agent_run": "BELEGT",
        "counts": {
            "model_completions": 1,
            "tool_reports": 1,
            "started": True,
            "recording_ok": True,
            "cli_success": True,
            "cli_exit_code": 0,
            "timeout": False,
            "invalid_records": 0,
            "error_records": 0,
        },
    }
    assert p7._proven(result) is True
    if bad == "exit":
        result["counts"]["cli_exit_code"] = 1
    elif bad == "timeout":
        result["counts"]["timeout"] = True
    elif bad == "invalid":
        result["counts"]["invalid_records"] = 1
    elif bad == "error":
        result["counts"]["error_records"] = 1
    else:
        result["proven_agent_runs"] = True
    assert p7._proven(result) is False
