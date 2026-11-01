[English](README.md) · **Deutsch**

<p align="center">
  <img src="assets/readme/Agent-Authority-dark.svg" alt="Agent Authority" width="256" height="256">
</p>

<p align="center">
  <a href="https://github.com/landjunge/threaddesk/blob/docs/product-family-readme-20261031/README.de.md" title="ThreadDesk"><img src="assets/readme/normalized/ThreadDesk-small.svg" alt="ThreadDesk" width="48" height="48"></a>
  &nbsp;
  <a href="https://github.com/landjunge/KiraBridge/blob/docs/product-family-readme-20261031/README.de.md" title="KiraBridge"><img src="assets/readme/KiraBridge-dark.svg" alt="KiraBridge" width="48" height="48"></a>
  &nbsp;
  <a href="https://github.com/landjunge/4AllPass/blob/docs/product-family-readme-20261031/README.de.md" title="4AllPass"><img src="assets/readme/normalized/4AllPass-small.svg" alt="4AllPass" width="48" height="48"></a>
  &nbsp;
  <a href="https://github.com/landjunge/tollgate/blob/docs/product-family-readme-20261031/README.de.md" title="TollGate"><img src="assets/readme/normalized/TollGate-small.svg" alt="TollGate" width="48" height="48"></a>
</p>

<h1 align="center">Agent Authority</h1>

<p align="center"><strong>Nachvollziehen, was deine KI-Agenten melden.</strong></p>

Agent Authority liest ausgewählte lokale Beobachtungen und macht Aufgabenaktivität, Widersprüche und fehlende Belege sichtbar. So kannst du Meldungen und ihre Quellen prüfen, bevor du Schlüsse ziehst.

**Quellstand: 0.3.0a2 · Lokale Produktvorschau · Python 3.12 oder neuer**

[Lokale Vorschau einrichten](docs/PRODUCT-PREVIEW.md) · [macOS-Entwicklungsoberfläche](native/macos/README.md)

Das Repository ist privat und benötigt eine Einladung. Es gibt kein veröffentlichtes Installationspaket und keinen fertigen Webdienst. Nutzung und Änderungen benötigen eine Erlaubnis gemäß [Lizenz](LICENSE).

## Wobei Agent Authority dir hilft

- **Beobachtungen lesen:** ausgewählte lokale JSON-Daten aufnehmen; ThreadDesk ist ein optionaler Leseadapter.
- **Verläufe prüfen:** gemeldete Aufgaben, Rückgaben und strukturelle Warnungen anzeigen; Lücken und Konflikte bleiben sichtbar.
- **Berichte ansehen:** Text, JSON oder einen offline lesbaren HTML-Bericht verwenden.
- **Zusammenhänge erkunden:** Dashboard, Authority Graph und Belegansicht in der nativen macOS-Entwicklungsoberfläche nutzen.

Agent Authority beobachtet und analysiert. Es erteilt keine Freigaben, gibt keine Geheimnisse oder Budgets frei und stoppt keine Aufträge. Gespeicherte Identitäts- und Erfolgsmeldungen sind keine unabhängig bestätigten Nachweise. Die vorhandenen Workflow-Leser verarbeiten ausgewählte Metadaten; vollständige Live-Anbindungen aller Produkte bleiben geplant. [Beobachtungsvertrag](docs/PRODUCT-OBSERVATION-CONTRACT.md) · [Workflow-Grenzen](docs/WORKFLOW-OBSERVATIONS.md).

## Loslegen

1. **Zugriff und Erlaubnis klären.** Die Vorschau richtet sich derzeit an eingeladene Nutzer mit einer lokalen Quellinstallation.
2. **Beobachtungen auswählen.** Nutze lokale JSON-Dateien oder ausdrücklich den ThreadDesk-Leseadapter.
3. **Bericht prüfen.** Öffne die Textausgabe oder speichere einen HTML-Bericht. Lies Warnungen und Belegreferenzen gemeinsam. [Schrittweise Anleitung](docs/PRODUCT-PREVIEW.md).

Der normale Leseweg verändert keine Aufgaben oder Quelldaten. Die macOS-Beispieldaten dienen der Erkundung der Oberfläche; echte Endpoint-Security-Beobachtung benötigt gesonderte Apple-Freigaben und Systemrechte. Die Vorschau ist keine allgemeine Sicherheitsbestätigung.

## Geplante Zusammenarbeit

Die fünf Produkte bleiben eigenständig. Geplant ist ein gemeinsamer Ablauf mit **KiraBridge als Kommunikationszentrale**:

| Produkt | Aufgabe im gemeinsamen Ablauf |
| --- | --- |
| [ThreadDesk](https://github.com/landjunge/threaddesk/blob/docs/product-family-readme-20261031/README.de.md) | Bewahrt Projektstand, Wissen und Ergebnisse. |
| [KiraBridge](https://github.com/landjunge/KiraBridge/blob/docs/product-family-readme-20261031/README.de.md) | Vermittelt Aufträge, Rückfragen und Antworten zwischen Chat, lokalen Agenten und Werkzeugen. |
| [4AllPass](https://github.com/landjunge/4AllPass/blob/docs/product-family-readme-20261031/README.de.md) | Verwaltet Zugangsdaten; soll gezielt erlaubte Zugriffe ermöglichen. |
| [TollGate](https://github.com/landjunge/tollgate/blob/docs/product-family-readme-20261031/README.de.md) | Prüft angeschlossene Aufrufe und setzt Verbrauchsgrenzen und Stopps durch. |
| [Agent Authority](https://github.com/landjunge/agent-authority-lab/blob/docs/product-family-readme-20261031/README.de.md) | Zeigt Beobachtungen, Widersprüche und fehlende Belege; erteilt keine Freigaben. |

Einzelne Schnittstellen sind vorhanden. Ein vollständig eingerichteter und geprüfter Ablauf aller fünf Produkte ist noch geplant. Freigaben bleiben beim zuständigen Werkzeug und beim Menschen. KiraBridge und Agent Authority benötigen Zugriff auf ihre privaten Repositorys.

## Lizenz

[Source-available, alle Rechte vorbehalten](LICENSE). Repositoryzugriff allein erlaubt keine Nutzung, Änderung oder Weiterverteilung. Historische MIT-Lizenzrechte bleiben erhalten.

Produktidee und Architektur: **Daniel Filipek (landjunge)**. KI unterstützt Implementierung und Dokumentation. Nachvollziehbare Reviews sind willkommen; Laborergebnisse behalten ihren begrenzten Forschungsumfang.

[Produktbedienung](docs/PRODUCT-PREVIEW.md) · [Workflow-Hinweise](docs/WORKFLOW-WARNINGS.md) · [macOS und Build](native/macos/README.md) · [Historische Forschung](docs/RESEARCH-BASELINE.md)
