# A1 Linux — vor dem ersten Writer eingefrorener Ausführungsvertrag

Die aktuelle Nutzerfreigabe erlaubt die praktische Runde mit Root ausschließlich
in der neuen separaten VM. Original-H-A1, macOS-Ergebnisse und Linux-Preflight
bleiben unverändert. Dieser Vertrag konkretisiert den bestehenden sechs-Fälle-
Entwurf, ersetzt ihn nicht rückwirkend. Kein Autor-/Modell-/Agentennachweis.

## H-LINUX-A1 und echte Voraussetzungen

Im vorab begrenzten Versuch auf genau einem spezifizierten Linux-Kernel ordnet
ein unabhängiger Kernel-Ereigniskanal jede erfolgreiche künstliche Schreibaktion
am bezeichneten Dateiobjekt ihrer verursachenden Prozessinstanz zu; inaktive/
anders schreibende Prozesse sowie falsche Claims werden nicht zu Schreibern
dieses Objekts. Prozessinstanz, Aktion und finaler Zustand sind getrennte Aussagen.

Gemessen: neue Ubuntu24.04.5-VZ-VM, Linux6.8.0-142-generic,x86_64,2CPU/2GiB/12GiB,
Boot-SHA256 ea23c1eead5c439d96e565f0df8e5f1a6a8d6f543205b4a35842d9bdc070e805.
GastRoot CapEff000001ffffffffff/Seccomp0; gewöhnliche Writer UID501.
BCC0.29.1+ds-1ubuntu7, Header6.8.0-142.142; Audit3.1.2-2.1ubuntu0.1.
Keine Hostmounts, keine Host-Rechteänderung; eigene VM-Dateien/SSH-Schlüssel.
Ausweichimage nach unerreichbarem Archiv: offizielles Ubuntu-Cloudimage,
SHA2566a81c37564db9b1ee84e141922625e1d7c5b389b99bb3c572e0243607d5bb4d2.

## Qualifizierte Quelle und Messvertrag

Tatsächliches Laden/Anhängen erfolgreich, aber noch keine Writer-Fälle gestartet:
BCC kprobe vfs_write entry + kretprobe maxactive128 sowie sched_process_exit.
Nicht gewählte Kandidaten tatsächlich geprüft: auditctl-s erfolgreich(enabled1,
lost0), fanotify-NOTIFY/PIDFD-init erfolgreich, Tracepoint-Formatlesung erfolgreich.
Deren eigenständige Schreiberkausalität wird nicht behauptet. Kein Auditregel-
oder Permission-fanotify-Ersatzversuch; nur ausgewählte eBPF-Kette für sechs Fälle.

Entry liest unabhängig struct-file inode/superblock s_dev, aktuellen TGID/TID,
Leader-start_boottime-ns und real-parent TGID. Scope nur gehaltenes reguläres
Testobjekt (dev/inode), kein Actor-/Orakel-/Claimfilter. Return korreliert über
Kernelpid/tid; liefert tatsächliches s64-write-Return, Anzahl, monotone Kernelzeit.
Positive Bindung verlangt ret=count=16, Kernelstart>0, Boot/PID-Namespace gleich,
Starttick-Abgleich gegen unabhängig pidfd-gehaltene Orakelinstanz (max1Tick
Quantisierung), tatsächlich gleiche Datei und Intervalleinbettung. Startns sind
keine PID-Version/exec-/Agentenidentität. Keine Prompts/Buffer/Dateiinhalte/argv/env.

Verlustchecks: proCPU Entry/Return/Submit/Fehler/Overwrite/Mapfehler/Lifecycle-
Submitzähler; pending am Ende; Perf-lost-callback; eigener kretprobe nmissed.
Wichtige vorab offengelegte Grenze: BCC-Entry nutzt Perf-kprobe, dessen nmissed
ist im gewählten Zugang UNBEKANNT; tracefs-Profil zeigt nur den klassischen
Returnprobe. Es wird kein fehlender Entry-Verlustwert als0 eingetragen.
Gezählte Orakelaktionen erlauben zusätzliche Kontrolle im begrenzten Versuch;
kein Anspruch auf lückenlose allgemeine Überwachung oder Lastfestigkeit.

## Feste sechs Positionen, unabhängiges Orakel

L1 write: A schreibt Ziel; L2 idle: B untätig; L3 sibling: C nur anderes Objekt;
L4 child: Enkel schreibt, Elternprozess nicht; L5 forged: inaktiveB-PID als
gefälschter Claim, A schreibt; L6 pair: A undC nacheinander dasselbe gehaltene
Objekt. Feste Reihenfolge, genau ein Versuch pro Position, keine Wiederholung/
Ersetzung. Insgesamt5 positive Ziel-write-Aktionen; zwei reine Ziel-Negativfälle
L2/L3 getrennt zählen. L5 inaktiveB zusätzlich, kein Claim an Collector.

Pro Position frisches normales lokales Ext4-Testobjekt und Geschwister, und
zufälliger Rollen-unabhängiger Scope-Dateiname. Observer erhält nur Pfad/Objekt
und Dauer6s (5s plus1s Drain), keine Spawn-PIDs/Fallrollen/Claim-PID/Sollwerte.
RootCollector liest kein Orakel. Getrennte SSH-Kanäle: Controller kennt tatsächliche
Fork-return-PID, öffnet pidfd vor Aktion, liest /proc-Start/PPID vor/nach Aktion,
prüft Wait/PIDFD-Exit. Orakelausgabe wird nur am Host gespeichert (kein Hostmount
in VM); Collector wird vor dem Offlineabgleich beendet, Capture/Oracle getrennt
gehasht. Der kontrollierte Writer meldet nur Return/Intervall/Objekt zum
separaten Controller; diese Werte sind kein Beobachterbeleg.

Host-Output frisch, Quellcommit/Hashes vor Position1, sauberer Git-Stand; Gast-
Quellhash muss mit committed Observer übereinstimmen. Max45s Ready,10s Orakel,
15s Collection; Fehler verbrauchen Fall. Writer nach Aktion0.3s bis kontrolliertem
Exit; Child-Elternteil waits, Collector zeichnet echten Writer-Exit auf.
Finaler Zustand/Persistenz wird nicht aus write-Return/Benachrichtigung abgeleitet;
keine fsync-/Crash-/mmap-/Async-/NetworkFS-/Writev-/Truncate-/Rename-Behauptung.

## PID-Reuse und Auswertung

Nach sechs Fällen genau eine gesonderte PID-Reuse-Kontrolle, außerhalb ihres
Nenners: GastRoot-Controller wartet erste Writerinstanz vollständig aus, setzt
ns_last_pid im isolierten VM-Kernel auf altePID-1 und startet zweite Instanz.
Kein Hostkernel-/Namespace-Eingriff. Tatsächliche PID-Gleichheit und verschiedene
Kernelstartwerte müssen gemessen sein; konkurrierende PID-Vergabe ergibt
UNBEKANNT bezüglich erzwungenem Reuse, kein Retry. RootWriter dieser Kontrolle
werden nicht als gewöhnliche UID501-Fälle in die Kohorte eingerechnet.
Zusätzlich Offline-Negativtest: gleichePID/falscherStart darf nicht verbunden werden.

BELEGT nur tatsächlich vollständige Action/Instance/File/Time-Kette in diesen
Fällen. TEILWEISE BELEGT bei Teilkette; UNBEKANNT bei fehlenden Feldern/gestörter
Messung; WIDERLEGT bei vollständigem spec-konformen unabhängigen Gegenbefund.
AchseA Konformität getrennt von H-LINUX-A1 und Generalisierung. Loss-/Pair-/
Profilfehler ergeben UNBEKANNT, niemals Wirkungsfreiheit. Korrekt/falsch/unklar
mit Aktionsnenner, Negativfälle separat; null Messung keine0%-Fehlerrate.

Messung: Events und Callback-Rohbytes; gespeicherte JSONbytes separat; Observer-
CPUuser/system samt BCCcompile/PeakRSS, nicht Kernel-/GesamtVM-Overhead.
Fehlende Kernelkosten und Entry-nmissed explizit UNBEKANNT. Unitfixtures sind
keine Kernelbelege; passende Tests und gesamte bestehende Suite zweimal.
Keine historischen Änderungen/Ready/Merge; nur eigener Forschungsbranch.
