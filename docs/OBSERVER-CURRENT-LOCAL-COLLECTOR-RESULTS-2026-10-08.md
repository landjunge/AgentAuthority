# Unmittelbar aktueller lokaler Collector: F1–F7

8. Oktober 2026. **SUPPORTED IN THIS CASE SET**, ausschließlich für den
eingefrorenen engen lokalen Aufrufweg. Ein tatsächlicher aktueller Check trägt
F1/F2/F7; alte oder handgefertigte Packets ohne diesen Check sowie geschlossene
Handles tragen F3–F6 nur **UNBEKANNT**. Keine Produkt-/Herkunftsgarantie.

Sieben Aufrufe: **7 korrekte A, 0 falsche A; 7 korrekte C, 0 falsche C**.
Vier korrekte Identitätsenthaltungen, drei positive Identitätsaussagen mit
vollständig passender aktueller Prüfung; null unbeurteilbare Fälle.
Aufnahme-, Referenz-, Speicher- und unerwartete Messfehler: null.

## Ausgang, Freeze und Trennung

| Stand | Vollständiger Commit |
|---|---|
| Ausgang, vorheriger negativer V3/V5-Befund | `916e810b3db338defabb90c4e2437573e43e0093` |
| Neuer docs-only Vertrag | `f13078e58dba3e5dce9ee0de735bb328b9c2a5bd` |
| Additiver Forschungsweg und eingefrorene Test-/Auswertungshilfen | `4ad4ade9db7b8cccd4d47769a816d07f1eb036df` |
| Originalantworten und Journale vor inhaltlichem GT-Abgleich | `c5d0de678479441f29360f7765c0b0fc0e608d70` |

Jeder Stand vor dem nächsten Arbeitsschritt gepusht und per `git ls-remote`
remote bestätigt. [Vorabvertrag](OBSERVER-CURRENT-LOCAL-COLLECTOR-CONTRACT-2026-10-08.md)
und Implementierung nach Freeze nicht verändert. Genau eine tatsächliche
Aufnahme, keine Wiederholung oder Reparatur während/nach dem Falllauf.

Pflichtquellen vollständig gelesen bzw. deren vollständig gelesenen bytegleichen
Bestand weiterverwendet: [vorherige Gültigkeit](OBSERVER-LOCAL-EVIDENCE-VALIDITY-RESULTS-2026-10-08.md),
[Live-Dateiidentität](OBSERVER-LIVE-LOCAL-FILE-IDENTITY-RESULTS-2026-10-08.md),
[Inodensuche](OBSERVER-LOCAL-INODE-REUSE-RESULTS-2026-10-08.md),
[lokale Dateiidentität](OBSERVER-LOCAL-FILE-IDENTITY-RESULTS-2026-10-08.md),
[Methodik](RESEARCH-METHOD.md), [Debt](OUT-OF-SCOPE-DEBT.md), Observer und
lokale Aufnahme-/Antwort-/I/O-/Freigabehilfen.

## Was sich eng geändert hat

Neu: `infer_current_local_file_identity(events, run, handles=...)` als additiver
Forschungsaufruf in [observer_research.py](../observer_research.py).
Die bisherigen primitiven run/kind/value-Belege bleiben unverändert; zwei
lokale FD-Argumente existieren nur während des Aufrufs. Keine neuen
serialisierten Belegfelder oder dauerhaft verwendbaren Gültigkeitsobjekte.
Keine Handles als globale/archivierte Ressourcen-IDs.

Der bisherige Parser wird nur zur Formprüfung verwendet. Seine frühere positive
Identitätsantwort ist kein Beleg für die neue Antwort. Das neue Verfahren
verlangt zusätzlich selbst ausgeführte aktuelle Messungen:

1. Beide unterschiedlichen int-FDs mit F_GETFD/fstat auf Gültigkeit und
   regulären Dateityp prüfen, **bevor** der Collector findmnt-Pipes öffnen kann.
2. Linux per uname prüfen, /tmp per findmnt als tmpfs prüfen und /tmp-st_dev
   mit dem aktuellen Gerät beider Handles vergleichen.
3. Beide FD-/Typ-/Paarprüfungen danach wiederholen; native Paare unverändert.
4. Die aktuell gemessenen Paare müssen **geordnet** mit den angebotenen Paaren
   übereinstimmen. Dann Gleichheit → DIESELBE; Ungleichheit → VERSCHIEDEN.

Ohne Handles überhaupt keine native Prüfung. EBADF beendet die Prüfung vor
findmnt. Keine selbstbestätigenden fresh-/verified-Felder, kein Callback,
Zeitstempel-, Hash- oder Kennungsgleichheitsersatz für einen aktuellen Check.

Weiterhin nur angeboten/behauptet: run-Zuordnung, Packet-Scopewerte,
same_collection_process=true, live_handle_overlap_confirmed=true und
regular_file=true. Der alte Parser verlangt diese Form weiterhin; das zeigt
keine zusätzliche empirische Notwendigkeit jedes Flags. **Keines dieser Flags
trägt alleine die positive Aussage.** Auch Herkunft und damalige Lebenszeit
des serialisierten Packets werden dadurch nicht authentisiert.

C ist eine direkte neue Observerausgabe: JA bedeutet vollständig erfolgreich
geprüfte notwendige Live-Gültigkeit für genau den angebotenen Vergleich;
NEIN bedeutet bekannt unzureichende aktuelle Beleglage; UNBEKANNT bedeutet
technisch nicht ausreichend beurteilbare Prüfung. Ein begonnener Aufruf ist
noch kein JA. F5/F6 haben einen Prüfversuch, aber C=NEIN.

## Was tatsächlich ausgeführt und erfasst wurde

Linux `6.18.44`, Python `3.12.14`, eigenes tmpfs-Gerät `34`. Neuer privater
Ordner `/tmp/aa-current-local-collector-20261008`, lokal 0700. Vier reale
Paaraufbauten mit insgesamt sechs exklusiv erstellten eigenen Dateien,
vier vorbereitenden nativen Packets, **sieben** direkte Observeraufrufe.
Reihenfolge tatsächlich: **P1 → P3 → P5 → P4 → P2 → P6 → P7**.
Alle verwenden run=1; F3/F5 ändern run oder native Werte nicht.

[Collector-/Lebenszeitjournal](observer-current-local-collector/2026-10-08/ground-truth/collector-lifecycle.json)
zeigt: fünf Aufrufe mit nativen Prüfversuchen; davon drei vollständige aktuelle
Bestätigungen und zwei erwartete EBADF-Abbrüche. F3/F4 haben null native Calls.
Insgesamt 35 journalisierte Aufrufe: 14 F_GETFD, 12 fstat, je drei uname,
findmnt und /tmp-stat. Drei positive Fälle jeweils elf Calls, F5/F6 jeweils
ein erfolgloses F_GETFD. EBADF war die beabsichtigte Beobachtung, kein
unerwarteter Aufnahmefehler.

Test-only Wrapper führten Originalfunktionen jeweils genau einmal mit gleichen
Argumenten aus und gaben ihre Resultate/Exceptions unverändert zurück.
Sie journalisierten nur im Speicher um den API-Aufruf und wurden in finally
vor Speicherung/I/O-GT restauriert. Die Journale sind interne Ablaufbelege,
**kein unabhängiger Kerneltrace oder Attestation**. Der Observer erhielt weder
GT, Journal, F-Name, Sollantwort noch Packet-Herkunftsklasse.

Nur benötigte Paar-/Typ-/Scopeprojektionen, Vollzugsstufen, Prüfstatus,
Referenz-Read-/Write-Längen und Hashes gespeichert. Keine Dateiinhalte,
Inhaltshashes, vollständigen stat-Dumps, fremden FD-Zielpfade oder Secrets.
Die Zufallsmarker für I/O blieben nur im Arbeitsspeicher/eigenen Testdateien.
Alle sechs Dateien am Ende entfernt; null verbleibende Ressourcenfiles,
null Cleanupfehler. Operationaler eigener Freigabenachweis, kein physischer
Kernel-Reklamations- oder Fremdprozessbeweis.

## F1–F7: Originalantworten und unabhängige Referenz

Die direkten Original-A/B/C/D liegen unter
[responses](observer-current-local-collector/2026-10-08/responses/P1/answer.json).
Die folgende Tabelle kürzt B/D nur für die Darstellung; keine neue Ableitung
ersetzt die Rohantworten.

| Fall | Tatsächlich angebotene/beobachtete Lage | A / C | Unabhängige Referenz | Ergebnis |
|---|---|---|---|---|
| F1 / P1 | Zwei separat geöffnete Handles einer eigenen Datei; aktuelle Paare beide `(34,21419)`, vollständige Vor-/Nach-/Scopechecks. | DIESELBE / JA | Eigene Markerwrites sichtbar, beide Gegenansichten folgen; aktuelles Calljournal vollständig passend. | KORREKT |
| F2 / P2 | Zwei eigene Dateien; aktuell `(34,21438)` / `(34,21439)`, vollständige passende Checks. | VERSCHIEDEN / JA | Eigene Markerwrites sichtbar, beide Gegenansichten bleiben jeweils unverändert. | KORREKT |
| F3 / P3 | P1 bytegleich nach vollständiger operationaler Freigabe, keine Handles; null aktuelle Calls. | UNBEKANNT / NEIN | Beide close-Rückgaben, sofort EBADF, unlink/ENOENT, null eigene Ziel-FD-Links; keine neue Prüfung. | KORREKT |
| F4 / P4 | Handgebaut zweimal `(123,456)`, alle positiven Booleanwerte; keine Handles/Collectorherkunft. | UNBEKANNT / NEIN | Konstruktion ohne Ressourcen und null aktuelle Calls; unzureichende Beleglage. | KORREKT |
| F5 / P5 | P1 erneut bytegleich mit live=true; alte geschlossene FD-Zahlen an neuen Aufruf. | UNBEKANNT / NEIN | Alte Freigabe unabhängig dokumentiert; allererster aktueller F_GETFD endet mit EBADF, kein findmnt danach. | KORREKT |
| F6 / P6 | Gültiges Packet vorbereitet, beide Handles unmittelbar vor aktuellem Check geschlossen. | UNBEKANNT / NEIN | Zwei close-/sofortige-EBADF-Referenzen; aktueller erster F_GETFD ebenfalls EBADF; danach gesonderte unlink/ENOENT/Null-FD-Link-Freigabe. | KORREKT |
| F7 / P7 | Zwei neue eigene Dateien; gespeichert und aktuell `(34,21449)` / `(34,21450)`, vollständig passend. | VERSCHIEDEN / JA | Beide eigenen Änderungen sichtbar, beide Gegenansichten jeweils unverändert; positiver Weg bleibt nutzbar. | KORREKT |

B in F1/F2/F7 nennt tatsächlich erfolgreiche aktuelle F_GETFD/fstat-Prüfungen
vor/nach Linux/tmpfs-/tmp-Geräteprüfung und passende unveränderte Paare.
B in F3/F4 nennt fehlende Handles und unzureichende gespeicherte true-Werte;
B in F5/F6 nennt den aktuellen ersten fehlgeschlagenen F_GETFD mit EBADF.

D in allen sieben Originalantworten: aktuell gehaltene reguläre Handles im
gleichen lokalen Linux/tmpfs-Prozess ohne konkurrierendes Schließen/FD-Neubelegung
oder Mount-/Namespacewechsel; sequenzielle Checks, kein atomarer Lebenszeitbeweis;
keine Packetherkunft, historische/permanente Identität, Inhalts-/Revisionsidentität,
andere Hosts oder Ressourcen bewiesen. B/D jeweils innerhalb dieser Grenzen.

Die I/O-GT wurde **nach Speicherung/Hash der jeweiligen Antwort** separat mit
dem unveränderten bidirektionalen Orakel erfasst. Native Werte/Gleichheit,
Pfad und geplante Operation gingen nicht in dessen Identitätsurteil ein:

| GT | Read-Längen Ausgang / nach Richtung 1 / nach Richtung 2 | Erfolgreiche Markerwrites | Beleg |
|---|---|---|---|
| F1 | `[32,32]` / `[64,64]` / `[96,96]` | 64 und 96 Bytes | [F1-I/O](observer-current-local-collector/2026-10-08/ground-truth/F1-io.json) |
| F2 | `[32,32]` / `[64,32]` / `[64,96]` | 64 und 96 Bytes | [F2-I/O](observer-current-local-collector/2026-10-08/ground-truth/F2-io.json) |
| F7 | `[32,32]` / `[64,32]` / `[64,96]` | 64 und 96 Bytes | [F7-I/O](observer-current-local-collector/2026-10-08/ground-truth/F7-io.json) |

Alle drei Orakel vollständig inklusive EOF-Proben und ohne Referenzfehler.
F3–F6 beweisen ausdrücklich **keine Verschiedenheit**, sondern fehlende
hinreichende aktuelle Beleglage. C wird anhand realer Callfolge, Rückgaben,
Scope/Typen und geordnetem Pairmatch bewertet, nicht anhand der A/C-Antwort
oder eines neuen true-Felds.

## Antworten vor GT-Abgleich gesichert

Alle Antworten gespeicherte direkte API-Ausgaben, lokal read-only; sechs
Dateiressourcen erst nach erforderlicher Sicherung/Referenz wieder freigegeben.
30 Originaldateien bytegleich kopiert, 32 Dateien im Antwortcheckpoint gehasht
(Originale plus zwei Freeze-Manifeste), dann Checkpoint committed/pushed/remote
bestätigt. Prüfer las GT bis dahin nur als opaque Bytes; inhaltliche Auswertung
erst danach. Auswertung in separatem derived-Verzeichnis, Originale unverändert.

| Packet | SHA-256 der vor dem GT-Abgleich gesicherten answer.json |
|---|---|
| P1 | `0e23aea4cdc211492b958c613dba69df033830c9536e4861edfb4d0c0921705d` |
| P2 | `a632f3a86daece33714533f339edb0307f0cb8edb7fe5df17f8c60b37f50837d` |
| P3 | `456dbb2ad77a6f38183ccc16e14790871ca61b84b6d6e87247596f872419d013` |
| P4 | `12b6912c5fe10170b6e2d8956780738577d015d359e1ecaa8428a51cffdcfa88` |
| P5 | `8cc36e6524a0dac689a387a26e8644e628a040fc2667c2446086dc79e92ca03c` |
| P6 | `4225b4c4b02342827810d3ac846b60fb9988c9488e040dbe560925db026c3acb` |
| P7 | `2062d06f0424966aa66aa7b864fafe450d6ce46d89983a1ed662a4e23b3c083c` |

P1/P3/P5-Inputs sind bytegleich; SHA-256:
`807fe35e1245b365d5a4dfba9553f34efed85d5434b72a78f7bf3a126725cd62`.
Alle true-Werte blieben true. Hash/Git sichern Integrität und dokumentierten
Ablauf, keine unabhängige Quellechtheit oder Uhr-/Zeitauthentisierung.

## Bewertung und Vergleich zu V3/V5

[Auswertung](observer-current-local-collector/2026-10-08/derived/evaluation.json):
7 korrekte/0 falsche A; 7 korrekte/0 falsche C; A=UNBEKANNT viermal, C=UNBEKANNT
nullmal, kein unbeurteilbarer Fall, keine positive A ohne aktuellen passenden
Check. Sieben erfüllte eingefrorene Anforderungen, keine Zusatzaufrufe.

| Historischer Fehlbefund, unverändert erhalten | Entsprechender neuer Fall | Belastbare Veränderung im **neuen** Weg |
|---|---|---|
| V3: früher gültiges Packet nach Freigabe → fälschlich DIESELBE für das neue Jetzt | F3, zusätzlich F5 mit geschlossenen FD-Zahlen | Ohne aktuelle Prüfung bzw. bei aktuellem EBADF → UNBEKANNT |
| V5: handgebautes true ohne tatsächlichen Collector → fälschlich DIESELBE | F4 | Handgebautes true alleine → UNBEKANNT |

**Wird handgebautes true weiterhin akzeptiert?** Im neuen F4-Weg ohne echte
Handles: keine positive Identitätsaussage. Parsergültigkeit alleine reicht nicht.
**Kann ein alter gültiger Beleg weiterverwendet werden?** Im neuen F3/F5-Weg
nach Freigabe ohne passende aktuelle gültige Handles: keine positive Aussage.

Die historische Funktion bleibt unverändert. Ihre Fehlbefunde sind weder
weggetestet noch ihre ursprünglichen Regeln rückwirkend geändert. Dieses
Ergebnis ist daher **keine Reparatur aller bestehenden Observer-Aufrufwege**.
Ein historisches/handgebautes Packet mit passenden wirklich aktuellen Handles
kann weiterhin einen **aktuellen** Vergleich tragen: das beweist weder seine
Herkunft noch die ursprüngliche historische Lebenszeit. Nicht experimentell
als allgemeine Provenienz-/Replayabwehr bestätigt.

H1–H4 und H5 für die hier konkret getesteten fehlenden/EBADF-Prüfungen sind
SUPPORTED IN THIS CASE SET. Andere Collectorfehler wurden nur synthetisch
behandelt, nicht als weitere echte Fälle gemessen. Kein allgemeines Ergebnis
für alle Fehlerarten. Achse A: PASS für diese eingefrorene Umsetzung/Fallmenge
und grüne Regression. Achse B: SUPPORTED IN THIS CASE SET, kein Sicherheitsbeweis.

## Regression und Methodenreview

Nach realer Aufnahme zweimal derselbe unveränderte Standardbefehl:

```sh
PYTHONDONTWRITEBYTECODE=1 /workspace/venvs/authority/bin/python -m pytest -p no:cacheprovider -o addopts='' -q
```

| Lauf | Ergebnis | Dauer | Exit |
|---|---|---|---|
| 1 | 383 passed, 5 deselected, 252 subtests passed | 10.11 s | 0 |
| 2 | 383 passed, 5 deselected, 252 subtests passed | 8.34 s | 0 |

[Rohlogs und Status](observer-current-local-collector/2026-10-08/standard-suite/status.json).
369 bestehende Tests plus 14 neue synthetische Tests. Die fünf historischen
RC-01–05-Fehlbefunde werden durch den **unveränderten** vorhandenen conftest
deselektiert; nicht repariert, nicht neu ausgeführt. OOS-021-Rotprobe nicht
ausgeführt. Grüne Regression ist kein Beweis für die neue Hypothese.

Vor Freeze 10 synthetische API-Fehlerpfadtests grün; Analyzerregressionen zunächst
3, nach Ergänzung einer weiteren 4 grün. Statische getrennte Kontextprüfung
fand vor Freeze Auswertungsprobleme: A-GT an Collector gekoppelt, Teilreferenzen
nicht robust, Gegenbelege hinter technischen/Teilabbruchgates verdeckbar,
exakte sieben Aufrufe nicht geprüft. Diese wurden **vor Implementierungsfreeze
und vor dem einzigen echten Falllauf** korrigiert und synthetisch geprüft.
Keine gescheiterte reale Originalmessung ersetzt. Nach Freeze Code unverändert.

Von 362 Ausgangsdateien bleiben 361 bytegleich. Die eine erlaubte Observerdatei
enthält nur zwei Imports und den additiven Forschungsaufruf; Entfernen exakt
dieser Addition stellt die ursprünglichen Bytes wieder her. Alle bestehenden
Tests, V3/V5-Berichte/Originale und früheren Hilfen bleiben bytegleich.
Interne Autoren-/Rollenprüfung und getrennter Reviewkontext Level 2; kein
externer unabhängiger Audit. Freeze-/Antwort-/Archivhashes dokumentiert.

Der getrennte Artifactreview bestätigte anschließend aus Originalen unabhängig
von der Auswertungszusammenfassung A/C je 7/7, die drei I/O-Referenzen, exakte
Reihenfolge, 32/32 Checkpoint- und 7/7 Implementierungshashes, 30/30 bytegleiche
Rohdateien und die unveränderten historischen V3/V5-Fehler. Keine Widersprüche
gefunden. Er führte keine Tests, Observerimports oder neuen Fälle aus; die
Standardsuite wurde vom Hauptprüfer ausgeführt. [Reviewzusammenfassung](observer-current-local-collector/2026-10-08/derived/review-summary.json).

## Grenzen, Confidence und STOPP

**CONFIDENCE IN EXPERIMENT RESULT: HIGH**, ausschließlich für die sieben
kontrollierten lokalen Fälle, gemessenen Callfolgen und unabhängigen I/O-
Referenzen unter den festgelegten Prozess-/Kernelannahmen.
**CONFIDENCE IN GENERALIZATION: LOW**. Ein Falllauf, eigener lokaler Prozess,
Linux/tmpfs; keine konkurrierenden Schließer/FD-Neubelegung, keine Namespace-
oder Mountwechsel, kein manipulierter Collector/Python-/Kernelprozess.
Sequenzielle fstat/F_GETFD-Snapshots sind keine atomare Lebenszeitgarantie.
Andere Hosts/Dateisysteme, Neustarts, Quellen/Agenten, verteilt gehaltene
Ressourcen, dauerhafte Identität und kryptografische Provenienz ununtersucht.

K14 außerhalb dieses begrenzten Live-Dateikontexts bleibt historisch
INCONCLUSIVE. Die E2-Metadatenlücke und OOS-021 bleiben offen. Agent Authority
bleibt ausschließlich Beobachter/Monitor/Analyseebene, ohne Aktionsfreigabe,
Rechte-/Secret-/Budgetsteuerung oder Stopbefugnis.

Die aktuelle lokale Nachprüfung schließt **in dieser Fallmenge und diesem
neuen Weg** die zwei gefundenen Belegfehler, ohne alle Aussagen pauschal
unbekannt zu machen. Daraus folgt kein weiterer automatisch begonnener Auftrag.
**STOPP nach Bericht, Commit, Push und Remote-Bestätigung.**
