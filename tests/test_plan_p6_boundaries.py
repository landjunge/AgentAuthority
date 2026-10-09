"""P6 ingress countercontrols. Invented counters are not an agent execution."""

from __future__ import annotations

import importlib.util
import json
import os
import stat
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "p1_controlled_run.py"
spec = importlib.util.spec_from_file_location("p6_observer", SCRIPT)
assert spec is not None and spec.loader is not None
p1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p1)
CANARY = "SYNTHETIC-P6-METADATA-MARKER"


def invented_bundle():
    rows = [
        {"run": 7, "kind": kind, "value": value, "t_ns": stamp, "event": i}
        for i, (kind, value, stamp) in enumerate(
            [
                ("target_initial", False, 10),
                ("tool_end", True, 15),
                ("cli_end", True, 20),
                ("target_absent", False, 25),
                ("target_seen", True, 30),
                ("target_final", True, 40),
            ],
            1,
        )
    ]
    result = {
        "run": 7,
        "mode": "late",
        "counts": {"model_completions": 1, "tool_reports": 1, "recording_ok": True},
        "proven_agent_runs": 1,
        "agent_run": "BELEGT",
        "target": p1.infer(rows, 7),
        "timing": p1.relate(rows, 7),
        "evaluation": "KORREKT",
        "timing_evaluation": "KORREKT",
        "scope": "local_snapshot_plus_post_end_order",
    }
    reference = {
        "calls": 1,
        "target_present": True,
        "valid": True,
        "order": "NACH",
        "order_applicable": True,
        "order_valid": True,
    }
    return rows, result, reference


@pytest.mark.parametrize("evidence_class", ["forged", "stale", "missing"])
def test_invented_complete_bundle_does_not_prove_agent(evidence_class):
    rows, result, reference = invented_bundle()
    reading = p1.assess(rows, result, reference, evidence_class)
    assert reading["agent_run"] == "UNBEKANNT"
    assert reading["bindung"] != "independent_local_effect"
    assert reading["wirkung"]["geltung"] == "UNBEKANNT"
    assert reading["herkunft"]["aussage"] == "UNBEKANNT"


def test_omitted_class_does_not_promote_archive_to_current():
    reading = p1.assess(*invented_bundle())
    assert reading["evidence_class"] == "stale"
    assert reading["wirkung"]["geltung"] == "UNBEKANNT"
    assert reading["agent_run"] == "UNBEKANNT"
    # Historical row consistency and chronology are still available.
    assert reading["wirkung"]["aussage"] == "BELEGT"
    assert reading["zeitbezug"]["ordnung"] == "NACH"


@pytest.mark.parametrize("invalid_class", [{"current": CANARY}, [CANARY], None, 1, True])
def test_invalid_class_returns_bounded_unknown(invalid_class):
    reading = p1.assess(*invented_bundle(), evidence_class=invalid_class)
    assert reading["evidence_class"] == "forged"
    assert reading["agent_run"] == "UNBEKANNT"
    assert reading["wirkung"]["geltung"] == "UNBEKANNT"
    assert reading["herkunft"]["aussage"] == "UNBEKANNT"
    assert CANARY not in json.dumps(reading)


def test_local_effect_remains_usable_without_model_or_origin(tmp_path):
    measured = p1.measure_controlled_late_effect(tmp_path / "local")
    reading = p1.assess(
        measured["observations"], measured["result"], measured["reference"], "current"
    )
    target = tmp_path / "local" / "target"
    assert stat.S_ISREG(target.lstat().st_mode) and target.stat().st_size == 0
    assert reading["wirkung"]["aussage"] == "BELEGT"
    assert reading["zeitbezug"]["ordnung"] == "NACH"
    assert reading["agent_run"] == "UNBEKANNT"
    assert reading["herkunft"]["aussage"] == "UNBEKANNT"


def test_held_fd_relation_remains_useful_and_untrusted_ingress_stays_unknown(tmp_path):
    first = os.open(tmp_path / "a", os.O_CREAT | os.O_EXCL | os.O_RDWR, 0o600)
    handles = [first]
    try:
        handles.append(os.dup(first))
        handles.append(os.open(tmp_path / "b", os.O_CREAT | os.O_EXCL | os.O_RDWR, 0o600))
        before = [os.fstat(fd) for fd in handles]
        after = [os.fstat(fd) for fd in handles]
        pairs_before = [(s.st_dev, s.st_ino) for s in before]
        pairs_after = [(s.st_dev, s.st_ino) for s in after]
        assert all(stat.S_ISREG(s.st_mode) for s in before + after)
        assert pairs_before == pairs_after
        assert pairs_before[0] == pairs_before[1]
        assert pairs_before[0] != pairs_before[2]
        for index, expected in [(1, "DIESELBE"), (2, "VERSCHIEDEN")]:
            packet = {
                "A": "DIESELBE" if pairs_before[0] == pairs_before[index] else "VERSCHIEDEN",
                "C": "JA",
                "fd_set_verified": True,
                "source_authenticated": False,
            }
            # Projection only: actual fstat is above, not established by JSON.
            projected = p1.measure_local_fd_relation(first, handles[index])
            assert projected["aussage"] == expected
            assert projected["source_authenticated"] is False
            reading = p1.assess(*invented_bundle(), fd_claim=packet)
            assert reading["fd_relation"]["aussage"] == "UNBEKANNT"
            assert reading["herkunft"]["aussage"] == "UNBEKANNT"
    finally:
        for fd in handles:
            os.close(fd)


def test_explicit_current_cannot_authenticate_an_invented_bundle():
    reading = p1.assess(*invented_bundle(), evidence_class="current")
    assert reading["agent_run"] == "UNBEKANNT"
    assert reading["wirkung"]["geltung"] == "UNBEKANNT"
    assert reading["herkunft"]["aussage"] == "UNBEKANNT"
    assert reading["recht_uebernommen"] is False


def test_binder_does_not_promote_invented_counters_and_reference():
    observations, result, reference = invented_bundle()
    binding = p1.bind(result, observations, reference)
    assert binding["agent_run"] == "UNBEKANNT"
    assert binding["independent_effect"] == "UNBEKANNT"
    assert binding["reason"] != "independent_local_effect"


def test_direct_fd_packet_is_not_a_verifier_measurement():
    packet = {
        "A": "DIESELBE",
        "C": "JA",
        "fd_set_verified": True,
        "source_authenticated": False,
        "D": CANARY,
    }
    reading = p1.apply_fd_measurement(packet)
    assert reading["aussage"] == "UNBEKANNT"
    assert reading["source_authenticated"] == "UNBEKANNT"
    assert CANARY not in json.dumps(reading)


def local_collect_fixture(observer):
    """Actual harmless local tool/receipt; zero model calls, not an agent run."""

    def collect(argv, prompt, root, run, events, timeout, arm):
        sleeper = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"])
        try:
            arm.write_text(str(sleeper.pid))
            completed = subprocess.run(
                [sys.executable, str(root / "tool.py"), "late"],
                check=True,
                capture_output=True,
                timeout=5,
            )
            observer.add(events, run, "tool_end", completed.returncode == 0)
        finally:
            sleeper.kill()
            sleeper.wait(timeout=5)
        observer.add(events, run, "cli_end", True)
        return {"model_completions": 0, "tool_reports": 1, "recording_ok": True}

    return collect


def test_live_capture_context_expires_and_rejects_changed_inputs(tmp_path, monkeypatch):
    monkeypatch.setattr(p1, "collect", local_collect_fixture(p1))
    kept = []

    def consume(rows, result, reference, context):
        kept.extend([rows, result, reference, context])
        current = p1.assess(rows, result, reference, "current", capture_context=context)
        assert current["wirkung"]["geltung"] == "lokaler_abfragepunkt"
        assert current["agent_run"] == "UNBEKANNT"  # zero actual model calls
        assert current["herkunft"]["aussage"] == "UNBEKANNT"
        assert (
            p1.bind(result, rows, reference, capture_context=context)["independent_effect"]
            == "KORREKT"
        )
        changed = {
            **result,
            "agent_run": "BELEGT",
            "proven_agent_runs": 1,
            "counts": {**result["counts"], "model_completions": 1},
        }
        forged = p1.assess(rows, changed, reference, "current", capture_context=context)
        assert forged["agent_run"] == "UNBEKANNT"
        assert forged["wirkung"]["geltung"] == "UNBEKANNT"
        assert (
            p1.assess(*invented_bundle(), "current", capture_context=context)["agent_run"]
            == "UNBEKANNT"
        )
        assert (
            p1.assess(rows, result, reference, "stale", capture_context=context)["wirkung"][
                "geltung"
            ]
            == "UNBEKANNT"
        )

    p1.capture(tmp_path / "capture", mode="late", on_capture=consume)
    rows, result, reference, context = kept
    expired = p1.assess(rows, result, reference, "current", capture_context=context)
    assert expired["wirkung"]["geltung"] == "UNBEKANNT"
    assert expired["agent_run"] == "UNBEKANNT"
    for path in (tmp_path / "capture").glob("*.json"):
        data = path.read_text()
        assert "capture_context" not in data and "receipt.jsonl" not in data
        assert str(tmp_path) not in data and CANARY not in data
    assert not p1._CAPTURE_CONTEXTS


def test_capture_context_is_revoked_on_consumer_error(tmp_path, monkeypatch):
    monkeypatch.setattr(p1, "collect", local_collect_fixture(p1))

    def fail(*args):
        raise RuntimeError("synthetic consumer error")

    with pytest.raises(RuntimeError, match="synthetic consumer"):
        p1.capture(tmp_path / "capture", mode="late", on_capture=fail)
    assert not p1._CAPTURE_CONTEXTS


def test_connect_consumes_real_measurement_before_context_expiry(tmp_path, monkeypatch):
    monkeypatch.setattr(p1, "collect", local_collect_fixture(p1))
    points = []

    def consume(rows, result, reference, context):
        points.append(p1.assess(rows, result, reference, "current", capture_context=context))

    bound = p1.connect(tmp_path / "connect", on_capture=consume)
    assert len(points) == 1
    assert points[0]["wirkung"]["geltung"] == "lokaler_abfragepunkt"
    assert bound["agent_run"] == "UNBEKANNT"
    assert bound["independent_effect"] == "KORREKT"
    assert bound["timing_evaluation"] == "KORREKT"
    assert not p1._CAPTURE_CONTEXTS


def test_fd_context_expires_and_projection_json_cannot_reissue_it(tmp_path, monkeypatch):
    original = p1.apply_fd_measurement
    seen = []

    def observe(context):
        seen.append(context)
        return original(context)

    monkeypatch.setattr(p1, "apply_fd_measurement", observe)
    with (tmp_path / "file").open("xb") as stream:
        measured = p1.measure_local_fd_relation(stream.fileno(), stream.fileno())
    assert measured["aussage"] == "DIESELBE"
    assert original(seen[0])["aussage"] == "UNBEKANNT"
    assert original(measured)["aussage"] == "UNBEKANNT"
    assert not p1._FD_MEASUREMENTS


@pytest.mark.parametrize("bad_fd", [True, -1, None, {}, 2**100])
def test_invalid_fd_does_not_produce_a_positive_or_leak_raw_input(bad_fd):
    reading = p1.measure_local_fd_relation(bad_fd, bad_fd)
    assert reading["aussage"] == "UNBEKANNT"
    assert reading["source_authenticated"] == "UNBEKANNT"


def test_fd_measurement_rejects_closed_or_non_regular_descriptors(tmp_path):
    with (tmp_path / "file").open("xb") as stream:
        descriptor = stream.fileno()
    assert p1.measure_local_fd_relation(descriptor, descriptor)["aussage"] == "UNBEKANNT"
    read, write = os.pipe()
    try:
        assert p1.measure_local_fd_relation(read, write)["aussage"] == "UNBEKANNT"
    finally:
        os.close(read)
        os.close(write)


def test_capture_context_does_not_survive_fork(tmp_path, monkeypatch):
    monkeypatch.setattr(p1, "collect", local_collect_fixture(p1))

    def consume(rows, result, reference, context):
        read, write = os.pipe()
        child = os.fork()
        if child == 0:
            os.close(read)
            try:
                reading = p1.assess(rows, result, reference, "current", capture_context=context)
                os.write(write, b"1" if reading["wirkung"]["geltung"] == "UNBEKANNT" else b"0")
            finally:
                os._exit(0)
        os.close(write)
        try:
            assert os.read(read, 1) == b"1"
        finally:
            os.close(read)
            os.waitpid(child, 0)

    p1.capture(tmp_path / "capture", mode="late", on_capture=consume)


def test_consumer_cannot_change_measured_bundle_and_keep_capability(tmp_path, monkeypatch):
    monkeypatch.setattr(p1, "collect", local_collect_fixture(p1))

    def change(rows, result, reference, context):
        result["counts"]["model_completions"] = 1

    with pytest.raises(ValueError, match="changed measured evidence"):
        p1.capture(tmp_path / "capture", mode="late", on_capture=change)
    assert not p1._CAPTURE_CONTEXTS


def load_p5():
    spec = importlib.util.spec_from_file_location("p6_p5", SCRIPT.with_name("p5_reliability.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_live_protocol_fixture_preserves_binding_but_replay_cannot(tmp_path):
    # Adapter-protocol fixture only. It launches local processes, not a model.
    # BELEGT assertions below test the live branch and are not P6 agent evidence.
    p5 = load_p5()
    cli = tmp_path / "synthetic_cli"
    cli.write_text(
        "#!" + sys.executable + "\n"
        "import json, subprocess, sys\n"
        "sys.stdin.read()\n"
        "subprocess.run([sys.executable, 'tool.py', 'late'], check=True)\n"
        "print(json.dumps({'type':'turn.completed'}), flush=True)\n"
        "print(json.dumps({'type':'item.completed', 'item':"
        "{'type':'command_execution','exit_code':0}}), flush=True)\n"
    )
    cli.chmod(0o700)
    retained = []

    def consume(rows, result, reference, context):
        retained.extend([rows, result, reference, context])
        scored = p5.score(rows, result, reference, capture_context=context)
        assert scored["evaluator_contract"] == "p6_live_acquisition"
        assert scored["expectation_role"] == "historical_p5_reference"
        assert scored["agent_run"] == "BELEGT"
        assert scored["package"] == "PASS"

    bound = p5.p1.connect(
        tmp_path / "capture", codex=str(cli), timeout=5, post_window=3, on_capture=consume
    )
    assert bound["reason"] == "independent_local_effect"
    rows, result, reference, context = retained
    assert p5.score(rows, result, reference)["package"] == "STOP"
    assert p5.score(rows, result, reference, capture_context=context)["agent_run"] == "UNBEKANNT"


def test_existing_run_score_cannot_be_overwritten(tmp_path, monkeypatch):
    import hashlib

    p5 = load_p5()
    lock = tmp_path / "expectation-lock"
    lock.write_text(hashlib.sha256(p5.EXPECTATION.read_bytes()).hexdigest())
    monkeypatch.setattr(p5, "EXPECTATION_SHA", lock)
    folder = tmp_path / "existing"
    folder.mkdir()
    score = folder / "reliability.json"
    score.write_text('{"historical":true}\n')
    before = score.read_bytes()
    record = p5.run_once(folder)
    assert record["package"] == "STOP"
    assert record["stop_reason"] == "FileExistsError"
    assert score.read_bytes() == before


@pytest.mark.parametrize("tampered", [1, float("nan"), float("inf")])
def test_corrupted_archive_digest_returns_bounded_stop(tmp_path, monkeypatch, tampered):
    import hashlib

    p5 = load_p5()
    lock = tmp_path / "expectation-lock"
    lock.write_text(hashlib.sha256(p5.EXPECTATION.read_bytes()).hexdigest())
    monkeypatch.setattr(p5, "EXPECTATION_SHA", lock)

    def fake_connect(folder, *, on_capture, **kwargs):
        # Evaluator error-path fixture only: no acquisition or agent proof.
        on_capture([], {}, {}, object())
        folder.mkdir()
        for name, data in (
            ("observations", []),
            ("result", {"tampered": tampered}),
            ("reference", {}),
            ("binding", {}),
        ):
            p5.p1.save(folder / (name + ".json"), data)
        return {}

    monkeypatch.setattr(p5.p1, "connect", fake_connect)
    output = tmp_path / "capture"
    record = p5.run_once(output)
    assert record["package"] == "STOP"
    assert record["stop_reason"] == "archive_disagrees_with_capture"
    assert record["agent_run"] == "UNBEKANNT"
    assert json.loads((output / "reliability.json").read_text()) == record
