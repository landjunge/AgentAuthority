# A3.1: reale Sitzung/Auftrag und lokal attestierter Client-Eintrittspunkt

**UNBEKANNT:** Eine unabhängige Provider-/Modellsitzungsbeglaubigung für einen
konkreten frischen Auftrag wurde in den tatsächlich verfügbaren Codex-/Grok-
Zugängen nicht gefunden. Das ist eine überprüfte Grenze dieser Zugänge, kein
Beweis weltweiter Nichtverfügbarkeit. Kein Providermechanismus simuliert.

**BELEGT unter lokalem Hostvertrauen:** Ein vendor-signiertes laufendes
Clientimage, seine vom Hostkernel gelesene Instanz und sein exklusiver
Antwortkanal wurden an einen frischen künstlichen Job und ein signiertes
lokales Receipt gebunden. Für Codex und Grok gelang jeweils der additive Join
zum signierten A3-Dispatch, registrierten Linux-Wrapper und unabhängig
beobachteten write. **TEILWEISE BELEGT** bleibt die übergeordnete reale
Agentenkette: logische Coding-Sitzung, tatsächlicher Antwortbyteschreiber,
kontinuierliche Host-exec-Generation, Provider und Modell sind nicht bewiesen.

## Quellen, Ausgangszustand und unveränderter Bestand

Basis `28ff798e2548a82dbf787cbba0399c5a1857437f`, eigener Branch
`codex/a31-session-job-binding-20261012`, Worktree
`/Users/landjunge/agent-authority-a31-session-job-binding`.
Gelesen: A3-Spec/Resultat und neue Rohdatensätze einschließlich Accounttoken-
prüfungen/Trustannahmen, A1-/A2-Linux-Specs und Resultate sowie ihre erhaltenen
Belegarchive. A3 bleibt unverändert bei10 Positionen,12 Writes,9 Wrapper-,
8 frischen Hostdispatch- und0 vollständigen realen Agentenketten.
Alle472 Basisdateien bytegleich: `baseline-preservation.json` im neuen Archiv.

Vier frische reale CLI-Läufe: Codex, Grok, zweite Codex-Sitzung, Codex mit
explizitem Delegationsauftrag. Zusätzlich ein echter Codex-App-Server-Versuch
mit aktivierter upstream-attestation capability. Keine bestehende Sitzung
fortgesetzt, keine produktiven Dateien oder anderen Prozesse/Umgebungen verändert.
Die alte Linux-VM war gestoppt, wurde ausschließlich für zwei neue Integrationen
gestartet und wieder gestoppt. Kein Wiederholen der A1/A2/A3-Writerbatterien.

Speccommit `df1bc53`; Client-/Native-/Receiptquellen `79fee3d`; CA-/Quellpin
`d0351df`, jeweils vor den vier echten Clientfällen. Bridge-/Providerprobequelle
und tatsächlicher Integrationsstand `92b3e5f`; Rohdaten, Fehlerkorrektur,
Accountdiagnose, Offlinejoin und Regressionen `4cbb165`. Vollständige Referenzen
stehen im Gitlog und in den Pins; bestehende Quellen nicht rückwirkend geändert.

## Tatsächliche Provider- und Accountmechanismen

| Mechanismus | Tatsächlich geprüft | Aussage und Grenze |
| --- | --- | --- |
| OpenAI/xAI JWT-JWKS | echte Cachetoken, lokale OpenSSL-Prüfung, bekannte HTTPS-Issuer | Issuer-Signaturen BELEGT; kein Antwort-/Jobdigest in den geprüften Claimfeldern |
| OIDC Audience | CLI-Client-IDs aus offiziellem Quellcode, unabhängig vom Token gepinnt | Codex-ID-Token-Audience passend, dieses ID-Token abgelaufen; Access-Audience nicht mit ID-Token-Audience gleichgesetzt |
| Subject/Ablauf/Nonce | echte signierte Subjekte privat verglichen, Ablauf und neue Jobnonce geprüft | Subjekte nicht leer/konsistent; externer Subject-Enrolmentanker und ursprüngliche Login-Nonce UNBEKANNT; neue Jobnonce nicht im Token |
| Coding-Thread-/Session-IDs | neue echte Clientausgaben | Claims tatsächlich empfangen und lokal per Metadatendigest gebunden; keine eigenständigen Providerattestierungen |
| Response-/Request-IDs | offizielle Responses-Verträge und beobachtete Clientfelder | IDs sind Verweise; kein qualifizierter Provider-Signaturvertrag für den konkreten Job gefunden |
| Codex attestation/generate | tatsächlich per requestAttestation aktiviert, einmal angefordert | Server fordert Hosttoken, params leer; keine Providerantwort mit Jobdigest. Kein Token erzeugt/erfunden. Antwort dennoch erhalten |
| OpenAI Webhooks | offizieller Vertrag gelesen | Signaturprüfung mit eingerichtetem Signing-Secret; kein hier konfigurierter öffentlich prüfbarer Responsebeleg. Nicht neu eingerichtet/ausgeführt |
| Vendor-Clientcode | codesign disk verification plus dynamische Security.framework-Prüfung | OpenAI/X.AI Developer-ID-Kette unter Apple-Trust BELEGT; signiert Softwareimage, keine Modellantwort |

OpenAI Client-ID aus `rust-v0.162.1`,
`codex-rs/login/src/auth/manager.rs`; xAI aus dem unabhängigen öffentlichen
Stand `2bdd1d6a6369de0e8c68132ea4539e9abd9e14a8`,
`crates/codegen/xai-grok-login/src/config.rs`. Dieser xAI-Quellstand wird nicht
als exakter Build-SHA der installierten Grok-Binärdatei behauptet. Historische
Quellpfade lieferten404; aktuelle Module wurden gelesen statt Inhalte erfunden.
`source-index.json` enthält URLs/Hashes und die konkrete Versionsgrenze.

Codex: ID-Token-Signatur, Issuer, Client-Audience und vorhandenes Subject
geprüft; Ablaufprüfung negativ. Ein anderer signierter Codex-Token ist noch
gültig, besitzt eine andere Audience; sein Ressourcen-Audienceanker bleibt
UNBEKANNT. Grok: signierter, noch gültiger Cachetoken mit passender publizierter
Client-ID-Audience; sein Tokenkind ist nicht als vollständiger OIDC-ID-Token-
Login qualifiziert. Zwei weitere Cacheformen bleiben UNBEKANNT. Subjekte nur
im Hostspeicher, keine Werte/Emails/Account-IDs archiviert. Falsche Issuer- und
Client-Audience-Kontexte passen nicht. Die ursprüngliche Loginchallenge fehlt;
keine Behauptung eines vollständig nachgeprüften frischen OIDC-Logins.

Der echte App-Server meldete Accounttyp chatgpt und lieferte einen Job. Er
forderte `attestation/generate` mit leeren Parametern an. Der Host antwortete
ausdrücklich Unsupported/-32601, weil kein autorisierter Token-Generator
vorlag. Der publizierte Vertrag bezeichnet den Token als opaque upstream
Clientattestation für x-oai-attestation. Kein Hosttoken wird zur Provider-
Antwortsignatur erklärt. Rohmetadaten/Bytehashes: `provider-capability.json`.

## Neue lokale, ausdrücklich schwächere Auftragsbindung

`process_probe.c` wurde mit vorhandenem Xcode/clang und Security/CoreFoundation
kompiliert, ohne Installation oder Hostprivilegien. Eigene neue Client-PIDs
werden über proc_pidinfo/proc_pidpath vor und nach der Signaturprüfung gelesen:
Kernelstart in Sekunden/Mikrosekunden, Boot, UID, PPID und geladenes Image.
SecCodeCopyGuestWithAttributes und SecCodeCheckValidity prüfen das **laufende**
Image gegen Apple generic anchor, konkrete Vendor-OU, Identifier und CDHash.
Popen-PID/Controller-PPID/UID sind getrennte Orakelwerte. Kein Prozessname allein.

Codex Team2DC432GLL2/Identifier codex, Grok Team5Y6N3AJ54S/
Identifier xai-grok-pager; CDHashes/Binärhashes vorab gepinnt. Alle vier
Liveprüfungen liefern validity_status0 und stabile Kernelstartwerte. Ein eigener
Apple-sleep-Kontrollprozess erfüllt die OpenAI-Anforderung nicht (-67050).
Eine gültige andere Codesignatur wird nicht als Codex übernommen.

Ein exklusiver eigener stdout-Kanal liefert ausschließlich den exakt erlaubten
künstlichen Job mit frischer Challenge. Der lokale Attestor signiert Channel-ID,
PID/Kernelstart/Boot/Imageprüfung, Metadatendigest mit Threadclaim, konkreten
Jobdigest, einmalige Receipt-ID und180s-Fenster. Private CA wird weder an Client
noch Gast gegeben. Verifier prüft mit gepinntem Publickey und unabhängig
gehaltenem Controllerkontext, nicht mit einem vom Claim gewählten Publickey.

Trustanker dieser Schicht sind **Host/registrierender Controller, macOS-Kernel,
Apple Code-Signing-Trust und lokale CA**. Sie authentisiert einen gemessenen
lokalen Client-Eintrittspunkt, keine extern beglaubigte KI-Agenten-/Modellsitzung.
Nachkommen können stdout erben; tatsächlicher Schreiber einzelner Antwortbytes
ist UNBEKANNT. Das Hostimage wird einmal dynamisch gemessen, kein kontinuierlicher
Host-exec-Generationsmonitor. Die gesamte Clientlaufzeit wird nicht als lückenlos
attestiert behauptet. Kompromittierter Host/CA/signed Client liegt außerhalb.

## Tatsächlich ausgeführte Kontrollen und Integrationen

| Fall | Methode | Ergebnis |
| --- | --- | --- |
| Gültig Codex/Grok | echte Antwort, native Code-/Instanzprüfung, signiertes Receipt | lokale Kanal-/Jobbindung jeweils BELEGT unter genannten Trustankern |
| Fremder Kontext | echte Grok-Receipt gegen echten Codex-Kontext, Signatur bleibt gültig | Client/Channel/Instanz passen nicht, lokale Übernahme zurückgewiesen |
| Replay | dieselbe echte Receipt zweimal im selben Verifierledger | erste Prüfung gültig, zweite nur anti_replay negativ |
| Jobdigest manipuliert | echtes Receipt, anderer künstlicher Job | gültige Signatur authentisiert nicht den anderen Digest |
| Sitzungswechsel | altes Receipt gegen zweite reale Codex-Instanz/Channel | kein Übertragen des alten Bindings |
| Delegation | echte CLI-Delegationsanforderung; Receipt gegen Elternkontext | keine Collab-/Delegiertenbelege geliefert; tatsächliche Delegation UNBEKANNT, Elternbinding nicht übertragen |
| Ablauf | vorhandenes echtes Receipt exakt am expiry-Rand | time negativ, kein frisches Binding |

Die7 Negativ-/Positivpositionen sind **ausgeführte Offlineprüfungen echter
öffentlicher Receipts** mit expliziter gespeicherter Prüfuhr. Keine simulierte
Providersitzung, kein neuer Modelllauf pro Mutationsfall. Replayledger besteht
im aktuellen Verifierlauf; Restart-/Mehrprozess-/dauerhafte Replayabwehr
UNBEKANNT. Der Delegationsauftrag wurde einmal gestellt, nicht still wiederholt
oder durch einen simulierten Delegate ersetzt. Ein gültiger Parentkanalnachweis
wird nicht zum Delegiertennachweis aufgewertet.

Zwei neue Integrationen waren fachlich nötig: der neue Client-/Job-Eintrittspunkt
war in A3 nicht vorhanden. Vorherige A3-Gastquellen bytegleich in eigenen Pfad
/opt/a31_dispatch kopiert, frische Wrapperkeys/Boot-/Namespace-/Dateibindung.
Signed Dispatch enthält SHA256 des neuen Clientreceipts; A2-Starter authentisiert
das Wrappercredential, unveränderter A1-Observer misst das konkrete Objekt.
Controller-Orakel bleibt separat, keine Identitätsdaten an A1.

Codex: Linuxwriter1121/Start98333000221ns. Grok:1136/113777689218ns.
Beide write-Returns16, genaue Datei/dev/inode und frische Wrapperhandshakes
passen. `independent-join.json` prüft Hostsignature, Metadatendigest, konkreten
Job, signierte Receiptverknüpfung, unveränderte A3-Signaturen/Instanz-/Zeitregeln
und unabhängige Kernel-Writes erneut. Beide lokalen Pipelineketten BELEGT;
vollständige reale Agentenketten weiterhin0/UNBEKANNT. Hostclient und
Linuxwrapper sind ausdrücklich unterschiedliche Prozesse auf verschiedenen
Kerneln, verbunden durch Dispatch, nicht durch gleiche PID oder Zeitnähe.

## Reale Fehler, Daten-/Ressourcengrenzen und Bestandsschutz

Der gemessene Bridgequellstand92b3e5f füllte ein falsch benanntes Zeitfeld
all_writes_before_client_receipt_expiry aus kernel_entry_ns>=0. Das ist **kein
Ablaufnachweis**. Rohdateien samt Feld bleiben erhalten; Verifier ignoriert es,
Regression prüft diese Nichtverwendung. `bridge-time-field-correction.json`
dokumentiert den Fehler. Quelle wurde korrigiert, keine Messung wiederholt.
Separat tatsächlich gemessen sind der Host-entry_gate_ns und der boolesche
Host-Collection-Ende-vor-Expiry-Test. Der numerische Host-Endzeitstempel wurde
damals nicht gespeichert und bleibt UNBEKANNT/null. Gast-/Host-Monotonicuhren
werden nicht unmittelbar verglichen oder rückwirkend gleichgesetzt.

Vier A1-Records/304 Callbackbytes, sechs Lifecycle-Records/264 Bytes;
bekannte Perf-Verluste0, Entry-/Fork-entry-nmissed UNBEKANNT. A1 CPUuser
4.018359s/system0.592960s, PeakRSSmax177729536B; Adapter1.967794s/
0.526153s, PeakRSSmax164429824B, inklusive BPFcompile. Hostclient-/Kernel-/
GesamtVM-Kosten UNBEKANNT. Speicherbytes/Hashes separat im Artifactindex.
Keine Dauerpersistenz-/Last-/mmap-/anderen Betriebssystemnachweise.

Tokenprüfung hielt Bearer/Claims ausschließlich privat im Hostspeicher/Prüfpipe.
JWKS, Codesigninformationen und Receipts sind öffentlich, keine Privatekeys oder
Modelltexte archiviert. Guestvault und Host-CA gelöscht, sichere RAM-Löschung
UNBEKANNT. kprobe_events leer, eigene Hostclientprozesse beendet, VM Stopped,
Colima unverändert Running. Keine Rechteumgehung und keine zusätzliche Host-
freigabe benötigt. Keine neue Anmeldung/Providerkonfiguration/Tokenweitergabe.
D-012 bleibt Beobachtung/Analyse, keine Produktrechte-/ALLOW/DENY-Folge.

## Prüfung, Reproduktion und Entscheidungsspielraum

16 neue Regressionen auf echten öffentlichen Belegen bestanden. Native C
kompiliert mit -Wall/-Wextra/-Werror; tatsächliche dynamische Vendorprüfungen
und beide BPF-Integrationen separat ausgeführt. Neue Quellen Ruff PASS, Format
des Repos PASS;16 historische Ruff-Findings bytegleich zur Basis,0 neue.
Mypy32/Bandit bestehender Core PASS. Gesamtsuiten/Commit-/Log-/JUnit-Hashes
stehen in quality.json; lokale Tests ersetzen keine Remote-CI.
Beide Gesamtsuiten auf unverändertem4cbb165 bestanden jeweils mit648 Tests,
0 failures/errors/skips. Die vorhandene Fork-DeprecationWarning bleibt erhalten.
Öffentliches Archiv:37 indexierte Dateien/185465 Bytes, ohne Index selbst,
Top-Level-Berichte, Quellcode und Tests.

Reproduktion: neue eigene temporäre CA und frische Quell-/Codepins;
process_probe.c lokal mit Security/CoreFoundation kompilieren; client_run.launch
mit eigenem Controllerkontext aufrufen; receipt.check getrennt prüfen.
provider_probe.py aktiviert den realen Codex-Vertrag ohne Fake-Token.
linux_bridge.py verwendet allein die bestehende eigene VM und führt maximal
zwei qualifizierte Integrationen aus. Alle Originalquellen/Artefakte dieser
Runde sind im Branch gepinnt; neue Messung benötigt neue Nonces/Keys/Datenpfade.
Die korrigierte Bridge speichert künftig den tatsächlichen Host-Endzeitstempel;
die alten Daten werden dadurch nicht ergänzt oder ersetzt.

**Konkrete Antwort:** Unter den geprüften vorhandenen Zugängen kann eine echte
Codex-/Grok-Providersitzung **nicht unabhängig an diesen einzelnen Auftrag
nachgewiesen werden**. Es fehlen ein geeigneter frischer, prüfbarer
Provider-/Agentensitzungs-/Antwortbeleg und die konkrete Digest-/Delegations-
bindung. Weltweite technische Unmöglichkeit bleibt UNBEKANNT. Als schwächere
Alternative ist eine lokal vertrauensgebundene Clientpipeline-/Dispatch-/
Linuxwirkungsbindung praktisch belegt. Weitere Rechte, Agentenidentitäts-
registrierungen oder Providerfunktionen wurden nicht eigenmächtig eingerichtet.
Keine Folgephase, kein Merge/Ready, keine historischen Ergebnisse umgedeutet.

Primärverträge: [OpenAI OIDC](https://developers.openai.com/siwc/website),
[Codex App-Server](https://developers.openai.com/codex/app-server),
[OpenAI Responses](https://developers.openai.com/api/reference/typescript/resources/responses),
[Webhooks](https://developers.openai.com/api/docs/guides/webhooks),
[Grok Enterprise](https://docs.x.ai/build/enterprise),
[xAI Responses](https://docs.x.ai/developers/rest-api-reference/inference/responses).
Öffentliche Client-ID-Quellen und installierte Apple-SDK-Schnittstellen sind
separat mit Pfaden/Hashes dokumentiert. Verträge sind keine Ersatzmessung.
