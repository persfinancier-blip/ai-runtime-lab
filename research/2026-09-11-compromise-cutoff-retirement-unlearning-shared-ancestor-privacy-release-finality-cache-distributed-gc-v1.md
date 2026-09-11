# LAB-093 evidence freeze — compromise cutoff poisoning, verifier retirement, shared-ancestor unlearning GC, privacy release races, finality cache invalidation, distributed graph-epoch GC

Date: 2026-09-11
Status: DESIGN FROZEN / RED-FIRST; **not executable proof**

Contract name: `COMPROMISE_CUTOFF_RETIREMENT_UNLEARNING_SHARED_ANCESTOR_PRIVACY_RELEASE_FINALITY_CACHE_DISTRIBUTED_GC_V1_FROZEN`

## Why this slice exists

LAB-086 exact source execution remains blocked in the current runtime before repository code executes (`git clone --no-checkout` cannot resolve `github.com`). Per `state/CURRENT.md`, the next safe fallback is therefore a distinct evidence/design slice. This document does not relax any retained LAB-086 gate and does not claim RED/GREEN execution.

The prior freezes established monotonic recovery/equivocation floors, authenticated stale-verifier retirement, theorem/profile-scoped unlearning, cumulative privacy accounting, provider-finality revalidation after retroactive compromise, and linearizable `CAN_RESTORE` GC epochs. This slice closes six remaining compositional holes where apparently valid evidence can become unsafe after cutoff poisoning, ancestor revocation, concurrent reservation release, cached finality, or replica disagreement.

## Primary donor mechanisms

1. **TUF root/metadata rollback discipline.** Trusted metadata has explicit versions/expiry and signature thresholds; clients reject rollback. Root/key recovery depends on trusted role thresholds rather than freshness alone. This motivates monotonic evidence generations and forbids a newly delivered compromise assessment from silently redefining an older cutoff without an authenticated superseding chain.
2. **RFC 9162 consistency proofs.** A signed tree head authenticates one view; append-only continuity between old and new heads requires a consistency proof. This motivates retaining compact checkpoint/tombstone commitments sufficient for retired verifier profiles to prove continuity rather than trusting a later head in isolation.
3. **NIST SP 800-226 privacy-budget composition.** Privacy budget is an upper bound on cumulative privacy loss across analyses. Therefore de-join/release may return only reservations proven unused; it cannot refund already incurred loss, including during races with newly admitted analyses.
4. **NIST SP 800-88 Rev. 2 cryptographic-erasure assurance.** CE requires sanitization/validation of relevant target key material and accounts for externally managed keys. This motivates graph-epoch barriers that cannot commit destructive GC while another inventory replica exposes a still-restorable authority path.

## Frozen invariants

### A. Compromise-evidence cutoff poisoning

- A compromise assessment is evidence, not an oracle. Its authority identity, signing interval, source-log head, evidence cutoff, predecessor assessment id, and canonical subject/failure-domain set are authenticated inputs.
- A later assessment may *extend* or *supersede* an earlier cutoff only through a monotonic assessment generation that commits the predecessor and the evidence set used to justify the change.
- Moving a compromise cutoff backward so that previously admissible signatures become compromised is security-relevant and forces re-evaluation of all dependent recovery/finality/unlearning claims; it does not rewrite historical durable effects.
- Moving a cutoff forward cannot resurrect authority previously quarantined by an accepted lower generation unless the superseding generation explicitly carries independent recovery authorization satisfying the current trust policy.
- Two valid assessments at the same generation with different cutoffs/source heads are `COMPROMISE_ASSESSMENT_FORK`; consumers fail closed rather than choosing by timestamp, arrival order, or longest cutoff.
- Poisoning or later compromise of the assessment issuer invalidates confidence in affected assessments for its compromised interval; already-established monotonic rollback/equivocation floors remain.

### B. Compact checkpoint/tombstone continuity across verifier-profile retirement

- Retirement is an authenticated state transition, not wall-clock deletion permission.
- A retirement record binds: retired verifier profile/version, last accepted checkpoint head, successor profile/version, successor checkpoint head, consistency/bridge proof digest, retention floor, and retirement generation.
- Compaction may discard detailed historical membership/proof rows only after preserving a cryptographic tombstone/commitment from which the successor verifier can prove that the retired head is an ancestor of the retained history.
- A successor signed head without a bridge/consistency proof is insufficient.
- If the retained compact checkpoint later equivocates, all dependent retirement claims are quarantined; GC cannot claim that missing predecessor evidence was safely retired.

### C. Unlearning re-proof GC with multiple current certificates sharing a revoked ancestor

- Model unlearning proof lineage is a DAG, not a list. Each current certificate commits theorem/profile root, deleted-data lineage, transformation/model lineage, direct proof parents, and guarantee class.
- Revocation/defect of a shared ancestor invalidates every descendant whose guarantee depends on that ancestor until each affected branch is independently re-proved/re-anchored.
- Re-proving one descendant does not repair siblings sharing the revoked ancestor.
- GC of a revoked ancestor is allowed only after every live descendant either (a) has an independently sufficient re-proof path that no longer depends on the ancestor, or (b) is itself durably revoked/tombstoned.
- A compact tombstone must preserve enough ancestry to prove that no surviving `CERTIFIED` claim still derives authority from the deleted proof.
- Re-signing a descendant under a new key without recomputing the theorem/profile proof does not sever the dependency.

### D. Privacy reservation-release races during resolver de-join

- Accounting state distinguishes `consumed_loss`, `reserved_loss`, `uncertain_loss`, and `released_unused_reservation`.
- A de-join/relink resolver may release reservation only against an authenticated accounting snapshot/cutoff and only for budget proven never consumed by an admitted analysis.
- Admission of a new analysis and reservation release serialize on one monotonic accounting generation (or equivalent compare-and-swap token).
- If an analysis is admitted after the release snapshot but before release commit, release must abort/recompute; it may not subtract the newly consumed/reserved amount.
- Resolver fork or source-log equivocation retains the conservative union/upper-bound floor until convergence proof; no branch may independently refund the same reservation.
- Duplicate release receipts are idempotent and cannot double-credit budget.

### E. Finality-revalidation cache invalidation after retroactive authority compromise

- Cached `FINAL` is derived evidence with explicit dependencies: provider effect id, receipt/finality attestation ids, authority generation, authority-validity interval, compromise-assessment generation, reconciliation source head, and cache generation.
- Retroactive compromise that intersects any authority-validity interval invalidates every dependent cache entry, including transitive summaries/materialized views.
- Cache invalidation changes confidence in evidence, not the external side effect. Destructive effects become `EFFECT_UNKNOWN` until independently reconciled.
- A cache hit from an older compromise-assessment generation is fail-closed stale even when its TTL has not expired.
- Successor/failover authority cannot repopulate predecessor finality merely by re-signing the cached conclusion; it needs independent transition/reconciliation evidence.
- Negative cache entries (`NO_EFFECT`) follow the same dependency invalidation rule; they may not authorize blind retry after retro-compromise.

### F. Crash-consistent/distributed GC barriers under authority-inventory epoch disagreement

- Destructive authority GC is admitted only against a globally identified immutable graph snapshot `G_e` and GC epoch `e`.
- Every authority-inventory replica participating in the safety domain must attest either `APPLIED(G_e)` or a stronger successor snapshot proven to contain no newly discovered restore edge relevant to the candidate.
- `UNKNOWN`, unreachable, lagging, or conflicting replica state is not an ACK; it blocks destructive commit unless that replica/domain has itself been durably and independently retired from the safety membership.
- The coordinator persists `PREPARE_GC(e,G_e,candidate_set)` before destructive work and `COMMIT_GC(e,proof_digest)` only after SCC/fixed-point closure and the distributed barrier are durable.
- Crash after PREPARE and before COMMIT is recoverable/idempotent: restart re-reads replica epochs and recomputes if any inventory state advanced.
- Discovery of a new `CAN_RESTORE` edge after proof evaluation but before COMMIT invalidates the epoch. Discovery after COMMIT creates a higher-epoch security incident/recovery obligation; it does not make the old proof silently true.
- Two coordinators cannot both commit different candidate sets for the same GC epoch; conflicting prepares/commits are explicit `GC_EPOCH_FORK` and halt further destructive GC.

## State machines

### Compromise assessment

`PROPOSED -> ACCEPTED -> SUPERSEDED`

Exceptional states: `FORKED`, `ISSUER_UNCERTAIN`, `QUARANTINED`.

Only a strictly higher authenticated generation can supersede `ACCEPTED`; same-generation disagreement is `FORKED`.

### Verifier retirement

`ACTIVE -> RETIRE_PREPARED -> BRIDGED -> RETIRED`

No history compaction before `BRIDGED`; no predecessor tombstone deletion before durable `RETIRED` and retention floor satisfaction.

### Unlearning proof

`CERTIFIED -> {SUPERSEDED | REVOKED}`; affected descendants become `REPROOF_REQUIRED` until independent proof commits.

### Distributed GC

`OPEN(e) -> PREPARED(e,G_e) -> BARRIER_SATISFIED -> DESTRUCTIVE_STEP -> COMMITTED(e)`

Any relevant graph/replica mutation before COMMIT returns to a higher `OPEN(e+1)`; no stale proof reuse.

## RED-first 40-case matrix

### Compromise cutoff poisoning (1-7)
1. Same-generation assessment changes cutoff backward: reject as fork.
2. Same-generation assessment changes cutoff forward: reject as fork.
3. Higher generation changes cutoff without predecessor commitment: reject.
4. Higher generation with poisoned/untrusted source-log head: quarantine.
5. Backward cutoff intersects recovery signatures: dependent recovery becomes uncertain; monotonic floor retained.
6. Forward cutoff attempts to resurrect quarantined authority without independent recovery authorization: reject.
7. Assessment issuer later compromised during signing interval: invalidate dependent assessment confidence and force re-evaluation.

### Verifier retirement continuity (8-13)
8. Wall-clock expiry alone used to delete predecessor checkpoint: reject.
9. Successor checkpoint is signed but no consistency/bridge proof exists: reject retirement.
10. Valid bridge with wrong retired profile/version: reject.
11. Valid bridge with retention floor below already-observed floor: reject rollback.
12. Compacted tombstone cannot prove retired head ancestry: fail closed.
13. Retained checkpoint later equivocates: quarantine retirement claim and block further predecessor GC.

### Shared-ancestor unlearning GC (14-20)
14. Two current certificates share ancestor A; A revoked; neither re-proved: both lose certified status.
15. Re-proof branch 1 only: branch 2 remains invalid.
16. Re-sign branch 2 without theorem/profile recomputation: remains invalid.
17. Delete A while live descendant still depends on A: GC blocked.
18. Tombstone A omits theorem/profile root: GC blocked.
19. All descendants independently re-proved or revoked, tombstone preserves ancestry: GC admissible.
20. New descendant appears after GC snapshot but before commit: abort/recompute.

### Privacy release races (21-27)
21. Release unused reservation with no concurrent admission: succeeds once.
22. Duplicate release receipt: idempotent, no double-credit.
23. Analysis admission races after release snapshot before commit: release aborts/recomputes.
24. Analysis already consumed budget but resolver marks reservation unused: reject refund.
25. Resolver fork gives two release candidates for same reservation: retain conservative floor.
26. Source-log equivocation discovered after tentative release before commit: abort release.
27. Namespace split/relink maps one original reservation into two identities: one accounting floor, no duplicated release.

### Finality cache invalidation (28-33)
28. Cached FINAL depends on authority later compromised in interval: invalidate cache, effect becomes UNKNOWN absent reconciliation.
29. Cached NO_EFFECT depends on compromised authority: invalidate; blind retry forbidden.
30. Cache TTL still valid but compromise-assessment generation advanced: stale/fail closed.
31. Successor authority re-signs old cached conclusion without reconciliation: reject.
32. Materialized summary transitively depends on invalid cache row: invalidate summary too.
33. Independent provider reconciliation confirms effect after invalidation: repopulate under new dependency generation.

### Distributed GC barriers (34-40)
34. All replicas attest same graph epoch and fixed point has no restore path: commit allowed.
35. One replica lags behind `G_e`: block.
36. One replica unreachable/UNKNOWN: block unless independently retired from safety membership.
37. Replica reports new restore edge after PREPARE before COMMIT: invalidate epoch/recompute.
38. Coordinator crashes after PREPARE: restart must not assume COMMIT; re-check all epochs.
39. Two conflicting PREPARE/COMMIT records for same epoch: `GC_EPOCH_FORK`, halt destructive GC.
40. New restore edge discovered after COMMIT: open higher-epoch incident/recovery; never rewrite old commit as proof of nonexistence.

## Minimal implementation shape when executable work resumes

Prefer extending existing authenticated-history/anchor abstractions rather than adding parallel subsystems:

- canonical `CompromiseAssessment` with generation, predecessor id, cutoff, source head and authority interval;
- authenticated `VerifierRetirementRecord` plus compact checkpoint/tombstone commitment;
- unlearning certificate dependency DAG with reverse dependency index for revocation/GC admission;
- privacy accounting generation/token covering admission + release;
- finality cache dependency vector and reverse invalidation index;
- authority-inventory `GraphSnapshot(epoch,digest)` plus durable PREPARE/COMMIT records and replica barrier attestations.

Every destructive or trust-lowering transition must be `verify -> BEGIN/lock -> re-verify generation -> mutate -> post-verify -> commit`, or the equivalent serializable primitive of the backing store.

## Security audit notes

- **Fresh signature != fresh truth.** Every cache/assessment/retirement proof must bind the generation/source head it reasons about.
- **Deletion is authority-sensitive.** GC can erase evidence needed to disprove a later forged history; tombstones must preserve minimal authenticated lineage.
- **Forks are first-class.** Never collapse same-generation disagreement by timestamp, arrival order, majority of replicas sharing one failure domain, or “latest wins”.
- **Unknown is not false.** Unknown restore edges, unknown effects, unknown reservation attribution and unreachable inventory replicas retain the conservative safety state.
- **Derived-state invalidation must be transitive.** A revoked authority/proof must invalidate cached/materialized descendants, not just its direct row.

## Acceptance boundary

This freeze is architecture/evidence only. It becomes implementation-ready after exact repository execution is available and regressions are authored first. No LAB-086/LAB-093 merge/readiness status changes from this document alone.

## Sources

- TUF roles/metadata and rollback/expiry discipline: https://theupdateframework.io/docs/metadata/
- TUF compromise/revocation guidance: https://theupdateframework.io/docs/faq/
- RFC 9162, Certificate Transparency v2, consistency proofs: https://www.rfc-editor.org/rfc/rfc9162.html
- NIST SP 800-226, Guidelines for Evaluating Differential Privacy Guarantees: https://doi.org/10.6028/NIST.SP.800-226
- NIST SP 800-88 Rev. 2, Guidelines for Media Sanitization: https://doi.org/10.6028/NIST.SP.800-88r2
