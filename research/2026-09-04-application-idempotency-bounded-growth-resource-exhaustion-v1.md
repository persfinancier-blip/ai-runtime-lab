# LAB-093 application-idempotency bounded-growth + resource-exhaustion contract V1

Date: 2026-09-04
Status: FROZEN DESIGN / RED-FIRST; production implementation waits for executable branch gates.

## Objective

Freeze how the LAB-093 application-idempotency registry behaves under finite storage and adversarial/high-volume key creation without weakening the previously frozen permanent-consumed-key property.

Required property:

> Resource pressure may reject new work, retire result payload bytes under authenticated retention policy, or require an authenticated capacity-policy change. It must never delete, recycle, silently forget, or reinterpret a historical application key in order to admit another effect.

This composes with:
- `WORKER_EFFECT_COMPLETION_RESULT_DELIVERY_APPLICATION_IDEMPOTENCY_V1_FROZEN`;
- `APPLICATION_IDEMPOTENCY_REGISTRY_INSTALLATION_PROVENANCE_RETENTION_AUTHORITY_V1_FROZEN`;
- the durable worker request/effect registry;
- shared canonical V1 encoding and the global parent-linked provenance chain;
- LAB-080 exact request identity;
- LAB-087 sole-writer ownership;
- LAB-091 operation-scoped SQL authorization;
- startup verification/recovery and worker-session revocation/re-entry.

V1 explicitly prefers fail-closed availability loss to an exactly-once/idempotency safety violation.

## 1. Fundamental boundedness statement

Permanent non-reuse of arbitrary application keys implies monotonic historical evidence. No finite fixed-capacity implementation can admit an unbounded number of previously unseen keys forever while retaining exact membership evidence for every consumed key.

Therefore V1 does **not** promise infinite admission under fixed storage. It freezes a bounded-admission contract:

1. every new application-key binding consumes a durable admission unit before the effect can become `BOUND`;
2. admission is limited by authenticated global and scope-specific budgets;
3. when a required budget is exhausted, the broker rejects the new key before any durable effect preparation/provider call;
4. cleanup may reduce payload bytes but does not refund consumed-key admission units;
5. increasing capacity requires an authenticated policy transition; it is never inferred from free disk, operator deletion, VACUUM, restart, or missing rows.

This converts resource exhaustion from a safety ambiguity into an explicit availability state.

## 2. Capacity policy V1

Freeze canonical policy:

```
ApplicationIdempotencyCapacityPolicyV1 {
  policy_id: UTF8_NONEMPTY,
  policy_version: INTEGER_NONNEGATIVE,
  global_key_limit: INTEGER_POSITIVE,
  per_principal_key_limit: INTEGER_POSITIVE,
  per_namespace_key_limit: INTEGER_POSITIVE,
  max_live_bound_per_principal: INTEGER_POSITIVE,
  max_live_bound_per_namespace: INTEGER_POSITIVE,
  max_result_bytes_per_principal: INTEGER_NONNEGATIVE,
  max_result_bytes_per_namespace: INTEGER_NONNEGATIVE,
  max_single_result_bytes: INTEGER_NONNEGATIVE,
  accounting_version: INTEGER_POSITIVE,
  policy_document_digest: BLOB32,
}
```

Canonical encoding uses the shared domain-separated V1 encoder.

`capacity_policy_digest = SHA256(domain || canonical_capacity_policy)`.

All fields are construction-bound/authenticated authority inputs. Environment variables, CLI flags, caller-supplied request metadata or filesystem free-space observations cannot silently override them.

## 3. What counts against which budget

### Permanent key-count budgets

Every successfully durable application row that ever reaches initial `BOUND` consumes exactly one permanent key-count unit in:
- the global counter;
- its `principal_digest` counter;
- its canonical `namespace` counter.

The unit remains consumed after `COMMITTED` and after `TOMBSTONED`.

It is not refunded by:
- result delivery;
- result payload retirement;
- tombstoning;
- deletion attempts;
- policy upgrade;
- restart;
- namespace becoming inactive;
- worker-session revocation.

### Live unresolved budgets

Rows in `BOUND` consume additional live-unresolved units per principal and namespace. These units are released only when the same authenticated operation reaches terminal `COMMITTED` or `TOMBSTONED` state through the existing exact recovery/commit protocol.

`UNKNOWN`, crash, timeout, session loss, cancellation or caller disappearance do not release a live unit.

### Result-byte budgets

Only retained result payload bytes count against result-byte budgets. Authenticated tombstoning may retire result payload bytes and therefore reduce result-byte usage, but never permanent key-count usage.

Canonical byte accounting is exact stored payload length, not caller-declared size and not compressed-on-wire size. Any storage compression is an implementation detail and does not change the logical quota metric in V1.

## 4. Durable accounting authority

Quota admission MUST NOT depend only on mutable cached counters.

Freeze authority model:
- authoritative consumed-key membership remains the authenticated application registry + global provenance continuity;
- authoritative `BOUND` state remains exact registry state joined to worker request/effect/recovery evidence;
- result-byte usage is recomputable from authenticated committed/tombstoned registry/result state;
- optional aggregate counters are caches/accelerators only unless each update is independently bound into the same authorized state transition and startup can recompute/verify them.

A cache mismatch is `CAPACITY_ACCOUNTING_MISMATCH` and fails closed before admitting new work. Startup may repair a cache only through an explicitly frozen deterministic repair path that derives solely from already-authenticated rows and performs no provider/effect action. V1 otherwise permits omitting caches entirely.

## 5. Admission boundary: before BOUND

For a previously unseen application key, capacity admission occurs inside the same final broker-authorized `BEGIN IMMEDIATE` transaction that would create the durable worker request/effect/application `BOUND` state.

Required sequence:
1. clean startup/session/effect preconditions already hold;
2. canonical key and operation digests are frozen;
3. broker checks whether key already exists;
4. if it exists, ordinary exact duplicate/conflict semantics apply and **no new quota unit is consumed**;
5. if it is new, broker recomputes/verifies all applicable capacity usage under the same write serialization boundary;
6. broker checks global, principal, namespace, live-unresolved and anticipated result-envelope constraints that are knowable pre-effect;
7. if any hard limit would be exceeded, abort before inserting `BOUND`, before LAB-080 intent allocation, before provenance PREPARED creation and before provider call;
8. only an admitted new key may create the atomic durable `BOUND` request/effect/application association.

Quota is therefore an admission precondition, never post-effect cleanup.

## 6. Duplicate convergence at capacity

Capacity exhaustion does not break idempotent lookup/retry of an already consumed key.

At any quota limit:
- same key + same canonical operation may discover `BOUND`, `COMMITTED` or `TOMBSTONED` state according to normal authorization;
- same live request may continue broker-owned exact recovery;
- committed result may be redelivered if current disclosure authorization permits;
- same key + different operation remains `APPLICATION_KEY_CONFLICT`;
- a new unseen key is rejected.

No additional permanent admission unit is charged for an exact retry of an existing key.

This distinction prevents capacity exhaustion from turning retry into duplicate execution.

## 7. Hard exhaustion semantics

Freeze statuses:
- `APPLICATION_CAPACITY_GLOBAL_EXHAUSTED`
- `APPLICATION_CAPACITY_PRINCIPAL_EXHAUSTED`
- `APPLICATION_CAPACITY_NAMESPACE_EXHAUSTED`
- `APPLICATION_LIVE_BOUND_PRINCIPAL_EXHAUSTED`
- `APPLICATION_LIVE_BOUND_NAMESPACE_EXHAUSTED`
- `APPLICATION_RESULT_BYTES_PRINCIPAL_EXHAUSTED`
- `APPLICATION_RESULT_BYTES_NAMESPACE_EXHAUSTED`
- `APPLICATION_RESULT_TOO_LARGE`
- `CAPACITY_ACCOUNTING_MISMATCH`
- `CAPACITY_POLICY_MISMATCH`

These statuses are non-authorizing. They do not permit eviction, tombstoning, provider calls, alternate request ids, namespace fallback or key rewriting.

When a key-count hard limit is reached, the correct V1 behavior is to stop admitting unseen keys in that scope until an authenticated capacity policy increases the relevant limit or a separate future protocol introduces stronger compact membership evidence. Ordinary cleanup cannot make room.

## 8. Result-size uncertainty and commit behavior

An effect may produce a result whose exact payload size is not knowable before provider execution.

V1 freezes two safe strategies; an implementation must choose one and bind the choice in `accounting_version`/policy:

### Strategy A — declared bounded result class
Before effect execution, operation policy provides an authenticated maximum result size. Admission reserves that maximum against result-byte capacity. Commit requires actual bytes `<= reserved_max`; unused reservation is released at terminal commit.

### Strategy B — result payload is not required for effect safety
The broker commits the externally meaningful effect/result digest/provenance first according to the existing exactly-once protocol, but if payload retention would exceed quota it stores only the authenticated terminal digest/status and returns `COMMITTED_RESULT_NOT_RETAINED_CAPACITY` rather than rolling back or repeating the already-committed effect. The application key remains permanently consumed.

V1 forbids treating a post-effect oversized result as permission to undo/reissue the effect. A future implementation must explicitly select and test A or B; it may not improvise between them per request.

## 9. Tombstone interaction

Authenticated `COMMITTED -> TOMBSTONED` may:
- retire result payload bytes;
- lower result-byte usage;
- preserve permanent key-count usage exactly;
- preserve operation/result digests in authenticated provenance;
- preserve lookup status `COMMITTED_RESULT_RETIRED`.

Tombstoning MUST NOT:
- decrement global/principal/namespace consumed-key counts;
- turn a namespace key into `MISS`;
- make the raw key reusable;
- be auto-triggered solely because capacity is low;
- bypass retention authority or minimum-age policy.

Resource pressure is not retention authority.

## 10. Namespace lifecycle

A namespace may be administratively closed to new admission, but closure does not delete history.

Freeze optional policy event:

`APPLICATION_IDEMPOTENCY_NAMESPACE_STATE_V1`

States:
- `OPEN`: new keys allowed subject to quotas;
- `SEALED`: no new keys; historical lookup/recovery remains available under authorization.

No `RESET` or `REUSE` state exists in V1.

Creating a new namespace is a new application scope, not reuse of the old namespace. Its identity must be canonical and policy-authorized. An implementation must not silently append an epoch suffix when the old namespace is exhausted; caller/policy must explicitly select the new authenticated namespace identity.

Historical sealed namespaces remain part of startup/provenance verification.

## 11. Capacity policy updates

Freeze authenticated provenance event:

`APPLICATION_IDEMPOTENCY_CAPACITY_POLICY_UPDATE_V1`

Canonical body binds:
- old policy digest/version;
- new policy digest/version;
- capacity-authority identity digest;
- parent provenance head/epoch;
- effective epoch;
- reason/audit digest if policy requires one.

Rules:
- policy version strictly increases;
- update is externally anchored through the existing provenance/LAB-080 protocol;
- a policy update cannot retroactively unconsume keys;
- lowering a limit below current usage is allowed only as a no-new-admission state; it does not delete or invalidate historical rows;
- an update cannot make tombstoned keys reusable;
- historical admission remains verified against the policy active at the time if that policy digest is recorded in the relevant provenance/event envelope.

Capacity authority is distinct from ordinary worker effect authority and from retention authority unless an explicit higher-level policy says the same principal holds both.

## 12. Restart accounting

Startup verification before worker delegation recomputes or re-authenticates:
- total consumed application keys;
- consumed keys per principal;
- consumed keys per namespace;
- live `BOUND` counts;
- retained result bytes;
- current capacity policy/version and its provenance continuity.

Required properties:
- restart never resets usage to zero;
- missing aggregate cache cannot make capacity larger;
- deleted application/tombstone/history rows fail existing provenance verification rather than reducing usage;
- a crash during new-key admission either leaves no `BOUND` row/no consumed unit or leaves the exact durable `BOUND` operation consuming exactly one unit;
- a crash during terminal commit cannot double-release live-bound usage;
- a crash during tombstoning cannot refund permanent key capacity.

If exact usage cannot be authenticated, startup yields `CAPACITY_ACCOUNTING_MISMATCH`/corruption and does not delegate workers.

## 13. Concurrency

Two brokers/requests racing for the last capacity slot are serialized by the broker sole-writer + `BEGIN IMMEDIATE` boundary.

For two different unseen keys with one remaining slot:
- at most one may commit `BOUND`;
- the loser observes updated usage and receives capacity exhausted before effect preparation/provider call.

For the same unseen key and same operation:
- one commits the binding;
- the other converges to the existing binding and consumes no second unit.

For the same key with different operations:
- one binding may win;
- the other receives `APPLICATION_KEY_CONFLICT`, never a capacity-based alternate execution.

## 14. Abuse resistance and fairness boundary

Per-principal and per-namespace quotas exist to prevent one authorized principal/namespace from consuming the entire global idempotency key space accidentally or maliciously.

V1 does not attempt scheduler fairness, billing, dynamic rate limiting or commercial metering. Those are separate policy layers. Capacity policy only constrains durable exactly-once history growth.

A principal cannot evade quota by:
- creating new worker sessions;
- changing worker request ids;
- retrying after restart;
- tombstoning old results;
- changing retention class after binding;
- using multiple operation classes under the same principal digest;
- case/Unicode variants that canonicalize to a different namespace only if policy explicitly treats them as distinct canonical namespaces.

Principal identity itself must come from the already-authenticated caller/session authority, not caller-declared text.

## 15. Storage pressure and SQLite failure

Physical storage errors (`SQLITE_FULL`, I/O error, ENOSPC, quota at filesystem layer) are not equivalent to logical application capacity.

Rules:
- an error before local PREPARED/BOUND commit leaves no claimed effect and is retryable only through a fresh authorized cycle;
- an error after durable PREPARED/BOUND but before external effect remains broker recovery-owned; do not delete the row to regain space;
- an error after provider commit/UNKNOWN requires exact request recovery; do not issue a second effect;
- if terminal metadata cannot be durably committed because storage is physically exhausted, runtime fails closed and preserves the external request identity/evidence available; operator capacity remediation may be required, but historical keys are not sacrificed;
- VACUUM/compaction may reclaim unused pages/payload space but cannot alter logical consumed-key accounting.

Logical quota policy should be configured with operational headroom so critical recovery metadata can still commit after normal admission is stopped. V1 recommends, but does not hard-code, a separately reserved broker-recovery metadata budget.

## 16. Reserved recovery headroom

Freeze optional but recommended policy field for implementation extension:

`recovery_metadata_reserve_bytes`.

Normal unseen-key admission must stop before consuming this reserved capacity. Only broker-owned recovery/terminalization/provenance metadata may use it.

This reserve does not authorize a new application effect. It exists so already-prepared operations can reach a safe terminal state under storage pressure.

If an implementation cannot enforce a reliable physical-byte reserve, it must conservatively stop normal admission earlier and document the operational requirement; it must not claim the reserve works without executable proof.

## 17. Audit observability

A capacity rejection should expose non-secret audit fields sufficient to explain the decision:
- current capacity policy id/version/digest;
- exhausted scope class (global/principal/namespace/live/result-bytes);
- current usage and configured limit when policy permits disclosure;
- whether the presented application key already existed;
- current provenance head digest/epoch used for the decision.

It must not expose other principals' raw keys, canonical application-key bytes, result bytes or private authority material.

## 18. RED-first matrix

Minimum executable matrix before production implementation:

1. first unseen key below all limits becomes BOUND and consumes exactly one global/principal/namespace unit;
2. same key + same operation retry consumes no second unit;
3. same key + different operation is conflict, not second admission;
4. second worker session retry of same committed key consumes no new unit;
5. restart preserves consumed-key counts;
6. COMMITTED does not refund permanent key count;
7. TOMBSTONED does not refund permanent key count;
8. result payload retirement lowers only result-byte usage;
9. global key limit rejects next unseen key before BOUND insert;
10. principal key limit rejects next unseen key for that principal before BOUND;
11. namespace key limit rejects next unseen key in that namespace before BOUND;
12. another principal can still admit when first principal is exhausted and global capacity remains;
13. another namespace can still admit when first namespace is exhausted and global capacity remains;
14. global exhaustion blocks all unseen keys regardless of local headroom;
15. capacity rejection allocates no LAB-080 request id;
16. capacity rejection creates no provenance PREPARED transition;
17. capacity rejection performs no provider call;
18. capacity rejection creates no worker effect binding;
19. exact lookup of existing COMMITTED key still works at global exhaustion;
20. exact lookup of existing TOMBSTONED key still returns retired status at exhaustion;
21. BOUND existing key returns pending reconciliation at exhaustion rather than duplicate execution;
22. live-bound principal limit blocks another unresolved effect for that principal;
23. terminalizing one BOUND operation releases exactly one live unit;
24. UNKNOWN retains its live unit;
25. cancellation/session revocation retains live unit until broker terminalization;
26. crash after BOUND commit retains live unit on restart;
27. crash before BOUND commit consumes no unit;
28. two different unseen keys racing for last slot yield exactly one BOUND winner;
29. two same-key/same-operation racers for last slot converge to one BOUND row/one unit;
30. same-key/different-operation race yields one binding + one conflict;
31. deleted application row does not reduce authenticated usage; startup fails closed;
32. deleted tombstone row/evidence does not free capacity; startup fails closed;
33. forged aggregate counter below actual usage is detected;
34. forged aggregate counter above actual usage is detected or ignored/recomputed according to implementation contract;
35. missing cache cannot be interpreted as zero usage;
36. policy digest mismatch fails closed before admission;
37. stale policy version cannot admit under an older larger limit;
38. authenticated capacity increase admits new keys only after policy transition commits;
39. crash/UNKNOWN during policy update keeps old policy active until exact recovery completes;
40. lowering limit below existing usage preserves history and blocks new admission;
41. policy update never rewrites historical application keys;
42. SEALED namespace rejects unseen key but permits authorized historical lookup;
43. restart preserves SEALED state;
44. creating a new namespace requires explicit authenticated identity/policy, not automatic suffixing;
45. session churn cannot evade principal quota;
46. changing worker request id cannot evade application-key count semantics;
47. tombstoning cannot evade key quota;
48. retention policy cannot convert tombstone to reusable capacity;
49. result exceeding `max_single_result_bytes` follows the policy-selected safe strategy without effect replay;
50. result-byte principal limit follows selected reservation/non-retention strategy without key reuse;
51. result-byte namespace limit likewise fails safe;
52. physical `SQLITE_FULL` before BOUND leaves no effect;
53. physical storage failure after BOUND transfers/remains broker recovery-owned and never deletes the key;
54. physical storage failure after provider UNKNOWN never mints a new request id;
55. VACUUM/compaction does not change logical consumed-key counts;
56. normal admission cannot consume configured recovery metadata reserve;
57. recovery terminalization may use reserve only for the exact already-prepared operation;
58. recovery reserve cannot authorize an unseen application key;
59. audit output does not reveal other principals' raw key/result data;
60. worker façade has no API to modify quota counters/policy or force eviction.

## 19. Production implementation gate

Do not implement production quota/capacity code until exact executable source is available and the matrix above is first expressed as RED tests at the same abstraction level as the frozen LAB-093 registry/effect implementation.

Before integration, execute and retain evidence for:
- application registry install/migration/tombstone tests;
- worker request/effect crash/recovery tests;
- session revocation/re-entry and effect-boundary tests;
- LAB-080 exact request/reconcile regressions;
- LAB-087 sole-writer composition;
- LAB-091 SQL authorization;
- startup verifier/evidence/recovery/broker finite-state gates.

No test result may be claimed until actually executed on exact source bytes.

## Decision

`APPLICATION_IDEMPOTENCY_BOUNDED_GROWTH_RESOURCE_EXHAUSTION_V1_FROZEN`.

V1 chooses monotonic safety over unbounded availability. New application keys consume permanent authenticated capacity; quotas are checked before `BOUND`; exhaustion rejects unseen work before any external effect; retries of existing keys continue to converge; tombstones reclaim result bytes but never key slots; capacity changes are authenticated provenance events; restart reconstructs usage rather than resetting it; and physical storage pressure never authorizes deletion/reuse of historical exactly-once evidence.
