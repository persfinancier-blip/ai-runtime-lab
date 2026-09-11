# EMERGENCY_ROOT_SUCCESSION_RETIREMENT_MULTITRANSITION_UNLEARNING_DUAL_INVALIDATION_PRIVACY_ALLOCATION_PROVIDER_COMPENSATION_FORK_GC_MEMBERSHIP_V1_FROZEN

Date: 2026-09-11
Status: architecture/evidence freeze; RED/GREEN execution pending
Parent: LAB-093/#178 design follow-up; does not supersede LAB-086/#163

## Run boundary

LAB-086 remained priority #1. A fresh direct `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git` failed before repository execution with `Could not resolve host: github.com`. GitHub connector read/write/compare remained available. No new LAB-086 behavioral, unsafe-seed, compileall, security-reconciliation, or conflict PASS is claimed.

This note freezes the next distinct evidence slice recorded in `state/CURRENT.md` so the run still advances durable architecture without pretending executable proof exists.

## Primary donor mechanisms

1. **TUF root succession** — a new root must be authenticated by threshold signatures from both the trusted predecessor root and the successor root; clients reject rollback and walk every intermediate root. Mechanism reused: transition-time continuity must be proven across authority generations rather than inferred from a self-consistent successor state.
2. **RFC 9162 Certificate Transparency** — a signed tree head authenticates a particular tree state, while a Merkle consistency proof establishes append-only continuity between two heads. Mechanism reused: compact checkpoints do not prove historical continuity merely because each checkpoint is individually signed.
3. **NIST SP 800-226 privacy budget** — privacy budget is an upper bound on cumulative privacy loss across analyses. Mechanism reused: rollback, split/merge, compaction, invalidation, or deletion cannot mint new budget or refund already incurred disclosure.
4. **AWS idempotent mutation guidance** — retries use a stable client token and identical parameters; changed parameters conflict, and some APIs explicitly bound token retention. Mechanism reused: effect identity is immutable and replay safety is scoped to the provider generation/retention contract, not to syntactic receipt validity alone.
5. **Raft joint consensus and snapshots** — old and new configurations cannot safely decide independently during membership change; snapshots carry the latest configuration needed after log compaction. Mechanism reused: compacted membership authority must retain enough transition proof to distinguish committed succession from an uncommitted or forked candidate.

## Frozen contract A — emergency/root authority succession after emergency authority rotation or compromise

### Problem
An emergency authority that was previously the independent escape hatch can itself rotate, fork, or be compromised. A later successor cannot be trusted merely because it signs a new recovery state.

### Required invariant
Every emergency/root succession checkpoint binds: predecessor authority generation, successor generation, recovery floor/head, known competing heads, compromise/revocation facts known at transition time, threshold policy, and authority-path identifier. Normal succession requires predecessor+successor authorization. If the predecessor is already known compromised, it cannot authorize its own escape; succession requires a separately pre-anchored authority path established before compromise.

`successor self-signature != continuity proof`.

### Fail-closed states
- predecessor compromised with no pre-anchored independent escape path -> `RECOVERY_AUTHORITY_UNRECOVERABLE`;
- multiple valid successor heads without an authenticated disambiguating transition -> `RECOVERY_AUTHORITY_FORK`;
- rollback to an earlier emergency/root generation -> reject.

## Frozen contract B — retirement continuity across multiple consecutive disjoint witness-policy transitions

### Problem
A verifier-retirement floor may traverse several witness-policy changes where adjacent or non-adjacent witness sets are disjoint. Equal/higher floors signed by a new set do not prove provenance by themselves.

### Required invariant
Each transition carries an authenticated bridge from `W_i` to `W_i+1`, including floor, policy generation, witness-set digest, threshold, revocations, and predecessor bridge digest. Disjoint transitions require explicit joint authorization by old+new policy or a previously anchored emergency authority. Compaction may collapse a validated chain only by committing the terminal non-resurrection floor and the digest/root of the full bridge chain.

The retirement floor is monotonic and never decreases after revocation, compaction, store loss, or witness replacement.

### Fail-closed states
- missing bridge in a multi-hop chain -> `RETIREMENT_CONTINUITY_UNKNOWN`;
- same floor with conflicting provenance -> do not collapse;
- successor-only statement over a disjoint witness set -> insufficient authority.

## Frozen contract C — unlearning cutover with independent invalidations at destination and retired source

### Problem
During result-store migration, the destination and the retired source may independently receive invalidations while partitioned. Either side can later carry descendants computed from a now-invalid result.

### Required invariant
The migration checkpoint binds source terminal root, destination imported root, theorem/profile generation, migration result set/range, invalidation frontier, descendant-closure root, and source retirement floor. Source and destination invalidation streams retain generation/vector lineage. Reconciliation computes the conservative union/closure of invalidations; a retired source can contribute evidence but never regain positive result authority.

Any descendant whose ancestry crosses an unknown or compacted dependency edge remains non-authoritative until revalidated against the reconciled invalidation closure.

### Fail-closed states
- incomparable invalidation frontiers with missing closure evidence -> `UNLEARNING_DEPENDENCY_UNKNOWN`;
- source rollback before retirement -> reject;
- stale descendant propagated to a third partition -> transitively invalid until exact revalidation succeeds.

## Frozen contract D — privacy branch allocation rollback/overspend with partially compacted event sets

### Problem
Two privacy-accounting branches can receive allocations, independently spend, compact part of their event sets, and later merge or roll back. Treating branch-local remaining budget as fresh authority can overspend the logical lineage.

### Required invariant
All branches share one immutable logical privacy-lineage ID. Allocation checkpoints commit parent allocation, child allocations, accountant generation, event-set root/range, cumulative loss bound, and prior checkpoint digest. Merge authenticates both heads, unions unique released-event identities, rejects same-ID/different-content collisions, and conservatively composes all unique releases. Compaction may replace events with a committed aggregate/root but cannot reduce already-incurred loss absent a reproducible proof over the identical immutable release set.

Rollback of an allocation or accountant generation never restores spent budget. Deleting/invalidating a released result never refunds already incurred privacy loss.

### Fail-closed states
- compacted branch cannot prove which releases its aggregate covers -> `PRIVACY_ACCOUNTING_UNKNOWN`;
- independent branches both claim the parent’s full residual budget -> reject;
- accountant version rollback/equivocation over the same event set -> reject.

## Frozen contract E — provider fork resolution after compensation effects on competing branches

### Problem
Provider-generation forks may each produce authenticated original effects and compensations before the lineage fork is detected or resolved. Receipt signatures prove possible effects, not which branch is authoritative.

### Required invariant
Every effect `E_n` has immutable effect identity, idempotency token, exact parameters, provider generation, predecessor effect (when semantically ordered), and outcome evidence. A compensation is a new effect with its own identity; it never erases the original effect. Fork resolution must first establish authoritative provider-generation lineage, then reconcile the union of effects/compensations known from all branches.

A late authenticated completion on the losing branch remains evidence that an external side effect may have happened and must be reconciled; it cannot be discarded merely because its provider-generation lineage lost authority. Blind replay after idempotency-retention expiry is forbidden unless an independent read/reconciliation proves no effect occurred.

### Fail-closed states
- conflicting `NO_EFFECT` and `COMPLETED` evidence -> `EFFECT_CONFLICT`, reconcile externally;
- compensation outcome unknown -> do not replay original or compensation blindly;
- valid receipt on unresolved generation fork -> evidence only, not mutation authority.

## Frozen contract F — compact GC membership-proof succession across multiple truncated transitions/snapshot generations

### Problem
After several Raft-style membership transitions and snapshots, all detailed joint-consensus log entries may be truncated. A later snapshot can name a current configuration without proving that every transition leading to it committed safely.

### Required invariant
Each compact membership checkpoint binds previous checkpoint, `C_old`, joint configuration, `C_new`, commit/finality evidence, last-included index/term (or equivalent ordering identity), snapshot generation, and scope covered by GC authority. A successor snapshot may compact prior checkpoints only after verifying their full chain and committing its digest/root. Split/merge scopes carry explicit coverage so destructive GC requires proven authority for every covered object/range.

Snapshot presence of `C_new` is not proof that `C_new` committed. Survivors confined to only one side of an unresolved joint transition cannot acquire destructive authority.

### Fail-closed states
- missing compact transition proof after log truncation -> `GC_FINALITY_UNKNOWN`;
- contradictory snapshot generations over the same transition -> fork;
- partial scope coverage -> GC only for the proven subset; never widen by inference.

## 48-case RED-first matrix

### A. Emergency/root succession — A1..A8
1. A1 normal old+new succession, exact bound state -> accept.
2. A2 successor-only self-signed root -> reject.
3. A3 predecessor known compromised before transition and no independent anchor -> unrecoverable.
4. A4 pre-anchored independent emergency path authorizes escape from compromised predecessor -> accept if exact policy satisfied.
5. A5 two valid successor heads from same predecessor -> fork/fail closed.
6. A6 rollback to earlier root generation -> reject.
7. A7 compacted checkpoint omits known competing head -> reject compaction/succession.
8. A8 rotated emergency authority later compromised; recovery through next pre-anchored independent path -> preserve monotonic floor/head.

### B. Multi-transition retirement — B1..B8
9. B1 overlapping witness transition with authenticated bridge -> accept.
10. B2 disjoint witness transition with explicit old+new joint authorization -> accept.
11. B3 disjoint successor-only floor statement -> reject.
12. B4 two consecutive disjoint transitions with complete bridge chain -> accept.
13. B5 missing middle bridge after compaction -> continuity unknown.
14. B6 equal terminal floors with distinct provenance roots -> keep distinct/fail closed on collapse.
15. B7 revoked intermediate policy -> floor remains, authority does not resurrect.
16. B8 destination witness store lost/restored from older checkpoint -> rollback rejected by terminal bridge/floor.

### C. Dual invalidation unlearning cutover — C1..C8
17. C1 source-only invalidation before cutover completes -> propagate to destination reconciliation.
18. C2 destination-only invalidation after import -> authoritative at destination and merge later.
19. C3 independent source+destination invalidations while partitioned -> union/closure on heal.
20. C4 same result invalidated with identical reason/generation lineage -> idempotent merge.
21. C5 conflicting invalidation identity/content -> fail closed.
22. C6 retired source emits new positive result -> reject authority.
23. C7 stale descendant propagated to third partition before heal -> invalid until transitive revalidation.
24. C8 dependency detail compacted and ancestry cannot be proven -> `UNLEARNING_DEPENDENCY_UNKNOWN`.

### D. Privacy allocation/overspend — D1..D8
25. D1 parent allocates disjoint bounded child budgets -> accept.
26. D2 both children independently spend within allocation -> merge cumulative loss.
27. D3 branch rollback attempts to restore already spent allocation -> reject/refund denied.
28. D4 both branches claim full parent residual budget -> detect oversubscription.
29. D5 partial event compaction with exact covered root/range -> merge conservatively.
30. D6 compact aggregate lacks event coverage proof -> accounting unknown.
31. D7 same released-event ID with different content on branches -> reject collision.
32. D8 result deletion/invalidation after release -> privacy loss unchanged.

### E. Provider fork + compensation — E1..E8
33. E1 original effect completed on authoritative branch only -> retain once.
34. E2 original effect completed on losing branch -> retain as possible external effect evidence.
35. E3 compensation completed on competing branch before fork resolution -> reconcile both effects.
36. E4 original `COMPLETED`, compensation `UNKNOWN` -> no blind retry.
37. E5 one branch `NO_EFFECT`, another authenticated `COMPLETED` -> effect conflict.
38. E6 retry same idempotency token + same parameters inside provider window -> same logical effect.
39. E7 same token + changed parameters -> reject conflict.
40. E8 idempotency retention expired with unresolved outcome -> external read/reconciliation required before mutation.

### F. GC membership-proof succession — F1..F8
41. F1 snapshot contains verified old->joint->new compact proof -> destructive GC within bound scope allowed.
42. F2 snapshot merely names `C_new` without transition proof -> reject destructive GC.
43. F3 two successive membership transitions compacted into a verified chained checkpoint -> accept.
44. F4 missing first transition after all detailed logs truncated -> finality unknown.
45. F5 survivor set has old-only quorum during unresolved joint phase -> no destructive authority.
46. F6 survivor set has new-only quorum during unresolved joint phase -> no destructive authority.
47. F7 split/merge GC scopes with only partial compact coverage -> GC only proven subset.
48. F8 contradictory snapshot generations for same membership boundary -> fork/fail closed.

## Cross-contract invariants

- **No self-authenticating succession:** successor state cannot prove its own right to replace predecessor authority.
- **No resurrection by evidence loss:** deleting a source store, witness set, invalidation detail, privacy events, provider receipts, or membership logs never restores retired authority or spent budget.
- **Compaction preserves proof obligations:** a compact root/checkpoint is authority only if it commits the information needed to re-establish the pre-compaction safety property.
- **Fork evidence is not silently discarded:** losing-branch evidence can remain safety-relevant even when it loses authority.
- **Unknown is not false/no-effect:** ambiguous external effects, ancestry, membership finality, or accounting coverage remain unknown and block unsafe mutation.

## Implementation order when exact execution is available

1. Add RED tests for the 48 cases at the owning abstraction layers; do not start with production refactors.
2. Reuse existing monotonic-generation / transition-proof / authenticated-root primitives where possible; avoid parallel authority subsystems.
3. Add compact proof structures only after demonstrating which detailed evidence can be safely discarded.
4. Run owner-specific focused suites, then downstream LAB-080..100 compatibility, unsafe expected-failure seeds, compileall, and security/reconciliation audit.
5. Keep all affected PRs draft until exact published-head execution is clean.

## Sources

- TUF Specification, root update / key migration: https://theupdateframework.github.io/specification/draft/
- RFC 9162, Certificate Transparency Version 2.0: https://www.rfc-editor.org/rfc/rfc9162.html
- NIST CSRC privacy budget / SP 800-226: https://csrc.nist.gov/glossary/term/privacy_budget
- AWS EBS idempotent StartSnapshot requests: https://docs.aws.amazon.com/ebs/latest/userguide/ebs-direct-api-idempotency.html
- AWS ECS idempotency and finite client-token TTL example: https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ECS_Idempotency.html
- Raft extended paper: https://raft.github.io/raft.pdf
