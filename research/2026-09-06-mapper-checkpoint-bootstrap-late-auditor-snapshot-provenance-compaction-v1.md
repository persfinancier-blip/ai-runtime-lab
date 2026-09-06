# Mapper checkpoint bootstrap / late-joining auditor / snapshot provenance and compaction — v1 frozen

Status: `MAPPER_CHECKPOINT_BOOTSTRAP_LATE_AUDITOR_SNAPSHOT_PROVENANCE_COMPACTION_V1_FROZEN`

Date: 2026-09-06

Scope: LAB-093 trust-frontier / mapper-completeness follow-up. Design and RED contract only; no production snapshotter, auditor bootstrap implementation, compactor, or behavioral PASS is claimed.

## Problem

The mapper-completeness contract requires every authenticated source-log position to receive exactly one committed disposition and requires the derived-map transition to be independently reproducible. A new auditor can always obtain maximum assurance by replaying the source log from genesis, but that becomes operationally expensive as history grows.

A naive shortcut is unsafe: accepting a recent signed `(source_root, map_root)` snapshot can launder an earlier skipped leaf, duplicated position, misclassification, invalid omission verdict, or fork. Cryptographic validity of the current roots proves only the committed current state; it does not prove that the path used to reach them satisfied historical mapper obligations.

This contract defines when a late-joining independent verifier may bootstrap from a later checkpoint without replaying genesis, and what history/evidence must remain after compaction so earlier fraud remains detectable and historical omission proofs remain reproducible.

## Primary donor mechanisms

### RFC 9162 Certificate Transparency

RFC 9162 gives the base ancestry primitive: a client holding an older signed tree head can verify a consistency proof to a newer tree head, while monitors may either retain all entries or verify new entries plus consistency material. The important donor rule is that a newer signed root alone is insufficient; reachability from a previously trusted root must be proven.

Reference: https://www.rfc-editor.org/rfc/rfc9162.html

### Transparency-dev compact ranges

Compact ranges provide mergeable commitments to contiguous Merkle ranges. `[0,N)` is a succinct commitment to the whole tree and adjacent ranges can be merged efficiently. They are useful for pruning full interior tree material while retaining independently verifiable commitments and append-only continuation evidence.

Reference: https://github.com/transparency-dev/merkle/blob/main/docs/compact_ranges.md

### IETF Key Transparency

The current Key Transparency work explicitly depends on retained prior state: users unable to maintain long-term state have weaker ability to detect operator misbehavior, and offline/partitioned clients need an independent continuity channel or auditor. This is a direct warning against treating a freshly downloaded snapshot as equivalent to retained trust history.

Reference: https://www.ietf.org/archive/id/draft-ietf-keytrans-protocol-03.html

### Trillian

Trillian separates append-only log semantics from application personalities and exposes signed roots, range reads, inclusion proofs and consistency proofs. It is a donor for independently reconstructible checkpoints, but snapshot authority remains an application-level policy decision.

Reference: https://github.com/google/trillian

## Frozen decisions

### 1. Bootstrap is a trust transition, not a storage optimization

A snapshot may reduce replay cost but cannot create authority from nothing. A late auditor must begin from one of:

- a previously retained locally trusted checkpoint/frontier;
- a policy-approved authenticated trust-root checkpoint distributed out of band;
- a threshold/witness-adjudicated checkpoint whose admission policy explicitly permits bootstrap for that auditor generation.

Downloading the latest mapper snapshot from the mapper itself is not an independent bootstrap.

### 2. Bootstrap checkpoint is content-addressed and self-describing

A `MapperBootstrapCheckpoint` binds at least:

- checkpoint generation and digest;
- predecessor authoritative mapper checkpoint digest;
- source-log checkpoint `{size, root, identity}`;
- derived-map `{revision, root}`;
- coverage/disposition commitment through the source frontier;
- mapper/schema/canonicalizer/policy/hash generations;
- trust-frontier checkpoint and witness/adjudicator set used for admission;
- snapshot manifest digest;
- retained-evidence manifest digest;
- compaction generation/policy;
- creation time source and freshness policy.

Unversioned or partially specified snapshots are not authority-bearing.

### 3. A late auditor must prove ancestry from an admissible anchor

If the auditor retains checkpoint `A` and bootstraps to checkpoint `B`, it must verify:

- source-log append-only consistency `A.source -> B.source`;
- mapper-checkpoint lineage continuity from `A` to `B`, directly or through an authenticated checkpoint chain/accumulator;
- derived-map transition continuity under the admitted mapper generations;
- trust-frontier continuity and no revocation/fraud record invalidating an intermediate checkpoint;
- snapshot manifest equality to the checkpoint commitment.

A valid root at `B` with unknown ancestry is `UNANCHORED_SNAPSHOT`, not PASS.

### 4. Snapshot state must be reproducibly committed

The snapshot contains or references enough canonical state to recompute its committed roots. File names, compression framing, database page layout, serializer map ordering, filesystem timestamps, and implementation-specific cache state are not semantic inputs unless explicitly committed by generation.

A verifier may reconstruct the semantic snapshot into a different physical layout and must obtain the same domain-separated state commitments.

### 5. Snapshot provenance includes the derivation frontier

The snapshot proves exactly which source positions are reflected in state. `source_size=N` is authority only if the accompanying mapper checkpoint has already satisfied coverage + execution obligations through N.

A snapshotter cannot take an unverified mapper state and upgrade it into verified state by signing a manifest.

### 6. Compaction cannot delete the only evidence required to challenge old authority

Before pruning, the compactor classifies retained material by proof role. At minimum it preserves authenticated commitments sufficient to reproduce or independently verify:

- source-log ancestry/consistency across retained anchor boundaries;
- mapper checkpoint ancestry;
- coverage/disposition commitments for compacted intervals;
- admitted fraud/equivocation/revocation evidence;
- publication promises and receipts still inside challenge/appeal windows;
- historical `OMISSION_PROVEN` evidence bundles;
- trust-root/witness/adjudicator generations needed to verify retained signatures;
- schema/canonicalizer/policy/toolchain identities needed to interpret retained proofs.

If no compact proof can preserve one of these properties, the underlying evidence remains unpruned.

### 7. Fraud evidence is non-compactable by ordinary retention policy

Once a skipped-leaf, duplicate-position, wrong-effect, equivocation, or proven-omission record is admitted, ordinary snapshot compaction may not remove the evidence needed to verify that finding or make an affected checkpoint appear clean.

Fraud evidence may move to archival storage, but its authenticated digest, location/availability policy, verification metadata and trust-frontier status remain committed in the active retained-evidence manifest.

### 8. Historical omission verdicts remain reproducible

If an earlier `OMISSION_PROVEN` verdict depended on a publication promise, post-deadline frontier, non-inclusion proof, mapper coverage proof and adjudication bundle, compaction must preserve that complete logical proof bundle or a policy-approved cryptographic compression that independently entails the same proposition.

Keeping only the final verdict bit or a signer assertion is insufficient.

### 9. Snapshot-to-source binding is two-way

The bootstrap bundle must prove both:

- the snapshot map root is the state produced by the admitted mapper checkpoint; and
- the mapper checkpoint covers the exact authenticated source frontier claimed by the snapshot.

A matching map root alone cannot hide a skipped source leaf whose semantic effect happened to be neutral.

### 10. Late auditor bootstrap has explicit assurance classes

- `GENESIS_REPLAYED`: verifier independently replayed all source history.
- `ANCHORED_REPLAY`: verifier retained anchor A and replayed all transitions after A.
- `ANCHORED_SNAPSHOT`: verifier retained/admitted A, verified continuity to B, verified B snapshot/proof manifests, then continues from B.
- `THRESHOLD_BOOTSTRAP`: no local A, but policy explicitly authorizes an independently witnessed bootstrap root.
- `UNANCHORED_SNAPSHOT`: informational only; never consequential authority.

Applications may require stronger classes for high-consequence decisions.

### 11. Compaction checkpoints are monotonic

A compaction event is itself append-only authority evidence and binds:

- previous retention manifest;
- exact newly retained anchors;
- exact pruned ranges/material classes;
- replacement compact commitments;
- archive destinations/digests if used;
- proof that all mandatory evidence classes remain verifiable;
- authorizing policy/trust-frontier generation.

Rollback to an older retention manifest cannot restore authority to evidence/checkpoints already revoked or superseded.

### 12. Archive availability is distinct from archive authenticity

A digest proves integrity of recovered archive bytes; it does not prove those bytes remain obtainable. Consequential reliance on archival evidence therefore requires an availability policy: e.g. multiple independent replicas, periodic retrieval audits, erasure coding, or another explicitly accepted mechanism.

If required evidence becomes unavailable, dependent historical verdicts become `EVIDENCE_UNAVAILABLE` / `REVALIDATION_REQUIRED`; they do not silently remain fully authoritative.

### 13. Pruned source leaves need boundary commitments

When source leaves below position K are pruned from hot storage, the system retains enough authenticated Merkle boundary/compact-range material to prove that the retained source suffix continues the same append-only tree and that the bootstrap source checkpoint is exactly the committed prefix.

A fresh tree rebuilt only from suffix leaves is not equivalent to the original log.

### 14. Snapshot generation migration cannot reinterpret old history

Changing snapshot encoding, mapper schema, canonicalizer, hash algorithm, compaction policy or proof format creates a new generation. Migration binds old checkpoint/root to new representation and requires independent equivalence or replay evidence appropriate to the change.

A new serializer cannot re-encode historical state and silently claim the old commitment.

### 15. Compaction is blocked by unresolved challenge windows

Evidence supporting outstanding publication promises, omission challenges, appeals, fraud investigations, or equivocation disputes cannot be pruned merely because a scheduled retention deadline arrived.

Retention deadline is subordinate to unresolved proof obligations.

### 16. Recovery from bad snapshot preserves the bad snapshot

If a late auditor discovers that an admitted snapshot omitted evidence or derived from a fraudulent checkpoint:

- snapshot becomes `SNAPSHOT_INVALID`;
- descendants enter revalidation according to dependency;
- bad manifest and fraud evidence remain retained;
- recovery starts from last known-good anchor or full replay;
- corrected snapshot forms a new lineage rather than overwriting the bad one.

## Minimum bootstrap bundle

A consequential `ANCHORED_SNAPSHOT` bundle contains:

```text
bootstrap_checkpoint
admission_anchor
source_consistency_proof_or_compact_range_bridge
mapper_lineage_proof
trust_frontier_continuity_proof
snapshot_manifest
snapshot_semantic_state_or_retrievable_chunks
coverage_disposition_commitment
execution_proof_or_admitted_auditor_attestation
retained_evidence_manifest
fraud_revocation_equivocation_frontier
historical_omission_bundle_index
schema_policy_toolchain_generation_manifest
archive_availability_evidence_if_required
```

Every referenced object is content-addressed. Missing mandatory objects fail closed.

## 80-case RED-first matrix

### A. Anchor and ancestry (1-10)
1. latest signed snapshot with no prior/admitted anchor => reject authority;
2. retained A + valid source consistency to B => source ancestry passes;
3. source consistency valid but mapper lineage gap => reject;
4. mapper lineage valid but trust-frontier rollback => reject;
5. predecessor digest mismatch => reject;
6. forked child checkpoints without recovery transition => equivocation;
7. threshold-bootstrap below configured quorum => reject;
8. revoked witness counted in bootstrap quorum => reject;
9. anchor from wrong logical deployment/database identity => reject;
10. complete anchored continuity => bootstrap may proceed.

### B. Snapshot manifest/state (11-20)
11. snapshot manifest digest mismatch => reject;
12. semantic state recomputes wrong map root => reject;
13. same semantic state in different physical DB layout => accept if canonical commitment matches;
14. noncanonical map ordering changes commitment => reject generation bug;
15. snapshot claims source N but mapper checkpoint covers N-1 => reject;
16. snapshotter signature valid over unverified mapper state => reject;
17. required schema generation missing => reject;
18. hash/domain generation mismatch => reject;
19. truncated chunk with matching outer filename only => reject;
20. complete canonical snapshot recomputes committed state => pass state stage.

### C. Coverage / skipped-leaf laundering (21-30)
21. historical skipped leaf before snapshot with no retained fraud evidence => bootstrap policy fails;
22. skipped leaf has neutral final state effect but missing disposition => still invalid;
23. duplicate source position hidden before snapshot => invalid;
24. wrong-effect transition later canceled by another event => historical fraud still invalid;
25. coverage commitment retained and independently verifies interval => pass coverage stage;
26. only map root retained, no coverage commitment => insufficient;
27. mapper generation needed to interpret coverage was pruned => reject;
28. full replay from anchor detects compacted misclassification => snapshot invalid;
29. compact proof and full replay disagree => adjudication disagreement;
30. fraud record predating snapshot remains visible after bootstrap => required.

### D. Compaction safety (31-40)
31. prune all leaves before K but retain no prefix commitment => reject;
32. retain `[0,K)` compact commitment + valid suffix continuation => acceptable source compaction primitive;
33. prune only copy of mapper checkpoint chain segment => reject;
34. replace chain segment with authenticated accumulator/proof accepted by policy => may pass;
35. prune only copy of schema/canonicalizer generation => reject;
36. ordinary retention attempts to delete admitted fraud proof => reject;
37. unresolved challenge evidence selected for pruning => reject;
38. compaction manifest has gap in pruned ranges => reject;
39. rollback to pre-fraud retention manifest => reject;
40. monotonic compaction checkpoint with complete replacement commitments => pass retention stage.

### E. Historical omission reproducibility (41-50)
41. keep `OMISSION_PROVEN` bit but delete promise => insufficient;
42. keep promise but delete eligible post-deadline checkpoint => insufficient;
43. keep non-inclusion proof but delete mapper completeness evidence => insufficient;
44. delete adjudicator identity/trust generation => verification blocked;
45. compact logical bundle into content-addressed proof archive with active manifest => acceptable;
46. archive bytes recovered but digest mismatch => reject;
47. archive authentic but unavailable across required availability threshold => degrade authority;
48. expired challenge window permits policy-approved evidence reduction only if proposition remains independently verifiable;
49. historical omission proof verifies after late bootstrap => pass;
50. snapshot cannot be authoritative if it erases proof that earlier omission verdict was later revoked.

### F. Archive and availability (51-60)
51. one archive replica disappears, policy requires 2-of-3 and two remain => availability passes;
52. all archives unavailable => dependent evidence unavailable;
53. mirror returns stale but authentic archive manifest => do not treat as current availability proof;
54. forged retrieval heartbeat => reject;
55. archive object relocated with same digest and authenticated manifest update => accept;
56. archive encryption key lost => evidence unavailable even if ciphertext exists;
57. archive decryption key rotation preserves reproducible plaintext digest => accept if policy-authorized;
58. archive provider controls all nominally independent replicas => collapse availability domain;
59. periodic retrieval audit not fresh enough => degrade per policy;
60. hot-storage deletion only after archive availability commit becomes authoritative.

### G. Late/offline auditor behavior (61-70)
61. auditor offline longer than retention horizon returns with only stale local A; valid continuity bridge available => catch-up allowed;
62. service supplies only latest B, no bridge from A => fail closed;
63. auditor loses all local state and policy forbids threshold bootstrap => no consequential authority;
64. auditor loses local state but has authenticated external anchor backup => resume from backup;
65. two independent bootstrap channels disagree on B => fork/disagreement;
66. newer archived checkpoint exists than online served checkpoint => omission/staleness handling, not silent downgrade;
67. auditor verifies snapshot but not retained fraud frontier => incomplete bootstrap;
68. auditor accepts stale revoked trust root => reject;
69. auditor continues with new source leaves after successful B bootstrap => normal anchored continuation;
70. later full replay contradicts prior snapshot => snapshot lineage revalidation required.

### H. Migration / recovery / composition (71-80)
71. snapshot format v1->v2 with no equivalence proof => reject migration;
72. hash algorithm migration without dual-boundary transition => reject;
73. canonicalizer migration reinterprets old source positions => reject;
74. corrected snapshot overwrites bad snapshot identity => reject;
75. corrected snapshot references last known-good anchor + fraud evidence => valid recovery shape;
76. child checkpoints of invalid snapshot remain PASS without revalidation => reject;
77. compaction occurs concurrently with unresolved mapper checkpoint publication => serialize/fail closed;
78. trust-frontier revocation lands during bootstrap => re-evaluate admission before commit;
79. bootstrap transaction crashes after local snapshot install but before durable anchor state => restart treats local install as untrusted staging;
80. full composition preserves source ancestry, mapper completeness, trust frontier, fraud evidence and omission-proof reproducibility => eligible for GREEN implementation.

## Implementation order when exact execution is available

1. Write the 80 RED cases against an isolated snapshot/bootstrap verifier before introducing compaction.
2. Implement canonical bootstrap/checkpoint/retained-evidence manifests.
3. Implement anchored continuity verification using existing source/mapper/trust-frontier proof objects.
4. Add semantic snapshot root recomputation.
5. Add compaction planner that refuses to prune evidence classes without a replacement proof.
6. Add archive availability policy separately from authenticity verification.
7. Add crash/restart and concurrent compaction/publication regressions.
8. Compose with publication-promise, non-inclusion, mapper-completeness, adjudicator trust-root and split-view contracts.

## Decision

Freeze `MAPPER_CHECKPOINT_BOOTSTRAP_LATE_AUDITOR_SNAPSHOT_PROVENANCE_COMPACTION_V1_FROZEN`.

The core rule is: **a snapshot may replace replay cost, but it may never replace provenance**. A late auditor may skip genesis replay only when it can prove an unbroken authenticated path from an admissible anchor to the snapshot and when compaction has preserved every evidence class required to detect earlier mapper fraud, trust-frontier equivocation and historical omission-proof invalidation.
