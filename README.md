<!-- readme-header-v1: Kopf nach ThreadDesk docs/contracts/readme-header-v1.md. Nicht von Hand umgestalten; scripts/readme_header.py apply/check verwenden. -->

<p align="center">
  <img src="assets/readme/normalized/Agent-Authority-large.svg" alt="Agent Authority" width="256" height="256">
</p>

<p align="center">
  <a href="https://github.com/landjunge/KiraBridge#readme" title="KiraBridge"><img src="assets/readme/normalized/KiraBridge-small.svg" alt="KiraBridge" width="48" height="48"></a>
  &nbsp;
  <a href="https://github.com/landjunge/threaddesk#readme" title="ThreadDesk"><img src="assets/readme/normalized/ThreadDesk-small.svg" alt="ThreadDesk" width="48" height="48"></a>
  &nbsp;
  <a href="https://github.com/landjunge/4AllPass#readme" title="4AllPass"><img src="assets/readme/normalized/4AllPass-small.svg" alt="4AllPass" width="48" height="48"></a>
  &nbsp;
  <a href="https://github.com/landjunge/tollgate#readme" title="TollGate"><img src="assets/readme/normalized/TollGate-small.svg" alt="TollGate" width="48" height="48"></a>
  &nbsp;
  <a href="https://github.com/landjunge/blockdesign#readme" title="BlockDesign"><img src="assets/readme/normalized/BlockDesign-small.svg" alt="BlockDesign" width="48" height="48"></a>
</p>

<p align="center"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/design/wordmarks/AgentAuthority-dark.svg"><img src="assets/design/wordmarks/AgentAuthority-light.svg" alt="Agent Authority" width="352"></picture></p>

<!-- AUTO-DOWNLOADS:START -->
<p align="center">
  <a href="https://github.com/landjunge/agent-authority-lab/archive/refs/heads/master.zip" title="agent-authority-lab-master.zip herunterladen / download"><img src="assets/readme/download-source.svg" alt="Download Quellcode / Source ZIP · 0.3.0a2" width="190" height="52"></a>
</p>
<!-- AUTO-DOWNLOADS:END -->

<p align="center"><strong>Understand what your AI agents report.</strong><br>Nachvollziehen, was deine KI-Agenten melden.</p>

**Teil der NetzwerkPunkt-Werkzeugfamilie:** KiraBridge verbindet ChatGPT mit den Werkzeugen auf deinem Rechner und ist der zentrale Weg für die Bedienung per Sprache oder Chat. Zur Familie gehören **KiraBridge** (Verbindung und Steuerung), **ThreadDesk** (Projekte und Arbeitsstände), **4AllPass** (Zugänge und Schlüssel), **TollGate** (Nutzungsgrenzen und Budgets) und **Agent Authority** (ausschließlich Beobachtung und Nachweise). Die Werkzeuge bleiben eigenständig. **Die Verbindung aller fünf Werkzeuge über Sprache ist unser gemeinsames Ausbauziel:** Vorhandene Anbindungen und geplante Funktionen werden jeweils getrennt dokumentiert, nicht als schon vollständig fertig dargestellt.

## Aktueller Funktionsstand / Current capabilities

**Deutsch:** AgentAuthority ist eine Beobachtungs- und Analyseschicht. Die lokale Preview liest ausdrücklich ausgewählte JSON-Beobachtungen; ThreadDesk ist ein optionaler Adapter. Sie zeigt gemeldete Aufgabenaktivität, Warnungen und Belegreferenzen als Text, JSON oder offline lesbaren HTML-Bericht. Die native macOS-Oberfläche ergänzt Dashboard und Authority Graph. AgentAuthority erteilt keine Freigaben, gibt keine Geheimnisse oder Budgets frei und stoppt keine Aufträge. Gemeldete Identitäten und Erfolge sind keine unabhängig bestätigten Nachweise.

**English:** AgentAuthority observes and analyses explicitly selected local JSON observations, with ThreadDesk as an optional adapter. It reports task activity, warnings and evidence references as text, JSON or an offline HTML report. The native macOS interface adds a dashboard and Authority Graph. It does not approve actions, release secrets or budgets, or stop work. Reported identities and success labels are not independent verification.

Python 3.12+ is required for the local CLI. / Die lokale CLI benötigt Python 3.12 oder neuer. [Bedienung / Usage](docs/PRODUCT-PREVIEW.md) · [Eingabevertrag / Observation contract](docs/PRODUCT-OBSERVATION-CONTRACT.md) · [macOS](native/macos/README.md).

## Current product role

AgentAuthority is exclusively an **observer / monitor / analysis layer**, as
recorded in [KI-Zentrale decision D-012](https://github.com/landjunge/KI-Zentralle/blob/main/DECISIONS.md#d-012--agent-authority-beobachtet-entscheidungen-bleiben-bei-den-zuständigen-tools).
It reports observations, contradictions, risks and missing evidence. It does not
grant or revoke rights, approve actions, release secrets or budgets, or stop work.

The ALLOW/DENY, gate and IFC mechanisms below are **historical fake-lab
experiments**. Their positive results, measured misses, repairs and frozen specs
remain evidence within their original scope; they do not establish product
decision authority or authenticate the sources of the observer preview. The existing
[practice/research reconciliation](https://github.com/landjunge/KI-Zentralle/blob/main/docs/agent-authority/ABGLEICH-TESTS-UND-BEOBACHTER-RECHERCHE-2026-10-07.md)
keeps those distinctions explicit.

## Local product preview

The product accepts source-neutral local observations. ThreadDesk is an optional
archive adapter, not the product contract:

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install .
.venv/bin/agent-authority inspect --source json-directory --input /path/observations --source-id local-run
.venv/bin/agent-authority inspect --thread THREAD_ID --format json --limit 10
.venv/bin/agent-authority inspect --thread THREAD_ID --format html > report.html
```

The [current observation contract](docs/PRODUCT-OBSERVATION-CONTRACT.md) defines
the neutral input and report schemas. `--thread` selects the optional ThreadDesk
adapter; only that adapter defaults to `~/.threaddesk`, with `--store PATH` as an override. The report cites the read entries, shows reported task activity
and structural problems, and makes incomplete input visible. Stored actor,
success and authentication labels do not establish identity, actual completion
or effects. It writes no store, cache or report files and imports no historical
enforcement lab. Exit 2 indicates incomplete input, never an action decision.

[P10-01 contract](docs/P10-01-PRODUKTVERTRAG-20261011.md) and
[product usage](docs/PRODUCT-PREVIEW.md) describe the bounded local preview.
This is the start of the product phase; further UI and production deployment
require their own concrete work. The historical research below retains its scope.

The HTML format provides a single offline browser report with task and warning
tables and expandable entry evidence. Saving it is an explicit shell redirection;
the command starts no server and opens no browser. Text/JSON and the source
projection retain their existing semantics. The
[P10-02 scope](docs/P10-02-BROWSERBERICHT-VERTRAG-20261011.md) describes this display.

## Native macOS application

The standalone [native application](native/macos/README.md) provides a compact
dashboard, Authority Graph, evidence inspector, German/English localization and
a separate macOS permission/test host. It consumes the unchanged neutral product
report; reported entries do not become authenticated identities or effects.
Its explicitly marked 50-agent sample is for UI exploration. The local Intel
bundle includes Python 3.12 and targets macOS 12. Live Endpoint Security testing
requires Apple-approved entitlement, signing, extension activation and the
collector's own Full Disk Access. The development build cannot substitute these.

## Workflow observations / Workflow-Beobachtung

**English:** The current local preview adds a versioned, bounded workflow-metadata
projection over selected existing task/audit/event records. The original neutral
v1 remains unchanged. The native graph reads the explicit workflow-report wrapper,
shows reported task/run/handoff/source references and retains unknown identity and
external effect. It creates no new task queue/audit stream and grants no rights,
secrets, budgets, stop authority or project acceptance. Identical events are
counted once; conflicting, missing and unordered records stay visible.
[Scoped workflow findings](docs/WORKFLOW-WARNINGS.md) compare revision/return,
artifact and declared control/stop evidence; conflicts remain reported claims,
missing prerequisites remain unknown, and zero findings proves no global safety. Actual
limits, supported producer types and remaining live-adapter gaps are documented
in [Workflow observations](docs/WORKFLOW-OBSERVATIONS.md).

**Deutsch:** Die lokale Vorschau ergänzt eine versionierte, begrenzte Projektion
vorhandener Workflow-Metadaten. Der neutrale v1-Vertrag bleibt erhalten. Graph und
Inspector lesen den ausdrücklich neuen Workflow-Reportwrapper; Identität und
externe Wirkung bleiben unbekannt. Keine neue Aufgabenwarteschlange/Auditwelt,
keine Rechte-, Geheimnis- oder Budgetfreigabe und keine Nutzerabnahme. Duplikate
zählen einmal; Konflikte und Lücken bleiben sichtbar.
[Begrenzte fachliche Hinweise](docs/WORKFLOW-WARNINGS.md) vergleichen Revisionen,
Rückgaben, Artefakt- und gemeldete Kontroll-/Sperrbelege. Keine Hinweise bedeutet
keine allgemeine Sicherheitsbestätigung. Das Repository ist privat;
es gibt keinen öffentlich freigegebenen Download oder fertigen Webdienst.

```sh
agent-authority workflow-inspect --input /path/selected-metadata \
  --source-tool kirabridge --source-id local-run --format json
```

Version **0.3.0a2** is still the local source preview; this change does not create a
GitHub release or installed runtime upgrade. Python3.12 CLI and the macOS native
development path are distinct from a released package. Existing bounded readers
are already implemented; no new unrestricted archive intake is introduced.
[Actual scoped evidence](docs/evidence/seven-tools-20261018/STATUS.md).

## Historical research baseline

Experimental security lab: can **deterministic workflow-level state and information-flow enforcement** stop **some modeled** composition attacks that per-action authorization misses?

This is **not** a production system and **not** a proof of general agent safety.

## License

**Source-available — all rights reserved.** The repository is currently **private**. Access for review, research discussion, or security evaluation requires an explicit invitation; but new material may not be copied, modified, distributed, deployed, or sold without prior written permission. Historical revisions published before the license-change commit remain available under the MIT License that applied to them. See [LICENSE](LICENSE) for the exact boundary and terms.

## Status

The original v0.2 specification remains frozen. Subsequent additive experiments are separately frozen and reviewed. They do not rewrite v0.2.

| Layer | What | Notes |
|---|---|---|
| Phase 1 | v0.2–v0.5/I9 composition monitor | Completed experimental slices |
| Phase 2 Exp 01 | Explicit IFC vs authority-only | Hypothesis SUPPORTED *inside the fake lab* |
| Phase 2 Exp 02 | Communication Gate | Hypothesis SUPPORTED *inside the fake lab* |
| Phase 2 Exp 03 | Modeled implicit / control-flow dependency | Hypothesis SUPPORTED *inside modeled control dependencies* |
| Phase 2 repair | Value-id binding (no SENSITIVE→PUBLIC rebind) | Additive. Not Experiment 04. `docs/PHASE2-VALUE-ID-BINDING.md` |
| Phase 1 repair | In-process `submit` lock + `INVALID_REQUEST` | `docs/PHASE1-SUBMIT-ATOMICITY.md` |
| Phase 1 repair | FakeAdapter canonical path = repo key (T-19) | `docs/PHASE1-ADAPTER-IDENTITY.md` |
| Phase 1 repair | Public `state()` is a snapshot; provenance frozen | `docs/PHASE1-STATE-ENCAPSULATION.md` |
| Phase 1 repair | Workflow registry: capacity+reserve atomic; `finish()` is coordinator-only | `docs/PHASE1-WORKFLOW-LIFECYCLE-ATOMICITY.md` |
| Tooling | Program-STOP numbers, PBT oracles, CI | Not Experiment 04. See `docs/RESEARCH-METHOD.md` §3.1 and `docs/PBT-ORACLE-v1.md` |
| Tooling | Convergence battery protocol + catalog v1 | Additive. Not Experiment 04. `docs/CONVERGENCE-BATTERY-v1.md`, `docs/CONVERGENCE-ATTACK-CATALOG-v1.md` |
| Tooling | Convergence battery v1 scores | `k = 1` MISSED (CB-01). Not refuted on this battery. **Not** SUPPORTED. `docs/CONVERGENCE-BATTERY-v1-RESULTS.md` |
| Tooling | Real-case transfer study v1 | External battery (Codex) against `cb2dc55`. RC-01–RC-05 are measured misses, not broken tests. `docs/REAL-CASE-TRANSFER-STUDY-v1.md` |

Latest verified suite is recorded in the most recent review. **PASS ≠ SUPPORTED.**

**PASS ≠ SUPPORTED.** Green tests are spec conformance in this fake world. See [docs/RESEARCH-METHOD.md](docs/RESEARCH-METHOD.md).

The lab is separate from 4AllPass. No real credentials, production systems, or secrets.

The G3 producer appends Phase-1 Authority Event Envelope JSONL
(`authority.requested` / `allowed` / `denied`). It is on by default outside pytest
and off by default under pytest. `LAB_AUTHORITY_EVENTS=1` enables it explicitly;
`0`, `false`, `off` or `no` disable it in either context, ignoring case and
surrounding whitespace. Missing, empty or whitespace-only values retain the
context default; other nonempty values retain their existing enabled behavior.
It never writes a ThreadDesk database and does not change lab ALLOW/DENY.
This is not a Phase-2 or external-effect event stream. Exported metadata is not
automatically secret-free; complete redaction remains an open limitation.

## P1: controlled observer attempt

[P1 contract](docs/P1-CONTROLLED-RUN.md) and
[measured results](docs/P1-CONTROLLED-RUN-RESULTS.md): one standalone research
script, independent local target snapshot, **UNBEKANNT** for missing evidence.
Historical enforcement is unchanged. A started CLI process is not a proven
agent run; P1's recorded attempt has **zero proven agent runs**.

```bash
.venv/bin/python scripts/p1_controlled_run.py --out /tmp/aa-p1-new-run --timeout 60
```

The output directory must be new. Exit 2 means the agent run or reference
comparison is unproven; inspect the separate observations, analysis and result.
No raw CLI text is archived. This is not a complete execution audit or an
implementation of the full six-case research panel.

Historical PR19 research and the PR17 service reference are inventoried in the
[current research reconciliation](docs/RESEARCH-PR-ABGLEICH-20261011.md), with
pinned original sources, reproduced integration conflicts and separate scopes.

## Method (canonical)

- [docs/RESEARCH-METHOD.md](docs/RESEARCH-METHOD.md) — PASS vs hypothesis, cycle STOP, program-STOP, CI
- [docs/CONVERGENCE-BATTERY-v1.md](docs/CONVERGENCE-BATTERY-v1.md) — program-STOP battery protocol
- [docs/CONVERGENCE-ATTACK-CATALOG-v1.md](docs/CONVERGENCE-ATTACK-CATALOG-v1.md) — ten attacks; monitor-off frozen
- [docs/CONVERGENCE-BATTERY-v1-RESULTS.md](docs/CONVERGENCE-BATTERY-v1-RESULTS.md) — scores; `k = 1`; not SUPPORTED
- [docs/REAL-CASE-TRANSFER-STUDY-v1.md](docs/REAL-CASE-TRANSFER-STUDY-v1.md) — real-case transfer mappings; RC-01–RC-05 are known gaps
- [docs/OBSERVATION-CASE-FINISH-LATE-EFFECT.md](docs/OBSERVATION-CASE-FINISH-LATE-EFFECT.md) — existing finish/late-effect evidence from the observer perspective; missing events remain explicit
- [docs/realcase/v1/README.md](docs/realcase/v1/README.md) — archived ZIP + import prompt
- [docs/PBT-ORACLE-v1.md](docs/PBT-ORACLE-v1.md) — Hypothesis contracts (not I9 default-deny)
- [docs/THREAT-MODEL.md](docs/THREAT-MODEL.md)
- [docs/OUT-OF-SCOPE-DEBT.md](docs/OUT-OF-SCOPE-DEBT.md)
- [docs/EVALUATION-MATRIX.md](docs/EVALUATION-MATRIX.md)
- [docs/ADR-002-research-method-and-review-semantics.md](docs/ADR-002-research-method-and-review-semantics.md)
- [docs/ADR-001-I8-I9-action-boundary.md](docs/ADR-001-I8-I9-action-boundary.md) — historical I8/I9 conflict (unchanged)

Historical files titled “Independent Verification” are **not** renamed. Going forward they are read as same-context adversarial / post-implementation verification, not external audits.

## Research question

Can a workflow of individually authorized agent actions still create a forbidden cumulative outcome, and can a small deterministic composition monitor detect those cases without putting an LLM in the trusted core?

## Rules

- Use existing security primitives where possible.
- No custom cryptography.
- No custom capability format unless a concrete gap is demonstrated.
- LLMs may propose actions but must not authorize them.
- Tests are acceptance criteria and must not be weakened to fit an implementation.
- A failed hypothesis is a valid research result.
- Do not expand scope because a review said STOP; a new experiment needs a new frozen spec.
- After every commit, **push** to `origin`. Local-only commits are not done (`scripts/install-git-hooks.sh`).

## Frozen sequence (Phase 1 origin)

1. Spec v0.1
2. Composition Gate
3. Technology decisions
4. Prototype Spec v0.2
5. Build deterministic prototype
6. Test against frozen v0.2
7. Additive slices v0.3–v0.5/I9 and Phase 2 experiments (each frozen separately)

See `docs/` for the frozen design documents. Historical reviews keep their original titles and verdicts.

## v0.2 prototype (deterministic core)

Local composition monitor only. No LLM, no network, no real credentials.

```text
ActionRequest → predict next WorkflowState → evaluate I1–I6
  ALLOW: commit state + provenance
  DENY:  leave state unchanged
```

### Invariants

| ID | Rule |
|---|---|
| I1 | `action_count <= 100` |
| I2 | unique written files `<= 10` |
| I3 | `config/security-policy.json` is immutable |
| I4 | `delegation_depth <= 1` |
| I5 | any `net.connect` destination is forbidden |
| I6 | `repo.delete` / `release.publish` need `parameters.approval_token` |

**Delegation convention:** root actor depth is 0. `root → A` is depth 1 (allowed). `A → B` is depth 2 (denied).

I4 only constrains the `delegate` action. Independent agents may still submit into the same `workflow_id` at depth 0 (required for the cross-agent accumulation tests). That is not a depth-chain.

### Run tests

```bash
python3.12 -m venv .venv
.venv/bin/pip install -e ".[dev]"
.venv/bin/pytest -q
# CI runs the same suite twice on Python 3.12 (see .github/workflows/test.yml)
```

### What v0.2 does **not** prove

- general agent safety
- alignment or proof of intent
- complete information-flow security
- semantic code safety
- enterprise readiness
- that Biscuit, Cedar, or FIDES would help (not integrated)

A STOP result on the research hypothesis is valid.

## v0.3 (canonical artifact identity)

Additive. Frozen v0.2 is unchanged. See `docs/PROTOTYPE-v0.3.md`.

- Path aliases (`./`, `..`, `//`) collapse before I2/I3.
- **I7:** `file.delete` of `tests/test_security.py` or anything under `tests/security/` needs `approval_token`.

## v0.4 (I8 — mutation completeness)

Additive. Frozen v0.2 and v0.3 are unchanged. See `docs/PROTOTYPE-v0.4.md`.

- Mutating verbs on the protected policy other than `file.write` are DENY (I8). I3 is not relaxed.
- Mutating verbs on security-test artifacts other than `file.delete` need `approval_token` (I8).
- I7 identity matcher is the v0.3 list only (no filename heuristic).
- Not in this slice: global default-deny, I2-on-delete, adapter key canonicalization.

## v0.5 (I9 — unknown action on protected identity)

Additive. Frozen v0.2–v0.4 are unchanged. See `docs/PROTOTYPE-v0.5-I9.md`.

- Unknown action string + protected canonical identity → DENY `I9_UNKNOWN_ACTION_PROTECTED`.
- Exact known/safe vocabulary only. No case folding, no alias interpretation, no LLM.
- I9 does not globally deny unknown actions on ordinary resources.
- `approval_token` does not authorize an unknown policy action.

## Phase 2 (Experiment 01 — IFC composition)

Additive and isolated under `lab/phase2/`. Frozen spec: `docs/PHASE2-EXPERIMENT-01.md`.

Does not amend Phase 1. No LLM. Two labels only (`PUBLIC` / `SENSITIVE`).

A/B: authority-only lets the READ→TRANSFER→EGRESS composition succeed; authority+IFC denies SENSITIVE external egress while PUBLIC egress by B remains ALLOW.

## Phase 2 (Experiment 02 — Communication Gate)

Additive. Frozen spec: `docs/PHASE2-EXPERIMENT-02-COMMUNICATION-GATE.md`. Experiment 01 is unchanged.

Cross-agent transfer is `A → Communication Gate → B`. The gate evaluates metadata only (`evaluate_transfer`). No payload, tools, credentials, or policy writes.

## Phase 2 (Experiment 03 — modeled implicit flow)

Additive. Frozen spec: `docs/PHASE2-EXPERIMENT-03-IMPLICIT-FLOW.md`. Experiments 01–02 unchanged.

Explicit `derived_from` IFC is the baseline. Modeled `control_decide` + `created_under` inherit SENSITIVE across A’s state write so B’s egress can be denied without transferring C1. PUBLIC control-flow egress remains ALLOW. No payload DLP, no LLM.


