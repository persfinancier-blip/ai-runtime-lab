# External provider UNKNOWN-outcome reconciliation oracle V1

Status: `EXTERNAL_PROVIDER_UNKNOWN_OUTCOME_RECONCILIATION_ORACLE_V1_FROZEN`

Date: 2026-09-05

Composes with: LAB-093 durable request/effect registry and application idempotency; epoch-aware client/API + external cutover adapter contract; `EXTERNAL_PROVIDER_IDEMPOTENCY_CAPABILITY_EVIDENCE_CONFORMANCE_LIFECYCLE_V1_FROZEN`; LAB-100 trusted provider/adapter capability authority; global authenticated provenance/recovery chain.

## Problem

An external effect can leave the local runtime in `UNKNOWN`: the request may have reached the provider and committed while the client timed out, disconnected, crashed, or lost the response. A blind resend is safe only while the exact historically bound provider-idempotency capability proves that retry remains duplicate-suppressed. Once that proof is absent or expired, retrying can create a second external effect.

A separate read/status surface can sometimes resolve the ambiguity, but only if it is authoritative enough to answer the exact already-bound operation. A generic resource list, an eventually-consistent `NOT_FOUND`, a heuristic search, or a new mutation request is not such an oracle.

Therefore reconciliation needs a versioned, evidence-backed **read-only outcome oracle contract**. It must distinguish positive evidence, pending evidence, strong negative evidence, weak/ambiguous absence and provider unavailability without manufacturing a new effect identity.

## Primary-source observations

### Amazon EC2: client-token idempotency is separate from read consistency

EC2 documents same-client-token/same-parameters idempotent retries and mismatch failure for changed parameters. The token's scope can be regional or zonal depending on the operation.

Source: https://docs.aws.amazon.com/ec2/latest/devguide/ec2-api-idempotency.html

Separately, EC2 explicitly documents eventual consistency: after creating a resource, a subsequent describe call can temporarily report that the resource does not exist. AWS recommends exponential backoff and warns that an `InvalidInstanceID.NotFound` result does not by itself prove the preceding operation had no effect.

Source: https://docs.aws.amazon.com/ec2/latest/devguide/eventual-consistency.html

Implication: `NOT_FOUND` is not a universal negative oracle. Negative authority depends on the exact query surface, consistency guarantee, propagation horizon and identity binding.

### Google Cloud long-running operations

Google APIs expose operation resources for asynchronous work; an operation identifier can be polled through a separate `get` method to retrieve the latest operation state. Cloud Storage's operations endpoint similarly exposes a read-only `GET .../operations/{operationId}` status surface.

Sources:
- https://docs.cloud.google.com/storage/docs/json_api/v1/operations/get
- https://docs.cloud.google.com/java/docs/long-running-operations

Implication: a provider-assigned operation ID can be a strong reconciliation handle **only if the local runtime durably receives and binds it**. A client timeout before receiving that ID remains unresolved unless another pre-bound selector exists.

### Google Cloud Storage: consistency is operation-specific

Cloud Storage documents strong global consistency for object read-after-write/delete and listings, while other configuration/access operations have propagation delays. Its retry documentation also distinguishes always-idempotent, conditionally-idempotent and non-idempotent operations.

Sources:
- https://docs.cloud.google.com/storage/docs/consistency
- https://docs.cloud.google.com/storage/docs/retry-strategy

Implication: oracle strength belongs to an exact service/operation/query combination; it cannot be inherited from a provider brand or account globally.

## Frozen V1 decision

Every effect class that can enter transport/provider `UNKNOWN` must declare one of:

1. a proven resend horizon under its pinned idempotency capability;
2. an independently queryable authoritative reconciliation oracle;
3. both; or
4. no automated recovery, in which case unresolved `UNKNOWN` enters permanent manual reconciliation rather than being resent.

An oracle is **independent** only when invoking it cannot create, retry, resume, duplicate or otherwise advance the original effect. It is a read/status operation over an identity already bound to the original effect.

No reconciliation path may mint a new provider request identity, new application idempotency key, new trust epoch or substitute resource solely to escape `UNKNOWN`.

## Pre-I/O identity binding

Before first consequential provider I/O, the durable effect record must bind every locally knowable selector needed for later reconciliation:

- `effect_id` / application idempotency key;
- trust epoch + effect namespace;
- exact provider/account/project/tenant/service/region/zone/resource scope;
- exact provider request/idempotency token;
- canonical effect payload fingerprint;
- adapter + provider capability evidence generation;
- expected deterministic resource name/id when the provider permits caller-chosen identity;
- oracle type/version and pre-bound query selector class;
- first-send timestamp and resend/query deadlines.

Provider-assigned identifiers received only after I/O — request IDs, operation IDs, resource IDs — are appended atomically to the same effect record when observed. They strengthen future reconciliation but cannot be assumed to exist after a timeout that prevented receipt.

If authoritative reconciliation requires a provider-assigned operation ID and the protocol provides no pre-send/deterministic way to recover that ID after a lost first response, then `timeout-before-operation-id` is explicitly an unresolvable ambiguity unless resend remains proven safe.

## Oracle capability identity

Oracle semantics are part of the immutable provider capability evidence generation. Bind at least:

- provider/service/API operation being reconciled;
- exact query/status API and API version;
- query selector (`client_token`, operation ID, deterministic resource ID, request ID, composite key, etc.);
- account/project/region/resource scope;
- adapter implementation/configuration;
- authentication/authorization class required for the read;
- result consistency model;
- propagation/visibility bounds when documented;
- result retention/garbage-collection horizon;
- whether query results are complete or filtered/paginated;
- state/error taxonomy;
- payload/resource fields sufficient to prove outcome identity;
- capability evidence generation and activation state.

A change to query API, selector interpretation, scope, consistency, retention or adapter parsing creates a new evidence generation. Already-bound UNKNOWN operations keep the historical oracle semantics with which they were created; they do not silently migrate to a more convenient successor.

## Oracle result lattice

The runtime normalizes provider reads into the following fail-closed result classes.

### `COMMITTED_MATCH`

Authoritative evidence proves the original bound effect committed and the observed outcome matches the expected effect identity/payload constraints.

Required checks include all authority-relevant scope and resource attributes. A resource merely having a familiar name is insufficient if another actor could have created it independently.

Action: persist/reconcile result, never resend.

### `FINAL_FAILURE_MATCH`

Authoritative operation evidence proves the exact bound request reached a terminal provider failure that could not have committed the consequential effect.

Action: record terminal failure. A *new business attempt*, if product semantics allow one, must be a distinct explicitly created operation; it is not an automatic retry of the UNKNOWN operation.

### `PENDING_MATCH`

The exact bound operation is known to exist but has not reached a terminal state.

Action: poll according to the pinned oracle policy; never send a second effect request merely because completion is slow.

### `STRONG_NEGATIVE`

The oracle proves that the exact original request/effect did not commit and cannot still appear later under the provider's acceptance/consistency model.

This is intentionally difficult to establish. All of the following must hold:

1. query selector is exact and complete for the original request/effect identity;
2. query surface's relevant reads are strongly consistent **or** a documented propagation/acceptance horizon has elapsed;
3. there is no provider-side async queue that can still accept/commit the request later;
4. result retention has not expired in a way that makes completed operations disappear into the same `NOT_FOUND` state;
5. authorization/filtering/pagination cannot hide the result;
6. account/region/tenant/resource scope exactly matches the original request;
7. no contradictory provider receipt/event/resource evidence exists.

Only `STRONG_NEGATIVE` may be treated as authoritative absence. Whether a new business attempt is permitted is a separate product/effect state-machine decision; it never reuses the historical request identity.

### `WEAK_NEGATIVE`

The provider returns `NOT_FOUND`, empty list or equivalent absence, but at least one strong-negative condition is unproven — for example eventual consistency, unknown propagation delay, operation-record expiry, incomplete list/filter scope or ambiguous selector.

Action: remain `UNKNOWN`/polling; do not resend solely from this result.

### `AMBIGUOUS`

The query returns multiple possible outcomes/resources, a resource whose provenance cannot be bound to the original request, contradictory states across replicas/APIs, or a semantically incomplete response.

Action: fail closed; continue safer evidence collection or manual reconciliation.

### `ORACLE_UNAVAILABLE`

Timeout, permission loss, throttling, provider outage, malformed response, adapter failure or inability to authenticate the read.

Action: no state inference. Retry only the read under bounded read-safe policy; never turn oracle failure into permission to resend the effect.

## Why `NOT_FOUND` is not enough

`NOT_FOUND` has at least four materially different meanings:

1. the effect truly never committed;
2. it committed but is not yet visible through an eventually-consistent read;
3. it committed but its operation/status record aged out;
4. the query is pointed at the wrong scope or lacks permission/filter coverage.

The runtime therefore stores the provider's raw code plus the normalized evidence class and the capability generation used to interpret it. No adapter may map all provider `404`/`NotFound` responses directly to `STRONG_NEGATIVE`.

EC2 is the concrete donor for this rule: AWS explicitly warns that post-create describe calls may temporarily report not found because of eventual consistency.

## Positive outcome binding

A positive resource/status read resolves UNKNOWN only when the runtime can prove it is the outcome of the **same bound effect**.

Preferred binding mechanisms, strongest first:

1. provider operation object keyed by the original bound request/client token and exposing terminal result;
2. provider response/status carrying the exact client token/request correlation identifier;
3. deterministic caller-chosen immutable resource ID/name bound before first send, plus provider semantics proving create-if-absent/conditional creation;
4. provider event/audit record cryptographically or authoritatively binding request identity to resource identity;
5. weaker heuristic matching — **never sufficient alone** for automatic resolution.

If a found resource could have been independently created by another actor with the same user-visible attributes, it is `AMBIGUOUS`, not `COMMITTED_MATCH`.

## Eventual-consistency polling contract

For an oracle whose positive/negative visibility is eventually consistent but whose maximum safe visibility horizon is documented/evidenced:

1. record `query_started_at` and pinned horizon before polling;
2. use bounded exponential backoff with jitter appropriate to provider limits;
3. positive exact matches may resolve as soon as authenticated;
4. negative results remain `WEAK_NEGATIVE` until every documented acceptance/propagation bound needed for strong absence has elapsed;
5. do not extend the bound merely because repeated weak negatives are convenient;
6. query throttling/outage pauses evidence acquisition but does not change effect state;
7. after the maximum automated reconciliation deadline, transition to manual reconciliation if neither a terminal positive nor a true strong negative is proven.

A repeated series of weak negatives never becomes strong by vote count alone.

## Retention and tombstone ambiguity

Some providers retain dedupe/status records for a bounded period. After expiry, `NOT_FOUND` may mean either "never happened" or "happened, record forgotten".

Therefore capability evidence must distinguish:

- dedupe retention horizon;
- operation/status-query retention horizon;
- resource lifetime;
- deletion/tombstone visibility horizon.

If operation evidence can expire before the runtime's maximum UNKNOWN reconciliation horizon, the runtime must either possess another durable authoritative outcome path or mark the later interval query-only/manual. Expiry can never convert an unresolved UNKNOWN into absence.

Deletion of a created resource also does not prove the original create never happened. A provider resource can be committed and later deleted by another actor. Outcome reconciliation must reason about the original effect, not merely current resource existence.

## Query-before-resend rule

For an already-bound UNKNOWN operation:

1. verify local durable effect/application-idempotency history;
2. load its **pinned historical** provider capability/oracle evidence;
3. if an authoritative oracle is available, query it before any contemplated resend;
4. `COMMITTED_MATCH` -> reconcile success; no resend;
5. `PENDING_MATCH` -> continue query/poll; no resend;
6. `FINAL_FAILURE_MATCH` -> terminal failure; no same-operation resend unless the provider contract explicitly defines the original request as retryable without effect and the historical retry policy says so;
7. `STRONG_NEGATIVE` -> mark original effect as proven non-committed; any new attempt follows the product state machine with a distinct operation identity;
8. `WEAK_NEGATIVE`, `AMBIGUOUS`, `ORACLE_UNAVAILABLE` -> remain fail closed;
9. only if the historical capability independently proves a still-valid safe resend may the exact original provider token/payload be resent;
10. once that resend horizon expires, no successor capability may resurrect it.

This ordering prevents a read oracle from becoming merely advisory while code still retries first.

## Polling / reconciliation expiry

Automated reconciliation has explicit time/budget limits but safety does not expire with the worker lease.

When polling budget or operational deadline is exhausted:

- stop automated provider reads if policy requires;
- transition the effect to `MANUAL_RECONCILIATION_REQUIRED`;
- retain the exact provider token, payload digest, oracle evidence generation and all observed raw/normalized query results;
- block any automatic resend/new identity derived from the unresolved effect;
- expose a least-capability diagnostic view for human investigation;
- require a separately defined authenticated manual-resolution protocol for any human terminal classification.

`MANUAL_RECONCILIATION_REQUIRED` is a durable safety state, not an error that a generic retry loop may clear.

## Crash and restart semantics

Every oracle observation is append-only/authenticated evidence linked to the existing global provenance chain.

Crash rules:

- crash before persisting a query result: restart may repeat the read; no effect mutation inferred;
- crash after persisting `PENDING/WEAK_NEGATIVE`: restart resumes from durable state and original bounds;
- crash after persisting terminal evidence but before local delivery: restart re-verifies the same terminal evidence and delivers/reconciles without provider mutation;
- crash during transition to manual reconciliation: atomic state transition must be replayable/idempotent;
- restart never resets first-send time, resend deadline, oracle horizon or capability generation.

Provider reads themselves must be side-effect-free according to capability evidence. If a purported "status" call can resume/retry the operation, it is not a V1 oracle and requires a separate mutation protocol.

## Authentication, scope and least capability

The oracle credential may be different from the effect credential and should be read-only/least-privilege where provider IAM allows it. However, lack of read permission is `ORACLE_UNAVAILABLE`, never proof of absence.

The query response must be bound to the exact provider account/project/tenant/region/service endpoint expected by the effect record. Cross-account or cross-region lookups cannot resolve the original operation unless the provider contract explicitly defines that scope and the capability evidence records it.

No secrets are stored in durable evidence; retain stable non-secret account/scope identifiers and response digests/selected fields sufficient for re-verification.

## Capability drift

Any authority-relevant change in oracle behavior — documentation, API version, consistency guarantee, retention, response parsing, scope, IAM filtering or adapter code — enters the existing provider capability drift lifecycle.

For **new** effects, drift blocks admission until a successor capability is verified.

For **already UNKNOWN** effects, the runtime must preserve their historical evidence generation. A newly discovered restrictive fact may make automation less permissive (for example, downgrade a supposed strong negative to weak/ambiguous), but a newer capability cannot reinterpret an old ambiguous read into a more permissive terminal state without independent evidence tied to that operation.

## Relationship to application idempotency

LAB-093 permanent application-key non-reuse answers: "have we already admitted this business effect locally?"

Provider idempotency answers: "can the exact already-bound external request be resent without duplicating the effect?"

The reconciliation oracle answers: "what happened to that exact already-bound external request without resending it?"

All three are required for a robust UNKNOWN path. None substitutes for another.

## Relationship to post-re-root epochs

A reconciliation query never changes trust/effect epoch. An UNKNOWN operation from old epoch `E0` remains an `E0` operation forever even if a later `E1` namespace has been security-authorized.

A provider resource discovered during E1 cannot be attributed to E0 without exact E0 request/effect evidence. Likewise, an unresolved E0 UNKNOWN cannot be copied/reissued under E1 simply to regain availability.

## RED-first regression matrix

Production implementation must start with executable tests. Minimum V1 matrix: 64 cases.

### Identity binding before first I/O
1. request token/payload/scope/oracle generation durably bound before provider mutation.
2. provider call attempted before binding -> reject/no I/O.
3. deterministic resource ID bound before send -> preserved through UNKNOWN.
4. operation ID received after send -> appended to same effect record.
5. timeout before operation ID with no recoverable selector -> stays ambiguous.
6. restart preserves original token and oracle selector.
7. successor capability cannot change selector of existing UNKNOWN.
8. trust-epoch change cannot change selector of existing UNKNOWN.

### Positive resolution
9. exact operation ID returns completed matching payload/resource -> `COMMITTED_MATCH`.
10. matching client token returns committed result -> `COMMITTED_MATCH`.
11. resource exists but request correlation mismatches -> `AMBIGUOUS`.
12. resource attributes match heuristically but provenance absent -> `AMBIGUOUS`.
13. provider returns terminal exact failure -> `FINAL_FAILURE_MATCH`.
14. provider returns exact pending -> `PENDING_MATCH`.
15. positive response in wrong account/region -> reject.
16. positive response parser omits authority-relevant field -> ambiguous/fail closed.

### Negative semantics
17. strongly-consistent exact query proves no request/effect -> `STRONG_NEGATIVE`.
18. eventual-consistent immediate not-found -> `WEAK_NEGATIVE`.
19. repeated weak negatives before horizon -> still weak.
20. documented propagation horizon elapsed + all strong-negative conditions met -> strong negative.
21. unknown propagation horizon -> never auto-upgrade to strong negative.
22. status record retention expired -> not-found remains ambiguous/weak.
23. permission-filtered empty result -> unavailable/ambiguous, not strong negative.
24. wrong-scope not-found -> reject.

### Eventual consistency / polling
25. pending -> pending -> committed -> resolve without resend.
26. weak negative -> committed within propagation window -> resolve committed.
27. throttled read -> retry read only.
28. oracle timeout -> retry read only.
29. provider outage -> no effect resend permission created.
30. polling deadline expires unresolved -> manual reconciliation.
31. restart during polling preserves original deadlines.
32. repeated polls do not extend provider resend horizon.

### Retry ordering
33. UNKNOWN with oracle + safe resend available -> query first.
34. query says committed -> resend forbidden.
35. query says pending -> resend forbidden.
36. query unavailable but historical resend still proven safe -> exact-token resend only if policy explicitly permits.
37. historical resend horizon expired -> no resend even if successor capability is safer.
38. weak negative does not authorize resend after horizon.
39. new token generated to resolve UNKNOWN -> reject.
40. new trust epoch used to resolve old UNKNOWN -> reject.

### Resource deletion / tombstones
41. original effect committed then resource deleted -> deletion does not become strong negative.
42. operation record committed but resource missing -> retain committed classification.
43. operation record aged out while resource remains exactly attributed -> reconcile via resource evidence if capability permits.
44. both operation record and resource absent after retention expiry -> manual/ambiguous unless strong negative independently proven.
45. recreated same human-readable resource name by another actor -> not original outcome.
46. provider tombstone exact request binding -> may resolve only if capability proves semantics.

### Crash / durable evidence
47. crash after provider query before local persistence -> safe read repeat.
48. crash after persisted committed evidence before client delivery -> no provider resend.
49. crash after persisted pending -> resume query.
50. crash while entering manual state -> deterministic recovery.
51. tampered stored oracle observation -> fail provenance verification.
52. rollback removes later terminal observation -> detected by global provenance continuity.

### Capability drift
53. query API version changes -> block new effects.
54. consistency guarantee becomes weaker -> invalidate new admission.
55. parser version changes authority-relevant interpretation -> new generation required.
56. historical UNKNOWN retains old generation after successor activation.
57. restrictive new evidence downgrades unsafe historical inference -> fail closed.
58. permissive successor cannot retroactively upgrade old weak negative to strong.

### Mixed namespaces / scope
59. E0 UNKNOWN remains E0 after E1 activation.
60. same provider token in another region cannot satisfy regional E0 query.
61. account migration cannot resolve old-account UNKNOWN from new account.
62. legacy client retry without epoch-aware identity cannot bypass reconciliation.

### Oracle purity / manual boundary
63. status API that resumes/retries operation is rejected as a read oracle.
64. unresolved ambiguity requires authenticated manual-resolution protocol; generic retry worker cannot clear it.

## Frozen implementation direction

When exact executable source becomes available, implementation should begin with a provider-agnostic normalized oracle interface plus durable tests, not provider-specific imperative retry code.

Suggested narrow interface shape:

- immutable `OutcomeQueryBinding` stored before first I/O;
- immutable/versioned `OutcomeOracleCapability` from provider evidence;
- pure adapter method `query(binding) -> RawOutcomeObservation` with no mutation method reachable through the reconciliation capability;
- deterministic normalizer `classify(raw, capability, effect) -> OracleClassification`;
- durable append of raw digest + canonical selected evidence + classification;
- state-machine transition guarded by exact effect version/CAS;
- separate resend decision consuming historical capability + oracle classification, never embedded inside the query adapter.

This separation makes it testable that the query path cannot silently mutate and that `NOT_FOUND` interpretation depends on authenticated capability semantics rather than provider-specific ad-hoc exception handling.

## Audit verdict

V1 closes the design gap between "idempotency retry" and "we know what happened". The core invariant is:

> **UNKNOWN is resolved by evidence, not by optimism.** A read/status result may authorize a terminal classification only when it is exact, scope-correct, capability-backed and sufficiently consistent. Weak absence, unavailable reads or expired status history preserve uncertainty; they never manufacture permission to resend.

No production implementation or behavioral PASS is claimed in this artifact. Exact RED/GREEN remains gated on executable source access.