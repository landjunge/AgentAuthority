# Vorabvertrag: begrenzter lokaler Dateiidentitäts-Observer

8. Oktober 2026. Ausgang: `2ba4d28f4af1af6396108bbc5ee4bab4ddc17c0b`.
Dieser neue Vertrag wird vor Implementierung committed, gepusht und remote
bestätigt. Historische Ergebnisse werden nicht geändert.

## Frage und eingefrorene Hypothesen

Kann der Observer mit minimalen lokalen Metadaten korrekt zwischen derselben
und verschiedenen gleichzeitig lebenden Dateireferenzen unterscheiden und
bei fehlendem Beleg UNBEKANNT bleiben?

- H1: gleiche native `(st_dev, st_ino)` bei zwei gleichzeitig lebenden regulären
  Dateien im selben festgelegten lokalen Messkontext → DIESELBE.
- H2: unterschiedliche native Paare unter denselben Voraussetzungen → VERSCHIEDEN.
- H3: nur Pfad/Name, Inhaltsgleichheit oder Inhaltshash → UNBEKANNT.
- H4: historische Kennung nach vollständiger Freigabe, ohne zusätzlichen gültigen
  Lebenszeitbeleg → UNBEKANNT, auch bei gleichen Paarwerten.

Scope ist ausschließlich ein kontrollierter Linux/tmpfs-Messprozess, ohne
Mount-/Namespacewechsel oder Fremdänderungen. Ressource bedeutet lebendes
reguläres Dateisystemobjekt, nicht Pfad, Inhalt, Revision, FD-Nummer oder offene
Dateibeschreibung. Das Paar ist ausdrücklich keine dauerhafte Ressourcen-ID.

Vollständig gelesene Grundlage: [Inodensuche](OBSERVER-LOCAL-INODE-REUSE-RESULTS-2026-10-08.md),
[lokaler Test](OBSERVER-LOCAL-FILE-IDENTITY-RESULTS-2026-10-08.md),
[Epochen-Repeat-01](OBSERVER-RESOURCE-EPOCH-REPEAT-01-RESULTS-2026-10-08.md),
[Real-Run](OBSERVER-REAL-RUN-PROTOTYPE-RESULTS-2026-10-07.md),
[Konsolidierung](OBSERVER-RESEARCH-CONSOLIDATION-E1-E7-2026-10-07.md),
[Methodik](RESEARCH-METHOD.md), [Debt](OUT-OF-SCOPE-DEBT.md) und der vollständige
aktuelle `observer_research.py`.

## Kleinster additiver Pfad nach Schemaprüfung

Eine neue reine Funktion `infer_live_local_file_identity(events, run)` in
`observer_research.py`, mit eigener enger Validierung. Keine Änderung von
`FIELDS`, `KINDS`, Recorder, historischen Ableitungen oder CLI. Die bisherige
Standardaufnahme verlangt boolesche Werte; sie wird nicht für Objekte geöffnet.
Eine gesonderte kleine Testaufnahme ruft die neue Funktion direkt auf.

Wiederverwendete Hülle: genau `run`, `kind`, `value`. Neuer begrenzter kind-Wert
`live_local_file_refs`; value verwendet die bereits im lokalen Test bewährte
Darstellung `{scope, references}`. Genau zwei Referenzen in einem gemeinsamen
Beleg vermeiden zusätzliche Referenz-IDs, zeitliche Joins oder Ereignisnummern.
Es werden keine neuen Top-Level-Felder eingeführt.

| Information | Ohne diese Information nicht getragene Aussage / Zweck |
|---|---|
| `run` (positiver exakter Integer) | Der Beleg ist nicht der abgefragten lokalen Vergleichsaufnahme zugeordnet. Nur lokale Zuordnung, keine Ressourcen-ID. |
| `kind=live_local_file_refs` | Pfad-/Inhalts-/Hashdaten könnten mit nativen Messbelegen verwechselt werden. |
| `value.references`, genau zwei | Die beiden Vergleichsreferenzen sind nicht vollständig bezeichnet. Listenposition ist nur Paarposition, keine neue Identität. |
| Je `st_dev` (Integer ≥ 0) | Inodenummer allein bezeichnet den lokalen Dateisystemkontext nicht. Hier keine Aussage über mehrere Dateisysteme getestet. |
| Je `st_ino` (Integer > 0) | Das native Objekt im Dateisystem ist nicht unterscheidbar. |
| Je `regular_file=true` | Für andere Dateitypen trägt der gelesene Beleg die Aussage nicht. Nur boolesche S_ISREG-Projektion, kein vollständiger Modus. |
| `scope.os=Linux`, `scope.filesystem=tmpfs` | Der Observer könnte den bisherigen begrenzten Befund außerhalb seines untersuchten Systems anwenden. Diese Angaben begrenzen die Aussage; keine universelle Minimalitätsbehauptung. |
| `scope.same_collection_process=true` | Gleiche Zahlen könnten aus nicht vergleichbaren Messkontexten zusammengeführt werden. Kein PID-/Hostprofil nötig. |
| `scope.live_handle_overlap_confirmed=true` | Historische Kennungen könnten als dauerhafte Identität missbraucht werden. Das ist die entscheidende Lebenszeitgrenze. |

Diese Darstellung ist eine begründete kleine Wiederverwendung, keine formal
kleinste oder endgültige Pflichtfeldstruktur. Scope/Regularität sind explizite
Collectorbelege: vertraute Quelle, keine Authentisierung durch true oder Token.
Fehlende/falsche/unbekannte Scopewerte, unvollständige oder ungültige Paare,
fehlende Laufbindung und mehrere nicht eindeutig zuordenbare Belege ergeben
UNBEKANNT. Keine Ersatzbindung aus Reihenfolge, Pfad, Status, Inhalt oder Hash.
Konservative Enthaltung bei mehreren Belegen; keine Replayfunktion.

Ausgabe für jeden Fall genau A/B/C: A DIESELBE/VERSCHIEDEN/UNBEKANNT,
B sichtbarer tragender Beleg bzw. konkret fehlender Beleg,
C ausschließlich eingefrorener Scope und dessen Grenze. Keine Steuerung,
Freigabe, ALLOW/DENY, Rechte-/Budget-/Secret- oder Stopfunktion.

## Einmalige Aufnahme T1–T7

Genau drei echte lokale Dateipaare, einmal pro Fall, in einem neuen privaten
Ordner `/tmp/aa-observer-live-local-file-identity-20261008` (0700); nur eigene
temporäre Dateien. Linux/tmpfs vorab lesend prüfen. Beide separat geöffneten
Handles werden durchgängig bis nach den Messungen/GT gehalten; fstat-Regulärstatus
und F_GETFD vor/nach der nativen Aufnahme prüfen. Keine Nebenprozesse oder
Mount-/Namespacewechsel. Fehler sichern, nicht im selben Versuch reparieren
oder den Versuch als ursprünglichen erfolgreichen Lauf wiederholen.

| Fall | Angebotene Information und Durchführung | Erwartung |
|---|---|---|
| T1 | Datei erzeugen/öffnen, umbenennen, neuen Pfad separat öffnen; natives Paar + bestätigter Live-Scope. | DIESELBE |
| T2 | Zwei getrennt exklusiv erzeugte, gleichzeitig offene Dateien; natives Paar + Live-Scope. | VERSCHIEDEN |
| T3 | Tatsächliche Kopie derselben anfänglichen Bytes, zwei gleichzeitig offene Dateien; natives Paar + Live-Scope. | VERSCHIEDEN |
| T4 | Nur zwei gleiche kontrollierte relative Pfadtexte; reduzierte/synthetische Auswertungssicht, kein zusätzlicher Dateiversuch. | UNBEKANNT |
| T5 | Nur tatsächlich gemessener Gleichheitsstatus der T3-Inhalte vor Markeränderung. | UNBEKANNT |
| T6 | Nur tatsächliche gleiche SHA256 der T3-Inhalte vor Markeränderung. | UNBEKANNT |
| T7 | Synthetisch gleiches historisches Paar aus der operational freigegebenen Ausgangsdatei der bereits abgeschlossenen Inodensuche, zweimal angeboten, aber live_handle_overlap_confirmed=false. Keine neue Freigabe-/Wiederverwendungssuche und kein Beleg einer echten Kollision. | UNBEKANNT |

Primärkanal enthält keine Operation, Fallbezeichnung, Erwartung, GT, Pfade,
Inhalte, Inhalts-Hashes, FD-Nummern, UID/GID oder Zeitstempel. Der kontrollierte
Abfrageplan ordnet run 1–7 den Fällen zu; der Observer sieht keine Sollwerte.
T4–T6 verwenden gesonderte kinds, deren Werte nie Identitätsbeweise sind.
Unnötige Inhalte bleiben transient. Nur T6 behält ausdrücklich beauftragte
Hashkontrollwerte; keine Rohbytes oder vollständigen stat-Dumps speichern.

## Unabhängige Ground Truth und versiegelte Antworten

T1–T3: tatsächliche bidirektionale I/O-Kopplung, entsprechend dem vorherigen
lokalen Test. 32-Byte-Startdateien, exakte 64-/96-Byte-Markerwrites mit truncate,
vollständige Reads mit EOF-Probe. Own-Write muss sichtbar sein; Übernahme des
Markers in beiden Gegenansichten → DIESELBE; beide Gegenansichten unverändert
gegen ihre jeweilige frische Basis → VERSCHIEDEN. Gemischte oder fehlgeschlagene
I/O → UNBEKANNT/UNBEURTEILBAR. Keine Namen, Operationserwartungen oder nativen
Paargleichheiten in der GT-Ableitung. Nur Checks/Längen/Stufen archivieren.

Die historische unveränderte I/O-Referenzfunktion darf als Testhilfe importiert
werden; weder sie noch die alten Tests werden geändert. Unabhängigkeit ist
methodisch, nicht infrastrukturell: beide Verfahren vertrauen Kernel/Collector.

Alle Originalinputs und GT getrennt speichern. Ein separater Antwortprozess
liest ausschließlich sieben vorher benannte Inputs, ruft die neue Funktion,
speichert A/B/C und SHA256 vor GT-Vergleich. Original-/Antwortcheckpoint committen,
pushen, remote bestätigen; erst danach GT inhaltlich vergleichen. Hashes/Commits
sind Integritäts-/Ablaufbelege, keine Quellechtheit oder externe Zeitauthentisierung.
Auswertungen getrennt; Originale niemals überschreiben.

## Bewertung und Abschluss

Jeden Fall als KORREKT/FALSCH/UNBEURTEILBAR ausweisen. T1–T3 zählen gegen die
unabhängige I/O-Referenz. T4–T7 zählen als erfüllte/verletzte Enthaltungsregel,
keine positiv erkannten unbekannten realen Identitäten. A/B/C gemeinsam prüfen:
passendes Wort mit missbrauchtem Beleg ist FALSCH.

SUPPORTED IN THIS CASE SET nur mit allen sieben erwarteten A-Antworten,
beurteilbarer Referenz für T1–T3 und korrekten Belegen/Grenzen ohne Pfad-/Inhalts-/
Hashschluss. Sonst FALSCH → REFUTED im betroffenen Umfang; Mess-/Referenzfehler
oder unentscheidbare Primärfälle → INCONCLUSIVE. Keine automatische Reparatur.

Vor realer Aufnahme statische interne Quellprüfung und kleine synthetische
Parser-Grenztests (fehlende Bindung, Scope, Zahlen, widersprüchliche Belege).
Diese sind Entwicklungsvalidierung, keine zusätzlichen realen Dateifälle.
Implementierung vor Aufnahme separat committen/pushen; nach Freeze keine Änderung
während der Aufnahme/Auswertung. Nach dem Test dieselbe Standardsuite zweimal:

```sh
PYTHONDONTWRITEBYTECODE=1 /workspace/venvs/authority/bin/python -m pytest -p no:cacheprovider -o addopts='' -q
```

Bestehende Tests unverändert; fünf RC-01–05-Deselektionen sichtbar. Separate rote
OOS-021-Probe außerhalb der Standardsuite nicht neu starten/reparieren. Neue
Parser-Grenztests sind synthetisch und belegen keine Dateisystemzuverlässigkeit.

Ausgangsdateien per Hashmanifest erhalten, einzige erlaubte bestehende Codeänderung
ist die additive Funktion in observer_research.py. Dessen alter Code muss nach
Entfernen dieses Zusatzes bytegleich sein. Vertrag und Implementierungs-/
Antwortcheckpoint unverändert. Ergebnisbericht nennt vollständige Commit-SHAs,
Information/Zweck, Originale, A/B/C, GT, Bewertungen, Fehler/Cleanup, Grenzen,
beide Suiteausgaben und beide Confidence-Achsen. K14 bleibt im historischen
Umfang INCONCLUSIVE; E2-Metadaten-Lücke und OOS-021 bleiben offen.

**STOPP nach Bericht, Commit, Push und Remote-Bestätigung.** Keine dauerhafte
ID, Register, Generation-Systeme, Cloud, URLs, Datenbanken, weitere Ressourcentypen,
Symlink-/Mount-/Namespace-Gesamtlösung, kryptografische Echtheit, Graphen,
weitere Inodensuche oder nächste Observerfunktion.
