# Abgleich der historischen Forschungs-PRs 19 und 17

Prüfstand: 11. Oktober 2026, Auftrag WB1684. Zuerst PR19, danach PR17.
Verglichen wurden die vollständigen Git-Bäume, Funktionen und bestehenden
Tests gegen `master` **70773abfad8ad873f3db6cd3a248f6a2cde576bf**; WB1689
bestätigt, nur weiterhin benötigte Forschungsinvarianten gezielt zu adaptieren.
Dieser Abgleich integriert keine Forschungsprogramme und ändert keine
historischen Erwartungen, Messdateien oder Abnahmegrenzen. D-012 gilt:
Agent Authority beobachtet und analysiert; operative Entscheidungen bleiben
bei den zuständigen Tools.

## PR19: eigenständige Forschung mit Integrationskonflikten

Quelle: [PR19](https://github.com/landjunge/agent-authority-lab/pull/19),
[vollständiger eingefrorener Stand f94f444e383052d04e2ef22bfed4ec03512cb066](https://github.com/landjunge/agent-authority-lab/tree/f94f444e383052d04e2ef22bfed4ec03512cb066).
Der Zweig enthält 70 eigene Commits gegenüber der gemeinsamen Basis
`ef2400fa5fad3c4ff051928b78fcb3093bb23453`; der heutige master hat 24 weitere
eigene Commits. Der Branch bleibt als historische Quelle erhalten.

Der vollständige Vergleich umfasst 474 PR19-Dateien und 226 master-Dateien:
125 Pfade sind identisch, vier gemeinsame Pfade verschieden, 345 nur in PR19
und 97 nur in master. Die **347 ursprünglichen Änderungspfade** zerfallen in
345 zusätzliche Forschungspfade, den bereits identisch integrierten
Prototypplan und den README-Nachtrag. Die vier gemeinsamen Unterschiede
betreffen README sowie drei später auf master reparierte Lab-Dateien.
Der konfliktfreie simulierte Drei-Wege-Merge behält `Lab.commit_effect`
und die Decision-Tickets; ein roher Endpoint-Diff ist kein belegter Rückbau.

| Fehlende Pfade / Funktion | Bedarf und Disposition |
| --- | --- |
| 309 Dokumente und Messartefakte | Eigenständige historische Belege erhalten, über den gepinnten Quellstand erreichbar. Keine Behauptung, sie seien bereits vollständig in master oder eine aktuelle Produktabnahme. |
| 18 Probes, fünf Research-Module, `observer_research.py` | Historische Capture-, Ablations-, Stress-, Datei-/Epoch-/Inode- und Auswertungswerkzeuge erhalten. Aktuelle P1/P5/P7/P8-Verträge sind getrennte, enger begrenzte Prüfungen. Keine unveränderte Laufzeitübernahme. |
| Elf Tests und ein Replay-Workflow | Zugehörige historische Verträge und eingefrorene Daten erhalten. Der Run03-Replay ist keine neue Capture oder OS-Herkunftsmessung. |
| README-Forschungsindex | Ein aktueller Abgleich mit Quellenpermalinks fehlt; dieser kleine Nachtrag erfüllt den Bedarf ohne eine Runtime-Integration. |

Zwei konkrete Gegenproben begrenzen eine Übernahme:

1. Der [Linux-FD-Verifier](https://github.com/landjunge/agent-authority-lab/blob/f94f444e383052d04e2ef22bfed4ec03512cb066/probes/independent_local_fd_identity.py)
   ergänzt eine tatsächlich fehlende Forschungsfunktion: ein sauber gestarteter
   separater Interpreter misst per `SCM_RIGHTS` die ihm übergebenen FD-Paare.
   Das heutige Mach-Modul belegt den unmittelbaren Nachrichtensender und ersetzt
   diese Dateirelation **nicht**. Schon die Anwesenheit der alten Verifier-Datei
   setzt aber im heutigen `p5_reliability._case_host` den erwarteten `SKIP`
   auf `FAIL`; P7s `score_package` wird `STOP`. Eine Integration benötigt einen
   ausdrücklich neuen Vertrag, keinen geänderten historischen Erwartungswert.
2. Der [alte FinishEffectSensor](https://github.com/landjunge/agent-authority-lab/blob/f94f444e383052d04e2ef22bfed4ec03512cb066/research/finish_effect_observation.py)
   sucht eine direkte AST-Zuweisung an `FakeAdapter.repo.files`. Der reparierte
   Adapter schreibt über `commit_effect` mit Callback; der alte Konstruktor
   wirft deshalb `StopIteration`. Der Sensor bleibt historische Implementation,
   kein heute reproduzierbarer Drop-in-Sensor.

In einem isolierten Checkout bestanden zunächst dieselben zwei vorhandenen
P5-/P7-Kontrollen. Nach unveränderter Aufnahme der beiden genannten PR19-Module
und vier ursprünglicher Sensortests scheiterten **sechs Tests**: die beiden
aktuellen Kontrollen und alle vier Sensorfälle. Kein Modell- oder Linux-Capture,
keine Abschwächung von Tests und keine Änderung am Produktcheckout.
Die sechs Fehler betreffen alte Integrationsannahmen; sie sind **kein
nachgewiesener Defekt des unveränderten aktuellen master**.

### Relevanz der elf alten Testdateien und gezielte Adaption

| Alte Testdateien (unter `tests/`) | Heutiger Bedarf |
| --- | --- |
| `test_collector_launcher_import_smoke.py`, `test_collector_run03_launcher_smoke.py` | Alte Run02-/Run03-Launcher-Smokes erhalten; ohne diese Harnesses keine aktuelle Startanforderung. |
| `test_collector_manipulation_c1_c7_run02.py`, `test_collector_source_boundary.py` | Historische falsche Quellen/Replay-Tradeoffs erhalten. P6s Forgery-, FD-Packet-, Archiv- und Digesttests sichern die heutigen Eingänge. Native Herkunft verlangt tatsächlichen Mach-Empfang. |
| `test_current_local_collector_analysis.py` | Historische F1–F7-Auswertung erhalten. Heute unabhängige Referenz, Widerspruchsprüfung und P7s veränderte-Belege-/Matrix-Abwehr; kein neuer F1–F7-Collectorauftrag. |
| `test_finish_effect_inference.py`, `test_observer_research.py` | Status ist keine Wirkung; fehlende Bindung, Konflikte und Zeitgrenzen bleiben unbekannt. P1/P3/P6/P7 decken diese Invarianten; Lieferreihenfolge an P1 gezielt zusätzlich prüfen. Alte Schemas, Ablationsroster und Native-Callbacks nicht übernehmen. |
| `test_finish_effect_sensor.py` | Historischen AST-Sensor erhalten. Passive Fehlergrenze am vorhandenen G3-Exporter zusätzlich prüfen; keinen neuen Trace-Sensor implementieren. |
| `test_independent_local_fd_identity.py` | Historischen Linux-Brokervertrag erhalten. Kein aktueller Auftrag für diesen zusätzlichen Verifier; heutige FD-Capabilities, Ablauf-/Closed-/Nonregular- und native Session-/Replaytests sind eigenständige Verträge. |
| `test_observer_current_local_collector.py`, `test_observer_live_local_file_identity.py` | Historischen Linux/tmpfs-/Formparservertrag erhalten. Heutige gehaltene FD-Messung und P6-Rückweisung unbeglaubigter Claims benötigen keinen neuen Findmnt- oder positiven Packetparser. |

Nur zwei weiterhin benötigte Prüfinvarianten werden an **bestehende**
Schnittstellen adaptiert, ohne Laufzeitänderung:
`tests/test_observer_research_invariants.py` prüft reale Export-I/O-Fehler
(Datei als Elternpfad und Verzeichnis als Ausgabeziel) gegen erlaubte
FakeAdapter-Wirkung, unveränderte abgelehnte Wirkung und erfolgreichen
Lifecycle-Abschluss. Für P1 prüft es alle 720 Lieferpermutationen jeweils
eines VOR-, NACH- und die Endgrenze überlappenden unbekannten Falls.
Messzeiten/Bindung bestimmen das Ergebnis; fehlende Ordnung bleibt unbekannt.
Die fünf parametrisierten Fälle sind künstliche lokale Tests, kein neuer
Modell-, Host- oder allgemeiner Herkunftsnachweis.
Mit den vorhandenen Exporter-/P1-Tests bestanden 65 gezielte Fälle; die
Gesamtsuite bestand mit 505 Tests und fünf unveränderten historischen
Abwahlen. Neue Testdatei Ruff/Format sauber, kein Laufzeitpatch.

Weitere weiterhin relevante Grenzen stehen in den Originalen:

- [FD-Verifier-Ergebnis](https://github.com/landjunge/agent-authority-lab/blob/f94f444e383052d04e2ef22bfed4ec03512cb066/docs/OBSERVER-INDEPENDENT-LOCAL-FD-IDENTITY-RESULTS-2026-10-08.md):
  `source_authenticated=false`; passend substituierte FDs samt Packet bleiben
  als Ursprungstäuschung nicht unterscheidbar. Positive FD-Relation ist keine
  dauerhafte Identität, Inhalts- oder Autorbeglaubigung.
- [Run03-Manipulation](https://github.com/landjunge/agent-authority-lab/blob/f94f444e383052d04e2ef22bfed4ec03512cb066/docs/OBSERVER-COLLECTOR-MANIPULATION-C1-C7-RUN03-RESULTS-2026-10-08.md)
  und [Source-Boundary-Replay](https://github.com/landjunge/agent-authority-lab/blob/f94f444e383052d04e2ef22bfed4ec03512cb066/docs/OBSERVER-SOURCE-BOUNDARY-AUTOMATED-CHECK-2026-10-08.md):
  C3/C4/C7 falsch positiv; die konservative Simulation setzt alle sieben
  unbeglaubigten Aussagen auf UNBEKANNT. Falsche Positive 3→0, nutzbare Positive
  5→0. Das ist ein Policy-Tradeoff, keine Erkennung einer kompromittierten Quelle.
- [E1–E7-Konsolidierung](https://github.com/landjunge/agent-authority-lab/blob/f94f444e383052d04e2ef22bfed4ec03512cb066/docs/OBSERVER-RESEARCH-CONSOLIDATION-E1-E7-2026-10-07.md):
  E2-Dummymarker sind keine allgemeine Metadatenbereinigung; Epoch-/Inode- und
  Stressbefunde gelten für die damaligen begrenzten Versuche.

CodeQL-Run37941477846 ist getrennt zu lesen: Versuch1 scheiterte am
09.10. an nicht aktiviertem Code Scanning beim Upload. Versuch2 bestand am
11.10. auf demselben f94-SHA mit erfolgreichem Upload und abgeschlossenem
Processing. Das ist kein Nachweis semantischer Kompatibilität mit heutigem master.

## PR17: historische Autorisierungsreferenz

Quelle: [Draft-PR17](https://github.com/landjunge/agent-authority-lab/pull/17),
[vollständige 14 Service-Dateien an b24a6305faecc46ec673dea8207b2ab83ab655df](https://github.com/landjunge/agent-authority-lab/tree/b24a6305faecc46ec673dea8207b2ab83ab655df/service).
Alle 14 fehlen auf master; das bedeutet keinen heutigen Integrationsbedarf.

Der ursprüngliche Vertrag verlangt für jeden Agentenakt Gateway-Entscheidungen
`ALLOW`, `DENY` oder `REQUIRE_APPROVAL`, gesperrte Direkttools, Rechte- und
Budgetentscheidungen. Diese Rolle widerspricht D-012. `AuthorityCore.evaluate`,
`AuthorityGateway`, `ApprovalStore` und `TrustedAdapter` werden deshalb nicht
als heutige Agent-Authority-Produktschicht übernommen oder umbenannt.

Auch die separat betrachteten Teile ergeben keine fehlende Beobachtungsfunktion:
`AuditLedger` protokolliert interne Bewertung und Caller-Labels, keine gemessene
OS-Quelle oder Zielwirkung. `ExecutionReceipt.executed=True` folgt einer
Fingerprint-Prüfung ausdrücklich ohne tatsächlichen Seiteneffekt. `BLIND_MAP`
beschreibt die damalige Autorisierungsreferenz, keine aktuelle Monitorabdeckung.
Persistenz, Authentisierung und Mehrprozesskoordination waren ausdrücklich offen.

Die ursprünglichen Service-Tests wurden unverändert getrennt ausgeführt:
**16 Charakterisierungstests bestanden**, während die explizit aufgerufene
`adversarial_battery_01.py` **vier MISSED-Fälle** reproduzierte. Die Battery-Datei
wird bei der üblichen Verzeichnissammlung nicht automatisch gefunden. Grüne
Charakterisierung, die bekannt blinde ALLOW-Fälle erwartet, ist keine bestandene
Sicherheitsbattery. Keine Reparatur oder Änderung dieser historischen Referenz.

## Dokumentierter Entscheidungsvorschlag und Nachweise

Keine pauschale Integration von PR19 oder PR17. Den aktuellen Forschungsindex
als kleinen separaten Kandidaten prüfen; die vollständigen alten
Zweige und negativen Belege erhalten. Die zwei Testinvarianten gezielt
übernehmen; den eigenständigen Linux-FD-Verifier nur
bei einem späteren ausdrücklich beauftragten Forschungsvertrag bearbeiten.
PR17 begründet keinen neuen Implementierungsauftrag unter D-012.

Die Codex-Triage einschließlich ergänzender lesender Codex-Prüfung ersetzt
keinen unabhängigen Grok-PASS. Die alten PRs bleiben bis zur konkreten
Entscheidung offen; dieser Bericht schließt oder mergt sie nicht. PR38 bleibt
ein separater UTC-Kandidat. Historische RC-/CB-/OOS-/P4-Grenzen bleiben bestehen.

Vollständige 347-/14-Pfadkarten mit Hashes und Dispositionen, eingefrorene
Quellarchive, Befehle, JUnit und Rohlogs liegen unter
`~/.threaddesk/artifacts/agent-authority/pr19-pr17-triage-20261011/`.
Die Bestandszählung lässt sich aus den gepinnten Git-Objekten mit
`git ls-tree -r --name-only <SHA>` und dem ursprünglichen PR19-Delta mit
`git diff --name-only ef2400fa5fad3c4ff051928b78fcb3093bb23453 f94f444e383052d04e2ef22bfed4ec03512cb066`
reproduzieren. Quellenstand, aktuelle Laufzeit und datierte Abnahmeberichte
bleiben getrennt; es entsteht keine neue allgemeine Zuverlässigkeits- oder
Produktionsfreigabe.
