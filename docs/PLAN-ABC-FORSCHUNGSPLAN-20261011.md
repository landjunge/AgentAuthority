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
