# Agent Authority als privater Browserdienst

Diese Dienstfassung überträgt die vorhandene native App auf eine eigenständige
Browser-/Python-Oberfläche. Sie ist lokal startbar, benötigt keine Drittanbieter-
Runtimepakete und läuft unabhängig vom Mac. Freigegeben ist ausschließlich der
private synthetische Prüfmodus. Veröffentlichung, echte Konten-/Datenanbindung,
Collectoraktivierung und Agentenaktionen sind nicht Bestandteil dieser Fassung.
Agent Authority bleibt Beobachtung und Analyse gemäß D-012.

## Sofortstart im eigenen Worktree

Python >=3.12 ist erforderlich. Auf dem Zielhost wurde Python 3.13.5 bestätigt.
Die Befehle installieren nichts, erzeugen nur einen neuen privaten eigenen State
und binden ausschließlich Loopback. Vorhandene Verzeichnisse werden beim
Initialisieren nicht überschrieben.

```sh
python3.13 -B -m agent_authority.browser init-synthetic --state /tmp/aa-browser-mein-test
python3.13 -B -m agent_authority.browser examples --output /tmp/aa-browser-meine-beispiele
python3.13 -B -m agent_authority.browser serve --state /tmp/aa-browser-mein-test --port 8873
```

`http://127.0.0.1:8873` im Browser öffnen. Bei Initialisierung werden einmalig
zufällige Kennwörter für **alice** und **bob** angezeigt. Das sind ausdrücklich
synthetische Prüfkonten, keine vorhandenen Produktionsnutzer. Gespeichert werden
nur gesalzene scrypt-Hashes. Keine Anmeldung erzeugt Beispielberichte.
Mit Ctrl+C oder SIGTERM endet der eigene Prozess; Sitzungen verfallen dabei.
Der private State bleibt zur erneuten Bedienung erhalten. Eigene Testverzeichnisse
nach Ende bewusst entfernen; sie gehören nicht zum Quellpaket.

Bei Mac-Umgebungen mit älterem `python3` den vorhandenen Interpreter ausdrücklich
wählen, z.B. `/usr/local/bin/python3.13`. Kein Python im App-Bundle wird verändert.

## Paket erzeugen und außerhalb des Repositories starten

```sh
python3.13 -B scripts/package_browser.py --output dist/browser
python3.13 -B dist/browser/agent-authority-browser.pyz --help
python3.13 -B dist/browser/agent-authority-browser.pyz init-synthetic --state /tmp/aa-paket-mein-test
python3.13 -B dist/browser/agent-authority-browser.pyz serve --state /tmp/aa-paket-mein-test --port 8873
```

Die Zipapp enthält Engine, Server, DE/EN-Ressourcen und statische UI, keine
Kundendaten, Credentials, Research-Runner, native App oder externen Netzressourcen.
`PACKAGE-MANIFEST.json` nennt Quellcommit, sauberen/unsauberen Quellstand und
SHA-256 jeder enthaltenen Quelldatei; `SHA256SUMS` bindet das fertige Paket.
Ein Paket aus unsauberem Stand ist ausdrücklich als solches gekennzeichnet.
Der Build ist bei identischem Quellcommit/-inhalt bytegleich reproduzierbar.
Die bestehende Python-Paketkonfiguration nimmt die UI-Ressourcen und den
zusätzlichen Einstiegspunkt `agent-authority-browser` ebenfalls auf. Eine
Wheelinstallation wurde für diesen Auftrag nicht benötigt oder ausgeführt.

## Bedienung

1. Anmelden, dann einen zugeordneten Bericht wählen oder **Bericht aufnehmen**.
   Quelle/Auftrag bilden ein fest konfiguriertes Paar. Für neutrale Beispiele
   `synthetic-alice / test-alice` und „Neutrale Einträge“ wählen, dann die Datei
   `SYNTHETIC-alice-observations.json`. Bob besitzt seine getrennten Paare.
2. Die vorhandene Engine berechnet Aufgabenaliase, Zähler und strukturelle
   Warnungen. Übersicht und Graph zeigen Herkunft und Vollständigkeit; Identität,
   tatsächliche Wirkung und globale Abdeckung bleiben unbekannt.
3. Graph anklicken oder mit Pfeiltasten auswählen. Inspector zeigt Fakten,
   Belege, Beziehungen, Herkunftskette und Rohdaten. Suche mit Enter abschließen,
   Filter wählen, Kette fokussieren, zoomen, ziehen und einpassen. Zurück stellt
   Ansicht, Auswahl, Filter, Suche, Gruppen und Viewport wieder her.
4. „Demo ausdrücklich öffnen“ lädt ausschließlich synthetische Agentenketten.
   Agenten- und Gruppenansicht, Gruppenöffnung und sechs Warnzustände entsprechen
   dem nativen Modell. Diese Warnbeispiele sind keine Live-Risikoanalyse.
5. Für den Privatdienst das Paar `synthetic-private-alice / <Hex-Auftrag>` wählen,
   „Privatdienst-Verifikationsbericht“ und `SYNTHETIC-alice-private-report.json`.
   Diese Datei trägt den echten GET-Vertrag, aber ausdrücklich erfundene
   Testwerte und eine ungültige Nullbyte-Signatur. Der Anzeigeadapter macht daraus
   keinen neutralen Produktbericht und keinen verifizierten Befund.
6. Einstellungen bieten DE/EN/System und Hell/Dunkel/System. Sprache/Darstellung
   sind die einzigen gespeicherten Browserpräferenzen. Native Betriebssystem-
   Rechte und Collector-/Writeraktionen werden auf „Dienst & Adapter“ erklärt.

Tastatur: Tab für Bedienelemente, Enter für Suche/Kettenfokus/Gruppe, Pfeiltasten
im Graph zur Auswahl, +/- für Zoom, 0 zum Einpassen, Alt+Links für interne
Zurücknavigation, Strg/⌘+F für die Graphsuche. Auf schmalen Fenstern stehen
Navigation und Inspector über ihre Schaltflächen zur Verfügung. Reduzierte
Bewegung des Systems hat Vorrang vor synthetischem Warnpulsieren.

## Quellen und Zugriff

HTTP Basic nach RFC 7617 dient nur der Anmeldung am ausdrücklich privaten
Loopbackdienst. Danach gelten zufällige, ausschließlich serverseitig gehaltene
30-Minuten-Sitzungen mit HttpOnly/SameSite=Strict-Cookie. Mutationen verlangen
CSRF-Token, vorhandene Origin muss exakt passen. Dieses HTTP-Profil setzt
Loopback oder einen SSH-Tunnel voraus; es ist keine öffentliche TLS-/SSO-Lösung.
Der Dienst kann nicht auf einer öffentlichen Adresse gestartet werden.

Owner **und** Quellen-/Auftragspaar begrenzen jeden Berichtszugriff serverseitig.
Fremde und unbekannte IDs ergeben identisch 404. Manipulierte Source-/Job-Paare
ergeben 403. IDs, URLs, Browserpfade und Freitext begründen keinen Zugriff.
Berichte und Passwörter landen nicht in Browserstorage; Datenantworten tragen
`no-store`. Fremdtexte erscheinen über DOM-Text, niemals als HTML oder Skript.

Import: maximal 8 MiB HTTP-JSON, keine doppelten Schlüssel/NaN, maximal 30 Ebenen
und 250.000 Werte. Neutrale Aufnahmen maximal 10.000 Einträge/65.536 Bytes pro
serialisiertem Eintrag. Darstellungsbericht maximal 100 Einträge/Aufgaben/
Warnungen mit sichtbaren Auslassungen. Privatbericht zusätzlich 64 KiB/12 Ebenen.
Pro Prüfkonto maximal 50 Berichte und 64 MiB gespeicherte Ausgaben. Sitzungen
maximal 128, Loginfehlversuche maximal zwölf pro Minute, Socketzeitlimit fünf
Sekunden, eine HTTP-Verarbeitung gleichzeitig. Diese Grenzen sind für die
private Prüfung bestimmt, kein Last-/Internetfreigabenachweis.

Neutrale Upload-Einträge werden mit den bestehenden `Entry`, `Snapshot` und
`build_report` ausgewertet. Ihr SHA-256 bezieht sich auf die dokumentierte
UTF-8-Importserialisierung (`json.dumps`, `ensure_ascii=False`, kompakte
Trennzeichen), nicht auf unbekannte Originaldateibytes. Diese Herkunft steht
in den Metadaten. Fertige Berichte bleiben unbestätigte Berichtsangaben.

Ein Operator kann den bestehenden sicheren Dateiadapter weiterverwenden:

```sh
python3.13 -B -m agent_authority.browser import-directory \
  --state /tmp/aa-browser-mein-test --user alice \
  --source-id synthetic-alice --job-id test-alice --input /pfad/zur/eigenen/neutralen/quelle
```

Nur der lokale Operator wählt dabei ein Verzeichnis; die Browser-API nimmt
keinen Serverpfad an. Der bestehende begrenzte Reader und die unveränderte
Engine liefern auch bei fehlender Quelle einen ausdrücklich unvollständigen
Bericht. Das ist keine erfolgreiche Quellaufnahme.

## Restgrenzen und weitere Bereitstellung

Die vollständige Funktionszuordnung steht in [BROWSER-PARITY.md](BROWSER-PARITY.md),
die belegten Schnittstellen in [BROWSER-CONTRACTS.md](BROWSER-CONTRACTS.md),
der konkrete spätere Bereitstellungsablauf in [BROWSER-DEPLOYMENT.md](BROWSER-DEPLOYMENT.md).
Prüfungen, Fehlerkorrekturen und offene Punkte werden in
[BROWSER-VERIFICATION.md](BROWSER-VERIFICATION.md) nach tatsächlichem Ergebnis
festgehalten. Ein lokaler Dienstabschluss ist keine Produktionsfreigabe.
