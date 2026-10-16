# Aufbewahrung und Empfang – qualifizierte Ergaenzung

Auftrag vom 16.10.2026, 23:22 Berlin. Ausschliesslich Agent Authority,
bestehender Worktree `hosted-qualification`, Branch
`codex/hosted-qualification-20261016`, Ausgangscommit `44af0b6`.
Vorgaenger `20261016T211328.908495Z` meldete `codex_completed`,
`completion.json` Ende `2026-10-16T21:32:31.117177Z`. Vor Aenderungen gelesen:
Runabschluss, damalige Bedien-/Qualifikationsberichte, Dienstcode und AGENTS.md.
Arbeitsstand anfangs sauber. Beim Abschluss erschien die fremde unversionierte
`docs/USER-ROADMAP-KI-ZENTRALE.md`; sie bleibt unveraendert und ausserhalb des
eigenen Commits. Keine weiteren Agenten/Worktrees durch diesen Auftrag, kein eigener Parallelauftrag,
kein Push, Deployment oder Produktserverzugriff.

## Implementiert

Der **bestehende private Dienst** besitzt fuer neue kurzlebige States jetzt
absolute Berichtstermine ab Fertigstellung (maximal 24h), ausdrueckliche signierte
Empfangsbestaetigung fuer Mandant/Job/Version/Digest, Zugriffssperre vor
Dateibereinigung und wiederholbare Bereinigung mit ehrlichem Fehlerstatus.
GET/Download/RST bestaetigt keinen Empfang. Eine Bestaetigung kann keine neue
Ausfuehrung ausloesen. Fristen bleiben ueber Prozessneustarts bestehen.

Eigene Eingabeenvelopes und Dispatchpins verschwinden nach Berichterstellung;
verschluesselte Zwischenstaende und abgebrochene Transaktionen werden bereinigt.
Stagnierende offene Jobs werden nach 60s, laufende nach 180s konservativ beendet,
keine automatische Wiederholung. Expliziter signierter Abbruch ist vorhanden.
AES-256-GCM je Auftrag und in-memory OpenSSL-Ed25519 ersetzen Klartextfelder und
Dienstsignaturtempfiles. `secure_delete`, Speicher-Tempstore, WAL-TRUNCATE und
Pfadpruefungen sind Teil der Bereinigungsbestaetigung. Ein dauerhaft maximaler
UTC-Zeitstand verhindert Wiederaufleben durch lokale Uhr-Rueckstellung.

DE/EN-Information vor Einreichung: `/` und `GET /v1/privacy`.
Status/Bericht/Empfangsantwort enthalten konkrete Fristen, Empfang, Zugriff,
Keydateizustand und **tatsaechlich bestaetigte** Bereinigung. Der CLI unterscheidet
vollstaendiges Empfangen von nachfolgender ausdruecklicher Bestaetigung:

```sh
python -m research.private_service.client receive JOB --config NEUER_STATE/config.json --output EMPFAENGERDATEI.json
python -m research.private_service.client confirm JOB --config NEUER_STATE/config.json --report-file EMPFAENGERDATEI.json
```

`receive` speichert 0600/O_EXCL, prueft Signatur und fsynct die Datei; keine
Bestaetigung durch blossen Abruf. `confirm` prueft die vollstaendige Datei erneut.
Die Empfaengerkopie unterliegt anschliessend deren eigener Aufbewahrung.
Der Browser zeigt Zustand und Bericht; er besitzt keine privaten Signierkeys.
Neue Demo-Transkripte enthalten nur Fall/Route/Rolle/Status/Fehlercode, keine
Request-/Berichtsinhalte. Der optionale rohe HTTP-Testtranskriptlogger ist entfernt.

## Praktisch geprueft

[Vertragstests](contracts-tests.log), [JUnit](contracts-junit.xml) und
[unveraenderte Produkt-/A1–A4-Regressionen](regressions-tests.log),
[JUnit](regressions-junit.xml). **91 Dienst-/Speicherpruefungen bestanden: 30 neue Loesch-/Aufbewahrungschecks,
39 bestehende Dienstchecks und 22 uebernommene Ledgerchecks. Separat 214
unveraenderte Produkt-/A1–A4-Regressionen bestanden (305 eindeutige Tests, keine
Addition wiederholter Laeufe).** [summary.json](summary.json).
Die neuen Tests benutzen echte private Tempverzeichnisse/SQLite-/WAL-Dateien,
kontrollierte UTC-Zeit und echtes Loopback-HTTP. Sie pruefen:

* gueltige/gefaelschte/fremde/unvollstaendige/falsche Version-/Digestbestaetigung;
  exakten und frisch signierten Retry, authentisierte Objektbindung;
* GET und TCP-RST ohne Empfangsbestaetigung, kein Inhalt/Secret in Fehlerlogs;
* letzte Millisekunde/Fristgrenze, ueberfaellige Neustarts, automatische Idlewartung;
* konkurrierende echte Prozesse fuer Abruf/Bestaetigung, Prozessabbruch vor/nach
  Commit (uebernommene Dienstpruefung), verwaiste Auftragdateien;
* Fehler/Abbruch/Timeout, verweigerte Dateiloeschung, gepinntes echtes WAL mit
  unvollstaendigem Checkpoint, Wiederholung und Neustart nach Bereinigungsfehler;
* verbleibende Replayabwehr und ihr konkretes Ende, kein Wiederanlegen nach
  Fristpruning oder Rueckstellung der Uhr, Authregister separat erhalten;
* bekannte AES-256-GCM-Testbytes, falsche AAD/Tags, bestehende historische
  Ed25519-/A4-Belege, fehlende Inhalts-/Key-/Ciphertextreste an eigenen zugesagten
  Dateipfaden, Rechte, kein Signaturtempfile und tatsaechliche API/OpenAPI-Felder;
* Historien-/Symlinkschutz und Runnerverweigerung vor jeglicher VM-Beruehrung.

Testpayloads/Keys werden am Fixtureende gezielt bereinigt, auch nach den bewusst
simulierten Fehlern. Die sieben diesem Auftrag zugeordneten inaktiven pytest-
Namensraeume wurden anschliessend nach explizitem Inventar entfernt; ihre Abwesenheit
ist geprueft. Die erste Inventur erzeugte SQLite-WAL-Sidecars und zwei
Regressionstests hinterliessen FIFOs: Die Bereinigung wurde dabei nicht als Erfolg
ausgegeben, sondern nach geschlossenem DB-Zugriff bzw. exakt geprueften FIFO-Pfaden
wiederholt. [Abschluss und Restdateiinventar](test-cleanup.json). Dauerhafte Nachweise enthalten nur Testausgaenge und
inhaltsfreie Inventare, keine neue Rohbeleg-/Schluesselkopie. Historische Belege
unter `docs/private-service-20261016/` werden ausschliesslich gelesen.
Es ist kein neuer Linux-/Kernel-Livelauf und kein frischer Wirkungsbeleg.

## Tatsaechliche Speicherinventur und Grenzen

| Speicherort | Inhalt / Behandlung |
|---|---|
| Neuer `STATE/service.sqlite` | GCM-Auftrag/Annahme/Pins/Bericht; nach Abschluss nur verschluesselter Bericht plus inhaltsfreier Status |
| `service.sqlite-wal`, `-shm`, moegliches `-journal`, SQLite-Freeseiten | 0600 im 0700-State; `secure_delete`, MEMORY-Tempstore; erfolgreicher TRUNCATE und Pfadpruefung vor Bereinigungserfolg. Sperrleser erzeugt sichtbar failed. SHM enthaelt WAL-Index, keine absichtlich kopierten Inhalte. |
| `STATE/jobs/SHA256(tenant)/server-id/content.key` | Einziger dauerhafter GCM-Key je Auftrag, 0600; nach Empfang/Ablauf unlink + Verzeichnis/fsync. Keine Kopie in DB/Config. Alte SSD-Keybytes/Prozesskopien nicht als physisch vernichtet ausgegeben. |
| derselbe Job `/scratch` | Nur eigene verschluesselte Zwischenstaende; nach Abschluss/Abbruch entfernen; keine Clientpfade. Aktueller Intake legt keine Upload-Rohdatei an. |
| `.lifecycle.lock`, `clock_state`, `requests`, `request_deadlines`, `lifecycle` | Inhaltsfreie Serialisierung/Zeit-/Sperrdaten. Fristen siehe unten. Keine Schatteninhaltskopie. |
| `STATE/config.json`, `root/`, `report/`, `sender/`, `receiver/`, `runner/` | Bewusste lokale Auth-/Signiercredentials und Register; kein Bericht und kein Inhaltloeschziel. Keine Kopie ihrer Secrets im Nachweis. |
| `TMPDIR/pytest-of-landjunge/pytest-263` bis `pytest-269` dieses Auftrags | Eigene neue synthetische Teststates, Fehler-/Abbruchsimulationen und Regressionstempdateien. Fixturebereinigung und anschliessende gezielte Entfernung inaktiver eigener Namensraeume; [konkretes Inventar/Pruefung](test-cleanup.json). Keine Wiederherstellungskopie, da dies absichtlich kurzlebige Testdaten sind. |
| Repo `.pytest_cache`, `__pycache__` | Testkennungen bzw. kompilierte Quellen, keine absichtlich abgelegten Laufpayloads/Keys. Kein Dienst-HTTP-/Berichtscache. |
| Python-/OpenSSL-/HTTP-Speicher, Socket-/OS-Puffer | Inhalt waehrend Pruefung/Ausgabe; keine RAM-Zeroisierung zugesagt, keine Payloadlogs. Privater Loopback ohne Proxy/oeffentliche URL; `Cache-Control: no-store`; kein Browserlocalstorage/Serviceworker. Clientkopien koennen nicht zurueckgerufen werden. |
| `/tmp/a2-sign-*`, `/tmp/a2-verify-*` | Historischer OpenSSL-Transport schreibt Nachrichten/Signaturen dort; **neuer privater Dienst benutzt ihn nicht**. A4-Evaluator wird mit identischem Bytecode und EVP-Signaturtransport separat gebunden, alte Quellen bleiben gleich. |
| historisch `STATE/evidence-JOB`, `/tmp/a4-private-host-RUN` | Alte Runnerrohdateien bzw. CA-Datei. Keine neue Nutzung unter dieser Zusage; neue VM-Ausfuehrung gesperrt. |
| VM `/opt/a4c-RUN`, `/var/tmp/a4c-private-RUN`, `/var/tmp/a1-research-a4-RUN`, `/var/tmp/aa-hosted-recovery-RUN` | Alte Quellen/Zertifikat/Registry/Bindung, Gastkeys, synthetisches Ziel und bewusst erhaltene Recoverydaten. Alter Harness entfernt drei Gastkeys/Host-CA, verschiebt restliche Dateien in Recovery. Das ist keine vollstaendige kurzlebige Dateiloeschung. Kein Zugriff/Loeschen dieser historischen Forschungsdaten im Folgeauftrag. |
| VM `/tmp`, BCC-/Compilerzwischenstaende, Pythoncache, root-/Journald-/SSH-/Lima-Logs, Gastswap | Kein vollstaendiger Inhaltsausschluss/-loeschnachweis des alten Harness; deswegen kein neuer Dispatch. Preinstalled Quellen/Compilerartefakte sind nicht pauschal eigene kurzlebige Jobdateien. |
| Host `~/.local/share/agent-authority-a1-linux-vm/a1-research/{disk,vz-efi,cidata.iso,ha.*.log,serialv.log}` | Gestoppter vorhandener VM-Datentraeger und historische Logs/Bootdaten; keine neue Nutzung/Aenderung. `disk`: logische Groesse 12GiB, 0600. Kein SSD-/Image-/Snapshot-Erase-Nachweis. |
| Historische `.private-service-state`, Archive/Git, Papierkorb aus Vorgaenger | Bewusst erhaltene Forschungs-/Bedienbelege und alte Credentials. Kein TTL-Migrationsziel; neuer Code verweigert implizite Altschemamigration. Keine pauschale Bereinigung. |
| Time Machine / APFS / andere Backups / Crashdumps / Hostswap / KI-Sessionlogs | Read-only Inventur: FileVault OFF; Worktree Included; keine konfigurierten Time-Machine-Ziele und keine ausgegebenen lokalen Snapshots. Das beweist weder globale Backupfreiheit noch die Vernichtung alter Keykopien. Keine neuen Payload-/Secretkopien an diese Systeme durch die App; keine Claim von SSD-/RAM-/Backupbereinigung. |

Konkrete Sperrfristen:

* signierte Requests: `max(request.expires_ms, signer_key.expires_ms) + 65000ms`;
  maximale Requestgueltigkeit 60000ms, Zertifikat maximal 86400000ms,
  zusaetzliche Aufbewahrungstoleranz 5000ms; Frische selbst ohne Uhrkulanz;
* unsigned Challenge-Request: `request.expires_ms + 5000ms`; Challenge an ihrem
  eigenen expires_ms; niemals ein Testausfuehrungsrecht;
* Enrollment-/Widerrufsaudit: zugehoeriges `key.expires_ms + 65000ms`;
* Job-/Loeschstatus: spaeteres Ende von beteiligter Keyepoche +65s und
  unveraenderter Berichtsfrist +65s; konkrete API `residual_expires_at`;
  fehlgeschlagene Bereinigung behaelt den offenen Status bis zur Erledigung;
* Authregister/Key-ID-Nichtwiederverwendung/Config und inhaltsfreier UTC-Maximalstand:
  bis zur expliziten Stilllegung dieser lokalen Dienstidentitaet. Kein als
  Sicherheitsaufbewahrung getarnter dauerhafter Berichtsspeicher.

**Offen:** Garantierte Dateientfernung binnen 24h bei komplettem Dienstausfall,
Fehlerfreiheit der Dateibereinigung, KMS-/Hardwaregestuetzte Vernichtung aller
Keykopien, verschluesselter kurzlebiger VM-/Runner-/Compiler-/Swap-/Logspeicher,
Rollback-/Backuprestoreepoche und Produktionshaertung. Bei Ausfall wird vor
Zugriff beim Neustart gesperrt und nachgeholt; physisch koennen Restdateien laenger
liegen. Schluessel-unlink ist nur Unzugaenglichkeit im aktuellen Dienstnamespace,
kein Beweis gegen vergangene Backups oder SSD-Forensik. **Keine vollstaendige
Produktions-Loeschzusage** und kein uneingeschraenkt live nutzbarer neuer Runner.

Die unabhaengig implementierbaren API-/Aufbewahrungs-/Dateischritte sind damit
reviewbar umgesetzt und praktisch getestet; die genannten Betriebszusagen sind
ausdruecklich nicht als erfuellt ausgewiesen. Keine historische Forschung geloescht,
kein neuer Dienst erfunden, keine VM gestartet, keine neuen Probes/Installationen.
