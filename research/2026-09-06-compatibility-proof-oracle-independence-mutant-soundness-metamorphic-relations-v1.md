# Compatibility proof oracle independence / mutant soundness / metamorphic relations V1

Date: 2026-09-06
Status: `COMPATIBILITY_PROOF_ORACLE_INDEPENDENCE_MUTANT_SOUNDNESS_METAMORPHIC_RELATIONS_V1_FROZEN`
Owner context: LAB-093/#178 follow-up to the frozen semantic-diff and distinguishing-corpus contracts.

## Why this contract exists

The preceding compatibility-proof contract requires every consequential semantic delta to produce witness obligations, positive fixtures, and a controlled negative mutant that the retained corpus can kill. That is necessary but not sufficient.

A test can still be self-fulfilling if the implementation under test and its oracle are generated from the same faulty interpretation. A mutant can also be useless because it is semantically equivalent, unrealistically broken, unreachable, masked by another mutation, or changes a different semantic dimension from the obligation it is supposed to prove.

Therefore a compatibility edge is not admissible merely because `candidate == oracle` on positive fixtures and `candidate != mutant` on negative fixtures. It must additionally establish oracle independence, mutant soundness, reachability, dimension fidelity, and at least one independent metamorphic relation where a stable relation can be stated without copying the same transformation logic.

## Donor evidence

This contract uses mutation testing and metamorphic testing as donor mechanisms, not as authority by themselves.

- Mutation testing treats mutants as small seeded faults and a test suite as adequate when it distinguishes them. Recent empirical work reiterates the coupling-effect rationale but also finds that common mutation operators can miss important classes of real faults. Source: Ahmed et al., 2024, DOI `10.1002/stvr.1874` — https://onlinelibrary.wiley.com/doi/full/10.1002/stvr.1874
- Equivalent mutants are a fundamental limitation: some syntactic mutants preserve program semantics and therefore cannot be killed by any correct test suite. Source: Schuler & Zeller, 2013, DOI `10.1002/stvr.1473` — https://onlinelibrary.wiley.com/doi/abs/10.1002/stvr.1473
- Metamorphic testing addresses the oracle problem by asserting relations across transformed inputs and outputs instead of depending only on a single expected-output oracle. Source: Altamimi et al., 2023, DOI `10.1002/smr.2509` — https://onlinelibrary.wiley.com/doi/10.1002/smr.2509
- The oracle problem is the core reason metamorphic testing exists; metamorphic relations are only useful when the relation itself is independently justified rather than inferred from the same faulty implementation. Source: Chen et al., IEEE AST 2015, DOI `10.1109/AST.2015.18` — https://ieeexplore.ieee.org/document/7166267/

## Frozen decision

A consequential compatibility proof is admissible only when all of the following are true for every retained witness obligation:

1. the semantic dimension is explicit;
2. the positive fixture reaches the intended branch/state;
3. the negative mutant changes exactly one prohibited interpretation, or a declared minimal interaction set;
4. the mutant is demonstrably non-equivalent for the obligation;
5. the oracle does not reuse the same transformation/codegen/extractor path whose correctness it is judging;
6. at least one independent relation, reference source, dual implementation, algebraic invariant, or historical authenticated artifact constrains the verdict;
7. mutation masking and nondeterministic provider behavior are excluded or surfaced as `INCONCLUSIVE`, never silently accepted;
8. the mutant catalog, oracle implementation, fixture generator, semantic model generation and proof output are all provenance-bound.

## Oracle independence model

### Independence classes

Each oracle is classified as one of:

- `SPEC_DERIVED`: hand-written or mechanically checked directly from a normative provider/spec statement, without invoking candidate codegen/serializer/extractor logic.
- `DUAL_IMPLEMENTATION`: a separately implemented parser/normalizer/verifier with an independently maintained code path and dependency graph.
- `AUTHENTICATED_HISTORICAL`: a privacy-minimized authenticated historical artifact whose semantic interpretation was committed before the candidate generation existed.
- `ALGEBRAIC_METAMORPHIC`: a relation that must hold across controlled transformations even when no absolute expected output is available.
- `PROVIDER_OBSERVED`: an externally observed provider result, usable only when the provider behavior is deterministic enough for the exact assertion and the observation is bound to provider/model/version/time/capability metadata.
- `SAME_PIPELINE`: derived from the same generator, serializer, schema projection, extractor or reconciliation path as the candidate. This class is never sufficient on its own for consequential admission.

### Common-mode prohibition

The following are non-independent and cannot alone authorize an edge:

- candidate DTO and expected DTO both generated from the same schema generator;
- candidate serializer and oracle serializer sharing the same mapping table;
- candidate parser and oracle parser both consuming the same generated field descriptors;
- expected signing payload produced by the same canonicalizer under test;
- expected retry class produced by the same provider error classifier under test;
- replay output compared against a fixture generated by running the same replay adapter;
- snapshot tests whose snapshot was automatically regenerated from the candidate after a semantic delta.

Shared low-level primitives are allowed only when they are not the disputed semantic transform. Example: both sides may use SHA-256, but both sides may not use the same candidate canonicalization routine before hashing when canonicalization is the property being tested.

## Mutant soundness model

Every mutant carries a machine-readable descriptor:

- `mutant_id`;
- source and target semantic generation;
- obligation id(s);
- exact semantic dimension;
- operator;
- intended prohibited interpretation;
- modified artifact/path;
- expected observable divergence;
- reachability predicate;
- equivalence-check status;
- interaction set if higher-order;
- provenance digest.

### Accepted mutant classes

A mutant must be one of:

- `FIRST_ORDER_SEMANTIC`: one semantic interpretation changed;
- `MINIMAL_INTERACTION`: the smallest declared set of coordinated changes necessary to express a prohibited interpretation that cannot exist as a first-order change;
- `HISTORICAL_REINTERPRETATION`: reinterpretation of an already authenticated historical fixture under a newer model/runtime;
- `BOUNDARY_MUTANT`: exact boundary shift such as inclusive/exclusive cutoff, absent/default collapse, unknown-enum rejection/acceptance, or retry-state reclassification.

### Rejected mutant classes

Reject and do not count toward adequacy:

- compile/syntax errors when the real prohibited interpretation is runtime-valid;
- always-raise / always-return / delete-whole-subsystem mutants;
- unrelated auth failures used to claim presence/default coverage;
- mutations that make the target path unreachable;
- mutations already forbidden by an earlier validation layer when the obligation is specifically about a downstream semantic layer, unless the purpose is to prove defense in depth and this is declared;
- broad multi-field changes where no minimal interaction proof exists;
- mutants that differ only in debug/log output when the obligation concerns request effect, replay, evidence, reconciliation or disclosure;
- stale mutants generated against a different semantic-model generation without an explicit transport proof.

## Equivalent-mutant handling

Equivalent mutants are expected and are not test failures. They are proof obligations.

A surviving mutant is classified as one of:

- `KILLED` — retained fixtures/oracles distinguish it as intended;
- `EQUIVALENT_PROVEN` — semantic equivalence is proven for the scoped obligation by canonical semantics or exhaustive finite-domain reasoning;
- `LIKELY_EQUIVALENT` — strong evidence exists but no proof; cannot count as killed or admissible evidence;
- `UNREACHED` — fixture did not execute the mutated semantic path;
- `MASKED` — another transformation prevented the expected divergence;
- `ORACLE_WEAK` — path was reached but oracle could not distinguish the intended semantic difference;
- `NONDETERMINISTIC` — provider/environment observation is unstable;
- `INVALID_MUTANT` — mutation did not faithfully encode the intended prohibited interpretation.

Only `KILLED` and `EQUIVALENT_PROVEN` discharge a mutant obligation. `LIKELY_EQUIVALENT`, `UNREACHED`, `MASKED`, `ORACLE_WEAK`, `NONDETERMINISTIC`, and `INVALID_MUTANT` block the affected compatibility edge until resolved or the obligation is redefined with recorded authority.

## Metamorphic relations required by semantic dimension

Metamorphic relations complement but do not replace exact expected-output oracles when an exact oracle exists.

### Presence/default

For a field where `absent`, `explicit default`, and `non-default` are semantically distinct:

- serialization/parsing round-trip must preserve the declared presence class;
- transforming `absent -> explicit default` may change presence-sensitive evidence/replay commitments even when wire scalar value is equal;
- transforming `explicit default -> non-default` must change the semantic commitment in the field's declared domain;
- adding an unrelated optional field must not collapse presence state of the target field.

A candidate that normalizes absent and explicit-default identically fails if the model declares presence-sensitive semantics.

### Enum / union openness

For open enum/union domains:

- replacing a currently known symbolic value with a future/unknown numeric or tagged value must preserve the raw unknown value through evidence/replay where the provider model requires open-world behavior;
- adding a new known enum symbol to the registry must not reinterpret a historical unknown value into a different historical byte/value commitment;
- known-value behavior must remain stable when an unrelated future enum value is added.

For closed domains, the inverse relation applies: unknown values must continue to fail at the same declared admission boundary rather than drift into a default branch.

### Signing / canonical request scope

- modifying a field outside the signed/canonical scope must leave the canonical signature input unchanged;
- modifying a field inside scope must change the canonical signature input unless the spec explicitly declares a normalized equivalence;
- reordering order-insensitive inputs must preserve the canonical commitment;
- reordering order-sensitive inputs must change it;
- the oracle canonicalizer must be independent of the candidate canonicalizer.

### Idempotency / retry

- replaying the same exact idempotency identity must not create a second authority identity;
- changing only transport-local nondeterminism must not change semantic idempotency identity;
- changing an authority-relevant request field must change the semantic idempotency/effect commitment where required;
- timeout/cancel/error transformations may only move among retry states allowed by the frozen transport-evidence classifier; they must never transform an `UNKNOWN` attempt into proof of `FAILED_BEFORE_IO` without independent evidence.

### Error classification

- changing presentation-only text while preserving provider error code/status/details must not change the semantic error class;
- changing the authority-relevant provider code/status must change the class exactly when the registry mapping declares it;
- adding an unknown error code must follow the declared open/closed fallback and must not silently alias a known retry-safe error;
- wrapper exceptions must preserve the underlying semantic commitment if the provider error identity is retained.

### Historical replay

- replay under the original bound generation must reproduce the original semantic commitment;
- replay under a newer generation that is proven compatible must preserve authority/effect/evidence/reconciliation semantics even if representation changes;
- replay under an edge marked incompatible must fail closed rather than reinterpret the historical artifact;
- adding newly known enum/error/schema fields cannot rewrite already authenticated historical meaning;
- historical fixture expectations are immutable; a newer generator may add a new interpretation layer but may not mutate the source fixture or its original commitment.

## Mutation masking and interaction rules

A mutant is `MASKED` when a distinct transform prevents the intended semantic difference from reaching the oracle. Masked mutants cannot be counted as kills.

For correlated deltas:

1. first test each first-order semantic mutant independently where representable;
2. identify shared predicates/impact-cone nodes;
3. synthesize the smallest interaction mutant needed to expose the coupled interpretation;
4. retain at least one witness that kills each first-order mutant and each required interaction mutant;
5. do not infer interaction coverage from killing only a broad higher-order mutant.

## Nondeterministic provider observations

Provider observations are never treated as stable truth unless the tested property is explicitly deterministic under the bound provider capability/model/version.

For nondeterministic outputs:

- prefer invariants over exact values;
- record allowed relation/range/set;
- repeat only when repetition itself does not create consequential side effects;
- if a one-shot consequential provider call cannot be safely repeated and no independent deterministic oracle exists, classify the proof `INCONCLUSIVE` rather than widening acceptance;
- never mask flaky oracle behavior with retries that change the authority/effect history.

## Provenance and generation binding

Each compatibility-proof bundle must commit to:

- source and target provider-model generation;
- normalized semantic closure digest;
- codegen generation and artifact digests;
- semantic-diff generation;
- impact-cone generation;
- fixture-synthesizer generation;
- mutant-catalog generation;
- oracle implementation/source generation;
- metamorphic-relation catalog generation;
- historical fixture frontier;
- test harness/runtime generation;
- result digest and verdict.

A newer registry frontier that discovers a missing semantic dimension, stronger oracle, invalid mutant, or previously equivalent mutant becoming distinguishable moves affected historical edges to `REVALIDATION_REQUIRED`. It does not silently rewrite the old proof bundle.

## Admission verdicts

Per compatibility dimension, only:

- `PROVEN_COMPATIBLE` — all obligations discharged with independent admissible proof;
- `PROVEN_INCOMPATIBLE` — at least one valid witness proves forbidden semantic drift;
- `REVALIDATION_REQUIRED` — proof was once admitted but a newer authenticated frontier invalidates an assumption or adds an obligation;
- `INCONCLUSIVE` — weak/common-mode oracle, unresolved equivalent mutant, nondeterminism, unreachable witness, stale provenance, masking, or missing relation.

`INCONCLUSIVE` is fail-closed for consequential activation, replay widening, evidence-schema widening, retry-policy widening, disclosure widening, and provider capability promotion.

## RED-first matrix

Freeze the following 80 cases before implementation.

### A. Oracle independence (1-16)
1. candidate + oracle share generator mapping table -> reject;
2. candidate + oracle share canonicalizer under test -> reject;
3. candidate + oracle share retry classifier under test -> reject;
4. snapshot regenerated from candidate after drift -> reject;
5. independent hand-coded spec oracle kills mutant -> admit evidence;
6. dual implementation agrees on positive and diverges on mutant -> admit evidence;
7. authenticated historical oracle predates candidate -> admit evidence;
8. same low-level SHA primitive, independent canonicalizers -> allowed;
9. shared disputed normalization helper -> reject;
10. oracle provenance missing -> `INCONCLUSIVE`;
11. oracle generation stale relative to model frontier -> revalidation;
12. oracle itself changes expected historical fixture -> reject;
13. two nominally independent oracles import same generated descriptor -> reject independence claim;
14. provider-observed oracle lacks version/model binding -> reject;
15. provider-observed deterministic property with binding -> allowed;
16. algebraic relation plus exact independent oracle both hold -> strongest evidence.

### B. Mutant fidelity / equivalence (17-32)
17. single prohibited default-collapse mutant -> valid;
18. syntax-error mutant -> invalid;
19. always-raise mutant -> invalid;
20. unrelated auth break used for enum obligation -> invalid;
21. mutant path unreachable -> `UNREACHED`;
22. mutant changes intended branch and fixture reaches it -> valid;
23. semantic-equivalent reorder under order-insensitive spec -> `EQUIVALENT_PROVEN`;
24. suspected but unproved equivalent -> `LIKELY_EQUIVALENT`, blocks;
25. equivalent mutant not counted as killed;
26. broad 5-field mutant without interaction proof -> invalid;
27. minimal 2-field interaction mutant with proof -> valid;
28. stale mutant against old model generation -> reject;
29. representation-only mutant for effect obligation -> invalid;
30. boundary inclusive/exclusive mutant -> valid;
31. historical reinterpretation mutant -> valid;
32. mutant descriptor missing expected divergence -> reject.

### C. Presence/default metamorphics (33-40)
33. absent round-trip remains absent;
34. explicit default remains explicitly present when semantics require;
35. absent vs explicit default commitment diverges when required;
36. non-default changes commitment;
37. unrelated optional field addition does not collapse presence;
38. candidate collapses absent/default -> kill;
39. oracle shares same collapse bug -> independence detector rejects proof;
40. historical absent fixture cannot be rewritten as explicit default.

### D. Enum/union openness (41-48)
41. open unknown enum raw value preserved;
42. registry later names historical unknown value without rewriting history;
43. unrelated future enum addition leaves known values stable;
44. closed enum unknown still rejects;
45. open->closed accidental drift mutant killed;
46. closed->open accidental widening mutant killed;
47. default/zero enum does not mask unknown future value;
48. oracle generated from same stale enum table rejected as sole oracle.

### E. Signing / effect / retry (49-60)
49. out-of-scope field change leaves signature input stable;
50. in-scope field change alters signature input;
51. order-insensitive reorder stable;
52. order-sensitive reorder diverges;
53. independent canonicalizer catches candidate omission;
54. same idempotency identity preserves one semantic authority identity;
55. transport-local nondeterminism does not alter semantic idempotency identity;
56. authority-relevant request change alters effect commitment where required;
57. timeout mutant cannot downgrade `UNKNOWN` to `FAILED_BEFORE_IO`;
58. certified-not-processed transport proof may permit exact retry state transition;
59. hidden SDK retry mutant is killed by attempt-count/evidence oracle;
60. retry oracle sharing candidate classifier rejected.

### F. Errors / reconciliation (61-68)
61. presentation text change leaves semantic class stable;
62. authority-relevant error code change updates class;
63. unknown error follows declared open/closed fallback;
64. unknown error cannot alias known retry-safe class silently;
65. wrapper preserves underlying error commitment;
66. error mutant masked by earlier generic exception -> `MASKED`;
67. reconciliation parser independent of candidate error DTO kills drift;
68. provider nondeterministic message field excluded from semantic oracle.

### G. Historical replay / provenance (69-80)
69. original generation replays original commitment;
70. proven-compatible newer generation preserves semantics;
71. incompatible generation fails closed;
72. historical fixture immutable under new generator;
73. newly known enum cannot rewrite old unknown commitment;
74. newly mapped error cannot rewrite authenticated historical class without explicit versioned interpretation;
75. stale oracle frontier -> `REVALIDATION_REQUIRED`;
76. newly discovered mutant obligation reopens edge;
77. mutant catalog downgrade cannot erase newer obligation;
78. common-mode bug found in both old candidate/oracle invalidates edge prospectively and triggers revalidation;
79. nondeterministic provider-only oracle with no safe repeat -> `INCONCLUSIVE`;
80. full bundle has source/target model, diff, cone, fixtures, mutants, oracles, relations and result digests -> provenance PASS.

## Implementation boundary

No production compatibility prover, mutant engine, oracle engine, metamorphic runner, or activation widening is claimed by this research artifact. Implementation must begin with executable RED fixtures for the matrix above, then GREEN the smallest coherent slice.

The proof engine must not be allowed to self-authorize by regenerating its own expected outputs. Any path that would widen consequential authority based only on same-pipeline equality must fail closed.

## Result

`COMPATIBILITY_PROOF_ORACLE_INDEPENDENCE_MUTANT_SOUNDNESS_METAMORPHIC_RELATIONS_V1_FROZEN`

This closes the design gap left by the prior fixture-synthesis contract: distinguishing fixtures are now required to be backed by independent oracles, semantically faithful mutants, explicit equivalent-mutant handling, metamorphic relations, and provenance-bound revalidation semantics.