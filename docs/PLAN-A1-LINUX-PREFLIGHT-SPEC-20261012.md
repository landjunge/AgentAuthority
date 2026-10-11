# A1-LINUX-PREFLIGHT — eingefrorener Diagnoseumfang

Basis: `f87157a044b308901083067d2f606b39bd52f875`, Repository
`landjunge/agent-authority-lab`. Eigenes Worktree
`/Users/landjunge/agent-authority-a1-linux-preflight`, eigener Branch
`codex/a1-linux-preflight-20261012`. Nutzerauftrag: ausschließlich vorhandene
Umgebungen und Schnittstellen prüfen, ein künftiges Protokoll entwerfen,
Dokumentation regulär versionieren. Keine Writer-Experimente oder Folgefreigabe.

## Frage und vorab festgelegte Regeln

Welche tatsächlich erreichbare Linux-Umgebung bietet unter den gegenwärtigen
Rechten eine dokumentierte, möglicherweise geeignete unabhängige Verbindung
zwischen Schreibaktion, konkretem Dateiobjekt und verursachender Prozessinstanz?
Dies ist ein Verfügbarkeitsvorcheck, kein neuer Test von H-A1. Keine eingefrorene
historische Hypothese wird ersetzt. Original-A1 und macOS-Folgerunde bleiben
INCONCLUSIVE, Writer/Agentenidentität UNBEKANNT.

Die Ergebnisdarstellung trennt drei Spalten: dokumentierter API-Vertrag,
tatsächlich gemessene Zugänglichkeit, experimentelle Kausalität. Metadaten,
Konfiguration, CLI-Präsenz oder ein lesbares Header/BTF sind kein gestarteter
Ereigniskanal. NICHT VERFÜGBAR bezeichnet nur die konkrete zugelassene Umgebung
und den bezeichneten Zugang; nicht die universelle Unmöglichkeit auf Linux.
BELEGT bezeichnet gemessene Diagnosefakten, UNBEKANNT nicht erhobene Tatsachen.

## Erlaubte Diagnose

Lesen: vorhandene A1/ABC/A2/C1-Dokumente, Herkunfts-/Prozessberichte, Whiteboard
1917/1922–1924/1927–1930; Git-Objekte, Branch/Remote/CI-Metadaten. Aktuelle
Ausführungsumgebung mit uname/OS/UID und vorhandene Container-/VM-Werkzeuge.
Colima nur bei bereits laufender VM: SSH mit normalem bestehendem Benutzer,
keine Start-/Neustartbefehle. Docker nur am expliziten Colima-Kontext: reduzierte
Bestands-/Konfigurationsabfragen. Bestehende gestoppte Container bleiben gestoppt.

Optional ein neuer kurzlebiger Diagnosecontainer ausschließlich aus einem bereits
lokal vorhandenen Image, `--pull never --network none --read-only --cap-drop ALL
--security-opt no-new-privileges --user 501:1000`, ohne Host-/Repo-Mounts. Er
erzeugt keine künstlichen Schreibfälle und verändert keine laufende Fremdarbeit.
Er ist ein Container auf dem VM-Kernel, keine eigene VM oder Linux-Simulation.

Ein neues ausschließlich auf diesem Forschungsbranch ausgelöstes Actions-
Diagnoseworkflow darf auf ubuntu-latest den identischen Standardbibliothek-
Lesecode ausführen. Keine Softwareinstallation, sudo oder bestehende Workflow-
Änderung; read-only GITHUB_TOKEN, kurze Laufzeit, keine produktiven Ereignisse.
Nur minimiertes JSON in stdout; kein neuer PR/Ready/Merge erforderlich.

Linux-Leseprobe: Kernel/Distribution/Architektur, eigene UID/GID/Capabilities,
seccomp/NoNewPrivs, eigene Namespace-Links und optional PID1-Namespace-Links
(Zugriffsfehler behalten), eigene /proc-Startzeit ohne comm/argv/env, ausgewählte
Mount-Typen/Optionen ohne produktive Pfade, LSM/Lockdown/AppArmor-Kontext,
BPF/perf-/fanotify-/Audit-relevante Sysctls und lesbare Kernel-Konfiguration.
Nur Dateimetadaten und eng gefilterte Tracepoint-Formatdefinitionen, keine
trace_pipe-, Auditlog-, Daten- oder Ereignislesevorgänge. Tool-Präsenz via PATH,
keine Installation. Fehlende Informationen bleiben null/UNBEKANNT.

Verboten: sudo/setcap, unshare/neue Rechte-Namespaces, seccomp/LSM/Sysctl-
Änderungen, BPF-Laden/Attach, perf-Aufnahme, Trace-Aktivierung, fanotify-Gruppen
oder Marks, Audit-Regeln/Daemon-/Multicast-Subscription, ptrace/strace von
Fremdprozessen, produktive Dateien/Inhalte, Prompts/Modelldaten/Secrets.
Kein Stoppen oder Neustarten bestehender Prozesse/VMs/Container, kein P7-Eingriff.

## Ausgabe, Schutz und Abschluss

Neue Dateien ausschließlich unter `docs/PLAN-A1-LINUX-*`,
`docs/a1-linux-preflight/2026-10-12/` und ein neues
`.github/workflows/a1-linux-preflight.yml`. Diagnosecode ist Forschungsartefakt,
kein Produktmodul. Alle 350 an der Basis versionierten Dateien werden mit
Git-Blobs verglichen und müssen unverändert bleiben. Keine Änderung an PR44,
R0, A2, B1/B2/C1, P7/P8, historischen Tests oder Daten.

Prüfen: Syntax/Format/Lint des neuen Diagnosecodes, nachvollziehbare JSON-
Struktur, Quellen-/Artefakthashes, Diff-/Bestandsschutz, explizites Push-Ziel.
Keine neue Forschungs-/Writer-Testausführung, keine vollständige Suite nötig
für dieses reine Diagnose-/Dokumentationspaket. Dokumentationskonformität und
Hypothesenausgang getrennt; Writer-Kausalität in dieser Runde immer UNBEKANNT.
STOP bei nötiger Rechteerhöhung, Installation, Ereignisaktivierung, unbekannter
Fremdarbeit, Scope-/Historienänderung. Gewöhnliche Diagnosefehler dokumentieren;
andere erlaubte Lesewege fortsetzen. Abschluss mit Vergleichsmatrix und
vorregistrierbarem, ausdrücklich UNGESTARTETEM Sechs-Fälle-Protokoll, regulären
Commits/Pushes nur auf dem eigenen Branch. Kein automatischer Folgeversuch.
