# Browserdienst: tatsächliche Prüfung und Restgrenzen

Auftrag und eigener Worktree vom 17.10.2026. Eingefrorene Ausgangsbasis
`22c4ee9fc479bb6a3df98fcbd786b0f5a7c9fe9b`, Branch
`codex/debian-browser-service-20261017T062735Z`. Keine Zusammenführung fremder
Arbeitsstände. Inventar und Portregeln stehen in [BROWSER-PARITY.md](BROWSER-PARITY.md)
und [BROWSER-CONTRACTS.md](BROWSER-CONTRACTS.md).

## Geprüfter Funktionsumfang

| Prüfung | Tatsächliches Ergebnis / Beleg |
|---|---|
| Neue Python-Projektion/Adapter/Server und relevante bestehende Produktregressionen | **161 bestanden, 0 Fehler, 0 übersprungen**, vorhandenes Python 3.12.13/pytest. [JUnit](browser-verification-20261017/python-tests.xml). Keine gesamte historische Researchsuite behauptet. |
| Browserseitiger Modellport und History | **34 gezielte Node-Checks bestanden**, `node tests/browser_model.cjs --python /usr/local/bin/python3.13`. Trace/Kettenstatus gegen Python-Port, deterministisches Layout/Zyklus, Gruppen/Kanten, Filter, Warntrennung, 100-Snapshotfenster, Back/Forward/Abzweig/reset, große Ordinalwerte, DE/EN. |
| Echter Browser auf finalem UI-Code | **23 Prüfungen bestanden**, Chrome `155.0.8059.84`, frisches Headless-Profil mit vorhandenem Playwright; [Ergebnis](browser-verification-20261017/final-export/browser-results.json). Keine Installation/Downloads. |
| Desktop/iPhone-Breite | Echte Screenshots aufgenommen und angesehen: [Desktop-Graph](browser-verification-20261017/final-export/desktop-demo.png), [neutrale Daten](browser-verification-20261017/final-export/desktop-report.png), [Privatvertrag](browser-verification-20261017/final-export/desktop-private.png), [390px-Ansicht](browser-verification-20261017/final-export/iphone-demo.png). Keine echte iOS-/Safari-Geräteprüfung behauptet. |
| Debian-Paketstart/Stop | **33/33 bestanden** mit unverändert vorhandenem Python **3.13.5**, zwei Prüfkonten, zwei gespeicherte Berichte, zwei Starts. [Erster Debianbeleg](browser-verification-20261017/debian-initial.json) benennt ehrlich `packageSourceClean=false` für den damaligen Zwischenbau. |
| Letztes aus sauberem Commit erzeugtes Lieferpaket | Exakter Quellcommit, Datei-/Runtime-/Pakethashes in `dist/browser/PACKAGE-MANIFEST.json`, `SHA256SUMS` und `debian-final.json`; letzter Beleg wird nach lokalem Commit mit demselben gezielten Paketprüfer erzeugt. Keine Gleichsetzung des Zwischenpakets mit dem Lieferpaket. |
| Quellhygiene | Ruff check/format und `git diff --check` für die neuen/angepassten Dateien bestanden. Syntaxprüfung JS und portable Zipapp-Ressourcen geprüft. Keine Runtimeabhängigkeiten ergänzt. |

Der echte Browser prüfte Anmeldung ohne automatische Demo, neutralen Upload,
richtige vier Graphknoten, auswählbare Details und fremden HTML-Text als reinen
Text. Er prüfte einen echten JSON-Download mit `ordinal=9007199254740993`,
Suche/Filter/Zurück einschließlich Zoom, alle nativen Seiten, sichtbare
Importfehler/leere Quelle, den getrennten `aa-report-v1`-Adapter, explizite Demo,
Gruppenöffnung, kritisches Warnbeispiel, reduzierte Bewegung, Tastatur, DE/EN
einschließlich laufender Meldung, responsive Tabelle, zwei getrennte Cookie-
Kontexte, fremde ID=404 und Abwesenheit privater Daten im Browserstorage.
Keine JavaScript-Seitenfehler. Alle Inhalte waren selbst erzeugt synthetisch.

Die Paketprüfung verwendet keine Browserinstallation auf Debian. Sie prüft
Ressourcen tatsächlich per HTTP aus der Zipapp, anonym=401, Owner-/Scopegrenzen,
CSRF, doppelte JSON-Schlüssel, neutrale Engineauswertung, Privatbericht als
unverifizierte Angabe, Demo nur auf ausdrücklichen GET, Produktionsblockade,
SIGTERM/Portende, einmaligen Neustart mit abgewiesener alter Sitzung und erhaltenem
zugeordnetem Bericht. Der Bericht benennt jeden nicht ausgeführten Check separat;
`passed=true` erfordert alle 33 tatsächlich ausgeführten positiven Checks.

## Gefundene Fehler und Korrekturen

- Die native App startet mit Beispieldaten. Der Dienst startet stattdessen
  geschützt und leer; keine Quelle/kein Importfehler schaltet auf Demo um.
- Native ReportProjection kollidiert bei legitimen Eintrags-IDs wie `task-A1`
  mit erzeugten UI-IDs. Der Port präfigiert nur solche Eintragsknoten mit
  `entry:` und erhält Originalreferenzen/Fingerabdrücke.
- Native Warnknoten können an mehr als 64 gültigen Kollisionsbelegen scheitern.
  Der Port begrenzt sichtbare Beleglisten ausdrücklich (`evidenceOmitted`),
  erhält den vollständigen minimierten Rohbericht und sichtbare Zuordnungen.
- API-/Modellwidersprüche wurden korrigiert: Demo-Warnprüfungen stehen außerhalb
  des Graphvertrags; private Fakten bis 2048 Zeichen passen zum gebundenen Adapter.
- Login/Logout senden explizite JSON-Bodies. Browseruploads senden Original-
  JSON-Text (`rawData`) zur serverseitigen Duplicate-Key-/Typ-/Grenzprüfung,
  statt Mehrdeutigkeiten durch vorheriges `JSON.parse` zu verlieren.
- Neutrale Eingangsordinals dürfen 63 Bit umfassen. Rohbericht und Export
  verwenden deshalb den exakten serverseitigen `graph.reportJSON`-String;
  JavaScript-Number-Rundung verändert weder Download noch Inspectorbeleg.
- Die interne History bewahrt stabile Browserindizes auch nach mehr als 100
  Schritten und stellt vollständige Zustände ohne neue Historyeinträge wieder her.
- Tatsächlich angesehene iPhone-Screenshots zeigten zunächst stark zerbrochene
  Tabellenwörter. Eine fokussierbare horizontal scrollbar begrenzte Tabelle
  korrigiert dies. Laufende Meldung/Kontobezeichnung werden beim Sprachwechsel
  neu übersetzt. Die native Farbpalette wird verwendet.
- Abbrechen/Escape schließen einen noch nicht abgesendeten Import. Während
  synchroner Serveraufnahme bleibt dies gesperrt; eine Prozessunterbrechung wird
  dadurch nicht versprochen.

## Erhaltene fehlgeschlagene Prüfversuche

Keine dieser Proben gilt als bestanden. Die Dateien bleiben als Belege erhalten.

| Versuch | Grund / tatsächlich erreicht |
|---|---|
| [first](browser-verification-20261017/first/browser-results.json) | Prüfer erwartete fehlendes `data-node-id`; nur Leerstart festgehalten. Sein eigener Browser-Close-Fehler unterbrach das finally; der konkrete eigene Restserver erhielt SIGTERM. Prüfer-Cleanup und Selektor wurden korrigiert. Kein Browsercrash. |
| [second](browser-verification-20261017/second/browser-results.json) | Nach Leer-/Fehler-/Navigationsprüfungen blockierte CSP die Eval-basierte Wartefunktion des vorhandenen älteren Playwright. Folgeprüfungen nicht bestanden. |
| [third](browser-verification-20261017/third/browser-results.json) | Detaillierter Prüferfehler belegte CSP-Eval; keine JavaScript-Seitenfehler. |
| [final Zwischenversuch](browser-verification-20261017/final/browser-results.json) | Privatadapter erreicht, dann derselbe Prüfer-Evalfehler bei wartender Demo. Danach eigene begrenzte Python-Wartefunktion über direkte DOM-Auswertung, ohne `unsafe-eval`/CSP-Abschwächung. |

Die anschließenden [qualified](browser-verification-20261017/qualified/browser-results.json),
[final-ui](browser-verification-20261017/final-ui/browser-results.json) und
[final-export](browser-verification-20261017/final-export/browser-results.json)
belegen die jeweiligen Korrekturen. Wiederholungen erfolgten wegen konkreter
Fehler und anschließender Änderungen; keine Absturzschleife oder behauptete
Browsergegenprüfung durch Dritte.

## Grenzen, die ausdrücklich offen oder gesperrt bleiben

- **Echte Konten/Produktionsidentität:** blockiert. Vorhandene Hilfezentrum-
  Sitzung und Bot-Bearer sind kein belegter AA-SSO-/Audience-/Ownervertrag.
  Nur ausdrücklich synthetische lokale Prüfkonten sind startbar.
- **Live-Daten/Privatdienstvertrauen:** blockiert. Der belegte echte GET-Vertrag
  ist integrierbar und synthetisch geprüft; ohne separate Pins/Signaturprüfung
  und Tenant-/Objektzuordnung bleiben Klassifikationen gemeldet und Ketten unbekannt.
  Der Anzeigeadapter ersetzt weder den bestehenden Verifier noch einen Collector.
- **Debian-Collector/Agentenaktionen:** blockiert. Bestehender Hardstop,
  stillgelegte Collectoridentität und Dienstgrenzen unverändert. Keine Aufträge,
  Wiederholungen, Capture-/Writer-Proben oder Berechtigungsänderungen ausgelöst.
- **macOS-APIs:** Plattformgrenze. TCC, Endpoint Security, Apple Events,
  Berechtigungsdialoge und native Writerkontrollen werden nicht im Browser angeboten.
- **Öffentlicher Dauerbetrieb:** nicht bereitgestellt. Nur Loopback, stdlib-
  Prüfserver, synthetischer privater State. TLS/SSO, eigener Produktionsserver,
  reale Aufbewahrung und Betriebsverantwortung benötigen die Entscheidungen aus
  [BROWSER-DEPLOYMENT.md](BROWSER-DEPLOYMENT.md).
- **Visualisierung:** Desktop-Chrome und simulierte iPhone-Breite tatsächlich
  geprüft. Kein echter iPhone-/Safari-/Screenreader-Nachweis und keine externe
  unabhängige Sicherheitsfreigabe. Groks automatisch vorgesehene Teamprüfung
  liegt außerhalb dieses lokalen Abschlussergebnisses.

## Erhaltung und Bereinigung

Native App und alle fremden Worktrees blieben unverändert. Die uncommittete
`EngineBridge.swift`-Ergänzung `-B` wurde nur gelesen, nicht übernommen; Designs/
Belege wurden nicht verschoben. Das eigene Paket nutzt `-B` bei Prüfstarts und
schreibt keinen Bytecode ins App-Bundle. Eigene erzeugte Browser-Bytecodes wurden
entfernt. Eigene Browserprofile, Downloads, Konten, SQLite-States und Serverprozesse
werden vom Prüfer bereinigt; Screenshots/Ergebnisdateien bleiben bewusst als
synthetische Prüfbelege erhalten.

Auf Debian ausschließlich eine mit `mktemp` neu angelegte private Übertragungskopie
unter `/tmp/aa-browser-qualification.*` und eigene untergeordnete Prüfprozesse.
Paketprüfer entfernen State/Beispiele/Prozesse und belegen geschlossene Ports;
Übertragungskopie wird nach Ergebnisabruf ebenfalls entfernt. Keine Datei unter
`/opt/ki-helper-runtime`, `/opt/aa-private` oder produktivem State verändert,
keine Installation, systemd-/Firewalländerung, Neustart fremder Dienste oder
Produktivdatenabfrage.

Der vorhandene lokale Git-post-commit-Hook führt standardmäßig einen Push aus.
Für diesen ausdrücklich lokalen Auftrag wird ausschließlich dessen vorhandene
Opt-out-Variable `SKIP_POST_COMMIT_PUSH=1` beim Commit gesetzt; Hook und globale
Gitkonfiguration bleiben unverändert. Kein Push/Merge/Deployment.
