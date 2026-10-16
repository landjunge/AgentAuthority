> Stand 17.10.2026: [Praktische Sicherheitsabnahme und offene Zielgrenzen](private-service-security-20261017/README.md).
> API-Konfiguration jetzt ohne Client-/Runnerkeys, Objekt-Subjects auch vor Cacheantworten,
> feste Routen/Parser-/Zeit-/Prozessgrenzen; Signierer/Verifier als begrenzte Unterprozesse.
> Gleiche Host-UID bleibt eine offene OS-Isolationsgrenze; keine Produktionsfreigabe.
>
> Stand 16.10.2026, Ergaenzung Aufbewahrung v1.1: Gilt fuer neue kurzlebige Teststates.
> Historische States/Belege werden nicht migriert oder geloescht.
> Neuer VM-Dispatch ist bis zur Speicherqualifikation gesperrt; die API und
> Berichtspruefung sind praktisch qualifiziert. [Nachweis und Grenzen](private-service-retention-20261016/README.md).

# Privater Testdienst: Schnittstellenvertrag v1

Fortsetzung des Dienstauftrags `20261016T205615.209078Z`, Nutzerergänzung vom
16.10.2026 einschließlich bestätigter Umsetzung. Reviewstand auf
`codex/hosted-qualification-20261016`, Basis `edd40b9`. Der vorhandene
[Abschluss und Plan](HOSTED-SERVICE-ASSESSMENT-20261016.md) gilt mit den hier
konkretisierten Integrationsstufen. Historische Forschungsquellen bleiben erhalten.

## Zweck und Grenze

Ausführbarer lokaler Testdienst für genau `a4-write16-v1`: zwei vom eigenen
Registrar kontrollierte Linux-Testprozesse, signierte Übergabe und Annahme,
ein unabhängig beobachteter synchroner VFS-Write von 16 Bytes an einem frischen
künstlichen Dateiobjekt. Die API-Auftraggeber sind registrierte Testschlüssel;
sie sind **nicht identisch mit den je Lauf frisch gestarteten Linux-Prozessen**.
Deren vorhandene A2/A4-Besitz-/SCM_CREDENTIALS-/pidfd-/Start-/Exec-/Boot-/Namespace-
Bindung wird gesondert geprüft. Die A4-Delegation bindet die Digests des exakten
API-Auftrags **und** seiner exakten API-Annahme. Dies erklärt die Verbindung
zwischen Dienstanforderung und beobachtetem Testprozess, ohne einen Browserkey
zur Prozess- oder Provideridentität umzudeuten.

Agent Authority prüft Beobachtungen und Delegationsbelege. Es entscheidet keine
Rechte, Budgets, Freigaben oder Stopps. `grants_rights=false` ist durchgängig.
Ressourcenzugriffsschutz schützt allein diesen Testdienst. Die fest installierte
Testaktion wird vom getrennten Versuchskoordinator ausgelöst. Eine geprüfte
Delegation erteilt keine Rechte. Es gibt keine Kundenprogramme, Shell-/Code-/URL-
oder frei wählbare Dateipfadparameter. Kein Produkt-VPS-Zugriff oder Deployment.

## HTTP, Authentisierung und Parser

Implementierung: `python -m research.private_service.http --state DIR --config
DIR/config.json --port 8765`. Ausschließlich `127.0.0.1`; kein konfigurierbarer
öffentlicher Bindhost. Browserinspektor unter `/`, Status/Bericht per gleicher API.
Der Browser hält den explizit eingegebenen Token nur im Eingabefeld, ohne Cookies,
LocalStorage oder URL-Parameter. Ausgaben über `textContent`, CSP ohne Inlinecode,
keine fremden Skripte. Botclients verwenden dieselben JSON-Routen.

Alle Datenrouten brauchen `Authorization: Bearer <zufälliger 256-bit-Testtoken>`.
Die private 0600-Operator-Konfiguration ordnet Tokens **außerhalb der Anfragen**
Mandant und Rolle zu. Kein JWT-Claim oder freies JSON legt diesen Kontext fest.
Rollen: `admin` Enrollment/Widerruf und Mandantenaufträge; `client` Auftrag/Annahme
und Abruf; `reader` ausschließlich Abruf; `runner` ausschließlich Nachweisaufnahme.
Jeder Mandant besitzt seine Dienstobjekte gemeinsam; v1 hat keine weiteren
Benutzerunterteilungen. IDs allein gewähren keinen Zugang. Alle DB-Lookups und
Unique-Schlüssel tragen den authentisierten Mandanten. Fremde Objekt-IDs ergeben
wie nicht vorhandene IDs `404 NOT_FOUND`, ohne Metadaten des fremden Objekts.

Der Server akzeptiert nur seinen exakten `Host: 127.0.0.1:PORT`. Ein vorhandener
`Origin` muss exakt `http://127.0.0.1:PORT` sein. Kein CORS, keine Umleitungen.
Alle Antworten `Cache-Control: no-store`, `nosniff`; keine HTTP-Zugriffslogs.
POST: `Content-Type: application/json`, genau eine positive Content-Length,
höchstens 262144 Bytes, kein Transfer-Encoding, Socketzeitlimit 5s.
Eine einzelne HTTP-Schleife begrenzt lokale Parallelität; das ist kein Internet-
Rate-Limit oder Schutz vor einem Angreifer im selben Betriebssystemkonto.
Falsche Methode auf einer Route wird nicht als Mutation interpretiert.
Nicht unterstützte HTTP-Verben werden vom Standardserver mit 501 beantwortet.

## Version und Signaturen

Neue JSON-Objekte tragen `schema=aa-private-v1`; [OpenAPI 3.1](PRIVATE-SERVICE-OPENAPI-v1.json) beschreibt die maschinenlesbaren Felder. Berichte `aa-report-v1`,
Nachweismanifeste `aa-evidence-v1`. Unbekannte Pflicht-/Fremdfelder in
den definierten neuen Eingabeschemata werden abgewiesen. Keine stille
Versionsverhandlung; neue inkompatible Formate benötigen neue Versionskennung.

Neue signierte Objekte verwenden das vorhandene A2-Envelope
`{"body":{...},"signature":"BASE64"}`. Ed25519 nach
[RFC 8032](https://www.rfc-editor.org/rfc/rfc8032), Publickey 32 Bytes,
Signatur 64 Bytes, Standard-Base64 mit Padding. Signiert werden **alle** Felder
von `body`, keine HTTP-Header und kein ungesichertes Teilfeld. SHA-256-Digests
referenzieren stets das vollständige kanonische Envelope einschließlich Signatur.

Kanonisierung: [RFC 8785 JCS](https://www.rfc-editor.org/rfc/rfc8785), mit bewusst
enger v1-Wertemenge: druckbare ASCII-Strings U+0020..U+007E (auch Propertynamen),
Integer mit Betrag <= 2^53-1, Boolean, Null, Arrays und Objekte; keine Fließzahlen,
Steuerzeichen, Unicode-Strings oder doppelten Propertynamen. Maximal 30 Ebenen.
Für diese Teilmenge erzeugt der vorhandene A2-Serializer (`sort_keys=True`,
`separators=(',',':')`, `ensure_ascii=True`, UTF-8 ohne BOM) genau JCS-Bytes.
Diese Beschränkung behauptet **keinen allgemeinen JCS-Serializer** für beliebige
Unicode-/Float-Eingaben. Format-/Duplicate-Key-Prüfung erfolgt vor Signaturprüfung.
`-0` wird als Integer 0 kanonisiert. Reihenfolge von Arrays bleibt relevant.

Historische A4-Objekte behalten ihren unveränderten A4-Serializer und Domains.
Sie werden als Standard-Base64 der **exakten Originaldateibytes** übertragen:
Registry-JSON, Capture-JSONL und Trial-JSON. Ihre Manifestdigests sind SHA-256
der dekodierten Originalbytes. Dadurch werden alte Mess-Fließzahlen oder
mehrzeilige Diagnosen nicht neu kanonisiert. Die neuen Envelopes signieren die
exakten Base64-Strings und das Manifest. Der Original-A4-Verifier prüft die
inneren Signaturen nach dem historischen Vertrag. Keine neue Kryptokonstruktion.

### Gemeinsamer signierter Requestbody

Alle Felder sind Pflicht, einschließlich `payload`:

| Feld | Typ / Regel |
|---|---|
| schema / domain | `aa-private-v1` / `AA-REQUEST-v1` |
| tenant | exakt authentisierter Mandant |
| audience | exakt `aa-private-local-v1`, keine Zielhost-Normalisierung |
| method / path | exakt `POST` und tatsächlich aufgerufener Pfad, ohne Query/Slashalias |
| kid | registrierte Key-ID, `[A-Za-z0-9_-]{1,80}` |
| nonce | 32 zufällige Bytes als 64 kleine Hexzeichen |
| idempotency_key | `[A-Za-z0-9_-]{1,80}`, mandantenweit über alle POST-Routen eindeutig |
| issued_ms / expires_ms | Integer UTC-Unixmillisekunden, `issued<=now<expires<=issued+60000` |
| payload | unten definierter Vorgangsinhalt |

Null Uhrtoleranz. Operator-/Clientuhr müssen stimmen. Der Dienst prüft Frische
unter der DB-Schreibsperre erneut, ebenso aktiven Schlüssel und Enrollmentzeit.
Eine Requestausgabe vor dem Enrollmentzeitpunkt ist unzulässig. Eine Anmeldung
ist höchstens 24h gültig; Aufnahmefenster höchstens 60s. Nach einem erfolgreichen
Dispatch endet das API-Auftragsfenster; die interne konkrete A4-Delegation hat
eigenständig exakt 5s monotone Gültigkeit und bindet Boot/Namespace/Objekt/Instanzen.
Nachweise müssen innerhalb 180s nach Dispatch frisch signiert aufgenommen werden.

## Vorgänge

| Methode / Pfad | Rolle, Eingabe | Ergebnis und Semantik |
|---|---|---|
| POST `/v1/challenges` | admin; unsigniertes JSON unten | 201; genau eine frische Besitzprobe, **keine Registrierung** |
| POST `/v1/enrollments` | admin; neuer Key signiert Request, separat gepinntes Root signiert Zertifikat, neuer Key signiert Probe | 201 registered; nur kontrollierte Testidentität |
| POST `/v1/revocations` | admin; Request eines aktiven registrierten Keys; payload `{kid}` | 200 revoked; atomarer Widerruf plus offene Läufe markieren |
| POST `/v1/jobs` | client/admin; actor-Key; payload `{scenario:"a4-write16-v1",receiver_kid}` | 202 awaiting_acceptance; **noch keine Ausführung**, URLs und exakter Auftragsdigest |
| POST `/v1/jobs/{id}/acceptances` | client/admin; exakt receiver-Key; payload `{job_id,job_sha256}` | 202 queued; exakte Annahme, **kein Wirkungsbeweis** |
| POST `/v1/jobs/{id}/evidence` | runner-Token **und** registrierter runner-Key des vorab gespeicherten Dispatchpins; unten | 201 completed; atomar gespeicherter dienstsignierter Prüfbericht, unabhängig vom positiven/negativen Befund |
| GET `/v1/jobs/{id}` | client/admin/reader, authentisierter Objektmandant | 200 aktueller menschenlesbarer Zustand; kein erneuter Vollzug |
| GET `/v1/jobs/{id}/report` | client/admin/reader, authentisierter Objektmandant | 200 historisches signiertes Envelope plus heutiger Schlüsselstatus; 409 solange kein Bericht |

Challenge-Pflichtfelder: `schema,kid,public_key,idempotency_key,nonce,issued_ms,
expires_ms`. Identifikatoren/Nonce/Zeit wie oben, Publickey Standard-Base64.
Mandant und Methode/Pfad stammen aus dem admin-authentisierten festen Kontrollweg;
dieser erste Challengewunsch besitzt keine Signatur. Die spätere PoP signiert
die **exakte** Antwort: `schema,domain=AA-POP-v1,tenant,audience,challenge_id,kid,
public_key,expires_ms`. Die 256-bit-Zufallsprobe ist mandanten-/key-/zeitgebunden,
einmalig verbrauchbar und mit Enrollment/Idempotenz in einer Transaktion verbraucht.
Anfrage-/Antwortwiederholung ohne Änderung ist auch hier dauerhaft idempotent.

Enrollmentpayload hat **genau** `certificate,proof,replaces`. `replaces=null`
bei Erstregistrierung; sonst vorherige aktive Key-ID. Certificate ist ein Envelope
mit exakt `schema,domain=AA-ENROLL-v1,tenant,audience,kid,public_key,role,issued_ms,
expires_ms`; role `actor|runner`. **Nur** der pro Mandant außerhalb der API gepinnte
Rootpublickey verifiziert das Zertifikat. Ein hochgeladenes CA-Feld ist unzulässig.
Die Probe ist das vom neuen Key signierte exakte Challengeantwortobjekt.
Der äußere Request wird ebenfalls vom neuen Key signiert. Die neue ID darf auch
nach Widerruf nie wieder verwendet werden. Neue ID, Zertifikat, Probe, Audit und
Widerruf des alten Keys werden gemeinsam committed; ein Fehler rollt alles zurück.
Die neue Key-ID darf denselben Publickey tragen, was als Identitätsrotation ohne
kryptografischen Keywechsel zu verstehen ist; echte Keyrotation verwendet neues
Schlüsselmaterial. Rootwechsel erfolgt ausschließlich operatorseitig mit neuer
Katalogversion; kein Rootwechsel durch Upload, kein Root-Rollback-Recovery implementiert.

Die Annahme referenziert `SHA256(JCS(vollständiger Auftragsrequest))`, nicht nur
dessen frei beschriebene Aktion. Sender und Empfänger müssen unterschiedliche
registrierte actor-IDs desselben Mandanten sein. Der Senderkey wird auch bei
Annahme erneut auf Gültigkeit geprüft. Eine zweite andere Annahme für denselben
Auftrag wird als Zustandskonflikt zurückgewiesen.

### Beobachtungsaufnahme und Trustklassen

Payloadpflichtfelder `manifest,registry,capture,trial`. Die letzten drei sind
Base64 der exakten Originalbytes; bei bewusst fehlender Quelle `null`. Manifest:
`schema,source_id,source_class,run_id,registry_sha256,capture_sha256,trial_sha256,
complete`. `complete` ist Boolean. Fehlende Quelle hat Digest SHA-256 der leeren
Bytes. Der Dienst prüft die vorhandenen Bytes trotz eines Vollständigkeitsclaims;
`complete=true` allein belegt nichts. Kein Streaming/halbfertiger Snapshot.

`source_id` ist registrierter Runnerkey, `source_class` muss exakt
`controlled-linux-collector` sein und mit dem vertrauenswürdig vor Ausführung
gespeicherten Dispatchkontext übereinstimmen. Run-ID, CA-Pin und Quellhashes
stammen **aus der Operatorvorbereitung vor der Ausführung**, nie aus Uploadclaims.
Nur dieser konkrete Runner darf das konkrete laufende Objekt schließen.
Registry, Besitzproben und Transportzeuge sind eine Quelle; VFS-/Lifecycle-
Kernelbeobachtung ist eine getrennte Quelle unter demselben kontrollierten Host-
Trustmodell. Dies ist kein unabhängiger externer Auditor und schützt nicht vor
einem kompromittierten Hostroot/Kernel. `customer-asserted` oder `untrusted-upload`
werden in diesem ausführbaren Profil nicht aufgenommen (`403`); sie würden
höchstens Claimprüfung erlauben, niemals unabhängige Wirkung. Kein freier Upload
führt auf einen privilegierten Collector oder akzeptiert eine neue CA.

Der neue Adapter übernimmt die 26 vorhandenen A4-Checks und 23 Verlustfelder.
Zusätzlich: genau ein Ready-/Summaryrecord und exakte `service_binding` in der
signierten A4-Jobstruktur: `{tenant,job_id,job_sha256,acceptance_sha256}`.
Perfbuffer-Reihenfolge über CPUs ist kein Kausalitätsbeleg: Der Adapter sortiert
eine Prüfkopy der Lifecycle-Records nach dem vorhandenen monotonen Kernelstamp,
löscht keine Duplikate und verändert keine archivierten Rohdaten. Die ursprüngliche
A4-Auswertung bleibt zusätzlich erhalten. Fehlende/gleiche/falsche Ereignisse
werden durch die vorhandenen Instanz-/Zeit-/Sequenzchecks nicht passend gemacht.

### Frische, Idempotenz und Neustart

Alle erfolgreichen Mutationen verwenden SQLite-WAL, `synchronous=FULL` und
`BEGIN IMMEDIATE`. `(tenant,idempotency_key)` und `(tenant,nonce)` sind eindeutig;
Zustandsänderung, Requestdigest und exakte HTTP-Status-/Antwortdaten committen
zusammen. Dasselbe Envelope im gültigen Zeitfenster ergibt exakt dieselbe
Aufnahmeantwort; ein anderer Inhalt unter gleicher ID `409 IDEMPOTENCY_CONFLICT`;
gleiche Nonce unter neuer ID `409 REPLAY`. Das gilt über API-/Workerprozesse und
Neustarts. Eine wiederholte Auftragserstellung liefert ihre ursprüngliche
202-Antwort; den **aktuellen** Zustand liefert GET. Ein Retry löst nie einen
zweiten Testlauf aus. Fehlerhafte Requests werden nicht als Erfolg reserviert.

Auth/Rolle, Ziel, Frische, Signatur und aktueller Keyzustand werden **vor**
Cachewiederholung geprüft. Deshalb wird ein abgelaufener oder widerrufener Request
auch bei bereits vorhandenem Erfolg nicht erneut als frisch aufgenommen; GET
bleibt für berechtigte aktuelle Tokens möglich. Nach Timeout: exakt denselben
Request wiederholen oder GET, niemals neue ID in der Annahme, der alte sei
fehlgeschlagen. Die Challenge-Anfrage nutzt dieselbe atomare Tabelle, ohne Signatur.

Der Worker hält zusätzlich einen hostweiten nichtblockierenden `flock` für die
gemeinsame Forschungs-VM. Vor Ausführung speichert er `running` dauerhaft und
vor dem Versuch die unabhängigen Trustpins. Beim nächsten Workerstart unter
derselben Sperre werden verbliebene `running`-Läufe als UNBEKANNT abgeschlossen;
kein erneuter Dispatch. Eine DB-Transaktion garantiert **keinen** Exactly-once-
Vollzug über Datenbank, SSH und Prozess. Zwischen Commit und tatsächlichem Start
kann ein unklarer Abbruch liegen; auch dann kein automatischer zweiter Write.
Ein frischer absichtlich neuer Versuch hat neue IDs/Keys/Objekte. Ein API-Neustart
führt keine Worker-Recovery aus und kann einen aktiven Worker nicht umklassifizieren.

Widerruf/Rotation vor Dispatch verhindert neuen Dispatch. Nach dessen dauerhafter
Beanspruchung kann eine Aktion bereits begonnen haben; Widerruf kann sie nicht
rückgängig machen. Offene betroffene Aufträge werden atomar UNBEKANNT, späte
Nachweise liefern Zustandskonflikt und erzeugen keinen positiven Gesamtbefund.
Abgeschlossene signierte Berichte bleiben bytegleich; GET zeigt getrennt den
heutigen Widerruf. Ein unbekannter Kompromissbeginn erlaubt keine pauschale
historische Sicherheitsbehauptung. Bearertoken werden operatorseitig ersetzt;
Tokenwiderruf ist von Agentenkeywiderruf getrennt.

## Zustände, Bericht und Fehler

Verarbeitung und Befund sind getrennt:

| Maschinenzustand | Oberfläche / Bedeutung |
|---|---|
| awaiting_acceptance | Annahme ausstehend; kein Test gestartet |
| queued | Wartet auf Testlauf; frische Annahme gespeichert |
| running | Testlauf wird beobachtet; Ausgang noch offen |
| completed | Prüfbericht verfügbar; kann positiv, widersprüchlich, unvollständig oder unbekannt sein |
| unknown | Testlauf unklar; keine automatische Wiederholung; konservativer signierter Bericht |

`GET` ist sicher wiederholbar; Polling frühestens nach 1s, nach 30s mit 5s Abstand,
lokal höchstens ein Poll je Oberfläche gleichzeitig. POST 202 ist nur Aufnahme,
kein Erfolg einer Aktion. Ein eingereichtes geschlossenes Paket ergibt synchron
201; das bedeutet ausschließlich „Prüfbericht dauerhaft gespeichert“. Zusätzliche
Queue-/Callback-/Pushdienste sind dafür unnötig. Worker einmalig explizit starten.
Ein wartender Auftrag wird nach 60s ab dauerhaftem created-Zeitpunkt als unklar
abgeschlossen; ein laufender nach 180s ab dauerhaftem dispatched-Zeitpunkt.
API-Idlewartung (nominal 0,5s), jeder Zugriff und Neustart pruefen dies. Kein Redispatch.

Bericht: Envelope des getrennten Dienstreportkeys (Operator verteilt dessen
Publickey außerhalb des Ergebnisdownloads). Body benennt Domain/Audience,
Signier-Key-ID, Mandant/Job, Prüfumfang `controlled-a4-write16`, Auftrags- und
Annahmedigest, Prüfer- und Trustkatalogversion, Quellenklasse/Run/Quellpins,
Einzelchecks, Verlustwerte, Gründe und Unsicherheiten. Der normale vollständige
Bericht zeigt getrennte Ebenen `request_signature`, `exact_service_acceptance`,
`controlled_process_and_delegation`, `independent_write`. Bei nicht gestarteten
oder abgebrochenen Läufen existiert ein kleinerer signierter Unknownbericht mit
konkretem Grund; fehlende Quellen werden dadurch nicht vorgetäuscht.
Das JSON-Außenobjekt von GET enthält zusätzlich den **aktuellen**, nicht durch
die historische Berichtsignatur gedeckten Schlüsselstatus. Der historische
Reportbody bleibt nach Widerruf unverändert. Vor Berichtvertrauen Signatur
gegen separat gepinnten Reportkey prüfen. Reportkeyrotation/KMS sind noch offen.

| Klassifikation | Anzeige / präzise Aussage |
|---|---|
| BELEGT | Alle konkreten Checks und gemessenen Verlustwerte tragen diese begrenzte Kette unter den benannten Trustannahmen. |
| WIDERSPRUECHLICH | Widersprüchlich: vorliegende Signatur-/Digest-/Instanz-/Quell-/Sequenzprüfung scheitert; keine Absichtsbehauptung. |
| UNVOLLSTAENDIG | Unvollständig: erwartete Quelle oder strukturelles Kettenglied fehlt. |
| UNBEKANNT | Unbekannt: Verlust-/Trust-/Betriebsgrenze verhindert die Aussage; eine nicht nachgewiesene Wirkung ist kein Beweis für Wirkungsfreiheit. |

Die ASCII-Maschinenwerte werden im Browser als JSON sichtbar; Zustandslabels
sind verständlich. `provider_model_session=UNBEKANNT` bleibt immer erhalten.
Die Signatur beweist die Integrität des Berichts unter dem Reportkey. Sie ist
**kein universelles Sicherheitszertifikat, keine Providerbeglaubigung und kein
eigenständiger Wirkungsbeweis**. Auch BELEGT betrifft nur die benannte Testaktion.

Fehler sind minimierte [RFC-9457-Problemobjekte](https://www.rfc-editor.org/rfc/rfc9457):
`type:"urn:aa:problem:<code-klein>",title:<code>,status:<HTTP>,code:<code>`.
Kein freier Stacktrace, Dateipfad, Requestecho oder fremde Objektkennung.

| HTTP | Codes (wesentliche vollständige Gruppen) | Wiederholung / Ergebnis |
|---|---|---|
| 400 | INVALID_JSON, DUPLICATE_JSON_KEY, TRANSFER_ENCODING_UNSUPPORTED, TRUNCATED_BODY | Eingabe korrigieren; kein erfolgreicher Request reserviert |
| 401 | AUTH_REQUIRED, KEY_UNKNOWN, SIGNATURE_INVALID, TRUST_PIN_INVALID, POP_INVALID | Zugang/Signer prüfen; mitgebrachte Root wird nicht akzeptiert |
| 403 | ROLE_FORBIDDEN, TENANT_MISMATCH, KEY_REVOKED, OBJECT_FORBIDDEN, SOURCE_FORBIDDEN, HOST_FORBIDDEN, ORIGIN_FORBIDDEN | keine neue Aufnahme; nicht mit neuem Nonce umgehen |
| 404 | NOT_FOUND | Objekt im authentisierten Mandanten nicht verfügbar |
| 409 | REPLAY, IDEMPOTENCY_CONFLICT, CHALLENGE_USED_OR_EXPIRED, KEY_ID_REUSED, STATE_CONFLICT, REPORT_PENDING, DISPATCH_PIN_MISSING | Poll bei REPORT_PENDING; sonst Kontext klären; kein neuer Vollzug durch Retry |
| 410 | EXPIRED_OR_FUTURE, KEY_EXPIRED, EVIDENCE_WINDOW_EXPIRED | nicht erneut als frisch aufnehmen; historischen Bericht per GET abrufen |
| 411 / 413 / 415 | LENGTH_REQUIRED / BODY_LIMIT / CONTENT_TYPE | Transport korrigieren |
| 422 | INVALID_FORMAT, INVALID_PUBLIC_KEY, TARGET_MISMATCH, SCENARIO_UNSUPPORTED, DELEGATION_MISMATCH, ROTATION_ROLE_MISMATCH, EVIDENCE_TARGET_MISMATCH, EVIDENCE_DIGEST_MISMATCH, EVIDENCE_ENCODING_INVALID | ungültiger neuer Vertrag, kein positiver Befund |
| 429 | CHALLENGE_LIMIT, QUEUE_FULL | höchstens 32 aktive Challenges pro Mandant, höchstens 16 offene Jobs auf lokalem Knoten |
| 500 / 503 | INTERNAL_ERROR / SERVICE_UNAVAILABLE, SCHEMA_UNSUPPORTED | Ausgang bei Antwortverlust unklar; gleicher Request oder GET, kein neuer Auftrag auf Verdacht |

Der lokal gestartete Worker kann `RUNNER_BUSY` (409) melden. Er startet dann
keinen weiteren Versuch. VM-/Kernel-/Probevoraussetzung fehlt: konkrete lokale
Fehlermeldung, Job bleibt vor Claim wartend; keine Installation auf fremden Hosts.

## Datensparsamkeit und Betriebsgrenzen

Der Dienst nimmt nur feste synthetische Szenarien und begrenzte Nachweispakete an:
Test-/Mandanten-/Keykennungen, Publickeys/Signaturen, Prozessinstanz-/Write- und
Verlustnachweise. Zweck ist ausschliesslich die Pruefung dieses konkreten Tests.
Keine freien Prompts, Kundendateien oder Clientpfade als Dateiziele. Vor Einreichung
stehen DE/EN-Hinweise ohne Authentisierung auf `/` und `GET /v1/privacy` bereit,
einschliesslich der unten genannten Betriebsgrenzen.

### Feste Frist und vollstaendige Empfangsbestaetigung

`completed_at` ist der beim Abschluss gespeicherte UTC-Zeitpunkt; `expires_at =
completed_at + 86400s`. Beide stehen im signierten Bericht und im API-Ergebnis.
Ein Neustart, GET, Retry oder eine fehlgeschlagene Bereinigung verschiebt sie nie.
Bei `now >= expires_at` ist kein neuer Berichtszugriff zulaessig (`410 REPORT_GONE`).
Nicht abgeschlossene Jobs haben noch kein expires_at; sie werden nach den obigen
60-/180s-Grenzen konservativ abgeschlossen und erhalten dann ihre feste Berichtsfrist.
Ein persistent gespeicherter maximal beobachteter UTC-Zeitstand verhindert ein
Wiederaufleben abgelaufener Requests nach einer Rueckstellung der Systemuhr.
Eine vertrauenswuerdige Uhr und unveraenderter Datentraeger bleiben Voraussetzungen;
ein Snapshotrollback wird dadurch nicht erkannt.

`POST /v1/jobs/{id}/receipts` verwendet dasselbe vollstaendige signierte
Requestenvelope, die gleichen Frische-/Rollen-/Mandantregeln und den exakten Pfad.
Zulaessig sind client/admin-Token plus derzeit gueltiger Originalsender- oder
Originalempfaengerkey des Objekts. Payload, ohne zusaetzliche Felder:

```json
{"job_id":"<server-generated-id>","report_version":"1","report_sha256":"<SHA256(JCS(report-envelope))>","received_complete":true}
```

Die Signatur bindet Mandant, Auftrag, Version, vollstaendigen Berichtsdigest und
die ausdrueckliche Aussage des Clients, alle Bytes empfangen zu haben. Sie ist
kein serverseitiger Beweis, dass der Client die Bytes gelesen/verstaendlich gefunden
hat. Weder GET, Transporterfolg noch Downloadbeginn gelten als Bestaetigung.
Die Server-API vertraut fuer diese Aussage dem berechtigten signierenden Client.
Der lokale CLI-Weg `receive --output DATEI` speichert erst eine neue 0600-Datei
vollstaendig, prueft die Reportkeysignatur und fsynct sie; er bestaetigt noch nichts.
`confirm --report-file DATEI` prueft Signatur/Mandant/Job erneut und bestaetigt erst
danach. Eine lokale Empfaengerkopie gehoert anschliessend zum Empfaenger, nicht
zu den kurzlebigen Dienstdateien. Browser-GET bestaetigt nichts; private Signierkeys
werden nicht in Browserstorage abgelegt.

Gueltige Bestaetigung sperrt Berichtszugriff und entfernt die Inhaltsreferenz in
einer SQLite-Transaktion. Erst danach erfolgen Dateibereinigung und WAL-Pruefung.
HTTP 200 bestaetigt den Empfang; **nur** `cleanup_confirmed=true` und ein konkretes
`cleanup_completed_at` bestaetigen die unten abgegrenzte Bereinigung. Fehlerhafte
Signatur `401`, falsches Objekt/Key `403`/`404`, falscher Digest/Version/kein voller
Empfang `422 RECEIPT_MISMATCH`, nach Ablauf `410 REPORT_GONE`. Exakter Retry im
gueltigen Requestfenster sowie neu signierte gleiche Bestaetigung sind sicher.
Die Bestaetigungsantwort liefert immer den aktuellen Bereinigungszustand statt
einen alten Erfolgswert aus dem Idempotenzcache. Ein Timeout kann deshalb ohne
neuen Auftrag durch erneute Bestaetigung oder Statusabruf geklaert werden.

`POST /v1/jobs/{id}/cancellations` hat Payload `{job_id}`, dieselben Objektkeys und
client/admin-Rollen. Fuer offene Jobs entsteht ein signierter UNBEKANNT-Bericht;
keine automatische Wiederholung. Eine moeglicherweise bereits begonnene Aktion
kann nicht zurueckgenommen werden. Der neue VM-Dispatch ist derzeit gesperrt.

### Speicher, Bereinigung und nachpruefbarer Zustand

Neue States verwenden internes Speicherschema 2 (keine automatische Altschemamigration):
0700-Verzeichnisse, 0600-Dateien. Generierte Auftragspfade
`STATE/jobs/SHA256(tenant)/server-id/`, keine Dateizielwahl durch Upload.
Auftrag, Annahme, Dispatchpins und Bericht sind mittels installiertem OpenSSL-3
EVP AES-256-GCM verschluesselt (zufaelliger 96-Bit-Nonce, 128-Bit-Tag, eigener
256-Bit-Auftragsschluessel; [OpenSSL-EVP](https://docs.openssl.org/3.0/man3/EVP_EncryptInit/)). Mandant/Job/Feld sind authentisierte Zusatzdaten.
Der einzige dauerhafte Auftragsschluessel liegt in `content.key` des Auftrags,
nicht in SQLite/WAL/Config/Keysicherung. Es existiert keine App-Backuproutine.
Ed25519-Envelopes und A4-Pruefregeln bleiben gleich; der private Dienst signiert
und verifiziert nun mit EVP im Speicher, ohne Message-/Signaturtempfiles.
Die historischen Forschungsmodule und archivierten Belege werden nicht veraendert.

Bei Abschluss/Fehler/Abbruch verfallen gespeicherte Eingabeenvelopes und Pins sofort;
die API persistiert keine hochgeladenen Rohpakete. Eigene verschluesselte
Zwischenstaende unter `job/scratch` werden entfernt. Orphan-Key-/Arbeitsverzeichnisse
nach Abbruch vor DB-Commit werden unter der gleichen Prozesssperre nachgeholt.
Bei Empfang/Ablauf werden zusaetzlich der Bericht und das ganze Auftragverzeichnis
inklusive Auftragsschluessel entfernt. SQLite `secure_delete=ON`,
`temp_store=MEMORY`, `synchronous=FULL`, WAL-Checkpoint mit `TRUNCATE` und
anschliessende Pfadpruefung gehoeren zur Bestaetigung. Eine blockierte WAL-Lesekopie
oder fehlgeschlagener unlink/rmdir laesst `cleanup_state=failed` stehen; der Zugriff
bleibt gesperrt. Idlewartung, naechster Zugriff und Neustart versuchen erneut.
Ein Dateibereinigungsfehler kann daher eine laengere, explizit ausgewiesene
Aufbewahrung verschluesselter Restdateien verursachen, niemals einen stillen Erfolg.

Status- und Berichtsantworten enthalten:

| Feld | Bedeutung |
|---|---|
| completed_at / expires_at | Konkrete absolute Frist, vor Fertigstellung null |
| report_version / report_sha256 | Bindung an exaktes signiertes Berichtsenvelope |
| receipt_state / received_at | unconfirmed oder confirmed, Zeitpunkt |
| access_state | pending, available oder blocked |
| deletion_reason | receipt oder expired, sonst null |
| cleanup_state | not_due, inputs_pending/inputs_failed, pending/failed oder complete |
| inputs_cleanup_completed_at | Bestaetigtes Ende eigener Eingabedateien und aktiver DB-/WAL-Kopien |
| content_key_state | present oder absent_from_owned_namespace; kein Nachweis gegen alte Backups/SSD-Reste |
| cleanup_confirmed / cleanup_completed_at | Tatsaechlich nachgepruefte Dienstdatei-/SQLite-Namespacebereinigung |
| cleanup_scope | Explizite Abgrenzung gegen physische SSD-/RAM-/Backuploeschung |
| residual_expires_at | Konkretes Ende des inhaltsfreien Job-/Loeschstatus |

Ein dateiuebergreifender `flock` plus lokale Threadsperre serialisieren
Reportmaterialisierung/-Versand und Loeschung ueber API-/Workerprozesse.
Nach Sperrcommit gibt es keinen neuen Abruf. Vorher bereits ausgegebene Bytes und
Empfaengerkopien koennen nicht zurueckgerufen werden. Sockets haben 5s Timeout;
eine vor der Frist begonnene Antwort kann noch unterwegs sein.

### Inhaltsfreie Sperrdaten und Authregister

Erfolgsrequests speichern nur Mandant, Idempotenz-ID, Nonce, Paketdigest,
minimalen Ergebnisstatus/-IDs und Zeitpunkt; keine Request-/Berichtsinhalte.
Ihr festes Ende ist `max(Request.expires_ms, tatsaechliches Signierkey.expires_ms)
+ 60000ms maximale Requestgueltigkeit + 5000ms Aufbewahrungstoleranz`. Die
Requestpruefung selbst gewaehrt **keine** Uhrtoleranz und erlaubt maximal 60s.
Zertifikate haben maximal 24h Gueltigkeit. Challenges und deren unsigned
Requestmerkposten enden an ihrer gespeicherten Frist bzw. Requestfrist + 5s;
sie koennen niemals einen Auftrag ausfuehren. Widerrufs-/Enrollaudit endet mit
der zugehoerigen Keyfrist + 65s. Job-/Loeschstatus bleibt bis zum spaeteren Ende
von beteiligter Sender-/Empfaengerepoche +65s und Berichtsfrist +65s. Fehlgeschlagene
Dateibereinigung verhindert das stille Entfernen ihres noch offenen Loeschstatus.

Nach Ablauf der Sperrfrist sind alte Requests und deren Signierkeys abgelaufen;
alte Key-IDs bleiben im Authregister gesperrt und koennen nicht erneut registriert
werden. Das verhindert eine erneute Ausfuehrung aus geloeschten Auftraegen.
Das Publickey-/Key-ID-/Rollen-/Gueltigkeits-/Widerrufsregister, Rootpins,
Bearer-/Report-/Clientsignerkeys und Config sind **keine** kurzlebigen
Berichtsinhalte. Sie gelten bis zur expliziten Stilllegung dieser lokalen
Dienstidentitaet; die Key-ID-Nichtwiederverwendung benoetigt das Register fuer
diese gesamte Identitaetsepoche. Kein pauschales inhaltsbezogenes Sicherheitsarchiv.
Der globale UTC-Maximalstand ist inhaltsfrei und gilt ebenfalls fuer diese Epoche.

### Offene Betriebsgrenzen dieser Implementierung

* Bei vollstaendig gestopptem Dienst laeuft keine Dateibereinigung. Die feste
  Frist bleibt gespeichert und wird beim Neustart **vor** Freigabe erzwungen;
  eine garantierte Dateientfernung exakt nach 24h waehrend eines Ausfalls ist
  **nicht umgesetzt**. Dafuer ist ein qualifizierter unabhaengiger Expiry-/KMS-Betrieb
  erforderlich. Dateibereinigungsfehler sind ebenfalls sichtbare Fristueberschreitungen.
* FileVault des untersuchten Hosts ist ausgeschaltet. GCM schuetzt Inhalte im
  Dateispeicher; der lokale Operator kann die Auftragsschluessel lesen. Unlink
  belegt keine SSD-/RAM-Zeroisierung oder Unwiederherstellbarkeit alter Keybytes.
  Keine KMS-/Hardware-Keyvernichtung oder nachgewiesene Loeschung von Keybackups.
* Keine App-Inhaltslogs/-Caches/-Backups. Es gibt aber keinen Nachweis ueber
  saemtliche hostexternen Backup-/Snapshot-/Swap-/Crashdump-/Admin-Systeme.
  Keine oeffentlichen Links, kein Proxy, nur Loopback. Backup-/Snapshotrestore in
  die aktive Epoche bleibt unzulaessig und technisch nicht rollbackfest;
  neue extern gesperrte Schluessel-/Token-/Requestepoche ist noch offen.
* Der bisherige A4-Liveharness erzeugt Klartext in Host-/VM-Arbeitsdateien und
  Gast-Recoveryverzeichnissen auf einer normalen VM-Disk. `run_once` verweigert
  deshalb neuen Dispatch mit `503 EPHEMERAL_RUNNER_STORAGE_UNQUALIFIED`, **bevor**
  VM/Lock/Claim/Dateierzeugung beginnen. Diese Sperre kann nicht durch einen
  hochgeladenen Pfad/Schalter umgangen werden. Kein frischer Live-Gate-Nachweis
  fuer verschluesselte Runnerdaten; die API-/Verifierregressionen nutzen die
  bereits vorhandenen synthetischen Testbelege. Historische States/Archive
  werden durch `LEGACY_STATE_PRESERVED` vor impliziter TTL-Migration geschuetzt.

Historisches Runnerprofil (neuer Dispatch derzeit gesperrt): bestehende VM, 2 CPUs, 2GiB RAM, 12GiB Disk; vor jedem Dispatch müssen
keine Hostmounts/Agentweiterleitung und keine aktiven fremden Probes vorliegen.
Nur der qualifizierte Ubuntu-Kernel 6.8.0-142-generic, zwei feste UIDs und ein
frisches Zielobjekt. Collectorfenster 12s, A4-Aktionsfenster 5s, lokale Aufruf-
Timeouts/Schlüsselbereinigung aus dem vorhandenen Harness. Fehler werden nicht
durch automatische Neuversuche verdeckt. Debian 13 / 6.12 bleibt separat offen;
Produkt-VPS/BCC-/Kernel-/Sicherheitsinstallationen sind ausgeschlossen.

## Konkrete Beispiele und Abnahme

[Live-Anfrage-/Antwortpaare](private-service-20261016/live-exchanges.json) enthalten
vollständige gültige synthetische Envelopes einschließlich überprüfbarer Signaturen,
Publickeys, Auftrags-/Annahme-/Nachweis-/Status-/Berichtsantworten. Sie sind historische
Testvektoren mit festen UTC-Zeiten; heute erneutes Einsenden muss wegen Ablauf
abgelehnt werden. Für einen neuen gültigen Satz erzeugt der Demo-Client neue Keys,
Nonces und Zeiten. Keine Bearertokens oder Privatekeys sind in diesem Archiv.
[Abnahme und Bedienung](private-service-20261016/README.md) benennt die tatsächlich
bestandenen Prüfungen, getrennt von früheren Befunden und zwei erhaltenen
Integrationsfehlversuchen.

Zwingende lokale Abnahmekriterien:

1. Registrierung benötigt admin-Zugang, unabhängigen Rootpin und frische exakte
   PoP; falsche Root, falsche Probe, Key-ID-Reuse und ungültige Rotation dürfen
   keine Registryänderung hinterlassen.
2. Auftrag allein führt nichts aus. Nur exakte receiver-signierte Annahme bindet
   denselben vollständigen Auftragsdigest; falscher Empfänger/Digest scheitert.
3. Ein echter frischer Lauf verbindet API-Digests mit der inneren A4-Delegation,
   Testprozessbindung und unabhängig erfasstem Write; Reportkeysignatur prüfbar,
   alle 28 Checks wahr und 23 Verlustfelder gemessen null für BELEGT.
4. Falsche Requestsignatur, wiederverwendete Nonce, andere Bytes unter derselben
   ID, Ablauf, Widerruf, fremder Mandant und unzulässiger Quellkanal werden über
   die HTTP-API praktisch geprüft. Kein Gegenfall erzeugt BELEGT.
5. Fehlender Nachweis ergibt UNVOLLSTAENDIG; falsche innere Signatur/Trustpin/
   Instanzbindung ergibt keinen Wirkungsbeweis; unbekannter Verlustwert ergibt
   UNBEKANNT. Doppelte/umgeordnete Records dürfen nichts erfinden.
6. Parallele Prozesse erzeugen genau ein Objekt und dieselben Aufnahmeantworten;
   Abbruch vor/nach Commit und Neustart erzeugen keine Duplikate. Unklarer Worker
   wird nie automatisch erneut ausgeführt. Widerruf eines laufenden Auftrags
   lässt keinen späteren positiven Gesamtbericht zu.
7. Fehlender Zugang, fremde Objekt-ID, Origin/Host/JSON-/Bytegrenze, DB-Ausfall und
   Browserausgabe sind praktisch geprüft; keine Fehler enthalten Geheimnisse.
8. Historische A2/A4-Quellen und bestehende Produktprüfungen bleiben unverändert;
   VM/Probes/eigene temporäre Schlüssel werden nachvollziehbar bereinigt.

Vor echtem Fremdbetrieb zusätzlich erforderlich: separater Zielhost/Kernel mit
echtem Load/Attach/Write-/Verlustnachweis, OS-/Privilegien-/Netztrennung,
TLS/Serviceidentität/KMS/Root-/Reportkeyrotation, ausfallfeste Dateifrist/Keyloeschung,
Recoveryepoche/Restoretests, Backup-/Monitoring-/Betriebsverantwortung und ein
geeigneter HTTP-Server. Keine dieser Produktionsvoraussetzungen wird durch
lokale Vertragstests als erfüllt ausgegeben.
