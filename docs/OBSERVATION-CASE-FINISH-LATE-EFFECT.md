# Observer case: a fake effect appears after workflow finish

**Documented: 7 October 2026.** Existing evidence only; no new execution of this
probe is asserted here. Agent Authority's product role is exclusively observation,
monitoring and analysis under KI-Zentrale D-012.

## Evidence and scope

- [Confirmed finding](FINDING-PHASE1-FINISH-ADAPTER-EFFECT-GAP.md): first recorded
  against `b35851f`, reproduced at `6765765`; single-process Phase-1 FakeAdapter.
- [Existing deterministic probe](../probes/test_finish_adapter_effect_atomicity_probe.py):
  threading events impose the order; no network, credentials or external effect.
- [Previously documented repetition](https://github.com/landjunge/KI-Zentralle/blob/882af70599e4211267b043cb7595551e6bccb25e/docs/threaddesk/tool-suite-review/agent-authority.md)
  at lab `a12c3d6819d490919f7f0dc70c16d34b87d664d7`: the explicit probe failed.
- [OOS-021](OUT-OF-SCOPE-DEBT.md) remains open. The finding does not invalidate
  the separately tested in-process submit/registry repairs.

These are probe/code/finding records, **not a captured AA event replay**. The
probe uses `workflow_id="wf-finish-effect-gap"`, actor `agent-a` and resource
`src/late.py`. The coordinator calls `finish`; it is not an agent-triggered reset.

## What the existing record establishes

| Order imposed by the probe | Existing evidence | Meaning and limit |
|---|---|---|
| 1. A write is submitted and the lab returns ALLOW internally. | Wrapper calls the original `submit`, checks `decision.allow`, then signals `authorized`. | Historical model decision; no effect yet, no current product permission. |
| 2. The adapter is paused before receiving that decision. | Wrapper waits on `release_effect`. | The write effect is pending outside the monitor lock. |
| 3. The coordinator calls `finish`, which returns True. | Explicit `finish` assertion after `authorized`. | Monitor lifecycle cleanup completed; this is not a real executor-stop or revocation acknowledgement. |
| 4. The file is still absent. | Explicit `path not in adapter.repo.files` check. | No write effect at this checkpoint in FakeRepo. |
| 5. The coordinator releases the adapter; the worker finishes. | `release_effect.set`, joined thread, no worker errors, ALLOW result. | The delayed adapter operation proceeds under its earlier decision. |
| 6. The final assertion that the file remains absent fails. | Recorded finding output and existing probe. | A fake write effect became visible after completed `finish`. |

The order is established by synchronization, not by guessed timestamps or log
arrival order. No wall-clock event times or event IDs are supplied by this record.

## An evidence-supported observer statement

> In this documented fake-adapter case, workflow cleanup completed before an
> already-submitted write became visible. Completion of the monitor lifecycle
> therefore did not establish completion of every pending adapter effect.

The statement is about the recorded lab case. It does not establish production
impact, malicious intent, an invalid grant, a real effect after revocation, or a
currently implemented detector. AA would report the evidence and its limits;
executor and target-system owners remain responsible for real execution and any
intervention. AA neither grants the write nor stops or rolls it back.

## Missing observation evidence

| Missing from the existing record | Consequence |
|---|---|
| Captured concrete event IDs and a shared action/attempt/generation reference. | The existing probe cannot be presented as a correlated JSONL replay. |
| A recorded `finish` event and an independently recorded adapter/target effect event. | Phase-1 requested/allowed/denied events alone cannot reconstruct this lifecycle/effect sequence. |
| Documented event-time meaning, receipt time and source coverage. | No production ordering or completeness claim can be inferred. |
| Real executor-stop/revocation confirmation and real target-system evidence. | No real stop or access-revocation test has been performed by this case. |
| Persistent history after lifecycle cleanup. | Cleared in-memory provenance is not a durable effect history. |

No synthetic events, timestamps, generation IDs or outcome receipts have been
created to fill these gaps. Existing tests, frozen specs and the red-first probe
remain unchanged. This case sheet authorizes no repair of OOS-021 or new sensor.
