# Verifier conformance-corpus completeness, parser differential testing, and scoped semantic-equivalence proof v1

Date: 2026-09-07
Status: FROZEN DESIGN CONTRACT
Contract id: `VERIFIER_CONFORMANCE_CORPUS_PARSER_DIFFERENTIAL_SCOPED_EQUIVALENCE_V1_FROZEN`
Related: LAB-093/#178; archive verifier durability chain; LAB-086 remains execution priority #1.

## Objective

Define when a frozen verifier replay corpus is strong enough to justify migration from verifier generation `N` to `N+1`, and when apparent agreement is merely sampled compatibility that must not be promoted into a universal semantic-equivalence claim.

This contract is intentionally narrower than full formal equivalence. For non-trivial parser/canonicalizer/cryptographic stacks, finite testing cannot prove that two implementations are equivalent for every possible byte string. The safe claim is therefore scoped: equivalence is established only for an explicitly frozen input language/profile, policy generation, accepted evidence schemas, cryptographic suites, and adversarial dimensions whose coverage is itself authenticated.

## Primary-source mechanisms and donors

1. RFC 8785 (JSON Canonicalization Scheme): canonicalization exists precisely because cryptographic operations require invariant representations. JCS also makes several security-relevant parser constraints explicit: duplicate property names are not allowed in the I-JSON subset; lone Unicode surrogates must cause failure; parsed string data must not be silently normalized; number handling is constrained to IEEE-754-compatible JSON numbers. These are direct corpus dimensions for canonicalizer/parser migration.
2. RFC 8949 (CBOR): deterministic encoding imposes concrete canonical rules including prohibition of indefinite-length items in deterministic encoding and deterministic map-key ordering. These supply canonical/non-canonical equivalence classes and rejection cases.
3. Project Wycheproof: implementation-independent cryptographic test vectors encode known attacks, specification inconsistencies, edge cases, and expected validity outcomes. This is a donor for cryptographic edge-case partitions, but not a complete proof of all crypto semantics.
4. Language-theoretic Security (LangSec): parser correctness must be grounded in an explicit input language, and computational equivalence of protocol endpoints matters because semantic gaps create attack surface. This supports defining a grammar/profile rather than treating arbitrary bytes as an undocumented parser contract.
5. USENIX Security 2025, “My ZIP isn't your ZIP”: differential fuzzing across many parsers systematically exposed semantic gaps caused by ambiguous format interpretation. This is direct evidence that implementation agreement on happy-path samples is not enough.
6. NDSS DiffCSP: differential testing across independent implementations found security and functional bugs, including differences caused by unclear specifications. This is a donor for differential-oracle design and for the rule that disagreement may reveal specification ambiguity rather than identify one implementation as automatically correct.

## Core decision

`CORPUS_AGREEMENT != UNIVERSAL_EQUIVALENCE`.

A verifier generation migration may claim only:

`SCOPED_SEMANTIC_EQUIVALENCE(profile_id, policy_generation, schema_set, crypto_suite_set, corpus_root, generator_root, coverage_manifest_root)`

and only when every required closure condition below is satisfied.

No finite replay corpus may produce a repository claim equivalent to “N and N+1 accept/reject every possible input identically” unless a separate formal proof establishes that property for the exact parser/canonicalizer/policy implementations.

## Model

### 1. `VerifierSemanticProfileV1`

Fields:
- `profile_id`
- `profile_version`
- `accepted_media_types`
- `accepted_schema_generations`
- `grammar_digest`
- `canonicalization_rules_digest`
- `normalization_rules_digest`
- `duplicate-field_policy`
- `unknown-field_policy`
- `numeric_domain_policy`
- `unicode_policy`
- `depth_size_resource_limits`
- `cryptographic_suite_set`
- `historical_trust_policy_digest`
- `receipt_semantics_digest`
- `error_classification_policy_digest`
- `evaluation_side_effect_policy`

The profile defines the language and semantics being compared. Inputs outside the profile are not “equivalent by omission”; their migration verdict is `OUT_OF_PROFILE` or `UNKNOWN`.

### 2. `ConformanceCorpusManifestV1`

Each case records:
- immutable `case_id`
- exact input bytes digest + size
- provenance (`historical_real`, `spec_example`, `grammar_generated`, `mutation_generated`, `differential_found`, `crypto_vector`, `manual_adversarial`)
- semantic profile + schema generation
- expected parse class
- expected canonical bytes digest or `REJECT`
- expected verifier verdict (`VALID`, `INVALID`, `UNKNOWN`, `OUT_OF_PROFILE`)
- expected normalized semantic object digest where applicable
- expected error class where rejection semantics matter
- adversarial dimensions/tags covered
- minimization lineage for fuzz-discovered cases
- source/generator seed and generator version when generated

The corpus root is a Merkle/content root over exact case bytes plus expected semantics, not only filenames or test code.

### 3. `CorpusCoverageManifestV1`

Coverage is semantic, not just line/branch coverage. Required dimensions include:
- grammar production/alternative coverage;
- field-presence/absence matrix;
- duplicate key/field behavior;
- ordering permutations;
- canonical vs non-canonical encodings;
- integer/floating boundaries and alternate representations;
- Unicode controls, noncharacters, combining sequences, lone surrogates where the format permits bytes that can express them;
- length-prefix and truncation boundaries;
- nested depth and resource-limit boundaries;
- unknown extension/tag behavior;
- trailing bytes and concatenated-object behavior;
- ambiguous delimiter/whitespace/comment behavior where relevant;
- parser recovery behavior after malformed input;
- signature/key/curve/hash parameter boundaries;
- malformed DER/raw signature forms where applicable;
- invalid points, small-order points, non-canonical signatures, high/low-S or equivalent suite-specific cases;
- expired/not-yet-valid/revoked/unknown historical trust evidence;
- missing or contradictory transparency/timestamp/status evidence;
- schema downgrade/upgrade collisions;
- canonicalization collisions (distinct raw inputs mapping to same canonical semantic object) and anti-collisions (semantically different objects that must remain distinct);
- parser resource exhaustion and bounded failure behavior.

A coverage manifest may additionally include implementation code coverage, but code coverage alone cannot satisfy semantic coverage.

### 4. `GeneratorProvenanceV1`

Grammar/mutation generators are themselves archived verifier dependencies:
- exact generator source/binary digest;
- grammar digest;
- seed corpus root;
- deterministic PRNG seed set where possible;
- mutation operators and weights;
- generation budget;
- minimizer digest;
- rejection classifier digest;
- produced-case root.

This makes later replay able to reproduce or extend the adversarial population without relying on a vanished fuzzing framework.

### 5. `DifferentialExecutionProofV1`

For each candidate migration, execute at least:
- historical verifier `N`;
- candidate verifier `N+1`;
- where available, one or more independently implemented reference parsers/canonicalizers/crypto implementations that do not share the same parser library or adapter path.

Record for every case:
- raw parse accept/reject;
- parsed semantic-object digest;
- canonical bytes digest;
- cryptographic verification result;
- historical trust result;
- final verifier verdict;
- error class;
- resource-limit outcome.

Agreement on only the final boolean is insufficient. Two implementations can both return `INVALID` for materially different reasons, or both return `VALID` while canonicalizing to different signed bytes.

### 6. `SemanticDivergenceV1`

A divergence is any difference in authority-relevant semantics, including:
- accept vs reject;
- different canonical bytes;
- different semantic object;
- different identity/resource/fence/generation binding;
- different signature/trust verdict;
- different handling of duplicated/unknown fields;
- different fail-open/fail-closed classification;
- different resource-exhaustion outcome that changes whether consequential work proceeds.

Every divergence is triaged into one of:
- `N_BUG_FIXED_BY_NPLUS1`
- `NPLUS1_REGRESSION`
- `SPEC_AMBIGUITY`
- `PROFILE_INTENTIONAL_CHANGE`
- `OUT_OF_PROFILE`
- `UNKNOWN_ROOT_CAUSE`

Only `N_BUG_FIXED_BY_NPLUS1` or an explicitly approved `PROFILE_INTENTIONAL_CHANGE` may alter historical expectations, and then the change requires a new semantic profile/policy generation rather than silently preserving the old equivalence claim.

## Corpus-construction requirements

### A. Historical real evidence

Include every historical evidence shape that was actually accepted or rejected in production/archive history, subject to privacy/secrets handling. Deduplicate by semantic class only after preserving exact-byte exemplars for ambiguous/canonicalization-sensitive cases.

### B. Specification examples and boundary derivation

For every normative MUST/MUST NOT or equivalent constraint in the supported serialization/canonicalization/crypto specifications, create at least one positive and one adjacent negative/boundary case where mechanically meaningful.

Examples derived directly from RFC 8785 include duplicate JSON names, lone surrogates, property-order changes, whitespace variants, IEEE-754 edge cases, escape representation variants, and Unicode normalization lookalikes that must remain byte/semantic-distinct when the scheme says strings are preserved as-is.

Examples derived from deterministic CBOR include indefinite-length alternatives, non-shortest numeric encodings, float-width alternatives, and map-key ordering variants.

### C. Grammar-derived adversarial generation

The grammar is used both positively and negatively:
- generate valid structures from every production;
- mutate one grammar constraint at a time;
- generate near-boundary invalid structures;
- combine valid prefixes/suffixes from different productions;
- recursively stress nesting and size limits;
- exercise extension/tag namespaces and reserved values.

Generation must preserve a mapping from case to grammar production/operator so coverage is auditable.

### D. Metamorphic relations

Required metamorphic properties are stronger than example replay because they generate equivalence classes:
- allowed whitespace/property-order transformations preserve semantics but canonicalize identically where the profile specifies that;
- semantically irrelevant transport wrapping must not alter signed semantic identity;
- adding an unknown field either deterministically rejects or follows the frozen unknown-field policy; it may not vary by implementation;
- duplicate-field insertion must follow the frozen rejection/handling rule;
- canonicalize(canonicalize(x)) = canonicalize(x) for accepted canonicalizable inputs;
- parse(canonicalize(x)) yields the same frozen semantic-object digest as parse(x) where canonicalization is defined;
- signature verification over canonical bytes must be invariant to non-semantic raw representation changes and must fail if an authority-relevant semantic field changes.

### E. Cryptographic vectors

Import applicable Wycheproof-style vectors and suite-specific standards vectors. Preserve exact vector provenance/version. Add local vectors for binding semantics that generic crypto suites cannot cover, such as wrong resource id, wrong generation, wrong fence, wrong provider id, wrong historical trust generation, and cross-schema replay.

### F. Differential fuzzing

Run generated/mutated cases across independent implementations. Any disagreement becomes a retained minimized regression case, even if a specification reading later identifies which side was correct.

Differential fuzzing is a discovery mechanism, not an oracle of truth. Majority vote is prohibited for authority semantics.

## Equivalence rule

`ScopedSemanticEquivalenceProofV1` may be `CLOSED` only when all are true:

1. Exact N and N+1 verifier artifacts and execution substrates are identified by immutable digest.
2. Semantic profile/policy generation is identical, or an intentional migration profile explicitly maps the permitted semantic delta.
3. Corpus, expected outcomes, generator provenance, coverage manifest, and independent reference implementations are all pinned.
4. Every frozen case executes on N and N+1 without unexplained divergence.
5. Grammar/spec/metamorphic required dimensions meet the declared coverage thresholds.
6. Applicable cryptographic edge suites are present and pass the frozen expected outcomes.
7. Every differential-fuzzing divergence discovered within the declared campaign is minimized, retained, and resolved or explicitly moved to a new profile generation.
8. Canonical bytes and semantic-object digests agree, not only final booleans.
9. No required case is skipped because a dependency/runtime/parser feature is unavailable.
10. Replay is performed in the hermetic/offline verifier environment defined by the preceding verifier-durability contract.
11. The proof states its scope and never upgrades finite evidence into universal equivalence.

If any required dimension is absent or an unexplained divergence remains, verdict is `UNKNOWN_EQUIVALENCE`, not PASS.

## Coverage policy

No single numeric percentage is a sound universal threshold. Instead use a conjunctive policy:

- 100% of frozen normative-rule inventory mapped to at least one case or authenticated `NOT_APPLICABLE` rationale;
- 100% of supported grammar productions reached by at least one positive case and, where meaningful, one adjacent invalid mutation;
- 100% of declared canonicalization equivalence classes exercised;
- 100% of declared authority-binding fields independently mutated with expected rejection;
- 100% of supported cryptographic suites covered by applicable known-attack/boundary vectors;
- all discovered differential divergences retained;
- implementation branch/condition coverage tracked as an advisory regression signal, never as the completeness proof itself.

Any downgrade of the declared profile/coverage universe requires a new policy generation and explicit migration evidence.

## Fail-closed semantics

Return `UNKNOWN_EQUIVALENCE` when:
- grammar/profile is incomplete or undocumented;
- a parser accepts inputs outside the frozen language and behavior is unspecified;
- corpus provenance/root is missing;
- expected verdicts were regenerated using only N+1 rather than independently frozen;
- an independent implementation disagrees and the cause is unresolved;
- a required crypto vector family cannot execute;
- canonical bytes cannot be compared;
- resource-limit behavior differs in a way that could allow consequential processing;
- corpus/generator/minimizer bytes are unavailable;
- a historical case is omitted due to parser crash or unsupported old schema;
- fuzzing found an ambiguity but the specification/profile has not resolved it.

## Fraud / contradiction proofs

### `CorpusOmissionProofV1`
Shows a required normative rule, grammar production, authority-binding field, historical case class, or discovered differential divergence absent from the sealed corpus/coverage manifest.

### `BooleanOnlyAgreementFraudProofV1`
N and N+1 return the same final boolean but produce different canonical bytes or semantic-object digests.

### `SelfOracleFraudProofV1`
Expected outcomes for migration were generated solely from N+1 or an implementation sharing its parser/canonicalizer path, so replay merely confirms itself.

### `MajorityVoteSemanticFraudProofV1`
Multiple parsers disagree and the selected truth value is justified only by majority vote rather than normative semantics/profile decision.

### `ProfileShrinkFraudProofV1`
N+1 obtains a clean corpus by silently removing a formerly supported schema, crypto suite, grammar production, or adversarial dimension without a new policy/profile generation.

### `GeneratorDriftFraudProofV1`
A later replay claims equivalent adversarial generation while grammar, mutation operators, seeds, minimizer, or generator implementation changed without a new generator provenance root.

## 80-case RED-first matrix

The implementation phase must instantiate at least the following families (10 cases each, exact case design may expand but not weaken them):

1. JSON/parser ambiguity: duplicate keys in varied positions; trailing bytes; BOM; escape variants; invalid/lone-surrogate sequences; control characters; top-level type mismatch; truncation; huge numeric exponent; signed zero/number formatting boundary.
2. Canonicalization: property-order permutations; whitespace variants; Unicode lookalikes without normalization; number representation aliases; idempotence; distinct semantic objects that must not collide; unknown field policy; nested object ordering; canonical/raw signature binding; canonicalization rejection propagation.
3. CBOR/binary-style deterministic semantics where used: indefinite length; non-shortest integer; float width; map ordering; duplicate map keys; unknown tags; trailing bytes; nested depth; length mismatch; canonical re-encode idempotence.
4. Schema/version: missing required field; unknown field; duplicate semantic alias; old/new field collision; downgrade replay; upgrade-only field; enum reserved value; default-value ambiguity; nullable/non-nullable collision; cross-schema canonical digest collision attempt.
5. Authority binding: mutate resource id; provider id; generation; fence; operation id; receipt id; issuer epoch; historical trust generation; policy generation; timestamp/checkpoint binding while retaining an otherwise valid signature.
6. Crypto: applicable Wycheproof known-invalid vectors; malformed signature encoding; wrong key; wrong curve/suite; truncated signature; non-canonical signature if suite relevant; boundary key material; revoked/expired/not-yet-valid trust evidence; timestamp after effective invalidity; unsupported algorithm downgrade.
7. Differential/parser: N accept vs N+1 reject; reverse; same accept/different AST; same AST/different canonical bytes; same final boolean/different error cause; independent parser disagreement; three-way disagreement; parser crash; timeout/resource exhaustion; implementation-specific extension acceptance.
8. Generator/metamorphic/replay: grammar production unvisited; invalid-neighbor mutation missing; metamorphic relation violated; seed reproducibility failure; minimizer changes semantics; historical real case absent; generator version drift; corpus-root mismatch; skipped case due missing dependency; profile shrink masked as pass.

All RED cases must demonstrate the old/insufficient migration checker fails to detect the intended weakness before the production closure rule is considered GREEN.

## Migration lifecycle

1. Freeze N semantic profile, exact verifier bundle, corpus root, expected-result root, generator root, coverage manifest.
2. Add new adversarial cases before evaluating N+1 where possible, preventing candidate-specific overfitting.
3. Execute N, N+1, and independent references hermetically.
4. Retain every disagreement as exact bytes plus minimized lineage.
5. Resolve against normative profile; do not majority vote.
6. Re-run full corpus after each semantic fix.
7. Produce `ScopedSemanticEquivalenceProofV1` with explicit scope and exclusions.
8. Only then may N+1 become the preferred verifier generation; N remains archived per verifier-durability policy.
9. New post-migration differential findings retroactively open a new migration audit; they do not rewrite the old signed proof.

## Security boundary and non-claims

- This contract does not prove arbitrary parser equivalence.
- It does not make fuzzing exhaustive.
- It does not treat line/branch coverage as language coverage.
- It does not treat multiple implementations as independent if they share the same parsing/canonicalization dependency.
- It does not allow current implementation behavior to redefine historical expected semantics without a policy-generation transition.
- It does not allow parser tolerance to expand the authenticated evidence language implicitly.

## Implementation recommendation

For LAB-093/archive-verifier implementation, make the corpus and coverage manifests first-class content-addressed archive objects. The replay runner should emit machine-readable per-stage results (parse, normalized semantic object, canonical bytes, crypto, historical trust, final policy) so differential comparison happens before final verdict collapse. Generate grammar/metamorphic cases from a frozen profile DSL where feasible and import version-pinned external crypto vectors. Treat every newly discovered differential as a permanent regression seed.

## Next research edge

After this contract, the next distinct unresolved evidence question is **conformance-corpus oracle independence / expected-verdict provenance / specification-ambiguity adjudication semantics**: how expected outcomes themselves are authenticated without circularly trusting verifier N, verifier N+1, or one mutable standards interpretation; how human/spec decisions become durable policy generations; and how later standards errata affect historical replay without silently rewriting old truth.
