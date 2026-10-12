"""Reported activity and structural warnings, with no task or effect decisions."""

from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any

from agent_authority.observations import Entry, Snapshot

KIND_TEXT = {
    "note": "Notiz gemeldet",
    "task": "Auftrag gemeldet",
    "claimed": "Übernahme gemeldet",
    "progress": "Fortschritt gemeldet",
    "result": "Ergebnis gemeldet",
    "decision": "Entscheidung gemeldet",
    "problem": "Problem gemeldet",
    "question": "Frage gemeldet",
    "system": "Systembeitrag gemeldet",
    "plan": "Plan gemeldet",
    "handoff": "Übergabe gemeldet",
}
DIAGNOSTIC_TEXT = {
    "invalid_thread_id": "Der Adapter meldet einen ungültigen Quellenbezeichner.",
    "invalid_source_id": "Der Quellenbezeichner entspricht nicht dem Eingangsvertrag.",
    "unsupported_reader_platform": "Der lesende Adapter ist auf dieser Plattform nicht verfügbar.",
    "source_unavailable": "Die ausgewählte Quelle ist nicht vollständig lesbar.",
    "input_limit": "Die Aufnahmegrenze wurde erreicht; weitere Dateien wurden nicht gelesen.",
    "invalid_filename": "Eine JSON-Datei hat keinen gültigen Eintragsbezeichner.",
    "unreadable_entry": "Ein Eintrag konnte nicht als reguläre Datei gelesen werden.",
    "nonregular_entry": "Eine nichtreguläre Eintragsdatei wurde nicht gelesen.",
    "entry_too_large": "Ein Eintrag überschreitet die begrenzte Eingangsgröße.",
    "invalid_json": "Ein Eintrag enthält ungültiges oder mehrdeutiges JSON.",
    "invalid_entry": "Ein Eintrag entspricht nicht dem benötigten Feldvertrag.",
    "entry_identity_mismatch": "Datei-, Eintrags- oder Quellenzuordnung widersprechen sich.",
    "source_changed": "Während der Aufnahme wurde eine Änderung an der Quelle beobachtet.",
    "ordinal_collision": "Mehrere Beiträge beanspruchen dieselbe gespeicherte Reihenfolge.",
}


def build_report(snapshot: Snapshot, limit: int = 20) -> dict[str, Any]:
    if type(limit) is not int or not 1 <= limit <= 100:
        raise ValueError("invalid display limit")
    ordered = sorted(snapshot.entries, key=lambda entry: (entry.ordinal, entry.identifier))
    by_ordinal: dict[int, list[Entry]] = defaultdict(list)
    by_task: dict[str, list[Entry]] = {}
    for entry in ordered:
        by_ordinal[entry.ordinal].append(entry)
        if entry.task_key is not None:
            by_task.setdefault(entry.task_key, []).append(entry)
    collisions = {ordinal for ordinal, values in by_ordinal.items() if len(values) > 1}
    warnings: list[dict[str, Any]] = [
        {"code": item.code, "evidence": [{"entry_id": item.entry_id}] if item.entry_id else []}
        for item in snapshot.diagnostics
    ]
    warnings.extend(
        {
            "code": "ordinal_collision",
            "evidence": [entry.reference() for entry in by_ordinal[ordinal]],
        }
        for ordinal in sorted(collisions)
    )
    tasks: list[dict[str, Any]] = []
    pending_claims = 0
    for index, values in enumerate(by_task.values(), 1):
        counts = Counter(entry.kind for entry in values)
        ambiguous = any(entry.ordinal in collisions for entry in values)
        claims = [entry for entry in values if entry.kind == "claimed"]
        results = [entry for entry in values if entry.kind == "result"]
        missing_result = bool(claims and (not results or claims[-1].ordinal > results[-1].ordinal))
        if missing_result and not ambiguous:
            pending_claims += 1
        tasks.append(
            {
                "task_alias": f"A{index}",
                "association_basis": "reported_task_id_only",
                "last_reported_kind": None if ambiguous else values[-1].kind,
                "order_ambiguous": ambiguous,
                "entry_count": len(values),
                "reported_kind_counts": dict(sorted(counts.items())),
                "claim_without_later_result": None if ambiguous else missing_result,
                "evidence": [entry.reference() for entry in values[-3:]],
            }
        )
    tasks.reverse()
    tasks.sort(key=lambda task: max(ref["ordinal"] for ref in task["evidence"]), reverse=True)
    complete = not warnings
    return {
        "schema_version": "agent-authority-observation-report-v1",
        "role": "observer_only",
        "source": {
            "scope": "selected_local_observations",
            "kind": snapshot.source.kind,
            "source_id": snapshot.source.identifier or None,
            "files_seen": snapshot.files_seen,
            "files_examined": snapshot.files_examined,
            "entries_read": len(ordered),
            "complete_observed_read": complete,
            "coverage_of_all_agent_activity": "UNBEKANNT",
            "source_authenticated": False,
            "identity": "UNBEKANNT",
            "effect": "UNBEKANNT",
        },
        "summary": {
            "reported_kind_counts": dict(sorted(Counter(entry.kind for entry in ordered).items())),
            "tasks_with_reported_association": len(tasks),
            "claims_without_later_result_in_read_entries": pending_claims,
            "structural_warning_count": len(warnings),
        },
        "tasks": tasks[:limit],
        "recent_entries": [
            {
                **entry.reference(),
                "reported_kind": entry.kind,
                "reported_actor_type": entry.reported_actor_type,
            }
            for entry in reversed(ordered[-limit:])
        ],
        "warnings": warnings[:limit],
        "display": {
            "limit": limit,
            "tasks_omitted": max(0, len(tasks) - limit),
            "entries_omitted": max(0, len(ordered) - limit),
            "warnings_omitted": max(0, len(warnings) - limit),
        },
        "task_completion_proven": False,
        "rights_inherited": False,
    }


def render_text(report: dict[str, Any]) -> str:
    source, summary = report["source"], report["summary"]
    state = (
        "vollständig im bezeichneten Leseumfang"
        if source["complete_observed_read"]
        else "unvollständig"
    )
    lines = [
        "Agent Authority — Aktivitätsbeobachtung",
        f"{source['entries_read']} Beiträge gelesen; Aufnahme {state}.",
        (
            f"{summary['tasks_with_reported_association']} gemeldete Aufgabenbezüge; "
            f"{summary['claims_without_later_result_in_read_entries']} Übernahmen ohne späteren Ergebnisbeitrag."
        ),
        "Herkunft, Identität und tatsächliche Wirkung: UNBEKANNT.",
        "Ergebnisbeiträge sind Meldungen; sie beweisen keinen Abschluss oder Vollzug.",
    ]
    if report["tasks"]:
        lines.append("\nAufgaben im gelesenen Verlauf:")
        for task in report["tasks"]:
            kind = task["last_reported_kind"]
            label = (
                KIND_TEXT[kind]
                if kind is not None
                else "Letzte Meldung UNBEKANNT (Reihenfolge mehrdeutig)"
            )
            refs = ", ".join(f"E{ref['ordinal']} [{ref['entry_id']}]" for ref in task["evidence"])
            pending = (
                "; kein späterer Ergebnisbeitrag gelesen"
                if task["claim_without_later_result"]
                else ""
            )
            lines.append(f"{task['task_alias']}: {label}{pending}; Belege: {refs}")
    if report["warnings"]:
        lines.append("\nStrukturelle Warnungen:")
        for warning in report["warnings"]:
            refs = ", ".join(ref["entry_id"] for ref in warning["evidence"])
            suffix = f" Belege: {refs}." if refs else ""
            lines.append(f"- {DIAGNOSTIC_TEXT[warning['code']]}{suffix}")
    else:
        lines.append("Keine strukturelle Warnung in den gelesenen Einträgen.")
    omitted = report["display"]
    if any(omitted[key] for key in ["tasks_omitted", "entries_omitted", "warnings_omitted"]):
        lines.append(
            f"Anzeige begrenzt: {omitted['tasks_omitted']} Aufgaben, "
            f"{omitted['entries_omitted']} Beiträge und {omitted['warnings_omitted']} Warnungen "
            "nicht angezeigt; alle ausgelesenen Einträge wurden ausgewertet."
        )
    return "\n".join(lines)
