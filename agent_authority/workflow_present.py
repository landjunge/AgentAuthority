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
}


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
        for key, value in event["binding"].items():
            lines.append(f"  {key}: {value}")
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
            for key, value in event["binding"].items()
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
        + f"<ul>{warnings}</ul>"
        + f"<p>{report['read']['events_omitted']} weitere Ereignisse nicht angezeigt / events omitted.</p>"
        + "<p>Gesamtabdeckung UNBEKANNT / Overall coverage UNKNOWN.</p></section>"
    )
    return base.replace('<section id="tasks"', section + '<section id="tasks"', 1)
