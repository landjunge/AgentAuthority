# P1: erster kontrollierter realer Lauf

Vorab-Festlegung, 9. Oktober 2026, vor Implementierung und Messung.
Auftrag: schlanker erster realer Lauf, unabhängiger Wirkungsbeleg, UNBEKANNT
bei fehlenden Belegen. Grundlage ist der unverändert übernommene
[Forschungsplan](OBSERVER-REAL-RUN-PROTOTYPE-PLAN-2026-10-07.md) aus dem
benachbarten Forschungs-Worktree. SHA-256 der Quelle:
`279af9826aaf52827205d57115c7dd66ca690534bf94964fdb61657e89d45ce5`.

## Frage und eingefrorene Hypothese

Kann eine inhaltsfreie Beobachtung eines einzelnen kontrollierten realen
Agentenaufrufs den Zustand eines vorher fehlenden lokalen Testziels am Ende
des Messfensters belegen, ohne CLI-/Werkzeugerfolg mit Wirkung gleichzusetzen?
Hypothese: ein separat erhobener, laufgebundener Dateibefund erlaubt diese
begrenzte Zustandsaussage; ohne gültigen Befund bleibt sie UNBEKANNT.
Ein einzelner positiver Lauf prüft weder die vollständige Sechs-Fall-Hypothese
des Forschungsplans noch allgemeine Agentensicherheit.

## Umfang

Ein Standardbibliothek-Skript, keine neuen Lab-/Produktmodule, UI, Gates,
Secrets, Rechte-, Ressourcen-, Rollen- oder Integrationssysteme. Keine Änderung
historischer Specs oder Tests. AA beobachtet; nur der Versuchsrunner startet
und beendet seinen eigenen begrenzten CLI-Prozess. Kein allgemeiner Agentenstopp.

Ein neuer temporärer Arbeitsordner, ein leeres Testziel, ein vom Runner
bereitgestelltes Werkzeug. Ein `codex exec --json --ephemeral` mit
workspace-write und approval never. Keine Überschreibung von HOME/CODEX_HOME,
Credentials oder bestehender Schutzregeln. Standardfall `write`; alternative
`noop`, `fail`, `write_fail` dienen separaten ausdrücklich gewählten Läufen.
Kein automatisches Panel oder nativer Ersatzlauf.

Das Werkzeug hält Aufrufe und seine tatsächliche Zielanlage als separate
Referenz fest. Ein unabhängiger Dateisensor prüft vor und nach dem CLI-Aufruf
den Zielzustand, ohne Werkzeugstatus, Agentenprosa oder Referenz zu verwenden.
Die Referenz wird erst nach der gespeicherten Analyse zur Bewertung geöffnet.
Unabhängigkeit meint hier getrennte Messwege im selben lokalen Vertrauensbereich,
keinen externen Audit oder Schutz gegen kompromittierten Host/Agenten.

Nur die fünf Planfelder `run`, `kind`, `value`, `t_ns`, `event` gelangen in
die Beobachtung. `value` ist boolesch; fehlende Messung erzeugt keinen Ersatzbeleg.
Kein Prompt, Antwort-, Command-, Fehler-, Pfad-, URL-, Provider-ID- oder
Credentialtext im Archiv. Rohströme werden begrenzt im Speicher verarbeitet.
Getrennte Buchführung hält ausschließlich Start-/Fehlerstatus, Zähler und
Referenzzustand. Metadatenprojektion ist keine allgemeine DLP-Garantie.

## Akzeptanz vor Implementierung

1. Zielzustand nur aus gültigen eigenen Anfangs-/Endproben mit passender
   Laufbindung; fehlende, falsch gebundene oder widersprüchliche Belege:
   UNBEKANNT. Identische Duplikate verändern die Aussage nicht.
2. Werkzeug-/CLI-Erfolg allein bleibt UNBEKANNT, auch bei erfolgreicher
   Abschlussmeldung. Misserfolg kann zusammen mit vorhandener Datei auftreten.
3. Ein belegter Agentenlauf erfordert beobachteten Modellabschluss und
   Werkzeugmeldung. Ein CLI-Prozessstart allein zählt nicht; Zugangsausfall
   wird als null belegte Agentenläufe dokumentiert. Zielzustand und
   Agentenlaufnachweis werden getrennt ausgewiesen.
4. Bezug zur tatsächlichen Werkzeuganlage wird nur bei gültiger getrennter
   Referenz bewertet; fehlende oder widersprechende Referenz:
   UNBEKANNT/unbeurteilbar. Keine Ableitung aus Modus oder Sollwirkung.
5. Aufzeichnungsfehler oder fehlendes CLI-Ende machen die Auswertung UNBEKANNT.
   Keine Rohdatenpersistenz, begrenzte Streams und Laufzeit, keine Fake-Events
   in realen Messarchiven. Tests mit künstlichen CLI-Events sind nur Unit-Tests.
6. Neue Tests für falschen Status, fehlende/konfligierende Belege,
   Referenztrennung, Projektion und reale lokale Prozessfehler. Bestehende
   Standardsuite unverändert zweimal, bekannte RC-Ausschlüsse sichtbar.

Keine Zeitordnungs-, Latenz-, Cancel-, Remote-, Herkunfts-, Identity- oder
Vollständigkeitsbehauptung. Der Snapshot sagt nur etwas über den benannten
lokalen Abfragepunkt. Historische RC-01–05, CB-01 und OOS-021 bleiben offen.
Nach Ergebnissen STOPP, keine automatische Erweiterung.

## Prozessgrenze

Der Forschungsplan verlangt Freeze-/Implementierungs-/Review-Commits samt Push.
Die Git-Metadaten dieses Worktrees liegen außerhalb der freigegebenen
Schreibpfade. Deshalb wird die Festlegung vor Code gespeichert und gehasht;
die vorgeschriebene Commitfolge ist hier nicht erfüllbar. Das ist eine
dokumentierte Prozessabweichung, keine Behauptung eines Commit-Freeze oder
externen Reviews. Ergebnisse stehen separat in P1-CONTROLLED-RUN-RESULTS.md.
