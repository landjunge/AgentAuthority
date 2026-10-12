"""Eight preregistered local attempts; never authenticate an agent identity."""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import math
import platform
import subprocess
from pathlib import Path

from lab.observation_completeness import describe_snapshot
from scripts import p7_integration as p7

N = 8
ROOT = Path(__file__).resolve().parents[1]
MATRIX = {
    "original_p8_rows": 15,
    "additional": {
        "A1_writer_pid_start": "BELEGT",
        "A1_sibling_distinct": "VERSCHIEDEN",
        "A1_forged_pid_rejected": True,
        "B1_scope": "UNVOLLSTAENDIG",
        "B1_target": "BELEGT",
        "B2_second_window": "SPAETER",
        "B2_foreign_capture": "UNBEKANNT/foreign_capture",
    },
}


def _json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n")


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sources() -> dict[str, str]:
    names = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT).decode().split("\0")
    return {name: _hash(ROOT / name) for name in names if name}


def exact_interval(k: int, n: int) -> list[float]:
    """Two-sided 95% Clopper-Pearson interval under the binomial model."""
    if type(k) is not int or type(n) is not int or n < 1 or not 0 <= k <= n:
        raise ValueError("invalid binomial counts")

    def quantile(indices: range, increasing: bool) -> float:
        low, high = 0.0, 1.0
        for _ in range(64):
            mid = (low + high) / 2
            probability = sum(math.comb(n, i) * mid**i * (1 - mid) ** (n - i) for i in indices)
            if (probability < 0.025) == increasing:
                low = mid
            else:
                high = mid
        return (low + high) / 2

    return [
        0.0 if k == 0 else quantile(range(k, n + 1), True),
        1.0 if k == n else quantile(range(k + 1), False),
    ]


def freeze(parent: Path) -> str:
    """Create fresh external preregistration before any cohort attempt."""
    parent = Path(parent)
    if parent.exists() or p7._forbidden(parent):
        raise ValueError("fresh external cohort directory required")
    if subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT).strip():
        raise ValueError("source must be committed and clean before freeze")
    cli = p7.REAL_CODEX
    version = subprocess.check_output([str(cli), "--version"], text=True, timeout=10).strip()
    manifest = {
        "schema": "abc-c1-preregistration-v1",
        "utc": datetime.datetime.now(datetime.UTC).isoformat(),
        "n": N,
        "order": list(range(1, N + 1)),
        "source_head": p7._source_head(),
        "source_sha256": _sources(),
        "codex_version": version,
        "codex_path": str(cli),
        "codex_sha256": _hash(cli),
        "configured_model": p7.p1.MODEL,
        "model_authenticated": False,
        "host": platform.platform(),
        "python": platform.python_version(),
        "scenario": "same supplied artificial local late-file case, eight fixed positions",
        "timeout": 120,
        "post_window": 5,
        "matrix": MATRIX,
        "A1": "closed INCONCLUSIVE",
        "B2_foreign": "not executed INCONCLUSIVE",
        "logical_agent_identity": "UNBEKANNT",
    }
    parent.mkdir()
    _json(parent / "manifest.json", manifest)
    return _hash(parent / "manifest.json")


def _manifest(parent: Path, digest: str) -> dict:
    if p7._forbidden(parent) or _hash(parent / "manifest.json") != digest:
        raise ValueError("manifest changed or forbidden output")
    manifest = json.loads((parent / "manifest.json").read_text())
    if manifest["n"] != N or manifest["order"] != list(range(1, N + 1)):
        raise ValueError("changed N/order")
    if manifest["matrix"] != MATRIX or manifest["source_head"] != p7._source_head():
        raise ValueError("source/matrix changed")
    if manifest["source_sha256"] != _sources() or manifest["codex_sha256"] != _hash(p7.REAL_CODEX):
        raise ValueError("source/executable changed")
    return manifest


def additional_rows(record: dict) -> list[dict]:
    """Project recorded scope; absent writer/window experiments stay unfulfilled."""
    score = record.get("capture_score") or {}
    current = next(
        (r.get("ist", {}) for r in score.get("rows", []) if r.get("fall") == "aktuell"), {}
    )
    valid = score.get("package") == "PASS" and current.get("reference_valid") is True
    present = current.get("reference_target_present") if valid else None
    scope = describe_snapshot(present, reason="prior_live_capture_snapshot")
    actual = {
        "B1_scope": scope["coverage"] if valid else "UNBEKANNT",
        "B1_target": scope["target_effect"],
    }
    return [
        {
            "case": name,
            "expected": expected,
            "actual": actual.get(name, "UNBEKANNT"),
            "status": "PASS" if name in actual and actual[name] == expected else "UNBEKANNT",
            "reason": "recorded_scope_projection"
            if name in actual
            else "required_experiment_not_measured",
        }
        for name, expected in MATRIX["additional"].items()
    ]


def summarize(rows: list[dict]) -> dict:
    completed = len(rows) == N
    k = sum(r["full_matrix_complete"] for r in rows)
    old = sum(r["original_matrix_pass"] for r in rows)
    return {
        "N_geplant": N,
        "N_Startversuche": len(rows),
        "N_gestartet": sum(r["cli_started"] for r in rows),
        "N_modellnachweise": sum(r["model_proven"] for r in rows),
        "N_abgebrochen": sum(r["timeout"] or not r["cli_started"] for r in rows),
        "N_ohne_Modellnachweis": sum(not r["model_proven"] for r in rows),
        "N_nicht_versucht": N - len(rows),
        "N_vollstaendig": k,
        "full_matrix_interval_95": exact_interval(k, N) if completed else None,
        "original_matrix_pass": old,
        "original_matrix_interval_95": exact_interval(old, N) if completed else None,
        "interval_scope": "eight planned attempts; binomial IID/common-p assumption unverified",
        "logical_agent_identity": "UNBEKANNT",
        "identity_effect_binding": "UNBEKANNT",
        "general_reliability": "UNBEKANNT",
        "retries": 0,
        "rows": rows,
    }


def run_cohort(parent: Path, digest: str) -> dict:
    parent = Path(parent)
    manifest = _manifest(parent, digest)
    if (parent / "cohort-result.json").exists() or list(parent.glob("run-*")):
        raise ValueError("cohort already attempted; no retry")
    assert p7.p1 is p7.p5.p1
    rows = []
    stop_reason = None
    for position in manifest["order"]:
        try:
            _manifest(parent, digest)
        except (ValueError, OSError) as exc:
            stop_reason = type(exc).__name__ + ": " + str(exc)
            break
        run_parent = parent / f"run-{position:02}"
        failure = None
        try:
            p7.prepare(
                run_parent,
                quelle_sha=manifest["source_head"],
                timeout=manifest["timeout"],
                post_window=manifest["post_window"],
            )
            record = p7.run(run_parent, codex=str(p7.REAL_CODEX))
        except Exception as exc:  # noqa: BLE001 — retain failed position, never retry
            failure = type(exc).__name__
            record = {}
        result_path = run_parent / "lauf" / "result.json"
        try:
            captured = json.loads(result_path.read_text()) if result_path.is_file() else {}
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            failure = type(exc).__name__
            captured = {}
        counts = captured.get("counts", {})
        extra = additional_rows(record)
        original = record.get("zeilen", [])
        old_pass = len(original) == 15 and all(r["status"] == "PASS" for r in original)
        rows.append(
            {
                "position": position,
                "run": captured.get("run"),
                "cli_started": counts.get("started") is True,
                "model_proven": record.get("modellnachweis") is True,
                "timeout": counts.get("timeout") is True,
                "acceptance": record.get("abnahme"),
                "reason": record.get("abnahme_grund"),
                "runner_failure": failure,
                "cli_success": counts.get("cli_success"),
                "recording_ok": counts.get("recording_ok"),
                "original_matrix_pass": old_pass,
                "additional_rows": extra,
                "full_matrix_complete": old_pass
                and record.get("modellnachweis") is True
                and all(r["status"] == "PASS" for r in extra),
                "integration_sha256": _hash(run_parent / "integration.json")
                if (run_parent / "integration.json").is_file()
                else None,
            }
        )
        _json(parent / f"position-{position:02}.json", rows[-1])
        print(
            json.dumps(
                {
                    "position": position,
                    "run": captured.get("run"),
                    "original_matrix_pass": old_pass,
                    "model_proven": rows[-1]["model_proven"],
                }
            ),
            flush=True,
        )
    try:
        _manifest(parent, digest)
    except (ValueError, OSError) as exc:
        stop_reason = type(exc).__name__ + ": " + str(exc)
    summary = summarize(rows)
    summary["global_stop"] = stop_reason
    if stop_reason:
        summary["full_matrix_interval_95"] = None
        summary["original_matrix_interval_95"] = None
    summary["manifest_sha256"] = digest
    summary["source_head"] = manifest["source_head"]
    _json(parent / "cohort-result.json", summary)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["freeze", "run"])
    parser.add_argument("parent", type=Path)
    parser.add_argument("--digest")
    args = parser.parse_args()
    if args.action == "freeze":
        print(freeze(args.parent))
    else:
        if not args.digest:
            parser.error("run requires preregistered --digest")
        run_cohort(args.parent, args.digest)


if __name__ == "__main__":
    main()
