# P8: begrenzter Praxistest am integrierten P7

Stand: 11. Oktober2026. **Zwei echte kontrollierte Läufe bestanden; unabhängige Prüfung und formale P8-Abnahme noch offen. Kein Ready/Merge.**

Grundlage: P7 formal im vorgelegten Umfang abgenommen und PR32 auf master64bf757ee7e32ca3df780b61a698466e2e299899 integriert, einschließlich erfolgreicher tatsächlicher Push-CI/CodeQL (WB1619). Bedingte Nutzerfreigabe WB1605 erlaubt damit die in WB30 definierte P8-Arbeit. Codex übernimmt die alleinige Umsetzung in bestehender Kontinuität; Grok prüft unabhängig. Kein neuer Observer oder verändertes Produktmodell.

Vor der Ausführung wurden die vollständigen193 vorhandenen Quellen gehasht und beide Versuche mit künstlichem lokalem Ziel, Timeout120s und Nachlauf5s/3s festgelegt. [Cohorterwartung](p8-runs/2026-10-11-stability/P8-EXPECTATION-BEFORE-COHORT.json), Hash3b137851bcae557e23cd0e6fc673aa4e4358a5cc72e0784884f5872a23a7e3cf, und [Ausführungsbindung](p8-runs/2026-10-11-stability/P8-PRE-RUN-LOCK.json) entstanden vor beiden Läufen. Zusätzlich wurde jede eigene Lauf-Erwartung vor ihrer Ausführung geschrieben, nachher unverändert. Genau zwei neue tatsächliche Versuche, kein Retry, keine Fixture als Modellnachweis.

Die unveränderte P7-Laufhülle verbindet p5.p1.connect und p5.score in derselben Modulinstanz und im aktiven Capturekontext. Ihre bestehenden phase/step=P7- bzw. P5-Felder bleiben originale Runnerdaten; der äußere dokumentierte Cohortauftrag ist P8. Keine Umbenennung eines alten Laufes in einen neuen Nachweis. P7s ursprünglicher Versuch wird nicht zu diesen zwei P8-Versuchen gezählt.

| Tatsächlicher Lauf | Nachlauf | Modellabschlüsse / Toolberichte / Exit | Wirkung / Ordnung / Vergleich | Herkunft und Identität | Vorherige Matrixerwartung |
| --- | --- | --- | --- | --- | --- |
| 8930311534831620534 | 5s | 1 / 1 / 0 | BELEGT / NACH / KORREKT | UNBEKANNT | 15 erfüllt, Host-Verifier SKIP |
| 3864572638349408912 | 3s | 1 / 1 / 0 | BELEGT / NACH / KORREKT | UNBEKANNT | 15 erfüllt, Host-Verifier SKIP |

Pro Lauf: recording_ok=true, cli_success=true, kein Timeout, keine invalid/error_records; genau eine tatsächliche Zielwirkung im unabhängigen Zielorakel (calls1, target_present=true, valid=true, order_valid=true). Abwesenheit nach gemeldetem Ende, anschließend Zielpräsenz im begrenzten Fenster; Ordnung NACH und Vergleich KORREKT. Das Zielorakel prüft tatsächliches Ziel und Tool-Receipt, nicht nur den Observeroutput. Temporäre Ziele werden nach Capture aufgeräumt; minimierte Belege bleiben. Ein Ende beweist keine Wirkungsfreiheit.

[Getrennte Originalergebnisse](p8-runs/2026-10-11-stability/P8-COHORT-RESULT.json) und [erster](p8-runs/2026-10-11-stability/actual-run-01/integration.json)/[zweiter](p8-runs/2026-10-11-stability/actual-run-02/integration.json) vollständiger minimierter Score. Beide tatsächlichen Ausführungen verwenden dieselbe gepinnte Codebasis und unterschiedliche begrenzte Nachlaufzeiten. Run-IDs sind verschieden. Bei Wirkung, Zeitordnung, Herkunft und Rückweisungen zeigt diese kleine Cohort keinen Widerspruch. Zwei erfolgreiche Läufe liefern keine repräsentative Trefferquote oder allgemeine Zuverlässigkeit.

| Vorherige Kontrollfrage, pro Lauf ausgewertet | Tatsächliches Ergebnis in beiden Läufen |
| --- | --- |
| Aktueller positiver lokaler Relationsfall | PASS: Wirkung BELEGT am lokalen Abfragepunkt; unabhängige Zeitordnung NACH. |
| Missing / stale / zusätzliche manipulierte Felder | PASS: ungesicherte Aussage und Herkunft bleiben UNBEKANNT; archive-only ist nicht aktuell. |
| Gefälschtes Agentenlabel oder Authentisierungsflag | PASS: keine erfundene Herkunft oder Identität. |
| Unvermessener Packet-/FD-Formatbeleg | PASS: keine globale Ressourcen- oder Quellenauthentisierung. |
| Host-Verifier | SKIP ausdrücklich erwartet, kein Positivbeleg. |
| Replay ohne Kontext / abgelaufener Kontext | STOP / UNBEKANNT, jeweilige vorherige Erwartung erfüllt. |
| Echter lokaler Agentenweg | Je1 Modellabschluss und1 Toolbericht aus ursprünglicher CLI; Fixturefalse, Grund originaler_codex_exec. Provider/Actor bleiben unauthentisiert. |

Erwartungshashes vor/nach jedem Lauf: cf899efd708b99e20e920441b8cb7057950cf483a032661ae6c3dc9419aa44c0 und4c832dbbed740de94410edb0c37e734c3f4b6d7744c61a1b608afc83a3ea577f. Alle193 vorher vorhandenen Quellen waren während und nach den Versuchen bytegleich. Für die Veröffentlichung wird nur dieser Bericht, die neuen P8-Belege und ein ausschließlich ergänzender P7-Abschlussnachtrag geschrieben; Laufzeitcode und Tests bleiben unverändert.

Die bestehende P7-Regression ist am identischen Laufzeitcode belegt: Codex zweimal450PASS/5historischeRC-Abwahlen, Grok450PASS/5Abwahlen, erfolgreiche Push-CI ebenfalls zweimal450. Keine identische lokale Gesamtsuite zusätzlich wiederholt; PR-Pflichtchecks werden am veröffentlichten Dokumentationsstand separat geprüft. Weitere nachgewiesene neue Produktfehler in diesen beiden Versuchen: keine.

D-012 gilt: beobachten, analysieren, warnen; keine operative Gate-, Rechte-, Secret-, Budget- oder Permit-Befugnis. Nur künstliche Testdaten und minimierte Felder, keine rohen Providertexte oder Secretbytes. Kein allgemeiner E2-Bereinigungsbeweis, keine dauerhafte Ressourcenidentität, keine universelle Sicherheit oder reale Agentenüberwachung. Historische RC/CB-FAIL-/MISSED-Referenzen bleiben; Reparaturnachweise nur im RemediationLab und OOS im FakeAdapter. P4 bleibt akzeptiertes ungeklärtes Restrisiko (WB1597), damaliger Writer unbekannt.

Primärbelege/Befehle/UTC/Quellenhashes: `/Users/landjunge/.threaddesk/artifacts/agent-authority/p8-stability-20261011/`. Formale P8-Abnahme und konkrete Integration sind nicht aus dem Startauftrag oder diesen Messungen abgeleitet. Die P9-Phase benötigt gemäß WB34 ein erfolgreich abgeschlossenes, geprüftes und nach master integriertes P8; unabhängige bereits zulässige Vortriage gemäß WB1605 bleibt möglich.

## Nachtrag: unabhängige Prüfung, P8-Abnahme und Integration

Stand dieses Nachtrags: 11. Oktober 2026, nach Abschluss von PR33. Die oben
stehenden OPEN-/Draft-Aussagen dokumentieren den damaligen Veröffentlichungsstand.
Grok hat die beiden Läufe und Primärbelege unabhängig bestätigt (WB1622/1625),
anschließend Archiv und Logs gegengeprüft (WB1626/1627). Keine weitere Modellmessung.

Die direkte Nutzerantwort „sinnvoll weiter“ auf die konkrete P8-Abnahme-/PR33-
Integrationsfrage erlaubt die vorgelegte begrenzte Paketabnahme und reguläre
Integration (Kontext und Wortlaut archiviert, WB1628). Ready und Squash mit
Match-HEAD `ce0079d8c250e655e979e237047953b103c58890`, kein Admin/Force/Bypass.
Squash `2523568fdca3e629bfba11361c4fefba2cd2d066`, Parent `64bf757`, Tree
`99e1d07465a780c722ca73f6d1a1e1bfe5aac48a` exakt Kandidat; Remote-master bestätigt.

Push-CI38115318251 und CodeQL38115318250 sind erfolgreich (WB1630), Upload
vollständig verarbeitet. Je450 erfolgreiche Pytest-Fortschrittsmarken in beiden
Schritten; die Sammelzeile ist wegen zweier Quiet-Stufen unterdrückt. Fünf
historische RC-Abwahlen sind durch unveränderte Conftest/ältere lokale Logs
belegt, nicht als wörtliche Push-Logzeile. Ruff28/Format21/Mypy9 bleiben
tolerierte offene Einzelprüfungen. Originale/API/Befehle/UTC/Hashes liegen unter
`/Users/landjunge/.threaddesk/artifacts/agent-authority/pr33-merge-20261011/`.

P8 ist formal im vorgelegten Umfang abgenommen und integriert. Keine allgemeine
Zuverlässigkeits-/Produktionsfreigabe; D-012 und alle genannten Grenzen bleiben.
Damit ist die P9-Startbedingung aus WB34 erfüllt; bedingte Arbeit nach WB1605 ist
zulässig. Das erteilt keine P9-Paketabnahme oder weitere pauschale Mergefreigabe.
