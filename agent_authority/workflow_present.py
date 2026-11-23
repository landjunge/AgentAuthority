"""Views over the existing report, with explicit versioned workflow claims."""

from __future__ import annotations

from html import escape
from typing import Any

from agent_authority.html_report import render_html
from agent_authority.report import render_text

WARNINGS = {
    "workflow_sequence_gap": "Lücke in gemeldeter Reihenfolge / Reported sequence gap",
    "workflow_order_unknown": "Globale Reihenfolge unbekannt / Global order unknown",
    "workflow_out_of_order": "Ungeordnet gelesen / Read out of order",
    "workflow_ordinal_conflict": "Widersprüchliche Reihenfolge / Conflicting order",
    "workflow_duplicate_conflict": "Gleiche ID, verschiedene Inhalte / Same ID, conflicting content",
    "workflow_chain_gap": "Fehlender Hashkettenbezug / Missing hash-chain link",
    "workflow_prefix_unobserved": "Früheres Segment nicht beobachtet / Earlier segment not observed",
    "workflow_identity_unverified": "Behauptete Identität ungeprüft / Claimed identity unverified",
    "workflow_invalid_update_evidence": "Ungültige Update-Beobachtung / Invalid update observation",
}

WARNINGS.update(
    {
        "workflow_revision_stale": "Veraltete Revision gemeldet / Stale revision reported",
        "workflow_revision_mismatch": "Abweichende Revision gemeldet / Different revision reported",
        "workflow_revision_unknown": "Revisionsbezug unbekannt / Revision relation unknown",
        "workflow_return_binding_unknown": "Rückgabebezug unzureichend belegt / Return binding insufficiently evidenced",
        "workflow_return_binding_mismatch": "Widersprüchlicher Rückgabebezug / Conflicting return binding",
        "workflow_result_artifact_missing": "Ergebnisbeleg fehlt / Result artifact reference missing",
        "workflow_control_point_missing": "Kontrollpunkt nicht ausreichend belegt / Control point insufficiently evidenced",
        "workflow_stop_order_unknown": "Effektive Sperrreihenfolge unbekannt / Effective stop order unknown",
        "workflow_dispatch_after_stop": "Versand nach gemeldeter Sperrbarriere / Dispatch after reported stop barrier",
    }
)


def _finding_lines(report: dict[str, Any]) -> list[str]:
    analysis = report.get("analysis", {})
    lines = [
        "Fachliche Hinweise / Workflow findings",
        "Nur Konsistenz gemeldeter Fakten; tatsächlicher Verstoß und Gesamtauftrag bleiben ungeprüft.",
        "Producer-claim consistency only; actual violations and project completion remain unverified.",
    ]
    for item in analysis.get("findings", []):
        lines.append(WARNINGS.get(item["code"], item["code"]) + " · " + item["classification"])
        lines.append("  " + item["finding_id"] + " · " + ", ".join(item["fields"]))
        for ref in item["evidence_refs"]:
            lines.append(
                "  "
                + ref["source_tool"]
                + "/"
                + ref["source_id"]
                + "/"
                + ref["event_id"]
                + " · "
                + ref["entry_id"]
                + " · sha256:"
                + ref["record_sha256"]
            )
    lines.append(f"Weitere Hinweise / Omitted findings: {analysis.get('findings_omitted', 0)}")
    lines.append(
        "Keine Hinweise ist kein Sicherheits- oder Vollständigkeitsnachweis. / No findings is not a safety or completeness proof."
    )
    return lines


def _event_rows(event: dict[str, Any]) -> list[tuple[str, str | int]]:
    rows = list(event["binding"].items())
    update = event.get("update_evidence")
    if update is not None:
        rows.extend(
            [
                ("update_id", update["update_id"]),
                ("signature_verification", update["signature_verification"]),
            ]
        )
        for name, fact in update["facts"].items():
            rows.append((name, fact["state"]))
            rows.extend((f"{name}.{key}", value) for key, value in fact["claims"].items())
        for difference in update["differences"]:
            rows.append((difference["state"], " / ".join(difference["fields"])))
    return rows


def _update_conflict_lines(report: dict[str, Any]) -> list[str]:
    lines = []
    for conflict in report.get("update_ci_conflicts", []):
        claims = ", ".join(
            f"{claim['status']} ({claim['event_id']})" for claim in conflict["claims"]
        )
        lines.append(
            "Gemeldeter CI-Widerspruch / Reported CI conflict · "
            f"{conflict['update_id']} · {conflict['ci_run_ref']} · {claims}"
        )
    if omitted := report.get("update_ci_conflicts_omitted"):
        lines.append(f"Weitere CI-Widersprüche / Omitted CI conflicts: {omitted}")
    return lines


def render_workflow_text(report: dict[str, Any]) -> str:
    lines = [
        render_text(report["observation_report"]),
        "",
        "Workflow-Metadaten / Workflow metadata",
        "Nur gemeldete Bezüge; keine Rechte, Budgets oder Stopps durch diesen Bericht.",
        "Reported references only; this report grants no rights, budget or stop authority.",
    ]
    for event in report["events"]:
        lines.append(f"{event['event_type']} · {event['source_tool']} · {event['event_id']}")
        for key, value in _event_rows(event):
            lines.append(f"  {key}: {value}")
    lines.extend(_update_conflict_lines(report))
    lines.extend(_finding_lines(report))
    for warning in report["warnings"]:
        lines.append("- " + WARNINGS.get(warning["code"], warning["code"]))
    lines.append(
        f"Nicht angezeigte Ereignisse / Omitted events: {report['read']['events_omitted']}"
    )
    lines.append("Identität, tatsächliche Wirkung und vollständige Abdeckung: UNBEKANNT / UNKNOWN.")
    return "\n".join(lines)


def render_workflow_html(report: dict[str, Any]) -> str:
    base = render_html(report["observation_report"])
    events = []
    for event in report["events"]:
        facts = "".join(
            f"<li><code>{escape(key)}</code>: {escape(str(value))}</li>"
            for key, value in _event_rows(event)
        )
        events.append(
            f"<details><summary>{escape(event['event_type'])} · "
            f"{escape(event['source_tool'])} · {escape(event['event_id'])}</summary>"
            f"<p>{escape(event.get('timestamp') or 'UNBEKANNT / UNKNOWN')}</p><ul>{facts}</ul>"
            "<p>Gemeldet / Reported · Identität und Wirkung unbekannt / identity and effect unknown</p>"
            "</details>"
        )
    warnings = "".join(
        f"<li>{escape(WARNINGS.get(item['code'], item['code']))}</li>"
        for item in report["warnings"]
    )
    section = (
        "<section id='workflow'><h2>Workflow-Metadaten / Workflow metadata</h2>"
        "<p>Nur Beobachtung. Keine Rechte-/Budgetfreigabe, kein Arbeitsstopp und keine Nutzerabnahme. "
        "Observation only: no rights/budget approval, enforced stop or user acceptance.</p>"
        + "".join(events)
        + "".join("<p>" + escape(line) + "</p>" for line in _update_conflict_lines(report))
        + f"<ul>{warnings}</ul>"
        + "<section id='workflow-findings'>"
        + "".join("<p>" + escape(line) + "</p>" for line in _finding_lines(report))
        + "</section>"
        + f"<p>{report['read']['events_omitted']} weitere Ereignisse nicht angezeigt / events omitted.</p>"
        + "<p>Gesamtabdeckung UNBEKANNT / Overall coverage UNKNOWN.</p></section>"
    )
    return base.replace('<section id="tasks"', section + '<section id="tasks"', 1)
