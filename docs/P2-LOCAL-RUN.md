# P2: ein lokaler Nachlauf an die Feldabbildung angeschlossen

9. Oktober 2026. Grundlage ist die abgenommene Abbildung
[PLAN-P1-FIELD-MAP-2026-10-09.md](PLAN-P1-FIELD-MAP-2026-10-09.md)
und Paket P2 in Abschnitt 5 des Entwicklungsplans. Diese Datei setzt P3 nicht um.

## Abnahme vor dem Lauf

Genau ein neuer Lauf im vorhandenen Modus `late` über `capture()`. Der Lauf
bindet Start, eine Werkzeugmeldung, den unabhängigen Dateibefund, `cli_end`
und den Nachlauf an eine `run`-ID. `agent_run=BELEGT` nur bei Modellabschluss,
Werkzeugmeldung und gültiger Aufzeichnung. Die Referenz wird erst nach der
Analyse gelesen. `tool_end` ist kein Wirkungsbeleg. Auftrag, Actor, Ursprung,
Prozessidentität, Pfad, Inhalt und `source_authenticated` bleiben UNBEKANNT.
Das Artefakt ist das vorhandene Werkzeug, das eine leere Testdatei anlegt.
Keine neuen Rechte, Gates, Secrets oder UI. Die Archive 03 und 04 bleiben
unberührt und sind nicht dieser Abschluss.

## Lauf

Archiv: [docs/p1-runs/2026-10-09-p2-local](p1-runs/2026-10-09-p2-local/binding.json).
Befehl: `scripts/p1_controlled_run.py --connect --mode late` mit Timeout 60
und Nachlauf 5, Exit 0. CLI `codex-cli 0.162.0`, Modell `gpt-6.1-sol`.
Lauf `6233001536916211328`.

| Feld | Wert |
|---|---|
| stdout / stderr | 1029 / 0 Bytes, 7 JSONL-Zeilen |
| Modellabschlüsse | 1 |
| Werkzeugmeldungen | 1, Exit erfolgreich |
| CLI | gestartet, Exit 0, kein Timeout, Aufzeichnung gültig |
| `agent_run` | `BELEGT` |
| Start | Ereignis 1, `target_initial=false` |
| Ende | Ereignis 3, `cli_end=true` |
| Wirkung | `BELEGT`, Ziel vorhanden, Beleg `[1, 3, 6]` |
| Nachlauf | `BELEGT`, Ordnung `NACH`, Beleg `[3, 4, 5]` |
| Referenz | ein Aufruf, Ziel vorhanden, gültig, Ordnung `NACH` |
| Bindung | `independent_local_effect`, Wirkung und Zeit `KORREKT` |

Die Abwesenheit liegt 48613643 ns nach `cli_end`, die Anwesenheit 22628681 ns
nach dieser Abwesenheit. Beide Differenzen sind die lokalen Monotonic-Zeiten
dieses Archivs. `startup_error` bleibt `UNBEKANNT`, weil stderr 0 Bytes hatte.
Die fünf Archivdateien enthalten keinen Prompt und keine Secretbytes.

Unbekannt bleiben Auftrag, Actor, Ursprung, Prozessidentität, Ressourcenpfad,
Ressourceninhalt und Quellenauthentisierung. Die Identitätsfunktion mit
`source_authenticated=false` wurde hier nicht ausgeführt. Der Dateiinhalt ist
kein Beobachtungsfeld.

## Archive 03 und 04

SHA-256 vor und nach dem Lauf unverändert.

| Datei | SHA-256 |
|---|---|
| 03 `analysis.json` | `5d128352cbaf991a75df8ece64eec8ccb5665689c7449223c36f0d6f0b172026` |
| 03 `observations.json` | `b25f07ac12dae176bbefd5c50698eb7da64eac0be24ffff6ce1457c4903d30ec` |
| 03 `reference.json` | `786a0e2f492d85934ae8b58884a1bb23b8d337b4234d4c1a4934b7908837af1c` |
| 03 `result.json` | `796318343769a49a6cf47584a31e5ab50f3d1e86e04d2bc837349f60796ca3e8` |
| 04 `analysis.json` | `f229c4d192c782866c2b257264a9e5a805dde109ad7fca5b95c995e3464cfcd9` |
| 04 `observations.json` | `910c6ac2100b5f17657db7b0eb01f95549e4d6c576354917e3a3b9efd915f6e9` |
| 04 `reference.json` | `24a90a55702e67b0131fba7775471e34c44a2f712191da75d4388d04be5f6cb6` |
| 04 `result.json` | `81ba1611ba37baf1ab4419e0b08a456643063ba68ee7e6bbf9707dc8882ad2af` |

## Prüfung

Neun Tests in `tests/test_plan_p2_local_connect.py`. Zusammen mit den drei
P1-Bindungstests: 12 bestanden. Gesamtsuite zweimal, jeweils Exit 0:
**282 passed, 5 deselected**. Pytest 9.1.1 hat im stillen Bericht keine
Sekundenzeile geschrieben. Ruff 0.16.1, Check und Format der beiden
Python-Dateien, bestanden.

## Historische rote Fälle, getrennt

RC-01–05 direkt über `tests/realcase/test_security_expectations.py`:
**5 failed, 5 passed**, Exit 1. OOS-021-Probe
`probes/test_finish_adapter_effect_atomicity_probe.py`: **1 failed**, Exit 1.
Keine dieser Lücken wurde geschlossen. CB-01 bleibt offen.

Ein Lauf belegt keine allgemeine Agentensicherheit, keinen Remote-Stopp und
keine Quellenauthentisierung. P3 ist nicht gestartet.
