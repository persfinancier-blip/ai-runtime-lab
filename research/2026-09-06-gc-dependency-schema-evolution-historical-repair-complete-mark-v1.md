# GC dependency-schema evolution / historical dependency repair / proof-of-complete-mark semantics v1

Status: `GC_DEPENDENCY_SCHEMA_EVOLUTION_HISTORICAL_REPAIR_COMPLETE_MARK_V1_FROZEN`

Date: 2026-09-06

Scope: design/evidence contract only. No production GC engine, migration, verifier, or behavioral PASS is claimed.

## Problem

The previous proof-carrying GC contract makes destructive deletion depend on authenticated roots, typed content-addressed dependency edges, horizons/holds, archive receipts, and a reproducible mark epoch. That is still insufficient if an older dependency schema was itself incomplete.

A later verifier may discover that object type `T@schema_v1` omitted a material dependency edge that should have kept evidence `E` reachable. If the system merely reinterprets old objects under `schema_v2`, history becomes mutable: the same historical object can acquire different meaning without authenticated evidence of what changed. If it ignores the discovery, future GC may delete evidence that is now known to have been required. If it silently edits old manifests, historical GC proofs cease to be reproducible.

The contract therefore needs a monotonic repair mechanism that adds newly discovered dependency knowledge without rewriting historical objects or pretending earlier GC decisions were made with knowledge they did not have.

## Donor mechanisms and limits

### Nix GC roots / reachability

Nix deletes store paths not reachable from a set of GC roots; live paths are the transitive closure from those roots. This is a useful donor for explicit root-based liveness, but it assumes the reference graph used by the collector already encodes the dependencies that matter.

Primary source: https://releases.nixos.org/nix/nix-2.27.0/manual/command-ref/nix-store/gc.html

### Git fsck connectivity

`git fsck` verifies connectivity and validity of objects and can report objects unreachable from reference heads. `--connectivity-only` checks that referenced reachable objects exist, but explicitly does not perform every semantic validity check. This distinction is the right donor boundary here: graph connectivity proof is only as strong as the edge semantics that define the graph.

Primary source: https://git-scm.com/docs/git-fsck

### TUF trusted-root evolution / rollback resistance

TUF requires a trusted continuity chain when root metadata evolves and rejects rollback to older trusted metadata versions. This is a useful donor for dependency-schema generations: new schema authority must advance monotonically from an authenticated predecessor rather than letting a verifier pick whichever historical schema is convenient.

Primary source: https://theupdateframework.github.io/specification/draft/

### IPFS recursive pins

IPFS recursive pins retain a root and its descendants from GC. This reinforces the distinction between direct roots and transitively retained objects, but—again—the retention guarantee depends on the traversed DAG being complete for the intended semantics.

Primary source: https://docs.ipfs.tech/how-to/pin-files/

## Core decision

**Historical objects are immutable; dependency interpretation is versioned; newly discovered material dependencies are represented by authenticated additive repair records, never by rewriting the old object or silently applying a new schema to old bytes.**

Let:

- `O` be a content-addressed historical object;
- `S_k` be the dependency schema generation under which `O` was originally admitted;
- `D_k(O)` be the dependency edges derivable from `O` under `S_k`;
- `R_j` be an authenticated dependency-repair record;
- `D*(O, F)` be the effective dependency set for frontier `F`.

Then:

`D*(O, F) = D_k(O) ∪ authenticated_applicable_repairs(O, F)`

A later schema `S_m` MUST NOT retroactively redefine `D_k(O)` in place. It may define how new objects are encoded and may authorize a repair detector, but historical augmentation occurs only through explicit repair records.

## Dependency schema generations

Every consequential object type has a schema identity:

```text
DependencySchemaGeneration {
  schema_id
  predecessor_schema_id | GENESIS
  object_type
  decoder_digest
  dependency_extractor_digest
  edge_type_registry_digest
  canonicalization_digest
  applicability_range
  authority_policy_generation
  created_at_policy_time
}
```

Properties:

1. `schema_id` is content-addressed over the canonical record.
2. Predecessor continuity is authenticated and monotonic.
3. A schema generation is bound to one object type and explicit applicability range.
4. Decoder/extractor/canonicalizer versions are authority-relevant inputs, not ambient implementation details.
5. Schema downgrade is fail-closed for destructive GC.
6. Two different schema generations cannot both claim the same generation number/frontier identity without equivocation evidence.

## Historical dependency repair record

A missing dependency discovered later is published as an immutable repair object:

```text
DependencyRepairRecord {
  repair_id
  subject_object_id
  subject_original_schema_id
  discovered_under_schema_id
  repair_reason_code
  added_edges[]
  detector_toolchain_digest
  detector_input_frontier
  proof_bundle_digest
  blast_radius_selector_digest
  authority_policy_generation
  signer_set
}
```

Rules:

- repairs are additive only; they cannot delete or weaken an old dependency edge;
- every added edge is typed and content-addressed;
- the repair binds the exact historical object and the schema under which it was originally interpreted;
- repair reason is explicit (`OMITTED_EDGE`, `MISCLASSIFIED_EDGE_TYPE`, `CANONICALIZATION_ALIAS`, `DEPENDENCY_SCHEMA_BUG`, etc.);
- a repair cannot be self-authorized solely by the same buggy extractor it corrects;
- repairs are independently replayable from retained evidence or are marked `REPAIR_UNVERIFIABLE`, in which case affected objects remain rooted/fail-closed;
- conflicting authenticated repairs produce `REPAIR_DISAGREEMENT`, not majority/latest-wins resolution.

## No historical reinterpretation

The following are forbidden:

- `schema_v2` reading an old object and silently replacing the edge set that `schema_v1` historically committed;
- editing the historical object manifest so that an old GC proof appears to have traversed the new edge;
- changing an old GC epoch's root/live/dead set in place;
- treating the absence of an old dependency edge as proof that the dependency never mattered;
- deleting the repair record after a later schema happens to encode the dependency natively.

Historical GC proofs remain statements about what the collector knew at that epoch. Repairs create a new authenticated fact that may invalidate or require re-adjudication of those historical conclusions.

## Blast-radius derivation

A repair must determine which retained or deleted decisions could have depended on the omitted edge.

The blast radius includes at minimum:

1. the repaired subject object;
2. every authenticated root/verdict/checkpoint whose dependency closure reaches the subject;
3. every GC epoch that classified either the subject or newly added dependency as dead;
4. every snapshot/bootstrap/compaction proof that used those GC results;
5. every consequential verdict whose proof bundle depends on affected evidence availability;
6. every later repair whose correctness assumed the old incomplete closure.

Blast-radius discovery itself is proof-carrying. A repair record contains a selector/derivation definition, and the resulting revalidation set is committed in a canonical `RepairImpactManifest`.

If the graph/index necessary to prove a bounded blast radius is incomplete, the system MUST widen conservatively. `UNKNOWN` blast radius means retain/revalidate more; it never authorizes deletion.

## Revalidation state transition

Discovery of a material omitted dependency causes:

```text
VALID/ADMITTED
  -> REVALIDATION_REQUIRED
  -> {VALID_REPAIRED | INVALIDATED | QUARANTINED}
```

During `REVALIDATION_REQUIRED`:

- the repaired object is a GC root;
- every newly added dependency is a GC root;
- the computed affected closure is rooted;
- destructive GC cannot rely on historical mark proofs that predate the repair frontier for affected objects;
- archive deletion/compaction of affected evidence is suspended;
- consequential verdicts depending on the affected closure cannot silently retain authority without re-adjudication.

## Canonical mark proof

Every destructive GC epoch emits a `CompleteMarkProof`:

```text
CompleteMarkProof {
  gc_epoch_id
  graph_frontier
  schema_frontier
  repair_frontier
  trust_frontier
  root_set_commitment
  reachable_set_commitment
  traversed_edge_commitment
  unresolved_node_commitment
  root_count
  reachable_count
  traversed_edge_count
  traversal_algorithm_id
  canonical_worklist_order_id
  verifier_toolchain_digest
  deletion_candidate_commitment
  predelete_recheck_frontier
}
```

A proof is valid only if a second verifier can reconstruct the same root set and, for every marked node, reconstruct the complete effective outgoing edge set under the exact `(schema_frontier, repair_frontier)`.

### Proof-of-complete-mark semantics

A mark proof demonstrates more than `all observed edges were traversed`.

For each reachable object `O`, verifier must establish:

1. exactly one original dependency schema applies to `O`;
2. all authenticated applicable repairs through `repair_frontier` were loaded;
3. the effective edge multiset is canonical and complete under those inputs;
4. every effective outgoing edge was either traversed or classified through an explicit terminal rule that cannot hide a live dependency;
5. every reached child was itself processed under the same frozen frontiers;
6. no unresolved decoder/schema/repair state exists for a deletion-relevant node.

If any object is undecodable, has an unknown schema, has conflicting repairs, or depends on a repair frontier newer than the proof, then the mark proof is not deletion-authoritative for that object/closure.

## Mark completeness vs graph integrity

Two separate claims are required:

- **graph-integrity claim**: the effective outgoing edge set for each object is correct under its historical schema plus authenticated repairs;
- **mark-completeness claim**: traversal visited every edge in that effective graph from every live root.

A perfect traversal over an incomplete dependency graph is unsafe. A complete dependency graph with a buggy traversal is also unsafe. The proof bundle records and independently verifies both.

## Repair-edge cycles

Additive repairs may create cycles. Cycles are permitted but do not create liveness by themselves.

- liveness still originates only at authenticated roots;
- canonical traversal uses visited object IDs to terminate;
- a repair-created cycle with no path from any authenticated root remains dead;
- a cycle that contains or becomes reachable from a root is wholly live as dictated by its edges;
- cycle introduction must not allow an object to self-root through a repair record that itself depends only on the subject.

## Schema migration

For a new dependency schema generation:

1. authenticate `S_n -> S_n+1` continuity;
2. freeze old schema decoder/extractor required for historical verification;
3. run differential detection over retained historical objects whose old semantics may be affected;
4. emit explicit repair records for every discovered material difference rather than rewriting history;
5. publish a `SchemaMigrationCoverageManifest` committing scanned object ranges, exclusions, failures and detector toolchain;
6. unresolved scan gaps remain rooted / `REVALIDATION_REQUIRED`;
7. only after coverage and repair adjudication may the new schema frontier become GC-authoritative.

A migration that says merely `all old objects now use v2` is invalid.

## Concurrent revocation and schema migration

Revocation can widen the effective dependency closure while schema migration is in progress. The GC epoch therefore freezes both a schema/repair frontier and a trust/revocation frontier.

If a signer/verifier/toolchain revocation arrives before physical deletion:

- pre-delete recheck observes the newer trust frontier;
- affected proof bundles and their dependencies are re-rooted;
- the epoch aborts or recomputes candidates;
- a stale mark proof cannot authorize deletion after the revocation frontier advanced.

If revocation arrives after deletion, the deletion remains historical fact but the affected epoch moves to `POST_GC_REVALIDATION_REQUIRED`; archive/recovery obligations and incident evidence become roots.

## Repair disagreement

If independent verifiers disagree about whether an edge is material or about its canonical target:

- state becomes `REPAIR_DISAGREEMENT`;
- all candidate targets implicated by authenticated interpretations are retained;
- destructive GC over the affected closure is blocked;
- resolution requires a new authenticated adjudication record that references both interpretations and the policy/schema authority used to decide;
- do not majority-vote, latest-wins, or choose the smaller retained set.

## Supersession

A future schema may natively encode an edge previously supplied by repair. That does not make the old repair deletable automatically.

The repair remains needed to reproduce historical frontiers unless a separate authenticated subsumption proof demonstrates that every supported historical verification/recovery path can reproduce the same dependency fact from retained replacement evidence.

## Failure policy

Fail closed for destructive GC on:

- unknown historical schema;
- missing decoder/extractor required to reproduce historical dependency semantics;
- stale repair frontier;
- missing repair object referenced by a frontier;
- conflicting repair records;
- incomplete migration coverage;
- unresolved dependency target;
- stale mark proof after schema/repair/trust frontier advance;
- pre-delete root publication race;
- inability of an independent verifier to reproduce graph-integrity or mark-completeness claims.

## RED-first matrix — 80 cases

### A. Schema identity / continuity (1-8)
1. unknown schema id on reachable object -> fail closed;
2. schema downgrade -> reject;
3. skipped predecessor generation -> reject;
4. forked same-generation schema -> equivocation;
5. wrong object type applicability -> reject;
6. decoder digest mismatch -> reject;
7. extractor digest mismatch -> reject;
8. canonicalizer digest mismatch -> reject.

### B. Historical reinterpretation (9-16)
9. v2 silently adds edge to v1 object without repair -> reject;
10. v2 silently removes v1 edge -> reject;
11. old object manifest rewritten -> historical proof mismatch;
12. old GC proof rewritten -> reject;
13. historical object decoded only by latest schema -> reject;
14. applicability range overlap without adjudication -> reject;
15. applicability range gap -> retain/fail closed;
16. migrated object bytes differ but retain same object id -> reject.

### C. Repair authentication (17-24)
17. unsigned repair -> ignore for authority/fail closed;
18. wrong subject object -> reject;
19. wrong original schema binding -> reject;
20. repair deletes dependency -> reject;
21. repair weakens edge type -> reject;
22. repair proof bundle missing -> unverifiable/root;
23. repair authorized solely by compromised extractor -> quarantine;
24. conflicting repair targets -> disagreement/root both.

### D. Blast radius (25-32)
25. direct subject only but dependent verdict omitted -> detect incomplete impact;
26. affected GC epoch omitted -> fail impact proof;
27. affected snapshot omitted -> fail impact proof;
28. affected omission verdict omitted -> fail impact proof;
29. affected later repair omitted -> fail impact proof;
30. reverse index corrupt -> fall back to conservative scan/root;
31. unknown impact boundary -> widen, never delete;
32. bounded impact manifest reproducible by second verifier -> accept.

### E. Graph-integrity proof (33-40)
33. missing original schema -> fail;
34. missing applicable repair -> fail;
35. extra unauthenticated repair -> fail;
36. duplicate effective edge canonicalizes deterministically;
37. conflicting edge type -> fail;
38. unresolved target id -> fail;
39. corrupted target object -> fail;
40. same effective edge set independently reproduced -> pass graph-integrity subgate.

### F. Mark completeness (41-48)
41. root omitted from root commitment -> fail;
42. one outgoing edge skipped -> fail;
43. child marked but never processed -> fail;
44. worklist nondeterminism changes commitment -> fail;
45. repaired edge skipped -> fail;
46. cycle terminates via visited set without dropping external edge -> pass;
47. unrooted cycle does not become live -> pass;
48. independent verifier reconstructs exact reachable/traversed commitments -> pass mark subgate.

### G. Migration coverage (49-56)
49. retained object range unscanned -> revalidation required;
50. scan exclusion unauthenticated -> fail;
51. scanner crash gap -> fail closed;
52. scanner resumes with overlapping range -> deterministic dedupe/accounting;
53. discovered material difference without repair -> block frontier activation;
54. non-material difference explicitly adjudicated -> allowed;
55. migration tries global reinterpretation instead of repairs -> reject;
56. complete coverage manifest + all repairs adjudicated -> allow new GC-authoritative schema frontier.

### H. Revocation concurrency (57-64)
57. verifier revoked before mark starts -> excluded/root affected closure;
58. verifier revoked during mark -> epoch stale;
59. signer revoked after mark before delete -> pre-delete abort/recompute;
60. toolchain revoked after mark before delete -> abort/recompute;
61. repair authority revoked -> affected repairs revalidation required;
62. schema authority revoked -> affected schema closure revalidation required;
63. revocation after physical delete -> post-GC revalidation/incident roots;
64. stale mark proof replayed after trust frontier advance -> reject.

### I. Repair cycles / laundering (65-72)
65. self-edge repair cannot self-root;
66. A<->B repair cycle unrooted -> dead;
67. A<->B cycle reachable from root -> both live;
68. repair record depends only on subject and claims itself as authority -> reject;
69. repaired edge later encoded natively but repair removed without subsumption proof -> reject;
70. supersession proof omits historical verifier path -> reject;
71. repair archived but unavailable -> root/restore required;
72. dependency omission hidden by compacted old evidence -> fail historical verification.

### J. GC proof / recovery (73-80)
73. mark proof missing schema frontier -> reject;
74. mark proof missing repair frontier -> reject;
75. mark proof missing traversed-edge commitment -> reject;
76. deletion candidate became rooted after mark -> pre-delete recheck blocks;
77. archive manifest exists but repair cannot be retrieved -> no hot deletion;
78. second verifier disagrees on reachable set -> block deletion;
79. repaired historical omission proof remains reproducible after migration -> pass;
80. full epoch reproduced from frozen roots/schema/repair/trust frontiers with identical candidates -> eligible for destructive action.

## Integration consequences for LAB-093

When production work becomes executable, LAB-093's proof/evidence subsystem must not implement GC as a standalone latest-schema traversal. It must compose:

- authenticated schema generations;
- immutable historical object semantics;
- additive repair records;
- blast-radius/revalidation state;
- proof-carrying graph integrity;
- proof-of-complete-mark;
- trust/revocation frontiers;
- archive/recovery availability;
- pre-delete race recheck.

The design intentionally prefers over-retention to deletion under uncertainty.

## Exact next research question

Freeze **dependency-repair authority / materiality adjudication / semantic-edge taxonomy semantics**: define who may declare an omitted edge material, how edge classes affect liveness/recovery versus mere audit provenance, how to prevent an over-broad repair authority from pinning arbitrary data forever, and how an independent verifier distinguishes security-relevant dependency repair from harmless metadata/schema evolution without trusting the buggy producer.
