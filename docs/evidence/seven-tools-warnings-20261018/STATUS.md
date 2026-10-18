# AA-C02 – begrenzte fachliche Warnungen

Stand: 18.10.2026 · privater Folgearbeitsstand, kein Deployment/Release.

## Ausgangspunkt und Zuständigkeit

- Originalanforderung: AA-03 / AA-C02 im unveränderten Sieben-Tools-Quellpaket
  `CODEX-BAUAUFTRAG-SIEBEN-TOOLS-20261018-1833.md`, Planversion 0.2.
- Produktbasis `origin/master`: `edd40b959fc898edc06e790fe3672e748d7dbb2c`.
- AA-C01/Design/DEEN-Grundlage: PR50, `9a0bd2acfbef64af0b56d0e566ee07d62adf05de`.
  Dessen Worktree bleibt clean/unverändert; separater Folgebranch/Worktree
  `feat/seven-tools-warnings-20261018` / `.worktrees/seven-tools-warnings-20261018`.
- Corecommit `cdbe24c`: Regeln, versionierte Hinweise, Text/HTML und gezielte Tests.
  Folgecommit enthält native Ansicht, zusätzliche Gegenfälle, Dokumentation und
  diese Belege. Keine fremden Rootdateien, historische Labbelege oder Laufzeiten
  geändert; keine Tokens/Prompts/Konten/Provideraufrufe.

## Tatsächlich umgesetzt

`workflow_rules.analyze_workflow_claims` wertet bereits minimierte Claims aus.
Additiver Bericht `analysis` mit Schema `agent-authority-workflow-findings-v1`.
Regeln: Revisionen getrennt, falscher Empfänger/Rückgabebezug, fehlende
Artefaktreferenz bei gemeldetem Abschluss/Lieferung, Versand nach gemeldeter
persistenter effektiver Sperrbarriere und fehlender/mismatched Kontrollpunkt.

Gemeinsame Identität/Revisionen/G01 bleiben opake **gemeldete** Bezüge. G02 benötigt
identischen Controller-/Projekt-/Workflowscope, denselben dauerhaften Zähler und
passende Task/Attempt/Request/Consumer/Actor-Angaben für einen Referenzvergleich.
Keine Kontrollinstanz angeschlossen/aktiviert. 4AllPass `access.approved` reicht
nicht als Gatebeleg; Gnom `work.finished` ist eine Abschlussmeldung, keine Abnahme.
Die minimale Ereignis-Whitelist ist additiv um vier Referenzfelder erweitert.

Jeder Hinweis enthält eine rotationsstabile ID, Klassifikation, engen Scope und
höchstens zwei Quellen-/Event-/Entry-/Recordhash-/Dateihashbezüge. Fehlende,
unbeobachtbare oder mehrdeutige Voraussetzungen bleiben unbekannt. Geordnete
explizite Meldungspaare können trotz anderer Lücken auf Widerspruch verglichen
werden; eine implizite Bindung braucht vollständigen und eindeutigen Ausschnitt.
Keine neue Queue, persistente Auditwelt, Ausführung, Rechte-/Budget-/Secretfreigabe
oder Stopdurchsetzung. Gemeldeter Turnabschluss, Lieferung und Review werden
niemals Projektabnahme.

Native Graph-/Inspector-/Hinweisauswahl und Text/HTML werden wiederverwendet.
Widerspruch vs. fehlender Nachweis ist DE/EN in Worten sichtbar; Ergebnis-/Entry-
Knoten bleiben gemeldet, tatsächlicher Verstoß ungeprüft. Die reale Findingansicht
verwendet keine synthetische `UIWarningDemo`-Bewertung. Die Beispieldaten sind
explizit `synthetic-aa-c02`, keine tatsächliche Agenten-/Projektabnahme.

## Gezielt geprüft

- **41 neue Python-Regelfälle**: 34 zunächst bestanden; eine Fixture hatte eine
  doppelte Keywordübergabe. Diese Testfixture korrigiert, alle sechs betroffenen
  Parametervarianten gezielt bestanden. Sechs später ergänzte Gate-/G01-Gegenfälle
  bestanden. Keine breite allgemeine v1-Testwiederholung.
- Je Regel passender/unpassender Fall: getrennte Revisionen; falscher Empfänger,
  Lauf/Task/Quellhash; fehlender/vorhandener Artefaktverweis; Stoprequested/pending
  ungleich effective; Versand vor/nach/gleich Barriere; fremder Quell-/Workflow-
  Controllerbereich, fehlende Sequenz; frühere Barriere wird durch spätere nicht
  aufgehoben. Fehlende/mehrere Bindungen und doppelte Ordinals bleiben unknown.
- Neue G01-Gegenfälle: fremder Attempt, Consumer, Actor, Requesthash oder Task
  erlaubt keine passende Gate-Referenz. Späterer/mehrdeutig geordneter Gatebeleg
  zählt nicht. 4AP-Zustimmung ist keine Reservierung; Gnomabschluss ohne Artefakt
  bleibt Beleglücke. Alles synthetisch, ohne Secret-/Bezahl-/Provideraufruf.
- **34 bestehende Workflow-Projektionsfälle einmal**: bestanden, da deren Bericht
  jetzt den neuen additiven Analyseblock enthält. Alte neutrale v1-Gesamtsuite
  nicht nochmals lokal durchlaufen.
- Swift: **5 WorkflowProjectionTests bestanden**, darunter zwei neue Fälle für
  Beleg-/Scope-/Geheimnisminimierung, unknown statt Verified, unbekanntes Schema,
  ungültige Klassifikation und >100-Findinggrenze. **1 neuer Inspectorfall**
  bestanden; nach der sichtbaren Label-/Auswahlkorrektur gezielt erneut geprüft.
- Ruff betroffene Pythondateien und Formatcheck, striktes Mypy Produkt,
  Bandit Produkt ohne Befund; nativer Quellencheck mit vollständigem DE/EN-Katalog,
  UTF-8 und unverändertem NOTIFY-only-Collector. Details der letzten Prüfung im
  Commit/PR; keine Sicherheitsgarantie daraus ableiten.
- Echte lokale SwiftPM-App auf Intel-macOS mit eigener AppKit-Viewaufnahme,
  `--report workflow-findings.json --graph-mode 0 --select warning-0`, DE 1680×960
  und EN Mindestfenster 1150×730. Kein Hostprobe/Collectorstart, keine anderen
  Sitzungen oder Berechtigungen angefasst. Ansichtspfade unten; Zahlen sind logische
  Fenstergrößen, PNG kann Retina-/Display-Skalierung enthalten.

## Originale und abgeleitete Belege

- `synthetic-source/segment-1.jsonl`: neue explizit synthetische TD-Bindung und
  Rückgabe; falsche Quellrevision/Empfänger und kein Artefaktverweis.
- `workflow-findings.json`, `.txt`, `.html`: reale Ausgabe des implementierten
  Lesers/Berichts über diese Daten. Drei Hinweise, keine tatsächliche Verifikation.
- `existing-tg-findings.json`: neue rein lesende Projektion der bereits in PR50
  versionierten Ableitung aus dem ursprünglichen synthetischen TG-C01-Beleg:
  `../seven-tools-20261018/derived-existing-tg-evidence/segment-1.jsonl`.
  Originalpin/Hash dort in `original-evidence-pin.json`, unverändert. Dieser
  Statusbeleg enthält **nur budget.checked/stop_state**, keinen geordneten
  Dispatch-/Barriere-/Gatebezug. Null fachliche Hinweise ist deshalb ausdrücklich
  **kein** Beleg, dass dieser Livekontrollweg vollständig beobachtet wurde.
- `native-de.png`, `native-en-small.png`: finale wirkliche DE/EN-Findingansicht.
  Erste Aufnahmen `*-initial.png` bleiben erhalten: dort war die alte Metrik noch
  „Structural warnings“. Die finale Ansicht benennt gemeldete Hinweise und kann
  sie über die vorhandene Auswahl anwählen; keine zusätzliche neue Warnwelt.

## Offen / Grenze

- Externe Wirkung, tatsächlicher Verstoß, Quellenidentität und Gesamtabdeckung
  bleiben UNBEKANNT, auch bei passenden Referenzen/Hashes und null Hinweisen.
- Echte TD→KB→kontrollierter Executor→Return-Abnahme erfordert die jeweiligen
  Produzenten-/Transport-/Kontrollbelege. Dieses Paket erzeugt und betreibt sie
  nicht. Keine Behauptung über beliebige CLI-/Kindprozesskontrolle.
- Der aktuelle native Reader importiert fertige Workflow-Reports; kein neuer
  Live-JSONL-/Web-/Sprachchattransport. AA-C03 ist weiterhin vom konkreten
  beauftragten Betriebs-/Transportumfang abhängig.
- Native Graphansichtexport minimiert Fakten; voller minimierter Hinweisbericht
  per CLI-JSON. Historische Forschungsarchive und Produktrolle unverändert.
- Weder Release, Runtimeaktivierung noch Nutzer-/Projektabnahme erfolgt.

## Integration und Rückweg

PR50 zuerst prüfen/integrieren, dann diesen abhängigen Folgebranch. Keine fremden
Commits überschreiben; finale Quellpins/PR stehen in der privaten Übergabe.
Bei Rücknahme ausschließlich die beiden AA-C02-Commits über Git revert entfernen;
keine Quelldatei-/Queue-/Datenbankmigration und keine Datenlöschung notwendig.
AA-C01-Berichte/ursprüngliche v1-Verbraucher bleiben unverändert nutzbar.
