"""Synthetic CLI records test the recorder; these are never real-agent evidence."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import time
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "p1_controlled_run.py"
spec = importlib.util.spec_from_file_location("p1_controlled_run", SCRIPT)
assert spec is not None and spec.loader is not None
p1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p1)


def event(kind, value, seq, run=1):
    return {"run": run, "kind": kind, "value": value, "t_ns": seq, "event": seq}


def observation(present=True, success=True):
    return [
        event("target_initial", False, 1),
        event("tool_end", success, 2),
        event("cli_end", success, 3),
        event("target_final", present, 4),
    ]


@pytest.mark.parametrize("success", [True, False])
@pytest.mark.parametrize("present", [True, False])
def test_snapshot_is_independent_of_reported_success(success, present):
    answer = p1.infer(observation(present, success), 1)
    assert answer["verdict"] == "BELEGT"
    assert answer["target_present"] is present
    assert 2 not in answer["evidence"]


@pytest.mark.parametrize("remove", ["target_initial", "target_final", "cli_end"])
def test_missing_measurement_never_becomes_effect(remove):
    rows = [e for e in observation() if e["kind"] != remove]
    assert p1.infer(rows, 1)["verdict"] == "UNBEKANNT"


def test_status_only_wrong_run_and_recording_error_are_unknown():
    assert (
        p1.infer([event("tool_end", True, 1), event("cli_end", True, 2)], 1)["verdict"]
        == "UNBEKANNT"
    )
    assert p1.infer(observation(), 2)["verdict"] == "UNBEKANNT"
    assert p1.infer(observation(), 1, False)["verdict"] == "UNBEKANNT"


def test_duplicate_and_conflict_handling():
    rows = observation()
    assert p1.infer(rows + [rows[-1].copy()], 1) == p1.infer(rows, 1)
    assert p1.infer(rows + [{**rows[-1], "value": False}], 1)["verdict"] == "UNBEKANNT"
    assert p1.infer(rows + [event("target_final", False, 5)], 1)["verdict"] == "UNBEKANNT"


@pytest.mark.parametrize(
    "patch",
    [{"kind": []}, {"value": 1}, {"run": True}, {"event": 0}, {"t_ns": -1}, {"payload": "private"}],
)
def test_malformed_evidence_is_unknown(patch):
    rows = observation()
    rows[-1] = {**rows[-1], **patch}
    assert p1.infer(rows, 1)["verdict"] == "UNBEKANNT"


def test_preexisting_target_or_reversed_measurement_is_unknown():
    rows = observation()
    rows[0]["value"] = True
    assert p1.infer(rows, 1)["verdict"] == "UNBEKANNT"
    rows = observation()
    rows[-1]["t_ns"] = 2
    assert p1.infer(rows, 1)["verdict"] == "UNBEKANNT"


def test_projection_drops_canaries_ids_and_usage():
    counts = {"invalid_records": 0, "model_completions": 0, "tool_reports": 0, "error_records": 0}
    rows = []
    raw = {
        "type": "item.completed",
        "id": "PRIVATE",
        "item": {
            "type": "command_execution",
            "exit_code": 0,
            "command": "PRIVATE",
            "aggregated_output": "PRIVATE",
            "status": "PRIVATE",
        },
        "usage": "PRIVATE",
    }
    p1.project(raw, 1, rows, counts)
    assert counts["tool_reports"] == 1
    assert set(rows[0]) == p1.FIELDS
    assert "PRIVATE" not in json.dumps(rows) + json.dumps(counts)
    raw["item"]["exit_code"] = True
    p1.project(raw, 1, rows, counts)
    assert len(rows) == 1 and counts["invalid_records"] == 1


@pytest.mark.parametrize(
    "mode,exists,code",
    [("write", True, 0), ("noop", False, 0), ("fail", False, 1), ("write_fail", True, 1)],
)
def test_real_local_tool_and_separate_reference(tmp_path, mode, exists, code):
    # Real filesystem/process test, NOT a real LLM/agent run.
    tool = tmp_path / "tool.py"
    tool.write_text(p1.TOOL)
    completed = subprocess.run([sys.executable, str(tool), mode], check=False)
    assert completed.returncode == code
    assert p1.probe(tmp_path / "target") is exists
    answer = p1.reference(tmp_path, (time.monotonic_ns(), time.monotonic_ns()))
    assert answer == {"calls": 1, "target_present": exists, "valid": True}


def test_missing_conflicting_or_late_reference_is_not_truth(tmp_path):
    cutoff = (1, 2)
    assert p1.reference(tmp_path, cutoff)["valid"] is False
    (tmp_path / "target").touch()
    receipt = tmp_path / "receipt.jsonl"
    for content in (
        '{"call": 1}\n',
        '{"call": true}\n',
        '{"call": true}\n{"created": [2, 3]}\n',
        '{"call": true}\n{"call": true}\n{"created": [1, 1]}\n',
    ):
        receipt.write_text(content)
        assert p1.reference(tmp_path, cutoff)["valid"] is False


def test_symlink_never_becomes_target_evidence(tmp_path):
    outside = tmp_path / "other"
    outside.touch()
    (tmp_path / "target").symlink_to(outside)
    assert p1.probe(tmp_path / "target") is None


def test_sensor_failure_is_missing_evidence(tmp_path, monkeypatch):
    def unavailable(self):
        raise PermissionError("PRIVATE")

    monkeypatch.setattr(Path, "lstat", unavailable)
    assert p1.probe(tmp_path / "target") is None


def test_capture_start_failure_and_reference_order(tmp_path, monkeypatch):
    original = p1.reference

    def checked_reference(root, cutoff):
        assert (tmp_path / "run" / "analysis.json").is_file()
        assert (tmp_path / "run" / "observations.json").is_file()
        return original(root, cutoff)

    monkeypatch.setattr(p1, "reference", checked_reference)
    result = p1.capture(tmp_path / "run", codex=str(tmp_path / "missing"))
    assert result["proven_agent_runs"] == 0
    assert result["agent_run"] == result["evaluation"] == "UNBEKANNT"
    assert result["target"]["verdict"] == "UNBEKANNT"
    assert "timing" not in result
    assert result["scope"] == "local_target_snapshot_at_window_end_only"
    with pytest.raises(FileExistsError):
        p1.capture(tmp_path / "run")


@pytest.mark.parametrize(
    "code",
    [
        "print('malformed')",
        "print('X' * 100000)",
        "print('[' * 1500 + ']' * 1500)",
        "import time; time.sleep(10)",
    ],
)
def test_actual_process_recording_errors_and_timeout(tmp_path, code):
    rows = []
    counts = p1.collect([sys.executable, "-c", code], "", tmp_path, 1, rows, 0.5)
    assert counts["recording_ok"] is False
    assert p1.infer(rows, 1, counts["recording_ok"])["verdict"] == "UNBEKANNT"
    assert counts["stdout_bytes"] + counts["stderr_bytes"] <= p1.MAX_STREAM + 8192


def test_capture_persists_no_raw_failure_text(tmp_path):
    fake_cli = tmp_path / "synthetic_cli"
    fake_cli.write_text(
        "#!" + sys.executable + "\nimport sys\n"
        "sys.stdin.read()\nprint('PRIVATE_RAW_CANARY')\n"
        "print('PRIVATE_RAW_CANARY', file=sys.stderr)\n"
    )
    fake_cli.chmod(0o700)
    result = p1.capture(tmp_path / "run", codex=str(fake_cli))
    assert result["agent_run"] == "UNBEKANNT"
    assert result["target"]["verdict"] == "UNBEKANNT"
    assert "PRIVATE_RAW_CANARY" not in "".join(
        path.read_text() for path in (tmp_path / "run").iterdir()
    )


@pytest.mark.parametrize("timeout", [float("nan"), float("inf"), 0, -1, 301])
def test_invalid_timeout_does_not_create_run(tmp_path, timeout):
    with pytest.raises(ValueError):
        p1.capture(tmp_path / "run", timeout=timeout)
    assert not (tmp_path / "run").exists()


def test_capture_pins_requested_model_and_keeps_controls(tmp_path, monkeypatch):
    original = p1.collect

    def checked_collect(argv, *args):
        assert argv[argv.index("--model") + 1] == "gpt-6.1-sol"
        assert argv[argv.index("--ask-for-approval") + 1] == "never"
        assert argv[argv.index("--sandbox") + 1] == "workspace-write"
        assert "--ephemeral" in argv and "--json" in argv
        return original(argv, *args)

    monkeypatch.setattr(p1, "collect", checked_collect)
    result = p1.capture(tmp_path / "run", codex=str(tmp_path / "missing"))
    assert result["requested_model"] == "gpt-6.1-sol"
    assert result["counts"]["cli_exit_code"] is None
    assert result["counts"]["startup_error"] == "UNBEKANNT"
    assert result["agent_run"] == "UNBEKANNT"


@pytest.mark.parametrize("known", [True, False])
def test_start_error_classification_across_reads_drops_raw_text(tmp_path, known):
    # A local synthetic process checks diagnostic projection, not model access.
    raw = (p1.START_ERROR if known else b"unrecognized failure") + b" PRIVATE_RAW_CANARY"
    code = (
        "import os, sys, time\n"
        f"raw = {raw!r}\n"
        "os.write(2, raw[:20])\n"
        "time.sleep(0.1)\n"
        "os.write(2, raw[20:])\n"
        "sys.exit(7)\n"
    )
    rows = []
    counts = p1.collect([sys.executable, "-c", code], "", tmp_path, 1, rows, 2)
    assert counts["cli_exit_code"] == 7
    assert counts["cli_success"] is False
    assert counts["startup_error"] == ("app_server_init_eperm" if known else "UNBEKANNT")
    assert counts["model_completions"] == counts["tool_reports"] == 0
    assert "PRIVATE_RAW_CANARY" not in json.dumps(counts) + json.dumps(rows)
    assert p1.infer(rows, 1)["verdict"] == "UNBEKANNT"


def test_capture_archives_only_known_diagnostic_enum(tmp_path):
    fake_cli = tmp_path / "synthetic_cli"
    fake_cli.write_text(
        "#!" + sys.executable + "\nimport sys\n"
        "sys.stdin.read()\n"
        f"sys.stderr.buffer.write({p1.START_ERROR!r} + b' PRIVATE_RAW_CANARY')\n"
        "sys.exit(1)\n"
    )
    fake_cli.chmod(0o700)
    result = p1.capture(tmp_path / "run", codex=str(fake_cli))
    assert result["counts"]["startup_error"] == "app_server_init_eperm"
    assert result["agent_run"] == result["evaluation"] == "UNBEKANNT"
    archived = "".join(path.read_text() for path in (tmp_path / "run").iterdir())
    assert "PRIVATE_RAW_CANARY" not in archived
    assert p1.START_ERROR.decode() not in archived


def stamped(kind, value, seq, t_ns, run=1):
    return {"run": run, "kind": kind, "value": value, "t_ns": t_ns, "event": seq}


def late_observation():
    return [
        event("target_initial", False, 1),
        event("tool_end", True, 2),
        stamped("cli_end", True, 3, 10),
        stamped("target_absent", False, 4, 12),
        stamped("target_seen", True, 5, 13),
        stamped("target_final", True, 6, 14),
    ]


def test_snapshot_ignores_post_end_samples():
    answer = p1.infer(late_observation(), 1)
    assert answer["verdict"] == "BELEGT"
    assert answer["target_present"] is True
    assert answer["evidence"] == [1, 3, 6]
    assert "timing" not in answer


def test_order_is_nach_only_with_absence_after_end_then_presence():
    answer = p1.relate(late_observation(), 1)
    assert answer == {
        "verdict": "BELEGT",
        "order": "NACH",
        "reason": "absence_after_end_then_presence",
        "evidence": [3, 4, 5],
    }
    assert 2 not in answer["evidence"]
    rows = late_observation()
    assert p1.relate(rows + [rows[3].copy()], 1) == answer


def test_first_sighting_after_end_is_not_a_late_effect():
    rows = observation(True)
    answer = p1.relate(rows, 1)
    assert answer["verdict"] == "UNBEKANNT"
    assert answer["order"] is None
    assert answer["reason"] == "insufficient_order_evidence"


def test_no_effect_makes_order_inapplicable():
    answer = p1.relate(observation(False), 1)
    assert answer["verdict"] == "NICHT_ANWENDBAR"
    assert answer["order"] is None
    assert answer["reason"] == "no_effect"


def test_interval_crossing_cli_end_stays_unknown():
    rows = [
        event("target_initial", False, 1),
        stamped("cli_end", True, 2, 10),
        stamped("target_absent", False, 3, 9),
        stamped("target_seen", True, 4, 11),
        stamped("target_final", True, 5, 12),
    ]
    answer = p1.relate(rows, 1)
    assert answer["verdict"] == "UNBEKANNT"
    assert answer["order"] is None


def test_presence_before_end_is_vor_and_conflicts_with_a_late_pair():
    rows = [
        stamped("target_seen", True, 1, 4),
        stamped("cli_end", True, 2, 10),
        stamped("target_final", True, 3, 12),
    ]
    assert p1.relate(rows, 1)["order"] == "VOR"
    late = late_observation()
    late[0]["value"] = True
    conflict = p1.relate(late, 1)
    assert conflict["verdict"] == "UNBEKANNT"
    assert conflict["order"] is None
    assert conflict["reason"] == "conflicting_evidence"


def test_boundary_and_bad_order_samples_are_unknown():
    rows = late_observation()
    rows[3]["t_ns"] = rows[2]["t_ns"]
    assert p1.relate(rows, 1)["order"] is None
    rows = late_observation()
    rows[3]["value"] = True
    assert p1.relate(rows, 1)["reason"] == "invalid_evidence"
    rows = late_observation()
    rows.append(stamped("target_absent", False, 8, 20))
    assert p1.relate(rows, 1)["reason"] == "conflicting_evidence"
    assert p1.relate(late_observation(), 1, False)["reason"] == "recording_error"


def test_reference_order_classifies_the_receipt_interval(tmp_path):
    cli_end = 1_000
    assert p1.reference_order(tmp_path, cli_end)["valid"] is False
    receipt = tmp_path / "receipt.jsonl"
    receipt.write_text('{"call": true}\n')
    assert p1.reference_order(tmp_path, cli_end) == {
        "order": None,
        "applicable": False,
        "valid": True,
    }
    (tmp_path / "target").write_bytes(b"")
    receipt.write_text('{"call": true}\n{"created": [1001, 1002]}\n')
    assert p1.reference_order(tmp_path, cli_end)["order"] == "NACH"
    receipt.write_text('{"call": true}\n{"created": [10, 11]}\n')
    assert p1.reference_order(tmp_path, cli_end)["order"] == "VOR"
    receipt.write_text('{"call": true}\n{"created": [999, 1001]}\n')
    assert p1.reference_order(tmp_path, cli_end)["valid"] is False
    receipt.write_text('{"call": true}\n{"created": [1000, 1002]}\n')
    assert p1.reference_order(tmp_path, cli_end)["valid"] is False
    (tmp_path / "target").unlink()
    receipt.write_text('{"call": true}\n{"created": [1001, 1002]}\n')
    assert p1.reference_order(tmp_path, cli_end)["valid"] is False


def test_order_disagreement_is_false_and_missing_reference_is_unknown():
    nach = p1.relate(late_observation(), 1)
    none = {"order": None, "applicable": False, "valid": True}
    after = {"order": "NACH", "applicable": True, "valid": True}
    before = {"order": "VOR", "applicable": True, "valid": True}
    invalid = {"order": "NACH", "applicable": True, "valid": False}
    assert p1.compare_order(nach, after, True) == "KORREKT"
    assert p1.compare_order(nach, before, True) == "FALSCH"
    assert p1.compare_order(p1.relate(observation(False), 1), none, True) == "KORREKT"
    assert p1.compare_order(nach, invalid, True) == "UNBEKANNT"
    assert p1.compare_order(nach, after, False) == "UNBEKANNT"
    assert p1.compare_order(p1.relate(observation(True), 1), after, True) == "UNBEKANNT"


def test_late_tool_creates_only_after_end_and_release(tmp_path):
    tool = tmp_path / "tool.py"
    tool.write_text(p1.TOOL)
    (tmp_path / "late.bound").write_text("8\n")
    held = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"])
    try:
        (tmp_path / "cli.pid").write_text(f"{held.pid}\n")
        parent = subprocess.run([sys.executable, str(tool), "late"], check=False, timeout=3)
        assert parent.returncode == 0
        assert p1.probe(tmp_path / "target") is False
        held.kill()
        held.wait(timeout=2)
        time.sleep(0.2)
        assert p1.probe(tmp_path / "target") is False
        (tmp_path / "post.observe").write_bytes(b"")
        deadline = time.monotonic() + 3
        while time.monotonic() < deadline and p1.probe(tmp_path / "target") is not True:
            time.sleep(0.02)
        assert p1.probe(tmp_path / "target") is True
    finally:
        if held.poll() is None:
            held.kill()
            held.wait(timeout=2)
    cutoff = time.monotonic_ns()
    assert p1.reference(tmp_path, (cutoff, cutoff)) == {
        "calls": 1,
        "target_present": True,
        "valid": True,
    }
    assert p1.reference_order(tmp_path, 1)["order"] == "NACH"


def test_late_tool_without_pid_creates_nothing(tmp_path):
    tool = tmp_path / "tool.py"
    tool.write_text(p1.TOOL)
    completed = subprocess.run([sys.executable, str(tool), "late"], check=False, timeout=3)
    assert completed.returncode == 0
    assert p1.probe(tmp_path / "target") is False
    assert p1.reference(tmp_path, (1, 1))["target_present"] is False


def executable(path: Path, body: str) -> None:
    path.write_text("#!" + sys.executable + "\n" + body)
    path.chmod(0o700)


def test_local_late_window_is_ordered_and_is_not_archived_as_text(tmp_path, monkeypatch):
    # Local processes only. Synthetic JSONL is not a real model run.
    original = p1.reference

    def checked(root, cutoff):
        analysis = tmp_path / "run" / "analysis.json"
        assert analysis.is_file()
        assert not (tmp_path / "run" / "reference.json").exists()
        assert "timing" in json.loads(analysis.read_text())
        return original(root, cutoff)

    monkeypatch.setattr(p1, "reference", checked)
    executable(
        tmp_path / "synthetic_cli",
        "import subprocess, sys\n"
        "sys.stdin.read()\n"
        "subprocess.run([sys.executable, 'tool.py', 'late'], check=False)\n"
        'print("{\\"type\\":\\"turn.completed\\"}", flush=True)\n'
        "print("
        '"{\\"type\\":\\"item.completed\\",\\"item\\":'
        '{\\"type\\":\\"command_execution\\",\\"exit_code\\":0}}",'
        " flush=True)\n"
        "print('PRIVATE_LATE_CANARY', file=sys.stderr)\n",
    )
    result = p1.capture(
        tmp_path / "run",
        codex=str(tmp_path / "synthetic_cli"),
        timeout=5,
        mode="late",
        post_window=3,
    )
    observations = json.loads((tmp_path / "run" / "observations.json").read_text())
    end = next(row for row in observations if row["kind"] == "cli_end")
    absent = next(row for row in observations if row["kind"] == "target_absent")
    seen = next(row for row in observations if row["kind"] == "target_seen")
    assert end["t_ns"] < absent["t_ns"] < seen["t_ns"]
    assert result["timing"] == {
        "verdict": "BELEGT",
        "order": "NACH",
        "reason": "absence_after_end_then_presence",
        "evidence": [end["event"], absent["event"], seen["event"]],
    }
    assert result["timing_evaluation"] == "KORREKT"
    assert result["evaluation"] == "KORREKT"
    assert result["target"]["target_present"] is True
    assert result["scope"] == "local_snapshot_plus_post_end_order"
    assert (
        next(row["event"] for row in observations if row["kind"] == "tool_end")
        not in (result["timing"]["evidence"])
    )
    archived = "".join(path.read_text() for path in (tmp_path / "run").iterdir())
    assert "PRIVATE_LATE_CANARY" not in archived
    assert "cli.pid" not in archived
    assert "post.observe" not in archived


def test_file_present_at_cli_end_is_not_called_late(tmp_path):
    executable(
        tmp_path / "synthetic_cli",
        "import sys\n"
        "sys.stdin.read()\n"
        "open('target', 'wb').close()\n"
        'print("{\\"type\\":\\"turn.completed\\"}", flush=True)\n'
        "print("
        '"{\\"type\\":\\"item.completed\\",\\"item\\":'
        '{\\"type\\":\\"command_execution\\",\\"exit_code\\":0}}",'
        " flush=True)\n",
    )
    result = p1.capture(
        tmp_path / "run",
        codex=str(tmp_path / "synthetic_cli"),
        timeout=5,
        mode="late",
        post_window=1,
    )
    assert result["target"]["target_present"] is True
    assert result["timing"]["verdict"] == "UNBEKANNT"
    assert result["timing"]["order"] is None
    assert result["timing_evaluation"] == "UNBEKANNT"


def test_quiet_late_window_does_not_invent_an_effect(tmp_path):
    executable(tmp_path / "synthetic_cli", "import sys\nsys.stdin.read()\n")
    result = p1.capture(
        tmp_path / "run",
        codex=str(tmp_path / "synthetic_cli"),
        timeout=5,
        mode="late",
        post_window=0.3,
    )
    assert result["agent_run"] == "UNBEKANNT"
    assert result["proven_agent_runs"] == 0
    assert result["timing"]["verdict"] == "NICHT_ANWENDBAR"
    assert result["timing"]["order"] is None
    assert result["timing_evaluation"] == "UNBEKANNT"
    assert result["evaluation"] == "UNBEKANNT"


@pytest.mark.parametrize("post_window", [0, -1, 31, float("nan")])
def test_invalid_post_window_does_not_create_run(tmp_path, post_window):
    with pytest.raises(ValueError):
        p1.capture(tmp_path / "run", mode="late", post_window=post_window)
    assert not (tmp_path / "run").exists()
