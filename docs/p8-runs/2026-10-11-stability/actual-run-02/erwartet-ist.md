# P7 Erwartet-Ist

Quelle: 64bf757ee7e32ca3df780b61a698466e2e299899
Befehl: /Users/landjunge/agent-authority-lab/.venv/bin/python scripts/p7_integration.py --parent /Users/landjunge/.threaddesk/artifacts/agent-authority/p8-stability-20261011/actual-run-02 --codex /Users/landjunge/.local/bin/codex --quelle-sha 64bf757ee7e32ca3df780b61a698466e2e299899 --timeout 120.0 --post-window 3.0
Umwelt: Python 3.12.13 macOS-15.7.4-x86_64-i386-64bit
Laufpfad: /Users/landjunge/.threaddesk/artifacts/agent-authority/p8-stability-20261011/actual-run-02/lauf
Nachlauf_Sekunden: 3.0
Timeout_Sekunden: 120.0
Laufnachweis: BELEGT (keine formale P7-Abnahme)
Grund: originaler_codex_exec
Modellnachweis: True
Herkunft: UNBEKANNT
Identitaet: UNBEKANNT

| Fall | Erwartet | Ist | Status |
| --- | --- | --- | --- |
| aktuell | PASS | PASS | PASS |
| fehlend | PASS | PASS | PASS |
| alt_geordnet | PASS | PASS | PASS |
| alt_zusatzfelder | PASS | PASS | PASS |
| gefaelscht_agentenlabel | PASS | PASS | PASS |
| gefaelscht_fd_flag | PASS | PASS | PASS |
| packet_ohne_messung | PASS | PASS | PASS |
| fd_format_keine_hostmessung | PASS | PASS | PASS |
| host_verifier | SKIP | SKIP | PASS |
| abgelaufener_kontext | UNBEKANNT | UNBEKANNT | PASS |
| replay | STOP | STOP | PASS |
| herkunft | UNBEKANNT | UNBEKANNT | PASS |
| identitaet | UNBEKANNT | UNBEKANNT | PASS |
| spaeteffekt | NACH | NACH | PASS |
| modellnachweis | belegt | belegt | PASS |

Grenzen bleiben offen: RC-01, RC-02, RC-03, RC-04, RC-05, OOS-021, CB-01, P4-Pytest-Cache.
Historische Referenzen bleiben erhalten. RC/CB-Reparatur: RemediationLab; OOS-Reparatur: FakeAdapter; P4: akzeptiertes ungeklärtes Restrisiko (WB1597).
D-012: beobachten, auswerten, warnen. Kein Recht, kein Secret, kein Budget, kein Stop.
