# Handoff: observer documentation and explicit event-export disable flag

**Date:** 7 October 2026. **Package:** one small documentation/code correction.
Requested by the repository owner: both documentation and code in small steps.

## Scope and changes

- Base: `a12c3d6819d490919f7f0dc70c16d34b87d664d7`.
- Branch: `fix/observer-docs-event-disable-flag`; separate review branch, no merge.
- README: current observer-only product role and references to KI-Zentrale D-012;
  historical ALLOW/DENY, IFC and gate experiments keep their original meaning.
- Threat model T-05: recognize documented Phase-1 in-process submit/registry
  checks; Phase-2/distributed concurrency and the adapter-effect gap remain open.
- [Finish/late-effect case sheet](OBSERVATION-CASE-FINISH-LATE-EFFECT.md): existing
  finding and probe interpreted from the observer perspective, missing events
  explicit. No new probe execution, generated replay or new detector is asserted.
- `lab/authority_emit.py`: explicit `0/false/off/no`, including case/whitespace
  variations, now disable export under pytest as well as outside it. Previously
  any nonempty value enabled export under pytest.
- `tests/test_authority_event_flags.py`: additive regression tests use in-memory
  lab actions and temporary output paths, including unchanged ALLOW/DENY results
  and absence of both the export file and its parent directory when disabled.

Missing/empty/whitespace flags retain their existing defaults: off under pytest,
on outside pytest. Other nonempty values retain their previous enabled behavior.
No event schema, gate, validator, execution, budget or approval logic changed.
Existing test files, frozen specs, historical reviews and the red-first probe
are unchanged.

## Verification

All new runs used the existing environment's Python 3.12 and pytest with
`PYTHONDONTWRITEBYTECODE=1` and `-p no:cacheprovider`. No new dependency was added.

| Check | Result and scope |
|---|---|
| New tests before implementation | **8 failed, 18 passed**: all eight failures were explicit disable values under pytest still writing events. |
| New tests plus existing emitter tests after implementation | **29 passed**. Real `Lab.submit` calls verify emission/defaults and model decisions; no network or real credentials. |
| Standard suite, run 1 | **239 passed, 5 deselected**. |
| Standard suite, run 2 | **239 passed, 5 deselected**. Reproducibility check, not a general security evaluation. |
| Existing test integrity | Changes are additive; no existing test or frozen specification altered. |
| Documentation | Relative links and diff whitespace checked; independent read-only documentation and code review passed. |

The five deselected Realcase expectations are the existing RC-01–05 gaps.
The finish/adapter probe is outside the standard test paths. Neither the green
suite nor this flag repair closes these findings. They were not explicitly
rerun for this package; their historical findings remain available.

## Remaining limits and next step

Metadata is not automatically secret-free. Missing shared action/attempt
references, Phase-2 emission, finish/effect events, persistence and source
authenticity remain unimplemented or unproven. No current AA observer detection
performance is established. OOS-021 remains open; this package neither repairs
that lifecycle boundary nor changes product AA into an enforcement component.

Publish this reviewed branch and record its commit in the KI-Zentrale handoff.
No automatic next feature or experiment is authorized by this package.
