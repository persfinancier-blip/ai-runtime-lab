# Effective-authority lease issuance / one-shot consumption / crash-replay contract V1

Date: 2026-09-05
Status: **FROZEN DESIGN — RED-first; no production behavioral PASS claimed**
Parent: LAB-093 / #178
Depends on: LAB-087, LAB-090..100 frozen authority/provenance/provider/UNKNOWN contracts
Verdict: `EFFECTIVE_AUTHORITY_LEASE_ONE_SHOT_CRASH_REPLAY_V1_FROZEN`

## 1. Problem

The authority-dependency manifest contract proves which consequential surfaces exist and requires a current effective-authority gate at each adapter-side sink. That is not sufficient by itself.

A worker can pass an authority check and then race with quarantine/revocation before provider I/O. A copied or stale authorization object can be replayed by another process. A process can crash after consuming local authority but before the provider call, or after the provider accepted the call but before local durable acknowledgement. A timeout can leave outcome `UNKNOWN`. If issuance or retry semantics mint fresh effect authority merely because the prior lease is expired/consumed, the runtime can duplicate a consequential external effect while every individual authorization check appears locally valid.

The missing contract is therefore the lifetime and consumption semantics of `EffectiveAuthorityLeaseV1`.

## 2. Security/correctness objective

A consequential provider action is permitted only when all of the following are simultaneously true:

1. the exact operation/effect identity already exists durably;
2. the requested surface is present in the authenticated authority manifest;
3. current effective authority admits that exact effect class/provider/scope;
4. a lease issuer signs/binds a lease to the exact operation, effect, surface, provider and authority generations;
5. the adapter verifies that lease immediately before the consequential I/O;
6. the lease has not been replayed, transferred, superseded, expired, quarantined or consumed for another attempt;
7. durable attempt state determines what a crash/retry may do next;
8. timeout/uncertainty enters the existing UNKNOWN reconciliation flow rather than minting fresh effect authority.

The core rule is:

> **A new lease is never evidence that an old effect attempt did not occur.**

Lease expiry, process death, lost acknowledgement, authority-generation change, or a fresh worker do not reset application/provider idempotency history.

## 3. Authority split

### 3.1 Lease issuer

The issuer may create a signed `EffectiveAuthorityLeaseV1` only after reading authenticated current state. It does **not** possess provider SEND/MUTATE authority merely by being able to issue leases.

Issuer inputs must include:

- `operation_id`
- `application_idempotency_key_digest`
- `effect_id`
- `effect_class`
- `attempt_id`
- `surface_id`
- `manifest_generation_id`
- `effective_authority_generation_id`
- `quarantine_generation_id`
- `trust_epoch_id`
- `effect_namespace_id`
- `provider_capability_generation_id`
- provider/service/operation/API identity
- account/tenant/region/scope identity
- canonical payload fingerprint
- pinned provider request/idempotency identity, when already assigned
- worker/process principal identity
- issuance time and expiration bound
- one-shot `lease_id` / anti-replay nonce
- parent provenance head/digest

The issuer must fail closed if any required generation or dependency is unknown, stale, challenged, quarantined, expired or not globally provenance-linked.

### 3.2 Adapter

The adapter is the final enforcement point. It must not accept a caller-supplied boolean such as `authorized=True` or a generic reusable bearer credential as proof of effect authority.

Immediately before provider-capable I/O, the adapter verifies:

- lease signature/authenticity;
- schema/domain/version;
- exact surface and provider operation;
- exact operation/effect/attempt/payload identity;
- provider/account/region/scope binding;
- manifest/effective-authority/quarantine/trust/provider-capability generations;
- worker/principal binding if the transport permits it;
- expiry/not-before;
- anti-replay/consumption state;
- current quarantine/revocation state.

A lease valid for one provider operation is not valid for status, cancel, refund, resume, another account, another region, another payload, or another effect class unless those are separately and explicitly represented as authority surfaces.

## 4. Lease form

`EffectiveAuthorityLeaseV1` is an authenticated, domain-separated object. Canonical encoding follows the repository's frozen V1 canonical provenance rules rather than defining a second encoding.

Recommended conceptual fields:

```text
schema = "EffectiveAuthorityLeaseV1"
lease_id
issuer_id
subject_principal_id
operation_id
effect_id
attempt_id
application_key_digest
payload_digest
surface_id
effect_class
provider_identity
provider_scope
provider_request_identity
manifest_generation_id
effective_authority_generation_id
quarantine_generation_id
trust_epoch_id
effect_namespace_id
provider_capability_generation_id
issued_at
not_before
expires_at
parent_provenance_digest
signature
```

`lease_id` must be globally collision-resistant in its issuer domain. The signed payload must not contain mutable aliases or object references whose meaning can change after issuance.

## 5. One-shot semantics

### 5.1 One lease = one provider attempt authority

A lease authorizes at most one exact consequential attempt. A successful consumption cannot be reset to `AVAILABLE`.

A lease is not a reusable session token. Batch or stream effects require either distinct leases per consequential item or a separately specified bounded-use protocol with a durable monotonic sub-sequence; V1 permits only one-shot leases.

### 5.2 Anti-replay ledger

The broker retains a durable lease/attempt record, minimally:

```text
ISSUED
CLAIMED
SEND_STARTED
OUTCOME_KNOWN
UNKNOWN
TERMINAL
REVOKED_BEFORE_SEND
EXPIRED_BEFORE_SEND
```

Transitions are append-only/provenance-linked or transactionally represented with equivalent authenticated monotonic evidence. `lease_id` uniqueness and terminal consumption survive process restart.

A second process presenting the same lease after `CLAIMED` cannot independently send. It may only attach to/read the existing attempt state through an explicitly read-only path.

## 6. Atomicity boundary and the unavoidable external gap

There is no general atomic transaction spanning local durable storage and an arbitrary external provider. The contract must therefore not claim impossible exactly-once delivery.

The safe local ordering is:

1. durably create operation/effect/provider-request identity;
2. issue exact one-shot lease;
3. atomically claim lease for `attempt_id` with compare-and-set/current-generation checks;
4. immediately revalidate current authority/quarantine at the adapter boundary;
5. durably record `SEND_STARTED` **before** effect-capable provider I/O;
6. perform exactly one provider call using the already pinned provider request/idempotency identity;
7. durably record the observed provider result;
8. on timeout/connection loss/ambiguous response, record `UNKNOWN`; do not mint a new effect identity.

`SEND_STARTED` is deliberately conservative: after it is durable, a crash cannot prove that no network bytes/provider acceptance occurred.

## 7. Crash matrix

### 7.1 Crash before lease issuance

No lease exists. A later issuer may issue one only if current authority still admits the exact operation/effect.

### 7.2 Crash after `ISSUED`, before `CLAIMED`

The unused lease may be reclaimed only under an authenticated recovery rule that proves no claim/send began. Simpler and preferred V1 behavior: mark it expired/superseded and issue a new lease for the **same effect/attempt plan**, never a new effect identity. The old lease remains non-usable.

### 7.3 Crash after `CLAIMED`, before `SEND_STARTED`

If durable state proves `SEND_STARTED` was never committed, recovery may transition the old claim to a terminal pre-send state and issue replacement authority for the same operation/effect. This decision must be transactional and single-writer so two recovering processes cannot both continue.

### 7.4 Crash after `SEND_STARTED`, before provider invocation

The system cannot distinguish this from a crash milliseconds later unless the external transport itself provides stronger evidence. Because `SEND_STARTED` intentionally precedes I/O, recovery treats the attempt as potentially sent.

The next step is provider outcome lookup or safe same-provider-idempotency retry **only if** the frozen provider capability contract proves that such retry remains safe for this exact pinned request identity and horizon. Otherwise it enters `UNKNOWN`/manual reconciliation.

### 7.5 Crash during/after provider invocation, before local result commit

This is `UNKNOWN` by default. Lease consumption remains final. A new lease must not authorize a fresh effect. Reconciliation uses the existing provider token/operation identity.

### 7.6 Crash after known result commit

Recovery replays only local completion bookkeeping/result delivery idempotently. No provider mutation authority is needed.

## 8. Timeout and UNKNOWN

A timeout does not produce `FAILED_TO_SEND`; it produces `UNKNOWN` unless provider-specific evidence proves rejection before effect acceptance.

When an attempt is `UNKNOWN`:

- the application key stays consumed;
- the effect identity stays fixed;
- the original provider request/idempotency identity stays fixed;
- the original lease remains consumed;
- fresh effect leases are prohibited;
- read-only oracle reconciliation remains permitted;
- a same-token provider retry is permitted only by the pre-declared provider capability semantics and existing UNKNOWN contract;
- if the safe retry/query horizon expires, transition to manual reconciliation rather than create a new attempt authority.

A retry that is semantically the same provider request may use a **retry authorization object** distinct from `EffectiveAuthorityLeaseV1`, or a lease subtype explicitly incapable of changing provider request identity/payload. It cannot authorize a new request identity.

## 9. Revocation/quarantine race

### 9.1 Revocation before adapter final check

Lease fails. If no `SEND_STARTED`, it can terminate as `REVOKED_BEFORE_SEND`.

### 9.2 Revocation after final check but before network I/O

A pure check-then-use design has TOCTOU. V1 therefore requires the broker/adapter to couple lease claim and the last current-generation check as tightly as the runtime can support, and consequential provider code must not execute arbitrary caller code between final validation and transport invocation.

For strict deployments, provider I/O occurs only inside the trusted broker process that owns current authority state. Lower-trust workers submit value-only commands and cannot carry a lease directly to the provider.

### 9.3 Quarantine concurrent with an in-flight send

Quarantine prevents new sends/claims immediately but cannot pretend already-started I/O was cancelled. The in-flight attempt resolves through result/UNKNOWN reconciliation. Its provider token remains consumed/pinned.

## 10. Expiry and renewal

Short lease lifetime reduces replay/TOCTOU exposure but is not a correctness substitute for durable one-shot state.

Rules:

- expiration only removes future use of an unconsumed lease;
- expiration never proves no effect occurred;
- a consumed lease is permanently consumed even after expiration;
- renewal is issuance of a distinct lease ID after proving pre-send state or is prohibited;
- after `SEND_STARTED`, generic renewal is prohibited;
- clock rollback cannot revive an expired/consumed lease; use trusted monotonic/server time semantics where available and durable state as the primary anti-replay control.

## 11. Delegation and non-transferability

A lease should be bound to the broker/adapter principal or workload identity when that identity is cryptographically available. A lower-trust worker should ideally never receive the raw provider credential or a provider-usable lease.

If cross-process transfer is required, the recipient identity and exact transport audience are signed into the lease. Re-export to a different process/audience fails.

Proof-of-possession is preferred over a pure bearer lease when practical. A copied signed object alone must not be sufficient to authorize a different principal at a different adapter.

## 12. Provenance and generation changes

Every lease is pinned to the authority generations that justified issuance. A new manifest, quarantine, trust epoch or provider-capability generation does not mutate an old lease.

If a generation changes before claim/final check, old lease fails and may be superseded only according to pre-send rules. If generation changes after `SEND_STARTED`, the operation remains pinned to its original provider/effect identity and follows outcome reconciliation.

Rollback of local policy/configuration cannot resurrect a previously consumed/revoked lease because anti-replay history is part of the authenticated monotonic provenance/startup verification boundary.

## 13. Relationship to provider idempotency

Lease anti-replay and provider idempotency solve different problems:

- lease anti-replay prevents the runtime from authorizing multiple sends accidentally or through stale/copied capability;
- provider idempotency bounds duplicates when a send may have occurred but the response is unknown.

Neither substitutes for the other. A one-shot lease without provider idempotency can still leave an unresolvable timeout-after-send. Provider idempotency without one-shot authority can still permit multiple intentionally distinct request tokens/effects.

## 14. Donor mechanisms

### RFC 9449 — DPoP

Useful donor, not a direct implementation template. DPoP binds a proof to a request method/URI and uses a unique `jti`; RFC 9449 explicitly describes tracking `jti` values during the validity window to reject replay, and recommends short proof lifetimes. It also warns that a proof does not protect arbitrary request-body contents unless they are separately bound. LAB should therefore bind the canonical payload/effect identity explicitly, not copy DPoP's minimal HTTP binding.

Source: https://www.rfc-editor.org/rfc/rfc9449

### RFC 9396 — Rich Authorization Requests

Useful donor for fine-grained structured authorization rather than broad scopes. The LAB lease similarly binds exact action/resource/provider details and rejects unknown or malformed authorization detail types. LAB requires stricter immutable canonical semantics because it is also durable replay/crash evidence.

Source: https://www.rfc-editor.org/rfc/rfc9396

### IETF Transaction Tokens draft, July 2026 (`draft-ietf-oauth-transaction-tokens-11`)

Useful current donor for short-lived signed authorization/request context propagated through workload call chains and for retaining the initiating transaction identity. LAB's contract is stricter in one respect: a transaction-context token alone is not send authority; consequential I/O additionally requires durable one-shot consumption and provider-attempt state.

Source: https://datatracker.ietf.org/doc/draft-ietf-oauth-transaction-tokens/

### RFC 7523 — JWT assertion replay pattern

Useful older donor for `jti` plus validity-window replay tracking. LAB must not rely on in-memory `jti` caches alone because crash/restart and multiple workers are explicit threat cases; lease consumption is durable.

Source: https://www.rfc-editor.org/rfc/rfc7523

## 15. RED-first regression matrix

Freeze at least the following 72 cases before production implementation.

### A. Issuance / exact binding (12)

1. valid exact issuance;
2. wrong operation ID;
3. wrong effect ID;
4. wrong application-key digest;
5. wrong payload digest;
6. wrong surface;
7. wrong provider operation;
8. wrong account/tenant;
9. wrong region/scope;
10. wrong trust/effect namespace;
11. wrong manifest/effective-authority generation;
12. wrong provider-capability generation.

### B. Signature / identity / delegation (8)

13. invalid signature;
14. wrong issuer;
15. wrong subject principal;
16. wrong adapter audience;
17. copied bearer to second process;
18. altered expiry;
19. altered provider request identity;
20. cross-domain schema/type confusion.

### C. One-shot / concurrency (10)

21. first claim succeeds;
22. second same-process claim fails;
23. second-process simultaneous claim fails;
24. replay after successful provider response fails;
25. replay after UNKNOWN fails as fresh effect;
26. replay after restart fails;
27. duplicate lease ID with different body rejected;
28. two leases for one attempt cannot both become SEND_STARTED;
29. stale worker cannot claim after newer authority generation;
30. read-only observer cannot upgrade into claimant.

### D. Crash ordering (12)

31. crash before issue;
32. crash ISSUED/pre-CLAIMED;
33. crash post-CLAIMED/pre-SEND_STARTED;
34. crash immediately after SEND_STARTED;
35. crash before socket write after SEND_STARTED;
36. crash during write;
37. crash after provider acceptance/pre-response;
38. crash after response/pre-local commit;
39. crash after local outcome commit;
40. duplicate recovery workers;
41. restart with orphan staged lease;
42. restart with corrupted consumption record fails closed.

### E. Timeout / provider idempotency (10)

43. timeout before proven provider acceptance when provider offers explicit rejection evidence;
44. generic timeout -> UNKNOWN;
45. UNKNOWN exact same-token safe retry within proven horizon;
46. UNKNOWN retry with changed token rejected;
47. UNKNOWN retry with changed payload rejected;
48. retry after provider dedupe horizon without authoritative oracle rejected;
49. authoritative COMMITTED lookup -> no resend;
50. authoritative final failure handling;
51. weak NOT_FOUND does not permit resend;
52. manual reconciliation transition after horizon.

### F. Revocation / quarantine / expiry (10)

53. quarantine before issue;
54. quarantine after issue/pre-claim;
55. quarantine after claim/pre-SEND_STARTED;
56. quarantine after SEND_STARTED;
57. provider capability revoked before send;
58. manifest superseded before send;
59. expiry before claim;
60. expiry after claim/pre-send;
61. expiry after SEND_STARTED does not reset attempt;
62. clock rollback cannot revive lease.

### G. Composition / provenance / recovery (10)

63. parent provenance mismatch;
64. rollback to older lease ledger snapshot;
65. trust-epoch transition cannot reuse old lease;
66. effect-namespace migration cannot reuse old lease;
67. challenge/quarantine re-admission creates new authority generation, not old-lease revival;
68. manifest completeness failure blocks issuance;
69. dynamic unmanifested adapter blocks final check;
70. broker restart verifies anti-replay before accepting work;
71. read-only reconciliation works while SEND authority quarantined;
72. same historical operation remains pinned through restart/re-admission.

## 16. Implementation boundary

No production code should be added from this contract until exact executable source is available and RED tests can be demonstrated on the supported LAB-087/LAB-090..100 composition.

The minimum coherent implementation unit is not a helper JWT class. It is:

1. durable attempt/lease schema;
2. canonical signed lease;
3. single-writer claim/consumption transition;
4. adapter-side verification immediately before provider I/O;
5. UNKNOWN integration using the already pinned provider identity;
6. startup/provenance verification;
7. multi-process/crash regressions.

Anything less risks turning a signed token into security theatre while preserving the same TOCTOU/replay hole.

## 17. Frozen conclusions

1. `EffectiveAuthorityLeaseV1` is one-shot attempt authority, not a reusable access token.
2. It is exact-bound to operation/effect/attempt/payload/surface/provider/scope and every authority generation that justified issuance.
3. Consumption is durable and survives restart; a copied/stale lease cannot create another send.
4. `SEND_STARTED` is committed before provider I/O and conservatively marks the point after which absence of an effect is no longer locally provable.
5. Timeout/crash after `SEND_STARTED` enters UNKNOWN; a fresh effect lease is forbidden.
6. Provider idempotency/oracle semantics determine whether the same pinned provider request can be safely retried; lease expiry does not.
7. Quarantine/revocation prevents new authority but cannot erase an already-started external attempt.
8. Adapter-side verification is mandatory immediately before I/O; lower-trust workers should use value-only broker commands rather than hold raw provider authority.
9. Durable anti-replay and global provenance are required; in-memory nonce caches alone are insufficient.
10. The contract removes the manifest-to-I/O TOCTOU/replay gap without pretending arbitrary external providers support atomic exactly-once transactions.
