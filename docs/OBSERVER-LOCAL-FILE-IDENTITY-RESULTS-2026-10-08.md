# Ergebnis: Identität echter lokaler temporärer Dateien

8. Oktober 2026. **Gesamturteil: SUPPORTED IN THIS TEST.**

Drei echte lokale Dateifälle wurden genau einmal aufgenommen. Der separat
ausgewertete native Metadatenvergleich lieferte drei korrekte, keine falsche
und keine unbeurteilbare Identitätsaussage gegenüber der getrennten
bidirektionalen Schreib-/Lese-Ground-Truth. Drei reduzierte Datensichten
lieferten jeweils UNBEKANNT. Keine Aufnahme-, Referenz- oder Cleanupfehler.

**Diese Aussage gilt ausschließlich für gleichzeitig lebende reguläre Dateien
im selben lokalen Linux/tmpfs-Messprozess. In L2 bleibt das alte Handle nach
unlink offen. Inodenwiederverwendung nach vollständiger Freigabe wurde nicht
geprüft.** Keine allgemeine Ressourcenbindung und keine Observererweiterung.

## Ausgangsstand, Vertrag und Reihenfolge

Branch: `research/observer-local-file-identity-2026-10-08`.

| Stand | Vollständiger Commit |
|---|---|
| Abgeschlossener Ressourcen-Epochen-Repeat-01, Ausgangsbasis | `eca84266e4d5c52368b5f5f0ca8476dc1a834933` |
| Neuer Vorabvertrag, vor jedem Dateiversuch gepusht | `3a3541dfe9750ad51b9d432c4089c277cfc0217b` |
| Notwendige isolierte Messhelfer, vor Versuch gepusht | `13c62a0ed3cd3d799f98f03bc2d8c6ff086e1a01` |
| Originalaufnahme und Antworten, vor GT-Vergleich gepusht | `5e072c92da5864b56b37c783d54985ad422e6e06` |

Vollständig gelesene, unveränderte Grundlage:

- [Ressourcen-Epochen-Repeat-01](OBSERVER-RESOURCE-EPOCH-REPEAT-01-RESULTS-2026-10-08.md).
- [Real-Run-Prototyp](OBSERVER-REAL-RUN-PROTOTYPE-RESULTS-2026-10-07.md).
- [Konsolidierung E1–E7](OBSERVER-RESEARCH-CONSOLIDATION-E1-E7-2026-10-07.md).
- [E3–E7](OBSERVER-E3-E7-2026-10-07.md).
- [RESEARCH-METHOD](RESEARCH-METHOD.md) und [OUT-OF-SCOPE-DEBT](OUT-OF-SCOPE-DEBT.md).

Der [Vorabvertrag](OBSERVER-LOCAL-FILE-IDENTITY-CONTRACT-2026-10-08.md)
blieb unverändert. Vor Ausführung erfolgten AST-Syntaxprüfung und eine
interne, kontextgetrennte Quelltextprüfung; dabei erkannte Lücken der
Fehleraufzeichnung wurden **vor** Helferfreeze und erstem Versuch behoben.
Es gab keinen vorherigen Entwicklungs-/Probelauf der Dateifälle.

Ablauf: Vertrag remote bestätigt → Helfer remote bestätigt → einmalige
Aufnahme L1–L3 → Originalinputs gesichert/gehasht → separater Analyst →
Antworten gespeichert/gehasht → Antwortcheckpoint remote bestätigt →
erst danach Ground Truth gelesen und verglichen → Standardsuite zweimal.
Vor dem Antwortcheckpoint wurden GT-Dateien nur unverändert byteweise kopiert
und gehasht, nicht inhaltlich gelesen oder verglichen.

[Capture-Prozess](observer-local-file-identity/2026-10-08/capture-process.json),
[Inputseal](observer-local-file-identity/2026-10-08/input-seal.json),
[Antwortcheckpoint](observer-local-file-identity/2026-10-08/answer-checkpoint-integrity.json)
und [getrennte Auswertung](observer-local-file-identity/2026-10-08/derived/evaluation.json)
halten diese Durchführung fest. Die Remote-Bestätigungen erfolgten über
`git ls-remote`. Reihenfolge/Isolation beruhen zusätzlich auf dem
Durchführungsprotokoll; Hashes allein beweisen weder Entstehungszeit noch
Quellechtheit. Kein externer unabhängiger Audit.

## Testsystem und Bedeutung der lokalen Informationen

[Aufgenommenes System](observer-local-file-identity/2026-10-08/system.json):
Linux **6.18.44**, Python **3.12.14**, `/tmp` auf **tmpfs**. Ein einziger neuer
privater Ordner `/tmp/aa-local-file-identity-20261008`; ausschließlich darin
selbst erzeugte Testdateien. Keine Nutzerdateien, Accounts, Secrets, Netzwerk-
oder Cloudressourcen. Keine Namespace-/Mountwechsel im Messprozess.

Die vorab lesend geprüfte Python-Dokumentation `os.stat_result`/`os.fstat`
und lokale glibc-Header `bits/struct_stat.h` beschreiben die nativen Felder:

| Information | Bedeutung und hier getragene Aussage | Grenze |
|---|---|---|
| `st_dev` | Geräte-/Dateisystemzuordnung des geöffneten Objekts | Kein universeller Host-, Mount- oder dauerhaft authentisierter Schlüssel |
| `st_ino` | Inodenummer innerhalb dieser Zuordnung | Allein nicht global; nach vollständiger Freigabe möglicherweise wiederverwendbar |
| Paar `(st_dev, st_ino)` per `fstat` | Vergleich der tatsächlich geöffneten, gleichzeitig lebenden Dateisystemobjekte | Nur im festgelegten lokalen Lebenszeit-/Dateisystemscope getestet |
| `regular_file` | `fstat` bestätigt reguläre Datei | Keine Aussage über andere Ressourcentypen |
| Überlappung und gleicher Messprozess | Beide Handles blieben offen; `F_GETFD` bestätigte ihre Gültigkeit | Vom lokalen Collector gemeldet, nicht kryptografisch attestiert |

Ressource bedeutet **lebendes Dateisystemobjekt**, nicht Pfad, Inhalt,
Inhaltsversion, Deskriptornummer oder offene Dateibeschreibung. Die beiden
Handles wurden jeweils separat geöffnet; der Analyst erhielt ihre Nummern
nicht. Beide blieben bis nach der Referenzprüfung offen.

Die [feste Aufnahmehilfe](../probes/local_file_identity_capture.py) und der
[separate Analyst](../probes/local_file_identity_analyze.py) importieren keine
Observer-/Lab-Produktlogik. Primärinputs enthalten nur zwei native Paare,
reguläre-Datei-Prüfung und den begrenzten Lebendigkeits-/Prozessscope.
Keine Fallnamen, Operationen, Erwartungen, GT, Pfade, Inhaltsdaten, Hashes,
vollständigen Stat-Dumps, UID/GID oder Zeitstempel im Primärinput.

Dies ist ein Eignungsvergleich, **keine Feldablation**. Eine weltweit oder
für andere Abläufe kleinste Pflichtfeldmenge ist nicht nachgewiesen;
insbesondere hatten alle sechs gemessenen Referenzen dasselbe `st_dev=34`.

## L1–L3: Originalbelege und gesicherte Antworten A/B/C

| Fall und tatsächliche Operation | Native Paare vorher/nachher | Antwort A vor GT-Vergleich | I/O-Ground-Truth | Bewertung |
|---|---|---|---|---|
| L1: A erzeugt, A nach B umbenannt, B separat geöffnet | `(34,3488)` / `(34,3488)` | DIESELBE | DIESELBE | KORREKT |
| L2: A erzeugt, unlink, unter demselben Pfad neue A exklusiv erzeugt; altes Handle behalten | `(34,3494)` / `(34,3495)` | VERSCHIEDEN | VERSCHIEDEN | KORREKT |
| L3: A erzeugt, B als echte Kopie mit gleichen anfänglichen Bytes erzeugt | `(34,3501)` / `(34,3502)` | VERSCHIEDEN | VERSCHIEDEN | KORREKT |

Originalinputs: [P1](observer-local-file-identity/2026-10-08/observations/P1.json),
[P2](observer-local-file-identity/2026-10-08/observations/P2.json),
[P3](observer-local-file-identity/2026-10-08/observations/P3.json).

Antwort B, unverändert aus dem [versiegelten Antwortartefakt](observer-local-file-identity/2026-10-08/responses/before-comparison.json):

- P1: „Native fstat-Paare (34, 3488) und (34, 3488) sind gleich; beide regulaeren Dateien gleichzeitig offen im selben lokalen Scope.“
- P2: „Native fstat-Paare (34, 3494) und (34, 3495) sind verschieden; beide regulaeren Dateien gleichzeitig offen im selben lokalen Scope.“
- P3: „Native fstat-Paare (34, 3501) und (34, 3502) sind verschieden; beide regulaeren Dateien gleichzeitig offen im selben lokalen Scope.“

Antwort C ist bei allen sechs Eingaben identisch, unverändert:

> Nur gleichzeitig lebende regulaere lokale Dateien im selben Linux/tmpfs-Messprozess; keine Pfad-/Inhalts-/Revisionsidentitaet, Persistenz nach Handlefreigabe, Quellechtheit, Neustarts, fremde Maschinen oder Netzwerke.

SHA256 der vor Vergleich gespeicherten gesamten Antwortdatei:
`f3bb7fdfbecacdb654f9c527fcffc26c89972ee9ad75fc22be4ba062c2ee197a`.
[Seal](observer-local-file-identity/2026-10-08/responses/sealed-sha256.json)
und Antwortcheckpoint enthalten die tatsächlichen Input-/Antwortdigests.
Originale blieben unverändert; Auswertung liegt getrennt unter `derived/`.

## Unabhängige Ground Truth: tatsächliche I/O-Wirkung

Die Referenzfunktion verwendet weder native Identitätspaare noch Fallnamen,
Sollwerte oder Analystantworten. Beide Handleansichten werden an Offset 0
vollständig gelesen, mit EOF-Probe. Dann wird über Handle 1 ein 64-Byte-Marker
geschrieben, die Datei auf diese Länge gesetzt und eigener sowie
gegenüberliegender Leseeffekt geprüft. Danach bilden die tatsächlichen neuen
Ansichten die frische Basis für die zweite Richtung: 96-Byte-Marker über
Handle 2, eigener und gegenüberliegender Leseeffekt.

Anfangsdateien hatten 32 Bytes. Die Markerlängen unterscheiden sich garantiert
von den jeweiligen Voransichten; eine Änderung wird nicht durch zufällige
Byteungleichheit vorausgesetzt. Exakte Write-Rückgaben waren in jedem Fall
64 und 96. Own-Write-Prüfungen waren in beiden Richtungen jeweils true.

| Fall | Längen `[Handle 1, Handle 2]`: Anfang → nach Write 1 → nach Write 2 | Gegenseite folgt dem jeweiligen Marker, beide Richtungen | Gegenseite bleibt gegenüber ihrer frischen Basis unverändert, beide Richtungen |
|---|---|---|---|
| L1 | `[32,32]` → `[64,64]` → `[96,96]` | true / true | false / false |
| L2 | `[32,32]` → `[64,32]` → `[64,96]` | false / false | true / true |
| L3 | `[32,32]` → `[64,32]` → `[64,96]` | false / false | true / true |

Damit folgt DIESELBE aus beidseitiger tatsächlicher Schreib-/Lesekopplung;
VERSCHIEDEN aus bestätigten eigenen Änderungen bei beidseitig unveränderten
Gegenansichten. Rename-/Copy-/Werkzeugstatus allein ist keine Ground Truth.
Gemischte/kurze/fehlgeschlagene I/O hätte UNBEKANNT ergeben. Sie trat nicht auf.

Getrennt archiviert: [L1](observer-local-file-identity/2026-10-08/ground-truth/L1.json),
[L2](observer-local-file-identity/2026-10-08/ground-truth/L2.json),
[L3](observer-local-file-identity/2026-10-08/ground-truth/L3.json).
Diese Artefakte enthalten tatsächliche Booleans, Längen, Vollzugsstufen und
Operationen, keine Inhalts-/Markerbytes oder nativen Identitätspaare.

**Unabhängigkeit ist methodisch, nicht infrastrukturell:** kausaler I/O-Befund
und Metadatenvergleich sind verschiedene Ableitungen, vertrauen aber demselben
Kernel und Collector. Eine kompromittierte Quelle, falsche Collector-Meldung
oder manipulierte native Metadaten wurden nicht untersucht.

## Negativkontrollen: drei Datensichten, keine zusätzlichen Dateifälle

Die Ansichten stammen aus L2/L3 **vor** den GT-Markeränderungen.
Der Analyst erhält daraus weder Falloperation noch Wahrheit.

| Kontrollinput | Tatsächlich sichtbare Daten | Antwort A | Bewertung der Zurückhaltung |
|---|---|---|---|
| [Nur Pfad](observer-local-file-identity/2026-10-08/controls/path_only.json) | Relative Pfadtexte `A`, `A` aus demselben L2-Ordner | UNBEKANNT | Vorgabe erfüllt |
| [Nur Inhaltsstatus](observer-local-file-identity/2026-10-08/controls/content_only.json) | `content_equal=true` | UNBEKANNT | Vorgabe erfüllt |
| [Nur Inhaltshashes](observer-local-file-identity/2026-10-08/controls/hash_only.json) | Zwei tatsächlich gleiche SHA256-Werte aus L3 | UNBEKANNT | Vorgabe erfüllt |

Der identische L3-Inhaltshash lautet:
`cec4bacdc055784c84ae4720487762245ffc907a8d0a6c4bc47c7c93957b0e72`.
Er ist nur Kontrollinformation über Bytes, keine neue Ressourcen-ID.
Antwort B für diese drei Eingaben, unverändert:

> Tragfaehige native Identitaet oder lokaler Lebendigkeitsscope fehlt; Pfad/Inhalt/Hash ersetzen sie nicht.

Antwort C steht oben. Alle drei unbekannten Antworten sind gültige
epistemische Zurückhaltung. Sie zählen weder als weitere Dateiversuche noch
als drei positive richtige Identitätsbehauptungen. Dass die zugrunde liegenden
L2/L3-Paare tatsächlich verschieden waren, wird ihnen nicht nachträglich als
Analystwissen zugeschrieben. Die Kontrollprüfung zeigt Einhaltung der
festgeschriebenen Enthaltungsregel, keine allgemein gelernte Sensorfähigkeit.
L2/L3 liefern zugleich konkrete Gegenbeispiele zu „gleicher Pfad/Inhalt/Hash
garantiert dieselbe Datei“.

## Messzahlen, Erhaltung und Standardsuite

| Messgröße | Anzahl |
|---|---:|
| Gestartete echte Dateifälle / Versuchsaufnahmen | 3 / 1 |
| Vollständig abgeschlossene Dateifälle mit unabhängiger Referenz | 3 |
| Aufnahme-, Referenz-, Cleanupfehler | jeweils 0 |
| Primäre korrekte / falsche Identitätsaussagen | 3 / 0 |
| Primär UNBEKANNT / UNBEURTEILBAR | 0 / 0 |
| Reduzierte Kontrollsichten / davon UNBEKANNT | 3 / 3 |
| Kontrollregel erfüllt / verletzt | 3 / 0 |
| Nach Aufnahme verbliebene temporäre Datenfiles | 0 |

[Capture-Status](observer-local-file-identity/2026-10-08/capture-status.json)
und unmittelbare Dateiprüfung bestätigten die Entfernung der temporären
Rohdatenfiles. **Keine Rohinhalte archiviert.** Payloads/Marker waren nur
transient in den eigenen Testdateien und im Speicher; `resources/` wurde
vom Ergebnisarchiv ausgeschlossen. Für L3 bleiben nur Gleichheitsstatus und
die ausdrücklich beauftragten Kontrollhashes erhalten.

Alle **221 getrackten Ausgangsdateien** bleiben bytegleich gemäß
[Freeze-Manifest](observer-local-file-identity/2026-10-08/frozen-integrity.json).
Vertrag, zwei Helfer sowie alle 15 ursprünglichen Mess-/Antwortartefakte
bleiben ebenfalls identisch zu ihren Freeze-/Checkpoint-Digests. Es wurden
nur die neuen isolierten Hilfen und Dokumentationsartefakte ergänzt.
Keine Änderung an Observer, Lab, bestehenden Tests oder historischen Befunden.

Gemäß Methodik zweimal dieselbe unveränderte Standardsuite:

```sh
PYTHONDONTWRITEBYTECODE=1 /workspace/venvs/authority/bin/python -m pytest -p no:cacheprovider -o addopts='' -q
```

| Lauf | Ergebnis | Exit |
|---|---|---:|
| [1](observer-local-file-identity/2026-10-08/standard-suite/run-1.log) | 340 passed, 5 deselected, 252 subtests passed in 7.67s | 0 |
| [2](observer-local-file-identity/2026-10-08/standard-suite/run-2.log) | 340 passed, 5 deselected, 252 subtests passed in 7.84s | 0 |

[Suite-Status](observer-local-file-identity/2026-10-08/standard-suite/status.json)
bewahrt Befehle und Exitcodes. Die fünf bisherigen Deselektionen sind
RC-01–RC-05 aus der unveränderten Real-Case-Collection, keine neuen Ausnahmen.
Die separate historische rote OOS-021-Probe liegt weiterhin außerhalb der
Standardsuite; sie wurde hier nicht erneut ausgeführt oder repariert.
Grüne Standardsuite bedeutet keine Ressourcen-/Sicherheitsgeneralisierung und
keine Wiederholung der einmaligen L1–L3-Aufnahme.

## Urteil, offene Grenzen und Confidence

**H1: SUPPORTED IN THIS TEST.** Im eingefrorenen lokalen Aufbau unterschieden
die tatsächlichen nativen Paare mit gemessenem Scope alle drei Fälle korrekt
gegenüber der I/O-Referenz. **H2: SUPPORTED IN THIS TEST.** Die drei reduzierten
Sichten erzeugten keine unbelegte Gleichheitsbehauptung; L2/L3 zeigen konkret,
dass gleiche Pfade bzw. gleiche Bytes/Hashes bei verschiedenen Dateien auftreten.

**CONFIDENCE IN EXPERIMENT RESULT: HIGH**, begrenzt auf diese eine Aufnahme
mit drei kontrollierten lokalen Dateifällen, gesicherten Daten und getrennten
Ableitungen. Keine statistische Belastungs- oder Reproduktionsaussage über die
Dateifälle: pro Fall gab es genau eine Ausführung.

**CONFIDENCE IN GENERALIZATION: LOW.** Untersucht wurden nicht:

- Vollständig freigegebene alte Dateien, Inodenwiederverwendung und ungebundene historische Snapshots. Gerade L2 hält das alte Objekt absichtlich lebend.
- Andere Dateisysteme, Dateitypen, Mount-/Namespacewechsel, konkurrierende Fremdänderungen oder Langzeitbeobachtung.
- Neustarts, andere Maschinen, Netzwerke, Cloudobjekte, URLs oder Datenbanken.
- Kryptografische Quellechtheit, kompromittierte Kernel/Collector, gefälschte Metadaten oder unabhängige externe Sensoren.
- Verteilte Agenten-/Connectorläufe, allgemeine Ressourcenbindung, ein minimaler universeller Pflichtfeldsatz oder ein Produktverfahren zur Handleverwaltung.

Historisches **K14 bleibt INCONCLUSIVE in seinem ursprünglichen Umfang**.
Der neue begrenzte lokale Beleg schließt die allgemeine Ressourcenfrage nicht.
Die E2-Metadaten-Lücke und OOS-021 bleiben unverändert offen. Keine neue
Befugnis, ALLOW/DENY-Funktion, Architektur, Graph oder allgemeine
Observerfähigkeit folgt aus diesem Ergebnis.

**STOPP.** Kein allgemeiner Ressourcensensor, Cloudtest, nächster Ressourcenfall
oder Folgeauftrag wurde begonnen.
