# Quellenneutraler Produktvertrag

Dieser aktuelle Vertrag ergänzt die eingefrorenen P10-Verträge. Historische
Spezifikationen und Forschungsnachweise werden nicht geändert.

`agent_authority.observations` definiert unveränderliche `Source`, `Entry`,
`Diagnostic` und `Snapshot`. Quelle: Adaptertyp und Quellenkennung; Beobachtung:
Eintragskennung, gespeicherte Reihenfolge (`ordinal`), gemeldeter Beitragstyp,
gemeldeter Actor-Typ, optionaler Aufgabenbezug und SHA256 der gelesenen Datei.
Reihenfolge und Actor sind Meldungen, keine Kernelzeit oder Authentisierung.
Der Vertrag verlangt weder ThreadDesk-Verzeichnisse noch zwölfstellige Hex-IDs
noch eine feste Liste von Agenten. Die vorhandenen Beitragstypen bleiben erhalten;
sie beschreiben Meldungen, keine Entscheidungen von Agent Authority.

Die JSON-Eingangsfassung heißt `agent-authority-observation-v1`. Pro Datei:

```json
{
  "schema_version": "agent-authority-observation-v1",
  "id": "event-1",
  "source_id": "local-run",
  "ordinal": 1,
  "kind": "result",
  "reported_actor_type": "local-client",
  "task_key": "task-1"
}
```

Die Datei heißt `event-1.json`. Quellen- und Eintragskennungen sind 1–128
ASCII-Zeichen: zuerst Buchstabe/Ziffer, danach zusätzlich `_`, `.` oder `-`.
`ordinal` ist eine Ganzzahl von 0 bis 2^63−1, kein Boolean; Actor-Typ maximal
80 Zeichen, Aufgabenkennung maximal 300 Zeichen, jeweils nicht leer.
Zusätzliche Inhalte und Metadaten werden nicht in den Bericht übernommen.
JSON mit doppelten Schlüsseln, nicht endlichen Zahlen oder widersprüchlichen
Kennungen wird abgewiesen. Dateifingerprints authentisieren keinen Verfasser.

```sh
agent-authority inspect --source json-directory --input /pfad/beobachtungen \
  --source-id local-run --format json
agent-authority inspect --source threaddesk-whiteboard --store /pfad/store \
  --thread 123456abcdef
```

Der ThreadDesk-Adapter hält seine bisherigen Format-, Actor- und ID-Prüfungen
lokal und liefert denselben Snapshot wie der neutrale Adapter. Alte Aufrufe mit
`--thread` wählen weiterhin diesen Adapter; nur dort gilt `~/.threaddesk` als
Standardpfad. Ohne Quellenwahl oder `--thread` wird kein Store angenommen.
Gemischte Adapterargumente werden abgewiesen.

`build_report`, Text und HTML hängen ausschließlich vom neutralen Snapshot ab.
Der Bericht heißt `agent-authority-observation-report-v1`, enthält
`source.kind` und `source.source_id` statt `thread_id`, und nutzt neutrale
Eintragsreferenzen (E42). Der frühere Whiteboard-Berichtsvertrag wird nicht
parallel ausgegeben. JSON-Verbraucher müssen diese explizite Schemaänderung
berücksichtigen. Die Aufgabenanalyse und Ausblendungszähler bleiben gleich.

D-012 gilt unverändert: ausschließlich Beobachtung und Analyse. Identität,
Herkunft und tatsächliche Wirkung bleiben UNBEKANNT; Aufgabenabschluss,
Rechteübernahme und Quellenauthentisierung werden nicht bewiesen. Dieser
Vertrag integriert keine A1–A4-Livebeobachtung und verspricht keine atomaren
Snapshots. Er ist der Eingang für die spätere eigenständige App, kein neuer UI-Bau.

## Ressourcenvertrag der Dateiadapter

Beide Dateiadapter benutzen dieselbe begrenzte Aufnahme in `file_reader.py`:

- Höchstens 10.000 zurückgegebene Verzeichniseinträge je Scan, unabhängig von Endung oder Typ. Ein weiterer Eintrag dient nur zur Überlauferkennung; er wird nicht in die Liste aufgenommener Namen übernommen.
- Zwei Scans (Aufnahme und Änderungskontrolle), jeweils höchstens 10.001 beobachtete Namen. Erst die begrenzte Namensmenge wird sortiert. Keine vollständige `listdir`-Aufnahme.
- Höchstens 10.000 untersuchte JSON-Dateien; reguläre Dateien mit höchstens 65.536 Bytes. Symlinks/FIFOs werden weiterhin nicht verfolgt beziehungsweise blockierend gelesen.
- 8 MiB Gesamtbudget tatsächlich gelesener Rohbytes pro Aufnahme, auch für anschließend verworfenes JSON. Eine laut `fstat` nicht mehr passende Datei wird vor dem Lesen abgewiesen. Bei Wachstum nach `fstat` wird höchstens ein zusätzlicher Byte zur Grenzerkennung gelesen und gezählt. Danach werden keine weiteren Dateien aufgenommen.

`directory_entries_seen` und `files_seen` beziehen sich auf die erste
Verzeichnisenumeration. `directory_scan_complete=false` und
`files_seen_is_lower_bound=true` zeigen an, dass keine exakte Gesamtzahl ermittelt
wurde. Auch 0 gesehene JSON-Dateien können dann eine Untergrenze sein. Text und
HTML verwenden ausdrücklich „mindestens“. `bytes_read` zählt tatsächliche
Rohbytes einschließlich verworfener Eingaben und eines etwaigen Grenzbytes.
Nach einem Abbruch bleiben weitere Inhalte UNBEKANNT; die bis dahin gelesenen
Einträge werden analysiert, nicht als vollständiger oder neuester Gesamtverlauf
ausgegeben. Bei vollständiger Enumeration bleibt die bisherige Sortierung erhalten;
bei Begrenzung hängt die Teilmenge von der Verzeichnisreihenfolge ab.

`directory_limit`, `input_limit` oder `input_byte_limit` machen den Bericht
unvollständig (Exit 2). Die bestehende Signaturprüfung der gelesenen Dateien und
der Quellenverzeichnisidentität bleibt erhalten. Ein während der Aufnahme
größer gewordenes Verzeichnis wird auch im Kontrollscan begrenzt und als
unvollständig/gegebenenfalls verändert gemeldet. Plattformen ohne sichere
`scandir(fd)`-/`open(dir_fd)`-Unterstützung werden abgewiesen.

Die Grenzen beschränken aufgenommene Daten und Iterations-/Parserarbeit, nicht
Wartezeiten einzelner Betriebssystemaufrufe oder die exakte Prozess-RAM-Nutzung.
Langsame oder blockierende Dateisysteme erfordern später gegebenenfalls eigene
Abbruchsteuerung durch die App. Keine atomare Snapshot- oder DLP-Garantie.
