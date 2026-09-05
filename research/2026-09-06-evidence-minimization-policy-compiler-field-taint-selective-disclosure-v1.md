# Evidence minimization policy compiler / field-taint admission / selective-disclosure verifier V1

Status: `EVIDENCE_MINIMIZATION_POLICY_COMPILER_FIELD_TAINT_SELECTIVE_DISCLOSURE_V1_FROZEN`

Date: 2026-09-06

Scope: LAB-093 retained-authority evidence plane and all provider adapter / retry / UNKNOWN / manual-resolution / transport-observer / archive / telemetry paths that can derive or persist evidence.

## Problem

The preceding privacy-minimization contract says durable evidence is allowlist-based, raw provider material is denied by default, minimization happens before the pre-I/O durability barrier, and replay/manual-resolution secrets live outside routine audit evidence.

That is not sufficient if the rule remains prose. A secret can still escape through:

- a nested SDK object that is serialized into generic metadata;
- an exception containing request or response fragments;
- a middleware-generated header/query field;
- a trace/log attribute added after the main evidence object was minimized;
- a debug or `extra` dictionary whose schema is open-ended;
- a derived search/index/export pipeline;
- a policy upgrade that silently changes a field from commitment-only to plaintext;
- a selective-disclosure export that omits the policy context needed to verify what was withheld.

This contract freezes an executable policy boundary: schema-level field purposes, taint propagation, sink admission, deterministic export verification and monotonic policy-generation semantics.

## Primary-source donors

1. **Smithy 2.0 `sensitive` trait** — model-level sensitivity classification; sensitive data MUST NOT appear in exception messages or log output. This is a strong donor for attaching classification to modeled fields rather than relying on string-name heuristics after serialization.
   - https://smithy.io/2.0/spec/documentation-traits.html#sensitive-trait
2. **OpenTelemetry sensitive-data guidance** — recommends not collecting unnecessary sensitive data and provides allowlist-style redaction/filtering; it explicitly warns that hashing predictable identifiers may not anonymize them. This is a donor for deny-by-default telemetry export and for treating generic hashing as insufficient for low-entropy values.
   - https://opentelemetry.io/docs/security/handling-sensitive-data/
   - https://opentelemetry.io/docs/specs/semconv/url/#sensitive-information
3. **Cedar schema validation** — policy validation against an explicit application schema catches unknown attributes/type mismatches before authorization evaluation, and schema changes require policy revalidation. This is a donor for compile-time policy/schema admission and generation-bound revalidation rather than runtime best-effort filtering.
   - https://docs.cedarpolicy.com/policies/validation.html
   - https://docs.cedarpolicy.com/schema/schema.html
4. **OPA bundles / signed policy distribution** — policies and data can be built into versioned bundles, optionally signed, and loaded as a unit. This is a donor for an authenticated compiled minimization-policy artifact rather than mutable ad-hoc configuration fragments.
   - https://www.openpolicyagent.org/docs/management-bundles
5. **CodeQL data-flow / taint tracking** — source-to-sink propagation across program operations is a donor for modeling derived sensitive values, not merely checking original field names.
   - https://codeql.github.com/docs/codeql-language-guides/analyzing-data-flow-in-python/
   - https://codeql.github.com/docs/writing-codeql-queries/about-data-flow-analysis/
6. **RFC 9901 SD-JWT** — selective disclosure binds undisclosed claims by digest while requiring verifiers to ensure that security-critical claims needed for validity are present/disclosed. This is a donor for deterministic disclosure manifests and the rule that authority-critical verification fields cannot be silently hidden.
   - https://www.rfc-editor.org/rfc/rfc9901

These are mechanism donors, not a claim that LAB uses Smithy/Cedar/OPA/SD-JWT wire formats directly.

## Frozen invariants

### 1. Policy is a closed schema, not a list of regex redactions

Every provider surface that can produce consequential evidence MUST have a compiled `EvidencePolicyGeneration` describing every admissible field path.

A field declaration binds at least:

```text
FieldRuleV1 {
  canonical_path
  semantic_type
  source_class
  sensitivity_class
  evidence_purpose
  sink_classes[]
  representation
  commitment_scheme?
  retention_class
  disclosure_class
  derivation_rules[]
}
```

Unknown field paths are `REJECT`, never `PASS_THROUGH`.

Open maps such as `metadata`, `extra`, `context`, arbitrary headers, arbitrary query maps, exception dictionaries, protobuf unknown fields, JSON extension objects or SDK-specific bags MUST NOT be copied into evidence wholesale. They require an explicit bounded extractor whose outputs are individually declared field paths.

### 2. Evidence purpose and representation are compiled together

Every admitted field has exactly one primary purpose:

- `ORDER_ONLY`
- `EQUALITY_ONLY`
- `RECOVERY_REQUIRED`
- `HUMAN_RECONCILIATION_REQUIRED`
- `PUBLIC_AUDIT_IDENTITY`

and exactly one durable representation:

- `OMIT`
- `CANONICAL_DIGEST`
- `KEYED_COMMITMENT`
- `TOKEN_REFERENCE`
- `ENCRYPTED_CAPSULE_REFERENCE`
- `PLAINTEXT_MINIMAL`

A policy compiler MUST reject incoherent combinations, including:

- sensitive/low-entropy `EQUALITY_ONLY` with plain digest;
- secret credentials with `PLAINTEXT_MINIMAL`;
- `ORDER_ONLY` carrying original value bytes;
- `RECOVERY_REQUIRED` plaintext in the general audit plane when the field is classified secret;
- `HUMAN_RECONCILIATION_REQUIRED` without an explicit disclosure/access policy;
- generic `raw`, `debug`, `serialized_object` or `unknown` representations.

### 3. Taint originates from modeled values and remains attached to derivatives

Each runtime value entering provider request construction carries a logical taint label derived from its `FieldRuleV1`, for example:

```text
PUBLIC
AUTHORITY_ID
PERSONAL
COMMERCIAL_SECRET
PROVIDER_CREDENTIAL
SESSION_SECRET
PRIVATE_KEY_MATERIAL
LOW_ENTROPY_IDENTIFIER
REPLAY_SENSITIVE
UNKNOWN_UNCLASSIFIED
```

Taint propagates through:

- string formatting/interpolation;
- concatenation/substrings;
- JSON/form/protobuf/multipart serialization;
- URL/query/header construction;
- exception wrapping;
- SDK request/response wrappers;
- copies into dictionaries/lists/dataclasses;
- encoding/base64/compression;
- hashes where the source is enumerable or where the hash itself is sensitive correlation data;
- trace/log baggage and structured logging fields;
- derived analytics/search/index documents.

Sanitizers do not merely erase taint by declaration. A sanitizer produces a new value with a specific downgraded representation only if the compiled policy names that transformation and its proof obligation.

### 4. `UNKNOWN_UNCLASSIFIED` is contagious and fail-closed

Any value entering a consequential evidence/export path without a known policy path receives `UNKNOWN_UNCLASSIFIED`.

If an object contains an unknown child, the container is not safe merely because known siblings are public. Generic serialization of the container is rejected.

This closes nested-object bypasses such as:

```text
safe_metadata = {
  "attempt_id": public_id,
  "sdk_context": request_object,   # contains token/body
}
```

A serializer cannot flatten an unknown subtree and then ask a downstream redactor to discover secrets heuristically.

### 5. The compiler emits sink-specific projections

The policy compiler MUST produce separate closed projections for at least:

- `AUTHORITY_EVIDENCE_DB`
- `RECOVERY_JOURNAL`
- `REPLAY_CAPSULE`
- `MANUAL_RECONCILIATION_CAPSULE`
- `APPLICATION_LOG`
- `TRACE`
- `METRIC_LABEL`
- `SEARCH_INDEX`
- `ARCHIVE_MANIFEST`
- `SELECTIVE_DISCLOSURE_EXPORT`

A field allowed in one sink is not thereby allowed in another.

Example: an idempotency token may be needed encrypted inside `REPLAY_CAPSULE`, committed in `AUTHORITY_EVIDENCE_DB`, omitted from `TRACE`, and selectively disclosed only to a reconciliation verifier.

### 6. Pre-I/O admission consumes only compiled projections

Before `SINK_ENTERED`, the runtime constructs the authority-evidence projection from typed/model-aware extractors and validates it against the compiled generation.

The durable barrier API accepts only an already-validated closed projection type such as:

```text
ValidatedEvidenceProjection<PolicyGeneration=N>
```

It MUST NOT accept arbitrary `dict`, SDK request object, exception object, logger context or serializer output.

If policy validation/extraction/commitment generation fails, consequential provider I/O fails closed before the durability barrier.

### 7. Provider adapters must declare source mappings, not just sink filters

Each admitted provider/SDK adapter generation MUST provide a mapping from provider model paths to LAB canonical field paths.

The mapping identifies:

- provider request fields;
- SDK-injected defaults;
- generated idempotency/request IDs;
- credential/auth fields;
- endpoint/account/region identity;
- response/reconciliation identifiers;
- exception/error structures;
- provider-specific arbitrary metadata surfaces.

An SDK upgrade is not automatically compatible when new fields, new nested error payloads, new telemetry hooks or new middleware appear. The adapter generation must be recompiled/revalidated against the current evidence policy.

### 8. Exceptions are tainted data structures, not trusted strings

Provider and SDK exceptions frequently carry request IDs, URLs, headers, serialized bodies, response snippets or nested request objects.

Consequential paths MUST NOT persist `str(exc)`, `repr(exc)`, `exc.__dict__`, generic stack-local dumps or logger `extra=...` payloads into authority evidence.

Instead, each provider adapter defines a closed `ErrorProjectionV1` with individually classified fields. Unknown exception attributes are dropped from ordinary logs and cause fail-closed rejection if a consequential durable evidence transition would otherwise depend on them.

Stack traces may retain code locations/types where allowed, but argument/local-variable capture is disabled for evidence and ordinary telemetry unless explicitly classified.

### 9. Logs/traces/metrics are downstream sinks, not alternate evidence channels

All derived observability uses the same policy generation or a stricter sink-specific projection.

No code path may bypass evidence minimization by logging immediately before or after the durable write.

In particular:

- trace span attributes are allowlisted;
- metric labels are limited to low-cardinality approved public/authority identifiers;
- URLs exclude user-info/password components and scrub sensitive query values;
- baggage/context propagation does not carry replay/manual-resolution plaintext;
- logger exception formatting does not serialize provider objects;
- debug mode cannot widen a consequential production sink policy.

### 10. Commitment schemes are selected by policy, not caller choice

The compiler selects commitment representation based on sensitivity and entropy class.

- public/high-entropy semantic values may use canonical domain-separated digest;
- low-entropy/sensitive equality values require a keyed commitment under the named `commitment_scheme_generation`;
- values requiring later recovery use token/capsule reference rather than audit plaintext;
- secret credentials/private key material are never equality-committed merely for convenience unless an explicit security design proves why such correlation is required.

Callers cannot request `hash=true` to downgrade a sensitive value.

### 11. Selective-disclosure exports are deterministic and self-describing

An audit/reconciliation export MUST include:

- source evidence object identity/digest;
- source `evidence_minimization_policy_generation`;
- commitment-scheme generation;
- disclosure profile ID;
- exact canonical paths disclosed;
- commitments/digests binding withheld-but-relevant fields where permitted;
- authority-critical fields required to validate the evidence state;
- authenticated export digest/signature/provenance binding;
- export time/frontier and purpose/audience where required.

The verifier reconstructs the same canonical disclosed projection and rejects:

- undeclared fields;
- missing mandatory authority/validity fields;
- duplicate/ambiguous canonical paths;
- disclosure generated under an unknown or downgraded policy generation;
- a commitment that is not bound to the original evidence record/policy context.

Selective disclosure is not a mechanism to hide fields needed to determine whether the underlying authority evidence is valid. This mirrors RFC 9901's requirement that verifiers ensure security-critical validity claims are available.

### 12. Policy generations are authenticated, monotonic and directionally compatible

Every compiled policy artifact has:

```text
policy_generation
parent_generation
schema_digest
compiler_version
provider_mapping_digests[]
sink_projection_digests[]
commitment_scheme_generation
compatibility_edges[]
artifact_digest
signature/provenance
```

A runtime may verify historical evidence with the historical policy generation, but may create new consequential evidence only under the currently admitted generation.

Upgrade rules:

- adding a new plaintext-retained field is an authority/privacy expansion and requires explicit review/admission;
- changing `KEYED_COMMITMENT -> PLAINTEXT_MINIMAL` is never an automatic compatible upgrade;
- reducing retained plaintext is directionally safe for new evidence but does not prove old copies were erased;
- changing canonicalization or commitment scheme requires an explicit verifier migration path; old commitments are not reinterpreted under new rules;
- removing a provider mapping field is safe only if provider-semantic/recovery proofs do not require it;
- downgrade to an older generation for new sends is rejected unless an explicit signed rollback authority names the exact generation pair and safety reason; ordinary config rollback cannot do it.

### 13. Compiler and runtime validator are independent enough to catch drift

The build/admission path compiles policy/schema/provider mappings into a canonical artifact. Runtime sink admission validates actual projection objects against that artifact.

For high-value consequential paths, golden fixtures MUST additionally run a second verifier implementation or schema validator over exported canonical JSON/CBOR-equivalent objects so one buggy extractor cannot both create and approve an invalid object.

At minimum, tests mutate each field independently and prove that unknown fields, wrong representations, missing mandatory fields and forbidden taint fail closed.

### 14. No arbitrary metadata escape hatch

Production authority APIs MUST NOT expose parameters equivalent to:

```text
metadata: dict[str, Any]
extra: Any
context: object
debug: object
headers: dict[str, str]
```

for durable evidence/telemetry without a compiled bounded schema.

If extension is required, use versioned typed extension records with closed fields and a separately admitted policy generation.

### 15. Derived stores carry policy provenance

Search indexes, exported CSV/JSON, investigation packages, analytics replicas and archive manifests must record the source policy generation and their own projection digest.

A derived store cannot claim compliance merely because its source DB was compliant. Its exporter must itself be a policy sink and must prove that only its compiled projection left the authority store.

### 16. Taint evidence is not itself a new secret-retention channel

Runtime taint labels and policy diagnostics persist only canonical path/classification identifiers, never copied secret values.

A violation report may say:

```text
sink=TRACE
canonical_path=provider.auth.bearer_token
class=PROVIDER_CREDENTIAL
rule=DENY
```

but MUST NOT include the rejected value in the error message.

## Policy compiler pipeline

```text
provider model/schema
  + LAB canonical evidence schema
  + field purpose/sensitivity declarations
  + provider source mappings
  + sink declarations
  + commitment schemes
  + policy parent generation
        |
        v
static validation
  - every reachable source classified
  - every admitted sink field declared
  - no incoherent purpose/representation pair
  - no open metadata containers
  - no missing provider exception mapping
        |
        v
canonical compile
  - per-sink projection schemas
  - taint propagation/sanitizer table
  - commitment selectors
  - selective-disclosure profiles
  - provider adapter compatibility digest
        |
        v
signed/authenticated policy artifact
        |
        +--> build-time golden fixture verifier
        +--> runtime pre-I/O projection validator
        +--> log/trace/export sink validators
```

## Suggested minimal implementation boundary

Do not begin with whole-program dynamic taint instrumentation.

V1 implementation should first make the dangerous interfaces unrepresentable:

1. typed closed evidence DTOs instead of arbitrary dictionaries;
2. provider-specific extractors from SDK objects into those DTOs;
3. generated per-sink serializers that know only admitted fields;
4. explicit commitment constructors returning tagged commitment types;
5. exception adapters producing closed error DTOs;
6. logger/trace helpers accepting only public/telemetry DTOs;
7. policy-generation digest pinned into every evidence record;
8. static/golden tests for nested objects, arbitrary metadata and exceptions.

Whole-program static taint analysis (for example CodeQL-style source-to-sink checks) is a complementary audit layer, not the primary runtime authority mechanism. It should detect direct logging/serialization bypasses that evade the typed APIs, but production correctness must not depend on a code-scanning job running later.

## RED-first matrix — 80 cases

### A. Schema/compiler validation — 12

1. unknown canonical field path rejected;
2. duplicate canonical path rejected;
3. open `metadata` map rejected;
4. open `extra` object rejected;
5. sensitive `EQUALITY_ONLY + CANONICAL_DIGEST` rejected;
6. credential `PLAINTEXT_MINIMAL` rejected;
7. order-only original-value retention rejected;
8. recovery-sensitive plaintext in audit plane rejected;
9. reconciliation field without disclosure policy rejected;
10. missing sink declaration rejected;
11. missing provider error mapping rejected;
12. non-canonical/ambiguous field alias rejected.

### B. Nested-object / taint propagation — 12

13. secret nested one level inside SDK object blocked;
14. secret nested many levels blocked;
15. safe sibling does not declassify secret child;
16. list/array propagation;
17. dictionary-value propagation;
18. string interpolation propagation;
19. URL/query construction propagation;
20. header construction propagation;
21. base64 retains taint;
22. compression retains taint;
23. enumerable-value plain hash remains sensitive;
24. unknown protobuf/extension field makes generic container non-admissible.

### C. Exceptions / failure paths — 10

25. `str(exc)` cannot enter durable evidence;
26. `repr(exc)` cannot enter durable evidence;
27. exception `__dict__` blocked;
28. nested request object in exception blocked;
29. response-body snippet blocked;
30. Authorization header in exception blocked;
31. request URL with sensitive query scrubbed/blocked;
32. stack trace without locals allowed where policy permits;
33. stack-local/argument capture blocked;
34. violation diagnostics contain path/class but not rejected value.

### D. Logs / traces / metrics — 10

35. trace unknown attribute rejected;
36. trace credential attribute rejected;
37. metric high-cardinality sensitive label rejected;
38. logger `extra` arbitrary map rejected;
39. logger exception auto-format path cannot leak request;
40. baggage secret rejected;
41. debug mode cannot widen sink;
42. post-write log cannot mirror replay capsule;
43. URL user-info/password never recorded;
44. approved public attempt/effect IDs remain observable.

### E. Provider adapter / SDK drift — 10

45. newly added SDK request field invalidates mapping;
46. newly added nested exception field invalidates mapping if relied upon;
47. changed SDK default requires adapter generation update;
48. middleware-injected header classified before evidence use;
49. generated idempotency token mapped correctly;
50. provider account/region scope mapped correctly;
51. arbitrary provider metadata bag cannot pass through;
52. old adapter cannot create evidence under incompatible new policy;
53. new adapter cannot claim historical compatibility without mapping digest edge;
54. provider error code/request ID selective fields still recoverable without raw body.

### F. Commitment selection — 8

55. high-entropy public value canonical digest allowed;
56. low-entropy sensitive value requires keyed commitment;
57. caller cannot override keyed commitment with plain hash;
58. commitment domain binds canonical path;
59. commitment domain binds evidence/policy context;
60. wrong commitment-scheme generation rejected;
61. replay plaintext stored only in capsule path;
62. routine audit reader cannot recover capsule plaintext.

### G. Selective disclosure — 10

63. deterministic field ordering/canonical export;
64. undeclared disclosed field rejected;
65. duplicate path rejected;
66. missing mandatory authority field rejected;
67. wrong policy generation rejected;
68. wrong disclosure profile rejected;
69. commitment from another evidence record rejected;
70. commitment from another canonical path rejected;
71. withheld non-critical field remains verifiably bound where profile requires;
72. verifier cannot treat absent security-critical field as valid merely because it was selectively disclosable.

### H. Policy generation / derived stores — 8

73. plaintext-expanding upgrade requires explicit admission;
74. commitment-to-plaintext transition not auto-compatible;
75. field-reducing upgrade applies only prospectively until erase proof exists;
76. canonicalization change cannot reinterpret old commitment;
77. ordinary config rollback cannot downgrade new sends;
78. search/export store carries source policy generation;
79. exporter with unknown field fails closed;
80. historic record remains verifiable under exact historical policy artifact after current-policy upgrade.

## Acceptance boundary

Freezing this contract does **not** claim:

- a production policy compiler exists;
- dynamic or static taint instrumentation is implemented;
- provider SDK models are fully classified;
- selective-disclosure cryptography is implemented;
- any of the 80 cases have passed.

Production implementation begins RED-first once exact executable source is available. The first coherent implementation slice should be closed typed evidence DTOs + policy-generation artifact + provider extractor + sink-specific serializer + exception projection, because those make the highest-risk arbitrary-object bypasses structurally impossible before attempting broad taint instrumentation.

## Security audit

The dangerous false shortcut is to build only a redaction processor on the final serialized output. That fails for at least four reasons: data may already have reached WAL/logs/traces before redaction; unknown nested objects may serialize secrets under unexpected keys; predictable hashes can remain identifying; and future SDK fields silently bypass name-based blocklists.

The second false shortcut is to make runtime taint labels authoritative without closing generic object/dict sinks. A missed propagation edge would then silently declassify data. Typed closed sink DTOs remain the primary enforcement boundary; taint analysis is defense in depth and policy validation evidence.

The third false shortcut is to treat selective disclosure as permission to omit authority-critical verification context. Any export used to support a consequential decision must disclose the fields the verifier needs to establish authenticity/validity, or the decision fails closed.

## Decision

Freeze `EVIDENCE_MINIMIZATION_POLICY_COMPILER_FIELD_TAINT_SELECTIVE_DISCLOSURE_V1` as the executable privacy/evidence admission boundary for LAB-093 and dependent contracts.

No production implementation is authorized until exact source execution is available and the RED-first matrix can be run. Until then, later designs must assume that arbitrary metadata, generic exception serialization and unconstrained observability are forbidden surfaces rather than convenient implementation details.
