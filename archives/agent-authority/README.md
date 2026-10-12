# Historical Agent Authority source contracts

These archives preserve complete, unmodified Git trees and their existing data,
code and tests. They are historical references, not active product modules or
newly accepted functionality. Extract separately to inspect an original contract.
No tests or experiments were executed during consolidation.

- PR19: the old FD verifier would change P5 merely through source-file presence;
  the original recorder/probes/tests remain together in their frozen source tree.
- The first resource-epoch branch contains an independent earlier trial and is
  retained separately from PR19 rather than replacing its later data.
- PR17: the operational ALLOW/DENY/REQUIRE_APPROVAL gateway contradicts D-012
  and remains an inactive historical reference. It is not product authority.
- Early runtime-hardening tests require mutable state allocation and unbound
  approval strings. Current snapshots, lifecycle/effect tickets and bound approvals
  remain unchanged; the old test/source contract is preserved intact.

Current code, tests, configurations and research evidence remain those of
`e72dc38dc87a87a786386f2cf961d94ea3c46769`, with the existing action-identity draft
added unchanged. `MANIFEST.json` records source SHAs, original-blob preservation,
archive hashes and per-branch merge/conflict dispositions. All branch histories
are retained through ordinary merges. No ThreadDesk, Tollgate or 4AllPass runtime
is introduced. This merge is not a tested baseline or a research acceptance.
