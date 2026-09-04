# LAB-093 worker request-envelope + effect-boundary authorization protocol V1

Date: 2026-09-04
Status: FROZEN DESIGN / RED-FIRST; production implementation waits for executable branch gates.

## Problem

The frozen LAB-093 worker-session protocol makes delegated capability validity temporal: a worker session is bound to broker-owned session epoch, provider generation, activation-authority digest, authenticated provenance head and aligned external evidence; revocation closes admission before any authority/provenance mutation.

That still leaves a finer boundary unresolved. A worker request can be admitted while the session is valid, perform compute for some time, and reach an effect boundary after the session or retained authority graph changed. Request retries can also race with broker recovery, crash/restart, or response loss. Without an exact request envelope and explicit pre-effect authorization rule, a valid-at-dispatch request can become a stale-session replay or duplicate external/durable effect.

The required property is:

> Worker identity authorizes compute only. Every durable or external effect is separately authorized by the broker at the effect boundary against the current session/authority state and one immutable canonical request identity. PREPARED/UNKNOWN work transfers to broker-owned recovery and can never be retried as a new worker effect.

## Composition

This protocol composes with:

- LAB-087: broker/process owns sole writable handles;
- LAB-090/LAB-100: provider activation/fencing authority;
- LAB-091: one-shot SQL writer authorization;
- LAB-093: least-capability façade and worker-session revocation/re-entry;
- LAB-080: deterministic external request identity and UNKNOWN reconciliation;
- LAB-097..100 + canonical provenance chain: retained authority/provenance state;
- frozen startup verifier/evidence/planner/recovery-executor/broker-state-machine contracts.

It does not create a second provider request-id namespace for the same effect and does not let workers call LAB-080, provider, SQLite, activation or recovery APIs directly.

## 1. Canonical WorkerRequestEnvelope

Every broker-admitted worker operation has one immutable value-only envelope:

- `protocol_version`: U64 semantic version, V1 = 1;
- `session_id`: exact broker-issued session id;
- `session_epoch`: exact broker-issued epoch;
- `worker_request_id`: 128-bit opaque identifier unique within the session;
- `method_id`: canonical operation identifier from the capability profile, not arbitrary callable text;
- `operation_class`: `READ_COMPUTE` or `EFFECT_REQUEST`;
- `payload_digest`: SHA-256 of canonical request payload bytes;
- `capability_profile_digest`;
- `provider_generation_id`;
- `activation_authority_digest`;
- `provenance_head_digest` and `provenance_head_epoch` observed by the broker when admitted;
- `admission_snapshot_digest`: digest of the broker's aligned/no-unresolved-activation admission snapshot;
- optional broker deadline/limits as additional constraints, never as authority.

The envelope itself is encoded with the shared canonical V1 byte encoding/domain-separation rules already frozen for provenance. Boolean/numeric/text coercion is forbidden; unknown or reordered fields fail closed.

Define:

`worker_request_digest = SHA256(domain || canonical_envelope_bytes)`

No field may be rewritten after admission. If payload or method changes, it is a different request and requires a different `worker_request_id`.

## 2. Broker request registry

The broker privately maintains a request record keyed by `(session_id, worker_request_id)` with exactly one immutable `worker_request_digest` and a broker-owned state:

`ADMITTED -> COMPUTING -> READY_FOR_EFFECT -> PREPARED -> COMMITTED`

Terminal non-effect states:

`CANCELLED`, `REJECTED`, `FAILED_BEFORE_EFFECT`.

Recovery-owned states:

`PREPARED_RECOVERY_OWNED`, `UNKNOWN_RECOVERY_OWNED`.

A duplicate `(session_id, worker_request_id)` with a different request digest is always `REQUEST_ID_REBOUND` and fails before compute/effect. A duplicate with the same digest is idempotent: it may return an already terminal result or attach to the same in-flight broker record, but can never create another effect path.

## 3. Two authorization checks

### A. Pre-dispatch check

Before dispatching worker compute, broker verifies:

1. session record is `ACTIVE`;
2. session id/epoch exactly match current private record;
3. method exists in the bound capability profile;
4. operation class matches method policy;
5. payload digest matches received canonical payload bytes;
6. envelope provider-generation / activation-authority / provenance bindings equal the broker's current verified state;
7. terminal external evidence is aligned and fresh enough for admission;
8. no unresolved activation/recovery/re-entry condition exists;
9. request id is unused or exact-idempotent same digest.

Failure produces no provider/SQLite/activation side effect.

### B. Pre-effect check

A passed pre-dispatch check does **not** authorize an effect later. Immediately before any durable/external mutation, broker must re-check inside the closest possible authoritative boundary:

1. request record is still the exact `READY_FOR_EFFECT` request;
2. session is still `ACTIVE`, same id and epoch;
3. request digest is unchanged;
4. capability profile still authorizes the method;
5. provider generation is unchanged;
6. activation-authority digest is unchanged;
7. authenticated provenance head digest+epoch are unchanged unless this exact broker operation is the sole operation whose authorized effect is the next append and the append protocol explicitly binds the parent;
8. terminal anchor/evidence class is still allowed for this operation;
9. no revocation/recovery/authority transition has begun;
10. LAB-087 sole-writer ownership is current;
11. LAB-091 exact one-shot SQL/effect permit is minted only after these checks and is bound to this request/effect identity.

Any mismatch cancels/rejects the effect. Compute output may be discarded or recomputed under a new session; it is never grandfathered by earlier admission.

## 4. Read/compute versus effect methods

`READ_COMPUTE` methods may only consume immutable/value data or broker-provided read snapshots. They cannot receive raw mutable handles. Their result is presentation-only unless later submitted through a separately authorized `EFFECT_REQUEST`.

`EFFECT_REQUEST` methods are requests for the broker to perform an effect. The worker does not execute the effect itself. The broker validates the worker-provided result/payload, performs the pre-effect check, freezes the exact effect identity/bytes, then invokes existing LAB-080/LAB-091/LAB-090/provenance machinery.

A method cannot dynamically upgrade itself from `READ_COMPUTE` to effectful behavior.

## 5. Effect identity and LAB-080 handoff

For effects that use the LAB-080 external monotonic anchor, the worker request identity is not substituted for LAB-080's deterministic provider request id.

Instead, the broker derives/binds the exact LAB-080 operation from the already-frozen worker request and retained state, and stores a durable association:

`worker_request_digest -> provenance/event digest -> LAB-080 intent_id/request_id/position`.

The association is one-to-one for the effect. A retry of the same worker request can only discover/re-present/reconcile this same association; it cannot allocate a second LAB-080 request id.

For purely local SQL effects, the one-shot LAB-091 permit is similarly bound to `worker_request_digest` plus exact old/new durable state.

## 6. PREPARED / UNKNOWN ownership transfer

The instant a worker-originated effect reaches durable `PREPARED`, ownership changes from worker-session execution to broker recovery semantics.

Rules:

- request state becomes `PREPARED_RECOVERY_OWNED` before returning control to worker-facing code;
- worker may not retry provider/SQL mutation directly;
- if the provider call returns UNKNOWN/timeout-after-commit, state becomes `UNKNOWN_RECOVERY_OWNED` and retains the exact original LAB-080 request id / canonical effect bytes;
- session revocation does not delete or rewrite this durable operation;
- restart does not require the old worker session to finish it;
- only the frozen verifier -> evidence -> planner -> recovery-executor path may reconcile/commit it;
- after recovery commits, duplicate worker response delivery is presentation-only and cannot re-execute the effect.

Thus stale-session replay is impossible even when the original worker disappears or retries after a timeout.

## 7. Response/result idempotency

Broker stores/derives a stable terminal result descriptor keyed by `worker_request_digest`:

- `COMMITTED`: exact committed effect/result identity;
- `CANCELLED/REJECTED/FAILED_BEFORE_EFFECT`: terminal non-effect reason;
- recovery-owned states expose only an opaque `PENDING_RECONCILIATION` status to the worker surface.

A duplicate exact request may receive the same terminal result. Delivery attempts are not effect attempts.

The broker must never interpret "client did not receive response" as permission to issue a fresh effect request id.

## 8. Cancellation semantics

Cancellation before `PREPARED`:

- `ADMITTED/COMPUTING/READY_FOR_EFFECT` may move to `CANCELLED`;
- pre-effect check subsequently fails;
- no new durable/external effect is allowed.

Cancellation after `PREPARED` or UNKNOWN:

- cannot erase/rewrite the operation;
- only stops worker-facing waiting/presentation;
- broker recovery still reconciles exact frozen identity as required for durable consistency.

Cancellation after COMMITTED affects response delivery only, never committed history.

## 9. Revocation interaction

Revocation ordering remains:

`close admission -> mark sessions REVOKING -> classify requests -> transfer PREPARED/UNKNOWN to broker recovery -> revoke -> mutate authority/recover`.

At classification:

- `ADMITTED/COMPUTING/READY_FOR_EFFECT` cannot cross the effect boundary once epoch changes;
- stale compute outputs fail the pre-effect check;
- `PREPARED/UNKNOWN` retain their exact durable effect identity but lose all worker authority;
- `COMMITTED` may be re-presented but cannot spawn a follow-on effect.

A copied/stashed old façade therefore cannot turn an old compute result into a new effect after re-entry.

## 10. Crash/restart

Worker request registry entries that matter to durable/external consistency must be recoverable from broker-owned durable state; ephemeral compute-only entries may disappear.

On restart:

1. all old sessions are invalid;
2. durable PREPARED/UNKNOWN effects are discovered from existing canonical provenance/LAB-080 records, not reconstructed from worker messages;
3. recovery completes or fails closed;
4. only after fresh clean re-entry can a new session resubmit application intent;
5. if it resubmits an operation corresponding to an already committed durable request, the application layer may map it to the prior terminal result only through an explicit stable idempotency key; otherwise it is a new request under the new session.

Do not revive old session-scoped `worker_request_id` as new authorization after restart.

## 11. Concurrency and duplicate races

Two brokers/workers racing the same `(session_id, worker_request_id)` must converge on one request record/digest. A different digest loses before effect. The sole-writer/LAB-091 boundary serializes effect preparation.

Two different worker request ids that describe semantically similar payloads are distinct application requests unless a higher-level application idempotency key is explicitly part of the method's canonical payload and policy. The broker must not guess semantic deduplication.

## 12. Failure taxonomy

Fail closed before effect:

- stale/revoked session;
- session epoch mismatch;
- request-id rebound;
- payload digest mismatch;
- method/capability mismatch;
- authority/provenance/provider-generation drift;
- stale/unaligned evidence;
- unresolved activation/recovery;
- lost sole-writer authority;
- malformed canonical envelope.

Recovery-owned, not worker-retryable:

- durable PREPARED;
- timeout-after-provider-commit / UNKNOWN;
- local commit pending after authenticated external confirmation.

Presentation-retryable:

- committed response lost;
- terminal non-effect result delivery lost.

## 13. RED-first executable matrix

Minimum matrix before implementation:

1. valid read/compute dispatch succeeds under active session;
2. forbidden method fails pre-dispatch;
3. payload one-byte mutation fails digest check;
4. same request id + different payload fails rebound;
5. same request id + same payload is idempotent;
6. request admitted then session revoked before effect -> no effect;
7. request admitted then provider generation changes -> pre-effect reject;
8. activation-authority digest changes -> pre-effect reject;
9. provenance head changes -> pre-effect reject unless exact authorized parent-bound append case;
10. terminal evidence becomes UNKNOWN -> pre-effect reject;
11. sole-writer lease lost -> pre-effect reject;
12. stale compute result cannot publish after epoch change;
13. READ_COMPUTE method cannot obtain raw SQLite/provider handle;
14. READ_COMPUTE cannot dynamically invoke effect path;
15. EFFECT_REQUEST worker never directly calls provider;
16. effect preparation binds exact worker request digest;
17. LAB-080 request association is created once;
18. duplicate exact worker retry does not allocate second LAB-080 request id;
19. duplicate exact worker retry does not allocate second SQL effect;
20. PREPARED transfers ownership to broker recovery;
21. worker cannot retry PREPARED effect;
22. UNKNOWN preserves exact original provider request id;
23. UNKNOWN retry through worker surface is rejected/presentation-only;
24. broker recovery can reconcile without worker process alive;
25. broker restart invalidates old session;
26. restart retains durable PREPARED/UNKNOWN identity;
27. committed response loss -> duplicate delivery only, no effect;
28. cancel before PREPARED prevents effect;
29. cancel after PREPARED does not erase durable recovery duty;
30. cancel after COMMITTED does not roll back history;
31. two concurrent duplicate exact requests converge to one record;
32. concurrent same id/different digest rejects one before effect;
33. two distinct ids are not silently deduplicated absent app idempotency policy;
34. capability-profile digest mismatch fails;
35. malformed integer/bool/text canonical type fails;
36. unknown/reordered envelope field fails;
37. worker_request_digest domain cannot be confused with provenance/ticket digest domain;
38. revocation classifies READY_FOR_EFFECT as no-effect cancelled;
39. revocation classifies PREPARED as recovery-owned;
40. old copied façade cannot submit old result after re-entry;
41. new session cannot reuse old session id/epoch binding;
42. committed result descriptor is immutable;
43. recovery-owned status leaks no mutable provider/recovery capability;
44. application idempotency key, when supported, is canonical payload data and cannot be rebound;
45. timeout before provider request leaves no PREPARED external effect;
46. timeout after provider commit enters exact UNKNOWN recovery path;
47. crash between PREPARED and provider call restarts from exact frozen identity;
48. crash between provider confirmation and local commit reconciles exact identity once;
49. final audit finds no worker-callable effect path that skips pre-effect authorization;
50. final audit finds no duplicate/idempotency path that can mint a second external/durable effect for one exact request.

## 14. Decision

Freeze as:

`WORKER_REQUEST_ENVELOPE_EFFECT_BOUNDARY_V1_FROZEN`.

Implementation order when executable RED/GREEN is available:

1. canonical value-only envelope + digest;
2. private broker request registry/state machine;
3. pre-dispatch authorization;
4. explicit read/compute vs effect method metadata;
5. pre-effect current-state authorization wired immediately before LAB-091/LAB-080/LAB-090 effect preparation;
6. exact worker-request -> durable effect/LAB-080 association;
7. PREPARED/UNKNOWN ownership transfer to broker recovery;
8. idempotent terminal result delivery;
9. revocation/restart composition;
10. execute the 50-case matrix and audit every worker-callable effect surface.

Do not implement this with only RPC-level retries, client-generated timestamps, token expiry, or worker-side `cancelled` flags. The broker must own request identity, effect authorization, duplicate convergence and recovery handoff.