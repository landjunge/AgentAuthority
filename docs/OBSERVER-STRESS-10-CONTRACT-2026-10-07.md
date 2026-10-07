# Vorabvertrag: Belastungsstufe 10

Grundlage vollständig gelesen: `OBSERVER-REAL-RUN-PROTOTYPE-RESULTS-2026-10-07.md`
am festgeschriebenen Commit `05cd98d977e28210d6427fb4ca1f5fc118cc4efe`.
Daniels neuer Auftrag autorisiert ausschließlich diesen Stresstest.

## Feste Frage und unverändertes Modell

Trägt die bestehende Ableitung zwei bereits definierte Aussagen bei einer
Zehnerkohorte mit parallelen Werkzeugaufrufen und ineinandergreifenden Meldungen?

1. Ziel im bezeichneten Endsnapshot vorhanden?
2. Falls anwendbar: Anlage vor/nach dem empfangenen Agentenabschluss?

Unverändert benutzt werden `observer_research.infer`, Recorder, TargetSensor,
Referenzerzeugung, judge sowie das originale harmlose `research/agent_task.py`.
Keine Änderungen an diesen Dateien oder den bisherigen Originalmessungen.
Zielzustandsinput ausschließlich `run/kind/value`; Zeitinput ausschließlich
`run/kind/value/t_ns`. `event` wird vor beiden Ableitungen entfernt.
Keine Risiko-/Autoritätslogik, Graphen, UI, neue Datenfelder oder Sachfragen.

## Definition der Belastungsstufe vor dem Lauf

Genau zehn neue native LLM-Kontexte, geringe Reasoning-Stufe, pro Kontext genau
ein Aufruf des vorhandenen Testwerkzeugs. Feste Zuordnung:

| Lauf | Aufgabe |
|---|---|
| 1, 6 | `write` |
| 2, 7 | `noop` |
| 3, 8 | `fail` |
| 4, 9 | `write_fail` |
| 5, 10 | `late` über die bestehende `late_native`-Fixture |

Der bereitgestellte native Zugang hat maximal sechs aktive Testkontexte neben
dem Koordinator. **Stufe 10 bezeichnet zehn unterscheidbare Läufe in einer Kohorte,
nicht zehn gleichzeitig aktive Modellkontexte.** Sie werden als 6+4 möglichst
überlappend gestartet; keine sechs-/vierer Zwischenstufentests oder eigene Urteile.
Die tatsächliche Überlappung wird gemessen, nicht aus zehn Starts behauptet.

Alle zehn unveränderten Zielsensoren laufen im selben gemeinsamen Messfenster.
Anders als der bisher serielle Socketversuchsserver bearbeitet allein ein neuer,
testspezifischer Runner die Aufrufe in getrennten Threads. Seine erste Startbarriere
öffnet, sobald sechs Calls angekommen sind; die zweite bei den vier verbleibenden.
Nach 60 Sekunden unvollständiger Barriere: Quelle-/Runnerfehler festhalten, nicht
heimlich die Kohorte ersetzen. Barrieren sind Versuchsplanung, keine AA-Befugnis.
Die Fixture selbst und ihre Wirkungs-/Fehlermodi bleiben unverändert.

Zeitpunkte für Dispatch, Barrieren und tatsächliche Aufrufgrenzen werden nur als
getrennte Versuchssteuerungsbuchführung mit den vorhandenen Primitiven
`run/kind/value/t_ns` gespeichert. Sie gehen niemals an die Ableitung.
Gemessen werden offene Modellanforderungen und überlappende instrumentierte
Werkzeugaufrufintervalle; das sind keine exakten OS-Prozess-/GPU-Parallelitätsmessungen.
Mindestens zwei Werkzeugaufrufintervalle müssen tatsächlich überlappen; andernfalls
ist höhere Werkzeugparallelität nicht nachgewiesen und Stufe 10 nicht bestanden.

## Unabhängige Wahrheit und unveränderte Aufnahme

Je Lauf eigener temporärer Ordner, ein vorab bezeichnetes leeres Testziel.
Ein gemeinsamer Beobachtungsstrom mit den bisherigen fünf Recorderfeldern;
keine Dateinamen-/Reihenfolgebindung im Analysteninput.
Die Referenz nutzt die originalen syscall-nahen Anlageintervalle und einen
gesonderten Zielcheck; Status, Sollmodus und Analystenantwort sind keine Wahrheit.
Überlappende/fehlende/widersprüchliche Referenz bleibt unbeurteilbar.
Der ursprüngliche `native_end` bleibt der tatsächliche Callback nach empfangenem
Agentenabschluss, kein physischer Stopp. `late` wartet diesen Callback tatsächlich ab.
Nach den zehn Abschlüssen bleibt das bisherige 0,5-Sekunden-Nachbeobachtungsfenster.

Nur der testspezifische Runner initialisiert zehn statt sechs Zustände; er verwendet
die vorhandenen call/close/finish-Methoden und eine parallele Testtransporthülle.
Die sechs-Lauf-Reporteinstiegsfunktion wird nicht umgebaut oder durch Mutation von
`PANEL` erweitert: eine separate Testauswertung ruft `infer` für die zehn vorab
festgelegten Laufnummern und genau die beiden festgelegten Projektionen auf.
Vorhersagen werden getrennt gespeichert, bevor Referenz/Szenariobuchführung gelesen
wird. Originalbeobachtungen, Capture und Referenz werden anschließend nicht überschrieben.

## Fehlerklassen und Entscheidung

- Agenten-/Ausführungsfehler: fehlender/mehrfacher Auftrag, Reparaturabweichung,
  ausbleibender Kontextabschluss oder unerwarteter Fixtureabschluss.
  Die vier beabsichtigten Exit-7-Fälle sind Versuchsmodi, keine solchen Fehler.
- Aufnahme-/Messfehler: Sensor-/Speicher-/Runnerfehler, Timeout, verlorener Callback
  oder fehlende/ungültige unabhängige Referenz. Nicht als Observerfehler umbenennen.
- Observer-/Ableitungsfehler: beurteilbare Antwort widerspricht unabhängiger Wahrheit.
- Unbekannt: Modell entscheidet mit seiner festen Sicht nicht.
- Nicht anwendbar: unabhängig belegte fehlende Zielanlage; kein positiver
  Vor-/Nach-Claim darf unter dieser Kategorie versteckt werden.
- Unbeurteilbar: Wahrheit fehlt oder ist mehrdeutig, keine negative Wahrheit einsetzen.

Die zwanzig Einzelbewertungen bleiben erhalten. Fehlerklassen können zusammen
auftreten; die Gesamtsummen werden nicht durch das Entfernen problematischer Läufe
geschönt. Erwartete Sollfälle werden niemals als Ersatzreferenz eingesetzt.

**BESTANDEN** ausschließlich bei zehn tatsächlich abgeschlossenen Kontexten,
je einem belegten Fixtureaufruf, nachgewiesener Werkzeugüberlappung, null
Agenten-/Messfehlern, null falschen oder unbekannten anwendbaren Aussagen und null
unbeurteilbaren Fragen. Bei korrekten unveränderten Szenarien wären das 16 CORRECT
und 4 NOT_APPLICABLE; bewertet wird dennoch die tatsächliche Referenz.

Jede falsche beurteilbare Observeraussage bedeutet **FAIL / NICHT BESTANDEN**;
nach Sicherung und Bewertung dieses festen Panels kein weiterer Lauf, keine
Reparatur, kein niedrigerer oder höherer Belastungstest. Ein Infrastruktur-/Quellfehler
kann ebenfalls das Bestehen verhindern, widerlegt aber nicht automatisch den Observer.
Auch bei Bestehen: STOPP, keine Zwischenstufen und keine neuen Felder.

Der Vertrag wird vor Runnerbau und Modellläufen separat committed und gepusht.
Ergebnis-Confidence und Generalisierungsgrenze bleiben getrennt. Bestehende
Fehlbefunde und Archivversionsgrenzen werden nicht überschrieben.
