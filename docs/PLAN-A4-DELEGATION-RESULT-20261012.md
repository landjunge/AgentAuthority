# A4: ausgeführte Zwei-Agenten-Delegation, Skalierungsgate UNBEKANNT

**TEILWEISE BELEGT:** Genau zwei kontrollierte Testagenten haben einmal einen
signierten Auftrag tatsächlich übertragen und angenommen. B verursachte
einen unabhängig beobachteten 16B-Zielwrite. Alle24 Komponentenprüfungen
bestehen, aber drei kritische Verlustmetriken bleiben UNBEKANNT. Das vorab
festgelegte vollständige Gate ist deshalb **UNBEKANNT**. **Phase2 mit100
Agenten wurde nicht gestartet**, keine weiteren Stufen oder Wiederholungen.
Dies widerlegt die Hypothese nicht; fehlende Nachweise werden nicht zum Erfolg.

## Ausgangspunkt, vorregistrierte Methode und Quellen

Basis `7f1b6121ee506fbb341d1179376f09b132ff6c06`, eigener Branch
`codex/a4-delegation-20261012`. Gelesen: A1-Linux-Experiment-Spec/Resultat und
Observer, A2-Identity-Spec/Resultat/Protokoll/Starter/Lifecycle/Hostverifier,
A3-Real-Agents-Spec/Resultat und A3.1-Session-Job-Spec/Resultat/Rohbelege/Bridge.
Alle522 Basisdateien bytegleich erhalten; keine früheren Hypothesen,
Messungen, Negativbefunde oder Quellen umgeschrieben. Nachweis im neuen
Archiv `docs/a4-delegation-runs/2026-10-12/baseline-preservation.json`.

`9b1549e`: Spec/Gate vor Versuch; `335e212`: neue ausführbare Agenten,
Registrar, Driver und OpenSSL-Join; `cd55e22`: öffentliche Registry/CA-Pin,
Quellhashes und tatsächliche Umgebung vor Versuch; `f5cd1b1`: unveränderte
Rohmessung, Auswertung und21 Offline-Regressionspositionen. Vollständige SHAs
stehen im Gitlog und `pins.json`/`attempt.json`. Kein Commit während der
abschließenden Gesamtsuiten; feste Code-/Datenbasis `f5cd1b1`.

Eigene bestehende Ubuntu24.04.5-VZ-VM, x86_64, Kernel6.8.0-142-generic,
2CPU/2GiB, /proc-Takt100Hz, keine Hostmounts oder SSH-Agentweitergabe.
Nur diese zuvor gestoppte VM gestartet und wieder gestoppt; keine Installation,
Hostprivilegien, Kernel-Konfigurationsänderung oder Änderung an Colima.
Neue Gastdateien in separatem `/opt/a4-<run>`; altes Gastprogramm unverändert.
`environment.json` enthält Diagnosebefehl und reale Ausgabe.

Das bestehende A1-Programm erhielt nur künstlichen zufälligen Zielpfad und12s,
keine Agentenclaims/PIDs/Orakelsollwerte. Es hält das reguläre Dateiobjekt
und liest dev/inode, Prozessstart und write-Entry/Return unabhängig im Kernel.
Unveränderter A2-Lifecycle zeichnet Fork/Exec/Exit auf. Der Registrar startet
TestA/UID61101 und TestB/UID61102 mit getrennten Ed25519-Testkeys, versiegelten
memfds, nondumpable/no_new_privs, pidfds und frischen Besitznachweisen.

A signiert den künstlichen Job mit Nonce, Jobdigest, Sender/Empfänger,
Delegations-ID, beiden registrierten Instanzen, Run/Boot/Namespace und5s-
Gastzeitfenster. Die tatsächliche A-Nachricht wird per UNIX-SEQPACKET am
Registrar mit SCM_CREDENTIALS empfangen und an B weitergeleitet. B prüft
A-Signatur/Scope und signiert Annahme des exakten Delegationsdigests mit
eigener Instanz/Nonce. Registrar empfängt die tatsächliche B-Nachricht,
signiert den Transportbeleg und gibt B den kontrollierten Zielwrite frei.
`forwarded_ns` bezeichnet den Beginn der Weiterleitungsoperation; Bs signierte
Annahme belegt den Empfang des konkreten Inhalts. Kein direkter A-B-Socket
oder vom Registrar unabhängiges Transporttrustdomain behauptet.

Ground Truth ist separat vom A1-Beobachter: Controller-Popen-PIDs, UIDs,
pidfds, /proc-Startticks vor/nach Annahme, Wait/Exit und Agentenreturn/-intervall.
Der Hostjoin prüft Ed25519 erneut mit OpenSSL statt dem Gast-Cryptography-
Verifier, mit **vorher gepinntem** CA-Schlüssel, und verbindet Signaturen,
Kernel-Credentials, Instanzen/Exec, Datei und Reihenfolge mit diesem Orakel.
`source-and-reference-checks.json` bestätigt Observerhash, Quellpins,
vorab committed CA und gemessene100Hz für den /proc-Abgleich.

Trustanker: Host/CA, Rootregistrar/Orakelcontroller, Gastkernel und gepinnter
kontrollierter Code. Unabhängiger Kernelkanal/Verifier sind keine vollständige
Unabhängigkeit vom vertrauenswürdigen Host/Root. Kompromittierte Anker,
weitergegebene private Keys oder bösartige Registrierung sind nicht geprüft.
Versuchsfreigabe ist keine neue Produkt-Rechteentscheidung; D-012 bleibt
Beobachtung/Analyse. Kein Codex/Grok-, Provider- oder Modellnachweis.

API-Referenzen zur Einordnung, keine Ersatzmessungen:
[Linux Kprobes](https://docs.kernel.org/trace/kprobes.html) dokumentiert
Returnmisses und verpasste Probeaufrufe;
[Linux unix(7)](https://man7.org/linux/man-pages/man7/unix.7.html) dokumentiert
kernelgeprüfte SCM_CREDENTIALS und Privilegienausnahmen. Hier sind Sender
unprivilegiert; der Registrar bleibt ausdrücklich vertraut. Einzelne direkte
Weböffnungen lieferten Abruffehler; der unix-Vertrag wurde über den offiziellen
Suchindex gelesen. Kein Abruffehler als positiver API-Nachweis gewertet.

## Tatsächlich gemessener Versuch und Gate

| Gegenstand | Tatsächlicher Befund | Klasse/Grenze |
| --- | --- | --- |
| TestA | PID1157, Kernelstart327417296754ns, UID61101, exec-Generation1 | BELEGT im kontrollierten Registry-/Kernelkontext |
| TestB/Writer | PID1158, Start327564267631ns, UID61102, Generation1 | BELEGT, eigenes Credential; nicht A-PID-Verwandtschaft allein |
| Auftrag/Annahme | unterschiedliche Signaturen; exact Digest, frische Nonces, Scope und Reihenfolge passen | BELEGT unter Registrar-/Hostvertrauen |
| Datei/Handlung | dev265289729/inode262996, ein write mit count=return16, Bs Instanz | BELEGT für beobachteten VFS-Aufruf; keine Crashpersistenz |
| Referenz | PIDs/Startticks/UIDs/Instanzen und Return/Intervall passen; zwei erfolgreiche Exits | BELEGT; Orakel nicht an A1 übergeben |
| Zielzuordnung | ein B-Kandidat, null falsche Positive, kein A-Zielwrite beobachtet | BELEGT für diese eine Position; keine Angriffserfolgsrate |
| Bekannte Verluste | Perf/Submit/Pair/Map-pending/Returnmisses0; Entry=Return=Delivered=Referenz1 | BELEGT für erfasste Zähler, kein allgemeiner Vollständigkeitsbeweis |
| Write-entry-nmissed | null, BCC-perf-Entry nicht durch klassischen Returnprofilzähler abgedeckt | UNBEKANNT |
| Fork-entry-nmissed | null im erhaltenen Lifecycle | UNBEKANNT |
| Lifecycle-Mapupdatefehler | kein eigener Fehlerzähler im vorhandenen Kanal | UNBEKANNT |
| Gesamtdelegation / Gate |24 Teilprüfungen wahr, drei kritische Verlustwerte fehlen | TEILWEISE BELEGT / vollständiges Gate UNBEKANNT |
| Externe Agenten-/Modellsitzung | keine entsprechende Attestierung untersucht/erzeugt | UNBEKANNT, A3.1-Grenze erhalten |

Die Zuordnung der tatsächlich beobachteten Handlung gelingt. Daraus folgt
keine lückenlose Erfassung aller möglichen Handlungen. Schon im eingefrorenen
Gate waren unbekannte Entry-/Forkwerte ausdrücklich blockierend, statt aus
Null-Perfverlust oder Referenzübereinstimmung null Misses abzuleiten.
Keine neuen Probeansätze oder Wiederholungen nach diesem einen Ergebnis.

Phase2 nicht ausgeführt: keine100 Keys/Agenten erzeugt, keine parallelen oder
mehrstufigen Ketten, Replay-/Fremdclaim-/Refusal-/Interrupt-/PID-Reuse-
Kernelversuche. Deren Resultate, Skalierungsdurchsatz und Tail-Latenzen bleiben
UNBEKANNT; sie sind nicht als bestanden oder widerlegt verbucht. Persistente
Anti-Replay-/Restart-/Mehrprozesssicherheit wurde nicht bewiesen. Der Driver
sperrt eine zweite Ausführung dieses archivierten Versuchs.

## Daten, Ressourcen, Prüfungen und Abschluss

Auftragsausgabe bis Registrar-Annahme: **2226593ns (2.227ms)**, einmalige
Messung inklusive lokaler Transport-/Signaturarbeit, ohne Start/Enrolment.
Kein Lastbenchmark oder allgemeiner Durchsatzwert. A1: zwei Records
(write+exit),152 Callbackbytes; Lifecycle: sechs Records,264 Callbackbytes.
Gespeicherte Dateien/Bytes/Hashes separat in `artifact-index.json`.

Observer-CPUuser2.016104s/system0.409085s, PeakRSS175955968B;
Registrar-CPUuser0.869298s/system0.297428s, PeakRSS164614144B, jeweils
inklusive BCCcompile. Keine summierte Gesamt-VM-/Kernel-/Agentenprozesskosten;
diese bleiben UNBEKANNT. Rohdateien samt leeren stderr-Logs erhalten.

21 neue Offline-Regressionen verändern Kopien der **realen** öffentlichen
Belege: falsche CA/Claims/Credentials, gleichePID/falscherStart, exec,
Dateiwechsel, fehlender/duplizierter write, fehlender Exit und Ablauf.
Unbekannte/boolean/string/positive Verlustwerte können kein Gate passieren.
Das sind Verifierregressionen, keine weiteren Agenten-/Kernelversuche und
kein praktischer Replay-/PID-Reuse-Angriffsnachweis.

Abschließende Qualitätsresultate/JUnit/Commands im Archiv: Gesamtsuite **zweimal669 Tests bestanden**
auf demselben Code-/Daten-HEAD; neue Ruffchecks/Format, Gesamtformat, striktes
Mypy für32 Kernquelldateien und Bandit im Kernbereich. Gesamt-Ruff hat weiterhin
die exakt selben16 historischen Befunde, keine neuen; kein grüner Gesamt-Ruff
behauptet, historische Quellen nicht zum Bereinigen geändert.

Gastvault und Host-CA gelöscht, beide Agenten-/Observer-/Registrarprozesse
beendet; tatsächlich nachgeprüft in `guest-cleanup-verification.json`.
`end-environment-ci.json`: VMStopped, Colima unverändertRunning; Branch-CI
keine Läufe. Workflow startet bei master-Push/PR, kein PR/Ready/Merge ausgeführt.
Regulärer Push ausschließlich eigener A4-Branch. Lokalen/Remote-End-SHA nach
Abschluss separat prüfen, keine selbstreferenzielle Commit-SHA im Messarchiv.
Der Auftrag endet hier am nicht bestandenen Phase1-Gate.
