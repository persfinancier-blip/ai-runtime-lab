# Conformance-corpus oracle independence, expected-verdict provenance, and specification-ambiguity adjudication v1

Status: `CONFORMANCE_CORPUS_ORACLE_INDEPENDENCE_EXPECTED_VERDICT_PROVENANCE_SPEC_AMBIGUITY_V1_FROZEN`

Date: 2026-09-07

Related: LAB-093 / #178; composes with `VERIFIER_CONFORMANCE_CORPUS_PARSER_DIFFERENTIAL_SCOPED_EQUIVALENCE_V1_FROZEN`.

## Problem

A differential/conformance corpus is not trustworthy merely because verifier N and verifier N+1 agree with an `expected` field. The expected field itself can be circularly derived from N, copied from a mutable implementation, silently changed after standards errata, or produced by the same parser/canonicalizer whose behavior it is meant to judge.

The missing contract is an independently attributable truth/provenance layer for expected outcomes.

## Frozen conclusions

### 1. Expected verdict is a signed adjudication, not an unversioned literal

Every authority-relevant test case MUST bind its expected outcome to an immutable `OracleAdjudicationV1` containing at least:

- `case_id` and exact input/fixture digest;
- `semantic_profile_id` + immutable profile digest;
- normative-source set and exact source revisions/snapshots;
- cited normative clauses/assertions;
- expected parse result, normalized-object digest/canonical bytes where deterministic, crypto/trust result, final verdict, and expected error class where applicable;
- adjudication method and reviewers/authority policy generation;
- ambiguity/errata state at adjudication time;
- supersedes/superseded-by linkage without mutating prior generations;
- signature/threshold evidence and timestamp/checkpoint evidence where used by the broader archival contract.

`expected=true` in a test file is convenience data only unless it is bound to this provenance.

### 2. Historical acceptance is not normative validity

The system MUST distinguish:

- `HISTORICALLY_ACCEPTED_BY(verifier_generation=N)` — observed behavior of a historical implementation;
- `NORMATIVELY_VALID_UNDER(profile=P, oracle_generation=G)` — adjudicated result derived from the frozen normative source set;
- `CURRENT_POLICY_ACCEPTED` — current operational policy, which may intentionally differ from historical or normative results.

No one of these may be substituted for another.

This matters when a historical verifier accepted an input later shown to violate the specification, or when a current policy intentionally rejects behavior that an older profile allowed.

### 3. Normative sources are versioned inputs to the oracle

A living or corrigible standard cannot be referenced only by a mutable URL. `NormativeSourceInventoryV1` MUST pin exact immutable snapshots/revisions and classify each source as normative, informative, erratum/corrigendum, test assertion, or implementation evidence.

RFC Editor behavior is a useful donor: published RFC source artifacts remain fixed; errors are tracked through a separate errata system rather than silently rewriting the published TXT/PDF/XML. Verified, Rejected, Reported, and Held-for-Document-Update are distinct states. This supports additive adjudication rather than historical mutation.

Likewise, WHATWG explicitly publishes frozen snapshots for historical references even though its standards are living documents. Historical verifier profiles therefore bind to the snapshot they actually implemented, not automatically to today's text.

### 4. Errata/corrigenda create a new oracle generation; they do not rewrite signed history

For an existing signed corpus generation G:

- a newly verified technical erratum may produce G+1;
- G remains immutable and historically replayable;
- migration evidence records which cases changed, why, which normative source/erratum caused the change, and whether the change is backward-compatible, security-tightening, or semantic-breaking;
- historical replay against G continues to mean "under the adjudication available at G";
- current conformance may require G+1.

A later erratum MUST NOT silently edit old expected verdicts in place.

### 5. Reported/unverified ambiguity is fail-closed for high-assurance equivalence

If the relevant standards text admits multiple defensible interpretations and no independently authorized adjudication exists, the case is not eligible to prove scoped semantic equivalence. Result: `UNKNOWN_ORACLE` / `UNKNOWN_SPEC_AMBIGUITY`.

Majority vote among implementations is not a normative oracle. Implementation convergence is evidence useful for standards adjudication, but cannot by itself transform ambiguity into normative truth.

### 6. Oracle independence is structural, not merely organizational

At least one authority path producing the expected verdict MUST be independent of the verifier implementation under test. Prohibited sole-oracle constructions include:

- verifier N generates the expected result and N+1 is tested against it;
- a reference parser sharing the exact production parser/core library generates parser/canonicalization expectations;
- the corpus generator computes expected canonical bytes by calling the same canonicalizer under test;
- expected crypto outputs are generated only through the production crypto wrapper under test;
- an LLM/human reviewer writes expected outputs without clause-level normative traceability and authenticated review provenance.

Independence can come from normative derivation, externally maintained official vectors, separately implemented generators, or threshold human/technical adjudication, depending on the domain.

### 7. Official vectors are strong donors but still scoped

NIST CAVP/ACVTS is a useful positive model: the validation system generates cases from declared capabilities and validates implementation outputs externally; public vectors can informally verify correctness, while formal validation is a distinct process. This cleanly separates implementation execution from the authority deciding expected results.

But a NIST crypto vector proves only the algorithm semantics it covers. It cannot prove local resource/fence/provider/policy binding. Those local semantics require local normative assertions and independent adjudication.

### 8. Test assertions must trace to normative requirements

W3C testing guidance is a useful donor: test cases should identify the relevant specification section/conformance requirement, and expected results describe what a conformant implementation should produce. W3C guidance also treats mapping tests to specification requirements as a traceability requirement.

Therefore every corpus case that participates in equivalence closure MUST have `NormativeAssertionBindingV1` mapping the case to exact source clauses/assertions. Unmapped cases may remain regression tests but cannot independently justify normative equivalence.

## Proposed data contracts

### `NormativeSourceInventoryV1`

Fields:
- `profile_id`, `profile_digest`;
- exact source artifact digests/immutable URLs or repository commits;
- status: normative/informative/erratum/corrigendum/test-assertion;
- publication/effective dates;
- supersession graph;
- retrieved artifact digest and archival location.

### `NormativeAssertionBindingV1`

Fields:
- assertion id;
- source id + exact section/anchor;
- requirement level (`MUST`, `MUST_NOT`, profile-defined equivalent);
- preconditions/applicability;
- machine-testable semantic proposition;
- cases covering the assertion.

### `OracleAdjudicationV1`

Fields:
- immutable case/input digest;
- semantic profile + source inventory digest;
- expected intermediate/final semantics;
- derivation method;
- independent evidence references;
- reviewer/threshold policy generation;
- ambiguity status;
- signature/attestation;
- prior/new adjudication generation links.

### `OracleIndependenceProofV1`

Must show that expected-result derivation does not transitively depend solely on the implementation under test. It records implementation/library/build provenance of the oracle path and the verifier path and declares shared components. Shared low-level primitives may be allowed only when their semantics are separately validated and cannot determine the disputed result by themselves.

### `OracleGenerationMigrationProofV1`

For G -> G+1:
- old/new source inventories;
- errata/corrigenda/policy changes;
- exact changed case set;
- old/new expected semantics;
- classification of each semantic delta;
- independent review evidence;
- replay of unchanged cases;
- explicit statement that G remains immutable.

## Adjudication policy

Preferred authority order for a disputed expected verdict:

1. unambiguous normative text in the exact frozen profile;
2. verified erratum/corrigendum applicable to that profile according to explicit policy;
3. official normative test assertions/vectors whose scope exactly covers the claim;
4. threshold adjudication by independent reviewers grounded in exact normative clauses;
5. independent implementation evidence as diagnostic support only.

If 1-4 cannot justify one outcome, return `UNKNOWN_SPEC_AMBIGUITY`; do not use implementation majority as the deciding oracle.

## Historical/current semantics

A verifier replay report MUST carry both `oracle_generation` and `semantic_profile_id`. This prevents a future verifier from appearing to regress merely because the test suite silently changed underneath it.

Recommended report tuple:

`(case_id, verifier_generation, semantic_profile, oracle_generation, actual_semantics, expected_semantics, verdict)`.

When current standards semantics intentionally differ from historical semantics, run both profiles separately. Do not collapse them into one mutable expected result.

## Fraud / contradiction proofs

The implementation must eventually support durable contradiction evidence for at least:

1. `SELF_ORACLE_PROVEN` — expected result derived solely from the verifier under test or equivalent shared implementation path.
2. `UNPINNED_NORMATIVE_SOURCE_PROVEN` — adjudication cites only mutable current source where a frozen revision is required.
3. `HISTORICAL_TRUTH_REWRITE_PROVEN` — signed corpus generation changed in place after errata/policy evolution.
4. `ORACLE_PROFILE_MISMATCH_PROVEN` — expected result from profile P applied to verifier replay claiming profile Q.
5. `UNAUTHORIZED_ERRATUM_PROMOTION_PROVEN` — Reported/Rejected/Held material treated as if Verified/applicable without policy authorization.
6. `MAJORITY_AS_ORACLE_PROVEN` — implementation vote used as sole normative adjudicator.
7. `ASSERTION_TRACE_GAP_PROVEN` — equivalence-closing case lacks required normative assertion binding.
8. `ORACLE_DEPENDENCY_CONCEALMENT_PROVEN` — oracle provenance omits a shared parser/canonicalizer/crypto component material to the expected result.

## RED-first matrix (80 cases)

Freeze 80 cases before production integration, grouped 10 each:

A. source pinning/versioning — mutable URL, wrong commit, missing digest, superseded source, mixed snapshot, missing archival artifact, profile/source mismatch, duplicate source identity, altered retrieval bytes, current-source substitution;

B. errata lifecycle — Reported, Verified, Rejected, Held, technical vs editorial, erratum effective-policy mismatch, late erratum, conflicting errata, withdrawn/superseded correction, silent in-place corpus rewrite;

C. self-oracle/circularity — N self-generates expected, N+1 from N outputs, shared parser, shared canonicalizer, shared crypto wrapper, shared schema decoder, hidden generated fixture, copied golden output, reference binary built from same source, shared mutable config;

D. normative assertion traceability — exact MUST, MUST NOT, precondition, optional feature, multiple clauses, conflicting clauses, missing mapping, stale anchor, informative text incorrectly normative, test assertion narrower than claim;

E. intermediate semantics — same final boolean/different parse tree, different canonical bytes, different error class, trust result difference, crypto difference, profile applicability difference, resource-limit difference, unknown vs invalid collapse, normalization drift, silent field dropping;

F. official/external vectors — correct scoped vector, wrong algorithm revision, retired algorithm, vector/profile mismatch, missing capability declaration, official vector plus local binding mutation, external expected output tamper, stale vector pack, partial vector family, vector pass falsely promoted to system-wide equivalence;

G. independent adjudication — two-review threshold, reviewer conflict, insufficient quorum, reviewer shares implementation dependency, clause citation missing, ambiguity declared, ambiguity improperly forced, implementation evidence used diagnostically, majority vote rejected, authenticated decision supersession;

H. historical/current replay — G replay unchanged, G+1 erratum change, old verifier under old profile, old verifier under current profile, current verifier under old profile, policy tightening, backward-compatible correction, semantic-breaking correction, immutable old signed truth set, migration delta manifest complete.

## Donors / evidence

- RFC Editor: published RFC artifacts are not silently rewritten; errata are separate and have explicit lifecycle/status. `https://www.rfc-editor.org/series/rfc/`, `https://www.rfc-editor.org/series/rfc-errata/`, `https://www.rfc-editor.org/series/errata/how-to-verify/`.
- NIST CAVP/ACVTS: external validation system generates/validates cases; public vectors are useful but explicitly do not replace formal validation. `https://csrc.nist.gov/projects/cryptographic-algorithm-validation-program`.
- W3C Test Metadata / testing guidance: expected results and spec-reference metadata; test cases should map to exact conformance requirements. `https://www.w3.org/TR/test-metadata/`, `https://www.w3.org/TR/test-methodology/`.
- WHATWG: living standards publish frozen snapshots for historical reference. `https://whatwg.org/faq`.

## Decision

`ORACLE_INDEPENDENCE_CLOSED` requires all equivalence-closing corpus cases to have immutable source/profile identity, authenticated expected-verdict provenance, normative assertion traceability, and a materially independent oracle path. Standards ambiguity without independently justified adjudication is `UNKNOWN_SPEC_AMBIGUITY`. Errata or policy evolution creates a new oracle generation; historical signed truth sets are never silently rewritten.

This contract is design-frozen only. Exact executable RED/GREEN remains pending behind the current source-execution blocker and LAB-086 priority gate.
