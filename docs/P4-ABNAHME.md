# P4-Abnahme

Abnahme im engen Sinn von Paket P4 aus Abschnitt 5. Geprüft ist der Stand `065f45d73e7cb1d4bdb03717b157c4692cebc52a`, nicht ein späterer Commit. Prüfer A urteilt ABNAHME. Prüfer B urteilt STOP, weil Pytest trotz `-p no:cacheprovider` die gitignorierten Dateien `.pytest_cache/v/cache/lastfailed` und `.pytest_cache/v/cache/nodeids` beschrieben hat. Das ist ein Verfahrensbefund. Es ist keine Produkt-STOP-Bedingung aus Abschnitt 5. Die Sachbefunde beider Prüfer stimmen überein. Dieser Cache wird nicht angefasst, nicht zurückgesetzt und nicht committet.

Das ist keine Produktreife, keine allgemeine Agentensicherheit, kein Remote-Stopp und keine Quellenauthentisierung.

## Umgebung und geprüfter SHA

- Repo, gelesen: `/Users/landjunge/agent-authority-p1`
- Branch: `codex/p1-observer-20261009`
- Geprüfter SHA: `065f45d73e7cb1d4bdb03717b157c4692cebc52a`
- `uname -sm`: Darwin x86_64
- Abnahmelauf: Python 3.12.13 aus `.venv`, Pytest 9.1.1
- `python3` auf dem PATH der Prüfer ist Python 3.8.0. Das ist nicht die Projektlaufzeit. `pyproject.toml` verlangt Python `>=3.12`.

## Beobachteter Ablauf

P2-Lauf `6233001536916211328` ist ein archivierter später lokaler Lauf. Gespeichert ist `agent_run=BELEGT`. Das folgt aus den Zählern in `result.json`: `model_completions` 1, `tool_reports` 1. Dieser Modelllauf wurde heute nicht erneut ausgeführt. Ein Transkript dieses Laufs liegt im Archiv nicht.

P3-Lauf `2847465012503918159` hat `agent_run=UNBEKANNT`, weil kein Modellabschluss im Archiv steht. `result.json` dieses Laufs hat `model_completions` 0 und `proven_agent_runs` 0.

Die frische Dateibeobachtung beider Prüfer ist ein neuer Aufruf von `measure_controlled_late_effect`, kein Modelllauf. Prüfer A hat Lauf `1473720987521066741` gesehen. Prüfer B hat Lauf `2695239286801725928` auf Python 3.12.13 gesehen. Beide Aufrufe melden `agent_run=UNBEKANNT`.

## Wirkung

Beide Prüfer haben die frische Datei `target` selbst mit `lstat` gesehen: vorhanden, kein Symlink, reguläre Datei, Größe 0. Das stimmt mit `BELEGT` und `target_present=true` überein. Die Observer-Antwort enthält weder den Pfad noch den Inhalt.

## Zeitbezug

Auf Python 3.12 liegt der selbst gelesene Receipt nach `cli_end`. Die Ordnung ist `NACH`. Ein Ende ist keine Wirkungsfreiheit. Im archivierten P3-`assess.json` steht `ende_ist_wirkungsfreiheit` mit Aussage `NEIN` und Grund `end_is_an_event`.

Auf Python 3.8 war `monotonic_ns` in Prüfer Bs Messung prozesslokal. Die Ordnung des Belegs war `VOR`, der Beobachter sagte `NACH`, `timing_evaluation=FALSCH`. Diese 3.8-Messung trägt die Abnahme nicht. Das Projekt verlangt Python `>=3.12`.

Die archivierten Beobachtungen von P2 und P3 ergeben bei Neurechnung mit `relate` ebenfalls Ordnung `NACH`. Das ist die Ordnung der gespeicherten Ereignisse, nicht ein heutiger Dateizustand.

## Unbekannte Punkte

Der heutige Dateizustand der archivierten Ziele ist UNBEKANNT. Der Pfad der archivierten P2- und P3-Ziele ist ebenfalls UNBEKANNT. In den JSON-Dateien dieser Archive steht kein Zielpfad.

Auftrag, Actor, Ursprung, Prozessidentität, Ressourceninhalt und Herkunft sind UNBEKANNT. Die P2-Bindung setzt dieselben Punkte und dazu `resource_path` auf `UNBEKANNT`.

`source_authenticated=true` wird nicht als Herkunft gelesen. Beide Prüfer haben ein gesetztes `true` verworfen. Die Aussage bleibt `UNBEKANNT`, der Grund `forged_authentication`.

Der Datei-SHA-256 des gepinnten Verifiers ist UNBEKANNT, weil `f94f444e383052d04e2ef22bfed4ec03512cb066` in diesem Git-Objektbestand nicht liegt. Die Verifier-Datei wurde nicht gehasht. Der im Archiv stehende String ist nur gespeicherter Text, keine hier geprüfte Summe.

FD auf darwin bleibt `unsupported_platform`, keine Authentisierung. `fd-platform.json` nennt Plattform `darwin`, Maschine `x86_64`, Rückgabe `B` gleich `unsupported_platform` und `source_authenticated` falsch. Die Projektion sagt `UNBEKANNT` mit Grund `verifier_not_positive`.

## Quellenqualität

Die frische Aussage auf Python 3.12 stützt sich auf `lstat`, den selbst gelesenen Beleg und dieselben Funktionen, die das JSON erzeugen. Sie belegt eine lokale Wirkung an diesem Abfragepunkt, nicht die Herkunft und nicht einen Agentenlauf. Die frische Datei ist eine andere Datei als die archivierten Ziele.

Die Archive sind interne Konsistenz. `infer`, `relate`, `bind` und `assess` erzeugen aus den gespeicherten Ereignissen dieselben Felder wieder. Sie öffnen die damalige Datei nicht.

`reference.json` von P2 und P3 sind bytegleich, weil sie nur sechs Felder ohne Laufnummer tragen: `calls`, `target_present`, `valid`, `order`, `order_applicable`, `order_valid`. Selbst mit `shasum -a 256` gerechnet, beide Dateien:

`24a90a55702e67b0131fba7775471e34c44a2f712191da75d4388d04be5f6cb6`

`analysis.json` von P2 ist bytegleich mit `docs/p1-runs/2026-10-09-attempt-04/analysis.json`, weil dasselbe Urteilsobjekt ohne Laufnummer drinsteht. Selbst gerechnete Summe beider Dateien:

`f229c4d192c782866c2b257264a9e5a805dde109ad7fca5b95c995e3464cfcd9`

Die `observations.json` dieser Läufe sind nicht bytegleich. Selbst gerechnet:

- P2 `observations.json`: `0f49f878f5af6a78ac22ed51f950e15f2480cfd650b3f7f96ba1db35e35e0a4d`
- P3 `observations.json`: `ef063a8295202e3d5c864938e38e8a195ddc4bd32339249ed4978a6e08d7f356`
- `docs/p1-runs/2026-10-09-attempt-04/observations.json`: `910c6ac2100b5f17657db7b0eb01f95549e4d6c576354917e3a3b9efd915f6e9`

Weitere selbst gerechnete Summen, gleich den Prüferberichten:

- P2 `binding.json`: `845a72645e174b6e7555084f62acdfbd71748ff594db146c8b7fcb97843a2b74`
- P2 `result.json`: `932ecf6fc554ef3c8b14d20d7b1d490321de2783589129cd77b72df39d26d99a`
- P3 `assess.json`: `2db8600a77f408d2bc75bd35efeb36534115dde48f6e540cd9a441012691d425`
- P3 `fd-platform.json`: `22371b4133995f4c1da8dd64b8faba58a996149c128be17b8a29c2b41ddd34d5`
- P3 `result.json`: `b1b31fc3086ea3cf760a0b7cbc3c1a482ae192c9648722fb19ac5adeb9910eac`
- `scripts/p1_controlled_run.py`: `da9dfd5faa4eceec1609fb265998756ffcbb275da4bb19cfcc8cfde34fbb56d8`

## Datenwahl

Jedes Ereignis hat genau fünf Felder: `run`, `kind`, `value`, `t_ns`, `event`. `value` ist boolesches Vorhandensein. Pfad und Inhalt stehen nicht im Observer-JSON.

## Offene Lücken

Diese Lücken sind nicht geschlossen. Beide Prüfer haben sie auf Python 3.12 ausgeführt.

RC-01 bis RC-05: 5 failed und 5 passed, Exit 1. Die fünf Fehlschläge sind RC-01, RC-02, RC-03, RC-04 und RC-05.

Die OOS-021-Probe `probes/test_finish_adapter_effect_atomicity_probe.py` ist 1 failed, Exit 1.

CB-01 bleibt MISSED, nicht repariert. In `docs/CONVERGENCE-BATTERY-v1-RESULTS.md` steht in Zeile 17:

```text
| CB-01 | Approval-token reuse | `I6_IRREVERSIBLE` | **MISSED** | **yes** |
```

Dieselbe Datei, Zeile 49:

```text
One truthy `approval_token` authorized both `repo.delete` and `release.publish` in one workflow. I6 checks token presence per action. It does not bind a token to one irreversible effect. The forbidden pair is in `irreversible_effects`. This item was **not** repaired.
```

In `docs/OUT-OF-SCOPE-DEBT.md`, Zeile 30, nennt OOS-020 CB-01 und endet mit dem Status `ACCEPTED MODEL LIMITATION`, nicht mit geschlossen:

```text
| OOS-020 | Approval-Token ist ein reiner Wahrheitswert; nicht an Actor, Aktion, Ressource, Workflow oder Generation gebunden (RC-03/04/05, CB-01) | High | Same core as OOS-015 (truthy flags; ACCEPTED MODEL LIMITATION) | Yes — I6 as bound capability | Real-case transfer RC-03/04/05; convergence CB-01 | Token binding (not authorized) | ACCEPTED MODEL LIMITATION |
```

Zeile 31 derselben Datei hält OOS-021 auf `OPEN`:

```text
| OOS-021 | Authorization-to-effect after `finish()`: an already-authorized FakeAdapter write can still mutate FakeRepo after `finish()` returned | High | v0.2 specifies no atomic adapter commit; finding-only | Yes — a finished generation must not produce later effects | `docs/FINDING-PHASE1-FINISH-ADAPTER-EFFECT-GAP.md`; red-first probe `probes/test_finish_adapter_effect_atomicity_probe.py` | Atomic adapter commit / generation token (not authorized) | OPEN |
```

Nichts davon wurde repariert oder abgeschwächt.

## Prüferurteile

Prüfer A: ABNAHME im engen Sinn dieser Prüffrage. Die eigene Stat-Beobachtung der frischen Datei stimmt mit der Wirkungsaussage überein. Die Neurechnung der Archive weicht in keinem genannten Feld ab. Fehlende Herkunft bleibt sichtbar. Die roten Fälle blieben rot.

Prüfer B: STOP. Die Sachaussage auf Python 3.12 stimmt mit Prüfer A überein. Abnahme wurde dort nicht erteilt, weil die Prüfung zwei gitignorierte Cache-Dateien im Repo verändert hat: `.pytest_cache/v/cache/lastfailed` und `.pytest_cache/v/cache/nodeids`. `git status --porcelain` zeigt sie nicht. Sie wurden nicht zurückgesetzt.

Keine allgemeine Agentensicherheit. Kein Remote-Stopp. Keine Quellenauthentisierung.
