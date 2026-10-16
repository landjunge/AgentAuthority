# Prüfbelege dieser Sitzung

Einstieg: `qualification-summary.json` und
`../HOSTED-SERVICE-ASSESSMENT-20261016.md`.

- `archive-summary.json`, `archive-reverification.json`: erneuter unveränderter
  A4-100er-Archivjoin; keine neue Kernelmessung.
- `live-gate/`: genau ein frischer Zwei-Testagenten-Lauf; Pins und Attempt vor
  Aktion, Originalcapture, signierte Registry/Delegation/Annahme, Orakel/Lifecycle,
  Evaluation und Cleanup. `harness-executed.py` ist der genaue ausgeführte Stand.
  Originale A4-Messquellen sind durch Quellhashes und Masterbasis gepinnt.
  Neuer Harness und Protokoll waren vor Versuch gehasht, aber nicht committed.
- `ledger-tests.log`, `ledger-junit.xml`: letzter 22er-Offline-Prüflauf.
  `*-first.*`: separater früher 18er-Lauf vor Ergänzungen, kein zusätzlicher
  unabhängiger Fallnenner. Der Ledger ist nicht an die Livekette angeschlossen.
- `existing-regressions.*`: 195 unveränderte Produkt-/A1–A4-Regressionspositionen.
  Die historischen `v0.2 composition summary`-Nullzähler im pytest-Abschluss
  stammen aus dem vorhandenen Hook und betreffen diese gezielte Auswahl nicht.
  Maßgeblich sind JUnit-Fälle/Failures/Errors und die tatsächlichen Einzelasserts.
- `lint.log`, `format.log`: gezielte neue Arbeitsquellen. `lint-initial.log`
  dokumentiert die vorherige automatisch korrigierte Importsortierung. Kein
  grüner repositoryweiter Lint-/Remote-CI-Lauf behauptet.
- `*-preflight.json`, `guest-postflight.json`, `vm-end-state.json`: eigene
  Forschungs-VM, Kernel/Mittel, keine Hostmounts; Probes entladen, VM gestoppt.
  Der Prozessscan enthält den `sudo`-Diagnoseelternprozess mit Suchstrings in
  dessen Argumenten. Er ist kein verbliebener Versuchsworker.
- `scratch-recovery.json`: sichere Verschiebung der eigenen synthetischen
  Testdatenbanken in den macOS-Papierkorb mit Hashes und Wiederherstellung.
  pytest-Symlinks wurden auf relative interne Ziele repariert und geprüft.
- `git-end-state.json`: Master unverändert sauber; lokale Appänderungen wie vor
  Auftrag erhalten. Neuer Worktree enthält ausschließlich zusätzliche Dateien.
- `original-source-hashes.json`, `origin-refs-at-session.txt`: gelesene Originale
  und lokale Remote-Ref-Momentaufnahme. Kein neuer Fetch in dieser Sitzung.
- `artifact-index.json`: SHA-256 der Belege und der neuen Quellen; Index selbst
  ausgenommen. Keine private CA, Agentenkeys, Providerzugänge oder Inhalte.

Geprüft mit vorhandener Python-3.12.13-venv unter
`/Users/landjunge/agent-authority-lab/.venv`, ohne Paketinstallation.
Reproduktion der Offline-Tests im Ergebnisworktree:

```sh
/Users/landjunge/agent-authority-lab/.venv/bin/python -B -m pytest tests/test_hosted_qualification.py
```

Ein neuer Liveversuch benötigt ausdrücklich einen neuen Ergebnisordner, neue
Registrierung und gestartete eigene Forschungs-VM; die vorhandenen Belege niemals
überschreiben. Diese Sitzung hat keinen weiteren Versuch oder Dienstbetrieb gestartet.
