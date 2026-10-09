# P6: Herkunftsgrenzen und isolierte Auswertungskorrekturen

Stand: 9. Oktober 2026. Auftrag: ThreadDesk-Thread `833554dffb6e`,
Eintrag 27; Gegenkontrollen und Lösungsvorschlag: Eintrag 36.
**P6 ist noch nicht vollständig abgenommen. Kein Merge und keine P7-Freigabe.**

## Basis und Zuständigkeit

Der GitHub-Connector bestätigt `master` an
`0f6b601e2212cde9f7d44f14927de39629250b34`, den Merge von PR 21.
P5 ist abgeschlossen und wurde nicht wiederholt. Seine Dateien, Tests und
Archive bleiben bytegleich. Codex ist der einzige Integrator und bearbeitet
`scripts/p1_controlled_run.py` sowie die neuen P6-Tests und diesen Bericht.
Grok bekam ausschließlich einen lesenden Prüfauftrag. Nach 45 Sekunden lag
keine auftragsbezogene Antwort vor; der Versuch wurde beendet. Ein Teamstart
oder Prüferurteil ist nicht belegt.

Der direkte Shell-Zugriff auf GitHub scheitert an DNS. Der verbundene
GitHub-Connector funktioniert für Repository-Lesezugriffe. Die Branchantwort
weist `protected=false`, ausgeschaltete Statuscheck-Erzwingung und leere
Pflichtchecklisten aus. Die Protection-Detail-API antwortet mit 403 wegen
Integrationsrechten; Rulesets mit 403 wegen des privaten Repositorytarifs.
Das ist keine allgemeine Aussage über verfügbare Administrationsrechte.

## Konkrete Änderungen

`assess()` verwendet ohne Klassenargument jetzt `stale` statt `current`.
Ein Archiv erhält damit keine aktuelle Geltung allein durch den Default.
Für `missing`, `stale` und `forged` werden Agentenlauf und unabhängige
Agentenbindung nicht mehr aus gespeicherten Zählern und Referenzen übernommen.
Ungültige Klassentypen werden vor der Mengenprüfung abgefangen und als
`forged` ausgewertet; ein Dictionary verursacht keinen `TypeError` mehr.
Providertexte und fremde Metadaten werden weiterhin nicht kopiert.

Die historischen Aussagen aus konsistenten Beobachtungszeilen bleiben
auswertbar. `BELEGT` in der historischen Wirkungsprojektion bezeichnet die
Konsistenz der übergebenen Zeilen, keine authentisierte aktuelle Wirkung.
Aktuelle Geltung, Agentenlauf und Herkunft sind davon getrennt.

## Gegenkontrollen

Die unveränderten, vor Ausführung definierten zwölf Kontrollen wurden vor und
nach dem Patch ausgeführt. Die alten Ergebnisse wurden nicht überschrieben.

| Fall | Gegenkontrolle | Vorher | Nachher |
|---|---|---|---|
| P6-01 | Tatsächlich gemessene lokale leere Datei, kein Modell | PASS | PASS |
| P6-02 | Fehlende Beobachtung und Referenz | PASS | PASS |
| P6-03 | Explizit alte, konsistente Zeilen | PASS | PASS |
| P6-04 | Vollständig erfundene Counts und Referenz, `forged` | FAIL | PASS |
| P6-05 | Archivformat ohne Klassenargument | FAIL | PASS |
| P6-06 | Untrusted FD-Claim über `assess()` | PASS | PASS |
| P6-07 | Fremdes Dictionary direkt an interne FD-Projektion | FAIL | FAIL |
| P6-08 | Behauptete Quellenauthentisierung | PASS | PASS |
| P6-09 | Künstliche Metadatenmarker und fremde Eventfelder | PASS | PASS |
| P6-10 | Dictionary als Klasse | FAIL | PASS |
| P6-11 | Tatsächlich gleichzeitig gehaltene reguläre FDs | PASS | PASS |
| P6-12 | Linux/tmpfs/SCM_RIGHTS-Verifier auf Darwin | SKIP | SKIP |

Vorher: **7 PASS / 4 FAIL / 1 SKIP**, Diagnose-Exit 2.
Nachher: **10 PASS / 1 FAIL / 1 SKIP**, Diagnose-Exit 2.
Die Diagnose ist weiterhin rot. Ihr FAIL wird nicht zu PASS oder SKIP umetikettiert.
P6-07 verletzt absichtlich den bestehenden internen Aufrufervertrag. Er belegt
keinen erreichbaren CLI-Angriff, zeigt aber die fehlende technische Bindung
der Projektion an den tatsächlichen Verifier-Aufruf.

Die neuen Regressionstests prüfen auch gleichzeitige `fstat`-Messungen an
`dup(A)` und einer anderen Datei B: die erste Relation ist gleich, die zweite
verschieden. Herkunft bleibt unbekannt. Die Descriptoren bleiben während
beider Messungen geöffnet und werden anschließend geschlossen. Dies ist
keine Linux/tmpfs-Messung und kein Nachweis dauerhafter Ressourcenidentität.

Zusätzlich dokumentiert ein Test die verbleibende Aufrufergrenze:
**Explizites `current` kann aus einem vollständig erfundenen, konsistenten
Bundle weiterhin einen positiven Agentenlauf erzeugen.** Dieser Test ist eine
Charakterisierung der offenen Grenze, keine bestandene Sicherheitsanforderung.
Die isolierten Änderungen schließen diesen Befund nicht.

## Validierung

- P6 plus bestehende P3/P4/P5-Tests: 30 passed, Exit 0.
- Zwei Gesamtläufe: jeweils 338 passed, 5 deselected, Exit 0.
- Ruff Check und Formatcheck der geänderten Python-Dateien: PASS.
- Kein neuer echter Modell-/Agenten-Testlauf. Der lokale Dateieffekt stammt
  aus dem bestehenden synthetischen Testwerkzeug.
- Die fünf Abwahlen sind die bestehenden RC-01–05; sie werden nicht als
  erfolgreiche Sicherheitsprüfungen gezählt. OOS-021 liegt außerhalb der
  Standardsuite. RC-01–05, OOS-021, CB-01 und der P4-Cachebefund bleiben offen.
- Remote-CI und Veröffentlichung müssen am tatsächlichen PR-Head geprüft
  werden. Eine grüne Regression ersetzt keine vollständige P6-Abnahme.

Der erste Remote-Schreibversuch (`github_create_blob`) wurde vor Ausführung
mit `MCP tool call requires approval, but approval policy is never` abgewiesen.
Deshalb ist kein Blob, Remote-Branch oder PR aus dieser Sitzung angelegt,
kein Push nachgewiesen und kein Merge erfolgt. Dieser Veröffentlichungsblocker
besteht zusätzlich zur offenen fachlichen Abnahme. Er wird nicht durch ein
anderes Terminal oder durch veränderte Sicherheitsregeln umgangen.

Die lokalen, exklusiv angelegten Vorher-/Nachherbelege liegen unter
`/Users/landjunge/.threaddesk/artifacts/agent-authority/operative-p6-20261009T210912Z/`.
Der unveränderte Diagnose-Runner liegt im dort referenzierten ursprünglichen
P6-Artefaktverzeichnis. Reproduzierbare Regressionen im Checkout:

```sh
python -B -m pytest -p no:cacheprovider tests/test_plan_p6_boundaries.py
python -B -m pytest -p no:cacheprovider
```

## Offener Abschlussblocker und notwendige Anschlussarbeit

`current` ist weiterhin nur eine explizite Aufrufer-Vorbedingung; es ist kein
vom tatsächlichen Collector gehaltener Ausführungskontext. `bind()` prüft
interne Konsistenz, keine Quellechtheit. `apply_fd_measurement()` interpretiert
ein Verifier-Ergebnis, kann dessen tatsächliche Herkunft selbst nicht belegen.
JSON-Flags, Dataclasses, Hashes und konsistente Referenzen authentisieren
diese Eingänge nicht.

Für den vollständigen P6-Abschluss müssen diese Übergänge an die reale
Aufnahme gebunden werden: beobachteter Modell-/Toolprozess, Run und Mess-Epoche,
unabhängige Zielmessung und ein eng begrenzter lebender Kontext; FD-Projektion
unmittelbar nach dem gepinnten Verifier-Aufruf mit gehaltenen FDs und passender
Vor-/Nachmessung. Aus importiertem JSON darf dieser Kontext nicht erzeugt
werden. Archiv-Replay muss historische Aussagen mit unbekannter aktueller
Geltung ausweisen. Dabei darf auch der aktuelle P5-Anschluss nicht länger
Archive durch ein selbst gesetztes `current` als frische Aufnahme behandeln.
Dieser Anschlussumfang ist durch die bisherige Vorgabe, P5-Dateien und Tests
nicht zu ändern, nicht als isolierter P6-Patch durchführbar. Diese Abhängigkeit
wird als Blocker dokumentiert; kein weiterer Anschluss wird hier implementiert.

P6 bleibt offen. P7 setzt vollständige Abnahme, Remote-Push und Merge von P6
voraus. P8 wartet auf P7, P9 auf P8. Kein Folgepaket wurde gestartet.
D-012 bleibt bindend: Authority beobachtet, analysiert und warnt; es erteilt
keine Rechte, Secrets oder Budgets und bildet kein Stop-Gate.
