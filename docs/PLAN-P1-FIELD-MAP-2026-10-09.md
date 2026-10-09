# P1 — Feldabbildung vorhandener Eingänge und Ausgaben

Schritt-ID: **P1** aus dem Gesamtentwicklungsplan
`docs/agent-authority/ENTWICKLUNGSPLAN-AUS-ALLEN-FORSCHUNGSSTAENDEN-2026-10-09.md`
in `ki-zentralle-d012-20261009`, Abschnitt 5. Ausgabe dieses Schritts ist
diese Abbildung. Sie fügt kein Schema, kein Modul, kein Gate und kein Recht
hinzu.

Gemessen am 9. Oktober 2026:

- Forschungsfunktionen am Checkout
  `feat/observer-wb-automation`, SHA `f94f444e383052d04e2ef22bfed4ec03512cb066`.
- Runner dieses Branchs in `scripts/p1_controlled_run.py`, Stand vor dieser
  Abbildung `79342e8ee6b57ab3e7921b076a85ffc76f7cf308`.

`docs/p1-runs/` bleibt unverändert. Ein späteres PASS schließt RC-01–05,
CB-01 oder OOS-021 nicht.

## Abnahme

Ein durchgehendes Beispiel mit künstlichen Werten bindet an vorhandene
Funktionen. Fehlende Daten bleiben UNBEKANNT. `answer=None` aus
`observer_research.infer` ist diese Unbekannt-Aussage, keine verneinende
Sachantwort. Ein direkter CLI-Fehler wird nicht als belegter Agentenlauf
ausgegeben.

## Zwei vorhandene Eingänge, kein gemeinsames Schema

| Eingang | Nimmt an | Gibt aus | Grenze |
|---|---|---|---|
| `observer_research.check_events` / `infer` | genau `run`, `kind`, `value`, `t_ns`, `event`; `kind` aus `tool_end`, `cli_end`, `native_end`, `target_probe`, `target_final` | `answer`, `reason`, `evidence` | Sechs-Fall-Panel. Kein Actor, kein Prozess, kein Auftragstext. |
| `observer_research.infer_finish_effect` | `run`, `kind`, `value`, `t_ns`; andere `kind`-Menge | `answer` `JA`/`NEIN`/`UNBEKANNT`, `reason`, `evidence` als Kindnamen | Fake-Lab-Sensor. Keine Quellechtheit. |
| `infer_current_local_file_identity` | Ereignisse plus gehaltene FDs | `A`/`B`/`C`/`D` | Linux/tmpfs. Fehlender Beleg: `A=UNBEKANNT`. |
| `verify_current_fd_identity` | Ereignisse, Lauf, Observerresultat, FDs | unter anderem `source_authenticated: False` | Positiver Rückgabeweg setzt dieses Feld weiter auf `False` (Funktion, Zeile 525). Hier nicht ausgeführt. |
| `scripts/p1_controlled_run.py` `add` / `infer` / `relate` / `project` | dieselbe Fünf-Feld-Menge; `kind` aus `target_initial`, `target_absent`, `target_seen`, `target_final`, `tool_end`, `cli_end` | `verdict` `BELEGT`/`UNBEKANNT`/`NICHT_ANWENDBAR`, optional `order` `VOR`/`NACH` | Ein Lauf. Nachlauf nur Modus `late`, Fenster `(0, 30]` Sekunden, Standard 5. |

Der festgelegte Agentenweg dieses Branchs ist `capture()`: ein
`codex exec --json --ephemeral` mit `--model gpt-6.1-sol`. Ein CLI-Start
ohne Modellabschluss und Werkzeugmeldung bleibt `agent_run=UNBEKANNT`.
Der Forschungsdriver bleibt ein Sechs-Fall-Panel und ist dieser Weg nicht.

## Künstliche Beispiele

Beispiel A, Forschungs-`infer`, Lauf 1. Gemessen:

```json
[
  {"run": 1, "kind": "cli_end", "value": true, "t_ns": 20, "event": 1},
  {"run": 1, "kind": "target_probe", "value": false, "t_ns": 25, "event": 2},
  {"run": 1, "kind": "target_probe", "value": true, "t_ns": 30, "event": 3},
  {"run": 1, "kind": "target_final", "value": true, "t_ns": 40, "event": 4}
]
```

| Frage | Ausgabe |
|---|---|
| `target_present` | `answer=true`, `reason=explicit_local_snapshot`, `evidence=[1,2,3,4]` |
| `appearance_vs_cli_end` | `answer=after`, `reason=absence_lower_bound_after_end`, `evidence=[1,2,3,4]` |
| nur `target_final` gegen `appearance_vs_cli_end` | `answer=null`, `reason=insufficient_observed_data`, `evidence=[1]` |

`null` wird als UNBEKANNT gelesen.

Beispiel B, Runner dieses Branchs. Dieselbe künstliche Ordnung in den
Runner-Arten. Gemessen über `infer` und `relate`:

```json
[
  {"run": 1, "kind": "target_initial", "value": false, "t_ns": 10, "event": 1},
  {"run": 1, "kind": "tool_end", "value": true, "t_ns": 15, "event": 2},
  {"run": 1, "kind": "cli_end", "value": true, "t_ns": 20, "event": 3},
  {"run": 1, "kind": "target_absent", "value": false, "t_ns": 25, "event": 4},
  {"run": 1, "kind": "target_seen", "value": true, "t_ns": 30, "event": 5},
  {"run": 1, "kind": "target_final", "value": true, "t_ns": 40, "event": 6}
]
```

| Funktion | Ausgabe |
|---|---|
| `infer` | `verdict=BELEGT`, `target_present=true`, `reason=local_snapshot_only`, `evidence=[1,3,6]` |
| `relate` | `verdict=BELEGT`, `order=NACH`, `reason=absence_after_end_then_presence`, `evidence=[3,4,5]` |
| nur `cli_end` mit `value=false` | `verdict=UNBEKANNT`, `target_present=null`, `reason=missing_evidence` |
| dasselbe Beispiel plus Feld `actor` | `reason=invalid_evidence` |

Beispiel C, `infer_finish_effect`, künstliche Zeiten 10, 20, 30, 40, 50 für
`write_started`, `finish_return_before`, `finish_return`,
`write_effect_before`, `write_effect`. Gemessen: A `JA` /
`finish_before_observed_write_effect`; B `JA` /
`same_observed_write_binding`; C `JA` /
`one_observed_write_after_finish_other_effects_unknown`. Nur
`write_started`: A `UNBEKANNT` / `missing_write_evidence`. C sagt nichts
über unbeobachtete weitere Wirkungen.

Beispiel D, `infer_current_local_file_identity([], 1)`: `A=UNBEKANNT`.
Ein leerer FD-Vergleich wird nicht zur Identität.

## Abbildung der Plandaten

| Benötigte Information | Gebunden an | Wenn der Beleg fehlt |
|---|---|---|
| Testlauf | `run` in beiden Eingängen | Forschungsfunktion: keine Zuordnung. Runner: `invalid_run` oder `UNBEKANNT`. |
| Auftrag | kein Eingangsfeld. `result.mode` nennt nur den Versuchsmodus | UNBEKANNT. Kein Threadtitel. |
| Ereignisreferenz | `event` beziehungsweise Kindname in der Finish-Evidenz | ungültige Zeile, Aussage UNBEKANNT |
| Ereignisart | `kind`, je Eingang eine eigene Menge | verworfen, nicht in die andere Menge übersetzt |
| Ursprungsreferenz | kein Feld | UNBEKANNT |
| gemeldeter Actor | kein Feld; Zusatzfeld scheitert am Runner | UNBEKANNT |
| beobachteter Prozess | keine PID im Archiv | UNBEKANNT. Prozessnummer wäre über Lebenszeiten nicht eindeutig. |
| Zeit und lokale Ordnung | `t_ns`; Fragen `appearance_vs_*` oder `relate` | `null` beziehungsweise `UNBEKANNT` |
| Gültigkeitsfenster | Identitätstexte `C`/`D`; Runner-`scope` nur für den lokalen Abfragepunkt | keine allgemeine Gültigkeit |
| Ressourcenbezug | boolesches Vorhandensein, kein Pfad und kein Inhalt | UNBEKANNT |
| Abschluss und Wirkung | `cli_end` getrennt von `target_final` / `target_seen`; Finish-Rückkehr getrennt von `write_effect` | fehlende Seite bleibt UNBEKANNT |
| Beleg und Herkunft | `evidence`; FD-Feld `source_authenticated=false` | UNBEKANNT. Eine FD-Relation authentisiert die Ressource nicht. |
| Befund | `answer` oder `verdict`, plus `reason` | UNBEKANNT, nicht als Sicherheit lesen |

`capture` setzt `agent_run` nur dann auf `BELEGT`, wenn `model_completions > 0`,
`tool_reports > 0` und `recording_ok` gilt. `project` macht aus `error` und
`turn.failed` keine Modell- oder Werkzeugereignisse: gemessen zwei
`error_records`, null Ereignisse, null Modellabschlüsse, null
Werkzeugmeldungen. Exit 0 allein erfüllt die Konjunktion nicht.

## Nächster Schritt

**P2 — den einen echten lokalen Ablauf anschließen.** Input ist diese
abgenommene Abbildung plus die vorhandenen Bausteine und ein künstliches
Testartefakt. P2 ist mit dieser Datei nicht begonnen. Die bereits
archivierten Läufe 03 und 04 bleiben Belege des Runners; sie werden hier
nicht nachträglich zum P2-Abschluss erklärt.
