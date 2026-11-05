# BP-AA-01: Konsistente Aufgabenbindung im Beobachter

Auftrag: Nutzer vom 06.11.2026, einen freien Big-Plan-Punkt ohne Störung der
laufenden Sitzung bearbeiten. Teilpaket `BP-AA-BRIDGE-BINDING-20261106-V1`,
Bearbeiter Codex, Instanz `codex-01a1adf9-98b1-7b03-a991-d79ca1d3e688`.
Basis `75fb14e99a50b967b8624191f0178963c433fbd9`, eigener Branch
`feat/bigplan-aa-bridge-binding-20261106` im gleichnamigen AA-Worktree.

## Ergebnis

Der bestehende reine Helper `project_bridge_task` lehnt eine explizit
widersprüchliche `bridge_task_id` jetzt ab. Er prüft auch die Übereinstimmung
von `task_id` und `original_task_id`, wenn beide mitgeliefert werden. Fehlende
oder ungültige Core-IDs liefern einen begrenzten `ReadIssue` statt eines
ungefangenen `KeyError`. Gültige alte Aufrufe ohne explizite Bridge-ID bleiben
möglich; ursprüngliche und Core-Aufgabenkennungen bleiben getrennt.

Der bestehende KiraBridge-Handoffmanager am gelesenen Koordinationsquellstand
verwendet `packet["task_id"]` als ursprüngliche ThreadDesk-Aufgabe und
`task["id"]` als Bridge-ID beim Bind-Aufruf. Seine Auditmetadaten können sich
auch auf `first_task_id` beziehen. Deshalb muss ein Exporter beim Projizieren
eines Folgeturns dessen eigene Core-ID verwenden und darf eine Bindung für den
ersten Turn nicht still umschreiben.

## Abnahme

- Regression vor Korrektur: vier neue Fälle fehlgeschlagen, vier bestanden.
  Drei widersprüchliche Bindungen wurden akzeptiert; fehlende Task-ID führte
  zum `KeyError`.
- Final: **83 Tests bestanden**, ausschließlich
  `tests/test_workflow_projection.py` und `tests/test_workflow_rules.py`.
  Verwendet wurde die vorhandene Python-3.12-Testumgebung ohne Installation
  oder Änderung ihrer Abhängigkeiten.
- Ruff-Prüfung, Formatprüfung, gezielte strikte Mypy-Typprüfung und
  `git diff --check` bestanden.
- Ein gültiges Ereignis wurde durch den vorhandenen JSONL-Reader und den
  Reportaufbau zurückgelesen: IDs/Revisionen erhalten, Geheimnisfixture
  ausgeschlossen, Eingaben unverändert, `task_completion_proven=false`.

## Umfang und Fortsetzung

Dies schließt nur diesen Konsistenz-Teilpunkt von BP-AA-01 ab. Es ist kein
produktiver Exporter, keine Quellen-/Geräteauthentifizierung und keine
Remote-/Handy-/Windowsabnahme. Kein Dienst, keine VM, kein Terminalfenster
und keine fremde Agentensitzung wurde gesteuert oder neu gestartet.

Die DE/EN-Fachbeschreibung wurde angepasst. README, Webseite, Bilder und
Downloads brauchen für diesen internen Helperfix ohne neues Paket keine
Verfügbarkeitsänderung. Kein Release, Deployment oder produktives Update.

Nächster eigener BP-AA-01-Schritt: einen ausdrücklich autorisierten,
minimierten TD→KB→Agent→Rückgabe-Snapshot mit korrekt gebundenen einzelnen
Coreturns über den vorhandenen Beobachter prüfen. Die aktive Windows-Abnahme
bleibt ihrer bisherigen Sitzung zugeordnet.
