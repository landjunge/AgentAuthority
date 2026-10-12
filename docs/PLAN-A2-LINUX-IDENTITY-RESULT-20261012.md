# A2 Linux: kontrollierte Testidentität → Instanz → Schreibhandlung

**BELEGT im ausgeführten Laborversuch:** Eine registrierte und frisch
kryptografisch authentisierte Testidentität wurde ihrer konkreten gestarteten
Prozessinstanz und einer unabhängig erfassten write-Handlung zugeordnet.
TestAlpha und TestBeta sind getrennt nachgewiesen. Codex, Grok, Provider, Modell,
Person oder Gespräch sind **UNBEKANNT**; keine solche Authentisierung behauptet.

Basis `ec82f2ae5e0168ef41abe13e9b0cf495d20a0293`, eigener Branch
`codex/a2-linux-identity-20261012`. Spec `1800b18`, öffentlicher Trust-/Quellpin
`6af3c49`; unveränderter echter Laufquellcommit ist in pre-run-lock.json und
cohort.json vollständig enthalten (`5d763c8`). Acht Positionen jeweils einmal,
keine Ausführungsfehler/Retry/Ersatz. Historische A1- und Mac-A2-Ergebnisse und
die ursprüngliche Mach-Sender-Hypothese bleiben unverändert und unbewertet.

## Praktische Umgebung und Vertrauensbasis

Die bestehende separate Forschungs-VM wurde ausdrücklich beauftragt gestartet:
Ubuntu24.04.5, Linux6.8.0-142-generic, x86_64,2CPU/2GiB/12GiB. Eigener Lima-
Speicher, keine Hostmounts/Agentweiterleitung, kein neuer Host-sudo/Helper oder
Hostinstallation. Root nur für Starter und eBPF im eigenen Gast. Crypto41.0.7
bereits vorhanden; Host-OpenSSL3.6.2 ebenfalls vorhanden. Colima/andere Projekte
und Prozesse nicht verändert. VM nach Export, Key-Löschung und Entladen sauber
gestoppt.404 Basisdateien einschließlich A1-Code/Daten bytegleich.

Neue lokale Labor-CA am Host signierte das **vor Fall1 gepinnte** Enrollment:
Publickeys von TestAlpha/TestBeta, getrennte UIDs61001/61002, Starterpublickey,
Run/Boot/PID-Namespace und Programmeinstiegshash. Das ist ein bewusst selbst
erzeugter **Testidentitätsraum**, keine reale Organisations-/Providerbeglaubigung.
Root-Starter und Linux-Kernel sind vertrauenswürdig vorausgesetzt; kein
Schutzbeweis gegen kompromittierten Root, Hypervisor oder Host/CA. Die Quelle
ist projektintern unabhängig vom Agentenclaim, kein externes Drittparteiaudit.

## Tatsächlich implementierte Kette

1. Host-CA-signiertes Register statt vom Actor mitgebrachter frei gewählter Keys.
2. Root startet Worker per fork/exec, leerer Gruppenliste, eigener UID und
no_new_privs. Nur eigener versiegelter memfd mit Testkey wird übergeben.
Rootspeicher wird durch exec ersetzt; kein Starter-/CA-Key an Worker übergeben.
Worker ist nicht dumpbar; Vault root0700/Dateien0600.
3. Additiver Lifecycle-BPF liefert exakten Kernelstart (wake_up_new_task),
erfolgreiche Exec-Generation/Zeit und Exit. Keine Tick-Approximation als neue
Instanzgleichheit; pidfd wird über Authentisierung/Lebenszyklus gehalten.
4. Frische domain-/Run-/Boot-/Instanz-/Datei-/Nonce-/Zeit-Challenge. Actor
signiert mit Ed25519. Empfänger nutzt SO_PEERCRED und **SCM_CREDENTIALS pro
Nachricht**: der Verbindungsöffner eines geerbten Sockets kann vom späteren
Nachrichtensender abweichen. Die gemessene Kindkontrolle zeigt genau dies.
5. Starter prüft Schlüsselbesitz und registrierten lebenden Start/Exec/UID,
signiert öffentlich nachprüfbares Receipt. Claim, Credential-Keyidentität und
frisch prozessgebundene Authentisierung sind getrennte Felder.
6. Unveränderter A1-eBPF-Observer erfasst Dateiobjekt, tatsächliches write-Return,
TGID/Kernelstart und Zeit ohne Identitäts-/Orakeldaten als Eingabe. Offline-
Join verlangt gleiche Boot/Namespace/Startinstanz, gültige Exec-Generation,
signierten File-/Zeit-Scope sowie vollständige Beobachtung im Messvertrag.

Nach Beendigung der Aufnahme verifizierte ein separates Host-OpenSSL die CA-,
Starter- und Actor-Signaturen erneut:11 Actor-Signaturen und11 Starterreceipts,
keine bloße Übernahme eines vom Gast behaupteten Verify-Flags. Ein mathematisch
gültiger alter Proof bleibt beim Replay unfresh. Signatur bestätigt Key-/
Nachrichtenherkunft; die Wahrheit einer mit signierten falschen Behauptung
folgt daraus nicht. Kein Receipt allein beweist die Dateischreibhandlung.

## Acht tatsächlich ausgeführte Fälle

| Fall | Behauptet / kryptografisches Credential | Handelnde Prozess-/Agentenbindung | Befund |
| --- | --- | --- | --- |
|1 Alpha | Alpha / frisches Alpha | Writer1216, Start1305735137762ns, AuthAlpha | Kette BELEGT |
|2 Beta | Beta / frisches Beta | Writer1231, Start1319294095880ns, AuthBeta | Kette BELEGT |
|3 falscher Claim | Beta / frisches Alpha | Writer1246 bleibt AuthAlpha; keine Betaübernahme | tatsächliche Alphakette BELEGT, Beta-Claim nicht übernommen |
|4 Kind/Socket-Key-Erbe | Alpha / frischer Alpha-Keybesitz | SO_PEERCRED1261, SCM-Sender und Writer1262; Kindstart1350570657175ns, nicht registriert | Wirkung BELEGT, handelnde authentisierte Testidentität UNBEKANNT |
|5 Exec-Wechsel | Alpha vor exec authentisiert | PID1277/Start unverändert, Exec-Generation1→2 vor Write | alte Bindung nicht übertragen; Identitätskette UNBEKANNT |
|6 PID-Reuse | beide Proofs kryptografisch Alpha | PID1292 tatsächlich wiedervergeben; Start1381363801782→1381661997003ns, alte pidfd beendet | alte Bindung nicht übertragen; neue Identitätskette UNBEKANNT |
|7 fremde Übernahme | Beta behauptet Alpha, signiert als Beta | fremder Alpha-FD-Zugriff EACCES13 im kontrollierten Worker; Writer1308 bleibt AuthBeta | Betakette BELEGT; keine Alphaübernahme |
|8 Public-Proof-Replay | alter gültiger Alpha-Proof durch Beta-Prozess | neue Nonce/Instanz nicht passend; Writer1324 erfasst | Signatur mathematisch gültig, keine frische Authentisierung; Kette UNBEKANNT |

Vier vollständige Testidentitäts-/Wirkungsketten, vier bewusst ungebundene
Identitätsfälle, alle acht tatsächlichen write-Handlungen unabhängig BELEGT.
Null falsche fremde Identitätsübernahmen in diesen Fällen. Negative UNKNOWNs
werden nicht als verfehlte Erfassung oder positive Identität umetikettiert.
Alle Negativworker durften die künstliche Datei trotzdem schreiben: keine
operative ALLOW/DENY-Folge. Die korrekte Nichtübernahme ist Konformität, keine
universelle Angriffssicherheitsgarantie. Kein A1-Sechs-Fälle-Rerun oder Modelllauf.

## Ground Truth, Verlust und Ressourcen

Controller-Spawns, bereitgestellter Testkey/UID, Wait-/Exit-Resultate und
kontrollierte Actoraktionen getrennt von A1-Capture. Keine Orakeldatei im Gast;
Hostausgabe, Capture und Trial separat gehasht. Starter ist gleichzeitig
vertrauenswürdiger Registrar: dies ist eine explizite Vertrauensbasis, kein
von Root unabhängiges Orakel. Kernel-Writes und Lifecycle-Metadaten sind die
unabhängigen OS-Kanäle. Auf fork-Records ist UID der emittierende Parent-Kontext,
nicht automatisch bereits die spätere Worker-UID; Exec/Credentials liefern diese.

16 A1-Records/1216 Callback-Rohbytes und36 Lifecycle-Records/1584 Rohbytes.
Bekannte Perf-/Submit-/Map-/Returnverlustindikatoren0; nicht sämtliche IPC-/
Kernelbytes gemessen. A1-Entry-nmissed und Lifecycle-Fork-Entry-nmissed bleiben
**UNBEKANNT**, keine Vollständigkeits-/Lastgarantie. Fehlendes Lifecycle-/
Signatur-/Scope-/Instanzsignal ergibt UNKNOWN, keinen Ersatz durch Selbst-PID.

A1-Observer CPUuser18.145035s/system1.965618s, PeakRSSmax177598464B;
Starter7.902175s/1.692907s, PeakRSSmax165003264B. Jeweils einschließlich
Kompilierung im Prozess; Worker-/Kernel-/GesamtVM-Kosten UNBEKANNT. Archivbytes
und Hashes separat im artifact-index.json. Kein Payload/Inhalt/Prompt/Modelltext
oder Privatekey archiviert. Private Vault und Host-CA-Privatefile nach Messung
gelöscht; sichere RAM-Zeroisierung nicht behauptet. Publicproof dauerhaft prüfbar.

## Tests, echter Fehlschlag und Bewertung

14 neue Tests mit realen temporären OpenSSL-Signaturen und konservativen
Offline-Joins, keine Fixtures als Kernelbeweise. Erste Gesamtsuite619PASS.
Zweite Suite619 Tests/4FAIL: währenddessen erstellter Commit änderte HEAD,
vier bestehende P7-Pins stoppten korrekt mit source_head_mismatch. Das war ein
vermeidbarer Verifikationsablauffehler, bleibt samt Tests/Logs/Hashes erhalten.
Keine Tests angepasst, kein Fehler wegklassifiziert. Nach fixes HEAD zwei
vollständige Läufe3/4 jeweils619PASS,0 errors/failures/skips, fünf unveränderte
historische Abwahlen. Source während acht VM-Fällen durchgehend unverändert.
Ruff Check/Format, Mypy32/Bandit bestehender Core PASS; native Compile/Verifier/
Attach, Ed25519 und SCM-/PID-Reuse/Exec-Kontrollen separat tatsächlich gemessen.
Kein neuer Remote-CI-Lauf; lokale Tests sind keine vorgespiegelten CI-Checks.

AchseA **PASS** für den eingefrorenen Testumfang; H-A2-LINUX **SUPPORTED** für
kontrollierte, vom vertrauenswürdigen Starter registrierte Testidentitäten.
BELEGT: ausgeführte vollständige Ketten und enge Rückweisungsbefunde.
Generalisierung, reale Codex/Grok-Identität, mehr als ein Agent pro Prozess,
Root-/Keykompromittierung, externe Identitätsanbieter, dauerhafte Persistenz,
Threads/async/mmap/andere Kernel/Dateisysteme bleiben **UNBEKANNT**.

Offener Übergang zu echten Agenten: unabhängig vertrauenswürdiges Enrollment,
Provenienz und Schlüsselverwaltung für deren tatsächliche Identitätsdomäne,
einschließlich Definition, was eine logische Instanz ist. Ein lokaler Testkey,
CLI-Name, Providerlabel, Signatur oder Kernel-PID ersetzt dies nicht. Kein
technologischer Vorsprung oder Produktions-/historische Paketabnahme behauptet.
Die ursprüngliche Mac-A2-Mach-Frage wird hier nicht als bestanden ausgegeben.
D-012 bleibt Beobachtung/Analyse; keine Produktrechte oder operative Steuerung.

Reproduktion/Review: neue Quellen unter `research/a2_linux/`, eingefrorene Spec
und Trustpins unter `docs/PLAN-A2-LINUX-IDENTITY-*`, public enrollment, receipts,
Proofs, Kernelcaptures/Orakel, Qualitäts-/Fehlerbelege und Hashindex unter
`docs/a2-linux-runs/2026-10-12/`. Archiv kann ohne private Keys unabhängig
nachverifiziert werden. Neue Wiederholung benötigt frisches Boot-/Run-/Key-
Enrollment und neuen Datenordner, überschreibt keine alte Aufnahme.
Primärverträge: [Ed25519](https://www.rfc-editor.org/rfc/rfc8032),
[SPKI](https://www.rfc-editor.org/rfc/rfc8410),
[Linux SCM-Credentials](https://github.com/torvalds/linux/blob/e8f897f4afef0031fe618a8e94127a0934896aba/net/core/scm.c).
Verträge ersetzen keine Messung; Archiv enthält getrennte Sources/Hashes.
Keine neue Phase gestartet, kein Ready/Merge. Runde nach regulärem Push beendet.
