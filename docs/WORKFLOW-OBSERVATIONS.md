# Workflow-Beobachtung / Workflow observations

18.10.2026 · AA-C01, begrenzter AA-D01/AA-R01-Anschluss · Auftrag
`seven-tools-build-20261018-1833` · Ausgang `edd40b959fc898edc06e790fe3672e748d7dbb2c`.

## Deutsch

Agent Authority beobachtet ausgewählte, bereits vorhandene Meldungen. Es führt
keinen Auftrag aus, vergibt keine Rechte, stellt keine Geheimnisse bereit,
erhöht kein Budget und setzt keinen Stopp durch. Historische `lab/`-Mechanismen
werden weder importiert noch als Produktkontrolle reaktiviert.

Der neue Eingang ist **`agent-authority-workflow-event-v1`**. Ein ausdrücklich
neuer Bericht **`agent-authority-workflow-report-v1`** umschließt den bestehenden
`agent-authority-observation-report-v1` unter `observation_report`. Der bisherige
`inspect`-Aufruf, neutrale JSON-v1-Eingang und Reportvertrag bleiben unverändert.
Der native Graph unterstützt beide ausdrücklich benannten Reportversionen;
v1-Verbraucher erhalten nicht still ein neues Schema. Kein zweiter Live-Auditlog,
kein Auftragsstore, keine Warteschlange und kein Hintergrundsender entstehen.

### Ausgewählte Eingänge und tatsächlicher Abgleich

| Quelle | Wiederverwendbarer Eingang | Reichweite dieses Standes |
|---|---|---|
| ThreadDesk | Issued-/Bind-/Return-Metadaten, alter optionaler Whiteboardreader | Versioniertes Workflowformat kann diese Metadaten aufnehmen; kein automatischer Storezugriff oder Auftrag |
| KiraBridge | Bestehende eigene Task-/Audit-/Runtime-Metadaten und dauerhaftes Handoff-Mapping | Reiner `project_bridge_task`-Helper; Aufrufer liefert bereits autorisierte Metadaten und bestehende Audit-ID/-Sequenz, kein neuer DB-Leser/Emitter |
| TollGate | Bestehendes Authority-Envelope-JSONL, kontrollierte Statusprojektion | `budget.*`, `consumer.frozen`, `request.blocked`, `loop.detected`; vorhandener synthetischer c3a062d-Nachweis zusätzlich minimiert gelesen |
| 4AllPass | Bestehendes `backend/app/authority_emit.py` | Tatsächliche Legacytypen `capability.granted/denied/revoked` sind **Meldungen**, niemals eigene Freigaben des Beobachters |
| Gnom-Hub-V1 | Bestehendes `src/gnom_hub/authority_emit.py` | Tatsächliche Legacytypen `work.started/finished`, `agent.invoked`, `delegation.created`, `tool.intent/result` unterstützt |
| BlockDesigner | Task-/Snapshot-/Reply-Metadaten | `design.handoff/delivered` im neuen Vertrag; produktiver Sender und vollständiger Designkreislauf noch nicht abgenommen |

Quellcodeabgleich: AA `edd40b9`, ThreadDesk-M2 `05403916`/PR76, TollGate-Core
`c3a062d`/PR34; beim lokalen Abruf TD origin/main `a40ed8e`, FP origin/main
`82bf0f8`, GH origin/main `8108c64`. Diese Pins sind Codebefunde und keine Aussage,
dass alle zugehörigen Runtimes integriert seien. Fremde Arbeitsstände blieben
unverändert. Der BlockDesigner-Code wird vom zuständigen Worker abgeglichen;
hier wird kein erfundener aktueller Betriebsnachweis behauptet.

### Felder und Bindung

Pro JSONL-Zeile maximal 4096 Bytes. Pflicht im neuen Format:
`schema_version`, `source_tool`, `source_id`, `event_id`, `event_type`.
`ordinal` ist, falls vorhanden, die gemeldete Produzentensequenz (0..2^63−1).
Fehlt sie im Legacy-Envelope, bleibt globale Reihenfolge unbekannt.
`timestamp` ist ein begrenzter ISO-Zeitstempel mit Zeitzone oder unbekannt.
Die lokale `segment_id` ist der gelesene Dateiname, keine attestierte Epoche.

Zugelassene Referenzen (1..256 ASCII-Zeichen, Buchstaben/Ziffern/`_.:-`, keine
Pfade, freien URLs oder Queryparameter): Projekt, Gesamtauftrag, Thread,
`handoff_id`, **`original_task_id` und `bridge_task_id` getrennt**, `task_id`,
`run_id`, `attempt_id`, `parent_task_id`, `subtask_id`, `return_id`, `recipient_id`,
`session_id`, `principal_ref`, `operator_scope`, `actor_claim`, `source_ref`,
`artifact_ref`. Ein `thread:task` wird nicht durch Entfernen des Doppelpunkts
umgedeutet. Sitzungskennung ist kein Ersatz für Task-/Laufkennung.

`handoff_revision`, `source_revision` und `task_revision` bleiben eigene,
streng ganzzahlige Werte; keine Bool-/Float-Umdeutung. `request_hash` und
`source_hash` sind exakt 64 kleine Hexzeichen. Diese Werte sind nur Bindungs- und
Vergleichsreferenzen, keine Personen-/Modellidentität und keine unabhängige
Quellbestätigung. Nur bewusst freigegebene Fingerprints exportieren.

Budgetmetadaten: `reserved_microusd`, `spent_microusd`, `available_microusd`,
`cost_kind` (`estimated`, `evidenced_final`, `no_final_cost`, `unknown`). Ganze
USD-Microeinheiten, nie Bool oder Float; ein importiertes `evidenced_final` bleibt
**gemeldet**, nicht vom Beobachter unabhängig geprüft. Stoppmetadaten:
`stop_state` (`requested`, `pending`, `effective`, `abort_confirmed`, `unknown`),
`dispatch_seq`, `barrier_seq`. Auch ein gemeldetes `effective` beweist aus dieser
Datei keine tatsächliche Dispatchsperre oder Prozessbeendigung.

`reported_status`: `accepted`, `started`, `running`, `waiting_question`,
`turn_completed`, `delivered_unverified`, `checked`, `accepted_by_user`,
`unknown`, `failed`, `cancelled`. Selbst `accepted_by_user` ist hier nur eine
Produzentenmeldung; Agent Authority erteilt keine Nutzerabnahme. Ein Bridge-
`completed` wird im Helper ausdrücklich als `turn_completed` projiziert.

Die versionierte Ereignistyp-Positivliste steht in `workflow.EVENT_TYPES`. Neue
unbekannte Typen werden diagnostiziert, statt still als kompatibel angenommen.
Providerantworten, Authheader, `args`, Prompts, Volltexte, Schlüssel, rohe Logs und
beliebige Zusatzfelder werden nicht in Berichte übernommen. Eine Positivliste ist
keine allgemeine DLP-Garantie: der autorisierte Exporter muss sicherstellen, dass
auch seine ausgewählten Identitäts-/Referenzfelder kein Geheimnis enthalten.

### Bedienung und vorhandene Zustände wiederverwenden

Nach bestehender Python-3.12-Installation:

```sh
agent-authority workflow-inspect --input /ausgewaehlte/metadatensegmente \
  --source-tool kirabridge --source-id lokale-runtime --format json --limit 20
agent-authority workflow-inspect --input /ausgewaehlte/metadatensegmente \
  --source-tool tollgate --source-id kontrollierter-lauf --format html > report.html
```

Der Befehl liest nur das gewählte Verzeichnis. Er startet keinen Dienst/Agenten,
schreibt keine Quelldatei und verändert keine Auditdaten. Eine Ausgabe-Datei ist
allein die ausdrücklich gewählte Shellumleitung. Der bisherige native
**Bericht öffnen**-Weg beziehungsweise `--report /pfad/report.json` lädt den
Wrapper. Graph und Inspector zeigen zusätzliche gemeldete Bindungsfelder;
vorhandene Auswahl, Zurücknavigation, Belege, DE/EN und Bewegungsreduktion bleiben.
Der native Export eines neuen Workflowimports verwendet das vorhandene minimierte
Graphmodell (bis24 ausgewählte Zusatzfakten je Knoten), nicht blind das importierte
Original-JSON. So werden unbekannte Zusatzfelder nicht weiterexportiert. Der volle
minimierte Workflow-Report bleibt über die CLI-JSON-Ausgabe verfügbar; der bisherige
v1-Reportexport bleibt unverändert. Ein erneuter Import des UI-Graph-Exportformats
ist im bestehenden Report-Öffnen-Weg nicht implementiert.
Die Offline-HTML-/Textbasis ist weiterhin überwiegend Deutsch; die neue Workflow-
Ergänzung benennt ihre Grenzen zweisprachig. Native UI und README sind DE/EN.

KiraBridge-Anschluss ohne neue Protokollwelt:

```python
from agent_authority.workflow import project_bridge_task

record = project_bridge_task(
    owned_task_metadata,
    persistent_handoff_binding,
    source_id=runtime_reference,
    event_id=existing_audit_reference,
    ordinal=existing_audit_sequence,
    source_hash=loaded_source_fingerprint,
)
```

Der Aufrufer muss **vorher** Principal-/Projektgrenzen prüfen. Der Helper fragt
keine fremden Tasks ab, erzeugt keine neue Sequenz und ersetzt kein vorhandenes
Audit. Daten lesen, projektiert ausgeben und erst bei ausdrücklichem Bedarf als
begrenzten Snapshot sichern. Rückgabe-/Quelle-/Handoff-Revisionen bleiben getrennt.

### Wiederholung, Lücken, Rotation und Grenzen

- Eindeutige Quelle + Ereigniskennung + gleiche kanonische Inhalte wird einmal
  ausgewertet, auch über mehrere ausgewählte Dateien. Gleiche ID mit anderem
  Inhalt entfernt beide konkurrierenden Versionen aus der positiven Ansicht und
  zeigt einen Konflikt. Keine zusätzliche Wirkung aus Duplikaten ableiten.
- Fehlende, doppelte oder ungeordnete Produzentensequenzen und fehlende
  Hashkettenbezüge werden angezeigt. Ein erstes erhaltenes Segment mit unbekanntem
  Vorgänger bleibt unvollständig. Hashketten/Fingerprints authentisieren nichts.
- Vorhandener begrenzter Reader: höchstens 10 001 Verzeichnisnamen zur
  Grenzerkennung, 64 ausgewählte `.jsonl`-Segmente, je höchstens 65 536 Bytes,
  8 MiB gesamte Rohaufnahme, 10 000 Records, je 4096 Bytes. Dateideskriptoren,
  NOFOLLOW/Regular-File-/Änderungskontrollen und JSON-Duplikatprüfung werden
  wiederverwendet. Zu große unrotierte Dateien werden abgewiesen, nicht als
  vollständig oder automatisch als neuester Verlauf ausgegeben.
- Quelle/Produzent rotiert gegebenenfalls selbst. Der Beobachter rotiert, löscht
  und kopiert keine historischen Logs. Nach vorgelagertem Löschen bleibt der
  unbeobachtete Zeitraum unbekannt. Keine wachsende neue Cache-/Reportdatenbank;
  Aufbewahrung ausdrücklich gespeicherter Berichte entscheidet der Betreiber.
- `complete_selected_read` bedeutet nur, dass die ausgewählten begrenzten Dateien
  gelesen wurden. `workflow_evidence_complete` prüft zusätzliche strukturelle
  Hinweise im ausgewählten Ausschnitt; es ist keine Vollständigkeit sämtlicher
  Arbeit. Die Gesamtabdeckung bleibt **UNBEKANNT**, auch bei Exit0. Exit2 bedeutet
  einen unvollständigen/strukturell unklaren Ausschnitt, niemals ein Handlungsverbot.
- Langsame OS-/Netzdateisystemaufrufe besitzen hier noch keinen eigenständigen
  Live-Abbruch; vorhandener nativer Engineprozess hat seinen begrenzten Leseweg.
  Ein Web-/Pushdienst, bestätigter Rückkanal in einer Sprachsitzung, neue
  Authentisierung und AA-C03-Betrieb sind hier nicht gebaut.

AA-C02 bleibt getrennt: auftragssemantische Regeln für alte Rückgabegrundlagen,
falsche Empfänger, fehlende Artefaktbelege und tatsächlich angeschlossenen
Stopppunkt benötigen den jeweiligen Producer-/Adapterbeleg. Die hier geprüften
Lücken-/Konflikthinweise ersetzen diese vollständige Abnahme nicht.

## English

Agent Authority remains strictly **observer-only**. It grants no rights, secrets,
budgets or stop authority and does not import historical enforcement modules.
The new `agent-authority-workflow-event-v1` projects selected existing metadata;
`agent-authority-workflow-report-v1` explicitly wraps the unchanged neutral v1
report. Existing `inspect` consumers remain compatible. There is no second live
audit log, task store, queue or background emitter.

The CLI above reads selected bounded JSONL files only. Native **Open report** or
`--report` uses the existing graph/inspector and DE/EN navigation. Native workflow
exports use the existing minimized graph model, not unfiltered original JSON;
use CLI JSON for the complete minimized workflow report. Reopening UI graph exports
is not supported by the current report importer. Original neutral-v1 exports are unchanged. Reported original
task ID, Bridge task ID, run, session, handoff/source revisions, scope references
and hashes remain separate. Hashes, actor labels and imported authentication flags
never establish identity. Completed Bridge turns are reported as turns, not
project acceptance. Imported billing/stop claims remain reported observations.
No credentials, prompts, full replies/arguments or arbitrary log fields enter the
projection; the trusted exporter still must keep its chosen opaque references
secret-free. A whitelist is not universal DLP.

`project_bridge_task` receives already authorized Store/audit/runtime metadata and
persistent binding; the existing audit ID/sequence is supplied by the caller.
It opens no database and writes no new stream. Known existing TollGate, 4AllPass
and Gnom Authority Envelope v1 types are supported, with unknown global order when
legacy records lack an ordinal. BlockDesigner/ThreadDesk records use the explicit
new metadata contract; no end-to-end live producer integration is claimed here.

Identical events are deduplicated; conflicting IDs are excluded and shown as
conflicts. Missing/unordered sequences, retained rotation prefixes and hash-chain
gaps stay unknown. Existing no-follow file/budget checks are reused: 64 segments,
64KiB each, 8MiB total, 10 000 records, 4KiB per record, bounded directory scans.
No source deletion/rotation or ever-growing secondary cache. Producer rotation
and retention of explicitly saved reports remain operator responsibilities.
Completeness refers only to this selected slice; global activity, identity and
external effect remain UNKNOWN even on exit0. Exit2 is not an enforcement decision.
No web deployment, voice-session push guarantee, production semantic warning suite
or live-agent acceptance is claimed. See the evidence status for actual tests.
