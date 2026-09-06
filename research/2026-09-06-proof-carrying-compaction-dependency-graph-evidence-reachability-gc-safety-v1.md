# Proof-carrying compaction dependency graph / evidence reachability / GC safety v1

Date: 2026-09-06
Status: `PROOF_CARRYING_COMPACTION_DEPENDENCY_GRAPH_EVIDENCE_REACHABILITY_GC_SAFETY_V1_FROZEN`
Scope: LAB-093 evidence/proof lifecycle follow-up. This is a design/evidence contract only; no production compactor, GC engine, snapshotter, or behavioral PASS is claimed.

## Problem

The previous bootstrap/compaction contract established that a late auditor may use an anchored snapshot instead of replaying from genesis, but compaction is safe only if it cannot remove the sole evidence needed to reproduce consequential historical decisions.

A simple retention rule such as "delete objects older than N days" is insufficient. A simple reachability rule such as "delete objects not referenced by the latest checkpoint" is also insufficient because:

1. a later revocation can make older signer/toolchain/proof objects relevant again;
2. an unresolved challenge or appeal can keep evidence live after the original verdict has aged out;
3. recovery can require the last known-good trust root, fork branch, or mapper checkpoint even when the current happy-path state no longer references it directly;
4. cyclic or self-asserted references can make arbitrary garbage appear live, while missing reverse dependencies can make required evidence appear dead;
5. concurrent publication and GC can race, producing a newly published verdict whose dependencies were just deleted;
6. an archive manifest is not evidence availability unless the archived objects are independently retrievable and integrity-verifiable;
7. a snapshot can be cryptographically valid while omitting historical fraud/equivocation/omission evidence that is still semantically required.

The required property is therefore **proof-carrying garbage collection**: every destructive pruning decision must itself be justified by an authenticated dependency graph, policy horizons, and a reproducible mark/sweep decision.

## Donor mechanisms

Primary donor mechanisms, adapted rather than copied:

- **Nix GC roots/reachability.** Nix treats objects reachable from configured roots as live and deletes only dead store paths. The useful mechanism is explicit roots + transitive reachability, not Nix's package-specific semantics. Source: Nix package-manager GC documentation, `nix-store --gc` / GC roots, https://nixos.org/ .
- **Git object reachability/prune.** Git pruning preserves objects reachable from refs (and optional supplied heads) and deletes unreachable objects only after an expiry horizon. The useful mechanism is mark-from-authoritative-roots + grace period, not Git's repository object model. Source: `git-prune` documentation, https://git-scm.com/docs/git-prune .
- **TUF monotonic trusted metadata.** TUF clients reject rollback/freeze and retain trusted root/version state; recovery after compromise can invalidate previously cached timestamp/snapshot state. The useful mechanism is that future trust changes can reactivate historical dependencies and that "latest" is not sufficient authority. Source: TUF specification v1.0.26, https://theupdateframework.github.io/specification/v1.0.26/ .
- **Sigstore/Rekor transparency evidence.** Rekor entries and inclusion/consistency evidence are intended for durable independent verification and monitoring. The useful mechanism is immutable evidence + externally verifiable inclusion rather than trusting a local cache. Sources: https://docs.sigstore.dev/logging/overview/ and https://docs.sigstore.dev/logging/cli/ .

No donor above directly solves LAB's semantic-evidence retention problem; the LAB contract adds consequential-verdict roots, revocation/appeal horizons, derivation edges, archive availability, and recovery-specific roots.

## Core model

Every durable proof/evidence object has a content address:

`object_id = H(type_tag || canonical_payload)`

The graph is directed from a **consumer** to every object required to verify that consumer:

`consumer -> dependency`

Examples:

- compatibility verdict -> proof bundle;
- proof bundle -> fixtures, mutants, oracle artifacts, toolchain descriptors, source/target model generations, policy generation;
- adjudication -> producer verdict, independent verifier verdict, trust-root generation, signer capability generation;
- monitor verdict -> checkpoint, witness set, observation receipts, publication promises, challenge transcript;
- omission verdict -> promise, eligible post-deadline frontier, subject-index/non-inclusion proof, mapper derivation proof;
- mapper checkpoint -> source-log frontier, disposition commitment, previous mapper checkpoint, target map root;
- snapshot -> mapper checkpoint, source-log checkpoint, trust-frontier checkpoint, retained-evidence manifest;
- trust-frontier checkpoint -> prior checkpoint / consistency proof / witness policy generation;
- recovery decision -> last-known-good checkpoint, fork/equivocation evidence, revocation record, corrected lineage.

Edges are typed. At minimum:

- `VERIFY_REQUIRES`
- `AUTHORITY_REQUIRES`
- `ANCESTRY_REQUIRES`
- `RECOVERY_REQUIRES`
- `CHALLENGE_REQUIRES`
- `REVOCATION_REVALIDATES`
- `ARCHIVE_LOCATES`
- `SUPERSEDES_WITH_PROOF`

An untyped arbitrary reference is not retention authority.

## Authoritative root set

The live root set is not merely "latest checkpoint". At GC epoch `E`, the authoritative roots are the union of:

1. current admitted trust-frontier checkpoints;
2. current consequential PASS/FAIL/REVALIDATION_REQUIRED verdicts that policy requires to remain reproducible;
3. unresolved challenges, appeals, investigations, fork/equivocation/omission cases;
4. all active revocations/quarantines plus their blast-radius revalidation sets;
5. recovery anchors: last-known-good checkpoints and branch/fork evidence required by the recovery protocol;
6. current snapshot/bootstrap anchors used by admitted late auditors;
7. legal/commercial/user-retention holds explicitly represented as authenticated policy objects, if such a product policy exists;
8. grace roots created by publication/GC concurrency protocol;
9. retained historical roots required until their policy horizon has elapsed and no reactivation condition remains.

A root must be authenticated by the policy generation that grants it root status. A self-authored evidence object cannot declare itself a GC root.

## Reachability rule

Let `R_E` be the authenticated roots at GC epoch E and `G_E` the authenticated dependency graph.

`LIVE_E = transitive_closure(R_E, allowed_dependency_edges)`

An object is a prune candidate only if all of the following are true:

1. it is not in `LIVE_E`;
2. it is older than its type-specific minimum retention/grace horizon;
3. no unresolved challenge/appeal/revocation/recovery hold references or can deterministically reactivate it under the current policy;
4. its absence will not make any retained object unverifiable under the supported verifier set;
5. if archived instead of deleted, archive availability and integrity have been independently verified after upload and before local deletion;
6. the GC epoch is closed against concurrent publication as defined below;
7. the pruning decision has an authenticated GC manifest that records the root set, graph generation, policy generation, mark result, candidate set and final deleted/archived object IDs.

Unknown graph state is fail-closed: `UNKNOWN != DEAD`.

## Reverse dependency index is optimization, not authority

A reverse index (`dependency -> consumers`) may accelerate impact analysis but cannot be the sole source of truth. It is derived from authenticated forward edges and must be reproducible. Corrupt/deleted reverse-index rows must not cause live evidence to be pruned.

## No self-asserted liveness laundering

A malicious or buggy object could otherwise create a cycle:

`A -> B -> A`

and claim both are live forever. Reachability begins only at authenticated roots. Cycles entirely outside the root closure remain dead. Conversely, cycles inside the root closure remain live because a genuine root reaches them.

An object cannot become a root merely because another unrooted object references it.

## Dependency completeness

Every consequential object type has a versioned **dependency schema** declaring the complete set of authority/proof dependencies that must be extracted from its canonical payload.

Admission requires:

1. payload parses under the exact schema generation;
2. extracted dependency set equals the dependency commitment carried by the object;
3. every required dependency exists or is represented by an admitted archive locator plus integrity/availability evidence;
4. no verifier is allowed to discover an undeclared authority dependency at runtime and silently fetch it from ambient state.

If a later verifier generation discovers that schema vN omitted a material dependency, affected historical objects become `REVALIDATION_REQUIRED`, and the newly discovered dependency is added through an authenticated repair/revalidation record. GC must treat the blast radius as live until revalidation completes.

## Horizons and delayed reactivation

Age alone never proves irrelevance. Each object type has a policy-defined horizon with explicit start condition, for example:

- challenge horizon starts only after authenticated publication of the verdict and proof bundle;
- appeal horizon starts only after challenge closure;
- revocation revalidation horizon starts only after all affected verdicts are re-adjudicated under non-revoked authority;
- fork/recovery evidence has no ordinary time-based expiry while any admitted descendant relies on the recovered lineage;
- fraud/equivocation evidence is non-prunable unless a higher-level retention policy explicitly proves no supported verification/recovery path can depend on it.

A later revocation can reactivate dependencies that were previously outside the ordinary challenge window. Therefore the system must retain either the original proof objects or an independently sufficient canonical archival proof package through the maximum revocation/recovery horizon.

## Supersession is not deletion authority

`new_object SUPERSEDES old_object` does not by itself permit pruning `old_object`.

Pruning through supersession requires a **subsumption proof** showing that every supported verification/recovery query answerable from the old object can be answered from the new object plus retained dependencies, with identical or stricter authority semantics.

Examples that are not automatically safe:

- replacing a full proof bundle with only its PASS verdict;
- replacing raw challenge transcripts with a summary hash;
- replacing a historical trust root with the current root;
- replacing two fork branches with the winning branch only;
- replacing mapper source coverage evidence with only the derived map root.

## Archive semantics

Archive relocation is a two-phase state transition:

1. write object to archive under its content address;
2. publish authenticated archive manifest binding object ID, byte length, digest, archive generation/location capability, and retention policy;
3. independently fetch the object through the supported archive path and verify bytes/content address;
4. only then may local hot-store deletion become eligible.

An archive locator that points to an unavailable object does not satisfy reachability. Periodic archive scrubbing samples or fully verifies retained objects according to policy. Archive loss reactivates restoration/re-replication work and can place dependent verdicts into `REVALIDATION_REQUIRED` if no surviving complete copy exists.

## Concurrent publication and GC

GC uses explicit epochs.

Protocol:

1. acquire/establish a durable `gc_epoch_start` frontier;
2. snapshot authenticated roots and graph generation at that frontier;
3. publication after that frontier must either:
   - write all dependencies before publishing the consumer and register a `POST_EPOCH_GRACE_ROOT`, or
   - wait for the GC epoch to close;
4. mark live objects from the epoch root set plus grace roots;
5. produce candidate deletion manifest;
6. re-check no candidate became reachable from a root/grace publication before delete;
7. atomically publish `gc_epoch_commit` with actual deleted/archived IDs.

A crash before the commit leaves objects undeleted or requires idempotent reconciliation from the manifest. A crash after some deletions but before commit must be detectable and must not be normalized as a clean epoch.

## State-loss recovery

The GC ledger/manifest is itself evidence. Recovery after local state loss requires:

- last admitted GC epoch commit;
- its root-set commitment;
- dependency-graph generation;
- actual deleted/archive manifests;
- archive integrity/availability state;
- trust-frontier ancestry to the current epoch.

If the system cannot prove what was deleted and why, it cannot claim historical evidence completeness. Recovery must fail closed or downgrade affected historical verdicts to `REVALIDATION_REQUIRED`.

## Revocation blast-radius reactivation

When signer/verifier/toolchain/policy generation X is revoked or quarantined:

1. compute all consequential objects whose verification dependency closure reaches X;
2. mark those objects `REVALIDATION_REQUIRED`;
3. add their complete old proof closures as temporary GC roots;
4. re-adjudicate under admitted non-revoked authority;
5. only after every required revalidation closes may old dependencies become GC candidates under normal horizons.

This prevents a sequence where old evidence is pruned first and only later a compromise is discovered.

## Omission/fraud/equivocation evidence

The following are presumptively long-lived roots or dependencies:

- proven equivocation pairs / split-view checkpoints;
- proven omission transcripts;
- skipped-leaf/duplicate-position mapper fraud proofs;
- revoked signer/toolchain evidence needed to establish the blast radius;
- last common checkpoint for a recovered fork;
- challenge transcripts that changed a consequential verdict.

A summarized verdict is not sufficient replacement unless a subsumption proof establishes future independent reproducibility.

## GC verdict states

For each candidate object:

- `LIVE_REACHABLE`
- `LIVE_HORIZON`
- `LIVE_CHALLENGE`
- `LIVE_REVOCATION`
- `LIVE_RECOVERY`
- `LIVE_GRACE`
- `ARCHIVE_PENDING`
- `ARCHIVE_VERIFIED`
- `PRUNE_ELIGIBLE`
- `PRUNE_BLOCKED_UNKNOWN`
- `PRUNED`

Only `PRUNE_ELIGIBLE` may transition to `PRUNED`.

## Canonical GC proof bundle

Every destructive GC epoch emits a reproducible bundle containing:

- `gc_epoch_id` and parent epoch;
- exact policy generation;
- trust-frontier checkpoint;
- dependency-schema generations;
- root-set commitment and root objects;
- graph commitment;
- mark algorithm/version and deterministic traversal order;
- live-set commitment;
- candidate-set commitment;
- horizon calculations and clock evidence;
- archive manifests and post-upload verification receipts;
- pre-delete recheck frontier;
- actual deleted object IDs;
- post-GC store/root commitment;
- signer/adjudicator identity and authorization evidence.

A second verifier must be able to recompute whether every deleted object was unreachable and horizon-eligible using only the bundle plus admitted archived dependencies.

## Determinism

Traversal/order must not affect semantics. Canonical ordering is by object ID bytes. Set commitments are canonical sorted Merkle/sequence commitments with algorithm/version pinned. Wall-clock decisions consume authenticated policy time evidence; local clock drift alone cannot shorten retention.

## 80-case RED-first matrix

### A. Root authority / basic reachability (1-10)
1. latest admitted consequential verdict keeps its proof bundle live;
2. proof bundle keeps fixture/oracle/toolchain dependencies live;
3. unrooted old object becomes candidate after horizon;
4. self-declared root is rejected;
5. unrooted A<->B cycle remains dead;
6. rooted A<->B cycle remains live;
7. missing root authentication fails closed;
8. stale policy generation cannot remove a current root;
9. current snapshot anchor keeps retained bootstrap dependencies live;
10. last-known-good recovery checkpoint remains live after newer checkpoint publication.

### B. Dependency completeness / graph integrity (11-20)
11. missing declared dependency blocks admission/GC;
12. dependency commitment mismatch blocks admission;
13. undeclared material authority dependency discovered later triggers revalidation;
14. corrupt reverse index cannot prune forward-reachable evidence;
15. duplicate graph edges are canonicalized without changing liveness;
16. wrong edge type cannot grant root authority;
17. schema-generation downgrade cannot hide a dependency;
18. dependency parser disagreement yields `PRUNE_BLOCKED_UNKNOWN`;
19. ambient runtime fetch not declared in payload is forbidden for reproducible verification;
20. graph object with invalid content address is rejected.

### C. Horizons / challenge / appeal (21-30)
21. object younger than grace horizon is live despite unreachability;
22. challenge opens immediately before ordinary horizon expiry and prevents prune;
23. appeal keeps challenge transcript live after initial verdict closure;
24. horizon starts at authenticated publication, not local file creation;
25. local clock forward-jump cannot shorten horizon;
26. stale/expired time authority fails closed;
27. closed challenge with all other dependencies dead eventually permits prune;
28. unresolved challenge dependency omitted from latest snapshot remains live;
29. policy change may extend but cannot retroactively shorten already-promised retention without explicit migration authority;
30. verdict publication missing proof-bundle publication leaves state incomplete, not pruneable.

### D. Revocation / reactivation (31-40)
31. signer revocation reactivates all dependent historical proof closures;
32. toolchain common-mode defect reactivates affected proofs;
33. oracle generation revocation affects only reachable blast radius;
34. previously GC-eligible object becomes live before deletion when revocation arrives;
35. revocation arriving after archive relocation requires archive copy to remain available;
36. revalidation under new authority closes temporary root only after durable adjudication;
37. partial revalidation keeps unresolved descendants rooted;
38. revoked root cannot authorize GC that deletes its own compromise evidence;
39. corrected verifier generation does not "unrevoke" old generation;
40. historical compromise discovered after ordinary challenge window still has sufficient retained/archive proof package.

### E. Archive safety (41-50)
41. upload without authenticated manifest cannot permit hot deletion;
42. manifest without independent post-upload fetch cannot permit hot deletion;
43. archive bytes with digest mismatch block deletion;
44. archive locator disappearing after deletion triggers availability incident/revalidation;
45. replicated archive with one lost replica remains valid only if policy quorum remains;
46. archive generation rollback is rejected;
47. archive manifest cannot self-assert object existence without retrieval proof;
48. archive object retrieval yields exact content address and supported verifier can use it;
49. archive migration preserves object IDs and manifest ancestry;
50. fraud/equivocation evidence cannot be silently demoted to lower-retention archive class.

### F. Supersession / compaction semantics (51-60)
51. PASS summary cannot supersede full proof bundle by assertion alone;
52. newer snapshot cannot erase fork losing-branch evidence;
53. mapper root cannot supersede source coverage/disposition proof without subsumption proof;
54. trust-root rotation cannot delete prior root required to verify transition;
55. canonical compressed proof package may supersede raw objects only after equivalence/subsumption verification;
56. failed subsumption proof keeps old objects live;
57. supersession chain with cycle is rejected as deletion authority;
58. newer schema cannot reinterpret old dependencies while claiming supersession;
59. compaction that drops only redundant duplicate bytes but preserves content-addressed proof semantics is allowed;
60. decompression/reconstruction of retained compact proof reproduces exact canonical dependencies.

### G. Publication/GC concurrency (61-70)
61. consumer published after epoch start receives grace root;
62. dependency published before consumer cannot be deleted between the two durable steps;
63. consumer published with missing dependency fails admission rather than racing GC;
64. candidate becomes reachable before delete and pre-delete recheck cancels prune;
65. crash after mark before delete is harmless/idempotent;
66. crash after partial deletion before epoch commit is detected on recovery;
67. two concurrent GC epochs cannot both mutate store from the same parent without conflict detection;
68. publication cannot reference an object already committed PRUNED;
69. archive relocation concurrent with GC resolves to one durable state transition;
70. deterministic re-run of same closed epoch yields same candidate/live commitments.

### H. Recovery / omission / historical integrity (71-80)
71. loss of local GC DB with retained authenticated epoch manifests reconstructs deletion history;
72. missing GC manifest downgrades affected historical completeness;
73. skipped-leaf fraud proof remains reproducible after unrelated compaction;
74. `OMISSION_PROVEN` remains independently reproducible after hot-store compaction;
75. fork recovery retains last common checkpoint plus both conflicting branches;
76. recovered lineage cannot authorize deletion of evidence proving the earlier fork until recovery policy allows it;
77. late auditor bootstrapped from snapshot can retrieve every dependency required by its assurance class;
78. orphaned trust root discovered during recovery blocks GC rather than being deleted as apparently unreachable;
79. archive-only newer checkpoint reactivates dependencies even when online store is stale;
80. full disaster recovery reproduces current root set, live-set commitment, archive inventory and all consequential historical verdict dependencies.

## Implementation direction

When executable source is available, implement tests first. Keep the compactor separate from the authority/proof producers: it consumes authenticated objects and dependency schemas but must not infer semantic dependencies from mutable runtime internals.

Preferred minimal architecture:

1. content-addressed evidence store;
2. canonical typed dependency manifests emitted at object admission;
3. authenticated root registry;
4. deterministic mark engine;
5. horizon/hold evaluator;
6. two-phase archive mover;
7. epoch-based sweep with pre-delete reachability recheck;
8. canonical GC proof bundle + independent verifier;
9. revocation blast-radius query over forward dependency graph;
10. recovery tool that reconstructs live state from GC manifests and archives.

## Security boundaries

- GC is destructive authority and must be least-privilege; it cannot mint trust roots, alter proof semantics, or modify evidence objects.
- A signed GC decision is not automatically correct; independent reproducibility is required.
- Storage pressure is not authority to shorten challenge/revocation/recovery horizons.
- Absence after GC is never treated as evidence that an object never existed.
- No production omission/non-inclusion verdict may depend on evidence that the GC policy is permitted to destroy before that verdict's full reproducibility horizon closes.

## Verdict

`PROOF_CARRYING_COMPACTION_DEPENDENCY_GRAPH_EVIDENCE_REACHABILITY_GC_SAFETY_V1_FROZEN`

This contract is ready to compose into LAB-093's eventual executable proof/evidence subsystem. Production RED/GREEN remains pending exact executable source and integration gates.