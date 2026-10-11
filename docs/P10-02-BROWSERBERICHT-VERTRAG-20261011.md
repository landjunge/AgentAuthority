# P10-02: lokale Browseransicht der Beobachterpreview

Vorabvertrag auf Master 9c07cb5fded0600a4914bad894a319cd3c1db6ca.
Nutzerauftrag: „sinnvoll weiter“ nach Integration von P10-01. Die optionale
Anzeigepräferenz wurde erfragt; ohne andere Vorgabe folgt die lokale
Browseransicht als kleiner eigener Produktschritt. P10-01 ist in WB1715
inklusive unabhängiger Quellen-/Integrationsgegenprüfung abgeschlossen.

## Ziel und Bedienung

Das installierte Kommando erhält zusätzlich `--format html`. Es gibt einen
vollständigen deutschen HTML-Bericht auf stdout aus. Der Anwender kann ihn
mit einer ausdrücklichen Shell-Umleitung in einer gewünschten Datei speichern
und im Browser öffnen. Das Programm schreibt keinen Bericht automatisch,
öffnet keinen Browser und startet keinen Server oder Hintergrunddienst.

Eine einzelne offline nutzbare Datei zeigt ausgewählten Thread/Leseumfang,
Zähler für Beiträge und gemeldete Aufgaben, strukturelle Warnungen, die letzten
gemeldeten Aufgabenstände und die letzten gelesenen Beiträge. Aufklappbare
Belege enthalten vorhandene Eintragsreferenzen und Datei-SHA256. Darstellung
mit Tastatur nutzbar, lesbar bei breitem und schmalem Fenster, ohne JavaScript,
externe Bilder, Webfonts oder Netzressourcen. Ein begrenztes Anzeigelimit zählt
Ausblendungen sichtbar; Analyse und Eingangsgrenzen bleiben die von P10-01.

## Aussage- und Datenvertrag

Die Ansicht verwendet ausschließlich `build_report` aus P10-01. Der lesende
Adapter und das JSON-Schema bleiben unverändert. Keine zusätzliche Inferenz,
keine übernommenen Freitextinhalte, Prompts, Titel, Pfade oder rohen
Auftrags-/Agentenlabels. Gespeicherte Herkunfts-/Erfolgsangaben authentisieren
nichts. Herkunft, Identität, Wirkung und globale Abdeckung bleiben UNBEKANNT.
Ein gemeldetes Ergebnis ist kein belegter Abschluss. Eine Übernahme ohne
späteren Ergebnisbeitrag ist kein Lauf-, Fehler- oder Stoppsignal.

Unvollständige Aufnahme, mehrdeutige Reihenfolge, leerer/nicht lesbarer Verlauf
und ausgelassene Anzeigeelemente werden sichtbar. Die vorhandenen Exitcodes
0/2 behalten ihren bisherigen Leseumfang und sind keine ALLOW/DENY-Entscheidung.
Die HTML-Ausgabe wird überall escaped; eine Meta-CSP erlaubt nur das feste
Inline-Stylesheet anhand seines Hashs und keine Skripte/Netzressourcen. Das ist
keine allgemeine Browser-/DLP-/Produktionssicherheitsfreigabe. D-012 und
historische P4/RC/CB/OOS/Herkunftsgrenzen bleiben unverändert.

## Erlaubte Dateien und Grenzen

- Neu `agent_authority/html_report.py`, rein darstellender Renderer.
- `agent_authority/cli.py`: zusätzliche Formatauswahl und Rendereraufruf.
- `agent_authority/__init__.py`: Previewversion 0.3.0a2.
- Neu `tests/test_product_html.py` für Darstellung, Grenzen und Aufruf.
- README und `docs/PRODUCT-PREVIEW.md`: konkrete HTML-Bedienung.
- Dieser neue Vertrag vor Implementierung committen und pushen.

Keine Änderungen an `whiteboard.py`, `report.py`, Paket-/CI-Konfiguration,
vorhandenen Tests, lab/, scripts/, historischen Dokumenten/Archiven oder
ThreadDesk-Quellen. Kein weiterer Konnektor, Live-Herkunftsalgorithmus oder
ThreadDesk-UI. Branch `codex/product-browser-20261011`, isolierter Worktree
`/Users/landjunge/agent-authority-browser`.

## Abnahme

1. HTML übernimmt dieselben Zähler, Aufgabenaliase, Arten und Belegfingerprints
   wie JSON; Ergebnis-/Herkunfts-/Wirkungsgrenzen bleiben sichtbar.
2. Canary-Freitexte und gefälschte positive Metadaten fehlen in der Ausgabe.
   HTML-Sonderzeichen werden nicht zu Markup. Ordinalkollisionen, fehlende
   Quelle und Anzeigeauslassungen bleiben ausdrücklich sichtbar.
3. Echtes installiertes Wheel außerhalb des Repositorys: HTML stdout,
   Version/Hilfe, Text-/JSON-Regressionslauf, Fehlquelle und realer Whiteboard-
   Verlauf. Store vor/nach bytegleich; keine automatischen Reportdateien.
4. Tatsächlicher Browserlauf in frischem Testprofil: breite/schmale Ansicht,
   sichtbarer Inhalt, native Belegdisclosure, Stylesheet-CSP und keine
   Berichtsnetzressourcen/Skripte prüfen. Screenshot archivieren und ansehen.
   Vorhandener Browser wird verwendet; kein Testwerkzeug als Runtimeabhängigkeit.
5. Gezielte Tests und gesamte Suite zweimal bestanden; historische Abwahlen
   und Plattformskips getrennt. Pflichtprüfungen Ruff/Format/Bandit/Mypy bleiben
   grün. Quellen/Installationsnachweise an veröffentlichten Commit binden.
6. Eigene Nachweise, konkreter PR und separate Quellengegenprüfung im Whiteboard;
   keine fremde Test-/CI-/Browsergegenprüfung behaupten. Für Integration Regeln,
   HEAD und Checks frisch prüfen, kein Admin/Force; Remote-Squash/Tree/Push-CI
   danach archivieren.

Technische Referenzen: [CSP3](https://www.w3.org/TR/CSP3/) und
[Chrome Headless](https://developer.chrome.com/docs/automation-and-testing/headless).
