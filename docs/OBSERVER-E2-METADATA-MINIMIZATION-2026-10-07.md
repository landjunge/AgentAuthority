# E2 – Metadaten in Agent Authoritys eigenen Speicher- und Exportpfaden

**Vorabprotokoll, 7. Oktober 2026.** Daniels Auftrag „e2 wenn fertig push und
commit und link“ und seine anschließende Korrektur begrenzen diesen Versuch auf
**Agent Authority als eigenständigen Beobachter / Monitor / Analyseebene**.
Keine ThreadDesk-Anbindung und keine Prüfung anderer Tools. Der vorher vorbereitete
Entwurf mit einem ThreadDesk-Importpfad wurde vor Freeze und Versuchsausführung
verworfen; daraus wurden keine Messergebnisse übernommen.

E2 aus der [Informationsgrenzen-Recherche](OBSERVER-INFORMATION-BOUNDARIES-2026-10-07.md)
motiviert die Prüfung, legt aber keine Integration fest. D-012 gilt: keine
Produktfreigaben, Rechtevergabe oder Eingriffe. Historische Labentscheidungen
bleiben Testdaten innerhalb ihres damaligen Umfangs.

## Basis und Umfang

- Arbeitsbasis einschließlich E1: `b2bb13603cbf88f89f40d07b886cc1781196e07b`.
- Abgerufener Lab-`master`: `ef2400fa5fad3c4ff051928b78fcb3093bb23453`.
  Die hier benutzten Labfunktionen und bestehenden Tests sind gegenüber dieser
  Basis unverändert. Die früheren Dokumentationsversuche liegen zusätzlich auf
  dem Arbeitsbranch; der Versuch ändert keinen Produktcode.
- KI-Zentrale: `96526cf99b94bfae9f6c177c6d07d2925404ecdd`; unverändert.
- Ausschließlich neue künstliche Daten in einem eigenen temporären Verzeichnis.
  Keine vorhandenen Logs, Datenbanken, Zugangsdaten oder Konfigurationsdateien lesen.
  Die URL wird nur als Zeichenfolge serialisiert, nicht aufgerufen.

Auf diesem `master` sind für diesen Versuch historische Labzustände, Provenienz
und der JSONL-Serializer vorhanden. Daraus wird **keine bereits implementierte
produktive Monitor-Eingangs-, Anzeige- oder Warnpipeline** abgeleitet.
Die fehlenden Anschlussbelege werden ausdrücklich offen gehalten.

Nach der [Forschungsmethode](RESEARCH-METHOD.md) werden Frage, Erwartungen,
Eingaben und Messgrenzen vor der Ausführung committed und gepusht. Ergebnisse
werden später angehängt; dieser Vorabteil bleibt bytegleich. Ein temporäres
Hilfsskript ruft ausschließlich bestehende Funktionen dieses Repositories auf.
Kein Produktcode und kein bestehender Test wird geändert. Kein Experiment 04
und kein weiterer E-Versuch.

## Frage und eingefrorene Hypothesen

Welche künstlichen Metadatenmarker bleiben in den vorhandenen eigenen Labdaten
und in ihrer ersten JSONL-Persistenz erhalten? Was schließt der bekannte
Parameterausschluss tatsächlich aus?

- **H1:** Actor, Resource, URL im Resource und Fehlertext im `reason_code` bleiben
  bei beiden Markerklassen im ersten Ereignislog erhalten. Auch der ausdrücklich
  secretähnliche Dummy wird auf diesem Exportpfad nicht automatisch entfernt.
- **H2:** Ein Marker ausschließlich in `parameters.e2_probe` erscheint bei
  `file.read` weder in den beiden exportierten Ereignissen noch in der
  untersuchten eigenen Provenienz und `public_view()` des Workflowzustands.
  Das gilt nur für diese Aktion und diese Speicher, nicht für alle Labaktionen.
- **H3:** Actor bleibt bei `file.read` in der Provenienz und in den Zustandsagenten
  erhalten. Resource und URL bleiben in der Provenienz; `touched_paths` bleibt
  für diese Leseaktion leer. Das ist eine aktionsabhängige Zustandsprojektion,
  keine Redaktion des Ressourcenwertes vor dem Log.
- **H4:** Die vier Metadatenträger in beiden Markerklassen erhalten trotz ihres Markers ein konstantes
  `PUBLIC`-Label und gültige Eventhashes. Label und Hash belegen keine Bereinigung.

Abweichungen werden als Ergebnis festgehalten, nicht durch geänderte Marker
passend gemacht. Eine Hypothesenbewertung betrifft nur diese Daten und
bestehenden Funktionen; sie belegt weder allgemeine DLP noch Warnqualität oder
die Eignung sämtlicher Felder als späterer Monitorinput.

## Zehn eingefrorene Fälle

Je Fall genau ein markierter Träger, ein neuer Labzustand und eine neue JSONL.
Die zwei Ereignisse pro Export sind keine zwei unabhängigen Fälle.

| Fall | Klasse | Träger | Exakter Marker |
|---|---|---|---|
| C1 | neutraler Canary | Actor | `E2_PRIVATE_CANARY_ACTOR_01` |
| C2 | neutraler Canary | Resource | `E2_PRIVATE_CANARY_RESOURCE_02` |
| C3 | neutraler Canary | URL im Resource | `E2_PRIVATE_CANARY_URL_03` |
| C4 | neutraler Canary | Fehlertext im `reason_code` | `E2_PRIVATE_CANARY_REASON_04` |
| C5 | neutraler Canary | Parameters, Gegenkontrolle | `E2_PRIVATE_CANARY_PARAMETERS_05` |
| S1 | secretähnlicher Dummy | Actor | `api_key=E2_FAKE_NOT_A_CREDENTIAL_ACTOR_06` |
| S2 | secretähnlicher Dummy | Resource | `api_key=E2_FAKE_NOT_A_CREDENTIAL_RESOURCE_07` |
| S3 | secretähnlicher Dummy | URL im Resource | `api_key=E2_FAKE_NOT_A_CREDENTIAL_URL_08` |
| S4 | secretähnlicher Dummy | Fehlertext im `reason_code` | `api_key=E2_FAKE_NOT_A_CREDENTIAL_REASON_09` |
| S5 | secretähnlicher Dummy | Parameters, Gegenkontrolle | `api_key=E2_FAKE_NOT_A_CREDENTIAL_PARAMETERS_10` |

Alle Marker sind vollständig erfunden und nicht einlösbar. „Private“ bezeichnet
eine künstliche Sensitivität, keine vertraulichen Nutzerdaten. Die zweite Klasse
prüft nur den Transport eines offensichtlich als Dummy benannten Schlüsseltexts.
Sie ist keine echte Zugangsinformation und kein Erfolgsnachweis für Secret-Erkennung.

Standardrequest: Actor `E2-Agent`, Aktion `file.read`, Resource `e2/object.txt`,
Parameters `{}`, Workflow `wf-e2-<Fall>`. Actor-/Resource-Fälle ersetzen nur das
jeweilige Feld. URL-Fälle setzen Resource auf
`https://example.invalid/object?note=<Marker>`; kein eigenes URL-Feld wird erfunden.
Parameterfälle setzen ausschließlich `parameters.e2_probe` auf den Marker.
Diese acht Fälle benutzen `Lab().submit(request)`; keine echte Datei wird gelesen.

C4/S4 benutzen denselben Standardrequest und ausschließlich den vorhandenen
Serializer `emit_decision(request, Decision(False, "synthetic-error:<Marker>", []))`.
Das ist ein synthetischer Fehlertext am Serializer, **kein von Lab.submit
ermittelter Entscheidungsgrund**. Die bestehende Zuordnung `deny_reason` zu
`reason_code` wird gemessen. Für diese zwei Serializer-Fixtures wird kein
Workflowzustand oder Provenienzlauf erfunden.

## Messstellen und Bewertung

1. **Eigene RAM-Daten:** Nach `Lab.submit` nur `Lab.state()` dieses künstlichen
   Workflows betrachten: `public_view()`, `touched_paths`, Agenten und seine
   Provenienz. Exakte Markerpositionen dokumentieren. Das sind Labdaten, kein
   erfundenes öffentliches Monitor-Datenmodell. Der Eingaberequest selbst trägt
   selbstverständlich den Marker; dies ist keine zusätzliche Minimierungsmessung.
2. **Erste Persistenz dieses Exportpfades:** Export ausdrücklich mit
   `LAB_AUTHORITY_EVENTS=1` und frischem `LAB_AUTHORITY_EVENTS_PATH` aktivieren.
   Existenz, zwei JSONL-Ereignisse, exakte Markerpositionen, `PUBLIC`, Hashwerte
   und interne Verkettung prüfen. Fehlende Ausgabe bedeutet Messfehler, nicht
   nachgewiesene Redaktion. „Erste Speicherstelle“ meint ausschließlich die
   erste Persistenz des untersuchten Exports, nicht alle Speichervorgänge im System.
3. **Nachprüfbare JSON-Repräsentation:** Nur diese neue JSONL mit dem
   Python-Standardparser lesen und Markerpositionen erfassen. Das bestätigt
   den gespeicherten Inhalt; es ist **kein vorhandener produktiver AA-Import**.
   Selbst die Gegenkontrolle wird auf vollständige Werte geprüft, nicht bloß
   auf die Abwesenheit eines Top-Level-Schlüssels namens `secret` oder `api_key`.
4. **Nicht belegte Anschlussstellen:** Eigene produktive Monitoraufnahme,
   Nutzeranzeige und abgeleitete Warnung aus diesen Ereignissen bleiben
   **NICHT GETESTET / in der geprüften Basis nicht als verbundener Pfad belegt**.
   Dafür wird kein Fremdtool herangezogen und kein Ersatz implementiert.

Werte: **erhalten**, **nicht enthalten**, **nicht anwendbar** oder
**nicht getestet / nicht belegt**. Kein fehlender Marker in einer Projektion
beweist seine Abwesenheit in allen früheren Daten. Keine historischen
Gate-Akzeptanzkriterien werden verändert oder neu bewertet. Prüfkonformität
dieses E2-Protokolls und Hypothesenbewertung bleiben getrennt.

## Abnahme und Ende dieses Auftrags

Vollständigkeit der zehn Fälle, Reproduktionsskript und Resultate dokumentieren;
Quellbezüge sowie unveränderte Vorabteilsbytes prüfen. Bestehende Exportchecks
und die unveränderte Lab-Standardsuite gemäß Forschungsmethode ausführen; ihre
Reichweite und vorhandene Ausschlüsse nennen. Getrennte read-only Prüfung im
selben Projektkontext, kein externer Audit. Keine Tests anderer Tools.

Danach Ergebnis committen, pushen und Remote-Commit bestätigen. **STOPP:** keine
Filterreparatur, Produktfunktion, Architekturentscheidung oder automatische E3-Arbeit.

<!-- E2-FROZEN-PROTOCOL-END -->

## Gemessene Ergebnisse

Ausführung am 7. Oktober 2026, Ereigniszeit `17:03:12Z`, Python 3.12.14.
Das Vorabprotokoll war vorher als
[`59a05aa223e3c33c051462057e9d5a7af551c394`](https://github.com/landjunge/agent-authority-lab/commit/59a05aa223e3c33c051462057e9d5a7af551c394)
committed, gepusht und mit identischem Remote-Commit bestätigt.
Vorabteils-SHA-256:
`a7022e06ff1b1e33c258e96677107697c0782c1d35b143d4cc3fbc182c12479b`.

**Alle acht Metadatenfälle behalten den exakten Marker im ersten JSONL-Export.
Beide Parameterkontrollen enthalten ihn dort nicht.** Dasselbe Ergebnis gilt
für neutrale Canarys und die ausdrücklich künstlichen `api_key=`-Dummys.
Die [synthetischen Messdaten](OBSERVER-E2-EVIDENCE-2026-10-07.json) enthalten
sämtliche zehn Requests, ihre begrenzten Zustands-/Provenienzansichten und die
zwanzig tatsächlich geschriebenen Ereignisse. Keine echten Zugangsdaten.

| Fälle | Träger | `public_view()` | Provenienz | Erstes JSONL: beide Ereignisse |
|---|---|---|---|---|
| C1 / S1 | Actor | erhalten in `agents[0]` | erhalten in `actor` und `state_after.agents[0]` | erhalten in `actor.agent_id` |
| C2 / S2 | Resource | nicht enthalten | erhalten in `resource` | erhalten in `resource` |
| C3 / S3 | URL im Resource | nicht enthalten | vollständige URL mit Querymarker in `resource` | vollständige URL mit Querymarker in `resource` |
| C4 / S4 | künstlicher Fehlertext | nicht anwendbar | nicht anwendbar | erhalten in `reason_code` |
| C5 / S5 | Parameters | nicht enthalten | nicht enthalten | nicht enthalten |

Für die acht `Lab.submit`-Fälle: genau ein Provenienzrecord je Fall und
`touched_paths=[]`; die Aktion war `file.read`. Resource und URL verschwinden
also aus dieser Zustandsprojektion, bleiben aber in Provenienz und Log.
Die Parameter stehen weiterhin im künstlichen Eingaberequest. **Gemessen wurde
keine Löschung aus dem gesamten Prozessspeicher.**

Für die zwei Reason-Fixtures: direkte synthetische `Decision` plus bestehender
Serializer; keine `Lab.submit`-Entscheidung und kein Workflowzustand. Die
Marker stehen in beiden `reason_code`-Werten. Daraus folgt weder, dass reguläre
Labfehler diese freien Texte erzeugen, noch dass eine Warnung sie verarbeitet.

Alle zehn Exportaufrufe schrieben genau zwei Ereignisse; kein fehlender oder
verschluckter Schreibvorgang wurde als Redaktion gewertet. Alle **20 Eventhashes**
und **10 internen Zweierketten** stimmen mit ihren gespeicherten Inhalten überein.
Alle Ereignisse tragen unverändert `data_labels=["PUBLIC"]`, auch die acht mit
sichtbarem Metadatenmarker. Die Datei enthält den Klartext zusätzlich zum Hash;
Hashing hat ihn nicht ersetzt. Das beweist keine Quellenauthentizität.

Die acht `Lab.submit`-Kontrollen lieferten die historische Labentscheidung
`ALLOW`; die zwei ausdrücklich eingespeisten Serializer-Fixtures `DENY`.
Das sind vorhandene Fake-Labwerte, **keine Produktfreigaben oder Sperren von AA**.

### Bewertung der eingefrorenen Erwartungen

| Ebene | Ergebnis | Tragweite |
|---|---|---|
| E2-Protokollkonformität | **PASS**, 10/10 Fälle | Eingaben, Messstellen und Umfang eingehalten; keine historische Spec umgeschrieben. |
| H1 | **SUPPORTED** | 8/8 Metadatenfälle behalten den Marker in beiden exportierten Ereignissen. |
| H2 | **SUPPORTED** | 2/2 inerte Parameterkontrollen fehlen in Export, untersuchter Provenienz und `public_view()` für `file.read`. |
| H3 | **SUPPORTED** | 2 Actorfälle in Zustandsagenten/Provenienz; 4 Resource-/URL-Fälle in Provenienz bei leerem `touched_paths`. |
| H4 | **SUPPORTED** | Alle acht Metadatenfälle erhalten PUBLIC und gültige Hashes trotz Klartextmarker. |

**CONFIDENCE IN EXPERIMENT RESULT: HIGH** innerhalb der zehn festen künstlichen
Eingaben und dieser Funktionen. Die separate Quellprüfung stimmt mit der
gemessenen Weitergabe überein.

**CONFIDENCE IN GENERALIZATION: LOW.** Keine realen Credentials, anderen
Aktionen, vollständigen Heaps, verteilten Systeme, produktiven Monitorinputs,
Warnalgorithmen oder UI-Wege wurden geprüft. Keine gemessene Secret-Erkennung
und kein Sicherheitsnachweis für Agent Authority als Gesamtprodukt.

### Belege und bisheriger Stand

Alle folgenden Codeverweise sind auf den unveränderten `master`-Quellstand
`ef2400fa5fad3c4ff051928b78fcb3093bb23453` festgelegt:

- [Emitter: Feldauswahl, PUBLIC und Schreiben](https://github.com/landjunge/agent-authority-lab/blob/ef2400fa5fad3c4ff051928b78fcb3093bb23453/lab/authority_emit.py#L63-L100):
  Actor, Resource und `deny_reason` werden unmittelbar kopiert; Parameters sind
  nicht ausgewählt. Der Versuch bestätigt dies praktisch, ohne den Export zu ändern.
- [Eigene Zustandsprojektion](https://github.com/landjunge/agent-authority-lab/blob/ef2400fa5fad3c4ff051928b78fcb3093bb23453/lab/models.py#L110-L122)
  und [aktionsabhängiger Zustand](https://github.com/landjunge/agent-authority-lab/blob/ef2400fa5fad3c4ff051928b78fcb3093bb23453/lab/state.py#L18-L38):
  erklären Zustandsagenten und die leeren Schreibpfade beim getesteten `file.read`.
  Der Docstring `No ... secrets` belegt keine Prüfung aller Stringwerte: Der
  getestete secretähnliche Actor-Dummy steht trotzdem in `public_view().agents`.
  Das ist eine Grenze dieser Formulierung, kein Versuch mit einem echten Secret.
- [Provenienz: Parameters nicht übernommen](https://github.com/landjunge/agent-authority-lab/blob/ef2400fa5fad3c4ff051928b78fcb3093bb23453/lab/provenance.py#L14-L32):
  übernimmt Actor und Resource, nicht Parameters.
- [Bestehende Exporttests](https://github.com/landjunge/agent-authority-lab/blob/ef2400fa5fad3c4ff051928b78fcb3093bb23453/tests/test_authority_emit.py#L20-L58):
  die früheren Assertions `"api_key" not in ev` / `"secret" not in ev` prüfen
  Top-Level-Schlüsselnamen. Sie widersprechen dem jetzigen Wertetransport nicht
  und belegen keine Bereinigung sensibler Metadatenwerte.
- [README zur Produktrolle und historischen Befundgrenze](https://github.com/landjunge/agent-authority-lab/blob/ef2400fa5fad3c4ff051928b78fcb3093bb23453/README.md#L3-L19):
  Beobachterrolle; historische Gates belegen keine implementierte
  produktive Beobachterintegration. Der Versuch füllt diese Lücke nicht aus.

Der bisher dokumentierte Parameterausschluss bleibt bestehen. Neu hinzu kommt
der reproduzierbare Wertetest an acht Metadatenfällen: Er zeigt konkret, warum
dieser Ausschluss **keine allgemeine Metadatenminimierung** ist. Die bestehende
Warnung im README über unbereinigte Exportmetadaten wird bestätigt, nicht verworfen.

### Weiter offen – ausdrücklich nicht mit Ersatzdatenwegen ausgefüllt

- Welche minimierten Ereignisse ein produktiver eigenständiger Monitor tatsächlich
  erhält, ist durch diesen Lab-Export nicht bewiesen.
- Eigener produktiver Import, Nutzeranzeige und abgeleitete Warnung:
  **NICHT GETESTET; verbundener Pfad in dieser Basis nicht belegt.**
- Keine Aussage über Sanitization anderer Metadatenfelder, andere Aktionstypen,
  Inhalte, Fehler-Stacktraces, Aufbewahrung oder Zugriffsgrenzen.
- Das feste PUBLIC-Label wird im Versuch nicht aus der künstlichen Sensitivität
  hergeleitet. Es ist deshalb kein Eignungsnachweis als zulässiger Monitorinput.

### Prüfungen, Übergabe und STOPP

- Ausgeführtes Hilfsskript: SHA-256
  `aa02d4a0492c9646f4266c8d20a2d207438c25f6e7dbdde4ce31e1e3514a9968`;
  vollständig im folgenden Reproduktionsabschnitt.
- Eingefrorene zehn Fälle und alle exakten Fundstellen gegen die Messdaten geprüft:
  10/10 protokollkonform, 20/20 Hashes, 10/10 Ketten, keine fehlenden Exporte.
- `LAB_AUTHORITY_EVENTS=0 /workspace/venvs/authority/bin/python -m pytest tests/test_authority_emit.py tests/test_authority_event_flags.py`:
  **29 bestanden**, 0,06 s. Bestehende Tests unverändert.
- `LAB_AUTHORITY_EVENTS=0 /workspace/venvs/authority/bin/python -m pytest`:
  zwei aufeinanderfolgende Läufe, jeweils **239 bestanden / 5 abgewählt**,
  4,34 s und 4,29 s. Diese Suitekonformität ist keine neue Erkennungsleistung.
- Die bestehende [Realcase-Auswahl](https://github.com/landjunge/agent-authority-lab/blob/ef2400fa5fad3c4ff051928b78fcb3093bb23453/tests/realcase/conftest.py)
  lässt RC-01–05 absichtlich aus der Standardsuite; ihre bekannten Misses
  bleiben offen. Der historische Finish-Probe wurde nicht ausgeführt.
- Dokumentprüfung **PASS**: Vorabteil bytegleich zum Freeze, eingebettetes Skript
  exakt gleich dem ausgeführten Hilfsskript, drei lokale Berichtlinks und sieben
  gepinnte Quelldateien geprüft; keine Änderung an `lab`, `tests` oder Paketkonfiguration.
- Zwei getrennte read-only Ergebnisprüfungen im selben Projektkontext **PASS**:
  eigene Nachberechnung der Markerpfade, 20 Hashes, zehn Ketten und zehn
  rekonstruierter JSONL-Dateihashes; zusätzlich Diff, Auftrag und Behauptungsgrenzen
  geprüft. Keine Produktaufrufe durch Prüfer; kein externer Audit.

**Schlussfolgerung:** Der vorhandene Parameterausschluss verhindert diese zwei
Parameterexporte; die vier untersuchten Metadatenträger bleiben dagegen bis in
die erste JSONL-Persistenz unbereinigt. Das ist jetzt mit synthetischen Werten
belegt. **STOPP.** Keine Reparatur, Integration oder Folgeexperiment begonnen.

## Reproduktion des gemessenen Datenwegs

Den folgenden Block unverändert als temporäre Datei `authority_e2_probe.py`
speichern. Er benutzt nur die bestehende Lab-API und Python-Standardbibliothek.
Mit Python 3.12 oder höher ausführen:

```sh
python /tmp/authority_e2_probe.py --lab /pfad/zu/agent-authority-lab --output-parent /tmp
```

Jeder Aufruf erzeugt ein neues `aa-e2-*`-Verzeichnis mit zehn isolierten
JSONL-Dateien und einer `results.json`. Es gibt keine Netzwerk-, Browser-,
Desktop-, Fremdtool- oder echten Dateiausführungen. Der Marker wird als
Zeichenfolge verfolgt, nicht als bösartigen Inhalt klassifiziert. UUIDs,
Zeitstempel, Dateihashes und temporäre Pfade variieren; die im Bericht genannten
Markerfundstellen und Anzahlen sind die Vergleichsgrößen.

```python
"""Synthetic E2 measurement of existing Agent Authority lab functions only."""
import argparse
import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path


def marker_paths(value, marker, path="$"):
    found = []
    if isinstance(value, dict):
        for key, child in value.items():
            found.extend(marker_paths(child, marker, f"{path}.{key}"))
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            found.extend(marker_paths(child, marker, f"{path}[{index}]"))
    elif isinstance(value, str) and marker in value:
        found.append(path)
    return found


parser = argparse.ArgumentParser()
parser.add_argument("--lab", type=Path, required=True)
parser.add_argument("--output-parent", type=Path, required=True)
args = parser.parse_args()
sys.path.insert(0, str(args.lab.resolve()))
from lab.authority_emit import emit_decision
from lab.models import ActionRequest, Decision
from lab.validator import Lab

root = Path(tempfile.mkdtemp(prefix="aa-e2-", dir=args.output_parent))
cases = [
    ("C1", "actor", "E2_PRIVATE_CANARY_ACTOR_01"),
    ("C2", "resource", "E2_PRIVATE_CANARY_RESOURCE_02"),
    ("C3", "url", "E2_PRIVATE_CANARY_URL_03"),
    ("C4", "reason", "E2_PRIVATE_CANARY_REASON_04"),
    ("C5", "parameters", "E2_PRIVATE_CANARY_PARAMETERS_05"),
    ("S1", "actor", "api_key=E2_FAKE_NOT_A_CREDENTIAL_ACTOR_06"),
    ("S2", "resource", "api_key=E2_FAKE_NOT_A_CREDENTIAL_RESOURCE_07"),
    ("S3", "url", "api_key=E2_FAKE_NOT_A_CREDENTIAL_URL_08"),
    ("S4", "reason", "api_key=E2_FAKE_NOT_A_CREDENTIAL_REASON_09"),
    ("S5", "parameters", "api_key=E2_FAKE_NOT_A_CREDENTIAL_PARAMETERS_10"),
]
results = []
for case_id, carrier, marker in cases:
    folder = root / case_id
    folder.mkdir()
    path = folder / "events.jsonl"
    os.environ["LAB_AUTHORITY_EVENTS"] = "1"
    os.environ["LAB_AUTHORITY_EVENTS_PATH"] = str(path)
    request = ActionRequest("E2-Agent", "file.read", "e2/object.txt", {},
                            "wf-e2-" + case_id)
    if carrier == "actor":
        request.actor = marker
    elif carrier == "resource":
        request.resource = marker
    elif carrier == "url":
        request.resource = "https://example.invalid/object?note=" + marker
    elif carrier == "parameters":
        request.parameters = {"e2_probe": marker}
    state_view = provenance = touched_paths = None
    if carrier == "reason":
        decision = Decision(False, "synthetic-error:" + marker, [])
        emit_decision(request, decision)
        entrypoint = "emit_decision synthetic Decision fixture"
    else:
        lab = Lab()
        decision = lab.submit(request)
        state = lab.state(request.workflow_id)
        state_view = state.public_view()
        touched_paths = sorted(state.touched_paths)
        provenance = [
            {"workflow_id": row.workflow_id, "actor": row.actor,
             "action": row.action, "resource": row.resource,
             "decision": row.decision, "state_before": dict(row.state_before),
             "state_after": dict(row.state_after), "timestamp": row.timestamp,
             "seq": row.seq}
            for row in state.provenance
        ]
        entrypoint = "Lab.submit"
    text = path.read_text(encoding="utf-8")
    events = [json.loads(line) for line in text.splitlines() if line.strip()]
    hashes_valid = []
    for event in events:
        body = {k: v for k, v in event.items() if k != "event_hash"}
        encoded = json.dumps(body, sort_keys=True, separators=(",", ":"),
                             ensure_ascii=True).encode("utf-8")
        hashes_valid.append(event["event_hash"] == hashlib.sha256(encoded).hexdigest())
    if len(events) != 2:
        raise RuntimeError(f"{case_id}: expected two emitted events, got {len(events)}")
    result = {
        "case": case_id, "carrier": carrier, "marker": marker,
        "entrypoint": entrypoint,
        "input_request": {"actor": request.actor, "action": request.action,
                          "resource": request.resource, "parameters": request.parameters,
                          "workflow_id": request.workflow_id},
        "decision_allow": decision.allow, "decision_reason": decision.deny_reason,
        "state_view": state_view, "provenance": provenance,
        "touched_paths": touched_paths,
        "state_marker_paths": None if state_view is None else marker_paths(state_view, marker),
        "provenance_marker_paths": None if provenance is None else marker_paths(provenance, marker),
        "log_marker_paths": marker_paths(events, marker),
        "raw_log_contains_marker": marker in text,
        "events": events, "event_count": len(events),
        "event_types": [event["event_type"] for event in events],
        "labels": [event["data_labels"] for event in events],
        "hashes_valid": hashes_valid,
        "chain_valid": (events[0]["previous_event_hash"] is None and
                        events[1]["previous_event_hash"] == events[0]["event_hash"]),
        "log_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    }
    (folder / "measurement.json").write_text(json.dumps(result, indent=2) + "\n",
                                             encoding="utf-8")
    results.append(result)
(root / "results.json").write_text(json.dumps({"cases": results}, indent=2) + "\n",
                                    encoding="utf-8")
print(json.dumps({"output": str(root), "cases": len(results),
                  "events": sum(row["event_count"] for row in results)}, indent=2))
```
