# Assessment-fork recovery, retirement revocation, unlearning races, privacy shards, finality cycles, and GC joint consensus — v1

Status: `ASSESSMENT_FORK_RETIREMENT_UNLEARNING_RACE_PRIVACY_SHARDS_FINALITY_CYCLES_GC_JOINT_CONSENSUS_V1_FROZEN`

Date: 2026-09-11

Issue context: LAB-093/#178 architecture continuation. LAB-086/#163 remains priority #1 and is not superseded.

## Why this slice exists

The preceding freezes established versioned compromise assessments, authenticated verifier retirement, dependency-aware unlearning proof lineage, race-safe privacy reservation release, transitive finality-cache invalidation, and crash-consistent distributed `CAN_RESTORE` GC. This slice closes six remaining ambiguity classes that become visible once those mechanisms overlap:

1. recovery from a compromise-assessment fork when nominally distinct assessment issuers share failure domains;
2. revocation of a verifier-retirement bridge after predecessor detail has already been compacted;
3. unlearning DAG re-proof races while new descendants are created during ancestor GC;
4. privacy reservation release for analyses spanning multiple accounting shards/epochs;
5. cyclic finality-cache dependencies and partial invalidation;
6. replica membership changes while a distributed destructive-GC epoch is open.

The contract below is fail-closed. It intentionally prefers loss of progress over silently converting ambiguous evidence into authority.

## Primary donors / mechanisms

### TUF root continuity and threshold rotation

The Update Framework requires a new root version to be signed both by the threshold authorized by the previously trusted root and by the threshold declared by the new root. Clients update root metadata one version at a time and reject rollback. This is the donor for monotonic trust-generation changes and for rejecting a purported recovery authority that cannot prove continuity from the last admissible state.

Source: https://theupdateframework.github.io/specification/draft/ — sections 5.3 and 6.1.

### RFC 9162 append-only consistency

Certificate Transparency v2 separates inclusion from append-only consistency. A signed tree head is not enough to prove that a later view extends an earlier view; a consistency proof is required, and split views require comparison across observers. This is the donor for retirement bridges and compacted predecessor-history checkpoints.

Source: https://www.rfc-editor.org/rfc/rfc9162.html

### NIST SP 800-226 privacy composition

NIST SP 800-226 treats repeated differentially private releases as composable privacy loss: re-running a release consumes additional budget and the total budget is cumulative. This is the donor for treating consumed privacy loss as non-refundable across shard migration, resolver repair, or reservation release.

Source: https://doi.org/10.6028/NIST.SP.800-226

### Raft joint consensus

Raft shows why changing replicated-cluster membership by directly switching from `C_old` to `C_new` is unsafe: disjoint majorities can exist. Its joint-consensus phase requires overlapping authorization from both old and new configurations before completing the transition. This is the donor for authority-inventory replica membership changes during an open GC epoch.

Source: https://raft.github.io/raft.pdf — section 6; USENIX ATC 2014.

### NIST SP 800-88 Rev. 2 cryptographic erase assurance

SP 800-88r2 requires sanitization assurance/validation and states that all copies of target cryptographic keys must be sanitizable; it also explicitly addresses externally managed keys. This is the donor for refusing destructive GC while authority-inventory completeness is ambiguous or a restore path remains live/unknown.

Source: https://doi.org/10.6028/NIST.SP.800-88r2

## Frozen contract

### 1. Compromise-assessment fork recovery with shared failure domains

A compromise assessment is accepted only as versioned authenticated evidence. Recovery after `COMPROMISE_ASSESSMENT_FORK` MUST reason over canonical failure domains, not signer/key count.

Define:

- `assessment_generation`: strictly monotonic generation;
- `assessment_parent_set_digest`: commits all predecessor fork heads being resolved;
- `evidence_cutoff`: latest evidence event included;
- `source_log_heads`: authenticated roots/checkpoints for every required evidence source;
- `issuer_domains`: canonical failure-domain identities for issuer authorities;
- `excluded_domains`: domains compromised or correlated for the affected interval;
- `surviving_threshold`: threshold evaluated after exclusions and canonical deduplication.

Rules:

- two signatures/issuers sharing one canonical failure domain count as one independent domain;
- a recovery generation MUST commit every fork head it resolves, not only the chosen branch;
- if the surviving independent-domain threshold is not met after interval-scoped compromise filtering, state remains `ASSESSMENT_FORK_UNRESOLVED`;
- later evidence may increase uncertainty or invalidate an issuer for an interval, but MUST NOT lower an already established rollback/equivocation floor;
- timestamps/arrival order/nominal issuer count are never fork-resolution rules;
- a recovery issuer whose authority derives only from a compromised predecessor domain cannot bootstrap independence by rotation or cross-signing.

### 2. Retirement-bridge revocation after predecessor compaction

Verifier-profile retirement may compact predecessor detail only after an authenticated bridge proves continuity from the last retained predecessor checkpoint into the successor verification profile.

A compacted retirement tombstone MUST retain at minimum:

- predecessor profile/version identity;
- predecessor authenticated checkpoint/root;
- successor profile/version identity;
- bridge digest and issuing authority generation;
- retention floor / minimum supported verifier generation;
- consistency/continuity proof digest;
- revocation status and revocation-parent digest.

Rules:

- revoking the bridge after predecessor detail has been compacted MUST NOT silently restore trust to either side;
- affected state becomes `RETIREMENT_CONTINUITY_UNCERTAIN` until a new independent bridge is established from retained authenticated material;
- compacted predecessor detail MUST NOT be reconstructed from successor claims alone;
- if retained material is insufficient to establish a new bridge, destructive GC that depends on retirement remains blocked permanently unless out-of-band recovery evidence is admitted by an explicit higher-level contract;
- a bridge signed only by the same compromised authority generation that is being revoked cannot self-heal by re-signing.

### 3. Unlearning re-proof races with new descendants during ancestor GC

Unlearning certificates form a dependency DAG, not a flat set. Ancestor GC is safe only against a snapshot that cannot gain unaccounted descendants before commit.

Each proof node MUST bind:

- proof/theorem profile generation;
- exact ancestor dependency set;
- model/artifact lineage digest;
- evidence cutoff;
- proof strength (`EXACT`, `CERTIFIED_BOUND`, `EMPIRICAL`, `UNKNOWN`);
- revocation/supersession parents.

Ancestor-GC protocol:

1. open `UNLEARNING_GC_EPOCH` over immutable DAG snapshot `S`;
2. block or version-fence creation of descendants that depend on ancestors scheduled for deletion;
3. independently re-proof/re-anchor every live descendant reachable from those ancestors;
4. require all such descendants to commit a proof generation not dependent on the retiring ancestor;
5. persist an authenticated ancestry tombstone;
6. only then delete ancestor proof material and commit GC.

If a new descendant appears after snapshot `S` and before commit, the epoch aborts/recomputes. Re-proofing one branch does not repair siblings. A stronger new profile does not retroactively upgrade old proofs.

### 4. Multi-shard / multi-epoch privacy reservation release

Privacy accounting across shards MUST preserve one conservative global floor even when an analysis spans multiple shards or accounting epochs.

Represent every reservation by a globally unique `analysis_id` with:

- shard-local reservation generations;
- global coordinator generation;
- consumed amount;
- reserved amount;
- uncertain amount;
- released-unused amount;
- participant shard set digest.

Release protocol:

1. obtain a read barrier from every participant shard at or beyond the coordinator cutoff;
2. prove the analysis cannot consume more budget on any participant at or before the release generation;
3. compute only `unused_reserved` as releasable;
4. write idempotent shard-local release records bound to the same global release generation;
5. publish global release completion only after every participant has durably acknowledged the same release generation.

Rules:

- consumed privacy loss is never released;
- missing/lagging/unknown shard blocks global release;
- partial release cannot be double-credited if retried;
- shard split/merge or accounting-epoch rotation during release aborts/recomputes unless covered by an authenticated transition bridge;
- resolver disagreement about participant set forces the union of plausible participant shards until convergence.

### 5. Finality-cache dependency cycles and partial invalidation

Cached `FINAL`, `NO_EFFECT`, or reconciliation conclusions MUST carry explicit dependency edges. The dependency graph may contain cycles (for example provider receipt -> transition proof -> authority assessment -> materialized finality -> receipt eligibility).

Rules:

- invalidation operates on strongly connected components (SCCs), not individual entries;
- if any dependency in an SCC becomes invalid/unknown for the relevant interval, every cache entry in that SCC becomes stale/unknown;
- invalidation then propagates transitively to downstream SCCs;
- an unaffected SCC may remain valid only if all inbound dependencies remain valid under the new evidence generation;
- stale `NO_EFFECT` cache entries MUST NOT authorize retry of destructive operations;
- partial recomputation MUST publish a new dependency-generation vector; mixing conclusions from old and new vectors is forbidden;
- cache cycles never create authority: an SCC with no independent valid source evidence resolves to `UNKNOWN`.

### 6. Distributed destructive-GC membership change via joint consensus

An open destructive `CAN_RESTORE` GC epoch is a replicated safety decision. Replica membership changes during that epoch MUST use an overlapping joint configuration rather than direct replacement.

Definitions:

- `C_old`: authority-inventory replicas admitted when the GC epoch opened;
- `C_new`: proposed new replica set;
- `C_joint = C_old + C_new` with authorization requiring the configured threshold/quorum of both sets;
- `gc_snapshot_digest`: immutable restore-graph snapshot;
- `membership_generation`: monotonic configuration generation.

Rules:

- direct `C_old -> C_new` switch during PREPARE/proof/destructive phases is forbidden;
- entering joint configuration requires authenticated membership transition evidence rooted in `C_old`;
- all safety-critical GC decisions during joint mode require sufficient authorization from both `C_old` and `C_new`;
- added replicas must catch up to the exact `gc_snapshot_digest` before contributing to the new quorum;
- retiring replicas remain safety-relevant until `C_new` is committed and every required old/new overlap condition is satisfied;
- if a removed replica reports a previously unknown `CAN_RESTORE` edge before final COMMIT, the GC epoch aborts even if `C_new` would otherwise form a quorum;
- unreachable/lagging replicas cannot be ignored merely by editing membership; retirement itself must be authorized by the joint transition contract;
- after joint consensus commits `C_new`, any unfinished old GC proof is invalid and must be recomputed against a new snapshot/membership generation unless the proof explicitly committed the joint transition and remained valid throughout it.

## Cross-domain invariants

1. `SIGNED != INDEPENDENT`: signature validity never proves failure-domain independence.
2. `COMPACTED != FORGOTTEN`: compaction must retain enough authenticated structure to detect rollback/revocation consequences.
3. `REPROVED_ONE_BRANCH != REPROVED_DAG`: proof repair is branch-specific unless independence is demonstrated for all descendants.
4. `PARTIAL_RELEASE != GLOBAL_CREDIT`: multi-shard privacy budget is credited only after a globally coherent release completion.
5. `CACHED_FINALITY != SOURCE_FINALITY`: cache validity is derivative and falls with its dependency SCC.
6. `MEMBERSHIP_EDIT != SAFETY_TRANSITION`: destructive-GC authority membership changes require an authenticated overlap phase.
7. No recovery/retirement/re-proof/release/cache/GC transition may lower a previously established uncertainty, rollback, equivocation, consumed-loss, or destructive-effect floor without new independent evidence that explicitly resolves it.

## RED-first regression matrix (40 cases)

### A. Assessment-fork recovery / shared failure domains

1. Two fork heads, nominally three issuer keys but two keys share one HSM/admin domain -> reject false 3-domain quorum.
2. Fork recovery commits only preferred branch, omits competing authenticated head -> reject.
3. Higher recovery generation commits both heads and meets surviving independent-domain threshold -> accept recovery while retaining fork ancestry.
4. Issuer compromise interval removes one domain after recovery proposal -> recompute threshold; reject if now insufficient.
5. Cross-signed successor key from compromised predecessor domain -> does not create independence.
6. Same-generation assessment with different cutoff -> explicit assessment fork, no timestamp tie-break.
7. Later benign assessment tries to lower previously established rollback/equivocation floor -> reject floor decrease.

### B. Retirement bridge revocation after compaction

8. Valid retirement bridge + compacted predecessor tombstone -> restart continuity verifies.
9. Revoke bridge authority after compaction with no independent retained path -> `RETIREMENT_CONTINUITY_UNCERTAIN`.
10. Re-sign revoked bridge payload under successor whose authority derives only from revoked predecessor -> reject self-heal.
11. Independent higher-generation bridge from retained predecessor checkpoint to successor -> continuity restored.
12. Compacted tombstone missing predecessor checkpoint/root -> reject GC/retirement verification.
13. Successor-only reconstruction of deleted predecessor details -> reject.
14. Bridge revocation while destructive GC is prepared but not committed -> invalidate/abort GC epoch.

### C. Unlearning DAG re-proof races

15. Ancestor A -> descendants B,C; re-proof B only; attempt A GC -> reject because C remains dependent.
16. Snapshot DAG, re-proof all known descendants, then create new descendant D(A) before commit -> abort/recompute.
17. New descendant created against fenced ancestor generation -> creation rejected or forced onto re-anchored generation.
18. Revoked theorem/profile ancestor infects all dependent descendants -> all affected claims non-current.
19. Stronger successor profile re-signs old evidence without fresh proof -> does not upgrade old claim.
20. All descendants independently re-proofed + authenticated ancestry tombstone -> permit ancestor proof GC.
21. Re-proof record omits exact lineage digest -> reject as insufficient to prove independence.

### D. Multi-shard privacy reservation release

22. Analysis reserves on shards A,B; A says unused, B unreachable -> no global release.
23. A releases locally, coordinator crashes before B; retry -> idempotent, no double credit.
24. Analysis consumed part of A reservation, unused on B -> release only proven-unused amounts; consumed loss retained.
25. Participant shard set resolver forks between {A,B} and {A,C} -> conservative union {A,B,C} until convergence.
26. Shard split B -> B1/B2 during release without authenticated bridge -> abort/recompute.
27. Accounting epoch rotates on A after barrier before completion -> abort/recompute unless transition is bound into release proof.
28. All shards acknowledge same global release generation -> publish one global release completion.

### E. Finality-cache cycles / partial invalidation

29. Cache SCC contains FINAL -> transition proof -> authority assessment -> FINAL cycle; compromise assessment invalidated -> entire SCC stale.
30. Downstream NO_EFFECT cache depends on stale SCC -> transitive invalidation; blind retry forbidden.
31. Independent cache SCC with no inbound edge from invalidated component -> remains valid after dependency check.
32. Recompute only one member of a cyclic SCC -> reject mixed-generation publication.
33. Cycle has no independent source evidence, only mutually supporting cache entries -> resolve UNKNOWN.
34. Old negative cache and new positive reconciliation share mismatched dependency vectors -> reject mixed decision.

### F. Distributed GC membership / joint consensus

35. Direct C_old -> C_new switch during PREPARE creates disjoint-majority possibility -> reject transition.
36. Enter C_joint with valid old-authorized membership transition; new replica not caught up to snapshot -> cannot contribute to C_new quorum.
37. C_joint obtains required old and new quorums on exact snapshot -> membership transition may advance.
38. Replica scheduled for retirement reports new restore edge before COMMIT -> abort GC despite sufficient C_new quorum.
39. Unreachable old replica is removed solely to make quorum -> reject; retirement must satisfy joint-transition contract.
40. C_new commits while old GC proof predates/omits transition -> invalidate proof and recompute under new membership/snapshot generation.

## Implementation guidance when exact execution becomes available

- Tests first. Each group above should become a focused executable RED suite before production changes.
- Reuse one canonical domain-identity function across assessment, witness, and recovery quorum logic; do not deduplicate separately by key ID.
- Model retirement bridge/tombstone records as authenticated append-only metadata with explicit parent/checkpoint digests.
- Make unlearning DAG generation and ancestor-GC epoch explicit durable fields; descendant creation must observe the GC fence.
- Use one global privacy release ID/generation with participant-set digest and shard-local idempotent acknowledgements.
- Represent finality dependencies as a graph and invalidate/recompute by SCC + generation vector.
- Treat destructive-GC replica membership as part of the authenticated GC state machine; do not mutate replica lists out-of-band while an epoch is open.

## Audit notes

- This freeze is architecture/evidence only. It does not claim exact repository behavioral execution.
- It does not weaken LAB-086's retained exact-byte materialization gate.
- TUF/RFC 9162/Raft/NIST are structural donors, not drop-in implementations; their mechanisms are adapted to the lab's authority graph and must still be regression-proved.
- The conservative union/unknown rules intentionally trade availability for safety where evidence lineage is ambiguous.

## Next distinct slice if executable gates remain unavailable

Focus next on: assessment issuer-domain registry rollback/equivocation; retirement tombstone root rotation; unlearning DAG snapshot isolation across distributed proof workers; privacy participant-set attestation and coordinator failover; finality-cache SCC compaction/checkpointing; and GC joint-consensus recovery after coordinator crash or split-brain during membership transition.
