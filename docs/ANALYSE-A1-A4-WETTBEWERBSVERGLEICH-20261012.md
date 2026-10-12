# Agent Authority A1–A4: Bestandsaufnahme und Wettbewerbsvergleich

Analyse und Quellenabruf: **2026-10-12**. Forschungsbasis:
`3a5e15666fe37d28d77f6c5b63276de8cda250c2` (A4-Finalstand).
Lokale Forschungslinie: `agent-authority-a1-linux-experiment` mit A4-Fortsetzung.
Remote: `https://github.com/landjunge/agent-authority-lab.git`.
Eigener Analysebranch: `codex/a1-a4-comparison-20261012`.

**Ergebnis:** Der Prototyp belegt im kontrollierten Linux-Versuchsrahmen eine
Kette von kryptografischer Testidentität, signierter Auftragsdelegation,
konkreter Prozessinstanz und unabhängig beobachteter Schreibhandlung.
A4 enthält ein bestandenes Zwei-Agenten-Gate und einen tatsächlich ausgeführten
Versuch mit 100 simulierten Agenten und 99 vollständigen positiven Ketten.
Eine authentifizierte externe Codex-/Grok-/Modell- oder Providersitzung bleibt
**UNBEKANNT**. Technische Überlegenheit, Markt-Alleinstellung und
Produktionsreife sind nicht nachgewiesen.

## 1. Umfang und Beweismaßstab

Verglichen werden A1–A4 einschließlich A3.1 und der macOS-Ausgangsgrenze mit
SPIFFE/SPIRE, Cilium Tetragon, OpenTelemetry und Sigstore. Diese Systeme lösen
verschiedene Teilprobleme; die Matrix ist keine Rangliste. Historische ABC-/
P-Phasen werden nicht neu bewertet. Das historische ABC-A3 zur FD-Identität
ist eine andere Frage als die hier betrachtete reale-Client-Runde A3.

| Kennzeichnung | Bedeutung |
| --- | --- |
| **BELEGT** | Konkreter Befund aus archivierter Messung, Originaldaten und zugehörigem Code, im benannten Versuchs-/Vertrauensrahmen. Keine neue Messung dieser Analyse. |
| **dokumentiert** | Offizielle Quelle beschreibt die Fähigkeit; nicht in unserem Aufbau praktisch geprüft. Kein gleichwertiger experimenteller Nachweis. |
| **ungeprüft** | Eine benannte Integration, Implementierung oder Angriffsklasse wurde im betrachteten Material nicht praktisch validiert. |
| **UNBEKANNT** | Die konkrete Aussage ist aus den verfügbaren Belegen nicht beantwortbar. Fehlende Messung bedeutet weder Erfolg noch Nullverlust. |

Historische Klassen **TEILWEISE BELEGT** und **WIDERLEGT** bleiben unverändert;
die Vergleichskennzeichnungen ersetzen sie nicht. Dokumentierte API-Eignung,
ungeprüfte Integration und unbekanntes Ergebnis können nebeneinander stehen.

Prozessidentität bezeichnet Boot/Namespace, PID, Start und gegebenenfalls
Exec-Generation. Logische Agentenidentität bezeichnet einen registrierten
Principal, bei A2/A4 ausdrücklich einen Testprincipal. Schlüsselbesitz,
Clientimage, Konto, Coding-Thread, Provider, Modell und Auftrag sind getrennte
Aussagen. Eine Signatur schützt Nachricht und Schlüsselherkunft unter dem
Trustanker; sie bestätigt nicht automatisch die Wahrheit jeder Behauptung.
Ein Kernel-Write belegt keine dauerhafte Speicherung nach Crash.

Gelesen: ABC-Plan samt Identitätsergänzung, A1-native-/Linux-Spec und Resultate,
A2-, A3-, A3.1-, A4-Delegations-/Completion-Spec und Resultate sowie
[A4-Finalbericht][E4]. Selektiv untersucht: Beobachter, Starter-/Bindungs-,
Delegations- und Join-Pfade unter `research/a1_linux/`, `a2_linux/`,
`a3_linux/`, `a31_binding/`, `a4_delegation/`, `a4_completion/` und
`a4_scale/`. Keine vollständige Code-/Sicherheitsprüfung oder Marktinventur.

### Lesende Archivkontrolle

SHA256 und vorhandene Bytezahlen wurden mit `hashlib` gegen die acht
`artifact-index.json` verglichen; alle folgenden Pfade liegen unter `docs/`.

| Archiv | Indexeinträge | Abweichungen |
| --- | ---: | ---: |
| `a1-native-runs/2026-10-11/` | 7 | 0 |
| `a1-linux-runs/2026-10-12/` | 20 | 0 |
| `a2-linux-runs/2026-10-12/` | 17 | 0 |
| `a3-linux-runs/2026-10-12/` | 26 | 0 |
| `a31-session-job-runs/2026-10-12/` | 37 | 0 |
| `a4-delegation-runs/2026-10-12/` | 23 | 0 |
| `a4-completion-runs/2026-10-12/` | 33 | 0 |
| `a4-final-runs/2026-10-12/` | 36 | 0 |

**199 Indexeinträge**, keine Behauptung, dass Indizes sämtliche Dateien
enthalten oder externe Unverfälschbarkeit garantieren. Zusätzlich stimmen
alle A4-Quellhashes aus `phase1/pins.json` und `phase2/pins.json` mit der
Forschungsbasis überein. Das letzte Objekt in `phase2/trial.jsonl` enthält
unter `result` exakt `phase2/trial-result.json`. Lesende Rohdatenzählung:
100 Bindings, 99 positive Rows, 99 Write-Records mit `count=result=16`,
99 Writerexit-Records und 300 Lifecycle-Records. Diese Prüfung ergänzt die
archivierten Signatur-/Join-Prüfungen; Forschungsprogramme, Verifier und
Tests wurden nicht erneut ausgeführt.

## 2. Bestand nach Forschungspaket

Alle Belegpfade sind in der Forschungsbasis erhalten. Abschlussreferenzen
bezeichnen historische Gitstände, keine neuen Messläufe.

| Paket / Git-Abschluss | Archivierter Befund | Nachweisgrenze und Beleg |
| --- | --- | --- |
| A1 macOS-native | **BELEGT:** eigene Prozess-/FD-Snapshots und konkrete Zugriffsablehnungen. Tatsächlicher Dateischreiber **UNBEKANNT**; keine Writer-Versuche. | macOS 15.7.4 / UID 501: Auditpipe `EACCES(13)`, ES `ERR_NOT_PRIVILEGED(5)`, kein zulässiger kausaler Kanal. Keine allgemeine macOS-Unmöglichkeit. [Native-Bericht][EN], `a1-native-runs/.../availability.json`. |
| A1 Linux / `ec82f2ae5e0168ef41abe13e9b0cf495d20a0293` | **BELEGT:** sechs Positionen, fünf korrekt zugeordnete Zielwrites; inaktive/anders schreibende Prozesse und gefälschte PID nicht aufgewertet. Separate PID-Reuse-Kontrolle: zwei Writes, gleiche PID 2435, verschiedene Starts. | UID 501-Kohorte und Root-Reuse haben getrennte Nenner. Entry-nmissed historisch **UNBEKANNT**. Auditstatus/fanotify-Initialisierung sind keine gemessenen alternativen Writerketten. [A1-Bericht][E1], `a1-linux-runs/.../L1.json` bis `L6.json`, `pid-reuse-control.json`. |
| A2 / `98c274ac5c1e475c335704d4f5aefa40f97f47b0` | **BELEGT:** acht Writes, vier vollständige Testidentitätsketten; vier bewusst ungebundene Identitätsfälle. Keine falsche fremde Identitätsübernahme in diesen Fällen. | Kind/Socket-Key-Erbe, Exec-Wechsel, echte PID-Reuse und Replay übernehmen kein altes Binding. Keine universelle Nichtweitergebbarkeit der Keys. Entry-/Fork-nmissed **UNBEKANNT**. [A2-Bericht][E2], `a2-linux-runs/.../case-1.json` bis `case-8.json`. |
| A3 / `28ff798e2548a82dbf787cbba0399c5a1857437f` | **TEILWEISE BELEGT:** zehn reale Clientpositionen, zwölf Kernelwrites, neun lokale Wrapperbindungen, acht frische Hostdispatch-Bindungen; null vollständige externe Agentenketten. | Reale Hostclients, kontrollierte Linux-Wrapper. Kontotoken signiert keine konkrete Antwort; Audience-/Sitzungsbezug unvollständig. [A3-Bericht][E3], `a3-linux-runs/.../case-*.json`, `account-token-checks.json`. |
| A3.1 / `7f1b6121ee506fbb341d1179376f09b132ff6c06` | **BELEGT** für die schwächere lokale Kette: vier reale Hostclientversuche, zwei Clientdispatch→Linux-Wirkungsjoins. Null provider-signierte Jobnachweise; externe Gesamtkette **UNBEKANNT**. | Apple-Developer-ID-/laufendes-Image-Prüfung plus Hostreceipt. Geerbte Antwortpipes und durchgehende Host-Exec-Generation offen. Nicht archivierte Bearer-Inputs verhindern vollständiges öffentliches Offline-Replay der Kontotokenprüfung. [A3.1-Bericht][E31], `a31-session-job-runs/.../provider-capability.json`, Linux-Integrationsbelege. |
| A4 initial / `88087a609128149aad752ad9bb52959009843e1f` | 24 Komponenten bestanden, vollständiges Gate wegen drei unbekannter kritischer Verlustwerte nicht erreicht; keine Skalierung auf 100. | Write-/Fork-Entry-nmissed und Lifecycle-Mapupdatefehler **UNBEKANNT**. [Initialbericht][E40], `a4-delegation-runs/.../evaluation.json`. |
| A4 Kontrollen / `e5f4a0bfde026b9d567bc05ae06fec32be7eb660` | Kontrollen ergänzt; Collectorabschluss scheiterte an `BPF.functions` statt `BPF.funcs`. Reparierte Instrumentierungsdiagnose ersetzte keinen Gateversuch. | Fehlversuch und Originalbelege erhalten. [Completion-Bericht][E41], `a4-completion-runs/.../`. |
| A4 final / `3a5e15666fe37d28d77f6c5b63276de8cda250c2` | **BELEGT:** frisches Zwei-Agenten-Gate; danach 100 Testprincipals, 99 vollständige positive Ketten, vier konkrete Negativabläufe. | Gate: 26 Prüfungen/23 kritische Werte null; Scale: 19 Gesamtprüfungen/24 kritische Werte null. Root/CA/Kernel vertraut; keine externe Provideridentität. [Finalbericht][E4], [Gate][ER1], [Scalejoin][ER2], [Originalcapture][ER3], [Originaltrial][ER4]. |

Spätere Erfolge ändern historische negative/unklare Ergebnisse nicht.
Linux-Instrumentierung löst keine macOS-Rechtefrage. Null falsche Zuordnungen
in kontrollierten Fällen ist keine populationsweite Fehlerrate.

## 3. Technische Tragfähigkeit und Grenzen von A4

**BELEGT:** CA-gepinntes Register, getrennte Ed25519-Keys/UIDs, frische
Besitzproben, pro Nachricht `SCM_CREDENTIALS`, pidfd und Kernelstart/Exec
binden Testprincipal und Prozessinstanz. Jobdigest, Nonce, Sender/Empfänger,
Delegations-ID, Objekt, Parentlinks und 5s-Gültigkeit werden signiert; B signiert
die konkrete Annahme. Root bezeugt Übergabe/Freigabe. Der Observer erhält nur
gehaltene künstliche Objekte, keine Actorclaims/Orakelsollwerte. OpenSSL-Join
prüft Signaturen, Instanzen, Datei, Return, Zeit und Referenzmengen.
Code: [Registrar][CR], [Observer][CK], [Lifecycle][CL], [Join][CJ].

**Unabhängigkeit:** Kernelbeobachtung ist unabhängig vom Actorclaim;
Host-OpenSSL ist eine andere Prüfimplementierung als Gast-Cryptography.
Registrar und Controllerreferenz teilen jedoch Root-/Hostvertrauen.
Archive/Signaturen sind keine Remoteattestierung eines unangetasteten Kernels
und kein externes Audit. Kompromittierte Root-/CA-/Host-/Hypervisoranker sind
**ungeprüft**; Widerstand dagegen **UNBEKANNT**.

**Verlust:** Klassische Entry-/Fork-Kprobes liefern `kprobe_profile`;
Return-nmissed, BPF-Rekursion, Map-/Read-/Submit-/Perf-/Pairfehler und Pending
werden getrennt erhoben. Fehlende Werte blockieren das Gate. [Probes][CP]
nutzt BCC 0.29.1 und `BPF.funcs`. Nullwerte gelten im Scope/Zeitfenster zusammen
mit dem Referenzabgleich. Globale Entry-/Returnhits 762/758 sind nicht atomar
und enthalten ungescopte Aufrufe: weder vier verlorene Zielwrites noch globale
Vollständigkeit daraus ableiten.

**Negativfälle:** [Registrar `negatives()`][CN] verarbeitet echte Replay-/
Fremdclaim-Pakete in einem gesonderten vorgegebenen Versuchspfad, setzt dort
`forwarded=False` und sendet Zurückweisung. Die gemessenen Fehlerbedingungen
steuern dort keinen allgemeinen Eingangsvalidator. Der positive `level()`-
Pfad prüft hingegen Body, Sender, Signatur und Nonceledger.
[Join ab Zeile306][CJN] prüft verbrauchte Nonce, frisches Replayfenster,
Credentials und falsche fremde Signatur; `no_forward` beruht auf dem
Root-signierten Witnessfeld. Bei Verweigerung/Unterbrechung wird zusätzlich
kein neuer passender Kernelwrite im begrenzten Capture festgestellt.

Die konkreten Pakete, Signatur-/Identitätsunterschiede und begrenzten
Handlungsausgänge sind **BELEGT**. Allgemeine produktive Replay-/Fremdclaim-
Abwehr über denselben Live-Validator und ein persistentes/verteiltes Ledger
sind **ungeprüft**. Das ändert das historische Gate nicht, sondern benennt
seinen begrenzten Geltungsbereich. Der Scalejoin zählt 99 vollständige
positive Ketten, zwei absichtlich unvollständige Delegationen (Verweigerung/
Unterbrechung) und zwei zurückgewiesene Nachrichtenfälle (Replay/Fremdclaim).
Letztere sind keine zusätzlichen positiven Handlungsketten.

**Wirkungsscope:** synchrones `vfs_write` an gehaltenen regulären Ext4-Dateien
mit `dev/inode`, Start, Entry/Return und 16 B-Ergebnis. Kein Persistenzbeweis;
`mmap`, `writev`, `io_uring`, Rename/Truncate, Netzdateisysteme und
Objektwiederverwendung außerhalb des gehaltenen Scopes **ungeprüft**.
Ein gemeinsamer Prozess oder weitergegebener Key authentisiert keine zweite
logische Agentensitzung.

**D-012:** [ABC-Plan][EP] hält Beobachtung/Analyse/Warnung ohne
Produkt-ALLOW/DENY oder Rechtevergabe fest. Aktive Starter/Freigaben und
kontrollierte Unterbrechung sind Versuchshülle. Ihre Übernahme in das Produkt
ist weder freigegeben noch als D-012-konform nachgewiesen.

## 4. Vergleichsmatrix

Externes Verhalten ist **dokumentiert**, nicht bei uns gemessen.
„UNBEKANNT: A4-Vertrag“ heißt: aus den geprüften Quellen keine vollständige
konkrete Kette nachgewiesen; keine Aussage technischer Unmöglichkeit.
Quellenkennungen führen direkt zu offizieller Dokumentation.

| Dimension | Agent Authority | SPIFFE/SPIRE | Cilium Tetragon | OpenTelemetry | Sigstore |
| --- | --- | --- | --- | --- | --- |
| Identitätsbindung | **BELEGT:** Testkey→Start/Exec-Instanz; externe Sitzung **UNBEKANNT**. E2/E31/ER2 | **dokumentiert:** Node-/Workloadattestation, selektorbasierte SPIFFE-ID, SVIDs; konfigurierter Workload. [S1][S1], [S2][S2] | **dokumentiert:** `exec_id`, Start, PID, Credentials, Pod-/Containerkontext; keine automatisch kryptografische KI-Sitzung. [T2][T2] | **dokumentiert:** Agent-/Provider-/Modellattribute und Spans; Instrumentierungsdaten, kein Identitätsbeweis. [O1][O1] | **dokumentiert:** Signeridentity/Issuer über OIDC/Fulcio; Prozess-/Modellsitzungsbindung **UNBEKANNT**. [G1][G1] |
| Signierte Auftragsdelegation | **BELEGT:** Digest, Nonce, Sender/Empfänger, Annahme, Instanz, Parentlink, Zeit im kontrollierten Protokoll. CR/CJ | **dokumentiert:** Delegated Identity API für fremde SVIDs; anderer Vertrag als Auftrag+Annahme+Wirkung. [S3][S3] | **UNBEKANNT:** A4-Auftragsprotokoll in geprüften Event-/Policyquellen nicht nachgewiesen. [T1][T1], [T2][T2] | **dokumentiert:** Agent-/Tool-/Workflowkontext; signierter A4-Vertrag **UNBEKANNT**. [O1][O1], [O4][O4] | **dokumentiert:** Blobs/eigene Predicates signierbar; entsprechendes Job-/Annahmeschema **ungeprüft**. [G2][G2], [G3][G3] |
| Unabhängige Kernelbeobachtung | **BELEGT:** Linux-VFS-Write+Lifecycle im Scope; macOS-Schreiber **UNBEKANNT**. E1/ER3/CK | **dokumentiert:** OS-gestützte Attestation; konkreter Write-Ereigniskanal dadurch nicht nachgewiesen. [S1][S1] | **dokumentiert:** eBPF-Prozess-/Dateioperationen, Kprobe-Argumente/Returnwerte. [T1][T1], [T2][T2] | **dokumentiert:** OBI-eBPF für Anwendungs-/Netzwerkobservability; exakter A4-Datei-/Returnvertrag **UNBEKANNT**. [O2][O2] | **UNBEKANNT:** eigener Kernelkanal aus Signaturquellen nicht nachgewiesen; Fremdbelege signierbar. [G2][G2] |
| Durchgehende Kette | **BELEGT:** 99 lokale Testketten; externe Antwort→Job fehlt. ER2 | **UNBEKANNT:** A4-Gesamtkette ohne zusätzliche Integration. [S1][S1], [S3][S3] | **dokumentiert:** Prozess-/Eltern-/Dateiereignisse; Principal-/Auftragsbindung zusätzlich nötig. [T2][T2] | **dokumentiert:** verteilte Korrelation; Trace/Baggage allein keine authentifizierte Wirkungskette. [O4][O4] | **dokumentiert:** Inhalte, Signaturen, Loginklusion; Wirkungswahrheit braucht Messquelle. [G3][G3], [G4][G4] |
| Verlust/Vollständigkeit | **BELEGT:** 24 Nullindikatoren+Referenz final; universelle Vollständigkeit **UNBEKANNT**. ER2 | **UNBEKANNT:** für unseren Write-/Lifecycle-Vertrag. [S2][S2] | **dokumentiert:** Probe-Misses, Mapfehler, Ringbuffer-/Queueverlust, Listeneroverflow; A4-Vertrag **ungeprüft**. [T3][T3] | **dokumentiert:** Collector-Queue-/Refusal-/Fehlermetriken; keine automatische Gesamtlossfreiheit. [O5][O5] | **dokumentiert:** Signatur-/Bundleprüfung; keine Vollständigkeitsgarantie fremder Erfassung. [G3][G3], [G4][G4] |
| Skalierbarkeit | **BELEGT:** einmal 100 Testprozesse, 99 Jobs/sechs Stufen; darüber **UNBEKANNT**. ER2 | **dokumentiert:** Server/Agenten auf mehreren Nodes; gleicher Benchmark **ungeprüft**. [S1][S1] | **dokumentiert:** nodeweises Deployment/Kernelfilterung; gleicher Benchmark **ungeprüft**. [T1][T1], [T4][T4] | **dokumentiert:** horizontale Collectors, Grenzen zustandsbehafteter Komponenten; gleicher Benchmark **ungeprüft**. [O5][O5] | **dokumentiert:** Signier-/Verifikationsdienste, Bundles; gleicher Benchmark **ungeprüft**. [G1][G1], [G4][G4] |
| Sicherheit/Betrieb | **BELEGT:** isolierte Root-VM, Test-CA, künstliche Dateien; Produktionsbetrieb **ungeprüft**. E4 | **dokumentiert:** Attestor-/CA-/Registrierungsvertrauen, Trusted-Delegate-Risiko. [S1][S1], [S3][S3] | **dokumentiert:** privilegierter Zugang, Hookauswahl/Threat Model; Enforcement optional. [T4][T4], [T5][T5] | **dokumentiert:** Instrumentierung/Collector/Backend; OBI-Capabilities und Baggagegrenzen. [O3][O3], [O4][O4] | **dokumentiert:** OIDC/Fulcio/Rekor/TUF, Logmonitoring, eigene Keys/Dienste. [G1][G1], [G5][G5] |

### Abgrenzungen gegen einen zu engen Vergleich

SPIREs **Delegated Identity API ist vorhanden**: Trusted Delegates dürfen
SVIDs anderer Workloads erhalten und diese impersonieren. PID-Attestation
verlangt Schutz gegen Recycling, etwa pidfd. Das ist kein fehlendes
Delegationsfeature, aber kein Nachweis eines angenommenen/geschriebenen Jobs.
[S3][S3] Der aktuell **Incubating** WIT-SVID bindet Workload-ID und Publickey
mit Proof-of-Possession-Anforderungen; `jti` darf nicht zur Replayabwehr dienen.
Workload-API-Profil optional, SPIRE-Aktivierung experimentell; hier nicht
benutzt. [S4][S4], [S2][S2]

Tetragon überlappt unmittelbar mit der Kernelbeobachtung. Eine Standardpolicy
meldet Schreibversuche; Gleichwertigkeit mit unserem Objekt-/Return-/
Referenzvertrag verlangt konkret geeignete Hooks/Felder und deren Prüfung.
Die Dokumentation nennt falsche Hookauswahl als Sichtbarkeitsrisiko.
Reiner Beobachtungsbetrieb ist konzeptionell mit D-012 vereinbar; keine
Policyintegration ausgeführt. [T1][T1], [T2][T2], [T4][T4]

OpenTelemetry ist weder auf selbstgemeldete Logs beschränkt noch ohne
Agentenbezug: OBI-eBPF und GenAI-Agent-/Toolkonventionen existieren,
letztere **Development**. Agent-/Providerattribute beschreiben
Instrumentierungswissen und authentifizieren keine externe Sitzung.
Baggage besitzt keine eingebauten Integritätschecks. [O1][O1], [O2][O2], [O4][O4]

Sigstore ist nicht auf Images beschränkt: Dateien/Blobs und eigene in-toto-
Predicates können signiert werden. **Analytische Folgerung:** deren Signatur
belegt Herkunft/Integrität, nicht die Wahrheit einer behaupteten Kernelhandlung.
Rekorzeit ist kein Dateiaktionszeitpunkt; Fulcio-Identity ist keine
Modellantwort. [G2][G2], [G3][G3], [G1][G1]

## 5. Skalierung und Betriebsaufwand

A4: Ubuntu 24.04.5, Linux 6.8.0-142-generic, x86_64, 2 CPU / 2 GiB.
100 gleichzeitig registrierte simulierte Agenten mit eigenen Keys/UIDs/
Startinstanzen. Agent000 schreibt nicht; 99 Binärbaumkanten, Frontiers
`2/4/8/16/32/37`, sechs Stufen. 37 überlappende Jobs, aber nur zwei
überlappende Kernelwrites: kein Test mit 100 gleichzeitig schreibenden
LLM-Agenten. PID-Reuse final **UNBEKANNT**; A1/A2-Reuse separat erhalten.

| Archivierter Messwert | Ergebnis | Grenze |
| --- | ---: | --- |
| Positive Pipeline | 99 / 3,542819838 s = 27,943843 Jobs/s | Ausgabe bis letzter Completion, nach Registrierung; kein Modell-/Startdurchsatz |
| Ausgabe→Annahme | Median 514,597 ms; p95 807,343 ms | 99 Jobs, Registrar-Empfang, nearest-rank-p95 |
| Ausgabe→Kernelwrite | Median 737,763 ms; p95 858,337 ms | 99 Jobs, Gast-monotonic; kein Host/Gast-Uhrvergleich |
| Observer CPU / PeakRSS | user 2,120654 s + system 0,217631 s / 178.479.104 B | samt Compile/Erfassung; kein isolierter Kerneloverhead |
| Registrar CPU / PeakRSS | user 1,234585 s + system 0,494667 s / 165.412.864 B | eigener Koordinationsprozess |
| Worker-CPU | user 12,557760 s + system 4,377090 s | Child-rusage vor Spawn bis Wait; Bootstrap/Negativfälle enthalten |
| Max. Agenten-RSS-Summe | 2.628.763.648 B | sieben Summensnapshots; gemeinsame Seiten mehrfach; kein physischer VM-Peak |
| Min. MemAvailable-Snapshot | 361.152.512 B | keine lückenlose Peakmessung |
| Callbackrohbytes | Write/Exit 15.048 B + Lifecycle 13.200 B | 198 bzw. 300 Records; keine gesamten IPC-/Kernelbytes |
| Original-JSONL auf Disk | Capture 64.645 B; Trial 1.225.528 B | Trial enthält Referenzen/Signaturen/Checkpoints; keine Callbackrohbytes |
| Alle `phase2/`-Dateien | 2.383.295 B | samt Registry/Pins/Join/abgeleitetem Resultat; kein Produktionsspeichermodell |
| Gesamt-VM-/Kerneloverhead, physischer RAMpeak | **UNBEKANNT** | keine Schätzung als Messwert |

Belege: [Originaltrial][ER4], [Originalcapture][ER3], [Scalejoin][ER2] und
`phase2/trial-result.json`. Die Versuchshülle prägt Latenz: `actual_sender()`
liest Lifecyclezustand; `state()` ruft `perf_buffer_poll(timeout=10)` auf.
[CR][CR], [CL][CL] Keine isolierte eBPF-Latenz oder Kapazitätsgrenze.

| System | Betriebskomponenten: belegt bzw. dokumentiert | Vergleichsgrenze |
| --- | --- | --- |
| Agent Authority | **BELEGT:** BCC/Kernelheader, eigene Root-VM, Registrar, temporäre CA/Keys, separate Erfassung/Export/OpenSSL-Join; manueller Forschungsworkflow. E4/CP | Dauerbetrieb, HA, Rotation, Recovery, Wartungszeit **ungeprüft/UNBEKANNT** |
| SPIRE | **dokumentiert:** Server/Datastore/CA, Agent pro Node, Attestorplugins, Registrierung und SVID-Verteilung. [S1][S1] | konkrete Integrationskosten/gleicher Benchmark **ungeprüft/UNBEKANNT** |
| Tetragon | **dokumentiert:** Nodeagent/Standalone, Kernel/BTF-Zugang, Policies/Export/Metriken; Containerbeispiel mit Hostnamespaces und `--privileged`. [T4][T4], [T5][T5] | Minimalrechte und Overhead für unseren Vertrag **ungeprüft/UNBEKANNT** |
| OpenTelemetry | **dokumentiert:** SDK/OBI, Collector/Backend; konfigurationsabhängige BPF-/Perf-/Proc-/Ptrace-Capabilities und Queuemanagement. [O3][O3], [O5][O5] | vollständige Beweisarchivierung/gleiche Kostenbasis **ungeprüft/UNBEKANNT** |
| Sigstore | **dokumentiert:** Cosign/Verifier; bei Keyless OIDC/Fulcio/Rekor; eigene Schlüssel oder Dienste/Trustroots möglich. [G2][G2], [G5][G5] | Pro-Job-Latenz, Verfügbarkeit und Betriebskosten hier **ungeprüft/UNBEKANNT** |

Kein Wettbewerber wurde auf identischer Hardware mit identischen Jobs,
Dateioperationen, Verlust-/Referenzdefinitionen und Betriebsgrenzen gemessen.
Relative Effizienz, Maximaldurchsatz und Kostenrangfolge sind **UNBEKANNT**.
„Leichter“, „schneller“ oder „besser skalierend“ ist nicht gerechtfertigt.

## 6. Kombinationen vorhandener Systeme

Die folgenden Optionen sind **analytische Ableitungen**, keine validierten
Integrationen oder neuen Arbeitsaufträge. Dokumentierte Teilfunktionen ergeben
noch keine belegte Gesamtlösung.

| Kombination | Möglicher Beitrag | Fehlende geprüfte Verbindung |
| --- | --- | --- |
| SPIRE+Tetragon | Workloadcredentials/Attestation plus Prozess-/Dateiereignisse. [S1][S1], [T2][T2] | SVID→exakte Start-/Exec-Instanz→Objekt/Return; Race-, Keytransfer- und Lossvertrag. **ungeprüft**, Gesamtkette **UNBEKANNT** |
| SPIRE+eigener signierter Delegationsvertrag+Tetragon | Frischer Jobdigest, Sender/Empfänger, Annahme, Parentlinks mit Workloadcredentials. [S2][S2], [S4][S4], [T1][T1] | Anwendungsschema, Trustpins, Replayledger, Zeitfenster und unabhängiger Join als Integration **ungeprüft**; keine A4-Parität behauptet |
| Vorige Kombination+OpenTelemetry | Agent-/Tool-/Workflowspans, Export und Korrelation. [O1][O1], [O5][O5] | Trace-ID ersetzt keine Beweisbindung; Sampling/Dropkontrollen und minimiertes Beweisarchiv separat. **ungeprüft** |
| Agent Authority oder vorige Kombination+Sigstore | Beweisdigests/Versionen/Predicates mit Signeridentity und Transparenzbeleg absichern. [G2][G2], [G3][G3], [G4][G4] | keine nachträgliche Beglaubigung der Messwahrheit; vertrauenswürdiger Observer/Signer und öffentliche/vertrauliche Metadaten separat. **ungeprüft** |

Keine Kombination bindet automatisch die konkrete externe Modellantwort/
Providersitzung an einen einzelnen Auftrag. Workloadidentity, Traceattribute
und signierte lokale Behauptungen beantworten andere Fragen. Passender
externer Nachweis bleibt im Forschungsstand **UNBEKANNT**, ohne globale
Unmöglichkeitsaussage.

## 7. Mögliche Differenzierung und offene Fragen

| Kandidat | Nachgewiesener Kern | Grenze der Alleinstellungsbehauptung |
| --- | --- | --- |
| Zusammengeführter Beweisvertrag | **BELEGT:** signierter Auftrag+Annahme, Testprozessinstanz, unabhängiger Write/Return, Parentlink und Referenzprüfung in einem Archiv. | Bausteine nicht neu, andere Kombinationen plausibel; technische Neuheit/Markt-Alleinstellung **UNBEKANNT** |
| Explizite Identitäts-/Nachweisgrenzen | **BELEGT:** Wrapper/Client/Account/Provider getrennt, unbekannte und unvollständige Fälle separat. | Merkmal dieses Bestands, kein Beweis, dass andere Systeme es nicht leisten |
| Loss-/Referenzgate vor Skalierung | **BELEGT:** alte Fehlversuche erhalten, finales Scopegate und 99 eindeutige Ketten mit Originaldaten. | Tetragon dokumentiert bereits Verlustmetriken; keine überlegene Erfassung behauptet |
| Inhaltsarme Wirkungsnachweise | **BELEGT** im Archivscope: Struktur-/Objekt-/Zeit-/Signaturdaten ohne Prompts, Bearertokens/private Keys. | Minimierung beweist keine Authentisierung/Kausalität/Datenschutzsicherheit; Metadaten bleiben sensibel |

Offene Fragen aus dem Bestand, ohne neue Forschungsphase:

1. **UNBEKANNT:** externe Sitzung→konkrete Antwort→Job; Account-/Clientbelege
   füllen diese Lücke nicht.
2. **ungeprüft:** Dauer-Enrolment, Rotation/Widerruf, Keyweitergabe,
   gemeinsame Prozesse und kompromittierte Trustanker.
3. **ungeprüft:** allgemeiner Live-Delegationsvalidator, verteilte/neu gestartete
   Verifier, persistente Replay-/Recoveryregeln; A4-Negativpfad ist begrenzt.
4. **UNBEKANNT:** Vollständigkeit außerhalb des VFS-/Objekt-/Zeit-Scope und
   Crashpersistenz; fehlende Events sind kein Wirkungsfreiheitsbeweis.
5. **UNBEKANNT:** andere Kernel/Architekturen, mehrere Nodes, Langzeitbetrieb,
   reale Modellworkloads und Kapazität über die einmalige 100er-Kohorte.
6. **ungeprüft:** Gesamtintegration mit Vergleichssystemen, exportierbare
   Standardschemata und ein gemeinsamer Ressourcenbenchmark.
7. **UNBEKANNT:** externe unabhängige Reproduktion/Audit und Markt-/Forschungs-
   neuheit; vollständige Literatur-/Patent-/Marktprüfung außerhalb dieses Umfangs.

Der Bestand trägt einen Forschungsnachweis einer **lokalen kontrollierten
Delegations-/Wirkungskette**. Eine Positionierung als möglicher Verbindungs-
und Analysebaustein neben bestehenden Identitäts-, Kerneltelemetrie-,
Observability- und Signatursystemen ist daraus ableitbar. Produktions-,
Sicherheitszertifizierungs- oder Überlegenheitsfreigabe folgt nicht.
Archivierte Qualität: zweimal 708 Tests bestanden, 25 neue Offline-Positionen;
Gesamt-Ruff: 16 historische Befunde, kein grüner Gesamt-Ruff. Quelle:
`a4-final-runs/2026-10-12/quality/summary.json`. Keine Tests dieser Analyse.

## 8. Quellenregister und Bestandsschutz

Alle folgenden offiziellen öffentlichen Quellen wurden am **2026-10-12**
abgerufen. `latest`-/`main` sind veränderliche Dokumentationsstände, keine
installierten eingefrorenen Produktversionen. Werbe-/Performanceversprechen
werden nicht übernommen. Die alte OTel-Agentenspans-Seite verweist auf das
neue offizielle GenAI-Repository; verwendet wurde dessen vorhandene Originaldatei.

| Kennung | Quelle mit URL | Abruf |
| --- | --- | --- |
| S1 | [SPIRE Concepts][S1] | 2026-10-12 |
| S2 | [SPIFFE Workload API][S2] | 2026-10-12 |
| S3 | [SPIRE Agent / Delegated Identity API][S3] | 2026-10-12 |
| S4 | [SPIFFE WIT-SVID, Incubating][S4] | 2026-10-12 |
| T1 | [Tetragon File Access Monitoring][T1] | 2026-10-12 |
| T2 | [Tetragon gRPC API][T2] | 2026-10-12 |
| T3 | [Tetragon Metrics][T3] | 2026-10-12 |
| T4 | [Tetragon Threat Model][T4] | 2026-10-12 |
| T5 | [Tetragon Container Deployment][T5] | 2026-10-12 |
| O1 | [OTel GenAI Agent-/Frameworkspans, Originaldatei][O1] | 2026-10-12 |
| O2 | [OpenTelemetry eBPF Instrumentation][O2] | 2026-10-12 |
| O3 | [OBI Security/Permissions/Capabilities][O3] | 2026-10-12 |
| O4 | [OpenTelemetry Baggage][O4] | 2026-10-12 |
| O5 | [OpenTelemetry Collector Scaling][O5] | 2026-10-12 |
| G1 | [Sigstore Security Model][G1] | 2026-10-12 |
| G2 | [Cosign Signing Blobs][G2] | 2026-10-12 |
| G3 | [Cosign In-Toto Attestations][G3] | 2026-10-12 |
| G4 | [Cosign Signature-/Bundleverification][G4] | 2026-10-12 |
| G5 | [Cosign Custom Components/Trustroots][G5] | 2026-10-12 |

Ausschließlich dieser additive Bericht wird versioniert. Die 642 Dateien der
Forschungsbasis einschließlich Code, Specs, Hypothesen, Fehlern und Original-
messungen bleiben unverändert. Keine Experimente, VM-Starts, Installationen,
Codeänderungen, Agentenaufträge oder Folgephase. Commit/Push nur auf den
benannten eigenen Analysebranch; kein Merge und keine PR-Freigabe.

[EN]: PLAN-A1-NATIVE-RESULT-20261011.md
[E1]: PLAN-A1-LINUX-EXPERIMENT-RESULT-20261012.md
[E2]: PLAN-A2-LINUX-IDENTITY-RESULT-20261012.md
[E3]: PLAN-A3-LINUX-REAL-AGENTS-RESULT-20261012.md
[E31]: PLAN-A31-SESSION-JOB-RESULT-20261012.md
[E40]: PLAN-A4-DELEGATION-RESULT-20261012.md
[E41]: PLAN-A4-COMPLETION-RESULT-20261012.md
[E4]: PLAN-A4-FINAL-RESULT-20261012.md
[EP]: PLAN-ABC-FORSCHUNGSPLAN-20261011.md
[ER1]: a4-final-runs/2026-10-12/phase1/evaluation.json
[ER2]: a4-final-runs/2026-10-12/phase2/independent-join.json
[ER3]: a4-final-runs/2026-10-12/phase2/capture.jsonl
[ER4]: a4-final-runs/2026-10-12/phase2/trial.jsonl
[CR]: https://github.com/landjunge/agent-authority-lab/blob/3a5e15666fe37d28d77f6c5b63276de8cda250c2/research/a4_scale/registrar.py#L224
[CK]: https://github.com/landjunge/agent-authority-lab/blob/3a5e15666fe37d28d77f6c5b63276de8cda250c2/research/a4_scale/kernel.py#L17
[CL]: https://github.com/landjunge/agent-authority-lab/blob/3a5e15666fe37d28d77f6c5b63276de8cda250c2/research/a4_completion/lifecycle.py#L71
[CJ]: https://github.com/landjunge/agent-authority-lab/blob/3a5e15666fe37d28d77f6c5b63276de8cda250c2/research/a4_scale/join.py#L66
[CN]: https://github.com/landjunge/agent-authority-lab/blob/3a5e15666fe37d28d77f6c5b63276de8cda250c2/research/a4_scale/registrar.py#L334
[CJN]: https://github.com/landjunge/agent-authority-lab/blob/3a5e15666fe37d28d77f6c5b63276de8cda250c2/research/a4_scale/join.py#L306
[CP]: https://github.com/landjunge/agent-authority-lab/blob/3a5e15666fe37d28d77f6c5b63276de8cda250c2/research/a4_completion/probes.py#L7
[S1]: https://spiffe.io/docs/latest/spire-about/spire-concepts/
[S2]: https://spiffe.io/docs/latest/spiffe-specs/spiffe_workload_api/
[S3]: https://spiffe.io/docs/latest/deploying/spire_agent/
[S4]: https://spiffe.io/docs/latest/spiffe-specs/wit-svid/
[T1]: https://tetragon.io/docs/getting-started/file-events/
[T2]: https://tetragon.io/docs/reference/grpc-api/
[T3]: https://tetragon.io/docs/reference/metrics/
[T4]: https://tetragon.io/docs/threat-model/
[T5]: https://tetragon.io/docs/installation/container/
[O1]: https://raw.githubusercontent.com/open-telemetry/semantic-conventions-genai/main/docs/gen-ai/gen-ai-agent-spans.md
[O2]: https://opentelemetry.io/docs/zero-code/obi/
[O3]: https://opentelemetry.io/docs/zero-code/obi/security/
[O4]: https://opentelemetry.io/docs/concepts/signals/baggage/
[O5]: https://opentelemetry.io/docs/collector/scaling/
[G1]: https://docs.sigstore.dev/about/security/
[G2]: https://docs.sigstore.dev/cosign/signing/signing_with_blobs/
[G3]: https://docs.sigstore.dev/cosign/verifying/attestation/
[G4]: https://docs.sigstore.dev/cosign/verifying/verify/
[G5]: https://docs.sigstore.dev/cosign/system_config/custom_components/
