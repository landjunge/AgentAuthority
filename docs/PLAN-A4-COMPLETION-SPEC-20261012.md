# A4-Fortsetzung: Messkontrollen, ein neuer Gateversuch, maximal100

Aktueller Nutzerauftrag; Basis88087a609128149aad752ad9bb52959009843e1f.
Eigener Branch codex/a4-loss-controls-20261012. Alle553 Basisdateien einschließlich
der alten A4-Spec und Rohdaten bleiben bytegleich. Kein historisches Gate geändert.
Dies setzt ausschließlich A4 mit zusätzlicher, vorher gepinnter Instrumentierung
fort. Kein neues Forschungsthema, keine Provider-/Modellsitzungsbeglaubigung.

## Tatsächlich geprüfte technische Grundlage

BCC0.29.1 attach_kprobe setzt maxactive0; libbpf.c versucht damit perf-PMU.
Bei maxactive>0 wird der vorhandene klassische tracefs-Weg verwendet. Für
Entry-Attachmenttype0 erzeugt er weiterhin p:, keine Returnprobe. Dieser
Low-Level-Anschluss wurde in der eigenen VM an vfs_write/wake_up_new_task
praktisch geprüft: beide klassischen Namen/Profile vorhanden, anschließend
entfernt. Direkte manuelle Events mit Fetchargs lieferten EINVAL; keine solche
Quelle als verfügbar verbucht. Keine Writer-/Agentenversuche dabei.

Neue additive Kopien, alte Quellen unberührt: Write-Entry und Fork-Entry
klassisch anschließen; jeden erwarteten Namen exakt in kprobe_profile lesen.
Fehlende Zeile/Lesefehler bleibt null/UNBEKANNT. Returnprofil weiterhin separat.
Lifecycle-Mapupdate-Return und Probe-Read-/Invalid-Instancefehler zählen;
Observer zählt Seen-Update-/Read-/Deletefehler. Alle Programme zusätzlich per
/proc/self/fdinfo auf tatsächlich vorhandene recursion_misses prüfen; fehlendes
Feld bleibt UNBEKANNT. Keine bpf_stats- oder andere Kernelkonfiguration ändern.
Maps512 für Lifecycle, begrenzte Objekt-/Pendingmaps für die feste Kohorte.

Quellen: BCC v0.29.1 src/cc/libbpf.c und installierte Pythonimplementation;
Linux6.8 kernel/trace/bpf_trace.c (trace_call_bpf), kernel/bpf/syscall.c
(bpf_prog_show_fdinfo); docs.kernel.org/trace/kprobetrace.html (Profilspalten).
Klassische Misses, BPF-Rekursion, Map-/Read-/Perf-/Submitfehler und Referenz
müssen gemeinsam geprüft werden; kein einzelner0-Zähler als Vollständigkeit.

## Eingefrorenes erneutes Zwei-Agenten-Gate

Genau ein neuer TestA→TestB-Auftrag mit den bisherigen24 Komponentenprüfungen:
getrennte Keys/UIDs, frische Nonces/Digests/IDs/5s-Fenster, Besitznachweise,
SCM_CREDENTIALS, signierte tatsächliche Annahme, Kernelstart/Exec/pidfd,
gehaltenes dev/inode, ein unabhängiger16B-VFS-write und separates Controller-
Orakel. A1-Kanal erhält ausschließlich Testobjekt und Dauer, keine Rollen/PIDs.

BELEGT/Gate nur wenn alle24 plus Profil-/Programmpräsenz wahr, alle kritischen
Zähler als gemessene Integer0 vorliegen, genau2 vollständige Referenz-
Fork/Exec/Exit-Instanzen und genau1 Zielwrite ohne Duplikate/fehlenden Return
übereinstimmen. Keine falsche Zuordnung. Jede kritische Lücke/null/Nichtnull
blockiert. Zähler decken den festen registrierten Zeitraum/Kanal ab, keine
universelle macOS-/mmap-/Async-/Crashpersistenz-/Providerbehauptung.
Neue Quellpins und öffentliche CA vor diesem einen Agentenversuch committen.
Bei Fehler keine Wiederholung dieses Gateversuchs; technische Korrekturen
können geprüft/dokumentiert werden, ersetzen seinen echten Befund nicht.

## Nur nach BELEGT: exakt100 kontrollierte Testagenten

Getrennte Ed25519-Keys/UIDs und registrierte Prozesse für Agent000..Agent099.
Binärbaum (Parent(i)=floor((i-1)/2)) mit99 tatsächlichen signierten Delegationen;
Parentbindungen/Digests an vorherige Annahme und Handlung knüpfen. Die
Frontier parallel abarbeiten, neue Nonces/IDs und eindeutig separate künstliche
Zielobjekte je Empfänger. Agent000 schreibt keinen Zieljob;99 Empfänger
schreiben je16B. Genau100 Agenten, keine zusätzliche Kohorte/Skalierungsstufe.

Replay desselben echten Auftrags und Fremdclaim mit tatsächlicher Signatur
eines anderen registrierten Testagenten als getrennte zusätzliche Nachrichten
innerhalb derselben Kohorte prüfen. Keine falsche vollständige Wirkungskette.
Verweigerte/unterbrochene Delegation innerhalb derselben Kohorte gesondert
protokollieren, keine fehlende Handlung als erfolgreicher Job. Keine künstlich
erzeugten Kernelverluste als echte Messung; bekannte Misses/Perfverluste und
Referenzfehlmengen/Duplikate tatsächlich zählen. PID-Reuse nur bei Messung,
sonst UNBEKANNT. Höchstens eine technische Korrektur, keine Endlosschleife.

Durchsatz/Wallzeit und Ausgabe→Annahme/Write-Latenzen mit Gastmonotonicuhren,
Rohereignisse/Bytes, gespeicherte Bytes, Registrar/Observer-/Child-CPU getrennt.
RAM: gemessene eigene Prozesswerte und ggf. explizit benannte Summe/Snapshot,
keine RSS-Summe als physischer VM-Overhead. Nicht erfasste Werte UNBEKANNT.
Scope/Signaturen/Start/Exec/Object/Time und Mengenabgleich offline unabhängig
mit OpenSSL gegen vorher gepinnte Registry/Referenz prüfen.

Trustanker weiterhin Host/CA, Gastkernel und Rootregistrar; Testagenten keine
extern authentisierten Codex/Grok- oder Modellidentitäten. D-012 unverändert,
Versuchssteuerung keine Produktrechtevergabe. Nur bestehende eigene VM,
keine Hostprivilegien/Installation/produktiven oder anderen Projekteingriffe.
Schlüssel nicht archivieren, nach Versuch löschen, eigene VM stoppen,
additive Belege/Tests/Bericht committen und nur eigenen Branch regulär pushen.
Kein Merge/Ready; nach Abschluss stop, maximal100.
