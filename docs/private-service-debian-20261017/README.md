# Private Einrichtung auf dem vorhandenen Debian-vServer

Auftrag: 17.10.2026, 00:33 Europe/Berlin. Vorhandener SSH-Zugang `netcup-daniel`,
bestehender Worktree `hosted-qualification`, Ausgangscommit `0b7e8ff`.
Projektanweisungen sowie Dienst-, Sicherheits-, Kapazitäts- und Retentionabschlüsse
wurden gelesen. Keine weiteren Agenten, kein neuer Server, kein Push/Merge.
Fremde Roadmap, Kapazitätsdateien, Forschungsarchive und App wurden erhalten.

**Tatsächlich eingerichtet:** private API `127.0.0.1:8765`, getrennte Linux-Konten,
authentisierte lokale Übergabekanäle, separater Verifier/Signierer, verschlüsselter
kurzlebiger Arbeitsspeicher auf Dateisystemebene und harte Linux-Ressourcenlimits.
Die API, Signierer, Verifier und Ressourcenwächter laufen. Runner/Collector sind
beendet, der Collector-Socket geschlossen, der neue Hardstop gesetzt und die
Testidentität des Collectors stillgelegt. Der bisherige VM-Runner bleibt unverändert
gesperrt. Es gibt keine neue öffentliche Route oder Portfreigabe.

**Ein frischer Debian-Auftrag ist vollständig nachgewiesen:**
`1d24c7f6521209d87a39057d765a3cac`, Szenario `a4-write16-v1`, ein beobachteter Write
mit `count=result=16`, **BELEGT, 28 wahre Checks und 23 ganzzahlige Nullverlustwerte**.
Der Bericht wurde nach einem echten API-Neustart unverändert abgerufen und geprüft.
Signierte vollständige Empfangsbestätigung, anschließender 410-Abruf und wiederholte
Bereinigung sind nachgewiesen. Dieser Lauf benötigte eine Reparatur der Aufnahme;
der bereits ausgeführte Auftrag wurde dabei nicht erneut ausgeführt.
**Ein fehlerfreier automatischer Normaldurchlauf und Produktionsbetrieb sind damit
nicht freigegeben. Weitere Aktionen und jede Laststeigerung bleiben gesperrt.**

## Originalbelege und erfolglose Versuche

| Auftrag / Beleg | Tatsächliches Ergebnis |
|---|---|
| [Erster Versuch](single-job.json), `0da3e0cd…` | Runnerfehler vor Aufnahme; Wirkung konservativ UNBEKANNT. Signierter unbekannter Bericht, ACK und Bereinigung in [Abschluss](failed-attempt-closure.json). |
| [Zweiter Versuch](completion-job.json), `4bbb5281…` | HTTP-Verbindungsabbruch vor Runnerstart; keine Aktion gestartet. UNBEKANNT, ACK und Bereinigung in [Abschluss](pre-dispatch-failure-closure.json). |
| [Dritter Versuch](qualified-job.json), `954ccd15…` | Collector-Paket übergeben, Aufnahme fehlgeschlagen; Rohpaket damals nicht erhalten. UNBEKANNT, ACK und Bereinigung in [Abschluss](capture-intake-failure-closure.json). |
| [Frischer erfolgreicher Auftrag](complete-service-job.json), `1d24c7f6…` | Initialer Koordinator scheiterte; derselbe verschlüsselte Übergabebeleg wurde anschließend unter der echten Runner-UID aufgenommen. [Vollständiger Abschluss](completed-same-fresh-job.json), [letzte Prüfung](receipt-revocation-final.log). |
| [Signierter Originalbericht](signed-report.json) | Fertigstellung `2026-10-16T23:32:10.695Z`; ursprüngliche maximale Abruffrist exakt 24h. Nach ACK früher gesperrt und entfernt. `grants_rights=false`, Provider-/Modellidentität UNBEKANNT. |
| [Unabhängige Signaturprüfung](independent-report-verification.txt) | Lokales OpenSSL prüft exportierte Originalbytes erfolgreich; ausschließlich synthetische öffentliche Belege exportiert. |

Keine erfolglosen Versuche wurden als erfolgreich umetikettiert. Die anfänglichen
Fehlerprotokolle bleiben erhalten. Der Abschluss dokumentiert auch zwei falsche
Erwartungen im Bedienprüfer: Nach der Aufnahmehilfe waren die ursprünglichen
60s-Requests bereits abgelaufen. Ihre exakten Wiederholungen müssen 410 ergeben.
Ein **zusätzlicher frischer** Request des widerrufenen Empfängerschlüssels wurde
separat mit 403 `KEY_REVOKED` abgewiesen. Die Fristen oder Diensttests wurden dafür
nicht gelockert. Die bestehende Dienstimplementierung bestimmt diese Reihenfolge.

Korrigiert wurden die fehlende öffentliche A2-Protokolldatei neben dem unveränderten
A4-Agenten, das notwendige Beenden eigener Kinder mit anderer UID, Timer-/Allocator-
Spitzen der API und die durch umask versehentlich auf 0700 reduzierte Verifier-
Übergabe. Diese hat jetzt gezielt 0750; Verifier schreibt, Signierer liest,
API/Runner besitzen dort keine Rechte. Aufnahmehilfe beansprucht keine neue Arbeit
und ruft keinen Collector auf. Der Übergabebeleg lag ausschließlich im verschlüsselten
Runner-Verzeichnis; ein eigener 180s-Timer begrenzte seine Lebensdauer.

## Rechte und tatsächliche Isolation

Der bestehende KVM-vServer hat acht vCPUs und 15,62GiB RAM. Für den ausschließlich
eigenen festen synthetischen Ablauf wurden Linux-UIDs sowie Mount-, Netzwerk- und
cgroup-Grenzen auf diesem Host gewählt und praktisch geprüft. Eine zusätzliche VM
würde einen anderen zu qualifizierenden Kernelpfad schaffen. Beliebiger Kundencode
ist in dieser Installation nicht zugelassen; der privilegierte Collector bleibt
ein ausdrücklich vertrauenswürdiger Bestandteil. Container/VM-Neuinstallation
war für diesen abgegrenzten Nachweis nicht erforderlich.

| Komponente | UID / Rechte / Kanal |
|---|---|
| API | `aa-api` 987, keine effektiven/erlaubten/vererbbaren/ambienten Capabilities; keine privaten Signierkeys, kein BPF/ptrace/perf; Loopback HTTP. |
| Signierer | `aa-signer` 986, eigener 0600-Reportkey, eigener Socket nur für API-UID; Signatur nur für festes Berichtsformat, Messbericht an unabhängiges Verifier-Ergebnis gebunden. |
| Verifier | `aa-verifier` 985, eigene unveränderbare Collector-Pins und eigene Verifikationsgrenze; Socket nur für API-UID. Keine Signierkeys. |
| Runner | `aa-runner` 984, eigener Runnerkey; nur feste Claim-/Pin- und Collector-Kanäle. Keine freie Shell, Datei-/URL-/Codeauswahl. |
| Registrar | `aa-registrar` 983, ausschließlich eigene synthetische Operatorcredentials in 0700-Verzeichnis. |
| Testakteure | UIDs 61101/61102, unterschiedliche Schlüssel; keine Capabilities. UID A kann das 0600-Testobjekt von UID B nicht öffnen. |
| Collector | Vertrauenswürdiger root-Dienst mit begrenztem Capability-Set: BPF, PERFMON, SYS_ADMIN, SETUID, SETGID, CHOWN, DAC_OVERRIDE, KILL. Kein allgemeiner Hostmitschnitt. Kein Schutzversprechen gegen kompromittierten root/Kernel/Collector. |

[48 praktische Prüfungen](completion-preflight.log) belegen gegenseitige
UID-/Key-/Objektverweigerung, Socket-ACLs, Ablehnung freier API-Signaturaufträge,
Ablehnung erfundener Verifier-Pins und echten BPF-EPERM der API-UID. Die finale
[native Rootverweigerung und Dienstprüfung](final-state.json) ergänzt dies.
SO_PEERCRED authentisiert eingehende Clients; Listener stammen von systemd/PID1.
Feste 512KiB-Eingabegrenze, 64KiB-Komponentenausgabe, 262KiB-Collector-Ausgabe,
absolute IPC-/HTTP-Fristen und keine frei wählbaren IPC-Endpunkte.

[Kernelprüfung ohne Aktion](actor-ready-kernel-check-two.log): sechs Programme auf
`6.12.101+deb13-amd64` tatsächlich geladen/angehängt, alle Rekursionsverlustwerte null,
eigene Profile vollständig und eigene Proben wieder gelöst, keine fremden Records.
VFS filtert **vor** dem Lesen des Dateiobjekts auf UID 61102 und den eigenen
Collector-cgroup-Kontext; Lifecycle zusätzlich auf eigene Starter-Nachkommen.
Nur eigene Profilzeilen werden gespeichert. Die unveränderten A2/A4-Prüfungen
entscheiden auch heute über 28 Checks/23 Verlustzähler.

Debians bestehendes `perf_event_paranoid=3` erforderte zusätzlich SYS_ADMIN im
Collector; die passende Kernelquelle wurde geprüft. Die globale Einstellung blieb
unverändert. ProtectKernelModules bleibt aktiv; die exakt passenden Header liegen
in einer separaten unveränderbaren Sicht. Nur die neuen Collector-Tracefs-Pfade
wurden schreibbar eingebunden. API und übrige Konten erhielten diese Rechte nicht.

## Budgets, Messung und Abbruch

[Frische 120s-Grundlast vor Einrichtung](baseline-before-summary.json): 13 Samples,
CPU-Median 0,620%, Maximum 1,667%, mindestens 15.837.712.384 Bytes MemAvailable.
Zusätzlich wurden unmittelbar vor den Versuchen neue 30s-Gesundheitsfenster geprüft;
diese enthalten laufende Prüf-/Dienstaktivität und sind **keine neue Idle-Baseline**.

[Einzelauftragsmessung](single-job-metrics.json): Collector 20,552s; erstes Runner-/
Aufnahmefenster 22,204s, 20 Gesundheitssamples, Host-CPU im Mittel 4,727%, maximal
8,764%, MemAvailable mindestens 15.505.063.936 Bytes. Eigene Slice maximal
621.948.928 Bytes und 10 Tasks, Swap 0; 5,795 CPU-s zwischen den erfassten
Slice-Zählerständen. Einschließlich manueller Aufnahme-/Prüfkorrekturen dauerte der
vollständige Abschluss 287,711s ab Runnerstart. Das ist **kein Durchsatznachweis**.
Hostgesamtlast umfasst andere Aktivität; 1s- und 10s-Samples sind nicht gleichwertig.

Vorab gesetzte automatische Schwellen: Host-CPU >10,5% drei Samples; MemAvailable
<25% bzw. 1GiB; eigene RAM-Nutzung >720MB zwei Samples; >43 Tasks; jeder neue OOM
oder eigener Swap; IO-full-PSI >5 drei Samples; KI-Endpunkt-/Aktivitätswechsel,
Probe >250ms zwei Samples, Messlücke >2,5s, zu wenig Plattenreserve. Der Wächter
schließt zuerst den Aktivierungssocket und stoppt anschließend echte Runner- und
Collector-cgroups. [Praktische Gegenfälle](limit-checks-three.log): kontrollierter
RAM-OOM stoppt beide echten Dienste, CPU-Quote plus Zeitlimit beendet Busyloop,
TasksMax verweigert den dritten Prozess, Dateibytegrenze greift, Ciphertext enthält
keinen Klartextmarker, falscher Restorekey kann das separate Probevolume nicht mounten.

Der erfolgreiche Test lief mit Slice 40% eines Kerns / 800.000.000 Bytes plus
separatem Wächter 5% / 64MiB. **Danach konservativ enger gesetzt:** Slice 35% /
768.000.000 Bytes, TasksMax 48; Wächter 5% / 64MiB außerhalb der zu stoppenden Slice.
Zusammen höchstens 0,4 Kerne = 5% des 8-vCPU-Hosts und 835.108.864 Bytes RAM
(ca. 796,42MiB). Die neue engere Grenze wurde statisch/live gelesen; darunter wurde
kein weiterer Schreibauftrag durchgeführt. [Änderung](final-budget-tightening.json).
Alle Dienst-cgroups haben MemorySwapMax=0. API 128MiB/8 Tasks; Signierer 96MiB/4;
Verifier 192MiB/4; Runner 64MiB/2/175s; Collector 512MiB/12/180s und 16MiB pro Datei.
Das verschlüsselte Arbeitsvolume hat zusätzlich eine harte 256MiB-Gesamtgrenze.

KI-Zentrale blieb aktiv mit derselben PID 1011380 und unverändertem Unit-Hash.
Ihr Limit bleibt 256MiB / 50% eines Kerns / 64 Tasks. Die unveränderte
TCP-Erreichbarkeit und HTTP-403-Baseline am geschützten Healthpfad wurden überwacht;
403 ist keine authentisierte fachliche Gesundheitsprüfung. Im erfolgreichen Fenster
keine Abbruchgründe. Die im Gesamtprotokoll enthaltenen OOM-Abbrüche stammen aus den
expliziten Negativtests. Keine Produktionsminderung wurde erzwungen.

## Speicher, Retention und konkrete Grenzen

`/var/lib/aa-private/epoch.ciphertext` (0600, 256MiB) → dm-crypt AES-XTS mit
512-Bit-Zufallsschlüssel → `/var/lib/aa-private/secure`, ext4 **ohne Journal**, nodev,
nosuid, noexec. Epochenschlüssel nur in Prozess-/Kernel-RAM erzeugt, keine Keydatei,
keine Keybackup-/Klartext-Recoverykopie. Dienstinitialisierung und geheime Testoperationen
laufen unter Swap-0-cgroups; der vorhandene unverschlüsselte Hostswap wurde nicht
abgeschaltet. Tatsächliche Hostzähler bis zum Abschluss: pswpin=pswpout=0.

Dort liegen API-SQLite/WAL/SHM, GCM-Jobkeys, Signier-/Runner-/Registrarcredentials,
Collector-Keys, kurzlebige Registry-/Testakteurskeys, Compiler-/Werkzeugtmp und der
begrenzt haltbare Übergabebeleg. In-memory-EVP vermeidet Signaturtempfiles.
Signer/Verifier/API erhalten kleine noswap-Tmpfs-Mounts, keine Payloadlogs oder
Coredumps. Eigene strukturierte Fehlerdaten enthalten nur Fehlerklasse/-code/Codeorte.
Host-/SSH-/systemd-Metadaten enthalten Dienstnamen, Zeiten, Ressourcen und Quellpfade;
kein versprochener Ausschluss sämtlicher Hypervisor-/RAM-/Betreiberkopien.

Nach ACK: alle Job-Inhaltsfelder NULL, Jobkey-Verzeichnis, Pins, Verifierurteil,
Targets und Übergabe weg; erneut GET 410, wiederholtes ACK 200. Alle vier entstandenen
Aufträge sind so abgeschlossen. [Eigene Testbereinigung](test-cleanup.log) entfernt
312 Dateien, 468 Verzeichnisse und 82 Symlinks im eigenen verschlüsselten
Regressionstree, ohne Symlinkziele zu verfolgen. Zwei nach einer unterbrochenen
Vorprüfung übrig gebliebene **eigene** Tracefs-Definitionen wurden gezielt gelöscht;
kein globales Flush. Keine Testprozesse/Erfassungsproben bleiben aktiv. Die bewusst
angelegte Empfänger-Berichtskopie wurde nach dem geprüften Export vom Server entfernt.

[Collector-Testepoche stillgelegt](collector-epoch-retirement.log): öffentliche
Testpins privat gesichert, Trustdatei auf stillgelegt gesetzt, direkt geprüftes
`COLLECTOR_IDENTITY_RETIRED`, UTC-Maximalstand fortgeschrieben, drei zusätzliche
inhaltsfreie Verbrauchsmarker danach entfernt. API-Replay-/Löschsperrdaten behalten
ihre bisherigen begrenzten Fristen; Authregister/Maximaluhrstand gehören zur
Dienstidentität. Dauerhafte Dienstkeys sind getrennte Authdaten, keine Berichtskopien.

[163 verschiedene bestehende Tests](debian-regressions.json) auf Debian bestanden:
erster Lauf 161/163, anschließend die zwei Fehler gezielt bestanden. Ursachen:
fehlendes `refs`-Verzeichnis im echten minimalen Git-Fixture und zu enges
Testprozessbudget für sechs gleichzeitige Ledger-Testarbeiter. Keine Tests geändert
oder übersprungen. Historische positive Fixtures sind ausdrücklich Regressionen,
kein frischer Debian-Wirkungsbeleg. Enthalten sind 24h-/Fristgrenzen, injizierter
Uhrrollback, Neustart-/Replay-/Widerrufs-, Parser-/Dateiabruf-/Slowclient-/Verifier-
Timeoutfälle sowie gesperrte WAL-/Dateibereinigung und deren Wiederholung.
Die Hostuhr wurde nicht verstellt und kein 24h-Wandzeitlauf behauptet.

Offen bleiben: originale Keybackup-Wiederherstellung/Hypervisor-Snapshotrollback,
hardwaregestützte Vernichtung sämtlicher RAM-/Datenträger-/Betreiberkopien,
Bereinigung während komplett ausgeschaltetem System, Dauerbetrieb und höhere Last.
Der Falschkey-Test betrifft ein separates kontrolliertes Volume; er ist kein
vollständiger Backup-/Restorebeweis des Servers. Bei Reboot geht die flüchtige
Speicherepoche verloren; Units starten nicht automatisch mit neuer Identität.
Bei laufendem Dienst gelten die 24h-Zugriffssperre und Retentionsmechanik; bei
Dienstausfall wird beim Neustart vor Zugriff gesperrt und Bereinigung nachgeholt.
Es wird keine physische Löschung oder Löschung bei ausgeschaltetem System zugesagt.

## Installation, Versionen, Rückfall und Weiterbetrieb

Debian 13.6, Kernel `6.12.101+deb13-amd64`, Python 3.13.5 blieben bestehen.
[Paketdifferenz](installation-diff.json): neue distributionspassende BCC-, LLVM-,
cryptsetup- und Testabhängigkeiten. `gpgv` zog trotz `--no-upgrade` fünf vorhandene
GnuPG-Pakete von `...+b4` auf `...+b5`; dies ist hier ausdrücklich ausgewiesen.
Kein OS-/Kernel-/Interpreterupgrade und kein Reboot. Exakte Header `6.12.101-1`
aus [Debians signiertem Archiv](https://snapshot.debian.org/archive/debian-security/20260807T000000Z/),
InRelease mit Debian-Keyring geprüft, Index und drei Pakete per SHA256 gebunden;
nur nach `/opt/aa-private/headers` extrahiert. [Provenienz](header-packages-authenticated.json).
Keine Paketquellen oder globalen Sicherheits-/Firewall-/SSH-Einstellungen geändert.

- Code: `/opt/aa-private/research/`; Header-Sicht `/opt/aa-private/kernel-headers-view`.
- Konfiguration: `/etc/aa-private`, API-Projektion root:aa-api 0640, nur Hashes/Publicpins.
- [Tatsächlich installierte Units](units/) in `/etc/systemd/system/aa-private*`.
- Verschlüsselter Zustand: `/var/lib/aa-private/secure/{api,signer,verifier,runner,registrar,collector,verdicts}`.
- Private Rückfallsicherung/Änderungshistorie: `/var/lib/aa-private-install-20261017`, root 0700.
  Vorherinventar, KI-Unit-Hash, betroffene eigene Unit-/Quellversionen und Metadatensicherungen;
  keine Produktionsdatenkopie und kein privater Epochenschlüssel darin.
- Laufende Messung: dort `health.jsonl`, nur Zahlen/Status, hart auf 16MiB begrenzt;
  erschöpftes Protokollbudget schließt weitere Arbeit. Kein unbegrenzter Dauerbetrieb.
- [Exakte drei abweichende Laufquellen](qualified-source-versions.json) unter
  `qualified-source/`; übrige Laufquellen durch Berichtspins, Repository und Uploadmanifeste gebunden.

Gezielter Rückfall: zuerst nur `aa-private-collector.socket`, eigene Dienste und
Sockets stoppen; Abhängigkeiten/Mountnutzer prüfen. Danach ausschließlich den eigenen
Secure-Mount aushängen, Mapping `aa-private-epoch` schließen und dessen tatsächliches
Loopdevice lösen. Ohne den absichtlich nicht gesicherten Epochenschlüssel ist diese
Epoche anschließend nicht wiederherstellbar. Eigene Units/öffentliche Konfiguration
sind aus der privaten Sicherung rücksetzbar; eigene Konten nur nach Prüfung ihrer
verbliebenen Dateieigentümer entfernen. Gemeinsame Pakete nicht pauschal deinstallieren
oder downgraden. KI-Zentrale, öffentliche Ports, Webroots, DBs und Authdaten bleiben
außerhalb dieses Rückfalls. Historische Forschung und App sind kein Löschziel.

Nächste Ausführungsfreigabe erfordert eine frische explizite Testidentität/Trustepoche
und erneute Einzelqualifikation unter dem engeren Endbudget, einschließlich eines
ununterbrochenen automatischen Pfads. Erst danach wären weitere bereits besprochene
Stufen einzeln zu beurteilen. Keine 100/1000-Paralleltests, keine öffentliche oder
produktive Freigabe aus diesem Ergebnis.
