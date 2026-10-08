# Vorabvertrag: manipulierter lokaler Collector C1–C7

8. Oktober 2026. Ausgangscommit
`957ccf76d5455e3ec073c70a279112646e5db0c3`. Dieser docs-only Vertrag wird
vor einer Fallausführung committed, auf dem vorhandenen Branch gepusht und per
`git ls-remote` bestätigt. Frühere Ergebnisse, insbesondere V3/V5, F1–F7,
RC-01–05, OOS-021, E2 und K14, bleiben historisch unverändert.

## Forschungsfrage und eingefrorene Hypothesen

Was erkennt der aktuelle passive Observer gegenüber einer falschen,
widersprüchlichen oder unvollständigen Collectorquelle? Kann er eine intern
konsistente, vollständig manipulierte Quelle unabhängig als Lüge erkennen?

- H1: Ein ehrlicher aktueller Collector trägt in diesem engen Linux/tmpfs-Scope
  DIESELBE beziehungsweise VERSCHIEDEN für zwei gehaltene reguläre Handles.
- H2: Einzelne Widersprüche zwischen angebotenem Packet und aktuellen oder
  wiederholten Collectorprüfungen führen zu UNBEKANNT, nicht zu einer
  Identitätsbehauptung.
- H3: Fehlende notwendige Typ-, Scope- oder Prüfinformation führt zu
  UNBEKANNT, nicht zu VERSCHIEDEN.
- H4: Ein vollständig kontrollierter, intern konsistenter Collector kann ohne
  unabhängiges vertrauenswürdiges Herkunftssignal nicht garantiert als falsch
  erkannt werden. Insbesondere ist C7 ein erwarteter negativer Grenzbefund,
  falls der Observer trotz unabhängiger I/O-GT DIESELBE meldet.

Keine allgemeine Sicherheitslösung wird gebaut. Es gibt keine Kryptografie,
Signatur, Attestation, TPM-Nutzung, Policyentscheidung oder neue
Observerfunktion. Agent Authority bleibt Beobachter und steuert niemals
Freigabe, Verweigerung, Budget, Secrets oder echte Agentaktionen.

## Gefahrmodell und Vertrauensgrenze

Gegenstand ist unverändert
`infer_current_local_file_identity(events, run, handles=...)`. Der
Versuchsprozess hält ausschließlich eigene reguläre Dateien. Ein isolierter
Testwrapper darf nur innerhalb dieses Prozesses die vom Observer verwendeten
Aufrufe `fcntl.fcntl`, `os.fstat`, `os.uname`, `subprocess.run` und `os.stat`
delegieren oder mit eingefrorenen Testwerten ersetzen. Betriebssystem, Kernel,
Mounts, fremde Dateien und Produktionssysteme werden nicht verändert.

Der Angreifer kann je nach Fall einen Teil oder alle Collectorantworten
kontrollieren. Er kontrolliert nicht das separate bidirektionale I/O-Orakel,
die Fallorchestrierung oder die vor dem Ground-Truth-Abgleich gesicherten
Antwortbytes. Wrapper werden in `finally` vollständig restauriert. Keine
Root-, Kernel-, Namespace-, Netzwerk- oder Fremdressourcentechnik.

Ein intern konsistenter Wert ist kein Herkunftsbeweis. Hashes und Git belegen
nur Byteintegrität und den dokumentierten Ablauf, nicht Quellechtheit oder
unabhängige Zeit.

## Linux-Gate und aktueller Vorabbefund

Ein gültiger Falllauf erfordert tatsächlich Linux, `/tmp` auf tmpfs und eine
bereits vorhandene Python-3.12-Testumgebung. macOS-Ausgaben dürfen niemals als
Linux-Messung gelten. Vor Freeze wurde nur die Verfügbarkeit legitimer
bestehender Wege geprüft:

- der gebundene Host ist Darwin 24.6.0;
- der ausgewählte OrbStack-Docker-Socket fehlt;
- Colima ist gestoppt;
- Lima hat keine Instanz;
- die vorhandene GitHub-CI läuft nur für `master`/Pull Requests und enthält
  keinen C1–C7-Aufnahmejob.

Es wird keine VM, kein Container, keine neue Infrastruktur und keine neue
Workflow-Automation gestartet oder installiert. Bleibt nach dem Vertragsfreeze
kein tatsächlicher gültiger Linux-Lauf verfügbar, endet dieser Forschungszyklus
mit einem ehrlichen **BLOCKED / INCONCLUSIVE**-Bericht. In diesem Pfad entstehen
keine Fallantworten, keine Ground Truth und kein Implementierungsbeleg.

## Eingefrorene Ausgabe A/B/C/D

Jeder Fall archiviert die direkte rohe ABCD-Rückgabe der unveränderten Funktion
vor jeder inhaltlichen Ground-Truth-Lektüre. Eine zusätzliche rein formale
Projektion für den Forschungsbericht verwendet:

- A: rohe Identitätsantwort DIESELBE / VERSCHIEDEN / UNBEKANNT.
- B: rohe tragende Observerbegründung zusammen mit den tatsächlich angebotenen
  Wrapperprojektionen; keine Ground Truth und kein Sollwert.
- C: rohe C-Antwort als Sicht des Observers auf eine vollständig passende
  (`JA`), bekannte unzureichende/widersprüchliche (`NEIN`) oder technisch nicht
  beurteilbare (`UNBEKANNT`) Collectorlage. Das ist interne Konsistenz aus
  Observerperspektive, keine Quellechtheit.
- D: `NEIN`, wenn der unveränderte D-Grenztext wie eingefroren ausdrücklich
  keine Packetherkunft beweist; andernfalls UNBEKANNT. Nie JA allein aus
  konsistenten Collectorwerten.

Der Projektionshelfer darf keine Identitätsentscheidung ergänzen oder
korrigieren. Rohantwort, Projektion und angebotene manipulierte Werte werden
gemeinsam gesichert. Erwartungsnamen, Sollurteile und GT gehen nie in den
Observerinput.

## Eingefrorene Fälle

Alle Aufrufe verwenden run=1 und exakt zwei verschiedene aktuelle numerische
FD-Argumente, soweit der Fall nicht gerade die notwendige Information vor der
nativen Prüfung ungültig macht. Der Wrapper sieht neutrale Packets P1–P7, nie
Fallname oder Erwartung.

| Fall | Tatsächliche Lage und angebotene Collectorquelle | Erwartung A | Erwartung C / D | Bewertungsschwerpunkt |
|---|---|---|---|---|
| C1 / P1 | Eine eigene Datei separat zweimal geöffnet; alle Collectoraufrufe ehrlich delegiert. | DIESELBE | JA / NEIN | Positivkontrolle gegen I/O-GT DIESELBE. |
| C2 / P2 | Zwei getrennt exklusiv erzeugte eigene Dateien; alle Collectoraufrufe ehrlich delegiert. | VERSCHIEDEN | JA / NEIN | Positivkontrolle gegen I/O-GT VERSCHIEDEN. |
| C3 / P3 | Tatsächlich zwei verschiedene Dateien; erforderliche native Vor-/Nachpaare und Packet werden als gleich präsentiert, übriger Scope intern passend. | UNBEKANNT | JA / NEIN | DIESELBE ist FALSCH, auch wenn die manipulierte Sicht intern konsistent wirkt. |
| C4 / P4 | Tatsächlich dieselbe Datei; erforderliche native Vor-/Nachpaare und Packet werden als verschieden präsentiert, übriger Scope intern passend. | UNBEKANNT | JA / NEIN | VERSCHIEDEN ist FALSCH. |
| C5 / P5 | Vor- und Nachprüfung widersprechen beim nativen Paar oder bei FD-Gültigkeit. | UNBEKANNT | NEIN / NEIN | Keine Identitätsbehauptung bei sichtbarem Widerspruch. |
| C6 / P6 | Erforderliche Typ-, Scope- oder Prüfinformation fehlt oder widerspricht bereits in der angebotenen Form. | UNBEKANNT | NEIN / NEIN | Fehlender Beleg ist keine Verschiedenheit. |
| C7 / P7 | Tatsächlich zwei verschiedene Dateien; **alle** Collectorantworten und das Packet präsentieren intern konsistent dieselbe Identität. | UNBEKANNT als sicheres Wunschverhalten | JA / NEIN | DIESELBE ist der zentrale eindeutige negative Vertrauensgrenzenbefund. |

Für C3/C4/C7 bedeutet erwartetes C=JA nur: die dem Observer vollständig
angebotene manipulierte Sicht ist intern konsistent. Es entschuldigt keine
falsche A-Antwort. D bleibt NEIN. C5 variiert genau einen sichtbaren
Vor-/Nach-Widerspruch. C6 verwendet genau eine fest vorab gewählte fehlende
Pflichtinformation: `regular_file` der zweiten Referenz fehlt; dadurch dürfen
keine nativen Aufrufe erfolgen.

## Unabhängige Ground Truth

C1–C4 und C7 verwenden die unveränderte bidirektionale I/O-Referenz:
32-Byte-Ausgangszustand, eigene 64-/96-Byte-Markerwrites, vollständige Reads
mit EOF-Prüfung. Gegenseitige Kopplung in beiden Richtungen ergibt DIESELBE;
sichtbare eigene Änderungen bei jeweils unveränderter Gegensicht ergeben
VERSCHIEDEN; gemischte oder fehlgeschlagene I/O ist UNBEURTEILBAR. Native
Paare, Packetwerte, Fallnamen, Pfade und Solloperationen bestimmen die GT nicht.

C5 belegt unabhängig die absichtlich verschiedenen Vor-/Nachprojektionen und
vollständige Wrapperrestauration. C6 belegt die fehlende Pflichtinformation im
gesicherten Input und null native Aufrufe. Beide Fälle beweisen unzureichende
Evidenz, nicht Ressourcenverschiedenheit.

## Reihenfolge, Pre-GT-Sicherung und Freeze

Nur bei bestandenem Linux-Gate:

1. Ein statisch geprüfter isolierter Capture-/Response-Helper wird additiv
   erstellt, getestet, committed, gepusht und remote bestätigt.
2. Genau ein Falllauf in einem neuen privaten Ordner
   `/tmp/aa-collector-manipulation-c1-c7-20261008` (0700), feste Reihenfolge
   P1 bis P7, keine Wiederholung oder Reparatur.
3. Pro Fall zuerst Observerantwort, angebotene Wrapperwerte und Calljournal
   speichern; anschließend Antwortdateien SHA-256-versiegeln.
4. Alle Antworten und Originaljournale als Checkpoint committen, pushen und
   remote bestätigen, bevor der Prüfer GT inhaltlich vergleicht.
5. Erst danach getrennte Auswertung und Bericht.

Der Vertrag wird nach diesem Commit nicht geändert. Nach Helper-Freeze werden
Observer, Wrapper und Fallprotokoll nicht geändert. Bestehende Tests bleiben
unverändert. Ein gescheiterter oder partieller Lauf wird archiviert und nicht
als ursprünglicher Erfolg wiederholt.

## Datei- und Änderungsumfang

Erlaubt nach Vertragsfreeze, nur wenn das Linux-Gate besteht:

- additive isolierte Dateien unter `probes/` und passende additive Tests;
- neues Archiv unter
  `docs/observer-collector-manipulation-c1-c7/2026-10-08/`;
- Ergebnisbericht
  `docs/OBSERVER-COLLECTOR-MANIPULATION-C1-C7-RESULTS-2026-10-08.md`.

`observer_research.py`, bestehende Tests, frühere Verträge, Berichte und
Archive bleiben bytegleich. Im BLOCKED-Pfad werden nur Vertrag und
Ergebnisbericht neu angelegt.

## Invaliditäts- und Honesty-Gates

INCONCLUSIVE statt SUPPORTED bei fehlender echter Linux/tmpfs-Laufzeit,
unsauberer Wrapperrestauration, fehlendem Pre-GT-Checkpoint, beschädigter
Antwortintegrität, fehlender unabhängiger Referenz, zusätzlichem Falllauf oder
partieller/uneindeutiger GT. Erwartete positive Antworten dürfen nicht durch
pauschales UNBEKANNT erreicht werden.

Keine Quellechtheit aus `true`, Hashgleichheit, Commitreihenfolge oder intern
konsistenten Werten ableiten. Keine falsche A-Antwort wegen korrektem C oder D
als bestanden werten. Keine Testerwartung nach Beobachtung ändern. Keine
fehlenden Daten als VERSCHIEDEN behandeln. Keine macOS- oder synthetischen
Systemcalls als echte Linux-Messung ausgeben.

## Bewertung und Stopkriterien

Pro Fall: KORREKT / FALSCH / UNBEURTEILBAR, mit direkter Rohantwort,
angebotenen Werten, unabhängiger Referenz, Checkpoint-Hash und Fehlerklasse.
C1/C2 müssen positiv nutzbar bleiben. C3/C4/C5/C6 müssen wie eingefroren
enthalten. C7 wird separat als Quellechtheitsgrenze bewertet und kann nie durch
interne Konsistenz pauschal bestehen.

- **SUPPORTED IN THIS CASE SET** nur, wenn alle positiven und negativen
  Anforderungen tatsächlich halten, alle Referenzen gültig sind und D nie
  Quellechtheit vortäuscht.
- **NOT SUPPORTED**, sobald eine beurteilbare falsche Identitätsbehauptung
  entsteht, insbesondere DIESELBE in C7.
- **INCONCLUSIVE** bei einem Invaliditätsgate oder fehlender gültiger Laufzeit.

Achse A (Durchführung/Vertrag) und Achse B (Hypothese) werden getrennt
ausgewiesen; ebenso CONFIDENCE IN EXPERIMENT RESULT und CONFIDENCE IN
GENERALIZATION. Bei gültigem Lauf folgt die unveränderte Standardsuite zweimal:

```sh
PYTHONDONTWRITEBYTECODE=1 /workspace/venvs/authority/bin/python -m pytest -p no:cacheprovider -o addopts='' -q
```

Kann die Suite nicht auf tragfähigem Linux laufen, wird sie nicht als grün
behauptet. Fünf historische RC-01–05-Deselektionen bleiben sichtbar;
OOS-021-Rotprobe wird nicht ausgeführt. Nach Bericht, Commit, normalem Push und
Remote-SHA-Bestätigung: **STOPP**. Kein weiterer Forschungsblock.
