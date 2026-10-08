# Vorabvertrag: manipulierter lokaler Collector C1–C7, Run 02

8. Oktober 2026. Geplanter Ausgangscommit
`9d6b1b2f4d1795a277acd648afceadd2a15db4ee`. Dies ist ein **neuer,
getrennter** Versuch. Der historische Vertrag
`OBSERVER-COLLECTOR-MANIPULATION-C1-C7-CONTRACT-2026-10-08.md` und sein
BLOCKED/INCONCLUSIVE-Ergebnis bleiben unverändert und werden nicht als
ausgeführte Studie umgedeutet. Run 02 verwendet eigene Dateien, einen eigenen
Linux-Prozess und das neue Archiv
`docs/observer-collector-manipulation-c1-c7-run02/2026-10-08/`.

Dieser docs-only Vertrag wird vor jeder experimentellen Implementierung auf
`feat/observer-wb-automation` committed, normal gepusht und mit
`git ls-remote` bestätigt. Danach ist er unveränderlich.

## Forschungsfrage und eingefrorene Hypothesen

Was erkennt der unveränderte passive Observer
`infer_current_local_file_identity` gegenüber einer falschen,
widersprüchlichen oder unvollständigen Collectorquelle? Kann er eine intern
konsistente, vollständig manipulierte Quelle unabhängig als Lüge erkennen?

- H1: Ein ehrlicher aktueller Collector trägt in diesem engen Linux/tmpfs-Scope
  DIESELBE beziehungsweise VERSCHIEDEN für zwei gehaltene reguläre Handles.
- H2: Ein sichtbarer Widerspruch zwischen angebotenen oder wiederholten
  Collectorprojektionen führt zu UNBEKANNT, nicht zu einer
  Identitätsbehauptung.
- H3: Fehlende notwendige Typ-, Scope- oder Prüfinformation führt zu
  UNBEKANNT, nicht zu VERSCHIEDEN.
- H4: Ein vollständig kontrollierter, intern konsistenter Collector kann ohne
  unabhängiges vertrauenswürdiges Herkunftssignal nicht garantiert als falsch
  erkannt werden. Insbesondere ist C7 ein erwarteter negativer Grenzbefund,
  falls der Observer trotz unabhängiger I/O-GT DIESELBE meldet.

H1–H4, die A/B/C/D-Projektion und die I/O-GT-Regeln entsprechen methodisch dem
historischen Vertrag. Ihre Bedeutung wird nicht rückwirkend geändert. Run 02
liefert höchstens Evidenz für diese sieben Fälle, keine allgemeine
Sicherheitslösung und keinen Produktionsreife- oder Quellechtheitsnachweis.

## Gefahrmodell und unveränderter Gegenstand

Gegenstand ist ausschließlich die vorhandene Funktion
`infer_current_local_file_identity(events, run=1, handles=...)` in
`observer_research.py`. Diese Datei und alle bestehenden Tests bleiben
bytegleich. Der Versuchsprozess hält ausschließlich selbst erzeugte reguläre
Dateien. Aufruflokale Python-Wrapper dürfen nur im eigenen Prozess die von der
Funktion verwendeten Aufrufe `fcntl.fcntl`, `os.fstat`, `os.uname`,
`subprocess.run` und `os.stat` delegieren oder durch die unten eingefrorenen
Projektionen ersetzen. Alle Originale werden in `finally` restauriert.

Kein Kernel, Mount, Namespace, Betriebssystem, fremder Prozess und keine
fremde Datei wird verändert. Keine Host-Privileges, Secrets, externe Aktion,
Freigabe-, Verweigerungs-, Budget- oder Policyentscheidung. Der Angreifer
kontrolliert je nach Fall bestimmte Collectorantworten, nicht die separate
bidirektionale I/O-GT, die Fallorchestrierung oder bereits versiegelte
Antwortbytes.

## Laufzeit- und Gate-Vertrag

Die Aufnahme ist nur gültig in einem Container aus
`python:3.12-slim-bookworm` oder einem inhaltlich darauf basierenden,
isolierten temporären Image mit Python 3.12, `pytest>=8` und
`hypothesis>=6.100`. Abhängigkeiten dürfen einmal mit Netzwerk ausschließlich
in dieser isolierten Laufzeit installiert werden. Gate, statische Prüfungen,
Unit-Tests, Aufnahme, GT und Standardsuite laufen danach mit `--network none`.

Vor Aufnahme werden gesichert und geprüft:

- `os.uname().sysname == "Linux"` und reale Kernelangabe;
- `/tmp` wird durch `findmnt -T /tmp -n -o FSTYPE` als ausschließlich `tmpfs`
  bestätigt;
- `os.stat("/tmp").st_dev` ist das Gerät der Versuchsdateien;
- Python ist 3.12; pytest und Hypothesis erfüllen die Mindestversionen;
- der Run-02-Vertrag ist Remote-HEAD-Ancestor, der Baum ist sauber und das
  additive Helper-/Testset existiert noch nicht.

Gate-Fehler beenden Run 02 ehrlich als BLOCKED/INCONCLUSIVE. macOS- oder
synthetische Antworten gelten niemals als Linux-Messung.

## Eingefrorene A/B/C/D-Ausgabe

Pro Fall werden die direkte unveränderte ABCD-Rückgabe, das exakte Inputpacket
und das Wrapper-Calljournal vor jeder GT-Inhaltsprüfung archiviert.

- A ist die rohe Identitätsantwort DIESELBE / VERSCHIEDEN / UNBEKANNT.
- B bleibt die rohe Observerbegründung zusammen mit den tatsächlich
  angebotenen Wrapperprojektionen; keine GT und kein Sollwert gehen ein.
- C wird als Observeraussage über die vollständig passende (`JA`), sichtbar
  unzureichende/widersprüchliche (`NEIN`) oder technisch nicht beurteilbare
  (`UNBEKANNT`) Collectorlage gelesen. C beweist keine Quellechtheit.
- D ist nur dann methodisch korrekt, wenn der unveränderte Grenztext keine
  Packetherkunft behauptet; formal D=NEIN bezüglich Quellechtheit. Interne
  Konsistenz kann D nie zu JA machen.

Ein Auswertungshelfer darf A nicht ergänzen oder korrigieren. Fallname,
Erwartung und GT werden dem Observer und seinen Wrappern nie übergeben.

## Eingefrorene Fälle und Manipulationsprofile

Alle Fälle verwenden `run=1`, genau zwei verschiedene numerische FD-Argumente
und ein neutrales Packet P1 bis P7. Jeder Fall besitzt ein frisches Dateipaar
mit 32 zufälligen Ausgangsbytes. C1, C4 und C5 öffnen dieselbe Datei zweimal;
C2, C3 und C7 öffnen zwei exklusiv erzeugte verschiedene Dateien. C6 verwendet
ein eigenes gleiches Dateipaar, erreicht wegen der Packetform aber keinen
nativen Aufruf. Alle nicht ausdrücklich manipulierten Aufrufe delegieren an
das Original und werden protokolliert.

| Fall | Vorab eingefrorene Collectorprojektion | Erwartung A | Erwartung C / D |
|---|---|---|---|
| C1 / P1 | Alle fünf Schnittstellen delegieren ehrlich. | DIESELBE | JA / NEIN |
| C2 / P2 | Alle fünf Schnittstellen delegieren ehrlich. | VERSCHIEDEN | JA / NEIN |
| C3 / P3 | Tatsächlich verschieden. Nur alle vier `fstat`-Antworten projizieren beide Handles auf das reale erste `(st_dev, st_ino)`; das Packet bietet dieselben gleichen Paare. `fcntl`, `uname`, `run` und `/tmp`-`stat` delegieren. | UNBEKANNT | JA / NEIN |
| C4 / P4 | Tatsächlich dieselbe Datei. Nur alle vier `fstat`-Antworten projizieren Handle 1 auf sein reales Paar und Handle 2 auf dasselbe Gerät mit der fest gewählten positiven Ersatz-Inode `real_st_ino + 1`; das Packet bietet diese verschiedenen Paare. Übrige Aufrufe delegieren. | UNBEKANNT | JA / NEIN |
| C5 / P5 | Tatsächlich dieselbe Datei. Packet und initiale `fstat`-Antworten sind ehrlich gleich; ausschließlich die abschließende `fstat`-Antwort für Handle 2 verwendet `real_st_ino + 1`. Alle anderen Aufrufe delegieren. | UNBEKANNT | NEIN / NEIN |
| C6 / P6 | Der zweiten Referenz fehlt als einzige Formabweichung der Schlüssel `regular_file`; Wrapper sind installiert, müssen aber null native Aufrufe sehen. | UNBEKANNT | NEIN / NEIN |
| C7 / P7 | Tatsächlich verschieden. Alle fünf erlaubten Schnittstellen werden intern konsistent kontrolliert: `fcntl` meldet Erfolg, alle vier `fstat`-Antworten dasselbe feste reguläre Paar `(os.stat("/tmp").st_dev, 424242)`, `uname` Linux, `run` Erfolg/tmpfs und `stat("/tmp")` dasselbe Gerät; Packet passt exakt. | UNBEKANNT als sicheres Wunschverhalten | JA / NEIN |

`real_st_ino + 1` darf nur verwendet werden, wenn es positiv und ungleich ist;
andernfalls ist der Lauf vor dem ersten Observeraufruf ungültig. C3/C4/C7 mit
C=JA bedeuten ausschließlich, dass die angebotene Sicht intern passt. Eine
positive falsche A-Antwort bleibt FALSCH. Besonders DIESELBE in C7 ist der
eingefrorene NOT-SUPPORTED-Grenzbefund, kein zu reparierender Testfehler.

## Getrennte bidirektionale I/O-Ground Truth

C1–C4 und C7 verwenden nach dem Pre-GT-Checkpoint unverändert die bestehende
`io_reference`-Semantik: validierte vollständige 32-Byte-Ausgangsreads,
64-/96-Byte-Markerwrites, eigene und gegenseitige vollständige Reads sowie
EOF-Prüfung. Gegenseitige Kopplung in beiden Richtungen ergibt DIESELBE;
eigene sichtbare Änderungen bei unveränderter Gegensicht ergeben VERSCHIEDEN;
gemischte oder fehlgeschlagene I/O bleibt UNBEURTEILBAR. Native Paare,
Packetwerte, Pfade, Fallnamen und Sollurteile bestimmen diese GT nicht.

C5 belegt getrennt das exakt eine projizierte Vor-/Nachdelta und die
vollständige Wrapperrestauration. C6 belegt die fehlende Pflichtinformation im
gesicherten Input und null native Aufrufe. Diese beiden Kontrollen beweisen
unzureichende Evidenz, nicht Ressourcenverschiedenheit.

## Einmaligkeit, Prozesshaltung und Pre-GT-Freeze

Nach grünem Gate wird ein additiver Helper plus additive Fake-/Unit-Tests unter
`probes/` und `tests/` statisch geprüft, getestet, separat committed, normal
gepusht und per `git ls-remote` eingefroren. Danach werden Helper, Tests,
Observer, Fallprofile und Orchestrierung nicht geändert.

Es gibt genau **einen** gültigen neuen Messprozess in einem vorher nicht
existierenden privaten Verzeichnis
`/tmp/aa-collector-manipulation-c1-c7-run02-20261008` mit Modus 0700 und fester
Reihenfolge P1, P2, P3, P4, P5, P6, P7. Der Prozess hält sämtliche Handles
offen und führt jeden Observerfall genau einmal aus. Danach versiegelt er
Inputpacket, rohe ABCD-Antwort und Calljournal mit SHA-256 und wartet ohne
inhaltliche GT-Prüfung auf eine explizite Fortsetzung.

Diese Rohdateien werden aus dem netzlosen Container in das neue Git-Archiv
kopiert, separat als Pre-GT-Checkpoint committed, normal gepusht und remote
bestätigt. Erst danach wird derselbe wartende Prozess einmalig zur I/O-GT
fortgesetzt. Kein Fall wird repariert, neu gestartet oder wiederholt. Ein
Prozessabbruch, fehlender Checkpoint, Hashfehler oder eine unvollständige GT
ergibt PARTIAL/INCONCLUSIVE; erwartete Daten werden nicht angepasst.

## Erlaubter additiver Umfang

Nach Vertragsfreeze sind ausschließlich erlaubt:

- ein isolierter Run-02-Helfer unter `probes/` und seine neuen Unit-Tests unter
  `tests/`;
- das neue Archiv
  `docs/observer-collector-manipulation-c1-c7-run02/2026-10-08/`;
- der neue Ergebnisbericht
  `docs/OBSERVER-COLLECTOR-MANIPULATION-C1-C7-RUN02-RESULTS-2026-10-08.md`.

Historische C1–C7-Dateien und Archive, `observer_research.py`, bestehende Tests
und bestehende Forschungsberichte werden nicht geändert.

## Invaliditäts-, Bewertung- und Stopregeln

INCONCLUSIVE statt SUPPORTED gilt bei fehlendem Linux/tmpfs/Python-Gate,
unsauberer Wrapperrestauration, Helperänderung nach Freeze, zusätzlichem
Observeraufruf, fehlendem Remote-Pre-GT-Checkpoint, beschädigter Integrität,
fehlender unabhängiger Referenz oder partieller/uneindeutiger GT. Keine
Quellechtheit wird aus Hash, Git, Commitreihenfolge oder intern konsistenten
Wrapperwerten abgeleitet.

Pro Fall lautet die Bewertung KORREKT / FALSCH / UNBEURTEILBAR. C1/C2 müssen
positiv nutzbar sein; C3/C4/C5/C6 müssen die eingefrorenen Erwartungen halten;
C7 wird getrennt als Quellechtheitsgrenze bewertet.

- **SUPPORTED IN THIS CASE SET** nur, wenn alle positiven und negativen
  Anforderungen bei gültigen Referenzen halten und D nie Quellechtheit
  vortäuscht.
- **NOT SUPPORTED**, sobald eine beurteilbare falsche Identitätsbehauptung
  entsteht, insbesondere DIESELBE in C7.
- **INCONCLUSIVE** bei einem Invaliditätsgate oder fehlender gültiger
  Laufzeit/Referenz.

Achse A (Durchführung/Vertrag) und Achse B (Hypothese) sowie CONFIDENCE IN
EXPERIMENT RESULT und CONFIDENCE IN GENERALIZATION werden getrennt berichtet.
Nach der GT wird die vollständige vorhandene Suite in derselben passenden
Linux-Python-3.12-Umgebung zweimal identisch mit sichtbaren Test- und
RC-Deselektionszahlen ausgeführt; OOS-021 bleibt als historische Rotprobe
ausgeschlossen. Danach folgen neuer Ergebnisbericht, Abschlusscommit, normaler
Push und `git ls-remote`-Bestätigung. Dann **STOPP**.
