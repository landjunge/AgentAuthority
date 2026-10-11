# P10-01: erste installierbare Beobachterversion

Vorab festgeschrieben am 11. Oktober 2026, auf
`875e6b0fad5525b8352734533f298a7925315bb9`. Direkter neuer Nutzerauftrag:
„agent-authority in die produktphase bringen“. Dieser Schritt beginnt die
Produktphase mit einer nutzbaren lokalen Preview, nicht mit einer allgemeinen
Produktions- oder Sicherheitsfreigabe.

## Nutzerziel und Schnittstelle

Ein Anwender kann Agent Authority installieren und mit
`agent-authority inspect --thread THREAD_ID [--store STORE] [--format text|json]`
einen bestehenden ThreadDesk-Whiteboard-Verlauf lesend zusammenfassen.
Ohne `--store` wird `~/.threaddesk` gewählt. Ohne `--format` erscheint ein
verständlicher deutscher Textbericht. `--limit` begrenzt die Anzeige, nicht die
Analyse des ausgewählten lokalen Verlaufs. `--help` erklärt die Nutzung;
`--version` bezeichnet die Preview.

Der Bericht beantwortet: Welche Beiträge wurden gelesen? Welche Aufgaben sind
durch ihre gemeldeten IDs korrelierbar? Welche Übernahmen haben in den gelesenen
Beiträgen noch keinen späteren Ergebnisbeitrag? Wo sind die Daten unlesbar,
strukturell widersprüchlich oder während des Lesens verändert worden? Jeder
Befund trägt konkrete lokale Eintragsreferenzen und einen Inhaltsfingerprint.
Ein Ergebnisbeitrag ist eine Meldung und kein Vollzugs- oder Abnahmebeweis.

## Datenvertrag und Aussagegrenzen

Eingang: ausschließlich die JSON-Dateien des ausdrücklich ausgewählten
`STORE/whiteboard/THREAD_ID`-Verzeichnisses. ThreadDesk-IDs sind zwölf kleine
Hexzeichen. Begrenzung: höchstens10.000 JSON-Dateien, je höchstens65.536Bytes.
Dateien werden nur zum Lesen geöffnet; symbolische Eintragsdateien und
nichtreguläre Dateien werden nicht verfolgt. Der Adapter benötigt POSIX-
Verzeichnisdeskriptoren; macOS und Linux werden geprüft, Windows nicht abgenommen.
Während des Lesens beobachtete Änderungen ergeben einen unvollständigen Bericht.
Keine allgemeine atomare Snapshot- oder Vollständigkeitsgarantie.

Benötigte Felder: passende `id`/`thread_id`, ganzzahlige nichtnegative `ordinal`,
bekannte `entry_type`/`actor_type`, optionale kurze `task_id`. Ordinal ist eine
gespeicherte Reihenfolge, keine authentisierte Ursprungszeit. Eine mehrfach
vergebene Ordinalnummer wird sichtbar und bei betroffenen Aufgaben nicht zur
eindeutigen letzten Meldung aufgelöst. Doppelte JSON-Schlüssel, falsche IDs,
ungültige Feldtypen, fehlende Dateien und Lesefehler werden diagnostiziert.
Unvollständige Daten erzeugen keine Aussage „alles erledigt“.

Minimierte Ausgabe: feste Arten/Actor-Typen, Ordinal-/Eintragsreferenzen,
Datei-SHA256, Zähler, lokale Aufgabenaliase und feste Diagnosecodes. Keine Inhalte,
Prompts, Titel, Freitextnamen, rohen task/run/actor/instance/room-Labels,
Metadatenwerte, Pfade oder Nachrichtenbytes werden in den Bericht übernommen.
Es wird kein Archiv, Cache oder Exportziel automatisch geschrieben. Diese
Minimierung ist keine vollständige DLP- oder Anonymitätsgarantie.

Alle Eingangsbeiträge sind lokale archivierte Angaben. Ein kopiertes
`source_authenticated=true`, Actor-Label, Erfolgstext oder Receipt wird niemals
zu aktueller OS-Herkunft, Gesprächsidentität oder realer Wirkung.
`source_authenticated=false`, Identität/Herkunft/Wirkung UNBEKANNT und der
bezeichnete Archivumfang bleiben sichtbar. Die bereits vorhandene native
Empfangsschnittstelle bleibt getrennt; kein neuer Observer-Inferenzalgorithmus.

D-012 gilt: beobachten, analysieren, warnen. Keine ALLOW/DENY-Produktentscheidungen,
Rechte, Freigaben, Secrets, Budgets, Taskumschaltungen, Stop-Gates oder Aktionen
auf ThreadDesk. Warnungen ändern weder Aufgaben noch Agenten. Ein Prozess-Exit
bezeichnet nur die Ausführbarkeit/Vollständigkeit dieses Lesekommandos.

## Erlaubte Änderungen

- Neuer Namespace `agent_authority/`: lesender Adapter, Bericht und Kommando.
- Neue passende Tests unter `tests/test_product_observer.py`.
- `pyproject.toml`: Paketaufnahme, Konsolenkommando und Previewversion.
- `.github/workflows/ci.yml`: vorhandene verpflichtende Prüfungen zusätzlich
  auf den neuen Produktnamespace anwenden.
- README: produktbezogener Einstieg; neue Produktdokumentation.

Keine Änderung an vorhandenen `lab/`, `scripts/`, Tests, historischen
Dokumenten/Archiven oder ThreadDesk-Quellen. RC-/CB-/OOS-/P4-/Herkunftsgrenzen
bleiben nach ihrem tatsächlich geprüften Umfang erhalten.

## Konkrete Abnahme vor Veröffentlichung

1. Ein normaler Verlauf liefert korrekte gemeldete Arten, Aufgabenbezüge und
   Belegreferenzen; spätere Ergebnisse beseitigen nur den beschriebenen Hinweis
   auf fehlende Ergebnisbeiträge. Kein „Ergebnis gemeldet“ wird zu „Wirkung belegt“.
2. Fehlende/unlesbare/zu große/symbolische Eingänge, falsche Thread-/Datei-IDs,
   boolesche Ordinals, doppelte JSON-Schlüssel und Ordinalkollisionen bleiben
   sichtbar; ungesicherte letzte Meldungen werden nicht erfunden.
3. Beobachtete Änderungen während der Aufnahme kennzeichnen Unvollständigkeit.
   Ein angezeigtes Limit verdeckt keine Analysedaten; begrenzte Aufnahmen werden
   ausdrücklich als Auswahl gezeigt.
4. Inerte Canarywerte in sämtlichen Freitext-/Label-/Metadatenfeldern fehlen in
   Text und JSON. Gefälschte positive Authentisierungs-/Wirkungsangaben bleiben
   wirkungslos. Der ausgewählte Store bleibt nach tatsächlicher Ausführung
   bytegleich; kein Verzeichnis oder Hintergrunddienst wird angelegt.
5. Ein gebautes Wheel lässt sich in einer eigenen frischen Umgebung installieren.
   Das installierte Kommando funktioniert außerhalb des Repositorys; Hilfe,
   Version, Text/JSON, eine künstliche Fehlquelle und der tatsächliche ausgewählte
   Whiteboard-Verlauf werden ausgeführt und getrennt belegt.
6. Gezielte neue Tests und die bestehende Gesamtsuite zweimal bestanden;
   historische Abwahlen und Plattformskips getrennt. Ruff0.17.0, Format,
   Bandit1.9.4 und Mypy2.4.0 sind im bisherigen und neuen Namespace sauber.
   CI-Prüfungen bleiben verpflichtend. Veröffentlichung bindet sich an den
   tatsächlich geprüften Commit, mit Remote-Nachweis.

Danach ist ausschließlich P10-01 als lokale Produktpreview umgesetzt.
Eine ThreadDesk-Anzeige, laufende Beobachtung, weitere Konnektoren, Nutzertests
oder Produktionsauslieferung werden nicht aus diesem Schritt vorweggenommen.
