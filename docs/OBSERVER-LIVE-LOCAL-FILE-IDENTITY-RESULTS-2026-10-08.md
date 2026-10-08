# Begrenzter Observerpfad: gleichzeitig lebende lokale Dateien

8. Oktober 2026. **SUPPORTED IN THIS CASE SET.**

Der neue additive Observerpfad lieferte in einer Aufnahme drei korrekte
Identitätsaussagen gegenüber unabhängiger bidirektionaler I/O-Ground-Truth:
Rename DIESELBE, zwei getrennte Dateien VERSCHIEDEN, tatsächliche Kopie
VERSCHIEDEN. Vier reduzierte/synthetische Negativkontrollen ergaben UNBEKANNT.
**7 KORREKT, 0 FALSCH, 0 UNBEURTEILBAR**, getrennt gezählt als drei positive
Sachvergleiche und vier erfüllte Enthaltungsregeln. Keine Aufnahme-, Referenz-,
Antwortinput- oder Cleanupfehler.

Diese Fähigkeit gilt ausschließlich für die beobachteten, gleichzeitig lebenden
regulären Dateien im selben kontrollierten Linux/tmpfs-Messprozess. Sie liefert
keine dauerhafte Dateiidentität, keine allgemeine Ressourcenbindung und keine
neue Befugnis für Agent Authority.

## Ausgangsbasis, Freeze und Reihenfolge

Branch `research/observer-live-local-file-identity-2026-10-08`, im vorhandenen
Checkout `/workspace/agent-authority-local-file-identity`; kein neues Worktree.

| Stand | Vollständiger Commit-SHA |
|---|---|
| Abgeschlossene Inodensuche, Ausgang | `2ba4d28f4af1af6396108bbc5ee4bab4ddc17c0b` |
| Docs-only Vorabvertrag mit Erhaltungsmanifest | `adb5cfb3a924ac391b71448502bfedfec4b464b5` |
| Implementierung vor erster echter Aufnahme | `66967deca13039845b258a62d69876ce12d4e564` |
| Originale und Antworten vor GT-Vergleich | `b06a388b68847f6634332d1005bd15356e1982ab` |

Vollständig gelesen: [Inodensuche](OBSERVER-LOCAL-INODE-REUSE-RESULTS-2026-10-08.md),
[vorheriger lokaler Test](OBSERVER-LOCAL-FILE-IDENTITY-RESULTS-2026-10-08.md),
[Epochen-Repeat-01](OBSERVER-RESOURCE-EPOCH-REPEAT-01-RESULTS-2026-10-08.md),
[Real-Run-Prototyp](OBSERVER-REAL-RUN-PROTOTYPE-RESULTS-2026-10-07.md),
[Konsolidierung E1–E7](OBSERVER-RESEARCH-CONSOLIDATION-E1-E7-2026-10-07.md),
[Methodik](RESEARCH-METHOD.md), [Debt](OUT-OF-SCOPE-DEBT.md), aktueller Observercode.
Die bisherigen Ergebnisse und deren Grenzen bleiben unverändert.

[Vorabvertrag](OBSERVER-LIVE-LOCAL-FILE-IDENTITY-CONTRACT-2026-10-08.md) und
Implementierung wurden jeweils vor dem nächsten Schritt gepusht und mit
`git ls-remote` remote bestätigt. Vor Implementierungsfreeze: AST-Prüfung,
29 synthetische Parser-Grenztests bestanden, interne kontextgetrennte Sourceprüfung.
Eine im Review erkannte Differenz zwischen Vor-/Nach-Regularitätsprüfung im
Vertrag und zunächst einfacher fstat-Prüfung wurde **vor Freeze und erster
Aufnahme** behoben. Kein Entwicklungs-/Probelauf der echten Dateifälle.

Reihenfolge: Vertragsfreeze → Implementierungsfreeze → genau eine Aufnahme
T1–T3 plus vier Kontrollsichten → Originale/Inputdigests sichern → separater
Observerantwortprozess → Antwortdatei speichern/hashen → Antwortcheckpoint
pushen und remote bestätigen → erst danach GT inhaltlich lesen/vergleichen →
Standardsuite zweimal. GT und stderr wurden bis zum Antwortcheckpoint nur
byteweise kopiert/gehasht. stderr war leer. Nach Freeze keine Codeänderung,
keine Messreparatur und keine Wiederholung.

## Was genau gebaut und beobachtet wurde

Eine neue reine Funktion
[`infer_live_local_file_identity(events, run)`](../observer_research.py) mit
eigener enger Validierung. Sie importiert keine Autorisierungs-/Enforcementlogik
und gibt für das abgefragte Paar genau A/B/C aus. Die bestehenden `FIELDS`,
`KINDS`, Recorder, boolesche Schemaprüfung, historische Ableitungen und CLI
bleiben unverändert. Der bestehende Bool-Recorder wird nicht zum allgemeinen
Objektspeicher erweitert.

Die [Aufnahmehilfe](../probes/live_local_file_identity_capture.py) ist eine
isolierte Forschungs-Teststrecke für die drei beauftragten Dateifälle; der
[Antwortprozess](../probes/live_local_file_identity_responses.py) ruft tatsächlich
die neue Observerfunktion auf. Die unveränderte historische I/O-Referenzfunktion
wird als Testhilfe importiert, nicht in den Observer verschoben. Keine weiteren
Ressourcentypen, universellen Connectoren oder Funktionen gebaut.

Wiederverwendete Hülle: genau `run`, `kind`, `value`. Ein gemeinsamer Paarbeleg
verwendet `kind=live_local_file_refs` und die bereits bekannte Darstellung
`value={scope,references}`. Es gibt keine zusätzlichen Top-Level-Felder,
Referenz-/Generation-IDs, Ereignisnummern oder Zeiten für diese neue Frage.

| Verwendete Information | Warum sie hier nötig ist / ohne sie fehlender Beleg |
|---|---|
| `run`, positiver exakter Integer | Ordnet den gemeinsamen Paarbeleg der abgefragten lokalen Vergleichsaufnahme zu. Keine Ressourcen-ID, kein projektübergreifendes Bindungssystem. |
| `kind=live_local_file_refs` | Kennzeichnet den nativen Paarbeleg; Pfad-/Inhalts-/Hashsichten sind keine Ersatzmessung. |
| `value.references`, genau zwei | Bezeichnet vollständig die zwei verglichenen Referenzen in demselben Beleg. Paarposition reicht hier, zusätzliche Referenz-IDs nicht nötig. |
| Je `st_dev`, exakter Integer ≥ 0 | Gibt den lokalen Geräte-/Dateisystembezug der Inodenummer. Ohne ihn wäre das native Paar unvollständig. Alle echten Messwerte haben dev=34; keine Mehrdateisystemprüfung. |
| Je `st_ino`, exakter Integer > 0 | Liefert die native Objektnummer innerhalb dieses Bezugs. Ohne sie fehlt die untersuchte Unterscheidungsinformation. |
| Je `regular_file=true` | Belegt per S_ISREG-Projektion den untersuchten Dateityp für beide Referenzen. Ohne diese Prüfung wäre der erlaubte Scope unbekannt. Kein vollständiger st_mode. |
| `scope.os=Linux`, `scope.filesystem=tmpfs` | Begrenzen die Ableitung auf den belegten Systemscope. Ohne sie würde ein nicht untersuchtes System als abgedeckt behandelt. |
| `scope.same_collection_process=true` | Belegt den gemeinsamen lokalen Messkontext. Gleiche Zahlen aus unbekannten Kontexten reichen nicht. Keine PIDs oder Hostprofile gesammelt. |
| `scope.live_handle_overlap_confirmed=true` | Belegt die überlappenden gehaltenen Handles; ohne diesen Lebenszeitbezug keine Identitätsbehauptung, auch nicht bei gleichen Zahlen. |

**Minimalitätsgrenze:** Die Informationsarten sind für diesen engen Pfad
begründet; ihre Darstellung ist weder formal kleinste noch endgültige Pflichtstruktur.
Die Tests belegen keine universelle Feldunersetzbarkeit. OS-/Dateisystemangaben
begrenzen hier den Befund, statt neue Systemfähigkeiten zu messen.

Der Scope wird vom kontrollierten Collector beobachtet und dann als primitive
Information angeboten. true-Werte authentisieren keine Quelle. Der Observer
öffnet selbst keine Dateien, misst keine Handles und verifiziert keinen Kernel.
Ein archivierter Beleg beschreibt seine damalige gemeinsame Aufnahme, keinen
heutigen Fortbestand. Ein alter Scope darf nicht auf eine neue Beobachtung
übertragen werden; eine falsch behauptete Live-Bindung wird hier nicht erkannt.

## Echter Aufbau und unabhängige I/O-Referenz

[System](observer-live-local-file-identity/2026-10-08/system.json): Linux 6.18.44,
Python 3.12.14, `/tmp` tmpfs. Genau ein neuer privater Ordner
`/tmp/aa-observer-live-local-file-identity-20261008`, Modus 0700. Nur selbst
erzeugte temporäre reguläre Dateien; keine Nutzerdateien, Secrets, Accounts,
Netzwerk- oder Cloudressourcen. Git-Push dient der Forschungsdokumentation.
Dies sind reale lokale Dateifälle, keine neuen autonomen Agentenläufe.

Beide Handles wurden separat geöffnet und durchgängig bis nach GT gehalten.
F_GETFD und fstat/S_ISREG wurden vor/nach der nativen Paaraufnahme geprüft.
Gespeichert wurden nur die nativen zwei Zahlen und der Regularitätsstatus pro
Referenz, kein vollständiger stat-Dump. Keine Mount-/Namespacewechsel oder
konkurrierenden Fremdänderungen im kontrollierten Aufbau.

Die Referenzfunktion liest beide Ansichten vollständig mit EOF-Probe. Ein
64-Byte-Marker wird über Handle 1 geschrieben, truncate bestätigt und eigene
sowie Gegenansicht gelesen; danach 96-Byte-Marker über Handle 2 mit frischen
Baselines. Alle Writes gaben exakt 64/96 zurück; eigene Änderungen waren in
beiden Richtungen sichtbar. Die Markerlängen unterscheiden sich von den
vorherigen Ansichten. GT verwendet keine Dateinamen, Operationserwartungen
oder native Paarvergleiche. Nur tatsächliche Checks, Längen und Vollzugsstufen
werden archiviert; keine Payload-/Markerbytes.

| Fall | Gelesene Längen: Beginn → nach Write 1 → nach Write 2 | Gegenansicht übernimmt Marker, beide Richtungen | Gegenansicht bleibt gegen frische Basis gleich, beide Richtungen | I/O-GT |
|---|---|---|---|---|
| [T1](observer-live-local-file-identity/2026-10-08/ground-truth/T1.json) | `[32,32]` → `[64,64]` → `[96,96]` | true / true | false / false | DIESELBE |
| [T2](observer-live-local-file-identity/2026-10-08/ground-truth/T2.json) | `[32,32]` → `[64,32]` → `[64,96]` | false / false | true / true | VERSCHIEDEN |
| [T3](observer-live-local-file-identity/2026-10-08/ground-truth/T3.json) | `[32,32]` → `[64,32]` → `[64,96]` | false / false | true / true | VERSCHIEDEN |

Die unabhängige Ableitung ist methodisch, nicht infrastrukturell: Metadaten und
I/O vertrauen demselben Kernel/Collector. Keine externe Prüfung oder
kryptografische Quellechtheit; gemischte/fehlgeschlagene I/O wäre unbeurteilbar.

## Gesicherte A/B/C und Bewertung T1–T7

Unveränderte [Antworten vor Vergleich](observer-live-local-file-identity/2026-10-08/responses/before-comparison.json),
SHA256 `13fcb3c9a46ca86c94780ca2a305c3f9742e26db6e001c44d22ae4af8c65a3f8`.
[Antwortseal](observer-live-local-file-identity/2026-10-08/responses/sealed-sha256.json),
[Inputseal](observer-live-local-file-identity/2026-10-08/original/input-seal.json)
und [Checkpointmanifest](observer-live-local-file-identity/2026-10-08/answer-checkpoint-integrity.json)
bewahren Digests; Git-Abfolge und Durchführungsprotokoll tragen zusätzlich die
Reihenfolge. Hashes allein beweisen keine Entstehungszeit oder Quellechtheit.
Der Antwortprozess las nur die sieben benannten Inputs, keine GT/Sollwerte,
Operationen oder Aufnahmebuchführung.

| Fall / Input | Tatsächlich angebotener Beleg | Antwort A vor GT | Bewertungsbasis | Ergebnis |
|---|---|---|---|---|
| [T1 Rename](observer-live-local-file-identity/2026-10-08/inputs/T1.json) | `(34,17277)` / `(34,17277)`, beide regulär, Live-Scope | DIESELBE | I/O-Kopplung DIESELBE | KORREKT |
| [T2 getrennte Dateien](observer-live-local-file-identity/2026-10-08/inputs/T2.json) | `(34,17283)` / `(34,17284)`, beide regulär, Live-Scope | VERSCHIEDEN | I/O-Kopplung VERSCHIEDEN | KORREKT |
| [T3 echte Kopie](observer-live-local-file-identity/2026-10-08/inputs/T3.json) | `(34,17288)` / `(34,17289)`, beide regulär, Live-Scope | VERSCHIEDEN | I/O-Kopplung VERSCHIEDEN | KORREKT |
| [T4 Pfad](observer-live-local-file-identity/2026-10-08/inputs/T4.json) | Nur synthetische relative Texte `A`, `A` | UNBEKANNT | Eingefrorene Enthaltungsregel | KORREKT |
| [T5 Inhalt](observer-live-local-file-identity/2026-10-08/inputs/T5.json) | Nur tatsächliches `content_equal=true` aus T3 vor Markerwrites | UNBEKANNT | Eingefrorene Enthaltungsregel | KORREKT |
| [T6 Hash](observer-live-local-file-identity/2026-10-08/inputs/T6.json) | Nur zwei tatsächlich gleiche SHA256 aus T3 vor Markerwrites | UNBEKANNT | Eingefrorene Enthaltungsregel | KORREKT |
| [T7 historische Kennung](observer-live-local-file-identity/2026-10-08/inputs/T7.json) | Synthetisch zweimal `(34,5469)`, overlap=false | UNBEKANNT | Eingefrorene historische Enthaltungsregel | KORREKT |

Antwort B für T1–T3 nennt wortgetreu die in der Tabelle stehenden nativen Paare,
deren Gleichheit/Verschiedenheit und den bestätigten regulären lokalen Live-Scope.
Keine Identitätsableitung aus Rename/Copy/Name/Inhalt/Hash. Antwort B für T4–T6:

> Genau ein zugeordneter nativer Paarbeleg fehlt; Pfad, Inhalt oder Hash ersetzen ihn nicht.

Antwort B für T7:

> Gleichzeitige lebende Handles im selben Linux/tmpfs-Messprozess sind nicht belegt; historische Kennungen reichen nicht.

Antwort C, bei allen sieben Fällen unverändert:

> Nur gleichzeitig lebende regulaere Dateien im selben lokalen Linux/tmpfs-Messprozess ohne Mount-/Namespacewechsel; keine dauerhafte Identitaet nach Freigabe, Inhalts-/Revisionsidentitaet oder Quellechtheit; keine anderen Hosts, Neustarts oder Ressourcen.

T6 bietet den ausdrücklich erlaubten Kontrollhash
`8873655f971d041bf7645f0e55e17fdae7e31e2877a07211dd6a4e9530ac5060`
zweimal an. Der Observer kopiert ihn nicht in seine Antwort. T4 ist eine
synthetische Pfadsicht, kein neuer Pfad-Gegenbeweis. T5/T6 stammen aus T3;
dessen verschiedene Dateien liefern einen realen Gegenbeleg zu
„gleiche Bytes/Hashes garantieren dieselbe Datei“.

**T7 ist ausdrücklich synthetisch:** Die alte Kennung stammt aus der
operational geschlossen/unlinkten Ausgangsdatei des abgeschlossenen
10000er-Versuchs. Die zweite gleiche Kennung ist konstruiert; es wurde weder
eine reale Paarwiederkehr noch eine neue Dateilebenszeit gemessen. Das prüft
ausschließlich die Enthaltungsregel bei fehlender Überlappung. Die historische
Nichtbeobachtung der Wiederverwendung bleibt INCONCLUSIVE für dauerhafte
Identität; sie wird weder bestätigt noch widerlegt durch diese Kontrolle.

Die vier UNBEKANNT sind korrekt zurückhaltende Antworten, keine vier positiv
erkannte tatsächliche Ressourcenidentitäten. Getrennte
[Auswertung](observer-live-local-file-identity/2026-10-08/derived/evaluation.json)
vergleicht A sowie passenden Beleg B und Grenze C; sie leitet T1–T3-GT nochmals
nur aus den I/O-Checks ab. Fehlende Information wird nicht zum negativen Beweis.

## Messzahlen, Erhaltung und Standardsuite

| Messgröße | Wert |
|---|---:|
| Aufnahmen / gestartete echte Dateipaare | 1 / 3 |
| Beurteilbare echte Paare mit unabhängiger I/O-GT | 3 |
| Korrekte / falsche / unbekannte primäre Identitätsaussagen | 3 / 0 / 0 |
| Kontrollsichten / davon UNBEKANNT / Enthaltungsregel erfüllt | 4 / 4 / 4 |
| Gesamte Fallbewertungen KORREKT / FALSCH / UNBEURTEILBAR | 7 / 0 / 0 |
| Aufnahme-, Referenz-, Cleanup-, Antwortinputfehler | jeweils 0 |
| Verbliebene temporäre Ressourcendateien | 0 |
| Primärinputs T1–T3, formatierte JSON-Bytes | jeweils 485, zusammen 1455 |
| Kontrollinputs T4/T5/T6/T7, formatierte JSON-Bytes | 93 / 73 / 227 / 484 |

Die sieben Observerinputs umfassen zusammen **2332 Bytes**. Kein Maß für
Gesamt-RAM, Providerpersistenz, Gesamtarchivgröße oder ein universelles Minimum.
[Capture-Status](observer-live-local-file-identity/2026-10-08/capture-status.json)
und unmittelbare Prüfung bestätigen die Entfernung aller eigenen Rohdatenfiles.
`resources/` wurde nicht archiviert. Keine Rohinhalte oder vollständigen
Terminal-/Statverläufe gespeichert; T6 behält nur den beauftragten Kontrollhash.

Nach dem Test gemäß Methodik zweimal dieselbe Standardsuite:

```sh
PYTHONDONTWRITEBYTECODE=1 /workspace/venvs/authority/bin/python -m pytest -p no:cacheprovider -o addopts='' -q
```

| Lauf | Tatsächliches Ergebnis | Exit |
|---|---|---:|
| [1](observer-live-local-file-identity/2026-10-08/standard-suite/run-1.log) | 369 passed, 5 deselected, 252 subtests passed in 7.78s | 0 |
| [2](observer-live-local-file-identity/2026-10-08/standard-suite/run-2.log) | 369 passed, 5 deselected, 252 subtests passed in 7.60s | 0 |

[Befehle/Status](observer-live-local-file-identity/2026-10-08/standard-suite/status.json).
340 bestehende Tests plus 29 neue synthetische Parser-Grenztests; keine alten
Tests abgeschwächt. Sie prüfen unter anderem fehlenden/falschen Live-Scope
auch bei ungleichen Paaren, ungebundene Läufe, boolesche Scheininteger,
nicht reguläre Referenzen, unvollständige Formen und widersprüchliche Belege.
Das ist keine neue reale Dateiaufnahme oder statistische Reproduktion von T1–T3.
Die fünf RC-01–05-Deselektionen bleiben sichtbar/unverändert; historische Misses
werden durch Grün nicht geschlossen. Die separate rote OOS-021-Probe wurde
nicht ausgeführt oder repariert. Suite-PASS ist kein Sicherheitsbeweis.

[Ausgangsmanifest](observer-live-local-file-identity/2026-10-08/frozen-integrity.json)
umfasst 272 bestehende Dateien: 271 bytegleich, einzige erlaubte Änderung ist
die 65-zeilige additive Funktion in observer_research.py. Nach Entfernen des
Zusatzes ist dessen vollständiger alter Code bytegleich. Alle alten Tests,
Dokumente und Messdaten unverändert. Vertrag, sechs im
[Implementierungsmanifest](observer-live-local-file-identity/2026-10-08/implementation-integrity.json)
benannte Dateien und alle 18 Original-/Antwortcheckpointartefakte unverändert.
Originale und Auswertung/Suitelogs liegen getrennt.

## Urteil und offene Grenzen

Achse A: **PASS** für diesen eingefrorenen additiven Daten-/Aussagevertrag und
die unveränderte Regression mit neuen Parser-Grenztests. Achse B:
**SUPPORTED IN THIS CASE SET** für H1/H2 innerhalb der drei echten Paare und
H3/H4 als nachgewiesene Einhaltung der vier Enthaltungsregeln. Kein positiver
Beweis dauerhafter oder allgemeiner Identität folgt aus H4.

**CONFIDENCE IN EXPERIMENT RESULT: HIGH**, ausschließlich für diese eine
gesicherte Aufnahme mit drei kontrollierten Dateipaaren, unabhängiger I/O-
Ableitung und vier definierten Kontrollsichten. Je echter Fall eine Ausführung;
keine Reproduktionsstatistik, kein externer Audit. Interne Source-/Archivprüfungen
erfolgten in getrennten Kontexten derselben Projektumgebung.

**CONFIDENCE IN GENERALIZATION: LOW.** Offen/untersucht wurde nicht:

- Dauerhafte Identität nach vollständiger Freigabe; reale Inodenwiederverwendung,
  weitere Dateisysteme, andere Dateitypen, Mount-/Namespacewechsel oder Neustarts.
- Falsche/stale Live-Scope-Meldungen, kompromittierte Quellen/Kernel/Collector,
  kryptografische Authentisierung, konkurrierende Fremdänderungen.
- Andere Hosts, Cloud, URLs, Datenbanken, allgemeine Revisionen oder globale IDs.
- Reale verteilte Agenten-/Connectorzuordnung, Langzeitbetrieb oder universelle
  minimale Pflichtfelder. Keine Schutz-/Warnquote oder Menschenverständlichkeit.

Historisches K14 bleibt INCONCLUSIVE in seinem ursprünglichen Umfang; die
E2-Metadaten-Lücke und OOS-021 bleiben offen. AA bleibt selbständiger Beobachter.
Keine ALLOW/DENY-Produktfunktion, Rechtevergabe, Freigabe oder Stopfunktion.

**STOPP nach Ergebnis, Commit, Push und Remote-Bestätigung.** Keine dauerhafte
ID, Register, Generation-Systeme, Graphen, neuen Ressourcentypen, Cloudtests,
weitere Inodensuche oder nächste Observerfunktion begonnen.
