# Provider-fence proof portability / provider-native receipt authenticity / adapter-verifier independence v1

Status: `PROVIDER_FENCE_PROOF_PORTABILITY_PROVIDER_NATIVE_RECEIPT_AUTHENTICITY_ADAPTER_VERIFIER_INDEPENDENCE_V1_FROZEN`

Date: 2026-09-07
Related: LAB-093/#178, LAB-086/#163, provider-fence attestation follow-up

## Problem

The preceding provider-fence contract requires evidence that an external or multi-region provider enforced one monotonic fence. A remaining common-mode failure exists if the same SDK/adapter that issued the consequential request also constructs the only proof that the provider accepted, ordered, rejected, or fenced that request.

An adapter can be buggy, compromised, semantically stale, or simply interpret a provider response incorrectly. Therefore an adapter-generated JSON record, even if durably stored, is not by itself provider-native evidence. Historical audit after SDK/API/provider migration additionally requires that proof remain verifiable without re-running the original client library or trusting mutable provider control-plane state.

## Security objective

A provider-fence proof is portable only when an independent verifier can bind a consequential operation to provider-origin evidence using a durable trust root and stable semantics, without trusting the issuing adapter's interpretation of the result.

Formally, for operation `O` and provider fence generation `g`, closure may rely on receipt `R` only if:

1. `R` is cryptographically or otherwise independently bound to provider authority or to an independently trusted witness of provider output;
2. `R` binds the exact operation identity, resource scope, fence/epoch, request digest, result class, and ordering/version evidence needed by the claim;
3. verification can be performed by an implementation that is independent of the issuing adapter;
4. required trust material and semantic schema are retained immutably enough for later verification;
5. replay, substitution, endpoint/region confusion, and API-version reinterpretation are rejected;
6. the evidence class is strong enough for the claim being made. A signed "request observed" receipt cannot prove "stale epoch rejected" unless it commits to that rejection semantics.

## Evidence classes

### R0 — adapter assertion

Examples: locally generated JSON, log line, SDK object serialization, exception string, locally inferred commit timestamp.

Properties:
- useful for debugging and correlation;
- no independent provider authenticity;
- MUST NOT alone support `HANDOFF_CLOSED`, destructive GC, or revocation closure.

### R1 — authenticated transport observation

Examples: TLS-authenticated API response bytes retained with request digest, endpoint identity, server certificate chain, protocol metadata, and verifier-captured transcript metadata.

Properties:
- stronger than R0 because bytes originate through an authenticated channel;
- ordinarily does not provide durable non-repudiation after certificate/key rotation;
- cannot automatically prove that a response was globally committed or that another region did not accept a stale epoch;
- may support reconciliation but not historical closure unless augmented by stronger provider semantics/evidence.

### R2 — provider-signed receipt

Provider/HSM/key signs a canonical receipt that binds operation digest, resource, result, provider order/version token, fence generation, issuer identity/key epoch and time/sequence context.

Properties:
- independently verifiable with retained provider trust chain;
- survives SDK replacement if receipt schema and trust anchors are retained;
- suitable for positive acceptance/rejection evidence when signed semantics are explicit;
- still requires a separate global/non-equivocation argument when provider may sign contradictory receipts.

### R3 — provider-signed receipt plus append-only/transparency inclusion

R2 plus independently verifiable inclusion proof/checkpoint in an append-only log or equivalent signed digest chain.

Properties:
- improves historical durability and equivocation detection;
- supports independent replay/audit without live provider access;
- transparency proves publication/inclusion, not by itself correctness of provider business semantics.

### R4 — quorum / multi-witness provider receipt

Receipt semantics are independently attested by multiple provider regions, quorum members, or independent witnesses bound to a common monotonic order/fence.

Properties:
- candidate for strongest P1 cross-region closure;
- verifier MUST prove the witnesses belong to the same fence authority and that quorum intersection/non-equivocation rules are satisfied;
- multiple copies of the same adapter observation are not R4.

## `PortableProviderReceiptV1`

Required canonical fields:

- `receipt_version`;
- `provider_id` and stable provider implementation/service identity;
- `provider_api_family` + exact semantic revision;
- `resource_scope` canonical identifier;
- `operation_id` generated before request;
- `request_digest` over canonical consequential request bytes/semantics;
- `operation_class` (`RENEW`, `REVOKE`, `FENCE_ADVANCE`, `STALE_REJECT`, `READBACK`, etc.);
- `fence_generation` and predecessor/reference generation;
- `provider_order_token` / commit version / transaction ID / sequence as applicable;
- `result_class` with closed enum semantics;
- `result_digest` where a result body matters;
- `region_or_failure_domain`;
- `provider_issuer_id` + `provider_key_epoch`;
- `provider_signature_or_native_proof`;
- `trust_bundle_digest`;
- `verifier_policy_digest`;
- optional `transparency_entry` / digest-chain link / RFC3161 timestamp;
- optional independent readback/witness receipts;
- `capture_time` only as observational metadata unless independently timestamped.

Unknown fields are preserved but cannot acquire security meaning without a new semantic revision.

## Canonicalization and type binding

Provider evidence must sign or otherwise authenticate the exact typed payload. Generic JSON reserialization is not a security boundary unless the provider defines a canonical form.

Preferred shapes:

1. provider-native signed binary/protobuf/CBOR with stable schema;
2. DSSE-style typed envelope around the exact provider receipt bytes;
3. RFC 8785/JCS only when the provider contract explicitly defines it;
4. detached signature over an exact byte digest plus explicit media/type identifier.

DSSE is a useful donor because it authenticates both message and payload type and deliberately avoids requiring arbitrary message canonicalization. It does not solve key ownership or PKI by itself.

## Trust-root retention

Historical verification MUST NOT depend on asking today's provider API which key was trusted years ago.

For every accepted R2+ receipt retain:

- exact public certificate/key chain or immutable key identifier plus independently retained trusted root;
- validity interval and key epoch;
- revocation/status evidence needed by policy at verification time;
- provider identity binding;
- semantic schema/version used to interpret signed fields;
- any transparency-log/checkpoint trust roots;
- verification policy generation.

Trust-root rotation is additive. Old receipts retain their historical verification material; later roots do not retroactively reinterpret earlier signatures.

Google Cloud HSM attestation is a positive donor shape: the HSM returns a cryptographically signed attestation plus certificate chains that can be downloaded and verified independently, and the attestation binds properties such as the key-version resource identity. The important mechanism is independent machine verification of provider-origin bytes, not the specific HSM use case.

## Independent verifier domain

`AdapterVerifierIndependenceV1` requires separation between:

- **issuer adapter**: constructs/sends consequential API request;
- **receipt capture**: preserves provider-origin evidence without semantic rewriting where possible;
- **verifier**: independently parses and validates signature/trust/schema/request binding;
- **policy evaluator**: decides whether the verified receipt is sufficient for a specific fence/revocation claim.

For E2/E3/E4 consequences, issuer adapter and verifier MUST NOT share the same parsing/decision implementation as the sole correctness check. Shared schema libraries are acceptable only if an independently specified conformance corpus proves the critical semantics and parser ambiguity is fail-closed.

## Adapter/API drift

Every adapter/provider semantic generation has a digest and explicit validity interval. Migration from API vN to vN+1 cannot silently reinterpret old receipts.

Rules:

- unknown receipt semantic revision => `UNKNOWN_UNVERIFIABLE_SCHEMA`;
- removed/deprecated provider field cannot be reconstructed from local guesses;
- changed provider ordering semantics require a new verifier policy generation;
- provider migration A→B never converts A's local version token into B's fence token without an authenticated handoff proof;
- historical verification executes against retained receipt bytes and frozen semantic schema, not current SDK objects.

## Signed receipts are not enough for non-equivocation

A provider can cryptographically sign two contradictory receipts. Therefore:

`AUTHENTIC(receipt) != NON_EQUIVOCATING(provider)`.

For closure claims needing uniqueness/monotonicity, one of the following is required:

- provider-native globally linearizable order whose signed token can be independently checked;
- append-only transparency/digest-chain evidence with consistency proofs/checkpoints;
- quorum receipts with proven quorum intersection;
- finite drain/expiry that makes contradictory stale acceptance harmless after a proven horizon.

Sigstore/Rekor is a positive donor for portability: its bundle carries verification material, transparency-log entries/inclusion proofs and RFC3161 timestamps so verification can be performed later/offline. The reusable mechanism is a self-contained verification bundle plus independently trusted root, not Sigstore-specific artifact semantics.

AWS CloudTrail is another useful donor: digest files include hashes of log files, digest-chain linkage and digital signatures; validation can be implemented independently using CloudTrail public keys, and moved logs can still be validated outside their original storage location. This demonstrates a provider-origin signed evidence chain that survives relocation. It does not prove arbitrary API operation linearizability and must not be generalized beyond its stated semantics.

RFC3161 is a narrow donor for trusted time evidence: it can prove that a digest existed by a TSA time, but it does not prove provider acceptance/order/fencing. Timestamp tokens may augment R2/R3; they never upgrade an R0 assertion into provider-native truth.

## Portable verification algorithm

For each consequential receipt:

1. Load retained raw receipt bytes and declared receipt media/type.
2. Select exact frozen semantic schema by authenticated revision digest.
3. Verify provider signature/native proof against retained trust bundle and historical key policy.
4. Recompute and match `request_digest` from the canonical operation record.
5. Verify resource, operation ID/class, fence generation, provider identity, region/failure-domain and result semantics.
6. Validate provider order/version token according to that frozen provider semantic generation.
7. Verify transparency/digest-chain/quorum evidence where required.
8. Cross-check independent reconciliation evidence for negative claims such as `STALE_REJECT` or global non-acceptance.
9. Emit a typed verdict: `VERIFIED_POSITIVE`, `VERIFIED_NEGATIVE`, `AUTHENTIC_BUT_INSUFFICIENT`, `CONTRADICTED`, `UNKNOWN_UNVERIFIABLE_SCHEMA`, or `INVALID`.
10. Never convert timeout/missing evidence into a positive or negative provider claim.

## Fraud/contradiction proofs

### `AdapterFabricatedReceiptProofV1`
Local adapter record claims provider success/rejection but no matching provider-authentic receipt exists where policy requires R2+.

Effect: dependent closure remains `UNKNOWN`; adapter generation quarantined pending audit.

### `ReceiptRequestBindingMismatchProofV1`
Valid provider signature exists but signed request/resource/fence generation does not match the consequential operation record.

Effect: receipt is unusable for that operation; replay/substitution suspected.

### `ProviderReceiptEquivocationProofV1`
Two authentic receipts for the same provider/resource/order scope assert mutually incompatible fence/result states that cannot coexist under the claimed semantics.

Effect: provider non-equivocation assumption invalidated; affected closure/finalization/GC certificates stale until a stronger reconciliation/fraud-resolution proof exists.

### `SemanticDriftMisverificationProofV1`
Current adapter/verifier interprets an old receipt differently from its frozen authenticated semantic revision.

Effect: current verifier generation is disqualified for historical proof; re-run with frozen semantics and create migration evidence if needed.

### `ReceiptTrustRollbackProofV1`
Historical receipt is revalidated under a later/weaker/unrelated trust root without authenticated rotation lineage.

Effect: verification fails closed.

## Negative evidence

A core design rule is that positive receipt evidence and negative exclusion evidence differ.

- Provider-signed `SUCCESS(g)` proves acceptance of `g` only under its defined scope.
- Provider-signed `STALE_REJECT(g-1,current=g)` can prove one rejected attempt if semantics bind the exact request.
- Absence of a receipt does not prove rejection.
- One endpoint readback of `g` does not prove no other material endpoint can accept `g-1`.
- A transparency log proving inclusion of `SUCCESS(g)` does not prove absence of a contradictory `SUCCESS(g-1)` unless the log/order semantics and consistency proof establish that property.

## Historical portability acceptance criteria

A receipt set is `PORTABLE_VERIFIED` only if all of the following hold offline from the original issuing adapter:

- exact raw provider-origin evidence retained;
- verification trust material retained and independently rooted;
- exact semantic schema/revision retained;
- operation/request/fence binding recomputable;
- required inclusion/quorum/order proofs retained;
- verifier can run without current provider SDK;
- no live mutable provider lookup is required to decide historical authenticity;
- any required revocation/status/time policy has retained evidence sufficient for historical evaluation;
- contradictions are detected rather than resolved by latest-wins.

## RED-first matrix (80 cases)

### A. Authenticity and request binding (1-16)
1. R0 local success JSON rejected for closure.
2. R0 locally signed by adapter key rejected as provider-native.
3. TLS response retained without provider signature classified R1.
4. valid R2 signed receipt accepted for positive claim.
5. wrong provider key rejected.
6. wrong provider identity rejected.
7. correct signature/wrong resource rejected.
8. correct signature/wrong operation ID rejected.
9. correct signature/wrong request digest rejected.
10. correct signature/wrong fence generation rejected.
11. replayed receipt for prior request rejected.
12. result-body digest mismatch rejected.
13. unknown operation class fail-closed.
14. unknown required signed field fail-closed.
15. extra unknown unsigned field cannot alter verdict.
16. receipt type-confusion attack rejected.

### B. Trust/root/history (17-28)
17. historical chain retained -> offline verification succeeds.
18. current provider API unavailable -> retained proof still verifies.
19. old key expired after operation but trusted historical-time proof retained -> policy-consistent verification.
20. missing historical trust bundle -> UNKNOWN/invalid per policy.
21. later unrelated root cannot verify old receipt.
22. authenticated root rotation lineage accepted.
23. rollback to older root rejected.
24. revoked key with no retained historical status evidence -> UNKNOWN.
25. HSM/provider attestation binds expected service/key identity.
26. attestation for different resource rejected.
27. certificate chain substitution rejected.
28. trust bundle digest mismatch rejected.

### C. Adapter/verifier independence (29-40)
29. issuer and verifier same code only -> insufficient for E3/E4 claim.
30. independent parser reproduces verdict -> accepted independence evidence.
31. adapter omits provider failure field -> independent verifier detects mismatch.
32. SDK exception mapped to stale rejection but raw response disagrees -> contradiction.
33. raw receipt retained, adapter object not retained -> verification still succeeds.
34. only deserialized SDK object retained -> non-portable.
35. verifier uses frozen schema, current SDK removed -> succeeds.
36. shared schema library + independent conformance corpus -> allowed.
37. parser ambiguity yields divergent security verdict -> fail-closed.
38. issuer rewrites receipt before persistence -> digest mismatch/fail.
39. independent capture preserves raw bytes -> accepted.
40. adapter-generated timestamp cannot establish provider event time.

### D. API/schema migration (41-52)
41. v1 receipt verified under v1 frozen semantics after v2 rollout.
42. v2 verifier silently interprets v1 field differently -> rejected.
43. unknown semantic revision -> UNKNOWN_UNVERIFIABLE_SCHEMA.
44. deprecated field missing from new API does not erase old semantics.
45. provider A receipt cannot become provider B token.
46. A→B authenticated handoff proof composes correctly.
47. semantic revision digest mismatch rejected.
48. current SDK cannot parse old bytes but independent verifier can -> portable.
49. current provider deletes live history endpoint -> retained bundle still verifies.
50. migration rewrites raw receipt bytes -> rejected.
51. additive metadata leaves signed raw receipt unchanged -> allowed.
52. schema rollback to weaker interpretation rejected.

### E. Transparency/time/non-equivocation (53-66)
53. R2 + valid inclusion proof accepted as R3.
54. invalid inclusion proof rejected.
55. signed entry timestamp without required inclusion proof classified per frozen policy.
56. transparency checkpoint key mismatch rejected.
57. inconsistent log checkpoints trigger equivocation/UNKNOWN.
58. valid RFC3161 timestamp proves existence-time only.
59. RFC3161 timestamp does not prove provider acceptance.
60. provider signs contradictory SUCCESS receipts -> equivocation proof.
61. two regions sign incompatible fence states -> contradiction.
62. quorum receipt with proven intersection accepted.
63. multiple witnesses without common authority not treated as quorum.
64. one-region readback remains insufficient for global exclusion.
65. stale rejection receipt binds exact old attempt -> valid negative event evidence.
66. absence of stale-success receipt is not negative proof.

### F. Crash/replay/recovery/GC (67-80)
67. crash after provider response before local record -> reconciliation locates provider-native receipt if available.
68. crash after local R0 before provider response -> remains UNKNOWN.
69. timeout-after-send with no receipt -> UNKNOWN.
70. duplicate identical receipt deduplicated by digest/operation ID.
71. contradictory receipt never latest-wins away prior evidence.
72. recovery verifier replays raw bytes idempotently.
73. tampered archive copy rejected.
74. archive relocation with preserved receipt/trust bundle still verifies.
75. GC forbidden while required trust/schema material is unarchived.
76. GC forbidden while receipt contradiction unresolved.
77. stale verifier policy cannot silently authorize destruction.
78. provider migration retains old proof bundle before decommission.
79. historical audit succeeds without original SDK/provider account access.
80. inability to prove portability leaves closure `UNKNOWN`, never success.

## Decision

Freeze `PROVIDER_FENCE_PROOF_PORTABILITY_PROVIDER_NATIVE_RECEIPT_AUTHENTICITY_ADAPTER_VERIFIER_INDEPENDENCE_V1_FROZEN`.

For LAB-093 composition:

- R0 adapter assertions are telemetry, never provider authority.
- R1 authenticated transport observations are reconciliation evidence but not automatically durable historical proof.
- R2 provider-signed/native receipts are the minimum preferred evidence for provider-origin positive/negative claims when available.
- R3/R4 are required when the claim additionally depends on historical non-equivocation/global ordering that a single signed receipt cannot establish.
- Exact raw provider receipt bytes, trust bundle and frozen semantics must be retained before provider/API migration or destructive GC.
- Issuer adapter and historical verifier must be independently checkable for E2/E3/E4 consequences.
- Missing/ambiguous historical evidence preserves `UNKNOWN`.

## Primary donors

- AWS CloudTrail log file integrity validation: provider-signed digest chain; independent public-key validation; moved logs can still be custom-validated. Mechanism donor for portable provider-origin evidence, not arbitrary operation linearizability.
- Sigstore bundle / Rekor: verification material, transparency inclusion evidence and RFC3161 timestamps packaged for later/offline verification. Mechanism donor for self-contained proof bundles and independent roots.
- DSSE: typed signing envelope that authenticates payload type while avoiding fragile generic canonicalization assumptions.
- RFC 3161: trusted timestamp token proving existence of a digest by a time; deliberately insufficient to prove provider operation semantics.
- Google Cloud HSM attestation: cryptographically signed attestation plus certificate chains independently verifiable outside the issuing SDK, with resource/key identity binding.

## Source notes

Primary references checked 2026-09-07:

- AWS CloudTrail, "Validating CloudTrail log file integrity" and custom validation documentation.
- Sigstore bundle format / protobuf specs and Rekor CLI documentation.
- Secure Systems Lab DSSE specification.
- RFC 3161, Internet X.509 PKI Time-Stamp Protocol.
- Google Cloud KMS, "Verifying attestations".
