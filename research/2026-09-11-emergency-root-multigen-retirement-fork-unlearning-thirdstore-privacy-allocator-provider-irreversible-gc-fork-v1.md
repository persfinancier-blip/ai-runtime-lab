# MULTIGEN_EMERGENCY_RETIREMENT_FORK_UNLEARNING_THIRDSTORE_PRIVACY_ALLOCATOR_PROVIDER_IRREVERSIBLE_GC_FORK_V1_FROZEN

Date: 2026-09-11
Status: design/evidence freeze only; exact RED/GREEN remains pending
Parent tracking issue: LAB-093 / #178
Priority note: LAB-086 / #163 remains priority #1. This document does not substitute for its executable security gate.

## Per-run execution observation

A fresh direct probe of `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git` failed before repository execution with `Could not resolve host: github.com`. The GitHub connector remains usable for auditable repository reads/writes, but this run exposes no supported primitive that byte-exactly materializes the pinned LAB-086 closure into the local executor. No new LAB-086 behavioral, unsafe-seed, compileall, security-reconciliation, or current-main conflict PASS is claimed here.

## Primary donors re-verified

1. **TUF root succession** — a new root must be authenticated by thresholds from both the immediately trusted predecessor root and the successor root, with monotonic versions and rollback rejection. This is the closest donor for authority-generation succession and demonstrates why a successor cannot self-authenticate a trust transition.
   - https://theupdateframework.github.io/specification/draft/
2. **RFC 9162 Certificate Transparency** — a signed Merkle head is not itself proof of append-only continuity; consistency proofs bind old and new tree states. This is the donor for compact fork/continuity witnesses.
   - https://www.rfc-editor.org/rfc/rfc9162.html
3. **NIST SP 800-226** — privacy budget is an upper bound on cumulative privacy loss across analyses of a dataset; composition accumulates loss rather than refunding it when outputs are deleted or invalidated.
   - https://csrc.nist.gov/pubs/sp/800/226/final
4. **AWS idempotency guidance** — retries of one mutation use a stable client token; same token + same parameters is one logical effect, while token reuse with changed parameters conflicts. Concrete APIs also impose finite token-retention TTLs, so a stale token cannot be assumed to prove no prior external effect indefinitely.
   - https://docs.aws.amazon.com/wellarchitected/latest/framework/rel_prevent_interaction_failure_idempotent.html
   - https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ECS_Idempotency.html
5. **Raft extended paper** — membership transitions require joint consensus; snapshots retain the latest configuration as of the last included index because detailed log entries may be compacted. This is the donor for compact membership-proof succession after transition-log loss.
   - https://raft.github.io/raft.pdf

## Core decision

Compact state is only safe if it preserves the *original proof obligation*, not merely the terminal value. Across all six contracts below, a later object may summarize earlier history, but it may not create authority from its own self-consistency. When predecessor evidence is retired, compacted, partitioned, or compromised, the surviving checkpoint must still bind the lineage, competing heads/forks, policy generation, and any monotonic non-resurrection/non-refund floors that were established before evidence loss.

## Contract A — multi-generation emergency/root cut-set independence after escape authority retirement

### Problem
An emergency escape authority E1 is pre-anchored to recover from compromise of normal authority R0. Later E1 itself retires in favor of E2. If compact state records only `current=E2`, a compromise or fork can make E2 appear self-authorizing, recreating the same bootstrap flaw the emergency path was meant to avoid.

### Frozen invariant
Every emergency-generation transition carries an authenticated predecessor/successor bridge plus an independence certificate for the failure-domain cut set that justified the escape path. Retirement of E1 does not erase the fact that E2's authority was derived through E1. If E1 is known compromised before it authenticated E2, E2 cannot inherit authority from that path; recovery must use a separately pre-anchored independent authority established before compromise.

### Required compact evidence
`{generation, predecessor_generation, predecessor_head, successor_head, policy_generation, cutset_id, independence_domain_set_digest, competing_heads_root, transition_digest, nonrollback_floor}`.

### Fail-closed states
`RECOVERY_SUCCESSOR_SELF_AUTHENTICATING`, `RECOVERY_CUTSET_INDEPENDENCE_UNKNOWN`, `RECOVERY_PREDECESSOR_COMPROMISED_BEFORE_BRIDGE`, `RECOVERY_FORK_UNRESOLVED`.

## Contract B — retirement witness-policy fork resolution after bridge-chain compaction

### Problem
Several consecutive verifier-retirement transitions use disjoint witness policies. Detailed bridge records are later compacted. Two partitions may retain different terminal compact chains with the same non-resurrection floor but incompatible bridge provenance.

### Frozen invariant
Equal terminal floors are not sufficient for equivalence. A compact retirement checkpoint must commit to the ordered bridge-chain root and witness-policy generations. Fork resolution requires a common authenticated ancestor or an independently pre-anchored reconciliation authority; selecting the numerically highest floor is insufficient. Once any verifier generation is retired, no reconciliation may lower its retirement floor.

### Required compact evidence
`{terminal_floor, chain_root, first_generation, last_generation, witness_policy_root, revoked_bridge_root, competing_chain_heads_root}`.

### Fail-closed states
`RETIREMENT_CHAIN_FORK`, `RETIREMENT_PROVENANCE_UNKNOWN`, `RETIREMENT_RECONCILIATION_NO_COMMON_ANCESTOR`, `RETIREMENT_FLOOR_REGRESSION`.

## Contract C — unlearning invalidation-vector compaction after descendants crossed a third store

### Problem
A model/result moves source S1 -> S2 while invalidation evidence is in flight. Before convergence, descendants derived from the stale object are copied to S3. Later S1/S2 detailed dependency edges are compacted, leaving only local invalidation vectors.

### Frozen invariant
Invalidation authority is transitive across migration boundaries. Compaction must preserve a lineage/vector summary sufficient to prove descendant closure across all stores that could have received descendants. A store that cannot prove whether its object descends from a pre-invalidation ancestor cannot return an authority-bearing positive result; it must enter `UNLEARNING_DEPENDENCY_UNKNOWN` until exact revalidation or conservative invalidation completes.

### Required compact evidence
`{lineage_id, invalidation_epoch_vector, migration_edges_root, descendant_frontier_root, participating_store_set, compacted_ancestry_root}`.

### Fail-closed states
`UNLEARNING_VECTOR_FORK`, `UNLEARNING_DESCENDANT_CLOSURE_UNKNOWN`, `UNLEARNING_THIRD_STORE_UNACCOUNTED`, `UNLEARNING_PREINVALIDATION_DESCENDANT_REJOIN`.

## Contract D — delegated privacy-allocation reconciliation after allocator-generation compromise

### Problem
A root privacy accountant delegates budget slices to allocators A1/A2. A1 spends part of its allocation, then its generation is compromised and rotated. A stale snapshot can make A1's old delegation look unspent, or two restored branches can each present the original allocation as available.

### Frozen invariant
Delegation partitions one logical privacy budget; it does not mint independent budgets. Reconciliation is over immutable release-event IDs plus allocation/delegation lineage. Rotation or compromise may invalidate *authority to spend further*, but it never refunds privacy loss already incurred. Same event ID with different canonical release content is a hard collision, not deduplication.

### Required compact evidence
`{dataset_lineage_id, allocator_generation, delegation_id, parent_allocation_id, allocation_bound, spent_event_root, revoked_generation_root, reconciliation_epoch}`.

### Fail-closed states
`PRIVACY_ALLOCATION_FORK`, `PRIVACY_DELEGATION_REPLAY`, `PRIVACY_EVENT_ID_COLLISION`, `PRIVACY_BUDGET_OVERRUN`, `PRIVACY_SPEND_PROVENANCE_UNKNOWN`.

## Contract E — provider fork resolution with irreversible/non-compensable external effect

### Problem
Provider-generation fork P1/P2 occurs. P1 executes an irreversible external effect E1 (for example, an external publication or deletion with no true inverse). P2 becomes preferred and later observes a valid receipt from P1. A compensation workflow cannot safely pretend E1 was erased.

### Frozen invariant
Receipt authenticity and lineage authority are separate. A valid losing-branch receipt remains evidence that the external world may contain E1. Non-compensable or irreversible effects are monotonic facts in the effect ledger. Fork resolution may select one provider lineage for future authority but cannot rewrite E1 to `NO_EFFECT`; downstream state must reconcile or quarantine around the surviving external fact. After provider idempotency retention expires, unknown E1 outcome forbids blind replay.

### Required compact evidence
`{effect_id, idempotency_token, canonical_request_digest, provider_generation, branch_id, receipt_digest, outcome_class, reversibility_class, compensation_effect_id?, retention_deadline}`.

### Fail-closed states
`PROVIDER_EFFECT_UNKNOWN`, `PROVIDER_IRREVERSIBLE_FORK_EFFECT`, `PROVIDER_RECEIPT_LINEAGE_CONFLICT`, `PROVIDER_IDEMPOTENCY_RETENTION_EXPIRED`, `PROVIDER_COMPENSATION_NOT_AN_INVERSE`.

## Contract F — GC membership-proof fork after replicated compact snapshots and total transition-log loss

### Problem
Raft-like membership changes C0 -> Joint01 -> C1 -> Joint12 -> C2 are committed and then compacted. Different partitions replicate snapshots that both claim C2 but carry conflicting compact membership-proof roots; all detailed transition log entries are gone.

### Frozen invariant
A snapshot naming C2 does not prove the membership transition path. Compact state must bind the latest committed configuration plus proof of every compacted membership transition needed to establish quorum-intersection continuity. If replicated snapshots disagree on this proof lineage and no surviving common authenticated ancestor/reconciliation proof exists, neither partition gets destructive GC authority. One-sided survivors of an unresolved joint configuration likewise cannot authorize destructive collection.

### Required compact evidence
`{snapshot_generation, last_included_index, last_included_term, current_config, membership_chain_root, joint_transition_root, competing_snapshot_heads_root, scope_coverage_root}`.

### Fail-closed states
`GC_MEMBERSHIP_PROOF_FORK`, `GC_JOINT_FINALITY_UNKNOWN`, `GC_SNAPSHOT_PROVENANCE_UNKNOWN`, `GC_DESTRUCTIVE_AUTHORITY_WITHHELD`.

## 48-case RED-first matrix

### A. Emergency/root cut-set independence
A1. R0 -> E1 -> E2 normal chain; E2 compact checkpoint verifies.
A2. E2 self-signed with no E1 bridge; reject.
A3. E1 compromised before E1->E2 bridge; reject E2 authority.
A4. E1 compromised after valid E1->E2 bridge; preserve E2 if bridge predates compromise and cut-set remains independent.
A5. Same E2 head but altered independence-domain set; reject.
A6. Two E2 competing heads from one E1; mark fork unresolved.
A7. Compact checkpoint omits known competing E2 head; reject incomplete recovery evidence.
A8. E2 retires to E3 with disjoint independent cut set; require authenticated E2/E3 transition and nonrollback floor.

### B. Retirement bridge-chain fork
B1. Three disjoint witness-policy transitions with intact chain; accept terminal floor.
B2. Same floor, different chain roots; do not collapse as equivalent.
B3. Fork A contains revoked bridge that fork B omits; reject B as incomplete.
B4. Highest numeric floor lacks authenticated common ancestor; reject winner-by-number.
B5. Common ancestor + authenticated reconciliation bridge; accept reconciled chain.
B6. Compaction removes intermediate witnesses but preserves chain root and policy generations; accept if proof verifies.
B7. Reconciliation proposes lower terminal floor; reject.
B8. All detailed bridges gone and compact chain proof missing; `RETIREMENT_PROVENANCE_UNKNOWN`.

### C. Unlearning third-store closure
C1. S1->S2 migration, invalidation converges before S3 derivation; S3 positive result may remain if ancestry proves post-invalidation recomputation.
C2. S3 descendant created from stale S2 before invalidation; invalidate transitively.
C3. S3 receives descendant directly from retired S1; retired S1 evidence informs invalidation but grants no positive authority.
C4. Local S2 compaction drops ancestry edge to S1; mark dependency unknown, not clean.
C5. Vector merge across S1/S2/S3 has incomparable epochs; conservatively union invalidations.
C6. S3 rejoins with pre-invalidation descendant after S1/S2 advanced; reject positive result until catch-up/revalidation.
C7. Migrated object ID reused for different lineage; hard collision.
C8. Third-store set itself is incomplete after compaction; withhold authority-bearing result.

### D. Privacy delegated allocation
D1. Parent budget delegates 0.4 to A1 and 0.6 to A2; aggregate spend <= 1.0 accepted.
D2. A1 spends 0.3 then rotates; new A1 generation sees remaining 0.1, not 0.4.
D3. Restore pre-spend A1 snapshot after rotation; replayed allocation rejected.
D4. A1 and A2 restored independently and both claim same parent residual; reconciliation detects over-allocation.
D5. Same release-event ID appears on both branches with identical canonical content; deduplicate once.
D6. Same release-event ID appears with different content/epsilon; hard collision.
D7. Result deletion after A1 compromise; no refund of incurred spend.
D8. Accountant-version change yields tighter bound only from reproducible recomputation over identical immutable release-event set; otherwise keep conservative bound.

### E. Irreversible provider effect
E1. Preferred branch executes reversible effect with confirmed compensation; record both effect IDs, never erase original.
E2. Losing branch executes irreversible E1; preferred branch must retain external-effect fact.
E3. Valid receipt from losing branch but no authoritative provider lineage; receipt proves possible/actual effect, not future authority.
E4. Unknown E1 outcome before idempotency TTL expiry; retry only with identical token+parameters.
E5. Unknown E1 outcome after TTL expiry; no blind retry, require external reconciliation.
E6. Compensation endpoint reports success for a non-invertible effect; classify as new effect, not inverse proof.
E7. Two branches produce receipts for same token with different canonical parameters; hard generation/receipt conflict.
E8. Reconciliation chooses P2 for future authority while E1 from P1 persists externally; system remains usable only with explicit reconciled external-state fact or quarantine.

### F. GC snapshot/membership fork
F1. C0->Joint01->C1->Joint12->C2 committed; snapshot carries complete membership-chain proof; accept C2.
F2. Snapshot says C2 but omits Joint12 proof; withhold destructive authority.
F3. Two snapshots same C2/config but different chain roots; mark fork.
F4. Partition A proves only old side of Joint12, partition B only new side; neither may destructively GC.
F5. Common authenticated predecessor snapshot plus valid compact transition proof resolves fork; accept successor.
F6. Snapshot lastIncludedIndex/term conflicts with membership proof boundary; reject.
F7. All transition logs truncated and one snapshot loses membership-chain root; `GC_SNAPSHOT_PROVENANCE_UNKNOWN`.
F8. Scope coverage differs across forked snapshots; destructive GC limited to intersection only if independently proven safe; otherwise withhold.

## Implementation notes for later RED/GREEN

- Keep proof objects immutable and domain-separated; do not reuse a generic digest without a type/version tag.
- Persist monotonic floors separately from liveness/current-head convenience indexes.
- Treat compact checkpoints as authenticated summaries of prior evidence, not replacements that can be regenerated from current mutable state.
- For fork resolution, compare canonical lineage/proof roots before accepting equal terminal values.
- Tests must include restart/recovery and post-compaction paths; in-memory happy paths are insufficient.
- Negative tests must verify fail-closed behavior occurs before destructive/provider/SQL mutation wherever that is the safety boundary.

## Audit

This freeze deliberately avoids claiming executable correctness. It extends the architecture only where the new failure modes are distinct from prior frozen contracts. The largest residual engineering risk is still the widening gap between design-frozen contracts and exact executable gates. LAB-086 remains the mandatory first probe on the next run; if exact source materialization becomes available, execution work supersedes further design expansion.
