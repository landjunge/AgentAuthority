# Authority: automatisierter Quellen-Grenztest nach Run 03

Datum: 8. Oktober 2026. Dieser Test liest ausschließlich eingefrorene
Run-03-Belege. Er erzeugt **keine neue C1-C7-Messung**, keinen neuen
Collector-Aufruf und schreibt weder an `observer_research.py` noch an die
früheren Rohdaten und Forschungsberichte.

## Was automatisch kontrolliert wird

`.github/workflows/collector-source-boundary.yml` führt nach jedem Push auf
`feat/observer-wb-automation` oder `master`, bei Pull Requests nach `master`
und manuell über `workflow_dispatch` einen isolierten Python-3.12-CI-Job aus.
Es läuft die neue Testdatei
`tests/test_collector_source_boundary.py` zweimal; anschließend erzeugt
`python -m probes.collector_source_boundary_analysis --archive
docs/observer-collector-manipulation-c1-c7-run03/2026-10-08` einen
JSON-Vergleichsbericht als GitHub-Actions-Artefakt (14 Tage Aufbewahrung).
Bei verletzten Assertions oder beschädigten Archivdateien schlägt der Job fehl.

## Was das Ergebnis bedeutet

Im eingefrorenen Datensatz gab es unter fünf referenzierten Identitätsfällen
drei falsche positive Aussagen (C3/C4/C7) und zwei korrekte (C1/C2).
Ein separater, **bewusst konservativer** Policy-Prototyp ersetzt bei allen
sieben Fällen eine nicht unabhängig authentifizierte Quelle durch
`A=UNBEKANNT`. Damit entstehen im Replay **null falsche positive
Identitätsaussagen**, aber **auch null nutzbare positive Identitätsaussagen**.

Das ist **keine Erkennung einer Manipulation** und kein Nachweis einer
vertrauenswürdigen Quelle: Ehrliche und manipulierte Antworten werden ohne
unabhängiges Vertrauenssignal gleichermaßen zurückgehalten. Ein solches
Vertrauenssignal ist noch nicht implementiert. Der ursprüngliche Observer
bleibt unverändert und hätte weiterhin seine drei belegten Falschaussagen.

## Manuelle lokale Wiederholung

Nach Installation der Dev-Abhängigkeiten und vom Repository-Root:

```sh
python -m pytest -p no:cacheprovider -o addopts='' -q tests/test_collector_source_boundary.py
python -m probes.collector_source_boundary_analysis \
  --archive docs/observer-collector-manipulation-c1-c7-run03/2026-10-08
```

Der Workflow ist ein automatisierter **Regressionstest**, kein kontinuierlicher
Agentenprozess und keine laufende Sicherheitsüberwachung. GitHub muss Actions
für das Repository ausführen dürfen; ein grüner Cloud-Lauf muss anhand der
GitHub-Actions-Ausführung separat bestätigt werden.
