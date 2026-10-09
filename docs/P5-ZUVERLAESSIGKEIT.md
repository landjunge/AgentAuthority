# P5: Zuverlässigkeit bei fehlenden, alten und manipulierten Belegen

Ein Lauf. Kein zweiter Versuch. Paket `PASS`, `stop_reason` leer. Das ist keine allgemeine Agentensicherheit, kein Remote-Stopp und keine Quellenauthentisierung.

## Umgebung

- `uname -sm`: Darwin x86_64
- Python 3.12.13, Pytest 9.1.1, Ruff 0.16.1
- CLI `codex-cli 0.162.0`
- Modell aus der Konstanten `MODEL`: `gpt-6.1-sol`. Dasselbe steht als `requested_model` im Archiv.
- Geprüfter Ausgangs-SHA: `1a2d24d3a631419a59cc7688c2393babb4977a64`
- Erwartung vor dem Lauf, SHA-256 unverändert: `eff432d4c5ee4f305d98d287510273a22e531c09895ae58822dece204c15c0c1`

## Lauf

Archiv `docs/p1-runs/2026-10-09-p5-reliability`. Laufnummer nur von dort: `7027111266611887455`.

`connect()` lieferte `agent_run=BELEGT` und Bindungsgrund `independent_local_effect`. Die Zähler sind `model_completions` 1, `tool_reports` 1, `recording_ok` wahr, `proven_agent_runs` 1. CLI-Exit 0, kein Timeout, `invalid_records` 0. `stdout_bytes` 1020, `stderr_bytes` 152. `startup_error` bleibt `UNBEKANNT`; der stderr-Text ist nicht archiviert und wird hier nicht zitiert.

`measure_controlled_late_effect` war dieser Lauf nicht.

## Erwartet und Ist

| Fall | Erwartet | Ist | Status |
|---|---|---|---|
| aktuell | Wirkung `BELEGT`, Ziel vorhanden, Geltung `lokaler_abfragepunkt`, Grund `local_snapshot_only`. Zeit `BELEGT`, Ordnung `NACH`, Grund `absence_after_end_then_presence`. Ende `NEIN` / `end_is_an_event`. Identität `UNBEKANNT` / `no_identity_measurement`. Herkunft `UNBEKANNT` / `no_source_field`. `agent_run=BELEGT`, Bindung `independent_local_effect`, `recht_uebernommen` falsch, `fehler` leer. Referenz `valid`, `calls` 1, Ziel vorhanden, Ordnung `NACH`, `order_valid` und `order_applicable` wahr. Bewertung und Zeitbewertung `KORREKT`. | dieselben Aussagen. Wirkungsbeleg `[1, 3, 6]`, Zeitbeleg `[3, 4, 5]` | PASS |
| fehlend | Nur die echte `cli_end`-Zeile, Klasse `missing`, Referenz leer. Wirkung und Zeit `UNBEKANNT`, Zeitgrund nicht `no_effect`, Ende `NEIN`, Identität `missing_evidence`, Herkunft `UNBEKANNT`, `agent_run` `UNBEKANNT`, keine authentisierte Herkunft | so gelesen | PASS |
| alt_geordnet | Geordnete Originalzeilen, Klasse `stale`. Wirkung darf `BELEGT` bleiben, Geltung `UNBEKANNT`, Identität `stale_source`, Herkunft `UNBEKANNT`. Keine aktuelle Identität | Wirkung `BELEGT`, Geltung `UNBEKANNT`, `stale_source` | PASS |
| alt_zusatzfelder | `live`, `released` und ein künstlicher Name auf der letzten Zeile. Wirkungsgrund `invalid_evidence`, Geltung `UNBEKANNT`, Identität `stale_source`, Name nicht im JSON | `invalid_evidence`, Name nicht im JSON | PASS |
| gefaelscht_agentenlabel | `model_completions` 0, Label `BELEGT`, `proven_agent_runs` 1, Klasse `forged`. `agent_run=UNBEKANNT`, `forged_source`, Herkunft `UNBEKANNT`, kein übernommenes Recht | `UNBEKANNT`, `forged_source` | PASS |
| gefaelscht_fd_flag | `source_authenticated=true` im Claim. Aussage `UNBEKANNT`, Grund `forged_authentication`, nicht als wahr übernommen | `UNBEKANNT`, nicht als wahr übernommen | PASS |
| packet_ohne_messung | Konsistentes FD-Packet ohne Messung: `UNBEKANNT` / `unmeasured_packet_not_identity` | derselbe Grund | PASS |
| fd_format_keine_hostmessung | Positive Form mit `source_authenticated=false` darf die Relation behalten und das Feld falsch lassen. Keine Hostmessung, keine Herkunft | `DIESELBE`, `source_authenticated` falsch, `recht_uebernommen` falsch | PASS |
| host_verifier | `verify_current_fd_identity`: SKIP, Datei nicht in diesem Checkout. Kein SHA von `f94f444` als hier geprüft | SKIP, `datei_nicht_in_diesem_checkout` | SKIP |

Ein SKIP der Host-FD-Datei ist kein Positivbeleg und kein Paketfehler. Eine positive FD-Relation wurde auf diesem Host nicht gemessen.

## Wirkung, Zeit, Unbekannt

Wirkung und Zeit sind belegt und voneinander getrennt zu lesen. Die Wirkung ist der lokale Abfragepunkt: Ziel vorhanden, Grund `local_snapshot_only`. Die Zeit ist Ordnung `NACH` nach dem Ende, Grund `absence_after_end_then_presence`. Ein Ende ist keine Wirkungsfreiheit.

Unbekannt bleiben Identität, Herkunft, Auftrag, Actor, Ursprung, Prozessidentität, Ressourcenpfad, Ressourceninhalt und `source_authenticated`. Eine alte Quelle ist keine aktuelle Identität. Ein gefälschtes Label oder ein gesetztes `source_authenticated=true` wird nicht übernommen. Das FD-Format ohne Hostmessung ist keine Herkunft.

Die unabhängige Referenz entstand im Lauf nach der Analyse durch Receipt plus `lstat`. Der Prüfer muss die behaltene Datei selbst sehen. Der heutige Zustand nach späterem Löschen ist dann unbekannt. Der behaltene Zielpfad steht nicht in diesem Bericht und nicht im Observer-JSON.

## Datenwahl

Jedes archivierte Ereignis hat genau die fünf Felder `run`, `kind`, `value`, `t_ns`, `event`. `value` ist boolesches Vorhandensein. Kein Prompt, kein Pfad und kein Dateiinhalt im Observer-JSON.

Die Archive `2026-10-09-attempt-03`, `2026-10-09-attempt-04`, `2026-10-09-p2-local` und `2026-10-09-p3-controlled` sind bytegleich zu den SHA-256 vor diesem Lauf. `scripts/p1_controlled_run.py` ist unverändert.

## Offene Grenzen

Keine Reparatur. RC-01 bis RC-05, direkt `tests/realcase/test_security_expectations.py`: **5 failed, 5 passed**, Exit 1. Die Fehlschläge sind RC-01, RC-02, RC-03, RC-04 und RC-05.

OOS-021, `probes/test_finish_adapter_effect_atomicity_probe.py`: **1 failed**, Exit 1.

CB-01 bleibt offen. Diese Prüfung hat die Konvergenzbatterie nicht als Reparatur gelesen und nichts davon geschlossen.

Der P4-Pytest-Cache bleibt ein Verfahrensbefund. In diesem Worktree ist nach den Läufen mit Cache unter `/tmp/aa-p5-pytest-integrator` und `-p no:cacheprovider` kein `.pytest_cache` entstanden. Das repariert den Befund nicht. Es wurde nichts gelöscht und nichts committet.

## Prüfung

Fünf Tests in `tests/test_plan_p5_reliability.py`. Keiner startet Codex. Gesamtsuite zweimal, jeweils Exit 0: **326 passed, 5 deselected**, 16,88 s und 16,89 s. Ruff 0.16.1, Check und Format der beiden neuen Python-Dateien, bestanden.
