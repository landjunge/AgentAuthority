# Erneuter isolierter Vergleich: Ressourcenidentität über Epochen

8. Oktober 2026. **SUPPORTED IN THIS TEST**, ausschließlich für die drei
künstlichen Informationskarten mit gesetzter Gültigkeit der Bindungen.
Neue verblindete Erstlektüren: **R1 UNBEKANNT, R2 DIESELBE, R3 VERSCHIEDEN**.
Drei KORREKT, null FALSCH, null UNBEURTEILBAR für die Ressourcenidentitätsfrage
mit jeweils tragfähiger Begründung; keine unerlaubten Namens-/Aliasschlüsse.

Das Ergebnis zeigt, welche Information in diesem isolierten Vergleich die
Identitätsaussage trägt. Es löst keine reale Ressourcenidentität und baut
keine Observerfunktion. Historisches K14 bleibt INCONCLUSIVE.

## 1. Forschungsbasis und getrennte Durchführung

| Stand | Vollständiger Commit-SHA |
|---|---|
| Beauftragter Ausgangsstand | `c9abf753b5a3060a630ec6b4f19d6de3b9ca610a` |
| Vorabvertrag, Karten, Vorlagen und Erwartungen vor Bewertung | `824ebcfe806894876dc6ded7ba9adb4d0ef16648` |
| Wortgetreue neue Antworten und Hashcheckpoint vor Vergleich | `b64014161fa374597be6563f6ebeeb7640b37af3` |

Der erneute Auftrag enthält zusätzlich den Real-Run-Bericht als Pflichtquelle.
Separates Worktree `/workspace/agent-authority-resource-epoch-repeat01` ab
exakt dem beauftragten Ausgangscommit; Branch
`research/observer-resource-epoch-repeat-01-2026-10-08`. Der vorherige Vergleich
bleibt auf seinem bisherigen Branch unter
`4be9a61d9659d4f36347f0ad705369032b8c0a7c` erhalten. Dessen Leserantworten sind
keine Eingaben oder Ersatzantworten dieses neuen Versuchs.

Alle sieben Pflichtquellen vor Änderungen vollständig gelesen:
[Real-Run-Ergebnis](OBSERVER-REAL-RUN-PROTOTYPE-RESULTS-2026-10-07.md),
[Konsolidierung](OBSERVER-RESEARCH-CONSOLIDATION-E1-E7-2026-10-07.md),
[E3–E7-Bericht](OBSERVER-E3-E7-2026-10-07.md),
[alle historischen Karten](OBSERVER-E3-E7-CARDS-2026-10-07.json),
[beide vollständigen Antwortphasen](OBSERVER-E3-E7-RESPONSES-2026-10-07.jsonl),
[Methodik](RESEARCH-METHOD.md),
[Finish-Minimalpfad-Ergebnis](OBSERVER-FINISH-MINIMAL-PATH-RESULTS-2026-10-08.md).
Die sechs schon zuvor vollständig gelesenen Quellen wurden gegen c9abf753
bytegleich bestätigt; die zusätzliche Quelle jetzt vollständig gelesen.

Der Real-Run-Bericht prüft pro Lauf ein vorher bezeichnetes Testziel und
schließt eine Lösung von K14 ausdrücklich aus. Seine erfolgreichen kleinen
Feldmengen liefern keinen allgemeinen Ressourcenschlüssel. Das Finish-Ergebnis
bindet nur seinen einen beobachteten Fake-Schreibvorgang. E3/K14 bindet den
Actor, nicht ausdrücklich die Ressource über Epochen; anders als K02 fehlt
Ressourcenstabilität. Keine dieser Angaben wird als fehlende Ressourcenbindung
in neue Karten übertragen. Alte Karten und Ergebnisse bleiben unverändert.

[Vorabvertrag](OBSERVER-RESOURCE-EPOCH-REPEAT-01-CONTRACT-2026-10-08.md) und
Antwortcheckpoint wurden jeweils committed, gepusht und mit identischem
Remote-SHA bestätigt, bevor Bewertung beziehungsweise Vergleich begann.
Keine Hypothesen-/Kriterienänderung nach Ergebnis.

## 2. Exakte drei Karten und isolierte Informationsänderung

Eingefroren: H1 ohne Ressourcenbindung → UNBEKANNT; H2 mit gültiger
Gleichheitsbindung → DIESELBE; H3 mit gültigem Verschiedenheitsbeleg → VERSCHIEDEN.
[Erwartungen](observer-resource-epoch-repeat-01/2026-10-08/expectations.json).

Gemeinsame Daten identisch: p-a, geordnete Epochen 1/2, ausdrücklich gebundene
gleiche Actorinstanz, dieselben zwei Meldungen, Aktionsart, Ressourcentyp,
beide Referenzen, Anzeigenamen und Aliase. Rollen oder sonstiger Kontext werden
in keiner Karte ergänzt. Namen/Aliase sind ausdrücklich nicht eindeutig.
Keine echten Nutzerdaten, Dateien, Accounts oder Agentidentitäten.

Vor Freeze und nach Vergleich mechanisch geprüft: Nach Entfernen nur von
resource_binding sind alle drei Karten identisch. R2/R3 unterscheiden sich
innerhalb der Bindung nur in relation. Die Bindung ist ein gesonderter gesetzter
Papierbeleg, keine dritte Aktionsmeldung. Diese JSON-Darstellung ändert kein
bestehendes Observerfeld und schreibt keine zukünftige ID-Struktur vor.

Vollständiger Wortlaut der eingefrorenen Karten:

### R1

[Originalkarte R1](observer-resource-epoch-repeat-01/2026-10-08/cards/R1.json)

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

[Originalkarte R2](observer-resource-epoch-repeat-01/2026-10-08/cards/R2.json)

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

[Originalkarte R3](observer-resource-epoch-repeat-01/2026-10-08/cards/R3.json)

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

## 3. Neue verblindete Einzelbewertungen und Sicherung

Drei neue KI-Kontexte ohne Gesprächsfork, jeweils nur ihre eine Karte,
Hinweis auf nicht eindeutige Namen/Aliase, erlaubte Antworten und exakt:

1. Bezeichnen die Ressourcen vor und nach dem Epochenwechsel dieselbe Ressource?
   Zulässige Antworten: DIESELBE, VERSCHIEDEN, UNBEKANNT.
2. Welcher sichtbare Beleg trägt diese Aussage?
3. Was bleibt mit den sichtbaren Informationen ausdrücklich offen?

Exakte Einzelvorlagen: [R1](observer-resource-epoch-repeat-01/2026-10-08/reader-inputs/R1.txt),
[R2](observer-resource-epoch-repeat-01/2026-10-08/reader-inputs/R2.txt),
[R3](observer-resource-epoch-repeat-01/2026-10-08/reader-inputs/R3.txt).
Die initialen Leseraufträge entsprechen diesen Vorlagen. Gleiche Vorlagehülle;
keine H1/H2/H3, anderen Karten, Erwartungen, R-Kennung, alte K14-Auswertung
oder Autorenkonversation. Kein Leser erhielt alte Vergleichsantworten.
Keine Tool-/Dateiaufrufe, Follow-ups, wechselseitigen Nachrichten, Ersatzleser
oder Wiederholung. Verwendet wurden die drei ersten finalen Texte.

Alle Texte unverändert als UTF-8 ohne angehängten Zeilenumbruch archiviert,
read-only gesetzt und vor Vergleich gehasht;
[gesicherte Hashes und Vorlagezuordnung](observer-resource-epoch-repeat-01/2026-10-08/responses/sealed-sha256.json).
Antwortcheckpoint gepusht und remote bestätigt. Erst danach Erwartungen-Datei
für den Vergleich geöffnet. Antwortbytes und Hashes blieben unverändert.

Nur die Leser sind bezüglich Hypothesen/Erwartungen verblindet; der Autor
kennt sie aus dem Auftrag. Getrennte Kontexte derselben internen KI-Umgebung,
keine doppelte Verblindung, externe unabhängige Prüfung oder Menschenstudie.
Read-only, Hash und Commit sind Nachvollziehbarkeit dieser Teststrecke,
keine Quellechtheit oder technische Isolation gegen böswillige Teilnehmer.

Unveränderter Wortlaut der vor Vergleich gesicherten Antworten:

### Antwort R1

[Originalantwort R1](observer-resource-epoch-repeat-01/2026-10-08/responses/R1.txt)

```text
1. UNBEKANNT.
2. `resource_binding` ist `null`. Gleiche Anzeigenamen und Aliase beweisen laut Prämissen keine Ressourcenidentität; die gültige Akteursbindung betrifft nur den Akteur.
3. Offen bleibt, ob `ref-alt` und `ref-neu` dieselbe oder verschiedene Ressourcen bezeichnen. Die reale Quellechtheit der Bindung ist ebenfalls nicht geprüft.
```

### Antwort R2

[Originalantwort R2](observer-resource-epoch-repeat-01/2026-10-08/responses/R2.txt)

```text
1. DIESELBE.
2. Die als gültig bezeichnete `resource_binding` verbindet `ref-alt` aus Epoche 1 mit `ref-neu` aus Epoche 2 durch `same_resource` innerhalb des Projekts `p-a`.
3. Die reale Quellechtheit der Bindung bleibt ungeprüft. Über die künstliche Papierkarte hinausgehende tatsächliche Vorgänge sind nicht belegt.
```

### Antwort R3

[Originalantwort R3](observer-resource-epoch-repeat-01/2026-10-08/responses/R3.txt)

```text
1. VERSCHIEDEN.

2. Die ausdrücklich gültige Ressourcenbindung verbindet `ref-alt` aus Epoche 1 mit `ref-neu` aus Epoche 2 durch `relation: "different_resources"`.

3. Die reale Quellechtheit der Bindungen bleibt ungeprüft. Weitere konkrete Identitäten und Eigenschaften der Ressourcen sind nicht angegeben.
```

## 4. Bewertung einschließlich Begründung und offener Formulierung

Referenz ist ausschließlich die gültig gesetzte Papierinformation, keine
unabhängige reale Objektmessung. Getrennte
[Auswertung](observer-resource-epoch-repeat-01/2026-10-08/derived/evaluation.json):

| Karte | Erwartung / neue Leserantwort | Tragender sichtbarer Beleg | Bewertung |
|---|---|---|---|
| R1 | UNBEKANNT / UNBEKANNT | resource_binding=null; Name-/Aliasschluss ausdrücklich abgelehnt, Akteursbindung nur für Akteur. | KORREKT |
| R2 | DIESELBE / DIESELBE | Gültige same_resource-Bindung zwischen ref-alt/Epoche 1 und ref-neu/Epoche 2 innerhalb p-a. | KORREKT |
| R3 | VERSCHIEDEN / VERSCHIEDEN | Gültige different_resources-Bindung zwischen denselben Referenzen/Epochen. | KORREKT |

**3 KORREKT, 0 FALSCH, 0 UNBEURTEILBAR.** **0 beobachtete unerlaubte
Namens-/Aliasschlüsse.** R1 erhält die Ressourcenidentität als offen; R2/R3
stützen sich ausdrücklich auf ihre jeweilige Ressourcenbindung. Projekt,
Akteursgleichheit, Nähe, Reihenfolge und Referenztext werden nicht zu
Identitätsbeweisen umgedeutet. Die passenden Wörter allein wären ohne
passende Begründung kein Erfolg.

**Erhaltene Formulierungsgrenze in R1, Frage 3:** Der Leser sagt „Die reale
Quellechtheit der Bindung ist ebenfalls nicht geprüft“, ohne „der Bindung“
genauer zuzuordnen. Dieser Bezug wird nicht nachträglich festgelegt. Das ist
kein Beleg einer zusätzlichen Ressourcenbindung. Frage 1 und 2 sind eindeutig:
Ressourcenidentität UNBEKANNT, resource_binding=null; deshalb ist die
beauftragte Identitätsaussage mit ihrer Begründung sauber beurteilbar. Der
unspezifizierte Bezug bleibt als solcher erhalten, statt die Antwort zu ändern.

R2/R3 lassen reale Quellechtheit und weitere tatsächliche Vorgänge bzw.
Ressourceneigenschaften offen. Kein realer Identitäts-/Revisionsbeweis wird
behauptet. Drei Karten mit je drei Fragen sind keine neun unabhängigen Tests.
Die Zahlen bewerten die drei Identitätseinordnungen einschließlich ihrer
Begründungen, keine Produkt-Erkennungsquote oder allgemeine Leserzuverlässigkeit.

**SUPPORTED IN THIS TEST** gemäß unveränderter Entscheidungsregel, für die
H1/H2/H3 innerhalb dieser drei Papierkarten. Das frühere Ergebnis wird nicht
überschrieben oder für dieses Urteil als Ersatzbeleg herangezogen.

## 5. Tatsächlicher Erkenntnisumfang und weiter offene Fragen

Der isolierte Unterschied liegt allein in der Ressourcenbeziehung über
Epochen. Eine ausdrücklich gültig gesetzte Gleichheits-/Verschiedenheitsbindung
zwischen den benannten Referenzen trägt hier DIESELBE/VERSCHIEDEN. Ohne diesen
Beleg bleibt die Frage offen. Die vorher gebundene Actorinstanz kann eine
fehlende Ressourcenbindung nicht ersetzen. Keine Klarnamen oder Rohinhalte nötig
für diese begrenzte Papierzuordnung; keine Vermutung aus anderen Karten.

**Gültigkeit ist vorausgesetzt, nicht gemessen.** valid=true allein authentisiert
keine reale Quelle. Dieser Test prüft die Aussage, die eine gültige Beziehung
trägt; nicht, wie diese Beziehung gewonnen oder verifiziert wird. Keine
Feld-für-Feld-Ablation, universelle Feldminimalität oder vorgeschriebene ID-Struktur.

Weiter offen:

- Reale Ressourcenbindung über Epochen und ihre unabhängige Validierung;
  falsche, widersprüchliche oder manipulierte Quellen/Belege.
- Kryptografische Echtheit von IDs/Quellen sowie reale Gültigkeit, Scope,
  Namensräume und Zuverlässigkeit eines Bindungssystems.
- Dateien, Symlinks, URLs, Cloudobjekte und Datenbanken mit ihren tatsächlichen
  Auflösungs-, Austausch-, Versions- und Identitätsgrenzen.
- Projektübergreifende Identität und Ressourcenrevisionen. Gleiche Ressource
  ist hier kein Beweis unveränderten Zustands oder Inhalts.
- Alternative hinreichende Information, minimale Darstellungsfelder, zukünftige
  ID-Technik oder Architektur; diese werden nicht festgelegt.
- Reale AA-Sensoren, automatische Zuordnung, Monitoring-/Schutzleistung,
  Menschenverständnis und allgemeine Zuverlässigkeit von KI-Lesern.
- Historisches K14 bleibt für die Ressourcenfrage INCONCLUSIVE; Real-Run-
  Minimalmengen werden nicht zu deren Lösung umgedeutet. E2-Metadaten-Lücke,
  OOS-021 und weitere bestehende Misses bleiben offen. Keine Originalprobe
  oder anderen Agentenläufe begonnen.

AA bleibt eigenständiger Beobachter / Monitor / Analyseebene. Keine Aktionen
allow/deny, keine Rechtevergabe, Freigaben oder Stopps durch diesen Vergleich.
Kein Observercode, Sensor, Datenfeld oder bestehender Test wurde geändert.

## 6. Standardsuite und erhaltene Dateien

Nach Ergebnis gemäß Methodik zweimal derselbe Befehl:

```sh
PYTHONDONTWRITEBYTECODE=1 /workspace/venvs/authority/bin/python -m pytest \
  -p no:cacheprovider -o addopts='' -q
```

| Lauf | Tatsächliches Ergebnis | Originalausgabe |
|---|---|---|
| 1 | 340 passed, 5 deselected, 252 subtests passed; Exit 0; 8,18 s | [Suite 1](observer-resource-epoch-repeat-01/2026-10-08/standard-suite/run-1.log) |
| 2 | 340 passed, 5 deselected, 252 subtests passed; Exit 0; 7,88 s | [Suite 2](observer-resource-epoch-repeat-01/2026-10-08/standard-suite/run-2.log) |

[Befehle und Status](observer-resource-epoch-repeat-01/2026-10-08/standard-suite/status.json).
Python 3.12.14, pytest 9.1.1, vorhandene Umgebung; keine Installation.
Keine neuen Filter/Ausschlüsse. Die fünf RC-01–05-Deselektionen bleiben
unverändert sichtbar; ihre historischen Misses werden durch Grün nicht geschlossen.
Keine zusätzlichen Unit-/Probeversuche. Achse A: keine neue Implementierung
bewertet; unveränderte Regression bestanden. Achse B: begrenztes Papierurteil.
Suite-PASS ist kein Identitäts- oder Sicherheitsbeweis.

Alle 202 getrackten Ausgangsdateien gegen c9abf753 bytegleich, einschließlich
historischer Karten/Antworten/Berichte, Observer, Sensoren und Tests.
Alle neun Vorabartefakte seit Vertragscommit und vier Antwortartefakte seit
Antwortcheckpoint unverändert. Belege:
[Freeze-Manifest](observer-resource-epoch-repeat-01/2026-10-08/frozen-integrity.json),
[Archiv-/Integritätsmanifest](observer-resource-epoch-repeat-01/2026-10-08/archived-integrity.json).
Karten, Vorlagen, Erwartungen, Originalantworten, Ableitungen und Suiteausgaben
liegen getrennt. Das frühere Worktree bleibt unverändert. Ausschließlich neue
Dokumente im separaten Branch hinzugefügt.

## 7. Confidence und Abschluss

**CONFIDENCE IN EXPERIMENT RESULT: HIGH** ausschließlich für die drei
Identitätsaussagen mit sichtbaren Begründungen innerhalb der künstlichen,
gültig gesetzten Karten: isolierte Variation und gesicherte neue Erstantworten
vor Vergleich. Der unpräzisierte R1-Bezug bleibt offen; keine neue
Quellen-/Identitätsgewissheit daraus. Kein realer Bindungstest.

**CONFIDENCE IN GENERALIZATION: LOW.** Drei interne KI-Kontexte, eine Antwort
je Karte; keine Wiederholungsstatistik, externe unabhängige Systeme,
Menschenstudie, realen Ressourcen, Sensoren oder Quellechtheit untersucht.
Keine allgemeine Zuverlässigkeit, Produktfähigkeit oder Sicherheit behauptet.

**Schlussfolgerung:** Im isolierten Vergleich trägt eine ausdrücklich gültig
gesetzte Beziehung zwischen den Ressourcenreferenzen/Epochen die Aussage
DIESELBE oder VERSCHIEDEN; fehlt sie, bleibt die Zuordnung UNBEKANNT. Das
Erzeugen und Validieren eines realen Belegs bleibt offen.

**STOPP nach Ergebnis, Commit und Push.** Keine Ressourcenbindung implementiert,
kein nächster Test und keine Erweiterung des Observers begonnen.
