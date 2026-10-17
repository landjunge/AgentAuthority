# Anschlussstand für Konten, Quellen und Privatdienst am 17.10.2026

Gezielter Vertragsabgleich zum Quellstand
`57691679a02c9f2b0738dff77a28c1774de5958e`. Gelesen wurden die beiden vom Auftrag
benannten `AGENTS.md`, die Browser-Architektur-, Dienst-, Deployment-, Vertrags-
und Verifikationsdokumente sowie die unten genannten Implementierungen und
synthetischen Testverträge. Im Worktree liegen keine zusätzlichen
`AGENTS.md`/`PROJECT.md`/`ARCHITECTURE.md`; das benannte
`docs/BROWSER-ARCHITECTURE.md` ist der geltende Browser-Architekturstand.

Zusätzlich gelesen:
`/Users/landjunge/agent-bridge/queues/gesamtabschluss-20261017T084846Z/BETRIEBSVORAUSSETZUNGEN.json`,
Status `grok_completed`, Lauf `20261017T085438.853371Z`. Diese lesende
Bestandsaufnahme bezieht Agent Authority auf denselben Festcommit und ist keine
Abnahme des nachfolgenden Debianabschlusses. Die hier relevanten Abhängigkeiten
sind dort B-09 bis B-15. Betreiberangaben anderer Produkte schaffen weder eine
AA-Identität noch einen AA-Speicher- oder Dienstvertrag.

## Bereits vorhandene kleinste Anschlüsse

| Zweck | Vorhandener konkreter Vertrag | Heute tatsächlich nutzbar |
|---|---|---|
| Anmeldung und Kontozuordnung | `browser_contracts.py:AccessControl` v1 mit `authenticate`, `resolve`, `refresh`, `authorize`, `revoke` | Lokale synthetische Konten. `Principal.subject` wird serverseitig zum Owner; der Import besitzt kein Ownerfeld. Das Sitzungssubjekt und aktuelle geladene Rechte werden erneut geprüft. |
| Quellenzulassung | `Scope(source_id, job_id, adapters)` und `aa-browser-synthetic-config-v2` | Explizite Source-/Job-/Adapterbindung. Neutrale Paare erlauben `observations`/`report`, Privatpaare `private-verification`. Eigene v1-Paare ohne eindeutige v2-Bindung werden abgewiesen. |
| Begrenzte Auswertung | `ReportAnalysis.project(source, job, adapter, data)` v1 | Drei feste Codezweige; keine vom Browser gewählten Module, Endpunkte, Pfade oder ausführbaren Aufträge. |
| Berichtsbesitz und Ablage | `ReportRepository` v1, `BrowserService` und lokale SQLite-Implementierung | Owner und Source/Job/Adapter vor Payloaddekodierung auswählen; Sessiontoken vom Datenport fernhalten; Quote und Insert gemeinsam lokal transaktional ausführen. |
| Privatbericht anzeigen | `adapt_private_report(data, source_id, job_id)` für `aa-private-v1`/`aa-report-v1` | Schema-/Job-/Grenzprüfung und minimierte Anzeige. Kein Netzabruf, keine Signaturprüfung und keine authentisierte Tenantzuordnung. `signature_verification=UNBEKANNT`, `production_integration=blocked` bleiben gesetzt. |

`BrowserService` akzeptiert nur passende Portversionen. Der Composition Root
`Store` setzt ausschließlich die festen lokalen Implementierungen zusammen.
Diese Anschlüsse erfüllen bereits den unabhängig umsetzbaren lokalen Umfang;
zusätzliche produktive Adapter ohne belegten Gegenvertrag würden Identität,
Vertrauen oder Infrastruktur erfinden. Deshalb wurde für diesen Abgleich kein
neuer Adapter und kein verteilter Unterbau ergänzt.

Das gesamte heutige Dienstprofil ist bewusst synthetisch: `session_document`
meldet `synthetic=True`, gespeicherte Metadaten melden `syntheticAccount` und
`accessIdentity=synthetic-private-account`, der Status sperrt Produktivanschlüsse.
Bei einem später freigegebenen echten Identitätsadapter müssen diese
Profilangaben zusammen mit dessen konkretem Vertrag angepasst und geprüft
werden. Allein der Austausch einer Pythonklasse ergibt noch keine reale
Kontenanbindung.

## Konkret offene reale Anschlussverträge

| Blockierter Anschluss | Fehlender Vertrag und benötigter Nachweis | Abhängige Umsetzung nach Entscheidung |
|---|---|---|
| Echte Konten / Hilfezentrum-Zugang | Eigene AA-Audience und Identitätsautorität oder belegte Sessionbrücke; exakte Subject-/Tenant-/Ownerzuordnung; aktuelle Source-/Job-/Adapterrechte; Ablauf, Widerruf und Rechteversion. Ein Hilfezentrum-Cookie, Bot-Bearer oder Link belegt dies nicht. | Konkrete `AccessControl`-Implementierung; geschlossene Ablehnung bei Ausfall; gemeinsame Login-/Sitzungsgrenzen; Widerruf und Berechtigungswechsel auch vor Commit konsistent prüfen. |
| Echte Quelle | Autorisierte Quelle und ihr Besitzer, erlaubte Objekte/Jobs und Adapterversion; fest serverseitig konfigurierter lesender Endpoint oder Operatorpfad; minimale Dienstrechte und Fehler-/Größenvertrag. | Gezielter vorhandener Quellenadapter beziehungsweise fester lesender Abruf. Browserdaten dürfen keine URLs, Pfade oder Dienstidentitäten auswählen. |
| Privatdienstvertrauen | Separat gepinnter vorhandener Report-Public-Key und geeigneter bestehender Verifier; authentisierte Tenant-/Job-/Sourcezuordnung; bestätigte Audience/Domain; heutiger Keystatus getrennt vom historisch signierten Body. | Bestehenden Verifier und feste Objektzuordnung gezielt anbinden. Ein Schlüssel aus dem Ergebnisdownload, eine syntaktisch passende Job-ID oder ein Digest genügt nicht. Bis dahin keine positive Vertrauensaussage. |
| Gemeinsamer Zustand / weitere Instanz | Konkrete gemeinsame Auth-/Widerrufsautorität, relationale Berichtsautorität, Schema-/Migrationsvertrag und atomare globale Quoten; globale Zulassung und gegebenenfalls eindeutiger Importversuchs-/Idempotenzvertrag. | Andere v1-Portimplementierungen mit explizitem Konsistenzvertrag. Zweite aktive Instanz erst nach gemeinsamem Zustand und globalen Limits. SQLite-Kopie, In-Memory-Sitzungen und lokaler POSIX-Lock reichen nicht. |
| Öffentlicher oder dauerhafter Dienst | Benanntes unprivilegiertes Betriebskonto, eigene Origin/TLS, Secure-Cookies, enges Proxy-/Forwarded-Vertrauen, geeigneter HTTP-Server, Release-/Statepfade, Ressourcen und Verantwortlicher. | Separat freigegebener Betrieb nach `BROWSER-DEPLOYMENT.md`; derzeit ausschließlich private synthetische Loopbackbedienung. |
| Reale Berichtsaufbewahrung | Erlaubte Daten und Empfänger, Fristen, Verschlüsselung, Sicherungs-/Restore-/Ausfallvertrag und Umgang mit importierten Kopien. | Reale/private Speicherung erst nach konkret freigegebenem Aufbewahrungsvertrag; Privatdienst-ACK/Löschung gilt nicht automatisch für die Browserkopie. |

Der Ausbaupfad in `BROWSER-ARCHITECTURE.md` bleibt konkret: zuerst gemeinsame
Identität/Widerruf und Berichts-/Quotenautorität, dann abgesicherter Eingang und
globale Zulassung; begrenzte Worker, Queue und Lastverteilung nur bei Bedarf mit
festem Besitz-/Ergebnisvertrag. Er beschreibt offene Umsetzung, keine vorhandene
Mehrserverfreigabe. Anbieter, Kosten und reale Betreiberwerte bleiben offen.

## Synthetische Vertragsbelege und Grenze dieses Abgleichs

Die bestehenden Tests wurden hier gelesen, nicht erneut ausgeführt:

- `tests/test_browser_auth.py` bindet Sitzung und aktuelle Rechte, prüft Widerruf,
  Ablauf, Source/Job/Adapter gemeinsam sowie enge v1-Kompatibilität.
- `tests/test_browser_modules.py` verhindert Portaufrufe bei verweigertem Scope,
  Commit nach Widerruf während der Analyse, Auth-Fallback und Sessiontokens im
  Datenport; inkompatible Portversionen werden abgewiesen.
- `tests/test_browser_repository.py` prüft Auswahl vor Payloaddekodierung,
  Berichtslistenzustände nach Neustart, atomare lokale Quote und Statelease.
- `tests/test_browser_adapter.py` trennt historische Berichtsdaten vom heutigen
  unsignierten Keystatus; synthetische Nullbyte-Signaturen werden nicht als
  verifiziert ausgegeben. Fehlende Quellen bleiben fehlend.

`BROWSER-VERIFICATION.md` dokumentiert dazu die alten lokalen Ausführungen. Dieser
Abgleich ist Quell-/Vertragslektüre und Dokumentation, kein neuer Testlauf, keine
unabhängige Produktfreigabe und kein Debianbeleg. Die tatsächliche aktuelle
Debianausführung und Paketidentität gehören gesondert in den Debianabschluss.

D-012 bleibt erhalten: Agent Authority beobachtet und analysiert. Aus einer
Beobachtung entstehen keine Rechte, Budgets, Geheimnisse oder fremden Aktionen.
Collector-Hardstop und Diensttrennung bleiben unverändert. Graphaufbau, Layout,
Filter, Zoom und Rendering bleiben im Nutzerbrowser; Owner-/Scopeentscheidung
und Datenbegrenzung bleiben serverseitig. Auslieferbares JavaScript bleibt
einsehbar, ein Kopierschutzversprechen besteht nicht.
