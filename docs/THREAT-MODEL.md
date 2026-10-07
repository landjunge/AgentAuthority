# Threat Model (lab-wide, conservative)

Fake-world laboratory. Evidence is **only** as strong as the modeled APIs and pytest suite on the cited commits. **PARTIALLY TESTED** is the default when a threat was exercised only inside that fake model.

Status values: `TESTED` · `PARTIALLY TESTED` · `NOT TESTED` · `OUT OF MODEL`

| ID | Threat | Attacker / failure source | Description | Security relevance | Current status | Evidence | Tested in | Remaining gap | Claim impact |
|---|---|---|---|---|---|---|---|---|---|
| T-01 | Accidental agent mistake | Confused but non-malicious agent | Individually allowed actions that still violate a global invariant | High for composition | PARTIALLY TESTED | I1–I9 deny paths; Phase 2 honest mistakes encoded as APIs | Phase 1, Exp 01–03 | Unmodeled APIs; real planner mistakes | Supports narrow claim only for modeled verbs |
| T-02 | Malicious task decomposition | Task splitter | Split a forbidden goal into allowed steps | High | PARTIALLY TESTED | Budget/file/delegation split; IFC composition; implicit-flow encode | Phase 1 I1/I2/I4; Exp 01; Exp 03 | Semantic task graphs untested | Does not cover planner-level malice |
| T-03 | Budget splitting | Colluding agents | Exhaust a shared action budget across actors | High | PARTIALLY TESTED | A 60 + B 41 → action 101 DENY | Phase 1 I1, cross-agent tests | Real schedulers; in-process last-slot and registry races are tested separately | Narrow composition claim |
| T-04 | Delegation splitting | Agent chain | Extra hop beyond depth 1 | Medium–high | PARTIALLY TESTED | root→A ALLOW, A→B DENY | Phase 1 I4 | Peers at depth 0 still share workflow (by design) | I4 is chain-depth, not collusion |
| T-05 | Multi-agent cumulative composition | Several agents, one `workflow_id` | Shared counters / shared IFC graph | High | PARTIALLY TESTED | Cross-agent I1; Exp 01 transfer; Exp 03 state read; Phase-1 in-process submit/registry races (`docs/REVIEW-WORKFLOW-LIFECYCLE-ATOMICITY.md`) | Phase 1, Exp 01, Exp 03 | Phase-2 concurrency and distributed execution; Phase-1 adapter-effect commit is a separate open gap (OOS-021) | Supports workflow-global state claim inside the modeled APIs |
| T-06 | Confused deputy | Caller abuses a privileged helper | Gate/runtime used to write/execute | High | PARTIALLY TESTED | Exp 02: no `execute`/`write`/`read_payload` on gate | Exp 02 | Compromised runtime (T-18) | Only for exposed gate API |
| T-07 | Explicit information laundering | Wrap/copy/derive, claimed PUBLIC | Strip SENSITIVE via modeled transforms | High | PARTIALLY TESTED | Exp 01 wrap; Exp 03 wrap/copy under control dep | Exp 01, Exp 03 | Unmodeled byte edits (OOS-008) | Modeled transforms only |
| T-08 | Cross-agent sensitive-data transfer | A reads, B sends | READ→TRANSFER→EGRESS | High | PARTIALLY TESTED | Authority-only attack SUCCESS; IFC DENY at egress | Exp 01, gated in Exp 02 | Direct Exp 01 path still exists by design | Core of Exp 01 claim |
| T-09 | Label spoofing | Agent-supplied PUBLIC | Forged label on transfer | High | PARTIALLY TESTED | Extra kwargs ignored; runtime envelope wins | Exp 02 | Wrong initial label (T-20) | Gate/runtime only |
| T-10 | Provenance spoofing | Drop origin | Agent tries to rewrite `derived_from` | High | PARTIALLY TESTED | Origin stays `fake://customers` | Exp 02 | Runtime compromise | Same |
| T-11 | Value substitution | Bind C1 payload to P1 envelope | Identifier swap | High | PARTIALLY TESTED | `(workflow_id, value_id)` binding | Exp 02 | Adapter mismatch Phase 1 | Exp 02 modeled store |
| T-12 | Replay | Reuse `message_id` | Duplicate delivery | Medium | PARTIALLY TESTED | Consumed id → REPLAY | Exp 02 | Not cryptographic replay | Lab replay only |
| T-13 | Cross-workflow substitution | Other `workflow_id` | Steal foreign value_id | High | PARTIALLY TESTED | CROSS_WORKFLOW_REFERENCE; Exp 03 isolated labs | Exp 02, Exp 03 | Shared process memory if runtime broken | Workflow-scoped values |
| T-14 | Modeled implicit / control-flow leak | Encode bit in state without `derived_from(C1)` | Decision→public-looking state→B egress | High | PARTIALLY TESTED | Baseline SUCCESS; control-dep BLOCKED | Exp 03 | Unmodeled `if` (T-15) | Hypothesis scoped to modeled APIs |
| T-15 | Unmodeled implicit flow | Raw `if` never calling `control_decide` | Same leak without modeled decision | High | NOT TESTED / OUT OF MODEL | Exp 03 review names it as remaining weakness | Exp 03 limitations | Would refute broader IFC claims | Must not be claimed solved |
| T-16 | Prompt injection | Untrusted text → tools | Not in fake lab | High | NOT TESTED | None | — | Entire class | Broader claim invalid if asserted |
| T-17 | Malicious agent with system knowledge | Agent knows monitor rules | Game the modeled APIs | High | PARTIALLY TESTED | Adversarial probes inside APIs | All slices | Knowledge of unmodeled channels | Only modeled surface |
| T-18 | Compromised runtime | Trusted store lies | Labels/payloads rewritten | Critical | OUT OF MODEL | Specs say so | Exp 02 §13 | Invalidates all IFC | Never claim runtime honesty |
| T-19 | Compromised adapter | Execution path ≠ monitor identity | Canonical deny, wrong file mutated | High | PARTIALLY TESTED | FakeAdapter now uses `canonical_path` for submit and repo keys (`docs/PHASE1-ADAPTER-IDENTITY.md`). A future adapter that skips that edge is still this threat. | Phase 1 adapter identity repair | Real/other adapters | FakeAdapter aligned; not a general adapter proof |
| T-20 | Wrong initial label | Source labels C1 PUBLIC | Poisoned birth certificate | High | OUT OF MODEL | Exp 02 non-claims | — | IFC follows bad labels | Do not claim labeling oracle |
| T-21 | Off-channel collusion | Side chat, shared disk | Bypass workflow objects | High | OUT OF MODEL | Exp 02 | — | Breaks “workflow is the channel” | Narrow claim only |
| T-22 | Cross-session laundering | Persist bit across runs | New workflow_id clean | Medium–high | NOT TESTED | Isolation is per object, not durable store | — | No session model | Unclaimed |
| T-23 | Timing channel | Duration leaks C1 | — | Medium | OUT OF MODEL | — | — | Noninterference | Unclaimed |
| T-24 | Covert channel | Any unused bit | — | High | OUT OF MODEL | Exp 02/03 | — | — | Unclaimed |
| T-25 | Semantic harmful composition | Allowed acts, harmful meaning | — | High | NOT TESTED | No semantic analyzer (by design) | — | Alignment/intent | Explicitly non-claimed |
| T-26 | Intent drift | Goal changes over steps | — | Medium | NOT TESTED | No intent model | — | — | Unclaimed |
| T-27 | Allowed-channel abuse | Encode via allowed fields | Status bit in Exp 03 | High | PARTIALLY TESTED | Exp 03 modeled status; other channels not | Exp 03 | Other PUBLIC fields | Only modeled state keys |
| T-28 | Encoding / steganography | Hide data in PUBLIC payload | — | High | NOT TESTED | PUBLIC payload `CUSTOMER_FLAG` ALLOW (anti-DLP) | Exp 01–03 | Content hiding | DLP not a claim |
| T-29 | Denial of service | Deny all comms / freeze workflow | — | Medium | PARTIALLY TESTED | Honesty: PUBLIC comms still ALLOW | Exp 02 | Resource exhaustion | Not a DoS study |
| T-30 | Provenance-log manipulation | Alter attempt logs | Integrity of explanations | Medium | NOT TESTED | Logs are in-process lists | — | No signed log | Explanations are not tamper-evident |
| T-31 | Agent-invoked `finish()` | Agent with a Lab reference | `finish(workflow_id)` drops counters and provenance; the next `submit` is a new generation | High | PARTIALLY TESTED | Lifecycle tests treat `finish` as coordinator-only; it is not an I1–I9 action | Phase 1 workflow lifecycle | No in-lab access control on the Python method; the object is TCB | Do not claim agents cannot reset budget if they can call `finish` |
| T-32 | Registry TOCTOU / stale lock | Concurrent `submit` / `finish` / new ids | Capacity check vs reserve; `finish` dropping a lock `submit` still holds a reference to | High | PARTIALLY TESTED | Forced-seam tests in `tests/test_workflow_lifecycle_atomicity.py` | Phase 1 workflow lifecycle | Multi-process (OOS-011) | In-process table only |

Phase 1 I1–I9 remain composition/state experiments, not a full IFC OS. Treat them as **PARTIALLY TESTED** even where pytest is green.
