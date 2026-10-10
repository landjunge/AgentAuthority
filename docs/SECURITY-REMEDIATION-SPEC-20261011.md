# Reparaturspezifikation zu Nutzerfreigabe WB1098

Quelle: Whiteboard `833554dffb6e`, Entscheidung `2f7fcbc9daab` vom
2026-10-10T22:07:12Z. Ausgangsstand: `21691ae9817f832ecfb111f980b0c8a3e6b63d61`.
Arbeitszweig: `codex/security-remediation-20261011`.

Die Freigabe umfasst RC-01 bis RC-05, OOS-021 und CB-01 im lokalen Fake-Lab.
Agent Authority bleibt gemäß D-012 Beobachter: keine operative Gate-, Rechte-,
Secret-, Budget- oder Permit-Befugnis. Keine echte Shell, MCP-Verbindung,
Publikation oder Credential-Verarbeitung. P4-Verfahrensvorbehalt, formale
P6-Abnahme und P7 bis P9 bleiben offen. Keine Merge-/Produktionsfreigabe.

## 1. Eingefrorene Ausgangsbelege und Profilgrenze

Originalquellen: REAL-CASE-TRANSFER-STUDY-v1 Abschnitt 5.3,
OUT-OF-SCOPE-DEBT OOS-020/021, FINDING-PHASE1-FINISH-ADAPTER-EFFECT-GAP,
tests/realcase/catalog.py, tests/convergence/catalog.py und score.py.
RC-01 bis RC-05 sind am Ausgangsstand rot, OOS-021 ist rot, CB-01 ist MISSED.
Die zwei unabhängigen unveränderten Prüfläufe am exakten Ausgangsstand sind
unter `p6-acceptance-review-20261010/` archiviert; sie werden nicht wiederholt.

Das historische `Lab` mit truthy Token und der historische CB-MISSED-Test
bleiben Referenz. Das neue explizite Forschungsprofil `RemediationLab` prüft
dieselben eingefrorenen ActionRequests gegen gebundene Zustimmung. Ein PASS
des historischen MISSED-Tests zählt weiterhin nicht als Reparatur.
Die unveränderten RC-Sicherheitsassertions werden zusätzlich mit Austausch
nur des Lab-Konstruktors gegen RemediationLab ausgeführt. Kein Umschreiben
von Katalog, Sink, Assertion oder alter Ergebnisdatei.

## 2. Gebundene Zustimmung und Steuerungsressourcen

RemediationLab bleibt eine deterministische, in-memory Fake-API. Nur ein
vertrauenswürdiger Versuchskoordinator kann `approve(request)` aufrufen;
das ist kein Agentenrequest und kein menschlicher/cryptographischer Beleg.
Der ausgegebene lokale Handle wird im Lab gespeichert und gebunden an
Actor, Workflow-Eintrag/Generation, exakte Aktion, kanonische Ressourcenidentität
und einen kanonischen JSON-Digest aller Parameter außer approval_token.
Nicht endliche oder nicht JSON-fähige Parameter werden begrenzt abgewiesen.
Die Gültigkeit ist kurz (maximal 300 Sekunden) und einmalig. Finish verwirft
die Generation samt Handles. Pro Workflow höchstens 64 aktive Handles.
Eine Ablehnung wegen bestehender Invarianten verbraucht keine Zustimmung.

Gebundene Zustimmung ist zusätzlich erforderlich für:

- Mutationen an `.vscode/settings.json`, `.cursor/mcp.json` und
  `.cursor/rules/mcp.json`, einschließlich kanonischer Pfadvarianten;
- die simulierten Effekte `shell.exec`, `mcp.start`, `cache.poison`;
- irreversible Fake-Aktionen und Sicherheits-Testmutationen, für die das
  historische Modell einen truthy approval_token akzeptiert.

I1 bis I9 bleiben mindestens ebenso streng: keine Zustimmung überschreibt
Budget, Delegationsgrenze, Netzverbot oder unveränderliche Policy. Harmloses
Lesen/Schreiben außerhalb dieser Steuerungsgrenzen bleibt möglich. Das ist
kein globales Default-Deny als Ersatz für eine Effekt-/Zustimmungsbindung.
Andere unbekannte Verben bleiben eine separat sichtbare Modellgrenze;
eine Behauptung über reale Adaptervollständigkeit wird nicht abgeleitet.

RC-03/04 brauchen zusätzliche Kontrollen mit zunächst gültiger Zustimmung:
eine Parameter-/Commandänderung und Handle-Replay werden dann am gebundenen
Mechanismus abgewiesen. RC-05 erhält einen direkten Test für einen gestohlenen,
nicht ausgestellten Handle. CB-01 wird sowohl unverändert ohne gültige
Zustimmung als auch mit gültiger Zustimmung nur für die erste Aktion geprüft.
Eine andere Actor-/Workflow-/Generations-/Ressourcen-/Aktionsbindung genügt nicht.

## 3. Atomarer Fake-Adapter-Effekt (OOS-021)

Ein ALLOW aus submit bezeichnet weiterhin die Entscheidung, nicht den
vollzogenen Effekt. Lab registriert pro Entscheidung ein internes, einmaliges
Commit-Ticket am konkreten Workflow-Eintrag. FakeAdapter schreibt/löscht nur
über einen Commit unter dessen Lock. Finish wartet auf einen begonnenen Commit
oder retiert den Eintrag vor einem späteren Commit. Eine nach Finish freigegebene
alte Entscheidung darf keine FakeRepo-Wirkung erzeugen, auch bei gleicher
Workflow-ID in einer neuen Generation. Ein neues Decision-Objekt, ein anderes
Lab, eine geänderte Entscheidung oder ein bereits verbrauchtes Ticket genügt nicht.
`effect_committed` berichtet den tatsächlichen Effekt getrennt von `allow`.

Die unveränderte deterministische OOS-021-Probe muss bestehen. Zusätzlich:
DENY ohne Repo-Mutation; finish(unknown) ohne Allokation; zwei Commits desselben
Tickets höchstens einmal; Generation-Reuse ohne alten Effekt; Finish wartet auf
den gestarteten Commit; verschiedene Workflows blockieren einander nicht.
Der externe Entscheidungs-Emitter bleibt außerhalb des Workflow-Locks.

## 4. Abnahme des Reparaturkandidaten

1. Spezifikation und Ausgangshashes vor Implementierung archivieren.
2. Unveränderte fünf RC-Assertions gegen RemediationLab, ursprüngliche OOS-021-
   Probe und gebundene CB-01-Kontrollen bestehen. Harmloser FP-Innenraum und
   legitim neu ausgestellte Zustimmung bestehen; RC-06 bis RC-10 bleiben grün.
3. Alle alten Dateien/Kataloge/Archive und Tests bleiben unverändert, außer den
   isoliert beschriebenen Lab-/Adapter-Erweiterungen und neuen Reparaturtests.
   Bestehende komplette Suite, gezielte P6-Prüfung und Lifecycle-Rennen bestehen.
   Geänderte Python-Dateien haben eigene Ruff-/Format-/Mypy-Nachweise.
4. Grok prüft unabhängig am exakt gepinnten Kandidaten Originaltests, Mechanismen,
   legitime Kontrollen, Diff und Grenzen. Review ist erst mit Originalbelegen
   erledigt. Codex dokumentiert Ergebnis und verbleibende Grenzen append-only.

100 Prozent bezeichnet ausschließlich diese Kandidatenprüfung, nicht formale
P6-Abnahme. Publikation/Integration wird durch diese Spezifikation nicht freigegeben.

## Umsetzungsergänzung aus Groks Spezifikationsprüfung WB1170

Die Uhr ist für deterministische Ablaufzeitkontrollen injizierbar; normal wird
time.monotonic verwendet. Die alte Workflow-ID wird nach Finish erneut benutzt,
um die Eintrags-/Generationsbindung tatsächlich zu prüfen. Ein Commit-Ticket
wird vor dem Callback verbraucht: Bei einer Callback-Ausnahme wird der Fehler
weitergegeben, effect_committed bleibt false und ein Replay bleibt abgewiesen.
Das ist eine At-most-once-Grenze, keine Rollback-Transaktion für beliebige,
teilweise ausgeführte Callbacks. Die FakeAdapter-Callbacks sind einzelne lokale
Dictionary-Mutationen. Es wird keine atomare reale Adaptertransaktion behauptet.
Die vorher archivierte Spezifikation behält ihren ursprünglichen Hash.
