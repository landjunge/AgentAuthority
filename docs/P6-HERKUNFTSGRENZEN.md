# P6: Aufnahmebindung und Herkunftsgrenzen

Die folgenden Entwicklungsstände bleiben als Verlauf erhalten. Die aktuellen
Veröffentlichungs- und Abnahmegrenzen stehen im Nachtrag am Ende dieser Datei.

Stand: 10. Oktober 2026. Verbindlicher Auftrag: ThreadDesk `833554dffb6e`,
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
Die operative Fortsetzung adressierte die bekannte P5-Sitzung
`01a12270-21d4-7d23-bf72-65c0dc477bab` direkt mit `--resume` und einem
abgegrenzten lesenden Auftrag zum Prüfcommit `b66be94`. Die konkrete
Task-ID wurde in deren User-Historie zurückgelesen. Das belegt CLI-Annahme,
keine Modell-Empfangsbestätigung: Retry-Updates nennen DNS-Fehler für
`cli-chat-proxy.grok.com`. Der eigene Versuch endete nach 183,03 Sekunden
mit Exit -9. Keine Modellantwort, Teamstarts oder Ergebnisse sind belegt.
Der Auftrag bleibt ohne Reviewresultat; er erteilt keine Mergefreigabe und
deckt den nachfolgenden Fehlerfix nicht automatisch ab.

Am 10. Oktober gelang die Übergabe über den direkten Nutzerkanal an die
aktuell antwortende Sitzung `01a12296-ef98-7aa1-b34a-53aa992005b7`. Grok
bestätigte Task-ID `authority-p6-grok-review-eb1fe8b-20261009` und tatsächlichen
HEAD `eb1fe8b3bd38bda51e5848c502e54a8e7d7cf14d`, las den Auftrag und prüfte
Whiteboard, Git, Produktcode, Tests und Logs. Die dazu gespeicherten Toolresultate
belegen den Arbeitsbeginn. Es gab keinen Codex-Doppelstart. Nach ausdrücklicher
neuer Nutzeranweisung wurden keine zusätzlichen Prüfer gestartet; zwei
Abschlussmeldungen derselben Sitzung sind keine unabhängigen Teamreviews.

Grok bewertete vier Themen lesend als PASS, führte selbst keine Tests aus und
erteilte keine Paketabschluss- oder Mergefreigabe. Codex begrenzte das Archiv-PASS
anhand des nachfolgend beschriebenen eigenen Gegenbelegs. Groks weitere
Belegkritik war zutreffend: Für die zwei in `eb1fe8b` geänderten Python-Dateien
fehlte im Übergabeordner ein eigener Ruff-Laufbeleg. Check und Format wurden
am unveränderten `eb1fe8b` mit `--no-cache` erneut ausgeführt, jeweils Exit 0,
und mit Commit und Logs gespeichert. Dieser Lauf ist keine Prüfung des
nachfolgenden Binderfixes; dessen eigene Prüfungen sind unten ausgewiesen.

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

Eine weitere modellfreie Gegenkontrolle am Zwischenstand `b66be94` fand einen
Fehler an diesem Archivübergang: Von Python als JSON geladene `NaN`-/`Infinity`-
Werte lösten bei der kanonischen Digestbildung einen ungefangenen `ValueError`
aus. Die neuen Regressionen waren zunächst **2 failed / 1 passed**. Der
Anschluss behandelt nicht kanonisierbare Archivdaten jetzt wie eine Abweichung:
begrenztes STOP `archive_disagrees_with_capture`, keine Promotion und keine
Ausgabe der fehlerhaften Eingangswerte. Die endliche Abweichung bleibt STOP.
Diese Tests injizieren ausschließlich den Anschluss-Fehlerpfad; sie sind weder
eine tatsächliche Aufnahme noch ein Agenten-/Modellnachweis.

Eine zusätzliche Anschlusskontrolle auf `eb1fe8b` fand eine weitere
Archivkonsistenzlücke: Nach dem gültigen Live-Unit-Consumer konnte `binding.json`
durch `null`, eine Liste oder einen String ersetzt werden, ohne den bisherigen
Vergleich auszulösen. Außerdem akzeptierte Python-Dictgleichheit die Änderung
`tool_report.value: true` zu `1`. Das Paket blieb in diesen vier Fällen PASS.
Die unveränderte gültige Bindung und ein abweichendes Dictionary dienten als
Positiv- beziehungsweise bereits abgewiesene Negativkontrolle.

Der Folgefix verlangt für die gespeicherte Bindung einen Dictionary-Typ und
denselben kanonischen JSON-Digest wie für die tatsächlich zurückgegebene
Live-Bindung. Typänderungen, andere Werte und nicht kanonisierbare Daten
ergeben begrenztes STOP `binding_weicht_ab`. Fehlerpriorität und Prüfung der
eigentlichen Aufnahmedaten bleiben erhalten. Die sechs Anschlussregressionen
waren zuerst **4 failed / 2 passed**; nach dem Fix bestehen alle sechs.
Ihre synthetische CLI-Protokollfixture führt lokale Prozesse aus und prüft
den echten Anschlusszweig, ist aber kein tatsächlicher Modell-/Agentenbeleg.
Der Aufnahme-/FD-Quelltext wurde für diesen Fix nicht geändert.

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

Operative Fortsetzung mit dem begrenzten Archivfehlerfix:

- P6 enthält nun 31 Regressionen; gezielt P6 und Anschluss: **36 passed**, Exit 0.
- Gesamtsuite erneut zweimal: jeweils **357 passed, 5 deselected**, Exit 0.
- Ruff Check und Format der beiden zusätzlich geänderten Python-Dateien: PASS.
- Der Aufnahme-/FD-Quelltext ist gegenüber `b66be94` unverändert; der dort
  belegte ursprüngliche Diagnose-Runner bleibt diesem identischen Quelltext
  zugeordnet. Keine neue Linux/tmpfs-Messung und kein neues Grok-Review behauptet.

Zusätzliche Auftrags-, Empfangs-, DNS-, Rot-/Grün- und Transportbelege:
`/Users/landjunge/.threaddesk/artifacts/agent-authority/p6-grok-handoff-20261009T214202Z/`.
Ein verifiziertes lokales Git-Bundle ist nur ein Transportartefakt, kein
Remote-Push- oder Mergebeleg. Das Bundle für `b66be94` enthält den nachfolgenden
Archivfehlerfix nicht und wird durch das Bundle des Folgecommits ergänzt.

Prüfungen des weiteren Binder-Archivfixes auf Basis `eb1fe8b`:

- P6 enthält 37 Regressionen; gezielt P6 und Anschluss: **42 passed**, Exit 0.
- Gesamtsuite zweimal: jeweils **363 passed, 5 deselected**, Exit 0.
- Ruff Check und Format der beiden geänderten Python-Dateien mit `--no-cache`: PASS.
- Historische Archive, Workflows, `lab` und `tests/realcase` bleiben unverändert.
- Keine neuen echten Modell-/Agentenläufe. Keine allgemeine Sicherheitsfreigabe.

Während Groks Review blieb dessen Worktree auf `eb1fe8b` eingefroren. Codex
bereitete den bestätigten Folgefix in einem eigenen isolierten Git-Worktree vor.
Nur Codex integriert ihn nach dem abgeschlossenen Review und grünen Prüfungen.
Groks Bericht zu `eb1fe8b` gilt nicht automatisch als Review des Folgefixes.
Auftrags-/Arbeitsbeginn-/Review-, Ruff- und Rot-/Grün-Belege liegen unter
`/Users/landjunge/.threaddesk/artifacts/agent-authority/p6-resume-20261009T220150Z/`.

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

## Nachtrag: versionierte Abnahmebelege, 10. Oktober 2026

Verbindliche Quellen sind Whiteboard `833554dffb6e`, insbesondere Einträge
27, 77, 79, 82, 126–128. Dieser Nachtrag bearbeitet ausschließlich P6;
P7–P9 werden dadurch nicht gestartet.

Der tatsächliche P6-Remote-Stand ist inzwischen belegt: PR #22 ist gemergt,
`master` steht an `674e7fe86e232c1fd8d26d0247bf2ae4cf853c8d`. Parent ist der
P5-Merge `0f6b601e2212cde9f7d44f14927de39629250b34`. Tree
`90194321c8d6d3a56240dca3efb6c6d65a9ac5bb` entspricht exakt dem zuvor lokal
geprüften und veröffentlichten P6-Commit `d0b1a91441ee752be056d7779fba8e65ee1dd02f`.
Die früheren Aussagen über fehlenden Remote-Push oder Merge beschreiben den
damaligen Zwischenstand. Sie sind keine aktuelle Statusmeldung.

### Geschlossene lokale Beleglücke

Die drei Dictionary-Gegenkontrollen aus Eintrag 77 waren nur in einem separaten
Prüfskript samt Laufbelegen archiviert. Sie gehören jetzt zur bestehenden
Regression `test_live_attachment_rejects_corrupted_archived_binding`.
Die ursprüngliche gültige Bindung sowie die bisherigen beschädigten Typen
bleiben als Kontrollen erhalten. Es gibt keinen neuen Produktpatch.

| Änderung an gespeicherter Bindung | Tatsächlich geprüfter Pfad | Erwartet und beobachtet |
| --- | --- | --- |
| Dictionary mit `NaN` | Kanonische Digestbildung wirft `ValueError` | Begrenztes STOP `binding_weicht_ab` |
| Dictionary mit `+Infinity` | Kanonische Digestbildung wirft `ValueError` | Begrenztes STOP `binding_weicht_ab` |
| Dictionary mit `-Infinity` | Kanonische Digestbildung wirft `ValueError` | Begrenztes STOP `binding_weicht_ab` |
| Unveränderte Bindung | Kein Kanonisierungsfehler | PASS ausschließlich im synthetischen Protokolltest |

Die Tests messen den tatsächlichen Exception-Pfad des bestehenden Auswerters,
statt einen Fehler künstlich zu werfen. Sie prüfen zusätzlich das gespeicherte
Ergebnis gegen den Rückgabewert; Kontrollfeld und nichtendliche Werte fehlen
im Ergebnisbericht. Die absichtlich beschädigte synthetische Eingangsdatei
enthält diese Werte weiterhin als Testeingang. Daraus folgt kein allgemeiner
Minimierungsnachweis für andere Kanäle.

Prüfung am isolierten Codex-Worktree auf Basis des tatsächlichen Remote-Masters,
Python 3.12.13, `-B -p no:cacheprovider`: gezielt P6 und Anschluss **45 bestanden**;
Gesamtsuite **366 bestanden, 5 historische Abwahlen**, Exit 0. Ruff Check und
Format der geänderten Testdatei bestanden. Produktcode, Workflows und alte
Archive bleiben bytegleich. Es wurden keine neuen echten Modellläufe ausgeführt;
der positive Protokollfall ist keine echte Agentenabnahme. Keine Wiederholung
von Groks abgeschlossener H3-Prüfung und keine neue unabhängige Prüfung behauptet.

### Weiterhin offene vollständige Abnahme

Der aktuelle Remote-Job `test` ist grün (Run `38002016327`, Job `114062072638`).
CodeQL `Analyze (python)` bleibt rot (Run `38002016367`, Job `114062072771`):
Rohlogs melden deaktiviertes Code Scanning und `configuration error` beim
Ergebnisupload. Die Artefaktabfrage dieses Runs liefert **null Artefakte**.
Ein lokales `codeql` ist nicht installiert; ein alternativer vollständiger
Analysebeleg ist damit nicht vorhanden. Kein CodeQL-PASS und keine Aussage
über fehlende Schwachstellen.

Der GitHub-Lesezugriff meldet `protected=false`; der Protection-Endpunkt ist
für die Integration mit HTTP 403 nicht zugänglich. Rulesets liefern HTTP 403
mit Tarifhinweis. Der normale `gh api`-Leseweg scheitert in diesem
Arbeitsbereich an der Verbindung zu `api.github.com`. Eine vollständige
Pflichtcheckliste ist nicht nachgewiesen; CodeQL wird deshalb nicht unbelegt
als verpflichtender Branch-Schutzcheck bezeichnet. Keine Schutz-, Tarif-,
Secret- oder Workflowänderung und kein Umgehen des Ergebnisuploads.

Groks früherer Merge außerhalb seines lesenden Auftrags bleibt als historische
Integratorabweichung dokumentiert. Diese Tests genehmigen ihn nicht nachträglich
und lösen keinen P6-Nachmerge aus. RC-01–05, OOS-021, CB-01 und der
P4-Verfahrensvorbehalt bleiben offen. Vollständige P6-Abnahme und die
Voraussetzung für P7 sind weiterhin nicht erklärt.

Aktuelle Test-, Quellhash-, Remote- und Abschlussbelege:
`/Users/landjunge/.threaddesk/artifacts/agent-authority/p6-acceptance-20261010T003759561Z/`.
Commit, Push und mögliche Remote-Nachweise werden dort und append-only im
Whiteboard getrennt von diesem lokalen Testergebnis dokumentiert.

## Nachtrag: begrenzter P6-Prüfstand und Integration

Stand: 10. Oktober 2026. Auftrag Whiteboard `833554dffb6e`, Eintrag 527,
verlangt zuerst die dokumentierte formale P6-Abnahme. Diese bleibt offen.
Codex hat die Kriterien aus Eintrag 27, die begrenzte Entscheidung 386 sowie die unabhängigen
Grok-Prüfungen 295/296, 512 und 549 mit den Originalbelegen abgeglichen.
**Der begrenzte technische P6-Prüfstand und seine Integration sind bestanden.
Die vollständige/formale P6-Paketabnahme bleibt offen wegen RC-01–05, OOS-021,
CB-01 und P4. Die Voraussetzung für P7 ist nicht erfüllt.** Dies entspricht
Entscheidung 386, der Gegenprüfung 549 und der anschließenden ausdrücklichen
Nutzerkorrektur. Die in PR #28 behauptete formale Paketabnahme war eine
Fehlinterpretation durch Codex und wird hiermit zurückgenommen. Die früheren
Publikations- und CodeQL-Zustände bleiben als Verlauf erhalten; der erfolgreiche
Merge-Nachweis aktualisiert diese technischen Punkte, nicht die Paketabnahme.

[PR #27](https://github.com/landjunge/agent-authority-lab/pull/27) wurde von
Codex regulär per Squash mit gepinntem Kandidaten-HEAD
`df5100d94ef73b56e744dcbbb8d0d42be3cf5187` integriert. Merge-Commit ist
`1e500c222e2ca0fa32ecb5192f00a08e82faae6c`, einziger Parent
`674e7fe86e232c1fd8d26d0247bf2ae4cf853c8d`. Tree
`589813b713d53717b147a56aefa10d19f9a803b6` ist identisch mit dem geprüften
Kandidaten und dem unabhängig gerechneten Merge-Tree. Remote-Master zeigte
bei der Integrationsprüfung auf diesen Commit; P5-Merge `0f6b601` ist darin
enthalten.
Aktuelle Regeln, Reviews und erfolgreiche Checks wurden vor Ready und vor
Merge erneut geprüft. Es gab keinen Admin-, Force- oder Auto-Merge-Bypass.

| Kriterium aus dem P6-Auftrag | Prüfstand und tatsächlicher Umfang |
| --- | --- |
| Keine falsch authentisierten Quellen; alte/gefälschte Eingänge bleiben unbekannt | 40 P6-Regressionen bestanden; Quellenherkunft bleibt `UNBEKANNT`. |
| Mindestens ein brauchbarer enger Positivfall | Tatsächlicher lokaler Dateieffekt und gleichzeitig gehaltene FD-Paare sind geprüft; sie authentisieren keinen Provider oder Actor. |
| Minimierung und Marker | Geprüfte Projektionen erhalten keine sensiblen Rohdaten; sieben Markerregressionen bestanden. Keine umfassende Bereinigung anderer Kanäle oder alter Marker behauptet. |
| Regression und Quellenbindung | 47 gezielte und 373 Standardtests bestanden, fünf historische RC-Abwahlen separat ausgewiesen. Alle 177 geprüften Quelldateien bytegleich; Groks eigenständige Prüfung stimmt überein. |
| Reguläre Integration und Remote-Prüfung | Merge/Parent/Tree belegt; beide Pytest-Durchläufe der Merge-CI erfolgreich; originale CodeQL-Analyse und Ergebnisupload erfolgreich verarbeitet. |
| Grenzen und negative Belege | RC-01–05, OOS-021, CB-01, P4-Vorbehalt und Qualitätsaltlasten sind weiterhin offen und in der begrenzten Risikobewertung ausgewiesen. |

[Merge-CI 38085424077](https://github.com/landjunge/agent-authority-lab/actions/runs/38085424077)
mit Job `114310802970` und
[CodeQL 38085424075](https://github.com/landjunge/agent-authority-lab/actions/runs/38085424075)
mit Job `114310802948` sind am exakten Merge-SHA erfolgreich. Der Originalupload
ist vollständig verarbeitet; native Analyse `1929667609` gehört zu diesem
Commit. Der SARIF-Artefaktworkflow lief auf diesem Push nicht. Die vorher
beschriebene rote CodeQL-Ausführung an `674e7fe` ist ein historischer Befund,
kein aktueller Uploadblocker dieses Merge-Stands.

Die historischen direkten Gegenprüfungen bleiben **RC: 5 failed / 5 passed**,
**OOS-021: 1 failed**, **CB-01: MISSED**. Der P4-Verfahrensvorbehalt bleibt
offen. Ruff meldet weiterhin 27 Fehler, Format 24 Dateien und Mypy neun
Fehler; der bestehende CI-Workflow toleriert diese Exit-1-Ergebnisse. Sein
grüner Jobstatus bezeichnet diese Einzelprüfungen nicht als bestanden.
P6 enthält **null neue echte Modell-/Agentenläufe**. Die Registry ist keine
Sicherheitsgrenze gegen kompromittierte Collector-, CLI-, Python- oder
Kernelprozesse. Die begrenzte technische Akzeptanz schließt keine der
genannten Grenzen und erfüllt nicht die vollständige Paketabnahme.

Vollständige Originalbelege, JUnit, Quellenhashes, Risikobewertung und
Abnahmematrix: lokale Ablage
`/Users/landjunge/.threaddesk/artifacts/agent-authority/product-finalization-20261010/`.
Die frühere fehlerhafte formale Entscheidung und ihre Quellen-/JUnit-/Remote-
Prüfung liegen unverändert unter `formal-p6-acceptance-20261010/`. Die
übergeordnete Statuskorrektur liegt unter `p6-status-correction-20261010/`;
Mergebefehle, Remote-Belege, Original-CI-/CodeQL-Logs und Digests unter `pr27-integration-20261010/`.
Die Prüfung wiederholt keine unveränderten Tests und keinen P5-Lauf.

P7 ist nicht freigegeben: Die vollständige P6-Paketabnahme fehlt. Codex hat
den irrtümlich erteilten P7-Auftrag 590 mit Whiteboard-Eintrag 719 widerrufen.
Grok hatte bereits einen sauberen Worktree angelegt und Arbeitsbeginn gemeldet.
Nach dem Widerruf wurden zwei uncommittete P7-Dateien und gezielte Prüfungen
beobachtet; Codex pausierte daraufhin die bestehende Sitzung. Die Dateien sind
unverändert gesichert. Diese Arbeiten sind nicht freigegeben oder abgenommen.
Ein Empfangsnachweis des Widerrufs fehlt weiterhin. P8 und P9 bleiben wartend.
D-012 bleibt unverändert: Authority beobachtet, analysiert und warnt; es
vergibt keine Rechte, Secrets, Budgets oder Permits und bildet kein Stop-Gate.

## Nachtrag: integrierte Sicherheitsreparatur und offene Paketentscheidung

Stand: 11. Oktober 2026. Dieser Nachtrag ergänzt die bisherigen Prüfstände;
ihre damaligen Ergebnisse und Entscheidungen bleiben erhalten. Die technische
Reparatur aus Nutzerfreigabe WB1098 und die Integration aus WB1549 sind
abgeschlossen. Nutzerentscheidung WB1597 behandelt den historischen
P4-Verfahrensvorbehalt als akzeptiertes, weiterhin ungeklärtes Restrisiko.
**Die formale P6-Paketabnahme bleibt OFFEN. P7, P8 und P9 sind nicht freigegeben.**

[PR #30](https://github.com/landjunge/agent-authority-lab/pull/30) ist regulär
gemergt. Squash `ba34d92744553f3504ca7665f4c367f76a5d1013` hat genau einen
Parent, `21691ae9817f832ecfb111f980b0c8a3e6b63d61`. Sein Tree
`c056c1630d73c95a29c9950050415f13952a5725` ist identisch zum unabhängig
geprüften Kandidaten `4a9d42e23ea07b21eeacc228d09889587a1ac329`.
Remote-master zeigte beim abschließenden Readback auf diesen Squash.
Regeln, Reviews, HEAD, CI, CodeQL und SARIF wurden vor der Integration frisch
geprüft; Ready und Squash-Merge mit `--match-head-commit` liefen ohne Admin,
Force oder Bypass. WB1593 dokumentiert den Abschluss.

Die vor der Umsetzung archivierte
[Reparaturspezifikation](SECURITY-REMEDIATION-SPEC-20261011.md) definiert
ausdrücklich das neue Forschungsprofil `RemediationLab`. Die gebundene
Zustimmung gilt in diesem Profil; der Lifecycle-Fix gilt für `FakeAdapter`.
Die historischen `Lab`-/MISSED-Referenzen, Kataloge und Assertions bleiben
unverändert. Ein neuer Schließungsnachweis ändert keinen alten FAIL/MISSED.

| Fall | Neuer technischer Nachweis | Erhaltene Grenze |
| --- | --- | --- |
| RC-01 | Unveränderte RC-Assertion besteht mit RemediationLab; ungebundene Mutation der IDE-Steuerdatei wird vor dem Fake-Sink abgewiesen. | Keine Aussage über eine reale IDE; historisches Lab bleibt Referenz. |
| RC-02 | Unveränderte RC-Assertion besteht; ungebundene Mutation der MCP-Steuerdatei wird abgewiesen. | Kein realer MCP-Start oder allgemeiner Adapterbeweis. |
| RC-03 | Unveränderte RC-Assertion und zusätzliche Kontrolle mit zuerst gültiger Zustimmung bestehen; geänderte Parameter passen nicht zur Bindung. | Keine kryptographische Herkunfts- oder Identitätsauthentisierung. |
| RC-04 | Unveränderte RC-Assertion und zusätzliche Kontrolle mit zuerst gültiger Zustimmung bestehen; geänderte Shell-Komposition und Replay werden abgewiesen. | Opaque Fake-Effekte benötigen zusätzliche Zustimmung; kein globales Default-Deny. |
| RC-05 | Unveränderter Runner wird bei cache.poison gestoppt; zusätzlicher direkter Publish-Test weist den gestohlenen, nicht ausgestellten Handle ab. | Die eingefrorene Runner-Assertion selbst erreicht den späteren Publish-Sink nicht. |
| OOS-021 | Ursprüngliche unveränderte Probe besteht: nach finish erscheint src/late.py nicht. Einmaliges Commit-Ticket ist an die Generation gebunden. | ALLOW und effect_committed sind getrennt; Callbackfehler haben keinen allgemeinen Rollback. |
| CB-01 | Neue Kontrollen am unveränderten Katalog weisen fehlende Zustimmung und Replay nach der ersten erlaubten Wirkung ab; gültige neue Zustimmung bleibt nutzbar. | Historischer MISSED-Test bleibt MISSED auf Lab; sein PASS ist kein Reparaturbeleg. |

Grok prüfte den Hauptcommit unabhängig im eigenen sauberen Worktree (WB1442):
61 Reparaturtests, ursprüngliche OOS-Probe, historische RC-/CB-Kontrollen,
10 unveränderte RC-Assertions im Reparaturprofil, 47 P6-/Anschlussprüfungen,
vier P4-Prüfungen und 434 Gesamttests mit fünf historischen RC-Abwahlen.
WB1525 bestätigt den exakten finalen HEAD mit Diffprüfung und 62
Reparatur-/OOS-Tests. Codex führte die vollständige Suite wegen der letzten
Teständerung vor Merge erneut aus: **434 passed, 5 deselected**, Exit 0.
Die historische RC-Referenz wird dadurch nicht als grün ausgewiesen.

Grok bestätigte anschließend auch die vollständige Suite am identischen
gemergten Tree (WB1594): **434 passed, 5 deselected**, Exit 0, eigener sauberer
Worktree. Original-JUnit und Log sind gegengeprüft; alle 180 Quellenhashes
stimmen mit dem Kandidaten überein. Auch diese Prüfung hebt P4s STOP nicht auf.

[Push-CI 38093141005](https://github.com/landjunge/agent-authority-lab/actions/runs/38093141005)
ist am Squash erfolgreich; die Rohlogs enthalten zweimal 434 tatsächliche
Passpunkte. [CodeQL 38093141018](https://github.com/landjunge/agent-authority-lab/actions/runs/38093141018)
ist erfolgreich, einschließlich vollständig verarbeitetem Ergebnisupload.
Vor Merge war das SARIF-Artefakt `11684597801` am identischen Kandidaten
verfügbar. Bestehende globale Qualitätsaltlasten bleiben sichtbar: 27 Ruff-
und neun Mypy-Befunde werden von der CI toleriert. Job-SUCCESS bedeutet
nicht, dass diese Einzelprüfungen fehlerfrei sind.

### P4-Entscheidung und Abgleich der übrigen P6-Kriterien

P4s historischer Prüfer-B-STOP betrifft beschriebene gitignorierte Caches.
Der damalige Writer bleibt nicht zugeordnet. Die aktuelle Prüfung verwendet
Python 3.12.13, einen tatsächlich blockierten Cacheprovider ohne Cacheinstanz
und temporäre Prüfdateien außerhalb des Repository. Die historischen
Cachehashes sind vor/nach der neuen Vollsuite identisch. Das trägt ein
aktuelles Verfahrensurteil, rekonstruiert aber keine historischen Prozesstraces.
Die ursprüngliche [P4-Abnahme](P4-ABNAHME.md) bleibt unverändert.

Die auftraggebende Stelle hat den historischen P4-Vorbehalt mit WB1597
ausdrücklich auf Entscheidungsebene behandelt: **akzeptiertes ungeklärtes
Restrisiko**, keine rückwirkende Entlastung und kein Nachweis des damaligen
Writers. Diese Entscheidung entwertet die späteren Reparatur-/Testergebnisse
nicht automatisch. Ein weiteres P4-Verfahrensurteil wird hier nicht verlangt.

Codex gleicht gemäß WB1597 die übrigen ursprünglichen Kriterien aus WB27
mit den Originalbelegen ab. Die 40 P6- und sieben Markerfälle aus dem
gezielten 47er-Lauf sind auch in Groks ursprünglichem 434er-JUnit enthalten
und dort fehlerfrei; die Quellen sind zum integrierten Tree identisch.
Die folgende Bewertung ist ein technischer Kriterienabgleich, kein Abnahmeurteil.

| Ursprüngliches Kriterium / bestehende Verpflichtung | Originalnachweis und Bewertung |
| --- | --- |
| Kein falsch authentisierter Quellenbeleg | Erfundenes Bundle, explizites current, direkte FD-Packets und behauptete Herkunft bleiben unbekannt; 40 P6-Regressionen einschließlich dieser Negativfälle bestanden. |
| Stale/gefälschte/fehlende Belege bleiben UNBEKANNT | Klassen-/Replayfälle, abgelaufene oder veränderte Kontexte und Fork bestehen; historische Zeilenkonsistenz wird nicht zu aktueller Herkunft umgedeutet. |
| Mindestens ein brauchbarer enger positiver Relationsfall | Tatsächlicher leerer lokaler Dateieffekt nach Ende sowie gleichzeitig gehaltene gleiche/verschiedene FD-Paare unabhängig am Ziel gemessen; Herkunft und Agentenidentität bleiben UNBEKANNT. |
| Keine sensiblen Rohdaten im geprüften Beobachterpfad | Minimierte Projektionen weisen künstliche Metadatenmarker und rohe FD-Eingänge ab; sieben Markerfälle prüfen leere private reguläre Dateien und unveränderte vorhandene Marker. Kein allgemeiner E2-Bereinigungsnachweis für andere Kanäle. |
| Tests belegen das konkrete Ziel, Regressionen bleiben grün | 47 gezielte Tests, 434 Standardtests und separate unveränderte RC-/OOS-Kontrollen mit Original-JUnit/Logs belegt; fünf historische RC-Abwahlen offen ausgewiesen. |
| Unabhängigkeit von P5 und Erhalt alter Erwartungen | Historische P5-Erwartungen/Archive und ursprüngliche Kataloge/Assertions bleiben unverändert; notwendige Anschlussänderungen gehören zum dokumentierten P6-Auswertungsvertrag. PR30 ändert keine P5-Dateien; kein erneuter P5-Paket-/Modelllauf. |
| D-012 und Zuständigkeit | Observer bleibt beobachten/analysieren/warnen; gebundene Fake-Zustimmung ist Teil des ausdrücklich genehmigten RemediationLab-Forschungsprofils, keine operative Authority-Befugnis. |
| Reguläre Integration mit Remote-Nachweis | PR30, Kandidat/Squash/Parent/Tree/master, erfolgreiche Push-CI/CodeQL und vorheriges SARIF-Artefakt belegt; kein Admin/Force/Bypass. |
| Unabhängige technische Gegenprüfung | Grok WB1442/1525/1594 mit Originalfällen, Kontrollen, finalem Tree und vollständiger Suite bestätigt. Sein gesonderter Kriterienabgleich zum neuen Auftrag WB1597 wird separat dokumentiert. |

Im ursprünglichen P6-Monitoring-Scope hat Codex damit keinen zusätzlichen
fehlgeschlagenen technischen Abnahmenachweis festgestellt. Die historischen
RC-/CB-Referenzen bleiben auf Lab rot/MISSED; ihre neuen Reparaturnachweise
gelten im genehmigten RemediationLab-Profil. Ein neuer echter Modelllauf,
Linux/tmpfs-Nachweis oder eine allgemeine Quellenauthentisierung ist dadurch
nicht belegt und wird nicht als zusätzliche erfüllte Fähigkeit ausgegeben.

Noch fehlt die **ausdrückliche formale P6-Paketentscheidung** nach dem
angeforderten unabhängigen Kriterienabgleich. WB1597 erteilt sie ausdrücklich
nicht; WB1098 und WB1549 ebenso wenig. Der neue Dokumentationsnachtrag liegt
zunächst als Draft-PR vor; seine Integration ist gesondert zu behandeln.
Weder P4s Risikoannahme noch eine spätere P6-Paketentscheidung erteilt einen
P7-Auftrag; hierfür bleibt eine eigene ausdrückliche Freigabe nötig.

Originalbefehle, UTC, JUnit, Logs, Quellen-/Cachehashes und Remote-Belege:
`/Users/landjunge/.threaddesk/artifacts/agent-authority/security-remediation-20261011/`
und `pr30-merge-20261011/`. Der zweite Ordner enthält `ABSCHLUSS.md`,
`MERGE-STATUS.json`, `P4-VERFAHRENSVORBEHALT.md` und `SHA256.json`.
D-012 gilt unverändert: beobachten, analysieren und warnen, keine operative
Gate-, Rechte-, Secret-, Budget- oder Permit-Befugnis. Herkunft und Actor bleiben
bei fehlender Authentisierung UNBEKANNT; der aktuelle Nachweis ist ein Fake-Lab-
und Beobachterprüfstand, keine allgemeine Agentensicherheits- oder Produktfreigabe.


## Formale P6-Paketabnahme: Nutzerentscheidung WB1602

Die auftraggebende Stelle hat am 11. Oktober 2026 die **formale P6-Paketabnahme
für den dokumentierten Umfang ausdrücklich erteilt** (WB1602,
`eccc0ccab937`, 10. Oktober 2026, 23:17:26 UTC). Dieser spätere Entscheid
schließt die oben noch offene Paketentscheidung; die bisherigen Prüfstände
und Originalbelege bleiben als Historie erhalten.

Die Abnahme gilt für den integrierten Stand
`ba34d92744553f3504ca7665f4c367f76a5d1013`. Grundlage sind Codex' Kriterienabgleich
WB1598, Groks unabhängiger Abgleich WB1599 und dessen Matrixbestätigung WB1600,
die integrierte Sicherheitsreparatur PR30 sowie Groks Vollsuite WB1594 mit
434 bestandenen Fällen und fünf ausdrücklich ausgewiesenen historischen
RC-Abwahlen. Beide Prüfer haben keinen weiteren fehlenden Nachweis aus dem
ursprünglichen P6-Auftrag festgestellt. Die dokumentierten RC-/CB-Nachweise
gelten im genehmigten RemediationLab, OOS-021 im FakeAdapter. Historische
Lab-FAIL-/MISSED-Referenzen werden nicht umgedeutet.

P4s Verfahrensvorbehalt bleibt gemäß WB1597 ein **akzeptiertes, weiterhin
ungeklärtes Restrisiko**; der damalige Writer bleibt unbekannt. Es gibt keine
rückwirkende Entlastung. Die Abnahme beweist weder universelle Sicherheit
noch reale Agentenüberwachung. D-012 und die dokumentierten Herkunfts-,
Modell- und Qualitätsgrenzen bleiben erhalten.

**P7, P8 und P9 sind durch diese Entscheidung nicht freigegeben oder gestartet.**
Separate ausdrückliche Phasenfreigaben bleiben erforderlich. Der
Dokumentations-PR31 ist weiterhin ein eigener Draft; die Paketabnahme wird
nicht von seinem Merge abhängig gemacht.

Die wörtliche Nutzerentscheidung, der frühere offene Status, der append-only
Dokumentationsdiff und die Abschlussbelege sind getrennt archiviert unter
`/Users/landjunge/.threaddesk/artifacts/agent-authority/formal-p6-acceptance-20261011/`.

### Aktualisierter Dokumentationsstand nach P8-Integration

Stand: 11. Oktober 2026. Die ursprüngliche formale P6-Entscheidung WB1602
bleibt unverändert; sie ist nicht erneut zu erteilen. Die damaligen Aussagen
zu P7/P8/P9 beschreiben ausschließlich den Umfang dieser P6-Entscheidung.
Spätere konkrete Nutzerentscheidungen erlaubten P7 und P8: PR32 wurde auf
`64bf757` integriert (WB1616/1619), PR33 auf `2523568` (WB1628/1630), jeweils
mit erfolgreicher tatsächlicher Push-CI und CodeQL. P9s Voraussetzung aus
WB34 ist erfüllt; seine bedingte Arbeit nach WB1605 und Teamprüfung ist
begonnen, ohne automatische P9-Paketabnahme oder weitere Mergefreigabe.

PR31 wurde durch einen gewöhnlichen Merge des bestätigten master-Standes
`2523568` aktualisiert, ohne History-Rewrite oder Force-Push. Gegen master
bleibt ausschließlich dieser ergänzende P6-Dokumentationsnachtrag. Alle
früheren Textpräfixe und Originalbelege bleiben erhalten. Die konkrete
Integration dieses eigenen Dokumentations-PRs ist noch nicht freigegeben;
er bleibt Draft. D-012, historische Referenzen, profilgebundene Remediation,
unbekannte Herkunft und P4s akzeptiertes ungeklärtes Restrisiko gelten weiter.
