# Linux-A1 — vorregistrierbarer Protokollentwurf, NICHT AUSGEFÜHRT

Eigenständiger Anschlussentwurf zum reinen Umgebungsvorcheck. Keine Freigabe zur
Ausführung, Installation oder Rechteänderung. Original-H-A1/macOS-Ergebnisse
bleiben unverändert. Dieser Entwurf ist noch keine vollständig versiegelte
Registrierung: konkrete zulässige Quelle und Implementierungs-/Quellenhash fehlen.

## Fragestellung und bedingte Hypothese

H-LINUX-A1: Im vorab begrenzten Versuch auf genau einem spezifizierten Linux-
Kernel ordnet ein unabhängiger Kernel-Ereigniskanal jede erfolgreiche künstliche
Schreibaktion am bezeichneten Dateiobjekt ihrer verursachenden Prozessinstanz zu;
inaktive/anders schreibende Prozesse sowie falsche Claims werden nicht zu
Schreibern dieses Objekts. Prozessinstanz, Aktion und finaler Zustand sind
getrennte Aussagen. Agenten-/Autor-/Modellidentität bleibt UNBEKANNT.

Vor dem Start in einem neuen Spec-Commit fixieren: Host/Kernel/Distribution,
aktuelle Rechte/LSM/seccomp, Quelle und exakter Ereignistyp, Quellcode-/Binärhash,
Namespace- und Bootbindung, Dateisystem, Uhr/Präzision, Rückgabe-/Fehlersemantik,
Verlustindikatoren, Filter und Grenzen. Ohne diese Werte keine Registrierung,
keine Sechs-Fälle-Ausführung. Kein weiterer A2-/Agentenidentitätsversuch daraus.

## Quellen-Gate und kleinster möglicher Umfang

Im Preflight ist **kein qualifizierter zugänglicher Kanal ausgewählt**. Ein
Metadatensnapshot, inotify, Syscall-entry mit numerischem FD oder Kontrollwissen
sind keine Ersatzquelle. Es gibt keine automatische privilegierte Alternative.

fanotify-NOTIFY wäre der kleinere Kandidat für **Änderungsbenachrichtigung zu
Prozessinstanz**: konkrete einzelne Inode-Marks, `FAN_MODIFY`, verfügbarer
`FAN_REPORT_PIDFD`, Kernel-Datei-FD oder unabhängige Objekt-FID. Keine Mount-/
Filesystem-Marks, Permission-Klassen, Antworten oder globalen unbegrenzten Queues.
Es benötigt für fremde Prozesskennungen die entsprechenden bestehenden,
ausdrücklich erlaubten Rechte. Im unprivilegierten Modus bleibt fremde PID0 und
PIDFD fehlt. Keine Hostrechte durch User-Namespace oder Containerprivilegien.

Auch bei erlaubtem Zugriff reicht fanotify für die **strenge Einzeloperation**
nicht automatisch: Ereignisse können zusammenfallen, enthalten im geprüften
Vertrag keinen Kernel-Aktionszeitstempel oder erfolgreichen Byte-Rückgabewert,
und der Prozess kann vor PIDFD-Auslieferung sterben. Ein `FAN_CLOSE_WRITE` allein
ist kein Schreibbeweis. Fehlende Prozessinstanz/Granularität ergibt UNBEKANNT;
die positive H-LINUX-A1 wird nicht zu einer schwächeren Hypothese umgeschrieben.

Für den strengen Anspruch wäre ein bereits erlaubter, separat spezifizierter
eBPF-/Tracing-Kanal mit konkretem `struct file` und verursachendem `current` am
validierten VFS-Schreibpfad sowie Entry/Return-Korrelation geeigneter zu prüfen.
Minimal nur `write` auf regulärem, lokalem, vorab identifiziertem Dateiobjekt;
kein mmap, async/io_uring, Netzwerk-FS, Pwrite-/Writev-/Truncate-/Rename-Scope.
Kernel-/ABI-spezifische Hooks, positive/partielle/fehlgeschlagene Rückgaben und
Kernel-Startzeitfelder vorab validieren. Nur gezielte eigene Versuchstasks und
Dateiobjekte filtern; keine Pfade/Benutzerdaten/Buffer, keine fremden Tasks
exportieren. BPF-Programm laden/anhängen ist außerhalb des aktuellen Auftrags.

Audit ist nur bei bereits erlaubtem passendem Kernelstream ein Kandidat: pro
Syscall serial/timestamp, kernel-origin record types, Rückgabe und Dateiobjekt
zusammenführen. Bereits existierende Regelabdeckung, Lifecycle-/Instanzbindung
und Verlust-/Netlinkprüfungen sind zwingend. AUDIT_USER-Selbstmeldungen sind
kein Kernel-Schreibbeleg; PID/serial allein sind keine Prozessinstanz. Keine
Auditregeln oder auditd für diesen Entwurf installieren/aktivieren.

## Getrennte Ground Truth und Ablauf

Nur frisches privates temporäres Verzeichnis auf lokalem Test-FS, kein Host-/
Repo-/Produktmount. Bereits geöffnete Objekt-FDs halten Inodeidentität gegen
Wiederverwendung; vorab dev/inode und, falls benötigt, Mount-ID/FID festhalten.
Existierendes leeres Ziel mit einer kleinen festen künstlichen Sequenz ändern;
Dateierzeugung separat benennen, nicht aus Schreibereignis ableiten.

Ein Controller startet gewöhnliche kleine Writer A/B/C und hält sie bis zur
Beobachterauswertung lebend. Sein separates Orakel protokolliert Spawn-/Wait-
Resultate, eigene pidfd-Bindung, Namespace/Boot, bekannte Prozessinstanz und
Aktionsergebnis. Kernelstartzeit aus `/proc/<pid>/stat` gegen gehaltene pidfd,
Lebendigkeit und Namespace prüfen; keine PID-Gleichheit trotz Wiederverwendung.
Dieser kontrollierte Soll-Datensatz ist Ground Truth, **niemals Beobachterquelle**.

Orakeldatei liegt außerhalb des Beobachterzugriffs; der Beobachter erhält nur
Zielobjekt, Scope-/Zeitgrenzen und Quelle. Keine Spawn-PIDs, Rollen, Fallplan,
Claim-PID oder Writer-Logs in den Collector. Scorer erhält Claims/Orakel erst,
nachdem Beobachterausgabe abgeschlossen und gehasht ist. Den gefälschten Claim
nimmt nur eine nachgelagerte Analyseschicht entgegen; er ist kein Prozesssignal.
Rollenreihenfolge und Seeds vorregistrieren, gegenüber Collector verblinden;
der synthetische Controller gehört zur Vertrauensbasis des Orakels und ist
kein unabhängiger Beleg einer logischen Agentenidentität.

Pro Fall eine frische Aufnahme und eine vorgegebene erfolgreiche `write`-Aktion
je wirklichem Schreiber. Collector maximal 5 Sekunden, danach 1 Sekunde Drain;
Writer halten maximal 10 Sekunden bis zur Auswertung. No retries/replacements.
Timeout/Startfehler verbrauchen die Position und bleiben unbewertet/UNBEKANNT.
Separate finale Größen-/Hashkontrolle durch Controller, nie Inhalt archivieren.
Ein Return>0 belegt angenommene Bytes, keine dauerhafte Persistenz; fsync und
Persistenzprüfung wären ein gesonderter ausdrücklich definierter Anspruch.

| Fester Fall | Soll-Ground-Truth | Vorab erwartete Aussage |
| --- | --- | --- |
| L1 A schreibt Ziel | genau A, eine write-Aktion | A-Instanz + Ziel + Aktion unabhängig gebunden |
| L2 B bleibt untätig | kein Zielwriter | kein positiver B-Beleg; nicht allgemeine Wirkungsfreiheit |
| L3 C schreibt andere Datei | C, nur Geschwisterobjekt | kein Zielbeleg für C; Scopeabwesenheit getrennt von Vollständigkeit |
| L4 Kind schreibt Ziel | Kindinstanz, Elternteil schreibt nicht | Kind belegt; Parent/PID-Abstammung allein genügt nicht |
| L5 gefälschte PID | A schreibt, Claim nennt inaktiven B | Kernelbindung A; Claim B nicht übernommen |
| L6 A dann C am selben Objekt | A und C, getrennte Aktionen/Instanzen | beide Objektbindungen, Reihenfolge nur bei tragfähigem Zeit-/Ordnungsbeleg |

Zusätzlich innerhalb des Messvertrags: Collector-ready vor erster Aktion,
drained Ende, korrekte Objektidentität, vollständige Entry/Return-Paare,
Exit-/Lifecyclekontrollen und vom Collector unabhängiges Nicht-Schreiber-Orakel.
Kein PID-Reuse-, mmap-, Agenten-/Mehrhost- oder Lastverlustexperiment einschieben.

## Messung und vorab festgelegte Auswertung

Minimal pro Record: Quelle/Version, Boot-/Namespacebindung, TGID/TID und
Kernel-Instanzstart oder valide kausale pidfd, Dateiobjekt, Aktion/Rückgabe,
Kerneluhr oder ehrlich begrenztes Empfangsintervall, Sequenz/Drop-Zähler und
Erfassungsfenster. Startzeit, PIDFD und Namespace-PID nicht gleichsetzen.
Fehlende Teile null/UNBEKANNT. Dateiinhalt, argv/env, Prompts/Antworten/Secrets
werden nicht erfasst. Datenminimierung separat von Belegqualität bewerten.

Recordanzahl, erfolgreiche Aktionen laut Orakel, Rohbytes vor Minimierung,
gespeicherte Bytes, Collector-CPU user/system und Peak-RSS getrennt; Compiler/
Controller/CI-Overhead getrennt oder UNBEKANNT. Keine 1:1 Record-/Syscall-
Annahme bei zusammengefassten Events. Pro Aktionsnenner: korrekt, falsch,
unklar; zusätzlich false-positive Ziel-/Claim-/Kind-Zuordnung. L2/L3 als
Negativfälle haben eigenen Nenner. Ohne ausgeführte Fälle keine Rate.

Overflow/FAN_Q_OVERFLOW, FAN_NOPIDFD/FAN_EPIDFD, BPF-reserve-Fehler/fehlende
Paare, unbekannte Lifecycle-/Uhr-/Namespace-/Dateibindung oder unvollständige
Auditserie machen die betroffenen Zuordnungen UNBEKANNT; keine verlorenen
Events als Nichtschreiben. Dropindikator0 allein beweist keine universelle
Vollständigkeit. Ausgeführter vollständiger spec-konformer Gegenfall kann
H-LINUX-A1 WIDERLEGEN; gestörter Messvertrag ergibt INCONCLUSIVE.

Technische Abnahme separat: erlaubte Quelle/Scope, alle sechs Positionen,
getrenntes Orakel, feste Hashes, konservative Fehlerbehandlung. Hypothese
SUPPORTED nur bei vollständigem unabhängigen Nachweis aller geforderten Fälle,
sonst PARTIALLY SUPPORTED/INCONCLUSIVE/REFUTED nach Forschungsmethode. Kein
Security-/Agentenidentitätsbeweis. Generalisierung auf übrige Linux-Kernel,
andere Schreibpfade/Dateisysteme oder macOS bleibt UNBEKANNT.

STOP bei Rechteänderung, produktivem Zugriff, notwendiger Installation ohne
neuen Auftrag, fehlender Quelle/Instanzbindung, Orakelleck, unerlaubten Marks/
Hooks, verlorenen Belegen oder historischen Änderungen. Nur eigene Aufnahme
beenden; keine produktiven Prozesse steuern. Jetzt endet ausschließlich der
Preflight: **alle sechs Fälle NICHT AUSGEFÜHRT**.
