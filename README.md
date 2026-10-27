# Agent Authority Lab

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/design/icons/dark/Agent-Authority-dark-128.png">
  <img src="assets/design/icons/light/Agent-Authority-light-128.png" alt="Agent-Authority" width="96" height="96">
</picture>

## Aktueller Funktionsstand

Agent Authority ist eine Beobachtungs- und Analyseschicht. Die lokale Vorschau
liest ausdrücklich ausgewählte JSON-Beobachtungen; ThreadDesk ist ein optionaler
Adapter. Sie zeigt gemeldete Aufgabenaktivität, Warnungen und Belegreferenzen als
Text, JSON oder offline lesbaren HTML-Bericht. Die native macOS-Oberfläche ergänzt
Dashboard und Authority Graph. Agent Authority erteilt keine Freigaben, gibt keine
Geheimnisse oder Budgets frei und stoppt keine Aufträge. Gemeldete Identitäten und
Erfolge sind keine unabhängig bestätigten Nachweise.

Die lokale CLI benötigt Python 3.12 oder neuer.
[Bedienung](docs/PRODUCT-PREVIEW.md) ·
[Eingabevertrag](docs/PRODUCT-OBSERVATION-CONTRACT.md) ·
[macOS](native/macos/README.md).

## Aktuelle Produktrolle

Agent Authority ist ausschließlich eine **Beobachtungs-, Überwachungs- und
Analyseschicht**, wie in [KI-Zentrale-Entscheidung D-012](https://github.com/landjunge/KI-Zentralle/blob/main/DECISIONS.md#d-012--agent-authority-beobachtet-entscheidungen-bleiben-bei-den-zuständigen-tools)
festgehalten. Es meldet Beobachtungen, Widersprüche, Risiken und fehlende Belege.
Es erteilt oder entzieht keine Rechte, genehmigt keine Aktionen, gibt keine
Geheimnisse oder Budgets frei und stoppt keine Aufträge.

Die unten beschriebenen ALLOW/DENY-, Gate- und IFC-Mechanismen sind
**historische Experimente in einem künstlichen Labor**. Positive Ergebnisse,
gemessene übersehene Fälle, Korrekturen und eingefrorene Spezifikationen bleiben
Belege innerhalb ihres ursprünglichen Umfangs. Sie begründen weder eine
Entscheidungsbefugnis des Produkts noch authentifizieren sie die Quellen der
Beobachtungsvorschau. Der vorhandene [Praxis-/Forschungsabgleich](https://github.com/landjunge/KI-Zentralle/blob/main/docs/agent-authority/ABGLEICH-TESTS-UND-BEOBACHTER-RECHERCHE-2026-10-07.md)
hält diese Unterschiede ausdrücklich fest.

## Lokale Produktvorschau

Das Produkt nimmt quellenneutrale lokale Beobachtungen entgegen. ThreadDesk ist
ein optionaler Archivadapter und bestimmt nicht den Produktvertrag:

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install .
.venv/bin/agent-authority inspect --source json-directory --input /path/observations --source-id local-run
.venv/bin/agent-authority inspect --thread THREAD_ID --format json --limit 10
.venv/bin/agent-authority inspect --thread THREAD_ID --format html > report.html
```

Der [aktuelle Beobachtungsvertrag](docs/PRODUCT-OBSERVATION-CONTRACT.md) definiert
die neutralen Eingabe- und Berichtsschemata. `--thread` wählt den optionalen
ThreadDesk-Adapter; nur dieser verwendet standardmäßig `~/.threaddesk`, mit
`--store PATH` als abweichender Vorgabe. Der Bericht zitiert gelesene Einträge,
zeigt gemeldete Aufgabenaktivität und strukturelle Probleme und macht
unvollständige Eingaben sichtbar. Gespeicherte Akteur-, Erfolgs- und
Authentifizierungskennzeichnungen belegen weder Identität noch tatsächlichen
Abschluss oder Wirkung. Die CLI schreibt keine Speicher-, Cache- oder
Berichtsdateien und importiert kein historisches Durchsetzungslabor.
Exitcode 2 zeigt unvollständige Eingaben an, niemals eine Aktionsentscheidung.

[Vertrag P10-01](docs/P10-01-PRODUKTVERTRAG-20261011.md) und
[Produktbedienung](docs/PRODUCT-PREVIEW.md) beschreiben diese begrenzte lokale
Vorschau. Dies ist der Beginn der Produktphase; weitere Oberfläche und
Produktivbetrieb benötigen eigene konkrete Arbeiten. Der Umfang der unten
beschriebenen historischen Forschung bleibt erhalten.

Das HTML-Format liefert einen einzelnen offline lesbaren Browserbericht mit
Aufgaben-/Warntabellen und aufklappbaren Eintragsbelegen. Gespeichert wird durch
ausdrückliche Shellumleitung; der Befehl startet keinen Server und öffnet keinen
Browser. Text/JSON und Quellenprojektion behalten ihre bisherige Bedeutung.
Der [Umfang von P10-02](docs/P10-02-BROWSERBERICHT-VERTRAG-20261011.md) beschreibt
diese Darstellung.

## Native macOS-Anwendung

Die eigenständige [native Anwendung](native/macos/README.md) bietet ein kompaktes
Dashboard, Authority Graph, Beleginspektor, deutsche/englische Lokalisierung und
einen gesonderten macOS-Berechtigungs-/Testhost. Sie verarbeitet den unveränderten
neutralen Produktbericht; gemeldete Einträge werden dadurch nicht zu
authentifizierten Identitäten oder Wirkungen. Die ausdrücklich gekennzeichnete
50-Agenten-Probe dient der Oberflächenerkundung. Das lokale Intel-Bundle enthält
Python 3.12 und zielt auf macOS 12. Live-Tests von Endpoint Security benötigen
von Apple genehmigte Berechtigung, Signierung, Erweiterungsaktivierung und den
eigenen Festplattenvollzugriff des Kollektors. Der Entwicklungsbuild ersetzt
diese Voraussetzungen nicht.

## Workflow-Beobachtung

Die lokale Vorschau ergänzt eine versionierte, begrenzte Projektion ausgewählter
vorhandener Aufgaben-/Audit-/Ereignismetadaten. Der neutrale v1-Vertrag bleibt
erhalten. Graph und Inspektor lesen den ausdrücklich neuen Workflow-Berichts-
wrapper und zeigen gemeldete Aufgaben-, Lauf-, Übergabe- und Quellenreferenzen;
Identität und externe Wirkung bleiben unbekannt. Es entstehen keine neue
Aufgabenwarteschlange oder Auditwelt, keine Rechte-, Geheimnis-, Budget- oder
Stoppbefugnis und keine Projektabnahme. Identische Ereignisse zählen einmal;
widersprüchliche, fehlende oder ungeordnete Einträge bleiben sichtbar.
[Begrenzte fachliche Hinweise](docs/WORKFLOW-WARNINGS.md) vergleichen Revisionen,
Rückgaben, Artefakte und gemeldete Kontroll-/Sperrbelege. Widersprüche bleiben
gemeldete Behauptungen, fehlende Voraussetzungen bleiben unbekannt; keine
Hinweise sind keine allgemeine Sicherheitsbestätigung. Tatsächliche Grenzen,
unterstützte Erzeugertypen und offene Live-Adapterlücken stehen in der
[Workflow-Beobachtung](docs/WORKFLOW-OBSERVATIONS.md). Das Repository ist privat;
es gibt keinen öffentlich freigegebenen Download oder fertigen Webdienst.

```sh
agent-authority workflow-inspect --input /path/selected-metadata \
  --source-tool kirabridge --source-id local-run --format json
```

Version **0.3.0a2** ist weiterhin die lokale Quellvorschau; diese Änderung erzeugt
keinen GitHub-Release und aktualisiert keine installierte Laufzeit. Die
Python-3.12-CLI und der native macOS-Entwicklungsweg sind von einem freigegebenen
Paket zu unterscheiden. Begrenzte Leser sind bereits implementiert; es wird
keine neue unbeschränkte Archivaufnahme eingeführt.
[Tatsächliche begrenzte Belege](docs/evidence/seven-tools-20261018/STATUS.md).

## Historische Forschungsgrundlage

Experimentelles Sicherheitslabor: Kann **deterministische Zustands- und
Informationsflussdurchsetzung auf Workflowebene** **einige modellierte**
Kompositionsangriffe stoppen, die eine Autorisierung einzelner Aktionen übersieht?

Dies ist **kein** Produktivsystem und **kein** Beweis allgemeiner Agentensicherheit.

## Lizenz

**Quelltext einsehbar – alle Rechte vorbehalten.** Das Repository ist derzeit
**privat**. Zugang für Prüfung, Forschungsdiskussion oder Sicherheitsbewertung
benötigt eine ausdrückliche Einladung. Neues Material darf ohne vorherige
schriftliche Erlaubnis nicht kopiert, verändert, verbreitet, eingesetzt oder
verkauft werden. Vor dem Lizenzwechsel veröffentlichte historische Fassungen
behalten die damals geltende MIT-Lizenz. Genaue Grenze und Bedingungen stehen
in [LICENSE](LICENSE).

Diese Erläuterung ist eine deutsche Zusammenfassung. Die operative LICENSE
enthält bis zur Freigabe des vollständigen deutschen Entwurfs weiterhin das
englische Original. Deutsch als Zielsprache ist entschieden; eine bereits
maßgebliche deutsche Vertragsfassung wird hier nicht behauptet. Der frühere
Vorschlag eines englischen Sprachvorrangs ist verworfen.

[Die Lizenzhistorie und Drittbestandteile](docs/LICENSE-HISTORY-AND-THIRD-PARTY.md)
dokumentiert Quellpins und offene Auslieferungsprüfungen.

## Status

Die ursprüngliche Spezifikation v0.2 bleibt eingefroren. Spätere ergänzende
Experimente sind jeweils gesondert eingefroren und geprüft. Sie schreiben v0.2
nicht um.

| Ebene | Gegenstand | Hinweise |
| --- | --- | --- |
| Phase 1 | Kompositionsmonitor v0.2–v0.5/I9 | Abgeschlossene experimentelle Teilschritte |
| Phase 2 Exp 01 | Explizite IFC gegenüber reiner Autoritätsprüfung | Hypothese SUPPORTED *innerhalb des künstlichen Labors* |
| Phase 2 Exp 02 | Kommunikationsschranke | Hypothese SUPPORTED *innerhalb des künstlichen Labors* |
| Phase 2 Exp 03 | Modellierte implizite/Kontrollflussabhängigkeit | Hypothese SUPPORTED *innerhalb modellierter Kontrollabhängigkeiten* |
| Korrektur Phase 2 | Wert-ID-Bindung, keine SENSITIVE→PUBLIC-Neubindung | Ergänzend. Kein Experiment 04. `docs/PHASE2-VALUE-ID-BINDING.md` |
| Korrektur Phase 1 | Prozessinterne `submit`-Sperre und `INVALID_REQUEST` | `docs/PHASE1-SUBMIT-ATOMICITY.md` |
| Korrektur Phase 1 | Kanonischer FakeAdapter-Pfad entspricht Repositoryschlüssel (T-19) | `docs/PHASE1-ADAPTER-IDENTITY.md` |
| Korrektur Phase 1 | Öffentliches `state()` ist eine Momentaufnahme; Herkunft eingefroren | `docs/PHASE1-STATE-ENCAPSULATION.md` |
| Korrektur Phase 1 | Workflowregister: Kapazität und Reservierung atomar; `finish()` nur durch Koordinator | `docs/PHASE1-WORKFLOW-LIFECYCLE-ATOMICITY.md` |
| Werkzeuge | Programm-STOP-Zahlen, PBT-Orakel, CI | Kein Experiment 04. Siehe `docs/RESEARCH-METHOD.md` §3.1 und `docs/PBT-ORACLE-v1.md` |
| Werkzeuge | Konvergenzprüfprotokoll und Katalog v1 | Ergänzend. Kein Experiment 04. `docs/CONVERGENCE-BATTERY-v1.md`, `docs/CONVERGENCE-ATTACK-CATALOG-v1.md` |
| Werkzeuge | Ergebnisse der Konvergenzprüfung v1 | `k = 1` MISSED (CB-01). In dieser Prüfung nicht widerlegt. **Nicht** SUPPORTED. `docs/CONVERGENCE-BATTERY-v1-RESULTS.md` |
| Werkzeuge | Übertragungsstudie realer Fälle v1 | Externe Prüfung (Codex) gegen `cb2dc55`. RC-01–RC-05 sind gemessene übersehene Fälle, keine defekten Tests. `docs/REAL-CASE-TRANSFER-STUDY-v1.md` |

Die zuletzt geprüfte Testsuite ist im jüngsten Review dokumentiert.
**PASS ≠ SUPPORTED.** Grüne Tests zeigen Spezifikationskonformität innerhalb
dieser künstlichen Welt. Siehe [Forschungsmethode](docs/RESEARCH-METHOD.md).

Das Labor ist von 4AllPass getrennt. Keine echten Zugangsdaten, Produktivsysteme
oder Geheimnisse werden verwendet.

Der G3-Erzeuger hängt JSONL-Einträge des Phase-1-Authority-Event-Envelope an
(`authority.requested` / `allowed` / `denied`). Außerhalb von pytest ist er
standardmäßig an, unter pytest aus. `LAB_AUTHORITY_EVENTS=1` aktiviert ihn
ausdrücklich; `0`, `false`, `off` oder `no` deaktivieren ihn in beiden Kontexten,
unabhängig von Groß-/Kleinschreibung und umgebenden Leerzeichen. Fehlende, leere
oder nur aus Leerzeichen bestehende Werte behalten den Kontextstandard;
andere nicht leere Werte behalten das bisherige aktivierte Verhalten.
Er schreibt niemals in eine ThreadDesk-Datenbank und ändert kein ALLOW/DENY des
Labors. Dies ist kein Phase-2- oder externer Wirkungseventstrom. Exportierte
Metadaten sind nicht automatisch frei von Geheimnissen; vollständige Schwärzung
bleibt eine offene Grenze.

## P1: kontrollierter Beobachtungsversuch

[Vertrag P1](docs/P1-CONTROLLED-RUN.md) und
[gemessene Ergebnisse](docs/P1-CONTROLLED-RUN-RESULTS.md): ein eigenständiges
Forschungsskript, unabhängige lokale Zielmomentaufnahme, **UNBEKANNT** bei
fehlenden Belegen. Historische Durchsetzung bleibt unverändert. Ein gestarteter
CLI-Prozess ist kein nachgewiesener Agentenlauf; der dokumentierte P1-Versuch
enthält **null nachgewiesene Agentenläufe**.

```bash
.venv/bin/python scripts/p1_controlled_run.py --out /tmp/aa-p1-new-run --timeout 60
```

Das Ausgabeverzeichnis muss neu sein. Exitcode 2 bedeutet, dass Agentenlauf oder
Referenzvergleich unbewiesen bleiben; die getrennten Beobachtungen, Analyse und
Ergebnisse sind zu prüfen. Roher CLI-Text wird nicht archiviert. Dies ist kein
vollständiges Ausführungsaudit und keine Umsetzung des vollständigen
Forschungspanels mit sechs Fällen.

Historische PR19-Forschung und die PR17-Dienstreferenz sind im
[aktuellen Forschungsabgleich](docs/RESEARCH-PR-ABGLEICH-20261011.md) inventarisiert,
mit gepinnten Originalquellen, reproduzierten Integrationskonflikten und
getrennten Geltungsbereichen.

## Maßgebliche Methode

- [Forschungsmethode](docs/RESEARCH-METHOD.md) – PASS und Hypothese, Zyklus-STOP, Programm-STOP, CI
- [Konvergenzprüfung v1](docs/CONVERGENCE-BATTERY-v1.md) – Programm-STOP-Prüfprotokoll
- [Angriffskatalog v1](docs/CONVERGENCE-ATTACK-CATALOG-v1.md) – zehn Angriffe; Monitor-aus-Zustand eingefroren
- [Ergebnisse v1](docs/CONVERGENCE-BATTERY-v1-RESULTS.md) – Ergebnisse; `k = 1`; nicht SUPPORTED
- [Übertragungsstudie realer Fälle v1](docs/REAL-CASE-TRANSFER-STUDY-v1.md) – Zuordnungen realer Fälle; RC-01–RC-05 bleiben bekannte Lücken
- [Beobachtung nach Abschluss](docs/OBSERVATION-CASE-FINISH-LATE-EFFECT.md) – vorhandene Abschluss-/Spätwirkungsbelege aus Beobachtersicht; fehlende Ereignisse bleiben ausdrücklich sichtbar
- [Archiv realer Fälle v1](docs/realcase/v1/README.md) – archiviertes ZIP und Importprompt
- [PBT-Orakel v1](docs/PBT-ORACLE-v1.md) – Hypothesis-Verträge, kein allgemeines I9-Verweigern
- [Bedrohungsmodell](docs/THREAT-MODEL.md)
- [Offene und bewusst ausgeschlossene Punkte](docs/OUT-OF-SCOPE-DEBT.md)
- [Bewertungsmatrix](docs/EVALUATION-MATRIX.md)
- [ADR-002](docs/ADR-002-research-method-and-review-semantics.md)
- [ADR-001](docs/ADR-001-I8-I9-action-boundary.md) – historischer I8/I9-Konflikt, unverändert

Historische Dateien mit dem Titel „Independent Verification“ werden nicht
umbenannt. Sie werden künftig als adversarielle Prüfung im selben Kontext bzw.
Prüfung nach Umsetzung gelesen, nicht als externe Audits.

## Forschungsfrage

Kann ein Workflow einzeln autorisierter Agentenaktionen weiterhin ein verbotenes
Gesamtergebnis erzeugen, und kann ein kleiner deterministischer
Kompositionsmonitor diese Fälle erkennen, ohne ein LLM in den vertrauenswürdigen
Kern aufzunehmen?

## Regeln

- Vorhandene Sicherheitsbausteine verwenden, soweit möglich.
- Keine eigene Kryptografie.
- Kein eigenes Capability-Format ohne belegte konkrete Lücke.
- LLMs dürfen Aktionen vorschlagen, aber nicht autorisieren.
- Tests sind Abnahmekriterien und dürfen nicht zugunsten einer Implementierung abgeschwächt werden.
- Eine gescheiterte Hypothese ist ein gültiges Forschungsergebnis.
- Den Umfang nicht erweitern, weil ein Review STOP meldet; ein neues Experiment benötigt eine neue eingefrorene Spezifikation.
- Nach jedem Commit zu `origin` **pushen**. Nur lokale Commits sind nicht abgeschlossen (`scripts/install-git-hooks.sh`).

## Eingefrorene Reihenfolge am Ursprung von Phase 1

1. Spezifikation v0.1
2. Kompositionsschranke
3. Technologieentscheidungen
4. Prototypspezifikation v0.2
5. Deterministischen Prototyp bauen
6. Gegen die eingefrorene v0.2 prüfen
7. Ergänzende Teilschritte v0.3–v0.5/I9 und Phase-2-Experimente, jeweils gesondert eingefroren

Die eingefrorenen Entwurfsdokumente stehen unter `docs/`. Historische Reviews
behalten ihre ursprünglichen Titel und Urteile.

## Prototyp v0.2: deterministischer Kern

Ausschließlich lokaler Kompositionsmonitor. Kein LLM, Netzwerk oder echte
Zugangsdaten.

```text
ActionRequest → predict next WorkflowState → evaluate I1–I6
  ALLOW: commit state + provenance
  DENY:  leave state unchanged
```

### Invarianten

| ID | Regel |
| --- | --- |
| I1 | `action_count <= 100` |
| I2 | Anzahl unterschiedlicher Dateien, in die geschrieben wurde, `<= 10` |
| I3 | `config/security-policy.json` ist unveränderlich |
| I4 | `delegation_depth <= 1` |
| I5 | Jedes `net.connect`-Ziel ist verboten |
| I6 | `repo.delete` / `release.publish` benötigen `parameters.approval_token` |

**Delegationskonvention:** Der Wurzelakteur hat Tiefe 0. `root → A` hat Tiefe 1
(erlaubt). `A → B` hat Tiefe 2 (verweigert).

I4 begrenzt nur die Aktion `delegate`. Unabhängige Agenten können weiterhin in
dieselbe `workflow_id` auf Tiefe 0 einreichen, wie für agentenübergreifende
Akkumulationstests benötigt. Das ist keine Tiefenkette.

### Tests ausführen

```bash
python3.12 -m venv .venv
.venv/bin/pip install -e ".[dev]"
.venv/bin/pytest -q
# CI runs the same suite twice on Python 3.12 (see .github/workflows/test.yml)
```

### Was v0.2 nicht beweist

- allgemeine Agentensicherheit
- Ausrichtung oder Absichtsnachweis
- vollständige Informationsflusssicherheit
- semantische Codesicherheit
- Unternehmenseinsatzbereitschaft
- einen Nutzen von Biscuit, Cedar oder FIDES; diese sind nicht integriert

Ein STOP zur Forschungshypothese ist gültig.

## v0.3: kanonische Artefaktidentität

Ergänzend. Die eingefrorene v0.2 bleibt unverändert.
Siehe `docs/PROTOTYPE-v0.3.md`.

- Pfadaliase (`./`, `..`, `//`) werden vor I2/I3 normalisiert.
- **I7:** `file.delete` für `tests/test_security.py` oder alles unter `tests/security/` benötigt `approval_token`.

## v0.4: vollständige Mutationsprüfung I8

Ergänzend. Die eingefrorenen v0.2 und v0.3 bleiben unverändert.
Siehe `docs/PROTOTYPE-v0.4.md`.

- Ändernde Verben auf der geschützten Richtlinie außer `file.write` werden durch I8 verweigert. I3 wird nicht gelockert.
- Ändernde Verben auf Sicherheitstestartefakten außer `file.delete` benötigen nach I8 `approval_token`.
- Der I7-Identitätsabgleich verwendet ausschließlich die v0.3-Liste, keine Dateinamenheuristik.
- Nicht Teil dieses Schritts: allgemeines Verweigern, I2 beim Löschen, kanonischer Adapterschlüssel.

## v0.5: unbekannte Aktion auf geschützter Identität I9

Ergänzend. Die eingefrorenen v0.2–v0.4 bleiben unverändert.
Siehe `docs/PROTOTYPE-v0.5-I9.md`.

- Unbekannte Aktionszeichenfolge und geschützte kanonische Identität ergeben DENY `I9_UNKNOWN_ACTION_PROTECTED`.
- Exaktes bekanntes/sicheres Vokabular. Keine Groß-/Kleinschreibungsanpassung, Aliasinterpretation oder LLM.
- I9 verweigert nicht pauschal unbekannte Aktionen auf gewöhnlichen Ressourcen.
- `approval_token` autorisiert keine unbekannte Richtlinienaktion.

## Phase 2: Experiment 01, IFC-Komposition

Ergänzend und unter `lab/phase2/` isoliert.
Eingefrorene Spezifikation: `docs/PHASE2-EXPERIMENT-01.md`.

Phase 1 bleibt unverändert. Kein LLM. Nur zwei Kennzeichnungen (`PUBLIC` / `SENSITIVE`).

A/B: Reine Autoritätsprüfung lässt READ→TRANSFER→EGRESS zu; Autoritätsprüfung mit
IFC verweigert den externen SENSITIVE-Abfluss, während der PUBLIC-Abfluss durch
B weiterhin ALLOW bleibt.

## Phase 2: Experiment 02, Kommunikationsschranke

Ergänzend. Eingefrorene Spezifikation:
`docs/PHASE2-EXPERIMENT-02-COMMUNICATION-GATE.md`. Experiment 01 bleibt unverändert.

Die agentenübergreifende Übertragung ist `A → Communication Gate → B`.
Die Schranke prüft nur Metadaten (`evaluate_transfer`). Keine Nutzdaten,
Werkzeuge, Zugangsdaten oder Richtlinienänderungen.

## Phase 2: Experiment 03, modellierter impliziter Informationsfluss

Ergänzend. Eingefrorene Spezifikation:
`docs/PHASE2-EXPERIMENT-03-IMPLICIT-FLOW.md`. Experimente 01–02 bleiben unverändert.

Explizites `derived_from`-IFC ist die Grundlage. Modelliertes `control_decide`
und `created_under` vererben SENSITIVE über As Zustandsänderung, sodass Bs
Abfluss ohne Übertragung von C1 verweigert werden kann. PUBLIC-Kontrollflussabfluss
bleibt ALLOW. Keine Nutzdaten-DLP und kein LLM.
