"""One P7 run over the existing late capture. No second observer and no gate.

A synthetic CLI can satisfy the live score branch. That result is not a model
proof. Only the configured local Codex executable can set ``modellnachweis``.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import platform
import shlex
import subprocess
import sys
from pathlib import Path

_SCRIPT = Path(__file__).resolve().parent / "p5_reliability.py"
_spec = importlib.util.spec_from_file_location("p7_loaded_p5_reliability", _SCRIPT)
assert _spec is not None and _spec.loader is not None
p5 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(p5)
p1 = p5.p1

ROOT = _SCRIPT.parents[1]
REAL_CODEX = Path("/Users/landjunge/.local/bin/codex")
P5_EXPECTATION_LOCK = Path("/tmp/aa-p5-expectation-before.txt")
P5_WORKSPACE_LOCK = Path("/tmp/aa-p5-workspace-path.txt")
P5_RUNS = ROOT / "docs" / "p1-runs"
P6_DOC = ROOT / "docs" / "P6-HERKUNFTSGRENZEN.md"
PROMPT_MARK = "Run exactly this supplied"
TESTZIEL = "ein connect mode=late auf das vorhandene lokale Werkzeug"
OPEN_LIMITS = tuple(p5.GRENZEN)


def _window(value: object, limit: float) -> bool:
    if type(value) is bool or type(value) not in (int, float):
        return False
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return False
    return 0 < value <= limit


def _resolve(path: Path) -> Path:
    return path.resolve()


def _inside(path: Path, root: Path) -> bool:
    try:
        _resolve(path).relative_to(_resolve(root))
    except ValueError:
        return False
    return True


def _forbidden(path: Path) -> bool:
    resolved = _resolve(path)
    blocked = {_resolve(P5_EXPECTATION_LOCK), _resolve(P5_WORKSPACE_LOCK), _resolve(P6_DOC)}
    if resolved in blocked:
        return True
    return _inside(resolved, ROOT)


def _source_head() -> str:
    return subprocess.check_output(
        ["/usr/bin/git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip()


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_json(path: Path, value: dict) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def _locks() -> dict[str, bytes | None]:
    found: dict[str, bytes | None] = {}
    for path in (P5_EXPECTATION_LOCK, P5_WORKSPACE_LOCK, P6_DOC):
        found[str(path)] = path.read_bytes() if path.is_file() else None
    return found


def _bare(reason: str) -> dict:
    return {
        "step": "P7",
        "abnahme": "STOP",
        "abnahme_grund": reason,
        "modellnachweis": False,
        "herkunft": "UNBEKANNT",
        "identitaet": "UNBEKANNT",
        "geschrieben": False,
        "grenzen": {name: "offen" for name in OPEN_LIMITS},
    }


def _expectation_ok(raw: object, parent: Path) -> bool:
    if not isinstance(raw, dict):
        return False
    sha = raw.get("quelle_sha")
    if (
        type(sha) is not str
        or len(sha) != 40
        or any(char not in "0123456789abcdef" for char in sha)
    ):
        return False
    if raw.get("phase") != "P7" or raw.get("modus") != "late" or raw.get("testziel") != TESTZIEL:
        return False
    if not _window(raw.get("timeout_sekunden"), 300) or not _window(
        raw.get("nachlauf_sekunden"), 30
    ):
        return False
    if _resolve(Path(str(raw.get("laufpfad")))) != _resolve(parent / "lauf"):
        return False
    expected = raw.get("erwartet")
    if not isinstance(expected, dict):
        return False
    return (
        expected.get("replay") == "STOP"
        and expected.get("abgelaufener_kontext") == "UNBEKANNT"
        and expected.get("herkunft") == "UNBEKANNT"
        and expected.get("identitaet") == "UNBEKANNT"
        and expected.get("fixture") == "kein Modellnachweis"
    )


def prepare(
    parent: Path,
    *,
    quelle_sha: str,
    timeout: float = 60,
    post_window: float = 5,
) -> dict:
    """Write the expectation before ``lauf`` exists. Refuse P5 and P6 paths."""
    if type(quelle_sha) is not str or len(quelle_sha) != 40:
        raise ValueError("quelle_sha")
    if any(char not in "0123456789abcdef" for char in quelle_sha):
        raise ValueError("quelle_sha")
    if not _window(timeout, 300) or not _window(post_window, 30):
        raise ValueError("window")
    parent = Path(parent)
    if _forbidden(parent) or _forbidden(parent / "lauf") or parent.exists():
        raise ValueError("parent")
    parent.mkdir()
    lauf = parent / "lauf"
    expectation = {
        "phase": "P7",
        "quelle_sha": quelle_sha,
        "laufpfad": str(lauf),
        "testziel": TESTZIEL,
        "nachlauf_sekunden": post_window,
        "timeout_sekunden": timeout,
        "modus": "late",
        "erwartet": {
            "aufnahme": "score im aktiven capture_context",
            "replay": "STOP",
            "abgelaufener_kontext": "UNBEKANNT",
            "herkunft": "UNBEKANNT",
            "identitaet": "UNBEKANNT",
            "spaeteffekt": "NACH nur aus der laufenden Aufnahme",
            "fixture": "kein Modellnachweis",
            "grenzen": "offen",
        },
    }
    _write_json(parent / "erwartung-vor-lauf.json", expectation)
    if lauf.exists():
        raise ValueError("lauf")
    return expectation


def classify_late_measurement(measurement: object) -> dict:
    """Label the existing local late sampler. It never becomes a model proof."""
    result = measurement.get("result") if isinstance(measurement, dict) else None
    timing = result.get("timing") if isinstance(result, dict) else None
    trusted = (
        isinstance(result, dict)
        and result.get("proven_agent_runs") == 0
        and result.get("agent_run") == "UNBEKANNT"
        and result.get("mode") == "late"
        and isinstance(timing, dict)
        and timing.get("order") in {"NACH", "VOR"}
    )
    return {
        "modellnachweis": False,
        "agent_run": "UNBEKANNT",
        "proven_agent_runs": 0,
        "ordnung": timing.get("order") if trusted else "UNBEKANNT",
        "herkunft": "UNBEKANNT",
        "identitaet": "UNBEKANNT",
        "grund": "lokale_werkzeugmessung_kein_modelllauf",
    }


def _row_map(record: object) -> dict[str, dict]:
    if not isinstance(record, dict):
        return {}
    rows = record.get("rows")
    if not isinstance(rows, list):
        return {}
    return {
        row["fall"]: row for row in rows if isinstance(row, dict) and type(row.get("fall")) is str
    }


def _load_archive(lauf: Path) -> tuple[object, object, object, str | None]:
    loaded: list[object] = []
    error: str | None = None
    for name in ("observations.json", "result.json", "reference.json"):
        try:
            loaded.append(json.loads((lauf / name).read_text(encoding="utf-8")))
        except (OSError, UnicodeError, json.JSONDecodeError, RecursionError) as exc:
            loaded.append(None)
            error = error or type(exc).__name__
    observations, result, reference = loaded
    return observations, result, reference, error


def _digest_matches(
    live: tuple[object, object, object], loaded: tuple[object, object, object]
) -> bool:
    try:
        return p1._capture_digest(*live) == p1._capture_digest(*loaded)
    except (TypeError, ValueError, RecursionError, OverflowError, UnicodeError):
        return False


def _narrow_timing(result: object) -> dict:
    if not isinstance(result, dict):
        return {"ordnung": "UNBEKANNT", "urteil": "UNBEKANNT", "bewertung": "UNBEKANNT"}
    timing = result.get("timing")
    order = timing.get("order") if isinstance(timing, dict) else None
    verdict = timing.get("verdict") if isinstance(timing, dict) else None
    evaluation = result.get("timing_evaluation")
    return {
        "ordnung": order if type(order) is str else "UNBEKANNT",
        "urteil": verdict if type(verdict) is str else "UNBEKANNT",
        "bewertung": evaluation if type(evaluation) is str else "UNBEKANNT",
    }


def _proven(result: object) -> bool:
    if not isinstance(result, dict):
        return False
    counts = result.get("counts")
    return (
        type(result.get("proven_agent_runs")) is int
        and result["proven_agent_runs"] == 1
        and result.get("agent_run") == "BELEGT"
        and isinstance(counts, dict)
        and type(counts.get("model_completions")) is int
        and counts["model_completions"] > 0
        and type(counts.get("tool_reports")) is int
        and counts["tool_reports"] > 0
        and counts.get("recording_ok") is True
        and counts.get("started") is True
        and counts.get("timeout") is False
        and counts.get("cli_success") is True
        and type(counts.get("cli_exit_code")) is int
        and counts["cli_exit_code"] == 0
        and type(counts.get("invalid_records")) is int
        and counts["invalid_records"] == 0
        and type(counts.get("error_records")) is int
        and counts["error_records"] == 0
    )


def _line(fall: str, expected: str, actual: str, reason: str) -> dict:
    clean = reason.replace("|", "/")[:80]
    return {
        "fall": fall,
        "erwartet": expected,
        "ist": actual,
        "status": "PASS" if actual == expected else "FAIL",
        "grund": clean,
    }


def _matrix(
    score: dict, replay: dict, expired: dict, timing: dict, model_expected: str, model_actual: str
) -> list[dict]:
    rows = _row_map(score)
    lines: list[dict] = []
    for name in p5.CASES:
        row = rows.get(name)
        actual = (
            row.get("status")
            if isinstance(row, dict) and type(row.get("status")) is str
            else "UNBEKANNT"
        )
        reason = (
            row.get("grund")
            if isinstance(row, dict) and type(row.get("grund")) is str
            else "fehlende_zeile"
        )
        expected = "SKIP" if name == "host_verifier" else "PASS"
        lines.append(_line(name, expected, actual, reason))
    expired_rows = _row_map(expired)
    current = expired_rows.get("aktuell")
    ist = current.get("ist") if isinstance(current, dict) else None
    geltung = ist.get("geltung") if isinstance(ist, dict) else None
    lines.append(
        _line(
            "abgelaufener_kontext",
            "UNBEKANNT",
            geltung if type(geltung) is str else "UNBEKANNT",
            "kontext_nach_aufnahme_ungueltig",
        )
    )
    lines.append(
        _line(
            "replay",
            "STOP",
            replay.get("package") if type(replay.get("package")) is str else "UNBEKANNT",
            replay.get("stop_reason")
            if type(replay.get("stop_reason")) is str
            else "archiv_ohne_kontext",
        )
    )
    lines.append(_line("herkunft", "UNBEKANNT", "UNBEKANNT", "kein_herkunftsbeleg"))
    lines.append(_line("identitaet", "UNBEKANNT", "UNBEKANNT", "kein_identitaetsbeleg"))
    lines.append(_line("spaeteffekt", "NACH", timing["ordnung"], "nur_aus_der_laufenden_aufnahme"))
    model_reason = "originaler_codex_exec" if model_actual == "belegt" else "kein_modellnachweis"
    lines.append(_line("modellnachweis", model_expected, model_actual, model_reason))
    return lines


def bericht(record: dict) -> str:
    """German expected-versus-actual matrix. It does not add a measurement."""
    lines = [
        "# P7 Erwartet-Ist",
        "",
        f"Quelle: {record.get('quelle_sha')}",
        f"Befehl: {record.get('befehl')}",
        f"Umwelt: Python {record.get('python')} {record.get('system')}",
        f"Laufpfad: {record.get('laufpfad')}",
        f"Nachlauf_Sekunden: {record.get('nachlauf_sekunden')}",
        f"Timeout_Sekunden: {record.get('timeout_sekunden')}",
        f"Laufnachweis: {record.get('abnahme')} (keine formale P7-Abnahme)",
        f"Grund: {record.get('abnahme_grund')}",
        f"Modellnachweis: {record.get('modellnachweis')}",
        "Herkunft: UNBEKANNT",
        "Identitaet: UNBEKANNT",
        "",
        "| Fall | Erwartet | Ist | Status |",
        "| --- | --- | --- | --- |",
    ]
    for row in record.get("zeilen") or []:
        lines.append(f"| {row['fall']} | {row['erwartet']} | {row['ist']} | {row['status']} |")
    lines.append("")
    lines.append("Grenzen bleiben offen: " + ", ".join(OPEN_LIMITS) + ".")
    lines.append(
        "Historische Referenzen bleiben erhalten. RC/CB-Reparatur: RemediationLab; "
        "OOS-Reparatur: FakeAdapter; P4: akzeptiertes ungeklärtes Restrisiko (WB1597)."
    )
    lines.append(
        "D-012: beobachten, auswerten, warnen. Kein Recht, kein Secret, kein Budget, kein Stop."
    )
    return "\n".join(lines) + "\n"


def _finish(parent: Path, record: dict) -> dict:
    if PROMPT_MARK in json.dumps(record, ensure_ascii=False, allow_nan=False):
        record = _bare("name_im_json")
    text = bericht(record)
    if PROMPT_MARK in text:
        record = _bare("name_im_json")
        text = bericht(record)
    record["geschrieben"] = True
    _write_json(parent / "integration.json", record)
    (parent / "erwartet-ist.md").write_text(text, encoding="utf-8")
    return record


def run(parent: Path, *, codex: str, fixture: bool = False) -> dict:
    """Score inside the active capture, then show replay and expiry as historical."""
    parent = Path(parent)
    if type(codex) is not str or not codex or len(codex) > 400 or PROMPT_MARK in codex:
        return _bare("codex_pfad")
    if type(fixture) is not bool or _forbidden(parent):
        return _bare("forbidden_path")
    expectation_path = parent / "erwartung-vor-lauf.json"
    integration_path = parent / "integration.json"
    lauf = parent / "lauf"
    if integration_path.exists() or lauf.exists() or (parent / "erwartet-ist.md").exists():
        return _bare("FileExistsError")
    if not expectation_path.is_file() or _forbidden(lauf):
        return _bare("expectation_missing")
    try:
        names = sorted(path.name for path in parent.iterdir())
        raw = json.loads(expectation_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return _bare(type(exc).__name__)
    if names != ["erwartung-vor-lauf.json"] or not _expectation_ok(raw, parent):
        return _bare("expectation_invalid")
    if raw["quelle_sha"] != _source_head():
        return _bare("source_head_mismatch")
    expectation_digest = _sha256(expectation_path)
    before = _locks()
    held: dict[str, object] = {}

    def consume(observations: list[dict], result: dict, reference: dict, context: object) -> None:
        held["score"] = p5.score(observations, result, reference, capture_context=context)
        held["context"] = context
        held["observations"] = observations
        held["result"] = result
        held["reference"] = reference

    failure: str | None = None
    binding: object = None
    try:
        binding = p1.connect(
            lauf,
            codex=codex,
            timeout=float(raw["timeout_sekunden"]),
            post_window=float(raw["nachlauf_sekunden"]),
            mode="late",
            on_capture=consume,
        )
    except Exception as exc:  # noqa: BLE001 — class name is the stop reason
        failure = type(exc).__name__
    if _locks() != before:
        failure = failure or "p5_datei_veraendert"
    try:
        if _sha256(expectation_path) != expectation_digest:
            failure = failure or "expectation_changed_during_capture"
    except OSError:
        failure = failure or "expectation_missing_after_capture"
    score = held.get("score")
    result = held.get("result")
    if not isinstance(score, dict) or not isinstance(result, dict):
        failure = failure or "aufnahme_fehlt"
        score = {}
    loaded = _load_archive(lauf) if lauf.is_dir() else (None, None, None, "aufnahme_fehlt")
    observations, reference = held.get("observations"), held.get("reference")
    live_bundle = (observations, result if isinstance(result, dict) else None, reference)
    archive_matches = _digest_matches(live_bundle, loaded[:3])
    if not archive_matches:
        failure = failure or loaded[3] or "archive_disagrees_with_capture"
    replay = p5.score(loaded[0], loaded[1], loaded[2])
    expired = (
        p5.score(observations, result, reference, capture_context=held.get("context"))
        if isinstance(score, dict) and score
        else {}
    )
    timing = _narrow_timing(result)
    resolved = Path(codex)
    try:
        same_executable = resolved.resolve() == REAL_CODEX.resolve() and REAL_CODEX.is_file()
    except OSError:
        same_executable = False
    model_actual = (
        "belegt"
        if (not fixture and same_executable and _proven(result) and failure is None)
        else "nicht_belegt"
    )
    model_expected = "nicht_belegt" if fixture or not same_executable else "belegt"
    # A path that is not the real executable cannot be promoted by omitting fixture.
    if not same_executable:
        model_expected = "nicht_belegt"
        model_actual = "nicht_belegt"
    current = _row_map(score).get("aktuell")
    current_ist = current.get("ist") if isinstance(current, dict) else None
    if not isinstance(current_ist, dict) or current_ist.get("herkunft") != "UNBEKANNT":
        failure = failure or "herkunft_nicht_unbekannt"
    if not isinstance(current_ist, dict) or current_ist.get("identitaet") != "UNBEKANNT":
        failure = failure or "identitaet_nicht_unbekannt"
    binding_reason = binding.get("reason") if isinstance(binding, dict) else None
    positive = (
        failure is None
        and isinstance(score, dict)
        and score.get("package") == "PASS"
        and binding_reason == "independent_local_effect"
        and replay.get("package") == "STOP"
        and timing["ordnung"] == "NACH"
        and archive_matches
    )
    matrix = _matrix(score, replay, expired, timing, model_expected, model_actual)
    if any(row["status"] != "PASS" for row in matrix):
        positive = False
        failure = failure or "expectation_matrix_failed"
    modellnachweis = positive and model_actual == "belegt" and model_expected == "belegt"
    if modellnachweis:
        acceptance = "BELEGT"
        reason = "originaler_codex_exec"
    elif failure is not None:
        acceptance = "STOP"
        reason = failure
    elif fixture or not same_executable:
        acceptance = "STOP"
        reason = "fixture_kein_modellnachweis"
    else:
        acceptance = "STOP"
        reason = score.get("stop_reason") if isinstance(score, dict) else None
        if type(reason) is not str or not reason:
            reason = "agent_run_unbekannt"
    record = {
        "step": "P7",
        "quelle_sha": raw["quelle_sha"],
        "erwartung_sha256": expectation_digest,
        "befehl": shlex.join(
            [
                sys.executable,
                "scripts/p7_integration.py",
                "--parent",
                str(parent),
                "--codex",
                codex,
                "--quelle-sha",
                raw["quelle_sha"],
                "--timeout",
                str(raw["timeout_sekunden"]),
                "--post-window",
                str(raw["nachlauf_sekunden"]),
            ]
            + (["--fixture"] if fixture else [])
        ),
        "python": platform.python_version(),
        "system": platform.platform(),
        "laufpfad": str(lauf),
        "nachlauf_sekunden": raw["nachlauf_sekunden"],
        "timeout_sekunden": raw["timeout_sekunden"],
        "bewertung_aus": "aktiver_aufnahmekontext"
        if isinstance(score, dict) and score
        else "kein_lauf",
        "score_package": score.get("package") if isinstance(score, dict) else "STOP",
        "capture_score": score,
        "replay_score": replay,
        "expired_score": expired,
        "abnahme": acceptance,
        "abnahme_grund": reason,
        "modellnachweis": modellnachweis,
        "fixture": fixture,
        "herkunft": "UNBEKANNT",
        "identitaet": "UNBEKANNT",
        "zeitordnung": timing,
        "agent_run": score.get("agent_run")
        if isinstance(score, dict) and type(score.get("agent_run")) is str
        else "UNBEKANNT",
        "bindung": binding_reason if type(binding_reason) is str else "UNBEKANNT",
        "zeilen": matrix,
        "grenzen": {name: p5.GRENZEN[name] for name in OPEN_LIMITS},
        "geschrieben": False,
    }
    if any(value != "offen" for value in record["grenzen"].values()):
        record["abnahme"] = "STOP"
        record["abnahme_grund"] = "grenze_veraendert"
        record["modellnachweis"] = False
    return _finish(parent, record)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--parent", type=Path, required=True)
    parser.add_argument("--codex", default=str(REAL_CODEX))
    parser.add_argument("--quelle-sha", required=True)
    parser.add_argument("--timeout", type=float, default=60)
    parser.add_argument("--post-window", type=float, default=5)
    parser.add_argument("--fixture", action="store_true")
    args = parser.parse_args(argv)
    prepare(
        args.parent,
        quelle_sha=args.quelle_sha,
        timeout=args.timeout,
        post_window=args.post_window,
    )
    record = run(args.parent, codex=args.codex, fixture=args.fixture)
    print(
        json.dumps(
            {
                "abnahme": record.get("abnahme"),
                "grund": record.get("abnahme_grund"),
                "modellnachweis": record.get("modellnachweis"),
                "quelle_sha": record.get("quelle_sha"),
            },
            allow_nan=False,
        )
    )
    return 0 if record.get("abnahme") == "BELEGT" else 2


if __name__ == "__main__":
    raise SystemExit(main())
