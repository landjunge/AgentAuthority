# Browserdienst: gezielter Architekturabschluss vom 17.10.2026

Dieser Nachlauf erhält den fertiggestellten Browserdienst und gleicht die später
präzisierten Anforderungen zu Clientgrafik, zusätzlichen Servern und Modulschutz
ab. Die bestätigte Reihenfolge wurde umgesetzt: zuerst Anmeldung und
Rechteprüfung kapseln, danach Berichtsablage austauschbar anbinden. Der vorhandene
Beobachtungskern und der Browsergraph bleiben erhalten. Agent Authority beobachtet
und analysiert; es erteilt keine Rechte oder Budgets und führt keine fremden
Agentenaktionen aus.

Arbeitsumfang bleibt das eigene Entwicklungsworktree. Es wurden keine echten
Konten, Quellen, Produktionsschlüssel, Dienste oder zusätzliche Server angebunden.
Der bestehende Debian-Collector-Hardstop ist keine Abhängigkeit dieser lokalen
Refaktorierung und bleibt unverändert gesperrt. Quellen, Entwicklungsstand und
Produktionsdaten bleiben getrennt. Dieser Stand ist weiterhin ausschließlich
ein privates synthetisches Loopback-Prüfprofil, keine Mehrserverproduktion.

## Clientgrafik: vorhandene Umsetzung erhalten

| Nutzeranforderung | Tatsächlicher Code und Ergebnis |
|---|---|
| Graph aus freigegebenen strukturierten Daten aufbauen | `browser_static/app.js:setDocument`, `visibleGraph` und `clustered` bauen Browserzustand und sichtbare Teilmengen auf. Der Server liefert nur den zuvor berechtigten Bericht und seine begrenzte fachliche Strukturprojektion. |
| Anordnung von Knoten und Kanten im Nutzerbrowser | `graphLayout` in `app.js` berechnet Kahn-Tiefen, deterministische Positionen und das Agentenraster. `renderGraph` berechnet die SVG-Kurven aus diesen Positionen. |
| Gruppierung, Fokus, Filter und Suche lokal | `clustered`, `trace`, `visibleGraph`, `focusChain`, `expandGroup` und die Such-/Filterhandler verändern den lokalen Graphen und lösen lokale Neuberechnung aus. Gruppierungssemantik bleibt entsprechend der vorhandenen Funktionszuordnung für die explizite Demo belegt. |
| Zoom, Pan, Viewport und Zeichnen lokal | `renderGraph`, `fitGraph`, `zoom`, `updateViewport`, Pointer-/Wheelhandler und `ResizeObserver` erzeugen SVG, Minimap und Viewport vollständig im Browser. Dafür erfolgt keine API-Anfrage. |
| Keine nutzerspezifische Layout-/Renderlast auf Debian | `browser_model.decode_report` und `browser_adapter.adapt_private_report` liefern Knoten, Beziehungen, Fakten und Herkunft, keine Layoutkoordinaten, Graphbilder oder Grafikstreams. Der Dienst hat keine Rendering- oder Desktopübernahme-Schnittstelle. |
| Datenrechte weiterhin serverseitig | API und `BrowserService` beziehen die aktuelle Sitzung und den konfigurierten Scope. Das Repository selektiert Owner **und** Quelle/Auftrag/Adapter vor dem Payloadlesen. Browserfilter sind reine Darstellung und begründen keinen Zugriff. |

Die Serverprojektion ist fachliche Beobachtungsauswertung und eine begrenzte
Datenaufbereitung. Sie wird nicht für jede Zoombewegung, Gruppierung oder
Ansichtsänderung erneut aufgerufen. Das vollständige Bedienmodell aus
[BROWSER-PARITY.md](BROWSER-PARITY.md) bleibt bestehen; der Dienst wird nicht auf
ein Graphbild reduziert. Die bereits vorhandenen Begrenzungen und sichtbaren
Auslassungen schützen weiterhin Netzwerk, Serverspeicher und Nutzerbrowser.
Ob später eine automatische oder manuelle Wahl kleinerer Ansichten sinnvoll ist,
bleibt offen; dieser Nachlauf führt dafür keine neue Produktfunktion ein.

## Module, Verantwortung und konkrete Verträge

`browser_contracts.py` definiert die internen Python-Protokolle mit
`CONTRACT_VERSION = 1`. `BrowserService` verwirft unpassende Vertragsversionen.
Dies sind austauschbare lokale Schnittstellen, keine bereits verteilten
Netzwerkdienste. Ausschließlich vertrauenswürdiger Servercode setzt deren
Implementierungen zusammen; Browserdaten wählen keine Klassen oder Endpunkte.

| Modul | Begrenzte Ein-/Ausgabe, Verantwortung und Abhängigkeit |
|---|---|
| `browser_static/app.js`, HTML/CSS/Katalog | Browsernavigation, Graphmodell, lokale Auswahl/Gruppierung, Layout und Rendering; Eingang sind freigegebene JSON-Daten, Ausgang sind DOM/SVG und feste API-Anfragen. Keine serverseitige Berechtigungsentscheidung. |
| `browser.py` | Feste HTTP-Routen und Webressourcen, Host-/Origin-/CSRF-Grenze, begrenztes JSON, Cookies und Antworten. Übergibt serverseitig aufgelöste Principals an `BrowserService`; greift nicht direkt auf Berichtstabellen oder Passworthashes zu. |
| `browser_auth.py`, `AccessControl` | Anmeldung, Sitzung, Ablauf/Widerruf und Source/Job/Adapter-Berechtigung. `refresh` bindet das Sitzungssubjekt und verwirft vom Aufrufer mitgebrachte veraltete Rechte zugunsten der aktuellen geladenen Konfiguration. Nur die explizit synthetische lokale Implementierung ist vorhanden. |
| `browser_service.py`, `BrowserService` | Orchestriert die drei Ports. Prüft Zugriff vor Lesen/Analyse und erneut vor Ergebnisspeicherung. Erzeugt Bericht-ID/Zeit und bindet Ergebnis an Quelle/Auftrag/Adapter. Sitzungstoken werden vor Übergabe an das Datenport entfernt. |
| `browser_analysis.py`, `ReportAnalysis` | Begrenzte synchrone Analyse/Projektion mit Prozesssemaphore und Statuszählern. Verwendet unverändert `Entry`, `Snapshot` und `build_report`; feste Adapter für neutrale Einträge, neutrale Berichte und den getrennten Privatbericht. Keine Grafik, Netzabfrage oder Auftragsausführung. |
| `browser_model.py`, `browser_adapter.py`, vorhandene Quellenadapter | Bestehende explizite Datenverträge, Validierung und fachliche Projektion. Der Privatadapter behauptet weder Signaturprüfung noch Mandantenauthentisierung. Der Verzeichnisleser bleibt ausschließlich lokal durch den Operator konfiguriert. |
| `browser_repository.py`, `ReportRepository` | Immutable Ergebnissnapshots, Owner-/Scope-selektierte Listen/Lesezugriffe, atomare Quote und Insert. Lokale Implementierung ist SQLite; keine Kenntnis von HTTP, Passwörtern, Sitzungen oder Agentenaktionen. |
| `browser_support.py` | Gemeinsame begrenzte JSON-Dekodierung und private lokale Dateiprüfung. Keine dynamische Adapterauflösung oder allgemeine Ausführungsfunktion. |
| `Store` und `StateLease` | Lokaler Composition Root: feste lokale Implementierungen verbinden, eigenes State exklusiv belegen und Ressourcen bei Fehler/Ende freigeben. Keine verteilte Koordination. |

Der HTTP-Vertrag und die vorhandenen Berichtsschemata bleiben erhalten:
`agent-authority-observation-v1`, `agent-authority-observation-report-v1`,
`agent-authority-ui-graph-v1` sowie der gesonderte `aa-private-v1`-/
`aa-report-v1`-Anzeigeadapter. Ihre semantischen Grenzen stehen in
[BROWSER-CONTRACTS.md](BROWSER-CONTRACTS.md). Der neue interne Portvertrag
ersetzt diese Fachverträge nicht. Ein späterer Adapter muss beide Seiten explizit
erfüllen; gleiche Versionsnummern allein belegen weder Sicherheit noch
Netzwerkkompatibilität.

Die neue synthetische Konfiguration `aa-browser-synthetic-config-v2` benennt
erlaubte Adapter je Source/Job-Paar. Neutrale Beispielquellen erlauben
`observations` und `report`, die gesonderte Privatquelle nur
`private-verification`. Unbekannte Adapter oder ein Adapter außerhalb des Scopes
werden vor seinem Aufruf abgewiesen. Bestehendes v1 wird nur für die zwei exakt
bekannten, vom ursprünglichen Initialisierer erzeugten synthetischen Paare je
Nutzer übernommen. Eigene v1-Scopes brauchen eine ausdrückliche v2-Bindung;
ihre Bedeutung wird nicht aus frei gewählten Quellnamen geraten. Die vorhandene
Berichtstabelle wird weiterverwendet. Ein alter Bericht mit nun unzulässiger
Adapterbindung bleibt gespeichert, wird aber nicht ausgegeben.

Der öffentliche Scope bleibt dabei unverändert `{sourceId, jobId}`; die
Adapterpolicy gehört zur serverseitigen Konfiguration. Der Browser übergibt
weiterhin das bestehende explizite Importfeld `kind`. Für diese Bindung wurden
weder JavaScript noch Bedienablauf verändert.

## Modulschutz und Vertrauensgrenzen

Private Repositories, Dateirechte und Betreiberzugang können Zugriff auf
Serverquellen begrenzen. HTML, CSS und JavaScript werden zur Bedienung an den
Nutzer geliefert und bleiben einsehbar. Das Paket veröffentlicht über
`STATIC_FILES` ausschließlich feste Webressourcen, keine Pythonquellen,
Konfigurationsdateien, Schlüssel oder fremden Nutzerberichte. Fremde Texte
werden als Text in DOM/SVG eingesetzt. Dateiaufteilung allein ist keine
Sicherheitsisolation; die heutigen Module laufen mit derselben Prozessidentität.

Die Auswahl eines Berichts wird vor der Payloaddekodierung im Repository nach
Owner, Source/Job und Adapter begrenzt; fremde und unbekannte IDs ergeben 404.
Importe prüfen das erlaubte Paar und dessen Adapter vor der Analyse und erneut
vor dem Insert. `Principal.session_id` bleibt im Auth-/Servicekontext und wird
nicht an das Repository übergeben. Das Repository prüft seine begrenzte
Objektbindung zusätzlich. Ein vom Browser behaupteter Owner, Modulname,
Serverpfad, URL oder Shellbefehl ist kein gültiger Aufrufvertrag. Die Adapter
sind feste Codezweige und führen keine solchen Angaben aus.

Der lokale CLI-Einstieg `import-directory` ist eine gesonderte vertrauenswürdige
Operatorfunktion: Erst Berechtigung prüfen, dann den vom lokalen Operator
benannten bestehenden Reader verwenden. Er ist keine Browserroute. Weder
Dateifingerabdrücke noch ein passend formatierter Privatdienst-Job beweisen
Produktionsidentität. Die fehlende authentisierte Tenant-/Objektbindung und die
getrennte Signaturverifikation bleiben Freigabesperren.

Für spätere Prozess- oder Servertrennung sind feste notwendige Endpunkte,
standardbasierte Dienstidentitäten und minimale Rechte erforderlich. Eine
Dienstidentität erlaubt den Transport zwischen Komponenten; sie ersetzt nicht
die Endnutzer-/Owner-/Scopeentscheidung. Es entstehen weder ein Pluginökosystem
noch ein Lizenzserver, eigener Kryptografiemechanismus oder Kopierschutzversprechen.

## Tatsächlicher Zustand und heutige Schutzgrenzen

| Zustand / Ressource | Heute gespeichert und begrenzt | Folge für weitere Instanzen |
|---|---|---|
| Konten, Passworthashes, Scope-/Adapterbindung | Private `config.json`, beim Start in den Authprozess geladen | Kein gemeinsamer Identitätsdienst und kein Live-Abgleich mit anderen Hosts. Konfigurationsänderung erfordert Neustart; bloßes Kopieren erzeugt keine gemeinsame Autorität. |
| Sitzungen, CSRF, Ablauf, Widerruf | Prozessspeicher; Sitzung hält Subject, Token und Ablauf, Rechte stammen jeweils aus der geladenen Konfiguration | Logout/Widerruf wirkt nur in diesem Authprozess. Neustart verwirft alle Sitzungen. Gemeinsamer autoritativer Widerruf fehlt. |
| Loginfehlversuche und Sitzungsanzahl | Prozessspeicher; zwölf Fehlversuche je Minute und maximal 128 aktive Sitzungen | Keine globalen Mehrinstanzlimits. Weitere Kopien würden diese Grenzen vervielfachen. |
| Berichts-/Quellen-/Auftrags-/Adapterzuordnung | Lokale `reports.sqlite3`; `(owner,id)` als Primärschlüssel, zusätzliche Source/Job/Adapter-Spalten und unveränderter Payloadsnapshot | Gleiche Objekte müssen später über eine gemeinsame Datenautorität eindeutig gebunden werden; unabhängige Datenbankkopien sind kein gemeinsamer Zustand. |
| Ergebnisse und Speicherquote | Lokale SQLite-Transaktion mit `BEGIN IMMEDIATE`, Quotenprüfung und Insert gemeinsam | Atomar über Verbindungen auf dieselbe lokale Datenbank, keine globale Quote über getrennte Hosts/States. |
| Uploads und laufende Importe | Begrenzter Request und Zwischenobjekte im RAM, synchron bis zum Ergebnis; kein Uploadspool | Kein Wiederanlauf, Resume oder verteilter Importbesitz. Prozessende verliert unfertige Analyse; unklar beantworteter Commit darf nicht automatisch wiederholt werden. |
| Verarbeitung und Auslastung | Eine HTTP-Verarbeitung; Analyseport mit einer Semaphore, Prozesszähler für aktiv/abgeschlossen/fehlgeschlagen/bei Belegung abgewiesen | Kein Jobdispatcher, keine dauerhafte Queue, keine hostübergreifende Zulassung oder Lastverteilung. |
| Statebesitz | `StateLease` hält einen exklusiven POSIX-Lock auf `.instance.lock` | Zweiter kooperierender lokaler Dienst mit demselben State wird beim Start abgewiesen. Keine verteilte Lease, kein Netzwerkdateisystemvertrag und keine Sperre gegen kopierte States. |
| Browserzustand | Bericht und Navigation im Speicher des jeweiligen Browsers; nur lokale Darstellungspräferenzen im Browserstorage | Kein serverseitiger Viewport-/Layoutzustand und kein serverseitiges Remote-Rendering. |

Die Lockdatei wird beim Schließen nicht entfernt, damit ein späterer Öffner
keinen noch benutzten Lock-Inode umgehen kann. Prozessende gibt den Kernel-Lock
frei. Diese lokale Sicherung verhindert, dass versehentlich zwei Dienstprozesse
denselben State verwenden und dabei prozesslokale Schutzgrenzen verdoppeln.
Zwei eigenständige Stateverzeichnisse bleiben zwei getrennte synthetische
Prüfumgebungen; daraus folgt keine globale Konten- oder Kapazitätsgrenze.

Konkrete konfigurierte Grenzen sind eine HTTP-Verarbeitung, Socket-Backlog 8,
fünf Sekunden Socketzeitlimit, 8 MiB HTTP-JSON, maximal 30 Strukturebenen und
250.000 Werte. Das Socketzeitlimit ist keine garantierte Gesamtdauer der
Auswertung; der Backlog ist keine dauerhafte Anwendungswarteschlange. Der
Analyseport lehnt einen belegten Verarbeitungsslot unmittelbar mit
`429 ANALYSIS_BUSY` ab. Sein Status unter `/api/status` nennt ausdrücklich
Prozessscope, Zähler, null wartende Jobs, keine dauerhafte Queue und keine
automatische Wiederholung. Weil HTTP heute seriell arbeitet, ist dieser Status
während einer laufenden HTTP-Analyse keine unabhängig erreichbare Betriebsprobe.

Weitere Grenzen: 10.000 neutrale Eingangseinträge, 65.536 Bytes je serialisiertem
Eintrag und die gemeinsame 8-MiB-Eingangsgrenze, Engine-Darstellung maximal 100
Einträge/Aufgaben/Warnungen mit Auslassungsangaben, 24 MiB je gespeicherter
Antwort und je Konto 50 Berichte/64 MiB. SQLite wartet bei Sperren höchstens
die konfigurierten zwei Sekunden und meldet belegte Datenablage als
`503 STORAGE_BUSY`. Die Privatprojektion bleibt zusätzlich auf ihren vorhandenen
engeren Vertrag begrenzt. Dies sind Schutzgrenzen des Prüfprofils, keine
Kapazitätsmessung, Nutzerzahl oder Durchsatzzusage. Clientgrafik beseitigt weder
Netzwerk- noch Datenbank-/RAMkosten.

## Ausfall, Neustart und eindeutige Ergebnisse

Jeder ausdrücklich ausgelöste Import erhält eine neue zufällige Bericht-ID und
einen festen Owner/Source/Job/Adapter-Bezug. Das vorhandene `jobId` bezeichnet
einen berechtigten Berichts-/Quellenbezug, keinen ausführbaren Agentenauftrag.
Erneuter ausdrücklich ausgelöster Import bleibt nach bestehender Semantik ein
neues Ergebnis. Doppelte bereits vorhandene Bericht-ID wird als
`409 REPORT_EXISTS` abgewiesen; bestehende Ergebnisse werden nicht überschrieben.

Die lokale Transaktion schreibt Quote und Ergebnis gemeinsam oder rollt zurück.
Ein bestätigter Commit bleibt bei regulärem Neustart erhalten; Sitzungen und
Prozesszähler gehen verloren. Die spätere Infrastruktur muss Datenträgerausfall,
Backup/Restore, Aufbewahrung und Wiederherstellung separat festlegen. Die
Refaktorierung schafft dafür keinen neuen Betriebsvertrag.

Bei Verbindungsabbruch kann das Ergebnis bereits gespeichert sein, obwohl der
Browser keine Erfolgsantwort sah. Abbrechen oder Browserende beweist keinen
Serverabbruch. Es gibt deshalb keinen automatischen Retry und keinen behaupteten
Exactly-once-Vertrag. Die bestehenden zugeordneten Berichte können nach erneuter
Anmeldung überprüft werden. Ein belastbares späteres Importversuchs-/
Idempotenzprotokoll muss diese Mehrdeutigkeit ausdrücklich auflösen, bevor eine
Queue Wiederaufnahme erlauben darf.

## Konkreter Erweiterungsweg vom Debian-Host zu weiteren Instanzen

Die lokale Schnittstellentrennung ermöglicht zusätzliche Implementierungen,
schließt die folgenden Integrationen aber nicht ab. Anbieter, Kapazitätskosten
und die Entscheidung für konkrete produktive Identitäts-/Speicherdienste sind
offen. Es wurden keine Ressourcen beschafft oder produktiven Systeme verändert.

1. **Eine gemeinsame Identitäts- und Rechteautorität festlegen.** Den vorhandenen
   `AccessControl`-Vertrag mit vereinbartem standardbasiertem Identitätsdienst
   oder belegter Sessionbrücke verbinden. Feste AA-Audience, Subject-/Tenant-/
   Ownerzuordnung, aktuelle Source/Job/Adapterrechte, Ablauf und Widerruf müssen
   über alle Instanzen gleich gelten. Bei Nichterreichbarkeit geschlossen
   ablehnen. Login-/Sitzungslimits gemeinsam durchsetzen; Sticky Sessions allein
   lösen Widerruf und globale Limits nicht. Rechteänderung während einer Analyse
   erfordert im späteren Commitprotokoll eine autoritative Rechteversion oder
   passende atomare Prüfung, damit veraltete Berechtigung kein Ergebnis freigibt.
2. **Berichtsablage gemeinsam autoritativ machen.** Den `ReportRepository`-Port
   an eine geeignete gemeinsame relationale Datenbank anbinden. Owner und
   eindeutige Ergebnis-ID sowie Source/Job/Adapter bleiben verbindliche Schlüssel;
   Auswahl erfolgt vor Payloadzugriff. Quote und Ergebnisbindung müssen in einer
   gemeinsamen Transaktion bestehen bleiben. Lokale SQLite-Dateien über Hosts
   kopieren oder auf ein ungeprüftes Netzwerkfilesystem legen erfüllt dies nicht.
   Eine konkrete Datenmigration einschließlich Konsistenz-/Rollbackprüfung ist
   vor mehreren aktiven API-Instanzen erforderlich.
3. **Ergebnisse und Eingänge kontrolliert speichern.** Für größere getrennte
   Verarbeitung entweder begrenzte Payloads in der gemeinsamen Datenbank oder
   bewusst verwalteten unveränderlichen Ergebnisspeicher mit atomarer
   Metadatenbindung festlegen. Temporäre Uploads benötigen Ownerbindung,
   Größen-/Zeitgrenzen, Aufbewahrung und bereinigbare Zustände. Keine öffentliche
   Objekt-URL und kein vom Browser frei benannter Speicherpfad. Die aktuelle
   Fassung besitzt diesen Upload-/Objektspeicher nicht.
4. **Eingang und Zulassung vor weiterer Parallelität festlegen.** Einen geeigneten
   Produktions-HTTP-Server und verteilbaren Eingang mit TLS, eigener Origin,
   Secure-Cookies und enger Proxy-/Forwarded-Header-Vertrauensgrenze einsetzen.
   Feste Upstreams, Request-/Verbindungsgrenzen und eine begrenzte Eingangswartung
   mit explizitem Gegendruck konfigurieren. Alle Annahme-/Speicher-/Loginlimits
   müssen global gelten, bevor zweite Instanzen Verkehr erhalten. Der jetzige
   Loopbackserver vertraut keinem Produktionsproxy und wird nicht lediglich durch
   Freigabe seiner Bindadresse zur Produktionslösung.
5. **Analyse erst bei Bedarf verteilen.** Den vorhandenen Analyseport an begrenzte
   Worker anschließen. Eine geeignete gemeinsame Auftragsablage braucht einen
   eindeutigen Importversuch mit Owner/Source/Job/Adapter, versionierter
   Eingangsreferenz, atomarer Annahme und transaktionaler Ergebnisbindung.
   Dauerhafte begrenzte Queue, Lease mit Fencing, kontrollierter Workerbesitz
   und globale Zulassung müssen doppelte Verarbeitung beziehungsweise doppelte
   Ergebnisspeicherung verhindern. Abgelaufene oder unklar beendete Versuche
   dürfen keine automatische Wiederholung auslösen, bevor Status-/
   Idempotenzvertrag das erlaubt. Diese Bausteine sind geplant und nicht
   implementiert; sie werden keine allgemeine verteilte Jobplattform oder
   Agentenaktionsschnittstelle.
6. **Dienstgrenzen und Betrieb vor dem Zuschalten prüfen.** Je Prozess/Host eine
   feste Dienstidentität mit minimalen nötigen Rechten, eng benannte Schnittstellen,
   Geheimnisversorgung und geschlossene Fehlerzustände vorsehen. API braucht nur
   autorisierte Daten-/Analysezugänge, Worker nur zugewiesene Eingänge/Ergebnisse;
   keine Komponente erhält pauschal fremde Quellen oder Shellausführung. Readiness
   muss Abhängigkeiten und Schema-/Vertragsversionen prüfen. Beobachtbare globale
   Annahme, aktive Arbeit, Queuealter/-belegung, Ablehnungen und Speicherbelegung
   sowie Instanzausfälle sind vor realem Betrieb erforderlich. Erst danach zweite
   Instanz mit synthetischen Zugriffs-/Widerruf-/Importversuchsproben zuschalten.

Für diesen Ausbau ist folgender **Konfigurationszielvertrag** erforderlich.
Die Tabelle definiert die später gemeinsam festzulegenden Angaben, keine bereits
vorhandenen CLI-Flags, Umgebungsvariablen oder Anbieterintegration. Heute sind
nur die dokumentierten lokalen CLI-Einstellungen wie `--state` und `--port`
implementiert. Unbekannte Anbieter, Kosten und zulässige Kapazitätswerte bleiben
offen.

| Zuständige Komponente | Später ausdrücklich zu konfigurierende und zu prüfende Angaben |
|---|---|
| Release und Composition Root | Freigegebener Release-/Paketdigest, interne Vertragsversion, Daten-/Konfigurationsschema und zulässige kompatible Adapterimplementierung. Inkompatible Versionen verhindern Readiness. |
| Eingang und Browser-API | Eine vereinbarte AA-Origin und Cookie-/CSRF-/Audiencezuordnung über alle API-Instanzen; TLS-Verantwortung, feste Upstreams und exakt erlaubte Proxy-/Forwarded-Headerherkunft. |
| Gemeinsame Autorisierung | Referenz auf den vereinbarten Identitäts-/Sitzungsdienst, AA-Audience, Subject-/Tenant-/Ownerbindung, Scope-/Adapterpolicy sowie gemeinsame Ablauf-/Widerrufsautorität. Ausfallverhalten: keine neue Freigabe aus veralteten lokalen Rechten. |
| Gemeinsame Berichtsablage | Geheimnisreferenz für Datenbankzugang statt Zugangsdaten im Browser/Quellcode, Schemainitialisierung/-version, Owner-/Objektschlüssel, atomare Quotenregel und Transaktions-/Verbindungszeitgrenzen. Die vorhandenen 50-Berichte-/64-MiB-Grenzen sind Quoten je Konto, keine Durchsatzzusage. |
| Quellen und interne Dienste | Feste erlaubte Quellen-/Endpunkt-/Objektzuordnung, jeweilige Dienstidentität, zulässige Gegenstelle und minimale Daten-/Adapterrolle. Dienstrechte werden getrennt von Endnutzerrechten geprüft; Browserwerte wählen keinen Endpunkt. |
| Zulassung und Analyse | Gemeinsame Autorität für globale Annahme, Login-/Sitzungslimits und aktive Arbeit; ausdrücklich begrenzte Workerparallelität, Queuelänge/-bytes, Warte-/Lease-/Auftragszeitgrenzen und Ablehnungszustände. Keine automatische Kapazitätsbuchung. |
| Ergebnis-/Uploadablage und Betrieb | Speicherreferenzen und Berechtigungen, Objekt-/Uploadgrenzen, Aufbewahrung/Bereinigung, Ergebnis-/Importversuchsbindung, Wiederherstellungs- und Mehrdeutigkeitsregeln sowie Readiness-/Auslastungszugriff. |

Ein Prozess- oder Einhostversuch ist kein Nachweis mehrerer realer Server. Vor
gemeinsamer Auth-/Daten-/Zulassungsintegration bleibt die Freigabe mehrerer
produktiver Instanzen gesperrt. Browsernavigation, lokales Graphlayout und
begrenzte Analyse-/API-Arbeit hängen nicht von dieser Infrastrukturentscheidung
ab und konnten unabhängig fertiggestellt werden.

## Abgleich mit dem tatsächlich abgeschlossenen Originalreview

Gelesene Ausgangsbelege sind das Buildergebnis
`/Users/landjunge/agent-bridge/queues/authority-debian-dienst-20261017T062735Z/review/BUILD-RESULT.json`
(`codex_completed`, aktualisiert `2026-10-17T06:27:41Z`) und
`/Users/landjunge/agent-bridge/queues/authority-architekturabschluss-20261017T064003Z/PREVIOUS-REVIEW.json`
(`grok_completed`, aktualisiert `2026-10-17T07:14:35Z`). Das Originalreview
arbeitete mit den drei beauftragten Teamrollen und urteilte
`changes_requested`. Seine folgenden konkreten Befunde sind Grundlage dieses
Nachlaufs; eine neue externe Reviewsession wurde hier nicht gestartet.

| Originalbefund | Gezielte Änderung und zugehöriger Nachweis |
|---|---|
| **R1-1:** Berichtliste liefert keinen gespeicherten Zustand; Auswahl zeigt deshalb alles als unbekannt | `LocalReportRepository.listing` liefert den vorhandenen gespeicherten `metadata.state` nach Owner-/Scope-Selektion und begrenzter Payloaddekodierung mit. `complete`, `incomplete` und `reported-private-verification` bleiben getrennt; fehlende/ungültige Altangabe bleibt `unknown`. Keine neue Analyse und keine Aufwertung des Nachweisstatus. Zugehörige gezielte Repositoryprobe prüft Listenzustände nach Neustart. |
| **R3-1:** Konkreter Erweiterungsweg und passende Trennung fehlen | V1-Ports `AccessControl`, `ReportRepository` und `ReportAnalysis`, getrennter HTTP-/Serviceaufbau und das obige Zustandsinventar mit sechs konkreten Ausbauetappen. Gemeinsame Auth-, Daten-, Speicher-, Zulassungs- und Queueintegration bleibt ausdrücklich ausstehend. |
| **R3-2:** Zwei Prozesse auf derselben SQLite vervielfachen prozesslokale Grenzen und können Quoten überschreiten | `StateLease` verweigert den zweiten lokalen Dienststart mit demselben State. Quote und Insert liegen jetzt gemeinsam unter `BEGIN IMMEDIATE`; SQLite-Belegung hat eine begrenzte Wartezeit und expliziten 503-Fehler. Zugehörige gezielte Repositoryproben prüfen konkurrierende lokale Verbindungen an der 50-Berichte-Grenze sowie Sperre/Freigabe bei zweitem Prozess und Prozessende. Gemeinsame Sitzungen/Widerrufe werden nicht vorgetäuscht: weitere produktive Instanzen bleiben bis zur gemeinsamen Autorität gesperrt. |

Das Originalreview bestätigte Clientlayout/-rendering und die synthetische
Owner-/Scope-/CSRF-Trennung anhand eigener gezielter Gegenproben. Es führte
keinen neuen Debianlauf und keinen echten Mehrserverversuch durch. Diese
Beleggrenzen werden übernommen; Korrekturen benötigen ihre eigenen gezielten
Nachweise und erhalten keine automatische externe Freigabe durch das alte Urteil.

## Umgesetzt, geprüft, vorbereitet und offen

| Stand | Konkrete Abgrenzung |
|---|---|
| **Umgesetzt** | Auth zuerst gekapselt; anschließend Repositoryport und lokale SQLite-Implementierung; feste v1-Portverträge; explizite v2-Adapterbindung mit enger v1-Kompatibilität; Zugriff vor Portaufruf und erneut vor Speicherung; SQL-selektierte Owner-/Source-/Job-/Adaptergrenze; gespeicherter Berichtszustand in der Auswahl; atomare lokale Speicherquote; exklusiver lokaler Statebesitz; begrenzter Analyseport mit Prozessstatus. Browsergraph und Auswertungskern erhalten. |
| **Geprüft: Quellabgleich** | Clientlayout, Gruppierung, Fokus, Filter, Viewport und Rendering anhand des tatsächlichen JavaScript geprüft; Serverprojektion enthält keine Layoutberechnung/Grafikstreams. Statische Ressourcenallowlist und feste Adapterauswahl geprüft. Neue Modul-/Zustandsgrenzen anhand der oben benannten Dateien abgeglichen. |
| **Gezielte aktuelle Laufprüfungen** | 42 gezielte synthetische Prüfungen und 33 lokale Zipapp-Prüfungen bestanden; Paket aus sauberem Runtimecommit `062333d`. Die 42 Modul-/Serviceprüfungen umfassen: 16 Service-, neun Auth-, sechs Modul- und elf Repository-/Leaseprüfungen. R1-1 einschließlich aller drei Listenzustände und R3-2 einschließlich konkurrierender Quoten, begrenztem Busy-Fehler und Prozessende sind damit lokal geprüft. [Ergebnis und Grenzen](BROWSER-VERIFICATION.md). Repositoryproben über zwei lokale Verbindungen oder lokale Prozesse belegen ausschließlich lokale Transaktions-/Leaseeigenschaften. |
| **Gelesene bestehende Belege** | 34 Modellchecks in `tests/browser_model.cjs`, 23 Browserprüfungen in `browser-verification-20261017/final-export/browser-results.json` und 33 Debian-Paketprüfungen in `browser-verification-20261017/debian-final.json` gelesen; unveränderten Clientgraph nicht grundlos neu ausgeführt. Das damalige Debianpaket stammt aus `642c8a61b90a3141c38408c8b9ac0f886a4d1abc` und ist kein Nachweis für den danach geänderten Servercode. |
| **Nur vorbereitet** | Austauschbare Auth-/Daten-/Analyseports und der konkrete Ausbaupfad. Keine fertige gemeinsame Identität, Lastverteilung, dauerhafte Queue, verteilte Lease oder produktive Dienstidentität vorhanden. |
| **Offen mit abhängiger Sperre** | Gemeinsame Identität/Widerruf/Scopes, gemeinsame persistente Daten-/Quoten-/Importversuchsautorität und globale Zulassung fehlen: echte Mehrinstanznutzung gesperrt. Produktionsidentität, reale Quellen, Privatdienstvertrauen, Aufbewahrung und öffentlicher Betrieb behalten die Sperren aus [BROWSER-DEPLOYMENT.md](BROWSER-DEPLOYMENT.md). Unabhängige lokale Bedien-/API-/Modularisierungsarbeit bleibt abgeschlossen. |
| **Externe Reviewabhängigkeit** | Groks ursprüngliches vollständiges Teamreview liegt als `changes_requested` vor und wurde konkret abgeglichen. Der nachgelagerte Review der Korrekturen gehört in die bestehende Queue und muss Clientberechnung, Zugriffsgrenzen, Modulschutz und ehrliche Skalierungsgrenzen bewerten. Dieser Nachlauf behauptet weder dessen Durchführung noch ein bestandenes Urteil. |
