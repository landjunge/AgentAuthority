# Ergebnis: unabhängige lokale FD-Identitätsprüfung

Datum: 2026-10-08. **Gesamtbewertung: PASS + SUPPORTED IN THIS MODEL.**
Der neue Grenzkanal bewahrt C1/C2 positiv und reicht C3/C4/C7 nicht falsch
positiv weiter; C5/C6 bleiben fail-closed. Diese Bewertung betrifft nur die
Relation der tatsächlich an den sauberen Verifier übergebenen FDs. Sie ist
ausdrücklich **kein Nachweis der authentischen Herkunft dieser Ressourcen**.

## Freeze und Änderungsumfang

- Ausgangscommit: `cc9a8d0f2184ca440155a691f2a64f791b50d175`.
- Separat vor Implementierung eingefrorener und remote bestätigter Vertrag:
  `4b5895212a7bb248c94dbcff9cc49b6066b31eb5`.
- Separat remote bestätigter Implementierungs-/Testcommit:
  `49e7d9d9608020fc4a9ae3eefc4e609b4bec70bc`.
- Bis zum Ergebnisbericht kamen gegenüber dem Ausgangscommit ausschließlich
  der neue Vertrag, `probes/independent_local_fd_identity.py` und
  `tests/test_independent_local_fd_identity.py` hinzu.
- `observer_research.py` blieb unverändert, SHA-256
  `9279ceac9912e938fed0965b8d87e0ed311c52c7f15f87bc7292ab786cb2ce27`.
  Ebenso unverändert blieben der historische Fail-closed-Replay
  `probes/collector_source_boundary_analysis.py` (SHA-256
  `36bb0fde6f3dc9f975555111e2ccfa253392bbeb61e7c66ce74659c1540e846d`),
  die Run03-Probe, sämtliche historischen Messdaten/Tests und alle Workflows.

## Gebauter unabhängiger Messweg

Der vertrauenswürdige Broker startet mit `python -I -S` einen neuen
Interpreter per `subprocess.Popen`/`exec`; es läuft kein fortgesetzter
importierter Collectorprozess. Ein direktes UNIX-Socketpaar ist der einzige
übergebene Brokerkanal. Genau zwei Kernel-FD-Rechte werden mit `SCM_RIGHTS`
gesendet. Der Verifier führt je FD `F_GETFD` und `fstat` vor und nach der
Relationsermittlung aus, verlangt zwei reguläre Dateien und unveränderte
Flags sowie geordnete `(st_dev, st_ino)`-Paare.

Die Antwort ist an Protokollversion, frische 256-Bit-Nonce, Request-ID,
Kind-PID, Eltern-PID und den direkten Prozess gebunden. Der Broker validiert
die Messzeilen selbst und gibt nur dann eine positive Aussage aus, wenn die
gemessenen geordneten Paare exakt mit den Packetpaaren und die daraus folgende
Relation exakt mit Observer-`A` übereinstimmen. Jede Abweichung oder technische
Störung ergibt `UNBEKANNT`. Auch ein positives Ergebnis trägt stets
`source_authenticated=false`; es authentisiert nur den aktuellen FD-Satz.

## C1-C7-Ergebnis aus neu geöffneten Dateien

Die Tests erzeugten für jeden Fall neue eigene reguläre Dateien auf `/tmp`.
Keine archivierte Run03-Ground-Truth wurde als Verifiereingabe verwendet. Die
Produktionslogik kennt keine Fallnummern oder Sollwertliterale.

| Fall | Tatsächliche übergebene FDs | Packet / ursprüngliches Observer-A | Broker-Endantwort | Befund |
|---|---|---|---|---|
| C1 | gleiche Datei, zwei numerische FDs | echte gleiche Paare / DIESELBE | **DIESELBE** | brauchbares Positiv bewahrt |
| C2 | zwei verschiedene Dateien | echte verschiedene Paare / VERSCHIEDEN | **VERSCHIEDEN** | brauchbares Positiv bewahrt |
| C3 | zwei verschiedene Dateien | konsistent falsch gleich / DIESELBE | **UNBEKANNT** | `verifier_packet_mismatch` |
| C4 | gleiche Datei, zwei numerische FDs | konsistent falsch verschieden / VERSCHIEDEN | **UNBEKANNT** | `verifier_packet_mismatch` |
| C5 | gleiche Datei | zeitlich widersprüchlich / UNBEKANNT | **UNBEKANNT** | keine positive Observeraussage |
| C6 | gleiche Datei | `regular_file` fehlt / UNBEKANNT | **UNBEKANNT** | Packetform unvollständig |
| C7 | zwei verschiedene Dateien | fünf Quellen konsistent falsch gleich / DIESELBE | **UNBEKANNT** | `verifier_packet_mismatch` |

Ergebnis der Matrix: **2 brauchbare Positive, 0 falsche Positive,
5 fail-closed Antworten**. Anders als der historische pauschale Replay setzt
der neue Weg nicht alle sieben Fälle auf `UNBEKANNT`.

## Prozess- und Negativkontrollen

Die 25 neuen Linux-Tests belegen zusätzlich:

- Verifier-PID und Broker-PID sind verschieden; `ppid` bindet das Kind an den
  Broker. Der gemeldete Interpreter stimmt mit dem gestarteten Interpreter
  überein, und die Syscallherkunft ist die frische Exec-Instanz.
- Gleichzeitige quellenseitige Monkeypatches für alle fünf erlaubten
  Schnittstellen (`fcntl.fcntl`, `os.fstat`, `os.uname`, `subprocess.run`,
  `os.stat`) werden im neuen Interpreter nicht geerbt und wurden vom Broker
  nicht als Ersatzmessung aufgerufen.
- Ungültige FDs, Pipes statt regulärer Dateien, fehlender Verifier,
  Verifierprozessfehler und Timeout liefern `UNBEKANNT`. Timeout- und
  Fehlerkinder werden beendet beziehungsweise geerntet.
- Null, ein oder drei übergebene FD-Rechte werden abgewiesen; nur genau zwei
  sind zulässig.
- Eine Antwort ohne Noncebindung sowie falsche Nonce, fehlende Request-ID,
  manipuliertes Urteil und veränderte Nachmessung werden abgewiesen.
- Vertauschte FDs und andere, nicht zum Packet passende Ersatz-FDs ergeben
  `UNBEKANNT`. Die Original-FDs des Brokers bleiben offen; Kindkopien,
  Socketenden und Prozesse werden bereinigt.
- Ein korrekt gemessener FD-/Packetbefund kann eine widersprechende
  Observerantwort nicht überstimmen; auch dann ist das Ergebnis `UNBEKANNT`.

## Ehrlich belegte Herkunftsgrenze

Ein eigener Negativbefund demonstriert die nicht lösbare Grenze dieses
Trust-Modells: Übergibt ein Sender andere gültige FDs **und passt zugleich
Packet und Observerprojektion an genau diese Ersatz-FDs an**, stimmen alle
drei Ebenen überein. Der Broker kann diese Substitution nicht von der
ursprünglich gemeinten Ressource unterscheiden und gibt die Relation des
Ersatzsatzes positiv aus. Das Ergebnis bleibt dabei korrekt mit
`source_authenticated=false` und einer ausdrücklichen Herkunftswarnung
markiert.

Damit ist der funktionsfähige unabhängige FD-Vergleich von authentischer
Ressourcenherkunft getrennt. Nicht abgedeckt sind kompromittierter Broker,
Verifier oder Kernel, ein außerhalb des Modells kontrollierter Socket- oder
Namespacepfad, FD-Neubelegung und TOCTOU außerhalb der sequenziellen
Vor-/Nachmessung, dauerhafte Identität, Pfad-, Inhalts- oder Revisionsidentität
sowie andere Hosts oder Netzwerkdateisysteme. Nonce und Request-ID binden die
Antwort an diesen direkten Kanal; sie sind keine Kernel- oder
Brokerattestation.

## Linux/Python-3.12-Reproduktion

Finale Messung exakt vom gepushten Implementierungscommit, übertragen mit
`git archive` als Tar-Stream in einen temporären Container; kein Host-Bind-
Mount, kein privilegierter Modus, `--network none`, `--cpus 2`, `--memory 4g`,
`--tmpfs /tmp:rw,nosuid,nodev,size=1g`. Image:
`aa-run03-python:20261008` (`sha256:f252fa0bcda79ed3a8283d5483fd36da26498cd9b38c8588d6e8a782ecf50542`).

- Linux `6.8.0-100-generic`, `x86_64`, Python `3.12.15`.
- `/tmp`: `tmpfs`, `rw,nosuid,nodev,noexec`, Größe 1 GiB.
- Relevante Gruppe aus neuem Testmodul plus unveränderten Source-Boundary-,
  Current-Collector-, Run02- und Launcher-Tests: **58 bestanden,
  0 fehlgeschlagen**, 2.36 s.
- Vollsuite Lauf 1: **431 bestanden, 0 fehlgeschlagen, 5 abgewählt**, 12.31 s.
- Vollsuite Lauf 2: **431 bestanden, 0 fehlgeschlagen, 5 abgewählt**, 11.98 s.

Die Abwahlen sind die bereits historisch ausgeschlossenen Real-Case-Fälle;
die OOS-021-Rotprobe wurde nicht gestartet. Die für diesen Branch bestehende
Remote-Aktion `Authority Collector Source Boundary` lief für
`49e7d9d9608020fc4a9ae3eefc4e609b4bec70bc` ebenfalls erfolgreich
(Run `37764520071`). Es wurde kein Workflow ergänzt oder geändert.

## Bewertung der eingefrorenen Hypothesen

- **H1 SUPPORTED:** Der saubere Verifier unterschied aktuelle stabile
  reguläre FD-Paare in C1/C2 korrekt.
- **H2 SUPPORTED IN THIS CASE SET:** Exakter Dreifachabgleich bewahrte C1/C2
  positiv.
- **H3 SUPPORTED IN THIS CASE SET:** C3/C4/C7 wurden generisch durch
  Mess-/Packetabweichung zurückgehalten; C5/C6 sowie sämtliche technische und
  Bindungsfehler blieben fail-closed.
- **H4 SUPPORTED als Grenzbefund:** Die Relation des tatsächlich empfangenen
  Satzes ist unabhängig messbar; dessen ursprüngliche semantische Herkunft
  bleibt bei passend manipulierter Substitution unbeweisbar.

**Achse A – Vertragsumsetzung: PASS. Achse B – Hypothesen: SUPPORTED IN THIS
MODEL. CONFIDENCE IN EXPERIMENT RESULT: HIGH** für die aufgeführten lokalen
Linux/tmpfs-Fakten. **CONFIDENCE IN GENERALIZATION: LOW** außerhalb des
eingefrorenen Trust-Modells. Kein produktiver Authority-Gate wurde verändert.
Mit Bericht, Push und Remote-SHA-Abgleich endet dieser Forschungsabschnitt;
keine weitere Serie wird begonnen.
