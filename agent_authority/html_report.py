"""Offline presentation of the existing minimized observer report."""

from __future__ import annotations

import base64
import hashlib
from html import escape
from typing import Any

from agent_authority.report import DIAGNOSTIC_TEXT, KIND_TEXT

STYLE = """:root{color-scheme:light;font-family:system-ui,-apple-system,sans-serif;color:#172539;
background:#f3f6fa;line-height:1.55}*{box-sizing:border-box}body{margin:0}
main{max-width:1120px;margin:auto;padding:40px 24px 64px}header{margin-bottom:28px}
h1{font-size:2.5rem;letter-spacing:-.04em;margin:4px 0}h2{font-size:1.3rem;margin:0 0 16px}
p{margin:10px 0}.eyebrow{font-size:.78rem;font-weight:700;letter-spacing:.12em;color:#52617a}
.muted,small{color:#52617a}.notice{padding:16px 20px;border:1px solid #b8c9df;
border-left:5px solid #356ca1;border-radius:8px;background:#edf4fc}
.partial{border-color:#e4ca96;border-left-color:#a46b0b;background:#fff7e8}
.stats{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin:20px 0}
.stat,section{background:white;border:1px solid #dbe3ee;border-radius:10px}
.stat{padding:16px}.stat strong{display:block;font-size:1.8rem}.stat span{font-size:.9rem}
nav{display:flex;flex-wrap:wrap;gap:20px;margin:24px 0}a{color:#255a91}
section{padding:24px;margin:20px 0}.table-scroll{overflow-x:auto}
table{width:100%;border-collapse:collapse;text-align:left;font-size:.9rem;min-width:620px}
caption{text-align:left;margin-bottom:12px;color:#52617a}th,td{padding:13px 12px;
border-bottom:1px solid #e2e8f0;vertical-align:top}th{font-size:.78rem;letter-spacing:.03em}
tbody tr:last-child td{border-bottom:0}td:first-child{font-weight:650}
summary{cursor:pointer;color:#255a91}summary:focus-visible,a:focus-visible{
outline:3px solid #356ca1;outline-offset:4px}details ul{padding-left:18px;margin:12px 0}
details li{margin-bottom:12px}code{font-size:.82em;overflow-wrap:anywhere}
.warnings{padding-left:20px}.warnings>li{padding:10px 0}.pending{display:block;
font-size:.8rem;color:#76500c;margin-top:4px}.omitted{font-size:.85rem;color:#52617a}
footer{color:#52617a;font-size:.85rem;margin-top:28px}
@media(max-width:650px){main{padding:24px 14px 40px}h1{font-size:2rem}
.stats{grid-template-columns:repeat(2,minmax(0,1fr))}section{padding:18px 14px}}
@media print{:root{background:white}main{max-width:none;padding:0}nav{display:none}
section,.stat{break-inside:avoid}.table-scroll{overflow:visible}table{min-width:0}}
"""


def _h(value: object) -> str:
    return escape(str(value), quote=True)


def _evidence(references: list[dict[str, Any]]) -> str:
    if not references:
        return "<span class='muted'>Keine Eintragsreferenz verfügbar</span>"
    items = []
    for ref in references:
        ordinal = f"WB{_h(ref['ordinal'])} · " if "ordinal" in ref else "Eintrag · "
        fingerprint = (
            f"<br><small>SHA256 <code>{_h(ref['file_sha256'])}</code></small>"
            if "file_sha256" in ref
            else ""
        )
        items.append(f"<li>{ordinal}<code>{_h(ref['entry_id'])}</code>{fingerprint}</li>")
    return (
        f"<details><summary>Belege ({len(references)})</summary><ul>{''.join(items)}</ul></details>"
    )


def render_html(report: dict[str, Any]) -> str:
    """Render the P10-01 projection; no archive reads, exports or new inferences."""
    source, summary, display = report["source"], report["summary"], report["display"]
    complete = source["complete_observed_read"]
    state = "vollständig im bezeichneten Leseumfang" if complete else "unvollständig"
    notice_class = "notice" if complete else "notice partial"
    thread = _h(source["thread_id"]) if source["thread_id"] else "keine gültige Quelle"
    cards = [
        (source["entries_read"], "Beiträge gelesen"),
        (summary["tasks_with_reported_association"], "Gemeldete Aufgabenbezüge"),
        (summary["structural_warning_count"], "Strukturelle Warnungen"),
        (
            summary["claims_without_later_result_in_read_entries"],
            "Übernahmen ohne spätere Ergebnismeldung",
        ),
    ]
    stats = "".join(
        f"<div class='stat'><strong>{_h(count)}</strong><span>{_h(label)}</span></div>"
        for count, label in cards
    )
    tasks = []
    for task in report["tasks"]:
        kind = task["last_reported_kind"]
        label = (
            KIND_TEXT[kind]
            if kind is not None
            else "Letzte Meldung UNBEKANNT (Reihenfolge mehrdeutig)"
        )
        pending = (
            "<span class='pending'>Kein späterer Ergebnisbeitrag gelesen</span>"
            if task["claim_without_later_result"]
            else ""
        )
        tasks.append(
            f"<tr><td>{_h(task['task_alias'])}</td><td>{_h(label)}{pending}</td>"
            f"<td>{_h(task['entry_count'])}</td><td>{_evidence(task['evidence'])}</td></tr>"
        )
    task_table = (
        "<div class='table-scroll'><table><caption>Neueste gelesene Aufgabenmeldungen; "
        "Aliase beruhen ausschließlich auf gemeldeten Auftragskennungen.</caption>"
        "<thead><tr><th scope='col'>Aufgabe</th><th scope='col'>Gemeldeter Stand</th>"
        "<th scope='col'>Beiträge</th><th scope='col'>Eintragsbelege</th></tr></thead>"
        f"<tbody>{''.join(tasks)}</tbody></table></div>"
        if tasks
        else "<p>Keine Aufgabenbezüge in den gelesenen Beiträgen.</p>"
    )
    warnings = "".join(
        f"<li>{_h(DIAGNOSTIC_TEXT[item['code']])}{_evidence(item['evidence'])}</li>"
        for item in report["warnings"]
    )
    warning_list = (
        f"<ol class='warnings'>{warnings}</ol>"
        if warnings
        else "<p>Keine strukturelle Warnung in den gelesenen Einträgen.</p>"
    )
    recent = "".join(
        f"<tr><td>WB{_h(entry['ordinal'])}</td><td>{_h(KIND_TEXT[entry['reported_kind']])}</td>"
        f"<td>{_h(entry['reported_actor_type'])} (gemeldet)</td>"
        f"<td>{_evidence([entry])}</td></tr>"
        for entry in report["recent_entries"]
    )
    recent_table = (
        "<div class='table-scroll'><table><caption>Gemeldete Beitragstypen und Actor-Typen, "
        "keine authentisierte Identität.</caption><thead><tr><th scope='col'>Beitrag</th>"
        "<th scope='col'>Meldung</th><th scope='col'>Actor-Typ</th>"
        f"<th scope='col'>Eintragsbeleg</th></tr></thead><tbody>{recent}</tbody></table></div>"
        if recent
        else "<p>Keine Beiträge gelesen. Daraus folgt keine Aussage über andere Agentenaktivität.</p>"
    )
    style_hash = base64.b64encode(hashlib.sha256(STYLE.encode()).digest()).decode()
    policy = (
        f"default-src 'none'; script-src 'none'; style-src 'sha256-{style_hash}'; "
        "base-uri 'none'; form-action 'none'"
    )
    return f"""<!doctype html>
<html lang="de"><head><meta charset="utf-8">
<meta http-equiv="Content-Security-Policy" content="{_h(policy)}">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Agent Authority — Whiteboard {thread}</title><style>{STYLE}</style></head>
<body><main><header><p class="eyebrow">LOKALES WHITEBOARDARCHIV</p>
<h1>Agent Authority</h1><p>Gemeldete Aktivität, nachvollziehbare Belege und Datenhinweise.</p>
<p class="muted">Ausgewählter Verlauf: <code>{thread}</code></p></header>
<div class="{notice_class}"><strong>Datenaufnahme: {state}</strong>
<p>{_h(source["files_examined"])} von {_h(source["files_seen"])} JSON-Dateien untersucht.
Herkunft, Identität und tatsächliche Wirkung bleiben <strong>UNBEKANNT</strong>.</p></div>
<div class="stats">{stats}</div>
<nav aria-label="Berichtsabschnitte"><a href="#tasks">Aufgaben</a>
<a href="#warnings">Warnungen</a><a href="#recent">Beiträge</a><a href="#scope">Leseumfang</a></nav>
<section id="tasks" aria-labelledby="tasks-heading"><h2 id="tasks-heading">Gemeldete Aufgabenaktivität</h2>
{task_table}<p class="omitted">{_h(display["tasks_omitted"])} weitere Aufgaben nicht angezeigt.</p>
<p class="muted">Eine Übernahme ohne spätere Ergebnismeldung beschreibt den gelesenen Verlauf.
Sie beweist weder einen laufenden noch einen gescheiterten Agenten.</p></section>
<section id="warnings" aria-labelledby="warnings-heading"><h2 id="warnings-heading">Strukturelle Warnungen</h2>
{warning_list}<p class="omitted">{_h(display["warnings_omitted"])} weitere Warnungen nicht angezeigt.</p></section>
<section id="recent" aria-labelledby="recent-heading"><h2 id="recent-heading">Letzte gelesene Beiträge</h2>
{recent_table}<p class="omitted">{_h(display["entries_omitted"])} weitere Beiträge nicht angezeigt.</p></section>
<section id="scope" aria-labelledby="scope-heading"><h2 id="scope-heading">Leseumfang und Aussagegrenzen</h2>
<p>Ausgewertet wurden die ausgelesenen Beiträge des bezeichneten lokalen Verlaufs.
Die Anzeigegrenze von {_h(display["limit"])} reduziert diese Analyse nicht.
Die Abdeckung sämtlicher Agentenaktivität bleibt UNBEKANNT.</p>
<p>Ergebnisbeiträge sind Meldungen; sie beweisen keinen Aufgabenabschluss oder tatsächlichen Vollzug.
Ein Datei-SHA256 dient zum Vergleich der gelesenen Bytes, nicht zur Verfasserauthentisierung.</p>
<p>Dieser Bericht verändert keine Aufgaben oder Agenten und erteilt keine Rechte oder Freigaben.</p></section>
<footer>Lokale Beobachterpreview · Offline-Bericht ohne automatische Aktualisierung.
Quellen können sich nach dem Lesen ändern; keine atomare Snapshotgarantie.</footer>
</main></body></html>"""
