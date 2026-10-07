# Vorabvertrag: Ressourcenidentität über einen Epochenwechsel

8. Oktober 2026, Berichtsdatum Europe/Berlin. Ausschließlich neuer, ausdrücklich
beauftragter Papiervergleich; keine Implementierung. Ausgangscommit:
`c9abf753b5a3060a630ec6b4f19d6de3b9ca610a`.

## Ausgangspunkt und Forschungsfrage

Vollständig vor Änderungen gelesen: Konsolidierung E1–E7, vollständiger
E3–E7-Bericht, alle 24 historischen Karten und beide vollständigen archivierten
Leserantwortphasen, RESEARCH-METHOD sowie Finish-Minimalpfad-Ergebnisbericht.

Die [Konsolidierung](OBSERVER-RESEARCH-CONSOLIDATION-E1-E7-2026-10-07.md),
Abschnitte A.10/B.12/C/H, und der
[E3-Bericht](OBSERVER-E3-E7-2026-10-07.md) halten fest: K14 bindet den Actor,
nicht ausdrücklich die Ressource über Epochen. Anders als K02 setzt K14
keine Ressourcenstabilität. Der historische Vergleich bleibt deshalb für
diese Ressourcenfrage INCONCLUSIVE. Karte, Antworten und Ergebnis werden
nicht nachträglich ergänzt, repariert oder umgedeutet.

**Forschungsfrage:** Welche sichtbare Information reicht im isolierten
Papiervergleich, um über zwei Epochen zu sagen, ob dieselbe Ressource gemeint
ist: ohne Ressourcenbindung, mit ausdrücklich gültiger Gleichheitsbindung
oder mit ausdrücklich belegtem Ressourcenwechsel?

Agent Authority bleibt eigenständiger Beobachter / Monitor / Analyseebene.
Dieser Versuch bewertet Informationsgehalt, keine Softwarefunktion oder
Befugnis. Keine produktive Bindung, neue ID-Struktur, Sensortechnik oder
Produktarchitektur wird eingeführt.

## Unveränderliche Hypothesen und Referenz

- **H1:** Ohne ausdrückliche Ressourcenbindung bleibt die Identität der
  Ressource über den Epochenwechsel UNBEKANNT.
- **H2:** Mit ausdrücklich gültiger Bindung alt → neu = dieselbe Ressource
  kann sie als DIESELBE zugeordnet werden.
- **H3:** Mit ausdrücklich gültigem Beleg alt → neu = verschiedene Ressourcen
  kann sie als VERSCHIEDEN zugeordnet werden.

Diese Hypothesen, Karten, Vorlagebytes und
[Erwartungen](observer-resource-epoch/2026-10-08/expectations.json) werden vor
jeder Leserbewertung zusammen committed, gepusht und remote bestätigt.
Nach Beginn keine Änderung oder Auswahl günstiger Antworten.
Die Referenz ist ausdrücklich die gesetzte Papierinformation, keine unabhängig
gemessene reale Objektidentität.

## Genau drei Karten und ihre Isolation

| Karte | Einzige veränderte Informationsgruppe | Eingefrorene Erwartung |
|---|---|---|
| [R1](observer-resource-epoch/2026-10-08/cards/R1.json) | resource_binding=null; keine epochenübergreifende Ressourcenbindung | UNBEKANNT |
| [R2](observer-resource-epoch/2026-10-08/cards/R2.json) | Genau eine ausdrücklich gültige same_resource-Bindung: ref-alt/Epoche 1 → ref-neu/Epoche 2 | DIESELBE, ausschließlich aufgrund dieser Bindung |
| [R3](observer-resource-epoch/2026-10-08/cards/R3.json) | Genau ein ausdrücklich gültiger different_resources-Beleg für dieselben beiden Referenzen/Epochen | VERSCHIEDEN, ausschließlich aufgrund dieses Belegs |

Gemeinsame Angaben sind bytegleich nach Entfernung ausschließlich von
`resource_binding`: Projekt p-a; Epoche 1 vor Epoche 2; ausdrücklich gültige
Actorbindung actor-alt/1 → actor-neu/2 = gleiche Instanz; zwei Meldungen;
dieselbe Aktionsart und derselbe künstliche Ressourcentyp; ref-alt/ref-neu;
jeweils derselbe nicht eindeutige Anzeigename und Alias. Rollen oder weitere
Kontextinformationen werden in keiner Karte ergänzt. Keine Rohinhalte,
realen Dateien, Accounts, Agentidentitäten oder Zugangsdaten.

Die Bindungen sind separate Aussagen im Papierkontext, keine zusätzliche
Aktionsmeldung. Die Anzahl der beiden Meldungen wird nicht verändert.
Die Papier-JSON-Schlüssel sind ausschließlich Darstellung dieser Karten,
keine neuen Observerfelder oder Vorschrift eines zukünftigen ID-Aufbaus.
Eine neue Referenz belegt allein weder Objektgleichheit noch Objektverschiedenheit.

Vor dem Freeze mechanisch prüfen: genau drei Karten, gleiche gemeinsamen
Angaben, gleiche zwei Meldungen und Actorbindung, ausschließlich die genannte
Ressourceninformation unterschiedlich. Keine fehlende Bindung aus K14,
K02 oder einer anderen Karte übernehmen.

## Getrennte Bewertung ohne Hypothesenwissen

Für jede Karte genau **ein eigener neuer KI-Leserkontext**, insgesamt drei.
Kein Gesprächsfork und keine Repository-/Autorenhistorie. Alle drei verwenden
dieselbe unveränderte Vorlagehülle und erhalten ausschließlich ihre eine
Karte, die Erklärung nicht eindeutiger Anzeigenamen/Aliase und diese Fragen:

1. **Bezeichnen die Ressourcen vor und nach dem Epochenwechsel dieselbe Ressource?**
   Zulässige Antworten: DIESELBE, VERSCHIEDEN, UNBEKANNT.
2. **Welcher sichtbare Beleg trägt diese Aussage?**
3. **Was bleibt mit den sichtbaren Informationen ausdrücklich offen?**

Die [drei exakten Leservorlagen](observer-resource-epoch/2026-10-08/reader-inputs/R1.txt)
werden einzeln archiviert; R2.txt und R3.txt liegen im selben Verzeichnis.
Die Karte selbst und die Leservorlage enthalten keine R-Kennung, Hypothese,
Erwartung, alte K14-Auswertung oder Autorenkonversation. Keine anderen Karten
im selben Kontext, keine Tools/Dateisuchen, keine wechselseitigen Nachrichten,
kein Follow-up zur Verbesserung einer Antwort. Fehlende oder nicht beurteilbare
Antwort wird dokumentiert; kein Ersatzleser oder wiederholter Testlauf.

Die Leser sind getrennte Kontexte derselben internen KI-Umgebung, keine
externen Prüfer oder Menschen. Der Versuchsautor kennt die beauftragten
Hypothesen beim Entwurf. Nur die Kartenleser sind bezüglich Hypothesen und
Erwartungen verblindet; keine doppelte Verblindung oder technische Isolation
gegen einen böswilligen Leser behaupten. Unterschiedliche Leserkontexte und
einmalige Antworten sind eine Übertragungsgrenze, keine Produktquote.

## Antwortcheckpoint, Vergleich und Entscheidungsregel

1. Erst nach bestätigtem Vertragscommit die drei festgeschriebenen Vorlagen
   jeweils einzeln an die getrennten Leser geben.
2. Jeden ersten vollständigen finalen Antworttext unverändert in separater
   UTF-8-Datei speichern. Keine Umschreibung oder Antwortnormalisierung.
3. Alle drei Antworten read-only setzen, SHA256 und Zuordnung zu den
   Vorlagehashes speichern; vor jeder Ergebnisvergleichsauswertung
   Antwortcheckpoint committen, pushen und remote bestätigen.
4. **Erst danach** die eingefrorene Erwartungen-Datei für den Vergleich lesen.
   Antwortdateien unverändert lassen, Auswertung getrennt speichern.
5. Jede Karte als KORREKT, FALSCH oder UNBEURTEILBAR bewerten und die sichtbare
   Begründung ausdrücklich prüfen. Ein bloß passendes Antwortwort genügt nicht.

R1 ist korrekt nur bei UNBEKANNT wegen fehlender Ressourcenbindung. Ein
Identitätsschluss aus Name, Alias, Projekt, Actorbindung, Nähe oder Reihenfolge
ist FALSCH. R2 ist korrekt nur bei DIESELBE aufgrund der ausdrücklich gültigen
Ressourcenbindung; R3 nur bei VERSCHIEDEN aufgrund des ausdrücklich gültigen
Wechselbelegs. Frage 3 darf keinen unbelegten realen Identitätsnachweis ergänzen.

- **SUPPORTED IN THIS TEST:** R1/R2/R3 entsprechen UNBEKANNT/DIESELBE/VERSCHIEDEN
  und die Begründungen tragen genau diese jeweiligen Informationsgrenzen.
- **NOT SUPPORTED:** Mindestens eine beurteilbare Karte falsch eingeordnet.
- **INCONCLUSIVE:** Design, Leserantwort oder Referenz erlaubt keine saubere
  Beurteilung. Eine solche Grenze nicht durch Vermutung schließen.

Die nutzerseitigen Ergebnisnamen gelten für diesen Versuch. Achse A der
[Methodik](RESEARCH-METHOD.md) bewertet hier keine neue Implementierung;
Standardsuite und Forschungsergebnis bleiben getrennt. Es sind genau drei
Papierkarten mit jeweils drei Fragen, keine neun unabhängigen Identitätstests.

## Standardsuite, Integrität, Bericht und STOPP

Nach gesichertem Vergleich gemäß Methodik §7/§11 die Standardsuite zweimal
identisch ausführen, ohne neue Filter oder Ausschlüsse:

```sh
PYTHONDONTWRITEBYTECODE=1 /workspace/venvs/authority/bin/python -m pytest \
  -p no:cacheprovider -o addopts='' -q
```

Vorhandene fünf RC-Deselektionen sichtbar erhalten. Kein Finish-Probeaufruf,
zusätzlicher Ressourcenfall oder neues Experiment. Kein Observer-/Sensorcode,
keine bestehenden Tests, IDs oder Felder verändern. Das
[Freeze-Manifest](observer-resource-epoch/2026-10-08/frozen-integrity.json)
enthält die Hashes aller 202 getrackten Ausgangsdateien; nach Vergleich und
Standardsuite erneut prüfen. Vertrags-/Karten-/Vorlage-/Erwartungsbytes ab
Freeze ebenfalls unverändert erhalten.

Neuer Ergebnisbericht mit Ausgangs-/Vertragscommit, exakten Karten,
wortgetreuen gesicherten Antworten, Bewertungen/Begründungen,
Alias-/Namensschlussfolgerungen, Aussagegrenzen, Suitebelegen sowie getrennt
CONFIDENCE IN EXPERIMENT RESULT und CONFIDENCE IN GENERALIZATION.
Neue Artefakte unter docs/observer-resource-epoch/2026-10-08/; Ergebnis als
eigenes Dokument. Historisches K14 bleibt INCONCLUSIVE; der neue Versuch
beantwortet allein seinen neu isolierten Informationsvergleich.

Nicht bewiesen: reale Ressourcenidentität, Quellechtheit/kryptografische IDs,
Symlinks/URLs/Dateien/Cloudobjekte/Datenbanken, Projektüberschreitung,
Revisionsidentität, notwendige künftige ID-Struktur oder ein vorhandener
AA-Ressourcensensor. E2-Metadaten-Lücke, OOS-021 und andere Forschungsfragen
werden durch diesen Test nicht geschlossen.

Nach Ergebnis Commit, Push, Remote-Bestätigung und Link. **Danach STOPP:**
keine Implementierung der Ressourcenbindung, kein nächster Test und keine
Observererweiterung.
