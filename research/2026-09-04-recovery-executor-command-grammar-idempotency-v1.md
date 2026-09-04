# Recovery Executor Command Grammar + Idempotency V1

Date: 2026-09-04
Status: design contract frozen; exact RED/GREEN pending
Related: LAB-080/086/090/091/092/093/097..100

## Objective

Freeze the only write-capable commands that may consume a previously verified `RecoveryPlan`. The executor must not discover new recovery work, repair arbitrary corruption, synthesize new request identities, or weaken activation fencing. It may only complete the single exact PREPARED transition already authenticated by the verifier/planner.

A fresh direct `git clone --no-checkout` again failed before repository access with `Could not resolve host: github.com`; no production code and no new behavioral PASS are claimed in this run.

## Source constraints retained

LAB-080 already provides the relevant idempotency shape: `reserve()` persists one deterministic `(intent_id, position, request_id)` as `PREPARED`; `execute()` may advance the provider with the exact request, then `_reauthenticate()` by exact `request_id`, and only afterward marks the local intent `CONFIRMED`. A timeout after provider commit is therefore recoverable only by reconciling the same request id. `verify_component()` is not an executor primitive because it can advance a watermark.

The previously frozen startup verifier/planner and external-evidence collector establish that verification is side-effect free, at most one immediate PREPARED child is actionable, every plan carries a `preconditions_digest`, and evidence collection never mutates provider/SQLite/activation state.

## Command grammar

V1 permits exactly three recovery commands plus no-op:

```text
NOOP
RETRY_EXACT_PREPARED_REQUEST
CONFIRM_EXACT_RECONCILED_REQUEST_THEN_COMMIT
COMMIT_CONFIRMED_PREPARED_TRANSITION
```

No generic `REPAIR`, `CATCH_UP`, `RELEASE_FENCE`, `RECREATE_SCHEMA`, `REBOOTSTRAP`, `ROTATE_PROVIDER`, `UPGRADE_AUTHORITY`, `ADVANCE_HEAD`, or `CONFIRM_LATEST` command exists.

Every non-NOOP command is fully bound to:

- logical database identity digest;
- retained authority graph digest;
- authenticated parent head `(epoch, link_digest)`;
- exact PREPARED transition id;
- exact event and successor-link digests;
- exact LAB-080 `anchor_intent_id`;
- exact LAB-080 deterministic `request_id`;
- exact predecessor and expected position;
- exact provider id/generation;
- exact activation-authority descriptor when applicable;
- exact local LAB-080 status expected by the command;
- planner `preconditions_digest`.

The executor never substitutes equivalent-looking rows or recalculates a new request id from mutable current state.

## Common executor preflight

Before any provider call or SQLite write, the executor:

1. validates the command/domain/version and strict canonical types;
2. opens the broker-owned supported database identity only;
3. starts no write transaction yet;
4. re-reads the authenticated parent head, exact PREPARED transition, event/link bytes, LAB-080 intent, provider descriptor and activation-authority descriptor;
5. recomputes the planner `preconditions_digest` and requires exact equality;
6. rejects if the PREPARED transition is no longer the sole immediate child of the head;
7. rejects any provider-generation/authority/schema drift;
8. requires any active LAB-090 activation fence to match the authenticated ticket/transition contract.

A stale plan is terminal for that execution attempt. The executor does not refresh or re-plan internally; caller must restart side-effect-free verification.

## Command 1 — `RETRY_EXACT_PREPARED_REQUEST`

Eligibility:

- local LAB-080 intent is exactly `PREPARED` with `receipt_binding IS NULL`;
- provider terminal evidence proves position is exactly the predecessor;
- exact `reconcile_increment(request_id)` proves no result for the frozen request;
- provider id/generation and activation authority still match the plan;
- event/link/transition bytes remain unchanged.

Ordering:

1. complete common preflight;
2. obtain fresh observational terminal read and exact-request reconcile;
3. if exact result now exists, do **not** issue increment; switch is not performed internally — reject as stale and require re-plan;
4. if provider is still exactly at predecessor and request has no result, issue exactly one mutating increment/catch-up using the already-frozen `request_id` and expected position;
5. on success or timeout/UNKNOWN, immediately use exact-request reconcile only;
6. if exact authenticated result at expected position is obtained, continue to the local confirmation/finalization sequence below;
7. otherwise leave local PREPARED state and any activation fence unchanged and return `RECOVERY_UNRESOLVED`.

Idempotency rule: repeated execution can never allocate a second request id or second position. Provider idempotency is keyed only by the frozen request id. An UNKNOWN result never authorizes a new probe mutation.

## Command 2 — `CONFIRM_EXACT_RECONCILED_REQUEST_THEN_COMMIT`

Eligibility:

- local LAB-080 intent is `PREPARED`;
- fresh exact-request reconcile proves the frozen request committed at the exact expected position;
- stable receipt binding is derivable and matches provider identity/generation;
- no local/authenticated state changed since planning.

Ordering:

1. common preflight;
2. fresh exact reconcile outside the SQLite write transaction;
3. verify exact request/position/provider/generation and derive canonical receipt binding;
4. begin the LAB-091-authorized `BEGIN IMMEDIATE` transaction;
5. re-read all local preconditions and recompute `preconditions_digest` inside the transaction;
6. consume the one-shot permit to change only the exact LAB-080 row `PREPARED,NULL -> CONFIRMED,<receipt_binding>`;
7. verify the exact provenance transition/event/successor link remain unchanged;
8. atomically mark the exact provenance transition `PREPARED -> COMMITTED` and advance the authenticated local chain-head cache to that successor under the frozen storage/append contract;
9. commit;
10. perform no provider mutation after the transaction.

If the process crashes after external commit but before step 6, restart re-plans the same command. If it crashes after SQLite commit, fresh startup verification must see the transition committed and must not replay provider mutation.

## Command 3 — `COMMIT_CONFIRMED_PREPARED_TRANSITION`

Eligibility:

- LAB-080 row is already exactly `CONFIRMED` with the frozen receipt binding;
- fresh exact-request reauthentication outside the write transaction reproduces the same binding;
- provenance transition remains PREPARED and is the sole immediate child of the authenticated head.

Ordering:

1. common preflight;
2. fresh receipt reauthentication outside the transaction;
3. begin LAB-091-authorized `BEGIN IMMEDIATE`;
4. recompute all local preconditions and exact receipt binding reference;
5. do **not** touch provider position or LAB-080 status;
6. atomically mark only the exact provenance transition COMMITTED and advance local authenticated head to its successor;
7. commit.

This command is local finalization only. It may never call provider increment/catch-up or change an activation fence.

## Terminal-anchor advancement rule

Only the first command may perform a provider-side terminal-anchor mutation, and only for the already frozen LAB-080 request id. Commands 2 and 3 are local completion commands after external commitment has already been proven.

No recovery command may skip positions, batch positions, issue a new request id, or advance a component watermark as a substitute for provenance completion.

## Activation-fence rules

Recovery never treats a fence as cleanup metadata.

- Evidence collection and common preflight cannot prepare/commit/release/abort a fence.
- If the transition being recovered is itself an activation transition, the executor may perform only the activation lifecycle action explicitly committed by that event-specific protocol and only after its own fresh preconditions are satisfied.
- A fence protecting an unresolved provider-generation activation remains installed across crashes, UNKNOWN outcomes, stale-plan rejection and local SQL failures.
- `release_activation` is permitted only after the exact local durable acknowledgement required by LAB-090/LAB-100 has committed and fresh verification proves the release precondition.
- Failed or stale recovery may never release/abort a fence as generic rollback.

For non-activation provenance commands, activation state must be byte/state-equivalent before and after execution except for independently specified event-specific transitions.

## Crash windows and deterministic restart classification

V1 explicitly recognizes these windows:

1. crash before provider mutation — local PREPARED remains; re-plan from scratch;
2. crash/UNKNOWN during provider mutation before caller knows result — reconcile exact frozen request id;
3. provider committed, local LAB-080 still PREPARED — command 2 after fresh reconcile;
4. LAB-080 CONFIRMED but provenance transition still PREPARED — command 3 after fresh receipt reauthentication;
5. provenance transition + head committed — no recovery command; normal full verification only;
6. crash after any failed SQLite transaction — no compensating provider mutation and no fence release; restart verification decides state.

The executor never writes a durable "execution succeeded" flag as an independent authority source. Authority remains exact provider receipt + authenticated local chain state.

## Stale-plan and concurrency rejection

Before every consequential local write, the executor must prove all plan-bound values are unchanged inside `BEGIN IMMEDIATE`. Any mismatch raises a typed stale/conflict outcome before mutation.

Two executors racing the same plan converge because:

- only one can hold the write transaction;
- the first successful transition changes the exact old-state predicate;
- the second must fail its precondition re-read and cannot reinterpret the new state as permission to continue;
- provider mutation is keyed by the same deterministic request id, never a newly generated id.

No command may act on `MAX(epoch)`, latest rowid, latest PREPARED row, or caller-selected alternate transition.

## Required typed outcomes

Minimum executor outcomes:

- `RECOVERY_NOOP`
- `RECOVERY_COMMITTED`
- `RECOVERY_UNRESOLVED`
- `STALE_PLAN`
- `PRECONDITION_MISMATCH`
- `EXTERNAL_EVIDENCE_UNAVAILABLE`
- `EXTERNAL_REQUEST_CONFLICT`
- `UNEXPLAINED_EXTERNAL_ADVANCE`
- `LOCAL_AUTHORITY_DRIFT`
- `ACTIVATION_FENCE_MISMATCH`
- `EPOCH_EXHAUSTED`

None implicitly authorizes another command. Re-verification/planning is required after every non-terminal attempt.

## RED-first matrix

Before production implementation execute at least:

1. NOOP performs zero writes/calls;
2. exact retry from predecessor with no provider result;
3. retry uses original request id exactly;
4. retry never allocates a second position;
5. UNKNOWN-after-commit reconciles exact request;
6. UNKNOWN with no result leaves local PREPARED;
7. exact result appears between plan and retry -> stale, no increment;
8. provider moves ahead between plan and retry -> fail closed;
9. provider generation changes -> fail closed;
10. authority descriptor changes -> fail closed;
11. command 2 exact reconcile then confirmation/commit;
12. command 2 wrong position -> fail closed;
13. command 2 wrong request id -> fail closed;
14. command 2 changed receipt binding -> fail closed;
15. crash after provider commit before SQL begin -> recoverable by command 2;
16. crash after LAB-080 confirmation before provenance commit -> command 3 only;
17. command 3 performs no provider mutation;
18. command 3 receipt reauthentication failure -> no local write;
19. stale `preconditions_digest` -> no mutation;
20. parent head advances before SQL commit -> rollback/no mutation;
21. event bytes change before SQL commit -> rollback;
22. successor link bytes change before SQL commit -> rollback;
23. LAB-080 row changes before SQL commit -> rollback;
24. two executors same plan -> one commit, one stale;
25. sibling transition appears -> no recovery;
26. historical PREPARED row -> no recovery;
27. second PREPARED row -> no recovery;
28. active unrelated activation fence remains unchanged;
29. unresolved activation fence survives UNKNOWN;
30. stale plan cannot release activation fence;
31. local SQL failure after external commit leaves exact request reconcilable;
32. local SQL failure does not issue compensating provider mutation;
33. no command advances component watermark;
34. no command creates missing schema/history rows;
35. no command re-bootstraps deleted history;
36. no command upgrades authority/provider generation implicitly;
37. epoch exhaustion rejects before mutation;
38. malformed canonical plan field fails before provider call;
39. bool/REAL/TEXT numeric confusion fails before provider call;
40. restricted LAB-093 worker cannot invoke raw executor/provider capability.

## Audit conclusions

- The executor is a narrow completion machine, not a repair engine.
- The exact deterministic LAB-080 request id is the sole external mutation idempotency key for V1 recovery.
- External mutation occurs at most once conceptually and is retried only under the same request identity.
- SQLite confirmation/provenance-head advancement is guarded by fresh external evidence plus an in-transaction recheck of the planner preconditions.
- Activation fences are authority state and survive uncertainty; generic recovery never releases them.
- Every executor attempt is followed by a fresh full startup verification. Successful execution does not directly open the runtime.

## Verdict

`RECOVERY_EXECUTOR_COMMAND_GRAMMAR_IDEMPOTENCY_V1_FROZEN`

Production implementation remains blocked on exact executable RED/GREEN capability. LAB-086 exact machine composition remains priority #1.