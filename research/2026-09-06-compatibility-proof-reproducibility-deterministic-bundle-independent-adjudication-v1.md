# Compatibility proof reproducibility / deterministic proof-bundle / independent adjudication V1

Date: 2026-09-06
Status: FROZEN DESIGN CONTRACT; production RED/GREEN pending
Parent: LAB-093 / #178

## Objective

Make a consequential provider-model compatibility verdict reproducible by a second verifier without rerunning candidate codegen or trusting the first verifier's private state. A proof that cannot be independently replayed from a closed, authenticated bundle is not admission evidence.

This extends the frozen semantic-diff, impact-cone, fixture-synthesis and oracle-independence contracts. It does not claim a production prover implementation or behavioral PASS.

## Donor mechanisms

Primary donor mechanisms are used narrowly:

- SLSA Provenance models a result together with builder identity, external parameters and resolved dependencies, and recommends rejecting unexpected external parameters. This supports explicit capture of verifier/toolchain/environment inputs rather than a bare boolean verdict: https://slsa.dev/spec/v1.0/provenance
- SLSA notes that verified reproducibility only adds assurance when rebuilders are genuinely independent; two verifiers using the same vulnerable pipeline are common-mode, not independent evidence: https://slsa.dev/spec/draft/faq
- Sigstore bundles package signatures plus verification material, timestamps and transparency-log evidence so verification can be performed later/offline without silently depending on mutable online state: https://docs.sigstore.dev/about/bundle/
- TUF detects rollback by comparing authenticated metadata versions against already-trusted state and uses snapshot metadata to prevent mixed views. LAB borrows the monotonic-frontier property, not TUF's update semantics: https://theupdateframework.github.io/specification/latest/ and https://theupdateframework.io/docs/metadata/

## Threat model

The contract must fail closed against:

1. fixture/mutant generation whose random seed or traversal order was not captured;
2. a verifier that recomputes disputed semantics with the same generator/canonicalizer as the candidate;
3. a proof bundle whose omitted file is silently fetched from current registry state;
4. toolchain/package substitution under the same logical version string;
5. nondeterministic provider observations being replayed as deterministic facts;
6. a second verifier disagreeing with the first and the system selecting the favorable result;
7. stale but internally valid proof bundles being replayed after registry/frontier advancement;
8. proof self-signing where the same mutable pipeline both manufactures disputed evidence and attests that it is valid;
9. partial bundles that preserve verdict JSON but omit obligations, killed mutants, negative witnesses, oracle provenance or historical fixtures;
10. environment-dependent behavior hidden behind locale, timezone, hash randomization, filesystem ordering, CPU/architecture, parser/runtime or dependency drift.

## Frozen terms

### Proof bundle

A closed immutable directory/object whose canonical manifest commits to every byte required to reproduce the compatibility judgment.

### Producer verifier

The verifier instance that first emits the proof bundle and proposed verdict.

### Adjudicator verifier

A separately admitted verifier that consumes only the bundle plus authenticated trust/frontier state and recomputes obligations and verdict. It MUST NOT invoke candidate codegen or fetch undeclared dependencies.

### Independent

Independence is semantic, not merely process/container separation. Producer and adjudicator may share neutral primitives such as SHA-256 or a standards-compliant JSON parser, but cannot share the disputed semantic implementation, generator, oracle package or generated intermediate artifacts as sole authority.

### Reproducible

Given the same admitted bundle and trust/frontier state, the verifier emits the same normalized obligation set, fixture/mutant identities, oracle classifications, per-obligation results and final verdict digest.

## Canonical bundle manifest V1

The canonical manifest MUST contain, at minimum:

- `bundle_version`
- `bundle_id = H(canonical_manifest_without_bundle_id)`
- source and target provider-model generation IDs plus raw and normalized closure digests;
- semantic-diff generation + digest;
- impact-cone generation + digest;
- evidence-policy/schema-registry generations;
- fixture synthesizer generation;
- mutant engine generation;
- oracle engine generation;
- verifier implementation digest;
- adjudicator compatibility profile;
- deterministic seed domain and exact seed bytes for every generated family;
- deterministic enumeration/sort rules;
- complete obligation catalog;
- complete fixture catalog with input bytes/digests and expected relation class;
- complete mutant catalog, provenance, targeted semantic dimension and equivalence status;
- complete oracle catalog and independence classification;
- historical fixture/frontier dependencies;
- provider-observed evidence objects, timestamps and authenticated provenance where applicable;
- exact dependency/toolchain digests, not only package version labels;
- execution environment declaration for every dimension known to influence semantics;
- per-obligation result records;
- producer proposed verdict;
- authenticated registry/global frontier observed at production time;
- manifest hash algorithm/domain separation identifiers.

Unknown top-level fields are rejected for consequential admission until the bundle schema generation explicitly admits them.

## Deterministic generation rules

1. Randomness is forbidden unless every generator call derives from a recorded domain-separated seed: `H(root_seed || generator_generation || obligation_id || purpose || ordinal)`.
2. PRNG algorithm and version are part of the generation identity.
3. Collection traversal, filesystem discovery, map/set iteration and concurrency completion order MUST NOT influence fixture/mutant identity. Inputs are canonical-sorted before generation.
4. Time, locale, timezone, hostname, process ID, temporary path, wall-clock randomness and ambient environment are forbidden semantic inputs unless explicitly declared in the bundle and independently justified.
5. A generated object's stable ID derives from canonical content plus generation/domain identity, never from production order alone.
6. Re-running bundle construction from already-closed source artifacts MUST produce byte-identical canonical catalogs and verdict material, or admission is `NON_REPRODUCIBLE`.

## Closed-world replay

The adjudicator operates with network/provider access disabled by default.

- Every file/dependency used for deterministic replay must already be present and digest-addressed in the bundle or in an authenticated immutable registry object explicitly named by digest.
- A URL, package name, branch, tag, version range or provider API date is not a dependency identity.
- Missing bytes are `BUNDLE_INCOMPLETE`; never fetch latest/current state as repair.
- Provider-observed relations are replayed from authenticated observation evidence and independently checked invariants; the adjudicator must not silently repeat a consequential provider request to make a failing proof pass.

## Toolchain trust and substitution

Logical version equality is insufficient. Toolchain identity commits to executable/package/module bytes and relevant configuration.

Classifications:

- `EXACT_TOOLCHAIN`: exact admitted implementation digest;
- `INDEPENDENT_COMPATIBLE_TOOLCHAIN`: different implementation with separately admitted semantics and compatibility profile;
- `SAME_LINEAGE_DIFFERENT_BUILD`: same disputed semantic lineage rebuilt elsewhere; not independent by itself;
- `UNDECLARED_SUBSTITUTION`: fail closed;
- `DOWNGRADE`: fail closed unless an authenticated compatibility edge explicitly admits old verifier consumption of the new bundle generation.

A verifier package signature proves artifact identity/authorship, not correctness or independence of its semantic oracle.

## Independent adjudication protocol

1. Authenticate bundle identity and registry/global frontier.
2. Reject rollback/stale bundle if its frontier is older than the minimum trusted frontier for the compatibility edge.
3. Validate bundle schema and completeness before any semantic evaluation.
4. Recompute all content digests and stable IDs.
5. Recompute obligation coverage from the frozen semantic diff and impact cone without trusting the producer's obligation list as complete.
6. Re-run deterministic fixture/mutant/oracle evaluation from bundle inputs.
7. Recompute mutant reachability/equivalence discharge status.
8. Recompute metamorphic relations and historical fixture obligations.
9. Emit an adjudicator result digest independent of producer verdict bytes.
10. Compare normalized producer/adjudicator obligation sets and verdicts.

Only exact semantic agreement may yield `ADJUDICATED_PASS`.

## Disagreement handling

Any material disagreement is fail-closed and produces `ADJUDICATION_DISAGREEMENT`.

The system MUST NOT:

- majority-vote two disagreeing semantic engines;
- choose the more permissive verdict;
- rerun with new seeds until agreement appears;
- drop the obligation on which disagreement occurred;
- treat a producer signature as override authority.

Resolution requires identifying the divergent obligation/input/toolchain and producing a new, higher-frontier proof bundle or an explicit human/product/security decision where the semantic ambiguity is genuinely policy-dependent.

## Attestation separation

Bundle authentication and semantic adjudication are separate layers.

- The producer may sign/attest the immutable bundle identity.
- The adjudicator separately attests its result over `(bundle_id, trusted_frontier, adjudicator_generation, normalized_result_digest)`.
- A producer's self-signature cannot convert `SAME_PIPELINE` evidence into independent adjudication.
- Where transparency/timestamp evidence is used, it proves existence/integrity/time of the signed object, not truth of the compatibility claim.

## Nondeterministic/provider-observed relations

Each such relation must declare:

- observation request/effect commitment;
- provider capability/model generation;
- observation time/window;
- authenticated response/evidence commitment;
- invariant actually being tested;
- retry/duplicate policy;
- why the invariant is stable enough for compatibility admission.

The bundle stores the evidence and verifier relation, not a claim that the provider will return byte-identical output later. If the invariant cannot be independently evaluated from durable evidence, the obligation is `INCONCLUSIVE`.

## Staleness and frontier rules

A proof bundle is bound to the authenticated registry frontier at which source/target models, schemas, policies, oracle generations and historical obligations were known.

- New obligations, invalid-mutant findings, oracle defects or model-registry corrections advance the frontier and mark affected old proof edges `REVALIDATION_REQUIRED`.
- Restoring an older database/bundle/archive does not lower the trusted minimum frontier.
- A previously valid proof may remain archival evidence while losing admission authority.
- Partial re-adjudication cannot silently reuse a stale PASS for newly affected obligations.

## Minimal verifier outputs

The canonical adjudication result contains:

- bundle ID;
- trusted frontier;
- verifier/adjudicator generation IDs;
- normalized obligation-set digest;
- fixture/mutant/oracle result digests;
- disagreement list if any;
- final state: `ADJUDICATED_PASS`, `ADJUDICATION_FAIL`, `ADJUDICATION_DISAGREEMENT`, `BUNDLE_INCOMPLETE`, `NON_REPRODUCIBLE`, `REVALIDATION_REQUIRED`, or `INCONCLUSIVE`;
- result digest and independent attestation metadata.

No boolean-only `compatible=true` artifact is accepted.

## RED-first matrix

Freeze at least these 80 cases before production implementation.

### Bundle closure / canonicalization (1-12)
1. omitted semantic-diff artifact;
2. omitted impact cone;
3. omitted negative fixture;
4. omitted killed mutant record;
5. omitted historical fixture;
6. unknown top-level field;
7. duplicate logical entry under alternate path;
8. manifest field-order perturbation;
9. Unicode normalization ambiguity;
10. canonical-content collision attempt;
11. dependency named only by version/tag;
12. undeclared external fetch required for replay.

### Seed / generation determinism (13-24)
13. missing root seed;
14. same seed but different PRNG version;
15. map iteration changes generation order;
16. filesystem-order drift;
17. concurrency completion-order drift;
18. wall-clock used in fixture generation;
19. locale-dependent normalization;
20. timezone-dependent result;
21. Python/hash-randomization dependence;
22. temp-path embedded in stable ID;
23. rerun produces semantically same but byte-different catalogs;
24. non-domain-separated seed reused across obligations.

### Toolchain identity / independence (25-38)
25. package version same, bytes differ;
26. oracle package silently substituted;
27. verifier downgraded;
28. generator downgraded;
29. same disputed semantic library linked by both verifiers;
30. two containers using identical flawed oracle counted as independent;
31. neutral hash library shared only;
32. independent compatible parser yields same result;
33. signed verifier binary with undeclared config drift;
34. transitive dependency drift;
35. compiler/runtime drift changes behavior;
36. architecture-dependent numeric behavior;
37. feature flag omitted from provenance;
38. environment variable influences semantic classifier.

### Adjudication / disagreement (39-52)
39. producer PASS / adjudicator FAIL;
40. producer FAIL / adjudicator PASS;
41. obligation-set mismatch;
42. mutant equivalence disagreement;
43. mutant reachability disagreement;
44. oracle independence disagreement;
45. metamorphic relation disagreement;
46. historical fixture missing only at adjudicator;
47. producer verdict bytes tampered but catalogs intact;
48. adjudicator result replayed against another bundle;
49. majority-vote attempt after disagreement;
50. rerun-new-seed attempt to erase disagreement;
51. dropped disputed obligation;
52. producer signature presented as semantic override.

### Provider-observed / nondeterministic evidence (53-62)
53. provider evidence missing authentication;
54. observation timestamp absent;
55. capability generation mismatch;
56. repeated one-shot consequential observation attempted automatically;
57. byte-level equality incorrectly required for nondeterministic output;
58. invariant independently holds over recorded evidence;
59. invariant cannot be evaluated from evidence;
60. retry policy omitted;
61. response commitment mismatch;
62. stale provider observation reused after capability/model frontier change.

### Frontier / stale replay / archive (63-72)
63. old valid bundle below trusted frontier;
64. restored database attempts to lower frontier;
65. new oracle defect invalidates old PASS;
66. new semantic obligation discovered;
67. mutant later classified invalid;
68. historical fixture corpus expands;
69. partial proof reused without affected-obligation replay;
70. archive restores bundle but not frontier evidence;
71. independently authenticated current frontier accepts exact current bundle;
72. stale proof retained as archive but denied admission authority.

### Attestation separation / completeness (73-80)
73. self-signed producer bundle with no adjudication;
74. producer and adjudicator signatures from same key but distinct semantics absent;
75. valid timestamp on semantically failing proof;
76. valid transparency inclusion on incomplete bundle;
77. adjudicator attestation bound to wrong bundle ID;
78. adjudicator attestation bound to wrong frontier;
79. all catalogs complete + independent replay agrees;
80. final PASS survives clean independent replay from closed bundle with network disabled.

## Admission rule

A consequential compatibility edge may become active only when all of the following hold:

1. the proof bundle is closed, canonical and authenticated;
2. its source/target/toolchain/policy/schema/frontier generations are exact;
3. deterministic replay is byte/semantic reproducible under the declared profile;
4. every obligation is discharged by the frozen fixture/mutant/oracle rules;
5. the adjudicator independently reconstructs the obligation set and result;
6. no material disagreement exists;
7. the bundle is at or above the current authenticated minimum frontier;
8. no affected obligation is `INCONCLUSIVE` or `REVALIDATION_REQUIRED`.

Anything weaker is evidence for investigation, not authority to activate a consequential provider compatibility edge.

## Implementation boundary

Production implementation waits for executable RED/GREEN. The first code slice should be a closed proof-bundle schema/canonicalizer plus offline adjudicator skeleton that intentionally rejects missing bytes, undeclared toolchains, stale frontier and producer-only boolean verdicts before any candidate runtime integration.
