# Manifest Schema Authority / Declaration-Slot Compiler / Schema-Completeness Proof V1

Status: `MANIFEST_SCHEMA_AUTHORITY_DECLARATION_SLOT_COMPILER_SCHEMA_COMPLETENESS_PROOF_V1_FROZEN`

Date: 2026-09-07

Scope: LAB-093 / #178 follow-up to producer-path manifest completeness. This is a design freeze and RED-first contract, not a claim of exact repository behavioral execution.

## Problem

The previous contract makes a consequential effect admissible only when its effect manifest is emitted on the same authenticated authority path and an independent verifier confirms all schema-required declarations. That is still insufficient if the closed-world schema itself is incomplete, ambiguous, stale, maliciously weakened, or interpreted differently by producer and verifier.

A producer and verifier can perfectly agree on an incomplete universe if both consume the same defective schema generation. Therefore schema publication, schema interpretation, generated declaration code and historical coverage must each carry independent authority/evidence.

## Donor mechanisms checked

Primary-source mechanisms used as design donors:

1. TUF root metadata provides versioned, threshold-authorized role/key definitions and requires each new root generation to be authorized both by the previous trusted root and by the new root, preventing unilateral rollback/replacement of trust metadata. Donor: schema-generation authority/rotation must itself be authenticated, monotonic and predecessor-linked.
   - https://theupdateframework.github.io/specification/v1.0.26/

2. Protocol Buffers assigns stable field numbers, forbids reuse after deletion, and recommends reserving removed numbers/names. Donor: declaration-slot identifiers are historical semantic identities, not positional indexes or reusable labels; removed material slots remain reserved.
   - https://protobuf.dev/programming-guides/editions/
   - https://protobuf.dev/programming-guides/proto3/

3. JSON Schema closed-world mechanisms (`additionalProperties:false`, `unevaluatedProperties:false`) demonstrate that completeness depends on the validator accounting for all evaluated properties across composition; unrecognized properties are otherwise open by default. Donor: schema-completeness must explicitly close the declaration universe and define composition behavior rather than assuming absence means forbidden.
   - https://json-schema.org/draft/2020-12/json-schema-core

4. OpenAPI discriminator/`oneOf` semantics require alternatives to be explicitly listed and document ambiguity/undefined behavior for unsupported compositions. Donor: operation-kind aliasing and polymorphic dispatch must have an explicit, unambiguous total mapping to one declaration rule; heuristic/default dispatch is unsafe for destructive authority.
   - https://spec.openapis.org/oas/latest.html

## Core decision

A manifest schema generation is consequential authority metadata. It MUST NOT be published by the same producer implementation whose declarations it governs acting alone.

`EffectSchemaGenerationV1` is admissible only if:

- its canonical digest is threshold-authorized by a dedicated `SCHEMA_AUTHORITY` role;
- the generation is monotonic and predecessor-linked;
- every operation kind maps to exactly one canonical declaration rule or to an explicit, separately authorized alias;
- every material declaration slot has a stable non-reusable `slot_id` and semantic class;
- the schema includes an explicit closed-world assertion for operation kinds and slots;
- an independently implemented schema checker proves internal totality/unambiguity before activation;
- generated producer/verifier artifacts carry the source schema digest and deterministic compiler identity;
- activation includes a coverage/rollout frontier so mixed-generation operation execution is not silently treated as homogeneous.

Schema signatures authenticate what was approved; they do not prove semantic completeness. Completeness requires separate evidence.

## Authority roles

Separate these capabilities:

- `SCHEMA_AUTHOR`: proposes operation kinds, aliases and slots; no activation authority.
- `SCHEMA_REVIEWER`: independently reviews materiality and closed-world coverage.
- `SCHEMA_AUTHORITY`: threshold-signs an immutable generation and its activation policy.
- `COMPILER_AUTHORITY`: identifies/audits supported declaration-slot compiler implementations; cannot change schema semantics.
- `RUNTIME_ACTIVATOR`: activates an already authorized generation at a declared frontier; cannot mutate it.
- `SCHEMA_AUDITOR`: may publish omission challenges/fraud proofs; cannot silently rewrite history.

No single producer/runtime signer may hold all consequential capabilities by default.

## Canonical EffectSchemaGenerationV1

Minimum authority-relevant fields:

- `schema_id`
- `generation`
- `predecessor_digest`
- `schema_digest`
- `operation_kind_registry_root`
- `slot_registry_root`
- `alias_registry_root`
- `materiality_policy_digest`
- `closed_world=true`
- `compiler_contract_version`
- `minimum_independent_checker_version`
- `activation_membership_epoch`
- `activation_frontier`
- `historical_coverage_requirement`
- `deprecated_slot_root`
- `reserved_slot_root`
- `trust_frontier`
- threshold signatures / authorization certificate.

A generation is immutable after activation.

## Stable declaration-slot identity

Each slot has a stable identifier independent of source-language symbol, field position or display name:

`slot_id = H(namespace || operation_family || semantic_role || slot_generation_origin)`

Each slot binds:

- edge/participant/recovery class;
- required/conditional/forbidden cardinality;
- destination-domain rule;
- derivation-key rule;
- materiality class;
- delayed/immediate semantics;
- cancellation semantics;
- required observation evidence;
- supersession/deprecation rule.

Once material, a `slot_id` is never reused for a different meaning. Removal reserves it permanently. Renames preserve identity. Semantic change requiring different obligations gets a new slot id.

## Operation-kind dispatch

Operation dispatch MUST be deterministic and total.

For every accepted runtime operation envelope:

`canonical_operation_kind(envelope, schema_generation) -> exactly one rule_id`

Unsafe states:

- two rules match one envelope -> `SCHEMA_AMBIGUOUS`;
- no rule matches a consequential envelope -> `SCHEMA_UNKNOWN_OPERATION`;
- alias chain cycles -> reject generation;
- alias resolves differently across checker implementations -> reject activation;
- catch-all/default rule for consequential unknown operations -> forbidden unless that rule requires a conservative superset of all possible material declarations and is separately authorized.

Operation identity is encoded canonically; locale, case folding, language enum ordinal and source-language class name are not authority inputs.

## Declaration-slot compiler

The compiler is a deterministic transform:

`compile(schema_digest, compiler_id, target_runtime) -> DeclarationProgram + CompilerManifest`

`CompilerManifest` binds:

- exact schema digest;
- compiler implementation/version digest;
- target runtime/ABI;
- canonical generated-artifact digest;
- operation->rule mapping root;
- rule->slot mapping root;
- reserved/deprecated slot roots;
- reproducibility metadata.

The producer and independent verifier MUST NOT rely solely on the same generated code blob. For consequential E2/E3/E4-class slots, at least one checker reinterprets the canonical schema through an independent implementation or validated IR.

Generated-code drift is detected by recomputing the compiler manifest from the activated schema. Runtime artifacts with a different schema digest or mapping root are rejected before effect release.

## Schema-completeness proof

No finite schema can mathematically prove it models every future semantic consequence. The useful safety claim is narrower and explicit:

`SchemaCompletenessProofV1` proves that, for a declared operation universe and materiality policy at a given trust/policy frontier:

1. every registered consequential operation kind has exactly one rule;
2. every rule's finite declaration-slot set is canonical and closed;
3. aliases are total, acyclic and unambiguous;
4. every materiality-policy obligation is mapped to at least one slot or to a reviewed `NOT_APPLICABLE` witness;
5. independent checker implementations agree on canonical operation->rule and rule->slot roots;
6. generated runtime artifacts match those roots;
7. coverage scanning establishes which historical/live operation generations were governed by this schema.

This is a proof of declared-universe completeness, not omniscience. A later discovered semantic class creates a schema-omission event and historical repair obligation.

## Independent completeness derivation

To avoid producer/schema common-mode bugs, define a second input domain: `OperationSemanticInventoryV1`.

This inventory is derived from authoritative product/runtime capability registration, not from the manifest schema itself, and records for each operation family the material capabilities it can invoke: storage mutation, external message, delayed scheduler, recovery dependency, authority transition, revocation propagation, archive move, GC reactivation, etc.

The independent checker computes required semantic classes from the inventory and requires the schema to discharge each class through a slot or explicit `NOT_APPLICABLE` witness. A schema that simply omits the class cannot make the checker forget it.

If the inventory and schema share one extractor/code generator, assurance is `SINGLE_DOMAIN_ASSURANCE`, not completeness.

## Schema rotation

Generation N+1 activation requires:

- authenticated predecessor N;
- threshold authorization under current schema authority and N+1 authority policy where authority itself changes;
- monotonic generation;
- explicit diff over operation kinds, aliases, material slots, materiality policy and compiler contract;
- downgrade analysis;
- coverage plan for historical operations affected by added/strengthened slots;
- mixed-generation rollout policy.

A removal or weakening of a material slot is deletion-authorizing and requires stronger review evidence than an additive strengthening.

Rollback to N after N+1 activation is forbidden except through a new N+2 generation that explicitly reinstates old semantics and carries current authorization.

## Partial rollout

Every producer effect records exact `schema_generation` and compiler manifest digest.

During rollout, barrier/finalization logic reasons per-effect; it MUST NOT infer generation from wall clock, host version or membership epoch alone.

If a producer that should have moved to N+1 emits under N after its authenticated activation frontier, reject/quarantine it as stale producer authority.

If N+1 introduces a new material slot, N-governed historical/live closures within declared coverage remain rooted until scan/repair establishes disposition.

## Late-discovered missing slot and fraud proof

`SchemaOmissionFraudProofV1` proves a material declaration class was absent from the activated schema itself, not merely omitted by one producer manifest.

Minimum evidence:

- authenticated schema generation and operation rule;
- authenticated operation/effect/manifest governed by that generation;
- independently authenticated semantic inventory or downstream effect evidence;
- materiality rule showing the consequence class was required;
- exact non-membership proof against the rule's slot-set commitment;
- alias/dispatch proof tying the operation to that rule;
- trust/policy frontiers.

Verdict: `SCHEMA_OMITTED_MATERIAL_SLOT_PROVEN`.

Consequences:

- affected generation/rule enters `REVALIDATION_REQUIRED`;
- affected finalization/GC certificates become stale;
- relevant historical closure becomes a GC root;
- schema authority may be quarantined/revoked by policy;
- repair is additive: publish N+1 plus authenticated historical repair edges/coverage, never mutate N bytes.

## Bounded historical repair

The fraud proof defines a blast-radius predicate over:

- schema generation range;
- affected canonical operation kinds/aliases;
- materiality class;
- producer membership epochs/frontiers;
- evidence retention horizon.

Only objects matching the predicate become mandatory repair candidates. Unknown scan gaps remain rooted. Unaffected operations may receive authenticated unaffected witnesses to avoid permanent global pinning.

## RED-first executable matrix (80 cases)

### A. Authority / publication
1. unsigned schema -> reject.
2. producer-only signature -> reject.
3. insufficient schema-authority threshold -> reject.
4. valid threshold -> admissible.
5. wrong predecessor digest -> reject.
6. skipped generation -> reject unless explicit authorized skip policy.
7. rollback generation -> reject.
8. expired/revoked schema authority -> reject new activation.
9. authority rotation lacking old threshold -> reject.
10. authority rotation lacking new threshold -> reject.

### B. Operation dispatch
11. one operation -> one rule -> accept.
12. no matching rule -> reject.
13. two matching rules -> reject ambiguous.
14. alias to exact rule -> accept.
15. alias cycle -> reject generation.
16. alias chain to missing rule -> reject.
17. case-fold collision -> reject canonical registry.
18. enum-ordinal drift -> reject artifact mismatch.
19. catch-all unknown consequential op -> reject.
20. conservative separately authorized fallback -> accept only under explicit policy.

### C. Slot identity / lifecycle
21. stable slot rename -> same id accepted.
22. reused deleted slot id with new semantics -> reject.
23. removed material slot not reserved -> reject generation.
24. duplicate slot id -> reject.
25. same label/different slot ids -> allowed only if unambiguous semantics.
26. changed materiality under same id -> reject semantic mutation.
27. additive new slot -> new id.
28. deprecated slot retained historically -> decode old generation.
29. reserved slot emitted by new producer -> reject.
30. slot cardinality weakened silently -> reject diff.

### D. Compiler / artifact binding
31. artifact schema digest mismatch -> reject.
32. compiler id mismatch -> reject.
33. operation->rule root mismatch -> reject.
34. rule->slot root mismatch -> reject.
35. stale generated artifact after schema rotation -> reject.
36. reproducible independent compile same roots -> accept.
37. nondeterministic compile differing roots -> reject activation.
38. producer+verifier same generated helper only -> mark weak assurance.
39. independent interpreter agrees -> strengthen assurance.
40. target ABI changes serialization semantics -> require new compiler manifest.

### E. Completeness proof
41. all inventory capabilities discharged -> accept proof.
42. storage mutation capability has no slot/witness -> reject.
43. delayed scheduler capability omitted -> reject.
44. recovery capability omitted -> reject.
45. authority transition omitted -> reject.
46. explicit reviewed not-applicable witness -> discharge.
47. schema invents inventory omission -> cannot discharge.
48. shared extractor for inventory+schema -> insufficient independence.
49. checker implementations disagree roots -> reject activation.
50. unknown materiality policy generation -> UNKNOWN/not safe.

### F. Downgrade / rotation
51. N+1 adds material slot -> historical coverage required.
52. N+1 removes E2/E3 slot -> stronger downgrade proof required.
53. N+1 changes alias target -> coverage analysis required.
54. N+1 adds operation kind -> compiler/checker update required.
55. stale producer emits N after activation frontier -> reject/quarantine.
56. N and N+1 coexist before frontier -> per-effect verification.
57. rollback to N bytes -> reject.
58. N+2 explicitly restores N semantics under current authority -> possible with new generation.
59. schema authority revoked mid-rollout -> freeze affected activation/finalization.
60. compiler authority revoked -> runtime artifacts revalidate; schema bytes remain historical.

### G. Schema omission fraud / repair
61. downstream effect maps to missing material slot -> fraud proof succeeds.
62. non-material omitted class -> fraud proof rejected.
63. wrong operation dispatch evidence -> fraud proof rejected.
64. forged downstream evidence -> reject.
65. exact non-membership against slot root -> omission proven.
66. commitment lacks sound non-membership -> retain full canonical set for proof.
67. proven omission stales finalization -> enforce.
68. proven omission re-roots affected closure -> enforce.
69. historical scan gap -> UNKNOWN/rooted.
70. unaffected witness with coverage proof -> release unaffected closure when other gates allow.

### H. Concurrency / recovery / GC
71. schema rotates while effect prepared -> commit only under immutable prepared generation or abort/reprepare.
72. schema rotates between manifest verify and release -> token binds generation; policy decides allowed frontier.
73. crash after schema activation before all producers update -> restart reconstructs rollout frontier.
74. duplicate activation certificate -> idempotent.
75. conflicting activation frontiers -> equivocation/block.
76. GC attempts delete old schema before historical challenge horizon -> reject.
77. archive relocation without verified retrieval -> no hot delete.
78. disaster recovery lacks historical schema generation -> cannot claim old manifest complete.
79. late auditor verifies old operation with exact old schema + repair chain -> deterministic verdict.
80. concurrent fraud proof and GC mark -> fraud/revalidation frontier invalidates stale mark before delete.

## Acceptance verdicts

Expose explicit states:

- `SCHEMA_AUTHENTICATED`
- `SCHEMA_AMBIGUOUS`
- `SCHEMA_UNKNOWN_OPERATION`
- `SCHEMA_COMPILER_MISMATCH`
- `SCHEMA_COMPLETENESS_PROVEN`
- `SCHEMA_SINGLE_DOMAIN_ASSURANCE`
- `SCHEMA_ROLLOUT_INCOMPLETE`
- `SCHEMA_OMITTED_MATERIAL_SLOT_PROVEN`
- `SCHEMA_REVALIDATION_REQUIRED`
- `UNKNOWN`

`UNKNOWN != SAFE_TO_RELEASE`, `UNKNOWN != SAFE_TO_FINALIZE`, and `UNKNOWN != SAFE_TO_GC`.

## Implementation direction

When executable source becomes available, implement tests before production changes. Start with a tiny canonical schema IR, two deliberately independent interpreters, a deterministic compiler manifest and an operation-semantic inventory fixture. RED tests should first demonstrate that producer+verifier agreement on the same defective schema falsely accepts an omitted slot; GREEN should add independent inventory discharge and fail before effect release.

Do not make generated code the durable source of truth. Durable authority is the canonical schema generation + authorization + compiler manifest + independent completeness proof + historical coverage evidence.

## Frozen conclusion

`MANIFEST_SCHEMA_AUTHORITY_DECLARATION_SLOT_COMPILER_SCHEMA_COMPLETENESS_PROOF_V1_FROZEN`.

Producer-path manifest binding is only sound when the closed-world declaration schema is itself authenticated, monotonic, unambiguous, independently checked against a separately derived semantic inventory, compiler-bound, rollout-frontier-bound and historically repairable. A signed schema is authority evidence, not proof that the schema remembered every material slot.