# SPEC: Action Identity + Approval Binding

**Status:** FROZEN (draft for review, 2026-10-03)
**Repo:** landjunge/agent-authority-lab
**Branch:** spec/action-identity-approval-binding
**Vorgänger:** docs/REAL-CASE-TRANSFER-STUDY-v1.md (Commit cb2dc55), docs/CONVERGENCE-BATTERY-v1-RESULTS.md (CB-01 MISSED), docs/OUT-OF-SCOPE-DEBT.md (OOS-015, OOS-020)
**Nicht autorisiert:** Experiment 04, I10, I6-Token-Binding-Repair im selben Motion. Diese Spec ist der Gegenstand, nicht die Implementierung.

---

## 1. Problemstellung

Die Transferstudie v1 (2026-09-03) zeigte eine klare Trennlinie:

- **Datenherkunft bleibt erhalten:** innerhalb des modellierten IFC-Graphen überzeugend. RC-06 bis RC-10 (Egress-Fälle) wurden mit IFC als SENSITIVE_EXTERNAL_EGRESS geblockt.
- **Autorität bleibt an die vollständige Handlung gebunden:** noch nicht modelliert. RC-01 bis RC-05 (Steuerungs-, Konfigurations-, Befehls- und Zustimmungsfälle) liefen bis zum verbotenen, aber inerten Endpunkt durch. Kein DENY.

Die fünf roten Fälle teilen eine gemeinsame fehlende Abstraktion:

1. **Sicherheitsidentität ist mehr als ein Pfad.** Bei MCPoison (RC-03) blieb der Name gleich, aber Befehl und Argumente änderten sich. Bei Copilot (RC-01) und CurXecute (RC-02) war der Pfad selbst Teil der Sicherheitssteuerung.
2. **Die Aktionssprache ist offen.** I9 sperrt unbekannte Verben nur an bereits geschützten Identitäten. shell.exec, mcp.start, issue.read, cache.poison auf gewöhnlichen Ressourcen sind ALLOW.
3. **approval_token ist nur Wahrheit/Falschheit.** Es ist nicht an Actor, Workflow, Generation, Aktion, Ressource, Parameter, Zeitpunkt oder einmalige Verwendung gebunden. Ein gestohlener Publish-Token und eine menschliche Zustimmung sehen im Modell gleich aus (CB-01, OOS-020).
4. **Wirkung und Verb sind nicht fest verbunden.** Ein zusammengesetzter Shell-Befehl kann Lesen und Egress in einem String verbinden, während der Monitor nur den äußeren Aktionsnamen sieht.

Diese Punkte liegen größtenteils in bereits dokumentierten Modellgrenzen (Prompt Injection, reale Adapter, Credentials, semantische Wirkungen). Die roten Tests widerlegen daher nicht die engen bisherigen Lab-Behauptungen. Sie zeigen, welche Grenze als Nächstes praktisch am wichtigsten ist.

---

## 2. Forschungsfrage

> Kann der Ausführungspunkt beweisen, dass jede reale Wirkung zu genau dem Descriptor gehört, über den der Monitor entschieden hat?

Das ist die Verallgemeinerung des bereits reparierten Adapter-Identity-Problems (T-19, docs/PHASE1-ADAPTER-IDENTITY.md): der FakeAdapter verwendet jetzt canonical_path für submit und repo keys. Die neue Frage erweitert das von Pfaden auf die vollständige Handlungsidentität inklusive Zustimmung.

Ein globales Default-Deny könnte RC-01 bis RC-04 scheinbar schnell schließen, beweist aber nicht, dass reale Adapter vollständig instrumentiert sind. Es kann außerdem legitime Erweiterungen blockieren. Deshalb: kein Default-Deny in dieser Spec.

---

## 3. Minimaler Gegenstand: ActionDescriptor

Ein normalisierter ActionDescriptor soll mindestens binden:

| Feld | Bedeutung | Beispiel |
|------|-----------|--------|
| actor | authentisierter Auftraggeber | root, agent-A |
| executor | ausführender Actor | agent-A |
| workflow_id | Workflow-Identität | wf-7 |
| generation | Lifecycle-Generation (nach finish() neu) | 3 |
| effect_class | kanonische Wirkungsklasse | READ, MUTATE, EXECUTE, CONNECT, PUBLISH, CONFIGURE_AUTHORITY |
| resource | kanonische Ressource (normalisierter Pfad) | repo://landjunge/x |
| parameters_digest | Digest der sicherheitsrelevanten Parameter | sha256(...)
| adapter_id | Adapter-Identität | FakeAdapter@canonical |
| target_system | Zielsystem | fake://external.example |
| expires_at | Ablaufzeit (falls Zustimmung nötig) | +300s |
| single_use | einmalige Verwendung (falls Zustimmung nötig) | true |

Regeln:

- Eine Zustimmung (approval) darf nur genau diesen Descriptor freigeben.
- Ändert sich ein sicherheitsrelevantes Feld, ist eine neue Zustimmung nötig.
- Ein Adapter darf keine Aktion ausführen, die nicht vorher in eine registrierte Wirkungsklasse übersetzt und vom Monitor entschieden wurde.
- Der Monitor sieht den Descriptor, nicht nur den Aktionsnamen.

---

## 4. Gefrorene Akzeptanzbedingungen

Vor Implementierung müssen RC-01 bis RC-05 rot bleiben. Danach müssen sie am vorgesehenen Mechanismus grün werden:

1. RC-01 bis RC-05 bleiben vor Implementierung rot und werden danach grün.
2. Ein geänderter Befehls-/Parameter-Digest braucht neue Zustimmung.
3. Zustimmung ist actor-, workflow-, generation-, action- und resource-gebunden, kurzlebig und standardmäßig einmalig.
4. Ein unbekannter realer Effekt darf den Adapter nicht erreichen.
5. Bekannte harmlose Reads/Writes innerhalb der bisherigen Grenzen bleiben erlaubt; eine eigene False-Positive-Grenzplatte ist erforderlich.
6. RC-06 bis RC-10 und alle 180 vorhandenen Tests bleiben unverändert.
7. Die neue Mechanik wird erst gegen das Fake-Lab bewertet. Eine Behauptung über echte IDEs, MCP-Server oder CI/CD braucht später einen separaten Adaptertest.

False-Positive-Panel: bestehende 28 Einträge (20 Interior + 6 Boundary + 2 Phase-2-PUBLIC) müssen ALLOW bleiben. Neue False Positives sind ein STOP.

---

## 5. Was diese Spec NICHT ist

- Keine Implementierung. Kein Code in diesem Motion.
- Kein Experiment 04, kein I10.
- Keine Behauptung über echte Produkte (Nx, Copilot, Cursor, Cline etc.). Die zitierten Vorfälle sind Abbildungsquellen, keine Zielsysteme.
- Keine Lösung für Prompt Injection (T-16), unmodellierte implizite Flüsse (T-15), Timing-/Covert-Channels (T-23/T-24), semantische Komposition (T-25). Diese bleiben in OUT-OF-SCOPE-DEBT.md.
- Kein Runtime-Attestation (OOS-002), kein Source-Labeling-Oracle (OOS-003).

---

## 6. Herkunft der Evidenz

| Quelle | Was sie liefert |
|--------|-----------------|
| REAL-CASE-TRANSFER-STUDY-v1.md | RC-01..05 MISSED, RC-06..10 CAUGHT-EXPECTED; Trennlinie Datenherkunft vs. Autoritaetsbindung |
| CONVERGENCE-BATTERY-v1-RESULTS.md | CB-01 MISSED (approval_token reuse); k=1, not SUPPORTED; FP 0/28 |
| OUT-OF-SCOPE-DEBT.md | OOS-015 (truthy tokens), OOS-020 (token not bound) |
| THREAT-MODEL.md | T-06 Confused Deputy, T-11 Value Substitution, T-19 Adapter Identity |
| PHASE1-ADAPTER-IDENTITY.md | Bereits repariert: FakeAdapter canonical_path |
| Norm Hardy, Confused Deputy (1988) | Klassisches Muster |
| MCP Security Best Practices (2026-07-28) | clientgebundene Zustimmung, Token-Audience |
| W3C PROV-DM | Entitäten, Aktivitäten, Verantwortliche; Ableitungen |
| MITRE CWE-367 | TOCTOU zwischen Prüfung und Nutzung |
| Denning (1976) | Lattice Model of Secure Information Flow |

---

## 7. Nächste Schritte (nach Freigabe dieser Spec)

1. Review dieser Spec durch Daniel.
2. Falls freigegeben: eingefrorene Implementierungs-Spec (ADR) mit Acceptance-Tests als rote Suite.
3. Implementierung nur gegen die rote Suite; grüne Suite darf nicht angepasst werden.
4. Separater Adaptertest für echte Frameworks erst nach Fake-Lab-Nachweis.

---

*Diese Spec ändert keine eingefrorene v0.2-v0.5- oder Phase-2-Spec. Sie ist additiv und separat eingefroren.*
