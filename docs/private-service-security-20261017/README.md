# Praktische Sicherheitsabnahme des privaten Testdienstes

Nutzerfreigabe vom 16.10.2026, 23:33 Berlin; Umsetzung im vorhandenen Worktree
`/Users/landjunge/agent-authority-lab/.worktrees/hosted-qualification`, Branch
`codex/hosted-qualification-20261016`, Ausgangscommit `09bc5f2`.
Vor Beginn gelesen: Projekt-AGENTS.md, Dienst-/Qualifikations-/Loeschberichte,
API-Vertrag, Implementierung und Tests. Der vorgeschaltete Loeschauftrag
`20261016T213239.014587Z` war abgeschlossen: `codex_completed`,
`completion.json` Ende `2026-10-16T22:01:05.135414+00:00`.
Keine weiteren Agenten, kein neuer Worktree, kein Produktserverzugriff, kein
Paket-/Kernel-/Probeeingriff, kein Push und keine Veroeffentlichung.
Die fremde unversionierte `docs/USER-ROADMAP-KI-ZENTRALE.md` bleibt erhalten.

**Ergebnisgrenze:** Abnahme der unten genannten privaten Loopback-Wege mit
synthetischen Gegenfaellen. Keine absolute Sicherheitsgarantie und keine
Produktionsfreigabe. Neue VM-Ausfuehrungen bleiben wegen der offenen
Speicherqualifikation gesperrt. D-012 bleibt unveraendert: Agent Authority
beobachtet; Zugangsschutz fuer Dienstressourcen erteilt keine fachlichen
Agentenrechte. Jeder Dienstbericht behaelt `grants_rights=false`.

## Konkrete Befunde und Korrekturen

| Befund am Ausgangsstand | Korrektur / Nachweis |
|---|---|
| Doppelte Host-Header wurden akzeptiert; der erste Wert entschied. | Doppelte sicherheitsrelevante Header werden mit 400 abgewiesen. Der Test fuehrt den unveraenderten alten Adapter aus Commit `09bc5f2` nur auf eigenem Loopback aus und reproduziert 200; der neue Adapter liefert 400. |
| 5s Sockettimeout war eine Frist zwischen Lesevorgaengen. Langsames Nachliefern konnte die Anfrage beliebig strecken. | Absolute 5s-Verbindungsfrist ab Setup einschliesslich Header/Body/Ausgabe; Socket wird geschlossen. Alter Adapter akzeptiert im eigenen Test noch nach 6s nachgelieferte Header; neuer Header- und Body-Gegenfall beendet nach etwa 5s. Intake haelt keinen Lifecyclelock; danach ist der Dienst wieder erreichbar, kein Auftrag entstanden. |
| Dienstkonfiguration enthielt Client-/Runner-/Reportkeypfade und rohe Bearerwerte. | API-Konfigurationsprojektion mit Publicpins, Token-SHA256 und ausdruecklichen Objekt-Subjects. CLI akzeptiert ausschliesslich diese Projektion und einen separat operatorseitig gesetzten Berichtssignierpfad. Keine privaten Keybytes werden zum Signieren in den API-Prozess geladen. Signatur und Verifier laufen in festen begrenzten Kindprozessen. |
| Bearerrolle plus Mandant reichten zum Lesen jedes Objekts desselben Mandanten. | Token-Subjects muessen Sender/Empfaenger des Objekts bzw. Signer des Schreibrequests umfassen. `*` ist eine ausdrueckliche lokale Verwaltungsfreigabe. Fremdes Objekt bleibt bei GET 404; fremder Signer 403, auch vor einem exakten Idempotenzcache-Treffer. Fehlende Subjects geben keine Objektberechtigung. |
| Runnerwiderruf sperrte seine weitere Aufnahme, schloss seine laufenden Jobs aber nicht sofort ab. | Widerruf/Rotation des konfigurierten Runnerkeys beendet betroffene wartende/laufende Jobs atomar als UNBEKANNT, wie bereits bei den beteiligten Actors. Kein automatischer Wiederanlauf; alte Nachweise sind danach unzulaessig. |
| Base64-Legacybelege umgingen die aeusseren JSON-Strukturgrenzen. | Zusaetzliche begrenzte Legacyparser mit Duplikat-, Tiefen-, Breiten-, Knoten-, Byte- und Nichtendlichkeitspruefung. Fehler werden unvollstaendige Belege oder ein technischer Fehler, niemals BELEGT. Positivklasse verlangt genau 28 wahre Checks und 23 gemessene ganzzahlige Nullverlustwerte. |
| Lifecycle-flock und sqlite-Wartezeit konnten die HTTP-Zeitgrenze uebersteigen. | Begrenztes lokales Lock/flock, begrenzte SQLite-Wartezeit und weitergereichtes Gesamtbudget. Echte blockierende Gegenprozesssperre liefert STORAGE_BUSY und ist nach Freigabe wieder nutzbar. |
| Client pruefte die Ziel-URL nur als Zeichenkettenpraefix und nutzte Standardredirects/-proxies. | Strukturell ausschliesslich `http://127.0.0.1:PORT`, keine URL-Zugangsdaten, Pfade, Query oder Fragmente; keine Redirects und keine Proxy-Umgebung. Gegenfaelle werden vor Verbindungsaufbau abgewiesen. |

Ein bestehender Speicherregressionstest erzeugte zuvor einen frei aufgebauten
Bericht mit `synthetic_marker`. Er benutzt jetzt einen regulaeren UNBEKANNT-Bericht
mit demselben Marker im unterstuetzten Katalogversionsfeld. Inhaltssuche,
Verschluesselung und Loeschpruefung bleiben erhalten; die neue Signiergrenze wird
nicht fuer Tests gelockert. Die historische Stateverweigerung erfolgt weiterhin
vor Konfigurations-/Keyinitialisierung. Historische Quellen und Messarchive wurden
nicht umgeschrieben.

## Tatsaechliche Architektur und Rechte

Der HTTP-Prozess bindet fest an IPv4-Loopback. Start als UID/EUID 0 wird verweigert;
unter Linux werden zusaetzlich geerbte effektive, erlaubte, vererbbare und ambiente
Capabilities abgewiesen. Der echte CLI-Start wurde als normaler macOS-Nutzer mit
projizierter Konfiguration und Loopback-Abruf geprueft. Rootverweigerung ist lokal
simuliert getestet; Linux-Capability- und Sandboxwirkung ist hier **kein** Livebeleg.

Rootzertifikate werden nur operatorseitig erstellt. Enrollment benoetigt weiterhin
Adminzugang, unabhaengigen Publicrootpin, frische Besitzprobe und exakte Signatur.
Root- und Berichtsschluessel koennen nicht als Actor/Runner registriert werden.
Der API-Server signiert keine Clientauftraege und besitzt dafuer keine Keybytes.
Der Berichtssignierer akzeptiert ausschliesslich das feste versionierte
Berichtsformat, bekannte Domains/Klassifikationen und keine Rechteerteilung.
Es existiert kein HTTP-Signier-/Shell-/Exec-/Datei-/Ziel- oder Schluesselabrufweg.

Signierer und Nachweispruefer sind feste kurzlebige Unterprogramme des bestehenden
Dienstes, keine neuen frei zugaenglichen Dienste. Uebergabe nur ueber private
stdin/stdout-Pipes, feste Operationsnamen, JSON bis 512KiB, Ausgabe bis 64KiB;
keine Clientargumente als Programm, Shell, Keypfad oder Netzadresse. Bereinigte
Umgebung, `close_fds`, keine Payload-/Secret-/Exceptionausgabe auf stderr, kein
Signaturtempfile. Timeout/Abbruch toetet und reapet den eigenen Kindprozess.
Ausgabegroesse wird im festen Kindprogramm **vor** dem Schreiben und danach im
Elternprozess geprueft; dies ist kein generischer Supervisor fuer beliebige Programme.
Der eigentliche Collector/Runner wird vom HTTP-Code nicht importiert/gestartet;
es gibt weder Claim- noch Dispatchroute. Sein bestehender Hardstop bleibt erhalten.

**Offene OS-Grenze:** Alle lokalen Komponenten laufen unter derselben Host-UID.
Die API kennt den operatorseitigen Reportkeypfad, und diese UID kann prinzipiell
auch andere lokale Schluesseldateien lesen. Getrennte Prozesse/Config/Pipes sind
damit eine implementierte Funktions- und Ressourcenaufteilung, **keine** nachgewiesene
Isolation gegen einen kompromittierten API-Prozess. Signierer ist auch kein
unabhaengiger Auditor der vom Verifier gelieferten Wirkungsbehauptung. Getrennte
Konten/KMS/ACLs, eigener Registrar und Runner mit engem authentisiertem Broker
muessen am Ziel tatsaechlich durchgesetzt und angegriffen werden. Ein kuenftiger
Broker darf keine direkten API-Schreibrechte auf Collector-Pins/Registry eroeffnen.

## Geschuetzte Schnittstellen und Grenzen

Oeffentlich im privaten Listener: nur `GET /`, `/inspector.js`, `/v1/privacy`.
Der Browsercode ist absichtlich einsehbar, enthaelt keine Secrets/Privatekeys und
benutzt `textContent`, CSP und `no-store`. Der Nutzer gibt seinen Zugriffstoken
selbst ein; kein Token in URL/Localstorage, keine behauptete Verschleierung.

Authentisiert: Challenges, Enrollment, Widerruf, Jobanlage, exakte Annahme,
Nachweisaufnahme, Status, Bericht, Empfangsbestaetigung und Abbruch. Erlaubte
Routen und HTTP-Methoden sind explizit festgelegt. Graph, Dateidownload, Quellcode,
Git, Archive, Config/Env, Key-/DB-/WAL-/Journal-/Backup-/Temp-/fremde Berichtspfade
und URL-/Traversalvarianten haben keinen Dateiserver. Ein echter Symlink unter
dem Namen `inspector.js` liefert weiter ausschliesslich den konstanten Browsercode.
Status/Bericht und Schreibcache passieren Mandanten- und Subjectkontrolle;
Fehler enthalten nur feste Codes. Bestehende technische DB-Fehler-, RST-,
Loeschfehler-, Symlink- und WAL-Gegenfaelle laufen weiter mit.

Signaturinhalt bleibt das eingeschraenkte versionierte RFC8785/JCS-Objekt:
Schema, Domain, Audience, Mandant, POST, exakter Pfad, registrierter Key,
Nonce, Idempotenz-ID, Gueltigkeit und exakte Payload. Verschiedene JSON-Whitespace-
Darstellungen sind derselbe kanonische Inhalt, keine Signatur ueber rohe HTTP-Bytes.
Signaturen ersetzen keine Wirkung. Annahme, Evidencepins und Empfang binden den
genauen Auftrag/Annahme-/Berichtsdigest. SQLite-Transaktion und prozessuebergreifende
Sperre schuetzen Replay/Idempotenz; Neustart, gleichzeitige echte Worker und Abbruch
vor/nach Commit sind geprueft. Widerruf wird vor Cacheantworten geprueft.
Die Audience bezeichnet diese private Dienstidentitaet; mehrere aktive Installationen
duerfen keine geklonten Keys/Registry/Restoreepoche benutzen. Schutz gegen einen
Snapshotrollback oder geklonte aktive Identitaeten bleibt offen.

| Budget | Implementierung / praktischer Umfang |
|---|---|
| Anfrage | 256KiB Body; 2KiB Requestzeile; 16KiB Header; keine Kompression/Transfer-Encoding/Folded Header/ambige Laengen |
| JSON | Tiefe 30; Objektbreite 128; Liste 4096; insgesamt 20000 Knoten inkl. Keys; String 196608 Zeichen; strenges ASCII/JCS-Profil aussen |
| Legacy | Insgesamt 192KiB decodierte Belege; maximal 4096 Capturezeilen; dieselben Strukturgrenzen; originale Legacy-Zahlen/Bytehashes erhalten |
| Zeit | Absolut 5s HTTP; Kind max. 2s und Restbudget; Lock max. 1s; SQLite max. 0,5s; bestehende 60s-Auftrags-/180s-Runnerfrist |
| Prozesse/Parallelitaet | Ein aktiver HTTP-Handler pro Prozess, Backlog 4, maximal ein synchrones Komponentenchild je Operation; ein Timerthread; 16 offene Jobs insgesamt. Prozessuebergreifende Mutationen serialisiert. OS-Scheduling/accept-Backlog ist kein garantierter Antworttermin. |
| Aufnahme/Metadaten | 120 Anfragen/Minute global pro API-Prozess und authentisiertem Mandanten; 32 aktive Challenges/Mandant; 8192 aktuelle Requests, 4096 Jobstatus, 4096 nie wiederverwendete Key-IDs. Voller Speicher ergibt 429, keine Replaypruning-Abkuerzung. Limits laufen beim exakten Retry nicht vor dem sicheren Cachetreffer. |
| CPU/Dateien | CLI: 120 CPU-Sekunden ueber Prozesslebenszeit; Kind: 2 CPU-Sekunden, 64 FDs, keine Corefiles; Kinddateigroesse 0, API-Einzeldateigroesse 32MiB. Echter CPU-Endlosloop im eigenen Child wird durch das OS beendet; HTTP-/Child-Timeout und Freigabe praktisch geprueft. |
| Speicher | Linux-Code setzt 512MiB RLIMIT_AS, hier **nicht live Linux-geprueft**. Der macOS-Host lehnt einen endlichen RLIMIT_DATA ab; es wird dort kein harter RSS-Schutz behauptet. Begrenzte Datenstrukturen sind lokal getestet. Harte RAM-/Swap-/CPUQuota-/Tasks-Grenzen am Ziel bleiben Freigabesperre. |

Rategrenzen sind lokal/prozessgebunden, kein verteilter oder restartfester
DoS-Schutz. Key-ID-Kapazitaet wird nicht durch Keyreuse freigegeben; bei Erreichen
braucht es eine neue kontrollierte Dienstidentitaetsepoche. Fehler/Timeout lassen
keinen positiven Bericht entstehen. Ein abgebrochener Worker wird nicht erneut
ausgefuehrt. Bereits gesendete Bytes koennen nicht zurueckgerufen werden.

## Loeschvertrag und Bedienung

Der [Loeschabschluss](../private-service-retention-20261016/README.md) bleibt
verbindlicher Teil des Ergebnisses: maximal 24h Berichtszugriff ab Fertigstellung,
frueher nach exakter signierter vollstaendiger Empfangsbestaetigung, Sperre vor
Bereinigung, sichtbares und wiederholbares Cleanup bei Fehlern. GET/RST ist kein
Empfang. Eingaben/Pins/Arbeitsdateien verschwinden nach Berichtsabschluss;
Jobkeys werden nicht in Config/DB/Backups kopiert. Replay-/Statusreste enden
weiterhin an ihren begrenzten gespeicherten Fristen. Authregister bleibt getrennt.
Historische States werden nicht still migriert oder geloescht.

Neue synthetische States werden weiterhin **offline** mit `demo.initialize`
erzeugt. Vollstaendige Operatorconfig bleibt privat und wird nicht vom HTTP-CLI
geladen. Projektion einmalig in eine noch nicht vorhandene private Datei:

```sh
PY=/Users/landjunge/agent-authority-lab/.venv/bin/python
$PY -m research.private_service.configuration \
  --operator-config NEUER_STATE/config.json --output NEUER_STATE/api-config.json
$PY -m research.private_service.http \
  --state NEUER_STATE --config NEUER_STATE/api-config.json \
  --signer-key NEUER_STATE/report/ca-private.pem --port 8765
```

CLI-Ausfuehrung vom vorhandenen Worktree, kein neuer Dienst und kein Zugriff auf
historische `.private-service-state`. Client/Empfang verwenden weiter die lokale
Operator-/Clientkonfiguration; niemals im Browser veroeffentlichen. Die obige
lokale Keypfaduebergabe ist ausdruecklich noch **kein** Mehrkonten-/KMS-Betrieb.

Weiter offen: garantierte Dateientfernung waehrend kompletten Ausfalls,
SSD-/RAM-/Swap-/Backuploeschung, Verschluesselung aller kurzlebigen Collector-/VM-
Dateien, Rollback-/Restoreepoche, KMS-Vernichtung aller Keykopien. Kein Loeschziel
des Vorauftrags wird durch diesen Sicherheitsstand abgeschwaecht.

## Tests, Belege und naechster sicherer Schritt

Die ausfuehrbaren Gegenfaelle stehen in
[test_private_service_security.py](../../tests/test_private_service_security.py).
Finale Zahlen/Module/Quellhashes: [summary.json](summary.json).
**377 eindeutige Pruefungen bestanden, keine Fehler oder Skips:** 72 neue
Sicherheitsfaelle, 39 bestehende Dienst-, 30 Loesch-/Aufbewahrungs- und 22 Ledger-
Checks (zusammen 163), danach separat 214 unveraenderte Produkt-/A1–A4-Pruefungen.
Ruff und Formatpruefung bestanden. Der historische v0.2-Kompositionszaehler am
Logende erfasst diese Suiten nicht; massgeblich sind die eindeutigen JUnit-Faelle.
[Vertragstests](contracts-tests.log), [JUnit](contracts-junit.xml),
[Produkt-/A1–A4-Regressionen](regressions-tests.log), [JUnit](regressions-junit.xml).
Mehrfachlaeufe und der absichtlich fehlerhafte alte Adapter zaehlen nicht als
weitere erfolgreiche Wirkungslaeufe. Es gab keinen frischen Linux-/Kernel-/VM-
Wirkungsversuch und keinen Test auf der produktiven KI-Zentrale.
Nachweise enthalten Testkennungen, Ausgangswerte und inhaltsfreie Inventare;
keine neue Rohpayload-/Credential-/Keykopie. [Testbereinigung](test-cleanup.json).
Die acht ausschliesslich diesem Auftrag zugeordneten pytest-Namensraeume sind
nachweislich weg; vier davon hatte pytest zuvor selbst bereinigt. Die restlichen
wurden nach Prozess-/Owner-/Typinventur ohne Symlinkverfolgung entfernt, darunter
52 verbleibende synthetische private PEM-Dateien aus den uebernommenen Regressionen
und zwei exakt erkannte Test-FIFOs. Keine Wiederherstellungskopie absichtlich
kurzlebiger Testkeys/-inhalte, keine Bereinigung historischer Dienststates.
Die [separate Ressourcenmessung](resource-observation.json) bestaetigt lokale
Child-CPU-/FD-/Core-/Dateigrenzen und die verweigerte macOS-Speichergrenze;
sie ist kein zusaetzlicher Wirkungsversuch oder weiterer Testzaehler.

**Naechster sicherer Schritt:** Ein separater nichtproduktiver Linux-Testhost,
weiterhin ohne oeffentliche Route. Dort getrennte API-, Signierer-/Registrar-
und Runnerkonten mit verweigertem gegenseitigem Key-/DB-/Quellarchivzugriff,
minimalem Broker, schreibgeschuetzten Quellen und authentisierten Pipes/Unixsocket
mit Peer-/Jobbindung nachweisen. API mit leerem CapabilityBoundingSet und
AmbientCapabilities, NoNewPrivileges, restriktivem Dateinamespace und ohne BPF-/
Tracing-/SSH-/sudo-Zugriff. Runner isoliert nur fuer den erlaubten synthetischen
Versuch; keine API-gesteuerten Programme/Parameter/Netzziele. Hartes MemoryMax/
MemorySwapMax/CPUQuota/TasksMax, Child-Abbruch, OOM, Neustart/Replay und ausfallfeste
Loeschung inklusive Backups/Restore praktisch abnehmen. Diese Angaben sind
**Betriebsentwurf**, keine installierte oder live bewiesene Zielkonfiguration.

Vor spaeterer Erreichbarkeit zusaetzlich: geeigneter Produktions-HTTP-Server,
TLS mit gepruefter Dienstidentitaet, unabhaengiger Zugangsschutz, globale Rate-/
Verbindungs-/Gesamtzeitgrenzen, explizite Host-/Origin-Regeln. Ein Proxy muesste
den fest erlaubten Upstream-Host setzen; keine freie Vertrauensnahme von
Forwarded-Headern. Keine Payload-/Authorization-/URL-Querylogs, Bodytempfiles,
Proxy-/Error-/Browsercaches oder Backupkopien; dies muss unter Fehler/Last/Abbruch
auch am Proxy nachgewiesen werden. Die lokalen HTTP-Checks beweisen das nicht.
Solange eine relevante dieser Grenzen fehlt, bleibt oeffentliche Freigabe ausgeschlossen.

Primarquellen fuer den Betriebsentwurf, am 17.10.2026 gelesen (kein Installationstest):
[Python http.server](https://docs.python.org/3.12/library/http.server.html),
[systemd.exec – primaere Handbuchquelle](https://github.com/systemd/systemd/blob/main/man/systemd.exec.xml),
[systemd.resource-control – primaere Handbuchquelle](https://github.com/systemd/systemd/blob/main/man/systemd.resource-control.xml),
[nginx HTTP-Grenzen und Bodydateien](https://nginx.org/en/docs/http/ngx_http_core_module.html),
[nginx Rate-Limits](https://nginx.org/en/docs/http/ngx_http_limit_req_module.html).
