# A1 Linux praktisch: Schreiberbindung im begrenzten VM-Versuch BELEGT

**Ja: Unter den hier geprüften Bedingungen wurden konkrete synchrone write-
Operationen unabhängig ihrer tatsächlich schreibenden Prozessinstanz zugeordnet.**
Neue isolierte Ubuntu24.04.5-VM, Linux6.8.0-142-generic/x86_64, Rootrechte für
den eBPF-Observer ausschließlich im Gast, gewöhnliche Writer UID501. Fünf
positive Zielaktionen in sechs vorregistrierten Fällen korrekt,0 falsch,0 unklar.
Keine allgemeine Zuverlässigkeitsquote oder logische Agentenauthentisierung.

Basis `ad72abf97880083d0aa1cc22545a13002b10a942` auf eigenem Branch
`codex/a1-linux-experiment-20261012`. Auftrags-/VM-Commit `3eada91`, konkrete
Spec/Quellpins `65e8af8`, tatsächlich durchgehend unveränderter Laufquellcommit
`7ca496e3ba5b5078bde701f2a16b37b9eb12f8e9`. Historischer Mac-A1 bleibt
INCONCLUSIVE, alter Linux-Preflight bleibt seine unprivilegierte Momentaufnahme.
Keine Änderungen an R0/A2/B1/B2/C1/P7/P8, PR44/45 oder bisherigen Rohdaten.

## Wirklich neue VM und Rechte

Lima2.1.1/VZ, eigenes `LIMA_HOME=/Users/landjunge/.local/share/agent-authority-a1-linux-vm`,
Instanz `a1-research`,2CPU/2GiB/12GiB, plain/mount-none/containerd-none.
Keine Hostmounts, kein SSH-Agent-Forwarding oder bestehender Dot-SSH-Keyimport.
Bestehende Colima-VM und ihre drei gestoppten Container unverändert. VM wurde
nach Export und Entladen aller Forschungsprobes sauber gestoppt; Disk bleibt
für Nachprüfung erhalten. Kein Host-sudo, Helper, Entitlement, FDA/TCC/SIP-
Eingriff nötig. Zusätzliche Hostfreigaben waren nicht erforderlich; die normale
VM-Erstellung war ausdrücklich beauftragt. Root im Gast ausdrücklich autorisiert.

Das alte Template-Image redirectete auf ein unerreichbares Archiv. Nur eigener
Erstellungsprozess49533 abgebrochen, kein fremder Prozess beendet. Neuer HTTPS-
Download des offiziellen Ubuntu-Cloudimages,625612288B, SHA256
`6a81c37564db9b1ee84e141922625e1d7c5b389b99bb3c572e0243607d5bb4d2`,
gegen veröffentlichte SHA256SUMS und zusätzlich lokal berechneten Hash geprüft.
Paketinstallation nur im Gast: BCC0.29.1+ds-1ubuntu7, Audit3.1.2-2.1ubuntu0.1,
GCC und passende Kernelheader6.8.0-142.142. Root CapEff000001ffffffffff,
Seccomp0; BPF-Sysctl2/perf_paranoid4 blieben unverändert, Rootzugang funktionierte.

## Quellen tatsächlich geprüft

| Quelle | Wirklich gemessen | Verwendeter Belegumfang |
| --- | --- | --- |
| eBPF/BCC | Compile, Verifier, Laden und Attach erfolgreich; danach echte Kernelrecords | Primärquelle: vfs_write Entry/Return + sched_process_exit |
| Linux Audit | auditctl-s Exit0, enabled1, lost0 vor/nach Versuch | Status/Verfügbarkeit BELEGT; keine Audit-Writerzuordnung oder Regeln als Ersatzbeweis |
| fanotify | NOTIFY/CLOEXEC/NONBLOCK/REPORT_PIDFD-init erfolgreich, FD geschlossen | Initialisierung BELEGT; keine Marks/Records/Schreiberkausalität behauptet |
| Tracing | write-Entry/Exit- und Prozess-Exit-Formate tatsächlich gelesen; eigener Returnprobe-Profilzähler | Tracepointzugang und kretprobe-nmissed0 BELEGT; numerischer FD allein bleibt unzureichend |

Auditstatusfeld failure1 ist eine konfigurierte Fehlerreaktion, kein gemessener
Versuchsfehler. Sourceverträge und tatsächlich gemessene API-/Kernelwerte werden
getrennt archiviert. Upstream6.8/BCC-Quelltexte erklären den Vertrag; sie werden
nicht als exakte Ubuntu-Downstream-Kernelquelle ausgegeben.

## Unabhängigkeit und kausale Kette

Observer erhielt ausschließlich das gehaltene künstliche Zielobjekt und6s-Dauer,
keine Writer-PIDs, Rollen, Fallpläne oder gefälschten Claims. Rollenunabhängige
zufällige Pfadnamen. Kernel-VFS-Entry lieferte aktuelles TGID/TID, Kernel-
Leaderstart_boottime_ns, tatsächliches Parent-TGID, dev/inode des struct-file-
Objekts und angeforderte Bytes. Kretprobe korrelierte denselben laufenden Task,
tatsächliches write-Return16 und monotone Entry/Return-Zeit. Prozess-Exit
lieferte getrennte Lifecycle-Records. Boot/PID-Namespace und Starttick-Einheit
sind gebunden; PID allein wurde nie als Instanzschlüssel verwendet.

Separater Testcontroller kannte die reale fork-return-PID, hielt vor der Aktion
pidfd, prüfte /proc-Start/PPID vor/nach Aktion sowie Wait/PIDFD-Exit. Das ist
kontrollierte Ground Truth, nicht Collectorquelle. Getrennte SSH-Kanäle; Orakel
nur am Host gespeichert, der Gast hat keinen Hostmount. Capture abgeschlossen
und getrennt gehasht vor Offlinevergleich. Die kontrollierte Writer-Rückgabe
ist Orakel, der unabhängige kernel-origin Return ist Beobachterbeleg.
Das ist projektinterne Quellen-/Rollentrennung, kein externer Drittparteiaudit.

Kernelzeit fällt in das separat protokollierte write-Intervall; Return/count16,
Filedev/inode und Prozessinstanz passen. Gehaltener Objekt-FD verhindert
Inode-Recycling während der Aufnahme. Objektidentität ist nicht ewige Pfad-
oder Generationidentität; Umbenennung/Ersetzung/Mountwechsel nicht getestet.

## Sechs originale Fälle, einmalig und ohne Retry

| Position | Tatsächlicher Befund | Bewertung |
| --- | --- | --- |
| L1 A schreibt Ziel | Kernelwriter2334, Start718891288741ns, inode262237, Return16 | BELEGT für Aktion/Instanz/Objekt |
| L2 B untätig |0 Zielrecords, keine positive B-Zuordnung | BELEGT nur für diese Negativkontrolle, keine allgemeine Wirkungsfreiheit |
| L3 C andere Datei |0 Zielrecords, keine falsche Zielzuordnung | BELEGT für Scope-Negativkontrolle; C-Schreiben nur Orakel, nicht unabhängige Geschwisterbeobachtung |
| L4 Kind schreibt | tatsächliches Enkel-TGID2389, Parent2388, Start747291588097ns, inode262243 | BELEGT für Kindaktion, kein Parent-als-Writer |
| L5 gefälschte PID | echter Writer2404/Start756605823990ns, falscher Claim nicht übernommen | BELEGT, Claim keine Quelle |
| L6 A dann C |2419/Start765561761369ns und2420/Start765864579039ns, dasselbe inode262247 | beide Aktionen und Reihenfolge BELEGT |

Fünf Zielaktionen und fünf zugehörige Writer-Exits,0 falsche/unklare Bindungen,
zwei reine Scope-Negativpositionen getrennt vom positiven Aktionsnenner. Keine
Wiederholung oder Ersetzung, Source-Commit durchgehend identisch. Positive
H-LINUX-A1 für diesen vollständigen kleinen Versuch SUPPORTED, AchseA PASS für
den eingefrorenen Umfang. BELEGT ist keine globale Sicherheitsabnahme.

## Tatsächlich erzwungene PID-Wiederverwendung, separate Kontrolle

Nach sechs Positionen genau eine zusätzliche Root-Writerkontrolle im isolierten
Gast. Erste Instanz beendet und über Wait/PIDFD bestätigt; VM-ns_last_pid gesetzt,
zweite Instanz gestartet. **PID2435 wurde tatsächlich zweimal vergeben.**
Unabhängige Kernelstarts `774702253420ns` und `775055346330ns`; Orakelstartticks
77470 bzw77505 bei100Hz. Beide write-Aktionen zum gleichen gehaltenen Objekt
korrekt als **verschiedene Instanzen** zugeordnet; je eigener Exitrecord.
2/2 BELEGT, keine Wiederholung. Rootkontrolle außerhalb des UID501-Sechs-
Fälle-/Fünf-Aktionsnenners. Keine Behauptung zu sämtlichen Reuse-/Exec-/Threadfällen.

## Verlust- und Ressourcenmessung

Alle Target-Entries haben Return und erfolgreichen Perf-Submit;0 pending,
0 Map-/Overwrite-/Submit-/Lifecycle-Submitfehler,0 gemeldete Perfverluste,
eigener klassischer kretprobe nmissed0 in allen sieben Aufnahmen. Zehn Records
für sechs Fälle, gemessene Callback-Rohbytes760B; Zusatzkontrolle vier Records,
304B. Das sind Callback-Rohdaten, nicht sämtliche Perf-/IPC-/Kernelverkehrbytes.

**UNBEKANNT bleibt nmissed des direkt über Perf angehängten Entry-Probes.**
Die BCC/Kernel-Schnittstelle stellt ihn hier nicht über das verwendete Profil
bereit. Weder fehlender Zähler noch0 beobachtete Drops beweisen allgemeine
Vollständigkeit/Lastfestigkeit. Das Orakel bestätigt die Anzahl der kleinen
kontrollierten Aktionen; ein allgemeiner Beobachter dürfte aus fehlendem Record
weiterhin keine Wirkungsfreiheit ableiten. Kein Last-/Overflowexperiment begonnen.

Sechs Observerprozesse insgesamt CPUuser11.747236s/system1.111579s, jeweils
einschließlich BCC-Kompilierung; größtes PeakRSS177643520B. Damit kein reiner
Streaming- oder Kerneloverhead gemessen. Kernel-CPU/GesamtVM-RAM/Eventverluste
außerhalb der vorhandenen Indikatoren UNBEKANNT. Speicherbytes/Artefakthashes
separat in artifact-index.json, Rohzählungen in metrics.json.

## Qualität, Grenzen und Nachprüfung

17 neue Offline-Tests: Reuse-/Start-, Datei-, Actor-/Return-/Zeit-, Boot-,
Verlust-, fehlende und fehlerhafte Daten bleiben konservativ. Keine Fixture als
Kernelbeleg. Ganze bestehende Mac-Suite zweimal605PASS,0 failures/errors/skips,
je5 unveränderte historische Abwahlen. Ruff Check/Format PASS; striktes Mypy
32 bestehende Coredateien/Bandit bestehenden Core PASS (keine Behauptung über
deren Analyse des eingebetteten BPF-C). Gast-BPF-Compile/Verifier/Attach und
reale Ausführung separat nachgewiesen. Kein neuer Remote-CI-Lauf für diesen
Branch; vorhandene fremde PR-Checks ersetzen keine Gastmessung.

Ordentliche Fehler erhalten: altes Image/Archiv nicht erreichbar; eigener
Download ersetzt und korrekt gepinnt; erstes host-python3.12 hatte kein pytest,
vorhandene venv3.12.13 ohne Hostinstallation verwendet; Qualifikation zeigte
nur Returnprobe im Profil, Grenze vor erstem Writer ausdrücklich eingefroren.
Kein Writer-Versuch gescheitert oder verborgen, keine nachträgliche Specänderung.

**Nachweisgrenzen:** Nur privilegierter, vertrauenswürdiger Observer im eigenen
Linux6.8.0-142-Gast, reguläre lokale Ext4-Dateien und kleine synchrone write-
Aufrufe. Kein Produktions-/unprivilegierter Runnernachweis, keine allgemeine
Linux-/Dateisystem-/Transport-/Thread-/mmap-/io_uring-Abdeckung. Kernel und
Collector sind Vertrauensbasis, nicht gegen kompromittierten Root abgesichert.
write-Return zeigt angenommene Bytes, keinen dauerhaften fsync-/Crashzustand.
Forkstart ist keine Exec-Image- oder logische Agentenidentität. Autor, Modell,
Gespräch und Prozess→logischerAgent bleiben **UNBEKANNT**. Historischer P4-
Writer und alte A1/A2/C1-Lücken werden nicht rückwirkend geschlossen. D-012
bleibt Beobachtung/Analyse; kein ALLOW/DENY oder operativer Produkteingriff.

Artefakte: `docs/a1-linux-runs/2026-10-12/` mit L1–L6, cohort, PID-Reuse,
Channels/Qualifikationen, pre-run-lock, VM-/Image-/Post-Run-Nachweisen, Quellen,
Tests, Metriken und Hashindex.370 Basisdateien bytegleich. Reproduktioncode:
`research/a1_linux/{observer,oracle,writer,driver,reuse_oracle,score,channels}.py`.
Bei späterer Wiederholung neue Boot-/Scope-/Quellregistrierung und neuen
Ausgabeordner verwenden, alte Aufnahme nicht fortschreiben oder ersetzen.

Primärverträge: [Linux VFS-write](https://github.com/torvalds/linux/blob/e8f897f4afef0031fe618a8e94127a0934896aba/fs/read_write.c),
[BCC-Probe-Attach](https://github.com/iovisor/bcc/blob/v0.29.1/src/cc/libbpf.c),
[Lima Plain](https://lima-vm.io/docs/config/plain/). Hashes und Datenquelle
stehen im Archiv; externe Vertragslinks allein sind kein Versuchsbeweis.
Forschungsrunde abgeschlossen. Keine weitere Phase, PR-Freigabe oder Merge.
