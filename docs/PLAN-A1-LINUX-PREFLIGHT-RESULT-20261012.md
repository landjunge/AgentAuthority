# A1-LINUX-PREFLIGHT — echte Linux-Umgebungen, Schreiberkausalität UNBEKANNT

Abgeschlossen ist ausschließlich der Umgebungsvorcheck. **Keine Writer-Fälle,
kein Kernel-Ereigniskanal, keine Rechteerhöhung oder Installation ausgeführt.**
Die vorhandenen Linux-Kernel bieten dokumentierte Kandidaten, aber unter den
gemessenen normalen Benutzerrechten ist kein qualifizierter zugänglicher
Dateischreiberkanal nachgewiesen. Das ist kein Unmöglichkeitsbeweis für Linux
oder macOS.

Repository `landjunge/agent-authority-lab`, Basis
`f87157a044b308901083067d2f606b39bd52f875`; separater Branch
`codex/a1-linux-preflight-20261012`, Worktree
`/Users/landjunge/agent-authority-a1-linux-preflight`. Datenpfad
`docs/a1-linux-preflight/2026-10-12/`; Datum ist Europe/Berlin,
Messzeiten innerhalb der JSON-Dateien UTC. Eingefrorener Diagnoseumfang:
`PLAN-A1-LINUX-PREFLIGHT-SPEC-20261012.md`, Spec-Commit `1cff776`.
Abschließende gemessene Probe: `44f714049a80dbc44549c642004f36cf89f3eea3`.
Spätere Ergebnisdateien ändern diese Probe nicht.

## Bestand und ursprüngliches A1

Gelesen und im Quellenmanifest gehasht: ABC-Forschungsplan einschließlich
additiver Identitätsfrage und F1–F7; ABC-Ausführungsbericht; Original-A1-Spec und
SDK-Preflight-JSON; A1-native-Spec und Ergebnis MD/JSON; A2-Status; C1-Ergebnis;
LOKALE-PROZESSBELEGE, NATIVE-HERKUNFTSMODUL und RESEARCH-METHOD. Dazu vorhandene
Whiteboard-Einträge 1917, 1922–1924, 1927–1930. Das Board ist Dokumentationsquelle,
kein Beweis der Betriebssystemhandlung oder Verfasseridentität.

Original-A1 blieb **A FAIL/B INCONCLUSIVE**, weil der statische Vorcheck in
FSEvents, kqueue und proc_pidinfo keinen unabhängigen kausalen Writer-Kanal
fand. Ein Writer-Versuch wurde nicht gestartet. Die spätere native Mac-Runde
belegte eigene Prozess-/FD-/Mach-Snapshots und tatsächliche Zugriffsablehnungen
bei Audit/ES/fs_usage/DTrace; ebenfalls keine Writer-Experimente. Weder alte
Hypothesen noch Ergebnislabels werden hier verändert. A2 bleibt gesperrt;
P7/P8/C1 enthalten reale begrenzte lokale Wirkungsbelege, keine unabhängige
Agenten-/Schreiberherkunft. Git/CI-PASS erzeugt keinen solchen Nachweis.

## Tatsächlich geprüfte Umgebungen

| Umgebung | Kernel/Typ: BELEGT | Gegenwärtige Rechte und Barrieren: BELEGT | Writer-Kausalität |
| --- | --- | --- | --- |
| Codex-Ausführung / Mac | Darwin24.6.0, macOS15.7.4, x86_64; kein Linux-Kernel | UID501; /proc und /sys fehlen; macOS-A1-Grenzen unverändert | UNBEKANNT; Linux-Kanal NICHT VERFÜGBAR in diesem Hostprozess |
| Bereits laufende Colima-VM | echter Linux6.8.0-100-generic, Ubuntu24.04.4, x86_64, macOS Virtualization.Framework; VM, keine Simulation | UID501, CapEff/Prm/Amb0, Seccomp0, NoNewPrivs0; BPF-Sysctl2, perf_paranoid4; Tracefs0700/root und Formate EACCES; BTF-Metadaten lesbar | UNBEKANNT; benötigte ereignisbezogene Rechte fehlen |
| Neuer kurzlebiger Diagnosecontainer | Debian12-Userspace auf genau diesem VM-Kernel6.8; echte Container-Namespace-Isolation, keine eigene VM | UID501/GID1000; alle Capability-Sätze einschließlich Bounding0; Seccomp2/1 Filter, NoNewPrivs1, docker-default(enforce), read-only Root/kein Netz/keine Hostmounts; Tracepoint-Dateien ENOENT | UNBEKANNT; keine Hostereignisrechte oder Tracefs-Sicht |
| Frischer GitHub-Actions-Job | github-hosted Ubuntu24.04.5, Kernel6.17.0-1022-azure, x86_64; Imageubuntu24/20261004.327.1 | UID1001, CapEff/Prm/Amb0; Seccomp0/NoNewPrivs0; BPF2/perf4; ausgewählte Tracepoint-Formate EACCES; Audittools fehlen, BPF/Perf/Compiler-Tools vorhanden | UNBEKANNT; Tools/BTF/CONFIG=y sind keine Zugriffsfreigabe |
| Bestehende drei Projektcontainer | Colima-Docker-Inventar: zweimal aa-run03-python, einmal agent-zero, alle exited | Nur Konfiguration gelesen, privileged=false. Effektive Laufzeit-Caps, seccomp und Namespaces UNBEKANNT, weil nicht gestartet | Kein aktuell laufender Kanal NICHT VERFÜGBAR; Kausalität UNBEKANNT |

Die Codex-VM ist nicht heimlich Linux; Git ist Versionsverwaltung, keine Linux-
Simulation. Colima-VM und Container teilen Kernel und Boot-Hash, aber haben
verschiedene PID-/Mount-/Net-/Cgroup-Namespaces. Eigene Namespace-Inodes und
UID/GID-Maps sind erfasst. PID1-Namespace-Zugriff ist in VM/Actions EACCES und
wird nicht zu einer bewiesenen Initial-Namespace-Gleichheit umgedeutet.

Nur Colima hat einen erreichbaren vorhandenen Docker-Socket. Registrierte
default/desktop-linux/orbstack-Kontexte beweisen keine laufenden Linux-Systeme;
ihre Sockets fehlen. Der anfängliche Docker-Aufruf am vorgewählten orbstack-
Kontext scheiterte. Danach wurde ausdrücklich `--context colima` verwendet,
ohne den globalen Kontext zu ändern. `limactl list` im normalen Lima-Kontext
meldet keine Instanzen; Colima verwendet seinen separaten Kontext. Keine
allumfassende Suche über alle Datenträger/Remote-Geräte behauptet.

Repository-Actions-Runner-API: total_count0 für zugängliche self-hosted Runner.
Die vorhandenen Projektworkflows verwenden ubuntu-latest. Nur historische
Runnerlogs zu lesen hätte Kernel/Capabilities nicht belegt: daher ein separates
branchgebundenes Push-Workflow, ohne PR oder Änderungen an bestehenden CI-Dateien.
Direkte neue Codex-Linux-Ausführungsumgebung nicht festgestellt.

## Kanäle: Vertrag, Zugang und Kausalität getrennt

| Quelle | Dokumentierte API-Eignung | Gemessener Zugang / konkreter Blocker | Experimenteller Nachweis |
| --- | --- | --- | --- |
| /proc, pidfd, Dateistat | Prozessstartticks/Boot/Namespace und gehaltene Instanzen/Objekte können Identitätskomponenten beitragen | Eigene /proc-Startzeit in drei Linux-Diagnosen BELEGT; pidfd/Dateiaktion nicht aufgerufen | UNBEKANNT; Snapshot oder offener FD enthält keine verursachende Schreibaktion |
| fanotify | Kernel-NOTIFY mit Änderungsmaske, Datei-FD/FID und optional kausal erzeugter PIDFD; Overflowanzeige | CONFIG_FANOTIFY=y in VM/Actions und lesbare Grenzwerte BELEGT; keine Gruppen/Marks aufgerufen. Ohne CAP_SYS_ADMIN unterdrückt Upstream6.8/6.17 fremde PID/PIDFD: für unabhängigen Schreiberkanal vertraglich NICHT VERFÜGBAR | UNBEKANNT; zusammengefasste Benachrichtigung, kein geprüfter einzelner write-Return oder Kernel-Aktionszeitstempel; PIDFD kann nach Exit fehlen |
| Audit/netlink | Kernel-SYSCALL+PATH/CWD ggf. Rückgabe/dev/inode, serial/Zeit; Lifecycle-/Instanzkorrelation zusätzlich nötig | CONFIG_AUDIT/AUDITSYSCALL=y BELEGT; CAP_AUDIT_READ/CONTROL fehlen, auditctl/ausearch fehlen. Keine Subscriptions/AUDIT_GET/Loglesung; Aktivzustand, Regeln, Verlustzahlen UNBEKANNT | UNBEKANNT; Auditsupport ist nicht aktive passende Aufzeichnung. Userspace-Auditmeldungen nicht als Kernelaktion übernehmen |
| eBPF VFS-Entry/Return | Potenziell verursachender Task samt Start/Lifecycle, struct-file-Objekt, Aktion/Return und monotone Kernelzeit; Verlustzähler implementieren | BPF/BPF_EVENTS/BTF-Konfig in VM/Actions BELEGT; BTF nur stat/access geprüft. CapBPF/Perfmon/SysAdmin fehlen, unprivileged_bpf_disabled2. BPF-Aufrufe/Attach absichtlich nicht versucht | UNBEKANNT; konkrete Hook-/ABI-/Verifier-/Dateisystemeignung nicht gemessen, keine eigene Probe durch beliebige Programmladung |
| Tracepoints/perf/ftrace | Sys_enter_write enthält FD/Count, sys_exit_write Return; Lifecyclepunkte und Zeit möglich. Numerischer FD ist kein konkretes Dateiobjekt; kausaler Datei-Join fehlt | Alle ausgewählten Format-Leseversuche VM/Actions EACCES, Container ENOENT; perf_paranoid4, keine Perfmon-Cap. Keine Tracing-Aktivierung/Perf-Events | UNBEKANNT; das kombinierte Prozess-/FD-Snapshotverfahren wäre weiter rennend |
| inotify | Lokale Änderungen/Watch/Queue-Overflow | Kein neuer Watch aufgerufen; bekannte Schnittstelle wird nicht als Writerquelle wiederholt | UNBEKANNT; kein verursachender Prozess im Ereignisvertrag |
| macOS historisch | BSD-/FD-/Mach-Komponenten BELEGT, ES/Audit technisch dokumentiert | Tatsächliche ES NOT_PRIVILEGED5, Audit EPERM/EACCES, native Tracer-Ablehnung aus unverändertem Archiv | UNBEKANNT; keine neue Umklassifizierung oder OS-Generalisation |

Linux-Quellverträge wurden an Upstream6.8 und6.17 gelesen und mit Commit/Hash
archiviert. Das sind **nicht** die behaupteten exakten Ubuntu-Downstream-
Kernelquellen. Daher sind Vertragsableitungen und gemessene Zugriffsversuche
unterschiedliche Belegklassen: kein fanotify-/BPF-/Audit-EPERM wird erfunden,
wenn der entsprechende Aufruf hier gar nicht stattfand.

VM/Actions: LSM-Liste mit capability/landlock/yama/apparmor/lockdown, Actions
zusätzlich ima/evm; eigener Prozess unconfined, AppArmor-Modul Y, Lockdown[none].
Das beweist keine global ausgeschaltete Sicherheitskontrolle. Im Container ist
der eigene AppArmor-Kontext docker-default(enforce); globale LSM/Lockdown-Dateien
nicht sichtbar. Fehlendes SELinux-enforce ist kein umfassender LSM-Aus-Beweis.
Seccomp0 gilt für den Diagnoseprozess; Seccomp2 gibt keine dekodierte Liste
der gesperrten Syscalls. Keine neuen User-Namespaces oder Entsperrversuche.

GitHub dokumentiert sudo-Möglichkeiten für gehostete Linux-VMs; das ist keine
Nutzerfreigabe zur Nutzung. Es wurde kein sudo, setcap, privileged Container,
Kernel-/Audit-/BPF-Konfigurationswechsel oder Paketinstallationsschritt ausgeführt.
GITHUB_TOKEN nur contents:read, checkout ohne gespeicherte Credentials,
Workflow3-Minuten-Limit. ubuntu-latest/Image/Kernel beweglich: dieser Befund ist
der zeitlich gepinnte Job, keine dauerhafte Runnergarantie.

## Reproduktion, Fehler und Qualität

Die finale Standardbibliothek-Probe ist `a1-linux-preflight/2026-10-12/probe.py`.
Sie liest ausschließlich feste Metadatenpfade, keine Ereignis-Streams/Buffer,
Fremd-argv/env oder Produktionsinhalte. Exakte lokale Diagnosebefehle, Zeit,
Exitcode, stdout-/stderr-Zählung und Hash: `commands.json`. Inventar und
Remote-Runner-API: `inventory.json`. Lokale Probe über stdin in `colima ssh`
(Arbeitsverzeichnis `/Users/landjunge`, kein VM-Neustart) und neues Docker-
Diagnoseobjekt aus bereits lokalem Image:
`python@sha256:34386ef0cb081344d7ec1c103ba398e6e9f64e9ab3a1509accc92a4e24a07258`.
Kein Pull/Install; ohne Netzwerk, read-only, keine Caps/Hostmounts. Vorher/nachher
dieselben drei gestoppten Projektcontainer, kein bestehender Prozess angefasst.

Reproduktion in einer separat erlaubten Linux-Umgebung:
`python3 -B docs/a1-linux-preflight/2026-10-12/probe.py --label github-actions`.
Die label-Zeichenfolge ist keine Authentisierung der Umgebung; tatsächliche
Runnerbindung stammt aus dem separaten Actions-API-/Git-Nachweis.

Frischer finaler Actions-Diagnosejob:
[38179870080](https://github.com/landjunge/agent-authority-lab/actions/runs/38179870080),
push, COMPLETED/SUCCESS, exakt Quellen-SHA44f7140. Minimiertes Ergebnis mit
Loghash, eigener UID/Caps/Namespaces und Runner-IDs dauerhaft im JSON-Archiv.
Die beiden früheren erfolgreichen Diagnosejobs werden als frühere Versionen
aufbewahrt; deren unvollständige Sysctlmessungen sind kein finaler Nachweis.

Ordentliche Fehler bleiben sichtbar: erster Colima-stdin-Aufruf aus einem
nicht VM-gemounteten neuen Worktree scheiterte vor der Probe; erneuter Aufruf
aus bestehendem Benutzerverzeichnis erfolgreich. Große read-Anforderung8MiB
auf Proc-Sysctl ergab ENOMEM12, **kein Rechtebeleg**; kleine4KiB-Leseschritte
lieferten dieselben Werte wie die getrennten anfänglichen cat-Diagnosen.
Initiale JSON-Versionen erhalten. Ein unbenutzter Import (RuffF401) wurde zu
früh im Implementierungscommit versioniert, in eigenem Fix entfernt; kein
historischer Commit umgeschrieben. Finale Ruff-/Format-/Syntax-/JSON-Prüfung
bestanden. Keine vollständige Testsuite oder Writer-Forschungsfälle ausgeführt;
erfolgreiches Diagnoseworkflow ist keine Kausalitäts-Acceptance-Suite.

Ressourcen (nur finale Python-Diagnoseprozesse, nicht VM/CI/Containerstart oder
Ereignismonitor): VM CPU user0.055495s/system0.028338s, PeakRSS18,219,008B;
Container0.218492s/0.038909s, PeakRSS21,037,056B;
Actions0.020640s/0.008256s, PeakRSS21,684,224B. Körperlaufzeiten und API-/
Diagnosebytes stehen separat in JSON. Rohereigniszahl/-bytes, Monitor-CPU/RAM,
korrekte/unklare Writerzuordnung und Fehlerraten bleiben null/UNBEKANNT.
Keine Nullverluste oder Zuverlässigkeitsquote aus null Experimenten ableiten.

## Ergebnis und nächster Schritt

Verfügbare **Metadatenquellen BELEGT**, Linux-Writerkausalität **UNBEKANNT**.
Kein tatsächlich zugänglicher qualifizierter unabhängiger Ereigniskanal im
gemessenen Rechteumfang ausgewählt. Keine H-LINUX-A1-Abnahme oder Aufwertung
von H-A1, A2 oder Agentenidentität. Hohe Sicherheit in den eng gemessenen
Konfigurations-/Zugriffsfakten; Eignung und Generalisierung UNBEKANNT.

Der [Protokollentwurf](PLAN-A1-LINUX-PROTOKOLL-ENTWURF-20261012.md) beschreibt
die sechs Fälle und ein vom Beobachter getrenntes Ground Truth-Orakel. Er ist
noch nicht vollständig versiegelt und wurde **nicht ausgeführt**. Empfohlen:
zuerst eine ausdrücklich erlaubte dedizierte Linux-Umgebung samt engem
Kernel-Beobachtungszugang bereitstellen/auswählen, danach exakte Quelle/Hashes
und Instanz-/Datei-/Zeit-/Verlustvertrag vorregistrieren. Keine pauschale
sudo-/CAP_SYS_ADMIN-Anforderung: fanotify wäre kleiner für Benachrichtigungen,
aber für strenge Einzeloperation möglicherweise unzureichend; eBPF benötigt
gesondert validierte Hooks und Rechte. Jetzt keine Installation, Rechtevergabe
oder Writer-Ausführung anschließen.

## Primärquellen

Alle gelesenen Projekt-/Whiteboard-Hashes in `read-sources.json`, externe
URLs/Commit-SHAs/Inhaltshashes in `primary-sources.json`. Upstream6.8:
`e8f897f4afef0031fe618a8e94127a0934896aba`; Upstream6.17:
`e5f0a698b34ed76002dc5cff3804a61c80233a7a`. Insbesondere
[fanotify-Zugriff und PIDFD](https://github.com/torvalds/linux/blob/e8f897f4afef0031fe618a8e94127a0934896aba/fs/notify/fanotify/fanotify_user.c),
[aktueller fanotify-Metadatenvertrag](https://github.com/torvalds/linux/blob/e5f0a698b34ed76002dc5cff3804a61c80233a7a/include/uapi/linux/fanotify.h),
[Audit-Netlinkrechte](https://github.com/torvalds/linux/blob/e8f897f4afef0031fe618a8e94127a0934896aba/kernel/audit.c),
[BPF-Rechteprüfungen](https://github.com/torvalds/linux/blob/e5f0a698b34ed76002dc5cff3804a61c80233a7a/kernel/bpf/syscall.c),
[Perf-Rechte](https://docs.kernel.org/admin-guide/perf-security.html),
[Sysctls](https://docs.kernel.org/admin-guide/sysctl/kernel.html),
[Tracepointverträge](https://docs.kernel.org/trace/events.html),
[BPF-Ringbuffer](https://docs.kernel.org/bpf/ringbuf.html),
[GitHub-Runner](https://docs.github.com/en/actions/reference/runners/github-hosted-runners).
Nicht erreichbare man7-Seiten nicht als gelesene Belege ausgegeben.

Bestandsschutz: sämtliche350 Basisdateien unverändert; neue Diagnose-/Dokument-
Dateien und genau ein neuer branchbegrenzter CI-Workflow. Kein Produktcode,
historischer Test/Archiv, P7, PR44, PR45 oder fremder Branch geändert. Reguläre
Versionierung nur eigener Forschungsbranch; kein Force/Ready/Merge. Die Runde
endet mit Dokumentation und Push-Nachweis, ohne Folgearbeiten.
