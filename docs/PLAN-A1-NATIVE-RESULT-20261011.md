# A1 native: independent Writer remains UNBEKANNT

This is the separately authorized, bounded follow-up to source
`2ac7e1d8050a0e0f0cdf796f714183c702fe8783`. It does not reclassify historical A1,
execute A2, alter R0/B1/B2/C1 or change PR44. Spec freeze is `6d562e6`, diagnostic
implementation `56f0355`; the exact full SHAs and measurements are in
`PLAN-A1-NATIVE-RESULT-20261011.json`. Branch remains
`codex/research-abc-20261011`, origin `landjunge/agent-authority-lab`.

**Answer: UNBEKANNT under the tested conditions.** On macOS15.7.4/build24G517,
x86_64, effective UID501, no accessible source qualified for independent,
reliable attribution of a file operation to its actual causing process. No
universal impossibility for macOS is claimed. Root, ES entitlement/TCC grants,
audit activation, SIP changes and target instrumentation were not attempted.

Historical A1 remained INCONCLUSIVE because the frozen three-candidate preflight
read SDK contracts only. FSEvents provided no actor PID, kqueue no causal
file/process join, and proc_pidinfo only process snapshots. The required
independent Writer channel was missing before an experiment could start. That
historical result remains A FAIL/B INCONCLUSIVE, not REFUTED. A2 requires A1
SUPPORTED plus a defensible start-time/PID-version instance connection; C1's
three unmeasured A1 rows remain UNKNOWN. Primary historical references:
`PLAN-ABC-FORSCHUNGSPLAN-20261011.md` F2/F3/identity addition,
`PLAN-A1-SPEC-20261011.md`, `PLAN-A1-PREFLIGHT-RESULT-20261011.json`,
`PLAN-A2-STATUS-20261011.md`, `PLAN-ABC-AUSFUEHRUNG-20261011.md`,
`PLAN-C1-RESULT-20261011.json`, `LOKALE-PROZESSBELEGE-20261011.md`,
`NATIVE-HERKUNFTSMODUL-20261011.md`. Existing Mach handshakes and P7/P8 runs were
not repeated as new research.

The new basis is an actual SDK-compiled availability probe of FD/Vnode data,
OpenBSM access, ES initialization rejection and own-task Mach metadata. SDK15.0,
Apple clang16.0.0, strict Wall/Wextra/Werror; deprecated audit declaration is
explicitly known and its compiler warning suppressed. Installed header paths and
eleven hashes, exact commands, native return values, binary/source hashes and
UTC timestamps are archived in `a1-native-runs/2026-10-11/availability.json`.

| Source | Fields and trust boundary | Rights and actual availability | Limit for Writer question |
| --- | --- | --- | --- |
| `proc_pidinfo(PROC_PIDTBSDINFO)` | Kernel-derived PID/UID/start seconds+microseconds, stable before/after own-process snapshot; 136 bytes twice | Two actual successful nonroot calls on the observer only. **BELEGT** for these snapshots. Other-process access not tested. | No action/file identity; fork start does not identify an exec image. Snapshot is not a causal event. |
| `proc_pidfdinfo(PROC_PIDFDVNODEPATHINFO)` + `fstat` | Own read-only FD, kernel open flags, dev/inode/generation; 1200-byte return matches held regular file | Actual success on one empty artificial file. No all-process scan; raw path discarded. **BELEGT** for this descriptor/object match. | FD ownership/readability is not a write. Generation observed0, no persistent-generation/reuse claim; names can rename/replace. |
| File stat / process I/O information | Stat identity/metadata; `proc_pid_rusage` aggregate process counters by contract | Held-file stat actually used; rusage-info API contract only, not invoked. Snapshot access does not grant tracing. | Neither mtime nor aggregate I/O supplies an operation's causing actor; zero content stored. |
| Own `task_info(TASK_AUDIT_TOKEN)` / historical Mach trailers | Kernel self-task PID/version: 32-byte token, PID matches own BSD snapshot. Historical trailers attest immediate message sender only. | Actual self-task call succeeds nonroot. No new receive, foreign task port, task_for_pid or ptrace. **BELEGT** for the self snapshot. | Not a file action. PID-version and fork start remain different fields; exec can change PID-version. No external atomic A2 join inferred. |
| OpenBSM audit | Contract: subject PID/user/session, selected syscall/return/vnode records, audit timestamp. Library decoding alone grants no source access. | `auditon(A_GETCOND)` returns-1/EPERM1. `/dev/auditpipe` root0600; read-only open returns EACCES13. No record read, no preselection/configuration change. **BELEGT** for denial; audit enabled/disabled status **UNBEKANNT**. | Need accessible, configured kernel records, origin discrimination from user submissions, file/FD reconstruction, lifecycle/start binding and loss checks. Subject alone lacks tested PID-version/start. API deprecated in SDK since macOS11. |
| Endpoint Security | Contract: message process audit token/exec PID-version, start_time version>=3; WRITE target stat; event/mach time and sequence counters with version guards | Actual `es_new_client` returns `ERR_NOT_PRIVILEGED(5)` at UID501; zero callbacks/subscriptions, no client. Binary unsigned. Requires root and proper ES entitlement plus TCC/FDA approval. Actual TCC status **UNBEKANNT** because root rejection preempts it. `eslogger` exists root0755 without setuid; it was not run. | Technically promising action/actor/file contract, **UNBEKANNT** experimentally. Need permitted client, correct message version/action/target/gap handling and six controls; NOTIFY write is not durable file-state proof. |
| `fs_usage` / DTrace | Native tracing contracts can describe filesystem/syscall actors under their own access controls | `fs_usage -t1 <own wrapper PID>` exits1/root rejection; DTrace lists only `syscall::write:entry`, exits1/privilege rejection. No provider enabled. World0666 `/dev/dtrace` does not establish tracing permission. | No accessible event stream; full PID/file/lifecycle precision and coverage remain untested. No privileged fallback. |
| FSEvents / kqueue | Same pinned SDK contracts as original preflight | Read only, no new failed attribution battery or claimed runtime measurement. | Still no independent Writer field/causal join. Combining timing/snapshots does not manufacture it. |

The smallest **actually permitted qualifying Writer channel is none**. The
available metadata components are individually BELEGT, but their causal
identity/effect connection remains UNBEKANNT. ES is a documented candidate,
not a selected accessible source or proof of reliability. A privileged service
or audit event record would need its own approved operating conditions and
demonstrated coverage; this round did not activate either.

All six requested Writer scenarios are **NOT EXECUTED**: A writes target, B idle,
C writes another file, child writes, forged PID, two sequential writers of one
file. Each attribution stays UNBEKANNT. No separate Writer oracle was created
because no observer channel qualified. The single empty file and read-only
descriptor were availability setup, not a substitute six-case experiment.
Denominator0; correct/unclear attribution counts and rate remain null/UNBEKANNT.
There is no new Writer-hypothesis REFUTED/WIDERLEGT result or zero-error claim.

The initial strict compile failed on formatting a size_t count macro as unsigned
int. One explicit cast corrected this ordinary issue; the count stays8. The
967 diagnostic bytes, original hashes, initial failure and source reconstruction
diffs are retained. The subsequent native access measurement succeeded as a
diagnostic and documented the above denials. Measurements were made from the
working copy at the spec HEAD, not falsely called a committed runtime. The
measured C hash equals the committed C; archived reverse diffs reproduce the
initial Python and failed C. Later Python changes only strengthen temporary-path
and missing-tool handling; actual API selection/interpretation is unchanged.

Measured native body CPU user0.000225s + system0.000557s =0.000782s, monotonic
body1.238ms, process invocation75.336ms, peak RSS7,294,976 bytes from macOS
getrusage. These describe this fresh probe, not an ES/audit event stream, compiler,
Python wrapper or tracing service. The successful explicit output structures
total1504 bytes: BSD2x136, FD1200, Mach32. This is not total IPC traffic or raw
event bytes. Successful compile/probe/tool stdout+stderr1151 bytes; failed compile
967 bytes; separate read-only codesign query83 bytes. No raw error text, memory
structures, file paths from Vnode, file contents, foreign-process argv/environment, prompts,
provider/model responses or secrets archived. Event count/raw event bytes and
event-stream CPU/RAM remain UNBEKANNT, not zero. Stored-byte totals and artifact
hashes are recorded separately in `archive-metrics.json` and `artifact-index.json`.
Fixed own diagnostic command lines are retained for reproduction.
Data minimization does not improve the missing proof of causation.

Nineteen new unit tests check unknown/error/root/path/loss-of-snapshot/ES-stop
gates; they are not simulated Writer evidence. Two full Mac suites each588PASS,
five historical deselections, zero errors/failures/skips, one existing fork
DeprecationWarning. Ruff check/format, strict Mypy on32 core files, Bandit on
existing core scope, and strict C compilation pass. Linux PR-CI validates Python
and existing suite; it cannot execute this macOS C/API measurement. Source
files, case counts, JUnit hashes and minimized per-test projections are archived.

New-round availability-spec Axis A **PASS**; actual Writer hypothesis Axis B
**INCONCLUSIVE**, Writer/logical agent/authenticated identity-effect binding
**UNBEKANNT**. This is separate from old A1's unchanged FAIL/INCONCLUSIVE.
Confidence is high in the narrow access facts at the recorded host/time;
generalization and reliability of an unexecuted Writer experiment are UNBEKANNT.
All335 starting tracked files are byte-identical; D-012, historic hypotheses,
measurements, negative results and old tests remain intact. No merge or Ready.

The missing prerequisite is **an explicitly permitted live kernel action record
that binds the concrete file to the causing process instance**, plus lifecycle,
loss and file-identity checks. ES would additionally require root, entitlement
and appropriate FDA/TCC; its six-case suitability remains unmeasured. Audit would
require lawful stream access and appropriate existing configuration plus stronger
instance binding. No universal necessity for root across all imaginable macOS
mechanisms is inferred. No claim about logical agents or other OSes is made.

Primary external references are pinned with hashes in `primary-sources.json`:
[Apple libproc](https://raw.githubusercontent.com/apple-oss-distributions/xnu/f6217f891ac0bb64f3d375211650a4c1ff8ca1ea/libsyscall/wrappers/libproc/libproc.h),
[XNU audit access](https://raw.githubusercontent.com/apple-oss-distributions/xnu/f6217f891ac0bb64f3d375211650a4c1ff8ca1ea/bsd/security/audit/audit_syscalls.c),
[XNU audit records](https://raw.githubusercontent.com/apple-oss-distributions/xnu/f6217f891ac0bb64f3d375211650a4c1ff8ca1ea/bsd/security/audit/audit_bsm.c),
[Apple fs_usage](https://raw.githubusercontent.com/apple-oss-distributions/system_cmds/408bba7453608006b89772db185defbac8fe2fd0/fs_usage/fs_usage.c),
[ES root rejection](https://developer.apple.com/documentation/endpointsecurity/es_new_client_result_err_not_privileged),
[ES process](https://developer.apple.com/documentation/endpointsecurity/es_process_t),
[ES write](https://developer.apple.com/documentation/endpointsecurity/es_event_write_t).
Published XNU main is an explanatory source, not asserted to be the installed
kernel's exact source. Installed SDK hashes plus actual API results distinguish
contract facts, accessible evidence and untested prospects.
