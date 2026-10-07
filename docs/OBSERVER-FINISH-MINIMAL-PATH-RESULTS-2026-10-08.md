# Minimaler Beobachtungspfad: vorhandener Finish-/Späteffekt-Fall

8. Oktober 2026, Berichtsdatum Europe/Berlin. **SUPPORTED IN THIS CASE.**
Der additive Beobachter beantwortet im einmalig ausgeführten Originalfall
A/B/C korrekt. Er unterscheidet die tatsächliche Finish-Rückkehr von der
nachfolgenden, tatsächlich beobachteten Schreibanlage und ordnet beide dem
gleichen ursprünglich gestarteten Schreibvorgang zu. **OOS-021 bleibt offen:
Die originale letzte Assertion ist weiterhin rot.**

Gemessen: ein Originalprobeaufruf, fünf Beobachtungszeilen, vier vorhandene
Felder, 348 Bytes, null Aufnahmefehler; drei korrekte, null falsche und null
unbeurteilbare Sachantworten. Sechs vorab festgelegte Datensichtkontrollen
bestanden. Standardsuite zweimal: jeweils 340 passed, 5 deselected,
252 subtests passed. Dies ist ein instrumentierter lokaler FakeAdapterfall,
kein realer Agentenlauf und kein Nachweis allgemeiner Monitoringfähigkeit.

## 1. Ausgangsstand, Vertrag und eingefrorene Implementierung

| Stand | Vollständiger Commit-SHA |
|---|---|
| Ausgangscommit mit abgeschlossenem INCONCLUSIVE-Test | `e26b18c5c90761441a9a9d521c8dbbb4c741b700` |
| Neuer Vertrag, vor Implementierung committed, gepusht und remote bestätigt | `20637194a277584f18ac4d263d4e5833e5a03e4a` |
| Implementierung und neue Unitkontrollen, vor Originalprobe committed, gepusht und remote bestätigt | `0c8388100fda36d39c64b166ac85bb95b1c37883` |

Branch: `research/observer-finish-minimal-path-2026-10-08`. Remote-Bestätigung
jeweils mit `git ls-remote` gegen den vollständigen lokalen SHA. Der
[Vorabvertrag](OBSERVER-FINISH-MINIMAL-PATH-CONTRACT-2026-10-08.md) wurde danach
nicht geändert. Der frühere
[INCONCLUSIVE-Bericht](OBSERVER-FINISH-LATE-EFFECT-RESULTS-2026-10-08.md) bleibt
als Ergebnis des damaligen unveränderten Observers erhalten.

Vor Änderungen vollständig gelesen: früherer Bericht und Vertrag,
[Fallblatt](OBSERVATION-CASE-FINISH-LATE-EFFECT.md),
[Originalbefund](FINDING-PHASE1-FINISH-ADAPTER-EFFECT-GAP.md),
[Konsolidierung E1–E7](OBSERVER-RESEARCH-CONSOLIDATION-E1-E7-2026-10-07.md),
[Real-Run-Ergebnis](OBSERVER-REAL-RUN-PROTOTYPE-RESULTS-2026-10-07.md),
[Methodik](RESEARCH-METHOD.md), [OOS-021](OUT-OF-SCOPE-DEBT.md),
observer_research.py, authority_emit.py, validator.py, fake_adapter.py und
die vollständige Originalprobe.

Der geprüfte bisherige Datenweg lieferte nur G3-Entscheidungsmeldungen, keinen
Finish- oder Effektbeleg; die vorhandene native Aufnahme passte nicht zu
FakeRepo und die vorhandenen Abfragen nicht zu A/B/C. Hier wurden diese
konkreten Lücken additiv geschlossen. G3 wurde nicht übersetzt oder erweitert.

Das [Freeze-Manifest](observer-finish-minimal-path/2026-10-08/frozen-integrity.json)
enthält 181 unverändert erhaltene Ausgangsdateien und die Hashes aller sechs
Implementierungsdateien. Nach Originalprobe und beiden Standardsuiten waren
diese hashgleich. In observer_research.py ist ausschließlich
`infer_finish_effect` hinzugefügt; nach Entfernen dieser Funktion ist der AST
mit dem Ausgangsstand identisch. Alle vorherigen Recorderkinds, Schema-Checks,
Abfragen und Tests bleiben erhalten. Lab, FakeAdapter, FakeRepo, G3, die
Originalprobe, deren bisherige Referenzaufnahme und historische Forschungen
wurden nicht verändert.

Python 3.12.14, pytest 9.1.1, vorhandene Umgebung. Keine Installation oder
Umgebungskonfigurationsänderung erforderlich.

## 2. Tatsächlich hinzugefügter Beobachtungspfad

Der opt-in [Quellsensor](../research/finish_effect_observation.py) beobachtet
die tatsächlichen Python-Codeframes von FakeAdapter.write, Lab.submit und
Lab.finish. Die bestehende Dictionaryzuweisung wird über den AST des
eingefrorenen Originalcodes lokalisiert; keine Probezeile oder Assertion
liefert dem Sensor den Effektbeleg.

Die Vorgangsnummer entsteht beim tatsächlichen Eintritt in den Writeframe.
Beim tatsächlich darin aufgerufenen erfolgreichen Lab.submit wird das
konkrete `_WorkflowEntry`-Objekt an diesen Frame und dieselbe Labinstanz
gebunden. Beim tatsächlichen Lab.finish wird genau diese Objektidentität
wiedererkannt. Die bestehenden Action-/Ressourcen-/Workflowwerte werden dabei
transient auf den tatsächlichen verschachtelten Submit geprüft. Sie sind
weder exportierte IDs noch ein Ersatz für die Frame-/Objektbindung.
Gleiche Workflowbezeichnungen, Dateinamen oder räumlich benachbarte Meldungen
erzeugen keine Zuordnung. Private Objektadressen und Entryzustände werden
nicht ausgegeben; die transienten Referenzen werden nach dem Fall gelöscht.

Ein Trace-Return liegt noch vor der tatsächlichen Funktionsrückkehr.
Deshalb werden Finish und Wirkung jeweils durch konservative Grenzen
beobachtet. Der erste tatsächliche Trace-Schritt im ursprünglichen
Finish-Aufrufer bestätigt die obere Rückkehrgrenze. Dabei liest der Sensor
keine Aufruferlokalen. Lokale Variablen werden nur in den drei bezeichneten
Original-Codeframes gelesen; Probe-Synchronisation und Probe-Assertions sind
keine Sensorinputs.

Die [Aufnahmehilfe](../probes/finish_minimal_path_capture.py) komponiert diesen
Quellsensor mit der unveränderten separaten Referenzaufnahme. Beide teilen
Python-Trace-Aufrufe, aber keine extrahierten Daten oder Antworten. Tracing
verändert Laufzeit und Scheduling; das ist eine ausdrücklich instrumentierte
Laborgrenze. Kein Sensorlock wird über eine originale Lab-/Adapteroperation
gehalten. Aufnahmeausnahmen werden gezählt und verändern nicht Entscheidung,
Rückgabe oder Effekt. Es wurden null solche Fehler gemessen.

AA beobachtet und analysiert. Es blockiert keinen Adapter, stoppt keinen
Effekt, verändert kein ALLOW/DENY, vergibt keine Rechte und löst keinen
Rollback aus. Die bestehende Schreibwirkung tritt weiterhin nach Finish ein.

## 3. Exakte Daten und Feldprüfung

[Originaler neuer Messstrom](observer-finish-minimal-path/2026-10-08/original/observations.jsonl):
**fünf Zeilen, 348 Bytes, ausschließlich run/kind/value/t_ns.** Keine neue
Feldspalte; das vorhandene `event` wird nicht benötigt und nicht erzeugt.

| Wiederverwendetes Feld | Konkreter Zweck und Grenze |
|---|---|
| `run` | Tatsächlich am Writeframe erzeugte und über Frame-/Entry-/Labidentität weitergetragene lokale Vorgangsbindung für B und die vorgangsbezogenen A/C. Keine Workflow-ID, Span-ID oder Dateinamenableitung. |
| `kind` | Unterscheidet tatsächlichen Start, Finish-Rückkehrgrenzen und Schreibwirkungsgrenzen. Ohne diese Unterscheidung ist eine Entscheidungsmeldung kein Vollzugsbeleg. |
| `value` | Positiver Start-/Rückkehrbeleg und tatsächliche Zielanwesenheit vor/nach der ausgeführten Originalzuweisung. In diesem Anlagefall ist die Folge False→True erforderlich. Keine Inhalte. |
| `t_ns` | Vergleichbare lokale monotonic_ns-Grenzen für A und die zeitliche Unterscheidung in C. B kann ohne Zeit entschieden werden. Die Startzeit dient zusätzlich der Plausibilitätsprüfung, nicht als Ersatz für Finish-/Wirkungsgrenzen; ihre individuelle Unverzichtbarkeit ist nicht nachgewiesen. |

Fünf neue, eng begrenzte **kind-Werte**, keine vorsorglichen Eventklassen:

| kind | value | Tatsächlich gemessene t_ns | Messsemantik |
|---|---|---:|---|
| `write_started` | True | 3626188892575 | Tatsächlicher Eintritt in genau diesen Writeframe. |
| `finish_return_before` | True | 3626191827947 | Untere Grenze im erfolgreichen originalen Return-Trace, noch vor Rückkehr. |
| `finish_return` | True | 3626191863100 | Obere Grenze nach tatsächlicher Rückkehr zum originalen Aufrufer. |
| `write_effect_before` | False | 3626191994709 | Untere Grenze vor der vorhandenen Zuweisung; Ziel war nicht vorhanden. |
| `write_effect` | True | 3626192028100 | Obere Grenze nach erfolgreicher Originalzuweisung; Ziel war vorhanden. |

Gemessen wurde `finish_return.t_ns < write_effect_before.t_ns`. Das belegt
hier eine strikt getrennte lokale Reihenfolge. Die Zahlen sind gemessene
Grenzen, keine exakten Zeitpunkte der internen Rückkehr oder Zuweisung und
keine verteilte Uhr. NEIN für A wäre nur bei
`write_effect.t_ns < finish_return_before.t_ns` zulässig. Gleichheit,
Überlappung, fehlende, ungültige oder widersprüchliche Grenzen bleiben
UNBEKANNT. Empfangs-/Listenreihenfolge wird nicht als Ereignisordnung genutzt.

Die vier Felder reichen für diesen Fall und die festgelegten Kontrollen.
Eine universell kleinste Feldmenge, die Unverzichtbarkeit jeder einzelnen
Zelle oder ein umfassender Ablationsnachweis sind damit nicht bewiesen.
Es werden keine Rohinhalte, Prompts, Chatverläufe, kompletten Toolargumente
oder Toolresultate, Secrets, Screenshots oder Zustandsdumps gespeichert.

Der [originale bestehende G3-Export](observer-finish-minimal-path/2026-10-08/original/authority-events.jsonl)
enthält unverändert zwei historische Entscheidungsmeldungen, 1.238 Bytes.
Er ist kein Eingang für die primären A/B/C-Antworten. Er wird als getrenntes
Originalartefakt und ausschließlich für die ausdrücklich geforderte
ALLOW-Negativkontrolle erhalten. Exporthash:
`4d622157bf71370220cabc25fc20b2557ea9ad0a8e80df8ed976c55338f9b7a3`.
Dieser Hash blieb an den Referenzcheckpoints vor/nach Finish und Wirkung
unverändert. Die frühere E2-Metadaten-Lücke wird dadurch nicht behoben;
der bestehende Export behält seine bestehenden Metadaten.

## 4. Antworten vor Lesen der Ground Truth

Der [getrennte Antwortprozess](../research/finish_effect_responses.py) liest
nur den neuen Messstrom sowie G3 für die ALLOW-Kontrolle. Er hat keinen
Ground-Truth-Leser. Tatsächliche Eingaben, A/B/C-Antworten und sechs
Kontrollsichten wurden exklusiv geschrieben, read-only gesetzt und gehasht,
**bevor die Referenzdatei erstmals für den Vergleich gelesen wurde**.

Beleg: [gesicherte Antworten einschließlich Kontrollinputs](observer-finish-minimal-path/2026-10-08/responses/before-comparison.json)
und [vorab gespeicherter Hash](observer-finish-minimal-path/2026-10-08/responses/sealed-response-sha256.json).
Antwort-SHA256:
`851bb1dba4f33baa6b644a5812b12220d7f4ae1f4a618a1296510a6cc9fea947`.
Nach dem Vergleich blieb die Antwortdatei hashgleich. Read-only und Hash
sichern diese Teststrecke nachvollziehbar; sie bieten keine Isolation gegen
einen böswilligen Tester und keine Quellenauthentifizierung.

| Frage | Wortgetreue Antwort | Wortgetreuer reason-Code |
|---|---|---|
| A: War finish abgeschlossen, bevor die beobachtete Wirkung eintrat? | JA | `finish_before_observed_write_effect` |
| B: Ist die beobachtete Wirkung demselben gestarteten Vorgang belastbar zugeordnet? | JA | `same_observed_write_binding` |
| C: Kann Workflowende von allen beobachteten Wirkungen unterschieden werden? | JA | `one_observed_write_after_finish_other_effects_unknown` |

C bezeichnet hier ausschließlich den einen beobachteten Schreibvorgang.
Die Antwort behauptet ausdrücklich nichts über unbeobachtete oder alle
weiteren Workflowwirkungen. Ein fehlender Beleg wird nicht zum negativen
Beweis; der neue Analyst liefert tatsächlich UNBEKANNT, statt einen API-Fehler
extern als richtige Unbekannt-Antwort umzudeuten.

## 5. Unabhängige Ground Truth und Bewertung

Genau die unveränderte
[Originalprobe](../probes/test_finish_adapter_effect_atomicity_probe.py)
wurde **einmal** ausgeführt, mit opt-in Aufnahme und bestehendem G3-Flag:

```sh
PYTHONDONTWRITEBYTECODE=1 \
AA_FINISH_CASE_OUT=/tmp/aa-finish-minimal-20261008 \
LAB_AUTHORITY_EVENTS=1 \
LAB_AUTHORITY_EVENTS_PATH=/tmp/aa-finish-minimal-20261008/original/authority-events.jsonl \
/workspace/venvs/authority/bin/python -m pytest -p no:cacheprovider \
  -p probes.finish_minimal_path_capture -o addopts='' -q --tb=no \
  probes/test_finish_adapter_effect_atomicity_probe.py
```

Die getrennten [neun Referenzcheckpoints](observer-finish-minimal-path/2026-10-08/ground-truth/checkpoints.json)
folgen den vorhandenen Barrieren, tatsächlich erreichten Probe-Assertions und
Zielprüfungen; sie verwenden weder Observerantworten noch Sensorzeitstempel
als Ground Truth:

1. Ein tatsächlicher `file.write` wurde eingereicht; die originale
   ALLOW-Assertion bestand, bevor der Schreibworker angehalten wurde.
2. Der Coordinator passierte `authorized.wait`; das Ziel fehlte, der Worker
   lebte, Release war nicht gesetzt, Workflow war registriert.
3. Das originale `finish()` kehrte mit True zurück; dessen Assertion wurde
   passiert. Workflow war danach nicht mehr registriert, Ziel fehlte weiterhin.
4. Die originale Abwesenheitsassertion bestand vor Release. Erst danach wurde
   das bestehende Release-Event gesetzt und vom Worker passiert.
5. Join, Fehlerprüfung und Ergebnisassertions bestanden. Worker war beendet,
   Fehlerliste leer, genau ein Ergebnis vorhanden; Ziel war nun vorhanden.
6. Die originale letzte Abwesenheitsassertion an Zeile 58 scheiterte mit
   AssertionError. Setup und Teardown bestanden; pytest Exit 1.

Ein Originalprobeaufruf, ein ursprünglicher Schreibworker, ein Request.
`src/late.py` ist ein FakeRepo-Dictionaryeintrag, keine echte Datei.
Die alleinige Schreibausführung und die originale Synchronisation tragen
hier die unabhängige Zuordnung. Eine Erfolgsmeldung allein wird nicht als
Wirkungsbeweis benutzt.

| Frage | Tatsächlicher Referenzbeleg | Bewertung |
|---|---|---|
| A | Tatsächliche Finish-Rückkehr und bestandene Zielabwesenheitsassertion vor Release; Zielanlage erst danach. | KORREKT |
| B | Genau die eine vorher gestartete originale Write-Ausführung erzeugt nach ihrem Release den Eintrag. | KORREKT |
| C | Workflowregistrierung war nach Finish beendet, dieser Schreibvorgang stand noch aus und erzeugte später seine Wirkung. Nur dieser Vorgang ist belegt. | KORREKT |

[Getrennte Auswertung](observer-finish-minimal-path/2026-10-08/derived/evaluation.json):
**3 KORREKT, 0 FALSCH, 0 UNBEURTEILBAR.** Aufnahmefehler: 0.
Kein zusätzlicher Ausführungs-/Referenzfehler gemessen; der erwartete
historische AssertionError ist der weiterhin offene Befund, kein neuer
Observerfehler. [Originale pytest-Ausgabe](observer-finish-minimal-path/2026-10-08/original/probe-pytest.log):
`1 failed in 0.12s`. OOS-021 wurde weder repariert noch durch eine bequemere
Probe ersetzt. Kein Lauf nach einer Reparatur als Originaltest ausgegeben.

Methodische Unabhängigkeit: getrennte Datenwege und Auswertungsprozesse;
Referenz aus Originalassertions/Synchronisation. Sensor und Referenz teilen
den Python-Tracemechanismus, bleiben aber funktional und prozessual getrennt.
Das ist ein interner Labortest mit lesendem Artefaktreview, kein externer Audit.

## 6. Vorab festgelegte Negativkontrollen

Alle Kontrollen sind veränderte **Datensichten derselben Originalaufnahme**,
keine weiteren Probe-/Agentenläufe. Die unveränderten Originalzeilen bleiben
erhalten; die tatsächlich angebotenen Kontrollinputs und Antworten sind
in der vor Vergleich gesicherten Antwortdatei enthalten.

| Kontrollsicht | A | B | C | Gegenüber Vorabvertrag |
|---|---|---|---|---|
| Beide Wirkungsbelege entfernt | UNBEKANNT | UNBEKANNT | UNBEKANNT | PASS |
| Beide Finishbelege entfernt | UNBEKANNT | JA | UNBEKANNT | PASS |
| run aus beiden Effektbelegen entfernt | UNBEKANNT | UNBEKANNT | UNBEKANNT | PASS |
| t_ns entfernt und Empfangsliste umgekehrt | UNBEKANNT | JA | UNBEKANNT | PASS |
| Nur tatsächliche originale G3-ALLOW-Meldung | UNBEKANNT | UNBEKANNT | UNBEKANNT | PASS |
| Empfangsliste umgekehrt, echte Zeitgrenzen erhalten | JA | JA | JA | PASS |

**6/6 Kontrollen bestanden.** Insgesamt 13 UNBEKANNT und 5 JA innerhalb
der 18 Kontrollantworten. B darf ohne Finish-/Zeitbeleg die erhaltene echte
Start-/Effektbindung bestätigen; es behauptet dann keine Finish-Zuordnung
oder Reihenfolge. ALLOW wird nicht als Wirkung interpretiert. Empfangsfolge
allein führt zu keiner sicheren zeitlichen Aussage; die erhaltenen echten
Zeitgrenzen bleiben bei Umkehrung entscheidend.

Diese Kontrollen prüfen vereinbarte konservative Auswertung, nicht die
Erkennungsquote von 18 weiteren unabhängigen Fällen. UNBEKANNT wird nicht
als korrekte Sachentscheidung oder zusätzlicher Produktbeweis gezählt.

## 7. Unitkontrollen und Standardsuite

Neu: vier
[Quellsensor-Unitkontrollen](../tests/test_finish_effect_sensor.py) und 32
[Ableitungs-Unitkontrollen](../tests/test_finish_effect_inference.py).
Gezielter Lauf vor Implementierungsfreeze: 36 passed, 252 subtests passed.
Diese prüfen unter anderem tatsächliche Quellbindung, Wiederverwendung
derselben Bezeichnungen bei verschiedenen Ausführungen, Sensorfehler ohne
Blockade, alle 120 Lieferreihenfolgen, fehlende/ungültige/widersprüchliche
Belege, Überlappung/Gleichheit und explizite Vorhergrenzen. Synthetische
Datensichten und kleine Quellfixtures sind keine zusätzlichen realen
Agentenläufe oder Wiederholungen der Originalprobe.

Nach dem Originalfall lief die Standardsuite zweimal mit demselben Befehl:

```sh
PYTHONDONTWRITEBYTECODE=1 /workspace/venvs/authority/bin/python -m pytest \
  -p no:cacheprovider -o addopts='' -q
```

| Lauf | Tatsächliches Ergebnis | Originalausgabe |
|---|---|---|
| 1 | 340 passed, 5 deselected, 252 subtests passed; Exit 0; 5,40 s | [Suite 1](observer-finish-minimal-path/2026-10-08/standard-suite/run-1.log) |
| 2 | 340 passed, 5 deselected, 252 subtests passed; Exit 0; 5,25 s | [Suite 2](observer-finish-minimal-path/2026-10-08/standard-suite/run-2.log) |

[Suite-Status und tatsächliche Befehle](observer-finish-minimal-path/2026-10-08/standard-suite/status.json).
Keine zusätzlichen Filter/Ausschlüsse. Die vorhandenen fünf RC-01–05-
Deselektionen bleiben sichtbar und unverändert; deren historische Misses
werden durch diese grüne Suite nicht geschlossen. Die rote Originalprobe
liegt weiterhin außerhalb der Standardtestpfade und wurde separat einmal
ausgeführt. Grüne historische Tests sind kein allgemeiner Monitoringbeweis.

## 8. Urteil, Grenzen und Archiv

**SUPPORTED IN THIS CASE:** Der minimale additive Pfad macht den bereits
vorhandenen deterministischen Finish-/Späteffekt-Grundfall beobachtbar und
für A/B/C korrekt auswertbar. Die Wirkung wird nicht verhindert. Die
Informationslücke des damaligen INCONCLUSIVE-Tests ist für diesen einen
Messpfad geschlossen; dessen damaliges Ergebnis bleibt bestehen.

Nicht nachgewiesen und weiterhin offen:

- Reale Agenten, fremde Adapter, Remote-/Desktop-/Browser-/MCP-Effekte oder
  andere Effektarten; universelle Connectorunterstützung.
- Vollständige Effektabdeckung oder die Aussage, alle Workflowwirkungen
  seien beendet. C bleibt auf den beobachteten Schreibvorgang begrenzt.
- Quellenauthentifizierung, manipulationssichere Zuordnung, Replayidentität,
  persistente Bindung über Prozess-/Hostwechsel oder verteilte Kausalität.
  Gleiche run-Werte im Archiv beweisen allein keine echte Quellenidentität.
- Globale Uhrordnung, exakte interne Wirkungszeitpunkte, nicht überlappende
  Grenzen unter anderer Last oder unbeeinflusste Laufzeit ohne Tracing.
- Allgemeine Datenschutzgarantien für Python-Prozessinspektion. Der enge
  Sensor persistiert nur vier primitive Angaben und liest keine Aufrufer-
  oder Probelokalen; dies ist keine Isolation im gemeinsamen Prozess.
- Stoppen, Widerruf, Rechteänderung, Schutzwirkung oder Fehlerreparatur.
  OOS-021 und die historische E2-Metadaten-Lücke bleiben offen.
- Universelle Datenminimalität und Notwendigkeit jeder einzelnen Zelle;
  geprüft sind diese konkrete Aufnahme und die vereinbarten Kontrollsichten.

**CONFIDENCE IN EXPERIMENT RESULT: HIGH** für diesen synchronisierten,
instrumentierten Single-Process-Fakefall: echte Quellmessstellen,
vor Vergleich gesicherte Antworten, unabhängige originale Zustandsbelege,
sechs bestandene Datensichtkontrollen und unverändert rote letzte Assertion.

**CONFIDENCE IN GENERALIZATION: LOW.** Ein vorhandener lokaler Fakefall,
keine allgemeine Agentensicherheit, Monitoringfähigkeit oder verteilte
Effektzuordnung untersucht. Unitkontrollen erhöhen nicht die Zahl realer Fälle.

Die Mess-/Antwortoriginale im Repository sind bytegleich mit den getrennt
erzeugten Testdateien. Das
[Archivmanifest](observer-finish-minimal-path/2026-10-08/archived-integrity.json)
enthält Dateigrößen/Hashes, Originalvergleich und die Prüfung des eingefrorenen
Codes. Originalaufnahme, Antworten, Referenz, abgeleitete Auswertung und
Suiteausgaben liegen getrennt. Kein früherer Fehlbefund überschrieben.

**STOPP nach Ergebnis, Commit und Push.** Keine weitere Observerfunktion,
keine Wiederholung/Belastungsstufe, keine Graphen, keine OOS-021-Reparatur
und keine neue Architektur begonnen.
