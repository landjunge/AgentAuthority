# A3 Linux: reale Clientläufe, unabhängig erfasste Wirkung, offene Agentenidentität

**TEILWEISE BELEGT:** Tatsächlich aufgerufene Codex-/Grok-Clients lieferten
künstliche Jobs, die ein signierter lokaler Linux-Ausführungswrapper ausführte.
Zwölf write-Handlungen sind unabhängig im Kernel erfasst. **UNBEKANNT** bleibt
die vollständige Kette *extern authentisierter realer KI-Agent → Sitzung →
Linux-Prozessinstanz → Wirkung*. Kein Wrapperlabel wird zur Providerbeglaubigung.
H-A3-REAL ist INCONCLUSIVE; keine schwächere Ersatzhypothese wird als bestanden
geführt. Kein Produktions-/Paketfreigabeurteil, kein technologischer Vorsprung.

## Ausgangsbasis und praktisch benutzte Umgebung

Basis `98c274ac5c1e475c335704d4f5aefa40f97f47b0`, eigener Branch
`codex/a3-linux-real-agents-20261012`. Gelesen: ABC-Forschungsplan einschließlich
additiver Identitätsfrage, A1-Linux-Spec/Resultat, A2-Linux-Spec/Resultat und
alle acht öffentlichen A2-Rohdatensätze. A1 belegt die begrenzte OS-Schreiber-
bindung; A2 vier kontrollierte Testidentitätsketten und vier korrekt ungebundene
Fälle. Sie authentisieren weder Codex/Grok noch Provider oder Modell.

Das historisch gesperrte ABC-A3 zur dauerhaften FD-Identität ist eine andere
Frage und bleibt unverändert. Der aktuelle Nutzerauftrag autorisiert diese
neue reale-Client-Runde.433 Basisdateien bleiben bytegleich; Hashliste unter
`docs/a3-linux-runs/2026-10-12/baseline-preservation.json`.

Bestehende eigene Ubuntu24.04.5-Lima/VZ-VM, Linux6.8.0-142-generic, x86_64,
2CPU/2GiB/12GiB, ohne Hostmounts und ohne SSH-Agentweiterleitung. Root nur im
Gast für Registrar und Kernelbeobachtung. Keine Hostinstallation, kein Host-
sudo, keine TCC-/Entitlement-/Kerneländerung, keine Credentialkopie in den Gast.
VM vor Versuch gestartet, nach Export und Schlüsselentfernung sauber gestoppt.
Colima bleibt Running mit unveränderten 2CPU/4GiB/30GiB-Einstellungen.

Auf dem Host tatsächlich verfügbar: Codex0.162.1, Grok1.0.50. Beide realen
Binärdateien sind mit SHA256 in den Clientdatensätzen identifiziert. Dies sind
lokale Messpins, keine geprüften Hersteller-Code-Signaturen. Codex meldete
ChatGPT-Login; beide Clients antworteten erfolgreich. Im Gast waren weder
Codex/Grok noch deren Authcaches vorhanden. Keine API-Keys in den geprüften
bekannten Umgebungsvariablen. Die verfügbare erlaubte Route ist deshalb
**Hostclient → geprüfter Job → lokaler Linux-Wrapper**, kein nativer
authentisierter Linux-Codex-/Grok-Client. Kein simulierter Modelllauf als Ersatz.

## Authentisierung: was sie tatsächlich belegt

`research/a3_linux/account_probe.py` prüfte lokal vorhandene JWT-Signaturen mit
Host-OpenSSL gegen per HTTPS gelesene öffentliche Issuer-JWKS. OpenAI RS256:
eine verifizierte abgelaufene und eine verifizierte noch gültige Tokeninstanz.
xAI ES256: eine verifizierte noch gültige Tokeninstanz. Nicht qualifizierbare
Tokenformen bleiben ausdrücklich UNBEKANNT. Keine Bearer-Tokens, Subjekte,
Account-IDs oder Tokenclaims wurden exportiert; der signierte Input blieb im
Hostspeicher/Prozessstdin. Temporäre öffentliche Prüfdateien wurden entfernt.

Das belegt die ausgeführte Issuer-Signaturprüfung, **nicht** eine vollständige
OIDC-Anmeldung: Audience ist nicht unabhängig gepinnt. Insbesondere ist eine
Authentisierungssitzung im Kontotoken keine Coding-Thread-ID. Kein geprüftes
Token qualifiziert in den geprüften Identitätsfeldern einen logischen
Agenten-/Modellnachweis. Die Tokenprüfung lässt
sich mit demselben autorisierten Cache und archivierten öffentlichen Keys
reproduzieren; ohne den bewusst nicht archivierten Bearer-Input ist kein
vollständiges öffentliches Offline-Replay dieses Kontonachweises möglich.

| Ebene | Befund und genaue Grenze |
| --- | --- |
| Clientstart/Jobtransport | BELEGT unter Vertrauen in Hostcontroller und bestehende Binärdateien; kein externer Clientattestationsnachweis |
| Accounttoken/Issuer | TEILWEISE BELEGT: reale Signaturprüfung; Audience/Agentenbezug nicht qualifiziert |
| Coding-Sitzung | UNBEKANNT als authentisierte logische Identität; beobachtete IDs stammen vom Client |
| Provider der konkreten Antwort | UNBEKANNT als unabhängiger Antwortnachweis; ein Kontotoken signiert nicht diese Modellantwort |
| Modell | UNBEKANNT; Codex-Anforderung gpt-6.1-sol ist ein Konfigurationsclaim, Grok nutzt seinen Default |
| Lokales Wrappercredential | BELEGT für registrierte Schlüssel/Instanzen, ausdrücklich kein realer Agentenschlüssel |
| Prozess/Datei/write | BELEGT für die gemessenen zwölf künstlichen VFS-write-Aktionen |
| Vollständige reale Agentenkette | UNBEKANNT; es fehlt das externe frische Agenten-/Sitzungs-Enrolment samt Delegations-/Instanzvertrag |

## Ausgeführter Start- und Messmechanismus

Spec `3f96dadc12fc259a9091d45746ffc4d4faaf99c8`, Implementierung
`b6acd389b8018c7c76cd0d05414999c449b05593`, öffentlicher Register-/Quellpin
und unveränderter Kernel-Fallstand `88029be0d5e28c2715d799660eef76621e12c060`.
Vor Kernel-Fall1 signierte eine neue lokale Host-CA das Wrapperregister mit
Boot/Namespace und Quellhash. Zwei lokale Credentials: WrapperCodex UID61011,
WrapperGrok UID61012. Der CA-Key blieb am Host; Starterkey im privaten Gastvault.

Reale Clients liefern nur das exakt erwartete synthetische JSON-Jobobjekt:
write16, Nonce, Position, Clientclaim. Kein freier Shelltext wird ausgeführt.
Für gewöhnliche Aufrufe sind Tools/Delegation ausgeschaltet; im gesonderten
Delegationsfall wurde genau eine Delegation angefordert. Zwei echte
App-Server-Versuche erzeugten jeweils zwei frische Threads im selben Host-
prozess, einmal nacheinander, einmal parallel. Kein vorhandener Thread wurde
fortgesetzt. Modellinhalte werden auf den erlaubten künstlichen Job reduziert;
übrige Ausgaben nur nach Ereignistyp/IDs/Bytezahl/SHA256 archiviert.

Ein signiertes Hostdispatch-Receipt bestätigt den lokalen Aufruf-/Jobdatensatz.
Es ist **keine Providersignatur**. Der additive Adapter verwendet unverändert
den A2-Starter, seine SCM_CREDENTIALS-/pidfd-/Start-/Exec-Bindung und Lifecycle-
BPF. Die neue Launchmethode nutzt Popen user/group/extra_groups statt preexec_fn;
der kontrollierte Worker setzt no_new_privs und non-dumpable unmittelbar nach
dem Interpreter-exec vor Handshake/Keynutzung. Nur eigener versiegelter Key-memfd
und öffentliches Dispatchpaket werden geerbt, kein Host-/Providercredential.

Der A1-VFS-Observer bleibt bytegleich und erhält nur das künstliche Dateiobjekt
und ein12s-Fenster. Root-Registrar, A1-Capture und Controller-Ground-Truth sind
getrennt; das Orakel wird am Host gespeichert und nicht an A1 übergeben.
OpenSSL prüft öffentliche CA-/Actor-/Starter-/Dispatchsignaturen offline.
Fileobjekt, Boot, PID-Namespace, Kernelstart, Generation und Zeitfenster müssen
passen. Für mehrere Proofs einer Instanz zählt der letzte zeitlich passende
signierte Handshake; das macht dessen Sitzung nicht extern authentisiert.

Die ersten zwei echten Zugangsantworten wurden bereits vor dem Codecommit
gewonnen und anschließend für Position1/2 verwendet. Ihr Clientcode war damals
noch uncommittet; hierfür wird **kein vorab committed Clientquellpin** behauptet.
Spec war zuvor committed. Vor allen Linux-Writes waren Wrapper-/Collectorquellen
und Enrollment committed/gepinnt; deren Hashes blieben durchgehend unverändert.

## Zehn ausgeführte Positionen, zwölf unabhängige Writes

| Position | Tatsächlicher Fall | Kernelwriter | Ergebnis/Grenze |
| --- | --- | --- | --- |
|1 Codex | echte CLI-Antwort, lokaler Adapter schreibt |1249, Start595331154878ns| WrapperCodex-Kette BELEGT; reale Agentenidentität UNBEKANNT |
|2 Grok | echte CLI-Antwort, lokaler Adapter schreibt |1265,610912888282ns| WrapperGrok-Kette BELEGT; reale Agentenidentität UNBEKANNT |
|3 Kind | Kind erbt Wrapperkey/Socket und schreibt |1282,637318111288ns| Keybesitz gültig, Kindbindung fehlt; Wrapper-Wirkungsbindung UNBEKANNT |
|4 Delegation | echte Codex-Anforderung, wait-Kollaborationsereignisse, Jobantwort |1297,673168990713ns| Wrapper BELEGT; tatsächlicher Spawn/Delegiertenantwort nicht ausreichend erfasst, Delegationsidentität UNBEKANNT |
|5 exec | registrierter Wrapper wechselt vor Write den Programmeinstieg |1313,698389815464ns| Generation1→2; alte Wrapperbindung nicht übernommen |
|6 Sitzungswechsel | zwei neue Threads nacheinander im App-Server PID69889 |1328,722360244123ns, zwei Writes| derselbe Wrapper authentisiert; zwei Client-Threadclaims sind keine zwei unabhängigen Identitätsbeweise |
|7 gemeinsam | zwei neue Threads parallel im App-Server PID70008 |1344,744384045109ns, zwei Writes| lokale Bindung BELEGT; logische Sitzung ist aus Kernel-PID nicht unterscheidbar |
|8 Replay | neuer realer Codex-Job, absichtlich altes öffentlich signiertes Dispatch ausgeführt |1359,769693654189ns| frisches Wrappercredential BELEGT; Dispatch-Nonce veraltet, kein frischer Sitzungsnachweis |
|9 Schlüsselweitergabe | lokaler Wrapperkey explizit ans Kind vererbt |1375,794914915123ns| gültiger Keybesitz überträgt keine registrierte Prozessbindung |
|10 Übernahme | Grok-Wrapper behauptet WrapperCodex und versucht fremden FD-Zugriff |1391,831847588253ns| kontrollierter open liefert EACCES13; Writer bleibt WrapperGrok, keine Codex-Übernahme |

Alle zehn Positionen einmal, kein Retry/kein ersetzter Fehlversuch.12 Controller-
aktionen passen zu12 unabhängig erfassten Writes,9 lokale Wrapperbindungen,
8 davon mit frischem Hostdispatch,0 vollständige authentisierte reale
Agentenketten.13 Actorproofs/Starterreceipts tatsächlich kryptografisch geprüft.
Kind/Keyweitergabe/Exec bleiben ungebunden, ohne ihre Wirkung wegzuklassifizieren.
Die FD-Zugriffsverweigerung ist Worker-Orakel, keine zusätzliche eBPF-open-Messung.
Replay ist hier ein **Hostdispatch-Replay**, kein erneut durchgeführter A2-
Proof-Replay. PID-Reuse wurde nicht nochmals ausgeführt; A2-Beleg bleibt erhalten.

WIDERLEGT im gemessenen engen Rahmen sind die Gleichsetzungen: gültiger
Wrapperkeybesitz = registriertes Kindbinding; unveränderte PID/Start = gültige
alte Exec-Bindung; gültige alte Dispatchsignatur = frische Jobbindung. Die
generelle Machbarkeit externer Agentenbeglaubigung wird dadurch nicht widerlegt.
Delegationsabdeckung bleibt teilweise: wait-Ereignisse allein belegen keinen
eindeutigen authentisierten Delegierten. Daher kein vollständiger A3-Protokoll-
PASS oder erfundener Agenten-Authentisierungs-PASS.

## Ressourcen, Fehler und Sicherheitsgrenzen

A1:22 Records/1672 Callback-Rohbytes; Lifecycle:38 Records/1672 Rohbytes.
Bekannte Perf-Verlustindikatoren0; A1-Entry-nmissed und Lifecycle-Fork-Entry-
nmissed UNBEKANNT. Keine globale Vollständigkeits- oder Lastgarantie.
A1 CPUuser20.221154s/system2.102414s, PeakRSSmax177590272B;
Adapter9.008081s/1.745079s, PeakRSSmax164560896B. Einschließlich jeweiliger
BPF-Kompilierung; Client-/Kernel-/GesamtVM-Kosten UNBEKANNT. Speicherbytes und
Einzelhashes stehen getrennt im Artifactindex. write-Return ist keine
Crashpersistenz, Modellentscheidung oder semantische Inhaltsherkunft.

Kein Writer-Ausführungsfehler. Ein tatsächlicher Nachverarbeitungsfehler
KeyError peak_rss_bytes wurde dokumentiert und allein durch Lesen des richtigen
vorhandenen Felds rss_peak_bytes korrigiert; keine Messung wiederholt.
Privatvault und temporäre CA gelöscht, keine eigenen Hostprozesse im
Versuchstemp-Scope übrig, kprobe_events leer. Sichere RAM-Löschung UNBEKANNT.
Host/CA, GastRoot, Kernel und Hypervisor sind ausdrücklich Vertrauensbasis;
kein Schutzbeweis gegen kompromittierten Root, Lieferkette oder Credentialdiebstahl.
Keine externen Zugangsschlüssel weitergegeben. Schlüsselweitergabe betrifft
ausschließlich das neu erzeugte künstliche Wrappercredential im Gast.

D-012 bleibt Beobachtung/Analyse: ungebundene Fälle durften trotzdem schreiben,
keine produktive ALLOW/DENY-/Rechtefolge. Das kontrollierte Job-Allowlisting ist
Versuchssicherheit, kein neues Produktgateway. Historische Ergebnisse,
Hypothesen, Messwerte und Negativbefunde wurden nicht neu klassifiziert.

## Prüfung, Reproduktion und verbleibende Voraussetzung

13 neue Offline-Regressionstests auf echten öffentlichen Messartefakten
bestanden. Sie prüfen Signaturen und negative Joins, ersetzen keine Kernelmessung.
Neue A3-Quellen Ruff PASS; Formatcheck des gesamten Repos PASS. Breiter Ruff-
Check zeigt16 bereits bytegleich an98c274a vorhandene historische Findings,
0 neue Findings. Keine historischen Quellen zur Verschönerung geändert.
Mypy32 bestehende Coredateien und Bandit Core PASS; keine BPF-C-Analyse dadurch.
Zwei Gesamtsuiten auf unverändertem `b5fd68e91cc943c661343fb5758980c9e2c55552`
bestanden jeweils mit632 Tests,0 failures/errors/skips; die vorhandene
Fork-DeprecationWarning bleibt erhalten. Genaue JUnit-/Loghashes: `quality.json`.
Remote-CI ist separat; bislang kein neuer Branchlauf, keine grüne CI behauptet.

Reproduktion benötigt die bereits qualifizierte eigene VM und vorhandene
autorisierte Hostclients. Neue Tempdaten, frisches run_id, frische CA/Enrollment;
niemals alte CA/Receipts oder Archivdateien überschreiben. Einstieg
`research/a3_linux/client.py`, `shared_client.py`, dann `driver.py prepare/run`;
die ersten beiden Clientjobs/state.json müssen im neuen Tempverzeichnis erzeugt
werden. Kernel-Freeze/Enrollment vor neuen Writes committen und separat pinnen.
Der vorhandene driver benennt absichtlich die konkrete Forschungs-VM, keinen
beliebigen Host. Keine Credentials/Orakel an den A1-Beobachter geben.

Für eine vollständige Kette fehlt ein unabhängig vertrauenswürdiger frischer
Nachweis, der **die konkrete reale Coding-Instanz/Sitzung und gegebenenfalls
Delegierte**, ihren Schlüssel und ihren Prozess-/Exec-Lebenszyklus registriert.
Kontotoken, Clientdateiname, modellgenannter Name, Zeitnähe, lokales Receipt und
Kernel-PID ersetzen dies nicht. Ein weiterer Gastlogin allein schließt die
semantische Identitätslücke nicht. Keine zusätzliche Hostfreigabe war für die
ausgeführte Route erforderlich; Tokenkopie oder neuer Login wären eigene
Entscheidungen und wurden nicht vorgenommen. Keine neue Phase begonnen.

Primärquellen für die verwendeten Clientverträge:
[OpenAI Authentisierung](https://developers.openai.com/codex/auth),
[nichtinteraktive Ausführung](https://developers.openai.com/codex/noninteractive),
[App-Server](https://developers.openai.com/codex/app-server).
Gemessene öffentliche OpenID/JWKS-Quellen samt Hashes sind getrennt archiviert.
Grok-Vertrag stützt sich auf tatsächlich gelesene installierte CLI-Hilfe;
die versuchte xAI-CLI-Dokumentseite war nicht erreichbar. Keine davon ersetzt
die ausgeführten Messungen. Kein Merge, kein Ready, PR44 unverändert Draft.

Öffentliches Archiv:26 indexierte Dateien/300671 Bytes, ohne Index selbst,
Top-Level-Berichte und Quellcode. Commitkette: Spec `3f96dad`, Code `b6acd38`,
Pins `88029be`, Rohdaten/Kontodiagnose/Regression `b5fd68e`, abschließender
Berichts-/Prüfcommit im Branchlog. Jeder Push regulär und ausschließlich auf
`codex/a3-linux-real-agents-20261012`; keine fremden Branches verschoben.
