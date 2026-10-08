# Vorabvertrag: manipulierter Collector C1–C7, Run 03

Datum: 2026-10-08. **Neuer eigenständiger Versuch vor der ersten realen Messung.**
Ausgangscommit: `5bb1aee1f7d549ee1bbd2fabb6c12251e998fa12`.
Branch: `feat/observer-wb-automation`.
Die historischen Runs 01 und 02 samt Vertrag, Messversuchen, Fehlern und
Ergebnisarchiven bleiben unverändert. Run 02 ist abgeschlossen als
PARTIAL/INCONCLUSIVE; Run 03 ist keine Wiederholung oder Korrektur seiner Rohdaten.

## Fragestellung und eingefrorene Hypothesen

Unverändertes Messobjekt: `infer_current_local_file_identity` in
`observer_research.py`. Prüfen, ob der passive Observer dieselben oder
verschiedene lokale File-Handles unterscheiden und sichtbare Widersprüche,
unvollständige Quellen und vollständig konsistente Collectorlügen erkennen kann.
H1: Ehrliche gleiche/verschiedene Handles werden korrekt erkannt.
H2: Sichtbare widersprüchliche Projektionen führen zu UNBEKANNT.
H3: Fehlende Pflichtinformationen führen zu UNBEKANNT.
H4: Ein vollständig kontrollierter, intern konsistenter Collector kann ohne
unabhängiges Herkunftssignal nicht zuverlässig als falsch erkannt werden.
Die rohe A/B/C/D-Antwort wird *vor* Ground Truth versiegelt und nie umgedeutet.
A ist Identität, B reine Begründung aus Observerprojektionen, C beurteilt nur
interne Eignung, D gibt keinen Quellechtheitsnachweis. Kein Erwartungswert und
keine Ground Truth erreichen Observer oder Wrapper.

## Fälle (fest, P1–P7; ausschließlich lokale eigene reguläre Dateien)

| Fall | Tatsächliche Handles / künstlicher Collector | Vorab-Erwartung A |
|---|---|---|
| C1 | identische Datei zweimal geöffnet, alle Aufrufe ehrlich | DIESELBE |
| C2 | zwei verschiedene Dateien, alles ehrlich | VERSCHIEDEN |
| C3 | verschieden, vier fstat und Packet melden dieselbe Identität | UNBEKANNT |
| C4 | gleich, vier fstat und Packet projizieren verschiedene Inodes | UNBEKANNT |
| C5 | gleich, nur letzte fstat von Handle 2 wechselt Inode | UNBEKANNT |
| C6 | gleich, bei zweiter Packetreferenz fehlt regular_file; null native Aufrufe | UNBEKANNT |
| C7 | verschieden, fünf Schnittstellen und Packet melden konsistent dieselbe falsche Identität | UNBEKANNT als sicheres Wunschverhalten |

C7 mit Antwort DIESELBE bei unabhängig bestätigtem VERSCHIEDEN ist ein
NOT-SUPPORTED-Grenzbefund, auch wenn die Quelle intern widerspruchsfrei aussieht.
C3/C4 liefern **keinen** Quellechtheitsbeweis durch intern passende Daten.
Genau zwei verschiedene numerische FD-Argumente pro Fall, 32 Ausgangsbytes,
für gleiche Fälle C1/C4/C5/C6 zwei FDs auf dieselbe Datei, sonst verschiedene.
Feste Reihenfolge P1 bis P7, jeder Observerfall genau einmal. Die
Collectorwrappers dürfen nur `fcntl.fcntl`, `os.fstat`, `os.uname`,
`subprocess.run`, `os.stat` aufruflokal ersetzen und müssen restauriert werden.

## Technische Schranken und Freeze

Neuer Helper unter `probes/collector_manipulation_c1_c7_run03.py` ist eine
bytegleich-logische Kopie des bereits geprüften Run-02-Helpers, ausschließlich
mit umbenannter Beschreibung und neuem **absoluten** Ausgabepfad
`/tmp/aa-collector-manipulation-c1-c7-run03-20261008`.
Der verifizierte Import-Start erfolgt **vom Repo-Root** ausschließlich mit:
`python -u -m probes.collector_manipulation_c1_c7_run03 --out /tmp/aa-collector-manipulation-c1-c7-run03-20261008 --wait-seconds 7200`.
Run-02-Helper/Observer/bestehende Tests bleiben bytegleich.

Vor Messung: Vertrag in separatem Commit normal pushen und Remote-HEAD
verifizieren. Danach Helper samt neuem Starttest schreiben, statisch prüfen,
die betroffenen Unit-/Fake-Tests ausführen, in eigenem Commit normal pushen,
Remote-HEAD verifizieren, sauberer Git-Baum. Danach keine Änderung am Helper,
Observer, Fallprofil oder Fallorchestrierung. Keine nachträgliche Reparatur
oder zweite Aufnahme desselben Run 03.

Isolierter Linux-Container aus `python:3.12-slim-bookworm`, Python 3.12,
pytest >=8, Hypothesis >=6.100, echtes `/tmp` ausschließlich tmpfs, echte
Linux-Uname, gleiche Gerät-ID von `/tmp` und Dateien, keine Netzverbindung
bei Gate, Aufnahme, GT oder Regression. Installationen höchstens zuvor in
getrennter Laufzeit mit Netzwerk. Kein Host-Bind-Mount, keine Privilegien,
keine fremden Dateien, keine Secrets, keine Kernel-/Mountänderungen.
Repository-Snapshot nur aus sauberem eingefrorenem Git-HEAD, keine .git/.venv.

## Einmalige Messung, unabhängige Referenz und Stopregeln

Ein einziger Prozess erzeugt eigenes bislang nicht vorhandenes Run-03-Verzeichnis
0700, hält die geöffneten FDs durch die Vorabphase, speichert und SHA-256-
versiegelt rohe Inputs, rohe ABCD-Antworten, Wrapper-Journale. Prozess wartet
auf **externen** Checkpoint `continue-after-remote-checkpoint`. Zuvor dürfen
keine I/O-GT und keine inhaltliche Sollwertbewertung stattfinden.
Zuerst Pre-GT-Dateien in
`docs/observer-collector-manipulation-c1-c7-run03/2026-10-08/pre-gt`
archivieren, Prüfsummen prüfen, separat committen, normal pushen und
`git ls-remote` gegen HEAD bestätigen. Erst danach autorisiert derselbe
wartende Prozess die getrennte bidirektionale 32/64/96-Byte-I/O-Ground-Truth
für C1/C2/C3/C4/C7. C5 belegt fstat-Delta/Wrapperrestauration; C6 belegt
Packetmangel/null native Aufrufe. Keine Ground Truth aus Namen, Pfaden,
Inodes oder Packetangebot ableiten.

Pre-GT-Fehler, fehlende Remote-Bestätigung, Hashfehler, FD-Verlust, ungeeignetes
Gate oder unvollständige GT => PARTIAL/INCONCLUSIVE. Beurteilbare falsche
Identitätsbehauptung => NOT SUPPORTED; alle Anforderungen einschließlich
ehrlicher Positivkontrollen erfüllt => SUPPORTED IN THIS CASE SET. Hypothesen,
Durchführungsachse und Generalisierbarkeit getrennt bewerten.
Im Anschluss die vollständige bestehende Linux-Python-3.12-Testsuite zweimal
mit sichtbaren Deselektionszahlen ausführen (historische OOS-021-Rotprobe
bleibt ausgeschlossen), Bericht unter
`docs/OBSERVER-COLLECTOR-MANIPULATION-C1-C7-RUN03-RESULTS-2026-10-08.md`
schreiben, normal pushen, Remote bestätigen; **STOPP**.
