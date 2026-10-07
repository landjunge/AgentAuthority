# Bauplan: Minimaldaten an realen Agentenläufen

**Vorab-Festlegung, 7. Oktober 2026.** Grundlage vollständig gelesen:
[Konsolidierung E1–E7](OBSERVER-RESEARCH-CONSOLIDATION-E1-E7-2026-10-07.md)
am Ausgangscommit `eb9ac5845c774db21338e88710c392f76bb482bb`.
Daniels neuer Auftrag erlaubt diesen Forschungsprototypen und reale Versuche.
Der STOPP des vorherigen Dokumentationsauftrags wird nicht als neuer Auftrag benutzt.
Historische Dateien, Gatebefugnisse, Tests und offene Befunde bleiben erhalten.

## Frage, Umfang und Hypothesen vor dem Bau

**Frage:** Welche Teilmenge der tatsächlich erfassten minimalen Angaben reicht
in unserem begrenzten realen Laufpanel für eine richtige Aussage über das lokale
Testziel und seine erste beobachtbare Erscheinung gegenüber dem CLI-Prozessende?

Ein Python-Programm mit Standardbibliothek, ein lokales Testwerkzeug und einfache
JSON-/Textausgabe. Ein Agentenzugang: der vorhandene Codex-CLI-JSONL-Weg.
Keine Graphen, UI, MCP-/Fremdproduktintegration, produktiven Ziele oder Secrets.
Keine Änderung des historischen Enforcement-Labs. AA beobachtet; der getrennte
Versuchsrunner führt nur die ausdrücklich beauftragten harmlosen Testläufe aus.
Timeout/Prozesspflege des Runners sind keine AA-Stop- oder Freigabefunktion.

Codex CLI `0.159.0-alpha.3` ist installiert. Modellzugriff und tatsächliche
Ereignisform müssen im Lauf belegt werden, nicht aus der Installation folgen.
Scheitert der Zugang, wird das als blockierter Lauf mit null belegten Agentenläufen
gemeldet; kein Fake-Lauf wird zum Ersatzbeweis umbenannt.

Vorab zu bewertende Forschungsbehauptungen:

1. **Status reicht:** Erfolgsmeldungen allein reichen für den Zielzustand.
   Widerlegt, sobald eine entschiedene Aussage einem unabhängigen Zielbeleg
   widerspricht. Unbekannt darf nicht als richtige Wirkungsbehauptung zählen.
2. **Eine kleine inhaltsfreie Sicht reicht:** Mindestens eine Teilmenge der unten
   begründeten Angaben erlaubt richtige Zielzustandsaussagen in allen tatsächlich
   beurteilbaren Panel-Läufen. SUPPORTED nur bei vollständiger Entscheidung dieser
   Fälle, ohne falsche Aussage und ohne verdeckten Zugriff auf die Referenzdaten.
   Fehlende Referenz oder unentscheidbare Fälle begrenzen das Ergebnis, keine
   automatische Bestätigung durch Schweigen oder Aussortieren fehlgeschlagener Läufe.
3. **Lokale Ordnung reicht für die begrenzte Zeitfrage:** Erscheinung vor/nach
   CLI-Ende lässt sich aus tatsächlich gemessenen lokalen Beobachtungsintervallen
   unterscheiden. Ein Intervall über der Endgrenze bleibt unbekannt. Keine
   Zehnsekundenannahme, verteilte Uhr, exakte Wirkungslatenz oder Remote-Stoppbehauptung.

Achse A: Implementierung hält diese Mess-/Datenbegrenzung ein.
Achse B: obige Aussagen können SUPPORTED, REFUTED oder INCONCLUSIVE werden.
Keine Hypothese wird nach gesehenen Ergebnissen verändert. Ergebnisse gelten nur
für kontrollierte reale LLM-Toolläufe, nicht allgemeine autonome Agenten.

## Fester Ablauf und unabhängige Referenz

Sechs reale, jeweils neue CLI-Aufrufe: `write`, `noop`, `fail`, `write_fail`,
`late`, nochmals `write`. Jede Aufgabe benutzt genau ein bereitgestelltes lokales
Testwerkzeug in einem eigenen temporären Ordner; dieselbe harmlose Zielbezeichnung
wird wiederverwendet. Der Agent soll das Werkzeug ausführen, nicht seine Wirkung
reparieren. Tatsächliche Abweichungen oder weitere Aufrufe werden gezählt und
erhalten; Sollmodus oder Agentenantwort ersetzen keinen beobachteten Zielbefund.

- `write`: leeres Testziel anlegen, Werkzeug erfolgreich beenden.
- `noop`: erfolgreiches Werkzeug ohne Anlegen des Testziels.
- `fail`: Werkzeugfehler ohne Anlegen des Testziels.
- `write_fail`: Testziel anlegen, danach Werkzeugfehler.
- `late`: Agent startet einen lokalen Kindprozess, der das tatsächliche Ende
  des beobachteten CLI-Prozesses abwartet und danach das Testziel anlegt.
  Kein Cancel-/Widerrufstest; nur eine lokale Lifecycle-/Nachwirkungsfrage.
- zweites `write`: erneuter realer Lauf mit gleicher Zielbezeichnung, keine
  behauptete Gleichheit physischer Objekte oder kryptografischer Identitäten.

**Beobachtersicht:** Projektierter CLI-Strom plus lokaler Ziel-Sensor. Der Sensor
beobachtet Existenzänderungen; bei Erscheinung hält er letzte bestätigte Abwesenheit
und erste bestätigte Anwesenheit fest. Ein gesonderter Snapshot bezeichnet den
Zustand am Abschluss des begrenzten Beobachtungsfensters. Gleichbleibende Polls
werden nicht vollständig gespeichert. Der Sensor interpretiert keine Inhalte.

**Referenz ausschließlich zum Bewerten:** Das Testwerkzeug protokolliert seine
tatsächlich erfolgte lokale Zielanlage mit lokaler Monotonic-Zeit getrennt von
AA. Nach dem Messfenster prüft der Runner den realen Zielzustand zusätzlich.
Diese Referenz ist kein Teil des Analysteninputs. Referenz fehlt/widerspricht sich:
unbeurteilbar, nicht Sollwirkung einsetzen. Kein allgemeiner Wahrheitsbeweis gegen
kompromittierte Werkzeuge; unsere instrumentierte lokale Strecke ist benannt.

Zwei Fragen: (a) Ziel am bezeichneten Fensterende vorhanden? (b) erste Erscheinung
vor/nach dem beobachteten CLI-Prozessende? Keine Wirkung: Zeitfrage nicht anwendbar.
Ein letzter Abwesenheitsbeleg nach CLI-Ende und spätere Anwesenheit tragen „nach“;
eine Anwesenheit vor Ende trägt „vor“. Erste Wahrnehmung nach Ende allein reicht nicht.

Alle Analysen werden zuerst aus ihrer jeweiligen Sicht berechnet und gespeichert;
erst danach erfolgt der Vergleich mit der getrennten Referenz. Keine Ableitung
aus Szenarioname, Referenzdatei, Agentenprosa oder erwarteter Wirkung.
Ablationen verwenden dieselben realen Aufzeichnungen, keine geänderten Prompts.
Eine flache gemeinsame Ereignisliste verhindert, dass Dateinamen entfernte
Laufbindungen ersetzen. Der Analyst kennt nur die abgefragte Laufreferenz und Sicht.

## Datenfeldprüfung: nur fünf Beobachtungsangaben

| Angabe | Begründeter Prüfpunkt / Messung | Grenze |
|---|---|---|
| `run` — lokale opaque Laufnummer | D Lauf-/Effektbindung: Zuordnung zweier realer Aufrufe; Entfernung der Bindung aus derselben gemeinsamen Sicht. | Vom tatsächlichen Runner-Aufruf gebunden, kein Klarname, Providerprincipal oder Projekt-Recht. |
| `kind` — feste Meldungs-/Beobachtungsklasse | D/F Status versus Zielbeleg: Toolabschluss, CLI-Prozessende, Zielprobe und Endsnapshot unterscheiden. | Nur vorhandene CLI-Meldungen bzw. eigene benannte Messstellen; keine erfundene Phase-2-/Remotequelle. |
| `value` — nur boolescher Erfolg bzw. beobachtete Existenz | G/E2 Metadatenbegrenzung und Zielzustandsfrage: Erfolg allein gegenüber ausdrücklichem lokalem Zielbefund. | Keine Reasonstrings, Rohargumente, Inhalte, Labels oder vollständige numerische Exitcodes. |
| `t_ns` — tatsächlich gemessene lokale Monotonic-Zeit | D Ordnung: beobachtete Erscheinungsgrenzen gegenüber CLI-Ende. | Empfangs-/Sensor-/Runnerzeit, kein ursprünglicher CLI-Toolstart, keine globale/Provideruhr. Für Zielzustand ablatierbar. |
| `event` — lokale opaque Belegnummer | D wiedererkennbarer Ereignisbezug: identische Wiederlieferung und veränderter Inhalt unter derselben Referenz. | Identität des projizierten Belegs, keine reale Effektidentität/Signatur oder allgemeine Replayabwehr. |

Alle Werte werden neu aus erlaubten Primitiven bzw. Messungen gebildet. Keine
Weitergabe beliebiger Strings durch Schlüssel-Whitelist. Kein Raw-JSONL,
Prompt-/Antwort-/Command-/Resulttext, Dateipfad, URL, Thread-ID oder Authmaterial
wird durch diesen Prototypen gespeichert. CLI läuft ephemeral; seine externe
Providerverarbeitung und sonstige systemeigene Telemetrie werden nicht als
kontrolliert ausgegeben. Nur inerte, bekannte Canarymarker in den Testaufgaben.

Getrennte **Versuchsbuchführung** speichert ausschließlich: Laufnummer/Modus,
CLI-Rückkehr-/Aufzeichnungsfehlerstatus, Rohbyte-/Zeilen-/Projektions-/Canaryzähler,
Referenz-Zielzustand, tatsächliche Werkzeugaufrufzahl und gemessene Referenzzeiten.
Diese Angaben begründen Reproduzierbarkeit, Ground Truth oder beobachtete Lücken;
sie sind kein heimlicher Analysteninput. Keine Tokens/Kosten/Personenprofile,
zusätzlichen Version-/Titel-/Rollen-/Herkunfts-/Ressourcenfelder auf Vorrat.

## Offene Prüfpunkte: je eine zugeordnete Messung

Die überlappenden offenen Punkte aus C/D/G/H der Konsolidierung sind hier
zusammengeführt. „Nicht untersucht“ schließt nichts und baut keine spätere Funktion.

| Vorhandener offener Punkt | Zugeordnete Messung | Umfang dieses Prototypen |
|---|---|---|
| Reale Lauf-/Instanz-/Effektzuordnung (C/D/G/H) | Gemeinsame Sicht der sechs Aufrufe; Feldablation `run` gegen separat zugeordnete Referenz. | Jetzt lokal; nur Aufrufbindung, keine echte Personen-/Provideridentität. |
| K14, reale Ressourcenalias-/Epochen-/Revisionsbindung (C/D/H) | Physische Objektbefunde vor/nach einem gezielten Alias-/Objektwechsel vergleichen, Actorbezug unverändert lassen. | Nicht untersucht: unser Panel hat keinen solchen Wechsel. Keine Ressourcenpflichtfelder sammeln; K14 bleibt INCONCLUSIVE. |
| Status versus Vollzug/Wirkung (D/F/G/H) | Erfolgsmeldung gegen lokalen Zielsnapshot und tatsächliche Anlage vergleichen; `noop`/`fail`/`write_fail` erhalten. | Jetzt, nur bezeichnetes lokales Ziel. Keine Nutzung/Buchung aus dem Status ableiten. |
| Cleanup/Cancel/Nachwirkung/OOS-021 (C/G/H) | Lokalen CLI-Endpunkt mit tatsächlicher späterer Zielanlage des gestarteten Kindprozesses vergleichen. | Jetzt lokaler Nachher-Fall; historische OOS-021, Remote-Stopp/Widerruf bleiben offen. |
| Originalzeit, Empfang/Ordnung/Dauer (C/D/G/H) | Gemessene lokale Beobachtungsintervalle und Endpunkt gegen getrennte Anlagezeit vergleichen; dieselbe Sicht ohne Zeit auswerten. | Jetzt lokal; Original-Anfragezeit, verteilte Uhren und genaue reale Ausführungslatenz nicht untersucht. |
| Duplikate, veränderte gleiche Referenz, Verlust/Coverage (C/D/G/H) | Eine identische Kopie, widersprechende Kopie und entfernte Zielbelege in einer Kopie der realen Aufzeichnung auswerten. | Jetzt als künstliche Übermittlungskontrolle; keine echte Netzwerk-/Replay-/Vollständigkeitsgarantie. |
| E2-Metadatenlücke, echte Fehlerpfade, erste Persistenz (C/G/H) | Inerte Marker im tatsächlich erzeugten Tool-/Fehler-/Ausgabetext zählen; alle benannten eigenen Archiv-/Reportdateien auf Markerwerte prüfen. | Jetzt neue eigene Strecke; kein Fix des historischen Emitters, keine echte Secret-/Heap-/DLP-Prüfung. |
| Quellechtheit, Quellenlüge/falsche Labels (C/D/H) | Statusbehauptung gegen unabhängigen lokalen Zielbefund vergleichen. | Nur lokale Diskrepanz; kompromittierte Runtime, kryptografische Echtheit und richtige Anfangslabels nicht untersucht. |
| Kontroll-/Datenherkunft, v1-Label, unmodelliertes `if` (C/D/G/H) | Tatsächlich übernommene instrumentierte Beziehung gegen separat bekannte Herkunft vergleichen. | Nicht untersucht: CLI-Metadaten liefern diese Lineage nicht; keine Ersatzlabels/-Kanten erfinden. |
| Kosten/Usage/Chargestufen/Zugang/TTL (C/D/H) | Quellenstufen gegen tatsächliche Ledger-/Zugangswirkung vergleichen. | Nicht untersucht: keine entsprechenden eigenen Quellen/Szenarien; keine Usage-/Budget-/Secretfelder sammeln. |
| Rollen/Delegation/Revision/Hinweisbearbeitung (C/D/H) | Tatsächliche Übergabe/Änderung gegen fachlich bekannten Auftrag vergleichen. | Nicht untersucht: keine Team-/Rollenquelle oder Übergabeaufgabe im Panel. |
| Analysebelege/Korrektur/optionale Angaben (D/H) | Jede Ausgabe auf sichtbare Belege, Scope und Unsicherheit prüfen; Feldminimalität an derselben Aufzeichnung vergleichen. | Jetzt für zwei Fragen; keine Regel-/Versions-/Hinweisstatusfelder auf Vorrat. |
| Prototypinput, lesbare Ausgabe/Zustellung (C/G/H) | Tatsächlichen CLI-Eingang, gespeicherte Projektion und ausgeführte Reportausgabe zählen. | Jetzt dieser Forschungsweg; keine Produktanzeige oder Fremdtoolintegration behaupten. |
| Empfängersicht/Maskierung/Hinweisexistenz (C/D/G/H) | Gleiche lokale Sicht bei geändertem Außenbezug unter ausdrücklich gesetzter Leseregel vergleichen. | Nicht untersucht: kein Empfänger-/Projektmodell bauen. Reale Rechte und allgemeine Nichtinterferenz bleiben offen. |
| Warnqualität/Nutzen/Mindestdaten/Menschenverständnis (C/G/H) | Korrekt/falsch/unbekannt gegen getrennte Referenz zählen; minimale richtige Feldmengen und getestete Ergänzungen ausweisen. | Jetzt Panelzahlen, keine Warnschwellen, allgemeinen Fehlerquoten oder Menschenstudie. |
| Rechtsgrundlage/Einwilligung/Leserrechte/Aufbewahrung/Anonymität (C/H) | Erfordert passende reale Festlegung bzw. eigene empirische Prüfung, nicht einen technischen LLM-Lauf. | Nicht untersucht/nicht durch diesen Lauf entscheidbar; keine solche Befugnis oder Garantie annehmen. |
| RC-01–05/CB-01, historische Teilkorrekturen und Snapshot-/Chronologiekonflikte (C/G) | Gegen ihren bereits dokumentierten konkreten Test-/Reviewumfang abgleichen. | Unverändert referenziert; kein neuer Reparatur-/Gateversuch, keine Schließung durch grüne Regression. |

## Messausgabe und Abnahme

Für jede Lauf-/Frage-/Sichtkombination: tatsächlich sichtbare Daten, abgeleitete
Aussage, korrekt/falsch/unbekannt/unbeurteilbar, Referenz erst in der Bewertung,
kleinste **getestete** Ergänzung aus den schon begründet erfassten Angaben.
Ungetestete weitere Informationen werden nicht als notwendig ausgegeben.
Alle Teilmengen der fünf Angaben werden untersucht; Werte, Dateinamen oder
Szenarionamen dürfen entfernte Beziehungen nicht heimlich wiedereinführen.
Minimalität gilt nur für diese Fragen, diese Auswertung und diesen Datensatz.

Zahlen: tatsächlich gestartete/belegte/blockierte Läufe, Werkzeugmeldungen,
Referenzabdeckung, richtige/falsche/unbekannte Aussagen getrennt, entschiedene
Abdeckung, gespeicherte Bytes und notwendige Feldmengen. Nicht anwendbare
Zeitfragen und fehlende Referenzen separat, nie zur besseren Quote wegfiltern.
Eine reine Erfolgsstatus-Baseline wird ebenfalls bewertet, einschließlich ihrer
Fehlaussagen. Vollsicht darf nicht über „immer unbekannt“ bestätigt werden.

Abnahme: neue bedeutungsvolle Tests für Datenschutzprojektion, Referenztrennung,
Fehlklassifikation/Unbekannt, Bindungs-/Zeitablation, Duplikatkonflikt und
Aufzeichnungsfehler; unveränderte Standardsuite zweimal mit vorhandenen fünf
RC-Ausschlüssen; reales Panel separat, keine simulierten CLI-Events als Realbeweis.
Getrennter read-only Methoden-/Code-/Ergebnisreview. Ergebnis-Confidence und
Generalisierungs-Confidence getrennt. Danach Commit/Push und begrenzter Befund;
keine automatische Erweiterung oder Produktentscheidung.

Dieser Bauplan wird vor Implementierung und Modellläufen committed/gepusht.
Die Konsolidierung und dieser Vorabteil bleiben anschließend unverändert.
