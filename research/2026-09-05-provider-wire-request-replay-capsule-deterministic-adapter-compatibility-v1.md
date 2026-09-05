# Provider wire-request replay capsule / deterministic adapter compatibility V1

Status: `PROVIDER_WIRE_REQUEST_REPLAY_CAPSULE_DETERMINISTIC_ADAPTER_COMPATIBILITY_V1_FROZEN`

Date: 2026-09-05

Scope: design-only fallback for LAB-093 while LAB-086 exact publication/execution remains blocked by the current runtime's lack of a supported byte-preserving predecessor+patch transform. This note creates no production implementation or behavioral PASS.

## Problem

The frozen retry-authority contract permits `SAME_IDENTITY_RETRY` only after durable `SEND_STARTED`, and only for the exact provider-side idempotency/request identity originally pinned before consequential I/O. That creates a second-order requirement: a future retry must not depend on re-running changed SDK serializers, default insertion, endpoint routing, token mapping, API-version selection, request signing, or credential-selection logic in a way that silently changes provider-visible semantics.

A naive answer is to persist the entire historical HTTP request and replay its bytes. That is unsafe or impossible for many providers because authentication material, timestamps, nonces, signatures, session credentials, content-length framing, TLS state, and SDK-generated transport headers are intentionally ephemeral. AWS Signature Version 4, for example, binds request authentication to a request timestamp and credential scope; old signed bytes are not the stable business identity that should be replayed indefinitely.

The opposite naive answer is to retain only the idempotency token and reconstruct everything else with the current adapter. That is also unsafe: provider idempotency often requires the same token *and* the same parameters/scope, and SDK/API upgrades can change defaults, serialization, endpoint selection, version headers, normalization, or implicit fields.

The required abstraction is therefore a **provider replay capsule** that freezes all *semantic/provider-identity-relevant* request material while explicitly excluding ephemeral transport/authentication material that must be freshly regenerated under a verified compatibility contract.

## Core invariant

After `SEND_STARTED`, a historical retry may refresh only transport/authentication material proven to be outside provider effect identity and idempotency comparison semantics.

Everything that can influence:

- provider-side operation identity;
- idempotency/deduplication identity;
- request parameters compared for mismatch;
- account/tenant/project ownership;
- region/zone/cluster/endpoint scope;
- API operation/version semantics;
- resource naming or destination;
- mutation payload;
- provider-generated routing that changes the target effect;

must be durably pinned before the original `SEND_STARTED` and reproduced or semantically re-materialized under an authenticated adapter-compatibility proof.

If the system cannot prove which fields are stable semantic identity versus refreshable transport/auth material, `SAME_IDENTITY_RETRY` is denied.

## Two-layer request model

### Layer A — stable replay capsule

`ProviderReplayCapsuleV1` contains the exact historical operation semantics. At minimum it binds:

- `operation_id`, `effect_id`, original `attempt_id`;
- provider/service/API operation identifier;
- exact API version / protocol version when provider semantics depend on it;
- canonical endpoint class and provider scope: account/tenant/project, region, zone, cluster, partition, sandbox/live mode, or equivalent;
- exact provider idempotency/client token bytes/string and token-construction generation;
- canonical semantic request payload or a lossless canonical representation sufficient to reproduce exactly the provider-compared parameters;
- digest of the canonical semantic payload;
- explicit defaults that were effective on the original request, including defaults normally inserted by SDK/server/client configuration when they can affect effect semantics;
- exact resource identifiers, destination identifiers, parent/container identifiers, and mutation mode;
- content type / request encoding / RPC method where these can change semantic interpretation;
- provider capability generation pinned to the original attempt;
- adapter mapping generation and serializer generation;
- endpoint-resolution generation / routing policy generation;
- any documented parameter normalization rules relevant to provider idempotency;
- trust epoch + effect namespace;
- parent global-provenance head;
- capsule schema/canonicalization version;
- digest/signature over the whole capsule.

The capsule is immutable after `SEND_STARTED`.

### Layer B — refreshable transport envelope

`ProviderTransportEnvelopeV1` is generated for a specific contact attempt from an accepted capsule. It may contain only material proven not to alter the underlying provider operation identity, such as:

- current authentication signature;
- current OAuth/access/session token;
- request timestamp/date;
- nonce required only for replay prevention/authentication;
- connection-level/TLS metadata;
- tracing headers;
- content length / transfer framing;
- hop-by-hop transport headers;
- retry-attempt telemetry;
- current DNS-resolved address when endpoint identity remains unchanged;
- refreshed credential proof for the *same provider account/principal scope* allowed by the original capsule.

Refreshing the transport envelope must never change the semantic request capsule.

## Why byte-for-byte replay is not the universal rule

Providers differ.

### Semantic same-token replay

AWS EC2 documents idempotency for supported operations using a client token. A retry with the same client token and same parameters succeeds without further action, while changed parameters can produce `IdempotentParameterMismatch`; scope may be regional or zonal depending on the operation.

For this class of provider, replay safety means preserving the exact token + parameter semantics + documented scope. Reusing an old HTTP Authorization header is unnecessary and often invalid.

### Ephemeral request authentication

AWS Signature Version 4 includes request date/time in the signed request and binds credential scope to date, region, and service. AWS S3 additionally documents a limited validity window for signed request reuse. This demonstrates that authentication bytes are deliberately time-bound and cannot be equated with stable business idempotency identity.

For this class, the correct replay operation is: regenerate a fresh valid signature over a request whose **semantic capsule is unchanged**, with the same provider account/service/region authority.

### Provider-managed idempotency windows

Stripe documents idempotent replays as scoped by idempotency key, API/account context, and a finite replay window (with version-specific behavior). This means replay compatibility must preserve API/account scope and respect retention; a textual key alone is insufficient.

### Read-only operation resources

Google long-running operations expose a separate `GetOperation`-style read surface for an already known operation resource. When such an operation ID is durably bound, outcome reconciliation can avoid mutating replay altogether; the replay capsule remains historical evidence while recovery uses least-capability read-only authority.

## Canonical semantic payload

The replay capsule MUST NOT rely on a hash of whatever current serializer emits.

Before original `SEND_STARTED`, the adapter must produce and durably persist a canonical semantic request representation whose meaning is defined by the adapter/provider capability generation.

Required properties:

1. explicit field presence versus omission is preserved when the provider distinguishes them;
2. null/empty/zero/default values are preserved distinctly when provider semantics distinguish them;
3. list order is preserved unless the provider contract proves order-insensitive semantics;
4. map/object ordering may be canonicalized only if provider semantics are order-insensitive;
5. numeric/string encodings preserve exact provider meaning;
6. binary data is preserved losslessly or by authenticated content-addressed reference;
7. server-generated defaults are not assumed unless provider documentation/evidence proves they are outside idempotency comparison and effect semantics;
8. SDK-inserted defaults that matter are materialized into the capsule before send;
9. endpoint path/query/RPC method components that change operation meaning are included;
10. secret-bearing semantic fields are handled through protected references without losing exact identity/verifiability.

The capsule digest is domain-separated from generic payload hashes.

## Secret and credential handling

The replay capsule must not become a warehouse of reusable secrets.

Classify request material into:

### Semantic secret

A secret whose value itself changes the requested effect (for example a destination secret value being installed/rotated). The exact semantic value may need durable protected storage or an authenticated sealed reference if retry must reproduce it. Redaction for human display must not alter the verifier-visible identity.

### Authentication credential

API keys, OAuth tokens, AWS secret/session credentials, signing keys, and equivalent request-authentication authority are **not** persisted as replay bytes merely to reproduce an old request. They are re-obtained from the current approved credential path and must resolve to an allowed same provider account/tenant/principal scope.

### Derived authentication artifact

Authorization headers, signatures, signed timestamps, presigned URLs, DPoP-like proofs, or nonces are transport-envelope material unless provider semantics explicitly treat them as request parameters. They are regenerated per contact.

A capsule that cannot separate semantic secret from authentication credential is not retry-safe until the adapter capability explicitly resolves the distinction.

## Credential rotation

Credential rotation must not change the provider-side business identity of the historical retry.

A retry using new credentials is allowed only when current credential authority is proven to act inside the exact provider account/tenant/project/scope pinned by the capsule and the provider capability contract proves credentials are not part of the idempotency identity.

Reject when rotation changes:

- account/tenant/project;
- sandbox/live mode;
- delegated principal scope where provider idempotency is principal-scoped;
- region/service partition;
- endpoint class;
- authorization context that changes resource visibility or request interpretation.

If provider idempotency is credential/principal scoped and the original principal can no longer be reproduced, retry is denied and recovery moves to read-only oracle/manual reconciliation.

## Adapter compatibility declaration

Every adapter generation that may replay historical capsules publishes an authenticated `ReplayCompatibilityDeclarationV1` containing at least:

- adapter/build digest;
- supported provider/service/API operation;
- accepted replay-capsule schema versions;
- accepted historical adapter/serializer/token-mapping generations;
- semantic fields that are replayed exactly;
- transport/auth fields permitted to refresh;
- endpoint-resolution constraints;
- credential-scope equivalence rule;
- API-version compatibility rule;
- serializer compatibility rule;
- provider idempotency scope/retention capability generation;
- downgrade/upgrade boundaries;
- conformance-test evidence identity;
- activation authority/global-provenance parent.

Compatibility is directional and explicit:

`adapter_new CAN replay capsule_old`

does not imply:

`adapter_old CAN replay capsule_new`.

Missing declaration means deny.

## Deterministic compatibility verifier

Before minting `EffectiveRetryAuthorizationV1`, the verifier checks:

1. capsule signature/digest/global provenance is valid;
2. original attempt reached `SEND_STARTED` and has no terminal outcome;
3. exact provider token/request identity is present;
4. pinned provider capability permits same-identity retry and retention has not expired;
5. current adapter has an authenticated compatibility declaration for the exact historical capsule generation;
6. semantic payload reconstruction from the capsule is deterministic and digest-identical;
7. current endpoint resolves to the same provider semantic scope;
8. current credential authority resolves to an allowed same provider account/principal scope;
9. only declared transport/auth fields differ;
10. API version/default/serializer behavior cannot add, remove, reinterpret, or reorder semantic parameters outside the frozen equivalence rules;
11. current quarantine/revocation state does not deny the effect class;
12. no unresolved provider-capability or adapter-compatibility challenge exists.

Any unknown predicate denies retry.

## SDK and serializer upgrades

Historical retries MUST NOT simply invoke the latest high-level SDK method with old application arguments.

An SDK upgrade can legitimately change:

- default values;
- omitted-field behavior;
- API version/header negotiation;
- endpoint discovery;
- enum/string normalization;
- list/map serialization;
- retry middleware;
- token auto-generation;
- content encoding;
- region/partition resolution;
- request signing inputs;
- hidden user-agent or feature flags that alter server behavior.

Therefore an adapter replay path must either:

1. materialize the provider request from the frozen semantic capsule through a compatibility-proved deterministic serializer; or
2. use a provider-native operation API where documented semantics guarantee equivalence from the frozen parameter set; or
3. deny mutation replay and use read-only/manual reconciliation.

A mere semantic-version range such as `sdk >= X` is not evidence of replay compatibility.

## Endpoint and routing drift

Endpoint resolution is authority-relevant whenever changing endpoint can alter account, region, zone, partition, sandbox/live environment, storage plane, or idempotency scope.

The capsule binds a semantic endpoint identity, not necessarily one IP address.

Allowed refresh examples:

- DNS address changes for the same authenticated hostname/service scope;
- provider-documented regional failover only if the idempotency contract proves cross-endpoint identity preservation;
- TLS certificate rotation under the same authenticated service identity.

Rejected without explicit proof:

- region migration;
- sandbox -> production;
- account-specific endpoint change;
- zonal -> regional change when idempotency scope differs;
- API hostname/version change that can alter request semantics;
- fallback to a generic endpoint whose provider identity mapping is unknown.

## Signed timestamps, nonces, and anti-replay headers

A provider may require each HTTP contact to carry a fresh timestamp, nonce, or signature to reject network-level replay. These fields are refreshed in the transport envelope **only when** the provider contract proves they authenticate the same semantic request and do not become part of the provider business idempotency comparison.

The adapter computes a semantic digest before transport signing and proves after signing that:

`semantic_digest(before_signing) == semantic_digest(extracted_from_final_request)`.

This prevents signing middleware from silently adding/changing semantic query parameters or endpoint scope.

## Pre-send capture ordering

Before the first provider I/O:

1. resolve exact provider/service/API operation and semantic endpoint scope;
2. resolve account/tenant/project/region/zone identity;
3. generate/load provider idempotency token exactly once;
4. materialize explicit effective semantic parameters, including relevant defaults;
5. construct canonical `ProviderReplayCapsuleV1`;
6. persist capsule + digest + provider capability generation + adapter/serializer/token-mapping generations;
7. verify capsule durability/global provenance;
8. claim one-shot effective-authority lease;
9. durably append `SEND_STARTED` referencing the capsule identity;
10. generate a fresh transport envelope from the capsule;
11. immediately re-verify semantic digest/scope after final request construction;
12. perform provider I/O.

If the process crashes after step 9, the capsule is already sufficient to classify recovery without re-deriving historical semantics.

## Recovery ordering

For a historical `UNKNOWN` attempt:

1. load the immutable replay capsule;
2. verify global provenance and original pinned capability;
3. verify idempotency retention/scope still permits replay;
4. select a current adapter generation with an authenticated compatibility declaration;
5. reconstruct semantic request and require digest identity;
6. obtain current approved credentials and prove same allowed provider scope;
7. mint/claim `EffectiveRetryAuthorizationV1` bound to the capsule;
8. durably append `RETRY_STARTED` referencing the same capsule/provider identity;
9. generate only refreshable transport/auth fields;
10. re-verify final semantic digest/scope immediately before I/O;
11. send;
12. persist result/evidence or remain `UNKNOWN` on crash/timeout.

No step is allowed to mint a replacement provider idempotency token.

## Drift and challenge lifecycle

A discovered mismatch between declared and observed adapter behavior transitions the compatibility declaration to challenged/invalidated for affected operations.

Examples:

- serializer emits a new default;
- provider changes parameter comparison semantics;
- endpoint resolver changes region/partition behavior;
- SDK starts generating a token automatically despite supplied historical token;
- auth middleware signs/adds a semantic query parameter;
- API version upgrade changes omitted-field meaning;
- account-scoping behavior changes.

Challenge blocks new historical mutation replays using that declaration. It does not rewrite old capsules, `SEND_STARTED`, `RETRY_STARTED`, provider tokens, or outcomes.

## Provider classes that cannot support safe replay

Some operations may not expose a stable idempotency token or may incorporate unavoidable fresh nonce/timestamp/random server routing into effect identity. Some SDKs may not provide a way to suppress hidden token regeneration. Some providers may document no bounded same-request replay semantics.

For these classes, the adapter capability must state `MUTATION_REPLAY_UNSUPPORTED`.

Allowed recovery is then only:

- read-only operation/resource oracle using already-bound identifiers; or
- manual reconciliation.

The architecture must not invent synthetic replay guarantees where the provider does not supply them.

## Primary-source donor observations

### AWS EC2 idempotency
Official EC2 documentation states that retrying a supported operation with the same client token and same parameters succeeds without further action, while changed parameters can yield `IdempotentParameterMismatch`. Scope can be regional or zonal.

Source: https://docs.aws.amazon.com/ec2/latest/devguide/ec2-api-idempotency.html

Reusable mechanism: stable replay identity is token + semantic parameters + provider scope, not the old HTTP authorization bytes.

### AWS Signature Version 4
AWS documents that request signing includes request date/time and credential scope (date, region, service); S3 documents a bounded signed-request validity window. Signatures authenticate a request but are deliberately time-bound.

Sources:
- https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_sigv-signing-elements.html
- https://docs.aws.amazon.com/AmazonS3/latest/developerguide/sig-v4-authenticating-requests.html

Reusable mechanism: separate stable effect/idempotency semantics from refreshable transport authentication; re-sign the same semantic request rather than replaying stale authorization artifacts.

### Stripe idempotency
Stripe documents that idempotent replay depends on the same idempotency key plus API/account context and a finite retention window, with version-specific behavior.

Sources:
- https://docs.stripe.com/api-v2-overview
- https://docs.stripe.com/error-low-level

Reusable mechanism: API version/account scope and retention belong in replay compatibility evidence, not just the token string.

### Google long-running operations
Google Cloud long-running operations expose `GetOperation` to retrieve the latest state of an already-known operation resource.

Source: https://docs.cloud.google.com/run/docs/reference/rpc/google.longrunning

Reusable mechanism: when provider operation identity is available, prefer least-capability read-only reconciliation rather than mutation replay.

## RED-first regression matrix

Freeze at least 80 cases before production implementation.

### A. Capsule capture and identity
1. original token captured exactly once;
2. semantic payload digest stable;
3. omitted vs explicit null preserved;
4. zero/empty/default distinction preserved;
5. list order preserved where meaningful;
6. binary semantic content losslessly bound;
7. endpoint/service/API version bound;
8. account/region/zone/sandbox scope bound;
9. adapter/serializer/token-mapping generations bound;
10. capsule mutation after `SEND_STARTED` rejected.

### B. Transport/auth separation
11. fresh timestamp allowed when declared transport-only;
12. stale timestamp not required for retry;
13. fresh signature allowed over same semantics;
14. old Authorization header not persisted as replay authority;
15. OAuth token rotation allowed only in same scope;
16. tracing header drift ignored when non-semantic;
17. content-length/framing drift ignored when semantic body identical;
18. auth middleware adding semantic query field rejected;
19. nonce refreshed only under declared rule;
20. credential change to another account rejected.

### C. Serializer/default drift
21. added SDK default rejected;
22. removed SDK default rejected;
23. enum normalization change rejected;
24. map ordering change accepted only if proven order-insensitive;
25. list ordering change rejected when semantic;
26. float/number encoding semantic drift rejected;
27. omitted-field meaning change across API version rejected;
28. content-type semantic change rejected;
29. request path/RPC method drift rejected;
30. SDK auto-generating replacement token rejected.

### D. Adapter compatibility declarations
31. exact supported old->new generation accepted;
32. undeclared generation denied;
33. compatibility is directional;
34. expired declaration denied;
35. challenged declaration denied;
36. wrong provider operation denied;
37. wrong capsule schema denied;
38. wrong endpoint class denied;
39. missing conformance evidence denied;
40. rollback to older declaration generation fail-closes.

### E. Endpoint/routing scope
41. DNS IP change same service accepted;
42. region drift rejected;
43. zone drift rejected when idempotency is zonal;
44. sandbox/live drift rejected;
45. account-specific endpoint drift rejected;
46. generic fallback endpoint unknown -> denied;
47. documented same-scope endpoint failover accepted only with capability proof;
48. API hostname version drift rejected without compatibility proof;
49. partition change rejected;
50. service-name change used by signing rejected when semantic scope changes.

### F. Credentials/secrets
51. API key rotation same account accepted when provider contract permits;
52. credential rotation different account rejected;
53. revoked principal with no equivalent authority -> retry denied;
54. semantic secret retained via authenticated sealed reference;
55. missing semantic secret material -> retry denied;
56. display redaction does not change capsule digest;
57. secret re-encryption preserves semantic identity;
58. auth credential never treated as semantic payload by default;
59. provider principal-scoped idempotency requires same principal equivalence;
60. ambiguous credential scope -> denied.

### G. Recovery/crash
61. crash after capsule persistence before `SEND_STARTED` leaves no sent claim;
62. crash after `SEND_STARTED` before first socket write remains UNKNOWN with complete capsule;
63. retry after crash uses same capsule identity;
64. retry cannot regenerate provider token;
65. retry semantic digest verified before signing;
66. final request semantic digest verified after signing;
67. crash after `RETRY_STARTED` remains UNKNOWN same identity;
68. terminal outcome prevents further replay;
69. concurrent workers cannot produce divergent semantic requests;
70. stale worker rejected after compatibility declaration revocation.

### H. Provider capability/retention
71. inside proven idempotency window eligible;
72. expired window denied even with same token;
73. unknown window denied;
74. provider parameter mismatch response does not mint new token;
75. in-progress response remains same identity;
76. provider drift challenge blocks replay;
77. mutation replay unsupported -> oracle/manual only;
78. read-only operation ID uses separate oracle authority;
79. weak `NOT_FOUND` does not reopen send authority;
80. new business attempt requires new effect authorization and is never represented by mutating the old capsule.

## Implementation boundary

Production implementation waits for executable RED coverage on the real LAB-093/LAB-090..100 composition.

The first code slice should be a pure deterministic verifier plus fixture-driven adapter compatibility tests. It should not perform live provider sends. The minimal proof goal is:

> Given one historical replay capsule and two adapter generations, the verifier deterministically proves whether the newer adapter can create a transport-authenticated request whose provider-semantic identity is exactly the original one, while forbidding any replacement idempotency token or semantic drift.

Only after that RED/GREEN gate should a live retry adapter be connected to `EffectiveRetryAuthorizationV1`.

## Decision

Freeze V1 with the following rule:

> Historical retry reuses one immutable provider-semantic operation capsule. Time-bound authentication may be refreshed only around that capsule. Adapter or SDK upgrades are not trusted to reconstruct history unless an authenticated compatibility declaration and deterministic verifier prove semantic identity preservation.

When that proof is unavailable, recovery is read-only reconciliation or manual reconciliation, never a best-effort reconstructed send.