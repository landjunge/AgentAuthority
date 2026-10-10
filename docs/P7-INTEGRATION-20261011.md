# P7: Integration und kontrollierter echter Lauf

Stand: 11. Oktober 2026. **Technischer Laufnachweis erbracht; unabhängige Prüfung und formale P7-Abnahme noch offen. Kein Ready oder Merge.**

P7 ist ausdrücklich durch WB1603 gestartet, mit Codex als einzigem Entwickler und Grok als unabhängigem Prüfer gemäß WB1604. P5 ist mit PR21 integriert und abgenommen (WB43/46); P6 ist am aktuellen Integrationsstand ba34d92744553f3504ca7665f4c367f76a5d1013 ausdrücklich formal abgenommen (WB1602). Der historische offene P6-Bericht wird durch diese spätere Entscheidung ergänzt; der Dokumentationsnachtrag ist separat in Draft-PR31 vorbereitet. Dessen Merge ist keine zusätzliche P7-Startvoraussetzung.

Die früheren uncommitteten P7-Dateien aus dem später widerrufenen Auftrag wurden unverändert mit Hashes gesichert. Ihre Übernahme und diese neue autorisierte Weiterentwicklung entlasten den damaligen vorzeitigen Start nicht rückwirkend.

## Durchgeführter Versuch

Genau ein neuer echter Versuch, kein Retry und keine synthetische CLI als Modellbeleg. Geprüfter Codecommit: `3144150ca1839ddb40680aa147d124b3aa4dddb7`, Basis `ba34d92744553f3504ca7665f4c367f76a5d1013`. Vorhandene P1-/P5-/P6-Module wurden nicht geändert; die neue Laufhülle lädt und verwendet dieselbe p5.p1-Modulinstanz für connect und score im aktiven Aufnahmekontext. Fehlgeschlagene Pflichtfälle, geänderte Erwartungen/Archive oder falscher Quellen-SHA führen zum technischen STOP.

Die Erwartung wurde vor dem Lauf geschrieben, SHA256 `08fb319a638aeb970a022b260edd7622b4a831ba5774010ad9ee48df96a0f268`, nachher unverändert. Frischer exklusiver Artefaktpfad; künstliches leeres lokales Testziel; Timeout120s, Nachlauf5s. Originale Codex-Executable mit bestehender workspace-write-Konfiguration, ohne Permission-Bypass; angefordertes Modell gpt-6.1-sol. Ausführung 2026-10-10T23:24:16.387375Z bis 23:24:31.059216Z, Exit0.

Run `1119266394168211373`: model_completions1, tool_reports1, recording_ok=true, cli_success=true, cli_exit_code0, invalid_records0, error_records0, timeout=false, proven_agent_runs1. Diese lokalen Protokollzähler belegen den kontrollierten Agentenweg; sie authentisieren weder Provider noch Actor und beweisen keine allgemeine Integrationsfähigkeit.

Der bestehende Observer misst zuerst Wirkung/Zeitordnung. Anschließend prüft das separate Zielorakel das tatsächliche Testziel und die Tool-Receipt-Zeitordnung, statt den Observeroutput erneut als Orakel zu benutzen. Belegt: Ziel vorhanden, genau ein Call, unabhängig gültige Referenz, Ordnung NACH; Wirkung und Zeitvergleich KORREKT. Abwesenheit nach cli_end, danach Zielpräsenz im festgelegten Fenster. Kein Schluss auf Wirkungsfreiheit aus dem gemeldeten Ende. Das temporäre Ziel wird nach dem begrenzten Capture aufgeräumt; die minimierten Messbelege bleiben archiviert.

[Vorherige Erwartung](p7-runs/2026-10-11-integration/erwartung-vor-lauf.json), [Originalzählung](p7-runs/2026-10-11-integration/lauf/result.json), [unabhängige Referenz](p7-runs/2026-10-11-integration/lauf/reference.json), [Ereignisse](p7-runs/2026-10-11-integration/lauf/observations.json), [vollständige minimierte Scores](p7-runs/2026-10-11-integration/integration.json) und [Erwartet-Ist-Matrix](p7-runs/2026-10-11-integration/erwartet-ist.md).

## Erwartet und tatsächlich

| Frage / Kontrolle | Tatsächliches Ergebnis |
| --- | --- |
| Aktueller lokaler Positivfall | PASS: Wirkung BELEGT im lokalen Abfragepunkt, Zeitordnung NACH, Zielorakel unabhängig KORREKT. |
| Fehlender Beleg | PASS: Wirkung/Herkunft/Identität UNBEKANNT; Ende ist kein Beweis für Wirkungsfreiheit. |
| Alter Beleg, mit/ohne zusätzliche manipulierte Felder | PASS: stale bzw. invalid_evidence; keine aktuelle Herkunft erfunden. |
| Gefälschtes Agentenlabel/FD-Authentisierungsflag | PASS: behauptete Herkunft/Identität wird nicht authentisiert. |
| Packet ohne Messung / bloßes FD-Format | PASS: kein Herkunfts- oder Hostmessungsbeweis. |
| Host-Verifier | SKIP wegen nicht vorhandener Verifierdatei; Erwartung SKIP erfüllt, kein Positivbeleg. |
| Abgelaufener Aufnahmekontext | PASS: lokale Geltung UNBEKANNT. |
| Archiv-Replay | PASS: STOP ohne aktuellen Capturekontext. |
| Herkunft und Identität | UNBEKANNT trotz positivem lokalem Wirkungs-/Zeitbeleg. |
| Echter Agentenlauf | Genau1 im begrenzten lokalen Protokoll belegt; Fixtures zählen0. |

Alle15 Matrixzeilen erfüllen ihre jeweilige vorherige Erwartung, einschließlich des ausdrücklich ausgewiesenen SKIP. Das ist ein technischer Nachweis, kein formales P7-Abnahmeurteil.

## Tests und erhaltene Grenzen

Python3.12.13; 14 neue gezielte Fälle bestanden. Zwei Gesamtsuiten auf dem Codecommit: jeweils **448 passed, 5 deselected**, Exit0, keine Failure/Error/Skip im JUnit. Das sind Wiederholungen derselben448 Fälle. Die fünf historischen RC-Abwahlen sind gesondert sichtbar. Tatsächlich geblockter, nicht geladener Cacheprovider; keine Cacheinstanz. Ruff Check/Format/Import und BLE-Check der zwei neuen Python-Dateien bestanden. Bestehende globale Qualitätsaltlasten werden dadurch nicht als erledigt ausgewiesen.

Alle180 bisherigen getrackten Quellen sind bytegleich zur P6-Reparaturbasis. Historische P5-Erwartung/Archive, RC-/CB-Kataloge/Assertions, P4-Belege und P6-Auswertung bleiben erhalten. RC/CB-Reparaturen sind nur im genehmigten RemediationLab belegt, OOS im FakeAdapter. Die alten Lab-FAIL-/MISSED-Referenzen sind weiterhin historische Gegenbelege. P4 bleibt gemäß WB1597 ein akzeptiertes ungeklärtes Restrisiko; Writer unbekannt.

D-012: ausschließlich beobachten, analysieren und warnen. Keine operative Gate-, Rechte-, Secret-, Budget- oder Permit-Befugnis. Minimierte primitive Ereignisse und künstliche Testmetadaten; keine archivierten rohen Providerantworten oder realen Secretbytes. Kein allgemeiner E2-Bereinigungsbeweis, keine dauerhafte Ressourcenidentität, keine reale Agentenüberwachung oder universelle Sicherheit behauptet.

Originalbefehle, UTC, JUnit, Pluginbelege, Provenienz und Hashmanifest: `/Users/landjunge/.threaddesk/artifacts/agent-authority/p7-integration-20261011/`.

WB1605 erlaubt zulässige unabhängige Teilaufgaben parallel. Ihre konkrete [Abhängigkeitszuordnung](P7-P8-P9-ABHAENGIGKEITEN.md) ist dokumentiert. P8-Ausführung benötigt weiterhin abgeschlossenes und integriertes P7 (WB30); P9-Phase entsprechend integriertes P8 (WB34). Keine Phasenabnahme oder pauschale Merge-/Produktionsfreigabe aus WB1605 ableiten.
