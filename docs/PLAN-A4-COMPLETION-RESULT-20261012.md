# A4-Fortsetzung: Verlustkontrollen geprüft, Gateversuch technisch unvollständig

**Endstand: vollständiges Zwei-Agenten-Gate UNBEKANNT,100-Agenten-Test nicht
gestartet.** Die drei ursprünglichen Kontrolllücken wurden technisch
adressiert. Der genau einmal ausgeführte neue Delegationsversuch erfasste
einen16B-Kernelwrite, verlor aber den Abschlussbericht durch einen von Codex
eingeführten BCC-Attributfehler. Das ist ein Collector-/Implementierungsfehler,
kein nachgewiesener Agentenfehler oder prinzipieller Linux-Blocker.

Der Fehler wurde einmal korrigiert und separat ohne weitere Agenten-/Writer-
Versuche geprüft. Die fehlenden Werte des tatsächlichen Delegationsversuchs
bleiben UNBEKANNT. Spätere Diagnosewerte werden nicht rückwirkend übernommen.
Keine abgeschwächten Erfolgskriterien, kein zweiter Writer-Versuch, keine100
Agenten, keine weitere Stufe. Kein vollständiger A4-Erfolg behauptet.

## Basis und erhaltene Quellen

Basis88087a609128149aad752ad9bb52959009843e1f; eigener Branch
codex/a4-loss-controls-20261012. Die553 Basisdateien einschließlich aller
A1/A2/A3/A3.1- und bisherigen A4-Rohdaten/Specs/Resultate bleiben bytegleich:
`docs/a4-completion-runs/2026-10-12/baseline-preservation.json`.
Neue Instrumentierung ausschließlich in `research/a4_completion/`.
Neue Spec/Resultat und Archive zusätzlich, keine rückwirkende Hypothesenänderung.
Die bisherigen24 bestandenen A4-Komponentenprüfungen bleiben historisch erhalten;
sie ersetzen keine Prüfung des neuen Versuchs.

Gelesen/geprüft: tatsächlicher A1-Observer, A2-Lifecycle/Starter/Protokoll,
A4-Guest/Agent/Driver/Verifier/Spec/Resultat, installierte BCC-Pythonimplementation
und BCC0.29.1-/Linux6.8-Quellverträge. Eigene bestehende VZ-Ubuntu-VM,
Kernel6.8.0-142-generic, Root ausschließlich darin. Keine Installation,
Hostprivilegien, Kernel-Konfiguration, produktiven Dateien oder Colima geändert.

## Neue Verlustkontrollen und tatsächlich gemessene Diagnosen

BCCs installiertes attach_kprobe ruft bpf_attach_kprobe mit maxactive0 auf;
der C-Vertrag versucht dann perf-PMU. Die neue Kopie ruft denselben vorhandenen
Low-Level-Anschluss mit Entrytype0/maxactive1 auf: dadurch klassischer tracefs-
Pfad, weiterhin eine **Entry**-Probe. Tatsächlich registrierte p:-Events und
exakte Profilnamen wurden in der VM geprüft. Manuelle Fetcharg-Registrierungen
lieferten zuvor EINVAL; deren Ursache bleibt offen und sie wurden nicht als
verfügbarer Kanal verbucht. Der funktionierende BCC-Weg wird getrennt belegt.

| Kontrolle | Neue Implementierung | Reale separate Diagnose | Grenze |
| --- | --- | --- | --- |
| Write-entry-nmissed | klassischer vfs_write-Entry, exakter kprobe_profile-Name | Idlekanal: Entry-/Returnprofil vorhanden, gemessene Misses0 | kein aktiver Writerjob, keine Delegations-Gatemessung |
| Fork-entry-nmissed | klassischer wake_up_new_task-Entry | ein /bin/true-Kind, Profil1Hit/0Misses, Fork/Exec/Exit passen zur separaten Popen-PID | keine Agentenidentität und kein Lasttest |
| Lifecycle-Mapupdatefehler | tatsächlichen Rückgabewert von states.update zählen | Normaldiagnose0;512 synthetische Mapplätze gefüllt, reales Kind startet/endet, Updatefehler1 und keine Lifecycle-Records | gezielte Instrumentkontrolle; kein tatsächlicher Agentenverlust behauptet |
| BPF-Rekursion | vorhandenes /proc/self/fdinfo.recursion_misses je geladenem Programm | jeweils drei Programme/lesbare Felder0 in gesonderten Diagnosen | keine provozierte Rekursions-Faultinjection, kein globaler Vollständigkeitsbeweis |
| Weitere Fehler | Read-/Invalid-instance-/Seen-update-/Delete-/Perf-/Submit-/Pair-Zähler | zugängliche Diagnosewerte separat archiviert | kein Einsetzen in den fehlenden Versuchsschluss |

Fehlende Profilzeile, fehlendes Feld oder Lesefehler ergibt null/UNBEKANNT.
Alle kritischen Gatewerte müssen gemessene Integer0 sein; bool/string/null
sind keine Nullverluste. Profil, Rekursion, Map-/Readfehler, Perf-/Submit-/
Pairkontrolle **und** unabhängiger Mengen-/Instanzabgleich bleiben erforderlich.
Keine einzelne Nullmessung beweist universelle Erfassung.

Installierte BCC-Methode/Quellhash: `bcc-source-inspection.json`.
Öffentliche Verträge:
[BCC0.29.1 libbpf.c](https://raw.githubusercontent.com/iovisor/bcc/v0.29.1/src/cc/libbpf.c),
[Kprobeprofilspalten](https://docs.kernel.org/trace/kprobetrace.html#event-profiling),
[Linux6.8 trace_call_bpf](https://raw.githubusercontent.com/torvalds/linux/v6.8/kernel/trace/bpf_trace.c),
[Linux6.8 fdinfo](https://raw.githubusercontent.com/torvalds/linux/v6.8/kernel/bpf/syscall.c).
Diese Quellen erklären die Schnittstellen; die neuen Rohdiagnosen belegen die
konkrete Zugänglichkeit. Keine besondere Fehlerrate oder Plattformüberlegenheit.

## Genau ein neuer Zwei-Agenten-Versuch und echter Abschlussfehler

Spec/Instrumentierungscommit `a56553a`, frische öffentliche Registry/CA-/
Quellpins `87e625a`, beides vor Ausführung. Registrierte TestA/TestB mit
getrennten Keys/UIDs,5s-Fenster und erhaltenem A4-Protokoll; Observer bekommt
nur künstliches Objekt, keine Rollen/PIDs/Orakelsollwerte. Die alte24er-
Prüfung wurde durch Profil-/Programmpräsenz und neue Verlustfelder ergänzt,
ohne ihren Inhalt oder das strikte Gate abzuschwächen.

Der Observer erfasste PID1180/Start412972319475ns, dev265289729/inode263042,
write-Entry413144447492ns/Return413144489864ns, count=return16, anschließend
Writerexit. Zwei Records/152 Callbackbytes. Kernel-Aufrufdauer42.372µs;
das ist keine Delegationslatenz. Ein beobachteter VFS-Aufruf beweist keine
Crashpersistenz, Modell- oder externe Agentenidentität.

Beim Abschluss rief der gemeinsame neue Helfer `bpf.functions.items()` auf.
Das installierte BCC hält geladene Funktionen in **bpf.funcs**. Der Fehler
trat im Lifecycle-Abschluss und im Observer-Abschluss auf. Beide Collector-
Prozesse endeten mit1. Guest erreichte laut gepinntem Kontrollfluss den
Abschluss nach den beiden Worker-Waits; deren Einzelresultate, signierte
Delegation/Annahme, Rootreceipt und separates Orakel wurden aber nicht
exportiert. Diese Felder sind unabhängig **UNBEKANNT**, nicht nachträglich
rekonstruiert oder als24 bestandene Prüfungen ausgegeben.

`phase1/trial.stdout.json` ist tatsächlich leer; capture.jsonl enthält die
beiden Kernelrecords, keinen summary. stderr-Logs, Status, Failureobjekt,
Attemptanzahl1, ursprüngliche Quellpins und Registry bleiben unverändert.
Der neue Write ist als beobachtete Prozess-/Dateihandlung **BELEGT**;
Testidentitäts-/Delegationskette insgesamt **TEILWEISE BELEGT**, formales
vollständiges Gate **UNBEKANNT**. Authentisierte konkrete Actorzuordnung,
falsche Positive, tatsächliche volle Kettenzahl und alle fehlenden Verlust-
Schlusswerte UNBEKANNT. Unabhängig vollständig geprüfte neue Ketten:0.
Keine Aussage, dass tatsächlich0 Ketten existiert hätten.

## Eine begrenzte Korrektur, keine Wiederholung des Gatejobs

`9b588fd` erhält den realen Fehler und korrigiert funcs; fehlende Registry/
fdinfo wird nun als unbekanntes Feld zurückgegeben statt Abschlussabbruch.
Neue Kontrolle `controls_probe.py`: keine Testkeys/Identitäten, Delegationen
oder Zielwritejobs. `b96c9d8` pinnt korrigierte Quellen vor Diagnosen in
eigenem Gastpfad. Drei instrumentbezogene Kontrollen: gesunder Fork/Exec/Exit,
absichtliche Mapfüllung und leerer2s-Dateikanal. Keine erneute A/B-Delegation.
`a46b107` archiviert deren Messungen und14 Regressionen.

Die Kontrollen zeigen eine tatsächlich verfügbare Messgrundlage. Sie liefern
keine fehlenden historischen Schlusswerte des bereits beendeten Versuchs.
Zähler/Orakel/Signaturpaket dieses einen Versuchs sind nicht aus seinem Ende
wiederherstellbar. Ein neuer erfolgreicher Gatejob ist nicht als stiller Retry
ausgeführt worden. Der aktuelle Auftrag endet mit diesem konkreten Blocker;
kein grundsätzliches Scheitern der Linux-Methode behauptet.

Phase2 vollständig nicht ausgeführt:0 gestartete Skalierungsagenten;
100er-Multistufen-/Parallel-/Replay-/Fremdclaim-/Refusal-/Interruption- und
PID-Reuse-Befunde, Durchsatz, Latenzen, CPU/RAM UNBEKANNT. Keine Simulation
oder Offlinefixture wird als erfolgreiches100-Agenten-Experiment ausgegeben.
Provider-/Modell-/Codex-/Grok-Sitzungsidentität bleibt UNBEKANNT.

## Ressourcen, Tests, Git und Sicherheit

Versuchs-CPU/RAM und Delegationslatenz fehlen wegen des Abschlussfehlers:
UNBEKANNT. Nur Kontroll-Observerkosten sind verfügbar: genaue User/System-
CPU und PeakRSS in `result.json`/`controls/write-channel-idle.jsonl`, inklusive
BCCcompile. Keine Agenten-/Kernel-/GesamtVM-Kosten daraus ableiten.
Gesunder Lifecycle132 Callbackbytes, Mapfüllkontrolle0, Idleobserver0;
fehlende Exportbytes sind kein positiver Nachweis fehlender Ereignisse.
Gespeicherte Bytes/Hashes getrennt im Artifactindex.

14 neue Regressionen prüfen tatsächliche BCC-funcs-Schnittstelle, unbekannte/
fehlerhafte fdinfo, exakte Profilnamen/erhaltene Nichtnullwerte, reale
Normal-/Mapfüll-/Idle-Diagnosen und dass der fehlerhafte Versuch keine späteren
Kontrollwerte erbt. Keine neuen Writer- oder Testagentenläufe dabei.
Gesamtsuiten **zweimal683 Tests bestanden** auf festem Code-/Daten-HEAD `a46b107`; JUnit/Commands im
neuen Archiv. Neue Ruffchecks/Format und Gesamtformat bestanden, Kern-Mypy
(32 Dateien) und Kern-Bandit bestanden. Gesamt-Ruff unverändert16 historische
Befunde, keine neuen; kein grüner Gesamt-Ruff behauptet.

`cleanup.json`: private Gastvault/Host-CA gelöscht, keine eigenen verbleibenden
Versuchsprozesse und keine übrig gebliebenen dynamischen Kprobe-Events.
`end-state-ci.json`: Forschungs-VMStopped, Colima weiterhinRunning, keine
Branch-CI-Läufe. Keine Hostfreigaben umgangen, keine Secrets/Privatekeys oder
Modellinhalte archiviert. D-012 unverändert: Versuchsteuerung keine Produkt-
Rechtevergabe. Nur eigener Fortsetzungsbranch regulär gepusht, kein Merge/Ready.
Abschluss-SHA/Remotegleichheit separat nach finalem Push verifizieren.
