# Ergebnis: manipulierter lokaler Collector C1–C7, Run 02

8. Oktober 2026. **Gesamturteil: PARTIAL / INCONCLUSIVE.** Das reale
Linux/tmpfs/Python-3.12-Gate bestand, der additive Helper wurde vorab getestet
und remote eingefroren, und die vollständige Standardsuite lief danach zweimal
grün. Der einzige eingefrorene Launcher-Versuch brach jedoch bereits beim
Modulimport vor `capture()` ab. Daher gab es null P1–P7-Observeraufrufe, keine
rohen ABCD-Antworten, keinen Pre-GT-Antwortcheckpoint und keine I/O-Ground
Truth. Es wurde vertragsgemäß nichts neu gestartet oder nach Ergebnis angepasst.

Der historische Vertrag
`OBSERVER-COLLECTOR-MANIPULATION-C1-C7-CONTRACT-2026-10-08.md` und sein
BLOCKED/INCONCLUSIVE-Ergebnis bleiben unverändert. Dieser Bericht betrifft nur
den getrennten Run 02 und etikettiert die frühere Studie nicht um.

## Repository-, Freeze- und Integritätskette

| Meilenstein | Commit / Befund |
|---|---|
| Ausgangs-HEAD, sauber | `9d6b1b2f4d1795a277acd648afceadd2a15db4ee` |
| Run-02-Vertrag, docs-only | `0532f31a726b3bb7675555c92bf9f78d00a20874` |
| Additive Auflösung des Gate-Zeitachsenkonflikts | `5e5d4ed06d3ea063c23e6ab10fd2878d26a64e2b` |
| Helper-/Test-Freeze | `43d91aea7f8aca190bf4c70b04a642e80c898a59` |
| Manifestiertes Fehler-/Gate-/Testarchiv | `2f2318e812051176ab062ad6634b4ff8ca3de02b` |
| Branch | `feat/observer-wb-automation` |
| Pushmethode | normale Pushes auf denselben Branch; kein Force-Push |

Jeder dieser vier neuen Commits wurde unmittelbar nach dem Push mit
`git ls-remote --heads origin refs/heads/feat/observer-wb-automation` gegen den
lokalen HEAD geprüft. Die Archivbelege liegen ausschließlich unter
`docs/observer-collector-manipulation-c1-c7-run02/2026-10-08/`; ihr
`MANIFEST.sha256` prüfte alle vier Nutzdateien mit `OK`.

Kontrollierte SHA-256-Werte:

| Datei | SHA-256 |
|---|---|
| eingefrorener Run-02-Vertrag | `07d72c3a9e34186e131456e78d080c8ecb093635a4c55880c26ff33a4ac8b748` |
| Run-02-Helper | `dd53c3dfa805b9e93660184219e12aaf3e6274b9dbacba00eaa2de876d938ab3` |
| additive Run-02-Tests | `a294239665964c1bfeba4936fadaba8f30300aff649d4ec2ba08dfbdb011791f` |
| unverändertes `observer_research.py` | `9279ceac9912e938fed0965b8d87e0ed311c52c7f15f87bc7292ab786cb2ce27` |
| historischer C1–C7-Vertrag | `b4d1fe82933806ed3158b5d974cb084fec762e4df92c3b26b640247f2eedfbb5` |
| historisches C1–C7-Ergebnis | `5a0781ce3828ed07d67cedb13a55797ff77a8f20c92b65f3956f4221942ce1ca` |

## Reales Gate

Die Abhängigkeiten wurden ausschließlich in einem temporären Container aus
`python:3.12-slim-bookworm` installiert. Gate, Helperprüfungen, Launcher und
Standardsuite liefen danach ohne Netzwerk, mit maximal zwei CPUs und 4 GiB
Speicher. Das Repository gelangte als `git archive HEAD` in den Container;
kein Host-Bind-Mount, `.git` oder `.venv` wurde übertragen.

| Gate | Reale Ausgabe / Projektion | Urteil |
|---|---|---|
| Kernel/Architektur | Linux `6.8.0-100-generic`, `x86_64` | PASS |
| Python | `3.12.15` | PASS |
| pytest | `8.4.2` | PASS |
| Hypothesis | `6.168.5` | PASS |
| `/tmp` | `tmpfs`, `rw,nosuid,nodev`, 256 MiB | PASS |
| Datei-/tmp-Gerät | im separaten Gate identisch (`st_dev=55`) | PASS |
| Netzwerk bei Forschung/Test | Docker `network_mode=none` | PASS |
| Ressourcenlimit | 2 CPUs, 4 GiB | PASS |

Image-ID und lokaler Repo-Snapshot wurden vor dem Launcher geprüft. Der Helper
und `observer_research.py` im Container entsprachen den eingefrorenen Hashes.

## Statische und synthetische Helperprüfung vor Freeze

Die In-Memory-Kompilierung von `observer_research.py`, allen `probes/*.py` und
allen `tests/**/*.py` umfasste **67 Dateien** und bestand. Die neue Testdatei
prüfte rein synthetisch die sieben Packetprofile, C5s einzelnes Projektdelta,
C6s Abbruch vor nativen Aufrufen, C7s vollständige Wrapperkontrolle und die
`finally`-Restaurierung. Diese Fake-Prüfungen sind ausdrücklich keine reale
C1–C7-Messung und kein Herkunftsnachweis.

Die relevanten Linux-Tests unmittelbar vor dem Helper-Freeze ergaben:

```text
27 passed in 0.11s
```

Enthalten waren die 13 neuen Run-02-Testfälle sowie die bestehenden aktuellen
Collector- und Analyseprüfungen. Es wurden keine bestehenden Tests geändert.

## Einziger Launcher-Versuch und Stop

Ausgeführt wurde im Repository-Arbeitsverzeichnis des netzlosen Containers:

```text
python -u probes/collector_manipulation_c1_c7_run02.py \
  --out /tmp/aa-collector-manipulation-c1-c7-run02-20261008 \
  --wait-seconds 7200
```

Die direkte Dateiausführung setzte den Importpfad auf das Unterverzeichnis
`probes/`; der Repository-Root stand dem Top-Level-Import nicht zur Verfügung.
Der reale Fehler war:

```text
ModuleNotFoundError: No module named 'observer_research'
```

Der Trace zeigt den Abbruch in Zeile 26 beim Modulimport. `capture()` wurde
nicht betreten. Eine anschließende read-only Prüfung im weiter laufenden
Container bestätigte, dass das festgelegte `/tmp`-Run-Verzeichnis nicht
existierte. Damit sind folgende Zählungen belegt:

| Gegenstand | Anzahl / Status |
|---|---|
| Launcher-Versuche | 1 |
| Eintritt in `capture()` | 0 |
| P1–P7-Observeraufrufe | 0 |
| rohe ABCD-Antworten | 0 |
| Wrapper-Calljournale | 0 |
| Pre-GT-Antwortcheckpoint | nicht erzeugt |
| I/O-GT-Fälle | 0 |
| Ground Truth begonnen | NEIN |
| Reparatur oder Neustart | NEIN |

Ein technisch naheliegender anderer Aufrufmodus wurde bewusst nicht versucht.
Der Helper wurde nach seinem Freeze nicht geändert. Der Vertrag bewertet einen
Prozessabbruch beziehungsweise fehlenden Pre-GT-Checkpoint als
Invaliditätsgate; ein zweiter Versuch hätte die Einmaligkeitsregel verletzt.
Das Archiv ist daher ein Fehlerbeleg und ausdrücklich **kein**
Pre-GT-Antwortcheckpoint.

## C1–C7 und H1–H4

| Fall | Rohe A/B/C/D-Antwort | unabhängige Referenz | Bewertung |
|---|---|---|---|
| C1 / P1 | nicht erzeugt | nicht erzeugt | UNBEURTEILBAR |
| C2 / P2 | nicht erzeugt | nicht erzeugt | UNBEURTEILBAR |
| C3 / P3 | nicht erzeugt | nicht erzeugt | UNBEURTEILBAR |
| C4 / P4 | nicht erzeugt | nicht erzeugt | UNBEURTEILBAR |
| C5 / P5 | nicht erzeugt | nicht erzeugt | UNBEURTEILBAR |
| C6 / P6 | nicht erzeugt | nicht erzeugt | UNBEURTEILBAR |
| C7 / P7 | nicht erzeugt | nicht erzeugt | UNBEURTEILBAR |

H1, H2, H3 und H4 bleiben für Run 02 jeweils **INCONCLUSIVE**. Insbesondere
wird C7 weder aus dem Quelltext noch aus der synthetischen C7-Unit-Prüfung als
NOT SUPPORTED ausgegeben: Ohne reale Antwort und getrennte I/O-GT ist dieser
Grenzbefund nicht gemessen.

## Vollständige Standardsuite auf Linux/Python 3.12

Nach dem Launcherfehler lief die unveränderte vollständige Suite im selben
netzlosen Linux-Container und auf demselben eingefrorenen Repo-Snapshot zweimal
mit identischem Befehl:

```text
PYTHONDONTWRITEBYTECODE=1 python -m pytest \
  -p no:cacheprovider -o addopts='' -q
```

| Lauf | Passed | Failed | Deselected | Zeit |
|---|---:|---:|---:|---:|
| 1 | 396 | 0 | 5 | 10.02 s |
| 2 | 396 | 0 | 5 | 9.65 s |

Die fünf sichtbaren Deselektionen sind die historischen bekannten Lücken
RC-01–RC-05. Die OOS-021-Rotprobe unter `probes/` wurde nicht ausgeführt. Die
zwei grünen Läufe sind ein deterministischer Regressionsbeleg auf diesem
Commit, keine reale C1–C7-Aufnahme und kein Sicherheitsbeweis.

## Bewertung und Grenzen

- **Achse A (Durchführung/Vertrag): FAIL für die vollständige Ausführung.**
  Vertrag, Gate, isolierte Implementierung, Helper-Freeze und Suite wurden
  erreicht; Aufnahme, Pre-GT-Checkpoint und GT wurden nicht erreicht. Der
  zuvor erkannte enge Gate-Zeitachsen-SPEC-CONFLICT wurde vor dem
  Helper-Freeze additiv aufgelöst und nicht stillschweigend umgeschrieben.
- **Achse B (Hypothesen): INCONCLUSIVE.** Es existiert keine verwertbare
  Fallmessung für H1–H4.
- **CONFIDENCE IN EXPERIMENT RESULT: HIGH** für den engen Befund „Importabbruch
  vor null Observeraufrufen“ und für die zwei Suitenläufe; nicht anwendbar für
  Collectorverhalten.
- **CONFIDENCE IN GENERALIZATION: NONE.** Es gibt keine neue empirische
  C1–C7-Evidenz und keinen Quellechtheitsnachweis.

Offen bleiben alle sieben realen Fallantworten, die bidirektionale I/O-GT und
damit insbesondere die Frage, ob der aktuelle Observer in C7 eine vollständig
kontrollierte intern konsistente Quelle fälschlich als DIESELBE akzeptiert.
Run 02 wird nicht heimlich fortgesetzt. Dieses Ergebnis behauptet weder
Produktionsreife noch Sicherheit autonomer Agenten. **NEXT STEP: STOPP.**
