# LAB-093 worker effect completion/result delivery + cross-session application idempotency V1

Date: 2026-09-04
Status: FROZEN DESIGN / RED-FIRST; production implementation waits for executable branch gates.

## Objective

Freeze the broker-owned bridge between a durable COMMITTED worker effect and safe result discovery/redelivery after worker-session loss or broker restart, without reviving old worker authority and without inferring semantic duplicates.

Required property:

> Session-scoped worker request idempotency and cross-session application idempotency are different authorities. A historical COMMITTED effect may be rediscovered by a new, freshly authorized session only through an explicit canonical application idempotency key that was bound before the effect. Lookup is presentation-only: it may reveal the already committed immutable result, but it cannot reopen, replay, rebind, or repeat the effect.

This composes with the frozen LAB-093 worker-session revocation/re-entry protocol, canonical worker request/effect envelope, durable worker request/effect registry, LAB-080 exact external request identity, provenance append/recovery, and the broker startup verification state machine.

It MUST NOT make old `session_id`/`worker_request_id` resumable, derive idempotency from payload similarity, mint a second provider request namespace, or allow a newly chosen key to claim a historical effect retroactively.

## 1. Two idempotency scopes

### Session-scoped request idempotency

Key: `(session_id, worker_request_id)`.

Purpose: converge retries while the same worker session is live and authorized.

Rules:
- same pair + same canonical worker request digest converges;
- same pair + different digest rejects as `REQUEST_ID_REBOUND`;
- after broker restart, the historical pair remains evidence only and cannot authorize a call.

### Application-scoped idempotency

Optional key supplied by the application before effect preparation.

Purpose: let a later freshly authorized session discover the same durable operation/result across worker-session loss or restart.

Rules:
- absence means no cross-session convergence guarantee;
- presence must be canonical and bound before the effect;
- same application key may name only one canonical operation identity within its declared scope;
- same key + different canonical operation digest is a conflict, never "latest wins";
- application keys never authorize provider/SQLite mutation by themselves.

## 2. Canonical application key

Freeze a typed structure:

```
ApplicationIdempotencyV1 {
  namespace: UTF8_NONEMPTY,
  key: BYTES_NONEMPTY,
  principal_digest: BLOB32,
  operation_class: UTF8_NONEMPTY,
  retention_class: UTF8_NONEMPTY,
}
```

Canonical encoding uses the shared domain-separated canonical V1 encoder.

`application_key_digest = SHA256(domain || canonical_application_key)`.

The canonical worker envelope contains either:
- `application_key = NONE`; or
- exact `canonical_application_key` + `application_key_digest`.

No normalization beyond the canonical encoder is permitted. Case folding, whitespace trimming, Unicode compatibility normalization, JSON map reordering outside canonical rules, numeric coercion, or semantic payload hashing are forbidden.

## 3. Canonical operation identity

Cross-session equality is not defined by the raw application key alone.

Freeze:

`application_operation_digest = SHA256(domain || application_key_digest || method_id || canonical_effect_digest || capability_profile_digest || operation_policy_digest)`

where `operation_policy_digest` binds every policy field that can change the externally meaningful operation semantics.

For an ANCHORED effect, the digest is bound before provider execution and before durable PREPARED ownership transfer. It does not include session identity.

For LOCAL_SQL effects, it similarly binds the exact canonical local effect.

A retry under a new session with the same application key must independently reconstruct the same `application_operation_digest`; otherwise it is `APPLICATION_KEY_CONFLICT`.

## 4. Durable application registry

V1 adds one broker-private STRICT table:

```sql
CREATE TABLE worker_application_idempotency_v1(
  application_key_digest BLOB PRIMARY KEY,
  canonical_application_key BLOB NOT NULL,
  application_operation_digest BLOB NOT NULL,
  worker_request_digest BLOB NOT NULL UNIQUE,
  effect_binding_digest BLOB NOT NULL UNIQUE,
  state TEXT NOT NULL CHECK(state IN('BOUND','COMMITTED','TOMBSTONED')),
  result_digest BLOB,
  tombstone_digest BLOB,
  retention_class TEXT NOT NULL,
  CHECK(length(application_key_digest)=32),
  CHECK(length(application_operation_digest)=32),
  CHECK(length(worker_request_digest)=32),
  CHECK(length(effect_binding_digest)=32),
  CHECK(result_digest IS NULL OR length(result_digest)=32),
  CHECK(tombstone_digest IS NULL OR length(tombstone_digest)=32),
  CHECK(
    (state='BOUND' AND result_digest IS NULL AND tombstone_digest IS NULL)
    OR
    (state='COMMITTED' AND result_digest IS NOT NULL AND tombstone_digest IS NULL)
    OR
    (state='TOMBSTONED' AND result_digest IS NULL AND tombstone_digest IS NOT NULL)
  )
) STRICT;
```

The row is created atomically with the durable worker request/effect binding before any provider call.

`worker_request_digest` and `effect_binding_digest` point to the one already-frozen durable worker operation. They do not create another effect identity.

The implementation must enforce one-to-one joins between this table and `worker_effect_requests_v1` / `worker_effect_bindings_v1` when an application key is present.

## 5. BOUND ownership semantics

`BOUND` means:
- the application key has been claimed by one exact canonical operation;
- the associated effect may be PREPARED/UNKNOWN/recovery-owned;
- no new session may execute a second effect for that key;
- callers may receive only `PENDING_RECONCILIATION` or equivalent non-authorizing status until the original operation reaches a terminal state.

A new session presenting the same key + same operation digest attaches to the historical operation for observation only. It does not obtain ownership of the provider request, provenance transition, LAB-080 intent, or old worker request id.

A new session presenting the same key + different operation digest fails closed before effect preparation.

## 6. COMMITTED result delivery

When the underlying durable worker effect reaches COMMITTED and `worker_effect_results_v1` is durably inserted, the broker atomically/monotonically updates the application row:

`BOUND -> COMMITTED`, binding exact `result_digest`.

A result lookup under a new session is allowed only after:
1. full broker startup/verification is clean;
2. the new session is freshly issued under current provider generation, activation authority, provenance head and least-capability profile;
3. caller presents the exact canonical application key;
4. broker reconstructs the requested `application_operation_digest` from the new request and verifies exact equality with the durable row;
5. durable request/binding/result/application joins re-authenticate successfully;
6. result digest and canonical result bytes verify.

The return path is presentation-only. It MUST NOT:
- execute provider calls;
- allocate a LAB-080 request id;
- prepare a new provenance transition;
- reopen worker recovery ownership;
- mutate the historical worker request/session identity;
- change result bytes.

## 7. Lost response semantics

If the effect COMMITTED but the original worker/client never received the response:
- same live session/request retry receives the immutable committed result;
- after restart, old session identity is rejected as authority;
- a fresh session may rediscover the result only if the original operation had a pre-bound application key and the new canonical operation digest matches exactly;
- without a pre-bound application key, the broker may expose administrative/audit discovery through a separate privileged diagnostic surface, but normal application retry cannot infer that a new request is the old operation.

No semantic duplicate detection by payload similarity is permitted.

## 8. UNKNOWN and recovery interaction

If an application key is BOUND while the operation is PREPARED/UNKNOWN:
- any session, old or new, receives `PENDING_RECONCILIATION` for the same exact operation identity;
- only broker-owned recovery may issue/reconcile the original LAB-080 request id;
- no second effect may be prepared under that application key;
- `APPLICATION_KEY_CONFLICT` remains distinguishable from `PENDING_RECONCILIATION`.

After recovery commits, ordinary verified lookup may expose the immutable result.

## 9. Retention and tombstones

Application idempotency cannot safely support silent row deletion because deletion would permit the same key to execute a second effect later.

V1 therefore freezes explicit retention classes but fail-closed semantics:

- `PERMANENT`: keep canonical key binding and result indefinitely.
- `TOMBSTONE_AFTER_RESULT_RETENTION`: result payload may be retired under a separately authenticated retention action, but the key binding becomes `TOMBSTONED`; the key can never be reused for another operation.

A tombstone contains a canonical authenticated digest binding:
- application key digest;
- application operation digest;
- original worker/effect digests;
- original committed result digest;
- retention policy/action identity.

`TOMBSTONED` lookup returns `COMMITTED_RESULT_RETIRED` (or equivalent) and never re-executes the effect.

V1 does not support "expiry means key reusable". Reusable TTL idempotency is deferred because it weakens exactly-once history and requires a separate epoch/namespace contract.

## 10. Principal and scope binding

An application key is not globally bearer-authority.

`principal_digest` and `namespace` are part of the canonical key. Lookup must re-authorize the current caller/session against the application namespace before returning even a committed result.

A caller knowing another principal's key cannot retrieve its result unless current policy explicitly authorizes that principal/namespace.

Authorization drift after commit may make an old result undiscoverable to a caller that has lost permission; historical ownership does not bypass current disclosure policy.

## 11. Crash consistency

### Crash before application/request/effect BOUND commit
No provider call has occurred. No durable claim exists. A future request may bind the key.

### Crash after BOUND commit, before provider call
The key is already occupied by the exact broker-recovery-owned effect. Retry attaches; no duplicate effect.

### Crash after provider commit, before local confirmation
The key stays BOUND. Exact LAB-080 request reconciliation completes the original effect.

### Crash after worker effect COMMITTED, before application row update
Startup verifier detects `worker_effect_results_v1=COMMITTED` with application row still BOUND and yields one deterministic broker-local completion action: verify exact joins/result and advance only that application row to COMMITTED. No provider call is permitted.

### Crash after application COMMITTED, before response
Any authorized exact lookup returns the immutable result.

## 12. Startup verification additions

Before delegation, startup must fail closed on:
- application row without matching worker request/effect binding;
- worker envelope declaring application key but no application row after durable PREPARED;
- canonical key digest mismatch;
- application operation digest mismatch;
- same application key claimed by multiple worker/effect rows;
- BOUND row whose operation is absent or terminally inconsistent;
- COMMITTED row whose worker effect/result is not COMMITTED or whose result digest differs;
- TOMBSTONED row missing authenticated retention evidence;
- deleted application row for a historical effect whose envelope proves a key was bound;
- coherent local column rewrites that fail canonical/provenance bindings.

Do not repair by newest timestamp, MAX(rowid), MAX(epoch), payload similarity, or a new session replay.

## 13. Authorization boundary for result lookup

Result lookup is broker-mediated and least-capability. A worker façade may request:

`lookup_application_result(canonical_application_key, expected_application_operation_digest)`

but the broker performs all durable verification and current authorization checks.

The worker never receives:
- raw SQLite handles;
- provenance mutation capability;
- LAB-080 provider request authority;
- activation provider handles;
- ability to alter/tombstone idempotency rows.

## 14. Conflict semantics

Freeze externally distinguishable classes:

- `MISS`: no durable key binding exists and a new effect may be prepared if current authorization passes.
- `PENDING_RECONCILIATION`: exact key + exact operation exists but is not terminal.
- `COMMITTED_RESULT`: exact key + exact operation has immutable result and current disclosure policy allows it.
- `COMMITTED_RESULT_RETIRED`: exact key + exact operation committed but payload was tombstoned under authenticated retention.
- `APPLICATION_KEY_CONFLICT`: key exists but requested operation digest differs.
- `UNAUTHORIZED`: current principal/session may not inspect or use this namespace/key.
- `CORRUPT_FAIL_CLOSED`: durable joins/canonical/authenticated history fail verification.

None of these classes authorizes a provider mutation by itself.

## 15. RED-first matrix

Minimum executable matrix before production implementation:

1. no application key preserves session-only behavior;
2. application key is bound atomically before provider call;
3. same live session/request + same digest converges;
4. new session + same key + same operation attaches without re-execution;
5. new session + same key + different payload/effect yields conflict;
6. same raw key under different namespace is distinct;
7. same namespace/key under different principal is distinct;
8. canonical key one-byte mutation is distinct/conflict as defined, never normalized silently;
9. Unicode/case/whitespace normalization is not inferred;
10. TEXT/REAL/bool type confusion rejects;
11. crash before BOUND commit permits later legitimate bind and proves no provider call occurred;
12. crash after BOUND/before provider call blocks duplicate effect;
13. crash after provider commit/before local confirmation remains one operation;
14. UNKNOWN uses original LAB-080 request id only;
15. new session while UNKNOWN receives pending, not effect authority;
16. recovery commit changes same application row to COMMITTED;
17. crash after worker-result COMMITTED/before application COMMITTED yields local-only completion;
18. local-only completion performs no provider call;
19. committed response loss redelivers immutable result;
20. result redelivery under new session performs no effect preparation;
21. old session after restart cannot lookup by session identity alone;
22. old session token + valid application key still fails session authorization; a new session is required;
23. new authorized session + valid application key can lookup committed result;
24. unauthorized principal cannot retrieve another principal's result;
25. authorization revoked after commit prevents disclosure but preserves durable binding;
26. deleted application row for keyed historical effect fails startup;
27. application row without worker request fails startup;
28. application row without effect binding fails startup;
29. application row points to wrong worker request fails startup;
30. application row points to wrong effect binding fails startup;
31. application operation digest rewrite fails startup;
32. application canonical key bytes rewrite fails startup;
33. COMMITTED application row with missing worker result fails startup;
34. COMMITTED application row with mismatched result digest fails startup;
35. BOUND application row pointing to unrelated COMMITTED effect fails startup;
36. two worker requests claiming same application key cannot both prepare;
37. concurrent same key/same operation race converges to one effect;
38. concurrent same key/different operation race yields one winner + conflict, never two effects;
39. retry after COMMITTED returns exact same canonical result bytes;
40. result bytes cannot be rewritten while retaining old digest;
41. PERMANENT key cannot be deleted/reused by normal operation;
42. authenticated tombstone retires result but preserves non-reusability;
43. tombstoned key lookup returns retired, not MISS;
44. tombstoned key cannot prepare a new effect;
45. deleting tombstone evidence fails startup;
46. stale pre-restart lookup snapshot cannot authorize result delivery after authority drift;
47. final lookup re-checks current session/principal disclosure authorization;
48. application key does not become a LAB-080/provider request id;
49. broker recovery ownership remains unchanged by cross-session lookup;
50. final audit proves no code path infers duplicate effects from payload similarity or revives historical session authority.

## 16. Decision

Freeze as:

`WORKER_EFFECT_COMPLETION_RESULT_DELIVERY_APPLICATION_IDEMPOTENCY_V1_FROZEN`.

Implementation order when exact executable RED/GREEN becomes available:
1. canonical application key + operation digest value types;
2. durable application registry and exact one-to-one guards;
3. RED tests for conflict/race/crash/UNKNOWN/restart;
4. broker-local BOUND->COMMITTED completion path;
5. fresh-session presentation-only lookup path;
6. retention/tombstone tests and guards;
7. LAB-091 writer authorization integration;
8. full LAB-087/LAB-080/provenance/LAB-093 downstream audit.

No production code is claimed or changed by this design freeze.