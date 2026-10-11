# Plan ABC: versionierte Abschrift der Whiteboard-Fassung

Stand dieser Abschrift: 2026-10-11. Die Quelle ist das append-only Whiteboard von ThreadDesk, Thread `833554dffb6e`. Die fünf Abschnitte unten geben das gespeicherte Feld `content` wortgleich wieder. Diese Datei ändert keine Whiteboard-Einträge, keine eingefrorenen Hypothesen und keine historischen Forschungsberichte.

Die Git-Versionierung ist die einzige hier erteilte Freigabe. R0, A1, A2, B1, B2, C1 und A3 werden dadurch nicht ausgeführt. Eine Mergefreigabe entsteht nicht. D-012 bleibt bestehen: Agent Authority beobachtet, analysiert und warnt.

Weicht diese Abschrift vom gespeicherten JSON ab, gilt das JSON unter `/Users/landjunge/.threaddesk/whiteboard/833554dffb6e/`. Die SHA-256-Werte beziehen sich auf die UTF-8-Bytes von `content`.

## Versionsreferenzen

| Feld | Wert |
| --- | --- |
| Thread | `833554dffb6e` |
| Basis-Commit | `3a9c0067a6e59a55b8e578b6ad870ffe6c74cb47` |
| Basis-Tree | `da6dedbd5c48f8f2b021acbb2999a5631e40ba26` |
| Basis-Parent | `35f592f0d8a9040ccb7c5f48cc22ac1b0c091729` |
| Remote-Branch zum Abschriftzeitpunkt | `master`, Merge 2026-10-11T17:54:13Z, PR 43 |
| PR19-Pin aus dem Plan | `f94f444e383052d04e2ef22bfed4ec03512cb066` |
| PR17-Pin aus dem Plan | `b24a6305faecc46ec673dea8207b2ab83ab655df` |
| D-012 | `landjunge/KI-Zentralle`, `DECISIONS.md`, Überschrift vom 2026-10-07 |
| Forschungsmethode | `docs/RESEARCH-METHOD.md` am genannten Tree, Abschnitte 1, 3, 4, 8 und 9 |

## Eintragsverzeichnis

| Ordinal | ID | Zeit (UTC) | SHA-256 von `content` | Rolle im Plan |
| --- | --- | --- | --- | --- |
| 1916 | `8a6ad14b8d21` | 2026-10-11T18:46:26.702845+00:00 | `33585534c717b6b343c7baa3047eb5384ef020ad730b414cbef2c7de363edacc` | Lage, Pins, bereits entschiedene Grenzen |
| 1917 | `1d183de16715` | 2026-10-11T18:46:26.949498+00:00 | `3cd80b9e08ecb9983187d44c6f9f242da0e15c25b4f5e63e9dbbd03b1387b635` | R0, A1, A2 und eingefrorene Hypothesen |
| 1918 | `e928a5ee1fbe` | 2026-10-11T18:46:27.186744+00:00 | `943a64a25ed1b936e5fc554a5440d0bfc71bb98aa9facbe46e6806fb005f3ce4` | B1, B2, C1 und gesperrtes A3 |
| 1919 | `690cba9f2cd2` | 2026-10-11T18:46:27.398158+00:00 | `4c54626f600381c9bc17bd60630656720e88be3546b5d49c042a74b75d221018` | Reihenfolge, Aufwand, STOP, offene Entscheidungen E1–E6 |
| 1920 | `75b8902f3202` | 2026-10-11T18:58:23.380898+00:00 | `de21a89492c76d2bbdbe0c9e9d0873db3200a9042d93817229747341dca17ab1` | Nachtrag: Negativpfade, getrennte Bewertung, Zeitblöcke, Neubewertung nach R0 |

Hypothesen, Abhängigkeiten, STOP-Bedingungen und die Entscheidungen E1–E6 stehen wortgleich in den Einträgen 1917, 1918, 1919 und 1920. Eine zweite Formulierung wird hier nicht angelegt.

Der Nachtrag 1920 lässt die Einträge 1916–1919 inhaltlich unverändert. Seine Planungshypothese von etwa 12,5 Arbeitstagen ergänzt die Bauzeitschätzung von etwa 8 Arbeitstagen aus Ordinal 1919. Beide Zahlen bleiben Schätzungen. Die Modelllaufzeit bleibt UNBEKANNT.

## Ordinal 1916 — `8a6ad14b8d21`

- Zeit: 2026-10-11T18:46:26.702845+00:00
- Art: note
- Akteur: Grok / grok
- Aufgabe: `aa-plan-abc-20261011`
- Externer Schlüssel: `grok-aa-plan-abc-20261011-1`
- SHA-256: `33585534c717b6b343c7baa3047eb5384ef020ad730b414cbef2c7de363edacc`

```text
PLAN ABC 1/4 — Lage und Grenzen. Nur Dokumentation. Kein Code, kein Test, kein Lauf, kein Merge. Dieser Eintrag ist eine Aufzeichnung, kein Wahrheitsbeweis. Labels: BELEGT, WIDERLEGT, HYPOTHESE, UNBEKANNT.

Auftrag: Plan für (A) überprüfbare Ereignisherkunft und Prozess-/Wirkungszuordnung, (B) unvollständige, manipulierte oder verspätete Beobachtungen, (C) messbare Zuverlässigkeit an realen lokalen Agentenläufen. D-012 bleibt: beobachten, analysieren, warnen. Keine ALLOW/DENY-Entscheidung, keine Rechte, kein Stoppen, keine Secret- oder Budgetfreigabe.

BELEGT, D-012: GitHub landjunge/KI-Zentralle DECISIONS.md, Überschrift „D-012 — Agent Authority beobachtet“, Datum 2026-10-07. In dieser Sitzung über die GitHub-API gelesen.

BELEGT, Git heute: Remote master 3a9c0067a6e59a55b8e578b6ad870ffe6c74cb47, Tree da6dedbd5c48f8f2b021acbb2999a5631e40ba26, Parent 35f592f0d8a9040ccb7c5f48cc22ac1b0c091729, Merge 2026-10-11T17:54:13Z, PR 43. gh api und git ls-remote. Offene PRs: keine. Sauberer Worktree /Users/landjunge/agent-authority-historical-kinds, HEAD 9de7290dd1be82fca493102048622e6b75908c9f, gleicher Tree. Lokale origin/master-Referenz im Hauptklon bleibt 35f592f0; sie wurde nicht nachgezogen. Hauptklon HEAD 09cbf153ed07 auf feat/authority-emit-g3 mit untracked Dateien. Das ist nicht der Produktstand. PR19-Pin f94f444e383052d04e2ef22bfed4ec03512cb066. PR17-Pin b24a6305faecc46ec673dea8207b2ab83ab655df.

BELEGT, laufende Prozesse, ohne Eingriff: codex exec PID 47737 seit 2026-10-10 21:36, Worktree .codex/worktrees/ad83, alter Auftrag 165. Interaktives codex PID 57185 und grok PID 62716, cwd /Users/landjunge, seit 10.10. abends. Codex-Daemon 95100/95119/96345. Keiner dieser Prozesse wurde beendet. Boardspitze vor diesem Plan: Ordinal 1915, id 4436566c330b. Kein jüngerer Eintrag zu diesem Plan. Ob die beiden TUIs inhaltlich einen anderen Auftrag führen, ist UNBEKANNT. Dirty und nicht anfassen: Hauptklon, agent-authority-p1, agent-authority-p7. Übrige geprüfte Worktrees waren sauber auf alten Zweigen.

BELEGT, enge Beobachtung: P8-Läufe 8930311534831620534 und 3864572638349408912, je ein Modellabschluss, ein Toolbericht, Exit 0, Wirkung BELEGT, Ordnung NACH, 15 Matrixzeilen, Herkunft UNBEKANNT. Quelle docs/P8-PRAXISTEST-20261011.md und docs/p8-runs/2026-10-11-stability/. reference.json von Lauf 01 enthält calls, target_present, valid, order, order_applicable, order_valid. Ein schreibendes PID steht dort nicht.

Zwischenstand und spätere Abnahme bleiben getrennt. P8-COHORT-RESULT.json enthält P8_formal_acceptance=false zum Messzeitpunkt. Der Nachtrag und WB1628 plus PR33-Squash 2523568fdca3e629bfba11361c4fefba2cd2d066 sind die spätere begrenzte Paketabnahme. P6-Frühtext hält die Abnahme offen. Der spätere Abschnitt nennt WB1602, id eccc0ccab937, auf ba34d92744553f3504ca7665f4c367f76a5d1013. P7 ist PR32, Squash 64bf757ee7e32ca3df780b61a698466e2e299899. Der P9-Berichtanfang sagt die formale Abnahme offen. WB1637 id fd12bfee2aaa, WB1639 id 5fd3a880846b und WB1641 id 7fb0cc27ed60 zeichnen eine begrenzte P9-Abnahme und die Merges PR34 fae9215e96f80eacdc397c011403823271ef3342 sowie PR31 edcce435c57a3333408a6afd14c267a2d6389067 auf. Grok-Readback WB1642 id e0f769ff35fb erteilt keine eigene Paketabnahme. Die wörtliche Nutzeräußerung wurde in dieser Sitzung nicht aus einem vom Board unabhängigen Log gelesen. Ihre unabhängige Rekonstruktion ist UNBEKANNT. Die Boardtexte und die Git-Merges sind BELEGT.

BELEGT, Herkunftsgrenze: lab.origin auf macOS belegt den unmittelbaren Mach-Sender und die frische lokale Empfangssitzung. Autor, Modell und Gespräch bleiben UNBEKANNT. Quelle docs/NATIVE-HERKUNFTSMODUL-20261011.md, PR36/37, Byte-Kette WB1705 id da77ece42f40. Erzwungener PID-Reuse ist dort ausdrücklich nicht ausgeführt. Die macOS-Prozessdiagnose in docs/LOKALE-PROZESSBELEGE-20261011.md ist eine Momentaufnahme. source_authenticated bleibt für Autor und Modell falsch. assess übernimmt fehlende, alte und gefälschte Herkunft nicht. Host-FD-Verifier auf diesem Mac ist SKIP, kein Positivbeleg. Quelle P3, P5, P6.

WIDERLEGT: PR17-Gateway als heutige Produktrolle. Der Vertrag verlangt ALLOW, DENY oder REQUIRE_APPROVAL und widerspricht D-012. 16 Charakterisierungstests bestanden, die separat gestartete adversariale Battery zeigte vier MISSED. Quelle docs/RESEARCH-PR-ABGLEICH-20261011.md. WIDERLEGT ist die Aussage, CB-01 sei erkannt worden: Convergence Battery, CB-01 MISSED, k=1, 9 von 10 erwartet erkannt. WIDERLEGT ist die Aussage, ein gemeldetes CLI-Ende beweise Wirkungsfreiheit: kontrollierte Nachläufe P1 Versuch 04, P2, P5, P7, P8. WIDERLEGT ist die Übernahme von source_authenticated=true aus einem Eingangsclaim: forged_authentication, Aussage UNBEKANNT, P3 und P4. WIDERLEGT ist die Deutung, die konservative C1–C7-Simulation erkenne eine kompromittierte Quelle: falsche Positive 3 auf 0 und zugleich nutzbare Positive 5 auf 0. Quelle Abgleich und die an f94f444 gepinnten Ergebnisdokumente. Das ist Enthaltung.

UNBEKANNT und deshalb der eigentliche Plan: kausaler Schreiber einer lokalen Dateiwirkung, Nebenwirkungen außerhalb des einen Zielpfads, Rate realer Läufe jenseits n=2, heutiges Linux-FD-Verhalten, PID-Reuse, Windows- und Linux-Transport, externes Audit. P4-Writer bleibt das akzeptierte ungeklärte Restrisiko WB1597 und wird nicht wieder geöffnet. RC-01 bis RC-05, CB-01 und OOS-021 bleiben historische Grenzen. lab.provenance.record zeichnet Entscheidungszeilen und wird nicht zur Beobachtungsschnittstelle ausgebaut. ThreadDesk ist nach WB1735 keine Agent-Authority-Fläche. Dieser Anhang nutzt nur das bestehende Board 833554dffb6e.

Nicht wiederholen: P1–P8-Matrizen, die zwei P8-Läufe, Mach-Empfang PR36/37, PR19-Sammelmerge, PR17-Service, Qualitätsgate PR40, P10-Vorschauen. Die 309 PR19-Artefakte werden nicht einzeln neu gelesen. Der Abgleich vom 11.10. bleibt die Übersicht. Einzellücken stehen in den Schritten 2/4 und 3/4.
```

## Ordinal 1917 — `1d183de16715`

- Zeit: 2026-10-11T18:46:26.949498+00:00
- Art: note
- Akteur: Grok / grok
- Aufgabe: `aa-plan-abc-20261011`
- Externer Schlüssel: `grok-aa-plan-abc-20261011-2`
- SHA-256: `3cd80b9e08ecb9983187d44c6f9f242da0e15c25b4f5e63e9dbbd03b1387b635`

```text
PLAN ABC 2/4 — Schritte R0, A1, A2. Hypothesen sind eingefroren. Eine spätere Umsetzung darf den Wortlaut nicht an das Ergebnis anpassen. Kein Start vor eigener Freigabe. Historische Specs, Tests und Negativbefunde bleiben unverändert. Neue Prüfung nur additiv.

R0 — Lesepin der acht Belege, von denen A bis C abhängen.
Forschungsfrage: Stimmen die in 1/4 genannten Objekte heute noch mit den zitierten Trees und Archivflags überein?
Eingefrorene Hypothese H-R0: Für die acht Pins master 3a9c006, Tree da6dedbd, P8-Archivflag false, P8-Nachtrag, reference.json ohne Writer-PID, WB1602, WB1628, NATIVE-HERKUNFTSMODUL ist das Objekt am genannten Pfad oder SHA vorhanden und der genannten Aussage gleich. Weicht ein Objekt ab, wird die betroffene Aussage UNBEKANNT, nicht still ersetzt.
Vorhandene Evidenz: die in 1/4 gelesenen Quellen. Diese Sitzung hat die Pins einmal gelesen und nichts verändert.
Echte Lücke: kein versiegeltes Claim-Register mit Datei-Hashes neben dem Board. Das Board allein reicht nicht.
Erlaubte Dateien und Schnittstellen: nur lesen. git ls-remote, gh api, git -C historische Worktrees rev-parse und sha256 der genannten JSON-Dateien. Kein fetch in den Hauptklon, kein Checkout, kein Prozessstart.
Konkrete Tests: keine neuen. Abgleich ist ein Leseskript außerhalb des Repos oder reine Befehle. Ergebnis nur als Board-Nachtrag.
Messgrößen: 8 Pins geprüft, 0 stillen Ersetzungen, Zahl der UNBEKANNT-Abweichungen.
Abnahme: H-R0 ist SUPPORTED nur, wenn alle acht Pins passen. Eine Abweichung macht R0 INCONCLUSIVE für den betroffenen Pin und stoppt A1.
Dauer: 4 Stunden.
STOP: fehlendes Objekt, Hashabweichung, neuer Board-Claim auf dieselben Dateien, Versuch zu schreiben.
Abhängigkeit: ausdrückliche Freigabe dieses Plans. R0 ist der einzige Schritt, den eine Planfreigabe öffnen darf.

A1 — Schreiber eines vorab benannten lokalen Dateiziels, ohne Autor- oder Modellidentität.
Forschungsfrage: Kann ein Beobachter auf diesem Mac den Prozess nennen, der eine vorab benannte reguläre Datei erzeugt, ohne dessen Selbstangabe zu glauben?
Eingefrorene Hypothese H-A1: In einem versiegelten Versuch mit zwei gewöhnlichen Benutzerprozessen nennt eine vom Schreiber unabhängige lokale Beobachtung PID und Kernelstartzeit des Prozesses, der die vorab benannte leere Datei erzeugt. Ein zweiter Prozess, der nur eine Geschwisterdatei schreibt, ist VERSCHIEDEN. Eine abweichende PID im Agenten-JSON wird nicht übernommen. source_authenticated für Autor, Modell und Gespräch bleibt falsch. Es gibt keine ALLOW/DENY-Folge.
Vorhandene Evidenz: P8-reference.json belegt Zielpräsenz und Ordnung NACH und enthält keinen Schreiber. LOKALE-PROZESSBELEGE belegt eine Momentaufnahme, keine Wirkungsbindung. Mach-Empfang belegt den Nachrichtensender, nicht den Dateischreiber.
Echte Lücke: die Zuordnung Wirkung zu Prozess ist UNBEKANNT. Eine Wiederholung von P8 schließt sie nicht.
Erlaubte Dateien nach eigener Umsetzungsfreigabe: neues Spec-Dokument unter docs/ mit Prefix PLAN-A1-, danach neues Paket lab/effect_attribution/ und neue Testdatei tests/test_effect_attribution_a1.py. Lesend erlaubt: lab/origin nur als Vergleich, scripts/p1_controlled_run.py und scripts/p5_reliability.py als Grenze. Verboten: jede Änderung an docs/p1-runs, docs/p7-runs, docs/p8-runs, historischen Tests, lab/provenance.py, lab/origin/*, ThreadDesk, P5-SKIP-Erwartung.
Konkrete Tests: zwei lokale Prozesse, kein Modelllauf. Positivfall Schreiber gleich Beobachteraussage. Negativfälle Geschwisterschreiber, gefälschte Selbst-PID, Schreiben vor dem Fenster, Schreiben nach dem Fenster, fehlende Beobachtung. Voller Suite-Lauf zweimal, historische fünf Abwahlen unverändert. Die neuen Tests liegen in der Acceptance-Suite. Ein Probe außerhalb der Suite bleibt außerhalb.
Messgrößen: attribution_match für das eine Ziel, false_belegt_on_forged_self_report = 0, sibling_called_same = 0, author_authenticated = false in allen Zeilen.
Abnahme: SUPPORTED nur für diesen Mac und dieses eine Ziel. Generalisierung LOW. REFUTED, wenn jede nutzbare Benutzer-API den Schreiber verfehlt oder eine Selbstangabe übernimmt. Dann bleibt die Zuordnung UNBEKANNT. Kein Ausweichen auf Endpoint Security oder ein privilegiertes Audit in diesem Schritt.
Dauer: Spec 4 Stunden, Umsetzung danach 2 Arbeitstage.
STOP: benötigtes Privileg, Selbstreport als einzige Quelle, Änderung historischer Erwartungen, Eingriff in den Prozess, Parallelbearbeitung von p5_reliability.py oder lab/origin.
Abhängigkeit: R0 SUPPORTED und eigene Freigabe für A1. Spec-Commit vor Code, gemäß docs/RESEARCH-METHOD.md Abschnitt 11.

A2 — Dieselbe Prozessbindung für Nachrichtensender und Dateischreiber.
Forschungsfrage: Sind der unmittelbare Mach-Sender und der Dateischreiber in einem versiegelten Versuch derselbe Prozess, und bleibt ein Relay sichtbar?
Eingefrorene Hypothese H-A2: Sendet derselbe Prozess genau eine native Origin-Nachricht und erzeugt das Ziel, stimmen Audit-PID samt PID-Version mit der A1-Bindung überein. Sendet ein Relay, während ein anderer Prozess schreibt, ist effect_sender_same falsch. Der Nachrichteninhalt erhält dadurch keinen Autor. Ein kopiertes Receipt bleibt kein neuer OS-Nachweis.
Vorhandene Evidenz: NATIVE-HERKUNFTSMODUL und WB1705 belegen den unmittelbaren Sender. Die Dateibindung fehlt, deshalb ist die Gleichheit UNBEKANNT.
Echte Lücke: zwei bereits belegte Ebenen sind nicht verbunden. A2 erfindet keine dritte Identität.
Erlaubte Dateien: neues docs/PLAN-A2- und tests/test_effect_sender_a2.py. lab.origin.receive wird aufgerufen und nicht verändert. lab/effect_attribution aus A1 wird nur gelesen, sofern A1 schon akzeptiert ist.
Konkrete Tests: ein echter macOS-Mach-Empfang mit zwei Prozessen, plus Replay der Wirebytes erwartet UNBEKANNT mit replayed_local_session. Kein zweiter Modellagent.
Messgrößen: sender_effect_same im Direktfall, sender_effect_same=false im Relay, author_authenticated=false, replay_accepted=0.
Abnahme: SUPPORTED nur für diesen einen Handshake auf diesem Mac. Generalisierung LOW.
Dauer: 1 Arbeitstag nach A1.
STOP: A1 REFUTED oder INCONCLUSIVE, Änderung am Origin-Empfänger, fehlender Kernel-Trailer, Versuch, Gesprächs- oder Modellidentität zu setzen.
Abhängigkeit: A1 SUPPORTED und eigene Freigabe für A2.
```

## Ordinal 1918 — `e928a5ee1fbe`

- Zeit: 2026-10-11T18:46:27.186744+00:00
- Art: note
- Akteur: Grok / grok
- Aufgabe: `aa-plan-abc-20261011`
- Externer Schlüssel: `grok-aa-plan-abc-20261011-3`
- SHA-256: `943a64a25ed1b936e5fc554a5440d0bfc71bb98aa9facbe46e6806fb005f3ce4`

```text
PLAN ABC 3/4 — Schritte B1, B2, C1 und der gesperrte Schritt A3. Kein Start vor eigener Freigabe. P3-, P5- und P6-Matrizen für fehlende, alte, gefälschte und nach dem Ende im Fenster liegende Fälle werden nicht erneut als Forschungsfrage gestellt.

B1 — Unvollständige Beobachtung außerhalb des einen Ziels.
Forschungsfrage: Bleibt ein unbeobachteter Geschwisterpfad als unvollständige Beobachtung sichtbar, während Zielabwesenheit keine Wirkungsfreiheit wird?
Eingefrorene Hypothese H-B1: Schreibt der Prozess nur eine Geschwisterdatei, bleibt die Zielzeile abwesend und die Vollständigkeitszeile heißt UNVOLLSTAENDIG. Schreibt er das Ziel, ist die Zielwirkung BELEGT. Die Vollständigkeitszeile behauptet dabei nicht, alle Wirkungen gesehen zu haben.
Vorhandene Evidenz: P8 prüft ein künstliches Ziel. Inventur und P9 lassen unbeobachtete Nebenwirkungen UNBEKANNT. P1 trennt Status von Wirkung für dieses Ziel.
Echte Lücke: eine gemessene Vollständigkeitszeile fehlt. Die 15 P8-Zeilen werden nicht wiederholt.
Erlaubte Dateien: docs/PLAN-B1-, tests/test_observation_completeness_b1.py, neues Modul lab/observation_completeness/. assess und historische Erwartungen bleiben bytegleich.
Konkrete Tests: lokale Prozesse, kein Modell. Fälle Ziel nur, Geschwister nur, beide, keines, Verzeichnis unsichtbar. Suite zweimal.
Messgrößen: false_absence_as_clean = 0, sibling_only_labeled_incomplete im passenden Fall, target_labeled_as_all_effects = 0.
Abnahme: SUPPORTED für diese lokalen Fälle. Allgemeine Vollständigkeit bleibt UNBEKANNT.
Dauer: 1 Arbeitstag. Dateien überschneiden A1 nicht. Die Schreiberzeile wartet auf A1. Die reine Vollständigkeitszeile darf den Schreiber UNBEKANNT lassen.
STOP: Umbau von assess, Umdeutung eines P8-Archivs, Behauptung vollständiger Hostbeobachtung.
Abhängigkeit: R0. A1 nur für die Schreiberzeile.

B2 — Verspätung außerhalb des vorab genannten Fensters und Fremdeingriff vor der Versiegelung.
Forschungsfrage: Wird ein Schreiben nach dem vorab genannten Nachlauf von der Fensterwirkung getrennt, und wird ein zweiter Prozess, der die Aufnahme vor dem Digest erweitert, als unbeglaubigt sichtbar?
Eingefrorene Hypothese H-B2: Ein Schreiben nach dem festgelegten Nachlauf ist SPAETER und nicht die Fensterordnung NACH und nicht Abwesenheit. Ein zweiter lokaler Prozess, der vor der Digest-Versiegelung ein Ereignis anhängt, macht die betroffene Zeile UNBEKANNT mit Grund foreign_capture. Die Zeile wird nicht zur belegten Wirkung. Ein bereits versiegeltes und danach geändertes Archiv bleibt der bestehende P6-Befund und ist hier kein neuer Versuch.
Vorhandene Evidenz: P8 nutzt Nachlauf 5s und 3s und ordnet Wirkung im Fenster als NACH. P6 bindet die Aufnahme an prozesslokalen Kontext und Digest. Die Manipulation nach der Versiegelung ist damit für die geprüften P6-Fälle schon behandelt. Der Eingriff vor der Versiegelung und die Grenze nach dem Fenster sind UNBEKANNT.
Echte Lücke: nur diese beiden Ränder. C1–C7, forged_authentication, stale und missing werden nicht wiederholt.
Erlaubte Dateien: docs/PLAN-B2- und tests/test_late_and_foreign_capture_b2.py. Lesend: scripts/p5_reliability.py und die P6-Digestprüfung. Keine Änderung daran.
Konkrete Tests: ein lokaler Schreiber im Fenster, einer danach, einer der die noch offene Aufnahme erweitert. Kein Modell. Erwartung des Digest-Falls vor dem Lauf einfrieren.
Messgrößen: post_window_called_NACH = 0, post_window_called_absent = 0, foreign_row_belegt = 0, sealed_archive_retest_count = 0.
Abnahme: SUPPORTED für diese drei lokalen Fälle. Eine Garantie gegen einen kompromittierten Host bleibt UNBEKANNT.
Dauer: 1,5 Arbeitstage.
STOP: Änderung der P6-Digestregeln, Aufweichen von Replay-STOP, privilegierter Eingriff, Modelllauf.
Abhängigkeit: R0 und eigene Freigabe. A1 ist nicht erforderlich.

C1 — Vorab festgelegte Zuverlässigkeitskohorte realer lokaler Läufe.
Forschungsfrage: Welcher Anteil von N neuen lokalen Codex-Läufen erfüllt die eingefrorene Matrix, und bleibt die Autoridentität in jedem Lauf UNBEKANNT?
Eingefrorene Hypothese H-C1: N=8 wird vor Lauf 1 festgelegt. Es gibt keinen Retry und keinen Austausch eines Fehlversuchs. Jeder Lauf erfüllt die 15 P8-Zeilen oder der Fehlschlag zählt. Dazu kommen die dann abgeschlossenen A1-, B1- und B2-Zeilen. Autor, Modell und Gespräch bleiben in allen acht Läufen UNBEKANNT. Berichtet wird das Clopper-Pearson-Intervall der vollständig erfüllten Läufe. Auch 8/8 lässt allgemeine Zuverlässigkeit UNBEKANNT. Die zwei alten P8-Läufe zählen nicht mit.
Vorhandene Evidenz: n=2, beide 15/15, P8 nur begrenzt formal abgenommen. P9 fand darin keinen neuen reproduzierten Produktfehler und keine Rate. Convergence 9/10 und Real-Case 5 plus 5 gehören zu anderen Fragen und werden nicht gemischt.
Echte Lücke: keine vorab registrierte Fehlerrate. Eine dritte Wiederholung der alten Matrix ohne neue Zeilen und ohne festes N unterbleibt.
Erlaubte Dateien: docs/PLAN-C1- vor Lauf 1, mit Erwartungs-Hash. Neue Minimierarchive unter docs/c1-runs/ nur nach Lauferlaubnis. Neues scripts/c1_cohort.py ruft vorhandene p5/p7-Funktionen auf und ändert sie nicht. Keine Rohprompts und keine Providertexte ins Board.
Konkrete Tests: vorher ein Fixture, Archiv ohne Kontext ergibt STOP, abgelaufener Kontext ergibt UNBEKANNT. Dann genau acht lokale Codex-Läufe. Timeout und Nachlauf stehen in der Erwartungsdatei. Zwei Nicht-Modell-Kontrollen, gefälschte Selbstangabe und Schreiben nach dem Fenster, zählen getrennt. Suite zweimal vor Lauf 1. Ein Fehlschlag wird gezählt und nicht wiederholt.
Messgrößen: N_gestartet, N_vollstaendig, N_abgebrochen, Clopper-Pearson 95 Prozent, false_author_belegt = 0, retries = 0.
Abnahme: der Bericht nennt Intervall und UNBEKANNT für Autor und allgemeine Zuverlässigkeit. SUPPORTED gilt für die Berechnung aus genau diesen acht Läufen.
Dauer: Protokoll 4 Stunden, Läufe etwa 1 Tag, Auswertung 4 Stunden. Die Laufzeit bleibt UNBEKANNT, bis Lauf 1 eine Dauer zeigt.
STOP: offene A1/B1/B2-Zeile würde als bestanden geführt. Ebenso Retry, N-Änderung nach Lauf 1, Netzwerkgeheimnis, Produktionsziel, fremder Runner-Claim.
Abhängigkeit: R0, abgeschlossene A1, B1 und B2, eigene Freigabe mit festem N. Empfehlung N=8. N=20 nur als Extraauftrag.

A3 — Dauerhafte Dateideskriptor-Identität. GESPERRT.
Forschungsfrage nur bei Extraauftrag: Unterscheidet Linux-SCM_RIGHTS einen ersetzten Deskriptor von der vorher gemessenen Inode-Generation, während ein kopiertes Paket UNBEKANNT bleibt?
Eingefrorene Hypothese H-A3, Ausführung gesperrt: Auf einem benannten Linux-Host ist ein ersetzter FD VERSCHIEDEN, ein kopiertes Zahlenpaket ohne neue Messung UNBEKANNT, source_authenticated falsch. Die P5-SKIP-Erwartung auf macOS bleibt.
Vorhandene Evidenz: PR19-FD-Dokument an f94f444. Passend ersetzte FDs waren als Ursprungstäuschung nicht unterscheidbar. Der alte Verifier kollidiert mit dem heutigen SKIP. Sechs Fehler im isolierten Versuch waren ein Integrationskonflikt, kein Defekt des unveränderten master.
Echte Lücke: vorhanden und außerhalb dieser Freigabe. macOS bleibt unsupported.
Erlaubte Dateien: keine, solange gesperrt. Tests und Abnahme erst nach benanntem Host und neuem Vertrag. Dauer dann 3 bis 5 Tage.
STOP jetzt: Import der alten Verifier-Datei, SKIP-Änderung, PID-Reuse, Windows-Transport.
Abhängigkeit: ein Auftrag, der A3 wörtlich nennt. R0 bis C1 öffnen A3 nicht.
```

## Ordinal 1919 — `690cba9f2cd2`

- Zeit: 2026-10-11T18:46:27.398158+00:00
- Art: note
- Akteur: Grok / grok
- Aufgabe: `aa-plan-abc-20261011`
- Externer Schlüssel: `grok-aa-plan-abc-20261011-4`
- SHA-256: `4c54626f600381c9bc17bd60630656720e88be3546b5d49c042a74b75d221018`

```text
PLAN ABC 4/4 — Reihenfolge, Aufwand, Risiken, offene Entscheidungen. STOP. Keine Umsetzung in dieser Sitzung.

Reihenfolge, strikt: R0, dann A1, dann A2, dann B1, dann B2, dann C1. A3, PID-Reuse, Windows- und Linux-Transport, P4-Writer, RC-01 bis RC-05, CB-01 und OOS-021 bleiben außerhalb. B1 darf die Vollständigkeitszeile ohne A1 entwerfen, der Lauf mit Schreiberzeile wartet auf A1. C1 startet erst, wenn A1, B1 und B2 jeweils SUPPORTED, REFUTED oder als UNBEKANNT abgeschlossen sind. Ein REFUTED-Schritt wird nicht durch eine schwächere Metrik ersetzt.

Aufwand nach Freigabe, eine Person, ohne Paralleländerung: R0 4 Stunden. A1 Spec 4 Stunden plus Umsetzung 2 Tage. A2 1 Tag. B1 1 Tag. B2 1,5 Tage. C1 Protokoll 4 Stunden, Läufe etwa 1 Tag, Auswertung 4 Stunden. Summe der offenen Schritte etwa 8 Arbeitstage. A3 zusätzlich 3 bis 5 Tage nur mit Extraauftrag. Die Modelllaufzeit von C1 ist UNBEKANNT.

Rollen nach bisheriger Arbeitsregel, hier nur vorgeschlagen: Codex setzt später um und mergt regulär. Grok prüft lesend den genannten SHA. Diese Sitzung hat nichts umgesetzt. Eine Planfreigabe ist keine Paketabnahme und kein Merge.

Risiken:
1. Der Hauptklon und die lokale origin/master-Referenz sind älter als Remote master. Ein künftiger Arbeitsbaum muss von 3a9c006 neu angelegt werden. ad83 und PID 47737 bleiben unbenutzt. Die untracked Dateien in Hauptklon, p1 und p7 bleiben liegen.
2. Zwei lange TUIs, PID 57185 und 62716, haben unbekannten Inhalt. Vor R0 ist die Boardspitze erneut zu lesen. Ein fremder Claim auf dieselben Dateien ist STOP.
3. Frühe Sätze in P6, P8 und P9 widersprechen späteren Nachträgen. Der Messflag false und die spätere begrenzte Abnahme sind beide wahr in ihrer Zeit. Nur der spätere formale Umfang gilt als Abschluss, und er ist eng.
4. PASS, 8/8 und n=2 bleiben Suiten- oder Kohortenbefunde. Allgemeine Sicherheit, Autoridentität und vollständige Beobachtung bleiben UNBEKANNT, solange kein eigener Beleg existiert.
5. Ein Linux-FD-Dateiimport kann die P5-SKIP-Erwartung auf FAIL ziehen. Deshalb ist A3 gesperrt.
6. lab.provenance.record und PR17 führen in eine Entscheidungsrolle. Beide bleiben unbenutzt.
7. Dieses Board bindet eine Nachricht nicht an den OS-Prozess. Die Eintrags-ID belegt die Speicherung, nicht den Verfasser. Primärbelege stehen in Git und in den genannten Dateien.
8. Qualitätszahlen aus dem P9-Text, darunter Ruff 28, Format 21 und Mypy 9, sind der damalige Stand. PR40 macht die Qualitätschecks blockierend. Die heutige Befundzahl ist UNBEKANNT und wird hier nicht fortgeschrieben.

Offene Entscheidungen, vor jedem Start:
E1. Ob dieser Plan freigegeben wird. Ohne ausdrückliche Freigabe endet die Arbeit hier.
E2. Ob die Freigabe nur R0 öffnet. Empfehlung: ja. A1 braucht eine eigene Freigabe nach dem Pin.
E3. Ob N für C1 bei 8 bleibt. Empfehlung: 8. 20 ist ein späterer Auftrag.
E4. Ob A3, PID-Reuse und andere Hosts weiter gesperrt bleiben. Empfehlung: ja.
E5. Ob der P4-Writer geschlossen bleibt. Empfehlung: ja, ACCEPTED_UNRESOLVED.
E6. Ob Codex später der einzige Integrator bleibt. Empfehlung: ja.

Globale STOP-Bedingungen: operative Entscheidung, Rechte, Stopp, Secret, Budget, Änderung historischer Tests oder Archive, Änderung einer eingefrorenen Hypothese nach dem ersten Ergebnis, neuer Thread, zweiter Plan auf einem anderen Board, Prozessneustart, Commit, Push oder Merge aus dieser Planrunde.

Nächster erlaubter Schritt nach Freigabe ist allein R0. A1 bis C1 und A3 starten dadurch nicht.
```

## Ordinal 1920 — `75b8902f3202`

- Zeit: 2026-10-11T18:58:23.380898+00:00
- Art: note
- Akteur: Grok / grok
- Aufgabe: `aa-plan-abc-20261011`
- Externer Schlüssel: `grok-aa-plan-abc-20261011-addendum-1`
- SHA-256: `de21a89492c76d2bbdbe0c9e9d0873db3200a9042d93817229747341dca17ab1`

```text
NACHTRAG ABC zu Ordinal 1916–1919. Ein Anhang. Die vier Originale bleiben unverändert. Keine neue Forschungsfrage und keine Wiederholung abgeschlossener Pakete. Dieser Nachtrag gibt weder R0 noch einen späteren Schritt frei. D-012 bleibt beobachten, analysieren, warnen. Keine Rechte, keine ALLOW/DENY-Produktentscheidung, kein Eingriff.

BELEGT, Readback vor dem Schreiben: 1916 8a6ad14b8d21 SHA256-16 33585534c717b6b3. 1917 1d183de16715 3cd80b9e08ecb998. 1918 e928a5ee1fbe 943a64a25ed1b936. 1919 690cba9f2cd2 4c54626f600381c9. Spitze vorher Ordinal 1919. Zwei Achsen: docs/RESEARCH-METHOD.md Abschnitte 1, 3, 4, 8 und 9, Tree da6dedbd. Methodentext, kein Messergebnis. Dieser Eintrag ist kein Beweis.

1. Negative Ergebnisse A1/A2. Die Sätze in Ordinal 1917 bleiben der Abnahmetext und werden nur eingeordnet. Ersatzmetriken sind unzulässig. Zeitordnung, Dateipräsenz und der belegte Mach-Sender werden nicht zum Schreiber-PID. Endpoint Security und privilegiertes Audit bleiben in derselben Bewegung ausgeschlossen.

Technisch nicht durchführbar: Vor jeder Schreiberbeobachtung fehlt eine erlaubte Voraussetzung. Der Prozess startet nicht, das Ziel lässt sich nicht anlegen, oder die eingefrorene Benutzer-API fehlt auf diesem Host und wird nicht aufgerufen. Achse A FAIL, wenn die Spec die Ausführung verlangt und sie reproduzierbar scheitert. Achse B INCONCLUSIVE. Archivsatz: auf diesem Mac mit den erlaubten Mitteln nicht ausgeführt. H-A1 bleibt dabei unbewertet.

REFUTED: Der Versuch lief. Jede in der Spec genannte nutzbare Benutzer-API wurde aufgerufen und verfehlte den Schreiber. Die Selbstangabe wurde nicht übernommen. Die Zeile bleibt UNBEKANNT. Das widerspricht der positiven Aussage von H-A1 und ist der verwertbare Negativbefund. Achse A kann PASS sein: der Beobachter weist die Selbstangabe zurück, historische Tests bleiben grün. PASS plus REFUTED ist nach Abschnitt 1 zulässig.

INCONCLUSIVE: Abbruch, unvollständige API-Liste oder gestörte Messung. Eine übernommene Selbstangabe ist Achse A FAIL. Abschnitt 8 setzt das Forschungsurteil dann auf INCONCLUSIVE. Der Wortlaut „Selbstangabe übernimmt“ in 1917 bleibt Ablehnungskriterium. Eine geglaubte Selbstangabe ist keine Widerlegung.

SUPPORTED: Die unabhängige Beobachtung nennt PID und Kernelstartzeit des Erzeugers der vorab benannten leeren Datei. Der Geschwisterschreiber ist VERSCHIEDEN. Eine falsche Selbst-PID wird abgelehnt. source_authenticated für Autor, Modell und Gespräch bleibt falsch. Geltung: dieser Mac, dieses eine Ziel, gewöhnlicher Benutzer. Generalisierung LOW, eingefroren in 1917. Kausalität außerhalb des Ziels und Vollständigkeit bleiben UNBEKANNT.

PARTIALLY SUPPORTED: Der direkte Fall hält, mindestens ein eingefrorener Negativfall fehlt. Die Abhängigkeit „A1 SUPPORTED“ ist damit nicht erfüllt. A2 startet nicht. Ein Aufstieg auf SUPPORTED unterbleibt.

Verwertbar ist das Archiv: API-Liste, Aufrufe, Rückgaben, beide Prozessidentitäten, Beobachterzeile, Achse A, Achse B, Geltung. Ein Satz ohne diese Werte ist kein Ergebnis.

A2 behält die Abhängigkeit A1 SUPPORTED. Bei den anderen vier A1-Ausgängen bleibt H-A2 unbewertet und wird nicht selbst REFUTED. Ein weiterer Mach-Empfang ohne neue Dateibindung wiederholt NATIVE-HERKUNFTSMODUL und WB1705 und unterbleibt. Fehlt bei gelaufenem A2 der Kernel-Trailer, gilt der STOP aus 1917. Die Senderzeile bleibt keine Schreiberzeile.

2. Getrennte Bewertung. Achse A: PASS, FAIL oder SPEC CONFLICT. SPEC DEVIATION wird gezeigt und nicht in PASS versteckt. Achse B: SUPPORTED, PARTIALLY SUPPORTED, INCONCLUSIVE oder REFUTED. Dritte Zeile: Geltung. PASS ist Spec-Konformität und kein Sicherheitsbeweis. Ungemessene Herkunft, Kausalität und Vollständigkeit bleiben UNBEKANNT. Vertrauen in Ergebnis und Übertragung werden erst nach dem Lauf genannt und sind vorher UNBEKANNT. Projektinterne Prüfung ist Level 1 nach Abschnitt 4, kein Audit Level 3 oder 4.

R0. A PASS: acht Pins gelesen, Abweichung ausgeschrieben, nichts ersetzt, nichts geschrieben. FAIL: fehlender Pin oder veränderte Datei. SPEC CONFLICT: H-R0 nur durch Änderung eines historischen Dokuments anwendbar, dann STOP. B SUPPORTED nur bei acht passenden Pins. Eine Abweichung bleibt nach 1917 INCONCLUSIVE für diesen Pin und stoppt A1. Geltung: diese acht Objekte zur Lesezeit.

A1. A PASS: neue Tests erfüllen die Spec, Alt-Tests bytegleich, zwei Suiten, Selbstangabe abgelehnt, keine Entscheidungsfolge. FAIL: reproduzierbarer Spec-Verstoß. SPEC CONFLICT: H-A1 nicht deterministisch ausführbar, STOP, Spec bleibt. B nach Abschnitt 1. Geltung: dieser Mac, eine leere reguläre Datei, Benutzerrechte. Andere Hosts, Autor, Modell, Gespräch, FD-Dauer und Vollständigkeit bleiben draußen.

A2. A PASS: ein Handshake, Relay getrennt, Replay UNBEKANNT, lab.origin unverändert. FAIL und SPEC CONFLICT wie A1. B nur nach gelaufenem Versuch, nur für Sender gleich Schreiber. Geltung: ein Handshake auf diesem Mac. Gespräch und Modell bleiben UNBEKANNT.

B1. A PASS: lokale Fälle tragen die vorgesehenen Zeilen, assess bytegleich. FAIL: Zielabwesenheit wird als Wirkungsfreiheit ausgegeben oder ein Archiv umgedeutet. B SUPPORTED nur für ausgeführte Fälle. PARTIALLY SUPPORTED öffnet keine Schreiberabhängigkeit. Allgemeine Vollständigkeit bleibt UNBEKANNT. Geltung: ein Ziel, ein Geschwisterpfad.

B2. A PASS: Nachfenster heißt SPAETER, Fremdzeile vor dem Digest heißt UNBEKANNT, P6-Archive werden nicht neu beforscht. FAIL: Nachfenster heißt NACH oder Fremdzeile wird BELEGT. B entsprechend. Kompromittierter Host bleibt UNBEKANNT. Geltung: eine Fenstergrenze, ein Eingriff vor der Versiegelung.

C1. A PASS: N=8 vor Lauf 1, kein Retry, Intervall aus genau diesen Läufen, fehlender Kontext STOP, abgelaufener Kontext UNBEKANNT, p5/p7 unverändert. FAIL: Retry, neues N, geänderte Altfunktion, Rohprompt im Board. B SUPPORTED nur für die Intervallrechnung aus acht neuen Läufen. Auch 8/8 lässt allgemeine Zuverlässigkeit UNBEKANNT. Ungemessene A1/B1/B2-Zeilen zählen nicht als erfüllt. Alte P8-Läufe, Convergence und Real-Case bleiben eigene Fragen. Geltung: acht neue lokale Codex-Läufe auf diesem Mac.

3. Zeit. BELEGT: Ordinal 1919 addiert R0 4 Stunden, A1 2,5 Tage, A2 1 Tag, B1 1 Tag, B2 1,5 Tage, C1 etwa 2 Tage, rund 8 Arbeitstage. Diese Bauzeitschätzung bleibt stehen und trennt die fünf Blöcke nicht.

Planungshypothese in Stunden, Reihenfolge Spec, Implementierung, Testlaufzeit, Auswertung, Level-1-Prüfung. R0: 0, 3, 0, 1, 2, Summe 6. A1: 4, 12, 2, 2, 4, Summe 24. A2: 2, 4, 2, 2, 3, Summe 13. B1: 2, 4, 2, 2, 3, Summe 13. B2: 3, 6, 3, 2, 3, Summe 17. C1: 4, 4, 3, 4, 4, plus Budget 8 für acht Läufe, Summe 27. Gesamt 100 Stunden, etwa 12,5 Arbeitstage. Suite-Minuten und Modelllaufzeit sind UNBEKANNT und nur Budgets. Ohne A1 SUPPORTED entfallen die 13 Stunden von A2. C1 zählt eine ungemessene Schreiberzeile nicht.

Neubewertungspunkt: der erste Board-Eintrag mit dem R0-Ergebnis, vor jedem A1-Spec-Commit. Geprüft werden die acht Pins, die tatsächlichen R0-Stunden, ein fremder Dateiclaim und die Restschätzung. Danach STOP. A1 braucht einen neuen ausdrücklichen Satz. STOP-Bedingungen und Abhängigkeiten aus 1917 bis 1919 gelten weiter.

Restrisiken: PASS kann als Sicherheitsaussage gelesen werden. Level 1 kann als externes Audit bezeichnet werden. Ein Negativsatz ohne API-Archiv ist nicht verwertbar. C1 kann das Laufzeitbudget überschreiten. Die Board-ID belegt die Speicherung und nicht den OS-Verfasser.

Offen bleiben E1 bis E6 aus Ordinal 1919. Die 12,5-Tage-Rechnung wird erst am Neubewertungspunkt angenommen oder verworfen. STOP.
```

## Ergänzung vom 2026-10-11: gezielte Korrektur F1–F7

Diese Ergänzung setzt ausschließlich den Dokumentationsauftrag nach dem Review
WB1922–1924 um (`b6a0c9abba0d`, `402ae248f103`, `84e97f95570f`). Die 277 Zeilen
der Abschrift am Commit `958b7e2c29848b87e62695b9cc20f8b2dd5bc7c3` bleiben
bytegleich. Forschungsfragen, Hypothesenwortlaut und historische Ergebnisse werden
nicht ersetzt. Dies ist die Klarstellung derselben Planfassung, kein zweiter Plan,
kein Messergebnis und keine Freigabe von R0, A1–C1, Ready oder Merge.

Für künftige Ausführungs- und Bewertungsregeln haben die ausdrücklich benannten
Konfliktauflösungen dieser Ergänzung Vorrang vor widersprüchlichen Anweisungen der
Abschrift. Sie gelten erst innerhalb eines separat freigegebenen Schritts und
müssen vor dessen erstem Ergebnis in seiner Spec stehen. Die Originale bleiben
als Quellen erhalten; eine positive eingefrorene Hypothese wird nicht durch eine
schwächere Ersatzmetrik erfüllt. Nicht auflösbare Voraussetzungen sind unten
OFFEN/UNBEKANNT und sperren den betroffenen Versuch.

### F1 — R0: acht eindeutige Pins und begrenzte Ausgabe

`B` bezeichnet ausschließlich den historischen Commit
`3a9c0067a6e59a55b8e578b6ad870ffe6c74cb47` im Repository
`landjunge/agent-authority-lab`, `T` seinen Tree
`da6dedbd5c48f8f2b021acbb2999a5631e40ba26`. Git-Dateien werden aus `B` gelesen,
nicht aus einer beweglichen Arbeitskopie. Ein Blob-OID bindet die erwarteten
Bytes; der spätere R0-Bericht ergänzt deren SHA-256. Folgende Tabelle definiert
Prüfobjekte und Sollwerte, keine hier ausgeführte R0-Abnahme.

| Pin | Objekt und Bindung | Vorab festgelegtes Wahrheitsprädikat |
| --- | --- | --- |
| R0-01 | Remote `refs/heads/master`, UTC-Zeit der späteren R0-Abfrage | SHA ist exakt `B`; ein inzwischen fortgeschrittener master ist eine Abweichung, kein stiller neuer Basis-Pin. |
| R0-02 | Git-Objekt `B^{tree}` | Tree ist exakt `T`. |
| R0-03 | `B:docs/p8-runs/2026-10-11-stability/P8-COHORT-RESULT.json`, Blob `4259c14861c99d7f1e86feaa83fa4944bef66e3c` | Top-Level `P8_formal_acceptance` ist JSON-Boolean `false`: historischer Messflag, keine Aussage gegen die spätere Abnahme. |
| R0-04 | `B:docs/P8-PRAXISTEST-20261011.md`, Blob `4cdd6d1c76a7e1738cdfddffee6b2a38611f01e4` | Abschnitt „Nachtrag: unabhängige Prüfung, P8-Abnahme und Integration“ nennt die begrenzte Abnahme, WB1628 und Squash `2523568fdca3e629bfba11361c4fefba2cd2d066`; keine allgemeine Zuverlässigkeitsfreigabe. |
| R0-05 | `B:docs/p8-runs/2026-10-11-stability/actual-run-01/lauf/reference.json`, Blob `c21d237b0977abbeb1209166b2821110ae5d3b04` | Enthält die sechs Felder `calls`, `target_present`, `valid`, `order`, `order_applicable`, `order_valid`, keinen Writer-PID-/Schreiberidentitätsbeleg. |
| R0-06 | Thread `833554dffb6e`, WB1602, ID `eccc0ccab937`, UTF-8-`content`-SHA256 `fb121950eeef76eae4ee965a37a84a7d1192263eeda208a85e3492f5434ce508` | Gespeicherter Inhalt dokumentiert begrenzte P6-Abnahme und unbekannten historischen P4-Schreiber; keine automatische P7–P9-Freigabe. Git-Querverweis: `B:docs/P6-HERKUNFTSGRENZEN.md`, Blob `91129d8e5775868f5299423fec930b523babf794`, Abschnitt „Formale P6-Paketabnahme: Nutzerentscheidung WB1602“. |
| R0-07 | Derselbe Thread, WB1628, ID `9bee9bd38144`, UTF-8-`content`-SHA256 `63d8d05680eddb288c31da76c22fd237f48841623154d28d0e35fe2d0d716c15` | Inhalt dokumentiert kontextbezogene begrenzte P8-Abnahme-/PR33-Freigabe, keine Produktions-/P9-Abnahme. Git-Querverweis ist R0-04. |
| R0-08 | `B:docs/NATIVE-HERKUNFTSMODUL-20261011.md`, Blob `b98a6e7dd068a893700b71bd61104d1817b2fce8` | „Schnittstelle und belegte Aussage“ begrenzt den Nachweis auf unmittelbaren Mach-Sender/frische lokale Sitzung; Autor, Modell, Gespräch und erzwungener PID-Reuse bleiben unbelegt. |

Die WB-Objekte liegen unter
`/Users/landjunge/.threaddesk/whiteboard/833554dffb6e/<ID>.json`. Ihr Inhalts-Hash
belegt Bytebindung, nicht den Verfasser oder die unabhängige Rekonstruktion der
damaligen Nutzeräußerung. Die Git-Querverweise sind zusätzliche Provenienz, keine
neunte Prüfeinheit. Fehlendes Objekt, falscher Typ, Hash-/OID-Abweichung und
semantische Abweichung sind jeweils ein fehlgeschlagener Pin.

R0 darf ausschließlich vorhandene Quellen lesen und seinen Ergebnisnachtrag im
bestehenden Board speichern. Keine Registerdatei, kein Leseskript als neue Datei,
kein Fetch/Checkout und kein neuer Agenten-/Forschungsprozess. Die erlaubten
Lesebefehle dürfen laufen. Der Bericht enthält pro Pin Objekt, Soll-/Ist-Bindung,
UTC-Abfragezeit, Werkzeugquelle, SHA-256 bei gelesenen Inhalten und Abweichung.
Die Primärreferenzen müssen eine unabhängige Wiederholung erlauben. Ein externes
versiegeltes Claim-Register wird damit **nicht** hergestellt; diese historische
Lücke bleibt OFFEN und ist kein behauptetes R0-Ergebnis.

Vorrang für die widersprüchlichen A-Regeln in WB1920: Bei mindestens einem
fehlgeschlagenen Pin gilt A **FAIL**, B **INCONCLUSIVE**, betroffene Aussage
UNBEKANNT und STOP vor A1, auch wenn der Fehler korrekt dokumentiert wurde.
A **PASS** / B **SUPPORTED** nur bei acht passenden Pins und eingehaltenem
Leseumfang. Ein widersprüchlicher Prüfvertrag ist **SPEC CONFLICT** / B
INCONCLUSIVE, STOP ohne historische Änderung. Eine unerlaubte Änderung ist
A FAIL, B INCONCLUSIVE und sofortiger STOP. Nichts wird still ersetzt.

### F2 — A1: begrenzter Machbarkeitsvorcheck und ehrliche Negativbefunde

Belegt sind nur Zielpräsenz/Zeitordnung (`scripts/p1_controlled_run.py`),
PID/UID/Startzeit als Momentaufnahme (`scripts/local_process_evidence.py`) und
Mach-Senderidentität (`lab/origin/macos.py`), jeweils an `B`. Keine dieser
vorhandenen Schnittstellen liefert den unabhängigen kausalen Dateischreiber.

| Kandidat für einen späteren A1-Vorcheck | Dokumentierte Grenze aus dem Review |
| --- | --- |
| Apple `FSEventStreamCallback` | Pfad, Flags, Event-ID; keine Writer-PID. |
| `kqueue`, `EVFILT_VNODE` / `EVFILT_PROC` | Dateiänderungs-/Prozessereignisse; keine nachgewiesene kausale Verknüpfung zum Schreiber. |
| `proc_pidinfo`-Startzeit-Snapshot | Prozessinstanz-Momentaufnahme; kein Schreibereignis. |

Diese begrenzte Liste ist ein Untersuchungsrahmen, keine bereits ausgeführte
API-Battery und keine Liste aller denkbaren macOS-Verfahren. Ein zusammengesetzter
Ansatz bleibt UNBEKANNT, solange sein kausales Quellensignal fehlt. Endpoint
Security/Root/privilegiertes Audit bleiben ausgeschlossen. Ebenso ausgeschlossen
sind Selbstreport, Teststeuerungswissen, Instrumentierung des Schreibers oder
bloße Zeitkorrelation als Ersatz für die unabhängige Beobachterquelle.

Vor einer späteren A1-Implementierung muss die separat freigegebene Spec eine
abschließende Kandidatenliste mit konkreter API/Version, Benutzerrechten,
Rückgabefeldern, Uhr/Erfassungsfenster und Herkunft der Writer-Identität fixieren.
Sie trennt Beobachterdaten vom Soll-Identitätsorakel des kontrollierten Versuchs.
PID und Kernelstartzeit müssen derselben lebenden Instanz zugeordnet sein;
fehlende oder rennende Lebenszyklusbindung ergibt UNBEKANNT. Jede Aussage gilt
nur für diesen Mac, das eine Ziel und die ausgeführten Negativfälle.

**OFFEN:** Es ist kein erlaubter, positiv belegter Writer-Mechanismus benannt.
Der Vorcheck gehört zum A1-Spec-Budget, nicht zu garantierter Implementierungszeit.
Ohne ausführbaren unabhängigen Kandidaten STOP vor Implementierung; B
INCONCLUSIVE, keine Widerlegung sämtlicher Benutzer-APIs. Ein später vollständig
ausgeführter Versuch kann bei spec-konformem Beobachter A PASS / B REFUTED
ergeben. Alle Aufrufe, Rückgaben, Identitätsquellen und Negativfälle sind zu
archivieren; fehlende Fälle bleiben PARTIALLY SUPPORTED oder INCONCLUSIVE gemäß
F7. Die positive Hypothese wird nicht zur Testpflicht umgedeutet.

### F3 — A2: tatsächliche API, getrennte Identitätsfelder

Der öffentliche Einstieg ist `lab.origin.OriginReceiver(task_id)` mit
`receiver.receive(*, timeout_ms=5000)`, höchstens 30.000 ms pro Aufruf, nicht
`lab.origin.receive`. Konstruktion/Bereinigung folgen der vorhandenen
Receiver-Schnittstelle; `lab/origin/*` bleibt unverändert.

| Quelle | Vorhandene Identitätsfelder | Nicht daraus ableitbar |
| --- | --- | --- |
| A1-Hypothese | Writer-PID, Kernelstartzeit; Einheit/Präzision müssen vorab feststehen | PID-Version, Autor oder Modell |
| Prozessmomentaufnahme | `pid`, `ppid`, `uid`, `start_seconds`, `start_microseconds` | kausaler Schreiber, PID-Version |
| `receipt.sender` aus Mach-Trailer | `pid`, `pid_version`, `uid`, `os_audit_session` | Startzeit, Dateischreiber, Autor/Modell/Gespräch |

Startzeit und PID-Version sind unterschiedliche Identitätskomponenten und
werden niemals ineinander umgerechnet. Gleichheit nur der PID ist kein
Instanznachweis. Ein späterer A2-Vertrag muss eine unabhängig begründete,
race-sichere Verbindung derselben lebenden Instanz zwischen Writer-Beobachtung
und Trailer benennen. Eine zusätzliche Prozessabfrage ist ohne diese Verbindung
nur ein Snapshot. **OFFEN:** Eine solche Verbindung ist derzeit nicht belegt.
Ohne sie bleibt `effect_sender_same` UNBEKANNT; kein Direktfall-PASS und STOP
vor A2-Ausführung. Der Hypothesentext bleibt erhalten.

`source_authenticated=true` im gültigen Originalreceipt gilt ausschließlich für
`source_scope=immediate_kernel_message_sender_only`. Das Receipt wird nicht
umgeschrieben. `author_identity`, `model_identity`, `conversation_identity`
bleiben UNBEKANNT, `task_author_authenticated` und `rights_inherited` falsch.
Eine neue Vergleichszeile übernimmt daraus keine Autor-/Modellauthentisierung.
Direktfall, Relay und Replay bleiben getrennte Fälle. Ein kopiertes Receipt
ist kein frischer Empfang; Replay bleibt `replayed_local_session`, fehlender
Kernel-Trailer STOP. A2 setzt A1 SUPPORTED und eigene Freigabe voraus.

### F4 — B1: technische Scope-Konformität, keine gemessene Hostvollständigkeit

B1 ist eine **technische Konformitätsprüfung des Coverage-Berichts**. H-B1 bleibt
wörtlich erhalten; ein SUPPORTED für die lokalen Ausgabefälle bedeutet keine
neue empirische Erkennung unbeobachteter Nebenwirkungen.

Getrennt berichtet werden: vorab benannter beobachteter Zielpfad, tatsächliche
Zielbeobachtung (präsent/abwesend im Fenster/UNBEKANNT bei Ausfall), Ausfallgrund,
Scope-Grenze und separat gespeicherte Orakel-Sollwerte. Die Geschwisterwirkung
ist dem Testorakel bekannt und wird nicht an den Beobachter weitergereicht.
Die Vollständigkeitszeile darf in allen Ein-Ziel-Fällen UNVOLLSTAENDIG heißen;
dies ist eine Scope-Aussage, kein Messwert für alle tatsächlichen Wirkungen.

Ein konstanter Scope-Status erfüllt allein nicht die technische Abnahme:
Ziel-only, Geschwister-only, beide und keines müssen ihre tatsächlichen
Zielbeobachtungen korrekt unterscheiden; ein unsichtbares Zielverzeichnis oder
gestörter Zugriff darf nicht als belegte Zielabwesenheit gelten. Keine
Wirkungsfreiheit, keine Schreiberidentität aus Szenarionamen, kein Umbau von
`assess`. Die Scope-Zeile braucht A1 nicht; eine positive Schreiberzeile schon.
Allgemeine Vollständigkeit bleibt UNBEKANNT.

### F5 — B2: zwei begrenzte Phasen; Fremdeingriff bleibt gesperrt

Der spätere Fensterprobe darf nur in der bereits genannten neuen B2-Testdatei
einen eigenen lokalen Diagnosehelfer verwenden. Das ist ein begrenzter
Testbeobachter, keine Änderung/Erweiterung der historischen p1-/p5-/P6-Laufzeit
und kein behauptetes Produktfeature. Jetzt wird kein Helfer und kein Test
geschrieben oder ausgeführt.

Vor einem späteren Versuch sind Zielpfad, monotone Uhr in Nanosekunden,
`t_end`, positive Dauern `w1`/`w2`, Poll-/Ereignisverfahren und dessen Auflösung
zu fixieren. Grenze `c1=t_end+w1`, Ende `c2=c1+w2`: erste Phase bis einschließlich
`c1`, zweite Diagnosephase strikt nach `c1` bis einschließlich `c2`.
Phasengleichheit gehört zur ersten Phase. Ein erfasstes Ereignis heißt nur bei
eindeutiger Bindung an Phase 2 SPAETER; es verändert die historische NACH-Zeile
der ersten Phase nicht. Bei Polling sind letzter negativer und erster positiver
Abfragezeitpunkt zu speichern. Überlappt das Entstehungsintervall `c1`, gilt
UNBEKANNT mit `window_boundary_overlap`, statt Genauigkeit vorzutäuschen.
Ein erstmaliger positiver Befund in Phase 2 belegt Präsenz dort, allein keine
exakte Entstehungszeit. Außerhalb beider Phasen oder bei Beobachtungsausfall
bleibt die Wirkung UNBEKANNT; Zielabwesenheit in Phase 1 ist keine dauerhafte
Abwesenheit. Die kontrollierte Writer-Zeit ist ein separates Soll-Orakel.

Der Fremdeingriffsteil hat folgenden notwendigen Vertrag, aber noch keinen
zulässigen Eintrittspunkt:

| Vertragsfeld | Festlegung/Grenze |
| --- | --- |
| Angreifer | Zweiter gewöhnlicher lokaler Benutzerprozess, kein Collector-/Interpreter-/Kernel-Kompromiss, keine Privilegien. |
| Angegriffenes Objekt | Noch offene **lebende** Ereignisaufnahme vor ihrem Digest; nicht bloß die spätere Archivdatei. |
| Eintrittspunkt | OFFEN: vorhandenes p1 stellt keinen erlaubten Fremd-Append-Eingang für seine Prozessliste bereit. |
| Beobachterbeleg | Muss unabhängig eine fremde/ungebundene Aufnahmezeile unterscheiden; Angreifer-Selbstlabel oder Testorakel genügt nicht. Quelle/Mechanismus derzeit UNBEKANNT. |
| Sollausgabe bei tatsächlich erfasstem Fremdeingriff | Betroffene Zeile UNBEKANNT, Grund `foreign_capture`, nie BELEGT; keine Writer-/Autoridentität behaupten. |
| Nicht gleichwertiger Fall | Fremd-Append zur Ausgabedatei ändert die lebende Liste nicht automatisch. Archiv/Capture-Differenz ist die bereits behandelte P7-Prüfung und kein Ersatzversuch. |

Der Digest bindet Bytes; er authentifiziert keinen vorab eingeschleusten
Verfasser. Ohne realen erlaubten Eintrittspunkt und unabhängiges Quellensignal
ist dieser Versuch **nicht ausführbar**, B INCONCLUSIVE und STOP vor dem
Fremdeingriff. Kein Dummy-Eingang in einem Test darf ihn als erfüllt ausgeben.
Neue Produktadapter oder Änderungen an p1/p5/P6 sind durch diesen Plan nicht
erlaubt. Eine dafür nötige spätere Scope-Erweiterung wäre ein eigener Auftrag;
sie wird hier nicht vorgeschlagen oder ausgeführt. H-B2 insgesamt bleibt ohne
diesen Teil unbewertet bzw. bei ausgeführtem Fensterteil höchstens PARTIALLY
SUPPORTED. Kein Nach-Digest-/Replay-Retest als neue Forschung.

### F6 — C1: deskriptiver Pilot mit festem Nenner

C1 ist eine **deskriptive lokale Pilotstudie**, keine Prüfung einer allgemeinen
Zuverlässigkeitsschwelle. H-C1 und N=8 bleiben erhalten; B SUPPORTED bezieht sich
nur auf das spezifizierte vollständige Berechnungsverfahren, nicht auf einen
empirischen Sicherheits-/Zuverlässigkeitsbeweis.

Vor Position 1 enthält die separate C1-Spec die acht festen Ausführungspositionen
und deren Reihenfolge, künstliches Szenario/Taskverteilung, Quellcommit und
Matrixhash, Host-/OS-/CLI-Version und konfigurierte Modellkennung (keine
Providerbeglaubigung), Timeout/Nachlauf und alle Erfolgskriterien. Erwartungsdatei
und Hash bleiben unverändert. Keine alten P8-Läufe, kein Retry, kein Ersatz,
keine nachträgliche Szenario-, N- oder Matrixänderung; N=20 bleibt Extraauftrag.

Jede Position erhält genau einen Startversuch. Ein Startfehler verbraucht sie
und zählt als Fehlschlag; Timeout, Abbruch und ungültige Aufnahme ebenso.
Getrennt berichten: `N_geplant=8`, `N_Startversuche`, tatsächlich gestartete
CLI-Prozesse `N_gestartet`, `N_vollstaendig`, `N_abgebrochen`, Startfehler und
wegen globalem STOP nicht versuchte Positionen. Erst nach acht abgearbeiteten
Positionen ist `k/8` der deskriptive Anteil vollständig erfüllter **geplanter
Versuche**. Sind weniger als acht tatsächliche lokale Läufe gestartet, darf
dies nicht „acht Agentenläufe“ oder H-C1 SUPPORTED heißen; H-C1 bleibt
INCONCLUSIVE. Bei vorzeitigem globalem STOP keine vollständige Kohorte und
keine Hochrechnung fehlender Positionen.

Die vorregistrierte Gesamtmatrix enthält die 15 P8-Zeilen und die ursprünglichen
A1-/B1-/B2-Anforderungen. Ungemessene, negativ abgeschlossene oder nur teilweise
belegte positive Anforderungen bleiben unerfüllt und werden nicht als N/A aus
dem Erfolgsnenner entfernt. Das kann trotz technisch korrekter UNKNOWN-Ausgaben
zu null vollständig erfüllten Läufen führen. Zusätzlich wird technische
Schutzregel-Konformität separat berichtet: erwarteter Host-SKIP oder korrekte
Herkunft UNKNOWN können dort passen, ohne positive Host-/Writerbelege zu liefern.
Diese Trennung schwächt H-C1 nicht. Die zwei Nicht-Modell-Kontrollen bleiben
außerhalb des Nenners.

Für eine abgeschlossene Kohorte wird das zweiseitige exakte Clopper-Pearson-
95%-Intervall aus `k` und acht Positionen berichtet. Seine populationsbezogene
Binomialinterpretation setzt unabhängige Versuche mit gleicher Erfolgswahrscheinlichkeit
voraus; auf einem Host mit wiederholtem Szenario ist das nicht automatisch
belegt. Ohne diese Annahmen nur Rechen-/Pilotbefund, Generalisierung UNBEKANNT.
Bei 8/8 ist das Intervall `[0.025^(1/8),1]`, ungefähr `[0.6306,1]`, kein hoher
allgemeiner Zuverlässigkeitsnachweis. Ein Startversuchsintervall wird ausdrücklich
so benannt und erfüllt bei weniger als acht tatsächlichen Läufen nicht H-C1.

Die künftige Laufhülle verwendet das von p7 geladene p5 und dessen identisches
p1-Modulobjekt mit lebendem Capture-Callback; kein zweiter p1-Import und kein
Archiv als aktueller Kontext. Frische Laufordner liegen außerhalb des Repos;
`docs/c1-runs/` nimmt erst minimierte Kopien auf. p5/p7 bleiben unverändert.
Linux-CI-PASS wird kein positiver macOS-Nativbeleg. Keine Rohprompts/Providertexte
ins Board und keine Beglaubigung von Autor, Modell oder Gespräch.

### F7 — Vorrangregeln, Abhängigkeiten und STOP

Die folgende prospektive Falltabelle löst insbesondere „Selbstangabe übernimmt“
aus der ursprünglichen A1-Abnahme versus WB1920 auf. Das positive H-A1 bleibt
unverändert. Geglaubte Selbstangabe verletzt den Mess-/Abnahmevertrag und ist
kein unabhängiger wissenschaftlicher Gegenbeleg.

| Fall, in dieser Priorität zu beurteilen | Achse A | Achse B / Folge |
| --- | --- | --- |
| Operative Rechte-/ALLOW/DENY-Folge, verbotene Änderung, privilegierter Ausweg, geglaubter Selbstreport oder anderes reproduziertes Messvertragsversagen | FAIL | INCONCLUSIVE, STOP; gestörter Versuch widerlegt nicht sauber die Hypothese. |
| Vertrag widersprüchlich oder innerhalb des freigegebenen Scopes nicht deterministisch spezifizierbar | SPEC CONFLICT | INCONCLUSIVE, STOP; keine historische Spec nachträglich anpassen. |
| Geforderte Voraussetzung fehlt; vorgeschriebene Ausführung scheitert vor unabhängiger Messung | FAIL, falls Spec sie verlangt | INCONCLUSIVE, nicht ausgeführt; STOP. Reine dokumentierende Machbarkeitsfeststellung ohne verlangte Ausführung ist kein Experiment-PASS. |
| Unvollständige API-Liste, Abbruch, fehlender erforderlicher Negativfall ohne auswertbaren Positivfall | FAIL bei Spec-Verstoß, sonst SPEC DEVIATION separat | INCONCLUSIVE, kein Folge-Gate. |
| Positivfall unabhängig belegt, einzelne erforderliche Negativfälle noch nicht ausgeführt | Spec-Abdeckung unvollständig, kein voller PASS | PARTIALLY SUPPORTED, A2 bleibt gesperrt. |
| Vollständiger, spec-konformer Versuch mit allen erforderlichen Fällen, unabhängige positive Vorhersage scheitert | PASS | REFUTED für den begrenzten Versuch/Kandidatenumfang; Zuordnung UNBEKANNT, kein universeller Unmöglichkeitsbeweis. |
| Vollständiger, spec-konformer Versuch; positive Vorhersage und alle Negativfälle halten | PASS | SUPPORTED nur im eingefrorenen Geltungsbereich; keine neue Generalisierung. |

F1 enthält die spezifischen R0-Pinregeln. B1/C1 haben den oben ausdrücklich
begrenzten Konformitäts-/Analyseumfang; ihr SUPPORTED ist kein zusätzlicher
empirischer Sicherheitsbefund. Für ungestartete A2/B2-Teile lautet der Status
„nicht ausgeführt, Hypothese unbewertet“, nicht REFUTED.

Die ursprüngliche strikte Liste ist eine bevorzugte Bearbeitungsreihenfolge,
keine Pflicht, ein gesperrtes A2 auszuführen. Die tatsächlichen Gates sind:

| Schritt | Voraussetzung und zulässiger Zweig |
| --- | --- |
| R0 | Eigene ausdrückliche Nutzerfreigabe; alleiniger erster Schritt. Nach Ergebnis Neubewertung und STOP. |
| A1 | R0 SUPPORTED und eigene Freigabe; Vorcheck/Spec vor Implementierung, OFFEN aus F2 sperrt den positiven Versuch. |
| A2 | A1 SUPPORTED, nachgewiesene Identitätsverbindung aus F3, eigene Freigabe. Sonst ausgelassen/unbewertet; keine Mach-Wiederholung. |
| B1 | R0 SUPPORTED und eigene Freigabe; Scope-Bericht ohne A1 zulässig, positive Schreiberzeile nur mit A1 SUPPORTED. |
| B2 | R0 SUPPORTED und eigene Freigabe; Fensterteil nach seinem Messvertrag, Fremdteil bis Eintrittspunkt/Quellensignal gesperrt. Kein automatischer Zweigstart nach A2-Auslassung. |
| C1 | R0 SUPPORTED, ausdrückliche dokumentierte Abschlussstände für A1/B1/B2 (einschließlich negativer/offener Teile), feste vollständige Matrix und eigene Lauf-Freigabe. UNKNOWN-Zeilen werden nicht zu Erfolgen. Ein ungelöster Messvertrag sperrt den betreffenden C1-Teil; nur die ausdrücklich festgelegte Pilot-Auswertung ist zulässig. |

A3, PID-Reuse, andere Hosts/Transporte, P4-Writer und historische RC/CB/OOS-Fragen
bleiben gesperrt. STOP bedeutet ausschließlich die eigene Forschungsarbeit
anhalten, keine produktive Agentensteuerung. Fremder Dateiclaim, unerlaubter
Scope, geänderte Pins, fehlender unabhängiger Messbeleg, Änderungen nach dem
ersten Ergebnis und fehlende Freigabe stoppen den betroffenen Schritt.

### Aufwand, Quellen und einmalige Abschlussmatrix

Die ursprünglichen Einzelposten ergeben bei acht Stunden täglich 68 Stunden
(8,5 Tage), der Nachtrag 100 Stunden (12,5 Tage). Das bleibt ein Budget, keine
Terminzusage. A1-Vorcheck, offene A2-/B2-Mechanismen und reale Suite-/Modellzeiten
sind nicht durch diese Dokumentkorrektur belegt. Keine neue Tageszahl, kein
automatisch größeres N. Der Neubewertungspunkt nach R0 bleibt vor jedem
A1-Spec-Commit; auch dann STOP und eigene Entscheidung, kein weiterer Lauf jetzt.

Quellenbasis dieser Ergänzung: Review WB1922–1924; vorhandene Architekturdateien
an `B`, insbesondere `lab/origin/{__init__,receiver,macos}.py`,
`scripts/{local_process_evidence,p1_controlled_run,p5_reliability,p7_integration}.py`
und `tests/test_plan_p7_integration.py` (nur Quelltext), sowie
`docs/RESEARCH-METHOD.md`. Die externen Primärreferenzen aus dem Review sind
[Apple FSEvents](https://developer.apple.com/documentation/coreservices/fseventstreamcallback?language=objc),
[Apple kqueue](https://developer.apple.com/library/archive/documentation/System/Conceptual/ManPages_iPhoneOS/man2/kqueue.2.html),
[Apple Endpoint-Security-Rechte](https://developer.apple.com/documentation/endpointsecurity/es_new_client_result_err_not_privileged?changes=latest_m_7&language=objc),
[Apple Entitlement](https://developer.apple.com/documentation/BundleResources/Entitlements/com.apple.developer.endpoint-security.client?changes=_8)
und [NIST Binomialintervall](https://www.itl.nist.gov/div898/handbook/prc/section2/prc241.htm).
Keine neue API-Messung oder Forschungsinventur. D-012 ist an
`landjunge/KI-Zentralle`, Commit `ee5a1d1683e22294538c0f95268515a2d54357d5`,
`DECISIONS.md`, Abschnitt D-012 gepinnt.

Die Statuswerte bewerten die **Dokumentationskorrektur**, keine technische oder
wissenschaftliche Abnahme. TEILWEISE benennt einen behobenen Planfehler mit
verbleibender technischer Voraussetzung. BEHOBEN bedeutet keine Startfreigabe.

| Befund | Korrektur | Beleg in dieser Ergänzung | Abschlussstatus / Restrisiko |
| --- | --- | --- | --- |
| F1 | Acht eindeutige Pins, Zeitpunkt/Bytebindung, Ausgabegrenze und A-Regelpriorität | F1, Tabelle R0-01–08 und R0-Fallregeln | **BEHOBEN**; externes versiegeltes Register ausdrücklich OFFEN, nicht Teil der erlaubten Ausgabe. |
| F2 | Begrenzter API-Vorcheck, unabhängige Quelle/Orakel getrennt, Negativausgänge | F2 und F7-Falltabelle | **TEILWEISE**; positiver unprivilegierter Writer-Mechanismus UNBEKANNT, Versuch gesperrt. |
| F3 | Tatsächliche Receiver-API, Feld-/Scope-Vertrag, kein PID-/Zeit-/Versionsersatz | F3 und A2-Gate | **TEILWEISE**; race-sichere Identitätsverbindung OFFEN, A2 gesperrt. |
| F4 | Technischer Coverage-Bericht; Scope, Ausfall, Zielmessung und Orakel getrennt | F4 | **BEHOBEN**; gemessene allgemeine Vollständigkeit wird nicht behauptet. |
| F5 | Zweite begrenzte Phase, Grenzüberlappung, Fremdeingriffsobjekt und Stop-Vertrag | F5, Phasenregeln und Vertragsfelder | **TEILWEISE**; realer Fremd-Append-Eingang/Quellensignal OFFEN, kein Ersatz durch Archivmanipulation. |
| F6 | Deskriptiver Pilot, feste Positionen/Nenner, Startfehler/UNKNOWN/SKIP, statistische Grenzen | F6 | **BEHOBEN**; tatsächliche Laufzeiten und Binomialannahmen bleiben UNBEKANNT. |
| F7 | Prospektive Vorrang-Falltabelle, verzweigte Gates, kein erzwungenes A2 | F7 | **BEHOBEN**; jede Stufe benötigt eigene Freigabe, kein Start durch Dokumentversionierung. |

Abschluss dieser Korrekturrunde: nur diese Plandokumentation darf geändert,
regulär auf PR44 committet/gepusht und im bestehenden Board dokumentiert werden.
Das ist die ausdrückliche Ausnahme für diesen Dokumentationsauftrag, kein
Commitrecht aus der ursprünglichen Forschungsplanrunde. Historische Texte,
Produktcode, Tests und Archive bleiben unverändert. PR44 bleibt Draft;
kein Ready/Merge, kein R0/A1–C1, keine neue Gegenprüfung und kein Agentenauftrag.
**STOP nach Versionierungs- und Speichernachweis.**
