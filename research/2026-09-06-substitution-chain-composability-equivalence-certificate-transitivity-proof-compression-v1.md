# Substitution-chain composability / equivalence-certificate transitivity / downgrade-safe proof compression v1

Status: `SUBSTITUTION_CHAIN_COMPOSABILITY_EQUIVALENCE_CERTIFICATE_TRANSITIVITY_PROOF_COMPRESSION_V1_FROZEN`

Date: 2026-09-06

Scope: LAB-093 follow-up to semantic-equivalence substitution and proof-carrying GC. Design + RED-first contract only. It does **not** claim LAB-086 execution, production integration, or behavioral PASS.

## 1. Problem

The prior substitution contract permits deleting a large object `O` after an independently verified substitute `S1` is proven sufficient for a declared dependency class, guarantee namespace, observation schema, verifier/recovery support set, context, and policy frontier.

That still leaves a dangerous optimization: repeatedly compressing already-compressed evidence.

Example:

`O -> S1 -> S2 -> S3`

If each edge is validated only against its immediate predecessor, a later substitute can look locally valid while the chain as a whole has already lost information that was material to the original guarantee. A missing field can be discarded by `O -> S1`; then `S1 -> S2` cannot discover that loss because the missing field no longer exists in `S1`. The chain launders the original information loss.

Therefore equivalence certificates are **not generally transitive**. Transitivity must be proved for the exact semantic relation, context and support set. Proof compression may reduce storage/verification cost only when it preserves the original root claim and all material observation obligations.

Core rule:

> A certificate for `S1 ~= S2` cannot be composed with `O ~= S1` merely because both edges say “equivalent.” Composition is authorized only when the second proof preserves every obligation, context binding and revocation dependency inherited from the first edge, or when a stronger proof directly establishes `O ~= S2` under the current support set.

## 2. Donor mechanisms

### SLSA Verification Summary Attestations — transitive dependency summaries remain bound to inputs and verifier policy

SLSA VSA can summarize verification results for an artifact and transitive dependency levels, but the summary remains tied to an exact subject digest, verifier identity/version, policy, and input attestations. Consumers must still verify the relevant subject/policy/input bindings rather than treat “PASSED” as a universally portable fact.

LAB inference: a compressed equivalence certificate must bind the original root subject and all input certificates it subsumes. A detached `PASS` over `S2` cannot inherit `O`'s guarantees without authenticated linkage and policy compatibility.

Primary sources:
- https://slsa.dev/spec/v1.1/verification_summary
- https://slsa.dev/spec/v1.2/verifying-artifacts

### SLSA provenance — completeness claims are scoped and cannot be inferred through omission

SLSA provenance distinguishes authenticated subject/material digests from completeness claims. Missing material information is not silently upgraded to complete merely because a later artifact has valid provenance.

LAB inference: if `S1` omitted a material observation from `O`, no later certificate derived only from `S1` can reconstruct or certify that observation unless it carries an independent proof rooted in `O` or another authoritative witness.

Primary sources:
- https://slsa.dev/spec/v1.2/build-provenance
- https://slsa.dev/spec/v1.0/requirements

### in-toto — chain verification binds steps, actors, materials and products

in-toto models a sequence of authorized steps whose materials/products are checked against signed policy. A later product does not retroactively authorize an earlier missing or unauthorized transformation.

LAB inference: every substitution hop is an explicit transformation/verification step. Composition must preserve the step graph and authorization lineage or replace it with a stronger proof that explicitly subsumes it.

Primary source:
- https://in-toto.io/docs/what-is-in-toto/

### Cryptographic accumulators / recursive proof systems — compression can attest verification of prior proofs, but statement binding is everything

Recursive proof systems can compress a chain of proofs by proving that prior proofs verified. That mechanism is safe only when the recursive statement includes the exact public inputs/constraints that must remain true. A small recursive proof does not make a weak or incomplete inner statement stronger.

LAB inference: proof compression may shorten the certificate chain, but the compressed statement must expose and bind the original object digest, inherited obligation set, support-set generations, context, policy/trust frontiers, and revocation dependencies. Compression cannot erase public inputs merely to save bytes.

This is a mechanism donor only; v1 does not require SNARK/STARK deployment.

## 3. Four relations that must not be conflated

### 3.1 `BYTE_IDENTITY`

Same canonical bytes/content address. Transitive by ordinary equality when object-context identity is also identical.

### 3.2 `LOSSLESS_RECONSTRUCTABILITY`

`S` can reconstruct exact canonical `O` under frozen decoder/toolchain dependencies. Transitive only if the complete decoder chain and dependencies remain available/authenticated and composing decoders reproduces exact `O`.

### 3.3 `GUARANTEE_SCOPED_SEMANTIC_EQUIVALENCE`

`S` preserves all material observations for an exact tuple:

`G = (dependency_class, namespace, observation_schema_gen, verifier_set_gen, recovery_set_gen, context_digest, policy_gen, trust_frontier)`.

This relation is **not assumed transitive**. A policy must explicitly establish transitivity for the observation algebra or require direct root-to-leaf revalidation.

### 3.4 `VERDICT_EQUIVALENCE`

Two objects happen to produce the same current verdict/output. This is not semantic equivalence and has no destructive-GC transitivity.

## 4. Root obligation set

When `O -> S1` is first admitted, create an immutable **root obligation set** `ROS(O,G)` containing every material observation and authority dependency that must remain provable after `O` is deleted.

At minimum it binds:

- original object digest/type/schema generation;
- dependency class and guarantee namespace;
- canonical observation schema and all material observation identifiers;
- verifier/recovery support-set generations;
- context digest and authority/trust frontier;
- equivalence procedure/toolchain generation;
- original transform-side and verifier-side witness digests;
- challenge/revocation dependencies;
- any decoder/reconstruction dependencies;
- any E3 recovery-only observations not exercised during ordinary verification;
- any conditions that make the relation non-transitive.

A later substitute may be smaller than `S1`, but the authoritative certificate chain may never contain less commitment to `ROS(O,G)` unless an authenticated policy migration proves that the removed obligation is no longer material.

## 5. Observation-set monotonicity

Every substitution certificate MUST expose two canonical sets:

- `OBS_REQUIRED`: observations inherited from the root obligation set under the current support/policy generation;
- `OBS_PROVABLE_BY_SUBSTITUTE`: observations independently provable from the substitute plus its retained witness bundle.

For composition to be admitted:

`OBS_REQUIRED(parent) subseteq OBS_PROVABLE_BY_SUBSTITUTE(child)`

and no required observation may become merely “previously checked” unless the parent certificate itself is retained as authoritative evidence and the child proof explicitly proves that parent certificate's statement under the same or a stronger support set.

Unknown observation compatibility is fail-closed.

A child certificate that drops an observation identifier because its current verifier does not read it is a downgrade, not compression.

## 6. Context and support-set compatibility

`O -> S1` and `S1 -> S2` compose only if all inherited dimensions are compatible.

### Exact-match dimensions by default

- guarantee namespace;
- dependency class;
- logical history/provider identity;
- authority/trust-root generation where material;
- canonicalizer/schema generation where semantics can change;
- recovery failure-class set for E3;
- external anchor/history position where bound into the claim.

### Monotone dimensions

A child may use a newer verifier/recovery support-set generation only if an authenticated subsumption proof shows the newer set preserves every old required observation and introduces no unmet material observation.

A smaller support set cannot inherit destructive authority from a larger parent support set.

### Partial context overlap

Partial overlap never implies composition. If parent applies to contexts `{A,B}` and child proves `{B,C}`, composition for `A` is absent and for `B` requires exact context-specific linkage. Certificates must be split or scoped explicitly rather than merged by union.

## 7. Equivalence-certificate structure

Every hop certificate `EC(parent, child)` MUST bind:

- certificate format/version;
- root original digest `O_root`;
- immediate parent digest;
- child substitute digest;
- parent certificate/MRW digests being consumed;
- root obligation set digest;
- inherited + newly added observation sets;
- dependency class / namespace / context;
- verifier/recovery support-set generations;
- transform/equivalence procedure generation;
- policy/trust/schema/materiality/substitution frontiers;
- independent verifier identities and diversity domains;
- revocation dependencies for parent and current hop;
- challenge horizon state;
- explicit composition mode;
- explicit statement whether direct root-to-child replay occurred;
- decision and signatures/threshold authorization.

Valid composition modes:

1. `DIRECT_ROOT_REPLAY` — strongest semantic path; child is compared directly with `O_root` or an exact/lossless reconstruction of it.
2. `PROOF_OF_PARENT_PROOF` — child proves the parent certificate statement and preserves the complete ROS; suitable only when statement-binding and verifier policy permit recursive composition.
3. `LOSSLESS_CHAIN` — each transform is reversible and exact root bytes can be reconstructed.
4. `NON_TRANSITIVE` — local equivalence only; no inherited destructive-GC authority.

## 8. Transitivity decision

For a chain `O -> S1 -> ... -> Sn`, destructive authority for deleting any still-retained ancestor requires one of:

### A. Direct root proof

A current independent verifier checks `Sn` against exact/reconstructed `O` and current `ROS(O,G)`.

### B. Proven transitive relation

Policy has frozen an equivalence relation whose transitivity is formally justified for the complete observation algebra, and each hop proves membership in that same relation under compatible context/support sets.

### C. Recursive proof of complete parent statement

A child proof verifies the parent proof/certificate and binds all parent public inputs, ROS, support-set/context/frontier values and revocation dependencies. The compressed proof must be independently verifiable from the root statement without trusting hidden intermediate state.

Absent A/B/C, the chain is not deletion-authoritative beyond its last directly verified ancestor.

## 9. Downgrade-safe proof compression

Proof compression is allowed to discard **representation redundancy**, not semantic obligations.

A compressed witness `CW` MUST expose or commit to:

- `O_root` digest;
- current substitute digest;
- ROS digest;
- exact chain/certificate set it subsumes;
- union of revocation dependencies;
- effective support-set generations;
- effective context;
- strongest dependency class preserved;
- verifier diversity provenance;
- policy/trust/schema frontiers;
- challenge status;
- compression verifier/toolchain generation.

Compression is rejected when it:

- replaces a list of material observations with only a final PASS bit;
- hides which certificate introduced an obligation;
- loses a revocation dependency;
- collapses independent verifier domains without recording the collapse;
- changes support-set/context scope;
- turns `E3` recovery equivalence into `E2` verification equivalence;
- removes evidence needed to audit the compression procedure itself.

## 10. Revocation blast radius

A transitive chain inherits revocation risk from **every material ancestor certificate, transform, verifier, canonicalizer and policy generation** that its compressed proof depends on.

When any such dependency is revoked or repaired:

1. identify all descendant certificates whose proof DAG reaches the revoked node;
2. mark them `REVALIDATION_REQUIRED`;
3. stale every GC mark/deletion authorization derived from those descendants;
4. re-root retained exact ancestors while available;
5. if exact root evidence is gone, determine whether another independently retained proof is sufficient under current ROS;
6. otherwise quarantine/degrade the consequential guarantee.

A compressed certificate that cannot reveal its ancestor dependency set is invalid for destructive GC.

Revocation does not delete history. Old certificates remain historical evidence that a substitution was once used.

## 11. Cycles and self-support

Certificate graph edges must form an acyclic dependency DAG for authority purposes.

`S1 -> S2` plus `S2 -> S1` cannot establish equivalence, liveness, completeness or retention authority. A cycle with no path to an authenticated root obligation set has zero authority.

If content-deduplication creates benign physical cycles, the logical proof graph must still expose an acyclic root-to-leaf derivation.

## 12. Mixed verifier generations

A chain may contain certificates created under v1, v2 and v3 verifiers. Composition requires explicit support-set subsumption.

Rules:

- newer verifier version is not automatically stronger;
- if v3 drops an observation checked by v1, chain portability fails for guarantees that still require it;
- if v3 adds a material observation, all affected descendants require revalidation;
- if v2 and v3 share a buggy parser/canonicalizer lineage, nominal version diversity does not create independent evidence;
- verifier retirement may be safe only after another retained proof path covers every inherited ROS obligation.

## 13. Compression checkpoints

Long chains MAY be periodically summarized by an authenticated **equivalence-chain checkpoint**.

Checkpoint binds:

- root object + current leaf substitute;
- chain Merkle/DAG commitment;
- ROS digest;
- effective observation/support/context/class tuple;
- union revocation set commitment;
- current policy/trust/schema frontiers;
- independent replay verdicts;
- challenge horizon status;
- predecessor checkpoint hash;
- monotonic sequence/epoch.

Late auditors may start from a trusted checkpoint only under the existing anchored-snapshot/bootstrap rules. A checkpoint from the same producer cannot erase the requirement for independent provenance and historical fraud/revocation evidence.

## 14. Safe deletion rule for chains

Before deleting `O`, `S1`, or any intermediate ancestor after a new compressed substitute is admitted:

1. freeze current root obligation set and support/context/frontier tuple;
2. verify the complete logical proof DAG;
3. prove observation-set monotonicity to the leaf;
4. prove valid transitivity mode for every compressed segment;
5. verify revocation-dependency union completeness;
6. independently replay either root-to-leaf semantics or the accepted recursive proof statement;
7. preserve original/ancestor evidence through the challenge horizon;
8. recompute proof-carrying GC reachability/complete mark;
9. prove no stronger dependency class or recovery path needs the ancestor;
10. bind deletion authorization to the exact GC/substitution epoch;
11. re-check trust/schema/materiality/substitution/revocation frontiers immediately before deletion.

If any check is `UNKNOWN`, deletion is denied.

## 15. Anti-laundering invariants

1. Local hop equivalence does not imply chain equivalence.
2. Same final verdict is never sufficient for transitivity.
3. Missing information cannot be recreated by a later certificate derived only from the already-lossy substitute.
4. Every child inherits the root obligation set until an authenticated materiality migration removes an obligation.
5. Support sets can expand only with revalidation/subsumption; they cannot silently shrink.
6. Partial context overlap never authorizes union-scoped composition.
7. Proof compression must retain revocation dependency closure.
8. Cyclic certificates do not self-authorize.
9. A compressed PASS bit cannot replace material observation commitments.
10. `E2` proof cannot inherit `E3` authority without recovery-specific evidence.
11. A newer verifier is not assumed stronger.
12. Direct root replay always dominates a weaker chain summary when they disagree.
13. Conflicting authenticated chain verdicts enter `EQUIVALENCE_DISAGREEMENT`; no latest-wins.
14. If root evidence is gone and the compressed proof cannot answer a newly material observation, degrade/quarantine rather than infer the missing fact.

## 16. 80-case RED-first matrix

No production chain-compression integration before these cases exist as executable RED-first tests at the appropriate abstraction level.

### A. Basic composition (1-10)
1. `O==S1==S2` byte identity composes.
2. two exact reversible encodings reconstruct `O` and compose.
3. semantic `O~S1`, semantic `S1~S2`, no transitivity proof -> reject inherited authority.
4. direct `O~S2` current proof -> accept independent of weak intermediate.
5. parent certificate missing -> reject.
6. root digest mismatch -> reject.
7. child names wrong immediate parent -> reject.
8. certificate chain reordered -> reject.
9. malformed chain checkpoint -> reject.
10. same final verdict but missing semantic proof -> reject.

### B. Observation monotonicity (11-20)
11. child proves superset of required observations -> compose candidate.
12. child drops one E2 material observation -> reject.
13. child drops recovery-only E3 observation -> reject E3 even if E2 passes.
14. unknown observation ID -> fail closed.
15. observation renamed with authenticated schema mapping -> accept when bijective/materiality-preserving.
16. observation merged lossy -> reject.
17. observation split with complete authenticated mapping -> accept candidate.
18. child retains commitment but no way to verify observation -> reject.
19. parent checked field then child stores only PASS -> reject unless valid proof-of-parent-proof binds the field obligation.
20. direct root replay catches field lost at first hop -> chain rejected.

### C. Context / namespace compatibility (21-30)
21. exact same context all hops -> candidate.
22. namespace A -> B without subsumption -> reject.
23. provider/history identity changes -> reject.
24. partial contexts `{A,B}` then `{B,C}` -> only explicit B-scoped proof may compose.
25. trust frontier mismatch material to observation -> reject/revalidate.
26. context hash reused with different canonicalizer generation -> reject.
27. external anchor position omitted by child -> reject when root bound it.
28. exact authenticated context-independence proof -> permit scoped reuse.
29. child broadens scope without evidence -> reject.
30. child narrows scope and tries to delete root used by excluded context -> reject.

### D. Support-set evolution (31-40)
31. identical verifier/recovery support sets -> candidate.
32. new verifier adds no observations with authenticated subsumption -> compose.
33. new verifier adds material observation, root available -> require direct revalidation.
34. new verifier adds material observation, root gone, substitute insufficient -> quarantine/degrade.
35. child silently removes old verifier -> reject inherited authority.
36. verifier version number increases but behavior weakens -> reject after observation diff.
37. two versions share same buggy parser lineage -> diversity collapse recorded.
38. recovery set shrinks while E3 live -> reject deletion authority.
39. retired verifier fully subsumed by independent retained proof -> allow policy retirement.
40. mixed support generations with no canonical mapping -> fail closed.

### E. Proof compression (41-50)
41. compressed proof binds root, leaf, ROS, chain digest, revocation union -> candidate.
42. compressed proof contains only leaf digest + PASS -> reject.
43. compression omits one ancestor certificate digest -> reject.
44. compression omits one revocation dependency -> reject.
45. compression changes dependency class E3->E2 -> reject.
46. compression changes namespace/context -> reject.
47. recursive proof verifies parent proof but not parent public inputs -> reject.
48. recursive proof binds all parent public inputs + current ROS -> candidate.
49. compression verifier revoked -> descendants revalidation required.
50. compressed checkpoint predecessor mismatch -> reject.

### F. Revocation / disagreement (51-60)
51. first-hop verifier revoked -> all dependent descendants stale.
52. intermediate transform revoked -> descendants stale.
53. irrelevant E0 provenance signer revoked -> no E2/E3 blast radius absent dependency edge.
54. revocation union incomplete -> compressed proof invalid.
55. independent direct root proof survives revoked intermediate chain -> preserve direct path only.
56. two authenticated equivalence verdicts disagree -> quarantine, no latest-wins.
57. revoked child does not erase historical use record.
58. materiality repair upgrades dependency class -> descendants revalidate.
59. trust-root revocation affects one chain branch only -> exact reachable blast radius.
60. revocation occurs after mark before delete -> deletion authorization stale.

### G. Cycles / adversarial laundering (61-70)
61. `S1->S2->S1` cycle without root -> zero authority.
62. cycle reachable from root but adds no new proof -> cannot replace acyclic root derivation.
63. producer creates many tiny hops to hide first lossy transform -> root replay detects/rejects.
64. hop self-signs equivalence using same buggy extractor -> diversity rule rejects consequential use.
65. two nominal verifiers generated from same code/oracle -> common-mode collapse.
66. attacker substitutes certificate with same display name different digest -> reject.
67. replay certificate from different namespace -> reject.
68. replay certificate from old policy generation with revoked observation -> reject/revalidate.
69. child commits parent certificate but not root obligation set -> reject.
70. chain summary falsely claims fewer hops than Merkle/DAG commitment -> reject.

### H. GC / crash / recovery (71-80)
71. valid chain admitted, ancestor kept through challenge horizon -> no early deletion.
72. archive ancestor retrieval fails before deletion -> deletion denied.
73. GC mark computed before new child certificate publication -> epoch recheck handles new state.
74. crash after chain acceptance before GC -> restart reconstructs same authority state.
75. crash after delete authorization before physical delete -> frontiers rechecked on resume.
76. root deleted, later new material observation missing -> guarantee degrades/quarantines, no invented data.
77. intermediate deleted but complete recursive proof + root/ROS survive -> verification still reproduces authorized statement.
78. late auditor bootstraps from authenticated chain checkpoint and independently verifies continuity.
79. disaster recovery uses substitute that passes E2 but lacks E3 field -> recovery rejects, proving class separation.
80. full independent replay reproduces root-to-leaf obligations, certificate DAG, revocation union and current GC eligibility.

## 17. Frozen decision

`SUBSTITUTION_CHAIN_COMPOSABILITY_EQUIVALENCE_CERTIFICATE_TRANSITIVITY_PROOF_COMPRESSION_V1_FROZEN` means:

- semantic equivalence is non-transitive by default;
- every substitution lineage carries an immutable root obligation set;
- composition requires observation-set monotonicity plus exact/authorized context and support-set compatibility;
- destructive authority may compose only through direct root replay, an explicitly proven transitive relation, or a recursive proof that binds the complete parent statement/public inputs;
- proof compression may remove representation redundancy but not obligations, revocation dependencies, context, class, support-set or authority-frontier bindings;
- revocation blast radius follows the full proof DAG even after compression;
- cycles/self-support have zero authority;
- E3 recovery obligations cannot be laundered into E2 verification-only summaries;
- deletion remains fail-closed on `UNKNOWN` and requires a fresh proof-carrying GC mark after chain/compression changes.

No production implementation or behavioral PASS is claimed.

## 18. Next research seam

The next distinct seam, if exact execution remains unavailable, is **equivalence-certificate trust-root rotation / cross-generation verifier handoff / recursive-proof verifier agility**: define how long-lived compressed chains survive signer/verifier-key rotation, algorithm retirement and proof-system upgrades without either trusting obsolete cryptography forever or invalidating all historical substitutions at once; require authenticated handoff/subsumption, downgrade resistance, algorithm-agility policy and RED cases for compromised old roots, dual-sign periods, mixed algorithm chains and offline late verification.
