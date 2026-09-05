# Epoch-aware client/API negotiation and external cutover adapter V1

Status: **FROZEN DESIGN / RED-FIRST CONTRACT**  
Date: 2026-09-05  
Primary follow-up: LAB-093 / #178  
Prerequisite design: `POST_REROOT_TRUST_EPOCH_EFFECT_NAMESPACE_MIGRATION_V1_FROZEN`

## Why this contract exists

The post-re-root migration contract intentionally permits no automatic reinterpretation of an old application idempotency key after historical non-reuse evidence becomes irrecoverable. The old effect namespace remains permanently sealed. If a human owner later authorizes resumption, runtime mechanics must still prevent two additional classes of ambiguity:

1. **client ambiguity** — an old or stale caller that knows only the pre-discontinuity API must not silently send a mutation into a newly created trust/effect epoch;
2. **external-provider ambiguity** — a provider adapter must not map a new-epoch request onto the same external idempotency/request identity as an old-epoch request.

A fresh internal `trust_epoch_id` is therefore necessary but not sufficient. The epoch must be explicit on the wire, explicitly acknowledged by the caller, included in the canonical operation identity, and preserved by the external adapter all the way to the provider's real deduplication namespace.

This document defines mechanics and RED-first tests only. **It does not authorize a production cutover.** The owner-level product/security authorization frozen by the preceding post-re-root contract remains mandatory.

## External evidence / donors

### IETF HTTPAPI Idempotency-Key draft

The latest archived HTTPAPI draft (`draft-ietf-httpapi-idempotency-key-header-07`, 2025-10-15; expired 2026-04-18) states the central semantic needed here: an idempotency key identifies retries of one request, must be unique, and must not be reused for a different payload. The draft is expired and therefore treated as a design donor rather than normative standards authority.

- https://datatracker.ietf.org/doc/draft-ietf-httpapi-idempotency-key-header/
- https://datatracker.ietf.org/doc/html/draft-ietf-httpapi-idempotency-key-header-07

### AWS idempotency behavior

AWS EBS documents the useful operational property that a retry with the same client token and same parameters returns the original result, while the same token with changed parameters conflicts. AWS Cloud Control likewise recommends a unique client token for mutating requests so retries can be disambiguated.

- https://docs.aws.amazon.com/ebs/latest/userguide/ebs-direct-api-idempotency.html
- https://docs.aws.amazon.com/cloudcontrolapi/latest/userguide/resource-operations.html

These are mechanism donors, not evidence that every provider has the same retention, scoping, normalization, or collision behavior.

## Non-negotiable invariants

### I1 — old namespace is never silently inherited

After a trust discontinuity, a request that omits epoch-aware fields is not mapped to the new epoch. It fails before application-idempotency lookup, provider request allocation, provider call, or durable effect mutation.

### I2 — client acknowledgement is exact, not advisory

Every mutating request in a post-discontinuity epoch carries and is checked against all of:

- `wire_version`;
- `trust_epoch_id`;
- `effect_namespace_id`;
- `application_key`;
- canonical `operation_digest` (or fields from which it is deterministically recomputed);
- an explicit `epoch_ack` bound to the same `(wire_version, trust_epoch_id, effect_namespace_id)`.

A stale epoch, missing acknowledgement, unknown version, or namespace mismatch fails closed.

### I3 — epoch participates in canonical identity

The canonical identity for every new externally consequential operation includes at least:

`protocol-domain || wire_version || trust_epoch_id || effect_namespace_id || principal_scope || effect_class || application_key || canonical_payload_digest`

Changing any authority-relevant field changes the canonical operation identity.

### I4 — provider request identity must preserve epoch separation

The adapter must prove that two canonical operations from different effect namespaces cannot be accidentally represented as the same provider idempotency/request identity under the provider's actual rules.

The proof must cover the provider's real behavior, including where applicable:

- maximum token length;
- accepted character set;
- case folding;
- Unicode or whitespace normalization;
- truncation;
- tenant/account/resource scoping;
- server-side token generation or rewriting;
- token retention/expiry;
- retry/result semantics;
- whether an outcome can be queried independently after an ambiguous timeout.

An adapter may not infer safety merely because the pre-normalized local strings are different.

### I5 — unsupported provider separation blocks the effect class

If the provider cannot preserve a safe epoch-aware request namespace, or the adapter cannot prove that it does, the corresponding effect class remains non-activatable after the discontinuity.

No fallback strips the epoch, hashes it away without collision control, reuses a legacy request ID format, or relies on timestamps.

### I6 — retries are pinned to the original epoch

A retry is always a retry of the epoch in which its application-idempotency record was first bound. A retry received after cutover does not get upgraded to the current epoch.

If its original epoch is sealed/incomplete, the retry returns a stable fail-closed outcome; it does not become a fresh request in the new namespace.

### I7 — provider UNKNOWN does not cross epochs

An operation with provider outcome `UNKNOWN` remains bound to its original provider request identity and epoch until reconciled or permanently failed closed under the existing UNKNOWN protocol. A cutover cannot turn an unresolved old request into a new provider call.

### I8 — wire negotiation never grants authority

Negotiation can reveal supported wire versions/current epoch metadata and can produce a challenge/acknowledgement token, but it cannot create cutover authorization, activate an effect namespace, or mutate provider state.

## Wire model V1

The V1 API surface has two conceptual operations.

### 1. Read-only negotiation

`GET/NEGOTIATE_EFFECT_CAPABILITY(effect_class, principal_scope)` returns an authenticated or server-origin-bound descriptor:

```text
EffectCapabilityV1 {
  wire_version = 1
  trust_epoch_id
  effect_namespace_id
  effect_class
  principal_scope
  epoch_status               # ACTIVE | SEALED | MIGRATION_PENDING | BLOCKED
  adapter_capability_digest
  discontinuity_generation
  epoch_ack_challenge
  challenge_expiry_or_sequence
}
```

The descriptor is informational/capability-negotiation state. It is not itself a mutation permit.

`epoch_ack_challenge` must be non-replayable across a different epoch/namespace/principal/effect class. If session-bound authentication exists, the challenge is bound to that authenticated session/principal. If no session binding exists, the server still verifies exact descriptor identity and one-way freshness before accepting the acknowledgement.

### 2. Mutating request

```text
EffectRequestV1 {
  wire_version = 1
  trust_epoch_id
  effect_namespace_id
  effect_class
  principal_scope
  application_key
  canonical_payload
  epoch_ack {
    challenge
    acknowledged_trust_epoch_id
    acknowledged_effect_namespace_id
    acknowledged_wire_version
  }
}
```

Server processing order is fixed:

1. authenticate caller/session;
2. parse and validate `wire_version` without mutation;
3. verify exact principal/effect scope;
4. verify epoch + namespace are currently valid for this request path;
5. verify explicit epoch acknowledgement;
6. compute canonical payload/operation digest;
7. perform application-idempotency lookup in the specified epoch/namespace;
8. if existing, follow existing retry/result/UNKNOWN path without allocating a new provider identity;
9. if new, require ACTIVE cutover + current adapter capability evidence;
10. reserve durable application/effect identity;
11. deterministically allocate and persist provider request identity;
12. only then permit provider execution under the existing request/effect state machine.

No step after (4) may silently substitute the server's current epoch for the client-supplied epoch.

## Legacy and mixed-client behavior

### Pre-discontinuity genesis compatibility

A deployment may retain an explicitly versioned genesis compatibility mode only while there has never been a trust discontinuity for that effect namespace. This compatibility is a declared policy, not an implicit default.

### After the first discontinuity

For that principal/effect scope:

- missing `wire_version` -> `EPOCH_NEGOTIATION_REQUIRED`;
- unsupported `wire_version` -> `WIRE_VERSION_UNSUPPORTED`;
- missing epoch fields -> `EPOCH_NEGOTIATION_REQUIRED`;
- stale `trust_epoch_id` -> `STALE_TRUST_EPOCH`;
- stale/wrong `effect_namespace_id` -> `STALE_EFFECT_NAMESPACE`;
- absent/mismatched acknowledgement -> `EPOCH_ACK_REQUIRED` / `EPOCH_ACK_MISMATCH`;
- a request that previously existed in an older epoch remains routed only to that old idempotency record and never auto-cloned to the new epoch.

HTTP status mapping, gRPC code mapping, CLI presentation, and localization are product-surface concerns. The semantic error identities above are the frozen contract; transport-specific numeric codes are deliberately not frozen here.

## Canonical provider request identity

V1 defines a canonical preimage, not a provider-specific final string:

```text
ProviderRequestPreimageV1 = CANONICAL_ENCODE({
  domain: "YTIM_EFFECT_PROVIDER_REQUEST_V1",
  trust_epoch_id,
  effect_namespace_id,
  principal_scope,
  effect_class,
  application_key,
  canonical_operation_digest
})
```

The adapter maps this preimage to a provider token using an audited encoding declared in its capability record.

### Adapter mapping requirements

The mapping is accepted only if all are true:

1. deterministic for the same canonical operation;
2. stable across restart and adapter process replacement;
3. includes epoch/namespace separation in the provider-observed identity;
4. respects provider length/charset rules without undocumented truncation or normalization;
5. collision-checked against the durable local provider-request registry before the first external call;
6. bound to the exact adapter capability version/digest that produced it;
7. never recomputed under a new adapter version for an already-bound operation.

If a digest/compact encoding is needed because the provider token is short, the durable registry must store both canonical preimage digest and final provider token and enforce a UNIQUE mapping. A local mapping collision fails closed before provider I/O. This does not convert probabilistic hash uniqueness into a proof about arbitrary external provider behavior; it merely ensures the runtime never knowingly aliases two canonical operations to one local provider token.

## Adapter capability attestation

Each effect adapter has a construction-bound immutable capability record:

```text
ExternalCutoverAdapterCapabilityV1 {
  adapter_type_id
  adapter_version
  provider_id
  account_or_tenant_scope
  effect_class
  token_scope_model
  token_max_length
  token_charset_or_encoding
  normalization_model
  retention_model
  same_token_same_payload_behavior
  same_token_different_payload_behavior
  outcome_query_model
  timeout_unknown_model
  epoch_domain_separation_method
  conformance_evidence_digest
  capability_policy_version
}
```

The authenticated digest of this record is included in the cutover evidence and active epoch descriptor.

Runtime accepts a provider call only when the exact capability digest is currently authorized for `(trust_epoch_id, effect_namespace_id, effect_class, provider_id, account_scope)`.

A mutable arbitrary caller-supplied adapter cannot self-attest its way into authority. This composes with LAB-093 and LAB-100: trusted implementation/capability authority is construction-bound and globally provenance-linked.

## Provider retention and UNKNOWN boundary

Token-domain separation alone is insufficient if provider deduplication expires before the runtime can safely close an ambiguous request.

For each adapter/effect class, one of these must be proven:

### Model A — provider idempotency covers the entire runtime retry horizon

The provider guarantees same-token deduplication/result semantics for at least the maximum period during which the runtime may resend an unresolved operation.

### Model B — independently queryable authoritative outcome

After an ambiguous timeout, runtime can query authoritative provider state by an immutable provider operation identity and converge without resubmitting a potentially duplicated side effect after token expiry.

### Model C — no safe ambiguity recovery

If neither A nor B is true, an ambiguous timeout transitions to a permanent fail-closed/manual-reconciliation state before the provider idempotency window can expire. Runtime does **not** retry after the safe window.

A provider with unknown/undocumented token expiry is Model C unless stronger evidence exists.

## Cutover activation gate

A post-discontinuity effect namespace may become mechanically `ACTIVE` only if all earlier owner/security authorization requirements are already satisfied **and** the runtime verifies:

1. new trust/effect epoch provenance is committed;
2. old namespace is permanently sealed;
3. wire V1 or a later explicitly compatible epoch-aware protocol is enabled;
4. legacy defaulting is disabled for the affected scope;
5. adapter capability evidence is authenticated and current;
6. provider request-ID domain separation passes conformance tests;
7. token retention/UNKNOWN model has a safe policy;
8. durable provider-request registry is empty/consistent for the new namespace and rejects cross-epoch aliasing;
9. a synthetic no-side-effect conformance probe or provider-supported dry-run verifies normalization/scoping assumptions where possible;
10. a fresh startup/recovery verification cycle passes.

Failure of any gate means `BLOCKED`, not degraded activation.

## Rollback and replay semantics

- An ACTIVE new epoch never makes the old sealed epoch ACTIVE again.
- Restoring an older config snapshot cannot restore legacy-default behavior.
- Replaying an old negotiation descriptor or acknowledgement against a new epoch fails exact identity/freshness checks.
- Replaying a new-epoch request into an old server fails unknown-version/epoch verification before mutation.
- Replaying an old provider request token into the new adapter path is rejected because no new-epoch durable registry binding exists for that canonical operation.
- Adapter downgrade is a provenance/policy transition and cannot silently reinterpret existing provider tokens.

## Crash ordering

### New request

Durable order:

`EPOCH_VERIFIED -> APPLICATION_KEY_BOUND -> PROVIDER_REQUEST_ID_BOUND -> PROVIDER_CALL_ALLOWED`

If the process crashes before `PROVIDER_REQUEST_ID_BOUND`, restart may deterministically complete allocation but must first revalidate the same epoch and adapter capability.

If it crashes after `PROVIDER_REQUEST_ID_BOUND`, restart reuses the exact persisted provider ID; it never generates a new-format token because an adapter version changed.

### Cutover

Cutover ordering remains inherited from the post-re-root contract:

`PROPOSED -> SECURITY_AUTHORIZED -> CUTOVER_PREPARED -> EXTERNAL_CUTOVER_ANCHORED -> PROVENANCE_COMMITTED -> VERIFIED -> ACTIVE`

Wire/adapter readiness is part of `VERIFIED`; it cannot be postponed until after ACTIVE.

## RED-first regression matrix

Minimum V1 matrix: **64 cases**.

### A. Wire/version negotiation (10)

1. legacy request accepted only in explicitly permitted pre-discontinuity genesis mode;
2. missing version after discontinuity fails before idempotency lookup;
3. unknown future version fails closed;
4. stale trust epoch fails;
5. stale effect namespace fails;
6. current epoch + wrong namespace fails;
7. current namespace + wrong principal scope fails;
8. current namespace + wrong effect class fails;
9. server restart preserves discontinuity/legacy-disable state;
10. rollback of config cannot re-enable implicit legacy defaulting.

### B. Epoch acknowledgement (8)

11. valid exact acknowledgement succeeds to lookup stage;
12. no acknowledgement fails;
13. acknowledgement for prior epoch fails;
14. acknowledgement for another namespace fails;
15. acknowledgement for another principal fails;
16. replayed expired/consumed challenge fails under the chosen freshness model;
17. session-bound acknowledgement reused by another authenticated principal fails;
18. acknowledgement verifies no mutation authority by itself.

### C. Application idempotency across epochs (10)

19. same application key retry in same epoch converges;
20. same key + changed payload in same epoch conflicts;
21. old-epoch key after cutover resolves only against old registry;
22. old sealed/incomplete key never becomes new-epoch MISS;
23. client cannot omit epoch to force current-epoch interpretation;
24. unresolved old UNKNOWN cannot be cloned to new epoch;
25. completed old result can be returned/read without opening new effect;
26. namespace sealing survives restart;
27. namespace sealing survives config rollback;
28. cross-principal same application key remains scope-separated.

### D. Provider request-ID mapping (12)

29. same canonical operation maps identically across restart;
30. different trust epochs map to distinct provider identities;
31. different effect namespaces map distinctly;
32. different principals map distinctly when provider scope requires it;
33. different effect classes map distinctly;
34. provider case-folding is modeled or blocks activation;
35. provider truncation is modeled and collision-checked or blocks activation;
36. illegal-character normalization is modeled or blocks activation;
37. final-token collision in durable registry fails before provider I/O;
38. adapter upgrade does not remap an existing bound request;
39. missing adapter capability digest fails before provider I/O;
40. stale/downgraded capability record fails.

### E. Provider scope/retention/UNKNOWN (10)

41. tenant-scoped token rule is included in identity/capability evidence;
42. account change cannot reuse an existing mapping without explicit migration;
43. documented safe retention supports bounded retry;
44. expired retention + queryable outcome uses lookup, not duplicate send;
45. expired retention + no outcome query becomes fail-closed/manual;
46. undocumented retention defaults to conservative Model C;
47. timeout before provider acceptance is handled without cross-epoch retry;
48. timeout after provider commit/UNKNOWN remains pinned to exact token;
49. restart during UNKNOWN reuses exact persisted token/capability;
50. new cutover cannot activate while old UNKNOWN would require unsafe replay.

### F. Mixed clients / rollout (6)

51. old and new clients may coexist only where old scope has not crossed a discontinuity;
52. after discontinuity old client gets negotiation-required, never silent upgrade;
53. new client stale cache gets stale-epoch response and must renegotiate;
54. retry library that strips unknown fields is detected/fails;
55. intermediary that normalizes provider token unexpectedly is detected by conformance evidence or blocks activation;
56. canary/read-only negotiation cannot perform effects.

### G. Cutover/replay/crash (8)

57. crash before provider-ID bind creates no provider call;
58. crash after provider-ID bind reuses exact token;
59. crash during VERIFIED does not imply ACTIVE;
60. rollback to pre-ACTIVE snapshot cannot reopen old namespace;
61. replay old acknowledgement after new epoch fails;
62. adapter without epoch separation permanently blocks that effect class;
63. successful conformance does not authorize owner-level production cutover;
64. full startup/recovery verification is required after activation provenance commit.

## Implementation consequences for LAB-093/LAB-100

When exact executable source is available, implement tests first around a least-capability broker surface rather than adding epoch fields piecemeal to provider calls.

Likely components:

- immutable `EffectEpochIdentity` value object;
- epoch-aware request parser/validator;
- negotiation descriptor/challenge issuer;
- durable application-idempotency registry keyed by epoch namespace;
- durable provider-request registry binding canonical preimage -> final provider token -> adapter capability digest;
- construction-bound `ExternalCutoverAdapterCapability`;
- adapter conformance verifier;
- activation verifier that refuses effect-class activation when any separation/retention property is unknown.

Do not implement production activation before owner authorization exists for the exact discontinuity/cutover payload.

## Audit / negative findings

1. **Do not treat `Idempotency-Key` as a universal guarantee.** The IETF draft is expired and, even while active, leaves validity/expiry policy to the resource; provider-specific semantics still require evidence.
2. **Do not use timestamps as epoch separators.** They do not prove uniqueness or continuity and are vulnerable to clock/coincidence ambiguity.
3. **Do not rely on local prefixing alone.** If a provider truncates, case-folds, normalizes, or scopes tokens differently, distinct local strings can collapse externally.
4. **Do not auto-upgrade legacy callers.** This would make a retry after trust discontinuity indistinguishable from consent to a new effect namespace.
5. **Do not regenerate provider IDs on retry after adapter upgrades.** Persist the exact provider identity before I/O.
6. **Do not infer safe retry from idempotency support without retention/outcome semantics.** UNKNOWN after expiry can otherwise become a duplicate side effect.
7. **Do not let negotiation become authorization.** It is a compatibility and explicit-ack gate only.

## Frozen verdict

`EPOCH_AWARE_CLIENT_API_NEGOTIATION_EXTERNAL_CUTOVER_ADAPTER_V1_FROZEN`

After a trust discontinuity, mutation semantics are opt-in to an explicit epoch on both sides of the broker boundary:

- the **client** must name and acknowledge the exact trust/effect epoch;
- the **runtime** must bind that epoch into canonical application/effect identity and durable retry state;
- the **adapter** must prove the epoch remains separated in the provider's real request/idempotency namespace, including normalization, scope, retention, and UNKNOWN behavior;
- if any layer cannot preserve that separation, the affected effect class remains blocked.

No part of this contract authorizes a real post-re-root production cutover.