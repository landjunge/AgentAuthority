# A4: frisches Gate und tatsächlich ausgeführter100-Agenten-Versuch bestanden

**BELEGT im abgegrenzten Linux-Testaufbau:** Das frische Zwei-Agenten-Gate
besteht unverändert. Danach liefen tatsächlich100 getrennte kontrollierte
simulierte Agenten.99 signierte Delegationen wurden über sechs Stufen mit
99 unabhängig beobachteten16B-Kernelwrites verbunden. Keine falsche Zuordnung,
keine fehlenden Referenzwrites oder duplizierten Kernelwrites, alle erfassten
kritischen Verlustwerte gemessen0. Vier echte Negativnachrichten/-abläufe
wurden separat geprüft. Keine weitere Kohorte oder Skalierungsstufe.

Externe Codex-/Grok-/Provider-/Modellsitzungsidentität bleibt **UNBEKANNT**.
TestCA/Key, Prozessinstanz und Kernelhandlung werden getrennt geprüft; eine
PID oder Claim allein wird nicht als Agentenauthentisierung gewertet.

## Ausführung, Gitbasis und unveränderte Geschichte

Ausgangsbasis e5f4a0bfde026b9d567bc05ae06fec32be7eb660, eigener Branch
codex/a4-final-run-20261012. Alle598 Basisdateien bytegleich erhalten,
einschließlich der alten positiven/negativen A1/A2/A3/A3.1/A4-Befunde und des
Collectorfehlers. Kein altes Gate/Resultat oder Produktcode verändert.
`docs/a4-final-runs/2026-10-12/baseline-preservation.json` belegt den Vergleich.

Aktueller Nutzerauftrag autorisierte ausdrücklich den neuen Gateversuch und
gezielte Fehlerkorrekturen. Tatsächlich ein frischer Gateversuch und ein
100er-Versuch, keine Laufwiederholung. Das ist Fortsetzung der bestehenden
A4-Phasen und Kriterien, keine neue Forschungsplanung.

`7d65836`: frische Gate-Registry/CA-/Quellpins vor Lauf; `e1dbbd8`: vollständiger
Gatebefund; `ae22c97`:100er-Hülle mit vorhandener Instrumentierung und
festem Binärbaum; `51e31c9`:100er-Registry/Sourcepins vor Lauf; `cd6d4f2`:
Rohdaten/ unabhängiger OpenSSL-Join; `28cc05b`:25 Offline-Regressionspositionen
und konservative Fehlerzählung des Verifiers. Vollständige Referenzen in
`attempt.json`, `pins.json`, `execution-commands.json` und Gitlog.

Eigene bestehende Ubuntu24.04.5-VZ-VM, x86_64, Kernel6.8.0-142-generic,
2CPU/2GiB, keine Hostmounts/SSH-Agentweitergabe. Nur diese zuvor gestoppte VM
gestartet und danach gestoppt. Keine Installation, Hostprivilegienerhöhung,
Kernelkonfiguration, produktive Dateien oder anderen Umgebungen verändert.
Colima blieb Running. Sämtliche künstlichen Objekte in neuem eigenen Scope.

## Frisches Zwei-Agenten-Gate

Unveränderte korrigierte A4-completion-Quellen eingesetzt: TestA/TestB,
getrennte Keys/UIDs, frische5s-Aufträge, signierte tatsächliche Übergabe und
Annahme, SCM_CREDENTIALS, pidfd, Kernelstart/exec/file/time und separates
Controller-Orakel. Der Observer erhält nur das künstliche Dateiobjekt.

Alle26 Prüfungen bestehen: ursprüngliche24 Komponenten plus Profil- und
Programmpräsenz. Alle23 kritischen Verlustwerte vorhanden und0, einschließlich
Write-/Fork-entry-nmissed, Lifecycle-Mapupdates, Rekursion, Perf/Submit/Pair/
Readfehler. Ein Zielwrite, zwei vollständige Fork/Exec/Exit-Referenzinstanzen.
OpenSSL prüft die Signaturen unabhängig von Guest-Cryptography.
`phase1/evaluation.json`, `capture.jsonl` und `trial.stdout.json` enthalten
die tatsächlichen vollständigen Belege. Das alte fehlgeschlagene Messpaket
wurde weder ersetzt noch nachträglich mit diesen Werten aufgefüllt.

Vor100er-Prepare und -Run wird dieses tatsächliche Gate erneut offline
verifiziert. Seine abgelaufenen Jobs/Bindings werden nicht für100 wiederverwendet:
neue CA/Registry, neue100 Agentenkeys, neue Instanzen und neue Jobnonces.

## Tatsächliche100-Agenten-Kohorte und unabhängiger Join

Agent000..Agent099:100 Ed25519-Keys,100 verschiedene UIDs62000..62099 und
100 verschiedene Kernel-Prozessinstanzen. Jeder Prozess besitzt nur seinen
eigenen versiegelten Key-memfd; nondumpable/no_new_privs. Registrierung:
frische signierte Besitzprobe, Kernel-SCM-Sender, Root-Popen-/proc-/pidfd-
Referenz und Fork/Exec-Metadaten. Keine bloße Prozessnamen-/PID-Verwandtschaft.

Binärbaum Parent(i)=floor((i-1)/2),99 Kanten. Agent000 ist Auftraggeber ohne
eigenen Zielwrite; jeder andere Agent empfängt einen positiven Job und schreibt
einmal16B. Ein weiterdelegierender Agent bindet den exakten Digest seiner
vorherigen Delegation/Annahme; dessen unabhängig beobachtete Handlung und
Completion liegen vor Ausgabe des Folgejobs. Sechs Frontiers2/4/8/16/32/37;
nach allen signierten Annahmen einer Frontier batched Freigabe ihrer Writes.
Tatsächlich37 überlappende Auftragsintervalle und zwei überlappende VFS-writes.

Alle100 Prozesse gleichzeitig registriert und verfügbar. Im Observer100
zufällig benannte, gehaltene reguläre Dateien und erlaubte dev/inode-Map;
keine Rollen, Agentenkeys, Spawn-PIDs oder Orakelsollwerte. Die korrigierten
Entry-/Return-/Exit-Zähler und Erfassungslogik bleiben erhalten; die zusätzliche
Map erweitert ausschließlich den festen Objekt-Scope. Lifecycle512 Plätze,
Targetmap128, Pending-/Seenmaps256; keine Kernelkonfiguration verändert.

`research/a4_scale/join.py` prüft mit vorher gepinnter CA:
100 Key-/SCM-/Instanz-/exec-/Orakelbindings, jede Sender-/Annahme-/Rootsignatur,
Scope/Digest/Nonce/5s-Fenster, tatsächliche Übergabereihenfolge, genau eine
passende Kernelhandlung je Job, Parentkette und Mengen-/Exitreferenz.
99 positive Ketten vollständig BELEGT, alle19 übergeordneten Scalechecks wahr,
alle24 Scale-Verlustfelder gemessen0 (zusätzlicher reservierter Stats-Slot).
300 Lifecycle-Records;99 Write- und99 Writerexit-Records.

Root/Host/CA und Linuxkernel bleiben Trustanker. Der unabhängige Kernelkanal
beobachtet gegenüber Agentenclaims; OpenSSL ist ein eigener Verifier gegenüber
der Gastprüfung. Das ist keine vollständige Unabhängigkeit von kompromittiertem
Root/CA/Kernel. Keysweitergabe, mehrere externe Modellsitzungen pro Prozess,
Produktangriffe oder Providerattestierung sind nicht bewiesen.

## Vier tatsächlich ausgeführte Negativfälle

| Fall | Tatsächliche Nachricht/Handlung | Unabhängig geprüfter Befund |
| --- | --- | --- |
| Replay | letzter realer signierter Auftrag vom tatsächlichen Sender erneut gesendet, innerhalb seiner5s-Frist | Originalsignature/SCM passen, Nonce bereits im Laufledger, keine neue Weitergabe/Wirkungskette |
| Fremdclaim | Agent099 signiert tatsächlich einen Senderclaim Agent001 | eigene099-Signatur gültig,001-Signaturprüfung falsch; SCM-Sender099, keine001-Übernahme |
| Verweigerung | zusätzlicher echter Auftrag048→098, signierte Refusal098 | Jobdigest/Instanz/Signaturen passen; keine Freigabe/kein neuer Write, erwartete unvollständige Kette |
| Unterbrechung | zusätzlicher echter Auftrag049→099 angenommen, vor Freigabe kontrolliert SIGTERM | Annahme/Instanz passen, Exit-15/Kernel-Lifecycle bestätigt; kein neuer Write, erwartete unvollständige Kette |

99 vollständige positive Ketten; zwei absichtlich unvollständige weitere
Delegationen, zwei zurückgewiesene Nachrichtenfälle. Diese Positionen sind
keine weiteren Erfolgsketten. Replay ist absichtliche Nachrichtenduplizierung,
keine duplizierte Kernelbeobachtung. Kein Ereignisloch als Wirkungsfreiheit
gewertet: sämtliche positiven Referenzwrites und alle100 Lifecycle-Instanzen
stimmen bei vorhandenen Nullverlustkontrollen überein.

Negative Routing-/Freigabebelege sind im kontrollierten Research-Registrar
bezeugt, keine ausgeführte Produktpolicy. Der unabhängige Join erkennt verbrauchte
Nonce/fremde Signatur/fehlende Handlung. Keine dauerhafte oder über mehrere
Verifier/Restarts geteilte Anti-Replay-Abwehr behauptet. Tatsächliches PID-Reuse
in diesem Versuch UNBEKANNT;100 unterschiedliche PIDs gemessen, kein erzwungenes
Reuse-Experiment begonnen. Kein Schlüsselentwendungs-/Rootkompromissnachweis.

## Messwerte und Kosten mit ihren Nennern

| Messung | Reales Ergebnis | Messgrenze |
| --- | --- | --- |
| Positive Jobpipeline |99 Jobs in3.542819838s,27.943843 Jobs/s | Ausgabe bis letzter Completion nach Enrolment; kein Modell-/Startdurchsatz |
| Ausgabe→Annahme | Median514.597ms, p95 nearest-rank807.343ms, max849.073ms |99 positive Jobs, Registrar-Empfang der Annahme |
| Ausgabe→Kernelwrite | Median737.763ms, p95 858.337ms, max862.604ms |99 positive Jobs, Guestmonotonic; keine Hostuhrvergleichung |
| Parallelität |37 inflight-Delegationen,2 überlappende Kernelwrites | gemessene Intervalle, VM2CPU; keine100 parallelen CPU-Kerne |
| Observer-CPU/RSS | user2.120654s +system0.217631s; Peak178479104B | eigener Prozess samt eigener Compile-/Erfassungsarbeit |
| Registrar-CPU/RSS | user1.234585s +system0.494667s; Peak165412864B | eigener Prozess/Koordination |
|100 Worker-CPU | user12.557760s +system4.377090s | RUSAGE_CHILDREN-Differenz nach BCCcompile/vor Spawn bis Wait aller100; inklusive Bootstrap/Negativfälle |
| Agenten-RSS-Snapshot | Maximum der sieben Summensnapshots2628763648B | RSS zählt gemeinsame Seiten mehrfach; kein physischer VM-RAMpeak |
| VM-MemAvailable | kleinster gemessener Snapshot361152512B | Momentaufnahmen, keine lückenlose Peakmessung |
| Callbackbytes | Observer15048B, Lifecycle13200B |198 bzw.300 tatsächliche strukturierte Records; JSON-Speicherbytes separat |
| Fehlende Ressourcen | Gesamt-VM-/Kerneloverhead, vollständiger physischer RAMpeak UNBEKANNT | nicht als0 ausgewiesen |

Die globale tracefs-Hitzahl von Entry/Return ist nicht atomar gleich
(762/758); sie enthält auch ungescopte laufende VFS-Aufrufe. Das ist kein
Ziel-Mengenvergleich. Für die gehaltenen Zielobjekte sind Entry=Return=
Delivered=Orakel99, Pending0, Returnmisses0 und alle übrigen kritischen
Zähler0. Keine allgemeine Aussage, dass beliebige globale VFS-Aktionen
lückenlos erfasst oder dauerhaft auf Platte persistiert wären.

## Rohdaten, Fehlerhistorie, Qualität und Abschluss

Archiv: `docs/a4-final-runs/2026-10-12/` mit getrennten phase1/phase2-Pins,
Registry, Attempts, Original-JSONL, stderr/Exitstatus, abgeleitetem Trialresult,
vollständigem unabhängigen Join, CPU/RSS-Samples und Qualitäts-JUnit.
`runtime-provenance-checks.json`: Observerhashes/Workerhash entsprechen Pins,
abgeleitetes Trialresult entspricht exakt dem finalen rohen JSONL-Objekt.
`source-epoch-checks.json`: vorab committed Quellhashes stimmen.
`execution-commands.json`: tatsächliche Kommandos/Quellstände/Versuchszahl.
`artifact-index.json`: Datei-/Bytezahlen und SHA256, keine Privatekeys/JWTs.

Keine neuen Lauf-/Collectorfehler in den beiden frischen Versuchen. Der alte
BPF.functions-Fehler bleibt im Basisarchiv. Eine kleine nachträgliche reine
Verifierhärtung verhindert volle Kettenzahlen bei falschem Trustpin/global
fehlgeschlagener Prüfung; sie verändert weder Messquellen noch gültiges
Messergebnis. Regression prüft Gleichheit zum archivierten realen Join.

25 neue **Offline**-Regressionspositionen auf Kopien realer Daten: manipulierte
CA/Startzeit/UID/Parent/Witness/Ablauf, fehlender/duplizierter write/Exit,
verlorene/unbekannte Zähler und mutierte Negativfälle müssen scheitern.
Sie sind keine weiteren Agenten-/Kernelversuche. Signaturcache in Tests hält
nur exakte öffentliche Key/Envelope-Paare; neue signierte Inhalte werden
erneut mit echtem OpenSSL geprüft, keine positiven Signaturestubs.

Gesamtsuite **zweimal708 Tests bestanden** auf festem HEAD28cc05b, keine
Commits während beider Läufe. Neue Ruff-/Formatchecks, Gesamtformat260 Dateien,
Kern-Mypy32 Dateien und Kern-Bandit bestanden. Gesamt-Ruff unverändert16
historische Befunde,0 neue; kein grüner Gesamt-Ruff behauptet. Diese Tests
ersetzen den oben tatsächlich ausgeführten Kernel-/Agentenversuch nicht.

Private CA-/Gastvaults gelöscht, sämtliche eigenen Versuchsprozesse beendet,
keine zurückgelassenen Kprobe-Events; tatsächlich geprüft in
`cleanup-environment.json`. VMStopped, ColimaRunning, Branch-CI keine Läufe:
`end-state-ci.json`. D-012 und Produktcode unverändert, keine Modelltexte,
Bearer-Token, privaten Schlüssel oder produktiven Inhalte archiviert.
Regulärer Push nur eigener Branch, kein Merge/Ready. Finalen SHA und dessen
Remote-Gleichheit nach Abschluss gesondert verifizieren. A4 endet nach diesem
100-Agenten-Versuch; weitere Arbeiten wurden nicht begonnen.
