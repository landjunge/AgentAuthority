# Vorabvertrag: unabhängige lokale FD-Identitätsprüfung

Datum: 2026-10-08. Neuer, enger Forschungs- und Bauabschnitt vor der ersten
Implementierung. Ausgangscommit: `cc9a8d0f2184ca440155a691f2a64f791b50d175`.
Branch: `feat/observer-wb-automation`.

Die Verträge, Messdaten, Proben und Resultate der Runs 01, 02 und 03, die
Observerfunktion `infer_current_local_file_identity` in `observer_research.py`,
alle bestehenden Tests sowie die bestehenden CI-Workflows bleiben unverändert.
Dieser Abschnitt ist additive Forschung; er integriert keinen neuen
produktiven Authority-Gate und bewertet historische Antworten nicht um.

## Forschungsfrage und eingefrorene Hypothesen

Kann ein sauber per `exec` gestarteter separater Python-Interpreter über einen
UNIX-Domain-Socket genau zwei mit `SCM_RIGHTS` übergebene Deskriptoren selbst
mit `F_GETFD` und `fstat` vor und nach der Relationsermittlung prüfen, sodass
ein vertrauenswürdiger Broker ehrliche positive C1/C2-Aussagen bewahrt, die
falschen positiven C3/C4/C7-Aussagen aber nicht als sichere Identität
weiterreicht?

- **H1:** Für zwei aktuell gültige, reguläre, stabile und tatsächlich
  übergebene FDs liefert der unabhängige Verifier im Fall gleicher
  `(st_dev, st_ino)` **GLEICH**, sonst **VERSCHIEDEN**.
- **H2:** Nur wenn Verifiermessung, geordnete angebotene Packet-Paare und die
  ursprüngliche positive Observerantwort exakt zusammenpassen, gibt der
  vertrauenswürdige Broker `DIESELBE` oder `VERSCHIEDEN` aus. C1 und C2 bleiben
  dadurch positiv.
- **H3:** Widerspruch, unvollständige Form, technische Störung oder fehlende
  Bindung führt fail-closed zu `UNBEKANNT`. C3, C4 und C7 werden nicht falsch
  positiv weitergereicht; C5 und C6 bleiben `UNBEKANNT`.
- **H4:** Der Kanal authentisiert ausschließlich die Relation des konkret
  empfangenen FD-Satzes in diesem Prozessmoment. Er beweist nicht, dass ein
  böswilliger Sender die ursprünglich gemeinten Ressourcen übergeben hat.
  Diese Herkunftsgrenze darf weder durch einen grünen Test noch durch passende
  Packetwerte in eine Quellen-Authentizitätsbehauptung umgedeutet werden.

## Vertrauens- und Angreifergrenze

Unter Angreiferkontrolle stehen nur quellenseitige Werte beziehungsweise
lokale Ersetzungen von `fcntl.fcntl`, `os.fstat`, `os.uname`,
`subprocess.run`, `os.stat` sowie das angebotene Packet und daraus entstehende
Observerprojektionen. Nicht unter Angreiferkontrolle stehen in diesem Modell:

1. Linux-Kernel und UNIX/`SCM_RIGHTS`-Semantik,
2. der Broker samt Abgleichslogik,
3. der per neuem Interpreter und `exec` gestartete Verifiercode,
4. der direkte Socketkanal zwischen genau diesem Broker und Verifier.

Der Verifier wird nicht per Python-`fork` als weiterlaufender, bereits
importierter Collectorprozess betrieben. Ein Launcher darf intern
`fork`/`posix_spawn` verwenden, muss aber unmittelbar einen neuen isolierten
Interpreter `exec`en; keine quellenseitigen Python-Monkeypatches dürfen dort
weiterleben. Nur der Broker übergibt die zwei FD-Kopien per `SCM_RIGHTS`.

Anfrage und Antwort werden an Protokollversion, frische Zufalls-Nonce und eine
aus Nonce plus kanonischer Anfrage berechnete Request-ID gebunden. Der Broker
akzeptiert nur genau zwei empfangene FD-Rechte, eine vollständige gebundene
Antwort und einen erfolgreichen, fristgerechten Verifierprozess. Das ist eine
Bindung an den direkten lokalen Kanal, keine kryptographische Attestation
eines kompromittierten Brokers oder Kernels.

## Verifier- und Brokerentscheidung

Der Verifier prüft für jeden empfangenen FD zuerst `F_GETFD`, dann `fstat`,
verlangt eine reguläre Datei, wiederholt `F_GETFD` und `fstat` und verlangt
unveränderte geordnete `(st_dev, st_ino)`-Paare. Nur dann ist sein enges Urteil
`GLEICH` oder `VERSCHIEDEN`; andernfalls ist die technische Antwort
`UNBEKANNT`. PID, Eltern-PID, Interpreterpfad, Protokollbindung und die beiden
Vor-/Nachmessungen werden als prüfbare Laufmetadaten zurückgegeben. Sämtliche
empfangenen FDs und Socketenden werden auf jedem Pfad geschlossen.

Der vertrauenswürdige Broker validiert Packet und ursprüngliches
Observerergebnis selbst. Eine positive Endaussage ist nur zulässig, wenn:

1. Packetform und zwei geordnete reguläre native Paare vollständig sind,
2. Observer-`A` exakt `DIESELBE` oder `VERSCHIEDEN` ist,
3. Verifierstatus, Nonce und Request-ID gültig sind,
4. beide Vor-/Nachmessungen stabil und regulär sind,
5. die geordneten Verifierpaare exakt den angebotenen Packetpaaren entsprechen,
6. die aus den Verifierpaaren folgende Relation exakt Observer-`A` entspricht.

Jede Abweichung liefert `UNBEKANNT`. Weder Packet noch Observer können selbst
den Verifier ersetzen oder eine positive Aussage erzwingen.

## Kontrollierte C1-C7-Matrix

Die neuen Tests öffnen pro Fall neue eigene reguläre Dateien und leiten die
Verifierentscheidung nicht aus archivierter Run03-Ground-Truth ab. Für
gleiche Fälle werden zwei verschiedene numerische FDs derselben neu erzeugten
Datei geöffnet, für verschiedene Fälle je ein FD zweier neuer Dateien. Die
Packet-/Wrapperprofile reproduzieren nur die Fallstruktur:

| Fall | Echte übergebene FDs | Angebot/ursprünglicher Observer | Enderwartung |
|---|---|---|---|
| C1 | gleich | ehrlich gleich / DIESELBE | **DIESELBE** |
| C2 | verschieden | ehrlich verschieden / VERSCHIEDEN | **VERSCHIEDEN** |
| C3 | verschieden | konsistent falsch gleich / DIESELBE | **UNBEKANNT** |
| C4 | gleich | konsistent falsch verschieden / VERSCHIEDEN | **UNBEKANNT** |
| C5 | gleich | zeitlich widersprüchlich / UNBEKANNT | **UNBEKANNT** |
| C6 | gleich | Pflichtfeld fehlt / UNBEKANNT | **UNBEKANNT** |
| C7 | verschieden | fünf Quellen konsistent falsch gleich / DIESELBE | **UNBEKANNT** |

C3/C4/C7 dürfen nicht anhand von Fallnummern, archivierten Sollwerten oder
Payload-Literalen erkannt werden; ausschlaggebend ist ausschließlich der neue
FD-Kanal und der generische Abgleich.

## Konkrete Akzeptanzkriterien und Negativtests

1. Additives Modul unter `probes/`, additive isolierte Tests unter `tests/`;
   keine Änderung an eingefrorenen Proben, Observer, historischen Daten,
   vorhandenen Tests oder Workflows.
2. Linux/Python 3.12; neuer Interpreterprozess mit anderer PID; Tests zeigen,
   dass quellenseitige Monkeypatches der fünf erlaubten Schnittstellen die
   Syscallmessung des Verifiers nicht beeinflussen.
3. C1/C2 sind positive Endantworten; C3/C4/C5/C6/C7 sind `UNBEKANNT`; damit
   zwei brauchbare und null falsche Positive in dieser Matrix.
4. Ungültige/geschlossene FDs, nicht reguläre FDs, fehlender oder nicht
   startbarer Verifier, Timeout, Prozessfehler, zusätzliche/fehlende FD-Rechte,
   manipulierte Antwort, falsche Nonce/Request-ID und fehlende Handshakebindung
   liefern `UNBEKANNT`.
5. Vertauschte verschiedenartige FDs und Substitution durch andere nicht zum
   Packet passende FDs liefern `UNBEKANNT`. Original-FDs bleiben beim Broker
   offen; Verifierkopien, Socketenden und Kindprozess werden auch bei Fehler
   oder Timeout nachweisbar bereinigt.
6. Relevante Tests und die vollständige unveränderte Suite laufen in einem
   netzlosen, unprivilegierten Linux-Container aus dem vorhandenen
   `aa-run03-python:20261008`-Image, Python 3.12, `/tmp` als `tmpfs`, maximal
   2 CPUs und 4 GiB, ohne Host-Bind-Mount. Der Code gelangt nur per
   `git archive`/`tar` in einen temporären Container. Die vollständige Suite
   läuft zweimal grün; exakte Zahlen werden berichtet.
7. Vertrag, Implementierung/Tests und Ergebnisbericht sind getrennte normale
   Commits; jeder wird auf denselben Branch gepusht und mit `git ls-remote`
   gegen den lokalen HEAD geprüft.

## Vorab dokumentierte Grenzen und Stopregel

Auch bei vollständigem PASS bleibt ein böswilliger Sender in der Lage, andere
gültige FDs zu übergeben. Stimmen diese Ersatz-FDs zufällig oder absichtlich
mit dem manipulierten Packet überein, kann der Kanal den Austausch nicht von
der ursprünglich gemeinten Ressource unterscheiden. Nicht gelöst sind ferner:
kompromittierter Broker/Verifier/Kernel, Socket- oder Namespacekontrolle
außerhalb des Modells, Deskriptor-Neubelegung und TOCTOU außerhalb der engen
Vor-/Nachmessung, historische oder permanente Identität, Inhalt/Revisionsstand,
Pfadherkunft, andere Hosts und Netzwerkdateisysteme. `SCM_RIGHTS` beweist den
Besitz beziehungsweise die Übertragung eines aktuellen Kernelobjekts, nicht
dessen semantische Herkunft.

Achse A bewertet die Umsetzung dieses Vertrags. Achse B bewertet H1-H4 nur im
genannten Modell. Ein PASS ist kein allgemeiner Authentizitäts- oder
Sicherheitsnachweis. Nach Ergebnisbericht, Push und Remote-SHA-Abgleich endet
dieser Forschungsabschnitt; keine weitere Serie wird automatisch begonnen.
