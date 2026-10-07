# Identische Wiederholung 02: NICHT BESTANDEN

7. Oktober 2026. Genau eine ausdrücklich beauftragte Wiederholung des
[Ersttests](OBSERVER-STRESS-10-RESULTS-2026-10-07.md).
Der [Wiederholungsauftrag](OBSERVER-STRESS-10-REPEAT-02-CONTRACT-2026-10-07.md)
wurde vor dem Lauf committed/gepusht unter
`b1279befdaefaefda28ea10374e407e0f94cf476`.

Unverändert: Observer, kompletter Stressrunner, Fixture, Referenzerzeugung,
Minimalfelder, 60-Sekunden-Barrieren, 0,5-Sekunden-Nachbeobachtung,
10 frische Kontexte mit geringer Reasoning-Stufe und 6+4-Startverfahren.
Dieselben Prompt-/Auftragstexte; ausschließlich Sessionadresse, temporäre Ziele
und Ausgabepfade wurden für den neuen Lauf ersetzt. Keine Parameteroptimierung,
Reparatur oder ersetzte Einzelaufträge. Zufällige Laufzeiten wurden nicht manipuliert.

## Messbarer Stand

| Messung | Erstlauf | Wiederholung 02 |
|---|---:|---:|
| Gestartete Agentenkontexte | 10 | 10 |
| Tatsächlich abgeschlossene Agentenkontexte | 10 | 10 |
| Ausgeführte Fixtureaufträge | 9 | 9 |
| Ausführungsfehler | 1: Lauf 7 | 1: Lauf 1 |
| Aufnahme-/Messwerkzeugfehler | 1: Lauf 7 | 1: Lauf 1 |
| Nachgewiesene LLM-Anweisungsfehler | 0 | 0 |
| Sensorfehler | 0 | 0 |
| Korrekte Aussagen | 15 | 14 |
| Falsche beurteilbare Aussagen | 0 | 0 |
| Unbekannt bei beurteilbarer Referenz | 0 | 0 |
| Nicht anwendbar | 3 | 4 |
| Unbeurteilbar | 2 | 2 |
| Maximale Werkzeugaufrufüberlappung | 6 | 5 |
| Gesamturteil nach identischem Vertrag | NICHT BESTANDEN | **NICHT BESTANDEN** |

Ausführungs- und Messfehler betreffen auch diesmal **denselben Fall**, nicht zwei
unabhängige Fehler. Alle zwanzig Fragen bleiben in der Bewertung.
Die vier beabsichtigten Fixturefehler mit Exit 7 sind keine unerwarteten
Agentenfehler. Lauf 1 befolgte seinen Terminalauftrag, wartete und meldete dessen
tatsächliche Rückkehr mit Exit 2; sein Fixtureauftrag wurde vom Runner nicht ausgeführt.

## Fehler und unabhängige Referenz

Diesmal überschritt die erste Sechsergruppe die feste Startbarriere:
Ankunftsspanne **64,591429154 Sekunden**, bei unverändert 60 Sekunden Wartefrist.
Lauf 1 wurde `stress_barrier_timeout`, `timeout=true`, `tool_attempts=0` zugeordnet.
Die Referenz enthält `calls=0` und
`reference_issue=uncontrolled_or_missing_tool_execution`.
Beide Wahrheiten bleiben deshalb unbeurteilbar. Kein exakter Timeoutzeitpunkt
wurde nachträglich erfunden; die 60 Sekunden sind die vorab definierte Grenze.

Die zweite Vierergruppe traf innerhalb von **24,333405626 Sekunden** ein und
führte alle vier Aufträge aus. Gemessene Werkzeugüberlappung: erste Gruppe 5,
zweite Gruppe 4. Es bleiben eine Zehnerkohorte unter der vorhandenen
Sechs-Kontext-Grenze und zwei Startgruppen, keine zehn simultanen Modellkontexte.
Die verzögerten Startbestätigungen der ersten sechs Kontexte wurden wie im
Erstlauf beibehalten; sie sind Buchführungsmarken, keine ursprünglichen Spawnzeiten.

Ground Truth wurde unverändert aus syscall-nahen Fixtureintervallen und einem
separaten Zielcheck bestimmt. Abschluss-/Werkzeugstatus und Sollmodus sind keine
Wahrheit. Der Observer meldete für Lauf 1 den tatsächlichen Endsnapshot als nicht
vorhanden; wegen fehlender gültiger Ausführungsreferenz ist die Aussage unbeurteilbar,
nicht automatisch korrekt oder falsch. Fehlende Information bleibt kein negativer Beweis.

## Die zwanzig festen Bewertungen

| Lauf | Zielzustandsbewertung | Zeitbewertung |
|---|---|---|
| 1 | Aussage nicht vorhanden, unbeurteilbar | unbekannte Aussage, unbeurteilbar |
| 2 | nicht vorhanden, korrekt | nicht anwendbar |
| 3 | nicht vorhanden, korrekt | nicht anwendbar |
| 4 | vorhanden, korrekt | vorher, korrekt |
| 5 | vorhanden, korrekt | nachher, korrekt |
| 6 | vorhanden, korrekt | vorher, korrekt |
| 7 | nicht vorhanden, korrekt | nicht anwendbar |
| 8 | nicht vorhanden, korrekt | nicht anwendbar |
| 9 | vorhanden, korrekt | vorher, korrekt |
| 10 | vorhanden, korrekt | nachher, korrekt |

Zielzustand ausschließlich `run/kind/value`; lokale Zeitfrage ausschließlich
`run/kind/value/t_ns`. `event` und sämtliche Steuerungs-/Referenz-/Szenarioangaben
wurden nicht an `infer` gegeben. Vorhersagen vor dem Referenzvergleich gespeichert.
Die vier NA-Zeitfälle stammen aus der unabhängigen Bewertung, nicht aus positiven
Observeraussagen; dort antwortete der Observer unbekannt.

Die Zählerdifferenz zum Erstlauf folgt aus dem **anderen ausgefallenen Modus**:
diesmal fehlt ein `write`, vorher ein `noop`. Sie belegt keine verschlechterte
Observerleistung. Beide vollständigen Zehnerkohorten scheiterten an der Runnerstrecke.
Bei 14 beurteilbaren Fragen dieser Wiederholung fand sich kein Ableitungsfehler;
die unbeurteilbaren Fragen werden dadurch nicht ausgeblendet.

## Separat gesicherte Wiederholungsdaten

Originale:
[Beobachtungen](observer-stress-10/2026-10-07/repeat-02/original/observations.jsonl),
[Capture](observer-stress-10/2026-10-07/repeat-02/original/capture.json),
[Referenz](observer-stress-10/2026-10-07/repeat-02/original/reference.json),
[Kontrollbuchführung](observer-stress-10/2026-10-07/repeat-02/original/control.json).
Getrennte Ableitungen:
[Vorhersagen](observer-stress-10/2026-10-07/repeat-02/derived/predictions.json)
und [Bewertung](observer-stress-10/2026-10-07/repeat-02/derived/evaluation.json).

49 Originalbeobachtungen, 3.738 Bytes, unverändert fünf alte Recorderfelder.
SHA-256 des Beobachtungsstroms:
`4e8999458587087a5cb14eaf707a8128055ea69a873798944812409fb8d86726`.
Archivkopien sind bytegleich zur Aufnahme. Der gesamte Erstlauf einschließlich
seiner Originale, Ableitungen und FAIL-Dokumentation bleibt unverändert erhalten.
Observer, Stressrunner, Native-Driver und Fixture sind bytegleich zum Ausgangscommit
`c0ac45b9bda2fe09c17789b910a514e11bf5f223`; keine vorhandenen Tests geändert.

**Testdurchführung:** NICHT BESTANDEN wegen Runner-/Ausführungsfehler.
**Observerhypothese für die vollständige Kohorte:** weiterhin INCONCLUSIVE;
kein beurteilbarer Observerfehler nachgewiesen. Keine Generalisierung aus zwei
kleinen kontrollierten Panels. Confidence HIGH für die gespeicherten Zahlen/
gültigen lokalen Vergleiche, MEDIUM für Aufnahme unter vertrauter Orchestrierung,
LOW für Übertragung auf andere Agenten, Quellen und Uhren.

**STOPP.** Wiederholung beendet. Keine Reparatur, dritte Wiederholung oder andere Stufe.
