"""Acceptance for the offline HTML presentation and unchanged observer semantics."""

from __future__ import annotations

import base64
import hashlib
import json
from html.parser import HTMLParser
from pathlib import Path

import pytest

from agent_authority.cli import main
from agent_authority.html_report import render_html
from agent_authority.report import build_report
from agent_authority.whiteboard import read_whiteboard

THREAD = "123456abcdef"
PRIVATE = 'PRIVATE_CANARY_<script>alert("private")</script>'


class Document(HTMLParser):
    def __init__(self, value):
        super().__init__()
        self.tags = []
        self.text = []
        self.styles = []
        self.in_style = False
        self.feed(value)

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))
        self.in_style = tag == "style" or self.in_style

    def handle_endtag(self, tag):
        if tag == "style":
            self.in_style = False

    def handle_data(self, data):
        (self.styles if self.in_style else self.text).append(data)


def put(store: Path, number: int, kind: str = "result", **changes: object) -> Path:
    folder = store / "whiteboard" / THREAD
    folder.mkdir(parents=True, exist_ok=True)
    identifier = f"{number:012x}"
    record = {
        "id": identifier,
        "thread_id": THREAD,
        "ordinal": number,
        "entry_type": kind,
        "actor_type": "codex",
        "task_id": PRIVATE,
        "actor": PRIVATE,
        "content": PRIVATE,
        "run_id": PRIVATE,
        "instance_id": PRIVATE,
        "room_id": PRIVATE,
        "metadata": {"source_authenticated": True, "effect": "BELEGT", "prompt": PRIVATE},
        **changes,
    }
    path = folder / (identifier + ".json")
    path.write_text(json.dumps(record))
    return path


def test_html_matches_report_counts_task_aliases_and_actual_citation_bytes(tmp_path):
    put(tmp_path, 1, "claimed")
    path = put(tmp_path, 2, "result")
    put(tmp_path, 3, "claimed", task_id="other-" + PRIVATE)
    value = build_report(read_whiteboard(tmp_path, THREAD))
    output = render_html(value)
    text = " ".join(Document(output).text)
    assert "3" in text and "Beiträge gelesen" in text
    assert "A1" in text and "A2" in text
    assert "Ergebnis gemeldet" in text and "Übernahme gemeldet" in text
    assert "WB2" in text and path.stem in text
    assert hashlib.sha256(path.read_bytes()).hexdigest() in text
    assert "Herkunft, Identität und tatsächliche Wirkung bleiben" in text
    assert "UNBEKANNT" in text
    assert "beweisen keinen Aufgabenabschluss" in text
    assert "Kein späterer Ergebnisbeitrag gelesen" in text
    assert value["task_completion_proven"] is False


def test_html_never_exports_private_source_content_or_positive_metadata_claims(tmp_path):
    put(tmp_path, 1)
    output = render_html(build_report(read_whiteboard(tmp_path, THREAD)))
    assert "PRIVATE_CANARY" not in output
    assert "BELEGT" not in output
    assert "source_authenticated" not in output
    assert not any(tag == "script" for tag, _ in Document(output).tags)


def test_renderer_escapes_projected_strings_instead_of_creating_active_markup(tmp_path):
    put(tmp_path, 1)
    value = build_report(read_whiteboard(tmp_path, THREAD))
    injection = '<img src="https://example.invalid/leak" onerror="alert(1)">'
    value["source"]["thread_id"] = injection
    value["tasks"][0]["task_alias"] = injection
    value["tasks"][0]["evidence"][0]["entry_id"] = injection
    value["tasks"][0]["evidence"][0]["file_sha256"] = injection
    output = render_html(value)
    doc = Document(output)
    assert injection in " ".join(doc.text)
    assert "&lt;img" in output
    assert not any(tag in {"img", "script", "svg", "iframe"} for tag, _ in doc.tags)
    assert not any(key.startswith("on") for _, attrs in doc.tags for key in attrs)


def test_offline_document_allows_only_its_actual_stylesheet_hash_and_native_disclosures(tmp_path):
    put(tmp_path, 1)
    doc = Document(render_html(build_report(read_whiteboard(tmp_path, THREAD))))
    policy = next(
        attrs["content"]
        for tag, attrs in doc.tags
        if tag == "meta" and attrs.get("http-equiv") == "Content-Security-Policy"
    )
    digest = base64.b64encode(hashlib.sha256("".join(doc.styles).encode()).digest()).decode()
    assert f"style-src 'sha256-{digest}'" in policy
    assert "default-src 'none'" in policy and "script-src 'none'" in policy
    assert "base-uri 'none'" in policy and "form-action 'none'" in policy
    assert any(tag == "details" for tag, _ in doc.tags)
    assert any(tag == "summary" for tag, _ in doc.tags)
    assert not any(tag in {"script", "link", "img", "iframe", "form"} for tag, _ in doc.tags)
    assert all(attrs["href"].startswith("#") for _, attrs in doc.tags if "href" in attrs)


def test_collisions_and_display_omissions_remain_visible_without_changing_analysis(tmp_path):
    put(tmp_path, 1, "claimed")
    put(tmp_path, 2, "result", ordinal=1)
    put(tmp_path, 3, "claimed", task_id="other")
    limited = build_report(read_whiteboard(tmp_path, THREAD), limit=1)
    full = build_report(read_whiteboard(tmp_path, THREAD), limit=20)
    text = " ".join(Document(render_html(limited)).text)
    assert limited["summary"] == full["summary"]
    assert "Datenaufnahme: unvollständig" in text
    assert "Mehrere Beiträge beanspruchen dieselbe gespeicherte Reihenfolge" in text
    assert "1 weitere Aufgaben nicht angezeigt" in text
    assert "2 weitere Beiträge nicht angezeigt" in text
    full_text = " ".join(Document(render_html(full)).text)
    assert "Letzte Meldung UNBEKANNT (Reihenfolge mehrdeutig)" in full_text


@pytest.mark.parametrize("existing", [False, True])
def test_missing_and_empty_sources_do_not_claim_absence_of_other_agent_activity(tmp_path, existing):
    if existing:
        (tmp_path / "whiteboard" / THREAD).mkdir(parents=True)
    output = render_html(build_report(read_whiteboard(tmp_path, THREAD)))
    text = " ".join(Document(output).text)
    assert "Keine Beiträge gelesen" in text
    assert "keine Aussage über andere Agentenaktivität" in text
    assert "Abdeckung sämtlicher Agentenaktivität bleibt UNBEKANNT" in text
    assert ("Datenaufnahme: unvollständig" in text) is (not existing)


def test_html_cli_uses_existing_exit_semantics_and_writes_only_stdout(tmp_path, capsys):
    path = put(tmp_path, 1)
    before = {
        str(p.relative_to(tmp_path)): p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()
    }
    args = ["inspect", "--store", str(tmp_path), "--thread", THREAD, "--format", "html"]
    assert main(args) == 0
    assert capsys.readouterr().out.startswith("<!doctype html>")
    assert before == {
        str(p.relative_to(tmp_path)): p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()
    }
    path.write_text("{INVALID")
    assert main(args) == 2
    assert "Datenaufnahme: unvollständig" in capsys.readouterr().out


def test_text_and_json_outputs_retain_their_default_behavior(tmp_path, capsys):
    put(tmp_path, 1)
    args = ["inspect", "--store", str(tmp_path), "--thread", THREAD]
    assert main(args) == 0
    assert capsys.readouterr().out.startswith("Agent Authority — Whiteboard-Beobachtung")
    assert main([*args, "--format", "json"]) == 0
    value = json.loads(capsys.readouterr().out)
    assert value == build_report(read_whiteboard(tmp_path, THREAD))
