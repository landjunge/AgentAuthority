# Vorabvertrag: minimaler Beobachtungspfad für den vorhandenen Finish-Fall

8. Oktober 2026. Neuer ausdrücklich beauftragter Bau-/Prüfauftrag nach dem
abgeschlossenen [INCONCLUSIVE-Test](OBSERVER-FINISH-LATE-EFFECT-RESULTS-2026-10-08.md).
Ausgangspunkt: `e26b18c5c90761441a9a9d521c8dbbb4c741b700`. Dieser Vertrag wird
vor jeglicher Implementierung committed, gepusht und remote bestätigt.

## Gelesener Stand, Frage und Abnahme

Vollständig gelesen: vorheriger Ergebnisbericht und Vertrag, Finish-Fallblatt,
Originalbefund, Konsolidierung E1–E7, Real-Run-Prototypbericht, RESEARCH-METHOD,
OUT-OF-SCOPE-DEBT, observer_research.py, authority_emit.py, validator.py,
fake_adapter.py und die vollständige Originalprobe.

Der geprüfte Datenweg: G3 exportiert zwei post-decision Meldungen, keine
Finish-Rückkehr oder Wirkung. Seine unabhängig erzeugten Spans binden keine
Schreibausführung. Der vorhandene native Recorder passt nicht zu G3; sein
TargetSensor beobachtet reguläre Dateien, nicht FakeRepo. Die ursprünglichen
vier Sachbelege existierten ausschließlich in der getrennten Probe-Referenz.
Diese werden nicht zum Observerinput umbenannt.

**Hypothese:** Ein zusätzlicher passiver, quellennaher Messpfad mit echter
Schreibvorgangsbindung und konservativen lokalen Zeitgrenzen ermöglicht dem
Observer A/B/C im unveränderten vorhandenen Fake-Fall korrekt zu beurteilen.
Keine Hypothese allgemeiner Sicherheit, vollständiger Coverage oder minimaler
universeller Felder. OOS-021 bleibt offen und seine letzte Assertion rot.

| Frage | Zulässige Antworten / enger Aussageumfang |
|---|---|
| A: War finish abgeschlossen, bevor die beobachtete Wirkung eintrat? | JA / NEIN / UNBEKANNT. Nur diese tatsächliche Finish-Rückkehr gegenüber dieser tatsächlich beobachteten Fake-Schreibanlage. |
| B: Ist die beobachtete Wirkung demselben gestarteten Vorgang belastbar zugeordnet? | JA / NEIN / UNBEKANNT. Nur durch unten beschriebene echte Quellbindung; fehlende Bindung ist UNBEKANNT. |
| C: Kann Workflowende von allen beobachteten Wirkungen unterschieden werden? | JA / NEIN / UNBEKANNT. Nur der ausdrücklich bezeichnete beobachtete Schreibvorgang; keine Aussage, alle Wirkungen des Workflows seien erfasst oder beendet. |

Erfolg: A/B/C jeweils KORREKT auf unabhängiger Referenz, erforderliche
Negativkontrollen bestanden, unveränderte historische Suite zweimal und
unverändert roter OOS-021-Grundfall. Fehlende Referenz/Information bleibt offen.

## Kleinster zusätzlicher Messpfad

Ein opt-in Python-Tracer in `research/finish_effect_observation.py`, der nur
die tatsächlichen Codeframes von FakeAdapter.write, Lab.submit und Lab.finish
sowie die Rückkehr zum tatsächlichen Finish-Aufrufer beobachtet. Er kennt
keine Probe-Datei, Probe-Zeilen, Probe-Assertions, Freigabeevents oder Ground Truth.
Keine Änderung von Lab, FakeAdapter, FakeRepo, G3 oder Originalprobe erforderlich.
Keine neue Gesamtarchitektur, allgemeine Plugin-/Connector-/Callbackplattform.

1. Beim tatsächlichen Eintritt in FakeAdapter.write eine neue lokale opaque
   Vorgangsnummer bilden und an genau diesen Python-Ausführungsframe binden.
2. Beim tatsächlichen Rückkehren des darin aufgerufenen Lab.submit dessen
   vorhandenes `_WorkflowEntry`-Objekt und die konkrete Labinstanz ausschließlich
   transient der Schreibausführung zuordnen. Den tatsächlichen Callstack prüfen;
   weder gleiche Workflowbezeichnung noch Nähe ersetzen diesen Bezug.
3. Beim tatsächlichen erfolgreichen Lab.finish dasselbe konkrete Entryobjekt
   und dieselbe Labinstanz wiedererkennen. Seine Rückkehrmeldung nur den
   tatsächlich daran gebundenen Schreibvorgängen zuordnen. Keine Generation-ID
   erfinden, keine privaten Objektadressen oder Zustände exportieren.
4. Trace-Return unmittelbar vor tatsächlicher Rückkehr liefert nur deren untere
   Zeitgrenze. Erst der nächste tatsächliche Trace-Schritt im ursprünglichen
   Aufrufer bestätigt eine obere Grenze **nach** Rückkehr. Fehlt dieser Schritt,
   fehlt der Finish-Rückkehrbeleg. Keine Gleichsetzung mit native_end.
5. Im selben ursprünglichen Writeframe unmittelbar vor der vorhandenen
   Dictionaryzuweisung Zielanwesenheit prüfen und lokale Zeit messen; unmittelbar
   nach erfolgreicher Zuweisung erneut prüfen und messen. Keine Inhalte lesen.
   Nur diese ausgeführte Zuweisung erzeugt einen Wirkungsbeleg, nicht ALLOW.

Tracer-Kontrolle greift nicht in Callstack, Rückgabewerte, Rechte, Locks,
Threading-Events, Timeouts, Entscheidungen oder Zieländerung ein. Kein Lock wird
über Lab-/Adapteroperationen gehalten. Speicheraufwand und Trace-Verzögerung
bleiben eine bekannte instrumentierte Laborgrenze. Tracefehler werden als
Aufnahmefehler gezählt, ohne die originale Aktion zu stoppen oder zu reparieren.
Nach dem Fall nur noch gespeicherte Daten auswerten; keine Wiederholung.

## Feldprüfung: keine neuen Felder, vier wiederverwendete Angaben

Der neue Messstrom enthält ausschließlich `run`, `kind`, `value`, `t_ns`.
Das schon vorhandene `event` wird für A/B/C nicht gebraucht und nicht erzeugt.
Keine Duplikatlieferungs-/Replayidentität behaupten. Identische vollständige
Zeilen dürfen zusammenfallen; unterschiedliche mehrfache Belege derselben
Messstelle werden nicht bequem ausgewählt, sondern bleiben UNBEKANNT.
G3 wird weder erweitert noch übersetzt; sein Export ist kein zusätzlicher
Analysteninput. Keine Identitäten, Pfade, Rollen, Workflowstrings, Zustandsdumps,
Prompts, Chats, Argumente, Resulttexte, Secrets oder Screenshots im Messstrom.

| Wiederverwendetes Feld | Konkrete Notwendigkeit und Quelle |
|---|---|
| `run` | B und die vorgangsbezogenen A/C brauchen die echte gemeinsame Bindung. Hier beim tatsächlichen Writeframe-Eintritt gebildeter Token; durch denselben Frame und tatsächliche Entry-/Labobjektidentität weitergetragen. Nicht workflow_id, span_id, Dateiname, Abfrageargument oder nachträgliche Enumeration. |
| `kind` | A/C müssen tatsächlichen Start, tatsächliche Finish-Rückkehr und tatsächliche Wirkung unterscheiden. Fünf unten begrenzte Messstellen, keine Statusumdeutung. |
| `value` | Positiver Start-/Rückkehrbeleg bzw. tatsächliche Zielanwesenheit vor/nach der Zuweisung. Ohne tatsächlichen Zielbeleg darf kein ALLOW zur Wirkung werden. Vorher-Abwesenheit und Nachher-Anwesenheit tragen hier die beobachtete Anlage. |
| `t_ns` | A und der zeitbezogene Unterschied in C brauchen vergleichbare lokale Grenzen. Gemessene monotonic_ns derselben Prozessuhr an benannten Quellmessstellen, keine Empfangs-/Appendordnung oder globale Uhr. B allein kann ohne Zeit entschieden werden, wenn seine tatsächlichen Bindungsbelege vorhanden sind. |

Genau fünf neue, fallbezogene **Werte von kind**, keine neue Feldspalte:

- `write_started`: tatsächlicher Eintritt, value=True.
- `finish_return_before`: untere Grenze unmittelbar vor tatsächlicher Finish-Rückkehr, value=True.
- `finish_return`: obere Grenze nach tatsächlicher Aufruferrückkehr, value=True.
- `write_effect_before`: untere Grenze vor tatsächlicher Zuweisung; value ist dortige Zielanwesenheit.
- `write_effect`: obere Grenze nach tatsächlicher erfolgreicher Zuweisung; value ist dortige Zielanwesenheit.

Sichere positive Ordnung nur bei strikt getrennten Grenzen:
`finish_return.t_ns < write_effect_before.t_ns` für JA, und
`write_effect.t_ns < finish_return_before.t_ns` für NEIN. Gleiche, überlappende,
fehlende, ungültige oder widersprüchliche Grenzen ergeben UNBEKANNT. Für den
Vergleich müssen auch `finish_return_before <= finish_return` und
`write_effect_before <= write_effect` gelten. Eine eigene fallbezogene Prüfung
der vier Felder erlaubt fehlende Felder in Kontrollsichten und liefert dann
wirklich UNBEKANNT; der historische fünfspaltige `check_events`-Pfad bleibt
unverändert und wird hier nicht als Fehler→UNBEKANNT-Ersatz benutzt.
Für den
bezeichneten Anlagefall werden tatsächliche Abwesenheit vor und Anwesenheit nach
der Originalzuweisung benötigt. Die Vorgangs-/Belegarten müssen passend und
eindeutig sein; keine Auswahl eines bequemen Teilbelegs aus Widersprüchen.

Additive `infer_finish_effect`-Auswertung in observer_research.py; bisherige
Recorderkinds, Abfragen, real-run-Auswertung und alle historischen Artefakte
bleiben unverändert. Antworten aus beobachteten Angaben allein, mit begrenztem
Begründungscode. Für C ausdrücklich nur beobachteter Vorgang, keine Behauptung
globaler Wirkungsvollständigkeit. Keine Entscheidung-/Eingriffsfunktion.

C ist eine begrenzte Unterscheidungsfrage: JA nur wenn Start, tatsächliche
Finish-Rückkehr und tatsächliche Wirkung dieses Vorgangs passend gebunden und
ihre konservativen Grenzen strikt getrennt sind. Bei A=JA wird ausdrücklich
benannt, dass dieser Effekt nach abgeschlossenem Lifecycle eintrat; bei A=NEIN,
dass dieser Effekt bereits vorher belegt ist. Beide erlauben die Unterscheidung,
also C=JA; keiner erlaubt eine Aussage über unbeobachtete Effekte. Fehlende,
überlappende oder widersprüchliche Belege ergeben C=UNBEKANNT, niemals eine
pauschale Aussage C=NEIN über die grundsätzliche Fähigkeit oder alle Effekte.

## Vorab festgelegte Kontrollen und einmaliger Originalfall

Nach Implementierung genau die vorhandene
`probes/test_finish_adapter_effect_atomicity_probe.py` ausführen. Keine Kopie
mit bequemeren Assertions und kein neuer Ersatzablauf. Originaler finaler FAIL
muss bestehen bleiben. Neue pytest-Aufnahmehilfe installiert den passiven
Quelltracer und komponiert ihn mit der bisherigen privaten Probe-Referenzaufnahme.
Die zwei Kanäle teilen nur Python-Trace-Aufrufe, keine extrahierten Daten oder
Antworten. Referenz besteht weiterhin aus Originalassertions/Synchronisation;
sie konsumiert keine neuen Observerbelege. Vorherige Aufnahmehilfe unverändert.

Originalmessungen, Aufnahmefehlerzahl und separate Referenz speichern. Getrennte
Antwortauswertung liest nur den neuen Messstrom. Antworten A/B/C und alle unten
festgelegten Datensichtkontrollen vor Lesen der Referenz exklusiv speichern,
read-only setzen und hashen; erst danach Referenz lesen und KORREKT/FALSCH/
UNBEURTEILBAR vergleichen. Kein Sollwert als Referenz einsetzen.

Mindestens folgende Kontrollen auf **Kopien** derselben Originalaufnahme, ohne
neuen Agenten-/Probeablauf; originale Zeilen bleiben unverändert:

1. Beide Wirkungsbelege entfernen: A/B/C UNBEKANNT, keine Wirkungsbehauptung.
2. Beide Finishbelege entfernen: A/C UNBEKANNT; B darf die vorhandene
   Start-/Effektzuordnung dieses Vorgangs erhalten, darf aber keine Finishbindung
   oder Reihenfolge behaupten.
3. `run` aus Effektbelegen entfernen: A/B/C UNBEKANNT, keine Ersatzbindung.
4. `t_ns` entfernen und Liste umkehren: A/C UNBEKANNT; B darf aus der echten
   erhaltenen Vorgangsbindung entscheiden. Empfangsfolge ist keine Ereignisordnung.
5. Nur tatsächliche originale G3-ALLOW-Meldung anbieten: A/B/C UNBEKANNT,
   keine automatische Übersetzung oder Wirkungsbehauptung.
6. Empfangsfolge bei erhaltenen echten Zeitgrenzen umkehren: Antworten müssen
   gegenüber der Vollsicht gleich bleiben.

Gezielte synthetische Unitkontrollen dürfen zusätzlich Gleichheit/Überlappung,
Widerspruch, explizite Vorhergrenzen, nicht passende Vorgangsbindung und
fehlgeschlagene Aufnahme prüfen; das sind keine weiteren realen Szenarien.
Kein neues Pflichtfeld aus diesen Kontrollen ableiten. Die historische Suite
und ihre fünf RC-Deselektionen nicht verändern; Standardsuite zweimal ausführen.

## Commitfolge, Grenzen und STOPP

Vertrag als Docs-only-Commit vor Implementierung pushen. Implementierung/neue
Unitkontrollen separat committen/pushen und vor Originalfall festschreiben.
Danach Originalaufnahme, vor Vergleich gesicherte Antworten, getrennte Referenz,
Kontrollen und Auswertung sowie neuer Ergebnisbericht unter
`docs/observer-finish-minimal-path/2026-10-08/` speichern und committen/pushen.
Ausgangs-, Vertrags- und Implementierungs-SHA dokumentieren, Remote bestätigen.

Keine existierenden Forschungsbefunde umschreiben. Interne lesende Prüfung,
keine externe Auditbehauptung. Confidence im engen Fakefall getrennt von LOW-
Übertragungs-Confidence. Keine andere Effektart, verteilte Uhr, echte Agenten,
vollständige Wirkungserfassung, Schutz-/Stopfunktion oder Quellechtheit behaupten.
**Danach STOPP: keine weitere Funktion, kein Graph, keine Belastungsstufe,
keine OOS-021-Reparatur und keine neue Architektur.**
