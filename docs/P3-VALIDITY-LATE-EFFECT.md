# P3: Gültigkeit und Späteffekt am P2-Ablauf

9. Oktober 2026. Grundlage ist Paket P3 in Abschnitt 5 des Entwicklungsplans
`ENTWICKLUNGSPLAN-AUS-ALLEN-FORSCHUNGSSTAENDEN-2026-10-09` und der
abgeschlossene Anschluss in
[P2-LOCAL-RUN.md](P2-LOCAL-RUN.md). Diese Datei ist die Erwartet-/Ist-Tabelle.
Sie setzt P4 nicht um und ändert den P2-Lauf nicht.

## Fälle

Gleicher Eingang wie P2: `infer`, `relate` und `bind` in
`scripts/p1_controlled_run.py`. Kein neues Ereignisschema, kein Gate, kein
Recht. Auftrag, Actor, Ursprung, Prozessidentität, Pfad und Inhalt bleiben
UNBEKANNT. Ein gemeldetes Ende ist kein Beleg für Wirkungsfreiheit.

| Fall | Frage | Erwartet | Ist | Beleg |
|---|---|---|---|---|
| P2-Lauf `6233001536916211328`, neu aus Beobachtung und Referenz gerechnet | Wirkung | BELEGT, Ziel vorhanden | BELEGT, `local_snapshot_only`, Geltung lokaler Abfragepunkt | `[1, 3, 6]` |
| derselbe Lauf | Zeitbezug | NACH | NACH, `absence_after_end_then_presence` | `[3, 4, 5]` |
| derselbe Lauf | Ende bedeutet Wirkungsfreiheit | NEIN | NEIN, `end_is_an_event` | keine |
| derselbe Lauf | Identität | UNBEKANNT | UNBEKANNT, `no_identity_measurement` | keine |
| derselbe Lauf | Herkunft | UNBEKANNT | UNBEKANNT, `no_source_field` | keine |
| derselbe Lauf | Agentenlauf | BELEGT | BELEGT, Bindung `independent_local_effect` | Modellabschluss und Werkzeugmeldung des vorhandenen Laufs |
| nur `cli_end` | Wirkung und Zeitbezug | UNBEKANNT | UNBEKANNT, Grund nicht `no_effect` | keine |
| nur `cli_end` | Identität und Herkunft | UNBEKANNT | UNBEKANNT, `missing_evidence` und `no_source_field` | keine |
| nur `cli_end` | Ende bedeutet Wirkungsfreiheit | NEIN | NEIN | keine |
| geordnete Zeilen, Quelle als alt markiert | Wirkung | Aufzeichnung darf BELEGT sein | BELEGT | `[1, 3, 6]` |
| geordnete Zeilen, Quelle als alt markiert | Geltung und Identität | nicht aktuell | Geltung UNBEKANNT, Identität `stale_source` | keine |
| Zeile mit `live`, `released` und Identitätsname | Identität | UNBEKANNT, Name nicht gespeichert | UNBEKANNT, `stale_source`; Zeile `invalid_evidence` | keine |
| `agent_run=BELEGT` ohne Modellabschluss | Agentenlauf und Herkunft | UNBEKANNT | UNBEKANNT, `forged_source`, `no_source_field` | keine |
| konsistentes FD-Packet ohne Messung | FD-Relation | UNBEKANNT | UNBEKANNT, `unmeasured_packet_not_identity` | keine |
| Packet mit `source_authenticated=true` | Herkunft | UNBEKANNT | UNBEKANNT, `forged_authentication` | keine |
| kontrollierte Datei nach Ende, Lauf `2847465012503918159` | Wirkung | BELEGT | BELEGT, `local_snapshot_only` | `[1, 3, 6]` |
| derselbe kontrollierte Lauf | Zeitbezug | NACH | NACH | `[3, 4, 5]` |
| derselbe kontrollierte Lauf | unabhängige Referenz | ein Aufruf, Ziel vorhanden, Ordnung NACH | `valid`, `calls=1`, `target_present=true`, `order=NACH`, Bewertung KORREKT | Receipt-Intervall beginnt nach `cli_end`; die Datei ist eine reguläre Datei |
| derselbe kontrollierte Lauf | Agentenlauf, Identität, Herkunft | UNBEKANNT | UNBEKANNT | kein Modellaufruf |
| gepinnter Verifier `verify_current_fd_identity` auf diesem Host | FD-Relation | keine erfundene Positive | `A=UNBEKANNT`, `B=unsupported_platform`, `source_authenticated=false` | Datei-SHA-256 `ace82c48bdc04e9faa707b28fd208378f06836a3b57876d729721c3f9dd6cead` an `f94f444e383052d04e2ef22bfed4ec03512cb066` |
| gepinntes Positivformat, das der Verifier auf Linux zurückgeben kann | FD-Relation | DIESELBE oder VERSCHIEDEN bleibt | DIESELBE und VERSCHIEDEN bleiben, `source_authenticated=false`, `recht_uebernommen=false` | keine Hostmessung |
| dasselbe Format mit `source_authenticated=true` | Herkunft | UNBEKANNT | UNBEKANNT, `forged_authentication` | keine |
| dasselbe Format ohne `fd_set_verified` | FD-Relation | UNBEKANNT | UNBEKANNT, `verifier_not_positive`, `source_authenticated=false` | konsistente Werte sind keine Messung |

Die Kontrollbelege des Dateilaufs liegen in
[docs/p1-runs/2026-10-09-p3-controlled](p1-runs/2026-10-09-p3-controlled/).
Der P2-Lauf liegt unverändert in
[docs/p1-runs/2026-10-09-p2-local](p1-runs/2026-10-09-p2-local/).
Keines der Archive enthält einen Prompt oder Secretbytes.

## Grenzen

Eine positive FD-Relation wurde auf diesem Host nicht gemessen. Der gepinnte
Verifier lief einmal unter `darwin`/`x86_64` und blieb wegen
`unsupported_platform` bei UNBEKANNT. Die Zeile zum Positivformat prüft nur
die Rückgabeform aus dem gepinnten Code. Sie ist keine Beobachtung eines
FD-Paars. Ob eine Messung auf Linux/tmpfs hier positiv wäre, ist unbekannt.

`positive_identity_authorized` steht im Rohrückgabewert dieses Aufrufs auf
`false` und wird nicht als Recht übernommen. Aktuelle Ressourcenidentität,
Epochen und K14 bleiben offen. Pfad und Inode sind keine Herkunft.

Archive 03 und 04 haben dieselben SHA-256 wie im P2-Abschluss. OOS-021 bleibt
die unveränderte historische rote Probe. CB-01 bleibt offen. Kein Lauf schließt
eine allgemeine Agentensicherheit oder einen Remote-Stopp.

## Prüfung

Neun Tests in `tests/test_plan_p3_validity.py`, darunter der kontrollierte
Dateilauf und das Lesen der beiden Archive. Gesamtsuite zweimal, jeweils
Exit 0: **291 passed, 5 deselected**, 12,57 s und 12,70 s. Pytest 9.1.1.
Ruff 0.16.1, Check und Format der beiden Python-Dateien, bestanden.

## Historische rote Fälle, getrennt

RC-01–05 direkt über `tests/realcase/test_security_expectations.py`:
**5 failed, 5 passed**, Exit 1. OOS-021-Probe
`probes/test_finish_adapter_effect_atomicity_probe.py`: **1 failed**, Exit 1.
Keine dieser Lücken wurde geschlossen.

P4 ist nicht gestartet.
