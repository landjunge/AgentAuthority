# Agent Authority / Hilfezentrum · Dauerbetrieb 17.10.2026

**Aktiviert und gezielt geprüft:** Der eigene private AA-Dienst läuft dauerhaft
auf Debian. Im öffentlichen Hilfezentrum sind DE/EN-Einstieg, autorisierte
lesende Vorgangsprojektion als Authority Graph und Rückweg veröffentlicht.
Der vollständige getrennte AA-Arbeitsbereich ist als **private synthetische
Vorführung mit eigener Anmeldung** erreichbar. Die reale Kontextübergabe an AA
bleibt gesperrt. Eine reale gemeinsame Anmeldung oder fertige Identitäts-/Daten-
integration ist damit nicht erreicht.

## Tatsächliche Zugangswege

- DE: <https://ki-hilfezentrum.netzwerkpunkt.de/#agent-authority>
- EN: <https://ki-hilfezentrum.netzwerkpunkt.de/en.html#agent-authority>
- Privater AA-Dienst: <https://v2202608211799501333.goodsrv.de/agent-authority/>

Im Hilfezentrum einen vorhandenen Vorgang unter „Meine Fälle“ auswählen. Die
Quelle prüft bestehendes Konto und gespeicherten Owner-/Beteiligtenbezug
serverseitig. Der Graph entsteht im Browser aus vorhandenen IDs, Enumzuständen,
Revisionen und Zeiten; Titel, Freitext, Kontakte und Schlüssel gehören nicht
zum Kontext. Der feste Rückweg führt zur ausgewählten Anzeige, DE oder EN.
Vorhandene synthetische Fallmarkierungen werden sichtbar angezeigt; sie
beweisen keine Konto- oder Agentenidentität.

Der ausdrücklich beschriftete private Vorführlink öffnet AA mit
`#hilfezentrum-demo-de` oder `#hilfezentrum-demo-en`. Er enthält keinen gewählten
Vorgang, Token oder Cookie; `noreferrer`/`no-referrer` verhindern eine
Referrerübergabe. Die getrennten Hosts teilen keine Anmeldung. AA lädt erst nach
eigener Anmeldung und CSRF-Prüfung eine feste synthetische Fixture, keine
Hilfezentrum-Produktivdaten. Der AA-Rückweg führt zum Hilfezentrum-Einstieg.

Der vorhandene Betreiberzugang ist die eingerichtete SSH-Verbindung `netcup`
mit Rootzugriff. Keine benannte reale Betreiberidentität wurde erfunden.
Das synthetische Konto `alice` hat den festen Fixture-Scope; `bob` ist ein
getrenntes leeres Konto für die Eigentümerprobe. Zufällige Passwörter liegen nur
root-lesbar in `/etc/agent-authority-browser/operator-access.json` (0600,
Elternordner 0700). Keine Defaultpasswörter. Dasselbe jeweilige Passwort gilt
für die äußere HTTPS-Basic-Abfrage und anschließend die innere AA-Anmeldung.

Der berechtigte Betreiber kann **selbst im Terminal** das Alice-Passwort ohne
Terminalausgabe in die macOS-Zwischenablage übernehmen. Dieser Geheimnisabruf
wurde nicht in Gesprächs-/Gitbelege ausgegeben:

```sh
AA_LOCK=/Users/landjunge/agent-bridge/queues/gesamtabschluss-20261017T084846Z/with-debian-lock.py
python3 "$AA_LOCK" ssh -o BatchMode=yes netcup cat /etc/agent-authority-browser/operator-access.json |
  python3 -c "import json,sys; print(json.load(sys.stdin)['accounts']['alice'], end='')" |
  pbcopy
```

Danach die private URL öffnen, `alice` an beiden Anmeldepunkten wählen und den
festen Hilfezentrum-Verbindungstest benutzen. Zugangswerte gehören nicht in
URLs, Screenshots, Chat oder Git.

## Installierter Dienst und Sicherheitsgrenzen

| Gegenstand | Aktiver Stand |
| --- | --- |
| Unit | `agent-authority-browser.service`, enabled / active |
| Benutzer | eigener unprivilegierter `aa-browser`, UID/GID 981 |
| Release | `/opt/agent-authority-browser/releases/f512ab6b5716ff097cdf/browser.pyz` |
| Aktiver Link | `/opt/agent-authority-browser/current` auf dieses Release |
| Runtime | eigene `/opt/agent-authority-browser/runtime` |
| State | `/var/lib/agent-authority-browser/data`, 0700 / aa-browser |
| Betriebsprogramme | `/opt/agent-authority-browser/operations`, root |
| Laufzeit | ein synchroner Gunicornworker, ein Thread, lokale SQLite + POSIX-StateLease |
| Dienstgrenze | 256 MiB RAM, Swap 0, 40 % CPU, TasksMax 16 |
| Eigene Slice | `aa-browser.slice`: 800 MiB RAM, Swap 0, 40 % CPU, TasksMax 32 |
| Sicherheitsstop | `/opt/agent-authority-browser/SECURITY-STOP`, persistente Startsperre |

Die Runtime ist eine isolierte Kopie der bereits qualifizierten Gunicorn-23.0.0-
und packaging-25.0-Bytes der Hilfezentrum-Runtime des Releases
`601de6bbd521f0a4e783d394b5d231720c3ea808`. Die 67 Dateihashes wurden erneut
abgeglichen. Keine globale Paketinstallation oder Änderung der Ursprungsruntime.
`/opt/aa-private` und `/opt/ki-helper-runtime` bleiben erhalten.

Verwendet wird der vorhandene Docker-Caddy mit gültigem TLS für den bestehenden
Host. Nur die eigene `/agent-authority/`-Route kam hinzu. Container-ID, übrige
Caddyrouten, Docker-Mounts und vorhandene Elternverzeichnisrechte bleiben erhalten.
Kein Containerneustart, neuer öffentlicher Backendport oder Firewallweg.
Pythonpaket, private Releasequellen, State und Secrets liegen außerhalb des Webroots.

AA bindet ausschließlich den Unix-Socket im eigenen Mount-Namespace
`/run/agent-authority-browser/browser.sock`; dahinter liegt der private Hostpfad
`/opt/4allpass/sites/.aa-transport` (0700). Der vorhandene Schutz von
`/opt/4allpass` (0750/root:root) bleibt bestehen. Caddy überschreibt den privaten
Proxytoken. AA verlangt AF_UNIX und diesen Token. Forwarded-Header begründen
weder TLS, Origin noch Identität. Der Browservertrag erwartet exakt den festen
HTTPS-Origin und unverändert weitergereichten Prefix.

Cookie `aa_session`: `Secure; HttpOnly; SameSite=Strict`,
`Path=/agent-authority/`, MaxAge 1800. API-Origin-/Fetch-Metadata-/CSRF-Prüfungen,
Scopes, Eigentümerfilter, Quoten und StateLease bleiben serverseitig wirksam.
Nur eine oberste GET-Navigation auf die exakte statische Einstiegsseite darf
ohne Origin von der Hilfezentrum-Seite kommen; sie liest keine Sitzung und setzt
kein Cookie. APIs bleiben bei Cross-Site-Zugriff geschlossen.

AA bleibt **single-instance-local-synthetic**. Prozesssitzungen werden bei
Stop/Neustart ungültig. Kein geteilter Mehrserverzustand, echter Collector,
Quellenimport, externer Job oder Fremdaktion. Die bestehenden Hilfezentrum-Limits
wurden nicht geändert: 256 MiB, 50 % CPU, TasksMax 64, Swaplimit `infinity`.
Swap 0 gilt für AA und eigene Prüfrunner, nicht pauschal für Altprodukte/Host.

## Veröffentlichte Produktverbindung und offener Übergabepunkt

Nach Abschluss des Hilfezentrum-Builders wurde dessen tatsächlicher Commit
`2befbe0b131f7262ece8361aa32be9ea31b7296b` im eigenen Integrationsworktree
übernommen. Originalworktree und eingefrorene Grok-Prüfkopien bleiben erhalten.
Vor Übernahme wurden aktuelle Quellen-/Webhashes geprüft. Backend und Frontend
übernahm ausschließlich der koordinierende Builder; keine parallele
Überschreibung laufender Arbeiten.

Backend aktiviert: **17.10.2026 13:39:39 Europe/Berlin**. Alte Worker geordnet
beendet; `/opt/ki-hilfezentrum` zeigt auf die neue private Produktquelle.
Runtime, Units, Umgebung, Originalauthkey und aktuelle Datenbank blieben erhalten.
Keine Schemamigration oder Wiederherstellung alter Nutzerdaten.

Web aktiviert: **13:40:47**, über den vorhandenen zertifikatsgeprüften FTPS-Weg.
Genau fünf Dateien: `authority-workspace.js`, `case-inbox.js`, `api.php`,
`en.html`, `index.html`. Private Relay-/Mail-/Rewritekonfiguration sowie
Besitzer/Gruppen/Rechte davor/danach geprüft; Staging entfernt, Rückfallsicherung
erhalten. Ausführbarer PHP-Relaycode wird nicht als öffentlicher Quelltext angeboten.

- `GET /api/account/authority-context?assignment_id=<vorhandene UUID>` verwendet
  die vorhandene Bearer-/Menschensitzung und prüft Konto, Elternquelle und
  Owner-/Beteiligtenzuordnung in einer konsistenten SQLite-Lesesicht. Anonym 401,
  fremde/fehlende/gelöschte Auswahl 404, zusätzliche/duplizierte Felder 400.
- `POST /api/account/authority-handoff` akzeptiert exakt `assignment_id`, prüft
  Anmeldung, Zuordnung und Browser-CSRF/Origin; anschließend immer
  **503 `authority_identity_contract_missing`**. Keine Übertragung/Speicherung;
  der Arbeitsbereich löst diesen POST nicht automatisch aus.
- AA `/api/hilfezentrum/context` bleibt mit **409** gesperrt.
  `/api/hilfezentrum/demo` akzeptiert nur `{}` und die feste synthetische Fixture
  im freigegebenen Alice-Scope; Bob erhält 404. Keine frei wählbaren Serverpfade,
  URLs oder realen IDs. Quoten und Sessionwiderruf werden nicht umgangen.

Der öffentliche Einstieg und eine autorisierte Hilfezentrum-Quellansicht sind
umgesetzt. Der Übergang des real ausgewählten Vorgangs in den vollständigen
getrennten AA-Arbeitsbereich bleibt offen.

## Gepinnte Quellen und Belege

| Quelle | Fest gepinnter Stand |
| --- | --- |
| AA-Ausgangsbasis | `0794aa53ffe71d502d4ae54f6764062a1ed77f97` |
| Aktive AA-Produktquelle | `27db3a848e9aad30318dd00f7380725b22bd8543` |
| AA-Paket SHA-256 | `f512ab6b5716ff097cdf9978ccd01bc26be6e03732989d747ffa947a3cd1c6f4` |
| AA-Opsfortschritt | `3ef1204`, `a201f07`, `78504e4`, `0a44557`; endgültiger Ops-/Auditpin `a6bc3fc57321f9529c8351a100c39c11f06443b1` |
| Finale AA-Unit SHA-256 | `8d27b1bc83cb8377c63dc508963ea8f904d9b97517df93149a1dbf44fc080db0` |
| Hilfezentrum-Produktquelle | `33c4b508d047a534524a214fc08325e807b07870` |
| Hilfezentrum-Archiv SHA-256 | `cee21a25a93c38259c582fabf7587d45843513b6e671b3e6a0df8aa480c82e4d` · 3.799.040 Bytes / 362 Dateien |
| Hilfezentrum-Transfer-/Aktivierungsops | `f3a9eabc3f6ee87dd53ec428a0b54740afc0cebe` |
| Hilfezentrum-finaler Webrückweg | `338da2a9a2ce090ec27bf60a13d26eb7101afdfd` |
| Hilfezentrum-Abschluss / Belege | `6ac66d7de1c005f8cddb1f243a67ba3bce62445c` |

[source-pins.json](browser-dauerbetrieb-20261017/source-pins.json) pinnt beide
Quellen und die minimalen geheimnisfreien Belege. Opsquelle und aktive
Produktquelle sind getrennt. Auf dem Server sichern `operations/SOURCE.json`
und `EVIDENCE.json` diese Zuordnung. Die frühere Berichtsfassung im Produktpaket
ist historisch; maßgeblich ist dieser lokale Abschluss und seine private
Server-Belegkopie.

| Gezielte Prüfung | Ergebnis / Reichweite |
| --- | --- |
| Neue AA-HTTP-/Kontext-/Ops-Tests | 19 Unittests bestanden; zusätzlich bestehender gezielter CSRF/Host/Origin/Methodentest bestanden |
| [AA-UI](browser-dauerbetrieb-20261017/hilfezentrum-ui.json) | 23 Aussagen bestanden, lokaler echter Browser, feste synthetische DE/EN-Verbindung und Rückweg |
| [AA live](browser-dauerbetrieb-20261017/live-checks.json) | 44 Aussagen bestanden: tatsächliches HTTPS/Proxy/Unix-Socket, Zugangsgrenzen, Cookie, Origin/CSRF, Owner200/Fremd404/anonym401, Scope, Lease, Stop/Start/Restart, Limits, Altdienste |
| [AA Wiederanlauf](browser-dauerbetrieb-20261017/recovery-checks.json) | 7 Aussagen bestanden: Codewechsel auf denselben ersten Pin, persistenter Sicherheitsstop, Startsperre, ausdrückliche Rootfreigabe, Konfiguration-/DB-Erhalt |
| [Startbegrenzung](browser-dauerbetrieb-20261017/start-rate-recovery.json) | ausschließlich eigene neue Unit korrigiert; finaler Unitpin oben |
| Hilfezentrum lokal | 4 API- und 3 isolierte Rückwegtests; 12 DE/EN-Browserpfade mit Fallmarker; 22 echte lokale PHP/cURL-Anfragen; 2 Paketierungstests und 2 gezielte Webrollback-Vorprüfungen bestanden |
| Hilfezentrum öffentlich | 35 Aussagen / 8 HTTPS-Anfragen bestanden: DE/EN, feste private Links, 4 HTTPS-Dateihashes, PHP-Hash privat über FTPS, anonym401, CSRF403, no-store; keine gültigen Credentials, Mail oder erfolgreichen Schreibvorgänge |
| [Finalaudit](browser-dauerbetrieb-20261017/final-audit.json) | aktive Pins/Bytes, einzelner unprivilegierter Worker, Limits, DB-Integrität, erhaltene Altunits/Container und vier Bestandstabellen |

Hilfezentrum-Belege liegen committed unter
`/Users/landjunge/Projects/ki-hilfezentrum/.worktrees/authority-integration-20261017/docs/belege/authority-integration-20261017/`;
Ablauf und Rückwege stehen dort im Worktree in `AUTHORITY-INTEGRATION.md`.
Die Quellen-/Beleghashes sind im AA-Manifest gepinnt. Positive echte Anmeldung
und autorisierte Produktivkontextauswahl wurden öffentlich mangels freigegebenem
Testvorgang **nicht** ausgeführt. Owner-/Participant200, Fremd404 und autorisierter
503-Gate sind auf der isolierten synthetischen Kopie geprüft.

Es gibt noch keinen älteren AA-Produktionsrelease. Die Wiederanlaufprobe belegt
den Stop-/Link-/Startweg auf demselben Pin, keinen Downgrade. Kein Reboot-,
Backup-Restore- oder Datenrollbacktest. `enabled`, Restart=on-failure und
Start-/Stop-/Restartproben belegen den eingerichteten Startmechanismus.
Der Operatorbefehl `rollback-proxy` wurde nicht zusätzlich live ausgeführt;
ein tatsächlicher Caddy-Rückbau erfolgte im geschlossenen Installationsfehlerpfad.
Keine Wiederholung der bereits unabhängig geprüften 46er-/Browser-/Researchserie.
Das frühere Grok-Pass gilt für seinen eingefrorenen Stand, nicht automatisch
für diese neuen Produktcommits.

## Bedienung, Sicherheitsstop und Code-Rückweg

Alle SSH-/Debianaktionen ausschließlich durch den gemeinsamen Exklusivstarter.
Für normale Bedienung jeweils die gewünschte einzelne Aktion ausführen:

```sh
AA_LOCK=/Users/landjunge/agent-bridge/queues/gesamtabschluss-20261017T084846Z/with-debian-lock.py
python3 "$AA_LOCK" ssh netcup systemctl status --no-pager agent-authority-browser.service
python3 "$AA_LOCK" ssh netcup systemctl stop agent-authority-browser.service
python3 "$AA_LOCK" ssh netcup systemctl start agent-authority-browser.service
python3 "$AA_LOCK" ssh netcup systemctl restart agent-authority-browser.service
```

Ein normaler Stop beendet den Dienst, lässt seine Aktivierung für den nächsten
Boot bestehen. Stop/Restart widerruft die inneren Prozesssitzungen. Dauerhafter
Sicherheitsstop:

```sh
python3 "$AA_LOCK" ssh netcup python3 -B /opt/agent-authority-browser/operations/browser_service.py security-stop
```

Dies setzt die persistente Markerdatei und deaktiviert/stoppt nur AA. Manueller
Start oder Codewechsel umgehen diese Markierung nicht. Erst nach Ursachenprüfung
darf Root genau diese Markierung entfernen und `systemctl enable --now
agent-authority-browser.service` über denselben Lock ausführen. Code-Rollback
löscht niemals einen Sicherheitsstop.

Codewechsel auf ein bereits privat vorhandenes, root-eigenes Paket verlangt den
vollständigen SHA-256, aktuell ausschließlich der erste qualifizierte Release:

```sh
python3 "$AA_LOCK" ssh netcup python3 -B /opt/agent-authority-browser/operations/browser_service.py rollback-code f512ab6b5716ff097cdf9978ccd01bc26be6e03732989d747ffa947a3cd1c6f4
```

Stop, atomarer Release-Linkwechsel, Start und Bereitschaftsprüfung. Bei Fehler
wird der vorige Link gestartet; scheitert auch das, bleibt AA sicher gestoppt.
State/DB werden nie zurückgespielt.

`rollback-proxy` im selben Programm prüft aktiven Caddyhash und Originalbackup,
setzt den Sicherheitsstop und entfernt die eigene Route. Bei paralleler
Caddyänderung verweigert es die Überschreibung. Private Serverbackups bleiben
unter `/var/backups/agent-authority-browser/20261017/` und
`/var/backups/ki-hilfezentrum/20261017-authority-integration/` erhalten.

Hilfezentrum-Rückweg im eigenen Integrationsworktree: zuerst
`python3.13 -B ops/authority_web_20261017.py rollback`, dann
`python3.13 -B ops/deploy_authority_20261017.py backend-rollback`.
Der Webweg prüft private Konfiguration **vor** öffentlichen Änderungen und
danach erneut. Backend verlangt den neueren Webrollbackbeleg; SSH erfolgt durch
denselben Exklusivstarter. Aktuelle Nutzerdaten bleiben erhalten.

## Bestandsbefund, Bereinigung und Restentscheidung

Die sechs unterbrochenen Dateien wurden vor Fortsetzung gegen das gesicherte
Manifest geprüft: identisch. Zuvor war keine AA-Browserunit installiert.
Vorhandene Teilpfade wurden geprüft und gezielt weiterverwendet; keine zweite
Unit, doppelten Konten oder parallelen Datenbankschreiber angelegt.

Bei Erstinstallation zwei Rechteprobleme geschlossen behoben: umask-bedingtes
Rootverzeichnis 0700 statt 0750 und der unter geschütztem Elternordner nicht
erreichbare Socket. Teilzustands-/Originalhashprüfungen ermöglichten die genaue
Fortsetzung; jetzt verwendet AA den eigenen Mount-Namespace. Die absichtlich
mehrfachen Neustarts trafen die eigene 120s-Startbegrenzung. Nur die neue AA-Unit
wurde von Burst 3 auf 6 korrigiert und ihr eigener Fehlerstatus zurückgesetzt.
Der historische Erstbeleg `activation.txt` enthält deshalb einen älteren
Unithash; maßgeblich sind Startkorrektur und Finalaudit. Keine Legacyunit wurde
zurückgesetzt. Prüfharnessfehler wurden im Harness korrigiert; CSP und
Produktzugangsgrenzen blieben erhalten.

Beide SQLite-Integritätsprüfungen: `ok`. AA enthält nach Entfernen des temporären
Prüfberichts null Reports. In vier geprüften Hilfezentrum-Tabellen sind alle
ursprünglichen Zeilen aus dem frischen Serverbackup unverändert enthalten:
11 Bots, 2 Anzeigen, 1 Menschenkontakt, 0 Menschensitzungen. Zwischenzeitlich kam
**eine Botzeile hinzu**, aktuell 12. Diese blieb erhalten; keine unbekannte
Akteurszuordnung wurde erfunden. Das ist ein Vergleich dieser vier Tabellen,
kein Gleichheitsbeweis aller DB-Bytes. Die öffentliche Nachprobe führte keinen
solchen Schreibvorgang aus. Die bestehende fehlende Löschledgerbindung bleibt
offen; sie wurde durch die Anbindung nicht hergestellt.

`aa-private-verifier.service` bleibt aktiv. Collectorservice/-socket bleiben
inaktiv. Die bestehende Collectorkonfiguration liegt außerhalb des alten exakten
Sender-/Receiver-Schemas; der boolesche Befund legt keine Pins offen und bestätigt
keine Identität. Der alte Watchdog bleibt `failed`; alte Qualifikations-/Fehler-
einträge wurden nicht pauschal zurückgesetzt. Produktive Auftragssperren,
reale Quellenimporte und Fremdaktionen bleiben geschlossen.

Eigene temporäre HTTP-/PHP-/Browserprozesse und Testdaten sind beendet/entfernt.
Das unbenutzte lokale Hilfezentrum-Testvenv liegt wiederherstellbar im Papierkorb.
Aktive Releases, State, notwendige Serverbackups, Quellen und Reviewartefakte
bleiben erhalten; eigenes Server-Transferstaging ist entfernt. Höchstens ein
eigener Laborrunner und stets gemeinsamer SSH-Lock. Reguläre Runner verwenden
die eigene begrenzte Slice. Eine kurze anfängliche Appfactory-Diagnose lief als
unprivilegierter Benutzer im Lock ohne eigenen Probe-Cgroup.

| Auftragspunkt | Abschlussstatus / nächster Schritt |
| --- | --- |
| Eigener Benutzer/Release/State, Start/Stop/Restart | umgesetzt, aktiviert, eng geprüft |
| HTTPS-/Cookie-/Origin-/Proxygrenzen | vorhandener TLS-Weg genutzt und geprüft |
| Privater synthetischer AA-Betrieb | dauerhaft aktiv mit privaten Zufallscredentials |
| Hilfezentrum-Einstieg, Quellansicht, DE/EN und Rückwege | veröffentlicht und gezielt geprüft; positive reale Anmeldung nicht live getestet |
| Reale Übergabe / gemeinsame Anmeldung | gesperrt; folgender Vertrag fehlt |
| Collector / reale Quellen / Fremdaktionen | unverändert gesperrt |
| Quellen / Belege / Bereinigung | lokal committed, private Serverkopien; kein Push/Merge/Sichtbarkeitswechsel oder Social-Beitrag |

**Kleinste noch benötigte Restantwort:** Welcher autorisierte AA-Aussteller und
welche feste Audience gelten, und wie darf das vorhandene Hilfezentrum-Konto
mit seiner Zuordnungs-ID auf AA `Subject`, `Tenant/Owner`, `Source/Job/Adapter`
abgebildet werden – einschließlich Ablauf, Widerruf und erlaubter Felder/
Speicherung? Ohne diese Zuordnung wird keine reale ID als AA-Berechtigung
übertragen. Hilfezentrum-E-Mailkontrolle genügt nicht als Agentenidentität.
Für echte Quellen bleiben zusätzlich autorisierte Quelle, Verifier/Schlüsselpin
und Aufbewahrung festzulegen; ein Reportdownload erzeugt keinen Vertrauensanker.
