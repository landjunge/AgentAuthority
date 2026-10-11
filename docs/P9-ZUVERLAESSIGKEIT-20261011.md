# P9: Fehlertriage und begrenzte Zuverlässigkeitsprüfung

Stand: 11. Oktober 2026. Technischer Abschlussbericht auf dem integrierten P8-Stand `2523568fdca3e629bfba11361c4fefba2cd2d066`. Formale P9-Paketabnahme und die Integration dieses Dokumentationspakets sind noch offen. Keine allgemeine Zuverlässigkeits- oder Produktionsfreigabe.

## Auftrag und Voraussetzungen

WB34 verlangt reproduzierbare Fehler aus P7/P8, priorisierte Ursachenprüfung, nur ausdrücklich freigegebene kleine Korrekturen, Regressionen und sichtbare Restrisiken. WB1605 erlaubt die Arbeit bedingt nach erfüllten Abhängigkeiten. P8 ist im konkret vorgelegten begrenzten Umfang abgenommen und mit PR33 integriert (direkte Nutzerantwort auf die konkrete Frage, WB1628/1630). Squash `2523568`, Parent `64bf757`, Tree `99e1d07465a780c722ca73f6d1a1e1bfe5aac48a` entspricht exakt Kandidat `ce0079d`. Remote-master bestätigt; Push-CI38115318251 und CodeQL38115318250 erfolgreich, Analyse vollständig hochgeladen und verarbeitet.

Codex führt Triage und Dokumentation aus. Gemäß ausdrücklicher Teamregel aus WB34 prüft eine zweite Codex-Instanz die Primärbelege lesend; sie bearbeitet keine Produktdateien. Groks bestehende unabhängige P7/P8-Gegenprüfungen bleiben getrennte Quellen. Kein behaupteter neuer Grok-Teamstart und keine Doppelimplementierung.

Die zweite Instanz `/root/p9_evidence_review` bestätigt nach lesender Prüfung der Originale, Quellenhashes, JUnit und Push-Logs: kein neuer aktuell offener reproduzierter Produktfehler in diesen Belegen. Code/Regressionen, unverändertes Original/Erratum und beide P8-Archive wurden getrennt geprüft. Sie hat weder Tests noch neue Modellversuche ausgeführt. Diese Teamprüfung ergänzt die vorhandene Grok-Gegenprüfung; sie ist keine neue Grok-Paketabnahme.

## Priorisierte Fehler und Erwartet/Ist

| Priorität / Befund | Reproduzierbare Erwartung und Primärbeleg | Aktueller Iststand und Entscheidung |
| --- | --- | --- |
| 1: Falsche positive Herkunft, Identität oder Beleggültigkeit | P7/P8-Matrizen: missing/stale/forged dürfen keine authentisierte Quelle erzeugen; Replay ohne aktiven Kontext STOP, abgelaufener Kontext UNBEKANNT. | Beide neuen P8-Captures erfüllen alle 15 vorherigen Erwartungen, einschließlich Host-Verifier SKIP. Herkunft und Identität bleiben UNBEKANNT. Kein neuer reproduzierter Fehler in diesen geprüften Fällen. |
| 2: P7-Modellnachweis falsch begründet, WB1611 | Originaler echter P7-Lauf meldete `belegt`, aber die Grundzeile war fest auf `fixture_ist_kein_modelllauf` gesetzt. Beide Gründe müssen dem tatsächlichen Istwert folgen. | Ursache war der konstante Berichtstext. Kleine Korrektur `a945b9d`, zwei parametrische Regressionen, unabhängig 16 gezielte Fälle bestanden; PR32 integriert. Aktuelle P8-Läufe nennen `originaler_codex_exec`. Bereits behoben, keine neue P9-Reparatur behauptet. |
| 3: Widersprüchliche Zielwirkung oder Zeitordnung bei Wiederholung | Zusätzliche echte P8-Läufe8930311534831620534/3864572638349408912, eigene Vorerwartungen, künstliches Ziel, Nachlauf5s/3s, unabhängige Zielreferenz. | Je eine Modellantwort und ein Toolbericht, Exit0, Zielreferenz calls1/present/valid/order_valid, NACH/KORREKT. Zwei einzeln konsistente Beobachtungen; keine repräsentative Stabilitätsmessung. |
| 4: CI- und Qualitätsbefunde unzutreffend als grün dargestellt | Native Push-CI und vollständig archivierte Rohlogs; nicht blockierende Qualitätsschritte separat lesen. | Zwei Pytest-Schritte je450 tatsächliche Passpunkte; Ruff28, Format21, Mypy9 bleiben offene tolerierte Qualitätsbefunde. Der erfolgreiche CI-Job bedeutet keine bestandenen Ruff-/Format-/Mypy-Einzelprüfungen. Keine pauschale Legacy-Reparatur autorisiert. |
| 5: Historische Modell- und Verfahrensgrenzen | Erhaltene negative Lab-Referenzen und P4-Entscheidung WB1597; Reparaturbelege in ausdrücklich getrennten Profilen. | Historische RC-01..05/CB-01 bleiben FAIL/MISSED-Referenzen, Remediation nur im RemediationLab, OOS-021 nur im FakeAdapter. P4 ist ACCEPTED_UNRESOLVED, damaliger Writer unbekannt. Keine globale Schließung. |

Im begrenzten geprüften P7/P8-Umfang liegt kein weiterer reproduzierter Produktfehler vor. Deshalb enthält P9 keinen neuen Laufzeitpatch, kein neues Modell und keinen erfundenen Reparaturfall. Ein unveränderter historischer OPEN-Snapshot in einem älteren Bericht ist kein neu offener Laufzeitfehler; der datierte P8-Nachtrag dokumentiert den heutigen Abschluss.

## Beleg- und Regressionsprüfung

Die Ursache des tatsächlich gefundenen P7-Fehlers ist am Original, Code und separaten Erratum nachvollziehbar. Das Original `docs/p7-runs/2026-10-11-integration/integration.json` bleibt unverändert, SHA256 `2c842519c5f6c1d41e7f5ec9cd222d6fb013aeb38db78b4318d5b4e2cdfa0eb8`. Die Korrektur ist keine rückwirkende neue Messung. `tests/test_plan_p7_integration.py::test_model_proof_reason_describes_the_actual_result` prüft `belegt/originaler_codex_exec` und `nicht_belegt/kein_modellnachweis`. Die unabhängige `label-junit.xml` enthält16 Fälle, 0 Fehler/Failures/Skips; `final-junit.xml` enthält450 Fälle mit denselben Nullwerten. Diese vorhandenen Läufe werden nicht als neue P9-Ausführungen bezeichnet.

Die bestehenden gezielten Regressionen lassen sich mit Python3.12 und den Projekt-Testabhängigkeiten aus dem Repository reproduzieren: `python -m pytest -o addopts='' -p no:cacheprovider tests/test_plan_p7_integration.py -q`. Das sind Tests mit kontrollierten lokalen Werkzeugen/Protokoll-Fixtures, kein echter Modellnachweis. Der Befehl ist hier eine Reproduktionsanleitung, keine zusätzlich ausgeführte P9-Messung. Ein archivierter Capture darf nicht als neuer aktiver positiver Nachweis gewertet werden; der vorhandene Replay-Test verlangt STOP.

Die P8-Archive im Repository stimmen byteweise mit den Originalen überein: 21 Dateien einschließlich16 Laufdateien. Cohorterwartung SHA256 `3b137851bcae557e23cd0e6fc673aa4e4358a5cc72e0784884f5872a23a7e3cf`; die beiden Lauferwartungen blieben unverändert. Grok prüfte unabhängig die konkreten Läufe (WB1622), die Veröffentlichung (WB1625) und Rohlogs/Archiv (WB1626/1627). Keine zusätzliche Modellwiederholung und kein neues Provider- oder Actor-Authentisierungszeugnis.

Die tatsächliche Push-CI am P8-Squash läuft zweimal über denselben unveränderten Testbaum und enthält je450 erfolgreiche Fortschrittsmarken. `pytest -q` zusammen mit `addopts = -q` unterdrückt die allgemeine Sammelzeile. Eine wörtliche Zeile `450 passed, 5 deselected` steht dort nicht. Die fünf historischen RC-Abwahlen folgen aus der unveränderten `tests/realcase/conftest.py` und früheren lokalen Protokollen; das JUnit enthält keine Deselection-Zählung. Fortschrittsmarken, lokale Sammelzeilen und JUnit werden als unterschiedliche Belege behandelt.

P9 vergleicht die Quellen gegen die vorab gesicherten215 Dateien des P8-Squash. Nur neue Dokumentation und datierte Nachträge werden veröffentlicht; Laufzeitcode, Tests, ursprüngliche Matrizen und Messdateien bleiben unverändert. Eine zusätzliche identische lokale Gesamtsuite erzeugt hier keinen neuen Erkenntnisgewinn. Die Remote-Prüfungen des konkreten Dokumentationskandidaten werden separat archiviert.

## Verbleibende Grenzen und Paketentscheidung

D-012 bleibt bindend: beobachten, analysieren, warnen; keine operativen Gates, Rechte, Secrets, Budgets oder Permits. Beobachtungen belegen lokale Beziehungen und tatsächliche künstliche Zielwirkung in begrenzten Fenstern. Sie authentisieren weder Provider noch Actor, beweisen keine dauerhafte Ressourcenidentität oder universelle E2-Bereinigung und begründen keine reale Agentenüberwachung. Ein gemeldetes Ende beweist keine Wirkungsfreiheit. Host-Verifier SKIP ist kein positiver Host-Nachweis.

Historische Sicherheitslücken, profilgebundene Remediation, Qualitätsaltlasten und P4s akzeptiertes ungeklärtes Restrisiko bleiben ausdrücklich sichtbar. Es gibt keine weitere kleine Korrektur mit nachgewiesenem Fehler als Voraussetzung. Der technische P9-Bericht kann im dokumentierten Umfang zur Paketentscheidung vorgelegt werden; formale P9-Abnahme und konkrete Integration folgen nicht automatisch aus WB1605 oder grünen Tests. Kein P10 ohne Auftrag.

Primärbelege, Quellenhashes, Teamprüfung, Befehle und Remote-Readbacks: `/Users/landjunge/.threaddesk/artifacts/agent-authority/p9-reliability-20261011/`. Der frühere P8-Merge-Nachweis liegt separat unter `pr33-merge-20261011/`.
