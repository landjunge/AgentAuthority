# Forschungsstand von Agent Authority nach E1–E7

**Konsolidierung, 7. Oktober 2026.** Ausschließliche Belegbasis ist der bereits
dokumentierte Stand im Repository bei
[`cd94ffeaacddba77d16f6c5e21a5064ffd30164d`](https://github.com/landjunge/agent-authority-lab/commit/cd94ffeaacddba77d16f6c5e21a5064ffd30164d).
Dieses Dokument führt keine Experimente, Tests, Reparaturen, Implementierung oder
neue externe Recherche durch. Bestehende Ergebnisse werden nicht umgeschrieben.

Agent Authority bleibt gemäß der in den Ausgangsunterlagen festgehaltenen D-012
ein **eigenständiger Beobachter / Monitor / eine Analyseebene**. Es erlaubt oder
verbietet keine Aktionen, vergibt oder entzieht keine Rechte, erteilt keine
Freigaben, gibt keine Secrets oder Budgets frei und stoppt keine Aktionen.
Historische Gateergebnisse begründen keine dieser Produktbefugnisse.
Fremdtools sind weder Voraussetzung noch Ersatz für fehlende AA-Beobachtung.

## Belegbasis und Leseregeln

Die vier folgenden Dokumente wurden vollständig gelesen, einschließlich ihrer
Ergebnisse und Grenzen. Ihre Verweise auf ältere Tests und Forschungsbefunde
werden als dokumentierte, datierte Belege übernommen, nicht erneut ausgeführt
oder über ihren bisherigen Umfang hinaus bestätigt:

| Kürzel | Vorhandene Quelle | Belegart |
|---|---|---|
| IB | [Informationsgrenzen](OBSERVER-INFORMATION-BOUNDARIES-2026-10-07.md) einschließlich A1–A13, B1–B6, C1–C8 und Belegregister K1–K3, L1–L9, T1/F1/F2/X1–X3 | Zweckgebundene Forschungsableitungen und dokumentierte ältere Befunde. Kein universelles Pflichtfeldschema, Sammelrecht oder Integrationsbeweis. |
| E1 | [Vollständiger Feldbedarfsvergleich](OBSERVER-E1-FIELD-NECESSITY-2026-10-07.md), insbesondere [Ergebnis](OBSERVER-E1-FIELD-NECESSITY-2026-10-07.md#ergebnis--nach-dem-vorab-freeze-ergänzt) | Sechs konstruierte Papierkarten K1–K6; analytische Auswertung mit KI-Lektüre. |
| E2 | [Vollständiger Metadatenvergleich](OBSERVER-E2-METADATA-MINIMIZATION-2026-10-07.md), insbesondere [gemessene Ergebnisse](OBSERVER-E2-METADATA-MINIMIZATION-2026-10-07.md#gemessene-ergebnisse) | Zehn künstliche Eingaben an vorhandenen eigenen Labfunktionen; vorhandene Speicher-/Exportwege praktisch untersucht. |
| E3–E7 | [Vollständiger Bericht](OBSERVER-E3-E7-2026-10-07.md), insbesondere [Ergebnisse](OBSERVER-E3-E7-2026-10-07.md#ergebnisse) | 24 konstruierte Papierkarten K01–K24, zwei Vorlagephasen, 78 archivierte Antworten. E6 zusätzlich mit bereits dokumentierten praktischen Exp03-Befunden abgeglichen. |

K1–K6 in E1, C1–C5/S1–S5 in E2 und K01–K24 in E3–E7 sind unterschiedliche
Versuchskennungen. IB-C1–C8 bezeichnet dagegen die Ausschlussbereiche der
Ausgangsübersicht. Beziehungen werden ausschließlich innerhalb des jeweiligen
Belegs übernommen. Keine Karte ergänzt fehlende Bindungen einer anderen Karte.

**Belegstatus und Belegart bleiben getrennt:** Eine Aussage kann innerhalb eines
Papierfalls belegt sein und für reale Abläufe trotzdem offen bleiben. Ein
`SUPPORTED` für Informationsunterschiede ist kein Nachweis einer Produktfunktion.
Eine unzureichende Informationslage widerlegt nicht den unbekannten Vorgang.
Dokumentierte Widersprüche bleiben als solche erhalten; spätere, belegte
Korrekturen gelten nur für ihren benannten Gegenstand.

In Abschnitt A bezeichnet die Confidence-Spalte die folgenden dokumentierten Grenzen:

- **E1-Grenze:** H1–H3 analytisch innerhalb der gesetzten Karten `SUPPORTED`.
  E1 vergibt kein zusätzliches HIGH-/LOW-Label. Reale AA-Erkennungsleistung und
  menschliche Verständlichkeit sind `INCONCLUSIVE / nicht gemessen`.
- **E2-Grenze:** `HIGH` für die zehn festen künstlichen Eingaben und untersuchten
  Funktionen; `LOW` für Generalisierung. Keine echten Credentials, produktive
  Monitoraufnahme oder allgemeine Secret-Erkennung geprüft.
- **E3–E7-Grenze:** `HIGH` ausschließlich für die konstruierten Informationsvergleiche
  unter ihren ausdrücklich gesetzten Voraussetzungen; `LOW` für reale Agenten,
  Quellen, Empfänger, Uhren und Monitoring-/Schutzfunktionen. K14s Ressourcenfrage
  bleibt davon ausgenommen und `INCONCLUSIVE`. Reale AA-Erkennung und
  Verständlichkeit für Menschen sind nicht gemessen.
- **Historischer Beleg:** Der datierte Fake-Lab-/Reviewumfang bleibt erhalten.
  Diese Konsolidierung vergibt dafür keine neue Confidence und keinen Produktbeweis.

Quellenzuverlässigkeit, Identitätsbindungen, Quellordnung und Leseregeln sind in
den Papierfällen **Voraussetzungen**, keine dort empirisch bewiesenen Eigenschaften.
Gemeldeter Status, zugeordnete Vollzugsmeldung und unabhängig belegte tatsächliche
Wirkung dürfen deshalb auch nach einem erfolgreichen Vergleich nicht gleichgesetzt werden.

## A – Was nach E1–E7 belastbar belegt ist

| Nr. | Aussage | Konkreter Beleg / Experiment | Genaue Aussagegrenze | Confidence / Übertragungsgrenze |
|---|---|---|---|---|
| A.1 | Eine sichtbare Vor-/Nach-Meldungsordnung ersetzt keinen Bezug des Effekts auf den betrachteten Lauf. | E1 K1/K2, [Auswertung](OBSERVER-E1-FIELD-NECESSITY-2026-10-07.md#was-e1-konkret-zeigt): Effektmeldung nach bzw. vor Cleanup sichtbar, gesamte Effekt-Laufbindung entfernt. | Meldungsordnung bleibt in diesen Karten sichtbar; Effekt **des beendeten Laufs** nicht zuordenbar. Keine Aussage, dass ohne Bindung jede Chronologie verloren geht. | E1-Grenze. |
| A.2 | Ohne sichtbaren Effektbeleg tragen identische reduzierte Angaben keine unterschiedliche Effektaussage. | E1 K3/K4, gleiche sichtbare Karten nach Entfernung der Effektmeldung. | Effekt unbekannt, nicht als ausgeblieben bewiesen; kein verlässlicher Effekt-vor/nach-Ende-Vergleich. | E1-Grenze. |
| A.3 | Mit ausdrücklich gebundenem Effekt und gesetzter Ordnung ist der begrenzte Effekt-vor/nach-Cleanup-Vergleich ohne Arbeitsinhalte möglich. | E1 K5/K6, H1–H3. | K5 vor, K6 nach Cleanup des benannten Laufs. K5 schließt weitere spätere Effekte nicht aus. Cleanup ist kein bewiesener Remote-Stopp oder Widerruf. | E1-Grenze. |
| A.4 | Parameterausschluss verhindert die Speicherung sensitiver Marker in anderen Metadatenfeldern nicht. | E2 C1–C4/S1–S4: acht Fälle, Marker in beiden JSONL-Ereignissen je Fall; [Ergebnistabelle](OBSERVER-E2-METADATA-MINIMIZATION-2026-10-07.md#gemessene-ergebnisse). | Actor, Resource, URL im Resource und direkter Reason-Serializer geprüft; nicht beliebige Felder, Aktionen oder echte Secretwerte. Das ist eine nachgewiesene Lab-Metadaten-Lücke. | E2-Grenze. |
| A.5 | Die zwei Parameterkontrollen erscheinen im untersuchten `file.read`-Export, der untersuchten Provenienz und Zustandsprojektion nicht. | E2 C5/S5 mit inertem `parameters.e2_probe`. | Der Request hält die Marker weiterhin. Keine allgemeine Parameterbereinigung anderer Aktionen und keine Löschung aus dem gesamten Prozessspeicher nachgewiesen. | E2-Grenze. |
| A.6 | Eine unauffällige Zustandsprojektion beweist keine Bereinigung anderer Speicherstellen. | E2: Actor-Marker auch im Zustandsagenten/Provenienz; Resource-/URL-Marker trotz fehlender Resource in `public_view()` in Provenienz und JSONL. | Leere `touched_paths` bzw. fehlende Resource bei `file.read` sind Projektion, keine Redaktion. Reason-Fälle haben keinen Workflowzustand. | E2-Grenze. |
| A.7 | `PUBLIC` und gültige Hashverkettung sind mit Klartextmarkern im Export vereinbar. | E2: alle 20 Ereignisse PUBLIC, 20 gültige Eventhashes, zehn passende Zweierketten; acht Metadatenfälle behalten Marker. | Hashing ersetzt keinen Klartext und authentisiert keine Quelle. Kein Nachweis eines echten Credential-Leaks oder einer funktionierenden Klassifizierung. | E2-Grenze. |
| A.8 | Die Reasonfälle belegen Klartexterhalt am vorhandenen Serializer. | E2 C4/S4: direkte synthetische `Decision` an `emit_decision`, Marker in `reason_code` beider Ereignisse. | Kein `Lab.submit`-Entscheidungsweg für diese Gründe, keine tatsächlich auftretenden Produktionsfehler oder Stacktraces geprüft. | E2-Grenze. |
| A.9 | Anzeigenamen allein trennen Instanzen und Ressourcen nicht; explizite Bindungen ermöglichen die Zuordnung innerhalb des gesetzten Projekts ohne Klarnamen. | E3 K01 gegenüber K12/K13, [Bindung statt Namensgleichheit](OBSERVER-E3-E7-2026-10-07.md#e3--bindung-statt-namensgleichheit), H3.1. | K12/K13: zwei Instanzen, dieselbe Fake-Ressource. Eindeutigkeit/Stabilität gesetzt; kein realer Identitäts- oder Anonymitätsbeweis. | E3–E7-Grenze. |
| A.10 | Eine gültig gesetzte Actor-Wechselbindung klärt nur den Actor-Wechsel. | E3 K02/K14, H3.2. | K02 Actor offen; K14 gleiche Instanz gesetzt. K14 bindet **nicht** zusätzlich die Ressource über Epochen. | E3–E7-Grenze; K14-Ressource INCONCLUSIVE. |
| A.11 | Ablehnung, erfolgreicher Check und Empfang einer Cancel-Anfrage reichen nicht als Nutzungs-, Buchungs- oder Cancel-Vollzugsbeleg. | E4 K03/K04/K05, [Status/Vollzug](OBSERVER-E3-E7-2026-10-07.md#e4--status-ist-kein-vollständiger-wirkungsbeleg), H4.1. | `access.denied` beweist keine globale Nichtnutzung; Check keine Buchung; Anfrageempfang keinen Vollzug. Fehlender Vollzug bleibt offen. | E3–E7-Grenze. |
| A.12 | Die ergänzte, zugeordnete Quelle meldet einen bestimmten Vollzug bzw. eine bestimmte Nichtausführung. | E4 K15/K16/K17, H4.2. | Nur Nichtausführung dieses Zugriffsversuchs, diese Ledgerbuchung bzw. Cancel-Vollzug dieses Executors. Nicht Gesamtverbrauch/-abrechnung, tatsächliche Operationswirkung oder Freiheit von entfernten Nachwirkungen. | E3–E7-Grenze; zuverlässige Quellen gesetzt. |
| A.13 | Empfangsfolge allein liefert keine Quellordnung; ein identisches Duplikat ist in den Karten kein zweiter Effekt. | E5 K06/K07 gegenüber K18/K19, [Ordnung/Duplikat](OBSERVER-E3-E7-2026-10-07.md#e5--ordnung-duplikat-und-fehlende-meldung), H5.1/H5.2. | K06/K07 trotz Empfang Ende→Effekt→Start Reihenfolge offen. K07/K19: drei unterschiedliche Ereignisse, vier Lieferungen bei gleicher ID **und gleichem Inhalt**. Keine allgemeine Replayabwehr. | E3–E7-Grenze. |
| A.14 | Ohne Endmeldung bleibt Ende offen; mit Ordnung ohne Zeit bleibt die numerische Dauer offen. | E5 K08/K20, H5.3. | K08 meldet Start→Effekt, kein Ende; kein Beweis dauerhaften Nichtabschlusses. K20 meldet Effekt vor Ende, keine Zeitdifferenz. | E3–E7-Grenze. |
| A.15 | Zuverlässig gesetzte Quellordnung/-zeiten erlauben im selben Kartenlauf einen Vorhervergleich und eine Quellzeitdifferenz. | E5 K18/K19. | Effekt vor Ende, zehn Sekunden **konstruierte** Quellzeitdifferenz. Keine gemessene reale Dauer, globale Uhr oder existierende `source_order`-Exportfunktion. | E3–E7-Grenze. |
| A.16 | Gleicher Ausgabeinhalt bzw. gleiche sichtbare Meldungen erklären die Herkunft nicht. | E6 K09/K10, [Herkunft](OBSERVER-E3-E7-2026-10-07.md#e6--inhalt-abblenden-herkunft-sichtbar-halten), H6.1; bestehender Exp03-Gleichwerttest im Bericht. | Fehlende Herkunft ist unbekannt, nicht PUBLIC oder harmlos. Historische gleiche Payloads mit unterschiedlicher Herkunft bleiben praktischer Beleg im modellierten IFC-Lab. | E3–E7-Grenze; praktischer Anteil historisch. |
| A.17 | Quelllabel und übernommene Kontrollbeziehungen erklären den konstruierten Herkunftsunterschied ohne Rohpayload oder Gateausgabe. | E6 K21/K22, H6.2: o1→d1→v1→Lesen durch b; o1 SENSITIVE bzw. PUBLIC. | Label von **o1**, nicht gemeldeter eigener Labelwert von v1. Egress bleibt Absicht. Keine Inhaltsgefährlichkeit, tatsächliche Ausleitung oder allgemeine IFC bewiesen; Anfrage allein keine Übernahme. | E3–E7-Grenze. |
| A.18 | Abgeleitete Hinweise können selbst Informationen außerhalb der gesetzten Empfängersicht offenlegen. | E7 K23/K24, [Hinweissicht](OBSERVER-E3-E7-2026-10-07.md#e7--der-hinweis-selbst-gehört-zum-sichtumfang), H7.1/H7.2. | K23 enthält fremde Referenzen/Beziehungen; K24 trotz Namenmaskierung Projektanzahl, Querbeziehung und von Außeninformation abhängige Hinweisexistenz. Nur gesetzte A-/AB-Sicht untersucht. | E3–E7-Grenze; kein realer Filter-/Zustellungsfehler nachgewiesen. |
| A.19 | Im festgelegten Weltpaar unterscheidet der identische, lokal ausgelöste Hinweis die Außenbeziehung nicht; die globale Erklärung fehlt zugleich. | E7 K11, H7.3. | Gleiches Verhalten genau in diesen zwei Papierwelten. AB-Ausgabe nicht gezeigt; keine allgemeine Nichtinterferenz oder implementierte sichere Filterung. | E3–E7-Grenze. |
| A.20 | Der dokumentierte Phase-1-Export belegt nicht den Original-Anfrageeingang oder eine vollständige Wirkungsfolge. | IB L1 und [E3–E7: eigene bestehende Belege](OBSERVER-E3-E7-2026-10-07.md#eigene-bestehende-belege-und-offene-grenzen). | `authority.requested` entsteht nach gebildeter Decision; Sekunden-Wallclock/Hashkette keine globale Ordnung/Quellechtheit. Keine Phase-2-, Finish- oder externe Effektfolge belegt. | Historischer/codebezogener Beleg; Papierordnung behebt diese Lücke nicht. |
| A.21 | Positive historische Fake-Lab-Ergebnisse bleiben erhalten, ohne zu Beobachterbefugnissen oder allgemeiner Sicherheit zu werden. | IB L2–L6; E6-Abgleich mit Exp03-Gleichwert-/Kontrollpfad-/PUBLIC-Tests. | Modellierte kumulative Abläufe, Metadatenübergabe, Kontrollherkunft, lexikalische Fake-Pfade und spätere Binding-Korrektur innerhalb ihrer jeweiligen Specs. Keine realen Identitäten, vollständigen Sensoren oder allgemeine semantische Flusskontrolle. | Historischer Beleg; neue Papiervergleiche erweitern seinen Umfang nicht. |
| A.22 | Lifecycle-Cleanup und später FakeAdaptereffekt können im dokumentierten Labor gemeinsam auftreten. | IB L8; E1/E4 verweisen auf vorhandenes Finish-Fallblatt/Finding. | Früher Labablauf, keine neue Ausführung in dieser Konsolidierung. Keine nachträglich erfundenen AA-Ereignisbindungen/Zeitstempel; weder realer Fernstopp noch Freigabeverstoß belegt. | Historischer Beleg; OOS-021 bleibt offen. |

Damit sind konkrete Informationsverluste und eine konkrete eigene Metadaten-Lücke
belegt. **Nicht belegt ist dadurch ein vollständiger oder verlässlich arbeitender
Produktmonitor.** Die in den Berichten bereits dokumentierten grünen Tests sind
Konformitäts-/Regressionsbefunde in ihrem jeweiligen Labumfang; `PASS ≠ SUPPORTED`.

## B – Was ausdrücklich NICHT belegt ist

Jeder folgende Nicht-Beleg bleibt eigenständig. „Nicht belegt“ bedeutet keine
Behauptung, der Vorgang sei unmöglich oder nicht geschehen.

Die Statusspalte trennt einen **im konkreten Gegenbeispiel widerlegten Nachweis**
von **nicht ausreichender Information** und einer **nicht durchgeführten/offenen
Untersuchung**. Widerlegt ist jeweils nur der bezeichnete Schluss innerhalb des
Labors bzw. Papierfalls, nicht die unbekannte reale Wirkung. K14 bleibt gesondert
INCONCLUSIVE. Die Belegart und Übertragungsgrenzen aus der Belegbasis gelten weiter.

| Nr. | Nicht belegte Aussage | Status des Nicht-Belegs | Konkrete Grenze / Quelle |
|---|---|---|---|
| B.1 | Reale Erkennungsleistung eines AA-Monitors. | Offen / nicht gemessen | E1 und E3–E7: INCONCLUSIVE/nicht gemessen; KI-Kartenlektüre ist keine Laufzeitmessung. |
| B.2 | Verständlichkeit oder Nutzbarkeit für menschliche Empfänger. | Offen / nicht gemessen | E1/E3–E7: keine Menschenstudie. |
| B.3 | Gemessene Warnqualität bzw. False-Positive-/False-Negative-Raten eines Beobachters. | Offen / nicht gemessen | IB L7/L9; historische 0/28 Gate-FP und RC-/CB-Befunde sind keine AA-Warnquote. |
| B.3a | Brauchbare Warnschwellenwerte eines Beobachters. | Offen / nicht gemessen | E1/E3–E7 messen keine reale Warnleistung; IB L9. |
| B.4 | Vollständige produktive Aufnahme aus dem E2-Export. | Offen / nicht untersucht | [E2: weiter offen](OBSERVER-E2-METADATA-MINIMIZATION-2026-10-07.md#weiter-offen--ausdrücklich-nicht-mit-ersatzdatenwegen-ausgefüllt): NICHT GETESTET / verbundener Pfad nicht belegt. |
| B.4a | Produktive Nutzeranzeige aus dem E2-Export. | Offen / nicht untersucht | E2: Anzeige ausdrücklich nicht getestet. |
| B.4b | Produktive Warnung aus dem E2-Export. | Offen / nicht untersucht | E2: Warnung ausdrücklich nicht getestet. |
| B.5 | Allgemeine Secret-Erkennung. | Nicht untersucht | E2: zehn feste Eingaben, kein Secret-Detektorvergleich. |
| B.5a | Allgemeine Metadatenbereinigung. | Als nicht ausreichend gezeigt (Lab) | E2: acht Metadatenfälle behalten Marker. |
| B.6 | Offenlegung echter, einlösbarer Zugangsdaten im E2-Versuch. | Nicht untersucht | Nur neutrale Marker und secretähnliche Dummys; keine echten Credentials gelesen. |
| B.7 | Allgemeiner Parameterausschluss bei allen Aktionen. | Offen; Kontrolle nur file.read | E2 C5/S5 nur `file.read`. |
| B.7a | Löschung der Marker aus dem gesamten Prozessspeicher. | Nicht gezeigt; Marker im Request erhalten | E2: Request hält Parameter weiterhin. |
| B.8 | Typischer Produktionsfehlertext oder Labentscheidung als Ursache der gemessenen Reason-Markerweitergabe. | Nicht untersucht | E2 C4/S4 direkte synthetische Serializerfixture, kein entsprechender `Lab.submit`-Pfad. |
| B.9 | Geheimnisfreiheit durch `PUBLIC`. | Als Bereinigungsbeleg widerlegt (Labmarker) | E2: PUBLIC-Ereignisse behalten Klartextmarker. |
| B.9a | Geheimnisfreiheit durch Hashes. | Als Bereinigungsbeleg widerlegt (Labmarker) | E2: gültige Hashes ersetzen die Klartextwerte nicht. |
| B.9b | Geheimnisfreiheit durch Top-Level-Schlüsselnamenprüfungen. | Als Nachweis nicht ausreichend (E2) | E2: alte Exportassertions prüfen keine vollständigen Stringwerte. |
| B.10 | Reale Quellenauthentizität durch Quellenlabel oder Hashkette. | Als Nachweis nicht ausreichend (IB/E5) | IB B4/Widersprüche; E3–E7 setzen Quellenzuverlässigkeit. |
| B.10a | Wahrheit einer Meldung durch authentisierte Herkunft allein. | Als Nachweis nicht ausreichend (IB) | IB B4/Widersprüche: auch Hash/Signatur/Herkunft sind kein Wahrheitsbeweis. |
| B.11 | Reale Agentidentität oder Gleichheit über Projekte/Referenzepochen ohne belegte Bindung. | Bindungsnachweis nicht ausreichend (Papier); real offen | E3 K01/K02; Projektbindung in K12/K13 bzw. Actor-Brücke in K14 nur gesetzt. |
| B.12 | Ressourcenstabilität über Epochen in K14. | INCONCLUSIVE (Papier) | E3 ausdrücklich INCONCLUSIVE; gleich geschriebene Referenz reicht dort nicht. |
| B.13 | Reale Symlink-, Mount-, URL- oder Hostidentität durch Fake-Pfadkanonisierung. | Offen; nur Fake-Identität geprüft | IB L6; E3 historische Fake-Adaptergrenze. |
| B.14 | Anonymität durch entfernte Klarnamen. | Nicht untersucht | E3: manuell gesetzte Projektbezüge, keine Anonymitätsprüfung. |
| B.14a | Unverknüpfbarkeit der Projektpseudonyme. | Nicht untersucht | E3: Verknüpfbarkeit bleibt möglich, nicht geprüft. |
| B.14b | Eine experimentell bewiesene Pseudonymisierungstechnik. | Nicht geprüft; in E3 kein Algorithmus implementiert | E3 setzt Bindungen manuell. |
| B.14c | Die Existenz eines geeigneten Pseudonymisierungsdienstes. | Nicht untersucht | E3 implementiert keinen Dienst und belegt keinen produktiven Pseudonymisierungspfad. |
| B.15 | Ein global verpflichtender Aufbau von IDs, Feldern oder Events. | Nicht abgeleitet; Feldminimalität nicht isoliert untersucht | E1 entfernt eine Informationsgruppe; E3/E4/E5 setzen konkrete Bindungen, keine universelle Feldminimalität. |
| B.16 | Globale Nichtnutzung nach einer Ablehnung. | Als Nachweis nicht ausreichend (Papier) | E4 K03 fehlt Nutzungsbeleg; K15 meldet nur Nichtausführung dieses Versuchs. |
| B.17 | Tatsächliche Nutzung nach erfolgreichem Budgetcheck. | Als Nachweis nicht ausreichend (Papier) | E4 K04; auch K16 meldet keine tatsächliche Operationswirkung. |
| B.17a | Buchung allein durch erfolgreichen Budgetcheck. | Als Nachweis nicht ausreichend (Papier) | E4 K04; K16 enthält dafür erst eine zusätzliche Ledgerquelle. |
| B.17b | Gesamtabrechnung durch eine einzelne Buchungsmeldung. | Als Nachweis nicht ausreichend (Papier) | E4 K16 meldet nur eine gebundene Ledgerbuchung. |
| B.18 | Physischer Fernstopp durch Cancel-Anfrage oder Cancel-Vollzugsmeldung. | Als Nachweis nicht ausreichend (Papier) | E4 K05/K17; IB L8 / OOS-021. |
| B.18a | Abwesenheit aller Nachwirkungen nach gemeldetem Cancel-Vollzug. | Als Nachweis nicht ausreichend (Papier) | E4 K17; IB L8 / OOS-021. |
| B.19 | Executor-Stopp, Tokenwiderruf oder Unmöglichkeit späterer Effekte durch Cleanup/`finish()`. | Als Nachweis nicht ausreichend (Papier/historisches Lab) | E1 und historisches Finish-Finding; Registrygrenze ist keine externe Wirkungsgrenze. |
| B.20 | Das Ausbleiben eines Effekts, Zugriffs oder Endes aus einer fehlenden Meldung. | Als Nachweis nicht ausreichend (Papier) | E1 K3/K4, E4 K03–K05, E5 K08. Fehlende Information ist kein negativer Beweis. |
| B.21 | Globale Ereignisordnung aus Empfangsfolge, Sekundenzeitstempeln oder Hashketten. | Als Nachweis nicht ausreichend (Papier/IB) | E5 K06/K07; bestehender G3-Export. |
| B.21a | Echte verteilte Uhrqualität. | Nicht untersucht | E5: zuverlässige Quellzeiten nur konstruiert gesetzt. |
| B.22 | Eine reale Zehnsekundenmessung. | Nur Papier; reale Messung nicht durchgeführt | E5 K18/K19 verwenden konstruierte Quellzeiten. |
| B.22a | Eine numerische Dauer ohne Quellzeit. | Als Nachweis nicht ausreichend (Papier) | E5 K20 erlaubt ohne Zeit nur Reihenfolge. |
| B.23 | Umgang mit veränderten Duplikaten. | Nicht untersucht | E5 prüft ausschließlich gleiche ID und identischen Inhalt. |
| B.23a | Abwehr bösartiger Replays. | Nicht untersucht | E5: keine Replayabwehr geprüft. |
| B.23b | Vollständigkeit der Lieferungen. | Offen / keine Vollständigkeitsgarantie | E5: keine Karte garantiert alle Meldungen. |
| B.24 | Eigener Labelwert von v1. | Offen (Papier) | E6 K21/K22 melden nur o1-Label. |
| B.24a | PUBLIC-Herkunft bei fehlender Lineage. | Als Nachweis nicht ausreichend (Papier) | E6 K09/K10 lassen Herkunft unbekannt. |
| B.25 | Übernommene Kontrollabhängigkeit allein durch eine Anfrage. | Als Nachweis nicht ausreichend (historischer Befund) | E6 / späterer Binding-Atomicity-Befund; Anfrage und Übernahme sind verschieden. |
| B.26 | Tatsächlicher Egress oder Leak durch eine Egressabsicht. | Als Nachweis nicht ausreichend (Papier) | E6 alle Karten: nur Absichtsmeldung. |
| B.27 | Vollständige allgemeine IFC. | Offen; nur modellierter Bereich geprüft | IB L4/L9; E6 nur modellierte Kontrollbeziehungen. |
| B.27a | Sichtbarkeit eines unmodellierten `if`. | Dokumentierte Blindstelle (Lab) | IB L4/L9; E6: roher Zweig außerhalb der modellierten Kontroll-API unsichtbar. |
| B.27b | Vollständige Beobachtung aller Nebenkanäle. | Offen / dokumentierte Blindstellen | IB L9; E6 keine allgemeine Flussabdeckung. |
| B.28 | Semantische DLP bzw. Erkennung gefährlicher Inhalte aus Herkunftsmetadaten. | Nicht untersucht | IB C2–C4/L9; E6 Herkunft ist kein Inhaltsbeweis. |
| B.28a | Ein Beweis von Absicht aus den beobachteten Metadaten. | Nicht untersucht | IB C2–C4/L9; E1–E7 prüfen keine Intent-Erkennung. |
| B.28b | Allgemeine Injection-Erkennung ohne Rohinhalt. | Nicht untersucht | IB C2–C4/L9; E6 kein semantischer Injection-Versuch. |
| B.29 | Korrekte Anfangslabels. | Offen / vorausgesetzt | IB L9; E6 setzt die Quellenlabels. |
| B.29a | Verlässliche Beobachtung bei kompromittierten Runtimes/Quellen. | Nicht untersucht | IB L9; E3–E7 setzen zuverlässige Quellen, keine adversariale Laufzeitprüfung. |
| B.30 | Sichere technische Empfängerfilterung. | Nicht untersucht | E7 K11 lediglich gesetztes Weltpaar; K23/K24 konstruierte Offenlegungen. |
| B.30a | Sichere Zustellung. | Nicht untersucht | E7: keine reale Übermittlung geprüft. |
| B.30b | Allgemeine Nichtinterferenz. | Offen; nur Weltpaar geprüft | E7 K11 untersucht ausschließlich zwei gesetzte Welten. |
| B.31 | Sichere Hinweise allein durch Namenmaskierung oder Entfernung direkter Referenzen. | Widerlegt im konstruierten Gegenbeispiel | E7 K24 zeigt verbleibende Anzahl, Beziehung und weltabhängige Hinweisexistenz. |
| B.32 | Reale Leserrechte. | Offen / nur fiktive Regel | IB Leseregeln/C-Bereich; E7 nur fiktive A-/AB-Regel. Analysebedarf schafft keine Berechtigung. |
| B.32a | Rechtsgrundlage der realen Datenverarbeitung. | Offen | IB Leseregeln/C-Bereich; durch E1–E7 nicht geklärt. |
| B.32b | Einwilligung zur realen Datenverarbeitung. | Nicht untersucht | IB Leseregeln/C-Bereich; keine reale Einwilligung untersucht. |
| B.32c | Geeignete Aufbewahrung. | Offen | IB C-Bereich; E7 reale Aufbewahrung unbekannt. |
| B.32d | Geeignete Löschung. | Offen | IB C-Bereich; E7 reale Löschung unbekannt. |
| B.33 | Vollständige aktuelle Ereignisverträge oder funktionierende Verbindungen zu Fremdtools. | Offen / keine reale Integration untersucht | IB T1/F1/F2/X1–X3 datierte Quellenstände; E1–E7 untersuchen keine reale Integration. |
| B.34 | Vollständige Beobachtungsabdeckung oder zuverlässige Verlust-/Ausfallmeldung. | Nicht ausreichend; dokumentierte Lücken | IB A12/L1: stille Emissionsfehler, fehlende Ereignisarten; fehlende Meldung kein Ausfallbeweis. |
| B.35 | Allgemein hinreichende Ressourcenmetadaten für jede Ressourcenfrage. | Offen; nur begrenzte Belege | IB A7/L6/L7; E3 reale Identität und K14 offen. |
| B.35a | Allgemein hinreichende Revisionsmetadaten für jede Änderungsfrage. | Offen; Granularität nicht bestimmt | IB A7/L7; konkrete Granularität nicht durch E1–E7 bestimmt. |
| B.35b | Allgemein hinreichende Rollenmetadaten für jede Rollenfrage. | Offen; Minimum nicht bestimmt | IB A10 nur zweckgebundener Bedarf; E1–E7 bestimmen kein Minimum. |
| B.35c | Allgemein hinreichende Kostenmetadaten. | Offen; nur begrenzter Statusvergleich | IB A8/F2; E4 untersucht nur Check/Buchungsmeldung, keine vollständige Kostenbeobachtung. |
| B.35d | Allgemein hinreichende Zugangsmetadaten. | Offen; historische Lücken erhalten | IB A9/F1/L7; historische Token-Reuse-/Bindungsgrenzen nicht durch E4 geschlossen. |
| B.36 | Beobachter-Produktkonformität durch bestandene historische Gate-/Regressionsprüfungen. | Als Nachweis nicht ausreichend (Lab) | E2/E3–E7 dokumentieren Labregression, keine neue Beobachterimplementierung; PASS ≠ SUPPORTED. |
| B.37 | Externe unabhängige Prüfung. | In diesem Forschungsblock nicht durchgeführt | Getrennte KI-Lektüren/Reviews im selben Projektkontext; keine externe Audit- oder Produktstudie. |
| B.37a | Allgemeiner Sicherheitsbeweis. | Nicht belegt; begrenzte Modelle | IB L9/E1–E7: begrenzte Modelle und LOW-Generalisation, keine allgemeine Produktsicherheit. |

## C – Widersprüche und offene Fragen

Die folgenden Konflikte und Lücken werden erhalten. „Später korrigiert“ bezeichnet
nur eine bereits dokumentierte Korrektur; hier wird nichts repariert.

| Punkt | Letzter belegter Stand und bestehende Grenze | Quelle / Status |
|---|---|---|
| Historische Gate-Specs gegenüber heutiger Rolle | Alte Freigabe-/Sperrmechanismen bleiben historische Experimente. D-012 legt den eigenständigen Beobachter fest; aus Lab-PASS folgen keine Befugnisse. | IB Widerspruch 1, K1; Rollenabgrenzung, keine experimentelle Produktentscheidung. |
| Parameterausschluss gegenüber Geheimnisfreiheit | Früherer Parameterausschluss bleibt bestehen. E2 zeigt zusätzlich Klartext über Actor/Resource/URL/Reason; `PUBLIC` ist dort keine bestätigte Sensitivitätsbewertung. | IB Widerspruch 2, E2 H1–H4; nachgewiesene Metadaten-Lücke, ungelöst. |
| `public_view()`-Beschreibung gegenüber Stringwerten | Die Beschreibung „No ... secrets“ ist als allgemeine Bereinigungsaussage nicht gedeckt; Actor-Dummy bleibt in der Projektion. Resource-Auslassung schützt andere Speicherorte nicht. | E2 Belege/bisheriger Stand; Dummybefund, kein Versuch mit echten Secrets. |
| Alter Abschaltflagbefund gegenüber korrigiertem Labstand | Der alte Befund für `LAB_AUTHORITY_EVENTS=0` unter pytest wurde durch PR #18 im benannten Labstand korrigiert. Nicht korrigiert sind damit Metadaten, andere Producer oder Beobachterpfade. | IB Widerspruch 3; datierte Teilkorrektur, nicht als aktuelle Flaglücke wiederholen. |
| Graphkanten/Quelllabel/Hash gegenüber Nutzung | Dokumentierte falsche Nutzungs-/Kostenkanten und mögliche Quell-/Typkombinationen tragen keinen Nutzungs-, Buchungs- oder Wahrheitsbeweis. | IB Widerspruch 4, E4; keine aktuelle Graphreparatur oder reale Quellechtheit geprüft. |
| Registryreparatur gegenüber spätem Effekt | Reparierte Registrygrenzen und dokumentierter später FakeAdaptereffekt betreffen verschiedene Grenzen. `finish()` ist kein externer Stop-/Widerrufsnachweis. | IB Widerspruch 5/L8, E1/E4; OOS-021 offen, vollständige AA-Replayfolge fehlt. |
| Früher Binding-PASS gegenüber späterem Atomicity-Befund | Früher Review übersah einen trotz DENY geschriebenen `self.decisions`-Kontrollrecord. Späterer Review dokumentiert die Korrektur: `decisions` unverändert nach verweigertem `control_decide`; nachfolgendes `state_write` ebenfalls DENY ohne State-/Effektänderung. Transfer-Provenienzcheckpoint bleibt erhalten. | IB Widerspruch 6/L5; E6 übernimmt den späteren begrenzten Befund, löscht den frühen nicht. |
| Snapshotbeschreibung gegenüber Record-Sharing | Dokumentation beschreibt Kopien/neue Records; Codebefund nennt geteilte unveränderliche Provenienzrecords. Unterschied erhalten; daraus kein nachgewiesener Mutationsangriff. | IB Widerspruch 7/L2. |
| K14-Ressourcenfrage | Actor-Brücke ist gesetzt, Ressourcenstabilität über Epochen nicht. K02 enthält eine zusätzliche Ressourcenannahme, K14 nicht; Vergleich für Ressourcenfrage nicht vollständig isoliert. | E3 K02/K14: ausdrücklich INCONCLUSIVE. Keine Ergänzung aus K02 oder anderen Karten. |
| E2 nach dem Export | Produktiver Monitorinput, Anzeige und Warnung unbekannt / nicht verbunden belegt. JSONL mit Standardparser lesbar ist kein Beleg dieses Pfads. | E2 weiter offen; NICHT GETESTET. |
| Zuordnung und Quellechtheit | Reale Instanz-, Ressourcen- und Wechselbindungen; Gültigkeit/Scope; kompromittierte oder widersprüchliche Quellen nicht empirisch geklärt. | E3/E4/E6, IB L6/L9; LOW-Generalisation. |
| Ordnung, Zeit und Abdeckung | Quellordnung der Karten nicht als G3-Funktion vorhanden belegt. Reale Uhren, Verlust, Lieferverhalten, geänderte Duplikate/Replays und Vergleich über Quellen unbekannt. `requested`-Zeit ist nicht Originaleingang. | E5; IB A5/A12/L1. |
| Herkunft und Wirkung | Eigener v1-Labelwert, tatsächliche Egresswirkung, vollständige Herkunft und unmodelliertes `if` bleiben offen. Herkunftsanfrage darf Übernahme nicht ersetzen. | E6, IB L4/L5/L9. |
| Reale Empfängergrenzen | Rechtsgrundlage, Leserrechte, technische Trennung, Übermittlung, Aufbewahrung/Löschung und andere Seitenkanäle unbekannt. K11 klärt nur sein Weltpaar. | E7, IB C7/B6; keine implementierte Schutzgarantie. |
| Kosten-/Zugangsaussagen | Reale Chargestufen, Verbraucherbindung, Summen/Einheiten, bereitgestellter Zugang versus Nutzung/Entzug sowie TTL/Bindung nicht durch E4 integriert oder global validiert. | IB A8/A9, F1/F2; E4 meldet nur gesetzte Status-/Vollzugsquellen. |
| Rollen, Delegation und Hinweisbearbeitung | Notwendige Rollen-/Revisionsgranularität, reale Delegationsbezüge, Nutzen und Leserzugriff von Hinweisstatus/Zuständigkeit nicht durch E1–E7 geprüft. | IB A4/A10/B6; zweckgebundene Ableitung, keine globale Teamhierarchie. |
| Historische gemessene Misses | RC-01–05 und CB-01-Token-Reuse-Miss bleiben bestehen. Standardsuite schließt RC-01–05 aus; grüner Lauf hebt sie nicht auf. | IB L7/L9; E2/E3–E7 Abschlussbefunde. Keine Übertragung auf eine AA-Warnquote. |
| Reale Leistung und Nutzerverständnis | Kein Produktmonitor oder Menschenversuch bewertet; Codekonformität einer neuen Beobachterfunktion nicht untersucht. | E1 und E3–E7: INCONCLUSIVE / nicht gemessen. |
| Datierter Vorschlagsstand der Ausgangsübersicht | IB endet mit „Experimente ... nicht begonnen / nächster Schritt E1“. Das ist ihr damaliger Ausgangsstand; spätere E1–E7-Ergebnisse liegen jetzt vor. Datei nicht rückwirkend umschreiben oder daraus einen neuen Experimentauftrag ableiten. | IB Schlussabschnitt gegenüber E1/E2/E3–E7 Abschluss; chronologische Einordnung, keine stillschweigende Änderung. |

Nicht jede unterschiedliche Perspektive ist ein Widerspruch: etwa Anfrageempfang
und späterer Vollzug oder Cleanup und externer Effekt können miteinander vereinbar
sein. Ein Widerspruch darf nur benannt werden, wenn Belege tatsächlich denselben
Gegenstand/Scope betreffen und unvereinbare Aussagen tragen; solche Vergleichbarkeit
ist nicht durch Namen, Zeitnähe oder angenommene Beziehungen herzustellen.

## D – Minimaler Informationsbedarf von Agent Authority

Die folgenden Kategorien gelten **für die jeweils benannte Beobachtungsfrage**:

- **Zwingend belegt:** Der Vergleich zeigt, dass die betreffende Aussage ohne
  diese Informationsart nicht getragen wird. Das gilt im dokumentierten
  Vergleichsumfang, nicht als universelle Sammlungspflicht.
- **Nur bedingt erforderlich:** Für eine bestimmte Frage gestützt oder in IB
  zweckgebunden dokumentiert; nicht als allgemeines Minimum experimentell bewiesen.
- **Weiterhin ungeklärt:** Notwendigkeit, Granularität oder reale Bereitstellbarkeit
  nicht ausreichend untersucht. Daraus wird kein Pflichtfeld abgeleitet.

Informationsarten sind keine neuen Events oder Felddefinitionen. Eine belegte
Bindung kann anders dargestellt werden als in einer Karte. Insbesondere beweist
E1 nicht zwei getrennte Pflichtfelder „Versuch plus Generation“, E4 kein zusätzliches
`attempt` bei der Buchung und E5 kein zwingendes Produktfeld `source_order`.

| Informationsart / benannte Frage | Einordnung | Konkrete Stütze | Grenze des minimalen Bedarfs |
|---|---|---|---|
| Bezug eines Effekts auf den betrachteten Lauf/Vorgang | **Zwingend belegt** für die Aussage über den Effekt dieses Laufs. | E1 K1/K2 gegenüber K5/K6; IB A2. | Ein eindeutig belegter Bezug ist erforderlich, nicht ein bestimmter ID-Aufbau. Workflowname, Nähe oder Instanzname allein ersetzen ihn nicht. Reale Bindung ungeprüft. |
| Sichtbarer Effektbeleg bzw. ausdrücklich zugeordnete Ziel-/Vollzugsmeldung | **Zwingend belegt** für die jeweilige positive Effekt-/Vollzugsaussage. | E1 K3/K4; E4 K03–K05 gegenüber K15–K17; IB A6. | Quellenmeldungen tragen nur ihren Scope. Keine Meldung heißt unbekannt; tatsächliche Wirkung braucht entsprechende Wirkungsbelege, nicht nur einen Statusnamen. |
| Vergleichbare Ordnung der betrachteten Meldungen/Vorgänge | **Zwingend belegt** für den untersuchten Vor-/Nach-Vergleich. | E1 gesetzte Ordnung; E5 K06/K07 gegenüber K18–K20; IB A5. | Empfangsfolge reicht nicht. Belegte Ordnung ist nicht mit einer globalen Uhr oder einem bestimmten Sequenzfeld gleichzusetzen. |
| Ausdrückliche Instanz- und Ressourcenbindung im relevanten Scope | **Zwingend belegt** für die untersuchte Gleich-/Verschieden-Zuordnung. | E3 K01 gegenüber K12/K13; IB A3/A7. | Projektbezogene Bindungen genügen in diesen Karten ohne Klarnamen. Realer Identity-Dienst und reale Ressourcenauflösung nicht bewiesen. |
| Belegter Bezug über einen Referenzwechsel | **Nur bedingt erforderlich**: wenn Aussagen über beide Referenzstände getroffen werden sollen. | E3 K02/K14; IB A2/A3. | Actor-Wechselbindung klärt nur Actor. Erforderlicher Ressourcenbezug über Epochen weiterhin ungeklärt; K14 darf ihn nicht liefern. |
| Unterscheidbarer Aussagegegenstand, Meldungsstufe und passende Quellenperspektive | **Zwingend belegt** als Informationsunterschied für die untersuchten Status-/Vollzugsaussagen. | E4 H4.1/H4.2; IB A1/A6/A8/A9. | Anfrage, Check, Vollzug und Wirkung sind verschieden. Keine isolierte Notwendigkeit eines bestimmten `source`-/Typfelds oder einer bestimmten Quelle empirisch bewiesen. Quellechtheit bleibt offen. |
| Quellzeiten mit bekannter Bedeutung und Vergleichbarkeit | **Nur bedingt erforderlich** für numerische Zeitdifferenzen. | E5 K18/K19 gegenüber K20; IB A5. | Für Reihenfolge kann Ordnung ohne Zeit genügen. Papierzeiten keine reale Uhrenmessung; Empfangszeit und Original-Anfragezeit nicht austauschbar. |
| Wiedererkennbarer Ereignisbezug und identischer Inhalt | **Nur bedingt erforderlich** für die hier untersuchte Duplikatzuordnung. | E5 K07/K19; IB A1. | Hier gleiche ID plus gleicher Inhalt; keine Pflicht zu Hash/UUID oder belegte allgemeine Replaystrategie. Andersartige Wiederholungen ungeprüft. |
| Herkunftslabel der Quelle sowie belegte übernommene Daten-/Kontrollbeziehungen und Wertbezug | **Zwingend belegt** für den begrenzten Herkunftsvergleich bei gleicher Ausgabe. | E6 K09/K10 gegenüber K21/K22; historische Exp03-Befunde; IB A11. | Nur für modellierte Herkunftsfragen. Kein eigenes v1-Label erfinden, Anfrage nicht Übernahme nennen. Reale Verfügbarkeit/Vollständigkeit weiterhin ungeklärt. |
| Zulässiger Empfängersichtumfang, wenn ein Befund adressiert/ausgegeben wird | **Nur bedingt erforderlich** für die Bewertung der Hinweissicht. | E7 setzt A/AB-Regel; IB C7/A13/B6. | E7 zeigt Konsequenzen einer gegebenen Regel, keine Erteilung oder Ermittlung realer Rechte durch AA. Inhalt und Hinweisexistenz können Außenbezüge tragen. |
| Umfang und Grenzen der vorhandenen Beobachtung, bekannte Filter/Verluste bzw. unbekannte Abdeckung | **Nur bedingt erforderlich**, um Aussagen über Sichtlücken korrekt zu begrenzen. | E1 K3/K4, E5 K08; IB A12/L1. | Fehlende Meldung ist kein negativer Beweis. Notwendige technische Coverage-Metadaten oder Verlustsensoren nicht experimentell festgelegt; keine neuen Heartbeat-/Zählerfelder. |
| Belegreferenzen, Frage, Scope, Unsicherheit und dokumentierter Korrekturbezug der eigenen Analyse | **Nur bedingt erforderlich**, dokumentarisch gestützt für nachvollziehbare Aussagen. | IB A13/L9; E1–E7 trennen ihre Quellen, Annahmen und Grenzen. | Keine Prüfung eines implementierten Analyseformats. Globale Pflicht für Regelversion/Zeitstempel oder vollständige interne Herleitung nicht durch Ablation bewiesen. Rohdaten nicht in Hinweise kopieren. |
| Kosten-/Zugangsmetadaten mit Stufe, Vorgangsbezug, Scope/Gültigkeit sowie gegebenenfalls Einheit/Zeitraum | **Nur bedingt erforderlich** für entsprechende Kosten-/Zugangsfragen. | IB A8/A9, F1/F2; E4 Check gegenüber Buchung bzw. Ablehnung gegenüber Zielmeldung. | Keine Secretwerte. E4 bestimmt keine allgemein minimalen Beträge, Zähler, TTL- oder Verbraucherfelder; deren konkrete Notwendigkeit bleibt ungeklärt. |
| Ressourcen-/Konfigurationsrevision, Aktion/Tool-/Zielklasse | **Nur bedingt erforderlich**, soweit die konkrete Ressourcen-/Änderungsfrage das benötigt. | IB A7/L6/L7; historische RC-01–05-Lücken. | Keine allgemeine hinreichende Semantik aus Namen/Verben. Revisionsgranularität und reales Ressourcenbinding nicht durch E1–E7 isoliert untersucht. |
| Delegations-/Beziehungstyp und Herkunft; Rollen-/Änderungsstatus mit fachlichem Scope/Gültigkeit | **Weiterhin ungeklärt** als experimentell bestimmtes Minimum; IB begründet zweckgebundenen Bedarf. | IB A4/A10, L2/L3, T1/F1/F2. | Keine globale Teamhierarchie, vollständige Rechteinventare oder Gleichsetzung von Span-Elternschaft mit Delegation. E1–E7 prüfen diese Granularität nicht. |
| Konkrete reale Quelle, Authentisierung, Synchronisation und Liefer-/Exportvertrag für diese Informationsarten | **Weiterhin ungeklärt**. | E3–E7 LOW-Generalisation; IB L1/T1/F1/F2/X1–X3. | Papierfelder sind keine vorhandenen Sensoren. Datierte Fremdtoolbefunde nicht zu neuen Pflichtabhängigkeiten machen. |

Die optionalen IB-B1–B6 werden nicht durch E1–E7 zu Pflichtangaben: bereinigter
Titel/Auftragstyp, zusätzliche Versions-/Retry-/Proxyangaben, feinere Dauer-/Token-/
Kostenverläufe, zusätzliche Belegpfade, Fehlerkategorien und minimierter
Hinweisbearbeitungsstatus/Zuständigkeit bleiben zweckgebunden optional.
„Bestätigt“, „erklärt“ oder „geschlossen“ beim Hinweis ist keine Aktionsfreigabe.
Ein optionales Datum kann für eine später ausdrücklich benannte Frage relevant
werden; E1–E7 belegen daraus keine allgemeine neue Sammlungspflicht.

## E – Informationen, die Authority nicht sehen soll

Der Ausschlussstand von [IB-C1–C8](OBSERVER-INFORMATION-BOUNDARIES-2026-10-07.md#c--sollte-agent-authority-nicht-erhalten)
bleibt erhalten. **Kein Experiment belegt einen Widerspruch, der eine Lockerung
dieser Ausschlüsse erforderlich macht.** E2 widerspricht der Behauptung einer
bereits geheimnisfreien Verarbeitung, nicht dem Ausschlussziel. E1/E3/E6 zeigen
Rohdatenverzicht nur für ihre begrenzten Fragen, keine vollständige Sicherheit
aller Beobachtungsaufgaben. Die Tabelle enthält keine neue Datenerlaubnis.

| Ausschlussbereich | Abgleich mit E1–E7 | Beleggrenze / offene Frage |
|---|---|---|
| **IB-C1: Secretwerte und einlösbares Authmaterial** — Passwörter, API-/Providerkeys, Access-/Refresh-/Pairing-/Approvaltokens, Cookies, private Schlüssel, Vaultinhalt, einlösbare Capabilities; auch Authmaterial des Beobachtungswegs nicht im Befund. | Ausschluss erhalten. E2 zeigt, dass secretähnliche Dummys über Metadaten erhalten bleiben; `PUBLIC`/Hash bereinigen nicht. Status oder belegte nicht einlösbare Referenz kann für eine bestimmte Frage genügen. | Kein tatsächlicher Secretzugriff getestet. Ob eine konkrete Referenz wirklich nicht einlösbar ist, muss belegt sein; Hashen erratbarer Secretwerte ist kein nachgewiesener Schutz. |
| **IB-C2: Vollständige Prompts, Systeminstruktionen, Antworten, Chats und Terminalverläufe** | Ausschluss erhalten. E1s Ablaufvergleich und E6s Herkunftsvergleich benötigen ihre Rohinhalte nicht. | Nicht auf alle Fragen verallgemeinern. Ohne Inhalt keine behauptete semantische DLP, Absichts- oder allgemeine Injection-Erkennung. |
| **IB-C3: Rohe Toolargumente/-resultate, vollständige Befehle, HTTP-Bodies und MCP-Payloads** | Ausschluss erhalten. E2s zwei Parameterkontrollen fehlen im untersuchten Export; andere Metadatenträger bleiben riskant. E4 braucht im Modell nur gebundene Status-/Vollzugsaussagen. | Parameterausschluss bei `file.read` beweist weder allgemeine Redaktion noch genügende Beobachtung aller realen Wirkungen. |
| **IB-C4: Datei-/Dokumentinhalte, Notizen, Bilder/Screenshots, Browserseiten, vollständige Workspace-/Memory-/Jobsnapshots** | Ausschluss erhalten. E1/E6 unterscheiden ihre begrenzten Vorgänge/Herkünfte ohne solche Inhalte. | Kein Beweis für alle Monitorfragen; kein zweiter Inhalts-/Wissensspeicher aus dem Forschungsblock abgeleitet. |
| **IB-C5: Unminimierte Pfade, URLs mit Query/Userinfo, Beschreibungen, freie Fehlertexte und Labels mit Rohwerten** | Ausschluss erhalten. E2 belegt Klartext über Resource/URL/Actor/Reason; eine kleine Zustandsprojektion schützt Provenienz/erste persistierte Exportdatei nicht. | Erste untersuchte persistente Stelle ist der JSONL-Export, nicht nachgewiesener erster Speicher im gesamten System. Reale geeignete Minimierung nicht untersucht oder repariert. |
| **IB-C6: Klarnamen/Kontaktdaten, pauschale Personen-/Geräteprofile, Arbeitszeit-/Leistungs-/Schuld-/Machtscores** | Ausschluss erhalten. E3 zeigt hinreichende Zuordnung ohne Klarnamen innerhalb gesetzter Projektbindungen. | Keine Anonymitätsgarantie. Aktivität oder Graphgrad ist kein Fehlverhaltensbeweis; nötige Personenbindung darf nicht global vorausgesetzt werden. |
| **IB-C7: Vollständige Rollen-/Rechte-/Vault-/Budget-/Abrechnungsbestände und fremde Projektinformationen außerhalb der zulässigen Sicht** | Ausschluss erhalten. E7 bestätigt im Papiermodell, dass auch abgeleitete Texte, Anzahl/Querbeziehung und weltabhängige Hinweisexistenz Außeninformationen offenlegen können. | Modellierte Regel, keine implementierte Zugangskontrolle. Reale Leserrechte, Rechtsgrundlage, Aufbewahrung/Löschung und technische Trennung bleiben offen. |
| **IB-C8: Fremde Freitexte als Steuerbefehle und Verwaltungs-/Ausführungszugänge** | Ausschluss erhalten. E1–E7 verleihen keine Freigabe-, Rechte-, Secret-/Budget- oder Stopkompetenz. Allgemeine MCP-Verfügbarkeit beweist keine reine Beobachtersicht. | D-012 ist Rollenmaßgabe, kein aus dem Experiment abgeleitetes Recht. Kein Steuer-/Adminpfad oder Schutz vor Ausführung hier implementiert/geprüft. |

Eine dokumentierte Analysefrage schafft weiterhin **kein Leserecht**. Auch
Zusammenführung und abgeleitete Aussagen können neue Vertraulichkeit tragen.
E7 erlaubt weder, reale Empfängerregeln zu erfinden, noch, fremde Beziehungen
„zur besseren Erklärung“ außerhalb der belegten zulässigen Sicht auszugeben.

## F – Aussageklassen von Authority

Die vorhandenen Ergebnisse stützen die folgenden sprachlichen Unterscheidungen.
Das ist keine neue Statusmaschine, Eventliste, Entscheidungstabelle oder Produktlogik.
Die Klassen beschreiben Belegstärke und Scope; sie sind nicht zwingend gegenseitig
ausschließende technische Werte.

| Aussageklasse | Was die Aussage tragen darf | Beleg / Grenze |
|---|---|---|
| **Gemeldet / beobachtete Meldung** | Eine bezeichnete Quelle meldet einen Status, eine Absicht, eine Anfrage oder ein Ereignis im sichtbaren Scope. | E4 K03–K05; E6 Egressabsicht. Quelle, Inhalt und Bezug nennen; Meldung nicht als Wirkung ausgeben. |
| **Vollzug gemeldet und passend zugeordnet** | Ein zusätzlicher Beleg meldet den bestimmten Vollzug bzw. die Nichtausführung des bestimmten Vorgangs. | E4 K15–K17. Quellenzuverlässigkeit ist dort gesetzt. „Buchung gemeldet“ ist weder Operationswirkung noch Gesamtabrechnung; „Cancel vollzogen gemeldet“ kein physischer Fernstopp. |
| **Wirkung innerhalb des benannten Belegumfangs belegt** | Der vorhandene Wirkungsbeleg trägt eine konkrete Wirkung; Umfang und Belegart müssen mitgenannt werden. | Historischer FakeAdapter-Späteffekt bzw. praktische modellierte Exp03-Befunde. E1/E3–E7 liefern dafür nur konstruierte Effekt-/Herkunftsmeldungen, keine unabhängige reale Wirkungsbestätigung. |
| **Zugeordnet / Reihenfolge oder Herkunft bedingt belegt** | Eine ausdrücklich gültige Bindung/Ordnung/übernommene Beziehung trägt genau den benannten Vergleich. | E1 K5/K6; E3 K12–K14 Actor; E5 K18–K20; E6 K21/K22. Keine zusätzliche Ressourcengleichheit, Dauer oder v1-Label ableiten. |
| **Widersprüchlich / widersprechende Belege oder Dokumentation** | Ein konkreter Konflikt wird mit beiden Belegen und ihrem vergleichbaren Scope benannt; keine vermutete Auflösung. | IBs sieben Konflikte und später belegte Teilkorrekturen; E2 Geheimnisfreiheitsanspruch gegenüber Markerbefund. Nicht jede Quellenperspektive oder Meldungsstufe widerspricht einer anderen. Keine neue automatisierte Konflikterkennung belegt. |
| **Unbekannt / nicht ausreichend belegt** | Vorhandene Sicht reicht für die betreffende Aussage nicht. Die fehlende Bindung, Meldung oder Information wird benannt. | E1 K1–K4; E3 K01/K02/K14 Ressource; E4 K03–K05; E5 K08/K20 Dauer; E6 K09/K10/v1-Label. Unbekannt ist weder negativ noch PUBLIC, harmlos, abgeschlossen oder verboten. |
| **Nichtausführung im ausdrücklich belegten Scope gemeldet** | Ein vorhandener negativer Beleg darf als solcher benannt werden, mit Versuch/Ziel und Quellenvoraussetzung. | E4 K15 `access.not_performed`: nur dieser Versuch. Unterschied zu „kein Vollzugsbeleg vorhanden“ erhalten; kein globales Nie-/Nichtnutzungsurteil. |
| **Nicht untersucht / außerhalb des Versuchs** | Keine passende Untersuchung liegt vor; es wird keine Ergebnisbehauptung erzeugt. | E2 produktiver Input/Anzeige/Warnung; reale Leistung/Menschenverständnis; reale Zugriffstrennung. Nicht mit Widerlegung oder bestandenem Test verwechseln. |
| **Nur im Labor / Papierfall gezeigt** | Ein positiver oder negativer Befund wird ausdrücklich an das Modell und seine Voraussetzungen gebunden. | E1/E3–E7 Papier; E2 eigenes künstliches Lab; ältere Gate-/IFC-/Adapterbefunde historisch. Experiment-Confidence getrennt von Übertragungs-Confidence nennen. |

Insbesondere müssen „nicht gemeldet“, „explizite Nichtausführung gemeldet“ und
„nicht untersucht“ auseinanderbleiben. Ein bekannter begrenzter Beleg kann neben
unbekannter tatsächlicher Wirkung stehen. Hinweisbearbeitung wie „bestätigt“ oder
„geschlossen“ bestätigt keinen Aktionsvollzug und erteilt keine Erlaubnis.

## G – Gefundene Probleme für eine spätere Umsetzung

Hier stehen ausschließlich bereits nachgewiesene oder dokumentierte Probleme.
Die Kennzeichnung unterscheidet einen gemessenen Fehler im vorhandenen Labweg
von einer Dokumentationsabweichung, einer bestehenden Beobachtungslücke oder
einem nur konstruiert gezeigten Risiko. **Keine dieser Zeilen ist eine Reparatur
oder neue Architekturentscheidung.**

| Problem | Beleg und Status | Grenze / noch nicht gelöste Frage |
|---|---|---|
| Metadaten erhalten Marker vor/in der untersuchten persistenten Exportdatei | E2 acht Metadatenfälle praktisch gemessen: Actor/Resource/URL/Reason in JSONL; Actor/Resource zusätzlich in benannten eigenen Speichern. | Konkrete vorhandene Lab-Datenlücke. Nicht durch Parameterausschluss, kleinere Stateprojektion, PUBLIC oder Hashing geschlossen; tatsächliche Monitoraufnahme unbekannt. |
| Bereinigungsbeschreibung und bisherige Assertions reichen für Stringwerte nicht | E2 `public_view()`-Docstring und Top-Level-Schlüsselprüfungen gegenüber Markerbefund. | Nachgewiesene Aussage-/Prüfgrenze; keine bestehenden Tests oder Beschreibung hier geändert. |
| Ereignis-/Spanreferenzen liefern keinen gemeinsamen belegten Aktionsbezug | IB L1 dokumentiert getrennte Event-/Span-UUIDs und fehlende gemeinsame Action-ID. E1/E4 zeigen die Folgen fehlender Bindung in Karten. | Bestehende Exportgrenze, keine neue ID erfunden. Welche reale Bindung genügt, bleibt offen. |
| Export deckt Phase 2, Finish und externe Wirkung nicht als vollständige Folge ab | IB L1/L8, E1 und E3–E7 eigene Belege. | Papierereignisse sind keine realen Sensoren. Historisches Finish-Finding enthält keine nachträglich ergänzbare vollständige AA-Replayfolge. |
| Emissionsfehler können still bleiben | IB A12/L1: Fehler werden geschluckt; fehlender Export nicht automatisch Inaktivität oder erfolgreiche Redaktion. | Keine vorhandene Vollständigkeits-/Verlustgarantie. Notwendige technische Erfassung nicht bestimmt. |
| Zeitstempel-/Ereignisnamen können eine falsche zeitliche Bedeutung nahelegen | IB und E5: `authority.requested` nach gebildeter Decision; Sekunden-Wallclock. | Kein Original-Anfrageeingang, keine globale Ordnung oder Latenzmessung. Kartenzeiten lösen den realen Exportbefund nicht. |
| Graph-/Statuskanten können Nutzung, Charge oder Wirkungsbezug überbehaupten | IB Widerspruch 4; E4 Status-/Vollzugsvergleich. | Historisch dokumentierte falsche Kanten und konstruiert gezeigte Informationsgrenzen; kein neu gemessener produktiver AA-Graphfehler. |
| Fake-Ressourcenidentität reicht nicht für reale Ressourcen-/Revisionsfragen | IB L6/L7; E3 K14 zusätzlich INCONCLUSIVE. | Lexikalische Aliase im Fake-Lab positiv; reale Symlinks/Mounts/URLs und Epochengültigkeit nicht bewiesen. K14 nicht repariert. |
| Lifecycle-Ende begrenzt externe Effekte nicht nachgewiesen | IB L8 / historisches Finish-Finding; E1/E4. | Später FakeAdaptereffekt dokumentiert; OOS-021 und reale Stop-/Widerrufs-/Effectbezüge offen. Kein Wiederholen des Probes. |
| Herkunftsanfrage ist kein Übernahmebeleg | IB L5/E6: früher Binding-PASS durch späteren Atomicity-Befund begrenzt. | Spätere Labkorrektur erhalten; nicht als weiterhin unreparierter gleicher Bug darstellen. Problem bleibt die falsche Schlussfolgerung aus bloßer Anfrage. |
| Fehlende Herkunft kann mit vorhandenen Labels verwechselt werden | E6 K09/K10 unbekannt; K21/K22 nur o1-Label; G3 PUBLIC konstant laut IB/E2. | Kein eigener v1-Labelwert, keine vollständige Monitor-Lineage oder allgemeine IFC belegt. Die unterschiedlichen Labels/Quelltypen sind nicht austauschbar. |
| Ein abgeleiteter Hinweis kann Außeninformationen enthalten | E7 K23/K24 praktisch nicht implementierte Papieroffenlegung; IB A13/C7. | Namenmaskierung lässt Inhalt/Anzahl/Querbeziehung bzw. weltabhängige Existenz zurück. Kein getesteter realer Empfängerfilter; K11 kein allgemeiner Schutzbeweis. |
| Bestehende Misses bleiben durch Regression nicht erledigt | IB L7/L9, E2/E3–E7: RC-01–05, CB-01; bestehende Ausschlüsse. | Historische Gate-/Transferlücken, keine gemessene Beobachterquote. Kein Fix und keine neue Untersuchung hier. |
| Datierte Fremdtoolverträge bilden keinen bewiesenen gemeinsamen Beobachtungspfad | IB T1/F1/F2/X1–X3: unterschiedliche Referenzen, Status-/Charge-/Abbruchgrenzen und SDK-/Protokollperspektiven. | Keine aktuelle Integration, keine Pflichtabhängigkeit von ThreadDesk, Tollgate, 4AllPass, Gnom-Hub, Codex, Claude Code, lokalen Agenten oder MCP. |
| Forschungsbelege reichen nicht bis reale Warnung/Empfang/Verständnis | E2 produktiver Pfad unbekannt; E1/E3–E7 reale Leistung und menschliche Verständlichkeit INCONCLUSIVE. | Dokumentierte Validierungs-/Forschungsgrenze, kein erfundener Ausfall einer vorhandenen Monitorfunktion. |

## H – Reicht der Forschungsstand für eine Spezifikation?

**Für eine begrenzte Spezifikation von Aussagegrenzen und zweckgebundenem
Informationsbedarf: teilweise ja. Für eine vollständige belastbare Spezifikation
eines realen Monitors, universeller Pflichtfelder oder von Erkennungs-/
Datenschutzgarantien: nein.** E1–E7 spezifizieren hier selbst nichts neu; die
folgende Vorlage grenzt ab, wofür ihre Belege ausreichen.

### Ausreichend untersucht für begrenzte Anforderungen

| Teil | Was daraus verantwortbar als Anforderung beschrieben werden kann | Bindende Grenze / Quelle |
|---|---|---|
| Aussagebedeutung und Unsicherheit | Gemeldeten Status, zugeordneten Vollzug, Wirkungsbeleg und unbekannten Stand getrennt benennen; fehlende Information nicht als negative Tatsache behandeln. | E1/E4/E5, Abschnitt F. Semantische Grenze, kein bewiesener automatischer Detektor. |
| Vorgangs- und Identitätsbezug | Eine Aussage über einen bestimmten Lauf, Actor oder eine Ressource braucht den tatsächlich belegten Bezug im benannten Scope; Bindung nicht aus Namen/Zeiten ergänzen. | E1/E3/E4. Kein vollständiges ID-/Eventschema; K14-Ressource offen. |
| Ordnung und Dauer | Empfangsordnung, Quellordnung und Zeitdifferenz verschieden behandeln; numerische Dauer nur mit passenden Zeitbelegen. | E5 und G3-Grenzen. Keine globale Uhren- oder Zustellgarantie. |
| Herkunftsaussagen im modellierten Bereich | Herkunft nur auf belegte Quellenlabels und übernommene Beziehungen stützen; weder Inhaltsgefährlichkeit noch eigenes v1-Label erfinden. | E6 plus bestehende Exp03-Befunde. Reale Erfassung/Vollständigkeit nicht nachgewiesen. |
| Dokumentation der Belegstärke | Labor-/Papierbefund, Voraussetzungen, offenen Scope und Übertragungsgrenze ausdrücklich mitführen; spätere belegte Korrektur nicht zur universellen Behauptung machen. | IB L9 und E1–E7. Kein hier erprobtes technisches Analyse-/Warnformat. |
| Vorhandene Daten- und Rollenbegrenzung | D-012 und IB-C1–C8 als bereits gesetzte Grenzen erhalten; E2-Lücke und E7-Risiken ausdrücklich in Anforderungen berücksichtigen. | Normative Ausgangsgrenzen plus E2/E7-Befunde. Forschung schafft keine Rechte; weder Redaktion noch technische Sichttrennung bereits bewiesen. |

Diese Teile tragen **Aussageanforderungen**, keine Produkt-/Architekturentscheidung.
Die als bedingt oder ungeklärt markierten Angaben aus D werden dadurch nicht zu
universellen Pflichtfeldern. Ein Teil mit unbekannter Informationslage kann nur
mit dieser sichtbaren Grenze beschrieben werden, nicht mit einer garantierten
Zuordnung, Erkennung oder Wirkung.

### Zwingender Forschungsbedarf vor weitergehenden Spezifikationsbehauptungen

Die folgenden offenen Fragen müssen geklärt sein, **bevor gerade die entsprechende
weitergehende Leistung oder das allgemeine Minimum verantwortbar behauptet werden
kann**. Sie verhindern nicht sämtliche oben begrenzten Aussageanforderungen.
Hier werden keine neuen Versuche entworfen oder begonnen.

| Offene Forschungsfrage | Welche Spezifikationsbehauptung dadurch noch nicht getragen wird | Vorhandener Ausgangsbeleg |
|---|---|---|
| Welche belegte Ressourcenbindung gilt über Referenz-/Epochenwechsel? | Verlässliche Ressourcenkontinuität über diesen Wechsel; insbesondere keine Schließung von K14. | E3 K02/K14; INCONCLUSIVE wegen nicht isoliertem Ressourcenvergleich. |
| Welche Informationsarten reichen in realen Abläufen tatsächlich für eine benannte Beobachtungsfrage, und welche fehlen? | Vollständiges minimales Pflichtfeldschema oder zuverlässige Wirkungs-/Zuordnungsaussage für reale Agenten. | E1/E3–E6 Papierannahmen, IB A1–A13, LOW-Generalisation. |
| Welche reale Herkunft, Quellechtheit und Gültigkeit sind belegbar; was passiert bei falschen Labels/kompromittierten Quellen? | Wahrheit oder vollständige Lineage allein aus Quelllabel, Hash oder Meldung. | IB L9, E6; Quellechtheit nicht untersucht. |
| Welche realen Zeit-/Liefer-/Coveragegrenzen erlauben tatsächlich den benötigten Vergleich? | Globale Ordnung, Vollständigkeit, Ausfall-/Nichtabschlussaussage oder belastbare Dauer ohne passende Quellenbelege. | E5, IB A5/A12/L1. |
| Welche Granularität wird für Kosten, Ressourcenrevisionen, Zugänge, Rollen und Delegation benötigt? | Allgemeine Vollständigkeit oder Hinreichendheit von IB-A4/A7–A10; universelle Zähler-, Betrag-, TTL-, Revisions- oder Rollenpflicht. | IB zweckgebundene Ableitungen; E4 begrenzte Status-/Vollzugsfälle; historische RC-/CB-Lücken. |
| Welche Warn-/Erkennungsleistung und welchen Nutzen erreichen die verfügbaren Informationen? | Beobachterqualität, brauchbare Schwellenwerte, Fehlalarm-/Missraten oder verständliche reale Analyse. | E1/E3–E7 reale Leistung INCONCLUSIVE; historische Gatezahlen keine Monitorzahlen. |
| Was verlieren reale Herkunftsfragen ohne Rohinhalt und unmodellierte Beziehungen? | Allgemeine IFC, semantische DLP, Absichts-/Injectionerkennung oder vollständige Beobachtung von Nebenkanälen. | E6, IB C2–C4/L4/L9; konkrete positive modellierte Befunde bleiben bestehen. |
| Welche Außeninformation enthalten Hinweise außerhalb des konstruierten Weltpaars? | Allgemeine Nichtinterferenz oder pauschal sichere maskierte Hinweise. | E7 K11/K23/K24; keine allgemeine oder technische Garantie. |

Einige Lücken sind außerdem **ausstehende Festlegungen**, keine allein durch einen
Test beantwortbaren Forschungsfragen: konkreter zulässiger Analysezweck, reale
Leserrechte/Rechtsgrundlage, Zugriffsumfang, Aufbewahrung/Löschung und notwendige
Rückmeldung. E7 setzt eine Regel voraus und legitimiert keine reale Regel.
Die Konsolidierung trifft diese Entscheidungen nicht. Eine entsprechende
Spezifikation muss die fehlende Grundlage ausdrücklich offenlassen.

### Spätere Umsetzungs- und Validierungsfragen, die offen bestehen bleiben können

Wenn eine spätere Spezifikation ihren Zweck, Scope und Aussagegrenzen auf die
gesicherten Teile beschränkt, können folgende Punkte als ausdrücklich ungelöste
Umsetzungs-/Validierungsfragen bestehen bleiben. Sie sind **keine schon erfüllten
Garantien** und werden hier weder gelöst noch als Folgeauftrag begonnen.

| Punkt | Warum eher Umsetzung / Validierung nach begrenzter Festlegung | Verbleibende Grenze |
|---|---|---|
| Tatsächliche Umsetzung der festgelegten Datenbegrenzung in den eigenen Speicher-/Export-/Analysewegen | E2 zeigt den konkreten bestehenden Mangel; das Ausschlussziel ist schon dokumentiert. | Keine behauptete Bereinigung, Secret-Erkennung oder Vollständigkeit. Welche reale Minimierung genügt, kann zusätzliche Forschung erfordern; E2 deckt nur seine Eingaben ab. |
| Nachweis eines später gewählten tatsächlichen Monitorinputs, der Anzeige und Zustellung | Verbindung und Verhalten müssen im jeweiligen ausgewählten Weg validiert werden. | E2 prüft diesen Pfad nicht. Quellenwahl/Verträge sind hier nicht festgelegt; keine Fremdtoolabhängigkeit ableiten. |
| Einhaltung bereits festgelegter Bindungs-, Meldungs- und Ordnungssemantik | Die Unterscheidungen sind gestützt; eine konkrete spätere Umsetzung muss ihre Semantik nachweislich einhalten. | Real unzureichende Quellen-/Uhrqualität kann weitere Forschung nötig machen. Keine globale Garantie aus Papieranalyse. |
| Technische Umsetzung einer später tatsächlich zulässigen Empfängersicht und Übermittlung | E7 dokumentiert das Risiko von Text und Hinweisexistenz; eine gewählte reale Regel muss technisch validiert werden. | Kein vorhandener Filter, keine sicheren Rechte oder Zustellung belegt. Allgemeine Informationsschutzbehauptungen benötigen zusätzlich die oben offene Forschung. |
| Erhaltene bekannte Lücken und Konformität des historischen Labs | Bestehende Regressionsergebnisse können datiert referenziert werden; späterer Änderungsumfang müsste separat geprüft werden. | RC-01–05/CB-01/OOS-021 nicht geschlossen; kein aktueller Gate-PASS als Beobachterbeweis. |
| Verständlichkeit einer späteren konkreten Darstellung | Empirische Nutzerprüfung gehört zur Validierung der dann tatsächlich vorhandenen Darstellung. | Heute keine Menschenstudie. Forschung zum Nutzen/Erkennungsanspruch bleibt davon getrennt; keine Nutzbarkeitsgarantie jetzt. |

**Schlussfolgerung:** Der Forschungsblock reicht für klar begrenzte Anforderungen
an Belegbezug, Aussageklassen und Datenbegrenzung; eine vollständige reale
Monitorspezifikation braucht zusätzliche, ausdrücklich beauftragte Klärung der
offenen Informations- und Übertragungsfragen.

**Abschlussgrenze dieser Konsolidierung:** Nur dieses neue Dokument und sein
dokumentarischer README-Verweis werden gespeichert, geprüft, committed und
gepusht. Keine bestehenden Forschungsdateien, Tests oder Programme verändert;
keine neuen Tests, Experimente, Reparaturen oder Folgeaufträge. **Danach STOPP.**
