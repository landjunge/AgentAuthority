# A1-Linux: ausdrücklich autorisierte praktische Folgerunde

Basis ad72abf97880083d0aa1cc22545a13002b10a942, eigener Branch
codex/a1-linux-experiment-20261012. Der aktuelle Nutzerauftrag autorisiert
eine neue isolierte Linux-VM, Kernelrechte ausschließlich darin, Installation
von Forschungswerkzeugen und die sechs bereits beschriebenen Writer-Fälle.
Die alte Preflight-Grenze verbietet nicht diese neue ausdrückliche Runde.
Historische A1-/macOS-/Linux-Preflight-Ergebnisse bleiben unverändert.

Vorhandenes Lima2.1.1, macOS VZ. Eigener LIMA_HOME
/Users/landjunge/.local/share/agent-authority-a1-linux-vm, Instanz a1-research.
2 CPUs, 2GiB RAM,12GiB virtuelle Disk, plain/mount-none/containerd-none,
keine Hostlaufwerke oder privaten SSH-Public-Keys übernommen. Normale
Hostbenutzerrechte501; kein Host-sudo, kein neuer Helper/Entitlement/FDA/TCC,
keine Colima-/bestehenden VM-/Prozessänderungen. Sollte eine zusätzliche
Hostfreigabe erforderlich werden: konkret anfordern und vor ihr pausieren.
VM-Erstellung und ihre normalen Benutzerdateien sind ausdrücklich beauftragt.

Im Gast Root ausschließlich für Paketinstallation und begrenzte unabhängige
Kernelbeobachtung. Keine produktiven Workloads/Dateien, Modelle oder Prompts.
Quellenprüfungen für eBPF, Audit, fanotify, Tracing. Sechs-Fälle-Ausführung
erst nach tatsächlicher Quellenqualifikation und konkreter Spec/Quellfreeze.
Keine reine Planung als Ersatz; Fehlschläge und Blocker bleiben Messdaten.

Instanzkey mindestens Bootbindung+Kernel-TGID+Kernel-Prozessstart; numerische
PID nicht allein. Gehaltenes Dateiobjekt dev/inode; tatsächliches Schreibreturn,
Kernelzeit, Entry/Return und Verlustzähler. Unabhängiger Collector erhält
keine Writer-PIDs/Fallrollen/Orakel-/Claimdaten. Orakel auf dem Host, nicht in
der VM gespeichert: der privilegierte Gast-Collector kann es nicht lesen.
Ground Truth stammt aus getrenntem Controller, keine Agentenauthentisierung.
PID-Reuse mindestens Instanzschlüssel und negative Wiederverwendungsprüfung;
tatsächlich erzwungene Wiederverwendung nur transparent als Zusatzkontrolle,
nicht als Bestandteil der sechs Originalfälle umetikettieren.

Reguläre getrennte Spec-/Code-/Ergebniscommits und Pushes nur eigener Branch,
kein Force/Ready/Merge. Alle370 Basisdateien bytegleich erhalten.
