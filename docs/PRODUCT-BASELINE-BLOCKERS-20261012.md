# Zwei Produktblocker: sequenzielle Umsetzung

Ausgangsbasis: konsolidierter `master`
`b72fa377f3a5908485b14749a101ff692ab5d130`.
Arbeitsbranch: `codex/product-contract-input-bounds-20261012`.
Keine Änderung an master, kein UI und keine neue Forschungsphase.

## Punkt 1 – abgeschlossen vor Beginn von Punkt 2

Befund: `whiteboard.py` definierte die internen Typen; `report.py` importierte
sie und schrieb ein Whiteboard-/Thread-Schema. CLI und HTML setzten ThreadDesk
als einzigen Eingang und Verlauf voraus.

Kleiner Umsetzungsplan: gemeinsame minimierte, unveränderliche Beobachtungstypen;
vorhandene sichere Dateioperationen ohne neue Ressourcenregeln herauslösen;
ThreadDesk als Adapter erhalten, neutralen JSON-Verzeichniseingang hinzufügen;
CLI-Auswahl und alle drei Reporter auf denselben Vertrag umstellen; verifizieren.

Umgesetzt in `agent_authority/observations.py`, `file_reader.py`,
`json_source.py`, `whiteboard.py`, `cli.py`, `report.py`, `html_report.py`.
Aktueller Vertrag: `PRODUCT-OBSERVATION-CONTRACT.md`; README und Produktnutzung
verweisen darauf. Historische P10-Verträge bleiben unverändert. Quellenkennung,
Eintragskennung und Actor-Typ erfordern kein ThreadDesk-Format. Alte CLI-Aufrufe
wählen ausschließlich den kompatiblen Adapter. JSON-Berichtsschema wechselt
explizit zu `agent-authority-observation-report-v1` mit `source.kind/source_id`.

Nachweise: `tests/test_product_contract.py` prüft adapterfreie Reporter, reale
neutrale Dateiaufnahme, gleichwertige Analyse beider Adapter, ungültige Verträge,
UTF-8-Ausgabe und fehlende/mischende CLI-Argumente. Die bisherigen Produkttests
wurden nur an die neutralen Feldnamen und Referenzbeschriftungen angepasst.
Alle Hash-, Nichtschreiben-, Symlink-, FIFO-, Snapshotänderungs-, Minimierungs-
und UNBEKANNT-Prüfungen bleiben erhalten.

Verifikation vor Beginn von Punkt 2 (Python 3.12.13, macOS):

- `pytest tests/test_product_observer.py tests/test_product_html.py tests/test_product_contract.py -q`: 61 bestanden.
- `pytest -q`: gesamte vorhandene Suite, 730 bestanden, Exit 0.
- `ruff check` und `ruff format --check` für Produktmodule und die drei Produkttestdateien: PASS (Ruff 0.17.0).
- `mypy agent_authority --strict`: PASS, neun Module (Mypy 2.4.0).
- `bandit -r agent_authority -ll`: PASS, keine Befunde.
- Separater neutraler CLI-Prozess: weder `agent_authority.whiteboard` noch `lab` importiert.
- CLI-Hilfe und `git diff --check`: PASS.

Bekannte Warnung der unveränderten Suite: Python meldet in
`tests/test_plan_p6_boundaries.py::test_capture_context_does_not_survive_fork`
einen Fork aus einem Prozess mit mehreren Threads. Kein Testfehler; keine
Änderung am historischen Test vorgenommen.

Verbleibende Grenzen von Punkt 1: externe JSON-Verbraucher müssen das neue Schema
beachten. Keine Quellenauthentisierung, keine bewiesene Agentenidentität oder
Dateiwirkung, keine A1–A4-Liveintegration und keine atomare Snapshotgarantie.
Die bisherige unbegrenzte Verzeichnisenumeration bleibt bis Punkt 2 explizit offen.
