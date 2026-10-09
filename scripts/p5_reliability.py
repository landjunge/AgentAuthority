"""Score one live local capture; archive replay cannot supply acquisition.

`run_once` calls `connect` once. It does not invent events and it does not steer.
"""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import tempfile
from pathlib import Path

_SCRIPT = Path(__file__).resolve().parent / "p1_controlled_run.py"
_spec = importlib.util.spec_from_file_location("p5_loaded_p1_controlled_run", _SCRIPT)
assert _spec is not None and _spec.loader is not None
p1 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(p1)

ROOT = _SCRIPT.parents[1]
EXPECTATION = ROOT / "docs" / "P5-ERWARTUNG-VOR-LAUF.md"
EXPECTATION_SHA = Path("/tmp/aa-p5-expectation-before.txt")
WORKSPACE_PATH = Path("/tmp/aa-p5-workspace-path.txt")
CANARY = "P5-CANARY-NOT-A-SECRET"
PROMPT_MARK = "Run exactly this supplied"
CASES = (
    "aktuell",
    "fehlend",
    "alt_geordnet",
    "alt_zusatzfelder",
    "gefaelscht_agentenlabel",
    "gefaelscht_fd_flag",
    "packet_ohne_messung",
    "fd_format_keine_hostmessung",
    "host_verifier",
)
REQUIRED = CASES[:-1]
GRENZEN = {
    "RC-01": "offen",
    "RC-02": "offen",
    "RC-03": "offen",
    "RC-04": "offen",
    "RC-05": "offen",
    "OOS-021": "offen",
    "CB-01": "offen",
    "P4-Pytest-Cache": "offen",
}
_AKTUAL = {
    "wirkung": "BELEGT",
    "target_present": True,
    "geltung": "lokaler_abfragepunkt",
    "wirkungsgrund": "local_snapshot_only",
    "zeitbezug": "BELEGT",
    "ordnung": "NACH",
    "zeitgrund": "absence_after_end_then_presence",
    "ende": "NEIN",
    "ende_grund": "end_is_an_event",
    "identitaet": "UNBEKANNT",
    "identitaetsgrund": "no_identity_measurement",
    "herkunft": "UNBEKANNT",
    "herkunftsgrund": "no_source_field",
    "agent_run": "BELEGT",
    "bindung": "independent_local_effect",
    "recht_uebernommen": False,
    "fehler": [],
    "reference_valid": True,
    "calls": 1,
    "reference_target_present": True,
    "reference_order": "NACH",
    "order_valid": True,
    "order_applicable": True,
    "evaluation": "KORREKT",
    "timing_evaluation": "KORREKT",
}
_FEHLEND = {
    "wirkung": "UNBEKANNT",
    "zeitbezug": "UNBEKANNT",
    "zeitgrund_ist_no_effect": False,
    "ende": "NEIN",
    "identitaet": "UNBEKANNT",
    "identitaetsgrund": "missing_evidence",
    "herkunft": "UNBEKANNT",
    "agent_run": "UNBEKANNT",
    "authentisierte_herkunft": False,
}
_ALT = {
    "wirkung": "BELEGT",
    "geltung": "UNBEKANNT",
    "identitaet": "UNBEKANNT",
    "identitaetsgrund": "stale_source",
    "herkunft": "UNBEKANNT",
}
_ALT_EXTRA = {
    "wirkungsgrund": "invalid_evidence",
    "geltung": "UNBEKANNT",
    "identitaet": "UNBEKANNT",
    "identitaetsgrund": "stale_source",
    "name_im_json": False,
}
_FORGED = {
    "agent_run": "UNBEKANNT",
    "identitaet": "UNBEKANNT",
    "identitaetsgrund": "forged_source",
    "herkunft": "UNBEKANNT",
    "recht_uebernommen": False,
}
_FD_FLAG = {
    "aussage": "UNBEKANNT",
    "grund": "forged_authentication",
    "source_authenticated": "UNBEKANNT",
    "als_wahr_uebernommen": False,
}
_PACKET = {
    "aussage": "UNBEKANNT",
    "grund": "unmeasured_packet_not_identity",
    "source_authenticated": "UNBEKANNT",
    "name_im_json": False,
}
_FD_FORMAT = {
    "aussage": "UNBEKANNT",
    "source_authenticated": "UNBEKANNT",
    "recht_uebernommen": False,
    "grund": "unmeasured_packet_not_identity",
    "verschieden": "UNBEKANNT",
    "ist_hostmessung": False,
    "ist_herkunft": False,
    "name_im_json": False,
}


def _token(value: object, fallback: str) -> str:
    if type(value) is not str or not value or len(value) > 80:
        return fallback
    if any(mark in value for mark in ("/", "\\", CANARY, PROMPT_MARK)):
        return fallback
    return value


def _leaked(value: object) -> bool:
    try:
        dumped = json.dumps(value)
    except TypeError:
        return True
    return CANARY in dumped or PROMPT_MARK in dumped


def _judge(fall: str, erwartet: dict, ist: dict, pass_grund: str) -> dict:
    if ist == erwartet:
        status = "PASS"
        grund = pass_grund
    else:
        status = "FAIL"
        differ = [key for key in erwartet if ist.get(key) != erwartet[key]]
        extra = [key for key in ist if key not in erwartet]
        grund = ",".join([*differ, *extra]) or "abweichung"
    return {"fall": fall, "status": status, "erwartet": erwartet, "ist": ist, "grund": grund}


def _blocked(fall: str, erwartet: dict, pass_grund: str) -> dict:
    return _judge(fall, erwartet, {"bewertet": False}, pass_grund)


def _run_of(result: object) -> int | None:
    if not isinstance(result, dict):
        return None
    run = result.get("run")
    if type(run) is int and run >= 1:
        return run
    return None


def _only_cli_end(observations: object, result: object) -> dict | None:
    """Return the single real cli_end row. Do not synthesize one."""
    run = _run_of(result)
    if run is None or not isinstance(observations, list):
        return None
    found: list[dict] = []
    for event in observations:
        if isinstance(event, dict) and event.get("kind") == "cli_end" and event.get("run") == run:
            found.append(event)
    if len(found) != 1:
        return None
    return copy.deepcopy(found[0])


def _copy_rows(observations: object) -> list[dict] | None:
    if not isinstance(observations, list) or not observations:
        return None
    if not all(isinstance(event, dict) for event in observations):
        return None
    return copy.deepcopy(observations)


def _forged_result(result: object) -> dict | None:
    if not isinstance(result, dict):
        return None
    forged = copy.deepcopy(result)
    counts = forged.get("counts")
    if not isinstance(counts, dict):
        return None
    counts["model_completions"] = 0
    forged["agent_run"] = "BELEGT"
    forged["proven_agent_runs"] = 1
    return forged


def _case_aktuell(
    observations: object, result: object, reference: object, capture_context: object = None
) -> dict:
    reading = p1.assess(observations, result, reference, "current", capture_context=capture_context)
    ref = reference if isinstance(reference, dict) else {}
    res = result if isinstance(result, dict) else {}
    ist = {
        "wirkung": reading["wirkung"]["aussage"],
        "target_present": reading["wirkung"].get("target_present"),
        "geltung": reading["wirkung"].get("geltung"),
        "wirkungsgrund": reading["wirkung"].get("grund"),
        "zeitbezug": reading["zeitbezug"]["aussage"],
        "ordnung": reading["zeitbezug"].get("ordnung"),
        "zeitgrund": reading["zeitbezug"].get("grund"),
        "ende": reading["ende_ist_wirkungsfreiheit"]["aussage"],
        "ende_grund": reading["ende_ist_wirkungsfreiheit"]["grund"],
        "identitaet": reading["identitaet"]["aussage"],
        "identitaetsgrund": reading["identitaet"]["grund"],
        "herkunft": reading["herkunft"]["aussage"],
        "herkunftsgrund": reading["herkunft"]["grund"],
        "agent_run": reading["agent_run"],
        "bindung": reading["bindung"],
        "recht_uebernommen": reading["recht_uebernommen"],
        "fehler": reading["fehler"],
        "reference_valid": ref.get("valid"),
        "calls": ref.get("calls"),
        "reference_target_present": ref.get("target_present"),
        "reference_order": ref.get("order"),
        "order_valid": ref.get("order_valid"),
        "order_applicable": ref.get("order_applicable"),
        "evaluation": res.get("evaluation"),
        "timing_evaluation": res.get("timing_evaluation"),
    }
    return _judge("aktuell", _AKTUAL, ist, "local_snapshot_only")


def _case_fehlend(observations: object, result: object) -> dict:
    line = _only_cli_end(observations, result)
    if line is None or not isinstance(result, dict):
        return _blocked("fehlend", _FEHLEND, "missing_evidence")
    reading = p1.assess([line], result, {}, "missing")
    fd = reading["fd_relation"]
    ist = {
        "wirkung": reading["wirkung"]["aussage"],
        "zeitbezug": reading["zeitbezug"]["aussage"],
        "zeitgrund_ist_no_effect": reading["zeitbezug"].get("grund") == "no_effect",
        "ende": reading["ende_ist_wirkungsfreiheit"]["aussage"],
        "identitaet": reading["identitaet"]["aussage"],
        "identitaetsgrund": reading["identitaet"]["grund"],
        "herkunft": reading["herkunft"]["aussage"],
        "agent_run": reading["agent_run"],
        "authentisierte_herkunft": fd.get("source_authenticated") is True
        or reading["herkunft"]["aussage"] not in {"UNBEKANNT"},
    }
    return _judge("fehlend", _FEHLEND, ist, "missing_evidence")


def _case_alt(observations: object, result: object, reference: object) -> dict:
    rows = _copy_rows(observations)
    if rows is None:
        return _blocked("alt_geordnet", _ALT, "stale_source")
    reading = p1.assess(rows, result, reference, "stale")
    ist = {
        "wirkung": reading["wirkung"]["aussage"],
        "geltung": reading["wirkung"].get("geltung"),
        "identitaet": reading["identitaet"]["aussage"],
        "identitaetsgrund": reading["identitaet"]["grund"],
        "herkunft": reading["herkunft"]["aussage"],
    }
    return _judge("alt_geordnet", _ALT, ist, "stale_source")


def _case_alt_extra(observations: object, result: object, reference: object) -> dict:
    rows = _copy_rows(observations)
    if rows is None:
        return _blocked("alt_zusatzfelder", _ALT_EXTRA, "invalid_evidence")
    rows[-1] = {**rows[-1], "live": True, "released": True, "identity": CANARY}
    reading = p1.assess(rows, result, reference, "stale")
    leaked = _leaked(reading)
    ist = {
        "wirkungsgrund": reading["wirkung"].get("grund"),
        "geltung": reading["wirkung"].get("geltung"),
        "identitaet": reading["identitaet"]["aussage"],
        "identitaetsgrund": reading["identitaet"]["grund"],
        "name_im_json": leaked,
    }
    return _judge("alt_zusatzfelder", _ALT_EXTRA, ist, "invalid_evidence")


def _case_forged_label(observations: object, result: object, reference: object) -> dict:
    forged = _forged_result(result)
    if forged is None:
        return _blocked("gefaelscht_agentenlabel", _FORGED, "forged_source")
    reading = p1.assess(observations, forged, reference, "forged")
    ist = {
        "agent_run": reading["agent_run"],
        "identitaet": reading["identitaet"]["aussage"],
        "identitaetsgrund": reading["identitaet"]["grund"],
        "herkunft": reading["herkunft"]["aussage"],
        "recht_uebernommen": reading["recht_uebernommen"],
    }
    return _judge("gefaelscht_agentenlabel", _FORGED, ist, "forged_source")


def _fd_ist(reading: dict) -> dict:
    fd = reading["fd_relation"]
    return {
        "aussage": fd.get("aussage"),
        "grund": fd.get("grund"),
        "source_authenticated": fd.get("source_authenticated"),
        "als_wahr_uebernommen": fd.get("source_authenticated") is True,
    }


def _case_fd_flag(observations: object, result: object, reference: object) -> dict:
    claim = {"A": "DIESELBE", "source_authenticated": True, "identity": CANARY}
    reading = p1.assess(observations, result, reference, "forged", fd_claim=claim)
    if _leaked(reading):
        return _judge(
            "gefaelscht_fd_flag",
            _FD_FLAG,
            {"name_im_json": True},
            "forged_authentication",
        )
    return _judge("gefaelscht_fd_flag", _FD_FLAG, _fd_ist(reading), "forged_authentication")


def _case_packet(observations: object, result: object, reference: object) -> dict:
    claim = {
        "A": "DIESELBE",
        "B": CANARY,
        "C": "JA",
        "fd_set_verified": True,
        "source_authenticated": False,
        "positive_identity_authorized": True,
        "identity": CANARY,
    }
    reading = p1.assess(observations, result, reference, "forged", fd_claim=claim)
    leaked = _leaked(reading)
    fd = reading["fd_relation"]
    ist = {
        "aussage": fd.get("aussage"),
        "grund": fd.get("grund"),
        "source_authenticated": fd.get("source_authenticated"),
        "name_im_json": leaked,
    }
    return _judge("packet_ohne_messung", _PACKET, ist, "unmeasured_packet_not_identity")


def _case_fd_format() -> dict:
    measured = {
        "A": "DIESELBE",
        "B": CANARY,
        "C": "JA",
        "D": CANARY,
        "fd_set_verified": True,
        "source_authenticated": False,
        "positive_identity_authorized": True,
    }
    kept = p1.apply_fd_measurement(measured)
    different = p1.apply_fd_measurement({**measured, "A": "VERSCHIEDEN"})
    leaked = _leaked(kept) or _leaked(different)
    ist = {
        "aussage": kept.get("aussage"),
        "source_authenticated": kept.get("source_authenticated"),
        "recht_uebernommen": kept.get("recht_uebernommen"),
        "grund": kept.get("grund"),
        "verschieden": different.get("aussage"),
        "ist_hostmessung": False,
        "ist_herkunft": kept.get("source_authenticated") is True
        or kept.get("recht_uebernommen") is True,
        "name_im_json": leaked,
    }
    return _judge("fd_format_keine_hostmessung", _FD_FORMAT, ist, "local_relation_not_origin")


def _verifier_defined() -> bool:
    needle = "def " + "verify_current_fd_identity"
    for path in ROOT.rglob("*.py"):
        if path.name == "p5_reliability.py" or "__pycache__" in path.parts:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            continue
        if needle in text:
            return True
    return False


def _case_host() -> dict:
    # Absence is not a measured FD relation and not a checked foreign SHA.
    if _verifier_defined():
        return {
            "fall": "host_verifier",
            "status": "FAIL",
            "erwartet": {"status": "SKIP"},
            "ist": {"status": "FAIL"},
            "grund": "datei_vorhanden",
        }
    return {
        "fall": "host_verifier",
        "status": "SKIP",
        "erwartet": {"status": "SKIP"},
        "ist": {"status": "SKIP"},
        "grund": "datei_nicht_in_diesem_checkout",
    }


def _expectation_sha() -> str | None:
    try:
        return hashlib.sha256(EXPECTATION.read_bytes()).hexdigest()
    except OSError:
        return None


def _package(agent_run: object, bindung: object, rows: list[dict]) -> tuple[str, str | None]:
    status = {row["fall"]: row["status"] for row in rows}
    if agent_run != "BELEGT" or bindung != "independent_local_effect":
        reason = bindung if bindung != "independent_local_effect" else "agent_run_unbekannt"
        return "STOP", _token(reason, "agent_run_unbekannt")
    for name in REQUIRED:
        if status.get(name) != "PASS":
            return "STOP", name
    if status.get("host_verifier") != "SKIP":
        return "STOP", "host_verifier"
    return "PASS", None


def score(
    observations: object, result: object, reference: object, *, capture_context: object = None
) -> dict:
    """Score within acquisition; replay cannot manufacture a live context."""
    current = p1.assess(observations, result, reference, "current", capture_context=capture_context)
    rows = [
        _case_aktuell(observations, result, reference, capture_context),
        _case_fehlend(observations, result),
        _case_alt(observations, result, reference),
        _case_alt_extra(observations, result, reference),
        _case_forged_label(observations, result, reference),
        _case_fd_flag(observations, result, reference),
        _case_packet(observations, result, reference),
        _case_fd_format(),
        _case_host(),
    ]
    agent_run = current.get("agent_run", "UNBEKANNT")
    bindung = current.get("bindung", "UNBEKANNT")
    package, stop_reason = _package(agent_run, bindung, rows)
    record = {
        "step": "P5",
        "evaluator_contract": "p6_live_acquisition",
        "expectation_role": "historical_p5_reference",
        "expectation_sha256": _expectation_sha(),
        "run": _run_of(result),
        "agent_run": agent_run if type(agent_run) is str else "UNBEKANNT",
        "package": package,
        "stop_reason": stop_reason,
        "rows": rows,
        "grenzen": GRENZEN,
    }
    return _scrub(record)


def _scrub(record: dict) -> dict:
    try:
        dumped = json.dumps(record)
    except TypeError:
        return {
            "step": "P5",
            "evaluator_contract": "p6_live_acquisition",
            "expectation_role": "historical_p5_reference",
            "expectation_sha256": _expectation_sha(),
            "run": None,
            "agent_run": "UNBEKANNT",
            "package": "STOP",
            "stop_reason": "TypeError",
            "rows": [],
            "grenzen": GRENZEN,
        }
    if CANARY in dumped or PROMPT_MARK in dumped:
        record = json.loads(dumped.replace(CANARY, "name").replace(PROMPT_MARK, "auftrag"))
        record["package"] = "STOP"
        record["stop_reason"] = "name_im_json"
    return record


def _load_archived(output: Path) -> tuple[object, object, object, object, str | None]:
    loaded: list[object] = []
    error: str | None = None
    for name in ("observations.json", "result.json", "reference.json", "binding.json"):
        try:
            loaded.append(json.loads((output / name).read_text(encoding="utf-8")))
        except Exception as exc:  # noqa: BLE001 — archive class only, no path text
            loaded.append(None)
            if error is None:
                error = type(exc).__name__
    observations, result, reference, binding = loaded
    return observations, result, reference, binding, error


def _guard_expectation(record: dict) -> dict:
    try:
        recorded = EXPECTATION_SHA.read_text(encoding="utf-8").strip()
        current = hashlib.sha256(EXPECTATION.read_bytes()).hexdigest()
    except OSError as exc:
        record["package"] = "STOP"
        record["stop_reason"] = type(exc).__name__
        record["expectation_sha256"] = None
        return record
    record["expectation_sha256"] = current
    if recorded != current:
        record["package"] = "STOP"
        record["stop_reason"] = "expectation_changed"
    return record


def _positive(binding: object) -> bool:
    return (
        isinstance(binding, dict)
        and binding.get("agent_run") == "BELEGT"
        and binding.get("reason") == "independent_local_effect"
    )


def _persist(output: Path, record: dict) -> None:
    output.mkdir(parents=True, exist_ok=True)
    p1.save(output / "reliability.json", record)


class _RetainedDirectory:
    """mkdtemp without deletion. One call site replaces TemporaryDirectory."""

    def __init__(
        self,
        suffix: str | None = None,
        prefix: str | None = None,
        dir: str | None = None,
        ignore_cleanup_errors: bool = False,
        *,
        delete: bool = True,
    ) -> None:
        del ignore_cleanup_errors, delete
        self.name = tempfile.mkdtemp(suffix=suffix, prefix=prefix, dir=dir)
        self._kept = True

    def __enter__(self) -> str:
        return self.name

    def __exit__(self, exc_type: object, exc: object, tb: object) -> bool:
        return False


def run_once(output: Path) -> dict:
    """One connect. No second attempt. Countercases use only stored rows."""
    if output.exists():
        record = score(None, None, None)
        record["package"] = "STOP"
        record["stop_reason"] = "FileExistsError"
        record = _guard_expectation(record)
        return _scrub(record)  # An existing run, including its score, is immutable.

    original = p1.tempfile.TemporaryDirectory
    kept: list[str] = []

    class _Remember(_RetainedDirectory):
        def __init__(self, *args: object, **kwargs: object) -> None:
            super().__init__(*args, **kwargs)
            kept.append(self.name)

    p1.tempfile.TemporaryDirectory = _Remember
    connect_error: Exception | None = None
    binding: object = None
    measured_records: list[dict] = []
    measured_digests: list[bytes] = []

    def consume(observations: list[dict], result: dict, reference: dict, context: object) -> None:
        measured_records.append(score(observations, result, reference, capture_context=context))
        measured_digests.append(p1._capture_digest(observations, result, reference))

    try:
        try:
            binding = p1.connect(
                output,
                codex="/Users/landjunge/.local/bin/codex",
                timeout=60,
                post_window=5,
                mode="late",
                on_capture=consume,
            )
        except Exception as exc:  # noqa: BLE001 — class name is the stop reason
            connect_error = exc
    finally:
        p1.tempfile.TemporaryDirectory = original
        if len(kept) == 1:
            WORKSPACE_PATH.write_text(kept[0] + "\n", encoding="utf-8")

    observations, result, reference, stored_binding, load_error = _load_archived(output)
    # Never upgrade reloaded JSON to a fresh measurement. Only the callback
    # which ran while the local acquisition was held can supply the score.
    record = (
        measured_records[0]
        if len(measured_records) == 1
        else score(observations, result, reference)
    )
    if len(kept) > 1:
        record["package"] = "STOP"
        record["stop_reason"] = "mehr_als_ein_verzeichnis"
    archive_matches = False
    binding_matches = False
    if len(measured_digests) == 1 and load_error is None:
        try:
            archive_matches = measured_digests[0] == p1._capture_digest(
                observations, result, reference
            )
            binding_matches = (
                isinstance(binding, dict)
                and isinstance(stored_binding, dict)
                and p1._capture_digest(None, binding, None)
                == p1._capture_digest(None, stored_binding, None)
            )
        except (TypeError, ValueError, RecursionError, OverflowError):
            # Parsed archive data may still be invalid for the canonical digest.
            # Treat it as a mismatch without exposing data or escaping STOP.
            pass
    record = _guard_expectation(record)
    if record.get("stop_reason") != "expectation_changed":
        if connect_error is not None:
            record["package"] = "STOP"
            record["stop_reason"] = type(connect_error).__name__
        elif load_error is not None:
            record["package"] = "STOP"
            record["stop_reason"] = load_error
        elif not archive_matches:
            record["package"] = "STOP"
            record["stop_reason"] = "archive_disagrees_with_capture"
        elif not binding_matches:
            record["package"] = "STOP"
            record["stop_reason"] = "binding_weicht_ab"
        elif not _positive(binding):
            record["package"] = "STOP"
            if not record.get("stop_reason"):
                reason = binding.get("reason") if isinstance(binding, dict) else None
                record["stop_reason"] = _token(reason, "agent_run_unbekannt")
    record = _scrub(record)
    _persist(output, record)
    return record


def main() -> int:
    output = ROOT / "docs" / "p1-runs" / "2026-10-09-p5-reliability"
    record = run_once(output)
    print(
        json.dumps(
            {
                "package": record.get("package"),
                "stop_reason": record.get("stop_reason"),
                "run": record.get("run"),
                "agent_run": record.get("agent_run"),
            }
        )
    )
    return 0 if record.get("package") == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
