# Unveränderter Observer: vorhandener Finish-/Späteffekt-Fall

8. Oktober 2026. **Gesamturteil: INCONCLUSIVE.** Der vorhandene Grundfall ist im
einmaligen Lauf erneut unabhängig belegt. Eine Erkennung durch den aktuellen
Observer ist nicht nachgewiesen: Er akzeptiert den vorhandenen Lab-Export nicht
und hat für A/B/C keine implementierten Abfragen. Das sind gemessene
Schnittstellengrenzen, keine drei richtigen Unbekannt-Antworten des Observers.

## 1. Teststand und Vorabvertrag

- Ausgangsstand: `2ff7d1497d681f4d7b4be39945ec5688356693f2`.
- Tatsächlicher Ausführungscommit, einschließlich eingefrorener Testhilfen:
  `9e0efbd0d6ce2f9bd592dc5ef89dfc6a518fb1c1`.
- [Vorabvertrag](OBSERVER-FINISH-LATE-EFFECT-CONTRACT-2026-10-08.md) vor dem Lauf
  committed, gepusht und mit `git ls-remote` unter demselben vollständigen SHA
  bestätigt. Branch: `research/observer-finish-late-effect-2026-10-08`.
- Observer unverändert: **JA**. Vorhandene Probe unverändert: **JA**. Alle 77 im
  [Freeze-Manifest](observer-finish-late-effect/2026-10-08/frozen-integrity.json)
  aufgeführten vorhandenen Dateien und beide vorab eingefrorenen Hilfen waren
  nach Probe und Standardsuite hashgleich. Kein historischer Befund überschrieben.
- Python 3.12.14, pytest 9.1.1, vorhandene Umgebung; keine Installation erforderlich.

Vollständig gelesene Mindestquellen: [Fallblatt](OBSERVATION-CASE-FINISH-LATE-EFFECT.md),
[Originalbefund](FINDING-PHASE1-FINISH-ADAPTER-EFFECT-GAP.md),
[OOS-021](OUT-OF-SCOPE-DEBT.md), [Methodik](RESEARCH-METHOD.md),
[Originalprobe](../probes/test_finish_adapter_effect_atomicity_probe.py),
[Observercode](../observer_research.py), sein Bauplan, Ergebnis und Verifikation;
zusätzlich vorhandener G3-Emitter, Lab-Lifecycle und FakeAdapter.

**Testspezifische Hilfsmittel:**
[passive pytest-Aufnahme](../probes/finish_observer_case_capture.py) und
[getrennter Antwortaufruf](../probes/finish_observer_case_responses.py).
Die Aufnahme liest vorhandene lokale Checkpoints mittels Python-Tracing; sie
ersetzt keine Methode, Assertion, Synchronisation oder Entscheidung. Diese
Referenzdaten sind keine neuen Observerevents. Der Antwortaufruf liest nur die
unveränderten G3-Zeilen. Er enthält keinen Ground-Truth-Leser und keinen
Schemaübersetzer. Der vorhandene Export wurde über seinen bestehenden Flag
ausdrücklich aktiviert. Tracing und Export-I/O beeinflussen Laufzeit; kein
früherer Timeout oder Aufnahmefehler trat auf. Vollständige FakeRepo-Dumps und
Inhalte wurden nicht archiviert (`--tb=no`, keine `longrepr`-Aufnahme).

Methodische Unabhängigkeit: Referenz aus dem synchronisierten Probe-Zustand,
nicht aus Observeraussage oder Statusmeldung; interner Level-1-Test mit
zusätzlichem lesendem Methoden-/Artefaktreview, kein externer Audit. Prozessuale
und funktionale Datentrennung, keine Isolation gegen einen böswilligen Tester.

## 2. Tatsächliche Ground Truth

Beleg: unveränderte Probe und separat gespeicherte
[Referenzcheckpoints](observer-finish-late-effect/2026-10-08/ground-truth/checkpoints.json).
Die Reihenfolge folgt den vorhandenen Threading-Events und den tatsächlich
erreichten Assertions, **nicht** der Log-Ankunft oder den G3-Zeitstempeln.

| Schritt | Tatsächlicher Beleg im einmaligen Lauf |
|---|---|
| 1. `file.write` wurde eingereicht. | Eintritt in die originale `submit_then_pause`-Funktion mit Actor `agent-a`, Workflow `wf-finish-effect-gap`, Ressource `src/late.py`. |
| 2. Lab gab ALLOW zurück. | Originales `submit` war zurückgekehrt; dessen `decision.allow is True`-Assertion war bestanden, bevor `authorized` gesetzt wurde. Historische Fake-Lab-Entscheidung, keine Produktbefugnis. |
| 3. Adaptereffekt war vor der Änderung angehalten. | Coordinator hatte `authorized.wait` erfolgreich passiert; `release_effect` war nicht gesetzt, Worker lebte, Ziel fehlte. Der originale Wrapper konnte seine Entscheidung noch nicht an den Adapter zurückgeben. |
| 4. `finish()` kehrte erfolgreich zurück. | Tatsächlicher Rückgabewert `True` plus erreichte Probe-Zeile 48 nach der bestandenen `finish(...) is True`-Assertion. Live-Workflow danach nicht mehr registriert. |
| 5. Ziel fehlte weiterhin. | Zielprüfung nach Rückkehr war `False`; die originale Abwesenheitsassertion war vor Zeile 50 bestanden. Release weiterhin nicht gesetzt. |
| 6. Adapter wurde freigegeben. | Bestehendes `release_effect.set()` zwischen Zeilen 50/51; Worker passierte sein originales Release-Wait erfolgreich. Keine zusätzliche Freigabe eingeführt. |
| 7. Schreibvorgang endete. | Originales Join, Worker-Fehlerprüfung und ALLOW-Resultprüfung waren vor Zeile 58 bestanden; Worker nicht mehr aktiv, Fehlerliste leer, genau ein ALLOW-Resultat. |
| 8. Ziel war danach vorhanden. | An Zeile 58 `target_present=True`; die originale letzte Abwesenheitsassertion schlug genau dort mit `AssertionError` fehl. |

**Ein Probeaufruf, ein Schreibworker, ein eingereichter Request.** pytest:
Setup bestanden, Call fehlgeschlagen, Teardown bestanden; Exit 1. Der
[Originalausgang](observer-finish-late-effect/2026-10-08/original/probe-pytest.log)
enthält `1 failed in 0.12s`. Der bekannte OOS-021-Befund bleibt ausdrücklich rot.
Kein zusätzlicher Ausführungs- oder Referenzfehler wurde gemessen.

Die Zuordnung dieses Effekts zur einzigen originalen Write-Ausführung ist in
dieser lokalen Referenz belegt. Sie ist keine vom Observer erhaltene
Action-/Attempt-/Generation-Referenz und kein Nachweis verteilten Vollzugs.
`src/late.py` bezeichnet hier ausschließlich einen FakeRepo-Dictionaryeintrag,
keine echte Datei und kein realer Agentenlauf.

## 3. Tatsächliche Observer-Eingangsdaten

[Originale G3-JSONL](observer-finish-late-effect/2026-10-08/original/authority-events.jsonl):
**2 tatsächliche Envelopes, 1.238 Bytes**, unverändert angeboten:

| Event | Vorhandene Angaben zum Vorgang |
|---|---|
| `authority.requested` | `file.write`, `src/late.py`, `wf-finish-effect-gap`, Actor `agent-a`, Entscheidung `ALLOW`. |
| `authority.allowed` | Dieselbe Action-/Ressourcen-/Workflow-/Actorbezeichnung, Entscheidung `ALLOW`. |

Exakte vorhandene Felder: `schema_version`, `event_id`, `timestamp`, `trace_id`,
`span_id`, `workflow_id`, `project_id`, `source_tool`, `event_type`, `actor`
(`agent_id`, `role`), `action`, `resource`, `decision`, `reason_code`,
`previous_event_hash`, `data_labels`, `event_hash`. Alle Werte und vorhandenen
IDs bleiben in der Originaldatei erhalten. Kein Feld wurde ergänzt, entfernt,
umbenannt oder als native Observerlaufnummer interpretiert.

Beide Zeitstempel lauten `2026-10-07T22:49:26Z` (UTC). Sie sind echte sekundengenau
erzeugte Emitterzeiten für zwei **nach der Entscheidung** erzeugte Meldungen;
kein Timestamp ist eine Finish-Rückkehrzeit oder ein Effect-Commit-Zeitpunkt.
Die beiden `span_id`-Werte sind verschieden und werden vom Emitter separat
erzeugt. Die Hashkette verbindet die exportierten Meldungen, nicht einen
unaufgezeichneten Effekt mit seiner Ausführung.

Der gleiche Exporthash wurde vor Finish, nach Finish, vor Release und nach dem
Schreibvorgang gemessen. In diesem Lauf kamen weder Finish- noch Effektmeldungen
hinzu. Dies gilt für den benannten Kanal dieses Falls, nicht für unbekannte
Quellen. Originalstream-SHA256:
`8452ae1f967042c869fbc62fbab4bd1e77c3a81e1f3642019d991e67ed476f0b`.

**Was der aktuelle Analyst akzeptierte: 0 Zeilen.** `check_events` benötigt die
andere vorhandene native Recorderform mit `run/kind/value/t_ns/event`; die
angebotenen G3-Envelopes wurden mit `ValueError: invalid_observation_schema`
abgewiesen. Sie wurden nicht nachträglich passend gemacht. FakeRepo ist auch
kein vom vorhandenen `TargetSensor` beobachtetes reguläres Filesystemziel.

Der Analyst bekam keine Probe-Checkpoints, Threadsignale, privaten Zustände,
Zielprüfungen oder Ground Truth. `run=1` war ausschließlich das notwendige
API-Abfrageargument; kein belegter Workflowbezug wurde daraus erzeugt.

## 4. Observerantworten vor dem Vergleich

Der getrennte Prozess rief die unveränderten Schnittstellen auf. Schemaaufnahme
und Abfrageunterstützung wurden getrennt geprüft; nach Schemaablehnung lief
**keine gültige native Auswertungspipeline**. Die Abfrageaufrufe prüfen die
vorhandene Schnittstelle und sind keine ersatzweise hinzugefügten Detektoren.

[Vor Vergleich gesicherte wortgetreue Rückgaben](observer-finish-late-effect/2026-10-08/responses/before-comparison.json):

| Frage | Wortgetreues API-Ergebnis |
|---|---|
| A | `ValueError: unknown_research_question`; keine inhaltliche Antwort zurückgegeben. |
| B | `ValueError: unknown_research_question`; keine inhaltliche Antwort zurückgegeben. |
| C | `ValueError: unknown_research_question`; keine inhaltliche Antwort zurückgegeben. |

Die Fragen wurden im vorab eingefrorenen Wortlaut aufgerufen. Die vorhandene
Abfragemenge umfasst nur `target_present`, `appearance_vs_cli_end` und
`appearance_vs_native_end`. Kein Aufruf wurde mit neuem Fragecode repariert.

Antwortdatei vor Ground-Truth-Lesen exklusiv geschrieben, read-only gesetzt und
gehasht; [vorab gesicherter Hash](observer-finish-late-effect/2026-10-08/responses/sealed-response-sha256.json):
`01f62dffb399a7ec92a519947308e7ba458a036ff6a7bc57f6e00bf1851576a3`.
Erst danach wurde die Referenzdatei gelesen und die getrennte Auswertung erstellt.
Der Antwortinhalt blieb dabei hashgleich. Read-only und Hash sind
Nachvollziehbarkeit dieser Teststrecke, keine generelle Manipulationssicherheit.

## 5. Vergleich

| Frage | Unabhängige Wahrheit im Fall | Observeraussage | Bewertung |
|---|---|---|---|
| A | JA: erfolgreiche Finish-Rückkehr vor dem sichtbaren Effekt. | Keine implementierte Antwort; oben dokumentierter API-Fehler. | **UNBEURTEILBAR** |
| B | Der Effekt stammt in der Probe aus demselben einzigen ursprünglichen Schreibvorgang. Daraus folgt keine Observerfähigkeit zur Zuordnung. | Keine implementierte Antwort; oben dokumentierter API-Fehler. | **UNBEURTEILBAR** |
| C | Nach Finish war die Workflow-Registrierung beendet, während dieser gestartete Effekt ausstand; der Effekt trat später ein. | Keine implementierte Antwort; oben dokumentierter API-Fehler. | **UNBEURTEILBAR** |

**0 KORREKT, 0 FALSCH, 3 UNBEURTEILBAR.** Externe Einordnung aller drei Fragen:
UNBEKANNT / NICHT BELEGBAR aufgrund fehlender Schnittstelle. Diese Einordnung
ist vom Tester; der Observer hat **nicht** selbst eine sachgerecht begrenzte
UNBEKANNT-Antwort erzeugt. Es darf deshalb auch nicht behauptet werden:
„Observer hat die Grenze korrekt offengelassen.“ Gemessen wurde keine gültige
Ableitung und keine Erkennungsquote. Die bekannten Referenzwerte wurden nicht
zu Ersatzantworten des Observers.

Maschinenlesbarer Vergleich:
[getrennte Auswertung](observer-finish-late-effect/2026-10-08/derived/evaluation.json).

## 6. Fehlende Informationen und überprüfte historische Lücken

| Prüfpunkt | Tatsächlicher aktueller Befund | Aussagegrenze |
|---|---|---|
| Konkreter Finish-Beleg | Kein Finish-Event im angebotenen Export und keine entsprechende native Klasse/Abfrage. Der erfolgreiche Return ist nur in der privaten Referenz belegt. | `native_end` ist Empfang eines Agentenabschlusses, nicht `Lab.finish()`. Keine Umdeutung erlaubt. |
| Unabhängiger Effekt-/Zielbeleg | Kein entsprechender G3-Event; keine vorhandene FakeRepo-Aufnahme im nativen Observer. Zielzustände sind nur Referenzdaten. | Die zwei ALLOW-Meldungen sind kein Vollzugs- oder Wirkungsbeweis. |
| Vorgangs-/Effektzuordnung | Workflow, Actor, Action und Ressource sind vorhanden, aber kein Effektbeleg mit gemeinsamem Action-/Attempt-/Generation-Bezug. | Zusätzliche IDs wurden nicht getestet; daraus folgt kein erfundenes Pflichtfeld. Die Probe-Identität ist kein heimlicher Observerinput. |
| Ereignis-/Empfangszeitsemantik | Export bietet nur die vorhandenen sekundengenauen Emitterzeiten, keine Finish-/Effektzeit und keine gesonderte Empfangszeit. | Referenzordnung folgt Synchronisation. Allgemeine Zeitminimalität oder verteilte Kausalität nicht geprüft. |
| Historie nach Cleanup | Vor Finish ein Live-Provenanceeintrag; danach kein registrierter Workflow. **Die zwei zuvor exportierten G3-Meldungen bleiben persistent erhalten.** | Die pauschale Behauptung „keine dauerhafte Historie“ wäre für diesen Export falsch. Die persistente Historie enthält weiterhin weder Finish noch Wirkung; keine dauerhafte vollständige Effekthistorie nachgewiesen. |
| Workflowende versus Effektende | Private Referenz zeigt den Unterschied; der angebotene Kanal zeichnet weder Lifecycle-Ende noch ausstehenden/vollzogenen Effekt auf. | Ausbleibende weitere Meldungen beweisen nicht, dass alle Effekte beendet sind. Kein Executor-Stopp-/Widerrufstest. |
| Vorhandene Anschlussfähigkeit | G3-Schema wird abgelehnt und A/B/C liegen außerhalb der implementierten Abfragen. | Keine produktübergreifende Integration behauptet; kein Übersetzer/Detektor hinzugefügt. |

Für eine sichere Fallbehauptung fehlen somit beobachterzugängliche Belege über
die tatsächliche Finish-Rückkehr, den tatsächlichen späteren Zielbefund und deren
Vorgangs-/Ordnungsbeziehung. Für eine Behauptung über **alle** Effekte fehlt eine
belastbare Abdeckung. Das sind benannte Informationslücken; der Test hat **keine**
neue minimale Feldmenge, notwendige ID-Form oder künftige Implementierung geprüft.

## 7. Gesamturteil, Standardsuite und Grenzen

**INCONCLUSIVE.** Der deterministische Fake-Fall ist belegt; dem vorhandenen
Observer fehlen für diese Frage aufnahmefähige Daten und implementierte Abfragen.
Erkennungsfähigkeit weder bestätigt noch durch eine falsche beurteilbare Aussage
widerlegt. Eine sichere Antwort wurde nicht erzeugt. OOS-021 bleibt offen.

Nach dem einmaligen Probe-Lauf die vorhandene Standardsuite zweimal unverändert
ausgeführt, ohne neue Filter oder Ausschlüsse:

| Lauf | Ergebnis | Originalausgabe |
|---|---|---|
| 1 | **304 passed, 5 deselected**, Exit 0, 4,93 s. | [Suite 1](observer-finish-late-effect/2026-10-08/standard-suite/run-1.log) |
| 2 | **304 passed, 5 deselected**, Exit 0. | [Suite 2](observer-finish-late-effect/2026-10-08/standard-suite/run-2.log) |

Die fünf RC-01–05-Deselektionen sind bereits vorhandene, dokumentierte Misses;
keiner wurde geändert oder durch Grün geschlossen. Die historische rote Probe
liegt außerhalb der Standardtestpfade und wurde genau einmal explizit ausgeführt.
Grüne Standardsuite ist Spec-Konformität der getesteten Labfälle, kein
Monitoringbeweis. Keine bestehenden Tests für dieses Ergebnis umgeschrieben.

Alle Originalarchive stimmen byteweise mit den separat erzeugten Messdateien
überein. Das [Archivmanifest](observer-finish-late-effect/2026-10-08/archived-integrity.json)
erhält Größe und SHA256 jeder benannten Datei vor diesem Bericht.

**CONFIDENCE IN EXPERIMENT RESULT:** HIGH für die vorgegebene synchronisierte
Fake-Reihenfolge, die unveränderte Exportsicht und die tatsächlich gemessenen
Schema-/Abfragegrenzen. Keine Accuracy-Confidence, weil keine gültige
Observerauswertung dieser Frage möglich war.

**CONFIDENCE IN GENERALIZATION:** LOW. Ein Single-Process-FakeAdapterfall,
keine realen Agenten, produktiven Effekte, anderen Effektarten, verteilten Uhren,
Stopp-/Widerrufsbestätigungen oder allgemeine Sicherheitsgarantie untersucht.

**STOPP.** Keine Reparatur, neuen Observerfelder, Wiederholung, Graphen,
Belastungsstufe oder Folgefunktion begonnen.
