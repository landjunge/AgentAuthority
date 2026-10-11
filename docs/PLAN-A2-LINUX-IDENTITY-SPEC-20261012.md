# A2 Linux — praktischer Testidentitäts-/Start-/Wirkungsversuch

Aktueller Nutzerauftrag autorisiert diese neue praktische Linux-A2-Runde,
isolierte vorhandene Forschungs-VM und ihre Kernelrechte, neue Code-/Test-/
Dokumentdateien, Commit/Push nur eigener Branch. Basis ec82f2a, Branch
codex/a2-linux-identity-20261012. Keine Änderung der alten Mac-A2-Hypothese,
A1-Ergebnisse, ABC-Plan, R0/B1/B2/C1/P7/P8 oder laufenden fremden Projekte.

H-A2-LINUX: In dieser isolierten Linux6.8.0-142-VM kann eine frische, vom
vertrauenswürdigen Starter registrierte und kryptografisch authentisierte
**kontrollierte Testidentität** an genau eine Prozessinstanz/Exec-Generation
gebunden und einer unabhängig erfassten write-Aktion zugeordnet werden.
Claims, Kind-/neue Prozesse, neue Exec-Generationen und wiederverwendete PIDs
übernehmen kein altes Binding. Schlüsselbesitz allein ist keine Instanzbindung.
Kein unabhängiger Nachweis für Codex/Grok/Provider/Modell/Person/Gespräch.

## Festgelegte Vertrauensbasis und Verfahren

Neue temporäre Host-CA (Ed25519, vorhandenes OpenSSL3, keine Hostinstallation),
Privatkey nur im neuen privaten temporären Ordner, nie ins Repo/Gast/Archiv.
GastRoot erstellt zwei Testkeypaare TestAlpha/TestBeta, getrennte numerische
UIDs61001/61002 und Starterkey; private Vault root0700/Dateien0600.
Öffentliches Enrollment enthält Testlabels/Publickeys/UIDs, Starterpublickey,
Boot/Runbindung und vorab gehashten Programmeinstieg. Host-CA signiert es und
pinnt ihren Publickey vor den Messfällen. Keine selbstgewählten Publickeys aus
Agentenclaims, keine Root-/CA-Privatkeys im Agenten. Rootvertrauen ausdrücklich
Teil des Versuchs, keine TPM-/SecureBoot-/Anti-Root-/Remoteattestation behauptet.

Starter startet per fork/exec gewöhnliche unprivilegierte Testworker, leere
Groups, eigene UID, no_new_privs, nicht dumpbar, nur eigener geerbter versiegelter
memfd mit seinem Testprivatekey. Exec vernichtet kopierten Rootspeicher; keine
Launcherprivatkeys/anderen Actor-FDs übergeben. UID ist Zusatzmerkmal, keine
kryptografische Identität. Keys werden nach Messung gelöscht, Publicproof bleibt.

Additiver Kernel-Lifecyclemonitor: wake_up_new_task liefert exakten Kernelstart
des vom Starter erzeugten Tasks; sched_process_exec liefert Exec-Zeit/Generation,
sched_process_exit liefert Ende. Scope nur Starterforks/deren Nachkommen in der
neuen VM. Keine Namens-/Modell-/Prompt-/argv-/Umgebungsdaten. Das historische
A1-observer.py bleibt bytegleich und beobachtet nur das künstliche Dateiobjekt.

Frische UNIX-SEQPACKET-Challenge, SO_PEERCRED plus **SCM_CREDENTIALS pro Nachricht**,
gehaltene pidfd, Boot/PID-Namespace/Kernelstart/Exec-Generation/UID. SO_PEERCRED
allein wäre bei geerbtem Socket kein Nachweis des späteren Nachrichtensenders.
Agent signiert kanonischen Domain-/Challenge-/Claim-Datensatz mit Ed25519.
Starter prüft Schlüssel anhand des gepinnten Registers, frischen Nonce und
Kernel-Absender/registrierten lebenden Instanz, signiert Prüf-/Startreceipt.
Nicht authentisierte Fälle dürfen die künstliche Datei trotzdem schreiben:
keine operative ALLOW/DENY-Entscheidung durch Agent Authority.

Offline: CA-/Starter-/Actor-Signaturen unabhängig mit Host-OpenSSL prüfen;
Receipt/Keypossession/Startbinding und Kernelwriter separat auswerten. Root-
Startreceipt gilt nur für registrierte Instanz/Exec-Generation/Zeitfenster und
dieses Run/Fileobjekt. Kein Lookup allein nach PID oder Zeitnähe. Der Kernel-
Dateischreiber wird aus dem unveränderten A1-Observer gelesen, nicht aus Receipt.
Exec nach Authentisierung invalidiert alte Generation. Prozesswechsel/ReUse
benötigen neue registrierte Bindung; keine automatische Vererbung/Delegation.

## Einmalige echte Fälle

1. TestAlpha gültig, schreibt; 2. TestBeta gültig, schreibt.
3. Alpha behauptet Beta: echte Authentisierung Alpha und falscher Claim getrennt.
4. Kind erbt Key/Socket: tatsächlicher Nachrichtensender und Writer sind Kind,
keine Parentbindung übernehmen trotz gültigem Keybesitznachweis.
5. Exec-/Programmwechsel nach Authentisierung: alte Generation passt nicht.
6. Tatsächlicher PID-Reuse nach Ende: alte Bindung passt nicht zum neuen Start;
ein Versuch, reale Wiederverwendung separat bestätigen, kein Retry/Erfinden.
7. Beta versucht fremden Alpha-Keyzugriff und behauptet Alpha: Credential-
Dateizugriff messen, echte Betaauthentisierung getrennt, keine Übernahme Alpha.
8. Öffentlichen alten Alpha-Proof auf Beta replayen: frischer Nonce/Instanzgate
verhindern neue Authentisierung; trotzdem eigene unabhängig beobachtete Wirkung.

Alle Testdateien frisch im Gast, Orakel/Scoring getrennte Hostausgabe; keine
Orakel-/Identitätsdaten im A1-Collector. Acht Positionen fix, keine Wiederholung
der historischen sechs A1-Fälle. Quellenfreeze und Registerpin vor Fall1.
Fehler/Abbruch verbrauchen Position, keine stille Ersetzung. Fenster A1 maximal
12s; jeder Broker-/Worker-/Collectorzugang bounded. Verlustindikatoren des
Lifecyclemonitors und A1 separat; A1-Entry-nmissed bleibt UNBEKANNT.

BELEGT/TEILWEISE BELEGT/WIDERLEGT/UNBEKANNT scoped; behauptete, key-authentisierte,
prozessgebundene und handelnde Identität separate Felder. Negative korrekte
Rückweisung ist Konformität, kein Beleg universeller Angriffssicherheit.
write-Return keine Dauerpersistenz. Roh-/Speicherbytes/CPU/RAM und fehlende
Messungen getrennt; kein Keymaterial, Prompts/Antworten/Secrets archivieren.
Unitfixtures keine Kernel-/Kryptoproduktionsnachweise; passende Tests und volle
Suite zweimal. Alle404 Basisdateien bytegleich. Kein Merge/Ready, STOP nach
Forschungsbericht, Code/Daten/Hashes und regulärem Push-Nachweis.
