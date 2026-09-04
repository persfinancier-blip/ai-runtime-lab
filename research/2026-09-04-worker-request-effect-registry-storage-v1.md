# LAB-093 durable worker request/effect registry storage + crash-consistency V1

Date: 2026-09-04
Status: FROZEN DESIGN / RED-FIRST; production implementation waits for executable branch gates.

## Objective

Freeze the exact broker-owned durable storage contract that makes the already-frozen worker request-envelope/effect-boundary protocol restart-safe without reviving stale worker-session authority.

Required property:

> An accepted worker request may be ephemeral while it is compute-only, but the moment it can lead to a durable/external effect the broker must durably bind one canonical worker request digest to at most one effect identity, at most one provenance transition, and at most one LAB-080 intent/request identity. PREPARED/UNKNOWN survives crash only as broker-owned recovery work; old worker sessions never survive restart as authority.

This composes with LAB-087 sole-writer ownership, LAB-091 operation-scoped SQL authorization, LAB-080 deterministic external request identity, the frozen provenance append/storage/recovery contracts, and the LAB-093 session revocation/re-entry + request-envelope/effect-boundary protocols.

It MUST NOT create a second external request-id namespace, infer semantic duplicate payloads, or reconstruct effect identity from a post-crash worker message.

## 1. Storage split: session metadata is not durable authority

Worker sessions remain non-resumable across broker restart. Durable storage may retain historical `session_id` and `session_epoch` only as provenance/idempotency labels for requests that crossed the effect boundary. Those fields never make the old session callable again.

Ephemeral states `ADMITTED`, `COMPUTING`, and ordinary read-only results do not need durable rows. If the broker crashes before durable effect preparation, the request is lost and must be resubmitted under a new freshly verified session.

Durability begins at broker effect preparation.

## 2. Frozen tables

V1 adds three broker-private STRICT tables inside the same logical SQLite authority boundary as the supported ledger/provenance state.

### `worker_effect_requests_v1`

```sql
CREATE TABLE worker_effect_requests_v1(
  worker_request_digest BLOB PRIMARY KEY,
  session_id BLOB NOT NULL,
  session_epoch INTEGER NOT NULL,
  worker_request_id BLOB NOT NULL,
  method_id TEXT NOT NULL,
  canonical_envelope BLOB NOT NULL,
  payload_digest BLOB NOT NULL,
  capability_profile_digest BLOB NOT NULL,
  provider_generation_id TEXT NOT NULL,
  activation_authority_digest BLOB NOT NULL,
  admitted_provenance_head_digest BLOB NOT NULL,
  admitted_provenance_head_epoch INTEGER NOT NULL,
  state TEXT NOT NULL CHECK(state IN(
    'EFFECT_PREPARED',
    'PREPARED_RECOVERY_OWNED',
    'UNKNOWN_RECOVERY_OWNED',
    'COMMITTED'
  )),
  effect_binding_digest BLOB NOT NULL,
  CHECK(length(worker_request_digest)=32),
  CHECK(length(session_id)=16),
  CHECK(length(worker_request_id)=16),
  CHECK(length(payload_digest)=32),
  CHECK(length(capability_profile_digest)=32),
  CHECK(length(activation_authority_digest)=32),
  CHECK(length(admitted_provenance_head_digest)=32),
  CHECK(length(effect_binding_digest)=32),
  UNIQUE(session_id, worker_request_id)
) STRICT;
```

Rules:

- `worker_request_digest` is the domain-separated digest of the exact frozen canonical envelope.
- `(session_id,worker_request_id)` is globally unique in durable history; same pair + different digest is `REQUEST_ID_REBOUND` corruption/rejection.
- every field except the allowed monotonic `state` transition is immutable after insertion.
- durable insertion is allowed only after a fresh pre-effect authorization check while the originating session is still ACTIVE.
- the row is historical evidence/idempotency state after restart, never restored worker authority.

### `worker_effect_bindings_v1`

```sql
CREATE TABLE worker_effect_bindings_v1(
  effect_binding_digest BLOB PRIMARY KEY,
  worker_request_digest BLOB NOT NULL UNIQUE,
  effect_kind TEXT NOT NULL,
  canonical_effect BLOB NOT NULL,
  provenance_transition_id BLOB,
  anchor_intent_id TEXT,
  local_effect_id BLOB,
  CHECK(length(effect_binding_digest)=32),
  CHECK(provenance_transition_id IS NULL OR length(provenance_transition_id)=32),
  CHECK(local_effect_id IS NULL OR length(local_effect_id)=32),
  CHECK(
    (effect_kind='ANCHORED' AND provenance_transition_id IS NOT NULL AND anchor_intent_id IS NOT NULL AND local_effect_id IS NULL)
    OR
    (effect_kind='LOCAL_SQL' AND provenance_transition_id IS NULL AND anchor_intent_id IS NULL AND local_effect_id IS NOT NULL)
  )
) STRICT;
```

Rules:

- exactly one effect binding exists for a durable worker request.
- `canonical_effect` contains the exact frozen broker effect bytes/digest inputs, not a worker callback or mutable object reference.
- ANCHORED effects bind exactly one existing provenance transition and exactly one LAB-080 `anchor_intent_id`; LAB-080 remains authoritative for provider `request_id`, `position`, receipt and UNKNOWN reconciliation.
- LOCAL_SQL effects bind one canonical local effect identity consumed by LAB-091 one-shot authorization.
- no row may be rebound from one worker request to another, from one provenance transition to another, or from one LAB-080 intent to another.

### `worker_effect_results_v1`

```sql
CREATE TABLE worker_effect_results_v1(
  worker_request_digest BLOB PRIMARY KEY,
  terminal_kind TEXT NOT NULL CHECK(terminal_kind IN('COMMITTED')),
  result_digest BLOB NOT NULL,
  canonical_result BLOB NOT NULL,
  committed_provenance_head_digest BLOB NOT NULL,
  committed_provenance_head_epoch INTEGER NOT NULL,
  CHECK(length(result_digest)=32),
  CHECK(length(committed_provenance_head_digest)=32)
) STRICT;
```

Only effectful terminal success needs durable result storage in V1. Pre-effect cancellation/rejection/compute failure may remain ephemeral because they have no consistency obligation after restart.

A committed terminal result is immutable. Re-delivery reads this row; it never re-enters the effect path.

## 3. Effect-binding digest

Freeze:

`effect_binding_digest = SHA256(domain || worker_request_digest || effect_kind || canonical_effect_digest || optional provenance_transition_id || optional anchor_intent_id/local_effect_id)`

using the shared canonical V1 typed/domain-separated encoding.

The binding is computed before any provider call. Text/REAL/bool numeric coercion, unknown fields, reordered fields, malformed UTF-8 and trailing bytes fail closed.

## 4. Atomic PREPARED ownership transfer

The critical SQL boundary is one `BEGIN IMMEDIATE` transaction executed only after the fresh pre-effect authorization check and under LAB-087/LAB-091 writer ownership.

For an ANCHORED effect:

1. re-read current session/authority/provenance/evidence preconditions and require they still match the envelope;
2. freeze canonical effect bytes and `effect_binding_digest`;
3. allocate/reuse the exact provenance PREPARED transition under the frozen provenance Transaction-A protocol;
4. allocate/reuse exactly one LAB-080 intent through existing LAB-080 deterministic identity semantics;
5. insert `worker_effect_bindings_v1` referencing that exact transition/intent;
6. insert `worker_effect_requests_v1` directly in `PREPARED_RECOVERY_OWNED` (or insert `EFFECT_PREPARED` and transition to `PREPARED_RECOVERY_OWNED` in the same transaction; no externally visible worker-owned PREPARED window is permitted);
7. commit.

For a LOCAL_SQL effect, the same transaction inserts the request+binding and applies only the exact LAB-091-authorized local mutation if that mutation is itself the final atomic effect. If the local effect has a later commit phase, it follows the same broker-owned prepared semantics.

After this transaction commits, worker-session ownership is over. The effect can be completed only by broker effect/recovery machinery even if the original worker remains alive.

## 5. One-to-one association invariants

For ANCHORED effects, verifier/recovery MUST prove:

- one `worker_request_digest` -> one `effect_binding_digest`;
- one binding -> one `provenance_transition_id`;
- one provenance transition -> one `anchor_intent_id` under the frozen provenance schema;
- one durable worker request cannot point to two LAB-080 intents;
- two durable worker requests cannot claim the same provenance transition or anchor intent unless an explicitly frozen future application-idempotency layer defines shared ownership. V1 rejects this aliasing.

The implementation should therefore add uniqueness on `provenance_transition_id` and `anchor_intent_id` for non-NULL ANCHORED rows (partial UNIQUE indexes or equivalent exact guards), and uniqueness on `local_effect_id` for LOCAL_SQL rows.

These uniqueness rules are defense-in-depth; startup still verifies semantic/canonical identity rather than trusting indexes alone.

## 6. State transitions

Allowed durable state transitions are monotonic:

- initial durable effect: `PREPARED_RECOVERY_OWNED`;
- exact provider call returns timeout/UNKNOWN: `PREPARED_RECOVERY_OWNED -> UNKNOWN_RECOVERY_OWNED`;
- exact reconcile/confirmation + local/provenance commit: `PREPARED_RECOVERY_OWNED|UNKNOWN_RECOVERY_OWNED -> COMMITTED`;
- `COMMITTED` is terminal.

No transition back to a worker-owned state exists. No `COMMITTED -> *`, no deletion, no rebinding, and no state reset on a new session/restart.

`EFFECT_PREPARED` remains a schema-reserved state only if an executable implementation needs an internal same-transaction staging marker; startup must never accept a durable externally visible row in that state. Prefer direct durable insertion as `PREPARED_RECOVERY_OWNED`.

## 7. UNKNOWN and crash windows

### Crash before durable prepare commit

No durable worker/effect row is authoritative. No provider call is allowed before prepare commit. New startup does not resurrect the old session/request.

### Crash after durable prepare, before provider call

Startup finds exact request+binding+provenance/LAB-080 PREPARED identity. Old session is invalid. Recovery may issue only the exact frozen LAB-080 request id after normal verifier/evidence/planner authorization.

### Timeout/crash after provider commit, before local confirmation

The original request/binding and LAB-080 request id remain immutable. Mark/reconstruct `UNKNOWN_RECOVERY_OWNED` from exact durable/evidence state. Only `reconcile_increment(original_request_id)` is allowed; no new probe request id.

### Crash after LAB-080 confirmation, before provenance/local commit

Recovery re-authenticates the exact receipt and completes the already PREPARED transition/binding. It cannot allocate a replacement request or effect.

### Crash after durable COMMITTED, before response delivery

Restart returns/reconstructs the immutable `worker_effect_results_v1` descriptor only to a newly authorized application request through explicit idempotency policy. It never revives the old worker session and never re-runs the effect.

## 8. Restart reconstruction

Startup order remains the frozen broker startup state machine. Before any worker delegation:

1. invalidate all pre-restart sessions unconditionally;
2. verify durable worker-effect registry schema exactly once provenance says it is installed;
3. canonical-decode/hash every durable request/binding/result used for a decision;
4. join ANCHORED bindings to exact provenance transition and LAB-080 intent;
5. reject orphan/rebound/deleted/duplicate associations;
6. classify every non-COMMITTED durable worker request as broker-owned recovery work;
7. run external evidence + recovery planner/executor at most once per startup cycle under the already-frozen rules;
8. full reverify;
9. only after a clean NONE plan/aligned evidence may a brand-new worker session be issued.

No restart path converts a historical `session_id/session_epoch` back into ACTIVE state.

## 9. Duplicate convergence

While the original broker process is alive:

- same `(session_id,worker_request_id)` + same digest attaches to the same registry record/result;
- same pair + different digest rejects before effect;
- if the record is PREPARED/UNKNOWN, duplicate worker calls receive only `PENDING_RECONCILIATION` and cannot call provider/SQL effect paths;
- if COMMITTED, duplicate delivery is presentation-only.

After restart, old session-scoped request ids are not accepted as authorization. Cross-session duplicate convergence requires an explicit application idempotency key included in the canonical payload/policy; V1 does not infer semantic equality.

## 10. Deletion/rebinding detection

Fail closed before provider/SQLite mutation when any of the following is observed:

- durable request exists without binding;
- binding exists without request;
- ANCHORED binding references missing/multiple/wrong provenance transition;
- referenced provenance transition references missing/wrong LAB-080 intent;
- same anchor intent or transition is claimed by multiple worker bindings;
- canonical request bytes do not hash to stored request digest;
- canonical effect bytes do not hash/bind to stored effect-binding digest;
- stored session/request id differs from decoded canonical envelope;
- result exists for non-COMMITTED request or result digest/bytes mismatch;
- COMMITTED request lacks a valid terminal result descriptor when the executable contract requires one;
- historical row fields are rewritten while digests/foreign references are made superficially coherent.

Do not repair these by selecting the newest row, MAX(rowid), MAX(epoch), timestamps, or worker resubmission.

## 11. SQL authorization / immutability

When implemented on executable source, fold these tables into LAB-091 one-shot broker permits:

- request insert: exact effect-prepare permit only;
- binding insert: same exact prepare permit / canonical identity;
- request state update: exact allowed old->new transition only;
- result insert: exact commit permit only after durable effect/provenance commit evidence;
- UPDATE of identity/binding/result bytes: forbidden;
- DELETE: forbidden during normal operation.

As with provenance storage, SQLite guards are defense-in-depth inside LAB-087 sole-writer ownership; this is not a same-privilege SQLite sandbox claim.

## 12. RED-first matrix

Minimum executable matrix before production implementation:

1. effect request creates exactly one durable request+binding;
2. durable row starts recovery-owned, not worker-owned;
3. provider call cannot occur before prepare transaction commit;
4. crash before prepare commit leaves no durable effect obligation;
5. crash after prepare/before provider call reconstructs exact frozen effect;
6. restart invalidates originating worker session;
7. restart never marks historical session ACTIVE;
8. same live session/request id + same digest converges;
9. same live session/request id + different digest rejects;
10. canonical envelope one-byte mutation rejects;
11. canonical effect one-byte mutation rejects;
12. TEXT/REAL/bool type confusion rejects;
13. request without binding fails startup;
14. binding without request fails startup;
15. duplicate binding for one request rejected;
16. two worker requests claiming one provenance transition rejected;
17. two worker requests claiming one LAB-080 anchor intent rejected;
18. ANCHORED binding missing provenance transition rejected;
19. ANCHORED binding missing LAB-080 intent rejected;
20. referenced transition points to different LAB-080 intent rejected;
21. LOCAL_SQL binding containing anchor/provenance ids rejected;
22. ANCHORED binding containing local_effect_id rejected;
23. PREPARED ownership cannot transfer back to worker;
24. worker retry while PREPARED is presentation-only/pending;
25. timeout after provider commit preserves original request id;
26. UNKNOWN cannot allocate a second LAB-080 request id;
27. UNKNOWN exact reconcile can advance only the same durable operation;
28. crash after provider confirmation/before local commit completes exact transition once;
29. COMMITTED request cannot return to UNKNOWN/PREPARED;
30. committed response loss does not repeat effect;
31. result row is immutable;
32. result for non-COMMITTED request rejected;
33. result digest mismatch rejected;
34. deleting historical request fails startup;
35. deleting historical binding fails startup;
36. deleting/rebinding referenced provenance transition fails startup;
37. deleting/rebinding LAB-080 intent/receipt fails existing provenance/ledger verification;
38. coherent rewrite of request fields with stale canonical bytes fails;
39. coherent rewrite of binding references with recomputed local columns but no authenticated parent proof fails;
40. rowid/MAX/timestamp attacker rows do not select authority;
41. duplicate exact insert race converges or one loses before provider call;
42. concurrent same id/different digest race cannot create two effects;
43. revocation after compute/before durable prepare prevents request row/effect;
44. revocation after durable prepare leaves recovery duty intact;
45. authority/provenance drift before prepare fails pre-effect check and leaves no durable effect;
46. authority/provenance drift after prepare cannot rewrite binding; recovery uses exact preconditioned operation or fails closed;
47. broker sole-writer loss prevents state transition/provider call;
48. startup with one valid PREPARED worker effect plus matching provenance/LAB-080 state yields one recovery plan;
49. startup with two unexplained PREPARED worker effects fails closed unless future executable contract explicitly supports serialized multiple pending effects;
50. final audit proves no worker-callable path can bypass registry creation before effect or mutate registry identities after preparation.

## 13. Decision

Freeze as:

`WORKER_REQUEST_EFFECT_REGISTRY_STORAGE_V1_FROZEN`.

Implementation order when exact executable RED/GREEN becomes available:

1. canonical request/effect value types and strict digests;
2. three STRICT tables + exact uniqueness/immutability guards;
3. atomic pre-effect prepare transaction with one-to-one provenance/LAB-080 association;
4. broker-only PREPARED/UNKNOWN state machine;
5. immutable terminal result delivery;
6. restart verifier/recovery joins;
7. session revocation/re-entry composition;
8. execute the 50-case matrix and downstream LAB-080/087/091/093/provenance gates.

Do not implement by persisting resumable worker tokens, inventing a second provider idempotency id, replaying worker RPC messages after crash, or reconstructing effect bytes from mutable post-crash state.