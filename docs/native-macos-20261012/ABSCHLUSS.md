# Native Agent-Authority-App — Umsetzung vom 12. Oktober 2026

Umgesetzt auf Basis des freigegebenen Entwurfs und master `9eda80d`.
Arbeitsbranch: `feat/native-macos-20261012`. Kein Merge in master.

Die lokal gebaute Intel-App liegt unter
`native/macos/build/Agent Authority.app`. Native Swift-/AppKit-Oberfläche,
eingebettete Python-3.12-Laufzeit und unveränderte Produktmodule; kein WebView.
Build- und Signierungsanleitung: [native/macos/README.md](../../native/macos/README.md).

Umgesetzte Bereiche:

- Kompakte Sidebar, native Toolbar/Menüs, Dashboard, Authority Graph,
  Inspector mit menschlicher Erklärung und Rohdaten sowie Evidence-Tabellen.
- Selektion, Suche, Statusfilter, Zoom, Trackpad/Pan, Miniatur, Kontextaktionen,
  Tastatursteuerung und Accessibility-Elemente; Root-/Delegationsketten bleiben
  bei der Untersuchung ihres Identitäts-/Authority-Nachweises im Kontext.
- Verdichtete Ansicht mit 50 gleichzeitig sichtbaren Beispielagenten;
  aufklappbare Gruppen und automatische Aggregation oberhalb von 80 Agenten.
  Gruppen zeigen ihre inneren Delegationen und äußeren Verbindungen.
- Qualitätsbewertung über Elternkette und Beziehungen. Eine lokal belegte
  Identität verdeckt keine fehlende Authority ihrer Eltern. Unbekannte
  Verlustkontrollen werden nicht als gemessene Null dargestellt.
- Quellenneutraler Ordnerimport über den unveränderten CLI, begrenzter und
  abbrechbarer Worker, Import vorhandener Produktberichte, Export; strukturelle
  Warnungen sind auswählbare Nachweise. Meldungen bleiben Meldungen.
- 272 vollständige DE/EN-Schlüssel, gespeicherte Sprachwahl und Systemerkennung
  nach dem geprüften ThreadDesk-Prinzip, mit eigenen Einstellungen/Katalogen.
  Dark, Light und Systemdarstellung; deutsche Texte als korrektes UTF-8.
- Separater macOS-Testhost mit offiziellen Ordner-, Accessibility-,
  Bildschirmaufnahme-, Apple-Events- und Systemerweiterungsmechanismen sowie
  versionsgerechten FDA-Einstellungen. Eigene Prozessprobe und implementierte
  sechs Writer-Kontrollen mit unabhängiger Collector-Voraussetzung.
- Kompilierte ES-Systemerweiterung mit NOTIFY-Ereignissen, begrenztem Scope,
  gegenseitiger XPC-Code-Signaturprüfung, PID-Version/Start-/Boot-/Objektbezug,
  Lifecycle und getrennten Verlustkontrollen. Keine Root-Shellschnittstelle,
  keine TCC-Manipulation, keine SIP-Abschwächung und keine Rechtevergabe.

Verifikation:

- 12 Swift-Tests bestanden: Sprache/Kataloge, Trace/Skalierung/Zyklen,
  Referenzprüfung, Produkt-/Kernelgrenzen, Elternketten und Unknown-Verlustwerte.
- 61 bestehende Produkttests bestanden; Engine, historische Lab-Module und
  bisherige Tests unverändert. Paketierte Produktdateien bytegleich geprüft.
- Release-Build; native Helfer und Collector mit Clang `-Wall -Wextra -Werror`.
  Ad-hoc-Paketsignatur mit `codesign --verify --strict --deep` geprüft.
- Quellen-/Lokalisierungs-/UTF-8-Prüfung und Ruff für die neuen Python-Werkzeuge.
- Native Starts über LaunchServices; App-Kindprozessbezug in
  [native-app-process-probe.json](native-app-process-probe.json) geprüft.
- Deutsche Dark- und englische Light-Ansicht, aktueller Produktbericht und
  5120×2880-Pixel-Ansicht der 50 Agenten visuell geprüft. Eigene native Ansichten
  wurden gerendert; keine fremden Bildschirme aufgenommen.
- Tatsächlicher Testhost: AMD Radeon R9 M380, 2 GB VRAM, macOS 15.7.4.
  [Renderbefund](render-benchmark.json): vollständiges Zeichnen des 50er-Ausschnitts
  in einen eigenen Bitmap-Puffer, keine GPU-Framezeit- oder allgemeine FPS-Zusage.
  Die laufende App hat keinen permanenten Graph-Render-Timer.
- Mindestversionen der eingebetteten Mach-O-Laufzeitdateien geprüft;
  Native-Ziel macOS 12, Python-Binärdateien höchstens macOS 12.

Echte verbleibende Grenzen:

1. Keine gültige Developer-ID-/ES-Signierung oder Apple-genehmigte Provisionierung
   vorhanden. Der lokale Build ist ad-hoc signiert. Der Live-Collector wurde
   nicht aktiviert und die Writer-Batterie nicht ausgeführt. Die tatsächliche
   unprivilegierte ES-Probe liefert Fehler 5; daraus wird kein FDA-Status erfunden.
   Entitlement, Signierung, Installation in `/Applications`, Benutzerfreigabe
   und Collector-FDA bleiben reguläre externe Voraussetzungen.
2. Der aktuelle Produktvertrag authentisiert keine Agentenidentität, Authority,
   Delegation oder Wirkung. Der UI-Datensatz ist ausdrücklich synthetisch.
   Auch qualifizierte Kernelereignisse beglaubigen keine externe Modellsitzung
   und keine dauerhafte Speicherung.
3. Die Binärziele berücksichtigen Monterey; ein tatsächlicher Lauf auf macOS 12
   ist noch nicht gemessen. Der erzeugte App-Build ist Intel. Apple Silicon
   benötigt eine passende Laufzeit-/Signierungsdistribution.
4. Die native Accessibility-Struktur ist implementiert. Eine vollständige
   manuelle VoiceOver-Abnahme und ein privilegierter Collector-Langzeittest
   sind nicht als bestanden ausgegeben.

Geänderte Dateien liegen in `native/macos/`, dem neuen macOS-CI-Workflow,
dem kurzen README-Einstieg und diesen Entwurfs-/Prüfunterlagen.
Andere Produkte, master und die funktionierende Engine wurden nicht umgebaut.
