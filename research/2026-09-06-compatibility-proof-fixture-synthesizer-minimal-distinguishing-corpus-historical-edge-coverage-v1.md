# COMPATIBILITY_PROOF_FIXTURE_SYNTHESIZER_MINIMAL_DISTINGUISHING_CORPUS_HISTORICAL_EDGE_COVERAGE_V1_FROZEN

Date: 2026-09-06
Status: design contract frozen; RED/GREEN implementation pending
Applies to: LAB-093 provider model registry / semantic-diff / compatibility-edge admission work

## Why this contract exists

The preceding semantic-diff contract makes compatibility directional and dimension-specific, but a compatibility edge can still pass vacuously if its tests never exercise the changed semantic branch. A fixture set that happens to produce equal outputs under both generations is not proof that a changed provider model has no consequential effect.

This contract therefore requires every admitted semantic delta to produce at least one **distinguishing witness obligation**. The compatibility attestation is valid only when the retained fixture corpus can demonstrate that the harness is capable of detecting the prohibited behavior for that delta class.

The target is not exhaustive input enumeration. The target is a deterministic, content-addressed witness corpus whose coverage is stated in terms of semantic predicates, impact-cone nodes and compatibility dimensions.

## Primary donors and verified facts

1. Smithy explicitly supports model diff rules, but its specification states that not every breaking change can be expressed through built-in `breakingChanges`; custom diff tooling can therefore be required. This supports treating fixture synthesis as a separate proof layer rather than trusting a model-diff label alone.
   - https://smithy.io/2.0/spec/model.html

2. Protobuf field presence changes observable API semantics even when the underlying wire format remains tag/value based. With implicit presence, a default-valued scalar can be indistinguishable from absence after parsing; explicit presence can preserve that distinction. A fixture corpus must therefore include absent/default/present witnesses, not only non-default values.
   - https://protobuf.dev/programming-guides/field_presence/

3. Protobuf documents wire-safe and wire-unsafe schema changes separately, and open enums can preserve previously unknown numeric values. Therefore wire compatibility is not a sufficient witness for application/replay/reconciliation compatibility; enum witnesses must include unknown/future numeric values and default-zero behavior.
   - https://protobuf.dev/programming-guides/proto3/
   - https://protobuf.dev/reference/cpp/cpp-generated/

4. The JSON Schema ecosystem's official test-suite/Bowtie approach demonstrates a useful donor mechanism: common semantic fixtures are run across independent implementations to detect behavioral disagreement. LAB uses the same general mechanism for generation A vs generation B and for old/new generated artifacts, but with stronger authority/effect-specific assertions.
   - https://json-schema.org/blog/posts/bowtie-intro

These are donor mechanisms, not authority for LAB's security semantics.

## Core proof object

For each candidate compatibility edge `A -> B`, build a content-addressed `CompatibilityFixtureProof` containing:

- source generation A digest;
- source generation B digest;
- normalized semantic-diff digest;
- compatibility dimension (`REQUEST_EFFECT`, `HISTORICAL_REPLAY`, `EVIDENCE`, `RECONCILIATION`, `DISCLOSURE`);
- impacted operation/message/error shape IDs;
- impact-cone artifact IDs and generations;
- typed semantic delta IDs;
- deterministic fixture-generator generation;
- selected fixture-set digest;
- per-fixture semantic predicate coverage;
- expected A and B observations;
- distinguishing-witness result;
- historical-corpus contribution digest;
- minimizer generation and proof trace;
- toolchain/compiler/runtime generations used for the observed execution.

An edge is inadmissible when any consequential delta lacks a satisfied witness obligation.

## Witness obligation

A semantic delta creates one or more obligations of the form:

`O = (delta_id, dimension, predicate, forbidden_observation_class)`

A fixture satisfies `O` only when all of the following hold:

1. the fixture reaches the semantic predicate affected by the delta;
2. the oracle can observe the dimension-specific consequence;
3. the negative mutation used to validate the harness changes that consequence;
4. removing or masking the delta causes the fixture to distinguish the prohibited implementation from the admitted implementation;
5. the result is deterministic under the pinned fixture/toolchain generations.

A fixture that executes but never reaches the changed branch is not coverage.

A fixture that produces equal A/B bytes when the relevant property is provider effect, error classification or presence semantics is not proof.

## Deterministic synthesis by typed delta

The synthesizer consumes typed semantic deltas, not free-form source diffs.

### Required field added
Generate at minimum:
- request without field;
- request with valid non-default field;
- historical serialized request/evidence lacking field;
- negative witness where B incorrectly accepts/constructs the absent form when the dimension requires rejection, or where replay invents an authority-relevant default.

### Optional/presence change
Generate the three-way boundary when the data model permits it:
- absent;
- explicitly present default (`0`, `false`, empty string, zero enum);
- present non-default.

The oracle must compare semantic presence separately from parsed scalar value.

### Default added/changed
Generate:
- field absent;
- field explicitly set to old default;
- field explicitly set to new default;
- a non-default control.

The fixture must distinguish parser default, serializer omission, SDK constructor default and provider-side default where these are separate layers.

### Enum widened / enum openness changed
Generate:
- each boundary-known value needed by impact-cone branches;
- zero/default value;
- at least one unknown numeric value outside A but admitted by B when the wire format can carry it;
- negative closed-enum witness.

The corpus may not contain only currently named values.

### Union/oneof variant added or openness changed
Generate:
- old known variant;
- new variant;
- unknown/extension variant when representation allows it;
- empty/no-variant state where legal;
- conflicting/multi-variant invalid state where parser semantics matter.

### Numeric/string constraint change
Generate boundary values, not a random interior sample:
- old min/max;
- new min/max;
- immediately inside/outside each changed boundary;
- zero/empty when semantically special.

### Wire name/location change
Generate exact request observations at the final serialized/request-extractor boundary:
- old and new header/query/path/body placement;
- duplicate old+new form;
- absence control;
- signing/canonicalization witness if the field is in auth scope.

### Idempotency/retry trait change
Generate at least:
- first attempt;
- repeated same semantic request with same idempotency identity;
- repeated request with changed identity;
- ambiguous timeout/UNKNOWN response path;
- negative hidden-retry witness.

The oracle observes effect multiplicity and authority state, not merely returned values.

### Auth/signing scope change
Generate requests differing only in the changed authority-relevant field and require the signing/final-request commitment to distinguish them. A fixture whose signature input is unchanged despite a newly signed field is a failing witness.

### Error model/classification change
Generate provider responses for:
- old known error;
- new error;
- unknown/unmodelled error;
- retryable/non-retryable boundary;
- terminal/UNKNOWN reconciliation boundary.

The oracle records classification, retry authority and reconciliation state.

### Sensitive/disclosure change
Generate a value carrying a canary secret and require that allowed evidence commitments remain stable while forbidden logs/traces/disclosures do not contain the cleartext canary. A test that omits the sensitive field is not coverage for a sensitivity delta.

### Transitive imported model change
Fixture provenance must name the transitive dependency node that introduced the obligation. Top-level source equality does not remove the obligation.

## Positive and negative witnesses

Every obligation gets two classes of fixture result:

- **positive witness**: legitimate A/B behavior that should remain admitted for the requested compatibility direction;
- **negative distinguisher**: a controlled semantic mutant representing the prohibited interpretation.

The negative distinguisher is essential. Without it, a test may pass because the assertion is too weak or the fixture never reaches the changed behavior.

Examples of controlled mutants:

- collapse absent and explicitly-default presence;
- use the wrong default;
- silently map unknown enum to zero;
- ignore a newly signed field;
- classify a new provider error as retryable;
- omit an impacted serializer from regeneration;
- drop a transitive dependency edge;
- accept unknown metadata into evidence;
- replay historical evidence using the current schema generation instead of its original generation.

A compatibility proof fails when its own retained fixture set cannot kill the relevant mutant.

## Minimal distinguishing corpus

Fixture minimization is permitted only after obligation generation and mutation validation.

Let each fixture cover a set of obligations. The minimizer may choose a deterministic set-cover approximation to reduce execution cost, but it must preserve:

- at least one killing witness for every consequential obligation;
- at least one positive control for every compatibility dimension touched by the edge;
- every fixture explicitly pinned by historical rarity policy;
- every boundary fixture whose removal would collapse two semantic states (for example absent vs explicit default);
- every fixture required to cover a distinct impact-cone artifact path.

The minimizer outputs a `minimization_trace` listing every removed fixture and the retained fixture(s) that subsume each obligation.

If the sole distinguisher for any obligation would be removed, minimization fails closed.

Do not minimize by source-diff hunk count or line coverage.

## Correlated changes and interaction witnesses

Independent per-delta fixtures are insufficient when deltas interact. The synthesizer must generate pairwise or targeted interaction fixtures when either:

- two deltas touch the same operation/message/error path;
- one delta changes reachability of another;
- one changes a default/presence state consumed by another policy branch;
- auth/signing and serialization deltas overlap;
- retry/idempotency and error-classification deltas overlap;
- an impact-cone node depends on multiple changed source nodes.

Full combinatorial explosion is not required. The interaction generator must document why selected combinations cover all shared semantic predicates.

## Historical corpus retention

Synthetic fixtures alone cannot represent all provider reality. Maintain an authenticated historical corpus of minimized, privacy-safe observations selected by semantic rarity.

Retention classes:

- enum values, especially unknown/future values;
- rare modeled and unmodelled error variants;
- absent-vs-default presence states;
- minimum/maximum and unusual numeric boundaries;
- legacy serialized payload/evidence generations;
- historical auth/signing variants;
- UNKNOWN/manual-resolution reconciliation cases;
- provider responses that previously caused parser/classifier divergence.

Raw secret-bearing payloads are not required. Historical fixtures must use the earlier privacy/evidence-minimization contract: retain closed projections, keyed commitments or encrypted replay capsules only when necessary.

A frequency-biased sampler that discards rare states because common happy-path traffic dominates is non-conformant.

## Historical edge coverage

Each retained compatibility edge remains bound to the fixture-set generation that admitted it.

When the generator/minimizer/oracle changes:

1. historical edges are not silently reinterpreted;
2. a new proof generation is created;
3. old fixtures remain reproducible or archived with authenticated provenance;
4. if the new generator discovers a previously uncovered obligation, the affected historical edge becomes `REVALIDATION_REQUIRED` rather than grandfathered;
5. consequential use that depends on that edge fails closed until revalidation succeeds.

Rollback to an older fixture engine cannot erase obligations discovered at a newer authenticated registry frontier.

## Reachability proof

The harness must record that the fixture reached the intended semantic branch. Acceptable evidence can include generated-artifact decision IDs, parser/extractor branch IDs, explicit semantic-state observations, or a deterministic trace projection.

Generic code coverage is insufficient because executing a line does not prove the relevant semantic state was exercised.

If an obligation's target branch is unreachable under all valid fixtures, this is not a PASS. It is either:

- evidence that the modeled delta is dead/unreachable and requires a separate no-impact proof; or
- evidence of a generator/model mismatch.

Both states fail closed until resolved.

## Oracle discipline

Oracles are dimension-specific.

`REQUEST_EFFECT` compares final semantic provider request/effect identities and multiplicity.

`HISTORICAL_REPLAY` compares replayability, original-generation interpretation and authority state transitions.

`EVIDENCE` compares closed evidence projection, commitments and provenance without requiring plaintext equality.

`RECONCILIATION` compares success/failure/UNKNOWN/manual-resolution classification and retry authority.

`DISCLOSURE` compares permitted/forbidden fields and selective-disclosure proof results.

A single `serialized_bytes_equal` oracle cannot stand in for all dimensions.

## Generator/toolchain drift

Fixture bytes and expected observations depend on tooling. Every proof binds:

- semantic-diff engine generation;
- normalizer generation;
- schema registry generation;
- fixture synthesizer generation;
- minimizer generation;
- generated DTO/serializer/extractor generations;
- relevant SDK/compiler/runtime versions.

Toolchain drift creates a new candidate proof. It never mutates an already authenticated historical proof in place.

## Admission algorithm

For candidate edge A -> B:

1. load exact authenticated A/B semantic graphs;
2. compute typed semantic deltas;
3. compute dimension-specific impact cone;
4. generate witness obligations;
5. synthesize deterministic positive and negative fixtures;
6. add selected authenticated historical rare-state fixtures;
7. run the negative mutants and require every obligation to be killable;
8. run A/B generated artifacts and collect dimension-specific observations;
9. minimize only after full obligation coverage is demonstrated;
10. rerun the minimized set and require identical obligation coverage;
11. bind proof to authenticated registry frontier and artifact generations;
12. admit only the specific proven compatibility directions/dimensions.

No step may infer reverse compatibility.

## RED-first matrix (80 cases)

### A. Vacuous fixtures / reachability (1-10)
1. fixture omits the changed optional field;
2. fixture always supplies a required field so missing-field branch is untested;
3. absent/default states collapse in oracle;
4. enum corpus contains only value zero;
5. error fixture never reaches new error classifier;
6. auth fixture does not vary newly signed field;
7. retry fixture performs only one attempt;
8. historical replay fixture is regenerated under B instead of retained from A;
9. branch reports code coverage but not semantic-state reachability;
10. target semantic branch is unreachable and is incorrectly marked covered.

### B. Presence/default semantics (11-20)
11. absent vs explicit zero;
12. absent vs explicit false;
13. absent vs empty string;
14. implicit -> explicit presence;
15. explicit -> implicit presence;
16. old parser default retained incorrectly;
17. new SDK constructor default masks provider default;
18. serializer omits explicit default when presence is authority-relevant;
19. replay invents a newly introduced default;
20. minimizer removes the only absent-state fixture.

### C. Enum/union/open-world behavior (21-30)
21. unknown numeric enum preserved vs mapped to zero;
22. new enum value reaches old switch default;
23. closed -> open enum;
24. open -> closed enum;
25. first/zero enum meaning changes;
26. alias changes interpretation;
27. new union variant;
28. empty union state changes validity;
29. unknown union extension is silently dropped;
30. minimizer keeps only currently named variants.

### D. Wire/effect/auth/retry (31-40)
31. header renamed;
32. query -> body relocation;
33. duplicate old+new field accepted differently;
34. path encoding/canonicalization change;
35. signing scope expands;
36. signing scope shrinks;
37. idempotency token location changes;
38. retryability trait changes;
39. timeout-after-send changes UNKNOWN classification;
40. hidden SDK retry creates duplicate effect.

### E. Errors/reconciliation (41-50)
41. new modeled error classified retryable;
42. old retryable error becomes terminal;
43. unknown error coerced to success;
44. error payload field default changes classifier;
45. reconciliation key renamed;
46. provider response omits newly required receipt field;
47. manual-resolution state loses distinguisher;
48. historical rare error absent from sampled corpus;
49. parser accepts malformed error only under B;
50. minimizer drops sole UNKNOWN classifier witness.

### F. Impact cone / regeneration (51-60)
51. request DTO regenerated but serializer stale;
52. serializer regenerated but final-request extractor stale;
53. response DTO regenerated but reconciliation parser stale;
54. error DTO omitted from cone;
55. disclosure policy omitted from cone;
56. retry classifier omitted from cone;
57. transitive imported node changes but top-level operation is unchanged;
58. no-impact rule asserted without fixture killing its inverse mutant;
59. generated artifact digest differs from attested cone;
60. partial regeneration passes generic smoke tests.

### G. Correlated mutations / minimization (61-70)
61. two individually safe deltas interact unsafely;
62. default change activates newly added enum branch;
63. serialization change plus signing change cancels naive byte diff;
64. error change plus retry change causes duplicate attempt;
65. correlated mutants make A/B happy-path outputs equal;
66. deterministic set-cover tie breaks nondeterministically;
67. minimizer removes sole boundary witness;
68. minimizer removes historical rarity-pinned fixture;
69. minimized rerun has lower obligation coverage than full set;
70. interaction fixture provenance omits one contributing delta.

### H. Historical/toolchain/frontier integrity (71-80)
71. old edge silently re-evaluated with new generator;
72. newer generator discovers obligation but old edge stays admitted;
73. rollback uses old fixture engine to erase new obligation;
74. historical corpus item loses source-generation provenance;
75. compiler/SDK drift changes fixture bytes without new proof generation;
76. fixture oracle generation changes in place;
77. archived fixture digest mismatches manifest;
78. restored old registry frontier omits a later discovered distinguisher;
79. privacy minimization removes authority-critical semantic predicate;
80. compatibility attestation is accepted with zero negative mutants killed.

## Frozen decisions

1. Compatibility requires **distinguishing power**, not just equal outputs on a convenient corpus.
2. Every consequential semantic delta creates explicit witness obligations.
3. Each obligation must have a retained negative mutant that the fixture set can kill.
4. Fixtures are generated from typed semantic deltas and impact-cone predicates, not source lines.
5. Presence/default/enum/error/retry/auth boundaries receive targeted fixtures even when wire compatibility is nominally preserved.
6. Minimization happens only after full obligation coverage and mutation validation, and produces an auditable trace.
7. Rare historical semantic states are authenticated, privacy-minimized and protected from frequency-biased eviction.
8. Historical edges remain bound to their original fixture proof; newer discovered obligations force revalidation rather than silent reinterpretation.
9. Generic code coverage and serialized-byte equality are insufficient proof for consequential compatibility.
10. Production implementation and compatibility PASS wait for executable RED/GREEN against this matrix.

## Relationship to prior frozen contracts

This contract composes with, and does not replace:

- provider evidence-schema registry / generated closed DTO / SDK drift admission;
- provider model normalization / transitive-reference closure / registry frontier admission;
- provider model semantic-diff / directional compatibility-edge / codegen impact-cone admission;
- evidence minimization / field-taint / selective-disclosure policy compiler;
- replay, UNKNOWN/manual-resolution, transport-observer and evidence-retention contracts.

A fixture proof may demonstrate compatibility only inside authority already granted by those contracts.

## Next implementation slice when exact execution is available

Implement RED tests first for the witness-obligation engine using a tiny synthetic provider schema with: optional/default scalar, open enum, modeled retryable error, signed header and idempotency field. Introduce controlled mutants for presence collapse, unknown-enum-to-zero, stale signing projection, stale retry classifier and omitted impact-cone serializer. Require the generated corpus to kill all five mutants, then implement deterministic minimization and prove the minimized corpus preserves the same obligation set.

No production compatibility admission should consume this contract until those RED tests execute and turn GREEN on the supported repository stack.
