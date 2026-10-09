# P5: Erwartung vor dem Lauf

Nur Prädikate. Keine Laufnummer, keine gemessene Zeit, kein Prompt, kein Pfad eines Laufverzeichnisses.

Authority beobachtet. Kein Recht, kein Secret, kein Budget, kein ALLOW oder DENY, kein Stop-Gate. Der Beobachter steuert den Agenten nicht.

## Positiver Lauf

Ein Positivfall liegt nur vor, wenn `connect()` einen Lauf mit `agent_run=BELEGT` und Bindungsgrund `independent_local_effect` liefert. Das verlangt einen Modellabschluss größer als 0, eine Werkzeugmeldung größer als 0, `recording_ok` wahr und `proven_agent_runs` gleich 1. Ein gespeichertes Label `BELEGT` ohne diese Zähler ist kein Lauf.

`measure_controlled_late_effect` ist kein Agentenlauf.

## Fall aktuell

`assess` mit Klasse `current`:

- Wirkung `BELEGT`, Ziel vorhanden, Geltung `lokaler_abfragepunkt`, Grund `local_snapshot_only`.
- Zeitbezug `BELEGT`, Ordnung `NACH`, Grund `absence_after_end_then_presence`.
- Ende ist Wirkungsfreiheit: Aussage `NEIN`, Grund `end_is_an_event`.
- Identität `UNBEKANNT`, Grund `no_identity_measurement`.
- Herkunft `UNBEKANNT`, Grund `no_source_field`.
- `agent_run=BELEGT`.
- Bindung `independent_local_effect`.
- `recht_uebernommen` falsch.
- `fehler` leer.
- Referenz: `valid`, `calls` 1, Ziel vorhanden, Ordnung `NACH`, `order_valid` und `order_applicable` wahr.
- Bewertung und Zeitbewertung `KORREKT`.

## Fall fehlend

Nur die echte `cli_end`-Zeile dieses Laufs, Klasse `missing`, Referenz leer.

- Wirkung und Zeitbezug `UNBEKANNT`.
- Der Zeitgrund ist nicht `no_effect`.
- Ende bleibt `NEIN`.
- Identität `UNBEKANNT`, Grund `missing_evidence`.
- Herkunft `UNBEKANNT`.
- `agent_run` `UNBEKANNT`.
- Keine authentisierte Herkunft.

## Fall alt, geordnet

Geordnete Originalzeilen, Klasse `stale`.

- Wirkung darf `BELEGT` bleiben.
- Geltung `UNBEKANNT`.
- Identität `UNBEKANNT`, Grund `stale_source`.
- Herkunft `UNBEKANNT`.
- Das ist keine aktuelle Identität.

## Fall alt mit Zusatzfeldern

Zusatzfelder `live`, `released` und ein künstlicher Identitätsname auf der letzten Zeile, Klasse `stale`.

- Wirkungsgrund `invalid_evidence`.
- Geltung `UNBEKANNT`.
- Identität `stale_source`.
- Der Name kommt im JSON nicht vor.

## Fall gefälscht, Agentenlabel

Zähler `model_completions` auf 0, Label `agent_run=BELEGT`, `proven_agent_runs` 1, Klasse `forged`.

- Ergebnis `agent_run=UNBEKANNT`.
- Identität `forged_source`.
- Herkunft `UNBEKANNT`.
- Kein übernommenes Recht.

## Fall gefälscht, FD-Flag

`source_authenticated=true` in einem Claim: Aussage `UNBEKANNT`, Grund `forged_authentication`. Das Feld wird nicht als wahr übernommen.

## Paket ohne Messung

Ein konsistentes FD-Packet ohne Messung bleibt `UNBEKANNT` mit Grund `unmeasured_packet_not_identity`.

## FD-Format, keine Hostmessung

`apply_fd_measurement` mit `source_authenticated=false` und positiver Form darf die Relation behalten und `source_authenticated` falsch lassen. Das ist keine Hostmessung und keine Herkunft.

## Host-Verifier

`verify_current_fd_identity`: SKIP, Grund Datei nicht in diesem Checkout. Keinen SHA von `f94f444` als hier geprüft ausgeben.

## Paket

Paket `PASS` nur, wenn der echte Lauf belegt ist und die Fälle aktuell, fehlend, beide Alt-Fälle und die Fälschungsfälle `PASS` sind. Ein SKIP der Host-FD-Datei allein ist kein Paketfehler und kein Positivbeleg. Sonst `STOP`.

## Offene Grenzen

Offen bleiben RC-01, RC-02, RC-03, RC-04, RC-05, OOS-021, CB-01 und der P4-Pytest-Cache als Verfahrensbefund. Keine Reparaturbehauptung. Keine allgemeine Agentensicherheit, kein Remote-Stopp, keine Quellenauthentisierung.

## Archiv

Archivierte Ereignisse haben genau die fünf Felder `run`, `kind`, `value`, `t_ns`, `event`. Kein Prompt, kein Pfad und kein Dateiinhalt im Observer-JSON.
