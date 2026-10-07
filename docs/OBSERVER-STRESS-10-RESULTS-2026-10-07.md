# Belastungsstufe 10: NICHT BESTANDEN

7. Oktober 2026. Ein fester Stresstest, keine Systemverbesserung.
Vollständig gelesene Grundlage:
[Prototypbericht](OBSERVER-REAL-RUN-PROTOTYPE-RESULTS-2026-10-07.md)
am Stand `05cd98d977e28210d6427fb4ca1f5fc118cc4efe`.
[Vorabvertrag](OBSERVER-STRESS-10-CONTRACT-2026-10-07.md), vor Runnerbau und
Modellläufen committed/gepusht unter `0a18445e8f9bca120d5a55957e7b8cded43c833e`.
Testspezifischer Runner vor Modellläufen committed/gepusht unter
`d0387f69045fc015d1446fa9add3cd31e0c7d3b2`.

## Ergebnis in Zahlen

| Größe | Gemessener Stand |
|---|---:|
| Gestartete echte Agentenkontexte | 10 |
| Tatsächlich abgeschlossene Agentenkontexte | 10 |
| Tatsächlich ausgeführte Fixtureaufträge | 9 |
| Fehlgeschlagene Ausführung | 1: Lauf 7 |
| Davon nachgewiesener Fehler beim Befolgen der Agentenanweisung | 0 |
| Aufnahme-/Messwerkzeugfehler | 1: Startbarriere von Lauf 7 |
| Sensorfehler | 0 |
| Korrekte Aussagen | 15 |
| Falsche beurteilbare Aussagen / Observerfehler | 0 |
| Unbekannt bei beurteilbarer Wahrheit | 0 |
| Nicht anwendbar | 3 |
| Unbeurteilbar | 2 |
| Stufe 10 gemäß Vorabvertrag | **NICHT BESTANDEN** |

Ausführungs- und Messfehler benennen **denselben Fall**, keine zwei unabhängigen
Fehler. Das Testwerkzeug von Lauf 7 wurde durch den Runner-Timeout nicht ausgeführt.
Der Agent führte seinen vorgegebenen Terminalaufruf aus, wartete auf dessen
Rückkehr und meldete Exit 2; das ist kein belegter LLM-Anweisungsfehler.
Die vier geplanten Fixture-Exit-7-Fälle (3, 4, 8, 9) sind keine unerwarteten
Agenten-/Ausführungsfehler. Alle zwanzig Fragen bleiben in der Auswertung enthalten.

## Tatsächliche Last und ihre Grenze

Zehn neue native Kontexte mit geringer Reasoning-Stufe, je ein fest vorgegebener
Terminalauftrag. Zwei Fälle pro Modus: Zielanlage, keine Anlage, Fehler ohne
Wirkung, Fehler trotz Anlage, Anlage nach empfangenem Abschluss.
Die Umgebung erlaubt maximal sechs Testkontexte neben dem Koordinator; die
Zehnerkohorte wurde deshalb als 6+4 gestartet, wie vorab ausdrücklich festgelegt.
Es wurden keine separaten Zwischenstufen getestet. **Kein Beleg für zehn
gleichzeitig aktive Modellkontexte.**

Alle zehn Zielsensoren liefen im gemeinsamen Messfenster. Gemessene Überlappung
der instrumentierten Werkzeugaufrufintervalle: **Maximum 6**, im zweiten Teil
**Maximum 3**. Die höhere Werkzeugparallelität gegenüber dem seriellen
Basistransport ist damit vorhanden; der zweite Viererstart blieb unvollständig.
Das sind Aufrufintervalle, keine exakte Messung gleichzeitig laufender OS-Prozesse
oder Modellberechnungen. Die bestehenden Observerfelder wurden nicht erweitert.

`peak_open_agent_requests=6` in der Auswertung ist Koordinatorbuchführung.
Die Startbestätigungen der ersten sechs Kontexte wurden erst nach deren Spawn
und empfangenen Abschlussmeldungen eingetragen. Ihre `t_ns` sind diese tatsächlichen
Bestätigungszeitpunkte, **keine nachträglich erfundenen ursprünglichen Spawnzeiten**.
Dieser Zähler beweist für sich keine Modellparallelität. Der Werkzeugüberlappungsnachweis
verwendet davon unabhängige, während der Aufrufe gemessene `tool`-Intervalle.

## Vollständig erhaltener Fehler: Lauf 7

Der Aufruf von Lauf 7 traf an der zweiten Startbarriere ein. Laut unverändertem
Vorabvertrag musste sie nach 60 Sekunden warten aufgeben, wenn nicht alle vier
Aufrufe angekommen waren. Die gespeicherten `queued`-Zeiten zeigen:
zwischen Lauf 7 und dem letzten Eintreffen der Gruppe lagen **61,161643212 Sekunden**.
Die erste Sechsergruppe hatte eine Ankunftsspanne von 48,629267771 Sekunden.

Lauf 7 erhielt `stress_barrier_timeout`, `timeout=true`, `tool_attempts=0`;
seine Referenz meldet `calls=0` und
`reference_issue=uncontrolled_or_missing_tool_execution`.
Ein exakter eigener Timeoutzeitstempel wurde nicht gespeichert; die 60 Sekunden
sind die eingefrorene Runnergrenze, nicht eine erfundene Messung dieses Zeitpunkts.
Die drei später angekommenen Aufrufe wurden nach Öffnung ihrer Barriere ausgeführt.

**Fehlerklasse:** Runner-/Ausführungsstrecke. Kein nachgewiesener falscher
beurteilbarer Observerclaim. Die notwendige unabhängige Ausführungsreferenz für
diesen Lauf fehlt. Die feste Referenzfunktion lässt deshalb beide Fragen
unbeurteilbar. Der Endsnapshot des Observers meldet zwar nicht vorhanden,
aber fehlende Referenz wird nicht als Beweis für Wirkungslosigkeit verwendet.

Keine Verlängerung der Barriere, kein Nachholen von Lauf 7, kein neuer Agent,
keine Reparatur von Runner oder Observer während/nach dem Lauf. Die Daten wurden
unverändert gesichert; der Stresstest wurde nicht durch einen Ersatzlauf verbessert.

## Einzelbewertungen unter den festen Minimalmengen

Zielzustand verwendet ausschließlich `run/kind/value`.
Zeitfrage verwendet ausschließlich `run/kind/value/t_ns`.
`event`, Kontrollbuchführung, Szenario und Referenz sind kein Analysteninput.
Die unveränderte Funktion `observer_research.infer` erhielt jeweils die gemeinsame
projizierte Ereignisliste und die abgefragte Laufnummer. Erst nach Speicherung
aller zwanzig Vorhersagen wurde die getrennte Referenz gelesen.

| Lauf | Modus | Zielzustandsbewertung | Zeitbewertung |
|---|---|---|---|
| 1 | `write` | vorhanden, korrekt | vorher, korrekt |
| 2 | `noop` | nicht vorhanden, korrekt | nicht anwendbar |
| 3 | `fail` | nicht vorhanden, korrekt | nicht anwendbar |
| 4 | `write_fail` | vorhanden, korrekt | vorher, korrekt |
| 5 | `late` | vorhanden, korrekt | nachher, korrekt |
| 6 | `write` | vorhanden, korrekt | vorher, korrekt |
| 7 | `noop`, Fixture nicht ausgeführt | Aussage nicht vorhanden, unbeurteilbar | unbekannte Aussage, unbeurteilbar |
| 8 | `fail` | nicht vorhanden, korrekt | nicht anwendbar |
| 9 | `write_fail` | vorhanden, korrekt | vorher, korrekt |
| 10 | `late` | vorhanden, korrekt | nachher, korrekt |

Ground Truth der neun ausgeführten Aufträge: unveränderte unabhängige
syscall-nahe Anlageintervalle und separater späterer Zielcheck, mit den bisherigen
Snapshot-/Endintervallgrenzen. Keine Wahrheit aus Werkzeugstatus oder „Agent fertig“.
Die drei NA-Fälle wurden erst durch die Referenz so klassifiziert; der Observer
gab dort unbekannt aus. NA wurde nicht in die korrekten Aussagen eingerechnet.

## Gesicherte Dateien und Prüfung

Originale, keine neuen Ableitungen darin:
[Beobachtungen](observer-stress-10/2026-10-07/original/observations.jsonl),
[Capture](observer-stress-10/2026-10-07/original/capture.json),
[Referenz](observer-stress-10/2026-10-07/original/reference.json),
[Kontrollbuchführung](observer-stress-10/2026-10-07/original/control.json).
Davon getrennt:
[Vorhersagen vor Referenzvergleich](observer-stress-10/2026-10-07/derived/predictions.json)
und [Auswertung](observer-stress-10/2026-10-07/derived/evaluation.json).
51 Beobachtungen, 3.892 Beobachtungsbytes, unverändert die fünf alten Recorderfelder.

SHA-256 der archivierten Originalbeobachtungen:
`d51d5e3e1c5452c7be2ac2e68aaffc9b50be8be03dfdd84bfe74210ed0b1e5c2`.
Die Kopien wurden bytegleich zur Aufnahme angelegt. Historische Messungen und
Fehlbefunde bleiben erhalten. `observer_research.py`, `native_driver.py`,
`agent_task.py`, historische Tests und Abhängigkeiten sind gegenüber dem Ausgangscommit
unverändert; ausschließlich der isolierte Stressrunner und neue Dokumente/Daten kamen hinzu.
Vor dem realen Lauf bestand die unveränderte Standardsuite zweimal:
304 passed, 5 bestehende RC-deselected. Kein zusätzliches Modellpanel oder Eignungstest.

**Achse A / Testdurchführung:** NICHT BESTANDEN wegen fehlgeschlagener Ausführung
und unvollständiger unabhängiger Referenz eines Laufs.
**Achse B / Observer unter dieser Last:** INCONCLUSIVE für die vollständige
Zehnerkohorte; in den 15 beurteilbaren Fragen wurde kein Fehler gefunden.
Das ist keine Bestätigung der ganzen Stufe durch Aussortieren des Fehlfalls.

**CONFIDENCE IN EXPERIMENT RESULT:** HIGH für die gespeicherten Zähler,
Barrieregrenze und gültigen lokalen Informationsvergleiche; MEDIUM für die
reale Aufnahme unter vertrauenswürdiger Orchestrierung.
**CONFIDENCE IN GENERALIZATION:** LOW. Kein allgemeines Mindestdatenschema,
Quellechtheits-, Wirkungsabdeckungs-, Stopp- oder Monitoringversprechen.

**STOPP.** Keine Reparatur, neue Felder, Wiederholung oder weitere Belastungsstufe.
