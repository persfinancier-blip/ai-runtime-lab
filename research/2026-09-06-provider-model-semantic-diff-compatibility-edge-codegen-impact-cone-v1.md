# PROVIDER_MODEL_SEMANTIC_DIFF_COMPATIBILITY_EDGE_CODEGEN_IMPACT_CONE_V1_FROZEN

Date: 2026-09-06
Status: FROZEN DESIGN CONTRACT — no production implementation or behavioral PASS claimed
Parent: LAB-093 / issue #178
Priority note: LAB-086 remains priority #1; this is the recorded distinct fallback while exact byte-preserving LAB-086 publication/execution remains unavailable.

## 1. Objective

Turn two already-admitted provider-model generations into a machine-verifiable, directional compatibility decision rather than a blanket `backward compatible` label.

The contract must answer five different questions independently:

1. Does the new generation preserve the request-effect semantics needed to send the same consequential request?
2. Can a runtime generated from the new generation parse and verify historical evidence created under the old generation?
3. Can the new runtime replay an old immutable capsule without silently changing provider-visible meaning?
4. Can an old runtime safely consume evidence emitted under the new generation?
5. Which generated DTOs, serializers, semantic extractors, replay adapters, reconciliation parsers, disclosure policies, fixtures, and provider-capability manifests must be regenerated or invalidated by this exact model delta?

A single package version, API version string, semver range, Smithy Diff result, protobuf wire-compatibility label, or OpenAPI diff verdict is not sufficient authority for any of the above.

## 2. Inputs and immutable identity

The diff engine accepts only two provider-model generations that already satisfy `PROVIDER_MODEL_NORMALIZATION_TRANSITIVE_REFERENCE_CLOSURE_REGISTRY_FRONTIER_ADMISSION_V1_FROZEN`.

Each endpoint of an edge is identified by at least:

- `provider_id`
- `service_id`
- `operation_set_id`
- `raw_source_set_digest`
- `normalized_semantic_closure_digest`
- `normalizer_generation`
- `closure_manifest_digest`
- `provider_evidence_schema_generation`
- `policy_generation`
- `codegen_toolchain_digest`

No human-readable version label substitutes for these identities.

The compatibility-edge attestation additionally commits to:

- `from_generation_digest`
- `to_generation_digest`
- `semantic_diff_engine_generation`
- `diff_graph_digest`
- `impact_cone_digest`
- exact generated-artifact digests after required regeneration
- exact positive/negative fixture-set digests
- directional verdict vector
- signer/authority generation and global registry frontier

## 3. Normalized semantic graph

The diff engine operates on a typed normalized graph, not line-oriented source text.

### 3.1 Required node classes

At minimum:

- service
- operation
- request/input structure
- response/output structure
- error shape
- field/member
- enum/union variant
- scalar/container target
- endpoint/routing binding
- HTTP method/path/query/header/prefix-header/payload/document binding
- auth/signing trait
- idempotency token/client token
- retryability/error classification
- pagination/waiter semantics where consequential reconciliation depends on them
- default/presence/nullability/requiredness semantics
- serialization protocol and media type
- request/response compression or streaming semantics
- sensitive/logging/evidence classification traits
- provider-native extension/options that affect wire, validation, auth, retry, or reconciliation semantics

### 3.2 Required edge classes

At minimum:

- operation -> input/output/error
- member -> target
- member -> wire binding
- member -> default/presence constraint
- shape -> trait/option
- operation -> endpoint/auth/retry/protocol traits
- schema -> transitive imported/referenced source
- generated artifact -> source semantic nodes
- evidence field -> source provider-model nodes
- semantic extractor rule -> source provider-model nodes
- replay mapping -> source provider-model nodes
- reconciliation parser -> response/error nodes
- disclosure policy -> evidence/model nodes

The final five dependency edge classes are mandatory because the impact cone must be computable, not guessed after the model diff.

## 4. Canonical delta vocabulary

Every normalized delta is represented as a typed record. At minimum:

- `NODE_ADD`
- `NODE_REMOVE`
- `NODE_RENAME_CANDIDATE`
- `TARGET_CHANGE`
- `WIRE_LOCATION_CHANGE`
- `WIRE_NAME_CHANGE`
- `HTTP_METHOD_CHANGE`
- `HTTP_PATH_CHANGE`
- `ENDPOINT_SCOPE_CHANGE`
- `AUTH_TRAIT_CHANGE`
- `SIGNING_SCOPE_CHANGE`
- `REQUIREDNESS_CHANGE`
- `PRESENCE_CHANGE`
- `NULLABILITY_CHANGE`
- `DEFAULT_ADD`
- `DEFAULT_REMOVE`
- `DEFAULT_VALUE_CHANGE`
- `ENUM_ADD`
- `ENUM_REMOVE`
- `UNION_VARIANT_ADD`
- `UNION_VARIANT_REMOVE`
- `OPEN_WORLD_CHANGE`
- `CONSTRAINT_TIGHTEN`
- `CONSTRAINT_RELAX`
- `ERROR_ADD`
- `ERROR_REMOVE`
- `ERROR_CLASSIFICATION_CHANGE`
- `RETRY_TRAIT_CHANGE`
- `IDEMPOTENCY_TRAIT_CHANGE`
- `SERIALIZATION_PROTOCOL_CHANGE`
- `MEDIA_TYPE_CHANGE`
- `COMPRESSION_CHANGE`
- `STREAMING_CHANGE`
- `SENSITIVE_TRAIT_CHANGE`
- `UNKNOWN_EXTENSION_ADD/REMOVE/CHANGE`
- `TRANSITIVE_SOURCE_CHANGE`
- `CUSTOM_OPTION_CHANGE`

Every delta includes old/new node identity, exact semantic paths, old/new canonical value commitments, and provenance back to raw source members.

## 5. No automatic rename inference

A remove+add pair MUST NOT be silently collapsed into a rename because names may carry wire, codegen, logging, disclosure, reconciliation, or human-operational meaning.

`NODE_RENAME_CANDIDATE` is advisory only. It can be promoted to an explicitly declared rename edge only if a provider-specific rule or signed migration mapping proves:

- old and new wire identities;
- old and new effect semantics;
- replay mapping;
- evidence mapping;
- reconciliation mapping;
- required artifact regeneration.

Similarity heuristics, edit distance, neighboring position, matching descriptions, or equal scalar type are never authority evidence.

## 6. Five-dimensional impact classification

Each atomic delta receives a conservative vector:

`impact = { request_effect, replay, evidence, reconciliation, disclosure }`

Each dimension is one of:

- `NO_IMPACT_PROVED`
- `REGENERATE_REQUIRED`
- `COMPATIBILITY_PROOF_REQUIRED`
- `BREAKING`
- `UNKNOWN_FAIL_CLOSED`

### 6.1 Request-effect impact

Examples:

- request HTTP method/path/wire location/signing scope change => `BREAKING` unless a provider-specific equivalence proof exists;
- optional response-only documentation trait => potentially `NO_IMPACT_PROVED` for request-effect;
- insertion of a request default => at least `COMPATIBILITY_PROOF_REQUIRED`, because an omitted historical value may begin producing provider-visible bytes or different validation behavior;
- idempotency/retry trait change => consequential effect boundary; never classify from type compatibility alone.

### 6.2 Replay impact

Replay asks whether an old immutable capsule can be transformed under the new generation without semantic invention or information loss.

A field removal may be wire-compatible for a parser but still replay-breaking because the old capsule contains an authority-relevant value that the new serializer would discard.

A field addition may be replay-safe only if historical omission has precisely defined semantics and the serializer is proven not to synthesize a consequential new default.

### 6.3 Evidence impact

Evidence impact is independent of request-effect.

Examples:

- response error enum widening may leave requests unchanged but require regenerated error DTOs/evidence schema;
- a `sensitive` trait addition requires evidence/log/disclosure regeneration even if wire bytes do not change;
- a newly modeled unknown extension is evidence-impacting until classified.

### 6.4 Reconciliation impact

Any delta that can change success/error classification, operation status lookup, idempotency reconciliation, pagination of authoritative history, retry safety, or provider terminal-state parsing is reconciliation-impacting.

### 6.5 Disclosure impact

Changes to sensitivity, identifiers, response fields, error metadata, headers or nested model openness can require policy recompilation even when runtime request/replay semantics remain compatible.

## 7. Directional compatibility edges

Compatibility is an edge, not an intrinsic property of one model.

For every admitted pair `A -> B`, compute independent booleans/verdicts:

1. `B_ACCEPTS_A_EVIDENCE`
2. `B_REPLAYS_A_CAPSULE`
3. `A_ACCEPTS_B_EVIDENCE`
4. `B_EMITS_REQUEST_EFFECT_EQUIVALENT_TO_A_FOR_A_CAPSULE`
5. `B_RECONCILES_A_OUTCOMES`
6. `B_DISCLOSES_A_EVIDENCE_UNDER_POLICY`

The reverse edge `B -> A` is a separate attestation. Symmetry must never be inferred.

A model delta may therefore be:

- safe for new-runtime parsing of old evidence;
- unsafe for old-runtime parsing of new evidence;
- safe for request generation;
- unsafe for historical replay;
- safe for replay;
- unsafe for disclosure because sensitivity policy changed.

## 8. Compatibility proof types

A directional verdict is admissible only through one or more explicit proof types.

### 8.1 Structural proof

Uses graph rules that are known to preserve the relevant dimension. Example: a Smithy mixin source refactor whose fully assembled semantic model is identical can prove no generated-artifact change if the normalized semantic closure is exactly equal.

### 8.2 Golden semantic fixture proof

For each affected operation, execute canonical old and new mappings over fixtures and compare the authority-relevant canonical projections. Required for changes involving defaults, presence, enum openness, wire bindings, or serializers where structural rules alone are insufficient.

### 8.3 Negative distinguishing fixture proof

Every compatibility claim must include at least one fixture capable of detecting the prohibited semantic change. Positive equality-only tests are insufficient.

### 8.4 Provider-specific migration proof

Required when semantics are intentionally changed but a safe mapping exists. The mapping itself is versioned, content-addressed, signed/authorized, and included in the impact cone.

### 8.5 Historical evidence/replay corpus proof

For admitted historical generations retained by the registry, a new generation must be exercised against representative and boundary fixtures from historical evidence/capsules for every compatibility edge it claims.

## 9. Codegen impact cone

The diff graph is traversed into generated/runtime artifacts. An artifact is invalidated if any source node on which it semantically depends changes and the dependency edge is not covered by a proved no-impact rule.

Artifact classes include at minimum:

- request closed DTO
- response closed DTO
- error closed DTO
- serializer
- deserializer
- final-request semantic extractor
- replay capsule encoder/decoder
- replay adapter/migration map
- evidence projection
- reconciliation parser/state classifier
- idempotency mapper
- retry classifier
- selective-disclosure policy bundle
- log/trace/metric projection
- provider capability/admission manifest
- golden fixture generator

Partial regeneration is rejected when any invalidated artifact remains bound to the old generation.

The admitted runtime stores an `artifact_generation_vector` and startup verifies that every operation/capability points to artifacts derived from one coherent source-generation/policy-generation edge set.

## 10. Critical delta rules

### 10.1 Defaults

Adding or changing a default is never assumed harmless. Classify separately:

- parser default only;
- serializer-emitted default;
- provider service-side default;
- SDK constructor default;
- codegen language default.

If these cannot be distinguished from captured model/toolchain evidence, result is `UNKNOWN_FAIL_CLOSED`.

### 10.2 Presence / requiredness / nullability

Type-level source compatibility does not prove semantic compatibility. Omitted, explicit null, zero/empty, and defaulted values remain distinct until the protocol/model proves equivalence.

### 10.3 Enum / union widening

An added response enum/union value can be forward-compatible only for consumers designed for unknown values. Closed generated evidence DTOs or exhaustive old-runtime classifiers can make `A_ACCEPTS_B_EVIDENCE=false` even if the wire protocol itself tolerates the new value.

An added request enum value does not by itself affect replay of old capsules, but it invalidates any claim that old and new accepted-input domains are identical.

### 10.4 Unknown/open extensions

A newly introduced `additionalProperties`, protobuf unknown field/extension, `Any`, `Struct`, Smithy trait, OpenAPI extension, or provider-native options surface is `UNKNOWN_FAIL_CLOSED` until the evidence-schema/policy compiler explicitly classifies it.

### 10.5 Error changes

Error additions/removals/classification changes are always checked against reconciliation and retry semantics, not merely response parser compatibility.

### 10.6 Semantically equivalent raw drift

If raw-source digest changes but normalized semantic closure remains exactly equal under the same normalizer generation, semantic diff may be empty, but provenance remains distinct. The compatibility edge can prove semantic equivalence; it must not coalesce the generations or erase raw attribution.

### 10.7 Transitive changes

A top-level operation file unchanged while an imported/ref'd target changes is treated exactly like a direct semantic delta. Closure membership and edge changes are first-class diff inputs.

## 11. Admission algorithm

For candidate generation `B` replacing active `A`:

1. verify both registry endpoints and global frontier;
2. compute typed semantic diff graph from admitted normalized closures;
3. reject unresolved or unclassified deltas;
4. classify all five impact dimensions;
5. compute artifact impact cone;
6. regenerate every invalidated artifact in an isolated candidate set;
7. bind candidate artifacts to exact source/policy/codegen generations;
8. generate minimal positive and negative fixtures from every non-trivial delta class;
9. execute directional evidence/replay/request-effect/reconciliation/disclosure proofs;
10. emit signed compatibility-edge attestation;
11. atomically admit the new provider capability generation only after every required edge is present;
12. retain old generation, old artifacts, edge attestations and fixtures needed for historical verification/replay.

No runtime may activate generation `B` merely because codegen succeeds or an upstream schema tool reports `compatible`.

## 12. Donor mechanisms and evidence

### Smithy

Primary source: https://smithy.io/2.0/guides/evolving-models.html

Smithy explicitly distinguishes backward-compatible and incompatible model changes and states that trait changes may be breaking when they change wire representation or relied-upon tooling behavior. It also exposes Smithy Diff for model comparison.

Primary source: https://smithy.io/2.0/spec/model.html

Smithy trait definitions can declare `breakingChanges` diff rules, but the specification explicitly notes that not every breaking change can be expressed through that mechanism and recommends custom diff tooling where necessary. This supports LAB's stricter dimension-specific compatibility layer rather than treating one upstream verdict as sufficient.

Primary source: https://smithy.io/2.0/spec/mixins.html

Smithy mixins are model implementation details that should be flattened/elided for code generation; removing a mixin while preserving equivalent applied members/traits is described as backward-compatible. This is a useful donor for semantic-vs-raw differentiation.

### Protocol Buffers

Primary source: https://protobuf.dev/programming-guides/proto2/#updating

Protobuf documents binary wire-safe and wire-unsafe schema changes. This is valuable transport compatibility evidence, but LAB deliberately does not equate binary wire compatibility with replay/evidence/reconciliation compatibility.

Primary source: https://protobuf.dev/news/2026-07-13/

The Protobuf project documents Edition 2026 default/codegen changes, illustrating why a provider-model edge also binds the codegen/toolchain generation rather than only schema bytes.

### JSON Schema / OpenAPI

Primary source: https://json-schema.org/blog/posts/stable-json-schema

JSON Schema's own compatibility work distinguishes specification evolution and acknowledges historical backward-incompatible changes. LAB therefore treats dialect/vocabulary generation as part of semantic identity and does not import a universal compatibility assumption.

OpenAPI compatibility is operation/use-context specific; LAB consumes normalized OpenAPI/JSON Schema semantics from the previously frozen model-normalization contract and applies the same five-dimensional edge proof rather than relying on a generic source diff.

## 13. RED-first matrix — 80 cases

Freeze at least the following 80 cases before production implementation.

### A. Identity / empty semantic diff (1-8)
1. identical raw + normalized generation => empty diff
2. raw whitespace/comment drift with equal normalized closure => provenance distinct, semantic diff empty
3. equal top-level source but changed transitive import => non-empty diff
4. changed normalizer generation with equal result => requires explicit cross-normalizer equivalence
5. source-generation endpoint mismatch => reject edge
6. stale registry frontier => reject edge
7. missing closure manifest => reject edge
8. diff graph digest mismatch after serialization => reject edge

### B. Rename / remove / target (9-16)
9. field remove+add with similar names must not auto-rename
10. explicit signed rename mapping admitted
11. request field rename with wire-name preserved but codegen name changed
12. request wire-name rename => request-effect breaking
13. response member rename => evidence/reconciliation impact
14. target scalar type change wire-compatible but validation-changing
15. operation rename/remove => breaking
16. error-shape rename => reconciliation impact

### C. Defaults / presence / requiredness (17-28)
17. request default added but serializer omits value
18. request default added and serializer emits value
19. provider-side default changes
20. SDK constructor default changes with model unchanged
21. default value changed
22. default removed
23. optional -> required request field
24. required -> optional request field
25. omitted vs explicit null distinguished
26. empty string vs omitted distinguished
27. zero vs absent distinguished
28. default semantics unresolvable => fail closed

### D. Enums / unions / open world (29-38)
29. response enum value added; new runtime accepts old
30. response enum value added; old closed DTO rejects new evidence
31. request enum value added; old replay unaffected
32. enum value removed that appears in historical capsule
33. union response variant added with unknown-variant support
34. union response variant added without old unknown support
35. open extension map added
36. open extension map removed
37. protobuf unknown field preserved but evidence DTO drops it
38. `Any`/`Struct` newly introduced => fail closed until classified

### E. Wire/auth/effect (39-50)
39. HTTP method change
40. path template change
41. request field header -> body
42. query -> header
43. wire name change
44. endpoint/account/region scope change
45. signing scope change
46. auth scheme change
47. idempotency trait added
48. idempotency trait removed
49. retryability trait changes
50. request compression/streaming trait changes

### F. Errors / reconciliation (51-58)
51. new terminal success response variant
52. new retriable error
53. error retriable -> terminal
54. error terminal -> retriable
55. error code wire binding changes
56. status lookup operation response field changes
57. pagination token semantics change
58. reconciliation-required response field removed

### G. Impact cone / partial regeneration (59-70)
59. request DTO invalidated
60. serializer invalidated
61. final-request extractor invalidated
62. replay adapter invalidated
63. evidence DTO invalidated
64. reconciliation parser invalidated
65. disclosure policy invalidated by sensitivity trait change
66. logs/traces projection invalidated
67. generated artifact claims new source but retains old digest => reject
68. one artifact omitted from regeneration => reject
69. mixed policy generations in one operation capability => reject
70. codegen toolchain changed with source equal => directional proof required

### H. Directionality / historical edges (71-80)
71. B accepts A evidence, A rejects B evidence
72. B replays A, A cannot replay B
73. B request-effect equivalent for A capsules but accepts additional new requests
74. B parses A evidence but reconciliation classifier changes => edge incomplete
75. reverse edge absent => no inferred symmetry
76. historical generation missing required artifact => no replay admission
77. fixture set lacks negative distinguisher => reject compatibility proof
78. migration map unsigned/unbound to endpoints => reject
79. old source archived but codegen generation unavailable => verification-only allowed, replay edge false
80. rollback to A after B frontier advanced without authorized rollback edge => reject

## 14. Frozen decisions

- Compatibility is directional and dimension-specific.
- Generic `backward compatible` is not a consequential authority claim.
- Raw-source identity and normalized-semantic identity remain separate.
- Semantic diff is graph-based and includes transitive dependencies.
- Rename inference is never automatic authority evidence.
- Defaults/presence/nullability are effect semantics, not cosmetic type metadata.
- Wire compatibility does not imply replay, evidence, reconciliation, or disclosure compatibility.
- Artifact invalidation is computed from explicit dependency edges; partial regeneration fails closed.
- Historical evidence remains bound to the original source/artifact generations.
- Every admitted compatibility edge is content-addressed, fixture-backed, directional, and frontier-bound.

## 15. Next implementation slice

When exact executable source becomes available for LAB-093, implement RED first for:

1. normalized typed diff records for request members and wire/default/presence semantics;
2. artifact dependency manifest + impact-cone traversal;
3. directional edge object and attestation digest;
4. fixtures covering default insertion, enum widening, response error reclassification, semantically equivalent raw drift, transitive target change, false rename inference and partial regeneration;
5. only then implement provider-specific Smithy/OpenAPI/protobuf adapters.

Until then, no production compatibility engine or PASS is claimed.