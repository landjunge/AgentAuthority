# Agent Authority als gehosteter Dienst: Iststand und sequenzieller Bauplan

Prüfbasis: `edd40b959fc898edc06e790fe3672e748d7dbb2c`, 16. Oktober 2026.
Eigenständige Sitzung, keine Fortsetzung einer Tool-/Download-Sitzung.
Vorabumfang: [Qualifikationsprotokoll](HOSTED-QUALIFICATION-PROTOCOL-20261016.md).
Dies ist ein interner Bau- und Prüfplan, kein öffentlich verfügbares Angebot.

## Empfehlung und Nutzen

Ein kleiner Dienst ist technisch plausibel und die bestehende Wirkungskette ist
in der vorhandenen isolierten Ubuntu-Forschungsumgebung erneut praktisch belegt.
Der sinnvolle erste Umfang ist ein **kontrollierter Delegationsnachweis in einer
eigenen Linux-Testumgebung**: vorher registrierte Testidentitäten, signierter
konkreter Auftrag, signierte Annahme, unabhängige Beobachtung einer begrenzten
Aktion. Der Dienst erklärt je Kettenglied, was belegt, widersprüchlich,
unvollständig oder unbekannt ist. Damit lassen sich z.B. eine behauptete Übergabe,
ein fehlender Abschluss oder eine falsche Prozesszuordnung nachvollziehen.

Der Nutzen muss vor öffentlichem Angebot an solchen konkreten Fragen abgenommen
werden. Er besteht zunächst im überprüfbaren Testablauf für registrierte
Testidentitäten. Die Beglaubigung beliebiger externer KI-Agenten ist offen.
Ein bloßer Uploadprüfer wäre ein ergänzender Zugang zum vorhandenen Produktvertrag,
ersetzt aber die gewünschte unabhängig beobachtete Wirkungskette nicht.

Agent Authority bleibt nach D-012 Beobachter, Analyse und Warnung. Es erteilt keine
Rechte, Budgets, Freigaben oder Stopps. Der Forschungskoordinator startet und
beendet ausschließlich seinen vorher festgelegten synthetischen Versuch. Dieses
Testverfahren darf nicht als Produkt-ALLOW/DENY-/Autorisierungsdienst übernommen
werden. Betriebszugriffsschutz schützt die eigenen Dienstressourcen; er entscheidet
keine Kundenhandlungen. Die macOS-App bleibt eigenständig. ThreadDesk bleibt
ein optionaler Adapter. API und Browsergraph sind spätere Dienstzugänge.

## Belegter Iststand, nach Ebenen getrennt

| Quelle | Forschungsbefund / tatsächliche Implementierung | Integration und Dienstgrenze |
|---|---|---|
| [Produktvertrag](PRODUCT-OBSERVATION-CONTRACT.md), `agent_authority/` | Neutraler JSON-Verzeichnisreader, Snapshot, Aufgaben-/Widerspruchsanalyse und Text/JSON/HTML-Bericht. Begrenzte Aufnahme, Fremdfelder werden nicht übernommen. | Tatsächlich in App-Dateiimport integriert. `source_authenticated=false`; Identität, Herkunft, Abschluss und Wirkung bleiben unbekannt. Kein A1–A4-Liveanschluss, kein gehosteter Dienst. |
| [A1 Linux](PLAN-A1-LINUX-EXPERIMENT-RESULT-20261012.md), `ec82f2a` | Fünf positive Writes im Sechs-Fälle-Versuch; zusätzliche echte PID-Wiederverwendung sauber getrennt. Kernelstart und gehaltenes Objekt statt PID/Dateiname allein. | Ubuntu 24.04.5 / 6.8.0-142, privilegierter Collector. Nur synchrones `vfs_write` an regulärer Ext4-Datei. Entry-Verlustmetrik damals teilweise unbekannt. |
| [A2](PLAN-A2-LINUX-IDENTITY-RESULT-20261012.md), `98c274a` | Ed25519 je Testagent, CA-Enrolment, SCM_CREDENTIALS je Nachricht, pidfd, Start/Exec/Boot/Namespace; vier vollständige Testidentitätsketten und vier bewusst ungebundene Fälle, acht erfasste Writes. | Vertrauenswürdiger Starter registriert Testidentitäten. Schlüsselbesitz allein überträgt keine Kind-/Exec-/PID-Reuse-Bindung. Keine Provideridentität. |
| [A3](PLAN-A3-LINUX-REAL-AGENTS-RESULT-20261012.md), `28ff798` | Zehn reale Clientfälle, zwölf Kernelwrites, neun lokale Wrapperbindungen. | Null vollständige externe Agentenketten. Kontotoken, Threadclaim, Name oder zeitliche Nähe ersetzen keinen Sitzungsnachweis. |
| [A3.1](PLAN-A31-SESSION-JOB-RESULT-20261012.md), `7f1b612` | Zwei Codex-/Grok-Pipelines bis zum lokalen Linux-Write; native lokale Clientimage-/Jobbindung. | Kein Provider-signierter konkreter Job-/Antwortbeleg. Externe Provider-/Modellsitzung unbekannt. Die damaligen Providerproben werden hier nicht neu ausgeführt oder als heutiger API-Vertrag ausgegeben. |
| [A4 Delegation](PLAN-A4-DELEGATION-RESULT-20261012.md), `88087a6` | Zwei Testagenten, eine signierte Übergabe und ein 16B-Write. | Drei Verlustmetriken unbekannt; damaliges Gate unbekannt, keine gestarteten 100 Agenten. |
| [A4 Verlustkontrolle](PLAN-A4-COMPLETION-RESULT-20261012.md), `e5f4a0b` | Zusätzliche Verlustinstrumentierung implementiert. | Echter BCC-Attributfehler verlor den Abschlussbericht; dieser Lauf bleibt fehlgeschlagen/unvollständig. |
| [A4 Finale](PLAN-A4-FINAL-RESULT-20261012.md), `3a5e156` und Archiv | Frisches Gate; danach 100 kontrollierte simulierte Testagenten, 99 signierte Delegationen, sechs Stufen 2/4/8/16/32/37 und 99 beobachtete Writes à 16 Byte; 24 gemessene Nullverlustfelder. | Host/Test-CA/Root-Registrar/Kernel/gepinnter Code sind Trustbasis. Kein externer Auditor, keine Providerbeglaubigung. `research/a4_scale/join.py` ist auf dieses Setup festgelegt und kein generisches Backend. |
| [App-Abschluss 13.10.](/Users/landjunge/agent-authority-macos-design-20261012/docs/ABSCHLUSS-BUILD-DATENPFAD-20261013.txt) | Neuer fenstergeprüfter Build auf `edd40b9` plus lokalem `0e7498b` (`python -B`), Dateiimport und Grenzen geprüft. 75 Produkttests; 23 native Tests als übernommener Nachweis. | ES-Livecollector blockiert: Signieridentität, Team/Profile/Entitlements/Aktivierung fehlen; `es_result=5`. FDA allein schließt diese Lücken nicht. Keine Collector→Agentenidentität→Delegation-Livekette. App hier unverändert. |
| [PR17/19-Abgleich](RESEARCH-PR-ABGLEICH-20261011.md) | Historische Mechanismen/Belege bleiben gezielt nutzbar; zwei Forschungsinvarianten bereits adaptiert. | Historischer Gate-Service widerspricht D-012 und wird nicht Produktarchitektur. Alte Module haben konkrete Integrationskonflikte; kein pauschaler Merge. |

Groks [fertige Gesamtsichtung](/Users/landjunge/.local/state/agent-bridge/20261016T202259.368577Z/run.json)
ordnet alle 73 Remote-Zweige ein. Der lokale Ref-Index dieser Sitzung liegt in
[origin-refs-at-session.txt](hosted-qualification-20261016/origin-refs-at-session.txt).
Es gab hier keinen neuen Fetch; `origin/master=edd40b9` ist der zuletzt abgerufene
Stand. Diese Sitzung überprüft gezielt die Originale und die technische Eignung;
sie behauptet keine zweite unabhängige vollständige Zweigsichtung.

Wichtige Gegenbelege bleiben erhalten:

- CB-01 war im historischen Profil MISSED (`k=1`), RC-01–05 erreichten ihre
  modellierten Steuerungs-/Zustimmungssinks. OOS-021 beschreibt den historischen
  späten FakeAdaptereffekt. Es existieren inzwischen separate Reparaturmechanismen
  mit gebundenen Handles und Commit-Tickets: [Reparaturspezifikation](SECURITY-REMEDIATION-SPEC-20261011.md),
  `lab/remediation.py`, `Lab.commit_effect` und `tests/test_security_remediation.py`.
  Deren enger Fake-Lab-Erfolg ist keine Dienst-Autorisierung und ändert weder
  alte Negativdaten noch beweist er atomare entfernte Wirkungen.
- Die beiden Stress-10-Pakete scheiterten nach ihrem Vorabvertrag jeweils an
  einer Startbarriere. P4s historischer Writer bleibt unbekannt. Lokale P7/P8-
  Clientläufe sind keine extern beglaubigten Agentenidentitäten.
- E2 (`eb9ac58:docs/OBSERVER-E2-METADATA-MINIMIZATION-2026-10-07.md`) erhielt
  Marker in Actor, Resource, URL und Reason in 8/8 Metadatenfällen; PUBLIC/Hash
  löschten keinen Klartext. E3–E7 im selben Commit sind konstruierte Karten,
  keine Menschenstudie/Produktquote. E7 zeigt, dass auch eine abgeleitete Warnung
  fremde Projektbeziehungen verraten kann. Diese Originale wurden gelesen.
- Die git-archivierte JUnit-Teilmenge enthält **4120 Ausführungen / 708 verschiedene
  Testlabels** in sechs verschiedenen XML-Blobs. Überlappende Suites und Kopien
  zählen nicht als unabhängige Agentenversuche. Neue Zahlen unten werden nicht
  zu dieser historischen Zahl addiert.

## Neue isolierte Qualifikation dieser Sitzung

Originalbelege liegen unter [hosted-qualification-20261016](hosted-qualification-20261016/).
Die Originalarchive und Messquellen wurden nicht verändert.

1. **Archivprüfung:** Der unveränderte A4-Scale-Verifier berechnet exakt denselben
   Originaljoin: 99 vollständige Ketten, alle 19 Sammelchecks wahr. [Zusammenfassung](hosted-qualification-20261016/archive-summary.json),
   [neuer vollständiger Join](hosted-qualification-20261016/archive-reverification.json).
   Das ist Nachverifikation eines alten Versuchs, kein neuer 100er-Lauf.
2. **Neues Live-Gate:** Genau ein neuer Zwei-Agenten-Versuch in der vorhandenen
   Forschungs-VM, neue CA/Keys/Run/Instanzen/Datei, unveränderte A4-completion-
   Messquellen. Ubuntu 24.04.5, Kernel 6.8.0-142, BCC 0.29.1, Crypto 41.0.7,
   100 Hz; Root nur dort. Alle 26 Checks wahr, alle 23 kritischen Verlustwerte
   gemessen null. Ein beobachteter Write à 16 Byte; zwei Fork/Exec/Exit-Instanzen.
   [Evaluation](hosted-qualification-20261016/live-gate/evaluation.json),
   [Kernel-Rohdaten](hosted-qualification-20261016/live-gate/capture.jsonl),
   [Registrar/Orakel/Lifecycle](hosted-qualification-20261016/live-gate/trial.stdout.json),
   [vorherige Pins](hosted-qualification-20261016/live-gate/pins.json).
3. **Dienstspeicher-Prototyp:** [ledger.py](../research/hosted_qualification/ledger.py)
   qualifiziert vorhandene OpenSSL-Ed25519-Helfer mit operatorseitigen Trustpins,
   getrenntem Test-Enrolment, atomarer Rotation/Widerruf und SQLite-Transaktionen.
   Er speichert ausschließlich eine Aufnahmefeststellung über einen signierten
   Nachweisdigest. Er prüft keine echte Wirkung und ist nicht mit dem Live-Gate
   zu einer durchgehenden Dienstpipeline verbunden.
4. **Sicherheitstests:** 22 Offline-Prüfungen bestanden. Acht gleichzeitig
   gestartete Prozesse ergeben genau eine neue Feststellung und sieben identische
   bestehende Ergebnisse. Neustart erhält Nonce-/Idempotenzschutz. Zwei echte
   Prozessabbrüche vor/nach Commit führen zu sauberem Neuanlegen bzw. Wiederlesen.
   Tests prüfen außerdem fremden Trustpin, Mandantkontext, falsche Signatur,
   Ablauf/Domain, Rotation, Widerruf, atomaren Rollback einer ungültigen Rotation,
   minimierte Ausgabe und logische Löschung ohne Wiederanlage durch Replay.
   [Tests](../tests/test_hosted_qualification.py), [Log](hosted-qualification-20261016/ledger-tests.log),
   [JUnit](hosted-qualification-20261016/ledger-junit.xml). Vor Ergänzungen bestand
   ein eigener 18er-Lauf; beide Läufe sind getrennt archiviert, nicht 40 Fälle.
   Zusätzlich bestanden **195 unveränderte Produkt-/A1–A4-Regressionen**:
   [Log](hosted-qualification-20261016/existing-regressions.log),
   [JUnit](hosted-qualification-20261016/existing-regressions-junit.xml).
   Gezielte Ruff-/Formatprüfungen der neuen Arbeitsquellen bestanden. Keine neue
   Gesamtsuite/Remote-CI, kein unabhängiges Agentenreview behauptet.
5. **Aufräumen:** Exakte eigene private Schlüsseldateien entfernt, keine Schlüssel
   archiviert. Nichtgeheime neue Gastdateien wurden in den in
   [cleanup.json](hosted-qualification-20261016/live-gate/cleanup.json) genannten
   Recovery-Scope verschoben. `kprobe_events` danach leer. Der einzige Treffer
   im Prozessscan war der `sudo`-Elternprozess der Diagnose selbst, kein Worker.
   VM wieder `Stopped`; kein Produktserverkontakt, keine Pakete/Hostrechte geändert.
   Die beiden nicht mehr benötigten lokalen Test-DB-Verzeichnisse liegen im
   macOS-Papierkorb; ihre internen pytest-Verweise sind auf relative Pfade repariert.
   Exakte Pfade, Dateihashes und Rückverschiebung beschreibt
   [scratch-recovery.json](hosted-qualification-20261016/scratch-recovery.json).
   Der Worktree enthält die überprüfbaren Arbeitsergebnisse und bleibt erhalten.

Der ausgeführte Harness liegt bytegenau in `live-gate/harness-executed.py` und
sein Hash in `attempt.json`. Die anschließend formatierte, auf Set-Comprehension
bereinigte Arbeitsfassung ist kein zweiter Liveversuch. Die eigentlichen
historischen Observer-/Lifecycle-/Registrar-/Agentquellen blieben bytegleich.

Noch nicht dadurch qualifiziert: Debian 13 / 6.12.101+deb13-amd64, verteilte DB,
Strom-/Plattenausfall, Backup-Rollback, VM-Snapshot-Replay, Produktionslast,
HTTP-Authentisierung, echte Mandantenisolation im Betrieb oder physische Löschung.
Die lokale SQLite-SQL-Trennung prüft die Verwendung eines schon vertrauenswürdig
zugeordneten Tenantkontexts; sie ist kein getesteter Login/RLS-/Container-Schutz.

## Zielbetrieb und konkrete Ein-/Ausgaben

Erste Operation: `controlled-delegation-check`. Der angemeldete Nutzer wählt einen
vorinstallierten, versionierten synthetischen Ablauf (zunächst zwei Testidentitäten
und `write16`). Er liefert keinen ausführbaren Code, Shelltext, Pfad oder Trustkey.
Die Testidentitäten bezeichnen ausschließlich die vom Dienst registrierten
Testprozesse. Später kann ein externer Adapter einen eng validierten Job beschreiben;
das ergibt noch keine externe Agentenidentität.

Eingabe aus dem Kontrollsystem: opake Mandant-/Laufkennung, Szenarioversion,
Idempotenzkennung. Der Dienst erzeugt vorab Scope, Nonces, Keys und Zielobjekte.
Der Ausführungsort ist eine eigene isolierte Linux-VM auf separat qualifiziertem
Forschungshost. Dort laufen ausschließlich gepinnte Forschungsprogramme.

Ausgabe: persistenter Befund mit je Kettenglied Status, konkreter Aussage,
Belegreferenz/Hash, Vertrauensbasis, Zeit-/Quellbereich, Fehl-/Verlustgründen,
Verifierversion und Trustkatalogversion. Keine erfundene globale Vertrauenszahl.
Signaturprüfung, Instanzbindung und Wirkung sind einzeln sichtbar. Beim neuen
Gate sind Test-Enrolment, Übergabe, Annahme, Prozess und der konkrete VFS-Write
belegt; externe Provider-/Modellsitzung bleibt unbekannt.

| Status | Festgelegte Bedeutung | Beispiel / Abnahme |
|---|---|---|
| BELEGT | Die genannten voneinander getrennten Quellen tragen genau diese Aussage unter dem ausgewiesenen Trustmodell. | Gültige registrierte Schlüssel + konkrete signierte Übergabe/Annahme + passende Instanz + Kernelwrite im Scope/Fenster, alle erforderlichen Verlustkontrollen vorhanden. |
| WIDERSPRÜCHLICH | Vorhandene Belege widersprechen dem benannten Claim oder ein kryptografischer/Bindungscheck scheitert. | Gültige B-Signatur behauptet A; falscher Digest/Empfänger/Instanz. Keine Aussage über Absicht. |
| UNVOLLSTÄNDIG | Für die benannte Kette erwartete Glieder fehlen in einem vorliegenden Paket. | Annahme vorhanden, Completion/Write-Beleg fehlt; bewusst verweigerter/unterbrochener Ablauf. Positiv belegte Teilglieder bleiben sichtbar. |
| UNBEKANNT | Quelle/Trust/Abdeckung erlaubt die Aussage nicht. | Unqualifizierter Kernel, unbekannter Verlustwert, ungepinnte Kunden-CA, externe Sitzung. Fehlender Write ist kein Beweis für Wirkungsfreiheit. |

Fehlendes Paket und verlorene Erfassung werden getrennt angegeben. Ein
Verlust-/Trustproblem kann die Gesamtkette unbekannt machen, obwohl ein einzelner
beobachteter Kernelrecord als Ereignisfakt dokumentiert bleibt. Eine wiederholte
HTTP-Anfrage innerhalb des festgelegten Retryfensters liefert denselben Befund;
sie erzeugt keine zweite Ausführung. Nach Ablauf/Widerruf bleibt der historische
Befund über einen separat authentisierten Abruf lesbar; ein altes signiertes
Paket wird nicht erneut als frisch aufgenommen.
Nach unklarem Runnerabbruch wird die Aktion nicht automatisch wiederholt:
Der alte Lauf bleibt unvollständig/unbekannt, ein ausdrücklich neuer Testlauf
bekommt neue Laufkennung, Keys und Objekte. DB-Idempotenz ist keine Exactly-once-
Garantie über Datenbank und externen Ausführungsprozess.

Ergänzende spätere Operation `inspect-observation`: vorhandener neutraler Vertrag
innerhalb seiner Ressourcenlimits. Ergebnis sagt, was die gelieferten Dateien
behaupten. Kundenkeys und `source_authenticated`-Claims werden nicht zu Trustankern.
Diese Operation darf keine unabhängig belegte Wirkung aus Uploads erzeugen.

## Sicherheits- und Datenvertrag vor Dienstbau

| Bereich | Konkrete Regel / Wiederverwendung | Nachweis jetzt; zwingende weitere Abnahme |
|---|---|---|
| Trustanker / Enrolment | Betreiber kontrolliert vor Lauf registrierten CA-Pin und versionierten Katalog. Kunden mitgebrachte Keys niemals automatisch vertrauenswürdig. Registry bindet Mandant/Lauf/Host-Boot/Namespace/gepinnten Code; eigene Agentenkeys und frische Besitzprobe pro Prozessinstanz wie A2/A4. | Test-CA und falscher Pin getestet. Dienst-Control-Plane mit Adminidentität, Audit und geschütztem Signing-Key noch zu bauen; API-Upload darf Enrollmentmethode nicht erreichen. |
| Prozess und Auftrag | Vorhandene Domain-/Digest-/Sender-/Empfänger-/Start-/Exec-/Boot-/Namespacebindung, SCM_CREDENTIALS, pidfd, Nonces und Ablauf beibehalten. Jeder Folgejob bindet exakte Parent-Delegation/Annahme. | A1–A4-Archiv und neues Gate. Kein Austausch durch Namens-/PID-/Timingheuristik. Neue variable Kohorten verlangen eigenen Vertrag; Scale-Verifier nicht einfach freischalten. |
| Rotation / Widerruf | Neue Key-ID, nie Wiederverwendung alter ID; neues gültiges Enrollment und Deaktivierung des Vorgängers in einer Transaktion. Widerruf vor erneuter Aufnahme prüfen. Langzeitrootwechsel nur operatorseitig/out-of-band mit auditierter Pinmigration. | Testrotation/Widerruf/Restart und fehlerhafter Rotationsrollback geprüft. Rootwechsel, KMS/Recovery und Widerrufverteilung auf echte Worker noch zu testen. Historische Gültigkeit und heutiger Widerruf getrennt anzeigen; bei unbekanntem Kompromissbeginn keine pauschale historische Sicherheit. |
| Replay / Idempotenz | Eindeutige `(tenant, nonce)` und `(tenant, idempotency_key)`; Digest, Nonce und Ergebnis in derselben dauerhaften Transaktion. Gleiche Bytes→bestehender Befund, andere Bytes bei gleicher ID→Konflikt. Nach Löschung Merkposten statt Neuanlage. | Lokale SQLite-WAL/FULL-Prüfung, acht Prozesse und Abbrüche bestanden. Keine Mehrhost-/Stromausfallgarantie. Für Mehrhostbetrieb eigene transaktionale DB mit denselben Rennen/Crash-/Restoreprüfungen qualifizieren. |
| Mandanten | Tenant kommt aus geprüftem Authkontext, niemals aus freiem JSON allein. Alle Lookup-/Unique-/Löschschlüssel tenantgebunden; getrennte Objektbereiche, Pins, Runner und Ergebnislinks. Kein gemeinsames Trialverzeichnis; erste Fassung ein Lauf pro VM, seriell, nur Testdaten. | SQL-Kontexte/cross-tenant lookup geprüft. HTTP-Auth, direkte Objektzugriffe, Listing, Cache, Browserwarnungen und Fehler-/Timingkanäle noch zu prüfen. Kein Versprechen, alle Seitenkanäle zu beseitigen. |
| Betriebstrennung | Öffentliche API/Verifier unprivilegiert, ohne BPF/Root/Runnerkeys. Privilegierter Registrar/Collector nur im dedizierten Gast auf gesondertem Forschungshost. Langzeit-CA bleibt außerhalb des Gasts; Worker erhalten nur eigenen versiegelten Key-memfd. | Forschungs-VM ohne Hostmount/Agentforwarding geprüft. Separater Diensthost, Egressregeln, minimale Übergabekanäle, mTLS/Serviceidentität, Patch-/Alarm-/Backup-/Wiederanlaufverfahren fehlen. Keine Probes neben KI-Zentrale auf Produkt-VPS. |
| Evidenztransport | Aufnahme über vorher registrierten Runnerkanal; Manifest bindet Run, Boot, Codehash, Quellen, Sequenz/Ende, Hashes und Verluststatus. Geschlossene Pakete atomar veröffentlichen, nie halbfertigen Snapshot als vollständig anzeigen. | Live-Hostkanäle und separate Rohbelege geprüft. Diensttransport/Queue/atomare Paketschließung noch zu implementieren und durch Auslassung/Duplikat/Umordnung/Timeout zu prüfen. Ein kundenseitig signiertes Paket wird dadurch nicht unabhängige Erfassung. |
| Erhebung | Nur opake Tenant-/Run-/Testagent-/Objektkennungen, Key-ID/Publickey/Signaturen, Joboperation und Digest, Boot/Namespace, PID/Start/Exec, Dateiobjekt, Bytezahl/Return, begrenzte Zeit-/Verlust-/Quellpins. Keine Standarderfassung von Prompts/Gesprächen, freien Fehlertexten, realen Pfaden/URLs oder Arbeitsinhalten. | Prototyp verweigert Fremdfelder/Prompt und gibt nur sieben Befundfelder aus; Produktvertrag bereits minimiert. Feldinventur für tatsächliche Runner-/HTTP-/Proxy-/Fehlerlogs vor Betrieb verpflichtend. Auch Hashes/Zeiten/Beziehungsgraph sind Metadatenrisiken. |
| Aufbewahrung / Löschung | Vorgeschlagener erster Dienstvertrag: rohe synthetische Aufnahme nach erfolgreicher Paketprüfung höchstens 24h; Befunde 7 Tage; auf Wunsch früher logisch löschen. Replay-Merkposten bis Ablauf zugehöriger Schlüssel-/Request-Epoche plus maximalem Retry-/Uhrabweichungsfenster. Keine freie Wiederherstellung alter Nonces. | Logische Löschung und Replay nach Löschung geprüft. Noch keine automatische TTL/physische Löschung/Backupregel implementiert. Vor Fremdbetrieb Fristen final festlegen, verschlüsselte Speicher/WAL/Backups und Restore-Löschjournal prüfen. Keine Anonymität oder SSD-/RAM-Zeroisierung behauptet. |

Die angegebenen Aufbewahrungsfristen sind ein konkreter Bauvorschlag, keine schon
aktive Dienstregel. Für Replay-Merkposten ist ein explizites maximales Zeitfenster
zu definieren: erster Testvertrag Jobs 5s, Serviceaufnahme höchstens 60s,
Test-Enrolment höchstens 24h, keine Uhrtoleranz im Prototyp. Eine spätere Toleranz
und Retryfrist müssen in Ablauf- und Löschtests dieselben Werte verwenden.
Backup-Restore muss einen außerhalb des zurückgesetzten Bestands gehaltenen
Epoch-/Widerrufstand prüfen; ist dieser nicht verfügbar, neue Aufnahmen als
unbekannt behandeln und frisches Enrollment verlangen. Bestehende Befunde dürfen
als historische Artefakte erneut geprüft werden, ohne neue Ausführung auszulösen.

## Sequenzieller Bau-/Prüfplan mit Abnahme

Jede Stufe beginnt erst nach dokumentierter Abnahme ihrer Voraussetzungen.
Der heutige Stand erfüllt Teile der ersten Stufe, keinen fertigen Dienst.

1. **Iststand und isolierter Mechaniknachweis – diese Sitzung.** Originale,
   Archive und Appgrenzen abgleichen; Archivjoin und neues Zwei-Agenten-Gate;
   lokale Aufnahme-/Replay-/Trustproben. Abnahme: konkrete Originalbelege,
   konservative Unknowns, keine Produktänderung. Erfüllt im oben genannten Umfang.
2. **Separaten Zielrunner qualifizieren.** Bestehende Ubuntu-VM bleibt der
   nachgewiesene Referenzrunner. Für das Debian-Ziel zuerst ein separat
   bereitgestelltes Debian-13-System mit Kernel 6.12.101+deb13-amd64 und passenden
   vorhandenen BCC/Headers/BTF-Mitteln festlegen. Genau vorab geplante
   Compile→Load→Attach→kontrollierte Aktion→Verlust→Detach-Prüfung ausführen.
   Abnahme: 26 Komponenten-/23 Verlustprüfungen oder neu dokumentierter,
   gleich strenger Kernelvertrag, Originalfehler erhalten. Keine Ableitung aus
   Kconfig/BTF oder altem Ubuntu-PASS. Braucht es neue VM/Hostpakete/Privilegien,
   genauen Bedarf separat beauftragen lassen; Produktserver bleibt ausgeschlossen.
3. **Dienst-Verifikationsvertrag extrahieren.** Vorhandene A2/A4-Prüfungen als
   explizit versionierten Zwei-Agenten-Vertrag isolieren. Run-/Tenant-/Trustkontext
   kommt vom Kontrollsystem. Archivverifier bleibt unverändert historisch.
   Ausgabe je Kettenglied mit Beleg-/Quell-/Trustreferenz; keine Gesamtzahl 99
   oder `Agent000..099` außerhalb des Scale-Vertrags erzwingen.
   Abnahme: neues echtes Gate + Archivgleichheit + falscher Pin/Domain/Digest/
   Empfänger/Instanz/Boot/Namespace/Frist, fehlende und duplizierte Records,
   unbekannte/positive Verlustzähler ergeben konservative Befunde; keine gefälschte
   Signatur/Collectorquelle wird zu BELEGT. Kein freier Upload für Rootcollector.
4. **Persistenz und Schlüsselbetrieb integrieren.** Aus dem isolierten Ledger-
   Nachweis einen Dienstbaustein mit Schema-Migration, Uhrvertrag, Enrollment-
   Adminweg und auditierter Rotation/Widerruf entwickeln. Ausführungswunsch,
   Dispatch und Befundzustand getrennt; Recovery eines unklaren Dispatchs erzeugt
   keinen automatischen zweiten Lauf. Abnahme: Neustart, konkurrierende Worker,
   Widerruf während Intake, Commit-/Queue-Abbruch, Datenbankfehler, Restore und
   TTL/Löschung an tatsächlichem Zielspeicher. SQLite nur für einen nachgewiesenen
   lokalen Knoten; neue DB/Mehrhostbetrieb erneut qualifizieren.
5. **Privaten Ablauf vollständig verbinden.** Kontrollsystem→frische Registrierung
   →Runner→unabhängiger Collector→abgeschlossenes Paket→gewöhnlicher Verifier
   →persistenter Befund. Nur versionierter `write16`-Ablauf, eigene Images,
   keine fremden Programme. Abnahme: derselbe eine reale Write erscheint mit
   exakten Belegen im gespeicherten Bericht; Replay/Refusal/Unterbrechung und
   Runnerausfall bleiben korrekt unvollständig/unbekannt. Collector hat keine
   Rollen-/Agentenclaim-Orakeldaten als Quelle. Begrenzter RAM/CPU/Dauer/Bytes/
   Parallelität sowie garantierte eigene Probe-/Key-/VM-Bereinigung geprüft.
6. **Private API und anschließend Browsergraph.** Zuerst Auth und Tenantkontext,
   Run anfordern, Status/Befund abrufen und Befund löschen; danach Graph aus
   demselben Befundschema. Beispielrouten: `POST /v1/test-runs`,
   `GET /v1/test-runs/{id}`, `GET /v1/reports/{id}`, `DELETE /v1/reports/{id}`.
   Idempotency-Key Pflicht; nur Szenarioenum, kein Codefeld. Erst intern,
   kein öffentlicher Endpoint in dieser Sitzung. Abnahme: Tenant A erhält weder
   Bericht noch Metadaten/Fehlerdetails von B, IDs allein geben keinen Zugang;
   Parser-/Rate-/Byte-/Zeitgrenzen, XSS/Graphlabels, Warnungsprojektion und
   Löschung einschließlich Cache geprüft. App und ThreadDesk bleiben unabhängig.
7. **Begrenzter Pilot, später Angebot.** Erst nach dokumentierter Funktionsmatrix,
   Datenschutz-/Aufbewahrungsregeln, Betriebsverantwortung und Recoveryprüfung.
   Pilotfragen: Kann der Nutzer eine echte Übergabe von einem bloßen Claim,
   eine fehlende Aktion und eine unbekannte Provideridentität korrekt unterscheiden?
   Mehr Testagenten erst nach eigenem Last-/Verlustvertrag; alte 100 Agenten sind
   kein Dauerlast-/SLA-Beleg. Öffentliches Angebot und sämtliche Texte erfordern
   gesonderte ausdrückliche Freigabe nach vollständiger Vorlage. Hier keine
   Posts, Nachrichten, Veröffentlichung, PR, Push, Merge oder Deployment.

## Konkrete verbleibende Voraussetzungen

- Separater gehosteter Runner und dessen Betriebstrennung; Debian-Zielkernel
  braucht einen eigenen isolierten Load-/Attach-/Write-Nachweis. Die bekannte
  rein lesende VPS-Prüfung liefert diesen nicht. In dieser Sitzung kein VPS-Zugriff.
- Dienstvertrag/Adapter zwischen A4-Messung, persistenter Aufnahme und Bericht;
  heutiges Live-Gate und heutiger Ledger sind noch getrennte Prüfungen.
- Echte API-Authentisierung, Mandantentrennung sämtlicher Speicher-/Cache-/Graph-
  pfade, Schlüsselverwahrung/Rootrotation, Backup-/Restore-/Epochschutz und
  fristgerechte Löschung. Prototyp-Tests decken jeweils ausdrücklich nur Teile ab.
- Für beliebige reale Agenten weiterhin ein unabhängiger frischer Sitzungs-/Job-
  beweis des betreffenden Providers. Er ist keine Voraussetzung für den ehrlich
  benannten Testidentitätsdienst, bleibt aber Voraussetzung für stärkere Claims.
- Für macOS-Livecollector gesondert gültige Apple-Signier-/ES-Unterlagen und reguläre
  Freigaben sowie die noch fehlende Identitäts-/Delegationsanbindung. Das blockiert
  den eigenständigen Linux-Testdienst nicht; die vorhandene App bleibt erhalten.
