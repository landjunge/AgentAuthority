# Laufzeitgrenze und begrenzter nativer Messaufbau

**Vor Umsetzung dieses Zusatzwegs, 7. Oktober 2026.** Der ursprüngliche
[Bauplan](OBSERVER-REAL-RUN-PROTOTYPE-PLAN-2026-10-07.md) bleibt unverändert.

## Belegter Anlass

Der eingefrorene Sechs-Fall-Aufruf wurde versucht: sechs gestartete CLI-Prozesse,
null belegte Modellläufe, null Werkzeugmeldungen, jeweils erfolgloser Prozessabschluss.
Ein Wiederanlauf des ersten Falls bestätigte denselben Startfehler. Danach wurde
das Panel mit den im vorhandenen CLI-Quellsnapshot dokumentierten temporären
`sqlite_home`-/`log_dir`-Overrides erneut versucht: wieder sechs Prozesse,
null Modell-/Werkzeugereignisse. stderr wurde nicht archiviert; Diagnose fand
generische Read-only-Dateisystemfehler. Authentisierung/Modellzugriff damit nicht
geprüft, nicht als fehlend behauptet. Kein HOME/CODEX_HOME, Credential oder Sandbox
wird dafür überschrieben, kopiert oder umgangen.

Das ist ein belegter Bedarf für einen tatsächlich verfügbaren Agentenzugang
zur ausdrücklich beauftragten realen Messung; kein neues Forschungsproblem.
Die ursprünglichen CLI-Hypothesen bleiben ohne reale CLI-Daten INCONCLUSIVE.

## Eng begrenzte Alternative vor deren Lauf

Die hier verfügbaren nativen Codex-Collaboration-Agenten können reale lokale
Terminalwerkzeuge ausführen. Sechs neue, getrennte Agentenkontexte bekommen nur
ihre jeweilige Mikroaufgabe. Ein lokaler Unix-Socket-Versuchsdriver führt das
bereitgestellte harmlose Werkzeug für diese Aufgaben aus. Er erfasst tatsächlichen
Werkzeugrückkehrstatus, lokale Zielproben und getrennte Werkzeugreferenzen.
Keine Rohprompts, Antworten, Argumente, Fehlermeldungen oder fremden Dateien im Archiv.

Der Versuchsleiter meldet dem Driver den tatsächlich empfangenen Agentenabschluss.
`native_end` bedeutet **diesen Empfangspunkt**, keinen physischen Executor- oder
Remote-Stopp. Im Nachher-Fall wartet das gestartete Kindwerkzeug auf diesen
Endpunkt, legt danach das Ziel real an und begrenzt die Anlagezeit unabhängig.
Kein nachträglich erfundener Prozessendzeitpunkt. `native_end.value=true` meldet
abgeschlossene Agentenkommunikation, nicht Werkzeugerfolg oder Wirkung.

Für diesen Aufbau lautet die Zeitfrage `appearance_vs_native_end`; sie wird nicht
als Messung von `appearance_vs_cli_end` ausgegeben. Die beiden anderen Behauptungen
(Status allein bzw. kleine inhaltsfreie Sicht für Zielzustand) werden separat für
diesen Aufbau bewertet. Dasselbe Sechs-Fall-Panel, dieselben fünf begründeten
Beobachtungsangaben, dieselbe getrennte Referenz und Feldablation; keine Graphen,
Empfänger-/Rollen-/MCP-/Fremdproduktintegration oder neuen Pflichtdaten.

Die Referenz wird um syscall-nahe Vor-/Nach-Zeitgrenzen präzisiert: Überlappung
mit Zielsnapshot-Intervall oder Endpunkt bleibt unbeurteilbar. Nachträglicher
Zielzustand bestätigt nicht allein eine frühere Beobachtung. Das setzt den
Methodencheck um und verändert keine Hypothese.

Der Driver ist ein ausdrücklich beauftragtes Forschungswerkzeug zum Ausführen
dieser eigenen Aufgaben, nicht eine Befugnis der AA-Auswertung. Lokale Aufnahme
belegt nur diesen instrumentierten Weg. Native Callback-/Laufzuordnung wird vom
Versuchsleiter beobachtet, nicht kryptografisch authentisiert. Andere Aktionen
der Agenten und uninstrumentierte Kanäle sind nicht vollständig erfasst.
Scheitert auch dieser reale Zugang oder fehlen Referenzen, bleibt das sichtbar.
Die Alternative wird vor Implementierung/Agentenläufen committed und gepusht.
