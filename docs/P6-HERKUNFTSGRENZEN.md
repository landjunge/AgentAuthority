# P6: Aufnahmebindung und Herkunftsgrenzen

Stand: 9. Oktober 2026. Verbindlicher Auftrag: ThreadDesk `833554dffb6e`,
Eintrag 27; ursprünglicher Befund: Eintrag 36. Der Nutzer hat die offene
Aufnahme-/Verifiergrenze ausdrücklich zur Behebung freigegeben, einschließlich
notwendiger Anschlussanpassungen. **Die Korrektur ist lokal geprüft; P6 ist
mangels Remote-Push, Remote-CI und Merge noch nicht vollständig abgeschlossen.**

## Basis und Zuständigkeit

Basis ist P5-Merge `0f6b601e2212cde9f7d44f14927de39629250b34` nach `master`.
Der GitHub-Leseconnector bestätigt diesen Remote-Stand erneut. Der lokale
P6-Zwischencommit `b68781d5ff03a07d93df433647f6b1718e762b08` korrigierte bereits
Defaultklasse, Klassenprüfung und Agentenpromotions für alte/gefälschte Eingänge.
Der neue Patch schließt die dabei ausdrücklich offen gebliebene Aufnahmegrenze.

Codex ist alleiniger Integrator. Zuständig sind der bestehende Aufnahmepfad,
der notwendige Anschluss in `scripts/p5_reliability.py`, zugehörige Regressionen
und dieser Bericht. Historische P1–P5-Archive, P4-Abnahme und vorab festgeschriebene
P5-Erwartung bleiben bytegleich. P5 wurde nicht erneut als Paket ausgeführt.

Grok erhielt einen ausschließlich lesenden Teamauftrag mit getrennten
Prüfthemen Aufnahme/Replay und FD-Herkunft/Minimierung. Nach 120 Sekunden lag
keine auftragsbezogene Antwort vor; der gestartete Versuch wurde beendet.
Teamstart, unabhängige Prüfer und Review-Abnahme sind nicht belegt.

## Tatsächliche Aufnahme statt Eingangsflag

`capture()` ruft den vorhandenen Collector auf und erhebt unabhängig die
lokale Zielbeobachtung und die instrumentierte Referenz. Nach Speicherung der
minimierten Belege ruft es einen Consumer auf, während sein Workspace noch
besteht. Nur für diesen Aufruf wird ein undurchsichtiger `object()`-Kontext in
einer pro Modul gehaltenen In-Memory-Registry registriert. Er ist an die
Prozess-ID und einen Digest der vollständigen Beobachtungs-/Result-/Referenzdaten
gebunden. Er ist kein JSON-Feld, keine boolesche Vertrauensmarkierung und keine
öffentlich aus Eingangsflags erzeugbare Dataclass.

`bind()` und `assess()` benötigen diesen passenden, noch registrierten Kontext
für positive aktuelle Geltung, Agentenbindung und unabhängig bestätigte Wirkung.
Explizites `current`, Zähler, Labels und konsistente Referenzen allein genügen
nicht. Der Kontext wird nach Rückkehr oder Ausnahme entfernt. Veränderte
Eingänge passen nicht mehr; ein Fork hat eine andere Prozess-ID. Ein Consumer,
der gemessene Eingänge verändert, verursacht einen begrenzten Fehler statt
eines erfolgreichen Capture-Abschlusses.

Die Geltung bezeichnet ausschließlich den erhobenen lokalen Snapshot. Sie
beweist weder den Dateizustand nach dem Messpunkt noch dauerhafte Identität.
Die historische Zeilenkonsistenz und Zeitordnung bleiben bei Archiv-Replay
nutzbar; aktuelle Geltung, Agentenlauf und unabhängige Bindung bleiben unbekannt.
Die Defaultklasse ist weiterhin `stale`.

`connect()` bindet direkt im Consumer, statt importierte JSON-Dateien zu einer
aktuellen Aufnahme zu erklären. Der Anschlussauswerter scored ebenfalls im
Consumer. Nachträglich geladene Archivdaten müssen mit dem während der Messung
gehaltenen Digest übereinstimmen. Ein vorhandenes Laufverzeichnis wird mit STOP
zurückgegeben, ohne seinen historischen Score zu überschreiben.
Neue Scores nennen ausdrücklich den Auswertervertrag `p6_live_acquisition`.
Der behaltene P5-Erwartungshash ist als `historical_p5_reference` gekennzeichnet;
er wird nicht als unveränderter aktueller P6-Auswertungsvertrag ausgegeben.

## FD-Relation aus tatsächlich gehaltenen Deskriptoren

`apply_fd_measurement()` übernimmt kein fremdes Dictionary mehr positiv.
Auch `fd_set_verified=true`, `source_authenticated=false` und ein konsistentes
Relationsergebnis erzeugen keinen Messkontext. Behauptete Authentisierung wird
nicht übernommen.

`measure_local_fd_relation()` dupliziert zwei tatsächlich erhaltene FDs, hält
die Duplikate über beide `fstat`-Messungen offen und verlangt reguläre Dateien
mit stabilen dev/inode-Paaren. Nur während dieser Messung wird ein separater,
prozessgebundener FD-Kontext registriert und unmittelbar projiziert. Danach
werden Kontext und Duplikate auch bei einem Fehler entfernt. Geschlossene,
ungültige oder nicht reguläre FDs ergeben UNBEKANNT.

Dies ist eine enge POSIX-Messung des tatsächlich erhaltenen, gleichzeitig
gehaltenen Paars. Sie misst keine Inhalte, Revisionen, ursprüngliche Pfade,
identischen Open-File-Description-Zustand oder globale Identität. Eine passende
FD-Substitution bleibt positiv nur für das erhaltene Ersatzpaar. Herkunft der
ursprünglich gemeinten Ressource bleibt unbekannt; `source_authenticated` bleibt
bei einer tatsächlichen lokalen Relation `false`. Es ist keine neue Ausführung
des historischen Linux/tmpfs/SCM_RIGHTS-Verifiers.

## Unveränderte Gegenkontrollen und neue Regressionen

Die ursprünglichen zwölf Vorab-Erwartungen und der ursprüngliche Diagnose-Runner
wurden nicht geändert. Ergebnisse seiner drei Entwicklungsstände:

| Stand | PASS | FAIL | SKIP | Diagnose-Exit |
|---|---:|---:|---:|---:|
| Ursprüngliche P6-Diagnose auf P1–P4 | 7 | 4 | 1 | 2 |
| Isolierter Zwischencommit b68781d | 10 | 1 | 1 | 2 |
| Aufnahme-/FD-Korrektur | 11 | 0 | 1 | 0 |

P6-07, das direkte Fremdpacket an der FD-Projektion, ist jetzt UNBEKANNT und
PASS der unveränderten Grenzerwartung. P6-12 bleibt SKIP: Auf Darwin wurde keine
Linux/tmpfs-Messung erfunden. Die alte Vorab-Runnerkonstante `base` verweist auf
den historischen Forschungsstand; die tatsächlich gelesene Source wird durch
ihren separaten SHA256 und die Prozessbelege ausgewiesen.

Die neuen P6-Regressionen prüfen explizites `current` mit erfundenem Bundle,
den direkten Binder, rohe FD-Packets, einen wirklichen lokalen Späteffekt ohne
Modell, gleichzeitig gehaltene gleiche/verschiedene FD-Paare, veränderte
Messdaten, fremde und abgelaufene Kontexte, Fork, Consumerfehler, geschlossenes
FD und Pipe, Archiv-Replay und unveränderliche vorhandene Scores.

Eine zusätzliche synthetische CLI-Protokollfixture prüft den positiven
Live-Binder-/Scoringzweig und dessen anschließenden Replay-STOP. Sie startet
lokale Testprozesse und sendet künstliche Completion-Marker; **sie ist kein
echter Modell-/Agentenlauf und kein unabhängiger Modellnachweis**. Echte neue
Modell-/Agentenläufe in P6: null. Die brauchbaren tatsächlich gemessenen
Positivfälle sind lokaler Dateieffekt und gleichzeitig gehaltene FD-Relationen.

Frühere P2–P5-Tests wurden für die strengere Replay-Semantik angepasst.
Historische Antworten bleiben unverändert; ihre frühere Gleichheit mit einer
aktuellen Auswertung ist keine aktuelle Herkunftsanforderung mehr. Die
historische Wirkungs-/Zeitprojektion wird weiter verglichen, während aktuelle
Geltung und Agentenbindung nun unbekannt sein müssen. Sicherheitsanforderungen
wurden nicht durch ignorierte Fehler oder neue Abwahlen ersetzt.

Validierung des finalen Codes, Python 3.12.13, `-B -p no:cacheprovider`:

- Gezielt P6/P2/P3/P4/P5: **55 passed**, Exit 0.
- Gesamtsuite zweimal: jeweils **354 passed, 5 deselected**, Exit 0.
- Ruff Check und Format der sieben betroffenen Python-Dateien: PASS.
- Unveränderter ursprünglicher Diagnose-Runner: **11 PASS / 0 FAIL / 1 SKIP**, Exit 0.
- Archiv-Diff gegen P5-Merge leer; keine alten Whiteboard-Dateien überschrieben.

Die fünf bestehenden Abwahlen betreffen RC-01–05. Diese historischen Lücken,
OOS-021 außerhalb der Standardsuite, CB-01 und der P4-Cachebefund bleiben offen.
Die Summary des alten Fake-Labs ist kein allgemeiner Sicherheitsnachweis.

Reproduktion:

```sh
python -B -m pytest -p no:cacheprovider tests/test_plan_p6_boundaries.py
python -B -m pytest -p no:cacheprovider
```

Exklusiv angelegte Ausführungsbelege:
`/Users/landjunge/.threaddesk/artifacts/agent-authority/p6-acquisition-20261009T212247Z/`.
Dort liegen Grok-Start-/Endbelege, unveränderte ursprüngliche Countercontrols,
gezielte Testlogs und beide Gesamtläufe. Der vollständige Commit-/Pushstatus
wird append-only im Whiteboard dokumentiert.

## Grenzen und Veröffentlichung

Die Registry trennt untrusted JSON vom tatsächlich ausgeführten lokalen
Aufnahmepfad. Sie ist keine Sicherheitsgrenze gegen einen kompromittierten
Pythonprozess, manipulierten Collector, CLI oder Kernel. Beobachtete
CLI-Protokollmarker authentisieren weder Provider noch Actor noch tatsächliche
Modellidentität. Quellenherkunft bleibt unbekannt. Hashes belegen Bindung an
Messdaten, keine allgemeine Quellechtheit. Minimierung ist für die geprüften
Projektions-/Persistenzpfade belegt, nicht für jeden möglichen Kanal.

Der normale Git-CLI-Zugriff aus diesem Agentenarbeitsbereich scheitert weiterhin
mit `Could not resolve host: github.com`; auch `gh` erreicht die API hier nicht.
Der Mac ist als Online-Gerät sichtbar, aber ein normaler Git-CLI-Aufruf über
sein Terminalwerkzeug wird vor Ausführung abgewiesen:
`MCP tool call requires approval, but approval policy is never`.
Es wurde kein genehmigungspflichtiger GitHub-Schreibconnector verwendet.

Der zulässige GitHub-Leseconnector bestätigt `master` an `0f6b601`,
`protected=false` und leere, ausgeschaltete Pflichtchecklisten. Für den neuen
P6-Stand fehlen Remote-Push und Remote-CI. Ohne deren Nachweis erfolgt kein
Merge und keine vollständige P6-Abschlussmeldung. Die Sitzung ändert keine
Schutzregeln und verwendet keinen Admin-Bypass.

P7 bleibt wartend. P8 und P9 werden nicht gestartet. D-012 bleibt bindend:
Authority beobachtet, analysiert und warnt; es vergibt keine Rechte, Secrets
oder Budgets und bildet kein Stop-Gate.
