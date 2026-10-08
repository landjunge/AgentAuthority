# Vorabvertrag: unmittelbar aktueller lokaler Collector

8. Oktober 2026. Ausgangscommit `916e810b3db338defabb90c4e2437573e43e0093`.
Ausgangspunkt: [NOT SUPPORTED mit V3/V5](OBSERVER-LOCAL-EVIDENCE-VALIDITY-RESULTS-2026-10-08.md).
Dieser neue docs-only Vertrag wird vor Implementierung committed, gepusht und
remote bestätigt. Historische Verträge, Ergebnisse, Originale und Tests bleiben
unverändert. Dies ist ausdrücklich ein neuer autorisierter Forschungszyklus.

## Frage und Hypothesen

Reicht eine unmittelbar aktuelle Prüfung im selben lokalen Observeraufruf,
um einen alten oder nur behaupteten Live-Beleg als alleinige Grundlage einer
sicheren Ressourcenidentitätsaussage auszuschließen?

- H1: Zwei tatsächlich jetzt gültige, gleichzeitig gehaltene reguläre Handles
  im geprüften gleichen lokalen Linux/tmpfs-Kontext, aktuelle native Paare und
  Übereinstimmung mit den angebotenen Paaren tragen DIESELBE bzw. VERSCHIEDEN.
- H2: Früher gültiges Packet nach vollständiger operationaler Freigabe ohne
  neue Prüfung trägt UNBEKANNT.
- H3: Handgefertigtes formal gültiges Packet mit ausschließlich positiven
  Behauptungen ohne aktuellen Collectoraufruf trägt UNBEKANNT.
- H4: Aktuelle Prüfung widerspricht behaupteter Gültigkeit, insbesondere
  ungültige Handles: UNBEKANNT. Die gespeicherte Behauptung gewinnt nicht.
- H5: Fehlende oder nicht erfolgreich vollständige Prüfung trägt UNBEKANNT.

## Grundlage und Änderungsgrenze

Vollständig gelesen: Ausgangsbericht, Live-Datei-Bericht, Inodenwiederverwendungs-
Bericht, lokaler Dateiidentitätsbericht, RESEARCH-METHOD, OUT-OF-SCOPE-DEBT,
Observercode und lokale Aufnahme-/Antwort-/I/O-/Freigabehilfen. Unveränderte,
bereits vollständig gelesene Quellen werden weiterverwendet, nicht ersetzt.

Ein additiver enger Forschungsaufruf `infer_current_local_file_identity` im
Observer erhält ausschließlich die bisherigen primitiven Packetdaten, run und
optional zwei lokale numerische Handles als **flüchtige Laufzeitargumente**.
Keine neuen serialisierten Belegfelder, keine Callback-/Proof-Objekte, keine
fresh-/verified-Flags. Die alte Funktion `infer_live_local_file_identity` bleibt
bytegleich mit ihrem historischen Verhalten bestehen. Nur der neue Weg wird
hier geprüft; dies repariert nicht alle alten Aufrufwege oder E2/OOS-021.
Keine Autorisierung, Aktionssteuerung oder zusätzlichen Befugnisse.

## Exakte aktuelle Prüfung

Die bestehende eindeutige run/kind/value-Paarform bleibt erforderlich. Scope
muss Linux/tmpfs mit den beiden bisherigen booleschen true-Behauptungen angeben;
Referenzen müssen st_dev/st_ino und regular_file=true enthalten. Diese Werte
sind weiterhin **Behauptungen und Formanforderungen**, kein Wahrheitsbeweis.

Positive Aussagen erfordern zusätzlich im neuen Aufruf selbst:

1. Genau zwei verschiedene nichtnegative eingebaute int-FDs, keine bools,
   fileno-Objekte oder vom Aufrufer gelieferten Prüfresultate.
2. F_GETFD und fstat/S_ISREG für beide FDs **vor jeder Subprozess-/Pipeöffnung**.
   Damit können geschlossene Zahlen nicht erst durch Collector-Pipes neu belegt
   werden. Fehler abbrechen, nicht um gespeicherte Flags herumprüfen.
3. Linux tatsächlich per uname; `findmnt -T /tmp -n -o FSTYPE` tatsächlich tmpfs;
   beide aktuellen st_dev gleich dem gemessenen /tmp-Gerät.
4. Beide FD-/Typ-/Paarprüfungen nach der Kontextprüfung wiederholen, ohne
   geänderte Paare. Beide Handles durchgängig vom lokalen Aufrufer gehalten.
5. Die geordneten angebotenen Paare müssen exakt den neu gemessenen entsprechen.
   Nur dann Gleichheit → DIESELBE, Ungleichheit → VERSCHIEDEN.

Ohne Handles keine native Collectorprüfung und keine sichere Identität.
EBADF, Nicht-Regularität, bekannter Scopefehler oder Paarabweichung ergeben
UNBEKANNT. Technisch nicht durchführbare Prüfung ebenfalls UNBEKANNT.
Kein Cache, dauerhaftes Gültigkeitsobjekt oder Herkunftsnachweis wird erzeugt.

Keine konkurrierenden Schließer, FD-Neubelegungen oder Mount-/Namespacewechsel
im kontrollierten Messprozess. Diese bleiben Annahmen des engen Versuchs.
Die Checks sind sequenzielle Momentaufnahmen, keine atomare Betriebssystem-
Garantie. Passende alte/handgefertigte Zahlen **mit wirklich aktuellen passenden
Handles** könnten den aktuellen Vergleich tragen; das authentisiert niemals
die damalige Lebenszeit oder Herkunft des Packets. Dies ist kein Beweis gegen
einen manipulierten Python-Prozess/Collector und keine permanente Identität.

## Antwort A/B/C/D

Direkte Originalausgabe des neuen Observers, kein Antwortadapter ergänzt GT:

- A: DIESELBE / VERSCHIEDEN / UNBEKANNT.
- B: konkrete im aktuellen Aufruf durchgeführte Messung oder konkret fehlender/
  fehlgeschlagener Prüfschritt; keine bloße Flagbestätigung als Begründung.
- C: **JA** nur wenn der gesamte notwendige aktuelle Beleg für genau den
  angebotenen Vergleich erfolgreich geprüft ist. **NEIN** bei bekannter
  unzureichender Beleglage, einschließlich fehlender Prüfung und EBADF.
  **UNBEKANNT** bei technischem Hindernis, das die Prüfung unbeurteilbar macht.
  Ein bloß begonnener Collectoraufruf ist noch kein JA. NEIN beweist weder
  verschiedene Ressourcen noch Fälschung oder historische Ungültigkeit.
- D: enger lokaler Scope und verbleibende Grenzen, keine Produktgarantie.

## Eingefrorene Fälle, genau sieben Aufrufe

Alle neutralen Packets P1–P7 verwenden run=1 und die unveränderte bisherige
Belegform. Observer erhält weder Fallname noch Erwartung, GT oder Journal.

| Fall / Packet | Festes Verfahren | Erwartung A | Erwartung C |
|---|---|---|---|
| F1 / P1 | Eine eigene Datei separat zweimal geöffnet; passendes vorbereitetes Packet; neue Prüfung während beide Handles gehalten sind. | DIESELBE | JA |
| F2 / P2 | Zwei getrennt exklusiv erzeugte eigene Dateien; passende gespeicherte Paare; neue Prüfung während beide gehalten sind. | VERSCHIEDEN | JA |
| F3 / P3 | P1 bytegleich nach nachgewiesenem Schließen beider Handles, unlink/ENOENT und null eigenen Ziel-FD-Links erneut anbieten; keine Handles und keine neue Prüfung. | UNBEKANNT | NEIN |
| F4 / P4 | Handgebaut: zweimal (123,456), regular_file und alle Scope-Flags true; keine Ressourcen, keine Handles, kein Collectoraufruf. | UNBEKANNT | NEIN |
| F5 / P5 | P1 bytegleich, live=true unverändert; die bereits geschlossenen alten FD-Zahlen an aktuelle Prüfung geben. Keine FD-Öffnung im Observer vor Prüfung; EBADF erwartet. | UNBEKANNT | NEIN |
| F6 / P6 | Weitere eigene Datei zweimal öffnen, gültiges Packet vorbereiten; beide Handles unmittelbar vor neuem Aufruf schließen, sofortiges F_GETFD=EBADF, danach ohne intervenierende FD-Öffnung neue Prüfung versuchen. | UNBEKANNT | NEIN |
| F7 / P7 | Zwei neue getrennte eigene Dateien, unterschiedliche gespeicherte Paare; passende aktuelle Prüfung, kein pauschales UNBEKANNT. | VERSCHIEDEN | JA |

Feste Reihenfolge: F1 Antwort sichern → F1 unabhängige I/O-GT → vollständige
Freigabe → F3 → F5 → F4 → F2 Antwort/I/O-GT/Freigabe → F6 → F7
Antwort/I/O-GT/Freigabe. Vier reale Paaraufbauten, insgesamt sechs neu erzeugte
physische Dateien; keine weitere Quelle oder Inodensuche.

## Aufnahme und unabhängig bestimmte Referenz

Privater neuer Ordner `/tmp/aa-current-local-collector-20261008`, 0700.
Nur eigene Dateien, kein Fremdinhalt, keine echten Secrets/Zugangsdaten.
Aufnahmehilfe wird erst nach Vertrag gebaut, statisch geprüft und vor dem
einen echten Falllauf separat committed/gepusht/remote bestätigt.

Die API wird im selben haltenden Prozess aufgerufen, nicht in einem Kind ohne
Handles. Für den Test protokollieren ausschließlich delegierende Wrapper die
tatsächlichen fcntl/fstat/uname/stat/findmnt-Aufrufe und Ausgänge um genau diesen
Aufruf. Sie führen die Originalfunktionen aus, ersetzen keine Rückgabewerte
und stellen dem Observer keine Journale bereit. Danach vollständig restauriert.
Keine Rohinhalte, vollständigen stat-Dumps oder FD-Zielpfade speichern; nur
Prüfstufen, Ergebnisklassen und nötige native Paarprojektion im Packet/B.
FD-Zahlen bleiben Laufzeitwerte und werden nicht als dauerhafte IDs archiviert.

F1/F2/F7: Antwort speichern und hashen **vor** anschließendem unverändertem
bidirektionalem I/O-Orakel aus dem bisherigen Versuch. 32-Byte-Ausgangszustand,
eigene 64-/96-Byte-Markerwrites, vollständige Reads mit EOF-Prüfung. Sichtbare
eigene Änderungen plus beidseitige Kopplung → DIESELBE; eigene Änderungen plus
jeweils unveränderte Gegensicht → VERSCHIEDEN; sonst unbeurteilbar. Keine
native Gleichheit oder Solloperation als Identitäts-GT.

F3–F6: GT ist die operational belegte fehlende hinreichende **aktuelle**
Beleglage, niemals negative Ressourcenidentität. F3/F5 Freigabejournal separat;
F4 Konstruktion ohne Collector; F6 close und sofortige EBADF-Prüfungen, danach
gesondertes unlink/ENOENT/Null-FD-Link-Journal. C-Referenz unterscheidet fehlend,
begonnen und erfolgreich vollständig; die Auswertung prüft das Journal, nicht
ein selbstbestätigendes live_checked=true.

Alle sieben Antworten inklusive Hashes und Originaljournale unverändert
sichern. Prüfer liest GT bis zum committed/gepushten und remote bestätigten
Antwortcheckpoint nur als opaque Bytes. Auswertung separat danach. Antwort-
helper sieht allein Packet und flüchtige Handles, niemals GT oder Erwartungen.
Hash und Git belegen Integrität/Ablauf, keine kryptografische Quellechtheit.

## Bewertung, Fehler, Regression und Grenzen

A und C separat zählen, B/D auf konkrete Messung und Grenze prüfen. Erwartete
Enthaltung ist korrekt, keine belegte Verschiedenheit. Aufnahme-, Speicher-,
Referenz-, Mess- und Observerfehler getrennt sichern. Keine Reparatur oder
Wiederholung dieses Falllaufs; fehlende/unsaubere Referenz → UNBEURTEILBAR.

SUPPORTED IN THIS CASE SET nur mit allen sieben A/C wie eingefroren, konkreter
aktueller Begründung und ausschließlich tatsächlich nachgeprüften positiven
Aussagen. NOT SUPPORTED bei einer beurteilbaren sicheren Identität ohne
vollständige aktuelle passende Prüfung oder falschem beurteilbarem A/C.
INCONCLUSIVE bei unsauberem Testweg/Referenz. Achse A (Umsetzung) und B
(Hypothese) separat ausweisen, beide Confidence-Achsen nennen.

Nach Aufnahme unveränderte Standardsuite zweimal gemäß Methodik:

```sh
PYTHONDONTWRITEBYTECODE=1 /workspace/venvs/authority/bin/python -m pytest -p no:cacheprovider -o addopts='' -q
```

Bestehende Tests nicht schwächen; fünf historische RC-Deselektionen sichtbar.
OOS-021-Rotprobe nicht durchführen/reparieren. Alte V3/V5 mit ihren falschen
DIESELBE-Antworten ausdrücklich vergleichen und erhalten. E2-Lücke offen,
K14 außerhalb dieses lokalen Scopes weiter INCONCLUSIVE. Keine signierte,
verteilte oder dauerhafte Herkunftsgarantie. Interne Review-Kontexttrennung,
kein externer Audit.

Bericht mit Basis-, Vertrags-, Implementierungs- und Antwortcheckpoint-SHA,
Definition aktueller Prüfung, bleibenden Behauptungen, F1–F7, vor GT gesicherten
Antworten, GT, Bewertung, V3/V5-Vergleich, Regression und Confidence speichern,
committen, pushen, remote bestätigen. **Danach STOPP.** Keine Kryptografie,
Signaturen, TPM, Attestation, Cloud, globale ID, weitere Observerfunktion,
Architektur, Graph, Produktentscheidung oder anschließender Forschungsauftrag.
