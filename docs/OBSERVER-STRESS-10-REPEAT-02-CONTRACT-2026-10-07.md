# Belastungsstufe 10: ausdrücklich beauftragte Wiederholung 02

7. Oktober 2026. Daniel beauftragt: „noch einmal gleichen test genauso wiederholen“.
Das autorisiert genau eine Wiederholung; der STOPP des Erstlaufs wird nicht als
automatische Wiederholungserlaubnis ausgelegt.

Ausgangspunkt: `c0ac45b9bda2fe09c17789b910a514e11bf5f223`.
Der vollständige [ursprüngliche Vertrag](OBSERVER-STRESS-10-CONTRACT-2026-10-07.md)
und [Erstbefund](OBSERVER-STRESS-10-RESULTS-2026-10-07.md) wurden gelesen.
Der Erstlauf bleibt NICHT BESTANDEN und unverändert erhalten.

Identisch wiederverwendet werden:

- Observer, Recorder, Sensor, Referenz-/Bewertungsfunktionen, Fixture und
  `research/stress_10.py` am bereits festgeschriebenen Stand.
- Genau zehn neue native Agentenkontexte, geringe Reasoning-Stufe; Start 6+4
  innerhalb derselben Grenze von sechs aktiven Testkontexten neben dem Koordinator.
- Modi `write/noop/fail/write_fail/late` zweimal, dieselben Laufnummern 1–10.
- Beide Startbarrieren mit unverändert 60 Sekunden, Nachbeobachtung 0,5 Sekunden.
- Genau dieselben zwei Fragen, Minimalmengen und Bestehenskriterien.
- Keine Wiederholung eines fehlgeschlagenen Einzelauftrags, Reparatur, neuen
  Felder oder weitere Belastungsstufe innerhalb dieser Wiederholung.

Neu sind ausschließlich die frischen Kontexte, temporären Ziele und getrennten
Ausgabepfade: `/tmp/aa-stress-10-repeat-02-20261007` sowie dauerhaft
`docs/observer-stress-10/2026-10-07/repeat-02/original` und `derived`.
Prompt und Terminalauftrag entsprechen dem Erstlauf; die Sessionadresse wird
durch die neue Adresse ersetzt. Zufällige Laufzeiten werden nicht künstlich an
die früheren Zeitpunkte angepasst oder als veränderte Parameter behandelt.

Auch die Steuerungsbuchführung wird nicht repariert: Startbestätigungen der
ersten sechs Kontexte erst nach deren Spawn und empfangenen Abschlüssen,
danach die vorhandenen Abschluss-Callbacks; vor der zweiten Gruppe deren
Dispatchmarken. Solche Marken sind keine ursprünglichen Modellstartzeiten.
Werkzeugüberlappung wird weiterhin aus den tatsächlich gemessenen
Aufrufintervallen bestimmt. Keine zehn simultanen Modellkontexte behaupten.

Alle Originale werden unverändert archiviert; Vorhersagen und Bewertung getrennt
gespeichert. Referenz erst nach den zwanzig Vorhersagen lesen. Fehlerklassen und
unbeurteilbare Fälle bleiben erhalten. Ein neuer PASS überschreibt den früheren
FAIL nicht; ein neuer FAIL wird nicht repariert oder durch eine dritte Wiederholung
ersetzt. Danach Ergebnis, Commit/Push, Remote bestätigen und STOPP.

Diese Aufzeichnung wird vor dem Lauf separat committed und gepusht.
