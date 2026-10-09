# P1: Implementierung, tatsächlicher Startversuch und Grenzen

**Aktueller Stand:** [Versuch 04](#fortsetzung-versuch-04-verspätete-wirkung)
belegt an einem echten Agentenlauf eine Dateiwirkung nach dem gemeldeten
CLI-Ende und ordnet sie als `NACH` zu. [Versuch 03](#fortsetzung-versuch-03-echter-agentenlauf)
bleibt der Beleg für die Wirkung am Fensterende ohne Zeitaussage. Der
Sandbox-Startblocker aus [Versuch 02](#fortsetzung-startdiagnose-und-versuch-02)
bleibt für Läufe innerhalb der Codex-Seatbelt dokumentiert. Der ursprüngliche
Befund von Versuch 01 folgt unverändert.

9. Oktober 2026. Grundlage: [vorab gespeicherter P1-Vertrag](P1-CONTROLLED-RUN.md)
und der unverändert kopierte [Forschungsplan](OBSERVER-REAL-RUN-PROTOTYPE-PLAN-2026-10-07.md).
Der Vertrags-Hash blieb seit Beginn der Implementierung unverändert:
`6d473e188fb60968ec94471c71cd7da7f1590336e9cdf85413d90b44af5bd264`.

## Ergebnis zuerst

Der kleine Mess-/Auswertungsweg ist implementiert und getestet. Der reale
CLI-Zugang konnte in dieser Umgebung keinen belegten Agentenlauf liefern.
**Ein tatsächlich gestarteter CLI-Prozess, null belegte Modell-/Agentenläufe,
null Werkzeugmeldungen, null instrumentierte Werkzeugaufrufe.** Kein Fake- oder
Unit-Test-Lauf wurde als reales Agentenergebnis archiviert.

[Messarchiv](p1-runs/2026-10-09-attempt-01/result.json): Der CLI-Prozess endete
erfolglos, ohne stdout-JSONL; stderr umfasste 199 Bytes. Fehlertext wurde nicht
archiviert. Die genaue Startfehlerursache, Authentisierung und Modellverfügbarkeit
sind damit nicht diagnostiziert. Keine Aufhebung von Sandboxregeln, kein
Credential-/HOME-/CODEX_HOME-Ersatz und kein nativer Ersatzlauf.

Der unabhängige Dateisensor belegt **nur**: das lokale Testziel war vor dem
Versuch und am Ende des Messfensters nicht vorhanden. Das ist ein gültiger
negativer Zustandsbefund, keine Behauptung über eine Agentenwirkung. Da die
separate Werkzeugreferenz fehlt, sind Agentenlauf und Referenzbewertung
**UNBEKANNT**. Ein erfolgreicher realer P1-Agentenlauf bleibt ausstehend.

## Implementierung und Belegtrennung

[`scripts/p1_controlled_run.py`](../scripts/p1_controlled_run.py) verwendet nur
die Standardbibliothek, keine Labmodule oder neue Produktkomponenten. Ein
temporäres Testwerkzeug kann ein leeres Ziel anlegen. Die Auswertung importiert
keine Autorisierungslogik und entscheidet keine Agentenrechte.

| Archiv | Funktion |
|---|---|
| `observations.json` | Laufgebundene Anfangs-/Endmessung, tatsächlich gemessener CLI-Endempfang, vorhandene projizierte Werkzeugmeldungen. Nur fünf begründete Planfelder. |
| `analysis.json` | Zielzustandsaussage aus den Beobachtungen; vor Lesen der Referenz gespeichert. Fehlende/ungültige/widersprüchliche Belege oder Aufzeichnungsfehler ergeben UNBEKANNT. |
| `reference.json` | Nachgelagerte getrennte Werkzeugreferenz, tatsächliche Aufrufzahl und zusätzliche Dateiprüfung. Fehlende Referenz erzeugt keinen Sollwert. |
| `result.json` | Prozess-/Aufzeichnungszähler, belegte Agentenläufe, Zustandsaussage und Referenzvergleich getrennt. |

Die Dateiprüfung übernimmt weder Werkzeugstatus noch Agentenprosa. Identische
Ereignisduplikate sind idempotent; geänderte gleiche Referenzen und mehrere
Endbelege sind unentscheidbar. Vorhandene Symlinks/Sonderdateien liefern keinen
positiven Zielbeleg. Erfolgreiche Werkzeug-/CLI-Meldungen allein bleiben unbekannt;
eine tatsächlich vorhandene Datei kann trotz Werkzeugfehler belegt sein.

Streams sind auf 64 KiB pro stdout-Zeile und etwa 1 MiB insgesamt begrenzt;
maximal ein zusätzlicher 8-KiB-Leseblock kann vor der Grenzprüfung anfallen.
Die CLI-Laufzeit ist begrenzt. Prozesspflege betrifft nur die eigene lokale
Prozessgruppe. Archivfehler werden weitergegeben und nicht als Erfolg verschluckt.
Neue Ausgabeverzeichnisse verhindern Überschreiben früherer Versuche.

## Tatsächlich ausgeführte Prüfungen

- Ausgangssuite vor Änderungen: 213 bestanden; bestehende RC-Ausschlüsse.
- 35 neue Tests: Status/Wirkung auseinanderhalten, fehlende/falsche Laufbindung,
  fehlende/konfligierende Belege, Duplikate, Reihenfolge, strenge primitive
  Projektion, Canary-Ausschluss, Referenztrennung, Sensorfehler und Symlinks.
  Tatsächliche lokale Prozesse testen Werkzeugvarianten, fehlerhafte/zu große/
  tief verschachtelte Eingaben sowie Timeout. Synthetische CLI-Ereignisse sind
  ausdrücklich Unit-Testdaten, keine realen Modellläufe.
- Gesamtsuite zweimal: **248 passed, 5 deselected**, 9,54 s und 9,40 s.
- Ruff für beide neuen Python-Dateien: Check und Formatprüfung bestanden.
- Historische Lücken separat nachgeprüft: RC-01–05 weiterhin rot
  (**5 failed, 5 passed**); OOS-021-Probe weiterhin rot (**1 failed**).
  Alte Tests und Labcode wurden nicht verändert; diese Befunde bleiben offen.

Der reale Versuch fand während der Implementierung statt. Danach wurden nur
Validierung für fehlerhafte Testeingaben und Formatierung vervollständigt.
Die archivierten Beobachtungen wurden mit der finalen Auswertung erneut geprüft;
ihre Aussage ist unverändert. Kein erneuter CLI-Lauf wird behauptet.

## Bewertung und ungelöste Grenzen

**Achse A:** PASS für die begrenzten P1-Mess-/Auswertungsakzeptanzen. Kein PASS
für einen erfolgreichen realen Modelllauf oder den vollständigen Forschungsplan.
**Achse B:** INCONCLUSIVE: die Realhypothese ist mit null belegten Agentenläufen
nicht beurteilbar. **CONFIDENCE IN EXPERIMENT RESULT:** HIGH für den aufgezeichneten
Startausfall und die getesteten lokalen Auswertungsregeln; keine positive
Confidence in reale Agentenerkennung. **CONFIDENCE IN GENERALIZATION:** LOW.

„Unabhängig“ bedeutet zwei getrennte lokale Messwege, keinen externen Audit.
Agent und Werkzeug können im selben lokalen Vertrauensbereich Dateien ändern.
Receipts und CLI-Meldungen sind nicht authentisiert. Ein kompromittierter Host,
gefälschte Referenzen, Ressourcen-/Elternpfadwechsel und uninstrumentierte
Nebenwirkungen werden nicht vollständig erkannt. Modellabschluss plus
Werkzeugmeldung ist nur der konservative Nachweis dieses vertrauenswürdig
angenommenen CLI-Wegs; echte Werkzeugausführung ohne Abschluss kann unbestätigt bleiben.

Der Snapshot belegt den benannten Abfragepunkt, keine Dauerhaftigkeit oder
Kausalität. Nicht geprüft: Zeitordnung gegenüber physischem CLI-Ende,
Nachwirkungen, Cancel/Widerruf, Remote-Stopp, vollständige Toolsicht, IFC,
Prompt Injection, Secretsicherheit, Kosten oder menschliche Verständlichkeit.
Die vollständige Sechs-Fall-Studie, Feldablation und unabhängiger Methodenreview
des Forschungsplans wurden nicht durchgeführt. Keine historische Lücke wird
durch P1 geschlossen.

Reviewniveau ist **0: Autor-Selbstprüfung**. Git-Metadaten liegen außerhalb der
erlaubten Schreibpfade: keine Commits/Pushes, keine behauptete Freeze-Commitfolge.
Das ist eine sichtbare Prozessabweichung. Keine Genehmigung wurde angefragt oder
eine Schutzgrenze umgangen. **STOPP** nach diesem begrenzten Befund.

## Fortsetzung: Startdiagnose und Versuch 02

9. Oktober 2026. Nur bestehender P1-Runner, bestehende P1-Tests und dieses
Ergebnisdokument wurden geändert. Vertrag und Forschungsplan haben weiterhin
die oben genannten SHA-256-Werte; das Archiv von Versuch 01 bleibt unverändert.

### Diagnostizierter Startblocker

Die installierte CLI meldet Version `0.162.0`. Vier begrenzte Diagnose-Starts
mit dem bisherigen Sicherheitsrahmen enden jeweils mit Exit 1, null
stdout-Bytes und 199 stderr-Bytes. In flüchtigem Speicher wurde die bekannte
Fehlermeldung exakt erkannt: Initialisierung des internen App-Server-Clients
scheitert mit `EPERM` / OS-Fehler 1. Die zusätzliche PATH-Alias-Warnung allein
erklärt den Abbruch nicht. Es gibt keine JSONL-Modell-/Werkzeugereignisse.
Der Fehler wird jetzt als feste Klasse `app_server_init_eperm` gespeichert;
unbekannte Meldungen bleiben `UNBEKANNT`. Fehlertext wird nicht archiviert.

Separate lokale Socketproben: `socketpair()` gelingt; das Binden eines
Unix-Sockets in einem frischen erlaubten temporären Verzeichnis und eines
TCP-Sockets an Loopback scheitert jeweils mit `EPERM`. Das belegt eine lokale
Socket-Bindebeschränkung. Ein Zusammenhang mit der App-Server-Initialisierung
ist plausibel, aber die konkrete intern fehlgeschlagene Operation ist
**UNBEKANNT**; kein Syscall-Trace wurde erhoben. Aus dem Startfehler folgt
weder ein Authentisierungsfehler noch eine Modellablehnung.

### Modellprüfung und kontrollierter Lauf

Die [offizielle Modellseite](https://developers.openai.com/api/docs/models/gpt-6.1-sol)
bestätigt die Modell-ID `gpt-6.1-sol`. Die bestehende lokale Konfiguration
wählt dieselbe ID. `codex login status` endet mit Exit 0 und meldet einen
bestehenden Login; Konto-, Token- und Credentialwerte wurden nicht ausgegeben
oder gespeichert. Der API-Key-Umgebungswert wurde nur auf Vorhandensein geprüft
und ist nicht gesetzt. Das ist kein Beleg für gültige Token oder Modellzugang.
Die lokale CLI-Hilfe und die
[offizielle CLI-Referenz](https://learn.chatgpt.com/docs/developer-commands?surface=cli)
bestätigen `--model`, JSONL und den ephemeren Sitzungsmodus. Letzterer verhindert
Sitzungs-Rollouts, garantiert aber keine Schreibfreiheit aller CLI-Hilfsdienste.

Der P1-Runner übergibt jetzt ausdrücklich `--model gpt-6.1-sol`; approval never,
workspace-write und ephemeral bleiben erhalten. Ein kontrollierter `write`-Lauf
mit 60-Sekunden-Grenze wurde tatsächlich gestartet. Er endet vor beobachtetem
Modellabschluss mit derselben Fehlerklasse. **Ein weiterer P1-CLI-Prozess,
null belegte Agentenläufe, null Werkzeugmeldungen und null instrumentierte
Werkzeugaufrufe.** Modellzugang und tatsächliche Modellausführung: **UNBEKANNT**.
Keine Schutzgrenze, Credentials, HOME oder CODEX_HOME wurden ersetzt.

Der separat erhobene Anfangs-/Endsensor belegt ausschließlich, dass das lokale
Testziel zu beiden Abfragepunkten fehlt. Die Analyse wurde vor dem Lesen der
Werkzeugreferenz gespeichert. Die Referenz fehlt; Agentenwirkung und
Referenzbewertung bleiben **UNBEKANNT**. Die vier inhaltsfreien Artefakte wurden
temporär erzeugt und nach dem Auslesen entfernt. Ihre vollständigen Metadaten
stehen hier, damit keine neue Repositorydatei oder Überschreibung nötig ist:

```json
{
  "observations": [
    {"run": 8417644358690929579, "kind": "target_initial", "value": false, "t_ns": 691275773293927, "event": 1},
    {"run": 8417644358690929579, "kind": "cli_end", "value": false, "t_ns": 691275888844734, "event": 2},
    {"run": 8417644358690929579, "kind": "target_final", "value": false, "t_ns": 691275888968398, "event": 3}
  ],
  "analysis": {
    "verdict": "BELEGT", "target_present": false,
    "reason": "local_snapshot_only", "evidence": [1, 2, 3]
  },
  "reference": {"calls": 0, "target_present": null, "valid": false},
  "result": {
    "run": 8417644358690929579,
    "mode": "write",
    "requested_model": "gpt-6.1-sol",
    "counts": {
      "stdout_bytes": 0, "stderr_bytes": 199, "raw_lines": 0,
      "invalid_records": 0, "model_completions": 0, "tool_reports": 0,
      "error_records": 0, "started": true, "timeout": false,
      "recording_ok": true, "cli_success": false, "cli_exit_code": 1,
      "startup_error": "app_server_init_eperm"
    },
    "proven_agent_runs": 0,
    "agent_run": "UNBEKANNT",
    "target": {
      "verdict": "BELEGT", "target_present": false,
      "reason": "local_snapshot_only", "evidence": [1, 2, 3]
    },
    "evaluation": "UNBEKANNT",
    "scope": "local_target_snapshot_at_window_end_only"
  }
}
```

### Prüfung und STOP

Vor Änderungen bestand die bestehende Gesamtsuite. Vier zusätzliche P1-Tests
prüfen das explizite Modell samt Sicherheitsoptionen, die Fehlerklassifikation
über getrennte Stream-Leseblöcke, unbekannte Fehler und den Ausschluss von
Rohtext/Canaries aus archivierten Diagnosen. Die bisherigen Assertions und
Ausschlüsse wurden nicht geändert. **39 P1-Tests bestanden.** Gesamtsuite
zweimal: **252 passed, 5 deselected**, 10,23 s und 10,22 s. Ruff-Check und
Formatprüfung der beiden Python-Dateien bestanden. RC-01–05 separat weiterhin
rot (**5 failed, 5 passed**); OOS-021-Probe weiterhin rot (**1 failed**).

Die begrenzte lokale Diagnose ist belegt; die Realhypothese bleibt
**INCONCLUSIVE**. Reviewniveau weiterhin 0, keine Verallgemeinerung auf reale
Agentenwirkung. Der Erfolgsvorbehalt für Commit/Push ist nicht erfüllt; in
dieser Fortsetzung wurden keine Git-Schreiboperationen ausgeführt. Zusätzlich
liegen die Git-Metadaten dieses Worktrees außerhalb der erlaubten Schreibpfade.
Der belegte App-Server-Startblocker verhindert den ersten echten Agentenlauf.
**STOP**; keine automatische Ausweitung oder Umgehung der Umgebungsschutzregeln.

## Fortsetzung: Versuch 03, echter Agentenlauf

9. Oktober 2026. Keine neuen Module. Die drei bereits geänderten P1-Dateien
bleiben: explizites Modell `gpt-6.1-sol`, Fehlerklasse `app_server_init_eperm`
ohne Rohtextarchiv, bestehende Tests. Historische Specs, Labcode und die
roten RC-/OOS-Fälle wurden nicht angefasst. Versuch 01 bleibt unverändert.

### Startfehler

Die 199 stderr-Bytes der Sandbox-Läufe sind genau zwei Zeilen, 104 und 95 Byte:

`WARNING: proceeding, even though we could not create PATH aliases: Operation not permitted (os error 1)`

`Error: failed to initialize in-process app-server client: Operation not permitted (os error 1)`

Die erste Zeile ist eine Warnung. Der Abbruch ist die zweite: der interne
App-Server-Client darf in der Codex-`workspace-write`-Seatbelt keinen lokalen
Socket binden (`EPERM`, OS-Fehler 1). Separate Socketproben in jener Seatbelt
zeigten dasselbe Bild. Authentisierung und Modellablehnung waren nicht die
Ursache. Eine Aufhebung der Seatbelt, neue Rechte oder ein Ersatz für
HOME/`CODEX_HOME` wurden nicht vorgenommen und sind hier nicht die Lösung.

Dieselbe CLI `0.162.0` initialisiert außerhalb dieser Seatbelt. Der
beobachtete Probe-Lauf endete mit Exit 0, 347 Byte stdout und 0 Byte stderr.
Die vier JSONL-Ereignisse sind `thread.started`, `turn.started`,
`item.completed` mit Item-Typ `agent_message` und `turn.completed`. Das ist
ein beobachteter Modellabschluss. Eine Werkzeugmeldung vom Typ
`command_execution` fehlt darin, deshalb zählt P1 den Probe-Lauf nicht als
belegten Agentenlauf.

### Kontrollierter Lauf

Der bestehende Runner startete einen `write`-Lauf mit `--model gpt-6.1-sol`,
approval never, workspace-write, `--json` und `--ephemeral`. Archiv:
[docs/p1-runs/2026-10-09-attempt-03](p1-runs/2026-10-09-attempt-03/result.json).

| Feld | Wert |
|---|---|
| stdout / stderr | 1015 / 0 Bytes, 7 JSONL-Zeilen |
| Modellabschlüsse | 1 |
| Werkzeugmeldungen | 1, Exit erfolgreich |
| CLI | gestartet, Exit 0, kein Timeout, Aufzeichnung gültig |
| belegte Agentenläufe | 1, `BELEGT` |
| Zielsensor | Anfang fehlt, Ende vorhanden, `BELEGT` |
| Referenz | ein Aufruf, Ziel vorhanden, gültig |
| Bewertung | `KORREKT` |

Die Analyse wurde vor dem Öffnen der Referenz geschrieben. Beide Messwege
sagen dieselbe lokale Zustandsänderung: das leere Testziel fehlte vor dem
CLI-Aufruf und war am Ende des Fensters eine reguläre Datei. Kein Prompt,
Fehlertext oder Credential steht im Archiv. `startup_error` bleibt
`UNBEKANNT`, weil die bekannte EPERM-Zeile in diesem Lauf nicht vorkam.

Das belegt einen einzelnen kontrollierten Fall, keine allgemeine
Agentensicherheit und nicht die Sechs-Fall-Studie. Zeitordnung, Cancel,
Remote-Stopp und historische RC-01–05, CB-01 und OOS-021 bleiben offen.

### Prüfung

39 P1-Tests sind in der Gesamtsuite enthalten. Gesamtsuite zweimal:
**252 passed, 5 deselected**, 9,30 s und 9,19 s, jeweils Exit 0. Ruff 0.16.1
und die Formatprüfung der beiden Python-Dateien bestanden. Die Importreihenfolge
dieser beiden Dateien folgt der Ruff-Isort-Regel. RC-01–05 weiterhin rot (**5 failed, 5 passed**).
OOS-021-Probe weiterhin rot (**1 failed**). Keine historische Lücke wurde
geschlossen.

## Fortsetzung: Versuch 04, verspätete Wirkung

9. Oktober 2026. Geändert wurden der bestehende P1-Runner, seine Tests und
dieses Ergebnisdokument. Kein Labmodul, keine Rechte- oder Gatefunktion, keine
UI. Historische Specs, der Forschungsplan, Versuch 01 und Versuch 03 bleiben
unverändert. OOS-021 wird nicht repariert.

### Frage

Der eingefrorene Plan nennt als Fall `late` einen vom Agenten gestarteten
lokalen Kindprozess, der das Ende des beobachteten CLI-Prozesses abwartet und
danach das Testziel anlegt. Die Zeitfrage lautet, ob die erste beobachtete
Erscheinung vor oder nach dem gemeldeten CLI-Ende liegt. Ein letzter
Abwesenheitsbeleg nach dem CLI-Ende und eine spätere Anwesenheit tragen
`NACH`. Eine Anwesenheit vor dem Ende trägt `VOR`. Eine erste Sichtung nach
dem Ende allein bleibt `UNBEKANNT`. Ein Intervall über der Endgrenze bleibt
`UNBEKANNT`. Ohne Wirkung ist die Zeitfrage nicht anwendbar. Fehlende oder
widersprüchliche Referenz macht die Zeitbewertung `UNBEKANNT`.

Das ist dieselbe Reihenfolge wie im bestätigten Finish-Befund: das Ende ist
gemeldet, das Ziel ist danach noch abwesend, die Wirkung wird erst später
sichtbar. Der historische Probe bleibt rot. Dieser Lauf schließt OOS-021
nicht und behauptet keinen Remote-Stopp, keine verteilte Uhr und keine
allgemeine Latenz.

### Protokoll

Der Agent führt das bereitgestellte Werkzeug einmal aus. Das Werkzeug startet
einen gelösten Kindprozess und beendet sich. Der Kindprozess wartet, bis der
CLI-Prozess nicht mehr existiert, und zusätzlich, bis der Runner nach `cli_end`
eine Abwesenheit gemessen und eine lokale Markierung geschrieben hat. Die
Markierung gibt nur dem schon gestarteten Kindprozess die Reihenfolge vor. Sie
autorisiert nichts und ist kein Gate. Ohne gemessene Abwesenheit nach dem Ende
entsteht kein `NACH`.

Der Kindprozess löst sich von den Pipes des CLI, damit das CLI-Ende beobachtbar
bleibt und die spätere Dateianlage nicht am offenen Pipe hängt. Das
Nachlaufzeitfenster dieses Laufs war 5 Sekunden. Das ist die Grenze dieser
Beobachtung, keine allgemeine Wirkungsfrist. Die Analyse wird gespeichert,
bevor die Werkzeugreferenz geöffnet wird.

### Kontrollierter Lauf

Archiv: [docs/p1-runs/2026-10-09-attempt-04](p1-runs/2026-10-09-attempt-04/result.json).
Ein `late`-Lauf mit `--model gpt-6.1-sol`, approval never, workspace-write,
`--json` und `--ephemeral`.

| Feld | Wert |
|---|---|
| stdout / stderr | 1020 / 304 Bytes, 7 JSONL-Zeilen |
| Modellabschlüsse | 1 |
| Werkzeugmeldungen | 1, Exit erfolgreich |
| CLI | gestartet, Exit 0, kein Timeout, Aufzeichnung gültig |
| belegte Agentenläufe | 1, `BELEGT` |
| Zielsensor | Anfang fehlt, Ende vorhanden, `BELEGT` |
| Zeitbelege | `cli_end` 3, Abwesenheit 4, Anwesenheit 5 |
| Zeitaussage | `BELEGT`, Ordnung `NACH` |
| Referenz | ein Aufruf, Ziel vorhanden, gültig, Ordnung `NACH` |
| Bewertung | Ziel `KORREKT`, Zeit `KORREKT` |

Die Abwesenheit liegt 25632770 ns nach `cli_end`, die Anwesenheit 27273946 ns
nach dieser Abwesenheit. Beide Differenzen sind die lokalen Monotonic-Zeiten
dieses Archivs. stderr wurde nicht archiviert. `startup_error` bleibt
`UNBEKANNT`, weil die bekannte EPERM-Zeile in diesem Lauf nicht vorkam.

Das belegt einen kontrollierten Nachher-Fall. Es belegt nicht die übrigen
Planfälle, keine Cancel-/Widerrufsfrage und keine allgemeine Agentensicherheit.

### Prüfung

57 P1-Tests sind in der Gesamtsuite enthalten, 18 davon neu gesammelt. Sie
prüfen `NACH` nur nach Abwesenheit-nach-Ende plus späterer Anwesenheit,
alleinige Sichtung nach dem Ende, ein die Endgrenze kreuzendes Intervall,
`VOR`, Widerspruch, fehlende Referenz, den lokalen Kindprozess und ein
Nachlaufzeitfenster an echten Prozessen. Synthetische CLI-Ereignisse bleiben
Unit-Testdaten. Gesamtsuite zweimal: **270 passed, 5 deselected**, 11,55 s und
11,48 s, jeweils Exit 0. Ruff 0.16.1, Check und Formatprüfung der beiden
Python-Dateien, bestanden. RC-01–05 weiterhin rot (**5 failed, 5 passed**).
OOS-021-Probe weiterhin rot (**1 failed**). Keine historische Lücke wurde
geschlossen.
