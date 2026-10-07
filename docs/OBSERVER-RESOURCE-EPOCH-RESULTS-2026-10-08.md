# Ressourcenidentität über einen Epochenwechsel: isolierter Papiervergleich

8. Oktober 2026, Berichtsdatum Europe/Berlin. **SUPPORTED IN THIS TEST.**
Genau drei künstliche Karten, drei getrennte KI-Leserkontexte, je eine
Erstantwort: **R1 UNBEKANNT, R2 DIESELBE, R3 VERSCHIEDEN.** Alle drei
Einordnungen und ihre sichtbaren Begründungen sind KORREKT; null FALSCH,
null UNBEURTEILBAR. Keine Identitätsableitung aus Anzeigenamen oder Aliasen.

Eine ausdrücklich gültig gesetzte Ressourcenbeziehung zwischen den beiden
benannten Referenzen/Epochen trägt in diesem isolierten Vergleich die Aussage
„dieselbe“ beziehungsweise „verschiedene“. Ohne diese Information bleibt
beides offen. Das untersucht Informationsgehalt, keine reale Ressourcenidentität
und keine implementierte Fähigkeit von Agent Authority.

## 1. Ausgangspunkt und eingefrorene Stände

| Stand | Vollständiger Commit-SHA |
|---|---|
| Beauftragter Ausgangsstand | `c9abf753b5a3060a630ec6b4f19d6de3b9ca610a` |
| Vertrag, genau drei Karten, drei Einzelvorlagen und Erwartungen vor Bewertung | `fccedf01896c7447c7c35527de7c8916983782f2` |
| Unveränderte Leserantworten samt Hashcheckpoint vor Vergleich | `fab154c93cf00f245731a27bc5afe30a7a9e0bf5` |

Branch: `research/observer-resource-epoch-2026-10-08`. Vertrags- und
Antwortcheckpoint jeweils committed, gepusht und per `git ls-remote` mit
identischem vollständigem Remote-SHA bestätigt, bevor der jeweilige nächste
Schritt begann. Der [Vorabvertrag](OBSERVER-RESOURCE-EPOCH-CONTRACT-2026-10-08.md)
und seine Hypothesen wurden nicht geändert.

Alle sechs vorgeschriebenen Quellen wurden vor Änderungen vollständig gelesen:
[Konsolidierung](OBSERVER-RESEARCH-CONSOLIDATION-E1-E7-2026-10-07.md),
[E3–E7-Bericht](OBSERVER-E3-E7-2026-10-07.md),
[alle historischen Karten](OBSERVER-E3-E7-CARDS-2026-10-07.json),
[beide vollständigen Antwortphasen](OBSERVER-E3-E7-RESPONSES-2026-10-07.jsonl),
[Methodik](RESEARCH-METHOD.md) und
[Finish-Minimalpfad-Ergebnis](OBSERVER-FINISH-MINIMAL-PATH-RESULTS-2026-10-08.md).

K14 bindet nur den Actor über die Epochen. Seine Ressourcenstabilität war,
anders als in K02, nicht ausdrücklich gesetzt; daher war der alte
Ressourcenvergleich nicht sauber isoliert. **Historisches K14 bleibt
INCONCLUSIVE.** Dieser neue Versuch übernimmt daraus keine fehlende Bindung
und verändert weder die alte Karte noch ihre Antwort oder Bewertung.

## 2. Design, exakte Karten und Isolationsprüfung

H1/H2/H3 und die [Erwartungen](observer-resource-epoch/2026-10-08/expectations.json)
standen vor Bewertung fest: ohne Ressourcenbindung UNBEKANNT; mit gültiger
Gleichheitsbindung DIESELBE; mit gültigem Verschiedenheitsbeleg VERSCHIEDEN.
Keine Änderung nach Ergebnis und keine Wiederholung günstiger Antworten.

Alle gemeinsamen Angaben sind gleich: Projekt p-a, zwei geordnete Epochen,
vorab ausdrücklich gebundene gleiche Actorinstanz, zwei Meldungen, Aktionsart,
Ressourcentyp, beide Referenzen, Anzeigenamen und Aliase. In keiner Karte sind
zusätzliche Rollen oder sonstige Kontextinformationen enthalten. Namen und
Aliase sind ausdrücklich nicht eindeutig. Alle Angaben sind künstlich.

Mechanisch vor Freeze und nach Vergleich geprüft: Nach Entfernung ausschließlich
von `resource_binding` sind alle drei JSON-Objekte identisch. R2/R3 unterscheiden
sich innerhalb der Bindung nur durch deren relation-Wert. Es gibt unverändert
zwei identische Meldungen je Karte. Die Bindung ist eine separate gesetzte
Papieraussage, keine zusätzliche Aktionsmeldung. Die Actorfrage ist ausgeschaltet.

Die folgenden Blöcke enthalten die vollständigen eingefrorenen Karten; die
verlinkten Dateien sind die maßgeblichen Originalbytes. JSON-Schlüssel und
Referenztexte sind nur die Darstellung dieses Papiervergleichs, kein neues
Observerdatenmodell und keine vorgeschriebene zukünftige ID-Struktur.

### R1

[Originalkarte R1](observer-resource-epoch/2026-10-08/cards/R1.json)

```json
{
  "premises": [
    "Alle Angaben sind künstliche Papierdaten; keine realen Dateien, Accounts, Agentidentitäten oder Sensoraufzeichnungen.",
    "Jede Ressourcenreferenz bezeichnet innerhalb ihrer jeweiligen Epoche eine Ressource.",
    "Ressourcenanzeigenamen und Aliase sind nicht eindeutig. Gleicher Text oder gleicher Anzeigename beweist keine Ressourcenidentität.",
    "Epoche 1 liegt vor Epoche 2. Beide Meldungen betreffen dieselbe Aktionsart und denselben Ressourcentyp.",
    "Ausdrücklich als gültig bezeichnete Bindungen gelten innerhalb dieser Papierkarte und des Projekts p-a. Ihre reale Quellechtheit ist nicht geprüft.",
    "Es gibt ausschließlich die hier sichtbaren Informationen. Keine Zusammenhänge aus anderen Karten ergänzen."
  ],
  "project": "p-a",
  "actor_binding": {
    "old_epoch": 1,
    "old_ref": "actor-alt",
    "new_epoch": 2,
    "new_ref": "actor-neu",
    "relation": "same_instance",
    "valid": true
  },
  "messages": [
    {
      "epoch": 1,
      "actor_ref": "actor-alt",
      "action_type": "Beobachtung",
      "resource_type": "künstliches Objekt",
      "resource_ref": "ref-alt",
      "resource_display_name": "Objekt",
      "resource_alias": "Alias"
    },
    {
      "epoch": 2,
      "actor_ref": "actor-neu",
      "action_type": "Beobachtung",
      "resource_type": "künstliches Objekt",
      "resource_ref": "ref-neu",
      "resource_display_name": "Objekt",
      "resource_alias": "Alias"
    }
  ],
  "resource_binding": null
}
```

### R2

[Originalkarte R2](observer-resource-epoch/2026-10-08/cards/R2.json)

```json
{
  "premises": [
    "Alle Angaben sind künstliche Papierdaten; keine realen Dateien, Accounts, Agentidentitäten oder Sensoraufzeichnungen.",
    "Jede Ressourcenreferenz bezeichnet innerhalb ihrer jeweiligen Epoche eine Ressource.",
    "Ressourcenanzeigenamen und Aliase sind nicht eindeutig. Gleicher Text oder gleicher Anzeigename beweist keine Ressourcenidentität.",
    "Epoche 1 liegt vor Epoche 2. Beide Meldungen betreffen dieselbe Aktionsart und denselben Ressourcentyp.",
    "Ausdrücklich als gültig bezeichnete Bindungen gelten innerhalb dieser Papierkarte und des Projekts p-a. Ihre reale Quellechtheit ist nicht geprüft.",
    "Es gibt ausschließlich die hier sichtbaren Informationen. Keine Zusammenhänge aus anderen Karten ergänzen."
  ],
  "project": "p-a",
  "actor_binding": {
    "old_epoch": 1,
    "old_ref": "actor-alt",
    "new_epoch": 2,
    "new_ref": "actor-neu",
    "relation": "same_instance",
    "valid": true
  },
  "messages": [
    {
      "epoch": 1,
      "actor_ref": "actor-alt",
      "action_type": "Beobachtung",
      "resource_type": "künstliches Objekt",
      "resource_ref": "ref-alt",
      "resource_display_name": "Objekt",
      "resource_alias": "Alias"
    },
    {
      "epoch": 2,
      "actor_ref": "actor-neu",
      "action_type": "Beobachtung",
      "resource_type": "künstliches Objekt",
      "resource_ref": "ref-neu",
      "resource_display_name": "Objekt",
      "resource_alias": "Alias"
    }
  ],
  "resource_binding": {
    "old_epoch": 1,
    "old_ref": "ref-alt",
    "new_epoch": 2,
    "new_ref": "ref-neu",
    "relation": "same_resource",
    "valid": true
  }
}
```

### R3

[Originalkarte R3](observer-resource-epoch/2026-10-08/cards/R3.json)

```json
{
  "premises": [
    "Alle Angaben sind künstliche Papierdaten; keine realen Dateien, Accounts, Agentidentitäten oder Sensoraufzeichnungen.",
    "Jede Ressourcenreferenz bezeichnet innerhalb ihrer jeweiligen Epoche eine Ressource.",
    "Ressourcenanzeigenamen und Aliase sind nicht eindeutig. Gleicher Text oder gleicher Anzeigename beweist keine Ressourcenidentität.",
    "Epoche 1 liegt vor Epoche 2. Beide Meldungen betreffen dieselbe Aktionsart und denselben Ressourcentyp.",
    "Ausdrücklich als gültig bezeichnete Bindungen gelten innerhalb dieser Papierkarte und des Projekts p-a. Ihre reale Quellechtheit ist nicht geprüft.",
    "Es gibt ausschließlich die hier sichtbaren Informationen. Keine Zusammenhänge aus anderen Karten ergänzen."
  ],
  "project": "p-a",
  "actor_binding": {
    "old_epoch": 1,
    "old_ref": "actor-alt",
    "new_epoch": 2,
    "new_ref": "actor-neu",
    "relation": "same_instance",
    "valid": true
  },
  "messages": [
    {
      "epoch": 1,
      "actor_ref": "actor-alt",
      "action_type": "Beobachtung",
      "resource_type": "künstliches Objekt",
      "resource_ref": "ref-alt",
      "resource_display_name": "Objekt",
      "resource_alias": "Alias"
    },
    {
      "epoch": 2,
      "actor_ref": "actor-neu",
      "action_type": "Beobachtung",
      "resource_type": "künstliches Objekt",
      "resource_ref": "ref-neu",
      "resource_display_name": "Objekt",
      "resource_alias": "Alias"
    }
  ],
  "resource_binding": {
    "old_epoch": 1,
    "old_ref": "ref-alt",
    "new_epoch": 2,
    "new_ref": "ref-neu",
    "relation": "different_resources",
    "valid": true
  }
}
```

## 3. Verblindete Einzelvorlage und Antwortcheckpoint

Jeder Leser bekam in einem neuen Kontext ohne Gesprächsfork ausschließlich
seine eine Karte, die Erklärung zu nicht eindeutigen Anzeigenamen/Aliasen und
exakt diese Fragen:

1. Bezeichnen die Ressourcen vor und nach dem Epochenwechsel dieselbe Ressource?
   Zulässige Antworten: DIESELBE, VERSCHIEDEN, UNBEKANNT.
2. Welcher sichtbare Beleg trägt diese Aussage?
3. Was bleibt mit den sichtbaren Informationen ausdrücklich offen?

[Vorlage R1](observer-resource-epoch/2026-10-08/reader-inputs/R1.txt),
[Vorlage R2](observer-resource-epoch/2026-10-08/reader-inputs/R2.txt),
[Vorlage R3](observer-resource-epoch/2026-10-08/reader-inputs/R3.txt).
Die tatsächlich gesendeten initialen Leseraufträge entsprechen diesen
Vorlagebytes. Gleiche Vorlagehülle; keine R-Kennung, Hypothese, Erwartung,
K14-Auswertung oder Autorenkonversation darin. Kein Leser erhielt andere
Karten; keine Tool-/Dateiaufrufe, Follow-ups, Austausch oder Ersatzleser.
Drei erste finale Antworten wurden verwendet.

Die finalen Antworttexte wurden als UTF-8 ohne Umschreibung und ohne
angehängten Zeilenumbruch gespeichert, read-only gesetzt und gehasht.
[Vor Vergleich gesicherte Hashes und Vorlagezuordnung](observer-resource-epoch/2026-10-08/responses/sealed-sha256.json).
Danach wurde der Antwortcheckpoint gepusht und remote bestätigt. **Erst danach
wurde die eingefrorene Erwartungen-Datei für den Vergleich geöffnet.**
Die Texte blieben beim Vergleich und der Archivierung hashgleich.

Der Autor kennt die Hypothesen aus dem Auftrag; die Kartenleser erhalten sie
nicht. Keine doppelte Verblindung behauptet. Es sind getrennte Kontexte
innerhalb derselben KI-Umgebung, keine externen unabhängigen Systeme,
Menschenstudie oder externe Prüfung. Die Einordnung entspricht einem internen
Versuch mit getrennten Leserkontexten gemäß Methodik; keine Level-3/4-Prüfung.
Read-only, Hash und Commit liefern Nachvollziehbarkeit, keine technische
Isolation gegen einen böswilligen Teilnehmer oder kryptografische Quellechtheit.

Nachfolgend der unveränderte Wortlaut der vor Vergleich gespeicherten Antworten.

### Leserantwort R1

[Originalantwort R1](observer-resource-epoch/2026-10-08/responses/R1.txt)

```text
1. UNBEKANNT.

2. `resource_binding` ist `null`. Gleicher Anzeigename und Alias beweisen laut Karte keine Ressourcenidentität. Die gültige Akteurbindung betrifft ausschließlich den Akteur.

3. Offen bleibt, ob `ref-alt` in Epoche 1 und `ref-neu` in Epoche 2 dieselbe oder verschiedene Ressourcen bezeichnen.
```

### Leserantwort R2

[Originalantwort R2](observer-resource-epoch/2026-10-08/responses/R2.txt)

```text
1. DIESELBE.

2. Die als gültig bezeichnete `resource_binding` verbindet `ref-alt` in Epoche 1 mit `ref-neu` in Epoche 2 durch `same_resource` innerhalb der Papierkarte und des Projekts `p-a`.

3. Die reale Quellechtheit der Bindung bleibt ungeprüft. Ebenso fehlen Angaben zu Zustand oder Veränderungen der Ressource und zum Inhalt der Beobachtungen.
```

### Leserantwort R3

[Originalantwort R3](observer-resource-epoch/2026-10-08/responses/R3.txt)

```text
1. VERSCHIEDEN.

2. Die gültige `resource_binding` verbindet `ref-alt` aus Epoche 1 mit `ref-neu` aus Epoche 2 ausdrücklich als `different_resources`.

3. Die reale Quellechtheit der Bindungen ist nicht geprüft. Gründe für die unterschiedlichen Ressourcen und weitere Zusammenhänge sind nicht angegeben.
```

## 4. Vergleich einschließlich sichtbarer Begründungen

Die Referenz sind die ausdrücklich gesetzten Papierbeziehungen. Es wurde keine
unabhängige reale Ressource untersucht. Der Vergleich erfolgt getrennt vom
unveränderten Antwortarchiv; [Auswertung](observer-resource-epoch/2026-10-08/derived/evaluation.json).

| Karte | Erwartung / Leserantwort | Tragender sichtbarer Beleg | Bewertung |
|---|---|---|---|
| R1 | UNBEKANNT / UNBEKANNT | resource_binding=null; Leser weist Namen-/Aliasschluss zurück und begrenzt Actorbindung ausdrücklich auf den Actor. | KORREKT |
| R2 | DIESELBE / DIESELBE | Gültige same_resource-Bindung zwischen den ausdrücklich benannten Referenzen und Epochen, innerhalb p-a. | KORREKT |
| R3 | VERSCHIEDEN / VERSCHIEDEN | Gültige different_resources-Bindung zwischen denselben Referenzen/Epochen. | KORREKT |

**3 KORREKT, 0 FALSCH, 0 UNBEURTEILBAR.** Alle drei Begründungen tragen die
Einordnung. **Alias-/Namensschlussfolgerungen: 0 beobachtet.** Die ausdrücklich
gleichen Namen/Aliase führten weder in R1 zu Gleichheit noch in R3 zur
Missachtung des Verschiedenheitsbelegs. Projekt, Actorbindung, Reihenfolge
und neue Referenztexte wurden nicht zu Ressourcenidentitätsbeweisen umgedeutet.

Frage 3 bleibt ebenfalls begrenzt: R1 lässt die Ressourcenidentität offen;
R2 weist auf ungeprüfte reale Quellechtheit und unbekannte Zustandsänderungen
hin; R3 auf ungeprüfte Quellechtheit und unbekannte Wechselgründe. Keine Antwort
erfindet reale Objekt-, Revisions- oder projektübergreifende Bindungen.

Gemäß eingefrorener Entscheidungsregel **SUPPORTED IN THIS TEST** für H1–H3
in diesen drei Karten. Drei Einordnungen mit je drei Fragen sind keine neun
unabhängigen Identitätstests. Keine gemessene Produkt-Erkennungsquote und kein
Beleg, dass andere denkbare Informationsformen unzureichend wären.

## 5. Was damit untersucht ist und was offen bleibt

Der neu isolierte Vergleich zeigt genau den Unterschied zwischen fehlender,
gültig gesetzter gleicher und gültig gesetzter verschiedener Ressourcenbindung
über zwei Epochen. Die Actorbindung bleibt dabei konstant. Ein ausdrücklich
gültiger Beleg über die Ressourcenbeziehung kann die Aussage ohne Klarnamen,
Rohinhalte oder Rückgriff auf andere Karten tragen. Fehlende Bindung führt hier
zu UNBEKANNT, nicht zu einem negativen Beweis.

**Gültigkeit ist eine Versuchsvoraussetzung.** Ein JSON-Wert valid=true ist
kein empirischer Beweis realer Gültigkeit. Die semantische Beziehung ist in
R2/R3 absichtlich gesetzt; die Lektüre prüft die daraus zulässige Aussage,
nicht das Entstehen, die Prüfung oder die Wahrheit einer realen Bindung.
Kein Feld-für-Feld-Ablationsversuch: Aus der getesteten Informationsgruppe
folgt kein universelles Pflichtfeld oder zwingender ID-Aufbau.

Weiter offen und durch diesen Versuch nicht gelöst:

- Wie eine reale epochenübergreifende Ressourcenbindung gewonnen und
  unabhängig validiert wird; falsche, widersprüchliche oder manipulierte Quellen.
- Kryptografische Echtheit von IDs und Quellen; Namensräume/Gültigkeit in
  realen Systemen, Quellechtheit und reale Zuverlässigkeit der Bindungsinformation.
- Symlinks, URLs, reale Dateien, Cloudobjekte und Datenbanken; deren konkrete
  Identität oder Wechselwirkungen mit Auflösung, Austausch und Revisionen.
- Projektübergreifende Identität und die Frage, ob eine Ressourcenrevision
  dieselbe Ressource bezeichnet. Gleiche Ressource bedeutet hier keine Aussage
  über unveränderten Inhalt, Version oder Zustand.
- Welche alternative Information ebenfalls genügen könnte, welche konkrete
  Felddarstellung minimal wäre und welche Bindungsform ein Produkt verwenden soll.
- Automatische AA-Erkennung, reale Sensoren/Connectoren, Implementierung,
  Monitorleistung und Verständnis für Menschen. Kein neuer Sensor wurde gebaut.
- Die historische K14-Karte bleibt für die Ressourcenfrage INCONCLUSIVE;
  E2-Metadaten-Lücke, OOS-021 und alle anderen bestehenden offenen Befunde bleiben
  unverändert. Der Finish-Minimalpfadfall wird nicht erneut ausgeführt.

AA erhält hier keine neue Befugnis, darf keine Aktionen erlauben/verbieten,
Rechte vergeben/entziehen oder Wirkungen stoppen. Keine ALLOW/DENY-Produktlogik
oder neue Architektur aus diesem Informationsvergleich abgeleitet.

## 6. Unveränderte Standardsuite und Integrität

Gemäß Methodik §7/§11 nach Vergleich zweimal derselbe Befehl:

```sh
PYTHONDONTWRITEBYTECODE=1 /workspace/venvs/authority/bin/python -m pytest \
  -p no:cacheprovider -o addopts='' -q
```

| Lauf | Tatsächliches Ergebnis | Originalausgabe |
|---|---|---|
| 1 | 340 passed, 5 deselected, 252 subtests passed; Exit 0; 6,85 s | [Suite 1](observer-resource-epoch/2026-10-08/standard-suite/run-1.log) |
| 2 | 340 passed, 5 deselected, 252 subtests passed; Exit 0; 6,80 s | [Suite 2](observer-resource-epoch/2026-10-08/standard-suite/run-2.log) |

[Befehle und Status](observer-resource-epoch/2026-10-08/standard-suite/status.json).
Python 3.12.14, pytest 9.1.1, vorhandene Umgebung; keine Installation.
Die fünf vorhandenen RC-01–05-Deselektionen sind unverändert sichtbar; deren
historische Misses werden nicht durch Grün geschlossen. Keine neuen Filter,
Ausschlüsse, Unit-/Probeversuche oder Veränderungen bestehender Tests.

Achse A: **keine neue Implementierung bewertet**, unveränderte historische
Regression zweimal bestanden. Achse B: **SUPPORTED IN THIS TEST** im
beschriebenen Papierumfang. Suite-PASS ist kein Identitäts- oder Sicherheitsbeweis.

Alle 202 getrackten Ausgangsdateien sind gegenüber Ausgangscommit bytegleich:
Produktcode, Observer/Sensoren, bestehende Tests, historische Karten und
Ergebnisse. Vorabvertrag, Karten, Vorlagen und Erwartungen bleiben seit Freeze
unverändert; Antworttexte und Hashcheckpoint bleiben seit Antwortcommit
unverändert. Belege im
[Freeze-Manifest](observer-resource-epoch/2026-10-08/frozen-integrity.json) und
[Archiv-/Integritätsmanifest](observer-resource-epoch/2026-10-08/archived-integrity.json).
Das Archiv trennt Karten, Leservorlagen, Erwartungen, rohe Antworten,
abgeleitete Bewertung und Standardsuiteausgaben. Nur neue Dokumente hinzugefügt.

## 7. Confidence und Abschluss

**CONFIDENCE IN EXPERIMENT RESULT: HIGH**, ausschließlich innerhalb dieser drei
konstruierten Karten mit gültig gesetzten Bindungen: sauber isolierte
Ressourceninformation, drei getrennte Erstlektüren, unveränderte gesicherte
Antworten vor Vergleich und passende sichtbare Begründungen. Das bewertet den
Papier-Informationsvergleich, keine Ressourcenbindung in einer Laufzeit.

**CONFIDENCE IN GENERALIZATION: LOW.** Einmalige KI-Lektüre pro Karte im
internen selben Modell-/Projektumfeld; keine Wiederholungsstatistik,
Menschenstudie, unabhängige reale Objektprüfung, Quellechtheit oder
Monitoring-/Schutzfunktion untersucht. Unterschiedliche Leserkontexte sind
keine kontrollierte Wiederholungsmessung der Zuverlässigkeit eines Produkts.

**Schlussfolgerung:** Im isolierten Papiervergleich reicht eine ausdrücklich
gültig gesetzte Beziehung zwischen den benannten Ressourcenreferenzen/Epochen
für DIESELBE oder VERSCHIEDEN; ohne diese Information bleibt die Zuordnung
UNBEKANNT. Wie ein realer Beleg gewonnen und validiert wird, bleibt offen.

**STOPP nach Ergebnis, Commit und Push.** Keine Ressourcenbindung implementiert,
kein nächster Test und keine Erweiterung des Observers begonnen.
