# Provider semantic-request extractor / post-signing equivalence attestation + golden conformance fixtures V1

Status: `PROVIDER_SEMANTIC_REQUEST_EXTRACTOR_POST_SIGNING_EQUIVALENCE_ATTESTATION_V1_FROZEN`

Date: 2026-09-05

Related: LAB-093/#178; composes with LAB-086, LAB-090..100 and `PROVIDER_WIRE_REQUEST_REPLAY_CAPSULE_DETERMINISTIC_ADAPTER_COMPATIBILITY_V1_FROZEN`.

## Objective

Turn adapter replay compatibility from a prose assertion into executable evidence. A historical consequential retry is admissible only when a provider/adapter-specific extractor can derive the same authority-relevant semantic request from:

1. the immutable `ProviderReplayCapsuleV1` pinned before the original `SEND_STARTED`; and
2. the final transport-authenticated request immediately before external I/O.

The equality check must fail closed on unknown or newly introduced semantics. It must not treat byte identity of the entire HTTP request as the goal because authentication, timestamps, nonces, tracing, connection framing and some transport codings may legitimately change. Conversely it must not treat a matching idempotency token as sufficient when payload/defaults/routing/provider scope changed.

## Primary-source donors

- AWS Signature Version 4 canonical request: method, canonical URI, canonical query, selected headers, signed-header set and hashed payload are explicit request components; AWS also identifies volatile hop-by-hop headers that should not be signed. This is a useful donor for separating semantic request material from volatile transport material, but the LAB extractor is provider-operation-specific and may need fields AWS signing does not sign. https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_sigv-create-signed-request.html
- RFC 9110 HTTP Semantics: `Content-Type` and `Content-Encoding` affect representation semantics; transfer coding is distinct from representation coding. Therefore decompression/recompression cannot automatically be treated as semantically irrelevant without a provider-specific declaration. https://www.rfc-editor.org/rfc/rfc9110.html
- RFC 7578 multipart/form-data: boundary is framing, while ordered parts, names, filenames, per-part content types and part payloads may carry application semantics. Generic byte hashing of a multipart body is too strong; generic unordered map normalization is too weak. https://www.rfc-editor.org/rfc/rfc7578.html
- Protocol Buffers documentation: deterministic serialization is explicitly not canonical across builds/languages/schema evolution, especially with unknown fields. Provider-semantic protobuf extraction therefore needs a schema/version-pinned field-aware function or exact-wire policy, never a generic deterministic-serialization hash. https://protobuf.dev/programming-guides/serialization-not-canonical/

## Core invariant

For every consequential provider attempt:

`semantic_digest(extract_capsule(capsule)) == semantic_digest(extract_final_wire(final_request))`

must hold **immediately before I/O**, under an authenticated extractor generation admitted for the exact provider/service/operation/API/adapter generation.

A mismatch, extractor error, unsupported field, parser ambiguity, missing provenance, unknown middleware mutation, or unclassified component removes mutation/retry authority. It never falls back to "same token, probably okay".

## Object model

### `SemanticExtractorDeclarationV1`

Immutable/authenticated fields:

- `extractor_generation_id`
- `provider_id`
- `service_id`
- `operation_id`
- `api_version`
- `adapter_generation_id`
- `serializer_generation_id`
- `signing_middleware_generation_id`
- `endpoint_resolver_generation_id`
- `request_media_types[]`
- `semantic_field_rules[]`
- `volatile_field_rules[]`
- `forbidden_or_unknown_field_policy = FAIL_CLOSED`
- `capsule_extractor_digest`
- `wire_extractor_digest`
- `fixture_set_digest`
- `source/build provenance digest`
- `parent global-provenance record`
- signer/quorum evidence required by the active authority graph.

Declarations are directional. A generation may be able to replay capsules from generation N without N being able to replay capsules from the newer generation.

### `ProviderSemanticRequestV1`

Canonical provider-semantic projection. At minimum:

- HTTP/RPC operation or provider action;
- normalized endpoint identity under an operation-specific endpoint policy;
- provider account/tenant/principal scope when idempotency/effect semantics depend on it;
- region/zone/project/namespace scope when relevant;
- exact idempotency/request token in provider-defined normalized form;
- semantic query multimap preserving duplicate-key/order semantics when provider-visible;
- semantic headers with explicit normalization rules;
- body semantic projection or exact body digest according to declared media-type policy;
- provider/API version selectors;
- SDK-generated effective defaults that are provider-visible;
- any operation-specific feature/version flags;
- extractor generation and canonicalization version.

The canonical digest uses the repository's frozen shared canonical V1 encoding and domain separation, e.g. `LAB-PROVIDER-SEMANTIC-REQUEST-V1\0 || canonical_bytes`.

### `PostSigningEquivalenceAttestationV1`

Created after all adapter serialization, signing and request middleware, immediately before I/O:

- replay capsule identity/digest;
- final request observation identity;
- extractor declaration generation;
- capsule semantic digest;
- final-wire semantic digest;
- equality verdict;
- exact build/config/plugin/authority generations;
- effective-authority lease/attempt identity;
- timestamp/monotonic sequence used only for audit, not semantic equality;
- authenticated append into the global provenance chain before or atomically with `SEND_STARTED` transition according to the attempt protocol.

No PASS attestation may be produced from an intermediate pre-middleware request.

## Extraction rules

### Method / RPC operation

Method/action is semantic by default. `POST` vs `PUT`, RPC method name, action parameter, GraphQL mutation name or provider operation discriminator cannot be normalized away unless provider primary documentation and conformance fixtures prove equivalence.

### Endpoint identity

The extractor must distinguish:

- scheme when provider behavior depends on it;
- canonical provider host/service identity;
- account/tenant encoded in host;
- region/zone encoded in host;
- provider endpoint variant (public/private/FIPS/dualstack/accelerated) if it can affect routing or idempotency scope;
- port where non-default or provider-significant.

DNS aliases, redirects and SDK endpoint rewrites are not automatically equivalent. A provider-specific equivalence table must be declared and fixture-tested.

### Query

Parse as an ordered multimap first. Rules must state whether:

- order is semantic;
- duplicate keys are allowed and whether duplicate order matters;
- percent-encoding normalization is valid;
- `+` and `%20` are equivalent;
- empty, absent and null-like parameters differ;
- provider/API version and action parameters are semantic.

Unknown query keys fail closed.

### Headers

Classify every final header into one of:

- `SEMANTIC_EXACT`
- `SEMANTIC_NORMALIZED`
- `AUTH_REFRESHABLE`
- `TRANSPORT_VOLATILE`
- `FORBIDDEN_UNKNOWN`

Examples requiring operation-specific treatment: `Content-Type`, `Content-Encoding`, conditional headers, provider version headers, idempotency headers, checksum headers, tenant/project headers and feature flags.

`Authorization`, fresh dates, OAuth/session tokens and signature material may be refreshable only after proving that changing them preserves the same provider account/principal/idempotency scope.

Hop-by-hop fields may be volatile when provider semantics truly exclude them, but this classification must be explicit rather than inferred from HTTP alone.

### JSON

Never compare arbitrary raw JSON bytes when the provider semantics are structural, and never canonicalize away distinctions the provider observes. The declaration must define:

- duplicate-key policy (normally reject before send);
- number representation/equality policy;
- null vs absent;
- string normalization policy (normally no Unicode normalization unless provider specifies it);
- array order;
- object member order;
- provider defaults inserted by SDK/middleware.

If the provider itself signs/hashes raw body bytes or treats exact bytes as part of idempotency matching, use exact-body digest instead of structural normalization.

### Form URL encoding

Treat as a provider-defined ordered or unordered multimap only after declaring rules for duplicate keys, encoding, charset, empty values and ordering. Do not assume common web-form equivalence.

### Multipart

RFC 7578 boundary bytes are framing, but part sequence and repeated-name ordering can be significant. Projection must preserve, per part:

- ordinal when ordering is semantic or unknown;
- field name;
- filename semantics;
- semantic per-part headers;
- per-part media type;
- exact payload digest or media-specific semantic projection.

Random boundary values may be ignored only after parsing succeeds uniquely and all parts are accounted for. Preamble/epilogue or malformed/ambiguous multipart fails closed.

### Compression and content codings

RFC 9110 makes `Content-Encoding` part of representation metadata. A provider-specific declaration must choose one of:

- `CODED_BYTES_SEMANTIC`: exact coded representation/digest is semantic;
- `DECODED_REPRESENTATION_SEMANTIC`: decode with an admitted deterministic decoder and compare underlying representation plus allowed coding metadata;
- `UNSUPPORTED_FOR_REPLAY`.

Do not decompress arbitrary or unbounded content in the authority path; enforce size/ratio/time limits and fail closed.

### Streaming / chunked bodies

`Transfer-Encoding: chunked` framing may be transport-only, but streamed provider payload is not. Before consequential I/O, semantic equality must be established by one of:

1. precomputed exact payload digest over a replayable immutable source;
2. provider-supported trailer/checksum scheme whose full semantics are authenticated and verified before provider commit is possible; or
3. a two-pass immutable stream where pass one computes semantic evidence and pass two is cryptographically bound to the same bytes.

If the first semantic digest can only be known after bytes have already been irreversibly sent, the adapter is not admitted for historical mutation replay unless the provider protocol supplies an independently safe abort/commit boundary.

### Presigned URLs

Signature, expiry, credential and nonce query fields may legitimately change, but the extractor must separately bind the underlying provider operation: method, bucket/resource/object identity, signed semantic headers, content digest/checksum, provider account/region scope and any query parameters affecting the operation. A presigned URL that changes operation/resource is a mismatch even if generated from the same capsule.

### Protobuf / gRPC

Do not use generic `SerializeToString(deterministic=True)` or equivalent as a durable semantic canonicalization across generations. Protocol Buffers explicitly warns deterministic serialization is not canonical and unknown fields make generic fingerprinting unsafe.

Each admitted RPC must declare one of:

- field-aware semantic extraction naming every authority-relevant field under an exact schema descriptor digest, with explicit unknown-field rejection/preservation policy; or
- exact-wire digest if provider semantics are byte-sensitive and exact wire reproduction is proven.

Schema/descriptor drift invalidates compatibility until new fixtures pass.

### SDK-generated defaults

The final-wire extractor, not only the capsule-side extractor, must observe defaults inserted by:

- serializers;
- endpoint resolvers;
- retry middleware;
- checksum middleware;
- request compression;
- API-version selection;
- user-agent-like provider feature headers when provider-semantic;
- content-length/type inference;
- convenience SDK wrappers.

A newly introduced provider-visible default is a semantic change until explicitly classified and fixture-proved.

## Middleware ordering and TOCTOU

Required pipeline:

`capsule load -> construct request -> serialize -> endpoint resolve -> provider SDK middleware -> auth/sign -> final request freeze -> extract final semantics -> compare digests -> durable attestation/SEND_STARTED protocol -> immediate I/O`

After final extraction, any middleware capable of changing method, endpoint, query, semantic headers or payload must be impossible. The actual socket/RPC send function must consume the frozen request object or immutable serialized representation inspected by the extractor.

If a library signs lazily inside the transport layer and does not expose the final request before send, that adapter generation is not admitted unless a lower-level audited transport hook can attest the exact pre-I/O request without opening a mutation gap.

## Golden conformance fixtures

Every admitted adapter generation needs a signed fixture set bound to its source/build/config digest. Fixtures are offline/read-only and contain no live secrets.

Each fixture includes:

- replay capsule;
- deterministic synthetic request construction inputs;
- final pre-I/O request observation with secrets replaced by typed placeholders where allowed;
- expected `ProviderSemanticRequestV1` projection;
- expected semantic digest;
- expected PASS/FAIL reason;
- exact extractor/build generations.

Required positive fixtures include fresh auth timestamp/signature, credential rotation within proven equivalent scope, different multipart boundary, permitted transfer framing change, and any provider-documented endpoint alias that is intentionally admitted.

Required negative fixtures include mutation of every semantic field class independently: token, resource, method, account, region/zone, API version, query parameter, duplicate query behavior, semantic header, payload field, default, multipart part/order, content coding mode, protobuf field/unknown field, endpoint variant and principal scope.

A fixture set is insufficient if it only contains hand-picked examples. The verifier must enforce field-coverage metadata showing that every semantic rule has at least one mutation fixture and every volatile rule has at least one allowed-change fixture.

## Compatibility proof and admission

An adapter generation is replay-compatible with historical capsule generation N only if all hold:

1. authenticated directional declaration exists;
2. exact source/build/config/plugin/SDK/serializer/signing-middleware digests match the declaration;
3. golden fixture set signature and global provenance verify;
4. all positive and negative fixtures execute successfully in the current binary;
5. extractor observes every final request component or explicitly rejects unsupported components;
6. provider-capability generation still permits same-identity retry within its proven retention/scope window;
7. effective-authority/quarantine/retry-authority contracts permit the attempt;
8. final live request equivalence attestation passes immediately before I/O.

Fixture success is necessary but not sufficient for a live send: it never overrides expired provider idempotency retention, challenge/quarantine, UNKNOWN/manual-reconciliation requirements or business/security approval boundaries.

## Failure modes

Fail closed to read-only oracle/manual reconciliation on:

- unknown header/query/body component;
- malformed or ambiguous parser input;
- unsupported media/content encoding;
- schema descriptor mismatch;
- middleware/build/config drift;
- missing fixture coverage;
- final request mutation after attestation;
- semantic digest mismatch;
- inability to observe lazy signing/middleware output before send;
- streaming payload whose complete semantics cannot be known before irreversible I/O;
- credential rotation that cannot prove same provider scope;
- provider documentation or observed behavior drift.

No failure path mints a new application key, provider token, effect identity or ordinary SEND lease.

## RED-first conformance matrix (80 cases)

### A. Declaration / provenance (1-10)
1. Missing extractor declaration => deny.
2. Wrong provider => deny.
3. Wrong service/operation => deny.
4. Wrong API version => deny.
5. Wrong adapter generation => deny.
6. Wrong serializer generation => deny.
7. Wrong signing middleware generation => deny.
8. Wrong endpoint resolver generation => deny.
9. Fixture-set digest mismatch => deny.
10. Broken global provenance/signature/quorum => deny.

### B. Method / endpoint / scope (11-20)
11. Same method/resource => pass.
12. Method mutation => deny.
13. Host alias not declared => deny.
14. Declared equivalent endpoint alias => pass.
15. Account/tenant mutation => deny.
16. Region mutation when scoped => deny.
17. Zone mutation when scoped => deny.
18. FIPS/dualstack/private endpoint semantic mutation => deny unless declared equivalent.
19. Port mutation => deny unless declared equivalent.
20. Redirect-resolved endpoint outside declaration => deny.

### C. Query / headers (21-32)
21. Query reordering when declared order-insensitive => pass.
22. Query reordering when order-sensitive/unknown => deny.
23. Duplicate query key introduced => deny unless exact declared semantics match.
24. `%20`/`+` normalization not declared => deny.
25. Semantic query value mutation => deny.
26. Unknown query key => deny.
27. Fresh auth date/signature => pass when scope-equivalent.
28. Idempotency header mutation => deny.
29. API/version header mutation => deny.
30. Unknown final header => deny.
31. Declared volatile trace header mutation => pass.
32. Credential rotation across principal/idempotency scope => deny.

### D. JSON/forms/defaults (33-44)
33. JSON object member reorder under declared structural semantics => pass.
34. JSON array reorder => deny.
35. null vs absent mutation => deny unless provider declaration proves equivalence.
36. duplicate JSON key => reject/deny.
37. number semantic mutation => deny.
38. Unicode normalization change not declared => deny.
39. exact-byte-sensitive JSON whitespace mutation => deny.
40. form duplicate key mutation => deny.
41. form ordering mutation with unknown semantics => deny.
42. SDK inserts same pinned effective default => pass.
43. SDK inserts new provider-visible default => deny.
44. SDK changes omitted-default behavior => deny.

### E. Multipart / coding / streaming (45-58)
45. Multipart boundary changes only => pass after unique parse.
46. Part payload mutation => deny.
47. Part name mutation => deny.
48. Filename semantic mutation => deny.
49. Repeated-name part order mutation when semantic/unknown => deny.
50. Unknown per-part semantic header => deny.
51. Compression algorithm changes under coded-byte semantics => deny.
52. Compression bytes change under decoded-representation semantics but decoded content equal => pass only if declared.
53. Decompression bomb/limit exceeded => deny.
54. Transfer chunk sizes change with identical preverified payload => pass if transport-only.
55. Stream source changes after prehash => deny via immutable-source binding.
56. One-pass irreversible stream before complete attestation => deny.
57. Trailer/checksum mode without proven provider commit boundary => deny.
58. Multipart malformed/ambiguous parse => deny.

### F. Protobuf / structured RPC (59-68)
59. Same field-aware projection => pass.
60. Known semantic field mutation => deny.
61. Unknown field appears under reject policy => deny.
62. Unknown field disappears under preserve/exact policy => deny.
63. Descriptor/schema digest changes => deny until new declaration/fixtures.
64. Deterministic serialized bytes differ but declared field projection equal => pass only for admitted field-aware extractor.
65. Bytes equal under wrong schema generation => deny.
66. Default/presence semantics change => deny.
67. RPC method mutation => deny.
68. Metadata carrying tenant/version semantics mutates => deny.

### G. Final-request / runtime integrity (69-80)
69. Attestation performed before signing middleware => deny.
70. Middleware mutates semantic header after attestation => deny.
71. Middleware mutates body after attestation => deny.
72. Lazy signer output unobservable pre-send => deny adapter.
73. Frozen request object sent unchanged => pass.
74. Attestation references wrong attempt/lease => deny.
75. Attestation references wrong replay capsule => deny.
76. Semantic digests differ => deny.
77. Fixture positive case unexpectedly fails => quarantine adapter generation.
78. Fixture negative mutation unexpectedly passes => quarantine adapter generation.
79. Provider-capability retry horizon expired despite equivalence PASS => no mutation retry.
80. Quarantine/challenge active despite equivalence PASS => no mutation retry.

## Implementation boundary

This document freezes the contract only. Do not add production mutation authority from this design without executable RED/GREEN at the same abstraction level, exact provider-specific fixture coverage, and composition with the already frozen authority/provenance/retry/quarantine contracts.

A first implementation should be offline/read-only:

- pure `extract_capsule_semantics()`;
- pure `extract_final_request_semantics()` over a frozen synthetic request type;
- domain-separated canonical digest;
- signed fixture loader/verifier;
- negative fixture coverage checker;
- adapter-generation compatibility verifier.

Only after those tests pass should the extractor be wired to the final pre-I/O authority gate.
