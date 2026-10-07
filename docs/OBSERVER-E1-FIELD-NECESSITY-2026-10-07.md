# E1 – welche Angaben einen Ablauf nachvollziehbar machen

**Vorabprotokoll, 7. Oktober 2026.** Auftrag: Daniels „e1“ wählt ausschließlich
E1 aus der [Forschungsübersicht](OBSERVER-INFORMATION-BOUNDARIES-2026-10-07.md).
Arbeitsbasis: `ba20763f6acf9bcfeb516318590f3b13e3445b37`; abgerufener `master`
weiterhin `ef2400fa5fad3c4ff051928b78fcb3093bb23453`. KI-Zentrale D-012 gilt:
Agent Authority beobachtet und analysiert, erteilt keine Freigabe und stoppt nichts.

Nach der [Forschungsmethode](RESEARCH-METHOD.md) wird dieses Protokoll
einschließlich der Karten vor ihrer Bewertung committed
und gepusht. Anschließend werden nur Ergebnisse angehängt; die Vorabteile bleiben
unverändert. Kein Experiment 04, keine Codeänderung, kein neuer Sensor und keine
Ausführung des historischen Finish-Probes oder anderer Labtests.

## Frage und vorab festgelegte Erwartungen

Welche Aussagen über einen gemeldeten Schreibeffekt gegenüber dem Lifecycle-Ende
eines bestimmten Laufs lassen sich nach Weglassen seiner Laufzuordnung oder der
Effektmeldung noch aus den sichtbaren Angaben begründen?

- **H1:** Mit expliziter gleicher Laufzuordnung, Effektmeldung und gesetzter
  Ereignisordnung lassen sich die beiden Papiersituationen unterscheiden.
- **H2:** Ohne Laufzuordnung der Effektmeldung ist bei zwei möglichen Läufen die
  Zuordnung zum beendeten Lauf offen. Die Reihenfolge der sichtbaren Meldungen
  kann gleichwohl erkennbar bleiben.
- **H3:** Ohne Effektmeldung lassen sich die beiden konstruierten Situationen
  nicht unterscheiden. Fehlende Meldung bedeutet nicht „kein Effekt“.

Das sind vorab prüfbare Erwartungen innerhalb dieser Karten, keine Aussage über
eine vorhandene AA-Erkennungsfunktion. Eine abweichende begründete Bewertung wird
festgehalten; Karten und Kriterien werden nicht passend gemacht.

## Voraussetzungen und Belegregeln

Alle Symbole und Meldungen sind **frei konstruierte Papierdaten**. Sie ersetzen
keine fehlenden IDs oder Zeiten des [historischen Finish-Falls](OBSERVATION-CASE-FINISH-LATE-EFFECT.md).
Die Vorher-Situation ist eine neue synthetische Kontrolle; die Nachher-Situation
ist durch das Finding motiviert, aber keine Aufzeichnung oder Wiederholung davon.

- Betrachtet wird `v-a / g-1`. Ein zweiter möglicher Lauf `v-b / g-2` benutzt
  denselben Workflownamen `w-papier` und dieselbe Ressourcenreferenz `obj-r`.
  Weder Workflowname noch Ressource noch Zeitnähe erlauben eine eindeutige Zuordnung.
- **Laufbezug** ist hier eine einzige Informationsgruppe, nicht zwei einzeln
  getestete Pflichtfelder. Eine eindeutig gebundene Versuchsreferenz oder ein
  anderer belastbarer Zusammenhang könnte sie ersetzen; Generation ist nicht
  pauschal zusätzlich erforderlich. Es wird kein Produktschema festgelegt.
- **Ordnung** bezeichnet eine für den Papierversuch gesetzte Reihenfolge des
  Ereigniseintritts. Die Zahlen sind keine Zeitstempel, Empfangszeiten oder
  lückenlose Sequenz. Eine fehlende Zahl verrät kein fehlendes Ereignis.
- Quellenzuverlässigkeit und die Bedeutung „Ziel meldet sichtbare Schreibwirkung“
  sind für diese Übung gesetzt. Diese Voraussetzungen sind im realen System
  gerade nicht durch die Übung bewiesen.
- „Cleanup beendet“ beschreibt Lifecycle-Aufräumen dieses Laufs, keinen
  Executor-/Remote-Stopp, Widerruf oder Nachweis inhaltlichen Erfolgs.
- Nur sichtbare Angaben der jeweiligen Karte zählen. Keine Zuordnung über
  Kartennamen, Schwesterkarten oder vermutete Ereignisse. Die vollständige
  Vorher-Karte schließt weitere spätere Effekte nicht aus.

## Bewertung – vorab festgelegte drei Fragen

Für jede Karte zuerst eine eigene Antwort mit Begründung festhalten:

1. **Effekt:** Gibt es eine sichtbare Meldung über eine Schreibwirkung?
2. **Zuordnung:** Ist diese Meldung eindeutig `v-a / g-1` zugeordnet?
3. **Laufreihenfolge:** Liegt die so zugeordnete Wirkung vor oder nach dessen
   Cleanup? Falls Zuordnung oder Effektbeleg fehlt: nicht bestimmbar. Eine
   schwächere Aussage nur über sichtbare Meldungsreihenfolge gesondert nennen.

Antworten: Effekt **gemeldet / unbekannt**; Zuordnung **eindeutig / offen /
nicht prüfbar**; Laufreihenfolge **vor / nach / nicht bestimmbar**.
„Kein Effekt“ und „unzulässige Fortsetzung“ sind aus diesen Karten nicht belegt.

K1–K4 werden vor K5–K6 beurteilt, erste Antworten danach nicht umgeschrieben.
Die Erstvorlage im getrennten KI-Kontext enthält ausschließlich Voraussetzungen,
Belegregeln, Fragen und K1–K4. Hypothesen, vollständige Karten, Zuordnungskontrollen
und vorangegangene Umsetzungskonversation werden nicht mitgegeben. Erst nach
gesicherter Erstantwort folgt eine separate Vorlage mit K5–K6. Es ist keine externe
Prüfung, keine Menschenstudie und keine Messung von Bedienbarkeit/Warnqualität.

## Synthetische Karten – zunächst K1 bis K4

Die Quellenbezeichnungen sind Papierrollen. Keine Ausführungssysteme wurden für
diese Karten angefragt.
Einreichungsmeldungen von `Ausführer` belegen hier keine Quellfreigabe.

### K1

| Ordnung | Quelle | Sichtbare Meldung | Workflow / Ressource | Laufbezug |
|---|---|---|---|---|
| 5 | Ausführer | Einreichung gemeldet | w-papier / obj-r | v-b / g-2 |
| 10 | Ausführer | Einreichung gemeldet | w-papier / obj-r | v-a / g-1 |
| 30 | Lifecycle | Cleanup beendet | w-papier / obj-r | v-a / g-1 |
| 40 | Ziel | Schreibwirkung sichtbar gemeldet | w-papier / obj-r | unbekannt |

### K2

| Ordnung | Quelle | Sichtbare Meldung | Workflow / Ressource | Laufbezug |
|---|---|---|---|---|
| 5 | Ausführer | Einreichung gemeldet | w-papier / obj-r | v-b / g-2 |
| 10 | Ausführer | Einreichung gemeldet | w-papier / obj-r | v-a / g-1 |
| 20 | Ziel | Schreibwirkung sichtbar gemeldet | w-papier / obj-r | unbekannt |
| 30 | Lifecycle | Cleanup beendet | w-papier / obj-r | v-a / g-1 |

### K3

| Ordnung | Quelle | Sichtbare Meldung | Workflow / Ressource | Laufbezug |
|---|---|---|---|---|
| 5 | Ausführer | Einreichung gemeldet | w-papier / obj-r | v-b / g-2 |
| 10 | Ausführer | Einreichung gemeldet | w-papier / obj-r | v-a / g-1 |
| 30 | Lifecycle | Cleanup beendet | w-papier / obj-r | v-a / g-1 |

### K4

| Ordnung | Quelle | Sichtbare Meldung | Workflow / Ressource | Laufbezug |
|---|---|---|---|---|
| 5 | Ausführer | Einreichung gemeldet | w-papier / obj-r | v-b / g-2 |
| 10 | Ausführer | Einreichung gemeldet | w-papier / obj-r | v-a / g-1 |
| 30 | Lifecycle | Cleanup beendet | w-papier / obj-r | v-a / g-1 |

## Vollständige Vergleichskarten – erst danach K5 und K6

### K5

| Ordnung | Quelle | Sichtbare Meldung | Workflow / Ressource | Laufbezug |
|---|---|---|---|---|
| 5 | Ausführer | Einreichung gemeldet | w-papier / obj-r | v-b / g-2 |
| 10 | Ausführer | Einreichung gemeldet | w-papier / obj-r | v-a / g-1 |
| 20 | Ziel | Schreibwirkung sichtbar gemeldet | w-papier / obj-r | v-a / g-1 |
| 30 | Lifecycle | Cleanup beendet | w-papier / obj-r | v-a / g-1 |

### K6

| Ordnung | Quelle | Sichtbare Meldung | Workflow / Ressource | Laufbezug |
|---|---|---|---|---|
| 5 | Ausführer | Einreichung gemeldet | w-papier / obj-r | v-b / g-2 |
| 10 | Ausführer | Einreichung gemeldet | w-papier / obj-r | v-a / g-1 |
| 30 | Lifecycle | Cleanup beendet | w-papier / obj-r | v-a / g-1 |
| 40 | Ziel | Schreibwirkung sichtbar gemeldet | w-papier / obj-r | v-a / g-1 |

## Vorab festgelegte Dokumentkontrollen und Auswertungsgrenze

- K1 ist K6 mit ausschließlich entfernter Laufzuordnung der Effektmeldung;
  K2 entsprechend K5. Alle anderen Meldungsfelder bleiben identisch.
- K3 entsteht aus K6, K4 aus K5 ausschließlich durch Entfernen der Effektmeldung.
  Die sichtbaren Meldungszeilen von K3 und K4 sind dadurch identisch.
- Beurteilung ausschließlich auf Papier, keine Parser-/Detektorimplementierung,
  kein JSONL-Replay und keine Lab-/App-/Sicherheitstests.
- Codekonformität (Forschungsmethode Achse A) ist hier **nicht untersucht**.
  Dokumentprotokolltreue und die Hypothesen H1–H3 werden separat beurteilt.
- Möglicher Erkenntnisgewinn ist die begründete Grenze dieser Angaben. Keine
  reale Datenverfügbarkeit, Echtheit, Zeitqualität, Sicherheit oder menschliche
  Verständlichkeit wird damit nachgewiesen.
- E1 endet mit Ergebnis, Grenzen, Belegprüfung, Commit und Push. Danach **STOPP**.
  E2–E7 und jede Implementierung bleiben unbeauftragt.

<!-- E1-FROZEN-PROTOCOL-END -->

## Ergebnis – nach dem Vorab-Freeze ergänzt

Vorab-Freeze: Commit `d8d190ca500f88ab3d7fa44633bab0e0f07c4828`, vor der Bewertung
nach `origin/docs/observer-e1-field-necessity-2026-10-07` gepusht und Remote-Commit
bestätigt. Der vorstehende Protokollteil bleibt unverändert.

### Erstantwort K1–K4

Prüfung in einem getrennten KI-Kontext, ohne die Hypothesen, K5/K6, die
Zuordnungskontrollen oder die vorherige Konversation. Der Prüfer las ausschließlich
den im Vorabprotokoll festgelegten Ausschnitt aus dem Freeze-Commit.
Die folgende Antwort wird vor Vorlage der vollständigen Karten gesichert.

| Karte | Effektmeldung | Zuordnung | Laufreihenfolge | Begründung und schwächere Aussage |
|---|---|---|---|---|
| K1 | gemeldet | offen | nicht bestimmbar | Die Zielmeldung nennt keinen Laufbezug; Workflow und Ressource sind nicht eindeutig. Sichtbar liegt die Effektmeldung mit Ordnung 40 nach der Cleanup-Meldung für `v-a / g-1` mit Ordnung 30. |
| K2 | gemeldet | offen | nicht bestimmbar | Die Zielmeldung nennt keinen Laufbezug; Workflow und Ressource sind nicht eindeutig. Sichtbar liegt die Effektmeldung mit Ordnung 20 vor der Cleanup-Meldung für `v-a / g-1` mit Ordnung 30. |
| K3 | unbekannt | nicht prüfbar | nicht bestimmbar | Keine Schreibwirkungsmeldung sichtbar. Die Einreichungsmeldungen liegen vor der Cleanup-Meldung; eine Reihenfolge zwischen Effektmeldung und Cleanup ist nicht feststellbar. |
| K4 | unbekannt | nicht prüfbar | nicht bestimmbar | Keine Schreibwirkungsmeldung sichtbar. Die Einreichungsmeldungen liegen vor der Cleanup-Meldung; eine Reihenfolge zwischen Effektmeldung und Cleanup ist nicht feststellbar. |
