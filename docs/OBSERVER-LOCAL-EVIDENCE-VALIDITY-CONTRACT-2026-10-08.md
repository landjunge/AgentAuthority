# Vorabvertrag: Gültigkeit lokaler Ressourcenbelege

8. Oktober 2026. Ausgang `8e7e112c7155577dd76def741aeb98ec75e42177`,
[abgeschlossener Live-Datei-Bericht](OBSERVER-LIVE-LOCAL-FILE-IDENTITY-RESULTS-2026-10-08.md).
Rolle: Forschungsprüfer des **unveränderten** Observers. Dieser docs-only Vertrag
wird vor jeder experimentellen Ausführung committed, gepusht und remote bestätigt.
Neue Hilfen werden danach statisch geprüft und vor Aufnahme ebenfalls eingefroren.
Keine neuen Akzeptanztests, kein Observerumbau, keine Reparatur.

## Frage, Gegenstand und Hypothesen

Welche Aussage darf der Observer über Ressourcenidentität treffen, wenn der
lokale Identitätsbeleg aktuell, veraltet, unvollständig oder nur behauptet ist?

**Frageanker ist das Jetzt des jeweiligen tatsächlichen Observeraufrufs.**
Ein alter Beleg kann seine ursprüngliche historische Paarbeobachtung weiter
beschreiben. Er darf damit keine **aktuelle** Live-Bindung einer neuen Anfrage
belegen. Getestet wird diese zusätzliche Gültigkeitsanforderung, nicht eine
nachträgliche Umschreibung des vorherigen Vertrags.

- H1: vollständig und aktuell beobachtete, gleichzeitig lebende reguläre
  Referenzen im kontrollierten gleichen Linux/tmpfs-Messprozess: gleiches
  natives Paar → DIESELBE; unterschiedliche Paare → VERSCHIEDEN.
- H2: unveränderter früherer Live-Beleg nach vollständigem operationalem Ende
  der damaligen Lebenszeit, ohne aktuelle Bestätigung → UNBEKANNT für die
  aktuelle Anfrage. Kein absichtlich falscher Laufparameter als Ersatztest.
- H3: nur behauptetes true, ohne tatsächlichen aktuellen Collectorbeleg →
  UNBEKANNT. Parserkonformität ist kein Herkunfts-/Gültigkeitsbeweis.
- H4: fehlender notwendiger Scope, Dateityp oder natives Teilfeld → UNBEKANNT.

Keine allgemeine Datei-/Quellechtheit, permanente Identität, kryptografische
Technik oder Produktarchitektur. Nur eigener kontrollierter Linux/tmpfs-Aufbau.

## Vollständig gelesene Grundlage und Beobachterbestand

Gelesen: Ausgangsbericht vollständig; [Inodensuche](OBSERVER-LOCAL-INODE-REUSE-RESULTS-2026-10-08.md),
[lokaler Identitätstest](OBSERVER-LOCAL-FILE-IDENTITY-RESULTS-2026-10-08.md),
[Epochen-Repeat-01](OBSERVER-RESOURCE-EPOCH-REPEAT-01-RESULTS-2026-10-08.md),
[Konsolidierung E1–E7](OBSERVER-RESEARCH-CONSOLIDATION-E1-E7-2026-10-07.md),
[Methodik](RESEARCH-METHOD.md), [Debt](OUT-OF-SCOPE-DEBT.md), vollständiger
aktueller Observercode. Die sechs älteren bereits vollständig gelesenen Quellen
sind gegen den damaligen Stand bytegleich bestätigt; ebenso bleibt der alte
Observerteil unverändert, der Zusatz wurde vollständig gelesen.

Getestet wird ausschließlich `infer_live_local_file_identity(events, run)`.
**Alle 305 bestehenden Dateien bleiben bytegleich**, einschließlich Observer,
historischer Testhilfen, Tests, Berichte und Originale.

Die aktuelle Funktion liefert A/B/C, wobei ihr C ein Grenztext ist; sie hat
keine gesonderte aktuelle Gültigkeitsausgabe. Das wird vorab sichtbar erhalten:

| Angefragter Punkt | Feste reine Serialisierung im neuen Testhelfer |
|---|---|
| A Identität | Original A wortgetreu |
| B konkreter Beleg | Original B wortgetreu |
| C aktuell und für diese Aussage gültig? JA / NEIN / UNBEKANNT | UNBEKANNT, ausdrücklich **fehlende Observerausgabe**, keine neue Ableitung |
| D Grenze | Original C wortgetreu |

Zusätzlich bleiben alle ursprünglichen A/B/C im Antwortartefakt gespeichert.
Eine identische Erklärung außerhalb der A/B/C/D nennt die fehlende C-Fähigkeit.
Der Helfer liest weder GT, Fallname, Herkunfts-/Freigabeprotokoll noch Erwartungen
und leitet keine JA-/NEIN-Antwort her. Das konstante C zählt **nie** als
erfolgreiche Gültigkeitserkennung oder bewiesene Enthaltung des Observers.
Identitätsaussage, Belegbegründung, Grenze und C-Ausgabevollständigkeit werden
getrennt bewertet. Kein LLM ergänzt die fehlende Funktion.

## Fest eingefrorene Fallmenge und verdeckte Eingaben

Genau sieben Observeraufrufe. Inputs heißen neutral `P1.json` bis `P7.json`;
die Fallzuordnung steht nur im Vertrag/GT, nicht im Observerinput. Alle
Abfragen verwenden run=1; run bezeichnet hier jeweils das eine angebotene
Paar im isolierten Aufruf, keine globale Lauf-/Ressourcen-ID. Keine Fallnamen,
Sollwerte, Schließstatus, Herkunftsklassen oder Zeitfelder im Observerinput.
Unveränderte Hülle und Belegform aus dem Ausgangstest, keine neuen Felder.

| Fall / Packet | Durchführung / angebotene Sicht | Erwartung A | Bewertungsbasis |
|---|---|---|---|
| V1 / P1 | Eine eigene reguläre Datei, zwei separat geöffnete Handles; vollständiges aktuell gemessenes natives Paar + Scope. Antwort tatsächlich während beide Handles offen sind. | DIESELBE | Bidirektionale I/O-GT + operative Live-Aufrufprüfung |
| V2 / P2 | Zwei eigene getrennt exklusiv erzeugte Dateien, beide offen; vollständiger aktueller Beleg. Antwort während beide Handles offen sind. | VERSCHIEDEN | Bidirektionale I/O-GT + operative Live-Aufrufprüfung |
| V3 / P3 | P1 **bytegleich** erneut anbieten, auch run=1 unverändert, erst nachdem beide alten Handles nachweislich geschlossen und der kontrollierte Datei-Link entfernt sind. Historische true-Werte bleiben true. Kein erneuter Collector-Snapshot. | UNBEKANNT | Unabhängige Freigabe-/Ablaufreferenz; nicht Ressource=VERSCHIEDEN |
| V4 / P4 | Reduzierte P1-Sicht: gemeinsame Collectorbestätigung und Live-Überlappungsfeld fehlen; native gleiche Zahlen bleiben. Während V1-Handles noch offen sind, um allein fehlende angebotene Information zu prüfen. | UNBEKANNT | Informations-/Enthaltungsregel, keine Verschiedenheits-GT |
| V5 / P5 | Handgefertigte ungeprüfte Eingabe: zwei gleiche synthetische Paare `(123,456)`, regular_file=true und alle Scopewerte formal gültig, insbesondere live_handle_overlap_confirmed=true. Kein Collector erzeugt diese Kennungen/Flags. | UNBEKANNT | Kontrollierte Provenienz: synthetische Behauptung, kein aktueller Collectorbeleg |
| V6 / P6 | Reduzierte P1-Sicht mit fehlendem st_dev einer Referenz, sonst unverändert; während V1-Livephase. | UNBEKANNT | Unvollständiges natives Paar, keine Verschiedenheits-GT |
| V7 / P7 | Reduzierte P1-Sicht mit fehlendem regular_file einer Referenz, sonst unverändert; während V1-Livephase. | UNBEKANNT | Fehlender angebotener Typbeleg, keine Verschiedenheits-GT |

V5 stammt ausdrücklich nicht aus einem anderen gemessenen Fall. Seine Zahlen
sind Testwerte, keine behaupteten echten Kernelmesswerte. Der Manipulationsstatus
steht im getrennten Herkunfts-/GT-Kanal, niemals als Antwortsignal im Input.

Feste Ausführungsreihenfolge: P1 → P4 → P6 → P7 (alle innerhalb derselben
gehaltenen V1-Lebenszeit) → V1-I/O-GT → vollständige V1-Freigabe → P3-Replay →
P2 während gehaltener V2-Handles → V2-I/O-GT/Freigabe → P5 synthetisch.
Keine weitere Quelle/Datei, kein anderer Test und keine Wiederverwendungssuche.

## Messung, Lebenszeit und unabhängige Ground Truth

Neuer privater Ordner `/tmp/aa-local-evidence-validity-20261008`, 0700, nur eigene
kontrollierte Dateien. Linux/tmpfs vor Erstellung der Testdateien lesend prüfen.
Keine Mount-/Namespacewechsel, Fremdänderungen, Hardlinks, dup, mmap oder
vererbten Ressourcen-FDs; Antwortkindprozess erhält nur den Inputpfad und keine
Ressourcenhandles. Elternprozess hält seine Handles durchgängig.

V1/V2: fstat-Regulärstatus und F_GETFD bei Aufnahme und unmittelbar vor/nach
dem tatsächlichen Antwortprozess prüfen. Die Scopewerte werden aus dem
kontrollierten Ablauf erzeugt. Zwei echte native Paaraufnahmen insgesamt;
die vier reduzierten/replay-Sichten erzeugen keine neue native Paaraufnahme.
Der Observer prüft selbst nur seine angebotenen Daten, nicht diese GT-Journale.

I/O-GT wieder mit der unveränderten historischen Funktion: anfänglich 32 Bytes,
eigene exakte 64-/96-Byte-Markerwrites und truncate; vollständige Reads mit
EOF-Probe. Gegenseitige Kopplung in beiden Richtungen → DIESELBE; sichtbare
eigene Änderungen mit jeweils unveränderter Gegenansicht → VERSCHIEDEN;
fehlgeschlagene/gemischte I/O → UNBEURTEILBAR. Weder native Gleichheit noch
Name, Pfad oder erwartete Operation bestimmen die Referenz.

V3: beide close-Rückgaben und sofortiges F_GETFD=EBADF ohne intervenierende
FD-Öffnung; unlink-Rückgabe, lstat=ENOENT und null eigene Ziel-FD-Symlinktreffer.
Keine FD-Zieldatei zur Kontrolle öffnen. Danach unveränderte P1-Bytes erneut
anbieten und ohne neue Paaraufnahme beantworten. Freigabejournal speichert
keine nativen Paare und ersetzt kein aktuelles Lebenszeitfeld im Input.
„Freigegeben“ ist operational im eigenen Aufbau, kein physischer
Kernel-Reklamations-/Fremdprozessbeweis. Keine Aussage über dauerhafte Paarwerte.

V4–V7: GT ist ausschließlich die fehlende hinreichende angebotene Information
bzw. die fehlende tatsächliche Collectorherkunft, **nie** „Dateien verschieden“.
Für C bietet die getrennte Referenz aktuelle vollständige Gültigkeit JA bei
V1/V2; der unveränderte alte Beleg für die Jetzt-Anfrage in V3 ist NEIN; V4–V7
sind NEIN als hinreichende aktuelle Identitätsbelege nach diesen festgelegten
Kriterien. Dies behauptet weder unterschiedliche noch nicht existierende
Ressourcen. Der Observer erhält diese Referenzwerte nicht.

Keine Inhalte/stat-Dumps speichern. Nur native Paarprojektion, boolesche
Prüfungen, Vollzugsstufen, I/O-Längen/Checks und notwendige Herkunfts-/Zuordnung
im getrennten GT-Kanal. Kein Inhaltshash erforderlich.

## Trennung, Sicherung und Fehlerregel

Der feste separate Antwortprozess liest nur sein eines Packet und run=1 und
ruft den unveränderten Observer genau einmal auf. V1/V2-Antworten müssen während
gehaltener Handles gespeichert/gehasht sein. Alle sieben Roh-/Formantworten
vor irgendeinem GT-Vergleich speichern/hashen. GT wird unabhängig erfasst,
aber vom Prüfer bis zum Antwortcheckpoint nur byteweise gesichert/gehasht.
Antwortcheckpoint committen/pushen und remote bestätigen; erst danach
inhaltliche GT-Auswertung. Originale read-only, Auswertung getrennt.

Kein Austausch alter Scopeflags durch false als Reparatur des V3-Inputs.
Kein Heraussortieren einer positiven manipulierten Antwort. Aufnahme-,
Antwortprozess-, Referenz-, Speicher- und Cleanupfehler getrennt sichern.
Bei Fehlern keine Reparatur/Wiederholung; fehlende Antworten bleiben sichtbar
unbeurteilbar. Keine Ergebniszählung aus Sollwerten, Status oder Szenarionamen.
Hashes/Git dokumentieren Integrität und Ablauf, keine Quellechtheit oder
unabhängige Zeitauthentisierung. Interne Rollen-/Kontexttrennung, kein externer Audit.

## Entscheidung, Regression und STOPP

Je Fall A/B/D als KORREKT/FALSCH/UNBEURTEILBAR; C separat als tatsächliche
Observerausgabe oder fehlende Fähigkeit ausweisen. Nicht sieben korrekte
C-Antworten aus einer konstanten Adapterausgabe konstruieren.

**SUPPORTED IN THIS TEST** nur mit allen sieben erwarteten A-Antworten und
passenden Begründungen zur vorhandenen/fehlenden Gültigkeit; gültige V1/V2
dürfen nicht durch pauschales UNBEKANNT ausgeschaltet werden. Fehlende C-
Fähigkeit bleibt auch dann ausdrücklich bestehen, statt Erfolg vorzutäuschen.
**NOT SUPPORTED** sobald ein beurteilbarer alter, manipuliert behaupteter oder
unvollständiger Beleg als sichere aktuelle Identität verwendet wird.
**INCONCLUSIVE** bei unsauberer Test-/Referenzlage; unabhängige Fehler nicht
automatisch als Observerfehler behandeln. Befund betrifft die neue
Gültigkeitsanforderung, nicht alte Specs rückwirkend.

Nach Ergebnis zweimal unveränderte Standardsuite:

```sh
PYTHONDONTWRITEBYTECODE=1 /workspace/venvs/authority/bin/python -m pytest -p no:cacheprovider -o addopts='' -q
```

Fünf bestehende RC-01–05-Deselektionen sichtbar; historische Tests nicht
verändern. Separate rote OOS-021-Probe nicht ausführen/reparieren. Grüne
Regression ist kein Gültigkeitsbeweis. Beide Confidence-Achsen im Bericht.
K14 im historischen Umfang INCONCLUSIVE, E2-Lücke/OOS-021 weiterhin offen.

**STOPP nach Bericht, Commit, Push und Remote-Bestätigung.** Keine Reparatur,
Signatur, Attestation, TPM, Zertifikate, Kryptografie, Register, globale
Generation-ID, Cloud-Identität, Vertrauenskette, Graph oder nächste Observerfunktion.
