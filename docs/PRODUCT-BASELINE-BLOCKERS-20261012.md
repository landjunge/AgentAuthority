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

Punkt 1 wurde als `85a9a1986379682ec5e36365dd045d2aff4399cb` gesichert,
mit sauberem Arbeitsbaum, bevor Punkt 2 begonnen wurde.

## Punkt 2 – Ressourcenbegrenzung abgeschlossen

Realer Aufnahmepfad: CLI → gewählter Adapter (`json_source.py` oder
`whiteboard.py`) → `file_reader.read_directory` → `read_record` → minimierter
Snapshot → neutraler Bericht. Beide bisherigen `os.listdir`-Aufnahmen lagen
nach Punkt 1 im gemeinsamen Reader; das Dateizahllimit griff erst danach.

Kleiner Umsetzungsplan: beide Enumerationen durch begrenztes `scandir(fd)`
ersetzen; jeden Verzeichniseintrag mitzählen, begrenzte Namensliste sortieren;
ein gemeinsames Bytebudget bis zur tatsächlichen `os.read`-Operation durchreichen;
Abbrüche/Zählgrenzen sichtbar machen; beide Adapter und Grenzfälle prüfen.

Konkrete Grenzen in `file_reader.py`:

- 10.000 Verzeichniseinträge je Scan, unabhängig von Dateiendung/Typ, plus genau eine zusätzliche Überlaufprobe. Zwei Scans, damit höchstens 20.002 zurückgegebene Einträge pro Aufnahme.
- Höchstens 10.000 JSON-Dateiversuche; weiterhin 65.536 Bytes je regulärer Datei und nichtblockierendes Öffnen mit `O_NOFOLLOW`/`O_NONBLOCK`.
- 8 MiB tatsächlich gelesene Rohbytes pro Aufnahme, einschließlich später ungültiger Eingaben. Nicht mehr passende Dateigrößen werden vor dem Lesen abgewiesen; beim Wachstum zwischen Größenprüfung und Lesen höchstens ein zusätzliches gezähltes Grenzbyte.
- Nach Erschöpfung des Bytebudgets keine weiteren Dateiaufnahmen. Signatur-, Dateiänderungs- und Verzeichnisidentitätsprüfungen bleiben erhalten.
- Erreichte Grenzen erzeugen Warnungen und Exit 2; Gesamtabdeckung bleibt UNBEKANNT. Nicht vollständig enumerierte Quellen melden `files_seen` nur als Untergrenze, auch in Text/HTML. Keine Behauptung eines vollständigen oder neuesten Gesamtverlaufs.

Geänderte Dateien für Punkt 2: `file_reader.py`, `json_source.py`,
`whiteboard.py`, `observations.py`, `report.py`, `html_report.py`,
`tests/test_product_observer.py` (nur Testhook-Signatur für gemeinsames Budget),
neu `tests/test_product_input_bounds.py`, aktueller Produktvertrag und Nutzung
sowie dieser Bericht. Keine Forschung, Lab-Logik oder historischen Tests geändert.

Nachweise: 14 gezielte Grenztests prüfen beide realen Adapter mit vielen Dateien,
Nicht-JSON-Verzeichniseinträgen, eine instrumentierte Enumeration mit sofortigem
Fehlschlag oberhalb der erlaubten Überlaufprobe und geschlossenem Iterator,
130 Dateien mit jeweils 65.536 Bytes, ungültiges JSON mit Budgetverbrauch,
Dateiwachstum, exakte Grenzwerte, begrenzten Kontrollscan bei Quellenwachstum,
tiefes JSON, FIFO/Übergröße und CLI-Exit 2.

Ein erster Grenztest erwartete für tief verschachtelte Arrays ausschließlich
`invalid_json`. Unter der verwendeten Laufzeit war das JSON syntaktisch gültig
und wurde als `invalid_entry` abgewiesen. Die Erwartung wurde auf die beiden
korrekten Ablehnungspfade präzisiert; weiterhin keine Einträge aufgenommen,
Bericht unvollständig, tatsächliche Bytes gezählt. Kein Erfolgskriterium für
Ressourcengrenzen wurde abgeschwächt. Danach alle betroffenen Prüfungen erneut grün.

## Abschlusschecks

Mit vorhandenen Werkzeugen, ohne Installation, VM-Start oder neue Forschung:

- `pytest tests/test_product_input_bounds.py -q`: 14 bestanden.
- `pytest tests/test_product_observer.py tests/test_product_html.py tests/test_product_contract.py tests/test_product_input_bounds.py -q`: 75 bestanden.
- `pytest -q`: 744 bestanden, Exit 0; die bekannte Fork-DeprecationWarning aus Punkt 1 bleibt.
- `ruff check agent_authority tests/test_product_observer.py tests/test_product_html.py tests/test_product_contract.py tests/test_product_input_bounds.py`: PASS, keine Befunde.
- `ruff format --check .`: PASS, 271 Dateien bereits formatiert.
- `mypy lab agent_authority --strict`: PASS, 35 Module.
- `bandit -r lab agent_authority -ll`: PASS, keine Befunde.
- `git diff --check` sowie Diff-Umfang und strikte UTF-8-Dekodierung der geänderten Dateien: PASS.

`ruff check .` bleibt mit Exit 1 und 16 historischen Befunden offen. Eine
lesende Gegenüberstellung per `ruff check . --output-format json` im
unveränderten master-Worktree und im Arbeitsworktree verglich Dateipfad,
Regelcode, Zeile und Spalte: alle 16 Befunde identisch, null neue Befunde.
Betroffen sind der archivierte A1-Preflight-Probe, `research/a1_linux/`
(channels, driver, observer), `research/a2_linux/` (agent, driver, host_crypto,
starter) und `tests/test_a2_linux_identity.py`. Regeln: UP017, PLW1510, I001,
SIM115, PLW1509 und RUF059. Diese Stellen bleiben gemäß Bestandsschutz unverändert;
ein global grüner Lint-Lauf wird ausdrücklich nicht behauptet.

## Verbleibende Grenzen und Bestandsschutz

Das neue JSON-Berichtsschema ist eine bewusste Vertragsänderung für Verbraucher.
Quellenauthentisierung, reale Agentenidentität, Wirkung und Gesamtabdeckung
bleiben UNBEKANNT. Teilaufnahmen sind keine atomaren Snapshots; bei Scanabbruch
ist die ausgewertete Teilmenge von der Verzeichnisreihenfolge abhängig.
Grenzen betreffen Datenvolumen und Iterations-/Parserarbeit, nicht eine harte
RAM-Zahl oder die Wartezeit einzelner Dateisystemaufrufe. Windows ohne sichere
POSIX-Aufnahme bleibt nicht unterstützt; die Tests liefen auf macOS/Python 3.12.

Diff gegenüber Ausgangsmaster ist ausschließlich auf aktuelle Produktmodule,
Produkttests, README und die drei aktuellen Produktdokumente begrenzt.
`lab/`, `research/`, Forschungs-/Originalmessungen, Quellpins, eingefrorene
Specs und inaktive Archive sind bytegleich erhalten. Lifecycle-, Snapshot-,
Approval- und Effect-Ticket-Mechanismen wurden nicht geändert und werden durch
die vorhandene vollständig bestandene Suite weiterhin geprüft. Keine neue
UI-Arbeit, keine Bereinigung und kein Merge nach master.
