# Recovery-anchor rotation, multi-revocation continuity, propagated stale descendants, privacy-version reconciliation, compensation-chain ambiguity, and GC joint-loss v1

Date: 2026-09-11
Status: `RECOVERY_ANCHOR_ROTATION_RETIREMENT_MULTIREVOKE_UNLEARNING_PROPAGATION_PRIVACY_VERSION_COMPENSATION_CHAIN_GC_JOINT_LOSS_V1_FROZEN`
Scope: architecture/evidence only; exact RED/GREEN execution is still pending.

## Why this slice

LAB-086 remains the executable priority, but exact byte-preserving source materialization into the local executor is unavailable in this run. Direct `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git` failed before repository execution with `Could not resolve host: github.com`. This note therefore advances only the next distinct design/evidence task recorded in `state/CURRENT.md`; it does not substitute for LAB-086 execution.

## Primary donors re-verified

1. TUF Specification 1.0.36 (last modified 2026-08-05): https://theupdateframework.github.io/specification/latest/
   - threshold/quorum trust, compromise containment, revocation, rollback rejection, predecessor/successor root continuity;
   - donor mechanism: a successor trust root is accepted through authenticated continuity from a previously accepted root, rather than by self-assertion.
2. RFC 9162 Certificate Transparency v2: https://www.rfc-editor.org/rfc/rfc9162.html
   - Merkle consistency proofs establish append-only continuity between historical and later authenticated heads;
   - donor mechanism: a signed/authenticated head alone is not evidence that two histories are consistent.
3. NIST SP 800-226 / privacy-budget glossary: https://csrc.nist.gov/pubs/sp/800/226/final and https://csrc.nist.gov/glossary/term/privacy_budget
   - privacy budget is an upper bound on allowable cumulative privacy loss across analyses over the same dataset;
   - donor mechanism: accounting lineage must survive coordinator/accountant replacement and cannot silently refund already released privacy loss.
4. AWS idempotency documentation: https://docs.aws.amazon.com/ebs/latest/userguide/ebs-direct-api-idempotency.html and https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ECS_Idempotency.html
   - same client token + same parameters denotes the same operation; changed parameters conflict; some APIs explicitly bound token retention by TTL;
   - donor mechanism: retries and compensations require stable operation identity, and expiry of provider dedupe retention cannot be treated as proof of no prior effect.
5. Raft extended paper, membership changes: https://raft.github.io/raft.pdf
   - joint consensus requires separate majorities from old and new configurations; new servers catch up before participating as voters;
   - donor mechanism: there must be no interval in which disjoint old/new configurations can independently authorize destructive state transitions.

## Frozen contract A — recovery-generation anchor rotation after recovery-of-recovery fork

A recovery decision has an immutable `(lineage_id, generation, predecessor_digest, competing_heads_digest, policy_digest, authority_set_digest)` identity. Once generation `g` is accepted, `< g` is rollback and another incompatible `g` is equivocation/fork evidence.

Rotating the recovery-generation anchor after a resolved recovery-of-recovery fork MUST:
- authenticate the exact accepted predecessor anchor and all known competing heads that the new anchor resolves;
- preserve inherited compromise/non-resurrection floors;
- require threshold authorization under the predecessor and successor authority policies when the authority set changes;
- reject a successor that omits a known competing head, rewrites the predecessor digest, or lowers any accepted generation/floor;
- retain a compact fork tombstone sufficient to reject replay even after detailed fork evidence crosses retention.

If the only compact anchor needed to prove this succession is later lost/revoked and no independent continuity proof survives, the result is `RECOVERY_ANCHOR_CONTINUITY_UNRECOVERABLE`; recovery authority stops rather than self-bootstrapping a new lineage.

## Frozen contract B — retirement continuity across multiple revoked checkpoints

Verifier retirement is a monotonic non-resurrection floor. Revoking checkpoint `C2` after `C1 -> C2 -> C3` does not lower the maximum retirement floor committed by the lineage.

A reconstructed continuity path MAY bypass one or more revoked checkpoints only when surviving authenticated evidence proves:
- the predecessor accepted floor;
- the successor accepted floor is greater than or equal to it;
- the successor commits the revoked checkpoint identities/range being bypassed;
- the successor trust transition itself is valid.

Multiple revoked checkpoints without a surviving bridge yield `RETIREMENT_CONTINUITY_UNRECOVERABLE`. This blocks further positive continuity claims but never re-enables a retired verifier.

## Frozen contract C — stale unlearning replica propagated descendants to another partition

Every authority-bearing unlearning result/descendant commits `(dataset_lineage, theorem_profile_generation, invalidation_root, parent_result_ids, worker_membership_generation)`.

When stale replica A creates descendants under invalidation root `R_old` and propagates them to partition B before A learns of rotation/revocation to `R_new`:
- B MUST treat those descendants as provisional/unknown once it learns of an incomparable or later authenticated invalidation checkpoint;
- transitive descendants are invalidated/revalidation-required, not only the directly stale result;
- healing requires exact frontier exchange so omitted descendants cannot remain positive merely because their originating replica is absent;
- the successor invalidation root commits the union of all discovered stale branches and the membership/frontier checkpoint used for closure;
- deletion/eviction of a stale object does not erase the fact that authority derived from it may have propagated.

If a propagated branch cannot be reconstructed sufficiently to determine dependency, dependent authority is `UNLEARNING_DEPENDENCY_UNKNOWN` and fails closed.

## Frozen contract D — privacy overrun reconciliation after coordinator/accountant version change

Privacy lineage identity is independent of coordinator process, shard name, accountant implementation version, and physical storage identity.

On coordinator/accountant transition `A_v1 -> A_v2`, the successor state commits:
- immutable released-analysis event set/frontier;
- outstanding reservations;
- participant/shard lineage identities;
- predecessor cumulative bound and accountant/version identifier;
- successor cumulative bound and the exact reproducible accounting rule/profile used.

A newer accountant MAY lower the numeric bound only by reproducibly re-evaluating the same immutable released-event set under a policy-authorized tighter method. It MUST NOT omit events, treat deleted/retracted outputs as refunds, or choose the lower result of conflicting branches without reconciling their union.

If old/new accountant results are incomparable or event/frontier completeness is uncertain, effective loss is the conservative safe bound and new release is blocked when that bound exceeds policy budget. Coordinator failover never mints a fresh budget.

## Frozen contract E — E1/E2/E3 compensation chain with contradictory late evidence

Each provider-side effect has its own immutable identity and parameters:
- `E1`: original mutation;
- `E2`: compensation for E1;
- `E3`: compensation/recovery action for E2 or a separate forward repair.

They MUST NOT reuse one idempotency key merely because they concern the same business object. A retry of a particular effect reuses that effect's identity only with identical parameters.

Late evidence is merged monotonically. Examples:
- `E1=UNKNOWN, E2=COMPLETED, later E1=COMPLETED` means both effects occurred; it is not equivalent to `NO_EFFECT`;
- `E1=COMPLETED, E2=UNKNOWN, E3=COMPLETED` remains unresolved with respect to E2 until authenticated evidence closes it;
- a later provider assertion conflicting with already authenticated completion is recorded as provider-evidence equivocation/uncertainty, not silently chosen by freshness;
- after provider idempotency retention expiry, absence from the provider's dedupe table is not proof that an old effect did not execute.

Blind redispatch is forbidden whenever it could duplicate a still-possible effect. Reconciliation must prefer authenticated read/status evidence or explicit human/vendor resolution if no safe machine-verifiable path remains.

## Frozen contract F — GC compact-root succession with replica loss on both sides of joint consensus

For destructive GC, membership transition `C_old -> C_joint -> C_new` and compact-root succession are separate but coupled state machines.

Requirements:
- new replicas catch up the exact authenticated GC root/scope/tombstone frontier before voting for destructive work;
- while `C_joint` is authoritative, a destructive commit requires the configured old-majority AND new-majority condition; neither side alone can authorize;
- losing replicas from both sets does not permit dynamically shrinking the quorum or declaring `C_new` authoritative unless the `C_new` transition itself was durably committed under valid joint authority;
- a committed destructive effect does not imply that the membership transition completed, and a committed membership transition does not fabricate evidence that a destructive effect occurred;
- after `C_new` is committed, stale `C_old`/`C_joint` authority is rejected even if enough old replicas later reappear;
- if losses make it impossible to prove whether `C_new` was validly committed, state is `GC_MEMBERSHIP_FINALITY_UNKNOWN` and future destructive GC is blocked.

Compaction may remove detailed parent-scope metadata only after a successor compact root proves exact scope coverage, predecessor continuity, non-resurrection floors, and membership-transition finality.

## RED-first matrix — 48 cases

### A. Recovery anchor rotation (A01-A08)
1. A01 valid g2 anchor after resolved g1 fork commits both fork heads -> accept.
2. A02 replay g1 after accepted g2 -> rollback reject.
3. A03 alternate same-generation g2 -> fork/uncertain.
4. A04 g3 omits a known g2 competing head -> reject incomplete resolution.
5. A05 g3 lowers inherited compromise floor -> reject.
6. A06 authority-set rotation signed only by successor set -> reject missing predecessor continuity.
7. A07 retained compact tombstone rejects old fork replay after detail deletion -> accept rejection.
8. A08 sole compact continuity anchor revoked/lost -> `RECOVERY_ANCHOR_CONTINUITY_UNRECOVERABLE`.

### B. Retirement multi-revocation (B01-B08)
9. B01 C1->C2->C3 all valid -> highest floor retained.
10. B02 C2 revoked, C1/C3 plus authenticated bypass bridge survive -> continuity valid, floor unchanged.
11. B03 C2 revoked and C3 does not commit bypassed checkpoint/range -> reject.
12. B04 C1 and C2 revoked but independent C0->C3 bridge survives -> accept only if floor monotonic.
13. B05 all intermediate continuity evidence removed -> unrecoverable, no resurrection.
14. B06 restart attempts to use retired verifier because latest checkpoint revoked -> reject.
15. B07 successor root rotation lowers retirement floor -> reject.
16. B08 same-floor successor with valid continuity -> accept; floor remains non-resurrection-only.

### C. Propagated stale unlearning descendants (C01-C08)
17. C01 stale A result never propagated, later invalidated -> local eviction/revalidation.
18. C02 stale A child propagated to B before partition heal -> B child becomes provisional on learning R_new.
19. C03 B produced grandchild from stale child -> transitive invalidation reaches grandchild.
20. C04 A omits one propagated branch during heal -> closure incomplete/reject positive authority.
21. C05 successor root commits complete union frontier -> revalidation may proceed.
22. C06 stale object deleted before heal but B retains descendant -> lineage evidence still triggers revalidation.
23. C07 theorem/profile generation changed while partitioned -> all affected descendants require new-generation proof.
24. C08 dependency branch cannot be reconstructed -> `UNLEARNING_DEPENDENCY_UNKNOWN` fail closed.

### D. Privacy coordinator/accountant version transition (D01-D08)
25. D01 A_v2 replays same event set and derives equal bound -> accept transition.
26. D02 A_v2 validly derives tighter bound from identical immutable event set -> accept if policy authorizes method.
27. D03 A_v2 omits an event to fit budget -> reject.
28. D04 deleted/retracted released result treated as refund -> reject.
29. D05 coordinator failover starts empty ledger -> reject fresh-budget minting.
30. D06 two branches each spent independently then merge -> union accounting, no min(branch) selection.
31. D07 old/new accountant outputs incomparable -> conservative bound and block release when necessary.
32. D08 outstanding reservation omitted during version transition -> reject incomplete frontier.

### E. Provider E1/E2/E3 chain (E01-E08)
33. E01 E1 timeout then same-token/same-params retry inside retention -> same effect identity.
34. E02 same token with changed E1 parameters -> conflict/reject.
35. E03 E1 unknown, E2 compensation completed, late E1 completed -> record both effects occurred.
36. E04 E1 completed, E2 unknown, E3 completed -> E2 remains unresolved; no synthetic cancellation.
37. E05 E1/E2/E3 reuse one idempotency key -> reject identity collapse.
38. E06 dedupe TTL expired and provider has no token record -> outcome remains unknown, no blind retry.
39. E07 authenticated late evidence contradicts earlier authenticated completion -> provider-evidence fork/uncertainty.
40. E08 all three effects independently authenticated -> reconcile business state from actual ordered effects, not token freshness.

### F. GC joint-consensus replica loss (F01-F08)
41. F01 C_joint healthy, old-majority+new-majority authorize destructive root -> accept.
42. F02 only old-majority survives during joint phase -> reject destructive commit.
43. F03 only new-majority survives before C_new commit -> reject destructive commit.
44. F04 C_new durably committed, old replicas later recover -> stale old authority rejected.
45. F05 destructive effect committed but C_new membership commit missing -> effect finality preserved; membership remains joint/unknown.
46. F06 C_new membership committed but destructive effect status unknown -> do not infer effect completion.
47. F07 losses make C_new commit proof unavailable -> `GC_MEMBERSHIP_FINALITY_UNKNOWN`, block future destructive GC.
48. F08 compact parent scope only partially covered by surviving successor roots -> reject retention compaction/destructive reuse.

## Cross-cutting invariants

- Authentication is necessary but not sufficient: continuity, completeness, scope and generation must also be proven.
- Revocation/loss converts positive authority to unknown/unrecoverable where evidence is insufficient; it never restores previously removed authority.
- Compaction cannot erase rollback/fork/non-resurrection safety floors.
- Identity of a logical lineage/effect/budget is not derived from its current process, replica, filename, namespace or storage location.
- `UNKNOWN` is a first-class state. It is never silently coerced to success or no-effect to regain availability.
- Executable RED/GREEN evidence is required before production refactors or merge readiness.

## Audit verdict

`RECOVERY_ANCHOR_ROTATION_RETIREMENT_MULTIREVOKE_UNLEARNING_PROPAGATION_PRIVACY_VERSION_COMPENSATION_CHAIN_GC_JOINT_LOSS_V1_FROZEN`

This is a distinct architecture/evidence increment and does not claim executable validation.