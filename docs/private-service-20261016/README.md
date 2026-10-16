# Ausführbarer privater Testdienst – Fortsetzung vom 16.10.2026

Der Dienst verbindet die vorher getrennten Bausteine jetzt tatsächlich:
HTTP-Enrollment mit unabhängig gepinntem Testroot und Besitzprobe → signierter
Auftrag → exakte signierte Annahme → dauerhaft beanspruchter Workerauftrag →
frische A2/A4-Testidentitäten in der isolierten VM → signierte Delegation mit
beiden API-Digests → unabhängiger Kernelwrite → HTTP-Nachweisaufnahme → dauerhafter
dienstsignierter Bericht → authentisierter Abruf nach API-Neustart.

[Normativer API-Vertrag und Abnahmen](../PRIVATE-SERVICE-API-v1.md),
[OpenAPI 3.1](../PRIVATE-SERVICE-OPENAPI-v1.json),
[Implementierung](../../research/private_service/),
[Vertragstests](../../tests/test_private_service.py).

## Tatsächlicher Nachweis

Der erfolgreiche frische End-to-End-Lauf
`b3e86d8b3b4ce9494fb68e7036aba484` enthält einen 16-Byte-Write, zwei kontrollierte
Testprozesse und genau eine innere Delegation/Annahme. Alle **28 Dienstchecks**
bestanden, alle **23 kritischen Verlustwerte** gemessen null. Die unveränderte
historische A4-Auswertung dieses Laufs besteht ebenfalls mit 26 Checks.
[HTTP-Transkript mit 25 Anfrage-/Antwortpaaren](live-exchanges.json),
[separat vor Ausführung gespeicherte Pins](live-dispatch-pins.json),
[Original-Rohdaten und gespeicherter Befund](live/),
[erneuter verifizierter Abruf nach Neustart und Pfadreparatur](restarted-client-report.json).

Die live verwendeten äußeren Auftraggeberkeys sind kontrollierte API-Testkeys.
Sie werden nicht als Linuxprozessidentität ausgegeben. Die innere A4-Kette hat
frische eigene Schlüssel und Besitz-/Kernel-/Prozessbindungen. Der signierte
innere Job trägt exakt die Digests des äußeren Auftrags und der äußeren Annahme.
Die Provider-/Modellsitzung bleibt UNBEKANNT. Eine Signatur allein belegt keine Wirkung.

Zwei frühere Integrationsversuche dieser Fortsetzung bleiben separat erhalten:

1. [Versuch 1](attempt-1-format-failure/): echte A4-Ausführung mit 26 bestandenen
   Checks/23 Nullverlustwerten; danach schlug die Paketaufnahme an den im
   eingeschränkten JCS-Profil nicht erlaubten Legacy-Rohdiagnosen/Fließzahlen fehl.
   Der Auftrag wurde UNBEKANNT; kein automatischer zweiter Dispatch desselben Jobs.
   Korrektur: exakte Legacy-Dateibytes als Base64 mit SHA-256 statt deren Daten
   in ein anderes Kanonisierungssystem umzuschreiben.
2. [Versuch 2](attempt-2-order-finding/): Aufnahme und Berichtssignatur funktionierten,
   aber das ursprüngliche A4-Verfahren erwartete bei zwei Lifecycleketten bereits
   sortierte Perfbuffer-Lieferung. Kernelzeitstempel zeigten vollständige korrekte
   Reihenfolge; Lieferung über CPUs war vertauscht. Der damalige widersprüchliche
   Bericht bleibt unverändert. Korrektur im neuen Dienstadapter: Prüfkopy nach
   Kernelstamp ordnen, keine Records löschen; historische Quellen unverändert.

Es gab in dieser Fortsetzung **drei** frische Zwei-Agenten-Versuche mit je einem
Write, davon einen vollständig positiven Dienstlauf. Das sind weder drei positive
Dienstläufe noch ein neuer 100-Agenten-Lauf. Der vorangegangene Auftrag und dessen
22-/195-Testnachweise werden nicht hinzuaddiert.

## Bedienung des vorhandenen lokalen Stands

Worktree: `/Users/landjunge/agent-authority-lab/.worktrees/hosted-qualification`.
Eigener Branch `codex/hosted-qualification-20261016`; kein Fork/Merge/Push/Deployment.
Die lokale Git-Konfiguration besitzt einen Auto-Push-Post-Commit-Hook. Lokale
Sicherungscommits dieses Auftrags verwenden dessen vorhandenen
`SKIP_POST_COMMIT_PUSH=1`-Schalter; es wird nichts veröffentlicht.

Der gespeicherte Lauf liegt in `.private-service-state/`. Dieses Verzeichnis ist
0700 und ausdrücklich gitignoriert; Config und Keys 0600. Es bleibt für den Nutzer
mit reparierten Start-/Keypfaden erhalten. Darin sind bewusst lokale Testcredentials,
keine Produktzugänge. Der Receiver wurde im Gegenfall bereits widerrufen. Sein
historischer Bericht bleibt lesbar und zeigt den heutigen Widerruf getrennt.
Keine manuelle Löschung der SQLite-Replaydaten bei Wiederverwendung dieses States.

Aus dem Worktree starten (sofern noch kein eigener Inspector läuft):

```sh
/Users/landjunge/agent-authority-lab/.venv/bin/python -m research.private_service.http \
  --state .private-service-state --config .private-service-state/config.json --port 8765
```

Der private Inspector ist unter `http://127.0.0.1:8765/` erreichbar. Für den Browser
benötigt man den lokalen `client`-Token aus `.private-service-state/config.json` und
die obige Laufkennung. Der Token gehört ausschließlich in das Passwortfeld,
nicht in URL/Chat/Archiv. Die Oberfläche zeigt verständliche Zustände und den
Prüfbericht; Details können aufgeklappt werden. Browseranzeige allein verifiziert
keinen unabhängig gepinnten Reportkey. Der CLI-Abruf prüft ihn aus der lokalen
Operator-Konfiguration, ohne Tokens oder Privatekeys auszugeben:

```sh
/Users/landjunge/agent-authority-lab/.venv/bin/python -m research.private_service.client report \
  b3e86d8b3b4ce9494fb68e7036aba484 --config .private-service-state/config.json
```

`status` statt `report` liest den Bearbeitungszustand. Ein weiterer Abruf führt
keine Aktion aus. Die Forschungs-VM kann dafür gestoppt bleiben.

## Einen neuen begrenzten Liveversuch wiederholen

Nur die vorhandene eigene Forschungs-VM, keine Installation oder Änderung von
Produktivhosts. Der Demo-Client erzeugt einen **neuen** privaten State (muss noch
nicht existieren), frische Signaturen/Keys/IDs und genau einen erlaubten Versuch:

```sh
LIMA_HOME=/Users/landjunge/.local/share/agent-authority-a1-linux-vm limactl start a1-research
/Users/landjunge/agent-authority-lab/.venv/bin/python -m research.private_service.demo \
  --state /tmp/aa-private-NEUE-EINDEUTIGE-KENNUNG \
  --output /tmp/aa-private-NEUE-EINDEUTIGE-KENNUNG-public.json --live
LIMA_HOME=/Users/landjunge/.local/share/agent-authority-a1-linux-vm limactl stop a1-research
```

Die Demo startet eine nur während des Versuchs lebende Loopback-API und verwendet
alle Datenrouten über echtes HTTP. Ohne `--live` prüft sie den Aufnahmeablauf und
die Unknown-Recovery ohne Kernelaktion. Bereits benutzte Statepfade werden nicht
überschrieben. Ein Fehler wird archiviert, nicht automatisch durch einen neuen
Liveversuch verdeckt. Private lokale Testkeys bleiben im angegebenen State zur
gezielten späteren Bedienung/Bereinigung; frische innere A4-Keys werden durch den
vorhandenen Harness exakt bereinigt. Nonsecret-Gastdateien erhalten Recoverypfade.

Für getrennten Dauerprozessbetrieb können API und expliziter Einzelworker denselben
lokalen State verwenden (`python -m research.private_service.runner --state DIR
--config DIR/config.json --url http://127.0.0.1:PORT`). Ein Workeraufruf bearbeitet
höchstens einen Job. Ein hostweiter Lock serialisiert die gemeinsame VM. Kein
Scheduler/Daemon oder öffentlicher Runner wird automatisch installiert.

## Qualifikation und verbleibende Grenzen

**61 lokale Prüfungen bestanden: 39 neue Dienstprüfungen und 22 übernommene
Speicherprüfungen.** Die finalen [Vertragstests](contracts-tests.log) und [JUnit-Daten](contracts-junit.xml)
prüfen tatsächliches HTTP, unabhängigen Rootpin/PoP, exakte Annahme, falsche
Signaturen, Replay/Idempotenz, Ablauf, Rollen/Mandanten/Objekte, Rotation/Widerruf,
fehlende/fehlerhafte echte Beobachtungsbelege und technische Fehler. Sechs getrennte
Prozesse liefern bei gleichzeitigem Auftrag genau ein Objekt und identische
Aufnahmeantworten. Echte Prozessabbrüche vor/nach Commit bleiben duplikatfrei.
Recovery eines bereits beanspruchten Workers führt keine zweite Aktion aus.
[Konkrete zusätzliche negative HTTP-Anfrage-/Antwortpaare](negative-exchanges.jsonl)
enthalten auch fehlenden Nachweis und technischen DB-Fehler. Alle Daten sind
synthetisch, ohne Bearertokens/Privatekeys.

**214 unveränderte Produkt-/A1–A4-Regressionen** bestanden separat:
[Log](regressions-tests.log), [JUnit](regressions-junit.xml). Sie enthalten gegenüber
der früheren Auswahl auch die bestehende Input-Bounds-/Native-Availability-Suite;
keine neue Gesamtsuite, Remote-CI, Last-/Menschenstudie oder unabhängiges Review.
Gezielte Ruff-/Formatprüfungen der neuen Quellen bestehen. Die Originalquellen
unter `research/a2_linux`, `research/a4_completion`, `research/a4_scale` sowie
Produkt-/Appquellen sind unverändert.

[Runnerabschluss](runner-final-state.json): keine eigenen Testprozesse, keine
aktiven Kprobes; VM regulär gestoppt. Gastkey-/Recoveryprotokolle liegen je Versuch
unter `cleanup.json`. Drei entbehrliche lokale States wurden nach Entfernung ihrer
exakt benannten Testkeys/Tokens mit Hashinventar in den macOS-Papierkorb verschoben:
[Wiederherstellung](scratch-recovery.json). Der aktive Inspectorstate und alle
anderen Worktrees/Anwendungen/Runnerpfade bleiben erhalten.

Dies ist ein nutzbarer privater Testdienst, kein fertiger öffentlicher Dienst.
Weiter offen: separater Debian-Zielrunner und Load/Attach-/Write-Qualifikation,
OS-/Privilegien-/Netztrennung, TLS/Serviceidentität/KMS/Root-/Reportkeyrotation,
aktive Kundenaufbewahrung/Löschung und Backup-/Restore-/Epochenbetrieb. Der aktuelle
State ist ein einzelner logischer Dienst mit eigenen Root-/Agenten-/Tokenkeys;
keine Kopie seiner Credentials in eine zweite Instanz. Die feste Audience bezeichnet
diese eine private Dienstinstanz, keine frei übertragbare Clusteridentität.
Für mehrere Instanzen muss zusätzlich eine eindeutige Operator-Audience konfiguriert
und separat qualifiziert werden. Externe Provider-/Modellidentität bleibt unbekannt.
Produktserver und macOS-App wurden nicht geändert, nichts öffentlich bereitgestellt.
