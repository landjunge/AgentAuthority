# P1: Implementierung, tatsächlicher Startversuch und Grenzen

9. Oktober 2026. Grundlage: [vorab gespeicherter P1-Vertrag](P1-CONTROLLED-RUN.md)
und der unverändert kopierte [Forschungsplan](OBSERVER-REAL-RUN-PROTOTYPE-PLAN-2026-10-07.md).
Der Vertrags-Hash blieb seit Beginn der Implementierung unverändert:
`6d473e188fb60968ec94471c71cd7da7f1590336e9cdf85413d90b44af5bd264`.

## Ergebnis zuerst

Der kleine Mess-/Auswertungsweg ist implementiert und getestet. Der reale
CLI-Zugang konnte in dieser Umgebung keinen belegten Agentenlauf liefern.
**Ein tatsächlich gestarteter CLI-Prozess, null belegte Modell-/Agentenläufe,
null Werkzeugmeldungen, null instrumentierte Werkzeugaufrufe.** Kein Fake- oder
Unit-Test-Lauf wurde als reales Agentenergebnis archiviert.

[Messarchiv](p1-runs/2026-10-09-attempt-01/result.json): Der CLI-Prozess endete
erfolglos, ohne stdout-JSONL; stderr umfasste 199 Bytes. Fehlertext wurde nicht
archiviert. Die genaue Startfehlerursache, Authentisierung und Modellverfügbarkeit
sind damit nicht diagnostiziert. Keine Aufhebung von Sandboxregeln, kein
Credential-/HOME-/CODEX_HOME-Ersatz und kein nativer Ersatzlauf.

Der unabhängige Dateisensor belegt **nur**: das lokale Testziel war vor dem
Versuch und am Ende des Messfensters nicht vorhanden. Das ist ein gültiger
negativer Zustandsbefund, keine Behauptung über eine Agentenwirkung. Da die
separate Werkzeugreferenz fehlt, sind Agentenlauf und Referenzbewertung
**UNBEKANNT**. Ein erfolgreicher realer P1-Agentenlauf bleibt ausstehend.

## Implementierung und Belegtrennung

[`scripts/p1_controlled_run.py`](../scripts/p1_controlled_run.py) verwendet nur
die Standardbibliothek, keine Labmodule oder neue Produktkomponenten. Ein
temporäres Testwerkzeug kann ein leeres Ziel anlegen. Die Auswertung importiert
keine Autorisierungslogik und entscheidet keine Agentenrechte.

| Archiv | Funktion |
|---|---|
| `observations.json` | Laufgebundene Anfangs-/Endmessung, tatsächlich gemessener CLI-Endempfang, vorhandene projizierte Werkzeugmeldungen. Nur fünf begründete Planfelder. |
| `analysis.json` | Zielzustandsaussage aus den Beobachtungen; vor Lesen der Referenz gespeichert. Fehlende/ungültige/widersprüchliche Belege oder Aufzeichnungsfehler ergeben UNBEKANNT. |
| `reference.json` | Nachgelagerte getrennte Werkzeugreferenz, tatsächliche Aufrufzahl und zusätzliche Dateiprüfung. Fehlende Referenz erzeugt keinen Sollwert. |
| `result.json` | Prozess-/Aufzeichnungszähler, belegte Agentenläufe, Zustandsaussage und Referenzvergleich getrennt. |

Die Dateiprüfung übernimmt weder Werkzeugstatus noch Agentenprosa. Identische
Ereignisduplikate sind idempotent; geänderte gleiche Referenzen und mehrere
Endbelege sind unentscheidbar. Vorhandene Symlinks/Sonderdateien liefern keinen
positiven Zielbeleg. Erfolgreiche Werkzeug-/CLI-Meldungen allein bleiben unbekannt;
eine tatsächlich vorhandene Datei kann trotz Werkzeugfehler belegt sein.

Streams sind auf 64 KiB pro stdout-Zeile und etwa 1 MiB insgesamt begrenzt;
maximal ein zusätzlicher 8-KiB-Leseblock kann vor der Grenzprüfung anfallen.
Die CLI-Laufzeit ist begrenzt. Prozesspflege betrifft nur die eigene lokale
Prozessgruppe. Archivfehler werden weitergegeben und nicht als Erfolg verschluckt.
Neue Ausgabeverzeichnisse verhindern Überschreiben früherer Versuche.

## Tatsächlich ausgeführte Prüfungen

- Ausgangssuite vor Änderungen: 213 bestanden; bestehende RC-Ausschlüsse.
- 35 neue Tests: Status/Wirkung auseinanderhalten, fehlende/falsche Laufbindung,
  fehlende/konfligierende Belege, Duplikate, Reihenfolge, strenge primitive
  Projektion, Canary-Ausschluss, Referenztrennung, Sensorfehler und Symlinks.
  Tatsächliche lokale Prozesse testen Werkzeugvarianten, fehlerhafte/zu große/
  tief verschachtelte Eingaben sowie Timeout. Synthetische CLI-Ereignisse sind
  ausdrücklich Unit-Testdaten, keine realen Modellläufe.
- Gesamtsuite zweimal: **248 passed, 5 deselected**, 9,54 s und 9,40 s.
- Ruff für beide neuen Python-Dateien: Check und Formatprüfung bestanden.
- Historische Lücken separat nachgeprüft: RC-01–05 weiterhin rot
  (**5 failed, 5 passed**); OOS-021-Probe weiterhin rot (**1 failed**).
  Alte Tests und Labcode wurden nicht verändert; diese Befunde bleiben offen.

Der reale Versuch fand während der Implementierung statt. Danach wurden nur
Validierung für fehlerhafte Testeingaben und Formatierung vervollständigt.
Die archivierten Beobachtungen wurden mit der finalen Auswertung erneut geprüft;
ihre Aussage ist unverändert. Kein erneuter CLI-Lauf wird behauptet.

## Bewertung und ungelöste Grenzen

**Achse A:** PASS für die begrenzten P1-Mess-/Auswertungsakzeptanzen. Kein PASS
für einen erfolgreichen realen Modelllauf oder den vollständigen Forschungsplan.
**Achse B:** INCONCLUSIVE: die Realhypothese ist mit null belegten Agentenläufen
nicht beurteilbar. **CONFIDENCE IN EXPERIMENT RESULT:** HIGH für den aufgezeichneten
Startausfall und die getesteten lokalen Auswertungsregeln; keine positive
Confidence in reale Agentenerkennung. **CONFIDENCE IN GENERALIZATION:** LOW.

„Unabhängig“ bedeutet zwei getrennte lokale Messwege, keinen externen Audit.
Agent und Werkzeug können im selben lokalen Vertrauensbereich Dateien ändern.
Receipts und CLI-Meldungen sind nicht authentisiert. Ein kompromittierter Host,
gefälschte Referenzen, Ressourcen-/Elternpfadwechsel und uninstrumentierte
Nebenwirkungen werden nicht vollständig erkannt. Modellabschluss plus
Werkzeugmeldung ist nur der konservative Nachweis dieses vertrauenswürdig
angenommenen CLI-Wegs; echte Werkzeugausführung ohne Abschluss kann unbestätigt bleiben.

Der Snapshot belegt den benannten Abfragepunkt, keine Dauerhaftigkeit oder
Kausalität. Nicht geprüft: Zeitordnung gegenüber physischem CLI-Ende,
Nachwirkungen, Cancel/Widerruf, Remote-Stopp, vollständige Toolsicht, IFC,
Prompt Injection, Secretsicherheit, Kosten oder menschliche Verständlichkeit.
Die vollständige Sechs-Fall-Studie, Feldablation und unabhängiger Methodenreview
des Forschungsplans wurden nicht durchgeführt. Keine historische Lücke wird
durch P1 geschlossen.

Reviewniveau ist **0: Autor-Selbstprüfung**. Git-Metadaten liegen außerhalb der
erlaubten Schreibpfade: keine Commits/Pushes, keine behauptete Freeze-Commitfolge.
Das ist eine sichtbare Prozessabweichung. Keine Genehmigung wurde angefragt oder
eine Schutzgrenze umgangen. **STOPP** nach diesem begrenzten Befund.
