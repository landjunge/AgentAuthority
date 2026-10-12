# A4: kontrollierte kryptografische Delegation, vorregistriertes Gate

Basis: `7f1b6121ee506fbb341d1179376f09b132ff6c06`, eigener Branch
`codex/a4-delegation-20261012`. Alle bisherigen Dateien bleiben bytegleich.
Externe Provider-/Modell-/Codex-/Grok-Sitzungsidentität bleibt UNBEKANNT.
Keine Umdeutung der früheren Hypothesen oder Resultate.

## Phase 1: genau zwei Testagenten, ein Versuch

H-A4: Im begrenzten Versuch ist die vollständige Kette A-Auftrag → B-Annahme
→ registrierte B-Prozessinstanz → unabhängig beobachteter write belegbar.
TestA und TestB erhalten verschiedene Ed25519-Schlüssel und verschiedene
unprivilegierte Gast-UIDs. Private Keys nur in rootprivatem Gastvault und
versiegelten, exklusiv übergebenen memfds; keine Archivierung. Host-CA pinnt
vor dem Versuch Registry, Quellhash und Gastboot/Namespace. Der vertraute
Rootregistrar vermittelt UNIX-SEQPACKET-Nachrichten und protokolliert
SCM_CREDENTIALS jedes tatsächlichen Senders, pidfd und Kernelstart/exec.
Dies ist eine echte Nachrichtendelegation zweier kontrollierter Programme,
kein Nachweis eines externen KI-Modells. Rootregistrar, Host-CA, Gastkernel
und kontrollierter Agentencode sind Trustanker; kompromittierte Anker und
Schlüsselweitergabe sind keine abgedeckten Sicherheitsbehauptungen.

A signiert Auftrag mit frischer Nonce, Jobdigest, Absender, Empfänger,
Delegations-ID, Run/Boot/Namespace, beiden registrierten Prozessinstanzen,
Zieldateiidentität und 5s-Gast-Monotonic-Gültigkeitsfenster. B erhält die
tatsächliche Nachricht, prüft A-Signatur und Scope und signiert deren Digest
sowie Annahme, eigene Instanz und frische Annahmenonce. Der Registrar
bezeugt Empfang/Weiterleitung/Annahme mit eigener Signatur und gibt B
anschließend das künstliche write frei. Diese Versuchssteuerung verändert
keine Produktrechte; D-012 bleibt Beobachtung/Analyse.

Unveränderter A1-Observer bekommt ausschließlich zufälligen Testdateipfad
und 12s-Fenster, keine Agentenidentitäten oder Orakelsollwerte. Separates
Controller-Orakel: Popen-PIDs, pidfds, /proc-Startticks vor/nach Handlung,
UIDs, Agentenreturn und Exit. Kernel-Lifecycle stammt aus unverändertem A2.
Unabhängiger Hostverifier prüft Ed25519 mit OpenSSL, extern gepinnte CA,
Signaturen/Digests/SCM-Sender/Kernelstart/exec/file/zeitliche Reihenfolge,
genau einen erwarteten write, kein A-write, keine zusätzliche Zuordnung.
Gehaltenes dev/inode, 16B-write und Return belegen keine Crashpersistenz.

**Gate vor Messung:** alle Signatur-, Scope-, Prozess-, Datei-, Zeit- und
Orakelprüfungen wahr; genau eine eindeutige B-Zuordnung und null falsche
Zuordnungen; alle kritischen Verlustmetriken vorhanden und null, inklusive
Entry-/Fork-entry-nmissed, Returnmisses, Perf-/Submit-/Pair-/Mapfehler sowie
kein ungeklärter Verlust gegenüber Referenz. UNBEKANNT/null ist kein null
Verlust. Die historischen Entry-/Fork-entry-nmissed sind derzeit UNBEKANNT;
Zähler-/Referenzübereinstimmung allein schließt diesen Blocker nicht.
Teilbelege getrennt von vollständigem Gate ausweisen. Bei fehlendem Gate
keine Phase 2, kein stiller Retry, keine zusätzliche Forschungsrunde.

## Ausschließlich bei bestandenem Gate: Phase 2 mit genau 100

100 getrennte kontrollierte Testidentitäten/Schlüssel, begrenzte parallele
und mehrstufige Nachrichtenketten mit separatem Orakel. Replay, fremde
Claims, Duplikate/Verluste, Ablehnung/Abbruch prüfen; PID-Reuse nur bei
tatsächlicher Messung, sonst UNBEKANNT. Durchsatz/Latenz, CPU/RAM,
vollständige/unvollständige Ketten und falsche Positive getrennt erfassen.
Nicht gestartete Phase erhält keine erfundenen Messwerte/Schlüssel/Resultate.
Stop bei100, keine1000 oder weitere Stufen.

Nur eigene bestehende isolierte Ubuntu-VM, künstliche Dateien, keine
Hostprivilegien/Installationen oder anderen Umgebungsänderungen. Daten:
Ereignisse, Callbackbytes, JSON-Speicherbytes, CPU/RSS des erfassten Prozesses;
Kernel-/GesamtVM-Kosten UNBEKANNT. Fehler/Rohdaten erhalten, fehlende Größen
UNBEKANNT. BELEGT / TEILWEISE BELEGT / UNBEKANNT / WIDERLEGT getrennt.
Nach Auswertung Keys löschen, eigene VM stoppen, additive Dateien testen,
committen und regulär nur eigenen Branch pushen; kein Merge/Ready.
