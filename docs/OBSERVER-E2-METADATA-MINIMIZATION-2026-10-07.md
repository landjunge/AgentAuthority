# E2 – Metadaten in Agent Authoritys eigenen Speicher- und Exportpfaden

**Vorabprotokoll, 7. Oktober 2026.** Daniels Auftrag „e2 wenn fertig push und
commit und link“ und seine anschließende Korrektur begrenzen diesen Versuch auf
**Agent Authority als eigenständigen Beobachter / Monitor / Analyseebene**.
Keine ThreadDesk-Anbindung und keine Prüfung anderer Tools. Der vorher vorbereitete
Entwurf mit einem ThreadDesk-Importpfad wurde vor Freeze und Versuchsausführung
verworfen; daraus wurden keine Messergebnisse übernommen.

E2 aus der [Informationsgrenzen-Recherche](OBSERVER-INFORMATION-BOUNDARIES-2026-10-07.md)
motiviert die Prüfung, legt aber keine Integration fest. D-012 gilt: keine
Produktfreigaben, Rechtevergabe oder Eingriffe. Historische Labentscheidungen
bleiben Testdaten innerhalb ihres damaligen Umfangs.

## Basis und Umfang

- Arbeitsbasis einschließlich E1: `b2bb13603cbf88f89f40d07b886cc1781196e07b`.
- Abgerufener Lab-`master`: `ef2400fa5fad3c4ff051928b78fcb3093bb23453`.
  Die hier benutzten Labfunktionen und bestehenden Tests sind gegenüber dieser
  Basis unverändert. Die früheren Dokumentationsversuche liegen zusätzlich auf
  dem Arbeitsbranch; der Versuch ändert keinen Produktcode.
- KI-Zentrale: `96526cf99b94bfae9f6c177c6d07d2925404ecdd`; unverändert.
- Ausschließlich neue künstliche Daten in einem eigenen temporären Verzeichnis.
  Keine vorhandenen Logs, Datenbanken, Zugangsdaten oder Konfigurationsdateien lesen.
  Die URL wird nur als Zeichenfolge serialisiert, nicht aufgerufen.

Auf diesem `master` sind für diesen Versuch historische Labzustände, Provenienz
und der JSONL-Serializer vorhanden. Daraus wird **keine bereits implementierte
produktive Monitor-Eingangs-, Anzeige- oder Warnpipeline** abgeleitet.
Die fehlenden Anschlussbelege werden ausdrücklich offen gehalten.

Nach der [Forschungsmethode](RESEARCH-METHOD.md) werden Frage, Erwartungen,
Eingaben und Messgrenzen vor der Ausführung committed und gepusht. Ergebnisse
werden später angehängt; dieser Vorabteil bleibt bytegleich. Ein temporäres
Hilfsskript ruft ausschließlich bestehende Funktionen dieses Repositories auf.
Kein Produktcode und kein bestehender Test wird geändert. Kein Experiment 04
und kein weiterer E-Versuch.

## Frage und eingefrorene Hypothesen

Welche künstlichen Metadatenmarker bleiben in den vorhandenen eigenen Labdaten
und in ihrer ersten JSONL-Persistenz erhalten? Was schließt der bekannte
Parameterausschluss tatsächlich aus?

- **H1:** Actor, Resource, URL im Resource und Fehlertext im `reason_code` bleiben
  bei beiden Markerklassen im ersten Ereignislog erhalten. Auch der ausdrücklich
  secretähnliche Dummy wird auf diesem Exportpfad nicht automatisch entfernt.
- **H2:** Ein Marker ausschließlich in `parameters.e2_probe` erscheint bei
  `file.read` weder in den beiden exportierten Ereignissen noch in der
  untersuchten eigenen Provenienz und `public_view()` des Workflowzustands.
  Das gilt nur für diese Aktion und diese Speicher, nicht für alle Labaktionen.
- **H3:** Actor bleibt bei `file.read` in der Provenienz und in den Zustandsagenten
  erhalten. Resource und URL bleiben in der Provenienz; `touched_paths` bleibt
  für diese Leseaktion leer. Das ist eine aktionsabhängige Zustandsprojektion,
  keine Redaktion des Ressourcenwertes vor dem Log.
- **H4:** Die vier Metadatenträger in beiden Markerklassen erhalten trotz ihres Markers ein konstantes
  `PUBLIC`-Label und gültige Eventhashes. Label und Hash belegen keine Bereinigung.

Abweichungen werden als Ergebnis festgehalten, nicht durch geänderte Marker
passend gemacht. Eine Hypothesenbewertung betrifft nur diese Daten und
bestehenden Funktionen; sie belegt weder allgemeine DLP noch Warnqualität oder
die Eignung sämtlicher Felder als späterer Monitorinput.

## Zehn eingefrorene Fälle

Je Fall genau ein markierter Träger, ein neuer Labzustand und eine neue JSONL.
Die zwei Ereignisse pro Export sind keine zwei unabhängigen Fälle.

| Fall | Klasse | Träger | Exakter Marker |
|---|---|---|---|
| C1 | neutraler Canary | Actor | `E2_PRIVATE_CANARY_ACTOR_01` |
| C2 | neutraler Canary | Resource | `E2_PRIVATE_CANARY_RESOURCE_02` |
| C3 | neutraler Canary | URL im Resource | `E2_PRIVATE_CANARY_URL_03` |
| C4 | neutraler Canary | Fehlertext im `reason_code` | `E2_PRIVATE_CANARY_REASON_04` |
| C5 | neutraler Canary | Parameters, Gegenkontrolle | `E2_PRIVATE_CANARY_PARAMETERS_05` |
| S1 | secretähnlicher Dummy | Actor | `api_key=E2_FAKE_NOT_A_CREDENTIAL_ACTOR_06` |
| S2 | secretähnlicher Dummy | Resource | `api_key=E2_FAKE_NOT_A_CREDENTIAL_RESOURCE_07` |
| S3 | secretähnlicher Dummy | URL im Resource | `api_key=E2_FAKE_NOT_A_CREDENTIAL_URL_08` |
| S4 | secretähnlicher Dummy | Fehlertext im `reason_code` | `api_key=E2_FAKE_NOT_A_CREDENTIAL_REASON_09` |
| S5 | secretähnlicher Dummy | Parameters, Gegenkontrolle | `api_key=E2_FAKE_NOT_A_CREDENTIAL_PARAMETERS_10` |

Alle Marker sind vollständig erfunden und nicht einlösbar. „Private“ bezeichnet
eine künstliche Sensitivität, keine vertraulichen Nutzerdaten. Die zweite Klasse
prüft nur den Transport eines offensichtlich als Dummy benannten Schlüsseltexts.
Sie ist keine echte Zugangsinformation und kein Erfolgsnachweis für Secret-Erkennung.

Standardrequest: Actor `E2-Agent`, Aktion `file.read`, Resource `e2/object.txt`,
Parameters `{}`, Workflow `wf-e2-<Fall>`. Actor-/Resource-Fälle ersetzen nur das
jeweilige Feld. URL-Fälle setzen Resource auf
`https://example.invalid/object?note=<Marker>`; kein eigenes URL-Feld wird erfunden.
Parameterfälle setzen ausschließlich `parameters.e2_probe` auf den Marker.
Diese acht Fälle benutzen `Lab().submit(request)`; keine echte Datei wird gelesen.

C4/S4 benutzen denselben Standardrequest und ausschließlich den vorhandenen
Serializer `emit_decision(request, Decision(False, "synthetic-error:<Marker>", []))`.
Das ist ein synthetischer Fehlertext am Serializer, **kein von Lab.submit
ermittelter Entscheidungsgrund**. Die bestehende Zuordnung `deny_reason` zu
`reason_code` wird gemessen. Für diese zwei Serializer-Fixtures wird kein
Workflowzustand oder Provenienzlauf erfunden.

## Messstellen und Bewertung

1. **Eigene RAM-Daten:** Nach `Lab.submit` nur `Lab.state()` dieses künstlichen
   Workflows betrachten: `public_view()`, `touched_paths`, Agenten und seine
   Provenienz. Exakte Markerpositionen dokumentieren. Das sind Labdaten, kein
   erfundenes öffentliches Monitor-Datenmodell. Der Eingaberequest selbst trägt
   selbstverständlich den Marker; dies ist keine zusätzliche Minimierungsmessung.
2. **Erste Persistenz dieses Exportpfades:** Export ausdrücklich mit
   `LAB_AUTHORITY_EVENTS=1` und frischem `LAB_AUTHORITY_EVENTS_PATH` aktivieren.
   Existenz, zwei JSONL-Ereignisse, exakte Markerpositionen, `PUBLIC`, Hashwerte
   und interne Verkettung prüfen. Fehlende Ausgabe bedeutet Messfehler, nicht
   nachgewiesene Redaktion. „Erste Speicherstelle“ meint ausschließlich die
   erste Persistenz des untersuchten Exports, nicht alle Speichervorgänge im System.
3. **Nachprüfbare JSON-Repräsentation:** Nur diese neue JSONL mit dem
   Python-Standardparser lesen und Markerpositionen erfassen. Das bestätigt
   den gespeicherten Inhalt; es ist **kein vorhandener produktiver AA-Import**.
   Selbst die Gegenkontrolle wird auf vollständige Werte geprüft, nicht bloß
   auf die Abwesenheit eines Top-Level-Schlüssels namens `secret` oder `api_key`.
4. **Nicht belegte Anschlussstellen:** Eigene produktive Monitoraufnahme,
   Nutzeranzeige und abgeleitete Warnung aus diesen Ereignissen bleiben
   **NICHT GETESTET / in der geprüften Basis nicht als verbundener Pfad belegt**.
   Dafür wird kein Fremdtool herangezogen und kein Ersatz implementiert.

Werte: **erhalten**, **nicht enthalten**, **nicht anwendbar** oder
**nicht getestet / nicht belegt**. Kein fehlender Marker in einer Projektion
beweist seine Abwesenheit in allen früheren Daten. Keine historischen
Gate-Akzeptanzkriterien werden verändert oder neu bewertet. Prüfkonformität
dieses E2-Protokolls und Hypothesenbewertung bleiben getrennt.

## Abnahme und Ende dieses Auftrags

Vollständigkeit der zehn Fälle, Reproduktionsskript und Resultate dokumentieren;
Quellbezüge sowie unveränderte Vorabteilsbytes prüfen. Bestehende Exportchecks
und die unveränderte Lab-Standardsuite gemäß Forschungsmethode ausführen; ihre
Reichweite und vorhandene Ausschlüsse nennen. Getrennte read-only Prüfung im
selben Projektkontext, kein externer Audit. Keine Tests anderer Tools.

Danach Ergebnis committen, pushen und Remote-Commit bestätigen. **STOPP:** keine
Filterreparatur, Produktfunktion, Architekturentscheidung oder automatische E3-Arbeit.

<!-- E2-FROZEN-PROTOCOL-END -->
