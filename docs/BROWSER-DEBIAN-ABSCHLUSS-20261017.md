# Agent Authority: Debian- und Dienstabschluss vom 17.10.2026

Der bestehende eigenständige Browserdienst ist als privates synthetisches
Eininstanzpaket auf dem vorhandenen Debian-Host **tatsächlich qualifiziert:
46/46 Paketprüfungen bestanden, keine fehlgeschlagen, keine unausgeführt**.
Der neue Debianlauf bezieht sich auf genau das unten benannte Paket. Er ersetzt
die bisher fehlende Debianqualifikation des neueren Servercodes. Er erteilt
keine Produkt-, Dauerbetriebs-, Realdaten- oder Mehrserverfreigabe.

Gearbeitet wurde ausschließlich in
`/Users/landjunge/agent-authority-lab/.worktrees/browser-architecture-20261017T064003Z`,
ausgehend vom sauberen Commit `57691679a02c9f2b0738dff77a28c1774de5958e`.
Die beiden vorgegebenen `AGENTS.md` wurden gelesen; weitere geltende
`AGENTS.md`, `PROJECT.md` oder `ARCHITECTURE.md` liegen im Worktree nicht vor.
Die vorhandene Browserarchitektur und beide abgeschlossenen Architekturstände
wurden wiederverwendet. Produktcode, Engine, Browserressourcen und native App
wurden in diesem Abschluss nicht verändert.

## Quell-, Paket- und Belegidentität

| Gegenstand | Exakte Identität |
|---|---|
| Sauberer Paketquellcommit | `56adfeb318f7fa6d315d5da13c072231643eb7fd` |
| Paket | `dist/browser-debian-abschluss/agent-authority-browser.pyz` |
| Paket-SHA-256 | `2efc74f7d86459c99f8d709af7c1e1ab9dc5c9d0261fd7fafc46407b70425b5a` |
| Runtime-SHA-256 aus sortierter Runtime-Dateihashmap | `72f0d81992cc5994c210efe129ee81a59111b212cbf4664272d02cc1b92088ee` |
| Manifest-SHA-256 | `4a7cfc718a183b3b52fb1faa84b1d1a0f41806f15f05de936ce84bcb803118e2` |
| Aktueller Debianbeleg | [debian-result.json](browser-debian-abschluss-20261017/debian-result.json), SHA-256 `0db22336c0d49f38e3ecb49ff39063b0dfcd0c257bf37b0323ffaab96fc6df7d` |
| Tatsächlich übertragener Paketprüfer | `scripts/check_browser_package.py`, SHA-256 `a808fb72c99d3b6a87733730eb97ed48906076f52fa2ef59f891c5e1183efe66` |
| Ausgeführter Debianablauf | [qualify.py](browser-debian-abschluss-20261017/qualify.py), SHA-256 `66db2980ddf37986b64bd563193afad4301e6f04f251474bca50d260f9c89f1a` |

Das Paket wurde aus sauberem Stand gebaut. Vor SSH wurden HEAD, sauberer
Worktree und sämtliche im Manifest benannten Quelldateihashes geprüft. Auf
Debian wurden Paketdigest, eingebettetes Manifest und alle enthaltenen
Dateihashes geprüft; zurückgegebene Paket-/Commitidentität wurde gegen die
lokalen Erwartungen abgeglichen. Manifest und `SHA256SUMS` liegen beim Paket;
das Manifest wird zusätzlich als Belegkopie in diesem Abschluss aufbewahrt.
Der folgende Belegcommit ergänzt Dokumentation und Ergebnisse. Das qualifizierte
Paket wird dadurch nicht erneut gebaut oder mit einem anderen Paket verwechselt.

## In diesem Abschluss tatsächlich ausgeführt

Der Hauptagent führte die Debianprobe selbst über SSH-Alias `netcup` aus.
Verwendet wurden ausschließlich das vorhandene Python **3.13.5**, Debian GNU/Linux
13 (trixie), Kernel **6.12.101+deb13-amd64** und vorhandene stdlib-/systemd-Werkzeuge.
Keine Installation, kein Download und kein Browser auf Debian. Herkunft des
vorhandenen Hostinterpreters und nicht erhobene Werkzeugversionen wurden nicht
neu attestiert.

Der genaue lokale Einstieg war:

```sh
/usr/local/bin/python3.13 -B scripts/package_browser.py --output dist/browser-debian-abschluss
/usr/local/bin/python3.13 -B docs/browser-debian-abschluss-20261017/qualify.py
```

`qualify.py` ruft ausschließlich folgenden gemeinsamen Starter mit seinem
vorher geprüften, im Skript vollständig erhaltenen SSH-Bootstrap auf:

```text
python3 /Users/landjunge/agent-bridge/queues/gesamtabschluss-20261017T084846Z/with-debian-lock.py ssh netcup <konkreter Python-Bootstrap aus qualify.py>
```

Der Lock umfasste Transfer, Proben, Stop und Bereinigung. Auch die vorausgehende
rein lesende Werkzeug-/Ressourcen-Vorprüfung verwendete diesen Starter. Der
Prüfablauf ist ein Beleg für diesen einen festen Paketstand; er verweigert
vorhandene Ergebnisdateien und abweichenden/unsaubereren Quellstand. Er ist kein
zusätzlicher allgemeiner Laborrunner.

| Tatsächliche Paketprobe | Ergebnis und Reichweite |
|---|---|
| Identität/Ressourcen | Manifest, alle Paketdateihashes, feste Webressourcen per HTTP, keine State-/Credentialdateien im Paket; `sourceClean=true`. |
| Start/Anmeldung | Zwei synthetische Konten, leerer Anfang, anonym=401, serverseitige Session, HttpOnly/SameSite-Cookie. |
| Laufender Widerruf | Logout erfolgreich, altes Cookie anschließend bei Session/Liste/Status=401, frische Anmeldung mit anderem Cookie erfolgreich. |
| Owner/Source/Job/Adapter | Fremder gespeicherter Bericht=404 und fremde Liste leer; fremder Ownerimport sowie einzeln manipulierte Source, Job und unzulässiger Adapter=403. CSRF und doppelte JSON-Schlüssel abgewiesen. |
| Berichte/Vertrauen | Neutrale Engineaufnahme und getrennte Privatberichtaufnahme erfolgreich; Privatbericht bleibt unverifiziert/UNBEKANNT und Produktivanschluss blockiert. Demo nur ausdrücklich und ohne gespeicherten Bericht. |
| Berichtzustandsliste | HTTP-Liste liefert `complete` und `reported-private-verification`; separate Repositoryprobe aus derselben Zipapp erhält nach Wiederöffnung zusätzlich `incomplete` und fehlenden Zustand als `unknown`. Keine Graph-/Reportpayloads in Listenmetadaten. |
| Lokale Instanzsperre | Zweiter echter `serve`-Prozess auf demselben State endet mit Exit 2; erster Dienst und vorhandener Bericht bleiben erreichbar. Kein Nachweis eines weiteren Servers. |
| Atomare lokale Quote | Zwei unabhängige SQLite-Verbindungen aus den tatsächlichen Zipapp-Modulen, separater eigener State: 49 gespeicherte Ergebnisse plus zwei konkurrierende Inserts ergeben genau einen Erfolg, einmal `409 STORAGE_LIMIT`, insgesamt exakt 50. Keine Prüfung mit realen Daten oder verteilten Backends. |
| Status/Zulassung | Graphberechnung `browser`, Profil `single-instance-local-synthetic`, eine HTTP-/Analyseverarbeitung, Backlog 8, Prozesszähler, null wartende Jobs, keine dauerhafte Queue/automatische Wiederholung, Mehrinstanz blockiert. |
| Stop/Wiederanlauf | Zwei Starts, jeweils SIGTERM mit Exit 0 und geschlossener Port; bestätigter Bericht nach Neustart vorhanden, altes Sitzungscookie ungültig, erneute Anmeldung erfolgreich. |
| Bereinigung | Alle eigenen Kinder abgeholt, alle Prüf-States/Beispiele entfernt, eigener Scope inaktiv und Transferverzeichnis entfernt. |

Die neue Unterprobe importiert Repository und Verträge explizit aus der `.pyz`,
nicht aus einer danebenliegenden Repositorykopie. Die Quoteprobe belegt die
lokale Transaktion mit zwei Verbindungen; sie belegt weder globale Quoten noch
eine verteilte Ausführung.

Die Prüfung lief als eigener **transienter Scope** mit effektiv gelesenen
Kernelgrenzen `cpu.max=35000 100000`, `memory.max=536870912`,
`memory.swap.max=0`, `pids.max=16`. Das bleibt unter den dokumentierten bestehenden
Laborbudgets von 35 % eines Kerns, 768.000.000 Bytes und 48 Tasks. Es wurden keine
persistenten Unitdateien angelegt oder fremden Ressourcenlimits geändert.
Beobachtet: eigener Speicherpeak **66.314.240 Bytes**, Taskpeak **5**, Swap **0**,
alle Deltas von `memory.events` einschließlich OOM **0**. Das ist keine Last-,
Kapazitäts- oder Durchsatzzusage.

Eigene Übertragung: `/tmp/aa-browser-debian-abschluss-hhux3f04`, eigener Scope
`aa-browser-abschluss-hhux3f04.scope`. Beide sind beendet/bereinigt. `TMPDIR` lag
innerhalb der Übertragung, damit auch abgebrochene Prüf-States erfasst wären.
Scopezustand und Prozesslisten wurden vor Löschen geprüft; Abfragefehler gelten
nicht als erfolgreiche Bereinigung. Keine produktiven Pfade, vorhandenen Dienste,
Konten, Collector, Schlüssel, Firewall oder Backups wurden dafür aufgerufen oder
verändert. Die SSH-Sitzung hatte UID 0; daraus folgt keine Freigabe für einen
dauerhaften Rootbetrieb des Browserdiensts.

Vorher führte die delegierte Paketprüferrolle einmal die gezielt erweiterte Probe
lokal aus: **46/46**, Python 3.12.13, explizit `sourceClean=false`. Beleg bleibt
unter `dist/package-checks-local-20261017T094900Z/local-package-check.json`
(SHA-256 `12fb9df160225f93ac969f5a8465d89dce68285a5b6598c31f4714530a291b32`).
Dies war Prüferentwicklung, kein sauberes Lieferpaket und kein Debianlauf.
Ruff check/format für beide geänderten Prüfer und `git diff --check` bestanden.
Die unabhängige Leserolle fand vor Ausführung vier konkrete Punkte des
Remoteablaufs; der Builder korrigierte Scopeabfrage, fehlerfesten Abschluss,
eingeschlossenen TMPDIR und Bindung an aktuelle lokale Paketidentität.
Der danach ausgeführte Debianlauf
bestand beim ersten Versuch; keine Wiederholung unveränderter Erfolge.

## Gelesene Altbelege und unabhängige Gegenprüfung

Die Dateien `BROWSER-ARCHITECTURE.md`, `BROWSER-SERVICE.md`,
`BROWSER-DEPLOYMENT.md`, `BROWSER-VERIFICATION.md` und `BROWSER-CONTRACTS.md`
wurden gelesen. Die unabhängige Leserolle las zusätzlich den vollständigen
Grok-Lauf einschließlich aller 53 Eventmeldungen. Der Hauptagent las dessen
vollständiges Urteil aus `run.json`. `status.json` allein ist keine Abnahme.

| Gelesener Nachweis | Einordnung |
|---|---|
| Grok `20261017T072638.620141Z/run.json`, SHA-256 `8b710f298dae2311cf8302bb2e57b9cb4afb5dca5bab9111e11fdabb58eeddb1` | **pass**, `findings=[]`, exakt `57691679…`, lokales synthetisches Profil. Keine neue Grok-Debian-/Produktionsfreigabe. |
| Derselbe vollständige Lauf `events.jsonl`, SHA-256 `65355fd13d2900f5afb9ce13591fc9e0040bbedd9e7b93be820511da6058ced1` | Eigene Gegenproben von Groks Team: 22 Auth-/Modul-/Servicefälle, elf Repository-/Leasefälle, enge HTTP-/Zweiprozessprobe und Node-Syntax/ein Layoutaufruf. Kein damaliger neuer Debian-/Browserlauf. |
| Architekturqueue `status.json`, SHA-256 `e6d85cd205d0a0bac3cdad6985be607af3d88c95698a64f8bfa49a514f49a6d2` | Abschlusszuordnung zum vollständigen Grok-Urteil; keine eigenständige Erfolgsaussage. |
| [Browser-Altbeleg](browser-verification-20261017/final-export/browser-results.json), SHA-256 `2a0e8aa1922d48283f4968f630c9635e967f7c3d50835531d6f877858a3343c1` | 23 positive echte Chromeprüfungen, Version 155.0.8059.84, keine Seitenfehler. Jetzt gelesen; Screenshots Desktop/Demo/Neutral/Privat/390px von der Leserolle angesehen, keine neue Bedienkampagne. |
| [Früherer Debianbeleg](browser-verification-20261017/debian-final.json), SHA-256 `fa6ee6509af8c9991422cc852719564eff6ea4c98fb3bc068b7c99c61526569b` | Nur altes Paket `f9eb9816…` aus `642c8a6…`, 33 Checks. Kein Beweis für den neuen Servercode. |
| [Architekturchecks](browser-architecture-20261017/checks.json), SHA-256 `f0287a2bf9ac4346c99eba2597a51ff624ad0f923d61f80df6dc77c45580f853` | Gelesener lokaler Nachlauf. Tatsächlich zehn Einträge in `sourceSha256`, alle bytegleich; Groks beiläufige Angabe „elf“ ist eine Zählabweichung. |
| Fertige `BETRIEBSVORAUSSETZUNGEN.json`, SHA-256 `b07839bd8aeb77b020d15c6f27978f7d4bbf4dce4b5e7204bbd36eee3a9ccbf0` | Lesende Bestandsaufnahme von Grok, kein Code-Review; relevante bestätigte Abhängigkeiten B-09 bis B-15 übernommen. |

Der vollständige Grok-Lauf liegt unter
`/Users/landjunge/.local/state/agent-bridge/20261017T072638.620141Z/`;
Queue und Betriebsinventur unter den im Nutzerauftrag benannten Pfaden.
Die drei alten Befunde sind entsprechend dem tatsächlichen Urteil behandelt:
R1-1 Listenstatus behoben, R3-1 konkreter Ausbaupfad mit externen Abhängigkeiten,
R3-2 lokale Lease/atomare Quote behoben. Keine blinde Wiederholung der
unveränderten Clientgraph- oder Enginekampagnen.

Navigation, Dashboard, Graph, Details, Suche/Filter, Gruppen, Zoom/Pan und History
sind durch die gelesenen echten Browserbelege nachvollziehbar nutzbar. Alle vier
aktuellen Browserressourcen sind bytegleich zum damaligen geprüften Client;
Graphaufbau, Layout und SVG-Rendering bleiben dort. Der alte neutrale Screenshot
zeigt noch den inzwischen behobenen Listenstatus „Unbekannt“; er ist keine neue
UI-Aufnahme. Der aktuelle Listenstatus wurde jetzt gezielt per Debian-HTTP und
Repositoryprobe geprüft.

Die unabhängige aktuelle Paketgegenprüfung durch die delegierte Leserolle ist
abgeschlossen: alle 33 Payloaddateien gegen Archiv und Git-Quellcommit geprüft,
genau 34 Archiveinträge einschließlich Manifest, keine Extras/Duplikate; sämtliche
23 Produktdateien plus Zipapp-Bootstrap sind bytegleich zum früher von Grok
geprüften Paket und Produktstand. Der unveränderte Runtimehash bestätigt diese
Bindung. Auch Prüfer-/Runner-/Bootstrap-/Tarhash und alle 46 ausgeführten neuen
Debianchecks wurden unabhängig gelesen und mit den lokalen Dateien abgeglichen.
Die Rolle führte selbst kein SSH und keine Tests aus. Eigene Debianausführung,
fremde Altproben und Produkt-/Betriebsfreigabe werden dabei nicht gleichgesetzt. Keine echte
iPhone-/Safari-/Screenreaderprüfung und kein unabhängiger neuer Sicherheits- oder
Produktionsabschluss werden behauptet.

## Konkreter Start- und Bedienweg

Das qualifizierte Paket liegt lokal im oben genannten Worktree. Auf diesem Mac
verwendet man den vorhandenen Interpreter; keine Installation erforderlich:

```sh
cd /Users/landjunge/agent-authority-lab/.worktrees/browser-architecture-20261017T064003Z
AA_BROWSER_DEMO=$(mktemp -d /tmp/aa-browser-vorfuehrung.XXXXXX)
/usr/local/bin/python3.13 -B dist/browser-debian-abschluss/agent-authority-browser.pyz init-synthetic --state "$AA_BROWSER_DEMO/state"
/usr/local/bin/python3.13 -B dist/browser-debian-abschluss/agent-authority-browser.pyz examples --output "$AA_BROWSER_DEMO/examples"
/usr/local/bin/python3.13 -B dist/browser-debian-abschluss/agent-authority-browser.pyz serve --state "$AA_BROWSER_DEMO/state" --port 8873
```

`http://127.0.0.1:8873` öffnen, mit dem einmalig ausgegebenen synthetischen
Alice-/Bob-Kennwort anmelden. „Bericht aufnehmen“, eigenes Source-/Job-Paar,
„Neutrale Einträge“ und passende Datei aus `examples` wählen. Übersicht und Graph
öffnen; Knoten zeigt Details. Suche mit Enter, Filter, Fokus, Zoom/Einpassen und
Zurück bedienen. Explizite Demo und Privatbericht sind getrennte Eingänge.
Die vollständigen Tastatur-/Sprach-/Mobilhinweise stehen in
[BROWSER-SERVICE.md](BROWSER-SERVICE.md). Bei belegtem Port einen freien eigenen
Port wählen; keine fremden Prozesse beenden.

Ctrl+C/SIGTERM beendet nur den eigenen Dienst. Derselbe Paket-/Statepfad startet
ihn erneut, mit erneuter Anmeldung und erhaltenen bestätigten Ergebnissen.
Initialisierung überschreibt keinen vorhandenen State. Lockdatei nicht entfernen.
Unklare Importantwort zuerst anhand der Liste prüfen, nicht automatisch wiederholen.
Eigene synthetische State-/Beispielkopie nach Ende bewusst entfernen; das
qualifizierte Paket und die Belege aufbewahren. Keine produktiven Backups nutzen.
Konsistenter Restore beschädigter realer Daten bleibt ein gesonderter Betriebsvertrag.

Auf Debian ist die qualifizierte temporäre Kopie absichtlich entfernt. Es läuft
dort kein neuer Browserdauerbetrieb. Nach einer späteren konkreten
Bereitstellungsfreigabe gilt derselbe `.pyz`-Start mit vorhandenem `python3`,
eigenem privaten State und Loopbackport. Ein SSH-Tunnel muss identische Browser-
und Zielportnummern benutzen, damit Host/Origin exakt passen. Produktions-UID,
Releasepfad, TLS-/Proxyprofil und Dauerprozess dürfen aus dieser Probe nicht
abgeleitet werden. Der konkrete Bereitstellungsplan bleibt
[BROWSER-DEPLOYMENT.md](BROWSER-DEPLOYMENT.md).

## Abgeschlossener Umfang und präzise offene Abhängigkeiten

Technisch abgeschlossen sind das startbare private Paket, die aktuelle
Linuxqualifikation gegenüber dem früheren Maclauf, gezielte neue Vertragsproben,
Konfiguration sowie Stop-/Wiederanlaufhinweise. Die kleinsten Anschlüsse sind
bereits vorhanden: versionierte `AccessControl`-/`ReportRepository`-/
`ReportAnalysis`-Ports und explizite v2-Source/Job/Adapterbindung. Es war kein
zusätzlicher Produktadapter ohne Gegenvertrag notwendig. Details und konkrete
Abhängigkeiten: [BROWSER-ANSCHLUSS-20261017.md](BROWSER-ANSCHLUSS-20261017.md).

| Offen / blockiert | Konkreter Grund und nächster notwendiger Vertrag |
|---|---|
| Echte Konten | AA-Audience, Identitätsautorität/Sessionbrücke, Subject/Tenant/Owner/Scopes, Ablauf/Widerruf und Rechteversion fehlen. Die heutigen synthetischen Profilclaims müssen mit einem echten Adapter gemeinsam angepasst werden. |
| Reale Quellen | Autorisierte Besitzer-/Objekt-/Jobzuordnung, feste serverseitige Quellen-/Endpointbindung und minimale Dienstrechte fehlen. Keine Browser-URL/-Pfadwahl. |
| Privatdienstvertrauen | Separater vorhandener Reportkey-Pin, geeigneter Verifier und authentisierte Tenant-/Source-/Jobbindung fehlen. Downloadkey und Digest schaffen keinen Vertrauensanker; historischer Body und heutiger Keystatus bleiben getrennt. |
| Reale Speicherung/Restore | Freigegebene Daten/Empfänger, Fristen, Verschlüsselung, Aufbewahrung, konsistenter Sicherungs-/Restore-/Ausfallvertrag fehlen. Keine Löschgarantie aus dem fremden ACK-Vertrag ableiten. |
| Weitere aktive Instanzen | Gemeinsame Auth-/Widerrufs-/Berichts-/Quotenautorität und globale Zulassung fehlen. Lokale SQLite-Dateien, Prozesssitzungen und Statelease sind kein Mehrserverbetrieb. |
| Lastverteilung/Worker/Queue | Erst gemeinsame Zustände und konkrete Besitz-/Commit-/Idempotenz-/Ausfallverträge festlegen; anschließend begrenzten Eingang/Worker/Lastverteiler bedarfsbezogen anbinden. Keine globale Zulassung, dauerhafte Queue oder automatische Wiederholung vorhanden. |
| Dauer-/öffentlicher Betrieb | Betreiber und unprivilegierte UID, feste Release-/Statepfade, geeigneter HTTP-Server, TLS/Origin/Secure-Cookie-/Proxyvertrag, Betriebsprozess und Ressourcenfreigabe fehlen. Kein Deployment erfolgt. |
| Plattformgrenzen | macOS-TCC, Endpoint Security, Apple Events und Writerkontrollen bleiben native Grenzen. Collector-Hardstop und stillgelegte Identität bleiben unberührt. |

Der vorhandene sechsstufige Ausbaupfad in `BROWSER-ARCHITECTURE.md` bleibt erhalten:
gemeinsame Identität/Widerruf, gemeinsame Daten/Quote, gesicherter Eingang,
globale Zulassung/gegebenenfalls eindeutige Queue, konkrete Kapazitätszuordnung,
danach gezielte Integrationstests. Anbieter, Kosten und künftige Versionen sind
ohne Beleg unbekannt. Keine verteilte Universalplattform oder Infrastruktur wurde
errichtet. Unabhängige Paket-/Linuxarbeit ist trotz dieser Abhängigkeiten fertig.

Agent Authority bleibt nach D-012 neben Hilfezentrum, ThreadDesk, Tollgate und
4AllPass ein Beobachtungs-/Auswertungsprodukt. Es erteilt keine Rechte/Budgets,
gibt keine Geheimnisse aus und führt keine fremden Aktionen aus Beobachtungen ab.
Owner-/Scopeprüfung und Datenbegrenzung bleiben serverseitig, Grapharbeit im
Browser. Browserquellen bleiben technisch einsehbar. Native App und fremde
Worktrees wurden erhalten; lokale Commits verwenden ausschließlich den bestehenden
Hook-Opt-out `SKIP_POST_COMMIT_PUSH=1`. Kein Push, Merge nach main/master,
Deployment oder Neustart produktiver Dienste.
