# Vorabvertrag: unveränderter Observer im vorhandenen Finish-/Späteffekt-Fall

8. Oktober 2026. Auftrag: einmalige nachgelagerte Prüfung, keine Entwicklung,
Reparatur oder Wiederholung. Interner, rollenseparierter Test (Level 1), kein
externer unabhängiger Audit. Ein separater lesender Kontext prüft die Methodik.

## Festgeschriebener Stand und Frage

Getesteter Ausgangscommit: `2ff7d1497d681f4d7b4be39945ec5688356693f2`.
Vollständig gelesen: [Fallblatt](OBSERVATION-CASE-FINISH-LATE-EFFECT.md),
[Originalbefund](FINDING-PHASE1-FINISH-ADAPTER-EFFECT-GAP.md),
[OOS-021 und übrige Schuld](OUT-OF-SCOPE-DEBT.md),
[Forschungsmethodik](RESEARCH-METHOD.md), vorhandener `observer_research.py`,
seine Bauplan-/Ergebnis-/Verifikationsdokumente und die vollständige
[Originalprobe](../probes/test_finish_adapter_effect_atomicity_probe.py).
Auch G3-Emitter, Lab-Lifecycle und FakeAdapter wurden gelesen.

**Hypothese:** Der unveränderte vorhandene Observer kann aus seinen vorhandenen
Eingangsdaten im bestehenden deterministischen Fall erkennen und zuordnen, dass
ein zuvor gestarteter Fake-Schreibeffekt erst nach zurückgekehrtem `Lab.finish()`
sichtbar wird, und Lifecycle-Ende von beendeten Effekten unterscheiden.

| Frage | Wortlaut / Maßstab |
|---|---|
| A | `finish() war abgeschlossen, bevor der Schreibeffekt sichtbar wurde?` Tatsächliche Rückkehr zum Coordinator, nicht Agentenabschluss oder Log-Ankunft. |
| B | `Kann der Observer den später sichtbaren Effekt sicher demselben vorher gestarteten Vorgang zuordnen?` Gemeinsamer Workflow allein ersetzt keine Effekt-/Vorgangsbindung. |
| C | `Kann der Observer unterscheiden zwischen Workflow beendet und alle daraus entstandenen Effekte beendet?` Cleanup ist keine Behauptung über vollständigen Executor-Stopp. |

Zulässige inhaltliche Antworten: JA, NEIN, UNBEKANNT / NICHT BELEGBAR.
Die Referenz beschreibt bei B den tatsächlichen Ursprung des Effekts, nicht eine
behauptete Observerfähigkeit. Bei C beschreibt sie den unterschiedlichen Zustand
von Lifecycle und ausstehendem Effekt am durch die Probe belegten Zeitpunkt.

## Bereits vor dem Lauf bekannte Schnittstellengrenze

`observer_research.infer` unterstützt nur `target_present`,
`appearance_vs_cli_end`, `appearance_vs_native_end`. Der Recorder akzeptiert nur
`run/kind/value/t_ns/event` und die fünf vorhandenen Klassen `tool_end`, `cli_end`,
`native_end`, `target_probe`, `target_final`. Der vorhandene G3-Emitter liefert
hingegen unveränderte Authority-Envelopes. Es gibt keinen vorhandenen G3→Recorder-
Übersetzer und keine Abfragen für A/B/C. FakeRepo ist ein In-Memory-Dictionary;
der vorhandene TargetSensor untersucht echte reguläre Dateien mittels `Path.stat`.

Diese Grenze wird **nicht** überbrückt. Insbesondere kein künstlicher Zielpfad,
kein `finish`→`native_end`, kein `workflow_id`→`run`, keine neuen Event-/Attempt-IDs,
Zeitstempel, Snapshot-/Effektmeldungen oder Antwortlogik. Ein Queryargument `1`
ist lediglich der unverändert erforderliche API-Parameter und **keine** belegte
Zuordnung zum Workflow; es wird nicht in den Eingangsdaten ergänzt.

Der Test prüft deshalb auch ausdrücklich, ob die tatsächlich angebotenen Daten
überhaupt angenommen werden und die beauftragten Fragen eine vorhandene Abfrage
haben. Scheitern diese Grenzen, wird kein künstlich passender Detector gebaut.

## Zulässige Eingangsdaten und Trennung

Einmal exakt die Originalprobe unter pytest ausführen. Bereits vorhandene
Exportkonfiguration: `LAB_AUTHORITY_EVENTS=1`, Ausgabe in einen neuen, isolierten
Testordner. Nur unveränderte, tatsächlich vom G3-Emitter geschriebene JSONL-Zeilen
dürfen dem Observer angeboten werden. Der explizite Flag ist nötig, weil der
bereits dokumentierte pytest-Default Export abschaltet. Er aktiviert keinen
neuen Sensor; zusätzliche I/O ist als Messbegrenzung auszuweisen.

Keine Ground Truth, Probe-Lokalen, Assertions, Threadsignale, privaten Labzustände,
Szenarioprognosen oder historischen Befunde werden in diese Eingabe übernommen.
Keine vollständigen Filesystem- oder FakeRepo-Dumps, keine Inhalte, Secrets oder
echten Identitäten lesen. Vorhandene Envelopes behalten ihre vorhandenen Felder
und wirklichen, vom Emitter erzeugten IDs/Zeitstempel unverändert.

**Unabhängige Referenz:** additive pytest-Hilfe
`probes/finish_observer_case_capture.py` liest mittels `sys.settrace` und
`threading.settrace` ausgewählte bereits vorhandene Probe-Zeilen sowie den
tatsächlichen `Lab.finish`-Rückgabewert. Kein Patch von Lab, Adapter, Repo, Probe,
Locks, Events, Assertions oder Timeouts. Beobachtungsaufwand beeinflusst Laufzeit;
die Ordnung wird ausschließlich durch die bestehenden Synchronisationsstellen
begründet. Es werden keine fehlenden Ereigniszeiten ergänzt.

Referenzpunkte: tatsächlicher eingereichter Request; bestandene ALLOW-Assertion;
bestandener `authorized.wait`; tatsächliche Finish-Rückgabe und danach erreichte
Probe-Zeile 48; bestandene Abwesenheitsprüfung vor Freigabe (Zeile 50); erfolgreiches
Release-Wait; bestandene Join-/Fehler-/Resultassertionen (Zeile 58), dortiger
Zielzustand und originale letzte Assertion. Live-Provenance-Anzahl und Register-
Existenz sind ausschließlich Referenzdiagnostik. Hash/Umfang des G3-Exports an
den bestehenden Checkpoints prüft nur Kanalabdeckung, keine Kausalität.

Der Probe-Lauf speichert diese Angaben separat in `ground-truth/checkpoints.json`.
Diese Datei bleibt bis zur gespeicherten Observerantwort ungelesen. Die getrennte
pytest-Berichtsaufnahme speichert nur Phase, Ergebnis und Exceptionklasse;
`--tb=no` verhindert einen automatisch ausgeschriebenen FakeRepo-Inhaltsdump in
der Ausgabe der erwarteten roten Assertion. Keine `longrepr`-Persistierung.
Die getrennte
Antwort-Hilfe `probes/finish_observer_case_responses.py` liest ausschließlich die
originale JSONL-Datei, ruft `check_events` sowie `infer` mit dem oben festgelegten
Wortlaut auf und speichert Rückgaben/Exceptions wortgetreu. Sie besitzt keinen
Ground-Truth-Leser. Testhilfen sind keine neue Produktfunktion.

Reihenfolge: Originaldaten erzeugen → Observer-Schnittstellenaufrufe → Antworten
mit exklusiver Dateierzeugung und Read-only-Modus sichern und Hash dokumentieren
→ erst danach Referenz lesen und vergleichen. Die Trennung ist prozessual und
funktional, keine Sicherheitsisolation gegen einen kompromittierten Versuchsleiter.

## Wertung vorab

Für jede Frage ausschließlich KORREKT, FALSCH oder UNBEURTEILBAR:

- JA/NEIN nur KORREKT, wenn vom realen Eingang getragen und unabhängig bestätigt.
- Sichere ungetragene oder widersprechende Aussage: FALSCH.
- Explizite, sachgerecht begrenzte Observerantwort UNBEKANNT: kein Erkennungserfolg;
  fehlende Prüfbarkeit wird als UNBEURTEILBAR gewertet und genau erklärt.
- Schema-/Queryexception oder nicht vorhandene Abfrage: **keine inhaltliche
  Observerantwort**. Extern als UNBEKANNT / NICHT BELEGBAR eingeordnet, getrennt
  vom wortgetreuen API-Fehler, UNBEURTEILBAR. Nicht behaupten, der Observer habe
  selbst korrekt UNBEKANNT ausgegeben. Schema-/Interfacebefund ist kein gemessener
  Ableitungsfehler; Detectorleistung wurde dann nicht ausgeführt.
- Frühere Assertion, Workerfehler, Timeout oder fehlender Referenzcheckpoint:
  Referenz-/Ausführungsfehler dokumentieren; nicht automatisch den Sollfall einsetzen.

Gesamt: SUPPORTED IN THIS CASE nur wenn notwendige Erkennung und Zuordnung
auf ausreichenden unabhängigen Referenzen tatsächlich gelingen; NOT SUPPORTED
bei beurteilbarem Observerfehler; ansonsten INCONCLUSIVE. Keine Gesamt- oder
Produktionsgarantie. Historische ALLOW-Entscheidung gehört nur zum Fake-Lab.

## Ausführung, Archivierung und STOPP

Vor Probeausführung diesen Vertrag, unveränderte Hilfen und Integritätsmanifest
committen, pushen und den Remote-SHA prüfen. Ausgangsdateien/Tests nicht ändern.
Neue Branch `research/observer-finish-late-effect-2026-10-08`.

Einmaliger Falllauf vom Repositoryroot:

```bash
PYTHONDONTWRITEBYTECODE=1 AA_FINISH_CASE_OUT=/tmp/aa-finish-observer-20261008 \
LAB_AUTHORITY_EVENTS=1 \
LAB_AUTHORITY_EVENTS_PATH=/tmp/aa-finish-observer-20261008/original/authority-events.jsonl \
/workspace/venvs/authority/bin/python -m pytest -p no:cacheprovider \
  -p probes.finish_observer_case_capture -o addopts='' -q --tb=no \
  probes/test_finish_adapter_effect_atomicity_probe.py
```

Erwartete historische rote letzte Assertion bleibt rot; sie ist kein neuer
Acceptance-Regressionsfehler. Nach dem einmaligen Lauf die vorhandene Standardsuite
ohne neue Ausschlüsse zweimal gemäß Methodik; keine erneute Probe und kein
Realagenten-/Stresstest. Python 3.12.14, pytest 9.1.1, vorhandene Umgebung wiederverwenden.

```bash
PYTHONDONTWRITEBYTECODE=1 /workspace/venvs/authority/bin/python -m pytest \
  -p no:cacheprovider -o addopts='' -q
```

Bestehende fünf RC-Deselektionen bleiben dokumentiert und unverändert. Ergebnis-
Confidence und Übertragungs-Confidence trennen. Neuer Bericht, Originalmessungen,
Ground Truth, vor Vergleich gesicherte Antworten und getrennte Auswertung unter
`docs/observer-finish-late-effect/2026-10-08/` speichern, committen und pushen.
**Danach STOPP: keine Reparatur, Felderweiterung, Wiederholung oder Folgefunktion.**
