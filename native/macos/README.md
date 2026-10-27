# Agent Authority für macOS

Native Beobachtungsanwendung auf Basis von master `9eda80d` und freigegebenem
Entwurf. Geteiltes AppKit-Fenster, kompaktes Dashboard, Graph, Inspektor,
Belegtabellen, deutsche/englische Lokalisierung, ausschließlich lesende
Produkteingabe und gesonderter macOS-Testhost. Python-Produktengine und
historisches Labor bleiben unverändert.

## Bauen und öffnen

Erforderlich sind Xcode/Swift 5.9 oder neuer und Python 3.12 für Bauwerkzeuge.
Der bereitgestellte Laufzeitdownload ist auf Intel-Macs gepinnt. Anwendungsziel
und native Helfer verwenden macOS 12; die eingebettete Intel-Python-Laufzeit
zielt auf 10.15.

```sh
cd native/macos
python3.12 scripts/fetch_runtime.py
python3.12 scripts/build_app.py
open "build/Agent Authority.app"
```

Das Bauverzeichnis ist von Git ausgeschlossen. Es enthält die Anwendung mit
verschiebbarer Python-Laufzeit, unveränderten `agent_authority`-Modulen,
nativer Prozessprobe, kontrolliertem Schreiber und kompilierter
Beobachter-Systemerweiterung. Die gebaute Anwendung benötigt weder pip-
Installation noch Terminalprozess oder Projektcheckout. Ein externer
Python 3.12+-Interpreter kann ausdrücklich in den Einstellungen gewählt werden.

Der Standardbuild ist **ad hoc für lokale Entwicklung signiert**. Er ist nicht
notarisiert und kann keinen Endpoint-Security-Kollektor aktivieren.
Datenschutzfreigaben sind an die ausführende signierte Komponente gebunden;
erneutes Bauen kann eine neue Nutzerzustimmung erfordern.

## Reale Eingaben verwenden

Einen Ordner mit `agent-authority-observation-v1`-JSON-Dateien und dessen
Quellkennung wählen. Die Anwendung startet ihren eigenen begrenzten Leseprozess
und zeigt den neutralen Bericht. Sie schreibt nie in die Quelle. Quellenlesen
hat eine überwachte Frist von 30 Sekunden, begrenzte Ausgabe, Abbruchmöglichkeit
und die unabhängigen Eingabegrenzen der vorhandenen Engine. Anzeigeverkürzungen
im Bericht werden getrennt von der Vollständigkeit des Lesens angezeigt.
Gespeicherte JSON-Berichte vom Typ `agent-authority-observation-report-v1`
lassen sich ebenfalls öffnen.

Meldungen sind gemeldete Einträge. Sie beweisen weder Agenten, Befugnisse,
Delegation, Abschluss noch externe Wirkung. Strukturelle Warnungen sind
wählbare Belegknoten. Die anfängliche 50-Agenten-Probe ist ausdrücklich synthetisch.

Graphmodi: fokussierte Kette, kompakte Agentenübersicht, zusammengefasste Zweige.
Ein Cluster wird per Doppelklick aufgeklappt. Ein-/ausgehende Gruppenbeziehungen
und Belegreferenzen bleiben im Modell. Darüberfahren zeigt vollständige
Knotenfakten. Die Auswahl erhält die zugehörige Zuordnungskette; Rohdaten sind
markierbar. Große Proben werden oberhalb von 80 Agenten automatisch gruppiert.
Der Graph wird bedarfsgesteuert mit Begrenzung auf sichtbare Knoten und
räumlicher Trefferprüfung gezeichnet. Keine periodische Animation oder
ständiger GPU-Effekt. Tabellen und Inspektor verwenden überlagerte Scrollleisten.

## Lokalisierung

`AuthorityCore/Resources/Strings.json` enthält alle eigenen UI-Texte auf Deutsch
und Englisch. Stabile Schlüssel, vollständige Kataloge und sichtbare Marker für
unbekannte Schlüssel folgen dem geprüften ThreadDesk-Prinzip, ohne dessen Code,
Einstellungen, Terminologie oder Architektur zu importieren. Sprachpriorität:
ausdrückliches Befehlsargument/Anwendungsauswahl, gespeicherte App-Einstellung,
Agent-Authority-/Locale-Umgebung, erste unterstützte bevorzugte macOS-Sprache,
danach Deutsch. `C`/`POSIX` werden übersprungen. Sprache und Erscheinungsbild
lassen sich ohne Neustart umschalten. Systemdatenschutzdialoge werden weiterhin
von macOS verantwortet und lokalisiert.

## macOS-Testhost und reale externe Voraussetzungen

Der Testhost implementiert native Ordnerauswahl, Bedienungshilfenprüfung/-abfrage,
Vorprüfung/-anforderung der Bildschirmaufnahme, Apple-Events-Zustimmung je
gewählter Zielanwendung, versionsbezogene Links zu Festplattenvollzugriff und
Systemerweiterungsaktivierung über `OSSystemExtensionRequest`. Er verändert
keine TCC-Datenbank, setzt keine Rechte zurück, deaktiviert SIP nicht und
startet Hauptanwendung oder Testschreiber nicht als root. Die lokale Prozessprobe
erfasst eigene Prozessinstanzmetadaten im Anwendungskontext; sie gilt nicht als
unabhängiger Schreiberbeweis.

Die Systemerweiterung verwendet nur ES-NOTIFY-Ereignisse für Schreiben,
Schließen, Fork, Exec und Exit. Ihre XPC-Schnittstelle hat vier feste
Lese-/Bereichsoperationen, begrenztes JSON, endliche Bereichslebensdauer und
gegenseitige, vom Kernel erzwungene Codesignaturanforderungen unter macOS 12.
Keine PID-basierte IPC-Authentifizierung oder beliebige root-Befehle.
Ereignisse enthalten keine Pfade, argv, Umgebungen oder Dateiinhalte.
Gewählte gehaltene Dateiobjekte, Eigentümer-UID, Prozessstart, PID-Version,
Bootkontext, Lebenszyklus, Kernelsequenzlücken, nicht monotone Folgen und lokale
Pufferverluste bleiben getrennt.

Sieben Starts setzen sechs Kontrollen um: A schreibt, B bleibt untätig,
C schreibt eine andere Datei, Kindprozess schreibt, gefälschte PID-Behauptung und
zwei aufeinanderfolgende Schreiber. Der Kollektor muss tatsächlich verbunden
sein. Qualifikation benötigt passende Kernelinstanz-/Lebenszyklusbelege,
bekannte Verlustkontrollen und die erwartete Schreibzahl. Fehlende
Voraussetzungen oder Ereignisse ergeben UNKNOWN; ein nachgebildeter Kanal
liefert keinen Beweis. Anbieter-/Modellidentität und dauerhafte Dateiwirkungen
bleiben auch bei erfolgreichen Kontrollen UNKNOWN. Minimierte Ereignisse
lassen sich im Graph untersuchen und exportieren.

Zum Aktivieren sind eine Apple-genehmigte Endpoint-Security-Berechtigung,
Developer-ID-Identität und passende Bereitstellungsprofile nötig. In der
dokumentierten Sitzung gab es **keine gültige Signierungsidentität**. Kein
privilegierter Live-Kollektor und keine Schreiberbatterie wurden als ausgeführt
behauptet oder gestartet. Mit tatsächlich verfügbaren Zugangsdaten bauen:

```sh
python3.12 scripts/build_app.py --sign "Developer ID Application: YOUR IDENTITY" \
  --team YOURTEAMID --host-profile /path/host.provisionprofile \
  --collector-profile /path/collector.provisionprofile
```

Die signierte Anwendung unter `/Applications` installieren, die Distribution mit
Apples Werkzeugen notarisieren, ihre Erweiterung aktivieren und **dem Kollektor
selbst** Festplattenvollzugriff erteilen. Die Freigabe der Hauptanwendung ersetzt
dies nicht. Das tatsächliche ES-Initialisierungsergebnis unterscheidet
Privilegien-, Entitlement- und TCC-Fehler. Diese Voraussetzungen lassen sich
nicht durch einen Buildschalter oder gewöhnliche Nutzerzustimmung allein erzeugen.

Offizielle Quellen: [Apple-ES-Beispiel](https://developer.apple.com/documentation/endpointsecurity/monitoring-system-events-with-endpoint-security),
[ES-Berechtigung](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.endpoint-security.client),
[XPC-Gegenstellenanforderung](https://developer.apple.com/documentation/xpc/xpc_connection_set_peer_code_signing_requirement),
[SIP-Laufzeitgrenzen](https://developer.apple.com/library/archive/documentation/Security/Conceptual/System_Integrity_Protection_Guide/RuntimeProtections/RuntimeProtections.html).
API-Deklarationen wurden auch in installierten Xcode 16-/SDK 15-Headern geprüft.

## Überprüfung

```sh
swift test
python3.12 scripts/check_sources.py
```

Native Bildschirmaufnahmen und Kurzprüfungen stehen unter
`docs/native-macos-20261012`. Der Momentaufnahmemodus erfasst die eigene native
Ansicht; er benötigt keine Bildschirmaufnahmefreigabe und erfasst keine anderen
Anwendungen. Er kann 2560×1440 logische bzw. 5120×2880 Bildpunkte darstellen, ohne die
Bildschirmeinstellungen des Nutzers zu verändern:

```sh
"build/Agent Authority.app/Contents/MacOS/AgentAuthorityMac" \
  --lang de --theme dark --size 2560x1440 --graph-mode 1 \
  --snapshot /tmp/agent-authority-native-5k.png
```

Tatsächliche UI-Prüfungen liefen auf einem R9-M380-/2-GB-Rechner unter macOS 15.7.4.
macOS 12-Kompatibilität wird durch API-Verfügbarkeit und Mach-O-Zielversionen
geprüft; ein echter Monterey-Lauf bleibt erforderlich. Das lokale Paket ist
Intel; Apple-Silicon-Auslieferung benötigt entsprechende Laufzeit und Signierung.

## Zurücknavigation und getrennte Warndemonstration

Die sichtbare Zurückschaltfläche stellt eine vorige fokussierte Ansicht mit
Graphmodus, Kettenanker, Auswahl, Belegfilter, Suche, aufgeklappten Gruppen und
exaktem Zoom/Verschiebung wieder her. Fokus, Modus, Filter und Gruppenöffnung
werden als Navigation erfasst; Texteingabe, Zoom und Verschiebung allein nicht.
Wiederherstellung erzeugt weder neuen Eintrag noch automatische Ansichtsgröße.
Austausch des Quelldokuments leert den Verlauf, auch bei Aktualisierung.

Warnungen sind von `ProofStatus` und dessen unveränderter Palette getrennt.
Das klar als synthetisch markierte Warnmenü bietet Information, erhöhte
Aufmerksamkeit, Warnung, kritisch, nicht bewertbar und einen ausdrücklich
geprüften unauffälligen Fall. Der Inspektor zeigt Grund, Bewertbarkeit,
Knoten/Beziehung, Zeit, Quelle und Belegreferenzen. Fehlende Referenzen bleiben
unbekannt. Kritische Meldungen bleiben dauerhaft auswählbar. Diese Testdaten
sind kein Teil von Engine-Berichten oder Belegexporten. Importierte Berichte
und Kernelbeobachtungen haben keine Warnbewertung und bleiben neutral/nicht
bewertbar; keine produktive Risikoerkennung oder Sicherheitszusage implementiert.

Nur sichtbare warnende/kritische Knotenränder animieren in lokalen Core-Animation-
Ebenen: Hin-/Rückläufe mit 2,8/1,8 Sekunden. Außerhalb der Ansicht oder bei verdecktem/
minimiertem Fenster stoppen sie. Der Graph hat keinen Animationszeichentimer und
kein wiederholtes Layout. Die Einstellung für Warnpulse wird gespeichert;
die offizielle NSWorkspace-Einstellung zur Bewegungsreduzierung hat stets
Vorrang. Statische Symbole, Farben, Beschriftungen und kritische Meldung bleiben.
Blau/Orange verwenden native Systemfarben; das vorhandene von ThreadDesk
abgeleitete Bernstein/Rot und alle Belegfarben bleiben unverändert.

In einer angemeldeten grafischen macOS-Sitzung die Prüfungen des tatsächlichen
Controllers ausführen:

```sh
python3.12 scripts/check_ui_regressions.py \
  --executable "build/navigation-warnings-review/Agent Authority.app/Contents/MacOS/AgentAuthorityMac" \
  --output /tmp/authority-ui-regression
```

Der Prüflauf untersucht Deutsch 1680×960 und Englisch 1150×730, scheitert an jeder
fehlgeschlagenen Zusicherung und startet keine Berechtigungsdialoge oder
Experimente. Neue Einheitstests prüfen Verlauf, Bewertbarkeit, Trennung
synthetischer/realer Daten und Bewegungsregeln. Ergebnisse und geprüfte native
Aufnahmen stehen unter `docs/native-ui-navigation-warnings-20261012`.
`--reduce-motion` erzwingt nur Reduzierung für Aufnahmediagnostik; es kann die
Systemeinstellung nicht ausschalten. Die tatsächliche Systemeinstellung wurde
bei dieser Arbeit gelesen, nicht verändert.

## Untersuchung des normalen Starts

Der beim normalen Prüfstart gemeldete leere Graph ließ sich bei späteren
kontrollierten Starts nicht reproduzieren. Der ursprünglich fehlerhafte Prozess
war bereits beendet; eine bestätigte Korrektur dieses ursprünglichen Symptoms
bleibt offen. Normale Launch-Services-Starts ohne Diagnoseargumente,
Seitenleistennavigation und gleichzeitiger Betrieb mit dem älteren Bundle wurden
mit vorhandener autorisierter Bedienungshilfennutzung und echten WindowServer-
Aufnahmen geprüft, getrennt von Bitmapdiagnostik. Ergebnisse:
`docs/native-ui-start-fix-20261012`.

Neue AppKit-XCTest-Fälle umfassen erstmaliges Laden und Anwendungsstart ohne
ausdrücklichen Neuaufbau, Seitenleistennavigation, getrennte Meldungen für leere
Quellen/Filter und passive Diagnostik, die fehlende Ansichten nicht laden darf.
Vorhandene Zurück-/Warnlogik und Belegfarben bleiben erhalten. Leere Quellen
haben eine eigene Erklärung und führen nie automatisch zu synthetischen Daten.

Ein Prüfbuild kann sich sichtbar kennzeichnen und dasselbe Produkt bleiben:

```sh
python3.12 scripts/build_app.py --output build/navigation-warnings-review \
  --review-label startup-check-20261012
```

Zur Erfassung eines künftig fehlerhaften Zustands das genaue Bundle mit dem
optionalen Argument `--normal-state-json /tmp/authority-live-state.json` starten.
Für 30 Sekunden zeichnet die Anwendung passiv Quelle, Filter, Graphmodus,
Auswahl, Geometrie, Ansichtsbereich, Anzahl der Zeichenvorgänge, Verlauf und Animationszustand
auf. Sie baut nicht neu, führt kein Layout/Anpassen/Rendern aus, ändert keine
Einstellungen und beendet die Anwendung nicht. Diagnoseereignisse gehen nur
mit diesem Argument nach stdout; ohne es laufen weder Beobachter noch
Ereignisprotokollierung. Die Untersuchung erprobte auch echte Menüaktionen,
Zoom, Mausverschiebung und drei Zurückschritte. Automatisierung muss vor der
nächsten Zoomaktion auf den abgeschlossenen Menüfokus warten. Statische
Aufnahmevergleiche behaupten keine durchgängige manuelle Sichtprüfung laufender Animationen.
