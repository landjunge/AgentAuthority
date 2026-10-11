# Agent Authority: lokale Produktpreview

Agent Authority liest einen ausgewählten ThreadDesk-Whiteboard-Verlauf und zeigt
gemeldete Aufgabenaktivität sowie strukturelle Warnungen. Es verändert weder
Aufgaben noch Agenten und trifft keine Ausführungsentscheidung.

Mit Python 3.12 oder neuer in einer eigenen Umgebung installieren:

```sh
python3.12 -m venv /tmp/agent-authority-preview
/tmp/agent-authority-preview/bin/python -m pip install /pfad/zum/agent-authority-lab
/tmp/agent-authority-preview/bin/agent-authority --version
/tmp/agent-authority-preview/bin/agent-authority inspect --thread THREAD_ID
```

Die Thread-ID hat zwölf kleine Hexzeichen. Die Datenquelle ist standardmäßig
`~/.threaddesk`; `--store /pfad/zum/store` wählt ausdrücklich einen anderen
lokalen Store. Für Werkzeuge gibt es `--format json`; `--limit 1` bis `--limit 100`
begrenzen nur die Anzeige. Ein lesbarer leerer Verlauf wird als leerer Verlauf
gemeldet, nie als Nachweis, dass keine Agentenaktivität stattgefunden hat.

Ein typischer Bericht nennt Aufgabenaliase wie A1, eine gemeldete Übernahme oder
ein gemeldetes Ergebnis sowie Belegreferenzen wie WB42 und die Eintrags-ID.
Damit kann der Anwender den Originalbeitrag in ThreadDesk wiederfinden.
JSON enthält zusätzlich den SHA256-Fingerprint der tatsächlich gelesenen Datei.
„Kein späterer Ergebnisbeitrag gelesen“ heißt genau das; es heißt nicht,
dass ein Agent noch läuft, gescheitert ist oder angehalten werden muss.

Quelle, Identität und reale Wirkung bleiben UNBEKANNT. Eine gespeicherte
`source_authenticated=true`-Angabe, ein Erfolgstext oder eine Kopie eines
nativen Receipts wird nicht zum aktuellen OS-Nachweis. Aufgabenbezüge beruhen
auf gemeldeten IDs. Lokale Aliase zeigen diese Korrelation, ohne rohe
Auftragsnamen, Inhalte, Prompts oder andere Labels auszugeben. SHA256 ist ein
Dateivergleich, keine Verfasserauthentisierung. Vollständige DLP/Anonymität ist
nicht behauptet.

Warnungen betreffen konkrete Eingangsdaten: doppelte Reihenfolgen, falsche
Thread-/Dateizuordnung, ungültiges JSON, fehlende Lesbarkeit oder beobachtete
Änderungen während der Aufnahme. Betroffene letzte Meldungen werden nicht als
eindeutig dargestellt. Ausgeblendete Aufgaben/Beiträge/Warnungen werden gezählt;
das Anzeigelimit reduziert die Analyse nicht.

Höchstens 10.000 JSON-Dateien mit je 65.536 Bytes werden gelesen. Das Kommando legt
keinen Store, Cache, Dienst oder Bericht an und folgt keinen symbolischen
Eintragsdateien. Exit 0 bedeutet einen vollständigen beobachteten Leseumfang;
Exit 2 bezeichnet unvollständige oder nicht lesbare Daten. Beide bedeuten weder
Sicherheit noch eine Freigabe oder Ablehnung. Quellen können nach dem Lesen
weitergeschrieben werden; keine atomare Snapshotgarantie. macOS/Linux sind der
erste Plattformumfang; der POSIX-Leseadapter ist unter Windows nicht verfügbar.

Dies ist Produktpreview 0.3.0a1, keine Produktions- oder allgemeine
Sicherheitsabnahme. D-012 sowie P4/RC/CB/OOS und unbelegte Herkunftsgrenzen bleiben
erhalten. Der [vorab veröffentlichte Vertrag](P10-01-PRODUKTVERTRAG-20261011.md)
definiert genau diesen ersten Schritt. Native Live-Herkunft, UI, weitere
Konnektoren und laufende Beobachtung sind gesonderte nächste Produktpunkte.
