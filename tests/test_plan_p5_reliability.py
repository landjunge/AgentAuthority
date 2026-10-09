"""P5 scores reliability of the existing observer. No test starts Codex."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "p1_controlled_run.py"
P5_SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "p5_reliability.py"
ROOT = SCRIPT.parents[1]
spec = importlib.util.spec_from_file_location("p1_controlled_run", SCRIPT)
assert spec is not None and spec.loader is not None
p1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p1)
p5_spec = importlib.util.spec_from_file_location("p5_reliability", P5_SCRIPT)
assert p5_spec is not None and p5_spec.loader is not None
p5 = importlib.util.module_from_spec(p5_spec)
p5_spec.loader.exec_module(p5)

CANARY = "P5-CANARY-NOT-A-SECRET"
PROMPT = "Run exactly this supplied"
FIELDS = {"run", "kind", "value", "t_ns", "event"}
EXPECTATION = ROOT / "docs" / "P5-ERWARTUNG-VOR-LAUF.md"
P5_RUN = ROOT / "docs" / "p1-runs" / "2026-10-09-p5-reliability"
ARCHIVE_SHA256 = {
    "2026-10-09-attempt-03/analysis.json": "5d128352cbaf991a75df8ece64eec8ccb5665689c7449223c36f0d6f0b172026",
    "2026-10-09-attempt-03/observations.json": "b25f07ac12dae176bbefd5c50698eb7da64eac0be24ffff6ce1457c4903d30ec",
    "2026-10-09-attempt-03/reference.json": "786a0e2f492d85934ae8b58884a1bb23b8d337b4234d4c1a4934b7908837af1c",
    "2026-10-09-attempt-03/result.json": "796318343769a49a6cf47584a31e5ab50f3d1e86e04d2bc837349f60796ca3e8",
    "2026-10-09-attempt-04/analysis.json": "f229c4d192c782866c2b257264a9e5a805dde109ad7fca5b95c995e3464cfcd9",
    "2026-10-09-attempt-04/observations.json": "910c6ac2100b5f17657db7b0eb01f95549e4d6c576354917e3a3b9efd915f6e9",
    "2026-10-09-attempt-04/reference.json": "24a90a55702e67b0131fba7775471e34c44a2f712191da75d4388d04be5f6cb6",
    "2026-10-09-attempt-04/result.json": "81ba1611ba37baf1ab4419e0b08a456643063ba68ee7e6bbf9707dc8882ad2af",
    "2026-10-09-p2-local/analysis.json": "f229c4d192c782866c2b257264a9e5a805dde109ad7fca5b95c995e3464cfcd9",
    "2026-10-09-p2-local/binding.json": "845a72645e174b6e7555084f62acdfbd71748ff594db146c8b7fcb97843a2b74",
    "2026-10-09-p2-local/observations.json": "0f49f878f5af6a78ac22ed51f950e15f2480cfd650b3f7f96ba1db35e35e0a4d",
    "2026-10-09-p2-local/reference.json": "24a90a55702e67b0131fba7775471e34c44a2f712191da75d4388d04be5f6cb6",
    "2026-10-09-p2-local/result.json": "932ecf6fc554ef3c8b14d20d7b1d490321de2783589129cd77b72df39d26d99a",
    "2026-10-09-p3-controlled/assess.json": "2db8600a77f408d2bc75bd35efeb36534115dde48f6e540cd9a441012691d425",
    "2026-10-09-p3-controlled/fd-platform.json": "22371b4133995f4c1da8dd64b8faba58a996149c128be17b8a29c2b41ddd34d5",
    "2026-10-09-p3-controlled/observations.json": "ef063a8295202e3d5c864938e38e8a195ddc4bd32339249ed4978a6e08d7f356",
    "2026-10-09-p3-controlled/reference.json": "24a90a55702e67b0131fba7775471e34c44a2f712191da75d4388d04be5f6cb6",
    "2026-10-09-p3-controlled/result.json": "b1b31fc3086ea3cf760a0b7cbc3c1a482ae192c9648722fb19ac5adeb9910eac",
}


def bundle(run: int = 7) -> tuple[list[dict], dict, dict]:
    observations = [
        {"run": run, "kind": "target_initial", "value": False, "t_ns": 10, "event": 1},
        {"run": run, "kind": "tool_end", "value": True, "t_ns": 15, "event": 2},
        {"run": run, "kind": "cli_end", "value": True, "t_ns": 20, "event": 3},
        {"run": run, "kind": "target_absent", "value": False, "t_ns": 25, "event": 4},
        {"run": run, "kind": "target_seen", "value": True, "t_ns": 30, "event": 5},
        {"run": run, "kind": "target_final", "value": True, "t_ns": 40, "event": 6},
    ]
    result = {
        "run": run,
        "mode": "late",
        "counts": {
            "model_completions": 1,
            "tool_reports": 1,
            "recording_ok": True,
            "cli_success": True,
        },
        "proven_agent_runs": 1,
        "agent_run": "BELEGT",
        "target": p1.infer(observations, run),
        "evaluation": "KORREKT",
        "scope": "local_snapshot_plus_post_end_order",
        "timing": p1.relate(observations, run),
        "timing_evaluation": "KORREKT",
    }
    reference = {
        "calls": 1,
        "target_present": True,
        "valid": True,
        "order": "NACH",
        "order_applicable": True,
        "order_valid": True,
    }
    return observations, result, reference


def test_synthetic_late_bundle_matches_current_missing_stale_and_forged():
    observations, result, reference = bundle()
    frozen = json.dumps(observations)
    scored = p5.score(observations, result, reference)
    dumped = json.dumps(scored)
    assert CANARY not in dumped
    assert PROMPT not in dumped
    assert json.dumps(observations) == frozen
    rows = {row["fall"]: row for row in scored["rows"]}
    assert tuple(rows) == p5.CASES
    aktuell = rows["aktuell"]["ist"]
    assert rows["aktuell"]["status"] == "FAIL"
    assert aktuell["wirkung"] == "BELEGT"
    assert aktuell["target_present"] is True
    assert aktuell["geltung"] == "UNBEKANNT"
    assert aktuell["wirkungsgrund"] == "local_snapshot_only"
    assert aktuell["zeitbezug"] == "BELEGT"
    assert aktuell["ordnung"] == "NACH"
    assert aktuell["zeitgrund"] == "absence_after_end_then_presence"
    assert aktuell["ende"] == "NEIN"
    assert aktuell["ende_grund"] == "end_is_an_event"
    assert aktuell["identitaet"] == "UNBEKANNT"
    assert aktuell["identitaetsgrund"] == "no_identity_measurement"
    assert aktuell["herkunft"] == "UNBEKANNT"
    assert aktuell["herkunftsgrund"] == "no_source_field"
    assert aktuell["agent_run"] == "UNBEKANNT"
    assert aktuell["bindung"] == "agent_run_unbekannt"
    assert aktuell["recht_uebernommen"] is False
    assert aktuell["fehler"] == []
    assert aktuell["calls"] == 1
    assert aktuell["reference_valid"] is True
    assert aktuell["reference_target_present"] is True
    assert aktuell["reference_order"] == "NACH"
    assert aktuell["order_valid"] is True
    assert aktuell["order_applicable"] is True
    assert aktuell["evaluation"] == "KORREKT"
    assert aktuell["timing_evaluation"] == "KORREKT"
    assert rows["fehlend"]["status"] == "PASS"
    assert rows["fehlend"]["ist"]["wirkung"] == "UNBEKANNT"
    assert rows["fehlend"]["ist"]["zeitbezug"] == "UNBEKANNT"
    assert rows["fehlend"]["ist"]["zeitgrund_ist_no_effect"] is False
    assert rows["fehlend"]["ist"]["agent_run"] == "UNBEKANNT"
    assert rows["alt_geordnet"]["status"] == "PASS"
    assert rows["alt_geordnet"]["ist"]["wirkung"] == "BELEGT"
    assert rows["alt_geordnet"]["ist"]["geltung"] == "UNBEKANNT"
    assert rows["alt_geordnet"]["ist"]["identitaetsgrund"] == "stale_source"
    assert rows["alt_zusatzfelder"]["status"] == "PASS"
    assert rows["alt_zusatzfelder"]["ist"]["wirkungsgrund"] == "invalid_evidence"
    assert rows["alt_zusatzfelder"]["ist"]["name_im_json"] is False
    assert rows["gefaelscht_agentenlabel"]["status"] == "PASS"
    assert rows["gefaelscht_agentenlabel"]["ist"]["agent_run"] == "UNBEKANNT"
    assert rows["gefaelscht_agentenlabel"]["ist"]["identitaetsgrund"] == "forged_source"
    assert rows["gefaelscht_agentenlabel"]["ist"]["recht_uebernommen"] is False
    assert rows["gefaelscht_fd_flag"]["status"] == "PASS"
    assert rows["gefaelscht_fd_flag"]["ist"]["grund"] == "forged_authentication"
    assert rows["gefaelscht_fd_flag"]["ist"]["als_wahr_uebernommen"] is False
    assert rows["packet_ohne_messung"]["status"] == "PASS"
    assert rows["packet_ohne_messung"]["ist"]["grund"] == "unmeasured_packet_not_identity"
    assert rows["fd_format_keine_hostmessung"]["status"] == "PASS"
    assert rows["fd_format_keine_hostmessung"]["ist"]["aussage"] == "UNBEKANNT"
    assert rows["fd_format_keine_hostmessung"]["ist"]["source_authenticated"] == "UNBEKANNT"
    assert rows["fd_format_keine_hostmessung"]["ist"]["ist_hostmessung"] is False
    assert rows["host_verifier"]["status"] == "SKIP"
    assert scored["package"] == "STOP"
    assert scored["agent_run"] == "UNBEKANNT"
    assert scored["step"] == "P5"


def test_stored_belegt_without_model_completion_stays_unknown():
    observations, result, reference = bundle()
    result["counts"]["model_completions"] = 0
    result["agent_run"] = "BELEGT"
    result["proven_agent_runs"] = 1
    scored = p5.score(observations, result, reference)
    assert scored["agent_run"] == "UNBEKANNT"
    assert scored["package"] != "PASS"
    assert CANARY not in json.dumps(scored)
    assert "Run exactly this supplied" not in json.dumps(scored)


def test_expectation_records_limits_and_not_the_new_archive_sha():
    text = EXPECTATION.read_text(encoding="utf-8")
    for mark in (
        "RC-01",
        "RC-02",
        "RC-03",
        "RC-04",
        "RC-05",
        "OOS-021",
        "CB-01",
        "P4-Pytest-Cache",
        "Keine allgemeine Agentensicherheit",
        "kein Remote-Stopp",
        "keine Quellenauthentisierung",
        "measure_controlled_late_effect",
        "independent_local_effect",
        "forged_authentication",
        "unmeasured_packet_not_identity",
        "stale_source",
    ):
        assert mark in text
    assert PROMPT not in text
    assert "2026-10-09-p5-reliability" not in text
    digest = hashlib.sha256(EXPECTATION.read_bytes()).hexdigest()
    local_lock = Path("/tmp/aa-p5-expectation-before.txt")
    if local_lock.is_file():
        assert local_lock.read_text(encoding="utf-8").strip() == digest
    if P5_RUN.exists():
        stored = json.loads((P5_RUN / "reliability.json").read_text(encoding="utf-8"))
        assert stored["expectation_sha256"] == digest
        result = json.loads((P5_RUN / "result.json").read_text(encoding="utf-8"))
        assert str(result["run"]) not in text
        for path in P5_RUN.iterdir():
            if path.is_file():
                assert hashlib.sha256(path.read_bytes()).hexdigest() not in text


def test_p5_archive_rows_match_score_without_prompt_or_extra_fields():
    if not P5_RUN.is_dir():
        pytest.skip("P5-Archiv fehlt")
    observations = json.loads((P5_RUN / "observations.json").read_text(encoding="utf-8"))
    reference = json.loads((P5_RUN / "reference.json").read_text(encoding="utf-8"))
    result = json.loads((P5_RUN / "result.json").read_text(encoding="utf-8"))
    stored = json.loads((P5_RUN / "reliability.json").read_text(encoding="utf-8"))
    scored = p5.score(observations, result, reference)
    assert scored["rows"][0]["status"] == "FAIL"
    assert stored["rows"][0]["status"] == "PASS"  # untouched historical result
    assert [row["status"] for row in scored["rows"][1:]] == [
        row["status"] for row in stored["rows"][1:]
    ]
    assert scored["agent_run"] == "UNBEKANNT"
    assert scored["package"] == "STOP"
    assert [row["fall"] for row in scored["rows"]] == [row["fall"] for row in stored["rows"]]
    for event in observations:
        assert set(event) == FIELDS
    for path in P5_RUN.iterdir():
        if path.is_file():
            blob = path.read_bytes()
            assert PROMPT.encode() not in blob
            assert CANARY.encode() not in blob
    if stored["agent_run"] != "BELEGT":
        assert stored["package"] != "PASS"
    if scored["agent_run"] != "BELEGT":
        assert scored["package"] != "PASS"


def test_older_archives_stay_byte_identical():
    root = ROOT / "docs" / "p1-runs"
    for name, digest in ARCHIVE_SHA256.items():
        path = root / name
        assert hashlib.sha256(path.read_bytes()).hexdigest() == digest
