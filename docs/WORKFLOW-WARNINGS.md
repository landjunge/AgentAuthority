# Fachliche Workflow-Hinweise / Semantic workflow findings

AA-C02 ergänzt die vorhandene ausgewählte Beobachtungskette. Keine neue Queue,
Auditdatenbank, Produzentenausführung oder Freigabeinstanz. Produktversion bleibt
0.3.0a2, Repository privat; kein Release und keine installierte Laufzeit geändert.
Die [Quellenprojektion](WORKFLOW-OBSERVATIONS.md) und deren Grenzen gelten weiterhin.

## Deutsch

`workflow-inspect` wertet nun standardmäßig wenige begrenzte Metadatenregeln aus.
JSON ergänzt unter `analysis` den ausdrücklichen Vertrag
`agent-authority-workflow-findings-v1`. Der umgebende Workflow-v1-Bericht und der
neutrale v1-Unterbericht bleiben rückwärtskompatibel. Text/Offline-HTML und die
native macOS-Ansicht zeigen Hinweise im bestehenden Bericht/Graph/Inspector.

| Regel | Beobachteter Vergleich | Fehlende Voraussetzung |
|---|---|---|
| Revision | Rückgabe gegen ihren vorher gemeldeten `handoff.bound`; Handoff-, Quell- und Taskrevision separat | Ohne passende Bindung oder Revision: unbekannt. Eine höhere als gebundene Revision heißt Abweichung, nicht veraltet. |
| Rückgabebezug/Empfänger | Task-/Original-/Bridge-ID, Lauf, Empfänger und vorhandene Hash-/Principal-/Scopebezüge gegen dieselbe Bindung | Fehlende Mindestbezüge Task/Lauf/Empfänger bleiben unbekannt; andere Quellen/Aufträge werden nicht zusammengezogen. |
| Ergebnisbeleg | Gemeldeter Abschluss/Lieferung ohne `artifact_ref` | Fehlender Referenzbeleg; ein vorhandener Verweis beweist weder Inhalt, Funktion noch Projektabnahme. |
| Stoppreihenfolge | `dispatch_seq` nach der frühesten ausdrücklich gemeldeten effektiven `barrier_seq` im selben persistenten Controller-Namensraum | Anfrage, pending, fehlende Sequenz, gleiche Sequenz oder anderer Controller: unbekannt. |
| Kontrollpunkt | Explizit referenziertes `budget.reserved` vor Versand, gleiche Aufgabe/Versuch/Request/Consumer/Actor-Angabe und Controller | Fehlender oder falsch zugeordneter Beleg bleibt unbekannt; `access.approved`, `budget.checked` und eine frühere Allow-Marke reichen nicht. |

Ein Warnhinweis `reported_contradiction` bedeutet **Widerspruch zwischen
Produzentenmeldungen**. `missing_evidence` bedeutet **fehlender Nachweis**. Beide
werden getrennt benannt. Kein importierter Sachverhalt ist ein unabhängig
beobachteter tatsächlicher Verstoß: `actual_violation_verified=false`,
`gate_authorization_proven=false`, `task_completion_proven=false`. Meldung eines
Agenten-Turnendes ist kein erfüllter Gesamtauftrag; Ankunft/Review ist keine
verifizierte Projektabnahme. Auch ohne Warnhinweise bleibt Gesamtabdeckung
UNBEKANNT. Keine Aussage über Absicht oder allgemeine Sicherheit.

### Produzentenvertrag (additiv, keine freien Inhalte)

Die vier optionalen Event-v1-Felder `binding_event_id`, `control_ref`,
`gate_event_id` und `consumer_id` sind dieselben begrenzten opaken Referenzen wie
andere IDs (1–256 ASCII-Zeichen aus `[A-Za-z0-9_.:-]`, erstes Zeichen alphanumerisch).
Keine URLs, Dateipfade, Rohprompts, Secrets oder vollen Antworten eintragen.
`binding_event_id` und `gate_event_id` referenzieren **Ereigniskennungen im selben
Produzenten-/Quellen-Namensraum**, keine Thread-/Session-ID.

Rückgaben werden nur im gleichen project/workflow/handoff und Produzentenbereich
verglichen. Explizite Bindungsreferenz hat Vorrang: ein ungültiger Verweis fällt
nicht still auf eine andere Bindung zurück. Nur bei strukturell vollständigem
Ausschnitt darf genau eine implizite Bindung herangezogen werden. Mehrere
Bindungen, fehlende/gleiche Produzentenordinals oder spätere Bindung ergeben
unbekannt. Explizit belegte Paare bleiben trotz anderweitiger Lücke als **Vergleich
zweier Meldungen** auswertbar; sie beweisen keine globale Vollständigkeit.

`control_ref` benennt einen persistenten, nicht zurückgesetzten Sequenznamensraum;
`barrier_seq` und `dispatch_seq` müssen dessen **selber dauerhaft geordneter Zähler**
sein. Keine Zeitstempel-/Dateinamenreihenfolge oder Zähler unterschiedlicher
Produzenten vergleichen. Das ist ein Exportvertrag, kein neuer Controller.
Nur `control.stop_effective` mit `stop_state=effective` und Barriere ist ein
expliziter effektiver Stoppclaim; requested/pending/unknown nicht. Eine spätere
Barriere hebt eine frühere nicht auf. Stop/Effekt wird **nicht** durch den
Beobachter geprüft oder durchgesetzt. Fremde CLI/Kinder bleiben unbeobachtet.

### API, Begrenzung und Belegpfad

`workflow_rules.analyze_workflow_claims(validated_claims, limit=100,
complete_selected_read=False)` liest ausschließlich schon minimierte
`WorkflowClaim`-Werte. Maximal 10 000 Claims; maximal 100 angezeigte Hinweise,
alle weiteren werden gezählt. Die vorhandene Reader-/Byte-/Rotationsbegrenzung
bleibt bestehen. Keine neue wachsende Speicherung, Quelle bleibt unverändert.

Jeder Hinweis enthält stabile `finding_id`, `rule_id`, Code, Klassifikation,
Schwere (`warning` oder `unknown`), betroffene Metadatenfelder und
`assessment_scope=producer_claim_consistency`. `reported_scope` bleibt gemeldeter
Bezug. Höchstens zwei `evidence_refs` nennen Quelle/Werkzeug, Ereignis-/Entry-ID,
Record- und Dateifingerprint. Finden sich identische Claims nach Rotation in einer
anderen Datei, bleibt die Finding-ID stabil; der Dateibeleg zeigt den aktuellen
Ausschnitt. Fingerprints sind **keine Identitätsbestätigung**.

`rule_results` zählt nur durchgeführte Vergleiche bzw. gemeldete Referenzen;
`counts`, `findings_omitted` und `claims_examined` machen die Anzeigegrenzen sichtbar.
Keine Werte sind Berechtigungen, Stop-Befehle oder verifizierte Kostenabrechnung.
CLI Exit0/2 behalten die bisherige Bedeutung des strukturellen Leseumfangs;
semantische Hinweise stehen in `analysis` und sind keine Prozessfreigabe.

Die native Oberfläche zeigt Widersprüche als Widerspruch und Beleglücken als
unvollständig; zusätzlich benennt sie die Klassifikation und den engen Prüfumfang
in Worten. Entry-Knoten bleiben gemeldet; keine Identität wird verifiziert.
Unbekanntes Analyseschema und ausgelassene Hinweise bleiben als Lücke sichtbar.
Die exportierte Graphansicht enthält nur ausgewählte minimierte Fakten, keine
beliebigen Originalzusatzfelder. Für vollständige minimierte Hinweise CLI-JSON
verwenden. Native Importannahmen und tatsächliche Prüfbelege siehe
[AA-C02-Prüfstand](evidence/seven-tools-warnings-20261018/STATUS.md).

## English

AA-C02 adds finite metadata consistency rules to the existing selected-source
projection and report/graph/inspector. `analysis` is explicitly versioned as
`agent-authority-workflow-findings-v1`; the existing neutral v1 report is unchanged.
This is not a second audit store, queue, runner, gate, or live enforcement layer.

Rules compare: separate source/handoff/task revisions against the referenced bound
handoff; return task/run/recipient/binding claims; reported completion/delivery
without an artifact reference; declared dispatch order after a reported effective
barrier in the same persistent controller namespace; a missing/mismatched
referenced reservation checkpoint. Each has matching/nonmatching synthetic cases.

The optional bounded opaque event fields are `binding_event_id`, `control_ref`,
`gate_event_id`, `consumer_id`. Explicit links refer to event IDs within the same
producer/source. Bindings require identical project/workflow/handoff, unique
strictly earlier producer ordinals; implicit lookup additionally requires a
structurally complete slice and exactly one binding. Missing/ambiguous/foreign
bindings remain unknown. Source, handoff and task revisions never substitute for
one another; original task, Bridge task, run and session remain separate.

Stop order requires a declared effective stop plus barrier and dispatch counters
from the **same persistent ordered controller journal**, not clocks, filenames or
foreign producers. Request/pending is not effective; equal/missing counters remain
unknown. An earlier barrier is not superseded by a later one. Gate-reference
matching requires task, attempt, request hash, consumer and actor claims to match
the referenced reservation and the same controller scope; this checks reports
only. 4AllPass approval or a standalone unchecked allow record is not a gate.

`reported_contradiction` is a conflict between reports; `missing_evidence` is an
unknown. Neither proves an actual violation. A supplied artifact reference is not
a functional check; turn completion is not project completion; arrival/review is
not verified project acceptance. All identity, effect and overall coverage claims
remain UNKNOWN, even with zero findings. No rights/budget/secret release or stop
is performed, and arbitrary CLIs/children are not controlled.

The pure analysis accepts at most 10 000 already validated minimized claims and
shows at most 100 findings with explicit omitted counts. Stable finding IDs survive
rotation of identical records; source/event/entry IDs and record/file hashes locate
the selected evidence. Hashes do not authenticate identity. Existing reader limits,
no-follow checks, immutable historical evidence, and operator-selected retention
continue to apply. No new persistent store is created. Text/HTML and native DE/EN
show findings, references, classification and the limited assessment scope.
Unknown schemas/omitted findings stay visible; imported extras are not exported.
Existing CLI exit status still describes structural reading, not authorization.
Private source preview only; no release/runtime upgrade, live safety claim, or
voice-chat push service. AA-C03 remains dependent on a concrete transport/operator
scope. The evidence report lists actual test and UI coverage.
