# Dependency repair authority / materiality adjudication / semantic-edge taxonomy v1

Status: `DEPENDENCY_REPAIR_AUTHORITY_MATERIALITY_ADJUDICATION_SEMANTIC_EDGE_TAXONOMY_V1_FROZEN`

Date: 2026-09-06

Scope: LAB-093 follow-up to the proof-carrying compaction / dependency-schema evolution work. This is a design and RED-first contract only. It does **not** claim production implementation or behavioral PASS.

## 1. Problem

The previous GC contracts establish that historical dependency schemas cannot be silently reinterpreted, that newly discovered dependencies must be represented as authenticated additive repair records, and that destructive GC requires both graph-integrity and complete-mark proofs.

A remaining authority gap is materiality itself.

If the same producer that omitted a dependency is also allowed to assert that a newly discovered edge is material, the repair process is not independently trustworthy. Conversely, if a broad repair authority can declare any arbitrary object permanently necessary, it can turn the evidence store into an unbounded retention/availability denial of service.

A safe design therefore needs to answer four separate questions:

1. **Who may propose that a missing edge exists?**
2. **Who may decide what semantic class that edge belongs to?**
3. **Who may make that edge GC-authoritative?**
4. **How can an edge later be weakened, superseded, revoked, or retired without rewriting history?**

These are different powers and MUST NOT be collapsed into one unrestricted repair-signing key.

## 2. Donor mechanisms and applicability

### Nix GC roots — reachability is authority, not commentary

Nix treats configured GC roots as live roots and retains their transitive dependencies. This is the useful donor property: an edge that participates in retention is operational authority over deletion, not merely descriptive provenance.

LAB inference: promotion of a repair edge into a retention-bearing class must be a separately authorized state transition. An audit annotation cannot silently become a GC root.

Primary source: Nix Reference Manual, garbage-collector roots / `nix-store --gc`.

### Git prune/gc — unreachable does not mean immediately disposable

Git prunes objects based on reachability from refs and additional retained roots, and its documentation explicitly warns that concurrent creation/reference establishment can race with pruning. Git also uses expiry/grace behavior rather than treating momentary unreachability as sufficient for immediate deletion.

LAB inference: edge removal/downgrade and GC deletion need a frontier/grace protocol. A repair-authority transition cannot make an object destructively collectible in the same instant without re-evaluating roots and concurrent publications.

Primary source: `git-prune(1)`, `git-gc(1)`.

### TUF role/key thresholds — authorization is scoped and revocable

TUF separates roles, associates roles with authorized key sets and thresholds, and changes/revokes trusted keys through authenticated root metadata continuity.

LAB inference: repair authority should be role/capability scoped by edge class and namespace. Revocation of a repair signer or adjudicator is a trust-frontier event that can trigger revalidation; it does not erase prior signed records.

Primary source: The Update Framework specification, root role / roles / thresholds / key rotation.

### in-toto / SLSA provenance — provenance is not equivalent to liveness

SLSA/in-toto provenance records subjects, materials and builder/process evidence. These attestations are useful evidence about derivation but do not inherently assert that every referenced material must remain a permanent GC root.

LAB inference: provenance relationships and liveness/recovery dependencies must be different edge classes. A provenance-only relation may be audit-relevant without being retention-authoritative indefinitely.

Primary source: SLSA provenance schema and in-toto statement/link model.

## 3. Semantic edge taxonomy

Every dependency edge MUST carry exactly one semantic class under an authenticated taxonomy generation. Classes are ordered by authority impact, but not all are directly comparable.

### `E0_AUDIT_PROVENANCE`

Meaning: useful to explain derivation, attribution, or audit lineage, but not required to execute a supported verification/recovery procedure.

GC effect: does not independently keep the target live after its policy retention horizon. It may remain retained because another stronger edge or root reaches it.

Examples: optional build-environment metadata, human-readable research notes, redundant provenance mirrors whose authenticated digest is retained elsewhere.

### `E1_REPRODUCIBILITY_INPUT`

Meaning: required to reproduce a supported computation/verdict but not required to validate an already materialized authenticated proof using a supported independent verifier.

GC effect: retained while reproducibility is an active product/security guarantee or while a challenge/reproduction window is open. May expire only through explicit policy-authorized retirement.

### `E2_VERIFICATION_DEPENDENCY`

Meaning: required for at least one supported verifier to check the truth/integrity of a consequential historical claim.

GC effect: live while any supported consequential verdict/checkpoint that depends on it remains authoritative or challengeable.

Examples: canonical schema generation, verifier semantics, proof bundle components, historical public key needed to validate a retained attestation.

### `E3_RECOVERY_DEPENDENCY`

Meaning: required to execute a supported recovery, re-adjudication, rollback/fork investigation, or compromise response path.

GC effect: live while the corresponding recovery guarantee exists. A recovery dependency may remain live after the ordinary verification horizon expires.

### `E4_AUTHORITY_CONTINUITY`

Meaning: required to establish monotonic authority/trust continuity itself.

GC effect: strongest ordinary retention class. It cannot be downgraded merely because a newer state supersedes it; an authenticated subsumption/continuity proof must show that every supported historical verifier/recovery path can still establish the same authority relation.

Examples: trust-root transition evidence, authenticated cutoff boundary, revocation frontier, fork-resolution bridge.

### `E5_LEGAL_OR_OWNER_HOLD`

Meaning: external retention requirement explicitly introduced by an authorized owner/legal policy surface.

GC effect: live until a matching authorized release. This class is intentionally outside autonomous repair adjudication: the repair system MUST NOT manufacture legal/owner holds.

### `E_NEG_NON_MATERIAL`

Meaning: authenticated adjudication that a proposed relation is not material to supported verification/recovery/authority semantics.

GC effect: no retention authority. This is not deletion authorization by itself; other live edges may still retain the object.

## 4. Separation of powers

A repair lifecycle has four distinct roles.

### 4.1 Reporter

May submit evidence that an expected dependency is absent, misclassified, or incorrectly targeted.

Reporter power is intentionally broad. Any authenticated monitor/auditor may report; reports have **zero** GC authority by themselves.

### 4.2 Classifier

May propose an edge class and rationale under a specific taxonomy generation.

Classifier capability MUST be namespace/class scoped. A classifier authorized only for reproducibility metadata cannot create `E4_AUTHORITY_CONTINUITY` edges.

### 4.3 Materiality adjudicator

Determines whether the proposed edge is actually material, based on independently reproducible evidence. For `E2+`, the adjudicator MUST NOT share the same material semantic extractor/oracle lineage as the producer whose omission triggered the repair unless policy explicitly degrades assurance and records that degradation.

### 4.4 Repair registrar

Commits the accepted repair record into the authenticated repair frontier. Registration proves that an adjudicated result is now part of the effective graph. Registrar cannot change class/content; it only admits the exact adjudicated digest.

A single implementation may hold multiple roles only when the policy generation explicitly permits that composition. For consequential `E3/E4` edges, default policy SHOULD require classifier/adjudicator diversity and a threshold or two-party authorization.

## 5. Canonical repair record

A repair record MUST bind at minimum:

- repair record version;
- historical subject object digest;
- original dependency-schema generation;
- discovered target object digest;
- proposed semantic edge class;
- edge direction and canonical relation type;
- discovery evidence digest(s);
- independent materiality evidence digest(s);
- classifier identity/generation/scope;
- adjudicator identity/generation/scope;
- taxonomy generation;
- repair policy generation;
- affected verdict/checkpoint/recovery namespace or deterministic blast-radius descriptor;
- creation frontier/checkpoint;
- supersedes/subsumes references, if any;
- canonical decision: `ACCEPT`, `REJECT_NON_MATERIAL`, `DISAGREEMENT`, `QUARANTINE`;
- signatures/attestations required by policy.

The record is additive and immutable. Corrections create new records; they do not mutate old bytes.

## 6. Materiality evidence

Materiality is a semantic claim and MUST be proven at the abstraction level of the supported guarantee.

### For `E1_REPRODUCIBILITY_INPUT`

Acceptable evidence: independent reconstruction shows that omitting/substituting the target prevents deterministic reproduction of the claimed result while all other recorded inputs remain fixed.

### For `E2_VERIFICATION_DEPENDENCY`

Acceptable evidence: at least one supported verifier requires the target (or its authenticated semantic equivalent) to validate the consequential claim; removing it makes verification impossible or changes verdict semantics.

### For `E3_RECOVERY_DEPENDENCY`

Acceptable evidence: a frozen recovery procedure demonstrably requires the target to reach an authenticated safe state from at least one supported failure/compromise condition.

### For `E4_AUTHORITY_CONTINUITY`

Acceptable evidence: removing the target breaks a required authenticated chain between two authority frontiers, trust roots, cutoffs, revocations, or fork-resolution states.

### Negative materiality

A `REJECT_NON_MATERIAL` result requires affirmative evidence that all supported verifier/recovery/authority paths remain valid without the proposed edge. Mere inability to reproduce the reporter's failure is `UNKNOWN`, not non-material.

## 7. Anti-pinning rules

Repair authority must not become a permanent storage DoS surface.

1. **Reports do not pin.** An unadjudicated report receives a bounded quarantine retention horizon, not permanent liveness.
2. **Class scope is enforced before registration.** A low-scope classifier cannot produce a higher-authority edge.
3. **Every accepted repair carries a deterministic blast radius.** `UNKNOWN` blast radius is permitted only as a temporary conservative root and MUST trigger mandatory refinement/review.
4. **No arbitrary transitive wildcard.** Repair records may not say “retain all descendants/all history” unless the exact dependency set is itself authenticated by a supported schema/query commitment.
5. **No self-rooting cycles.** Repair-created cycles remain dead unless reachable from an independent authenticated root.
6. **Retention budgets are telemetry, not deletion authority.** Exceeding a storage budget may escalate review or degrade product guarantees, but cannot silently downgrade `E2+` edges.
7. **Repeated frivolous reporter submissions may be rate-limited/quarantined without weakening already accepted repairs.**
8. **Registrar cannot invent targets.** It accepts only exact adjudicated content digests.

## 8. Upgrade / downgrade semantics

### Upgrade

`E0 -> E1 -> E2 -> E3/E4` requires a new authenticated repair/adjudication record with evidence satisfying the stronger class. Upgrades are additive and immediately participate in subsequent GC mark epochs after the repair frontier is committed.

### Downgrade

Downgrade is more dangerous than upgrade because it can authorize deletion.

A downgrade requires:

- a new authenticated adjudication;
- proof that every supported verifier/recovery/authority path remains valid under the weaker class;
- explicit affected-closure calculation;
- no unresolved challenge, fork, revocation revalidation, or repair disagreement involving the edge;
- freeze of trust/taxonomy/repair frontiers;
- a fresh GC mark after the downgrade is committed.

A downgrade NEVER rewrites the historical record that the edge was once classified more strongly.

### `E4` special rule

`E4_AUTHORITY_CONTINUITY` cannot be downgraded based only on age, supersession, or “newer root exists.” It requires an authenticated subsumption proof preserving continuity from every still-supported historical anchor.

## 9. Revocation and compromise

Revoking a classifier/adjudicator/registrar does not delete its historical records. It changes whether those records remain admissible at the current trust frontier.

If a revoked/compromised authority participated in an accepted `E2+` repair:

1. compute the proof-carrying blast radius;
2. root all implicated objects/closures as `REVALIDATION_REQUIRED`;
3. exclude the compromised authority from new threshold calculations;
4. independently re-adjudicate materiality under the current policy;
5. only after re-adjudication may the edge be reaffirmed, replaced, downgraded, or rejected;
6. destructive GC MUST NOT use a mark proof frozen before the revocation frontier.

Compromise can therefore reactivate old evidence and old objects that were otherwise nearing retirement.

## 10. Conflict handling

Conflicting authenticated repair decisions over the same canonical edge key create `MATERIALITY_DISAGREEMENT`.

During disagreement:

- retain the union of all stronger implicated targets/closures;
- do not majority-vote unless the policy explicitly defines a threshold over independent adjudicator domains;
- do not choose the cheaper or more permissive storage outcome;
- do not let `REJECT_NON_MATERIAL` override an accepted `E2+` decision without explicit conflict adjudication;
- preserve all contradictory signed records as evidence.

If the conflict is caused by common-mode semantic lineage, those adjudicators collapse into one diversity domain for threshold purposes.

## 11. GC composition

A destructive GC epoch MUST freeze:

- root set;
- dependency-schema generations;
- repair frontier;
- taxonomy generation;
- repair-policy generation;
- trust/revocation frontier;
- unresolved materiality disagreements;
- active challenge/recovery/owner-hold horizons.

The effective edge set is:

`original_schema_edges + accepted_repairs - only_those_retirements_proven_by_current_authenticated_downgrade/subsumption_records`

Audit-only `E0` edges are traversed for provenance export/audit completeness when requested, but do not independently mark targets live. `E1+` edges mark according to their active horizon/policy. `E5` roots are external explicit roots and cannot be synthesized by repair classifiers.

Any frontier advance before physical deletion invalidates the deletion decision for affected objects and requires re-check/remark.

## 12. RED-first matrix (80 cases)

The implementation MUST begin with executable failures for the following matrix before production refactor.

### A. Role separation and scope (1-10)
1. reporter alone cannot pin target;
2. classifier alone cannot register repair;
3. registrar cannot alter adjudicated class;
4. E1-scoped classifier cannot create E4 edge;
5. revoked classifier rejected for new repair;
6. stale classifier generation rejected;
7. wrong namespace scope rejected;
8. same producer+adjudicator common-mode rejected/degraded for required-independent E3;
9. valid independent two-party E4 accepted;
10. signature-valid but policy-unauthorized registrar rejected.

### B. Taxonomy semantics (11-20)
11. E0 provenance does not keep otherwise-dead target live;
12. E1 retained during reproduction horizon;
13. E1 retires only after authorized horizon closure;
14. E2 retained while consequential verdict is authoritative;
15. E3 retained after E2 horizon if recovery guarantee remains;
16. E4 retained across ordinary supersession;
17. E5 cannot be created by repair authority;
18. E_NEG does not itself delete target;
19. unknown class fails closed;
20. taxonomy-generation mismatch fails closed.

### C. Materiality evidence (21-30)
21. independent reproduction proves E1;
22. producer self-assertion alone insufficient for E2;
23. supported verifier dependency proves E2;
24. unsupported/debug-only verifier does not prove E2;
25. frozen recovery path proves E3;
26. hypothetical undocumented recovery path does not prove E3;
27. broken trust chain proves E4;
28. mere age/size does not negate materiality;
29. failure to reproduce reporter issue yields UNKNOWN, not non-material;
30. affirmative independent path analysis can support E_NEG.

### D. Anti-pinning (31-40)
31. thousands of reports do not become permanent roots;
32. unadjudicated quarantine expires according to bounded policy unless separately rooted;
33. wildcard retain-all repair rejected;
34. repair-created cycle does not self-root;
35. unrelated target injection rejected by canonical relation evidence;
36. duplicate repair records do not multiply liveness authority;
37. UNKNOWN blast radius temporarily roots conservative closure;
38. UNKNOWN must schedule/refuse GC until refinement according to policy;
39. storage-budget breach cannot silently drop E3;
40. reporter rate-limit cannot remove accepted E2 repair.

### E. Upgrades/downgrades (41-50)
41. E0->E2 requires new evidence/adjudication;
42. accepted upgrade affects next mark epoch;
43. E3->E1 downgrade without path proof rejected;
44. downgrade with unresolved challenge rejected;
45. downgrade with unresolved materiality disagreement rejected;
46. downgrade followed by stale old mark cannot delete;
47. downgrade preserves historical stronger record;
48. E4 age-only downgrade rejected;
49. E4 subsumption with full historical-anchor continuity accepted;
50. taxonomy migration cannot silently downgrade historical edges.

### F. Revocation/compromise (51-60)
51. classifier revocation revalidates affected repairs;
52. adjudicator revocation revalidates affected E2+ repairs;
53. registrar compromise does not erase authenticated history;
54. revoked authority excluded from new threshold;
55. old affected objects re-rooted during revalidation;
56. pre-revocation GC mark becomes stale;
57. independent reaffirmation restores admissibility;
58. conflicting re-adjudication enters disagreement;
59. unaffected repair outside blast radius remains usable;
60. unknown blast radius widens conservatively.

### G. Conflict/diversity (61-70)
61. ACCEPT E3 vs REJECT_NON_MATERIAL enters disagreement;
62. system retains stronger implicated closure during disagreement;
63. latest-wins forbidden;
64. cheapest-storage-wins forbidden;
65. two adjudicators sharing same semantic oracle collapse to one domain;
66. independent threshold resolves according to policy;
67. forged diversity metadata rejected;
68. stale trust frontier cannot resolve disagreement;
69. contradictory records preserved after resolution;
70. resolution record binds exact conflicting record digests.

### H. GC/race/recovery composition (71-80)
71. mark freezes repair/taxonomy/trust frontiers;
72. repair accepted after mark but before delete forces re-check;
73. revocation after mark but before delete forces re-check;
74. new E4 repair after mark prevents implicated deletion;
75. E0-only target can be deleted when no stronger root/horizon exists;
76. archive migration preserves accepted E2/E3 reachability semantics;
77. crash after repair registration before mark restart remains deterministic;
78. crash after mark before delete re-checks frozen/current frontiers;
79. disaster recovery reconstructs effective edge set from original schema + immutable repairs/adjudications;
80. second independent verifier reproduces the final GC eligibility decision from the frozen proof bundle.

## 13. Security invariants

1. **Existence, classification, materiality, registration and deletion authority are separate claims.**
2. **A repair report is not a root.**
3. **A provenance edge is not automatically a liveness edge.**
4. **A stronger semantic edge cannot be weakened by unauthenticated reinterpretation or schema migration.**
5. **No single buggy producer may both omit an edge and unilaterally prove its materiality/non-materiality for consequential classes.**
6. **Repair authority cannot create owner/legal holds.**
7. **Unknown/disputed materiality never authorizes destructive deletion.**
8. **Revocation may increase retention by reopening historical revalidation; that is intentional fail-closed behavior.**
9. **Cycles do not create liveness without an authenticated root.**
10. **Every destructive GC decision is reproducible from an authenticated, frozen authority/taxonomy/repair/trust frontier.**

## 14. Implementation guidance

Do not implement this as ad-hoc boolean fields on dependency rows. Use content-addressed immutable records and explicit current frontiers.

A minimal implementation should separate:

- `RepairReport`;
- `MaterialityProposal`;
- `MaterialityAdjudication`;
- `RegisteredRepair`;
- `RepairRetirement/Subsumption`;
- taxonomy/policy generations;
- trust/revocation frontier;
- GC proof bundle.

The production implementation must compose with the prior LAB-093 contracts for proof bundles, independent adjudication, trust-frontier witnesses, omission/non-inclusion, mapper derivation completeness, late-auditor bootstrap, compaction, dependency repair and complete-mark proofs. It must not create a parallel locally-valid authority island.

## 15. Decision

Freeze `DEPENDENCY_REPAIR_AUTHORITY_MATERIALITY_ADJUDICATION_SEMANTIC_EDGE_TAXONOMY_V1_FROZEN`.

No production mutation is authorized by this document. The next implementation step, when exact executable source access is available, is RED-first tests for the 80 cases above, beginning with role/scope separation and the critical malicious-pinning / omitted-security-edge / harmless-metadata-misclassification / downgrade / disagreement cases.
