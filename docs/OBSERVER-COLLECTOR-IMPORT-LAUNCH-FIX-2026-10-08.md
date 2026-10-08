# Collector C1–C7: Import-Startfehler unabhängig behoben

8. Oktober 2026. Dies ist **keine** neue C1–C7-Aufnahme und keine Änderung der
eingefrorenen Run-02-Daten oder des Run-02-Helfers.

## Reproduzierte Ursache

Aus dem Repository-Hauptverzeichnis gestartet:

```sh
python probes/collector_manipulation_c1_c7_run02.py --help
```

setzt Python den ersten Importpfad auf `probes/`. Das Top-Level-Modul
`observer_research.py` ist deshalb nicht auf dem Modulpfad. Der alte Start
bricht bereits bei `from observer_research import ...` ab:

```text
ModuleNotFoundError: No module named 'observer_research'
```

## Bestätigter Startweg

**Aus dem Repository-Hauptverzeichnis**, bei vorhandenen Python-3.12-Abhängigkeiten
(`pytest`, `hypothesis`):

```sh
python -m probes.collector_manipulation_c1_c7_run02 --help
```

Dieser Aufruf beendete sich im isolierten Linux/Python-3.12-Container erfolgreich
mit der argparse-Hilfe. Er importiert den unveränderten Helper korrekt und startet
wegen `--help` **keine** Collector-Messung. Die explizite Guard-Prüfung bestätigte,
dass kein Run-02-Experimentverzeichnis in `/tmp` angelegt wurde.

Der Regressionstest `tests/test_collector_launcher_import_smoke.py` verwendet
denselben Modulstart und prüft den Exitcode und die CLI-Hilfe, ohne `capture()`
auszulösen.

**Grenze:** Hiermit ist nur der frühere Import-/Launcher-Blocker beseitigt.
Die realen C1–C7-Messungen bleiben offen und dürfen nicht als Ergebnisse des
eingefrorenen Run 02 nachgeholt werden. Ein neuer Forschungsvertrag und eine
eigene Aufnahme sind weiterhin erforderlich.
