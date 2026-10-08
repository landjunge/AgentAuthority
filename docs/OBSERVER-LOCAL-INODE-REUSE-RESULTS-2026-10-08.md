# Native Dateikennung nach Freigabe: begrenzte Wiederverwendungssuche

8. Oktober 2026. **Gesamturteil: INCONCLUSIVE.**

Nach vollständiger operationaler Freigabe der Ausgangsdatei wurden genau
**10.000 neue Dateilebenszeiten** auf dem unveränderten lokalen tmpfs untersucht.
Die Ausgangskombination **`(st_dev=34, st_ino=5469)`** erschien nicht erneut.
Keine Aufnahme-, Freigabe-, Archivierungs- oder Cleanupfehler. Das Limit wurde
nicht erhöht, der Versuch nicht wiederholt und das Dateisystem nicht verändert.

**Wiederverwendung wurde in diesem begrenzten Versuch nicht beobachtet.
Langfristige dauerhafte Eindeutigkeit bleibt UNBEKANNT.** Das Ergebnis belegt
weder „Wiederverwendung ist unmöglich“ noch „st_dev + st_ino ist dauerhaft sicher“.

## Ausgangsbasis und vorab festgeschriebene Durchführung

Branch: `research/observer-local-inode-reuse-2026-10-08`, im vorhandenen Checkout
`/workspace/agent-authority-local-file-identity`; kein neuer Checkout nötig.

| Stand | Vollständiger Commit |
|---|---|
| Abgeschlossener lokaler L1–L3-Test, Ausgangsbasis | `bd00c3f56d56fbf86da42be8d59c81a7da8f352b` |
| Neuer docs-only Vorabvertrag | `eea95b07605fb38d34158a7d333f7afab7e5f382` |
| Separate Vorabklärung der A-Frage und fehlender Referenzen | `5c7105cda5efa282a93af81bb6889e8cce3dd96f` |
| Isolierte Messhelfer vor erster Ausführung | `b994c49a53889a434503d56d9d7f8b5adc98f936` |
| Originale und versiegelte Antworten vor GT-Vergleich | `89dcc359d019fc7cf4382d8a2f0b990c6cc20b57` |

Vor Versuch vollständig gelesen: [lokales L1–L3-Ergebnis](OBSERVER-LOCAL-FILE-IDENTITY-RESULTS-2026-10-08.md),
[Ressourcen-Epochen-Repeat-01](OBSERVER-RESOURCE-EPOCH-REPEAT-01-RESULTS-2026-10-08.md),
[Real-Run-Prototyp](OBSERVER-REAL-RUN-PROTOTYPE-RESULTS-2026-10-07.md),
[Konsolidierung E1–E7](OBSERVER-RESEARCH-CONSOLIDATION-E1-E7-2026-10-07.md),
[Methodik](RESEARCH-METHOD.md), [Out-of-Scope Debt](OUT-OF-SCOPE-DEBT.md).
Die vorherige lokale Aussage mit gehaltenen Handles bleibt unverändert.

[Vertrag](OBSERVER-LOCAL-INODE-REUSE-CONTRACT-2026-10-08.md) und
[Vorabnachtrag](OBSERVER-LOCAL-INODE-REUSE-CONTRACT-RESOLUTION-2026-10-08.md)
wurden vor Helfererstellung gepusht/remote bestätigt. Die erste Vertragsfassung
enthält eine dokumentierte Unschärfe: Sie behandelt A bei Paarungleichheit als
UNBEKANNT mit der Begründung, die Ausgangsdatei könnte anderswo weiterleben.
Das ist eine andere Frage als die vom Nutzer verlangte Identität **beider
Beobachtungen**. Der separate Nachtrag erhält den Nutzerwortlaut und präzisiert
vor Ausführung: unterschiedliche Paare → NEIN zu denselben konkreten Referenzen;
gleiche Paare ohne Lebenszeitbeleg → UNBEKANNT. Keine Regeländerung nach Ergebnis.
H1–H3, MAX und No-hit-INCONCLUSIVE wurden nicht verändert.

Vor Helferfreeze erfolgten AST-Syntaxprüfung und kontextgetrennte interne
Sourceprüfung. Erkannte Scan-/Fehlerjournal-Lücken wurden vor Freeze behoben;
keine Entwicklungsausführung der Testdateien. Nach Helferfreeze keine Änderung,
Reparatur oder Wiederholung des Messlaufs.

Reihenfolge: Vertrags-/Nachtragsfreeze → Helferfreeze → **eine** Suchaufnahme →
Originalsicherung/Inputhashes → separater Analyst → Antwortsicherung/Hash →
Antwortcheckpoint gepusht und mit `git ls-remote` bestätigt → erst danach GT
inhaltlich gelesen und getrennt bewertet → unveränderte Standardsuite zweimal.
Bis zum Antwortcheckpoint wurden GT und stderr ausschließlich byteweise
gesichert/gehasht. stderr war tatsächlich leer.

## System, Suchumfang und native Aufnahme

[System](observer-local-inode-reuse/2026-10-08/system.json): Linux **6.18.44**,
Python **3.12.14**, **tmpfs** unter /tmp. Genau ein neuer, exklusiv erzeugter
privater Ordner `/tmp/aa-local-inode-reuse-20261008`, Modus **0700**.
Strikt sequenziell; kein Mount, Neustart, Tuning oder künstliche Parallelbelastung.
Keine Nutzer-/Repositorydatei als Ressource, Accounts, Secrets, Cloud oder
Netzwerk im Versuch. Git-Push dient nur der verlangten Forschungsdokumentation.

Festes Maximum: **10.000 neue Dateien nach einer Ausgangsdatei**, höchstens
10.001 Dateilebenszeiten insgesamt. Verglichen wurde jede neue Kennung nur mit
der Ausgangskombination; kein Test beliebiger neue–neue Kollisionen.
Die Grenze ist ein Aufwandslimit, kein Wahrscheinlichkeits-/Ratenmodell.

| Messreferenz | Tatsächliches natives Paar |
|---|---|
| Ausgangsdatei | `(34,5469)` |
| Erste neue Datei, Versuch 1 | `(34,5470)` |
| Letzte neue Datei, Versuch 10000 | `(34,15469)` |

Die vollständigen [10.001 nativen Originalzeilen](observer-local-inode-reuse/2026-10-08/original/native-pairs.jsonl)
enthalten ausschließlich st_dev/st_ino. `st_dev` benennt die lokale Geräte-/
Dateisystemzuordnung, `st_ino` deren native Inodenummer. Das Paar ist keine
universelle oder kryptografisch authentisierte Ressourcen-ID.
Messpositionen dienen nur der Zuordnung/gefundenen Trefferstelle, nicht als
neue Ressourcen- oder Generation-IDs.

Die [Aufnahmehilfe](../probes/local_inode_reuse_capture.py) erzeugte jede leere
Datei mit O_CREAT|O_EXCL|O_NOFOLLOW, bestätigte per fstat eine reguläre Datei,
kopierte nur die beiden Zahlen und gab die Ressource vor der nächsten Erstellung
frei. Kein dup, fork, mmap, weiterer Hardlink oder gehaltenes altes Dateihandle.
Native Paare und Lifecycle-Befunde blieben während der Suchschleife im Speicher;
Archivdateien wurden erst danach geschrieben. Keine Inhaltsabfragen, Payloads
oder Datei-Inhaltshashes. Keine Rohinhalte archiviert.

## Unabhängige Ground Truth und tatsächliche Freigabe

Die [10.001 Lifecycle-Originalzeilen](observer-local-inode-reuse/2026-10-08/ground-truth/lifetimes.jsonl)
enthalten keine nativen Paare, Gleichheitsurteile oder erwarteten Antworten.
Alle Zeilen wurden nach Antwortcheckpoint geprüft, nicht nur Beispiele:

| Operationale Referenzprüfung | Tatsächlich bestätigt |
|---|---:|
| Exklusive Erstellung und reguläre Datei | 10001 / 10001 |
| Einziges eigenes Handle: close zurückgekehrt | 10001 / 10001 |
| Unmittelbares F_GETFD ergibt EBADF, vor neuer FD-Öffnung | 10001 / 10001 |
| unlink zurückgekehrt und lstat ergibt ENOENT | 10001 / 10001 |
| Eigene Zielpfad-FD-Symlinktreffer nach Freigabe = 0 | 10001 / 10001 |
| Neue Erstellung erst nach bestätigter vorheriger Freigabe | 10000 / 10000 |

Die Freigabeprüfung hält nur den proc-Enumerationskontext, öffnet keine
FD-Zieldatei und verwendet keinen st_dev/st_ino-Vergleich. Keine fremden
FD-Zielpfade archiviert. Eigene FD-Symlinktreffer sind **nicht** st_nlink.
Die erste Lifecyclezeile hat keine Vorgängerlebenszeit; jede neue Zeile
dokumentiert die tatsächlich vorher bestätigte Freigabe. Alle Versuchspositionen
0–10000 sind vorhanden, alle Release-Prüfungen vollständig.

Die Referenz für **neue Lebenszeit** ist close/EBADF → unlink/ENOENT → kein
eigener offener Zielbezug → anschließende erfolgreiche exklusive Erstellung.
Weder gleicher Pfad noch Inhalt, Name oder Kennungsdifferenz begründet sie.
Anders als im historischen L2 wurde die Ausgangsdatei nicht gepinnt.

„Vollständig freigegeben“ bleibt operational: einzige eigene offene Referenz
und kontrollierter Verzeichnislink entfernt. Nicht nachgewiesen sind physische
Kernel-Reklamation, Inodenverwaltungsstrategie oder Zugriffe fremder
privilegierter Prozesse. Kernel und Collector sind gemeinsame vertrauenswürdige
Voraussetzungen von Metadaten und Ablaufmessung. Kein externer Audit oder
kryptografischer Quellenbeweis.

## Analystenantworten vor Ground Truth und ihre Bewertung

Der [separate Analyst](../probes/local_inode_reuse_analyze.py) las ausschließlich
native-pairs.jsonl und den [nativen Scope/MAX](observer-local-inode-reuse/2026-10-08/original/identity-scope.json).
Kein Zugriff auf Lifetime-JSONL, Capture-Status, Fehlerlog, Freigabe-/
Exklusiverstellungsbelege oder historische Antworten. Ausgewähltes Analysepaar
gemäß Vertrag/Nachtrag: Ausgang und letzter neuer Messwert, da kein Paar-Treffer.

Unverändert [vor Vergleich gespeicherte Antworten](observer-local-inode-reuse/2026-10-08/responses/before-comparison.json):

- **A: NEIN.** Nur zur behaupteten Identität der beiden konkreten Messreferenzen.
- **B: NEIN.** Keine Ausgangspaar-Wiederkehr innerhalb der vollständigen
  10000er-Messliste; nicht „Wiederverwendung unmöglich“.
- **C**, wörtlich:

> Keine dauerhafte Eindeutigkeit oder Unmoeglichkeit von Wiederverwendung; keine allgemeine Rate, andere Dateisysteme, Hosts, Neustarts, Cloud- oder Netzwerkressourcen, kryptografische Quellechtheit oder zukuenftige ID-Loesung.

Gespeicherter Belegtext, wörtlich:

> Ausgangspaar {'st_dev': 34, 'st_ino': 5469}, ausgewaehltes neues Paar {'st_dev': 34, 'st_ino': 15469}; 10000 neue native Messpaare. Paarungleichheit verneint nur die Identitaet der beiden Messreferenzen. Keine Ausgangspaarrekurrenz in der vollstaendigen eingefrorenen 10000er-Liste. Kein Beleg fuer dauerhafte Eindeutigkeit, Fortbestand anderswo oder physische Freigabe.

Antwortdatei-SHA256 vor GT-Vergleich:
`f1bede8e4763da7f1fac166dc5766b69a36b9e9afa152591537bc231a74254bb`.
[Inputseal](observer-local-inode-reuse/2026-10-08/original/input-seal.json),
[Antwortseal](observer-local-inode-reuse/2026-10-08/responses/sealed-sha256.json)
und [Checkpoint-Manifest](observer-local-inode-reuse/2026-10-08/answer-checkpoint-integrity.json)
bewahren tatsächliche Digests. Hashes beweisen keine Entstehungszeit oder
Quellechtheit; Reihenfolge stützt sich zusätzlich auf Ausführungsprotokoll und
Git-Abfolge. Der Analyst ist ein fester lesender Testauswerter, kein AA-Produkt.

Getrennte [Bewertung](observer-local-inode-reuse/2026-10-08/derived/evaluation.json):
A stimmt mit vollständiger alter Freigabe vor neuer exklusiver Erstellung
überein; B mit null Ausgangspaar-Treffern in 10000 unabhängig zugeordneten
neuen Lebenszeiten. **Zwei beurteilbare A/B-Aussagen korrekt, null falsch,
null unbekannt.** C hält die vorgeschriebenen Grenzen ein. Das sind zwei Aussagen
in einem Suchlauf, keine zwei unabhängigen Experimente oder Produktquote.
Die übergeordnete Frage nach dauerhafter Eindeutigkeit bleibt trotzdem unbekannt.

## Zähler, Fehler und Cleanup

| Messgröße | Tatsächlicher Wert |
|---|---:|
| Suchaufnahmen / Ausgangsdateien | 1 / 1 |
| Eingefrorene maximale neue Lebenszeiten | 10000 |
| Tatsächlich exklusiv erzeugte neue Lebenszeiten | 10000 |
| Tatsächlich gemessene neue native Paare | 10000 |
| Ausgangspaar-Wiederverwendungen beobachtet | 0 |
| Erster Treffer | keiner |
| Vollständig operational geprüfte Freigaben einschließlich Ausgang | 10001 |
| Mess-/Freigabe-/Archivierungs-/Cleanupfehler | jeweils 0 |
| Analysten-Inputfehler | 0 |
| Verbliebene temporäre Testdateien / eigene Ziel-FD-Treffer | 0 / 0 |

[Capture-Status](observer-local-inode-reuse/2026-10-08/capture-status.json)
bewahrt den Stopgrund `maximum_reached_without_native_pair_recurrence`.
[Capture-Prozess](observer-local-inode-reuse/2026-10-08/original/capture-process.json):
ein Aufruf, Exit 0, stderr 0 Bytes. Die Quelle enthält Fehlerabbruch und
strukturierten Archiv-Fallback, diese Pfade wurden im echten Lauf nicht ausgelöst
und nicht nachträglich mit zusätzlichen Dateitests ausgeführt.

Alle selbst erzeugten Rohdateien sind geschlossen/unlinkt; unmittelbare
Nachprüfung fand keine Ressourcendatei im privaten Ordner. `resources/` wurde
nicht archiviert. Nur Originalmetadaten, getrennte GT, Antworten, Ableitungen
und Prüflogs bleiben. Kein vorhandener Fehlbefund wurde verdeckt oder verändert.

## Standardsuite und erhaltene Forschung

Gemäß Methodik zweimal derselbe unveränderte Befehl:

```sh
PYTHONDONTWRITEBYTECODE=1 /workspace/venvs/authority/bin/python -m pytest -p no:cacheprovider -o addopts='' -q
```

| Lauf | Tatsächliches Ergebnis | Exit |
|---|---|---:|
| [1](observer-local-inode-reuse/2026-10-08/standard-suite/run-1.log) | 340 passed, 5 deselected, 252 subtests passed in 7.33s | 0 |
| [2](observer-local-inode-reuse/2026-10-08/standard-suite/run-2.log) | 340 passed, 5 deselected, 252 subtests passed in 7.31s | 0 |

[Befehle/Status](observer-local-inode-reuse/2026-10-08/standard-suite/status.json).
Die fünf bisherigen RC-01–RC-05-Deselektionen bleiben unverändert; historische
Misses sind damit nicht geschlossen. Keine zusätzliche Probe, neue Ausnahme
oder Wiederholung/Erweiterung der Inodensuche. Die separate rote OOS-021-Probe
wurde nicht ausgeführt oder repariert. Regression-PASS ist kein Hypothesenbeweis.

Alle **248 getrackten Ausgangsdateien** sind bytegleich gemäß
[Freeze-Manifest](observer-local-inode-reuse/2026-10-08/frozen-integrity.json).
Vertrag, Vorabnachtrag, beide Helfer und alle elf Mess-/Antwortcheckpoint-
Artefakte bleiben unverändert. Keine Produkt-, Observer-, Lab- oder
Teständerungen. Historisches K14 bleibt in seinem Umfang INCONCLUSIVE;
E2-Metadaten-Lücke und OOS-021 bleiben offen. Kein neues Identitätssystem.

## Forschungsurteil und Confidence

**H1:** Wiederverwendung der Ausgangskombination ist in diesem Suchlauf nicht
nachgewiesen. **H2:** Der geforderte Gegenbeleg mit gleicher Kennung bei
getrennten Lebenszeiten trat nicht auf; die dauerhafte Eignung des Paares ist
damit weder bestätigt noch widerlegt. **H3 / Gesamturteil: INCONCLUSIVE.**

**CONFIDENCE IN EXPERIMENT RESULT: HIGH**, ausschließlich für die vollständig
archivierte No-hit-Aufnahme innerhalb des festen lokalen 10000er-Umfangs und
die operational belegten eigenen Freigaben. Nicht HIGH für langfristige
Eindeutigkeit, physische Inodenfreigabe oder Verhalten außerhalb der Aufnahme.

**CONFIDENCE IN GENERALIZATION: LOW.** Keine Wiederverwendungsrate oder
Kernelstrategie festgestellt, keine weiteren Dateisysteme, Prozesse/Hosts,
Neustarts, Netzwerke oder Cloudressourcen untersucht. Keine kryptografische
Quellechtheit, fremde privilegierte Zugriffe oder zukünftige ID-Technik geklärt.
Keine nächste Messung oder Reparatur daraus ableiten.

**STOPP nach Ergebnis, Commit und Push.** Kein weiterer Dateisystemtest,
keine dauerhafte ID, Generation-/Hash-ID, Register, Datenbank, Graph oder
Observererweiterung begonnen.
