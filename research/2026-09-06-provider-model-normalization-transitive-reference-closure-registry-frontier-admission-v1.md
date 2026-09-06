# Provider Model Normalization / Transitive-Reference Closure / Registry Frontier Admission Contract V1

Date: 2026-09-06  
Status: **FROZEN DESIGN / RED-FIRST — no production implementation or behavioral PASS claimed**  
Primary follow-up: LAB-093 / #178  
Priority note: LAB-086 / #163 remains priority #1 and is not superseded.

## Why this contract exists

The previous provider evidence-schema registry contract binds consequential provider capability to an exact evidence-schema generation derived from provider model material, canonical mappings, policy generation and generated artifacts. That still leaves a dangerous ambiguity one layer below the registry: **what exact bytes and reference closure constitute “the provider model”?**

A stable entry file is not sufficient evidence when:
- OpenAPI or JSON Schema `$ref` targets can resolve through mutable remote URIs or a changed `$id`/base URI;
- Smithy traits can be applied outside a shape definition and model assembly can combine multiple model files;
- protobuf descriptors depend on imported files and custom options whose definitions live in transitive descriptor dependencies;
- provider-native schema bundles load fragments through package manifests, filenames, API-version directories or runtime plugins;
- two different raw documents normalize to one representation because a normalizer discards an unknown extension, source identity, order that is actually semantically meaningful, or duplicate/conflicting input;
- a restored registry is internally valid but older than model generations already admitted elsewhere.

The frozen rule is:

> **Consequential admission binds both immutable raw-source identity and a versioned normalized semantic closure. Every reference/import/descriptor dependency required to interpret the admitted provider surface is resolved from an authenticated captured source set, never lazily from mutable network location. Registry history is append-only under an authenticated global frontier, and rollback or source replacement cannot silently reuse an existing generation identity.**

This contract deliberately does **not** claim that a universal cross-format semantic canonicalization exists. Raw identity and normalized semantic identity serve different purposes and both are retained.

## Primary-source donor mechanisms

1. **Smithy JSON AST and model assembly.** Smithy JSON AST uses absolute shape IDs, and traits can be applied externally through `apply`. Therefore an isolated shape definition is not a complete semantic unit; the assembled model and all applied traits that affect reachable shapes are material.
2. **OpenAPI 3.1 reference/base-URI semantics.** OpenAPI 3.1 inherits JSON Schema reference processing. Relative Schema Object references and `$id` values depend on the nearest base URI, and the specification warns that parsing referenced fragments without the complete containing document can miss keywords that change base-URI interpretation and creates security risk.
3. **JSON Schema 2020-12 loading/base identity.** JSON Schema defines an initial base URI and allows `$id` to establish canonical schema-resource identifiers. Retrieval location and schema identity therefore must not be conflated.
4. **Protocol Buffers descriptor dependency graph.** A protobuf `FileDescriptor` contains descriptors for its imported `.proto` dependencies, and `FileDescriptorSet` is the compiler-emitted set of parsed file descriptors. Protobuf serialization itself is explicitly not canonical across builds/schema evolution, so LAB must define its own descriptor normalization rather than hashing arbitrary serialized descriptor messages as durable semantic identity.

Primary references:
- Smithy JSON AST: https://smithy.io/2.0/spec/json-ast.html
- Smithy model: https://smithy.io/2.0/spec/model.html
- OpenAPI 3.1.1: https://spec.openapis.org/oas/v3.1.1.html
- JSON Schema 2020-12 core: https://json-schema.org/draft/2020-12/draft-bhutton-json-schema-00
- Protobuf descriptors: https://protobuf.dev/reference/java/api-docs/com/google/protobuf/Descriptors.FileDescriptor.html
- Protobuf FileDescriptorSet: https://protobuf.dev/reference/java/api-docs/com/google/protobuf/DescriptorProtos.FileDescriptorSet
- Protobuf serialization is not canonical: https://protobuf.dev/programming-guides/serialization-not-canonical/

## 1. Two identities, never one

Each captured model generation has two separate commitments.

### 1.1 RawSourceSetDigest

`raw_source_set_digest` commits to the exact captured source objects before semantic normalization:

```text
RawSourceObjectV1 {
    source_object_id          # immutable internal capture ID
    media_type
    declared_format
    exact_bytes_digest
    exact_length
    retrieval_provenance
    declared_uri_or_name
    capture_time
}

RawSourceSetV1 {
    normalizer_generation
    entry_object_ids[]
    source_objects[]          # sorted by source_object_id, not retrieval order
}
```

The raw digest exists to detect source replacement, parser/normalizer regressions and normalization collisions. A URL, package version, filename, API date or registry label is metadata, not source identity.

### 1.2 NormalizedSemanticClosureDigest

`normalized_semantic_closure_digest` commits to the versioned normalized graph actually used for compatibility analysis/code generation.

It is computed only after:
1. all references are resolved against the captured source set;
2. the complete reachable closure is known;
3. duplicate/conflicting identities are rejected;
4. unknown extensions with possible semantic relevance are classified or rejected;
5. format-specific normalization succeeds under an exact `normalizer_generation_id`.

The normalized digest never replaces the raw digest. Admission records both.

## 2. Deterministic capture before resolution

Remote references MUST NOT be fetched during startup, replay, verification or code generation of an already registered generation.

A candidate capture procedure may fetch model sources during an explicit model-ingestion operation, but before admission it must materialize every fetched object into the immutable `RawSourceSetV1` and bind:
- exact bytes digest;
- retrieval URI and redirect chain as provenance only;
- authenticated source/package provenance where available;
- content type / declared model format;
- fetch policy generation;
- all references observed during closure construction.

Subsequent normalization resolves only against captured objects by content identity and captured URI mapping. A network resource changing after capture cannot change a registered generation.

If a reference cannot be resolved from the captured set, the generation is incomplete and consequential admission fails closed.

## 3. Transitive-reference closure

Define a format-independent graph:

```text
ModelNodeV1 {
    node_id
    source_object_id
    local_identity
    normalized_payload
}

ModelEdgeV1 {
    from_node_id
    edge_kind                # smithy-target | trait | ref | import | option | extension | provider-native
    reference_text
    resolved_to_node_id
    resolution_context
}
```

Starting from every consequential operation entrypoint, closure traversal continues until every authority-relevant target is resolved.

Closure MUST include not merely request/response root messages but also:
- nested structures/messages/unions/maps/lists;
- enum definitions and aliases;
- traits/annotations/options affecting requiredness, defaults, sensitivity, wire location, idempotency, error behavior or serialization;
- custom annotation definitions needed to interpret applied annotations;
- error shapes and metadata reachable from the operation;
- shared/global definitions referenced by reachable nodes;
- discriminator/mapping targets where they affect accepted provider payloads;
- schemas used by middleware or generated-client defaults when they can alter provider-visible semantics.

A cycle is legal only if the format permits it and every node in the cycle is resolved unambiguously. The digest is over a canonical graph representation, not recursive textual expansion.

## 4. Smithy normalization profile

`SMITHY_NORMALIZER_V1` consumes a fully assembled Smithy model, not isolated IDL files.

Required rules:
- convert admitted input to one validated Smithy semantic model before normalization;
- identify shapes by absolute shape ID;
- apply all external `apply` trait statements before computing reachable semantics;
- include member traits separately from target-shape traits because member traits can override/refine target behavior;
- include service/operation/resource relationships required to interpret the admitted operation;
- preserve unknown custom traits unless explicitly classified irrelevant; do not silently discard them;
- sort maps/sets only where Smithy semantics make ordering irrelevant;
- reject conflicting duplicate shape definitions or trait applications rather than selecting by load order;
- record the Smithy specification/model-loader generation used to assemble the model.

Human-only documentation traits may be classified non-authority-relevant, but that classification belongs to the normalizer/policy generation and cannot be inferred ad hoc.

## 5. OpenAPI / JSON Schema normalization profile

`OPENAPI_JSONSCHEMA_NORMALIZER_V1` treats URI resolution as semantic material.

Required rules:
- parse the complete containing document before reference resolution where OpenAPI/JSON Schema rules require it;
- derive base URI exactly under the applicable OpenAPI + JSON Schema dialect/version;
- capture and bind every `$id`, `$anchor`, `$dynamicAnchor`, `$ref`, `$dynamicRef` or OAS Reference Object used by an admitted surface;
- distinguish retrieval URI from canonical schema-resource URI;
- resolve relative references only inside the captured source map;
- preserve JSON Schema dialect and vocabulary identity;
- reject an unsupported/unknown vocabulary if it can affect validation or instance semantics;
- preserve unknown OpenAPI extensions (`x-*`) until explicitly classified; they may be consumed by code generators/middleware;
- reject ambiguous duplicate canonical resource IDs/anchors;
- do not normalize fragments in isolation when parent-document base-URI context can alter resolution;
- preserve `additionalProperties`, unevaluated-properties semantics and other open-world controls because they affect DTO closure.

Canonical key ordering may be used for normalized representation, but only after duplicate-key handling and dialect-specific parsing rules have been fixed. Duplicate JSON/YAML keys are rejected rather than normalized by parser-specific “first wins” or “last wins”.

## 6. Protobuf normalization profile

`PROTOBUF_NORMALIZER_V1` starts from an exact descriptor closure rather than generated-language classes.

Required rules:
- capture `FileDescriptorProto` semantic fields for each reachable file;
- resolve every declared import to one exact captured descriptor;
- include public and weak dependency semantics where supported by the admitted edition/runtime;
- include custom options and the descriptor files defining those options when the options can affect generated/runtime behavior;
- include syntax/edition, package, type names, field numbers/types/labels/presence, oneofs, maps, enums, reserved names/numbers, services/methods and relevant features/options;
- reject unresolved dependencies; never use “allow unknown dependencies” placeholder semantics for consequential admission;
- preserve unknown descriptor/options material until explicitly classified;
- do **not** use generic deterministic protobuf serialization as the semantic digest representation.

Protobuf’s own documentation states deterministic serialization is not canonical across languages/builds/schema evolution. Therefore the normalized representation is a LAB-defined field-by-field canonical structure with explicit handling for unknown fields/options.

## 7. Provider-native normalization profile

A provider-native schema may be admitted only with a registered normalizer profile declaring:
- parser/tool identity;
- reference/import mechanisms;
- extension/plugin mechanisms;
- ordering semantics;
- default/presence semantics;
- unknown-field policy;
- duplicate identity policy;
- closure algorithm;
- normalized representation version.

“JSON-like”, “generated SDK model” or “package files” is not sufficient. If the provider format cannot define a closed deterministic capture and closure, consequential capability remains unadmitted.

## 8. Normalization-collision resistance

A semantic normalizer intentionally maps some different raw representations to one normalized meaning. That is acceptable only where equivalence is explicitly specified.

For each admitted generation store:

```text
raw_source_set_digest
normalized_semantic_closure_digest
normalizer_generation_id
closure_manifest_digest
```

Two different raw source sets producing the same normalized digest are **not** silently coalesced into one source generation. The registry records both raw identities and requires an explicit normalizer-defined equivalence reason.

The following are collision/admission blockers unless explicitly covered by the normalizer:
- parser-dependent duplicate keys;
- integer/float textual coercion that changes schema meaning;
- Unicode normalization of identifiers not mandated by the model format;
- case folding of case-sensitive identifiers;
- dropping unknown traits/extensions/options;
- treating absent and explicit default as equal when the format/runtime distinguishes them;
- sorting semantically ordered arrays/lists;
- resolving two different source URIs to one node merely because filenames match.

A normalizer-generation change always yields a new registry generation even when the normalized digest happens to be equal.

## 9. Closure manifest

Every generation stores a deterministic closure manifest:

```text
ModelClosureManifestV1 {
    entrypoints[]
    source_object_digests[]
    normalized_node_ids[]
    edge_records[]
    unresolved_references[]      # MUST be empty for admission
    unknown_extensions[]         # MUST all have classifications
    duplicate_identity_findings[]# MUST be empty
    normalizer_generation_id
}
```

The manifest allows audits to prove why a source was included and prevents a later implementation from silently shrinking the dependency set.

A top-level model digest without the closure manifest is insufficient evidence.

## 10. Authenticated source provenance

Source provenance strengthens supply-chain confidence but does not substitute for content identity.

Where available record:
- provider-published repository/release identity;
- commit/release digest;
- signed release/attestation identity;
- package registry integrity digest;
- TLS/retrieval metadata as non-authoritative provenance;
- capture tool generation.

A trusted URL or signed package label cannot authorize changed bytes under an existing schema generation. Conversely, exact bytes captured from an unauthenticated mirror may be useful for forensic comparison but are not automatically admitted as a trusted new provider generation.

Admission policy independently checks content identity and required provenance level.

## 11. Registry append/frontier model

Provider-model generations are append-only records in the authenticated authority history.

```text
ProviderModelGenerationV1 {
    generation_id
    provider_id
    api_id
    predecessor_generation_id
    raw_source_set_digest
    normalized_semantic_closure_digest
    closure_manifest_digest
    normalizer_generation_id
    provenance_digest
    compatibility_edges_digest
    status                       # CANDIDATE | ADMITTED | REVOKED | HISTORICAL
}
```

`generation_id` is domain-separated over all authority-relevant fields. It is never reused.

The registry maintains an authenticated `model_registry_frontier` committing to the latest recognized generation sequence. A local DB snapshot is not sufficient authority to establish the frontier.

Consequential startup verifies:
1. local registry chain integrity;
2. external/global authenticated frontier continuity;
3. all capability-bound model generations are recognized by that frontier;
4. no local generation was replaced by another object with the same mutable provider/API/version labels.

## 12. Source replacement and same-version drift

Providers can republish schemas under the same API version/date/package version. Therefore mutable labels never imply byte identity.

If newly captured bytes differ under the same labels:
- create a new candidate generation;
- compute raw and normalized diffs;
- classify every authority-relevant semantic delta;
- require directional compatibility admission;
- preserve both historical generations;
- never rewrite the old generation in place.

If raw bytes differ but normalized semantics are equal under the same normalizer, the new raw generation may be marked semantic-equivalent only after the normalizer’s equivalence conditions and provenance rules pass. It still receives distinct raw-source identity.

## 13. Rollback, restore and archive continuity

Archive/restore must preserve:
- every referenced raw source object needed to reproduce an admitted/historical normalized closure;
- closure manifests;
- normalizer generation artifacts/specification;
- authenticated registry chain/frontier evidence;
- compatibility attestations.

Restoring an internally valid old archive is rejected for consequential use when its frontier is behind the externally known monotonic frontier.

A downgrade to an older provider model is allowed only through an authenticated directional compatibility edge and only if the generation remains recognized by current frontier authority. “It was supported last month” is not sufficient.

Compaction may deduplicate identical content-addressed raw blobs, but cannot remove the logical source-object membership/provenance needed to reproduce historical closure.

## 14. Admission algorithm

For a candidate provider model:

1. Capture candidate entry source(s) exactly.
2. Discover references/imports using the format-specific parser without trusting network content by mutable name alone.
3. Materialize every dependency into the immutable source set.
4. Repeat discovery until fixpoint; reject unresolved references.
5. Validate duplicate identities, cycles and format rules.
6. Assemble the semantic model under the exact parser/model-loader generation.
7. Compute `raw_source_set_digest`.
8. Normalize under the exact registered normalizer generation.
9. Emit deterministic closure manifest and compute `closure_manifest_digest`.
10. Compute `normalized_semantic_closure_digest`.
11. Diff both raw and normalized identities against predecessor generation.
12. Run field/evidence-schema compatibility classification and generated closed DTO regeneration.
13. Execute format-specific positive/negative golden fixtures.
14. Append candidate generation to authenticated registry history.
15. Admit consequential capability only after required compatibility/provenance approvals and global frontier advancement are durable.

Any unclassified unknown extension, unresolved reference, ambiguous identity, unsupported parser behavior or frontier discontinuity is fail-closed.

## 15. RED-first 80-case matrix

| # | Group | Case | Required outcome |
|---:|:---:|---|---|
| 1 | A | identical raw source set reproduces identical raw digest | RED before implementation; GREEN required |
| 2 | A | one-byte source change changes raw digest | RED before implementation; GREEN required |
| 3 | A | source-set membership change changes raw digest | RED before implementation; GREEN required |
| 4 | A | retrieval order does not change raw digest | RED before implementation; GREEN required |
| 5 | A | mutable URL/version label change alone does not masquerade as content change | RED before implementation; GREEN required |
| 6 | A | same label with changed bytes becomes a distinct raw generation | RED before implementation; GREEN required |
| 7 | A | unsupported media/model format is rejected | RED before implementation; GREEN required |
| 8 | A | duplicate source-object identity with different bytes is rejected | RED before implementation; GREEN required |
| 9 | B | normalized digest is stable for permitted irrelevant map-order differences | RED before implementation; GREEN required |
| 10 | B | semantically ordered list reordering changes normalized digest | RED before implementation; GREEN required |
| 11 | B | unknown extension is not silently dropped | RED before implementation; GREEN required |
| 12 | B | case-sensitive identifier case change changes normalized identity | RED before implementation; GREEN required |
| 13 | B | absent vs explicit default remains distinct where semantics require | RED before implementation; GREEN required |
| 14 | B | normalizer-generation change creates a new registry generation | RED before implementation; GREEN required |
| 15 | B | two raw sets with equal normalized digest remain separately attributable | RED before implementation; GREEN required |
| 16 | B | duplicate JSON/YAML key is rejected rather than parser-order normalized | RED before implementation; GREEN required |
| 17 | C | direct reference target is included in closure | RED before implementation; GREEN required |
| 18 | C | reference-of-reference is included transitively | RED before implementation; GREEN required |
| 19 | C | unreachable source object is excluded from semantic closure but remains raw capture provenance when captured | RED before implementation; GREEN required |
| 20 | C | unresolved transitive reference blocks admission | RED before implementation; GREEN required |
| 21 | C | permitted reference cycle terminates deterministically | RED before implementation; GREEN required |
| 22 | C | conflicting cycle identity is rejected | RED before implementation; GREEN required |
| 23 | C | closure manifest edge records reproduce traversal result | RED before implementation; GREEN required |
| 24 | C | implementation cannot silently shrink previously admitted closure | RED before implementation; GREEN required |
| 25 | D | Smithy external apply trait changes normalized identity | RED before implementation; GREEN required |
| 26 | D | Smithy member trait override is preserved separately from target trait | RED before implementation; GREEN required |
| 27 | D | Smithy custom unknown trait blocks until classified | RED before implementation; GREEN required |
| 28 | D | duplicate conflicting Smithy shape definitions are rejected | RED before implementation; GREEN required |
| 29 | D | Smithy shape-map load order does not affect normalized output | RED before implementation; GREEN required |
| 30 | D | reachable error shape and traits are included | RED before implementation; GREEN required |
| 31 | D | documentation-only trait can be excluded only by registered rule | RED before implementation; GREEN required |
| 32 | D | Smithy loader/spec generation is bound into registry generation | RED before implementation; GREEN required |
| 33 | E | OpenAPI relative ref resolves using correct captured base URI | RED before implementation; GREEN required |
| 34 | E | parent `$id` changes relative Schema Object resolution and digest | RED before implementation; GREEN required |
| 35 | E | fragment parsed without required parent context is rejected | RED before implementation; GREEN required |
| 36 | E | remote ref is materialized and then resolved offline from captured bytes | RED before implementation; GREEN required |
| 37 | E | remote target drift after capture cannot change registered generation | RED before implementation; GREEN required |
| 38 | E | duplicate canonical `$id` resources with conflicting bytes are rejected | RED before implementation; GREEN required |
| 39 | E | `$anchor`/`$dynamicAnchor` identity is included when used | RED before implementation; GREEN required |
| 40 | E | unsupported JSON Schema vocabulary blocks admission | RED before implementation; GREEN required |
| 41 | E | OAS `x-*` extension consumed by generator cannot be silently dropped | RED before implementation; GREEN required |
| 42 | E | `additionalProperties`/open-world semantics survive normalization | RED before implementation; GREEN required |
| 43 | E | retrieval URI and canonical schema URI remain distinguishable | RED before implementation; GREEN required |
| 44 | E | OpenAPI dialect/version change is registry material | RED before implementation; GREEN required |
| 45 | F | protobuf direct import appears in descriptor closure | RED before implementation; GREEN required |
| 46 | F | protobuf transitive import appears in descriptor closure | RED before implementation; GREEN required |
| 47 | F | unresolved protobuf dependency blocks admission | RED before implementation; GREEN required |
| 48 | F | placeholder/allowUnknownDependencies mode is forbidden for consequential admission | RED before implementation; GREEN required |
| 49 | F | custom option definition dependency is included when option is relevant | RED before implementation; GREEN required |
| 50 | F | field-number change changes normalized identity | RED before implementation; GREEN required |
| 51 | F | syntax/edition/features change changes normalized identity | RED before implementation; GREEN required |
| 52 | F | oneof/presence change changes normalized identity | RED before implementation; GREEN required |
| 53 | F | enum alias/value change is preserved | RED before implementation; GREEN required |
| 54 | F | unknown descriptor/options material blocks until classified | RED before implementation; GREEN required |
| 55 | F | generic deterministic protobuf bytes are rejected as semantic canonical identity | RED before implementation; GREEN required |
| 56 | F | descriptor file ordering does not change LAB canonical graph digest | RED before implementation; GREEN required |
| 57 | G | provider-native profile must declare reference and unknown-field policy | RED before implementation; GREEN required |
| 58 | G | provider-native plugin-discovered schema source is captured before use | RED before implementation; GREEN required |
| 59 | G | provider-native filename collision cannot select by load order | RED before implementation; GREEN required |
| 60 | G | unregistered provider-native normalizer blocks capability admission | RED before implementation; GREEN required |
| 61 | H | authenticated source provenance is recorded separately from content digest | RED before implementation; GREEN required |
| 62 | H | trusted URL with changed bytes cannot reuse old generation ID | RED before implementation; GREEN required |
| 63 | H | identical bytes from different provenance remain attributable | RED before implementation; GREEN required |
| 64 | H | source-package signature failure blocks admission when policy requires signed provenance | RED before implementation; GREEN required |
| 65 | I | registry generation links predecessor and exact raw/normalized/closure digests | RED before implementation; GREEN required |
| 66 | I | generation ID cannot be reused after revocation | RED before implementation; GREEN required |
| 67 | I | same provider/API/version labels may coexist for distinct captured generations | RED before implementation; GREEN required |
| 68 | I | local valid chain behind external frontier is rejected for consequential startup | RED before implementation; GREEN required |
| 69 | I | forked registry history without authenticated frontier continuity is rejected | RED before implementation; GREEN required |
| 70 | I | capability-bound schema generation must be recognized by current frontier | RED before implementation; GREEN required |
| 71 | J | old archive restore preserves raw objects plus closure manifests | RED before implementation; GREEN required |
| 72 | J | restored archive behind global frontier cannot become active authority | RED before implementation; GREEN required |
| 73 | J | content deduplication cannot erase logical source membership/provenance | RED before implementation; GREEN required |
| 74 | J | historical normalizer generation remains available/verifiable for old evidence | RED before implementation; GREEN required |
| 75 | J | downgrade requires directional compatibility edge | RED before implementation; GREEN required |
| 76 | J | source replacement under same API version creates candidate, never in-place rewrite | RED before implementation; GREEN required |
| 77 | K | golden fixture mutating each resolved edge changes closure evidence as expected | RED before implementation; GREEN required |
| 78 | K | golden fixture mutating each unknown extension blocks until classified | RED before implementation; GREEN required |
| 79 | K | independent re-normalization from archived raw set reproduces admitted normalized digest | RED before implementation; GREEN required |
| 80 | K | end-to-end admission fails before consequential I/O on unresolved ref, collision, source replacement or frontier discontinuity | RED before implementation; GREEN required |

## 16. Implementation boundary

No production normalizer, registry frontier implementation, code generator or behavioral PASS is claimed by this research freeze.

Implementation must begin with executable fixtures for each supported format and deliberately adversarial source bundles: remote-reference drift, duplicate IDs, external Smithy trait applications, protobuf custom-option imports, reference cycles, unknown extensions and rollback archives. The RED matrix must execute before consequential capability code is refactored around this contract.

## 17. Interaction with retained contracts

This contract composes with, and does not replace:
- provider replay capsule / deterministic adapter compatibility;
- semantic request extractor / post-signing equivalence attestation;
- final-request freeze / transport interposition integrity;
- transport first-I/O ambiguity classification and observer durability;
- evidence-store capacity/archive continuity;
- privacy minimization / cryptographic erasure;
- evidence minimization policy compiler / taint / selective disclosure;
- provider evidence-schema registry / generated closed DTO / SDK drift admission;
- LAB-090..100 authenticated global provenance, activation and recovery contracts.

The important ordering is:

```text
raw model capture
  -> transitive closure
  -> versioned semantic normalization
  -> authenticated model-registry generation/frontier
  -> evidence-schema mapping/codegen generation
  -> provider capability admission
  -> request/replay/transport authority
```

No later stage may silently compensate for an incomplete or ambiguous earlier model generation.

## Frozen decision

**PROVIDER_MODEL_NORMALIZATION_TRANSITIVE_REFERENCE_CLOSURE_REGISTRY_FRONTIER_ADMISSION_V1_FROZEN**

A consequential provider model is identified by both exact raw-source-set content and a versioned normalized semantic closure. All transitive references/imports/descriptors are captured before admission and resolved offline from immutable content. Unknown extensions, ambiguous duplicate identities, unresolved references, normalization collisions and source replacement fail closed. Registered model history is append-only under authenticated frontier continuity; historical generations and normalizer versions remain reproducible and cannot be rewritten by rollback, archive restore or same-version provider republishing.