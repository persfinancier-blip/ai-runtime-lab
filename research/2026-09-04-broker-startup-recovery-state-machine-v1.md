# Broker Startup / Recovery State Machine V1

Date: 2026-09-04
Status: design contract frozen; exact RED/GREEN pending
Related: LAB-080/086/087/090/091/092/093/094..100

## Verdict

`BROKER_STARTUP_RECOVERY_STATE_MACHINE_V1_FROZEN`

## Objective

Freeze the end-to-end broker-owned startup machine that composes the already-frozen side-effect-free startup verifier, external-evidence collector, pure recovery planner, narrow recovery executor, and LAB-093 worker delegation boundary.

The state machine must terminate deterministically, never spin on UNKNOWN/stale state, never delegate a worker after a merely successful recovery command, and never collapse corruption into retryable recovery.

No production implementation or exact repository behavioral GREEN is claimed in this artifact. LAB-086 exact hidden-rowid publication remains priority #1 and production implementation of the provenance stack remains gated on executable RED/GREEN.

## Existing contracts composed

This machine does not create new lower-level authorities. It orchestrates:

- `verify_startup()` from `PROVENANCE_STARTUP_VERIFIER_RECOVERY_PLANNER_V1_FROZEN`;
- observational `ExternalEvidenceCollector` from `EXTERNAL_EVIDENCE_TERMINAL_ANCHOR_CONTINUITY_V1_FROZEN`;
- pure `plan_recovery()`;
- the four-command recovery grammar from `RECOVERY_EXECUTOR_COMMAND_GRAMMAR_IDEMPOTENCY_V1_FROZEN`;
- LAB-087 as sole writable broker/process/filesystem authority;
- LAB-091 as the local SQL/DML mutation gate;
- LAB-093 as least-capability worker delegation;
- LAB-090/LAB-100 activation fencing and retained activation authority;
- LAB-092/LAB-097..099 authenticated provenance and migration/history continuity.

The broker state machine is orchestration only. It may not bypass or emulate any of these contracts.

## Frozen states

V1 uses these conceptual states:

```text
START
  -> VERIFY_LOCAL
  -> COLLECT_EVIDENCE
  -> PLAN
  -> {FINAL_VERIFY | EXECUTE_ONCE | RETRYABLE_STOP | FATAL_STOP}
  -> POST_EXEC_VERIFY
  -> POST_EXEC_EVIDENCE
  -> POST_EXEC_PLAN
  -> {FINAL_VERIFY | RETRYABLE_STOP | FATAL_STOP}
  -> FINAL_EVIDENCE
  -> DELEGATE
  -> RUNNING
```

Terminal non-running states:

```text
RETRYABLE_STOP
FATAL_STOP
```

There is deliberately no generic `REPAIR`, `LOOP`, `TRY_AGAIN`, `AUTO_MIGRATE`, `AUTO_REBOOTSTRAP`, or `RELEASE_FENCE` state.

## Typed broker outcomes

A startup invocation returns exactly one class:

- `RUNNING(worker_capability_digest)` — delegation completed after the final clean gate;
- `RETRYABLE_EVIDENCE_UNAVAILABLE` — required observational evidence could not be obtained;
- `RETRYABLE_RECOVERY_UNRESOLVED` — exact recovery was attempted once but its outcome remains UNKNOWN/unresolved;
- `RETRYABLE_STALE_SNAPSHOT` — state changed after verification/planning and a fresh invocation is required;
- `RETRYABLE_CONCURRENT_PROGRESS` — another authorized actor advanced the exact state; no mutation is performed by this invocation;
- `RECOVERY_NON_PROGRESS` — a write-capable command reported success/progress but fresh verification still exposes the same actionable transition/snapshot class;
- `FATAL_CORRUPTION` — canonical/storage/chain/history/activation/migration/authority evidence is invalid;
- `FATAL_UNEXPLAINED_EXTERNAL_DRIFT` — terminal provider state is ahead/behind in a way not explained by exact authenticated provenance;
- `FATAL_AUTHORITY_MISMATCH` — retained DB/provider/activation/authority identities differ from construction-bound authority;
- `FATAL_UNSUPPORTED_VERSION` — canonical/protocol/schema version is unsupported;
- `FATAL_EPOCH_EXHAUSTED` — a required successor cannot be represented safely;
- `FATAL_INTERNAL_INVARIANT` — implementation violated the frozen state machine itself.

Retryable does not mean the broker may internally spin. It means the current invocation stops without worker delegation and without broadening authority.

## Phase 0 — retained construction

Before opening mutable runtime surfaces, construct and freeze the retained authority graph:

- canonical logical database identity;
- provider-history bootstrap/root identity;
- provider-history implementation/capability identity;
- exact provider descriptor/generation verification authority;
- LAB-100 activation-authority implementation/version/protocol descriptor;
- expected canonical schema/protocol versions;
- broker-owned least-capability evidence/executor handles.

Construction failure is fatal. No SQLite repair, bootstrap write, provider mutation, fence release, or worker endpoint creation occurs.

## Phase 1 — `VERIFY_LOCAL`

Call the side-effect-free verifier against a read-only or behaviorally read-only startup surface.

Required properties:

- full authenticated chain traversal from genesis;
- exact canonical decode/digest/type verification;
- exact local event-specific state-delta checks;
- at most one immediate PREPARED child;
- no provider calls hidden inside arbitrary local traversal;
- zero durable/runtime mutation.

Any verifier corruption class maps directly to a fatal broker outcome. Corruption is never passed to the planner as recoverable input.

On success, broker creates an immutable `StartupSnapshot` containing at least:

```text
snapshot_id
logical_database_identity_digest
retained_authority_graph_digest
verified_head_epoch
verified_head_link_digest
provider_descriptor_digest
activation_authority_digest
schema_state_digest
prepared_transition_digest | NONE
local_state_digest
```

The broker never identifies authority by `MAX(epoch)`, rowid, timestamp, or latest object.

## Phase 2 — `COLLECT_EVIDENCE`

Collect only the observational evidence explicitly requested by the successful verifier plus the terminal-anchor continuity evidence required for runtime opening.

All evidence must:

- carry the same `snapshot_id`;
- bind exact provider id/generation and retained verification authority;
- be observational: authenticated read, exact historical request reconcile, or independently-audited activation status read;
- leave SQLite, provider position, provider request-result state, provider generation, activation fence and authority state unchanged.

Unavailable transport/status becomes `RETRYABLE_EVIDENCE_UNAVAILABLE`. Invalid/forged/conflicting evidence is fatal, not retryable.

## Phase 3 — `PLAN`

Call pure `plan_recovery(VerifyResult, ExternalEvidence)`.

Exactly one of the following may result:

1. `NONE` — no write-capable recovery is authorized;
2. one exact command from the frozen grammar:
   - `RETRY_EXACT_PREPARED_REQUEST`;
   - `CONFIRM_EXACT_RECONCILED_REQUEST_THEN_COMMIT`;
   - `COMMIT_CONFIRMED_PREPARED_TRANSITION`;
3. typed retryable lack of evidence;
4. typed fatal mismatch/corruption.

The planner cannot refresh its own snapshot, choose a different transition, create a request id, or mutate state.

## Phase 4A — plan `NONE`

A `NONE` plan is necessary but not sufficient for worker delegation.

The broker proceeds to the final clean gate:

1. run a fresh side-effect-free verification;
2. require the authenticated local head/authority/schema identity to remain valid;
3. collect fresh terminal external evidence bound to the fresh final snapshot;
4. require terminal classification `ALIGNED` and no unresolved activation authority/fence condition that forbids runtime open;
5. require a fresh pure plan of `NONE`;
6. only then create/delegate LAB-093 worker capabilities.

If state changed between the first and final gate, do not reuse old evidence. Classify the fresh state from scratch.

## Phase 4B — `EXECUTE_ONCE`

If one exact recovery command is planned, the broker may invoke the write-capable executor **at most once in this startup invocation**.

The executor must perform its own preflight and in-transaction `preconditions_digest` recheck. The broker does not convert executor outcomes into alternate commands.

Outcome mapping:

- `RECOVERY_COMMITTED` -> mandatory `POST_EXEC_VERIFY`;
- `RECOVERY_UNRESOLVED` -> `RETRYABLE_RECOVERY_UNRESOLVED` and stop;
- `STALE_PLAN` / `PRECONDITION_MISMATCH` -> `RETRYABLE_STALE_SNAPSHOT` and stop;
- evidence unavailable -> `RETRYABLE_EVIDENCE_UNAVAILABLE` and stop;
- external conflict/unexplained advance/authority drift/fence mismatch -> fatal according to exact class;
- internal executor contract violation -> `FATAL_INTERNAL_INVARIANT`.

There is no second executor call from the same plan or snapshot.

## Phase 5 — `POST_EXEC_VERIFY`

After `RECOVERY_COMMITTED`, discard all previous `VerifyResult`, evidence, plan and snapshot objects.

Perform complete startup verification again from phase 1, with a newly computed snapshot id. Do not trust an executor success flag as evidence that the database/provider are now safe.

Then collect fresh evidence and plan again.

Required convergence rule:

- clean fresh state + final `NONE` plan may proceed to the final clean gate;
- corruption/drift is fatal;
- evidence unavailable is retryable stop;
- if the fresh planner still produces any actionable recovery command, **do not execute it in the same startup invocation**.

If the actionable transition digest and authenticated head are unchanged from the pre-execution snapshot, return `RECOVERY_NON_PROGRESS`.

If a genuinely new immediate PREPARED child/head appeared because another authorized actor progressed concurrently, return `RETRYABLE_CONCURRENT_PROGRESS`.

Both outcomes stop without worker delegation.

## Loop termination / liveness rule

V1 forbids unbounded in-process recovery loops.

Hard limits per broker startup invocation:

- unlimited pure local reads are not allowed as a spin mechanism; each logical phase executes once per snapshot;
- at most one external evidence collection bundle per snapshot, except the separately defined fresh final clean gate;
- at most one `RecoveryPlan` evaluation per snapshot;
- **at most one write-capable recovery executor invocation total**;
- at most one post-execution full verification/planning cycle;
- no sleep/retry/backoff loop inside the startup state machine.

A new retry requires a new broker startup invocation and therefore a fresh construction-bound snapshot/evidence cycle.

This bound is intentionally stronger than merely limiting attempts per request. The underlying exact LAB-080 request id remains the idempotency key across invocations, while one-executor-per-startup prevents a buggy planner/executor pair from self-driving through multiple authority transitions.

## Same-snapshot replay suppression

The broker retains an in-memory/run-scoped `AttemptFingerprint`:

```text
H(
  snapshot_id,
  authenticated_head_digest,
  prepared_transition_digest,
  plan_kind,
  preconditions_digest
)
```

Within one startup invocation, the same fingerprint may never reach `EXECUTE_ONCE` twice.

This fingerprint is a liveness guard only, not durable authority. It must not be persisted as a substitute for canonical provenance or LAB-080 request identity.

Across process restart, idempotency comes from the durable exact request/transition contracts, not this run-local fingerprint.

## Retryable versus fatal taxonomy

### Retryable only when authority/evidence remains intact

- temporary observational transport unavailable;
- exact UNKNOWN outcome remains unresolved after same-request reconciliation;
- plan became stale because authorized state changed before mutation;
- another authorized process made explainable progress;
- recovery command completed but a *different explainable* fresh immediate transition now requires a new startup invocation.

Retryable states preserve current activation fences and perform no generic cleanup.

### Fatal when trust continuity is not proven

- malformed canonical bytes/digest/type;
- schema or initialization provenance mismatch;
- chain gap/fork/rollback;
- missing/rebound provider history or activation ticket;
- retained authority/database/provider-generation mismatch;
- provider terminal position unexplained by authenticated provenance;
- conflicting historical request result;
- activation fence/authority mismatch;
- migration/authority transition bound to wrong parent;
- unsupported protocol/canonical version;
- same actionable state remains after an executor claimed committed progress.

Fatal startup never delegates a worker and never attempts repair.

## Activation-fence handling

The broker state machine itself has no fence mutation command.

- evidence phases never prepare/commit/release/abort;
- retryable stop preserves the exact current fence;
- fatal stop preserves the exact current fence unless a separately authenticated emergency protocol explicitly owns a change;
- executor may perform only event-specific activation lifecycle operations already permitted by LAB-090/LAB-100;
- generic startup success does not imply fence release;
- final delegation requires fresh verification that any activation lifecycle relevant to runtime opening is durably in the exact permitted terminal state.

A stale plan, transport outage, corruption finding, or startup timeout can never be treated as permission to release/abort a fence.

## Final delegation gate

LAB-093 worker delegation is a security transition and occurs only from a fresh clean final snapshot.

Before `DELEGATE`, require all of:

1. retained construction authority still matches;
2. fresh full local verification succeeded;
3. no PREPARED provenance transition is actionable/unresolved;
4. fresh terminal provider read is exactly `ALIGNED` with the authenticated local terminal position;
5. all required confirmed historical receipts/activation status evidence reauthenticate under the fresh snapshot;
6. fresh planner result is `NONE`;
7. no write-capable recovery has occurred since this final verification/evidence bundle;
8. no fatal/retryable outcome is pending;
9. worker capability set is derived only from the broker-owned least-capability LAB-093 façade, never from raw provider/SQLite/activation handles.

Delegation invalidates the startup snapshot for recovery purposes. If runtime later detects authority drift or a condition requiring recovery, it must revoke/close the runtime delegation according to the broker lifecycle and start a new startup/recovery invocation; it may not reuse startup recovery objects inside the worker.

## State transition table

| State | Success | Retryable | Fatal |
|---|---|---|---|
| START | VERIFY_LOCAL | — | construction failure |
| VERIFY_LOCAL | COLLECT_EVIDENCE | — | verification failure |
| COLLECT_EVIDENCE | PLAN | unavailable transport/status | invalid/conflicting evidence |
| PLAN/NONE | FINAL_VERIFY | unavailable evidence | planner invariant/corruption |
| PLAN/ACTION | EXECUTE_ONCE | unavailable evidence | invalid plan |
| EXECUTE_ONCE | POST_EXEC_VERIFY | unresolved/stale/concurrent | drift/conflict/invariant |
| POST_EXEC_VERIFY | POST_EXEC_EVIDENCE | — | verification failure |
| POST_EXEC_EVIDENCE | POST_EXEC_PLAN | unavailable | invalid/conflicting evidence |
| POST_EXEC_PLAN/NONE | FINAL_VERIFY | — | — |
| POST_EXEC_PLAN/ACTION | RETRYABLE_STOP or NON_PROGRESS | stop | same-state non-progress is fatal-class operational invariant for automation decisions but no repair |
| FINAL_VERIFY | FINAL_EVIDENCE | — | verification failure |
| FINAL_EVIDENCE | DELEGATE | unavailable/stale | invalid/conflicting evidence |
| DELEGATE | RUNNING | — | capability construction mismatch |

`FINAL_VERIFY` and `FINAL_EVIDENCE` always produce a new snapshot/evidence bundle; they cannot reuse the initial or pre-recovery bundle.

## RED-first matrix

Before production implementation, execute at least these cases on exact supported source:

1. clean aligned state -> final fresh verify/evidence -> delegate;
2. clean local state but final terminal read unavailable -> retryable stop, no delegation;
3. clean first snapshot, provider advances before final gate -> no delegation;
4. clean first snapshot, local head changes before final gate -> no delegation;
5. verifier corruption -> fatal, evidence collector not invoked when unnecessary;
6. invalid external evidence -> fatal, planner/executor not invoked;
7. actionable PREPARED -> exactly one executor invocation;
8. executor success -> old snapshot/evidence/plan discarded;
9. executor success -> full fresh verification required;
10. executor success -> fresh aligned NONE -> delegate only after final clean gate;
11. executor unresolved UNKNOWN -> retryable stop, no second executor call;
12. executor stale plan -> retryable stop, no internal re-plan/execute loop;
13. executor evidence unavailable -> retryable stop;
14. executor external conflict -> fatal;
15. executor authority drift -> fatal;
16. executor fence mismatch -> fatal;
17. executor reports committed but same transition/head remains actionable -> RECOVERY_NON_PROGRESS, no second execution;
18. executor commits and different authorized actor creates a new exact child before reverify -> concurrent-progress stop, no second execution;
19. same AttemptFingerprint cannot execute twice;
20. process restart may retry same durable request id through a new invocation;
21. retry across restart never creates a second request id;
22. retryable evidence outage preserves activation fence;
23. fatal corruption preserves activation fence;
24. stale plan preserves activation fence;
25. no generic startup state invokes release/abort activation;
26. no startup state calls catch-up/increment except executor command 1;
27. no startup state creates missing schema/history/bootstrap rows;
28. no startup state advances component watermark;
29. plan NONE from stale initial snapshot is insufficient for delegation;
30. final gate requires fresh snapshot id;
31. final evidence must all share final snapshot id;
32. final terminal classification ONE_BEHIND blocks delegation;
33. final terminal classification PROVIDER_AHEAD blocks delegation;
34. final activation status unverifiable blocks delegation;
35. fresh planner after final evidence becomes actionable -> no delegation;
36. unsupported canonical/protocol version -> fatal;
37. epoch exhaustion -> fatal before write;
38. chain fork discovered post-executor -> fatal, no repair;
39. historical ticket rebinding discovered post-executor -> fatal;
40. migration provenance mismatch post-executor -> fatal;
41. authority descriptor drift post-executor -> fatal;
42. restricted worker never receives raw verifier/executor/provider/SQLite authority;
43. worker delegation created only once per clean startup lifecycle;
44. failure while constructing delegated façade -> no partial raw-capability exposure;
45. runtime authority drift requires delegation shutdown + new startup invocation, not in-worker recovery;
46. two brokers start concurrently on one PREPARED transition -> at most one local commit; loser stops stale/concurrent;
47. two brokers both see clean state but one begins new authorized transition before the other's final gate -> stale broker does not delegate;
48. evidence collector side-effect snapshot before/after every startup path is unchanged;
49. retryable stop performs no compensating provider mutation;
50. fatal stop performs no compensating provider mutation.

## Audit conclusions

- Startup is a finite state machine, not a retry loop.
- A recovery command never directly authorizes runtime open; successful execution only authorizes fresh verification.
- One write-capable recovery attempt per startup invocation is sufficient for safety and makes non-progress observable rather than self-amplifying.
- Retryability is restricted to unavailable/uncertain but still authenticated state; trust discontinuity is fatal.
- Final worker delegation is based only on a fresh post-recovery/no-recovery verification plus fresh aligned external evidence and a fresh `NONE` plan.
- The state machine introduces no new mutation path beyond LAB-080/LAB-091/LAB-090/LAB-100 and no new raw capability beyond LAB-087/LAB-093.

## Next distinct evidence task if exact execution remains unavailable

Freeze the worker-session revocation/re-entry protocol after startup: exact conditions that invalidate a delegated LAB-093 session, how in-flight requests are quiesced, which runtime detections force broker re-entry, and proof that workers cannot retain stale SQLite/provider/activation capabilities across authority-generation or provenance-head changes. Do not implement production code until exact executable RED/GREEN is available.