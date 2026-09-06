# Provider Evidence-Schema Registry / Generated Closed DTO / SDK Drift Admission Contract V1

Date: 2026-09-06  
Status: **FROZEN DESIGN / RED-FIRST — no production implementation or behavioral PASS claimed**  
Primary follow-up: LAB-093 / #178  
Priority note: LAB-086 / #163 remains priority #1 and is not superseded.

## Why this contract exists

The preceding evidence-minimization contract made the durable boundary closed-schema and fail-closed. This follow-up makes that boundary provider- and SDK-version-aware.

A consequential provider adapter must not be admitted merely because:
- an SDK package has a familiar version string;
- application call sites did not change;
- an old serializer still runs;
- unknown request/response/error fields are ignored;
- a provider model is "backward compatible" in the ordinary SDK sense.

Those conditions are too weak for authority/effect evidence. A new provider model can add request fields, generated defaults, error metadata, aliases, middleware fields, enum values, or open extension bags that alter the semantic request or leak data into evidence while all ordinary application code continues to compile.

The frozen rule is therefore:

> **Every consequential provider capability is bound to one authenticated, content-addressed evidence-schema generation derived from an exact provider-model snapshot plus exact canonical mappings and generator identity. Unknown or changed authority-relevant model material blocks admission until explicitly classified and directionally admitted.**

## Primary-source donor mechanisms

1. **Smithy models and `sensitive` trait.** Smithy defines model-level sensitivity and states that sensitive data must not be exposed in exception messages or log output. AWS publishes public service API models as Smithy JSON AST and SDKs are generated from those models. This is a strong donor for model-snapshot provenance and sensitivity propagation, but Smithy sensitivity alone is not sufficient for LAB retention/purpose decisions.
2. **Botocore service-model loader.** Botocore loads versioned `service-2.json` and related model files from a defined service/version directory layout. This demonstrates that a runtime SDK version and a concrete API-model snapshot are separable objects; LAB must bind the latter rather than trusting only the package version.
3. **OpenAPI closed/open object semantics.** OpenAPI 3.0 defaults `additionalProperties` to `true`. Therefore an object is not closed merely because all currently documented properties are known. LAB codegen must explicitly reject or classify open-world structures.
4. **Protocol Buffers unknown fields.** Protobuf preserves unknown fields in binary messages, and field-by-field or JSON transformations can lose them. A generated LAB evidence DTO must not infer completeness from an older descriptor or JSON projection when newer unknown fields may exist.

## 1. Registry objects

### 1.1 ProviderModelSnapshotV1

Each provider/API surface admitted for consequential use has an immutable snapshot:

```text
ProviderModelSnapshotV1 {
    provider_id
    api_id
    api_version
    model_format              # smithy-json-ast | openapi | protobuf | provider-native
    normalized_model_digest
    transitive_model_digest   # imports/$refs/descriptors/extensions required to interpret surface
    source_provenance
    source_license
    generator_input_digest
    captured_at
}
```

`normalized_model_digest` is not a digest of a human summary. It covers the machine model after one versioned canonical normalization. `transitive_model_digest` prevents a stable top-level file from hiding changed referenced/imported schemas.

Mutable labels such as package version, SDK marketing version, API date, branch, URL or filename are metadata only. They never identify an evidence schema by themselves.

### 1.2 CanonicalEvidenceMappingV1

For every request/response/error field reachable by a consequential operation:

```text
CanonicalEvidenceMappingV1 {
    provider_field_path
    canonical_field_path
    direction                 # request | response | error | metadata
    semantic_role             # identity | effect | scope | retry | reconciliation | diagnostic
    sensitivity
    presence_semantics        # absent != default where required
    default_semantics         # explicit-client | generated-client | server-side | none
    wire_location             # body/query/header/path/trailer/etc
    durable_representation    # plaintext/token/keyed-commitment/digest/omit/encrypted-capsule
    allowed_sinks
    retention_class
    disclosure_class
    extractor_relevance
}
```

Mappings are closed. A field that is reachable from the provider model but has no mapping is an admission error, not an implicit OMIT.

### 1.3 GeneratedEvidenceDTOGenerationV1

The generator emits sink-specific closed DTOs and serializers:

```text
GeneratedEvidenceDTOGenerationV1 {
    evidence_schema_generation_id
    provider_model_snapshot_digest
    canonical_mapping_digest
    policy_generation_id
    generator_binary_digest
    generator_config_digest
    generated_artifact_digest
    sink_artifact_digests
}
```

The generation ID is domain-separated and content-addressed over all authority-relevant inputs.

## 2. Generated closed DTO rule

Generated serializers MUST NOT:
- call generic object-to-dict conversion;
- inspect `__dict__`, reflection metadata or arbitrary SDK attributes;
- recursively traverse arbitrary maps/objects;
- serialize exception objects wholesale;
- preserve `metadata`, `extra`, `context`, `extensions`, `Any`, `Struct`, free-form JSON, or equivalent bags without an explicit provider-field mapping;
- accept caller-selected hash/redaction representation.

Generated serializers MAY only access statically generated field paths from the admitted model/mapping generation.

A provider field that is intentionally irrelevant is still represented in the mapping registry as an explicit `OMIT` classification with rationale and compatibility scope. Absence from the registry is never equivalent to irrelevance.

## 3. Presence and default semantics

Ordinary SDK compatibility often treats adding optional fields/defaults as harmless. Evidence compatibility cannot.

The registry distinguishes:
- field absent;
- field explicitly set to its type default;
- generated SDK default inserted client-side;
- provider/server default not materialized on the client.

If an SDK upgrade begins materializing a previously absent request value, the evidence schema changes even when application call arguments are unchanged. Historical replay must use the historical replay/schema generation, not reinterpret the request through today's defaults.

## 4. Open-world structures

The following are closed-world blockers until explicitly constrained/classified:
- OpenAPI objects where `additionalProperties` is true/defaulted;
- protobuf unknown fields for authority-relevant messages;
- `google.protobuf.Any`, `Struct`, arbitrary JSON/document shapes;
- Smithy document/untyped document-like values;
- SDK extension/plugin bags;
- arbitrary error metadata maps.

A blocker can be lifted only by one of:
1. replacing the provider surface with a closed schema;
2. defining an operation-specific extractor that rejects unknown keys at runtime;
3. proving the open material is outside provider effect/evidence semantics and structurally unreachable by every durable/observability serializer.

"Current SDK ignores it" is not a proof.

## 5. SDK drift admission algorithm

For every candidate provider/SDK upgrade:

1. Capture the exact candidate provider-model snapshot and transitive references.
2. Compute candidate snapshot digests using the frozen normalizer generation.
3. Diff semantic model paths against the currently admitted generation.
4. Classify every added/removed/changed field, default, enum, alias, location, error shape, middleware-visible extension and open-world boundary.
5. Regenerate all sink DTOs/serializers.
6. Require artifact digests and generator identity to match the registry record.
7. Execute positive and negative golden fixtures.
8. Produce a **directional** compatibility attestation:
   - `new_runtime_accepts_old_evidence`
   - `new_runtime_can_replay_old_capsule`
   - `old_runtime_accepts_new_evidence`
   These are independent claims.
9. Bind provider capability, replay capsule, semantic extractor, evidence policy and applicable transport-observer generations to the admitted evidence-schema generation.
10. Only then allow consequential admission.

Any unclassified model delta is fail-closed.

## 6. Rollback/downgrade

Rollback is not automatically safe.

An older SDK/model can be admitted only if:
- the current authenticated registry frontier recognizes that historical generation;
- all current authority-relevant fields are either understood or directionally proven irrelevant;
- historical evidence remains interpreted under its original generation;
- rollback cannot cause a field introduced in a newer generation to be silently dropped, defaulted, or reclassified;
- generated artifact hashes match the recorded generation.

Registry generation IDs are immutable and never reused.

## 7. Historical evidence and replay

Every durable consequential attempt binds:

```text
evidence_schema_generation_id
provider_capability_generation
replay_capsule_generation
semantic_extractor_generation
policy_generation
```

Historical evidence is verified against its original evidence-schema generation. It is not migrated by rewriting rows into the latest DTO.

A newer adapter may consume historical evidence only through an explicit directional compatibility edge. If no edge exists, mutation retry is blocked; read-only/manual reconciliation may still proceed through separately admitted evidence.

## 8. Error and exception schema

Provider errors are first-class schema material because they can contain:
- request IDs;
- retry hints;
- provider scope;
- nested service metadata;
- reflected request values;
- credentials/tokens accidentally included by SDK wrappers;
- new extension fields.

The generated error DTO is therefore closed independently from the response DTO. Catching `Exception` and persisting `vars(exc)`, `str(exc)` plus arbitrary metadata, or SDK-specific raw error dictionaries is non-conformant.

## 9. Supply-chain and generated-artifact admission

The registry records:
- generator binary/tool digest;
- generator templates/config digest;
- dependency-lock digest where generation output depends on dependencies;
- generated DTO/serializer artifact digests.

At startup, consequential capability admission verifies the actual imported generated artifact against the expected digest/generation. A same-name Python/module/package substitution cannot inherit the previous generation identity.

Manual edits to generated DTOs are rejected unless they are regenerated and registered as a new generation.

## 10. Compatibility evidence

Each admitted generation requires:
- model snapshot fixture;
- canonical mapping fixture;
- generated artifact fixture;
- positive request/response/error fixtures;
- negative fixtures mutating every authority-relevant mapped field;
- fixtures for unknown/open extension fields;
- historical evidence fixtures from every supported predecessor generation;
- rollback fixtures.

The compatibility declaration is authenticated and directional. Version ranges such as `sdk >= 1.2` are not sufficient evidence.

## 11. RED-first 80-case matrix

| # | Group | Case | Required outcome |
|---:|:---:|---|---|
| 1 | A | same provider/API model bytes reproduce the same schema_generation_id | RED before implementation; GREEN required |
| 2 | A | one-byte model change changes schema_generation_id | RED before implementation; GREEN required |
| 3 | A | snapshot hash covers transitive imported/referenced model material | RED before implementation; GREEN required |
| 4 | A | snapshot hash covers generator configuration and normalization rules | RED before implementation; GREEN required |
| 5 | A | registry rejects an unparseable provider model | RED before implementation; GREEN required |
| 6 | A | registry rejects duplicate/conflicting model identities | RED before implementation; GREEN required |
| 7 | A | registry records provenance/license/source URI without making it authority | RED before implementation; GREEN required |
| 8 | A | registry lookup by mutable SDK version alone is rejected | RED before implementation; GREEN required |
| 9 | B | generated authority DTO exposes only declared canonical fields | RED before implementation; GREEN required |
| 10 | B | generated DTO has no arbitrary metadata/extra bag | RED before implementation; GREEN required |
| 11 | B | serializer cannot reflect/traverse __dict__ or unknown object attributes | RED before implementation; GREEN required |
| 12 | B | nested SDK object is projected only through generated field accessors | RED before implementation; GREEN required |
| 13 | B | unknown map/object field is rejected unless explicitly classified | RED before implementation; GREEN required |
| 14 | B | optional absent field remains distinguishable from explicit default when provider semantics require it | RED before implementation; GREEN required |
| 15 | B | generated serializer emits deterministic canonical field ordering | RED before implementation; GREEN required |
| 16 | B | DTO generation fails if a required canonical mapping is missing | RED before implementation; GREEN required |
| 17 | C | new SDK with identical provider model snapshot may be admitted after binary/toolchain checks | RED before implementation; GREEN required |
| 18 | C | new provider model field blocks consequential admission until classified | RED before implementation; GREEN required |
| 19 | C | removed provider model field blocks replay compatibility when historical capsule requires it | RED before implementation; GREEN required |
| 20 | C | default value change blocks admission even if application code is unchanged | RED before implementation; GREEN required |
| 21 | C | enum extension is treated as model drift and requires classification | RED before implementation; GREEN required |
| 22 | C | error/exception schema extension blocks durable exception projection until classified | RED before implementation; GREEN required |
| 23 | C | new middleware-injected provider-visible field blocks admission | RED before implementation; GREEN required |
| 24 | C | unknown extension bag from SDK runtime blocks admission | RED before implementation; GREEN required |
| 25 | D | provider capability generation binds exact evidence_schema_generation | RED before implementation; GREEN required |
| 26 | D | replay capsule generation binds exact evidence_schema_generation | RED before implementation; GREEN required |
| 27 | D | semantic extractor generation binds exact evidence_schema_generation | RED before implementation; GREEN required |
| 28 | D | transport observer profile binds exact evidence_schema_generation when request metadata is projected | RED before implementation; GREEN required |
| 29 | D | policy compiler generation binds exact evidence_schema_generation | RED before implementation; GREEN required |
| 30 | D | adapter upgrade cannot silently substitute a newer evidence schema for historical replay | RED before implementation; GREEN required |
| 31 | D | rollback to older adapter is rejected when it cannot understand current evidence schema | RED before implementation; GREEN required |
| 32 | D | generation graph records directional compatibility, not symmetric version equality | RED before implementation; GREEN required |
| 33 | E | explicit request field mapping preserves provider semantic identity | RED before implementation; GREEN required |
| 34 | E | implicit SDK default is materialized into canonical projection before SEND_STARTED | RED before implementation; GREEN required |
| 35 | E | server-side default that is not client-visible is marked distinct from client default | RED before implementation; GREEN required |
| 36 | E | query/header/body location changes are treated as semantic mapping changes | RED before implementation; GREEN required |
| 37 | E | serialization name/alias change blocks compatibility until attested equivalent | RED before implementation; GREEN required |
| 38 | E | multipart part schema changes are detected | RED before implementation; GREEN required |
| 39 | E | compression/framing-only change is allowed only by extractor declaration | RED before implementation; GREEN required |
| 40 | E | idempotency token field cannot disappear or move without compatibility proof | RED before implementation; GREEN required |
| 41 | F | successful response projection uses generated closed DTO | RED before implementation; GREEN required |
| 42 | F | provider error code/message/details projection is allowlisted | RED before implementation; GREEN required |
| 43 | F | raw exception object serialization is impossible through generated API | RED before implementation; GREEN required |
| 44 | F | nested error metadata added by SDK is rejected until classified | RED before implementation; GREEN required |
| 45 | F | HTTP headers copied into errors are individually classified | RED before implementation; GREEN required |
| 46 | F | retry-after/request-id fields may be retained only under declared purpose | RED before implementation; GREEN required |
| 47 | F | unknown protobuf response fields cannot be silently dropped when authority relevant | RED before implementation; GREEN required |
| 48 | F | response schema rollback cannot reinterpret stored historical evidence | RED before implementation; GREEN required |
| 49 | G | Smithy-sensitive field maps to SECRET/SENSITIVE by default | RED before implementation; GREEN required |
| 50 | G | secret field cannot be downgraded by adapter-local annotation | RED before implementation; GREEN required |
| 51 | G | Authorization/session credentials never appear in evidence DTO | RED before implementation; GREEN required |
| 52 | G | low-entropy identifier uses keyed commitment where configured | RED before implementation; GREEN required |
| 53 | G | nested sensitive field remains tainted after formatting/encoding | RED before implementation; GREEN required |
| 54 | G | exception path cannot bypass field classification | RED before implementation; GREEN required |
| 55 | G | log/trace/metric DTOs are separate generated sinks | RED before implementation; GREEN required |
| 56 | G | derived index/search projection cannot gain fields absent from source sink policy | RED before implementation; GREEN required |
| 57 | H | OpenAPI additionalProperties=true is treated as open-world and blocks closed DTO generation unless constrained | RED before implementation; GREEN required |
| 58 | H | OpenAPI additionalProperties=false permits closed object generation subject to refs | RED before implementation; GREEN required |
| 59 | H | protobuf unknown fields cause consequential admission failure unless explicitly proven irrelevant | RED before implementation; GREEN required |
| 60 | H | protobuf JSON round-trip is not used as an unknown-field detector | RED before implementation; GREEN required |
| 61 | H | map<string,Any> / Struct / arbitrary JSON payload is classified as open-world | RED before implementation; GREEN required |
| 62 | H | vendor extension field is rejected until mapped | RED before implementation; GREEN required |
| 63 | H | Smithy document/untyped blob is not traversed generically | RED before implementation; GREEN required |
| 64 | H | custom SDK plugin-added attribute is ignored only if inaccessible to generated serializer and proven non-semantic | RED before implementation; GREEN required |
| 65 | I | historical evidence remains verifiable with its original registry snapshot | RED before implementation; GREEN required |
| 66 | I | deleting an old registry snapshot while pinned evidence exists is rejected | RED before implementation; GREEN required |
| 67 | I | downgrade cannot erase knowledge of newer authority-relevant fields | RED before implementation; GREEN required |
| 68 | I | rollback to older model requires explicit directional compatibility proof | RED before implementation; GREEN required |
| 69 | I | restored backup with older registry frontier is rejected by monotonic registry frontier | RED before implementation; GREEN required |
| 70 | I | schema generation IDs are never reused after deletion/compaction | RED before implementation; GREEN required |
| 71 | I | archived snapshot digest is verified before use | RED before implementation; GREEN required |
| 72 | I | registry migration does not rewrite historical evidence under new schema IDs | RED before implementation; GREEN required |
| 73 | J | generator binary/tool hash is recorded | RED before implementation; GREEN required |
| 74 | J | same model + same generator config reproduces byte-identical DTO source/artifact where claimed | RED before implementation; GREEN required |
| 75 | J | codegen template drift changes generator generation identity | RED before implementation; GREEN required |
| 76 | J | dependency lock drift is detected | RED before implementation; GREEN required |
| 77 | J | unsigned/untrusted model source cannot become consequentially admitted without registry authorization | RED before implementation; GREEN required |
| 78 | J | generated artifact hash is checked at startup | RED before implementation; GREEN required |
| 79 | J | runtime imports cannot substitute a different generated DTO module under the same generation ID | RED before implementation; GREEN required |
| 80 | J | manual edits to generated DTO fail artifact verification | RED before implementation; GREEN required |

## 12. First implementation slice

Do not begin with whole-program dynamic taint tracking.

The smallest coherent implementation is:

1. `EvidenceSchemaRegistry` with content-addressed immutable generations and authenticated monotonic frontier.
2. One provider/model importer (prefer Smithy/AWS because public model snapshots and sensitivity traits are available).
3. Generated request/error closed DTOs for one consequential operation.
4. Runtime rejection of unknown/unmapped fields.
5. Artifact digest verification at capability admission.
6. Golden fixture runner exercising added field, changed default, nested error extension and rollback cases.
7. Bind the provider capability + replay/extractor generation to the schema generation.
8. Only after that broaden to OpenAPI/protobuf/importers and static/dynamic taint tooling.

## 13. Non-claims

This document freezes a contract. It does **not** claim:
- a production registry exists;
- provider models have been exhaustively classified;
- the 80 cases have executed;
- any LAB-093 production code is GREEN;
- any LAB-086 gate has changed.

## Frozen verdict

**PROVIDER_EVIDENCE_SCHEMA_REGISTRY_GENERATED_CLOSED_DTO_SDK_DRIFT_ADMISSION_V1_FROZEN**

Consequential provider execution is admitted only when the exact provider-model snapshot, canonical evidence mapping, generator identity, generated closed DTO artifacts, policy generation and directional compatibility have been authenticated as one evidence-schema generation. Unknown/new fields are not silently tolerated. Historical evidence and replay stay bound to the generation under which they were created.
