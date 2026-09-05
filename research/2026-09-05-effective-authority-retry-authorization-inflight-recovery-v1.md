# Effective-authority retry authorization / in-flight attempt recovery V1

Status: `EFFECTIVE_AUTHORITY_RETRY_AUTHORIZATION_INFLIGHT_RECOVERY_V1_FROZEN`

Date: 2026-09-05

Scope: design-only fallback for LAB-093 while LAB-086 exact publication/execution remains blocked by the current runtime's lack of a byte-preserving predecessor+patch transform path. This note creates no production implementation or behavioral PASS.

## Problem

The one-shot `EffectiveAuthorityLeaseV1` contract freezes `SEND_STARTED` before consequential provider I/O and conservatively treats crash/timeout after that point as an ambiguous external outcome. A recovery mechanism is still required for providers whose documented capability permits safe same-identity retries, and for providers exposing a read-only operation/status oracle.

The dangerous design is to recover by minting another ordinary SEND lease. That would turn worker death, lease expiry, broker restart, or timeout into a fresh effect-creation authority and could create a second provider request identity.

This contract therefore introduces a distinct non-effect-minting authority whose only permitted mutation-like action is a replay of the *already pinned* provider request identity when exact provider semantics prove that replay idempotent.

## Core invariant

After an attempt reaches durable `SEND_STARTED`, recovery authority MUST NOT create a new effect identity, provider request/idempotency token, payload identity, provider/account/region scope, trust epoch, effect namespace, operation identity, or application idempotency key.

Recovery is restricted to exactly one of three mutually exclusive paths:

1. `SAME_IDENTITY_RETRY` — replay the exact previously pinned provider request identity and exact payload only when current pinned provider-capability evidence proves this retry is still inside its safe semantics/window;
2. `READ_ONLY_ORACLE` — query the already-bound provider operation/resource/request identity without consequential mutation;
3. `MANUAL_RECONCILIATION` — fail closed and transfer adjudication to the frozen manual-UNKNOWN process when neither automatic path can prove safety.

No path may fall back to a generic SEND lease.

## Retry authority object

`EffectiveRetryAuthorizationV1` is a signed/domain-separated one-attempt recovery capability. Its canonical payload binds at least:

- `operation_id`;
- `effect_id`;
- original `attempt_id`;
- original `send_started_record_id`;
- original application-idempotency identity;
- exact payload digest/canonical request digest;
- exact provider/service/API operation;
- account/tenant/project/region/zone/cluster scope as applicable;
- exact provider request/idempotency token or exact pre-bound operation identity;
- provider-capability generation pinned at the original attempt;
- adapter generation and token-construction generation pinned at the original attempt;
- trust epoch + effect namespace;
- allowed recovery mode (`SAME_IDENTITY_RETRY` or `READ_ONLY_ORACLE`);
- retry sequence number / recovery claim id;
- issuance/expiry bounds;
- current quarantine/effective-authority generation used only as an additional deny gate;
- issuer/key/audience/principal identity;
- parent global-provenance head.

It intentionally contains no field that permits choosing a replacement token, replacement request identity, new payload, or new provider scope.

## Durable attempt state machine

Representative states:

`PREPARED -> LEASE_CLAIMED -> SEND_STARTED -> {OUTCOME_COMMITTED | UNKNOWN}`

From `UNKNOWN`, recovery may transition through:

- `RETRY_AUTHORIZED -> RETRY_STARTED -> {OUTCOME_COMMITTED | UNKNOWN}` using the same provider identity; or
- `ORACLE_AUTHORIZED -> ORACLE_QUERIED -> {COMMITTED_MATCH | FINAL_FAILURE_MATCH | PENDING_MATCH | STRONG_NEGATIVE | WEAK_NEGATIVE | AMBIGUOUS | ORACLE_UNAVAILABLE}`; or
- `MANUAL_RECONCILIATION_REQUIRED`.

`SEND_STARTED` and every `RETRY_STARTED` are append-only historical facts. A later outcome never rewrites them.

## Mint predicates

A `SAME_IDENTITY_RETRY` authorization is mintable only when all are true:

1. the durable original attempt exists and is at/after `SEND_STARTED`;
2. no terminal authoritative outcome is already committed;
3. original provider request identity/token and exact payload digest are durably pinned;
4. the provider-capability generation pinned to the attempt explicitly permits retrying the same identity with the same parameters;
5. the proven idempotency/deduplication retention horizon has not expired, or an independently authoritative provider contract proves equivalent safety;
6. token scope/normalization/truncation rules still map the exact stored token to the same provider-side identity;
7. no parameter drift exists, including hidden adapter defaults that are part of provider idempotency semantics;
8. current quarantine/revocation state does not forbid outbound recovery traffic for this exact effect class;
9. adapter/runtime generation is capable of reproducing the exact previously committed wire identity without minting/re-normalizing it into a different provider identity;
10. no concurrent recovery claim is active for the attempt;
11. global provenance and authority-generation continuity verify;
12. any provider-specific `PENDING` / in-progress response semantics are explicitly handled by the pinned capability contract.

If any predicate is unknown, false, expired, or unverifiable, same-identity resend is forbidden.

## Pinned capability versus current capability

The original attempt's provider-capability generation controls whether its historical request identity may be replayed. A newer capability generation cannot retroactively widen the historical retry envelope.

Current capability/quarantine state may only remove permission. It may not grant a historical retry that the pinned generation did not prove safe.

Therefore:

`effective_retry_allowed = historical_pinned_capability_allows AND current_policy_does_not_revoke`

Never:

`effective_retry_allowed = latest_capability_allows`.

This prevents a provider documentation/configuration change from reclassifying an old UNKNOWN attempt as safely retryable.

## Exact same-identity rule

For `SAME_IDENTITY_RETRY`, the adapter MUST load, not regenerate, all provider-visible authority-relevant values from durable attempt state.

At minimum the adapter verifies before I/O:

- exact provider token/request id bytes/string;
- exact canonical payload/request fingerprint;
- exact API operation and endpoint scope;
- exact account/tenant/region/zone/cluster dimensions required by the provider's idempotency model;
- exact adapter token mapping generation;
- exact original attempt/effect binding.

Any normalization, truncation, default insertion, endpoint change, credential/account change, region change, or payload change that can alter provider-side idempotency identity must fail closed.

A provider API returning an idempotent-parameter-mismatch/conflict response is evidence of identity inconsistency; it is not permission to mint a new token.

## In-progress responses

A provider may report that another request with the same token is still processing. Such a response is not failure evidence and not permission for a fresh identity.

The recovery policy may:

- continue bounded same-token polling/retry when the provider contract explicitly defines that as safe; or
- switch to a read-only operation/status oracle if an already-bound authoritative operation resource exists; or
- stop in `UNKNOWN`/manual reconciliation when the safety horizon is exhausted.

## Read-only oracle separation

`READ_ONLY_ORACLE` authority is a separate least-capability object. It may call only predeclared read/status surfaces and may use only already-bound selectors.

It cannot:

- invoke create/update/delete/resume operations;
- mint provider request tokens;
- call an endpoint whose read form can trigger implicit creation/resumption;
- transform a weak negative into `STRONG_NEGATIVE` without the frozen oracle predicates;
- consume or replace the original retry identity.

Oracle results compose with the existing result lattice and UNKNOWN reconciliation contract.

## Retention expiry

Finite provider idempotency retention is a hard boundary.

When the proven deduplication/replay window expires, the same historical token may no longer be safe to submit even if its textual value is unchanged. Expiry therefore transitions automatic resend authority to denied.

Allowed next steps are:

- authoritative read-only outcome query, if available and still within its own evidence-retention contract; or
- `MANUAL_RECONCILIATION_REQUIRED`.

Expiry never creates a fresh business attempt automatically.

A genuinely new business attempt, if product semantics require one after terminal reconciliation, must be a new application-level operation with a new explicitly authorized effect identity. It cannot be represented as recovery of the historical UNKNOWN attempt.

## Crash ordering

Before any same-identity retry provider I/O:

1. verify original attempt + global provenance;
2. verify exact pinned request identity and payload;
3. verify pinned capability retry predicates and current deny gates;
4. atomically claim the recovery sequence with compare-and-swap/unique durable constraint;
5. durably append `RETRY_STARTED(recovery_claim_id, original_provider_identity, payload_digest)`;
6. only then perform provider I/O;
7. append provider response/evidence/outcome or remain UNKNOWN on crash/timeout.

Crash before step 5 means no provider retry was authorized as started.
Crash after step 5 is conservatively another ambiguous contact with the *same* provider identity. Restart must not assume the retry did or did not reach the provider.

Multiple recovery crashes can therefore produce multiple `RETRY_STARTED` records, but every one must carry the exact same provider request identity and payload. They are repeated contacts for one provider-side idempotency identity, not new attempts/effects.

## Concurrency / stale workers

The durable store enforces at most one active recovery claim per original attempt/recovery sequence.

A stale worker holding an old retry authorization must revalidate immediately before provider I/O that:

- its claim is still current;
- no terminal outcome was committed;
- current quarantine/revocation has not denied the action;
- the historical retry window remains valid.

If any fail, the adapter performs no provider mutation.

The authority itself is audience/principal bound and one-shot claim bound; copying it to another worker must not bypass durable claim ownership.

## Quarantine and revocation races

Quarantine/revocation may prevent a not-yet-started recovery request from reaching the provider.

If `RETRY_STARTED` is already durably appended and provider I/O may have begun, revocation cannot erase that fact or reclassify the attempt as unsent. The outcome remains subject to the same UNKNOWN/oracle/manual-resolution rules.

Re-admission after quarantine never changes the original provider identity or extends an expired historical idempotency horizon.

## Provider drift

Observed/documented drift in token semantics, scope, retention, changed-parameter behavior, or operation-status behavior transitions the capability to a challenged/drift state for affected operations.

For historical UNKNOWN attempts this removes automatic retry authority unless the historical semantics remain independently proven. Drift never causes adapter fallback to a fresh token.

## Donor mechanisms / primary-source observations

### AWS EC2 idempotency
Official EC2 documentation states that retrying a successful request with the same client token and same parameters succeeds without further action, while the same token with changed parameters produces `IdempotentParameterMismatch`; scope may be regional or zonal depending on the API.

Source: https://docs.aws.amazon.com/ec2/latest/devguide/ec2-api-idempotency.html

Reusable mechanism: bind retry authorization to the exact token + exact request parameters + documented provider scope, and treat mismatch as fail-closed evidence rather than token-rotation permission.

### AWS Auto Scaling LaunchInstances
The API documents `IdempotentCallInProgress` for a request already processing with the same client token and directs clients to retry with the same token. The service's synchronous-provisioning documentation also gives a finite 8-hour client-token lifetime for that API; after that window, reuse can initiate a new launch.

Sources:
- https://docs.aws.amazon.com/autoscaling/ec2/APIReference/API_LaunchInstances.html
- https://docs.aws.amazon.com/autoscaling/ec2/userguide/launching-instances-synchronous-provisioning.html

Reusable mechanism: `PENDING/in-progress` is distinct from failure; provider-specific retention is part of retry safety and expiry must remove automatic resend authority.

### Google long-running operations
Google Cloud operation APIs expose read-only `GetOperation`-style status retrieval for an already known operation ID.

Source: https://docs.cloud.google.com/storage/docs/json_api/v1/operations/get

Reusable mechanism: separate read-only outcome polling authority from resend authority and require an already-bound operation identity.

### IETF Idempotency-Key draft
The HTTPAPI working-group draft specifies an Idempotency-Key header for fault-tolerant non-idempotent requests and leaves server/resource policy—including key lifecycle—to the resource implementation.

Source: https://datatracker.ietf.org/doc/draft-ietf-httpapi-idempotency-key-header/

Reusable mechanism: an idempotency-key field alone is not proof of infinite replay safety; concrete resource semantics and expiry belong in provider capability evidence.

## RED-first regression matrix

Freeze at least the following groups before production implementation (72 total cases across parameterizations):

### A. Identity immutability
1. retry uses exact original provider token;
2. changed token rejected;
3. changed payload rejected;
4. changed hidden/default parameter rejected;
5. changed endpoint/scope rejected;
6. changed region/zone/cluster rejected;
7. changed account/tenant credential scope rejected;
8. adapter normalization drift rejected.

### B. Authority separation
9. ordinary SEND lease cannot be used as retry authorization after `SEND_STARTED`;
10. retry authorization cannot mint a new token;
11. retry authorization cannot change payload;
12. read-only oracle authority cannot call SEND surface;
13. retry authorization cannot activate a new effect class;
14. terminal outcome prevents retry mint;
15. lease expiry alone does not produce retry authority;
16. worker death alone does not produce fresh SEND authority.

### C. Capability and retention
17. pinned capability permits same-token retry -> eligible;
18. pinned capability forbids -> denied even if latest permits;
19. latest revocation removes permission;
20. retention inside proven horizon -> eligible;
21. retention expired -> resend denied;
22. retention unknown -> denied;
23. token-scope ambiguity -> denied;
24. provider drift challenge -> denied/fail closed.

### D. Provider responses
25. cached/same-token success resolves outcome;
26. idempotent-parameter mismatch -> no new token;
27. in-progress -> remains bounded recovery/PENDING;
28. provider timeout -> UNKNOWN;
29. malformed response -> UNKNOWN;
30. final failure match handled without new effect;
31. provider returns different resource identity -> conflict;
32. stale operation-status data does not become terminal proof.

### E. Oracle separation
33. bound operation ID may be polled read-only;
34. missing operation ID cannot be invented;
35. `NOT_FOUND` weak negative remains weak;
36. strong negative requires all frozen predicates;
37. oracle unavailable -> no resend escalation;
38. oracle result conflict -> unresolved;
39. oracle capability expiry -> manual path;
40. read call with hidden mutation semantics is rejected as oracle.

### F. Crash ordering
41. crash before recovery claim -> no started retry record;
42. crash after claim but before `RETRY_STARTED` -> recover claim safely;
43. crash after `RETRY_STARTED` before provider call -> conservatively UNKNOWN same identity;
44. crash during provider call -> UNKNOWN same identity;
45. crash after provider success before outcome commit -> reconcile same identity;
46. crash after outcome commit -> no further retry;
47. repeated crashes produce repeated contacts only for identical token/payload;
48. restart never rewrites `SEND_STARTED`/`RETRY_STARTED` history.

### G. Concurrency / stale workers
49. two workers cannot hold active recovery claim simultaneously;
50. stale authorization rejected after newer claim;
51. terminal outcome racing retry start blocks provider call if observed before I/O;
52. quarantine racing retry start blocks not-yet-started call;
53. quarantine after possible provider contact preserves UNKNOWN;
54. expired retry window checked again immediately before I/O;
55. copied retry token cannot bypass principal/audience binding;
56. restart reconstructs active recovery claim deterministically.

### H. Cross-epoch / namespace / provenance
57. retry remains in original trust epoch;
58. retry remains in original effect namespace;
59. post-reroot epoch cannot absorb old UNKNOWN as fresh MISS;
60. global provenance parent mismatch fail-closes;
61. rollback to older authority generation fail-closes;
62. missing original request-binding record fail-closes;
63. corrupted provider-token evidence fail-closes;
64. locally valid but globally orphan recovery record fail-closes.

### I. New-attempt boundary
65. manual `NOT_COMMITTED` verdict does not itself authorize retry;
66. historical UNKNOWN key remains consumed;
67. expired token cannot be replaced by fresh token under recovery path;
68. new business attempt requires new operation/effect authorization;
69. new business attempt cannot reuse old provider token unless separately proven and explicitly modeled (default deny);
70. automatic scheduler cannot transform UNKNOWN into new attempt;
71. operator UI exposes no hidden resend action;
72. re-admission after quarantine restores only policy eligibility, never historical retry horizon.

## Implementation boundary

Do not implement production retry/resume code before executable RED coverage exists on the real LAB-093/LAB-090..100 composition. The first implementation slice should be verifier/state-machine tests that prove a retry authorization cannot produce a provider identity different from the one durably pinned before the original `SEND_STARTED`.

## Decision

Freeze V1 with the following safety rule:

> Recovery after `SEND_STARTED` is evidence-preserving continuation of one already-created provider identity. It is never another opportunity to mint effect authority.

A system unable to reproduce and prove that exact identity must choose read-only reconciliation or manual reconciliation, not a new SEND.