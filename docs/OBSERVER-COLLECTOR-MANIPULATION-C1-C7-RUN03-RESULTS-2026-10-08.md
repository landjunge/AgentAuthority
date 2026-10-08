# Ergebnis: manipulierter lokaler Collector C1–C7 — unabhängiger Run 03

Datum: 8. Oktober 2026. **Messung abgeschlossen; Gesamtbewertung: NOT SUPPORTED
für die sieben eingefrorenen Fallanforderungen.** Durchführung der Messkette:
PASS. Empirische Reichweite: **nur** dieser lokale Linux/tmpfs-Test und dieser
unveränderte Observer, kein allgemeiner Produkt- oder Sicherheitsnachweis.

## Einmalige Durchführung und Freeze

- Ursprünglicher Run 02 bleibt PARTIAL/INCONCLUSIVE und unverändert.
- Getrennter, **vor dem Experiment veröffentlichter** Run-03-Vertrag:
  `e83d59d6a600b97dad52376b63875c494fc96503`.
- Separat geprüfter und vor Messung eingefrorener Run-03-Helper/Test:
  `af3538f393a9e91e52598b92328f35dda58f9bea`.
  Run-03-Helper unterscheidet sich vom Run-02-Helper ausschließlich durch
  Beschreibung und eindeutigen Ausgabepfad. `observer_research.py` blieb
  unverändert (SHA-256
  `9279ceac9912e938fed0965b8d87e0ed311c52c7f15f87bc7292ab786cb2ce27`).
- Vorabprüfung der Import-/Wrapper-/Collector-Testgruppe:
  **24 bestanden, 0 fehlgeschlagen**.
- Linux `x86_64`, Python `3.12.15`, pytest `8.4.2`,
  Hypothesis `6.168.5`, `/tmp` = echtes `tmpfs`;
  isolierter Docker-Container, `network_mode=none`, 2 CPUs, 4 GiB RAM.
- **Genau ein** Run-03-Capture-Prozess mit **sieben** Observeraufrufen
  P1–P7; Original-Wrapper nach jedem Aufruf restauriert.
- **Vor Ground Truth**: sieben rohe Inputpackets, sieben rohe ABCD-Antworten,
  sieben Calljournale; **23** Nutzdateien im `pre-gt-manifest.json`
  SHA-256-verifiziert. Pre-GT-Checkpoint als eigener Commit
  `351e457a43709ce7eea35cd32f471acb3685476a` normal gepusht
  und per `git ls-remote` bestätigt.
- Erst **nach** der Remote-Bestätigung erfolgte die Autorisierung derselben
  wartenden Messung für die unabhängige bidirektionale I/O-Referenz.
  Ground Truth für C1, C2, C3, C4, C7 beendet: **0 GT-Fehler**;
  C5/C6-Kontrollen vorhanden; **0 Cleanup-Fehler**, 0 verbliebene Handles
  und 0 verbliebene Versuchsdateien. Post-GT-Manifest: **8 Nutzdateien**,
  SHA-256-verifiziert. Containerprozess Exitcode **0**.
- Rohdaten, beide Hashmanifeste und Testsuite-Logs:
  `docs/observer-collector-manipulation-c1-c7-run03/2026-10-08/`.
  Kein nachträglicher Observeraufruf, keine Wiederholung eines Falles.

## Eindeutige Messergebnisse

`A` ist die unverändert gespeicherte Observer-Aussage; I/O-GT wurde
getrennt **erst nach** versiegeltem Remote-Checkpoint erhoben.
`C=JA` sagt nur, dass die *angebotenen* Collectorwerte intern passen,
**nicht**, dass sie authentisch sind. D verneint ausdrücklich die
Behauptung, Packetherkunft bewiesen zu haben.

| Fall | Rohe Antwort A | Rohe C | Unabhängige I/O-GT bzw. Kontrollbefund | Fallbewertung |
|---|---|---|---|---|
| C1 | DIESELBE | JA | DIESELBE | KORREKT |
| C2 | VERSCHIEDEN | JA | VERSCHIEDEN | KORREKT |
| C3 | DIESELBE | JA | VERSCHIEDEN | **FALSCH** |
| C4 | VERSCHIEDEN | JA | DIESELBE | **FALSCH** |
| C5 | UNBEKANNT | NEIN | ein manipuliertes abschließendes `fstat` (Handle 2), vier Rückgaben, Wrapper restauriert | KORREKT |
| C6 | UNBEKANNT | NEIN | `regular_file` fehlt; **0** native Aufrufe, Wrapper restauriert | KORREKT |
| C7 | DIESELBE | JA | VERSCHIEDEN | **FALSCH** |

**Besonders wichtig:** C3, C4 und C7 enthalten angebotene, intern
konsistente, jedoch falsche Identitätsprojektionen. Der Observer antwortet
positiv statt mit dem für diese adversarialen Fälle eingefrorenen UNBEKANNT.
C7 manipuliert sämtliche fünf erlaubten Collector-Schnittstellen konsistent;
die eigene I/O-Prüfung beweist dennoch, dass die Handles verschieden sind.
Es ist daher **eine gemessene Erkennbarkeitsgrenze**, nicht ein
Importfehler oder ein fehlerhafter Regressionstest. Die D-Aussagen
beanspruchen in keinem dieser Fälle einen Quellechtheitsnachweis.

## Hypothesen und Reichweite

- **H1** (ehrliche positive Identität): in C1/C2 **SUPPORTED im engen Scope**.
- **H2** (widersprüchliche/irreführende Projektionen -> UNBEKANNT):
  nur C5 mit zeitlichem fstat-Widerspruch erfüllt; die vertraglichen
  C3/C4-Wunschantworten werden **nicht** erreicht. Die manipulierten
  Projektionen sind für den Observer intern konsistent und deshalb kein
  sichtbarer Widerspruch aus seiner Perspektive.
- **H3** (unvollständiges Packet -> UNBEKANNT): in C6 **SUPPORTED im Fall**.
- **H4** (keine garantierte Erkennung vollständig kontrollierter Quelle):
  C7 liefert den konkreten **negativen Grenzbefund**; keine daraus
  abgeleitete universelle Aussage über alle Quellen.

**Achse A – Experimentdurchführung: PASS** innerhalb des eingefrorenen
Run-03-Vertrags. **Achse B – volle Fallanforderungen: NOT SUPPORTED**, da
drei beurteilbare Falschaussagen auftreten. **CONFIDENCE IN EXPERIMENT
RESULT: HIGH** für diese lokalen aufgezeichneten Fakten;
**CONFIDENCE IN GENERALIZATION: LOW/NONE** außerhalb des engen
Linux/tmpfs/Observer-Szenarios. Weder Hash, Git, intern konsistente
Collectorwerte noch grüne Regressionstests beweisen Quellechtheit.

## Vollständige Regression nach Ground Truth

Zweimal identisch im selben isolierten netzlosen Linux/Python-3.12-Container:

```sh
PYTHONDONTWRITEBYTECODE=1 python -m pytest -p no:cacheprovider -o addopts='' -q
```

| Suite | Bestanden | Fehlgeschlagen | Abgewählt | Dauer | Prozess |
|---|---:|---:|---:|---:|---|
| Lauf 1 | 398 | 0 | 5 | 11.59 s | Exit 0 |
| Lauf 2 | 398 | 0 | 5 | 11.19 s | Exit 0 |

Die fünf Abwahlen entsprechen den historisch ausgeschlossenen RC-01–RC-05.
OOS-021 wurde nicht gestartet. Diese Regressionen sichern die getestete
Funktionsstabilität, **nicht** die adversariale Wahrheit der Collectorquelle.

**Abschluss:** Keine Korrektur von C1–C7 innerhalb dieses Runs, keine
Umbewertung der historischen Studien; die tatsächliche falsche Sicherheit
bei manipulierten Quellen wird als eigenständiger Forschungsbefund
archiviert. **STOPP nach Remote-Abschlussbestätigung.**
