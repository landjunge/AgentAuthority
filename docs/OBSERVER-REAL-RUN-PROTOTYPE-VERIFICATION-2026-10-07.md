# Post-Implementation Verification: Minimaldaten-Prototyp

Interner Review, kein externer Audit. Grundlage sind der unveränderte
[Bauplan](OBSERVER-REAL-RUN-PROTOTYPE-PLAN-2026-10-07.md) und die separat eingefrorene
[Laufzeitauflösung](OBSERVER-REAL-RUN-RUNTIME-RESOLUTION-2026-10-07.md).

## Erster Codefreeze und abgeschlossener Review

Geprüft: `091a44864499b3832a8d68206638295acb9b061f`.
Ein Review im vorhandenen Projektkontext (Level 1) und ein neuer Reviewer-Kontext
mit Quellen/Code/Artefakten statt Implementierungsdialog (Level 2), einschließlich
separater lesender Artefaktgegenprüfung. Reviewer änderten nichts, führten keine
Tests aus und begannen keine neuen Experimente. Code blieb während des Reviews
unverändert. Beide Reviews sind abgeschlossen.

Die sechs tatsächlichen nativen Panelbefunde sind konsistent: 32 Beobachtungen,
420 Ableitungen, Vollsicht 10 CORRECT/2 NOT_APPLICABLE, beide Statusvergleiche
je 2 WRONG, ohne Zielbelege 10 UNKNOWN/2 NOT_APPLICABLE. Alle 32 Feldteilmengen,
Referenzintervalle und gemeinsamen Panelminima wurden lesend gegengeprüft.
`run/kind/value` reichen beim festgelegten Analysten für sechs Zielsnapshots,
zusätzlich `t_ns` für die vier anwendbaren Zeitvergleiche. Dies ist kein allgemeines
Informationsminimum. `native_end` bleibt ein Kommunikationsempfangspunkt.

Level-1-Review: PASS für den begrenzten geprüften Vertrag und die drei zuvor
gefundenen Baufehler-Korrekturen. Level-2-Review: begrenzter PASS der vorhandenen
Panelbefunde, ausdrücklich kein uneingeschränkter PASS der Fehlerpfade.
Der konkretere Fehlerbefund bleibt erhalten:

1. Ungültige, unvollständige oder ungeordnet gebrackettete Werkzeugreferenzen
   werden nicht vollständig validiert. `lo=50, hi=10` könnte trotz Widerspruch
   eine entschiedene Wahrheit liefern. Das verletzt den bestehenden Bauplan:
   widersprüchliche Referenz muss unbeurteilbar bleiben. **Achse A: FAIL dieses
   Fehlerpfads**, kein Fehler der vorhandenen gültigen Panelintervalle.
2. Gültiges CLI-JSON mit nicht-stringförmigem `type` kann den Readerthread mit
   TypeError beenden, ohne Invalidzähler. Nicht im nativen Panel beobachtet;
   statisch belegter Messfehler, keine Widerlegung einer CLI-Forschungshypothese.
3. `tested_additions:[[]]` bei einer Kontrollansicht ohne Zielbelege könnte eine
   erfolgreiche Ergänzung suggerieren. Es bezeichnete globale Feldminima der
   ursprünglichen vollständigen Beobachtungsmenge. Der getrennte Belegvergleich
   ist korrekt; die Scopeangabe der Feldaddition fehlt.
4. Aufnahme fand während des Baus statt, vor ergänzten Fehlerpfadfeldern
   `tool_attempts`/`failure`. Original-`capture.json` entspricht daher nicht exakt
   dem Serializer des ersten Codefreeze. Originaldaten werden nicht nachgefüllt
   oder als erneuter Lauf ausgegeben. Herkunft/Versionsgrenze steht im Ergebnis.

Confidence: HIGH für die gültigen Panelvergleiche; MEDIUM für reale Aufnahme in
der vertrauten lokalen Strecke; LOW für Generalisierung. Hypothesen im nativen
Panel bleiben H1 REFUTED, H2/H3 eng SUPPORTED. Direkte CLI bleibt INCONCLUSIVE.

## Begrenzte Korrektur nach Abschluss dieses Reviews

Daniels laufender Auftrag ist der Bau eines messbaren Forschungsinstruments,
einschließlich korrekter unbekannter/falscher Aussagen. Die Korrektur dient nur
diesem bereits eingefrorenen Messvertrag. Es entsteht keine neue Hypothese,
kein neuer Prüfpunkt, keine Erweiterung der Datenerhebung und kein neuer realer Lauf.
Das ist keine Änderung des Specs, keine Reparatur historischer Systeme und kein E8.

Vor dem Korrekturbau festgehaltene Abnahme:

- Ungültige Referenzdatei/-einträge und ungültige Typen/Reihenfolge der lokalen
  Zeitintervalle liefern unbekannte Wahrheit mit festem Fehlerstatus; kein
  Rohwert oder Fehlermeldungstext wird übernommen.
- CLI-Projektion zählt nicht-stringförmiges `type` als ungültiges Record,
  statt bei Setmitgliedschaft zu scheitern.
- Feldadditionen gelten ausschließlich für gleiche ursprüngliche Beobachtungszeilen;
  bei Status-/Belegverlustkontrollen werden sie als nicht anwendbar ausgewiesen.
  Tatsächlich nötige Belege bleiben in `information_comparisons`.
- Neue gezielte synthetische Messlogiktests, unveränderte Standardsuite zweimal,
  erneute Auswertung derselben gespeicherten nativen Originalbelege und erneuter
  lesender Review am neuen Codecommit. Keine neuen Agentenläufe.

Dieser Befund/Korrekturvertrag wird vor der Korrektur separat committed und gepusht.
Die Erstbefunde werden nicht durch eine spätere positive Prüfung gelöscht.

## Zweiter abgeschlossener Review: verbleibender Schemafehler

Geprüft: `d724ce14d08e1d13fd8cf1ccf0d0d282ce6747d0`. Code blieb während der
beiden rein lesenden Reviews unverändert; Reviewer führten keine Tests/Läufe aus.
Typ-/Intervall-/JSONfehler, CLI-Recordtyp und Ergänzungsmetadaten sind korrigiert.
60 Messlogiktests und zweimal 299 passed/5 deselected wurden vom Autor ausgeführt.
Originalbeobachtungen, Capture und Referenz sind bytegleich; Hypothesenbefunde
und 420 Ableitungen bleiben erhalten.

Level-2-Review wertete die geprüften Guardteile als PASS. Der weitere
Level-1-Review fand einen spezifischeren Restfehler: leere/unbekannte Dicts im
Receipt werden ignoriert. `{"call":true}` plus `{}` und ein fehlendes Ziel können
dadurch sichere negative Wahrheit erhalten. Beide Reviewurteile werden erhalten;
**für den gesamten engen Receiptvertrag gilt wegen dieses Gegenbeispiels FAIL**.
Das widerlegt keine der sechs gültigen, unveränderten Originalreferenzen.

Der eigene Producer schreibt genau drei Eintragsformen: `call:true`, ein
vollständiges gültiges Creation-Intervall oder `creation_conflict:true`.
Der Restfehler wird nach diesem abgeschlossenen Review ausschließlich durch
Akzeptanz dieser vorhandenen privaten Formen korrigiert. Kein neuer Event,
Feldbedarf, Prüfpunkt oder Agentenlauf. Neue synthetische Empty-/Unknown-/False-
Receiptfälle prüfen denselben zuvor eingefrorenen Vertrag. Danach Standardsuite
zweimal, neuer Codefreeze und abschließender lesender Delta-Review.

Zusätzliche ausdrücklich offene Grenze: fertige `reference.json`-Archive werden
beim Report nicht gegen böswillige nachträgliche Änderungen authentisiert oder
erneut aus Originalsyscalls erzeugt. Die geprüften Originalarchive sind konsistent;
keine allgemeine Archivintegritäts-/Quellechtheitsgarantie entsteht daraus.
