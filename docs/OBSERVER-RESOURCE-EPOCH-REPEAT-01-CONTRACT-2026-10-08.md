# Vorabvertrag: erneuter isolierter Ressourcen-/Epochenvergleich

8. Oktober 2026, Berichtsdatum Europe/Berlin. Neuer ausdrücklich beauftragter
Papiervergleich. Ausgangscommit: `c9abf753b5a3060a630ec6b4f19d6de3b9ca610a`.
Separates Worktree und Branch `research/observer-resource-epoch-repeat-01-2026-10-08`.
Der vorherige Vergleich bleibt auf seinem Branch und unter
`4be9a61d9659d4f36347f0ad705369032b8c0a7c` unverändert erhalten; dessen Antworten
werden weder den neuen Lesern vorgelegt noch als neue Antworten übernommen.

## Quellen und Forschungsfrage

Alle sieben Pflichtquellen sind vor Änderungen vollständig gelesen: Real-Run-
Prototypbericht, Konsolidierung E1–E7, vollständiger E3–E7-Bericht, alle
historischen Karten, beide vollständigen Antwortphasen, RESEARCH-METHOD und
Finish-Minimalpfad-Ergebnis. Die sechs bereits zuvor vollständig gelesenen
Quellen wurden byteweise gegen den beauftragten Ausgangscommit bestätigt;
der zusätzlich genannte Real-Run-Bericht wurde jetzt vollständig gelesen.
Keine neue externe Recherche und keine fehlenden Zusammenhänge ergänzt.

Der [Real-Run-Bericht](OBSERVER-REAL-RUN-PROTOTYPE-RESULTS-2026-10-07.md) belegt
nur seine lokalen Zielsnapshot-/Zeitfragen bei einem vorher bezeichneten Ziel
je Lauf; er löst ausdrücklich keine allgemeine Ressourcenbindung oder K14.
Die [Konsolidierung](OBSERVER-RESEARCH-CONSOLIDATION-E1-E7-2026-10-07.md) und
[E3–E7](OBSERVER-E3-E7-2026-10-07.md) erhalten die Ressourcenfrage in K14 als
INCONCLUSIVE: Actor gebunden, Ressourcenstabilität über Epochen nicht gesetzt.
Das [Finish-Ergebnis](OBSERVER-FINISH-MINIMAL-PATH-RESULTS-2026-10-08.md) betrifft
seinen einen lokalen Fake-Schreibvorgang, keine allgemeine Ressourcenidentität.
Keine dieser Quellen liefert eine nachträgliche Bindung für die neuen Karten.

**Frage:** Kann ein Beobachter dieselbe Ressource über zwei Epochen zuverlässig
wiedererkennen: ohne Ressourcenbindung, mit ausdrücklich gültiger
Gleichheitsbindung oder mit ausdrücklich belegtem Ressourcenwechsel?
Geprüft wird ausschließlich, welche sichtbare Information die Aussage im
isolierten Papiervergleich trägt. Kein Programm wird entwickelt oder bewertet.

## Unveränderliche Hypothesen, Karten und Isolation

- **H1:** Ohne ausdrückliche Ressourcenbindung bleibt die Ressourcenidentität
  über den Epochenwechsel UNBEKANNT.
- **H2:** Mit ausdrücklich gültiger Bindung alt → neu = dieselbe Ressource
  kann die Ressource als DIESELBE zugeordnet werden.
- **H3:** Mit ausdrücklich gültigem Beleg alt → neu = verschiedene Ressourcen
  kann die Ressource als VERSCHIEDEN zugeordnet werden.

Genau drei künstliche Karten und die
[eingefrorenen Erwartungen](observer-resource-epoch-repeat-01/2026-10-08/expectations.json):

| Karte | Einzige variable Informationsgruppe | Erwartung |
|---|---|---|
| [R1](observer-resource-epoch-repeat-01/2026-10-08/cards/R1.json) | resource_binding=null; keine Ressourcenbeziehung über Epochen belegt | UNBEKANNT |
| [R2](observer-resource-epoch-repeat-01/2026-10-08/cards/R2.json) | Genau eine gültig gesetzte same_resource-Bindung ref-alt/1 → ref-neu/2 | DIESELBE, ausschließlich aufgrund dieser Bindung |
| [R3](observer-resource-epoch-repeat-01/2026-10-08/cards/R3.json) | Genau ein gültig gesetzter different_resources-Beleg für dieselben Referenzen/Epochen | VERSCHIEDEN, ausschließlich aufgrund dieses Belegs |

Gemeinsame Daten identisch: p-a, Epoche 1 vor Epoche 2, ausdrücklich gültig
gebundene gleiche Actorinstanz, dieselben zwei Meldungen, Aktionsart,
Ressourcentyp, beide Referenzen, Anzeigenamen und Aliase. Rollen werden in
keiner Karte hinzugefügt. Namen/Aliase sind ausdrücklich nicht eindeutig;
gleicher Text beweist keine Ressourcenidentität. Keine realen Nutzerdaten,
Dateien, Accounts, Agentidentitäten oder Zugangsdaten.

Mechanisch vor Freeze prüfen: genau drei Karten; nach Entfernen ausschließlich
von resource_binding sind die gemeinsamen Daten identisch. R2/R3 unterscheiden
sich innerhalb der Bindung nur in relation. Die zusätzliche Bindung ist eine
gesetzte Aussage im Papierkontext, keine zusätzliche Aktionsmeldung. Kein
Kontext, keine Actorbindung und keine Meldungsanzahl wird variiert. Keine
Übernahme fehlender Angaben aus einer anderen oder historischen Karte.
Die Darstellungsfelder sind keine neuen produktiven Observerfelder/IDs.

## Freeze, verblindete Einzelbewertung und Antwortcheckpoint

Dieser Vertrag, alle drei Karten, die identischen Vorlagehüllen, Erwartungen
und das Freeze-Manifest werden vor jeder Leserbewertung committed, gepusht
und remote bestätigt. Danach keine Änderung von Hypothesen, Karten oder
Bewertungskriterien, keine Auswahl günstiger Antworten.

Genau drei neue KI-Leserkontexte ohne Gesprächsfork, jeweils nur eine Karte;
keine Hypothesen, anderen Karten, Erwartungen, alte K14-Auswertung oder
Autorenkonversation. Auch der vorherige neue Vergleich bleibt diesen Lesern
unbekannt. Keine Tools, Dateisuchen, Nachrichten zwischen Lesern, Follow-ups,
Ersatzleser oder Wiederholung. Jede erste finale Antwort wird unverändert
verwendet. Vorlage R1.txt/R2.txt/R3.txt unter reader-inputs/ im Archiv.

Jeder Leser erhält dieselben drei Fragen in exakt diesem Wortlaut:

1. **Bezeichnen die Ressourcen vor und nach dem Epochenwechsel dieselbe Ressource?**
   Zulässige Antworten: DIESELBE, VERSCHIEDEN, UNBEKANNT.
2. **Welcher sichtbare Beleg trägt diese Aussage?**
3. **Was bleibt mit den sichtbaren Informationen ausdrücklich offen?**

Alle drei finalen Texte vor Vergleich separat als UTF-8 unverändert speichern,
read-only setzen, hashen und zu ihren Eingabehashes zuordnen. Antwortcheckpoint
committen, pushen und remote bestätigen. Erst danach die Erwartungen-Datei
für den Vergleich öffnen. Antworten unverändert erhalten, Bewertung getrennt.
Der Autor kennt die Hypothesen; nur die Kartenleser sind bezüglich Hypothesen
und Erwartungen verblindet. Keine doppelte Verblindung, externe Prüfung oder
technische Isolation gegen böswillige Teilnehmer behaupten. Die Leser gehören
derselben internen KI-Umgebung an; je eine Antwort ist keine Produktquote.

## Bewertung und Entscheidung

Je Karte KORREKT / FALSCH / UNBEURTEILBAR einschließlich Begründungsprüfung:
R1 nur UNBEKANNT wegen fehlender Ressourcenbindung; Identitätsschluss aus
Name, Alias, Projekt, Actorbindung, Nähe oder Reihenfolge ist FALSCH.
R2 nur DIESELBE aufgrund gültiger Ressourcenbindung; R3 nur VERSCHIEDEN
aufgrund gültigen Ressourcenwechselbelegs. Frage 3 darf keine weitergehende
Identität, Quellechtheit oder Revisionsbehauptung erfinden.

- **SUPPORTED IN THIS TEST:** alle drei erwarteten Antworten und tragfähige
  Begründungen ausschließlich aus der jeweiligen sichtbaren Information.
- **NOT SUPPORTED:** eine beurteilbare Karte falsch eingeordnet.
- **INCONCLUSIVE:** Design, Antwort oder Referenz erlaubt keine saubere Bewertung.

Die Referenz ist die gesetzte Papierinformation, keine reale Objektmessung.
Achse A: keine neue Implementierung bewertet. Achse B: dieses begrenzte
Informationsurteil. Drei Karten mit je drei Fragen, keine neun unabhängigen Fälle.
HIGH darf ausschließlich den nachprüfbaren konstruierten Vergleich bezeichnen;
Generalisierung separat als LOW, keine allgemeine Zuverlässigkeitsgarantie.

## Standardsuite, Ergebnis und STOPP

Nach dem Ergebnis gemäß [Methodik](RESEARCH-METHOD.md) §7/§11 zweimal identisch:

```sh
PYTHONDONTWRITEBYTECODE=1 /workspace/venvs/authority/bin/python -m pytest \
  -p no:cacheprovider -o addopts='' -q
```

Bestehende Tests und fünf RC-Deselektionen unverändert. Keine zusätzlichen
Probes oder Unitversuche. Alle 202 getrackten Ausgangsdateien über das
[Freeze-Manifest](observer-resource-epoch-repeat-01/2026-10-08/frozen-integrity.json)
vor und nach Bewertung/Suite byteweise erhalten; ebenso alle Vorabartefakte
und gesicherten Antworten. Das frühere Ergebnis im anderen Worktree erhalten.

Neuer Bericht: Ausgangs-/Vertragscommit, exakte R1/R2/R3-Karten, unveränderte
Antworten vor Vergleich, jede Bewertung/Begründung, unerlaubte Namens-/
Aliasschlüsse, tatsächlicher Erkenntnisumfang, offene Fragen, Suitebelege,
CONFIDENCE IN EXPERIMENT RESULT und CONFIDENCE IN GENERALIZATION.
Ein internes lesendes Artefaktreview darf Integrität und Aussagegrenzen prüfen,
aber keine weiteren Karten, Leserantworten oder Experimente erzeugen.

Nicht behaupten: reale Ressourcenidentität gelöst, kryptografisch echte IDs,
allgemeine Datei-/Symlink-/URL-/Cloud-/Datenbankbindung, projektübergreifende
Identität, automatische Revisionsgleichheit, notwendige zukünftige ID-Struktur
oder vorhandener AA-Sensor. K14 bleibt historisch INCONCLUSIVE; E2 und OOS-021
bleiben offen. Keine Implementierung, Sensoren, ID-/Feld-/Architekturänderung
oder neue Befugnis. AA bleibt unabhängiger Beobachter / Monitor / Analyseebene.

Nach Ergebnis Commit, Push und Remote-Bestätigung; Bericht und vollständigen
SHA ausgeben. **Danach STOPP: keine Ressourcenbindung implementieren, kein
nächster Test und keine Observererweiterung.**
