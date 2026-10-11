# Separates natives Empfangsmodul — 2026-10-11

Auftrag WB1668, bedingte reguläre Mergefreigabe WB1669/1670. Dieses Modul ist eine
optionale Agent-Authority-Diagnose. `Lab`, vorhandener Beobachter, `assess`,
Wirkungsanalyse, Adapter und ThreadDesk bleiben unverändert. Kein P10, keine
Produktions- oder allgemeine Sicherheitsfreigabe. D-012 bleibt Monitoring.

## Schnittstelle und belegte Aussage

`lab.origin.OriginReceiver(task_id)` wählt eine native Anbindung und liefert mit
`receive()` ein gemeinsames `origin-receipt-v1`-Ergebnis. Es gibt keinen Eingang,
der ein JSON-Archiv oder fremde `source_authenticated`-Angaben als Messung annimmt.
`lab.origin.transport.Transport` ist die austauschbare Empfangsschnittstelle.
Linux und Windows liefern ausdrücklich UNBEKANNT; ihre nativen Anbindungen sind
nicht implementiert oder getestet. Die vorhandene Paketstruktur und Tests bleiben
erhalten. Die bestehende PID-Prozessdiagnose wird nicht zur Nachrichtenauthentisierung
umgedeutet: sie ist keine Empfangsschnittstelle für einen Kernel-Audit-Trailer.

Auf macOS empfängt `MachTransport` eine begrenzte Inline-Mach-Nachricht mit ihrem
Kernel-Audit-Trailer. Erst nach dem tatsächlichen Empfang werden exakt dieselben
gehaltenen Nachrichtenbytes geparst und gehasht. `libbsm` liest PID, PID-Version,
UID und OS-Auditsitzung aus dem Trailer. PID-/Actor-/UUID-/Zeitangaben im JSON
werden nicht als OS-Beleg verwendet. Die Framing-Schnittstelle erlaubt solche
zusätzlichen Felder nicht; beliebiger Nachrichteninhalt bleibt opaker Inhalt.

Der Empfänger erzeugt beim Handshake eine neue lokale Protokollsitzung, einen
Frische-Challenge und eine monotone Frist. Die Antwort muss denselben vollständigen
Kernel-Audit-Token tragen. Sequenz eins wird genau einmal verbraucht. Ein anderer
Sender, alte/kopierte Sitzung, falscher Challenge, Replay, fehlender OS-Beleg oder
ungültiges Framing liefern UNBEKANNT. Höchstens acht Sitzungen, 4096 Framebytes,
2048 Inhaltsbytes; Empfangsaufruf höchstens 30 Sekunden plus begrenzte Replyzeit.
Gleichzeitige Aufrufe desselben Empfängers liefern `receiver_busy`, solange ein
Aufruf die Sitzung prüft und verbraucht. Tief verschachteltes JSON führt ebenfalls
zu UNBEKANNT. Empfangene Antwortrechte haben genau einen Bereinigungsverantwortlichen;
auch Fehler beim nativen Audit-Decoder werden vor der Rückgabe bereinigt.

`BELEGT` / `source_authenticated=true` gilt ausschließlich für den **unmittelbaren
lokalen Sender dieser Mach-Nachricht** und die frische lokale Empfangssitzung.
Ein Relay mit eigener Sitzung wird als Relay-Prozess beobachtet; die Herkunft
seines weitergeleiteten Inhalts ist damit nicht bewiesen. Der Auftrag wird vom
Empfänger konfiguriert und zugeordnet; `task_author_authenticated=false` verhindert
eine Behauptung über die Autorität dieses Auftragsnamens. Die OS-Auditsitzung ist
keine Codex-/Grok-Gesprächs-ID. Personen-, Modell-, ursprüngliche Autoren- und
Gesprächsidentität bleiben ausdrücklich UNBEKANNT. Eine Kopie dieses Receipts ist
kein neuer OS-Nachweis; lokale Archivhashes sind keine Verfasserauthentisierung.

## Explizite Nutzung

```sh
python -B -m scripts.native_origin receive --task mein-auftrag --count 2
python -B -m scripts.native_origin send --endpoint AUS_DER_READY_AUSGABE --replay < nachricht.txt
```

Der Empfänger gibt zuerst seinen Locator aus. Ein Locator wählt einen Endpunkt;
er authentisiert keinen Actor. Der macOS-Backend registriert vorübergehend einen
eigenen zufälligen Namen über das dokumentierte, aber veraltete `bootstrap_register`.
Er installiert keinen Launch-Agent, startet keine anderen Programme und entfernt
Registrierung und Ports beim Schließen. Der Client registriert keinen weiteren
Namen. Verfügbarkeit in anderen macOS-/Sandbox-Konfigurationen ist nicht abgenommen:
API-Fehler liefern UNBEKANNT. Es werden keine Rechte-, Secret-, Budget- oder
Gate-Funktionen hinzugefügt. Ein Diagnoseergebnis erlaubt oder verhindert keine
Agent-Authority-Aktion. Der Frische-Challenge ist kein Autorisierungscredential.

## Tatsächlicher Prüfstand

35 gezielte Tests, darunter vier tatsächlich ausgeführte macOS-Tests mit getrennten
Prozessen: Nachricht/Replay, kopierter Challenge aus anderem Prozess, Proxy mit
eigener Sitzung und Entfernung des Endpunkts. Die übrigen Tests simulieren
Session-/Framing-Gegenfälle und werden nicht als OS-Messungen ausgegeben. Ein
erzwungener PID-Reuse oder ein Wechsel des Programmimages wurde nicht durchgeführt;
der Vergleich umfasst den gesamten Audit-Token einschließlich PID-Version, ohne
daraus eine abgenommene Image-/Modellidentität abzuleiten.

Eine tatsächliche, von Codex in dieser Arbeitssitzung übergebene Auftragsnachricht
(365 Bytes) wurde zusätzlich nativ empfangen. Kernel-Sender PID `51434`,
PID-Version `2284290`, lokale Empfangssitzung `d5d68df807774e2ea0ab0922d62cb06a`,
Empfängerauftrag `authority-native-origin-module-20261011`. Inhalts-SHA256
`01c6c03e22b943b8b5aab40007b51cca327a6b7432a2733a161d34d1cca09228`.
Sender- und Empfängerausgaben stimmen überein; dieselben Wirebytes erneut geliefert
ergeben UNBEKANNT (`replayed_local_session`). Die beobachtete externe Codex-Thread-ID
ist lediglich Korrelationskontext, kein OS-authentisierter Gesprächsnachweis.

Archiv: `~/.threaddesk/artifacts/agent-authority/native-origin-module-20261011/`.
Es enthält den tatsächlichen Tool-/Empfangsnachweis, ursprünglichen Inhalt, Receipts,
Quellhashes, JUnit und vollständige Test-/Qualitätsausgaben. Gesamtsuite lokal:
500 bestanden, fünf unveränderte historische Ausschlüsse. Linux-CI überspringt
die vier neuen Mach-Tests sowie den bereits bestehenden Mac-Prozessdiagnosetest.
Neue Moduldateien Ruff 0.17 und Mypy 2.4 strict sauber; bestehende 29 Ruff-Befunde,
21 Format-Dateien und neun Mypy-Fehler werden nicht für erledigt erklärt. Der neue
UP017 aus PR35 bleibt ausdrücklich offen und wird hier nicht geändert.

Nach dem ersten veröffentlichten Kandidaten wurden Parser- und Rechtebereinigungs-
Fehler gefunden und korrigiert. Sieben Regressionen prüfen verschachteltes JSON,
Challenge-/Receipt-Sendefehler, gleichzeitigen Empfang sowie zwei Audit-Decoder-
Fehler. Die ursprünglichen Nachweise bleiben im Archiv erhalten; `v2/` enthält
die neuen Prüfungen und den tatsächlichen Empfang auf den korrigierten Runtime-Hashes.
Ein neuer Handshake mit denselben Inhaltsbytes ist eine neue unmittelbare Sendung;
das Modul weist keinen globalen Inhalts-Replay oder ursprünglichen Autor nach.
Das lokale Python 3.12 parst die geprüfte Tiefe noch; die Decoder-Erschöpfung wird
im zusätzlichen Fehlerfall ausdrücklich simuliert, nicht als nativer Absturz behauptet.
PR36 wurde trotz des zwischenzeitlich dokumentierten STOPs integriert (WB1675/1677).
Der vorliegende Korrekturstand benötigt eine eigene Prüfung auf aktuellem `master`;
der vorherige Grok-PASS ersetzt diese nicht.

Groks Gegenprüfung des tatsächlichen veröffentlichten Kandidaten sowie GitHub-
Pflichtchecks sind vor einem Merge erforderlich. Diese Dokumentation beschreibt
den Kandidatenprüfstand und behauptet deren Abschluss nicht vorweg. P4 und die
historischen RC-/CB-/OOS-Grenzen bleiben erhalten; PR17/19 sind unabhängige Aufgaben.

## Primärquellen

- [Apple Mach-Nachrichtenformat](https://raw.githubusercontent.com/apple-oss-distributions/xnu/main/osfmk/mach/message.h): Header, Inline-Framing, Audit-Trailer und Empfangsoptionen; zusätzlich die tatsächlich installierten SDK-Header.
- [Apple libbsm](https://github.com/apple-oss-distributions/OpenBSM): dokumentierte Audit-Token-Auslesefunktionen statt frei angegebener Senderfelder.
- [Apple Bootstrap-Schnittstelle](https://raw.githubusercontent.com/apple-oss-distributions/launchd/main/liblaunch/bootstrap.h): Registrierung/Lookup und ausdrücklicher Deprecation-Hinweis; keine installierte Hintergrundarchitektur.
