# Issuer registry, retirement-root rotation, distributed proof snapshot, privacy failover, finality checkpoint, and GC recovery — V1

Status: `ISSUER_REGISTRY_RETIREMENT_ROOT_UNLEARNING_SNAPSHOT_PRIVACY_FAILOVER_FINALITY_CHECKPOINT_GC_RECOVERY_V1_FROZEN`

Date: 2026-09-11

Context: LAB-086 exact executable closure remains blocked in this runtime because direct git transport cannot resolve `github.com`, while GitHub connector reads/writes remain available. This note is the next distinct evidence task recorded in `state/CURRENT.md`; it does **not** substitute for any executable RED/GREEN gate.

## Scope

Freeze fail-closed contracts for six adjacent authority/recovery problems that can otherwise reintroduce rollback, split-view, double-release, stale-finality, or unsafe destructive-GC behavior:

1. assessment issuer-domain registry rollback/equivocation;
2. verifier-retirement tombstone trust-root rotation;
3. unlearning DAG snapshot isolation across distributed proof workers;
4. privacy participant-set attestation and coordinator failover;
5. finality-cache SCC compaction/checkpointing;
6. destructive-GC joint-consensus recovery after coordinator crash or split-brain during membership transition.

## Primary donors and facts

### TUF root continuity / rollback discipline

The Update Framework specification v1.0.36 (last modified 2026-08-05) explicitly targets rollback, mix-and-match, freeze, and threshold-key compromise attacks, and its root-update workflow provides a useful donor model for authenticated trust-root succession rather than unilateral replacement.

Source: https://theupdateframework.github.io/specification/latest/

### RFC 9162 append-only consistency

RFC 9162 distinguishes inclusion from consistency: Merkle consistency proofs establish that a later authenticated tree extends an earlier authenticated tree. It also calls out the need to audit consistency of the log view presented to different observers. This is the donor for compacted checkpoint continuity and split-view handling.

Source: https://www.rfc-editor.org/rfc/rfc9162.html

### NIST SP 800-226 cumulative privacy accounting

NIST SP 800-226 defines a privacy budget as an upper bound on allowable cumulative privacy loss across analyses over a dataset. Participant migration/failover therefore cannot be treated as a fresh budget namespace merely because coordinator or shard ownership changes.

Sources:
- https://csrc.nist.gov/pubs/sp/800/226/final
- https://csrc.nist.gov/glossary/term/privacy_budget

### Raft joint consensus

Raft's membership-change design uses joint configuration so old and new memberships overlap during the transition; direct unsynchronized switches can admit disjoint majorities. This is the donor for destructive-GC membership recovery after coordinator failure.

Source: https://raft.github.io/

## Frozen contracts

### A. Assessment issuer-domain registry

`VALID_ASSESSMENT_SIGNATURE != VALID_ISSUER_DOMAIN_MEMBERSHIP`.

Each assessment must bind an authenticated issuer-domain registry generation, stable canonical failure-domain identity, effective interval, and registry-head digest. A registry generation is acceptable only when it extends the last accepted generation through authenticated continuity; timestamps and arrival order are not authority.

If two valid registry heads claim the same predecessor/generation but different issuer/failure-domain membership, the state is `ISSUER_REGISTRY_EQUIVOCATION`. Assessments depending on the disputed membership are `ASSESSMENT_AUTHORITY_UNKNOWN` until a higher recovery generation commits every conflicting head being resolved plus the last undisputed predecessor.

Rollback to an older registry head never restores an issuer removed/revoked at a higher accepted generation. Compromise filtering is interval-scoped and failure-domain-scoped: multiple keys or issuers mapping to one canonical failure domain contribute one independent domain.

### B. Verifier-retirement tombstone trust-root rotation

A retirement tombstone is authority-bearing history, not a disposable cache row. The tombstone must bind verifier/profile identity, retirement generation, predecessor trust-root/checkpoint, successor root, retention floor, and an authenticated continuity proof.

Trust-root rotation for retirement evidence requires an authenticated bridge from the currently trusted retirement root to the successor. A successor-only signature is insufficient after predecessor compaction. If the predecessor root is later compromised for the bridge interval, the bridge becomes `RETIREMENT_CONTINUITY_UNCERTAIN`; re-signing the same tombstone under the successor does not repair the lost continuity.

Compaction may discard old verifier material only after a retained checkpoint/tombstone root can prove both: (a) the verifier is retired at or above the monotonic retirement floor; and (b) the retained successor view is consistent with the authenticated predecessor view. Split-view tombstone heads block compaction.

### C. Distributed unlearning-DAG snapshot isolation

An unlearning proof worker may evaluate only against an immutable authenticated DAG snapshot identified by `(dag_generation, root_digest, dependency_profile_digest)`.

Every proof result binds that snapshot identity. The coordinator may aggregate worker results only when all results refer to the exact same snapshot and theorem/profile generation. A worker result from an older snapshot cannot be silently promoted because its local node set still exists.

Any new descendant, dependency edge, revocation, theorem/profile supersession, or influence-lineage discovery before commit invalidates the affected proof cone and forces a new snapshot/re-proof. Shared ancestors are handled once as dependencies but every live descendant branch must independently satisfy the current proof contract before ancestor evidence can be garbage-collected.

A crashed/restarted worker must reacquire the snapshot by digest, not reconstruct an equivalent-looking local graph from mutable current state.

### D. Privacy participant-set attestation and coordinator failover

Each analysis/reservation has one stable `analysis_id`, accounting generation, participant-set digest, and coordinator epoch. Participant membership is attested by the participating shards/domains themselves (or an authority that independently commits their identities), not self-asserted solely by the coordinator.

Failover is legal only when the successor coordinator proves continuity from the last committed accounting generation and adopts the conservative union of unresolved participant claims. Missing, lagging, or equivocal participant attestations keep the reservation unresolved; they cannot be discarded to release budget.

A release is idempotent and monotonic: it may release only proven-unused reservation capacity. Consumed privacy loss is never refunded. A coordinator epoch change, shard migration, namespace rotation, or participant split/merge does not reset cumulative accounting.

Two successor coordinators that each produce conflicting release/consume decisions for the same accounting predecessor create `PRIVACY_COORDINATOR_FORK`; both branches remain quarantined until a higher generation commits and reconciles both heads.

### E. Finality-cache SCC compaction/checkpointing

Finality cache/materialized-view nodes form a dependency graph. Strongly connected components are the unit of invalidation and checkpointing when cyclic derivations exist.

A compacted checkpoint must bind: SCC member identities, source-evidence digests, dependency-generation vector, finality authority generation, unresolved gaps/forks/unknowns, and the predecessor checkpoint digest. A checkpoint that records only the resolved value (`FINAL`, `NO_EFFECT`, etc.) is insufficient.

If any source evidence, authority generation, compromise assessment, or dependency generation changes, the checkpoint and every downstream dependent checkpoint become stale. Cycles without independent source evidence resolve to `UNKNOWN`; compacting the cycle cannot manufacture independent support.

Compaction may delete superseded cache nodes only after the retained checkpoint preserves enough authenticated provenance to re-evaluate invalidation and detect predecessor rollback/split view.

### F. Destructive-GC joint-consensus recovery

A destructive GC epoch binds an immutable graph/inventory snapshot and a membership configuration. During membership change, decisions require joint authorization under the configured old and new quorums until the transition commits.

Coordinator identity is not authority by itself. After coordinator crash, a successor must prove the current GC epoch, snapshot digest, joint-membership state, and highest durable phase before acting. Recovery cannot skip from `PREPARE`/barrier state directly to destructive commit based on local memory.

If two coordinators produce conflicting durable phase records or membership-transition heads, state is `GC_COORDINATOR_FORK`. No destructive step or membership finalization proceeds until a higher recovery generation commits both fork heads and reconstructs a single joint-consensus history.

A removed/unreachable replica cannot be edited out of the old configuration merely to satisfy the GC barrier. Added replicas cannot vote on the destructive snapshot until they prove catch-up to the exact bound snapshot. Any new `CAN_RESTORE` edge or inventory mutation before `COMMIT_GC` invalidates the proof epoch and requires recomputation.

## RED-first matrix (40 cases)

### Issuer-domain registry (1-7)
1. Same-generation registry heads with different issuer membership -> `ISSUER_REGISTRY_EQUIVOCATION`.
2. Same issuer under two keys mapped to one failure domain -> counts once.
3. Registry rollback reintroduces previously revoked issuer -> reject.
4. Assessment signed by valid key absent from bound registry generation -> authority unknown/reject.
5. Assessment binds registry generation but wrong head digest -> reject.
6. Higher recovery registry commits only one of two fork heads -> reject recovery.
7. Interval-scoped compromise removes enough independent domains to drop below threshold -> dependent assessment becomes unknown.

### Retirement tombstone/root rotation (8-14)
8. Successor retirement root signs tombstone without predecessor bridge -> reject.
9. Bridge exists but predecessor checkpoint digest mismatches retained history -> reject.
10. Predecessor root later compromised during bridge interval -> continuity uncertain.
11. Re-sign same tombstone under successor after predecessor compromise -> remains uncertain.
12. Two same-generation tombstone roots for one verifier -> split view; block compaction.
13. Tombstone proves retirement below already accepted retirement floor -> reject rollback.
14. Compaction removes all material needed to verify predecessor-to-successor consistency -> forbidden.

### Distributed unlearning DAG (15-21)
15. Workers return proofs for different DAG root digests -> reject aggregation.
16. Same root digest but different theorem/profile generation -> reject aggregation.
17. New descendant appears after snapshot before commit -> invalidate affected GC/proof cone.
18. New dependency edge discovered after snapshot -> invalidate affected results.
19. Shared ancestor re-proved for one sibling only -> other sibling remains unresolved.
20. Worker restart reconstructs mutable current graph instead of reacquiring bound snapshot -> reject result.
21. Revoked theorem/profile ancestor remains referenced by cached descendant proof -> descendant invalid until independent re-proof/re-anchor.

### Privacy participant/failover (22-28)
22. Coordinator claims participant set lacking shard/domain attestation -> unresolved.
23. Two shards disagree on participant set -> use conservative union; no release.
24. Coordinator crashes after consume before durable release decision -> successor resumes same accounting generation, no refund.
25. Coordinator crashes after release prepared but before commit -> idempotent replay under same release generation.
26. Two successor coordinators emit conflicting release/consume heads -> `PRIVACY_COORDINATOR_FORK`.
27. Namespace/shard migration attempts to start fresh budget -> reject; preserve cumulative floor.
28. Missing participant becomes unreachable -> cannot remove solely to release reservation.

### Finality-cache SCC checkpointing (29-34)
29. SCC checkpoint records resolved value but omits source-evidence digests -> reject checkpoint.
30. One source receipt authority is retroactively compromised -> entire dependent SCC stale.
31. Dependency generation changes inside SCC -> invalidate SCC and downstream graph.
32. Pure cycle has no independent source evidence -> resolve `UNKNOWN`, never `FINAL`/`NO_EFFECT`.
33. Predecessor checkpoint rollback supplied after newer accepted checkpoint -> reject.
34. Two incompatible checkpoint heads for same predecessor/generation -> finality split view; block compaction/retry authorization.

### Joint-consensus destructive GC recovery (35-40)
35. Coordinator crashes in joint configuration; successor lacks durable joint-membership proof -> block.
36. Old-config quorum alone authorizes destructive step while joint transition open -> reject.
37. New-config quorum alone authorizes destructive step while joint transition open -> reject.
38. Added replica votes before proving catch-up to exact GC snapshot -> reject vote.
39. Competing coordinators durably advance incompatible GC phases/membership heads -> `GC_COORDINATOR_FORK`; no destruction.
40. New `CAN_RESTORE` edge appears after proof/barrier but before `COMMIT_GC` -> invalidate epoch and recompute.

## Audit

- No rule treats timestamp, arrival order, local majority, coordinator identity, or re-signing as recovery authority.
- Every destructive/release/compaction transition retains a monotonic floor and explicit predecessor continuity.
- Split-view/equivocation is represented as state, not normalized away.
- Distributed workers/coordinators cannot combine outputs from different authenticated snapshots/generations.
- Privacy accounting never refunds consumed loss or creates a fresh budget by failover/migration.
- Joint-consensus recovery cannot remove dissenting/unreachable members to manufacture a quorum.

## Implementation direction

When exact executable source becomes available, implement tests first. Prefer small explicit records/types for registry head, retirement bridge, proof snapshot identity, participant-set attestation, finality checkpoint, and GC joint-membership phase rather than hidden booleans. Preserve authenticated predecessor digests and generation numbers so rollback/equivocation remain observable after compaction.

No executable PASS is claimed by this research freeze.