# Minimaldaten-Prototyp: gemessener Forschungsstand

7. Oktober 2026. Agent Authority bleibt ein selbständiger Beobachter.
Dieses Instrument untersucht zwei lokale Aussagen; es entscheidet nicht über Aktionen.

## Grundlage und feste Grenzen

Vollständig gelesene Grundlage: [Konsolidierung E1–E7](OBSERVER-RESEARCH-CONSOLIDATION-E1-E7-2026-10-07.md),
Ausgangscommit `eb9ac5845c774db21338e88710c392f76bb482bb`.
Der [Bauplan](OBSERVER-REAL-RUN-PROTOTYPE-PLAN-2026-10-07.md) wurde vor dem Bau
unter `3aec561fb8ada2b3299dc4c559158591c0c1e2ba` eingefroren und gepusht.
Die [belegte CLI-Grenze und native Alternative](OBSERVER-REAL-RUN-RUNTIME-RESOLUTION-2026-10-07.md)
wurden vor Umsetzung und Läufen dieses Zusatzwegs unter
`937c8cecb434fce58ee4602d98a51446f8eda68a` separat eingefroren und gepusht.
Erster festgeschriebener Implementierungscommit:
`091a44864499b3832a8d68206638295acb9b061f`.
Der [abgeschlossene Erstreview und enge Korrekturvertrag](OBSERVER-REAL-RUN-PROTOTYPE-VERIFICATION-2026-10-07.md)
halten einen Referenzvalidierungsfehler ausdrücklich fest. Die anschließende
Messlogik-Korrektur ist unter `d724ce14d08e1d13fd8cf1ccf0d0d282ce6747d0`
separat committed und gepusht. Ein weiterer Review erhielt den Restfehler
unbekannter/leerer Receiptformen als FAIL; die begrenzte Schließung unter
`cb198818f38ccd92317cb7072d95751b4c16bd25` akzeptiert ausschließlich die drei
bereits vorhandenen privaten Testwerkzeugformen. Spec, Hypothesen und Originaldaten
bleiben erhalten; die früheren FAIL-Befunde werden nicht überschrieben.

Gebaut wurden [Aufnahme und Auswertung](../observer_research.py),
ein [harmloses Testwerkzeug](../research/agent_task.py) und der begrenzte
[native Versuchsdriver](../research/native_driver.py), ausschließlich mit Python-Standardbibliothek.
Keine Graphen, UI, allgemeine Connectorplattform oder vorsorglichen Datenfelder.
Der Driver führt die beauftragten Testaufgaben aus; diese Ausführung ist keine
Befugnis des Beobachters. Historischer Labcode, Tests, Quellen und eingefrorene
Dokumente wurden nicht verändert. Kein E8 oder Folgeexperiment begonnen.

## Tatsächliche Läufe und ihre Herkunft

**Direkte Codex-CLI:** 13 gestartete Prozesse in zwei Sechs-Fall-Panels und einem
Wiederanlauf, **0 belegte Modellläufe, 0 Werkzeugmeldungen**.
Die begrenzte [Startbuchführung](observer-real-runs/2026-10-07/cli-startup-attempts.json)
enthält nur Status und Zähler. Jeder Versuch erzeugte 197 stderr-Bytes und keine
stdout-Ereignisse. Diagnose erkannte generische Read-only-Dateisystemfehler;
Rohmeldungen wurden nicht gespeichert. Der exakte Ursprung im installierten
Alpha-Build und dessen Modell-/Authentisierungszugang sind damit nicht geklärt.
Die ursprünglichen CLI-Hypothesen bleiben **INCONCLUSIVE**.

**Getrennter nativer Aufbau:** Sechs neue native Codex-Collaboration-LLM-Kontexte
führten jeweils einen echten lokalen Terminalaufruf des Drivers aus.
Es handelt sich um kontrollierte Mikroaufgaben, keine freien autonomen Workflows.
Der Versuchsleiter beobachtete die tatsächlichen Agentenabschlüsse und meldete
erst danach den Empfang an den Driver. Die Archivdateien allein authentisieren
keinen Modellaufruf; der Aufbau vertraut dieser beobachteten Orchestrierung.

`native_end` bedeutet Empfang des Agentenabschlusses beim Versuchsleiter.
Es bedeutet weder Werkzeugerfolg noch physisches CLI-/Executorende oder Remote-Stopp.
Die Zeitfrage lautet deshalb ausdrücklich `appearance_vs_native_end`.
Beim Nachher-Fall wartete ein real gestartetes Kindwerkzeug auf diesen Empfangspunkt
und legte danach das leere Testziel an. Die Versuche benutzten ausschließlich
disposable lokale Dateien und inerte Marker, keine echten Zugangsdaten.

Die sechs nativen Läufe erzeugten **6 Werkzeugmeldungen, 32 Beobachtungen,
0 Sensorfehler und 0 Werkzeug-Timeouts**. Jede unabhängige Referenz bestätigt
genau einen tatsächlich erfolgten Testwerkzeugaufruf.

## Zahlen und widerlegbare Vergleiche

| Lauf | Aufgabe | Gemeldeter Werkzeugerfolg | Ziel im Endsnapshot | Anlage gegenüber `native_end` |
|---|---|---|---|---|
| 1 | `write` | ja | vorhanden | vorher |
| 2 | `noop` | ja | nicht vorhanden | nicht anwendbar |
| 3 | `fail` | nein | nicht vorhanden | nicht anwendbar |
| 4 | `write_fail` | nein | vorhanden | vorher |
| 5 | `late` | ja | vorhanden | nachher |
| 6 | erneutes `write` | ja | vorhanden | vorher |

Alle sechs Agentenabschlüsse wurden empfangen, auch bei Werkzeugfehlern.
Die Referenz stammt aus tatsächlichen syscall-nahen Anlageintervallen und einem
getrennten späteren Zielcheck. Szenarionamen oder erwartete Wirkung bestimmen
keine Analystenantwort. Ein überlappendes Intervall wäre unbeurteilbar geblieben;
die vorhandenen vier Anlageintervalle überlappen ihre End-/Snapshotgrenzen nicht.

| Sicht / ausdrücklich getestete Ableitung | Korrekt | Falsch | Unbekannt | Nicht anwendbar | Unbeurteilbar |
|---|---:|---:|---:|---:|---:|
| Fünf-Felder-Vollsicht, eigener Analyst | 10 | 0 | 0 | 2 | 0 |
| Abschlussmeldung als Zielwirkung interpretieren | 4 | 2 | 4 | 2 | 0 |
| Werkzeugstatus als Zielwirkung interpretieren | 4 | 2 | 4 | 2 | 0 |
| Eigener Analyst ohne erforderliche Zielbelege | 0 | 0 | 10 | 2 | 0 |

Die Statusvergleiche sind bewusst zu prüfende vereinfachte Benchmarks, keine
Produktfunktion von AA. Abschlussstatus überschätzt `noop` und `fail`.
Werkzeugstatus überschätzt `noop` und unterschätzt die tatsächlich erfolgte
Anlage in `write_fail`. Sie können keine der vier anwendbaren Zeitfragen entscheiden.
Die beiden nicht anwendbaren Zeitfragen wurden erst bei der Referenzbewertung
so erkannt; der Analyst beantwortete sie mit unbekannt, nicht mit „kein Effekt“.

**H1 Status allein reicht: REFUTED im nativen Panel.** Je zwei falsche
Zielaussagen sind konkrete Gegenbelege. Ein Werkzeugfehler beweist ebenso wenig
Wirkungslosigkeit wie ein erfolgreicher Abschluss die gewünschte Wirkung beweist.

**H2 kleine inhaltsfreie Sicht reicht: SUPPORTED ausschließlich für die sechs
bezeichneten lokalen Zielsnapshots dieses Panels und den festgelegten Analysten.**
Alle sechs sind entscheidbar und korrekt; kein beurteilbarer Fehlerfall wurde entfernt.

**H3 lokale Ordnung reicht: SUPPORTED ausschließlich für die vier anwendbaren
Vergleiche mit dem empfangenen nativen Kommunikationsabschluss.** Drei Anlagen
lagen vorher, eine danach. Kein Beleg für die ursprüngliche CLI-Endfrage,
Remote-Stopp, Widerruf oder ausbleibende spätere Wirkung nach dem Messfenster.

## Welche Daten tatsächlich reichten

Der gemeinsame Beobachtungsstrom speichert nur `run`, `kind`, `value`, `t_ns`,
`event`: lokale opaque Lauf-/Belegnummer, feste Ereignisklasse, boolescher Wert,
tatsächlich gemessene lokale Monotonic-Zeit. Rohtext, Pfad, URL, reale Identität,
Argumente und Modellprosa sind keine Analysteneingabe.

Alle **32 Feldteilmengen derselben Aufzeichnung** wurden über alle sechs Läufe
und zwei Fragen verglichen: 384 abgeleitete Bewertungen, davon 32 korrekt,
288 unbekannt und 64 nicht anwendbar. Hinzu kommen 24 Statusbewertungen und
12 Zielbeleg-Verlustbewertungen: insgesamt 420 Ableitungen, **keine 420 unabhängigen
Agentenversuche**. Jede Vorhersage wurde vor dem Lesen der Referenz gespeichert.

| Frage | Gemeinsame kleinste erfolgreiche Feldmenge im beurteilbaren Panel | Getestete Ergänzung |
|---|---|---|
| Ziel am bezeichneten Endsnapshot vorhanden? | `run`, `kind`, `value` | Ein tatsächlicher `target_final`-Snapshot je Lauf. Ohne diesen Beleg blieb dieselbe Auswertung unbekannt; mit ihm waren alle sechs Antworten korrekt. |
| Anlage vor/nach empfangenem Abschluss? | `run`, `kind`, `value`, `t_ns` | Tatsächliche `target_probe`-Beobachtungen plus Endpunkt. Vorher benötigt eine bestätigte Anwesenheit vor Ende; nachher bestätigte Abwesenheit nach Ende und spätere Anwesenheit. |

Die getesteten Ergänzungen sind bereits aufgezeichnete Belege, keine nachträglich
erfundenen Pflichtfelder. [Report](observer-real-runs/2026-10-07/native/report.json)
enthält pro Fall die Aussage, Bewertung, minimale richtige Feldmengen und getestete
Feldergänzungen innerhalb derselben ursprünglichen Beobachtungszeilen.
Bei Status-/Belegverlustkontrollen ist diese Feldaddition nicht anwendbar (`null`),
weil fehlende Beobachtungen keine fehlenden Spalten sind.
`information_comparisons` benennt die tatsächlich entfernten und
wieder hinzugefügten Zielbelege mit Belegnummern. `panel_fieldsets` prüft dieselbe
Feldmenge über alle beurteilbaren Läufe, nicht nur separat pro Erfolg.

**Grenze der Minimalität:** Der Analyst ist festgelegt und verwendet bewusst
keine Ersatzbindung aus Lieferreihenfolge oder Belegnummer. Ein alternatives
Verfahren könnte andere vorhandene Informationsträger nutzen. Die Ablationen
beweisen daher keine universelle oder informationstheoretische Unersetzbarkeit
einzelner Felder. Pro Lauf gibt es genau ein vorab bezeichnetes Testziel; daraus
folgt kein allgemeiner Ressourcenschlüssel oder eine Lösung von K14.

`event` war für keine der beiden Sachfragen erforderlich. Es dient ausschließlich
der begründeten lokalen Beleg-Kopiediagnostik: Eine künstliche Wiederlieferung
erhöhte 32 auf 33 Lieferungen, blieb nach Deduplikation bei 32 Belegen und erzeugte
keinen Konflikt; veränderter Inhalt unter derselben Belegnummer wurde widersprüchlich.
Diese Kontrollen bearbeiten Kopien echter Messdaten, erzeugen keine neuen realen
Agenten-/Netzwerkläufe und belegen keine Echtheit oder allgemeine Replayabwehr.

## Speichergrenze und bekannte Probleme

Der reine Beobachtungsstrom benötigt **2.433 Bytes**. Alle fünf nativen Archivdateien
zusammen benötigen **299.718 Bytes**, überwiegend abgeleitete Bewertungsmatrizen;
die separate CLI-Startbuchführung weitere 4.205 Bytes.
Das ist keine Messung von Gesamt-RAM oder externer Provider-/Runtimepersistenz.

Die tatsächlichen Werkzeugausgaben enthielten acht Zeilen mit bekannten inerten
Markern, darunter simulierte Actor-/URL-Metadaten und zwei Fehlermeldungen.
In den fünf benannten eigenen Archivdateien wurden **0 Markerwerte** gefunden.
Das stützt die primitive Neubildung der Daten in dieser eigenen Strecke.
Es ist kein allgemeiner Secretfilter-/DLP-/Datenschutzbeweis und **keine Reparatur
der historischen E2-Metadatenlücke**. Systemseitige native Dialog-/Toolprotokolle,
Providerverarbeitung und unbekannte sensible Werte wurden nicht geprüft.

Während der Bauprüfung wurden Aufnahme-/Bewertungsfehler gefunden und vor dem
abschließenden Codefreeze abgesichert: vollständig verlorene Läufe bleiben im
festen Sechs-Lauf-Frageraster; Startfehler/Timeouts bleiben in der Buchführung;
eine fehlgeschlagene Endprobe liefert keinen alten Cutoff; Referenz-Checkfehler
werden unbekannt; positive Zeitbehauptungen bei fehlendem Effekt zählen falsch.
Nach dem realen Panel wurden diese Fehlerpfade und die Ableitungen ergänzt;
die gespeicherten Messbelege wurden nicht geändert und das reale Panel nicht
als neuer Lauf wiederholt. Die finalen Analysen verwenden dieselben Originaldaten.
Die ursprüngliche Aufnahmebuchführung besitzt noch keine Felder `tool_attempts`
und `failure` des finalen Serializers. Sie wurde nicht nachträglich ergänzt oder
als exakt vom finalen Code erzeugtes Capture ausgegeben. Ihre vorhandenen
Werkzeugzähler und getrennten Referenzaufrufe tragen die berichteten sechs Aufrufe.
Der Erstreview fand außerdem ungültige Receipt-/Zeitintervalltypen und einen
nicht-stringförmigen CLI-Recordtyp als statische Fehlerpfade. Die dokumentierte
Korrektur macht ungültige Referenzen unbeurteilbar und zählt den Recordfehler.
Die gültigen Originalintervalle und ihre Ergebniszahlen änderten sich dadurch nicht.
Unbekannte/leere oder falsch behauptete private Receiptformen werden ebenfalls
abgewiesen; fehlende Referenzinformation wird dadurch nicht zu „kein Effekt“.

## Was offen bleibt

Der Bauplan ordnet jeden vorhandenen Prüfpunkt einer Messung oder ausdrücklich
„nicht untersucht“ zu. Dieses Panel schließt insbesondere folgende Fragen nicht:

- Direkte CLI-/weitere Agentenzugänge und deren reale Ereignis-/Fehlerpfade.
- K14: Alias-, Ressourcenwechsel-, Revisions- und Epochenbindung.
- Echtheit/Unvollständigkeit von Quellen, kompromittierte Werkzeuge, Quellenlügen,
  uninstrumentierte Aktionen und tatsächlicher Nachrichtenverlust.
- Original-/verteilte Uhren, globale Kausalität, echte Laufzeit-/Wirkungslatenz.
- Historische OOS-021, Remote-Stopp/Cancel/Cleanup und spätere Nachwirkungen
  außerhalb des begrenzten Messfensters.
- Daten-/Kontrollherkunft, falsche Anfangslabels und unmodellierte implizite Flüsse.
- Reale Kosten/Usage/Ledger, Zugänge/TTL, Rollen, Delegation, Revisionen.
- Empfängersicht, Leserechte, Maskierung, Hinweisexistenz und Nichtinterferenz.
- Menschlicher Nutzen/Warnqualität, allgemeine Fehlerquoten, rechtliche Grundlage,
  Aufbewahrung und nachgewiesene Anonymität.
- Historische E2-Metadatenlücke sowie RC-01–05 und CB-01 mit ihren eigenen Grenzen;
  vorhandene Snapshot-/Chronologiekonflikte bleiben erhalten.
- Authentisierung fertiger Referenzarchive gegen nachträgliche Manipulation;
  der Report arbeitet mit dem benannten, geprüften Originalarchiv. Die private
  Receiptvalidierung ist keine allgemeine Archivintegritätsgarantie.

Diese Unbekannten sind keine negativen Beweise und erzeugen hier keine neuen
Felder, Schutzmechanismen, Architektur- oder Produktentscheidungen.

## Ausführen und nachprüfen

Vom Repositoryroot, Python 3.12; für Aufnahme/Auswertung keine Zusatzpakete:

```bash
# Gesicherte native Daten erneut auswerten, ohne neue Agentenläufe:
python observer_research.py report --native --input docs/observer-real-runs/2026-10-07/native

# Dasselbe feste Panel über eine tatsächlich funktionsfähige eigene Codex-CLI:
python observer_research.py capture --out /tmp/aa-new-cli-panel
python observer_research.py report --input /tmp/aa-new-cli-panel
```

Aufnahme benötigt einen neuen Ausgabeordner. Der Report überschreibt nur seine
abgeleiteten `predictions.jsonl` und `report.json`; Originalbeobachtungen,
Aufnahmebuchführung und Referenz bleiben erhalten. `--native` setzt ausdrücklich
die Forschungsfrage, damit selbst vollständiger Ereignisverlust sie nicht ändert.
Ein CLI-Startfehler wird nicht zum gelungenen Agentenlauf erklärt.

Für einen weiteren ausdrücklich beauftragten nativen Lauf: zuerst
`python -m research.native_driver serve --session /tmp/aa-new-native-panel`.
Dann erhalten sechs neue echte Agentenkontexte je genau den Terminalaufruf
`python -m research.native_driver call --session /tmp/aa-new-native-panel --run N`,
mit `N=1..6`, ohne Reparatur, weitere Dateien/Netzwerk oder Unteragenten.
Der bereitgestellte Driver weist den festen Modus zu; der Kontext bekommt keine
Referenzdaten. Erst nach tatsächlich empfangenem Abschluss des betreffenden
Agenten meldet der Versuchsleiter `close` mit derselben Session und Laufnummer.
Nach allen Abschlüssen folgt `finish` mit derselben Session, dann
`python observer_research.py report --native --input /tmp/aa-new-native-panel`.
Manuelles `call`/`close` ohne echte Agentenkontexte ist ein Fixturetest und darf
nicht als realer Agentenbeleg ausgegeben werden. Das geschieht hier nicht erneut.

## Prüfung und Confidence

Python 3.12.14, pytest 9.1.1: 65 neue Messlogiktests; unveränderte Standardsuite
nach dem abschließenden Codefix zweimal mit `python -m pytest -o addopts='' -q`:
jeweils **304 passed, 5 deselected**.
Die bestehenden fünf RC-Ausschlüsse bleiben erhalten; grüne Regression schließt
ihre historischen Misses nicht. Neue Tests enthalten synthetische Daten und
lokale Fixtureaufrufe, die keine zusätzlichen echten Agentenläufe belegen.
Keine historischen Tests wurden abgeschwächt.

Die [Reviewdatei](OBSERVER-REAL-RUN-PROTOTYPE-VERIFICATION-2026-10-07.md) erhält
die Erstbefunde und den abschließenden Review am festgeschriebenen Korrekturcommit.
Achse A ist Mess-/Datenvertragskonformität; Achse B enthält die drei begrenzten
Hypothesenurteile oben. PASS wäre weder Sicherheitsbeweis noch generalisierte
Monitoring-Leistung. Interne Reviews sind keine externen Audits.

**CONFIDENCE IN EXPERIMENT RESULT:** HIGH für die gespeicherten, konstruierten
Informationsvergleiche und Referenzintervalle; MEDIUM für die reale Aufnahme im
kleinen, instrumentierten Panel mit vertrauenswürdiger Orchestrierung.
**CONFIDENCE IN GENERALIZATION:** LOW für freie reale Agenten, andere Quellen,
Empfänger, Ressourcen, Uhren und Monitoring-/Schutzfunktionen.

**Forschungsgewinn:** Status genügte nachweislich nicht; sechs lokale Zielzustände
ließen sich ohne Inhalte mit drei Angaben korrekt feststellen, vier lokale
Zeitvergleiche mit einer weiteren. Diese Begrenzung und die benötigten Zielbelege
sind gemessen. Alle übrigen Forschungsfragen bleiben offen. **STOPP.**
