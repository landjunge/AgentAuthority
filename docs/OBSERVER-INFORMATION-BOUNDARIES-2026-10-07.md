# Welche Informationen Agent Authority beobachten sollte

Stand: 7. Oktober 2026. Forschungsübersicht, keine Implementierung oder neue
Gesamtarchitektur. Ausgangspunkt ist der abgerufene `master`
`ef2400fa5fad3c4ff051928b78fcb3093bb23453` einschließlich PR #18.
KI-Zentrale: `96526cf99b94bfae9f6c177c6d07d2925404ecdd`.

**Die vorhandenen Befunde sprechen für nachvollziehbare Vorgangsbezüge,
Quellmeldungen und belegte Zustandsänderungen statt Kopien der Arbeitsinhalte.**
Auch Metadaten können Geheimnisse, Personenbezüge und vertrauliche Zusammenhänge
enthalten. „Nur Metadaten“, ein `PUBLIC`-Label oder ein Hash machen sie nicht
automatisch unbedenklich.

Gemäß [D-012](#k1) ist Agent Authority ausschließlich Beobachter / Monitor /
Analyseebene. Es erlaubt oder verbietet keine Aktionen, vergibt oder entzieht
keine Rechte, erteilt keine Freigaben, gibt weder Secrets noch Budgets frei und
stoppt nichts. Die historischen Lab-ALLOW/DENY-Befunde bleiben erhalten, begründen
aber keine Produktbefugnis. Eine von einem anderen Werkzeug gemeldete Entscheidung
ist eine Beobachtung dieser Quelle.

## Wie die Kategorien zu lesen sind

- **A – notwendig zu beobachten:** notwendig für die jeweils ausdrücklich genannte
  Beobachtungsfrage. Nicht jedes Projekt benötigt Kosten-, Zugangs-, Delegations-
  oder Informationsflussanalyse. Daraus folgt kein pauschales Sammelrecht.
- **B – hilfreich, aber nicht zwingend notwendig:** Zusatzangaben mit einem
  erklärbaren Nutzen; sie können zunächst entfallen.
- **C – sollte Agent Authority nicht erhalten:** für diese Beobachtungsfragen
  entbehrliche Rohdaten oder Angaben mit unverhältnismäßigem Zusatzrisiko.

„Darf sehen“ bedeutet hier: Die zuständige Quelle kann für einen festgelegten
Zweck ausgewählte, minimierte Informationen bereitstellen, wenn Sichtumfang,
Leserzugriff und Aufbewahrung geklärt sind. Diese Untersuchung bestätigt keine
gesetzliche Rechtsgrundlage, Einwilligung oder sichere Zugriffstrennung.
Die entsprechenden Fragen sind in der KI-Zentrale ausdrücklich offen [K1, K2].
Analysebedarf erzeugt keine neuen Leserechte; private ThreadDesk-Inhalte sind
keine allgemeine Produktvorgabe (D-009/D-010).

**Belegdisziplin:** Die Auswahl unten ist eine Forschungsableitung. „Istcode“
belegt ein vorhandenes Feld oder Verhalten, keine vollständige Integration.
Dokumentierte historische Testergebnisse gelten nur an ihren genannten Baselines
und innerhalb der Fake-/In-Process-Modelle. Bestehende Testdateien wurden gelesen,
hier aber nicht ausgeführt. Die frühere Recherche und ihr Praxisabgleich werden
verwendet, keine neuen externen Quellen recherchiert. Keine echten Secrets,
Zugangsdaten, Tresore, privaten Arbeitsdaten oder Laufprotokolle wurden gelesen.

## A – notwendig zu beobachten

Alle Mengen sind auf den untersuchten Vorgang und Zeitraum begrenzt. Benötigte,
aber nicht verfügbare Angaben müssen als unbekannt erscheinen.

| Punkt / benötigte Information | Zweck und Folge bei Fehlen | Minimierung und Risiko | Quelle / tatsächlicher Beleg | Noch offene Frage |
|---|---|---|---|---|
| **A1 Ereignis und Aussagequelle:** Ereignisreferenz, berichtendes Tool, Ereignisart, Quell-/Formatstand und Aussageperspektive. | Einzelmeldungen, Wiederlieferung und abgeleitete Aussage unterscheiden. Ohne Quellenbezug kann dieselbe ID verschiedene Dinge bedeuten. | Quellklasse und begrenzte Referenz statt Geräte-/Kontoprofil. IDs und Quellnamen erlauben dennoch Verknüpfung; ein Quellenlabel authentisiert nichts. | [L1](#l1) Istfelder; [K2](#k2) CloudEvents-/Trace-Semantik; [K3](#k3) praktisch geprüfte Quellen-/Typverwechslung. | Welche Quelle liefert stabile Ereignisidentität und belegte Herkunft? |
| **A2 Zusammengehöriger Vorgang:** Projekt-/Auftragsbezug, konkreter Ausführungsversuch, Instanz und gegebenenfalls Generation; Herkunft ihrer Zuordnung. | Meldungen desselben Versuchs verbinden, parallele oder neu gestartete Arbeit trennen. Workflowname oder zeitliche Nähe allein reichen nicht. | Zweckbezogene, möglichst undurchsichtige Referenzen; gleiche Bezüge innerhalb des benötigten Scopes erhalten. Zu breite IDs erzeugen projektübergreifende Profile. | [L2](#l2) gemeinsamer Workflowzähler; [L8](#l8) fehlende Versuch-/Generationsbelege; [T1](#t1) vorhandene Handoff-/Jobbezüge. | Welche Zuordnungen über Toolgrenzen sind tatsächlich vorhanden? Keine Ersatz-ID erfinden. |
| **A3 Beteiligte Instanzen:** wer laut welcher Quelle handelt, getrennt von Anzeigename, Modellanbieter und Menschenzuordnung. | Gleichnamige Agenten, Ersatzinstanzen und Parallelität unterscheiden. Ein Anbietername sagt nichts über Zuständigkeit. | Projektbezogenes Pseudonym plus Instanzbezug; Klarnamen und private Personenprofile entfallen. Pseudonyme bleiben verknüpfbar und sind keine bewiesene Anonymisierung. | [K1](#k1) D-011/D-012; [T1](#t1) lokale Actor-/Instanzfelder; [L3](#l3) nur modellierte Actorzuordnung. | Wie bleibt die notwendige Korrelation erhalten, ohne globale Personenidentität? |
| **A4 Art einer Beziehung:** Meldung zu welchem Auftrag/Vorgang gehört; bei Delegationsfragen gemeldeter Auftraggeber, Empfänger, Elternauftrag und Zeitraum. | Delegation von Retry, Span-Elternschaft, Zugangsanfrage und beobachteter Nutzung trennen. Ohne Typ entstehen irreführende Graphkanten. | Nur die für den Vorgang nötigen Kanten, Quelle und Gültigkeit. Ein ganzer Sozial-/Rechtegraph ist entbehrlich und sensibel. | [K1](#k1) getypte, belegte Beziehungen; [K3](#k3) verweigerter Zugang als Nutzung dargestellt; [L2](#l2) Labtiefe ist keine reale Delegationsanalyse. | Meldet eine Quelle fachliche Delegation oder nur technischen Zusammenhang? |
| **A5 Zeit und Reihenfolge:** Quellzeit mit Bedeutung, Empfangszeit, bekannte Unsicherheit und vorhandene Sequenz-/Revisionsbezüge. | Verspätete Zustellung von später Wirkung unterscheiden. Ohne diese Angaben ist höchstens eine unsichere Teilordnung möglich. | Nur benötigte Präzision/Zeitraum; keine pauschale Arbeitszeiterfassung. Grobe Zeiten verringern die Detailtiefe, können aber die Prüffrage unentscheidbar machen. | [L1](#l1) G3-Zeit nur sekundengenau; [L8](#l8) Synchronisationsordnung ohne Ereigniszeiten; [K2](#k2) Ereignis-/Beobachtungszeit. | Welche Genauigkeit liefern die Quellen, und welche Reihenfolge ist unabhängig davon belegt? |
| **A6 Ablauf und tatsächliche Wirkung getrennt:** Anfrage/Annahme/Start/Fehler/Endmeldung, betroffenes Teilstück, vorhandener Ergebnis-/Zielbeleg; Stoppwunsch und bestätigter Vollzug auseinanderhalten. | „Fertig gemeldet“ von „Wirkung bestätigt“ unterscheiden. Ein Ende oder ein fehlender ACK beweist weder Stillstand noch Weiterausführung. | Status, Fehlerklasse und geschützte Belegreferenz statt Ergebnisinhalt oder Terminalausgabe. Selbstberichte bleiben begrenzt; eine Referenz beweist keinen Inhaltserfolg. | [L8](#l8) dokumentierter Effekt nach `finish`; [T1](#t1) delivered/unverified; [X1](#x1) soft cancel; [K2](#k2) Spanende/Finish-Grund. | Wer kann einen Ziel-/Effektbeleg liefern und welchen Teilvorgang deckt er ab? |
| **A7 Betroffene Ressource und Ausführungskontext:** stabile Ressourcenreferenz, Aktions-/Toolklasse, Zielklasse sowie relevante Konfigurationsrevision, wenn ein Wechsel untersucht wird. | Gleiche Ressource trotz Alias erkennen; gleichnamiges Tool mit geändertem Befehl von unveränderter Konfiguration unterscheiden. Namen allein verfehlen RC-03/04. | Quellseitig konsistente Ressourcenreferenz und Sicherheits-/Zielklasse statt vollständigem Pfad, URL oder Befehl. Detailverlust kann einen Wechsel unsichtbar machen; Klartext kann Secrets enthalten. | [L6](#l6) FakeAdapter-Aliasbindung; [L7](#l7) RC-01–05; [K3](#k3) sensibles Resource-Muster vor Ingest protokolliert. | Welche minimierte Revision/Referenz bewahrt die relevante Identität, auch bei realen Adaptern? |
| **A8 Nur für Kosten-/Loopfragen:** Tollgate-Meldungsstufe, Vorgangs-/Consumerbezug, Zeitraum und Einheit; zu vergleichender Betrag/Zähler oder gemeldete Grenze, soweit vorhanden. | Admission, Reservierung, Schätzung und Buchung unterscheiden; Wiederholungen dem passenden Vorgang zuordnen. Tokens sind keine Rechnung. | Zuerst benötigte Summen, Status und kurze Zeitfenster; keine Zahlungsdaten. Kostenverläufe können Geschäftsinformationen und Personenbezüge offenlegen. | [F2](#f2) Admission-Emitter und getrennte Audit-/Usage-Daten; [K1](#k1) Kostenstufen; [K3](#k3) Budgetcheck fälschlich als Belastung. | Welche Quelle liefert tatsächliche Buchung statt Schätzung, und ist ihr Vorgangsbezug vorhanden? |
| **A9 Nur für Zugangsfragen:** 4AllPass-Quellstatus angefragt/bereitgestellt/abgelehnt/abgelaufen/Entzug gemeldet, Scope, Gültigkeit, nicht einlösbare Beobachtungsreferenz und Zugangsmodus, soweit belegt. | Zugangsmeldung von Nutzung und Provider-/Verbraucherwirkung trennen. Eine verweigerte Bereitstellung macht spätere secretfreie Arbeit nicht verdächtig. | Status/Zeitraum/Referenz statt Token oder Secret. Referenz darf selbst keinen Zugang eröffnen. Vorhandene Scope-Bezeichnung ist kein eindeutiger Grantnachweis. | [F1](#f1) begrenzter realer Emitter, Security-Boundary; [K1](#k1) minimierte Zugangsmetadaten; [L7](#l7) truthy Token ohne Bindung. | Welche Bindung und TTL-/Entzugsbestätigung liefert die Quelle tatsächlich? |
| **A10 Nur für Rollen-/Änderungsvergleiche:** gemeldete Funktion/Zugangsklasse, fachlicher Scope, Quelle, Gültigkeit und voriger/neuer Revisionsbezug. | Änderungen demselben Gegenstand zuordnen. Projektrolle, Budgetrolle und Tresorzugang sind verschiedene Aussagen, kein automatischer Widerspruch. | Nur betroffene Zuordnung/Änderung, keine vollständigen Rechtebestände oder Standardhierarchie. Rollenbezüge bleiben sensibel; fehlende Revision macht Vergleiche unsicher. | [K1](#k1) D-009–D-012 und Zustandsvergleich; [T1](#t1) lokale Kontextfelder; [F1](#f1)/[F2](#f2) eigene Werkzeugzuständigkeiten. | Welche Quelle ist für diese konkrete Zuordnung zuständig und wie aktuell ist sie? |
| **A11 Nur für modellierte Informationsflussfragen:** Workflow-/Wertbezug, gemeldetes Label samt Herkunft, Daten-/Kontrollabhängigkeiten, Übergabe- und Egressbezug. | Herkunft eines Flusses statt bloß gleichen Inhalts betrachten. Ohne Kontrollbeziehung kann derselbe Statuswert verschieden sensibel sein, ohne sichtbar unterscheidbar zu werden. | Label, begrenzte Herkunftsklasse und nötiger Abhängigkeitspfad statt Payload. Auch Herkunft verrät sensible Quellen. Falsche Labels/fehlende Instrumentierung bleiben Blindstellen. | [L3](#l3) metadatenbasierte Fake-Übergabe; [L4](#l4) gleicher Inhalt, andere Provenienz; [L5](#l5) Bindungs-/Commitfolgebefund. | Lassen sich diese Metadaten außerhalb des Fake-Runtimes zuverlässig melden? G3 liefert sie derzeit nicht. |
| **A12 Sichtbarkeit und Lücken:** betrachtete Quellen/Zeiträume, letzte bekannte Beobachtung, bekannte Filter/Verluste und unbekannte Abdeckung. | „Nicht gesehen“ von „nicht passiert“ trennen. Ein stiller Producer kann ausgefallen oder lediglich inaktiv sein. | Quellstatus und Verlustzahl statt Queuepayload oder aller Logs. Detaillierte Verbindungsdaten können Infrastruktur verraten; fehlende Verlustanzeige bleibt unbekannte Abdeckung. | [L1](#l1) Exportausnahmen werden geschluckt; [K3](#k3) fehlende Phase-2-Events; [K2](#k2) Sampling/Queuegrenzen. | Existiert eine tatsächliche Verlust-/Aktualitätsmeldung oder nur die Erwartung einer solchen? |
| **A13 Authority selbst:** verwendete Quellreferenzen, Beobachtungsfrage/Regelstand, Zeitraum/Scope, Ableitung, Gegenbelege, Unsicherheit und Korrekturbezug eines Hinweises. | Einen Befund prüfen und spätere Korrektur nachvollziehen. Ohne Belege wird eine Warnung bloße Behauptung; fehlende Daten bedeuten nicht „normal“. | Nur benötigte Referenzen und begründeter Befund; keine Kopie sensibler Rohdaten in Warnungen. Abgeleitete Zusammenhänge können sensibler sein als Einzelereignisse. | [K1](#k1) Befund-/Vergleichsmodell; [L9](#l9) Aussagegrenzen; aktueller Labcode belegt keinen fertigen AA-Analysedienst. | Wie wenig Belegmaterial reicht für eine nachvollziehbare Erklärung und berechtigte Lesersicht? |

Bei Mengen-/Loopvergleichen genügen zugeordnete Zähler beziehungsweise relevante
Zustandsdifferenzen mit Quellperspektive; vollständige kumulative Pfadlisten sind
kein allgemeines Muss [L2]. Ein von Tollgate gemeldeter Freeze betrifft dessen
Admissionbereich; Scope und Ausnahmen müssen bekannt sein, bevor Meldungen
verglichen werden. Freeze ist kein Beleg für gestoppte Remoteeffekte [F2].
Bei Wiederlieferung ist Ereignis-/Nachrichtenidentität von Wertidentität getrennt
zu halten; eine neue Nachricht kann denselben Wert transportieren [L3, L5].

## B – hilfreich, aber nicht zwingend notwendig

Diese Angaben zunächst weglassen, wenn keine zusätzliche konkrete Frage ihren
Nutzen rechtfertigt. Zweckbedingt notwendige Kontextteile stehen bereits in A.

| Punkt / mögliche Zusatzinformation | Zweck | Minimierung und Risiko | Quelle / tatsächlicher Beleg | Noch offene Frage |
|---|---|---|---|---|
| **B1 Kurzer freigegebener Auftragstyp oder Titel**, ohne Notizen/Dateien. | Einer Person den Vorgang erklären; A-Referenzen reichen für technische Zuordnung. | Kategorie oder bereinigter Titel. Auch kurze Titel können Personen-/Projektinhalte verraten. | [T1](#t1) `list_threads` ohne Notizen, `get_thread` dagegen mit Inhalten. | Ist ein Titel nötig oder reicht die Vorgangsreferenz? |
| **B2 Anbieter-/Modell-/Connectorversion, Retryzahl und Proxy-Perspektive**, wenn nicht schon Gegenstand von A7. | Kompatibilitäts-/Pfadunterschiede erklären; logischen Aufruf von Unteraufrufen unterscheiden. | Klasse/Version statt vollständiger Toolbeschreibung, Startkonfiguration oder URI. Keine feste Zuständigkeit aus dem Anbieter ableiten. | [T1](#t1), [X1](#x1), [X2](#x2); [K2](#k2) Caller-/Retryperspektive. | Welche zusätzlichen Unterschiede erklären diese Angaben nachweisbar? |
| **B3 Dauer, Tokenindikatoren und feinere Kostenverläufe.** | Verzögerungen oder wiederholte Nutzung genauer erklären. Für einfachen Statusvergleich genügt A6. | Passend aggregiert; Einheiten/Zeitraum erhalten. Risiko von Arbeits-/Leistungsprofilen und falscher Gleichsetzung Tokens = Geld. | [F2](#f2) vorhandene Usage-/Auditdaten; [K2](#k2) GenAI-Konventionen als Development-Denkmodell. | Reicht eine Summe, und welches zusätzliche Detail verbessert den Befund? |
| **B4 Zusätzliche getypte Belegpfade oder unabhängiger Gegenbeleg.** | Quellenkonflikte und unvollständige Herkunft genauer erklären. | Nur relevante Referenzen; keine vollständigen Archive. Eine Signatur oder Hashkette beweist weder Wahrheit noch Vollständigkeit. | [L4](#l4) begrenzte Erklärungspfade; [K1](#k1) Gegenbelege; [L1](#l1) unkeyed Hash. | Gibt es überhaupt eine unabhängige Quelle, und genügt der vorhandene Pfad? |
| **B5 Bereinigte Fehlerklasse und grober technischer Ursachenbereich.** | Fehler und Abbruch verstehen. Freier Stacktrace ist dafür nicht zwingend nötig. | Kurzer Fehlercode, gegebenenfalls Komponente/Version. Auch Fehlertexte, Dateinamen und Stacktraces können Inhalte oder Zugangsdaten tragen. | [X1](#x1) Jobfehler und Toollogs; [X2](#x2) gemischte Protokollinhalte; [K1](#k1) Datenverzicht. | Welche Klassen genügen, ohne den Fehler unverständlich zu machen? |
| **B6 Minimierter Befundbearbeitungsstand und zuständige Stelle.** | Wissen, ob ein Hinweis erklärt, korrigiert oder noch ungeklärt ist. | Status/Zuständigkeitsreferenz statt interner Diskussion. Ein bestätigter Hinweis ist keine Ausführungsfreigabe. | [K1](#k1) offene Adressaten-/Bearbeitungsfrage; [T1](#t1) vorhandene Reviewstatus als Quellmeldung. | Wer darf den Befund sehen/bearbeiten, und welche Rückmeldung ist nötig? |

## C – sollte Agent Authority nicht erhalten

Der Verzicht begrenzt die Analyse bewusst. Fehlender Rohinhalt wird nicht durch
Behauptungen über Absicht, semantischen Schaden oder allgemeine Injection-Erkennung
ersetzt. Ein künftiger Inhaltsprüfauftrag wäre ein anderer, ausdrücklich zu
klärender Auftrag; er ist hier nicht beauftragt.

| Punkt / bewusst weglassen | Zweck des Verzichts / nicht erforderlich für | Risiko | Quelle / tatsächlicher Beleg | Noch offene Frage |
|---|---|---|---|---|
| **C1 Passwörter, API-/Providerkeys, Access-/Refresh-/Pairing-/Approvaltokens, Cookies, private Schlüssel, Vaultinhalte und einlösbare Capabilitywerte.** | A9 lässt sich mit Status und nicht einlösbarer Referenz untersuchen. Auch Authmaterial des Beobachtungswegs gehört nicht in Ereignisse/Befunde. | Zusätzlicher Secretbesitz, Weitergabe und Zugriffsmöglichkeit; Hashen eines erratbaren Secrets macht es nicht automatisch sicher. | [K1](#k1) D-004/D-012; [F1](#f1) Secret-/Tokenboundary; [L2](#l2) Parameter werden nicht in Provenienz kopiert. | Sind Referenzen wirklich nicht einlösbar und alle Speicher-/Exportwege frei von Werten? |
| **C2 Vollständige Prompts, Systeminstruktionen, Antworten und Chat-/Terminalverläufe.** | Technische Ablauf-/Statusbeobachtung braucht A1–A6, nicht vollständige Konversationen. | Vertrauliche Inhalte, personenbezogene Daten, Secretbeimischung und fremde Anweisungen. Verzicht bedeutet keine verlässliche semantische Injection-/Absichtserkennung. | [K1](#k1) Inhaltsverzicht; [K2](#k2) GenAI-Privacy und Uploadhook-Grenze; [X2](#x2) inhaltsreiche Protokolle. | Welche Statusinformation ist derzeit nur im Freitext verfügbar? Das rechtfertigt keine pauschale Sammlung. |
| **C3 Rohe Toolargumente/-resultate, vollständige Shellbefehle, HTTPbodies und MCP-Payloads.** | A7 benötigt Identitäts-/Revisionsunterschiede; A6 Status/Effektbezug. Diese sind nicht mit Inhalt gleichzusetzen. | Secrets und sensible Nutzdaten in Argumenten/Ergebnissen. Rohinhalt behebt nicht automatisch uninstrumentierte Wirkungen. | [L7](#l7) Verb/Befehl/Wirkung nicht gebunden; [X2](#x2) Toolresultate sind Inhalte; [L3](#l3) modellierte Metadatenprüfung ohne Payload. | Welche minimale Quellbeschreibung bewahrt den relevanten Unterschied ohne Rohbefehl? |
| **C4 Dokument-/Dateiinhalte, Notizen, Bilder/Screenshots, Browserseiten und vollständige Arbeits-/Memory-/Jobsnapshots.** | Zusammengehörigkeit und Status lassen sich über Referenzen beobachten; keine zweite zentrale Inhaltsablage erforderlich. | Vertrauliche Arbeit, Kundendaten, Bildschirminhalte, Tresor-/Sitzungsreste und private ThreadDesk-Nutzung. | [T1](#t1) Vollabfragen enthalten Notizen/Dateien; [X1](#x1) Einzeljob enthält Snapshot/Toollog; [K1](#k1) D-009/D-010. | Welche minimale Ergebnisreferenz ist verfügbar, ohne den Snapshot zu übernehmen? |
| **C5 Unminimierte Pfade, URLs inklusive Query/Userinfo, Beschreibungen, freie Fehlertexte oder Labels mit Rohwerten.** | Für Zuordnung reichen möglichst A7-Referenz und Ziel-/Ressourcenklasse, für Fehler B5. | Metadaten sind ein eigener Leckkanal. Bereinigung erst beim Empfänger lässt die frühere lokale Speicherung ungeschützt. | [L1](#l1) rohe Actor/Action/Resource/Workflow-Werte; [K3](#k3) künstliches Secretmuster vor TD-Ablehnung emittiert. | Ist Minimierung vor der ersten Speicherung sowie in Anzeige und Warnung nachgewiesen? |
| **C6 Klarnamen-/Kontakt-/Geräteprofile, pauschale Arbeitszeit-/Leistungs-/Schuld-/Machtscores.** | A3 braucht Instanzzuordnung, keine personenbezogene Gesamtschau. Hoher Knotengrad oder viel Aktivität beweist kein Fehlverhalten. | Zweckfremde Bewertung, Überwachung, falsche Schuldzuordnung und langfristige Verknüpfung. | [K1](#k1) keine pauschalen Profile/Scores; [K2](#k2) keine Rechtsgrundlage durch Kontrollkatalog belegt. | Welcher enge Personenbezug ist für den konkreten Projektfall unvermeidbar? |
| **C7 Vollständige Rollen-/Rechte-/Vault-/Budget-/Abrechnungsbestände und Daten fremder Projekte außerhalb der zulässigen Sicht.** | A8–A10 benötigen passende Quellmeldung/Revision, keine Kopie aller Bestände. | Ausweitung von Lesersicht, Geschäfts-/Finanzdaten, sensible kombinierte Beziehungen; abgeleitete Warnungen können Sichtgrenzen überschreiten. | [K1](#k1) offene Leser-/Aufbewahrungsregeln; [F1](#f1)/[F2](#f2) breite Antworten sind kein minimierter AA-Feed. | Wie werden Quellen, Hinweise, Exporte, Aufbewahrung und Löschung auf denselben erlaubten Scope begrenzt? |
| **C8 Freitextanweisungen als Steuerbefehle oder Verwaltungs-/Ausführungszugänge.** | Ereignisse beschreiben Arbeit; Beobachtung braucht keinen Schlüssel zum Freigeben, Freeze-Ändern, Stoppen oder Ausführen. | Prompt-/Anzeigeinjection und Rollenüberschreitung. Allgemeine MCP-/Brokeranbindung kann zugleich schreibende Tools zugänglich machen. | [K1](#k1) D-012; [F2](#f2) TG-Steuerwerkzeuge; [X2](#x2) Protokollfähigkeit ist keine Beobachterbegrenzung. | Welche vorhandene Datensicht lässt sich untersuchen, ohne solche Befugnisse mitzunehmen? Keine neue Schnittstelle wird hier entworfen. |

## Was der vorhandene Stand je Werkzeug tatsächlich trägt

Diese Übersicht beschreibt Beleglagen, keine neue Verbindungskette.

| Werkzeug | Vorhanden / belegt | Für AA noch nicht belegt / Datenverzicht |
|---|---|---|
| **ThreadDesk** | Lokale Actor-/Instanz- und Handoff-/Job-/Returnbezüge, Revisionen und Status; kleine Listenabfrage getrennt von inhaltsreicher Vollabfrage [T1]. | Kein kryptografischer Actor-/Reviewerprincipal und kein vollständiger gemeinsamer AA-Feed bewiesen. Auswahl A2–A4/A6/A10; private Notizen, Returninhalte und Dateien entfallen. |
| **Tollgate** | Admission-/Freeze-JSONL und getrennte Audit-/Usage-/Statusdaten [F2]. | Eventexport belegt keine Buchungsphase oder vollständige Consumer-/Requestbindung. Bei Kostenfragen A8; keine Providerkeys, vollständigen Auditantworten oder Steuerzugänge übernehmen. |
| **4AllPass** | Optional genutzter JSONL-Pfad für Brokerstatus; dokumentierte Grenzen von Pairing, TTL und kopiertem Secret [F1]. | Keine vollständige Identitäts-/Grant-/Nutzungs-/Entzugssicht. Bei Zugangsfragen A9; Tokenbytes, Beweis-/Tresorinhalte und einlösbare Referenzen entfallen. |
| **Gnom-Hub** | RAM-Jobs, Status-/Einzeljobabfragen, Soft-Cancel und Eventproducer im untersuchten Snapshot [X1]. | Vollständige TD→Gnom→AA-Korrelation, Neustartpersistenz und realer Remote-Stopp nicht bewiesen. Einzeljob-Snapshots/Toollogs sind für reine Statussicht entbehrlich. |
| **Codex** | Im untersuchten App-Server-Protokoll existieren Thread-/Turn-/Itembezüge; im TypeScript-SDK Tool-/MCP-Status und Tokenverbrauchsfelder [X2]. | App-Server und exec-JSONL sind verschiedene Verträge. `item.completed` umfasst auch Fehler; daraus folgt keine aktuelle AA-Anbindung. Nur ausgewählte Vorgangs-/Statusbezüge, keine kompletten Outputs. |
| **Claude Code / Agent SDK** | Im vorhandenen Python-Agent-SDK-Stand sind Session-/Taskbezüge und Task-/Toolstatusfelder dokumentiert [X3]. | SDK-Felder beweisen keine aktuelle CLI-/Hook-/Connectorintegration. Terminalstatus kann als `task_updated` statt separatem Abschluss eintreffen; `killed`/`stopped` unterscheiden sich je Nachricht. Vollständige Argumente/Transkripte entfallen. |
| **Lokale Agenten / MCP / sonstige Connectoren** | TDs minimaler stdio-Server und Gnom-MCP-lite unterscheiden lokale Request-/Antwort-/Toolfehler; MCP-lite ist ausdrücklich kein vollständiger MCP-Server [T1, X1]. | Request-ID ist keine Menschen-/Sessionidentität. JSON-RPC-Ergebnis beweist nicht alle späteren Zielwirkungen. Nicht instrumentierte Terminal-, Browser- und Desktopwege bleiben unbeobachtet [K1]. |
| **Agent Authority selbst** | Phase-1-Lab-Emitter und separate modellierte Phase-2-Metadaten/Provenienz [L1–L5]. | Kein vollständiger Beobachterdienst, kein Phase-2-/Finish-/Effect-Eventstrom oder geprüfter Hinweis-/Verlustsensor. A12/A13 bleiben Beobachtungsbedarf, keine Istfunktion. |

## Widersprüche und scheinbare Widersprüche ausdrücklich erhalten

1. **Gatekeepertexte versus D-012:** eingefrorene Specs behandeln ALLOW/DENY und
   Gates. Für das Produkt gilt ausschließlich D-012; die historischen Tests werden
   dadurch weder gelöscht noch als Beobachtertests umgedeutet [K1, L3, L9].
2. **„Kein Payload/keine Parameter“ versus Geheimnisfreiheit:** Parameters werden
   nicht in Provenienz kopiert; der aktuelle Emitter übernimmt andere Felder roh
   und setzt `PUBLIC` konstant. Die datierte Prüfung belegt ein künstliches
   Metadatenleck. Die vorhandenen Exporttests prüfen keine vollständige Redaktion
   aller Feldwerte. Das ist weiterhin offen [L1, L2, K3].
3. **Alter Abschaltflagbefund versus heutiger master:** der datierte Bericht nennt
   noch aktivierendes `"0"` unter pytest. PR #18 korrigiert dies im aktuellen Lab;
   die neuen Tests behandeln explizite false-Werte. Dieser alte Teilbefund ist
   überholt, nicht das Metadatenleck. Keine Übertragung des Labfixes auf andere
   Producer behaupten [L1, K3].
4. **Graph/Quelllabel/Hash versus tatsächliche Nutzung:** dokumentierte falsche
   Nutzungs-/Kostenkanten und unabhängige Quell-/Typenums verhindern, den Graphen
   als Grant-, Nutzungs- oder Kostenbeweis zu lesen. Hash ist kein authentisierter
   Herausgeber; auch authentisierte Herkunft wäre kein Wahrheitsbeweis [K3, K2].
5. **Registryreparatur versus später Adaptereffekt:** beide Befunde können zugleich
   gelten. Die In-Process-Reparatur betrifft `submit`/Registry, nicht den späteren
   Effekt. `finish` ist hier kein getesteter Produktionsstopp/Entzug [L8, L9].
6. **Früher Binding-PASS versus Folgeprüfung:** der frühe Review verfehlte einen
   trotz DENY geschriebenen `self.decisions`-Kontrollrecord. Nachfolgendes
   `state_write` verwendete den bereits vorhandenen PUBLIC-Katalogeintrag.
   Maßgeblich ist die spätere
   dokumentierte DENY-Atomicity-Prüfung, ohne den ersten Review umzuschreiben.
   Daraus folgt kein vollständiger Herkunftsgraph oder allgemeines IFC [L5, L4].
7. **Snapshotdokument versus heutiger Code:** die Phase-1-Encapsulation-Datei nennt
   Kopien/neue Provenienzrecords; der Code teilt bewusst unveränderliche Records.
   Diese Dokumentationsabweichung bleibt benannt, ohne daraus einen nachgewiesenen
   Mutationsfehler abzuleiten [L2, L9].

Zusätzliche Zeitgrenze: `authority.requested` wird im aktuellen G3 erst mit bereits
vorliegender Entscheidung emittiert. Sein Zeitstempel ist damit kein erfasster
Anfrageeingang. Die Begriffe alleine erlauben keine Latenzmessung [L1].

## Belegregister

Lablinks beziehen sich auf Dateien des oben genannten master-Stands. Die
historischen Reviewdateien nennen jeweils zusätzlich ihren damaligen Testcommit.
Andere Werkzeuge werden nur in den unten gepinnten, bereits vorhandenen Ständen
beurteilt; deren heutigen Remote-Stand hat dieser Auftrag nicht neu geprüft.

<a id="k1"></a>**K1 – verbindliche Rolle und vorhandene Beobachterforschung.**
KI-Zentrale `96526cf99b94bfae9f6c177c6d07d2925404ecdd`:
[D-009–D-012](https://github.com/landjunge/KI-Zentralle/blob/96526cf99b94bfae9f6c177c6d07d2925404ecdd/DECISIONS.md),
[Beobachter-Recherche, insbesondere Abschnitte 3, 5, 7, 10–12](https://github.com/landjunge/KI-Zentralle/blob/96526cf99b94bfae9f6c177c6d07d2925404ecdd/docs/agent-authority/BEOBACHTER-RECHERCHE-2026-10-07.md).
Rolle ist Vorgabe; Signalauswahl und Befundmodell sind ausdrücklich Vorschläge,
kein eingeführtes Schema oder praktisch bewiesener Analysedienst.

<a id="k2"></a>**K2 – bereits recherchierte Quellen und Praxisabgleich.**
[Quellenregister](https://github.com/landjunge/KI-Zentralle/blob/96526cf99b94bfae9f6c177c6d07d2925404ecdd/docs/agent-authority/BEOBACHTER-QUELLEN-2026-10-07.md)
und [A/B/C/D-Praxisabgleich](https://github.com/landjunge/KI-Zentralle/blob/96526cf99b94bfae9f6c177c6d07d2925404ecdd/docs/agent-authority/ABGLEICH-TESTS-UND-BEOBACHTER-RECHERCHE-2026-10-07.md).
OpenTelemetry-Zeit/Sampling (R1), GenAI-Privacy/Callerperspektive (R2,
**Development**), CloudEvents 1.0.2 (R3), Trace Context (R4, gelesener
**Editor's Draft**), PROV (R5, Recommendation) und NIST-Kontrollkatalog (R6).
Diese Begriffe sind keine Pflichtframeworks, Sensorbeweise oder gesetzliche
Datenschutzerlaubnis. Die 25 Analysefälle des Abgleichs bleiben ungemessen.

<a id="k3"></a>**K3 – datierte praktische Lab-/Eventprüfung.**
[Prüfbericht am Lab `a12c3d6`, insbesondere Zeilen 67–105](https://github.com/landjunge/KI-Zentralle/blob/96526cf99b94bfae9f6c177c6d07d2925404ecdd/docs/threaddesk/tool-suite-review/agent-authority.md#L67).
Enthält ausgeführte historische Secretmuster-, Quellen-/Graph- und Testbefunde;
keine neue Ausführung dieses Auftrags. Frühere Gatekeeper-Einbindungsvorschläge
sind verworfen, der Abschaltflagbefund durch PR #18 überholt.

<a id="l1"></a>**L1 – heutiger Phase-1-Export und seine Testgrenze.**
[Emitter](../lab/authority_emit.py), [Exporttests](../tests/test_authority_emit.py),
[Abschaltflagtests](../tests/test_authority_event_flags.py).
Rohe Metadaten, konstantes `PUBLIC`, unabhängige Span-/Ereignis-IDs, keine gemeinsame
Action-ID, Exportfehler ohne Verlustmeldung. Die Tests enthalten Format-/Flag-
und Dateierzeugungsprüfungen, keine vollständige Datenbereinigung.

<a id="l2"></a>**L2 – Phase-1-Kontext und Provenienz.**
[Modelle, insbesondere `public_view`](../lab/models.py),
[Provenienz ohne Parameterkopie](../lab/provenance.py),
[Zähler über mehrere Actors / getrennte Workflows](../tests/test_cross_agent_accumulation.py).
Fake-Workflowzustand; keine allgemeine Identitäts-, Privacy- oder Langzeitgarantie.

<a id="l3"></a>**L3 – historische metadatenbasierte Übergabe.**
[eingefrorenes Experiment 02](PHASE2-EXPERIMENT-02-COMMUNICATION-GATE.md),
[Review](REVIEW-PHASE2-EXPERIMENT-02.md),
[Tests einschließlich `test_gate_does_not_receive_payload_content`](../tests/phase2/test_experiment_02.py).
PayloadStore und SecurityEnvelope sind getrennt; bekannte Runtime/Actors sind
Modellvoraussetzungen. Das historische Gate entscheidet im Lab, nicht im Produkt.

<a id="l4"></a>**L4 – gleicher Inhalt, andere Daten-/Kontrollherkunft.**
[Experiment-03-Review](REVIEW-PHASE2-EXPERIMENT-03.md),
[Test gleicher Ausgabe mit verschiedener Provenienz](../tests/phase2/test_experiment_03.py),
[Runtime-Erklärung](../lab/phase2/gated_runtime.py),
[Control-Experiment-Erklärung](../lab/phase2/experiment03_control_flow.py).
Nur modellierte `control_decide`/`created_under`; rohe `if`-Zweige unsichtbar.
Erklärungspfade sind nicht als vollständiger Herkunftsgraph belegt.

<a id="l5"></a>**L5 – Bindungsbefunde und letzte Folgeprüfung.**
[früher Binding-Review](REVIEW-VALUE-ID-BINDING.md),
[DENY-Atomicity-Folgeprüfung](REVIEW-VALUE-ID-DENY-ATOMICITY.md),
[Bindingtests](../tests/phase2/test_value_id_binding.py).
Folgeprüfung dokumentiert zweimal 145 bestandene historische Tests: `decisions`
bleibt nach DENY unverändert; nachfolgendes `state_write` ebenfalls DENY ohne
State-/Effektänderung, Transfer-Provenienzcheckpoint erhalten. Keine
kryptografische oder verteilte Quellgarantie.

<a id="l6"></a>**L6 – Ressourcenidentität.**
[FakeAdapter-Identitätsreparatur](PHASE1-ADAPTER-IDENTITY.md),
[Adapteridentitätstests](../tests/test_adapter_path_identity.py).
Lexikalische Aliasnormalisierung im FakeRepo; reale Symlinks/Mounts/Adapter nicht
dadurch bewiesen.

<a id="l7"></a>**L7 – praktische Grenzen von Namen, Verben und Zustimmung.**
[Realcase-Transferstudie, insbesondere §3.2](REAL-CASE-TRANSFER-STUDY-v1.md),
[Convergence-Ergebnisse, CB-01](CONVERGENCE-BATTERY-v1-RESULTS.md),
[Realcase-Testfälle](../tests/realcase/REAL-CASE-CATALOG-v1.md).
RC-01–05 gemessene Misses am damaligen Teststand; CB-01 Token-Reuse-Miss.
0/28 historische Gate-False-Positives sind keine gemessene AA-Warnqualität.

<a id="l8"></a>**L8 – Lifecycle ist nicht Wirkung.**
[belegtes Finish-/Späteffekt-Fallblatt](OBSERVATION-CASE-FINISH-LATE-EFFECT.md),
[Finding](FINDING-PHASE1-FINISH-ADAPTER-EFFECT-GAP.md),
[vorhandener Probe außerhalb der Standardsuite](../probes/test_finish_adapter_effect_atomicity_probe.py).
FakeAdapter-Effekt nach `finish`, synchronisiert, keine erfasste AA-Eventreplayfolge
mit erfundenen Zeiten/IDs. OOS-021 bleibt offen; hier nicht neu ausgeführt.

<a id="l9"></a>**L9 – Methode und ausdrückliche Blindstellen.**
[Forschungsmethode](RESEARCH-METHOD.md), [Threat Model](THREAT-MODEL.md),
[Out-of-Scope Debt](OUT-OF-SCOPE-DEBT.md),
[historischer Snapshotvertrag](PHASE1-STATE-ENCAPSULATION.md).
PASS ≠ SUPPORTED; falsche Anfangslabels, kompromittierte Runtime, unmodellierte
Kanäle, reale Frameworks, verteilte Ausführung und semantische Injection bleiben
unbelegt. Kein bestehender Test wird durch dieses Dokument geändert.

<a id="t1"></a>**T1 – ThreadDesk-Istcode am vorhandenen Stand**
`1de98700bbb6b14f32edde94a2fdabe7e3fa2338`:
[Handoffbezüge und Revision](https://github.com/landjunge/threaddesk/blob/1de98700bbb6b14f32edde94a2fdabe7e3fa2338/src/threaddesk/services/handoff_contract.py#L19),
[Job-/Callbackbezüge](https://github.com/landjunge/threaddesk/blob/1de98700bbb6b14f32edde94a2fdabe7e3fa2338/src/threaddesk/services/gnom_jobs.py#L45),
[Return-Inbox](https://github.com/landjunge/threaddesk/blob/1de98700bbb6b14f32edde94a2fdabe7e3fa2338/src/threaddesk/services/return_inbox.py#L48),
[lokale Actors](https://github.com/landjunge/threaddesk/blob/1de98700bbb6b14f32edde94a2fdabe7e3fa2338/src/threaddesk/services/actors.py#L58),
[Whiteboard-Kontext](https://github.com/landjunge/threaddesk/blob/1de98700bbb6b14f32edde94a2fdabe7e3fa2338/src/threaddesk/services/whiteboard.py#L83),
[Listen-/Vollabfrage](https://github.com/landjunge/threaddesk/blob/1de98700bbb6b14f32edde94a2fdabe7e3fa2338/src/threaddesk/services/mcp.py#L185),
[minimaler stdio-Server](https://github.com/landjunge/threaddesk/blob/1de98700bbb6b14f32edde94a2fdabe7e3fa2338/src/threaddesk/ui/mcp_stdio.py#L21).
`list_threads` liefert ID/Titel/Status/Änderungszeit ohne Notizen; `get_thread`
liefert zusätzliche Inhalte. Lokale Actorzuordnung ist kein kryptografischer
Principal; `delivered/unverified` keine Abnahme. Vorhandene Arbeits-/Rückgabepakete
dürfen für ihre eigenen Zwecke mehr Daten benötigen als AA.

<a id="f1"></a>**F1 – 4AllPass-Istcode und dokumentierte Grenze**
`47cc823d36f7731001a83f7fbda87d38ccc8e9b4`:
[Emitter](https://github.com/landjunge/4AllPass/blob/47cc823d36f7731001a83f7fbda87d38ccc8e9b4/backend/app/authority_emit.py#L85),
[Security-Boundary](https://github.com/landjunge/4AllPass/blob/47cc823d36f7731001a83f7fbda87d38ccc8e9b4/docs/security-boundary.md#L442).
Projektkennung ist fest `4allpass`; Workflow/Trace verwenden lokale Request-ID,
`action` ist fest `secret.read`, `capability_id` übernimmt nur erstes Scopeelement.
Envelope enthält keinen vollständigen Principal-/TTL-/Handoffbeleg. Pairingtoken
ist keine kryptografische Agentidentität; Signatur-/StandingAccess-Bibliotheken
sind laut Boundary nicht im laufenden Sidecar verdrahtet. TTL widerruft keine
bereits kopierte Providercredential. „Optional“ beschreibt Nutzung, nicht
sicheren Default: der untersuchte Emitter ist außerhalb pytest standardmäßig an.

<a id="f2"></a>**F2 – Tollgate-Istcode am vorhandenen Stand**
`d07c3ffb7513473a3de1c87bd01e9a1c9ea39c85`:
[Admission-Emitter](https://github.com/landjunge/tollgate/blob/d07c3ffb7513473a3de1c87bd01e9a1c9ea39c85/src/tollgate/authority_emit.py#L61),
[RequestContext](https://github.com/landjunge/tollgate/blob/d07c3ffb7513473a3de1c87bd01e9a1c9ea39c85/src/tollgate/gateway/context.py#L19),
[Auditdaten](https://github.com/landjunge/tollgate/blob/d07c3ffb7513473a3de1c87bd01e9a1c9ea39c85/src/tollgate/audit_log.py#L27),
[Usage/Reservierung/Schätzung](https://github.com/landjunge/tollgate/blob/d07c3ffb7513473a3de1c87bd01e9a1c9ea39c85/src/tollgate/usage_ledger.py#L160),
[Freezescope](https://github.com/landjunge/tollgate/blob/d07c3ffb7513473a3de1c87bd01e9a1c9ea39c85/src/tollgate/freeze.py#L56),
[Admission-/Systemausnahme](https://github.com/landjunge/tollgate/blob/d07c3ffb7513473a3de1c87bd01e9a1c9ea39c85/src/tollgate/gateway/admit.py#L69),
[breite MCP-Steueroberfläche](https://github.com/landjunge/tollgate/blob/d07c3ffb7513473a3de1c87bd01e9a1c9ea39c85/src/tollgate/mcp_tools.py#L234).
Prozessweiter Workflow/default und feste Projektkennung statt vollständiger
RequestContext-/Consumerbindung im Envelope; keine Beträge/Buchungsphase im
Authority-Emitter. Getrennte Usagewerte enthalten unter anderem USD-Schätzungen,
keine belegte Providerrechnung. Auditantworten können Pfade/Freitext tragen.
Toolcall-Grenzen nutzen teilweise Clienthinweise; das ist kein beobachteter
semantischer Delegationszyklus. MCP bietet auch Freeze on/off, Configpatch und
Provideraufrufe, also keine belegte reine AA-Leseverbindung.

<a id="x1"></a>**X1 – Gnom-Hub-Istcode am vorhandenen Stand**
`e5c66176fc435fb9720360d21fe6581ef1ce41a2`:
[RAM-Jobs, Status, Snapshot und Cancel](https://github.com/landjunge/gnom-hub-v1/blob/e5c66176fc435fb9720360d21fe6581ef1ce41a2/src/gnom_hub/jobs.py#L435),
[Producer und Workflowauswahl](https://github.com/landjunge/gnom-hub-v1/blob/e5c66176fc435fb9720360d21fe6581ef1ce41a2/src/gnom_hub/authority_emit.py#L46),
[Pipelineereignisse](https://github.com/landjunge/gnom-hub-v1/blob/e5c66176fc435fb9720360d21fe6581ef1ce41a2/src/gnom_hub/pipeline/dispatch.py#L167),
[MCP-lite](https://github.com/landjunge/gnom-hub-v1/blob/e5c66176fc435fb9720360d21fe6581ef1ce41a2/src/gnom_hub/plugins/mcp_protocol.py#L1).
Einzeljob liefert Snapshot/Toollog; Listenstatus braucht diese Vollinhalte nicht.
Soft-Cancel ist Wunsch bis Stufengrenze/LLM-Rückkehr/Finalisierung. Eventworkflow
kann aus TD-Paket, Run-ID oder `gnom-local` stammen; das beweist keinen aktuellen
Auftragsbezug. Erlaubte Typnamen belegen keine vollständige Ereignisabdeckung.

<a id="x2"></a>**X2 – vorhandenes Codex-Quell-/Protokollmaterial**
`b4e3726d73a34e7906715464cad4d801326f2483`:
[App-Server-Itemstart](https://github.com/openai/codex/blob/b4e3726d73a34e7906715464cad4d801326f2483/codex-rs/app-server-protocol/schema/typescript/v2/ItemStartedNotification.ts#L6),
[Itemende](https://github.com/openai/codex/blob/b4e3726d73a34e7906715464cad4d801326f2483/codex-rs/app-server-protocol/schema/typescript/v2/ItemCompletedNotification.ts#L6),
[TypeScript-SDK-Ereignisse](https://github.com/openai/codex/blob/b4e3726d73a34e7906715464cad4d801326f2483/sdk/typescript/src/events.ts#L58),
[Tool-/MCP-Inhalte](https://github.com/openai/codex/blob/b4e3726d73a34e7906715464cad4d801326f2483/sdk/typescript/src/items.ts#L47).
Protokollfelder sind Quellbelege, keine tatsächlich installierte Anschlussversion,
kein geprüfter AA-Export und kein Effekt-/Identitätsnachweis. Unterschiedliche
Codex-Verträge nicht zusammenwerfen; vollständige Befehle/Antworten/Reasoning
sind keine datensparsame Standardbeobachtung.

<a id="x3"></a>**X3 – vorhandenes Claude-Agent-SDK-Quellmaterial**
`9c69ce7aced5cdf2aa1ac86fe62e877b4962de8b`:
[Tool-/Hookfelder](https://github.com/anthropics/claude-agent-sdk-python/blob/9c69ce7aced5cdf2aa1ac86fe62e877b4962de8b/src/claude_agent_sdk/types.py#L314),
[Taskstatus](https://github.com/anthropics/claude-agent-sdk-python/blob/9c69ce7aced5cdf2aa1ac86fe62e877b4962de8b/src/claude_agent_sdk/types.py#L1169),
[terminaler Taskstatus](https://github.com/anthropics/claude-agent-sdk-python/blob/9c69ce7aced5cdf2aa1ac86fe62e877b4962de8b/src/claude_agent_sdk/types.py#L1254),
[Kosten-/Nutzungsfelder](https://github.com/anthropics/claude-agent-sdk-python/blob/9c69ce7aced5cdf2aa1ac86fe62e877b4962de8b/src/claude_agent_sdk/types.py#L1340).
Diese SDK-Sicht darf nicht als verifizierter Claude-Code-Runtimeanschluss
ausgegeben werden. Ereignisvarianten, Version und wirklich verfügbarer Export
bleiben zu prüfen; Toolinputs/Responses und Transkriptpfade sind keine benötigten
Grunddaten für A1–A6.

## Kleinste sinnvolle nächste Experimente – nicht begonnen

Dokumentprüfung: lokale Verweise und interne Anker sowie 33 gepinnte Quellenpfade
gegen vorhandene Gitobjekte geprüft; Diff auf diese Übersicht und den README-Link
begrenzt. Getrennte read-only Prüfungen im selben Projektkontext decken Labbelege,
Toolbelege und Auftragsgrenzen ab. Kein externer Audit und keine neuen App-,
Sicherheits- oder Beobachtertestläufe.

Nur Vorschläge. Vor Durchführung braucht jeder ausgewählte Versuch einen eigenen
Auftrag und eine begrenzte, eingefrorene Frage mit erwarteten Beobachtungen nach
der vorhandenen Forschungsmethode. Ausschließlich synthetische Daten; keine
Produktintegration, echte Credentials oder Reparatur eines historischen Gates.

| Versuch | Kleinster Vergleich und Messfrage | Offene Punkte / bestehende Motivation |
|---|---|---|
| **E1 Einzelne Referenz oder Effektmeldung weglassen.** | Auf Papier zwei synthetische Ablaufkarten: Effekt vor Ende / Effekt nach Lifecycle-Ende. Jeweils genau Versuch-/Generationsbezug oder Effektmeldung entfernen. Prüfen, wann ein Mensch den Zusammenhang noch eindeutig erklären kann und wann „nicht auswertbar“ nötig ist; keine bisher nicht erfassten Events als echte Probeaufzeichnung ausgeben. | A2/A5/A6/A13; [L8](#l8). Das wäre ein neuer Verständlichkeits-/Feldbedarfstest, kein ausgeführter AA-Detektortest. |
| **E2 Minimierung an der ersten Speicherstelle prüfen.** | Je ein künstlicher Sensitivitätsmarker nur in Actor, Resource, URL oder Fehlertext; Parameterausschluss allein als Gegenkontrolle. In einem separat beauftragten Fake-Versuch untersuchen, ob der Marker vor erstem Log sowie in Import, Anzeige und Hinweis erhalten bleibt. | C1/C3/C5; [L1](#l1), [K3](#k3). Keine echten Schlüssel; keine Reparatur innerhalb dieses Auftrags. |
| **E3 Projektpseudonyme und Ressourcenalias vergleichen.** | Zwei gleichnamige synthetische Agentinstanzen und zwei Aliasnamen derselben Fake-Ressource. Klartext gegen konsistente projektbezogene Referenzen und einen Referenzwechsel vergleichen: nötige Zuordnung erhalten, falsche Zusammenführung sichtbar? Keine neue Pseudonymisierungstechnik implementieren. | A2/A3/A7; [L2](#l2), [L6](#l6). Nutzen/Verknüpfbarkeit beider Varianten offen. |
| **E4 Drei missverständliche Statusmeldungen.** | Je eine synthetische Karte „Zugang abgelehnt“, „Budgetcheck erfolgreich“ und „Cancel angefragt“, jeweils ohne Nutzungs-/Buchungs-/Vollzugsbeleg; positive Vergleichskarte mit explizitem Beleg. Messen, ob Leser die unbelegte Wirkung erkennen, ohne Rohpayload. | A6/A8/A9/B6; [K3](#k3), [F1](#f1), [F2](#f2), [X1](#x1). Fehlende Bestätigung darf nicht als bewiesener Verstoß gewertet werden. |
| **E5 Zeit-/Lieferqualität und Sichtlücken.** | Dieselben wenigen synthetischen Meldungen in vertauschter Empfangsfolge, einmal dupliziert und einmal mit fehlender Quellzeit/Endmeldung. Bekannte Reihenfolge gegen unbekannte vergleichen; prüfen, welche Aussagen noch zulässig sind und ob Nichtbeobachtung sichtbar bleibt. | A1/A5/A12; [L1](#l1), [K2](#k2). Keine globale Ordnung aus Eingangszeit oder Hash ableiten. |
| **E6 Herkunft ohne Inhalt.** | Die vorhandenen Exp03-Fälle mit gleicher Ausgabe als dokumentierte Grundlage nehmen; synthetische Beschreibung einmal mit und einmal ohne Kontrollabhängigkeit/Labelherkunft zeigen. Prüfen, ob nur mit vorhandener Herkunft die modellierte Unterscheidung erklärbar ist. | A11/B4/C3; [L3](#l3), [L4](#l4). Kein Test roher `if`-Erkennung oder semantischer DLP; kein vollständiger Herkunftsgraph behaupten. |
| **E7 Sichtumfang eines abgeleiteten Hinweises.** | Zwei fiktive Projekte mit unterschiedlich zulässiger Lesersicht auf Papier; ein Hinweis nutzt je eine Quellreferenz aus beiden. Prüfen, ob der Hinweis selbst die fremde Projektzuordnung verrät und welche Information entfallen muss. | A13/C6/C7; [K1](#k1). Ein Papiervergleich beweist keine technisch sichere Zugriffstrennung. |

**Nächster kleinster Schritt wäre E1 als separat beauftragter Feldbedarfstest.
Dieser Auftrag endet hier: STOPP. Keine Experimente ausgeführt, keine Implementierung
begonnen und kein Folgeauftrag übernommen.**
