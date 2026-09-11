# OVERLAP_EMERGENCY_RETIREMENT_REVOCATION_UNLEARNING_REMIGRATION_PRIVACY_DUAL_SPEND_PROVIDER_DELAYED_OBSERVATION_GC_BOUNDARY_V1_FROZEN

Date: 2026-09-12
Status: design/evidence freeze only; exact RED/GREEN remains pending
Parent tracking issue: LAB-093 / #178
Priority note: LAB-086 / #163 remains priority #1. This document does not substitute for its executable security gate.

## Per-run execution observation

A fresh direct probe of `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git` failed before repository execution with `Could not resolve host: github.com`. GitHub connector reads/writes remain available, but this run still exposes no supported non-model primitive that byte-exactly materializes pinned LAB-086 source into the local executor. No new LAB-086 behavioral, unsafe-seed, compileall, security-reconciliation, or conflict PASS is claimed.

## Primary donors re-verified

1. **TUF 1.0.36 root succession** — successor trust is derived through authenticated predecessor/successor transition with monotonic versioning and rollback rejection. A successor does not become trusted merely because it is internally self-consistent.
   - https://theupdateframework.github.io/specification/latest/
2. **RFC 9162 Certificate Transparency** — Merkle consistency proofs prove that one authenticated tree state extends another; a signed tree head alone does not prove append-only continuity or reconcile equivocation.
   - https://www.rfc-editor.org/rfc/rfc9162.html
3. **NIST SP 800-226** — privacy budget bounds cumulative privacy loss across analyses; composition accumulates spend rather than granting a fresh budget after rollback, deletion, or allocator replacement.
   - https://csrc.nist.gov/pubs/sp/800/226/final
4. **AWS idempotency semantics** — same token + same parameters represents one logical mutation only within the provider's retained idempotency window; changed parameters conflict, and finite retention means old tokens cannot indefinitely prove absence of a prior effect.
   - https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ECS_Idempotency.html
   - https://docs.aws.amazon.com/ec2/latest/devguide/ec2-api-idempotency.html
5. **Raft extended paper** — membership change safety depends on joint consensus and snapshots preserve `last included index/term` plus the latest configuration because detailed log entries may be discarded.
   - https://raft.github.io/raft.pdf

## Core decision

For all six contracts, reconciliation authority must be derived from preserved continuity evidence, not from whichever terminal object is newest, numerically highest, locally signed, or most available. Partial overlap is not equivalent to independence, equal terminal values are not equivalent when provenance forks, and delayed observation does not erase already possible external effects. Compact evidence may summarize history only if it preserves the proof obligation needed to distinguish valid succession from rollback/equivocation.

## Contract A — emergency/root cut-set renewal with partially overlapping escape domains

### Problem
Successive emergency authorities E1 -> E2 -> E3 rotate their signer/failure domains. E2 and E3 are each threshold-valid, but their domain sets partially overlap with the authority they are intended to escape. A compromise affecting the overlap can create two apparently valid successors from the same predecessor.

### Frozen invariant
Cut-set safety is evaluated over failure domains, not signer count alone. Every transition records the predecessor/successor domain sets and the minimum independent cut-set actually required by policy. A later transition may reuse domains only if the authenticated policy explicitly permits the resulting overlap and the surviving independent subset still satisfies the escape requirement. If compromise covers all independent domains connecting predecessor to successor, successor authority is not recoverable from that chain.

### Required compact evidence
`{generation, predecessor_head, successor_head, policy_generation, predecessor_domain_root, successor_domain_root, overlap_root, required_independent_cutset, satisfied_cutset_root, known_compromise_root, competing_heads_root}`.

### Fail-closed states
`RECOVERY_CUTSET_OVERLAP_UNSAFE`, `RECOVERY_INDEPENDENCE_PROOF_MISSING`, `RECOVERY_COMPROMISE_COVERS_BRIDGE`, `RECOVERY_SUCCESSOR_FORK`.

## Contract B — mutually exclusive retirement revocations after bridge-chain compaction

### Problem
Two compact retirement forks share a historical floor but each contains a valid revocation statement that excludes the witness set used by the other fork. Both chains are locally authentic and neither can simply be chosen by highest generation/floor.

### Frozen invariant
Revocation is monotonic against the authority it names, but revocation provenance itself must be ordered. Mutually exclusive revocations with no authenticated ordering/common successor produce an unresolved authority fork. Reconciliation must preserve the maximum proven non-resurrection floor while withholding any future authority whose derivation depends on a witness set revoked by an incomparable branch.

### Required compact evidence
`{terminal_floor, chain_root, revocation_set_root, revocation_order_root, witness_policy_root, common_ancestor_head, competing_chain_heads_root}`.

### Fail-closed states
`RETIREMENT_REVOCATION_FORK`, `RETIREMENT_REVOCATION_ORDER_UNKNOWN`, `RETIREMENT_WITNESS_SET_INCOMPARABLE`, `RETIREMENT_FUTURE_AUTHORITY_WITHHELD`.

## Contract C — third-store descendant remigration after unlearning compaction

### Problem
A stale descendant reaches S3 before invalidation convergence. S1/S2 compact detailed ancestry. Later the S3 descendant migrates to S4 and S3 is retired. A local S4 checkpoint can look clean even though its only ancestor proof was already stale/unknown.

### Frozen invariant
Unknown ancestry propagates across migration. Remigration cannot upgrade `dependency unknown` into `clean`; it carries the strongest invalidation/uncertainty state until exact lineage proof or conservative invalidation resolves it. Store retirement removes mutation authority but not lineage evidence required to classify descendants.

### Required compact evidence
`{lineage_id, object_generation, source_store, destination_store, migration_epoch, ancestry_root, invalidation_vector_root, uncertainty_floor, retired_store_root, descendant_frontier_root}`.

### Fail-closed states
`UNLEARNING_REMIGRATION_WITH_UNKNOWN_ANCESTRY`, `UNLEARNING_RETIRED_SOURCE_PROOF_MISSING`, `UNLEARNING_VECTOR_ROLLBACK`, `UNLEARNING_DESCENDANT_CLOSURE_UNKNOWN`.

## Contract D — concurrent near-limit privacy spend across allocator generations

### Problem
Allocator generation A1 has nearly exhausted a delegated parent budget when A2 is activated. During a partition both independently authorize spends near the remaining limit. Each branch is locally within its apparent allocation, but the union exceeds the parent budget.

### Frozen invariant
Allocator generation changes never create parallel residual budgets. Spend authorization requires a parent-lineage checkpoint or lease whose scope prevents simultaneous reuse of the same residual budget. During reconciliation, immutable release-event sets are unioned and cumulative privacy loss is recomputed conservatively. If the union exceeds the parent limit, the budget is exhausted/overrun; reconciliation cannot discard one valid disclosure to manufacture headroom.

### Required compact evidence
`{dataset_lineage_id, parent_budget_id, allocator_generation, allocation_epoch, allocation_bound, residual_checkpoint, spend_event_root, branch_head, revocation_epoch}`.

### Fail-closed states
`PRIVACY_CONCURRENT_RESIDUAL_REUSE`, `PRIVACY_ALLOCATION_GENERATION_FORK`, `PRIVACY_PARENT_BUDGET_OVERRUN`, `PRIVACY_RECONCILIATION_CANNOT_REFUND`.

## Contract E — delayed external observation contradicts provider branch-local receipts

### Problem
Provider branch P1 records `NO_EFFECT` or timeout-derived local state, while P2 proceeds. Later an independent external observation proves that P1's mutation actually occurred. Conversely, a branch-local `COMPLETED` receipt may later conflict with authoritative external state indicating the effect never materialized or was independently reverted.

### Frozen invariant
Branch-local receipt status, transport outcome, and externally observed world state are separate evidence classes. `NO_EFFECT` requires positive provider evidence, not merely timeout/absence. A later authenticated observation that proves an effect occurred upgrades the monotonic effect ledger even if the producing branch lost authority. Conflicting authenticated observations create an explicit evidence fork/quarantine; they are not resolved by rewriting history. Retry after idempotency retention expiry remains prohibited while outcome is unknown.

### Required compact evidence
`{effect_id, canonical_request_digest, idempotency_token, provider_generation, branch_id, receipt_status, receipt_digest, observation_epoch, observation_source_root, observed_world_state_digest, retention_deadline}`.

### Fail-closed states
`PROVIDER_DELAYED_EFFECT_DISCOVERY`, `PROVIDER_RECEIPT_OBSERVATION_CONFLICT`, `PROVIDER_EFFECT_STATE_FORK`, `PROVIDER_REPLAY_UNSAFE_AFTER_RETENTION`.

## Contract F — GC membership-chain reconciliation across different snapshot boundaries

### Problem
Two compact snapshots overlap in membership history but have different `lastIncludedIndex/Term` boundaries. Detailed transition entries below both boundaries are gone. The only overlap is a compact certificate for a joint-consensus transition.

### Frozen invariant
Snapshot freshness by index does not itself dominate membership provenance. Reconciliation must prove that both snapshots commit to the same joint transition and that the later boundary extends the earlier committed state without skipping/replacing membership authority. A compact joint certificate must bind old config, new config, joint config, transition index/term, and predecessor membership root. If boundary/proof roots are incompatible, destructive GC authority is withheld even if both snapshots name the same terminal configuration.

### Required compact evidence
`{snapshot_generation, last_included_index, last_included_term, current_config, predecessor_membership_root, joint_certificate_root, membership_chain_root, scope_coverage_root, competing_snapshot_heads_root}`.

### Fail-closed states
`GC_SNAPSHOT_BOUNDARY_FORK`, `GC_JOINT_CERTIFICATE_MISMATCH`, `GC_MEMBERSHIP_EXTENSION_UNPROVEN`, `GC_DESTRUCTIVE_AUTHORITY_WITHHELD`.

## 48-case RED-first matrix

### A. Partial-overlap emergency cut sets
A1. E1->E2 disjoint independent domains satisfy policy; accept.
A2. E2->E3 reuses one domain but still retains policy-required independent subset; accept with explicit overlap evidence.
A3. Threshold signer count passes but all signers map to one compromised failure domain; reject.
A4. Compromise covers only overlapping domains while independent bridge survives; preserve successor authority.
A5. Compromise covers every independent bridge domain before transition; reject successor derivation.
A6. Same successor head with altered domain mapping; reject.
A7. Two threshold-valid successors use overlapping cut sets from one predecessor; mark fork.
A8. Compaction drops overlap/cut-set proof and retains only signer IDs; independence unknown, reject.

### B. Mutually exclusive retirement revocations
B1. Ordered revocation R1 then R2 with authenticated bridge; accept terminal chain.
B2. Fork A revokes witness set WB; fork B depends on WB and has no later ordering proof; withhold B authority.
B3. Fork B revokes WA while A depends on WA; both locally valid; unresolved fork.
B4. Both forks share the same non-resurrection floor; do not collapse provenance.
B5. Authenticated common successor orders both revocations and preserves maximum floor; accept reconciliation.
B6. Reconciliation omits one known revocation; reject incomplete checkpoint.
B7. A revoked witness set is reintroduced under a renamed policy without independent reauthorization; reject.
B8. Detailed revocation records compacted but ordered revocation root verifies; accept compact proof.

### C. Third-store remigration
C1. S3 descendant has exact post-invalidation ancestry then migrates to S4; accept lineage.
C2. S3 descendant ancestry is unknown and migrates to S4; S4 remains unknown.
C3. S3 retires after migration; S4 must retain compact lineage proof to retired S3.
C4. S4 checkpoint drops retired-store lineage root; reject positive authority.
C5. S3 and S4 invalidation vectors are incomparable; conservatively union invalidations.
C6. S4 later obtains exact proof descendant was derived before invalidation; invalidate.
C7. S4 obtains exact post-invalidation recomputation proof; may clear uncertainty for that object only.
C8. Object ID reused during remigration for different lineage; hard collision.

### D. Concurrent privacy spend
D1. Parent residual 0.2 leased exclusively to A2; A1 cannot spend after revocation checkpoint; accept A2 spend <=0.2.
D2. A1 spends 0.15 and A2 independently spends 0.15 from the same apparent residual 0.2; reconciliation detects 0.3 union and overrun.
D3. Both branches use identical release-event ID/content; deduplicate once.
D4. Same event ID carries different epsilon/content; hard collision.
D5. A1 result deleted before merge; spend remains counted.
D6. A2 accountant version computes tighter bound over identical immutable event set; allow only reproducible conservative transition.
D7. Branch rollback restores pre-spend residual; do not restore spend authority.
D8. Parent allocation proof missing after partition heal; freeze new spend until reconciliation.

### E. Delayed provider observation
E1. Timeout with no positive provider evidence; classify UNKNOWN, not NO_EFFECT.
E2. Later external observation proves effect occurred; record effect despite losing branch.
E3. Local receipt says NO_EFFECT but authenticated provider audit proves completion; conflict/quarantine and retain possible effect.
E4. Local receipt says COMPLETED but independent provider audit proves rejected request; mark evidence fork rather than silently erasing receipt.
E5. Same token+same request retried inside retention window; one logical effect.
E6. Same token+changed request inside retention window; conflict.
E7. UNKNOWN after retention expiry; forbid blind replay.
E8. Compensation occurs before delayed discovery of original effect; retain both immutable effect identities and reconcile net external state explicitly.

### F. Different GC snapshot boundaries
F1. S1 boundary i=100 and S2 boundary i=150 share identical authenticated joint certificate at i=120; prove S2 extension and accept later chain.
F2. S2 names same terminal config but its joint certificate root differs; fork.
F3. S2 lastIncludedTerm conflicts with certificate transition term; reject.
F4. S1 retains predecessor membership root omitted by S2; without compact successor proof S2 cannot dominate.
F5. Common joint certificate binds old/new config and predecessor root; detailed transition logs may be absent if chain verifies.
F6. Higher snapshot index with lower/older membership-chain generation; reject winner-by-index.
F7. One partition has only old-side quorum evidence, another only new-side evidence; neither gets destructive authority.
F8. Authenticated reconciliation certificate links both snapshot heads and scope coverage; accept successor only after proof verifies.

## Implementation notes for later RED/GREEN

- Map signer IDs to explicit failure-domain IDs before evaluating independence; threshold cardinality is not an independence proof.
- Revocation checkpoints require ordered provenance and a monotonic non-resurrection floor separate from current-head convenience state.
- Propagate `dependency unknown` as a first-class monotonic safety state across migrations until exact proof resolves it.
- Privacy events require immutable globally scoped identities and canonical content digests; allocation generations must not each own a fresh residual copy.
- Provider effect ledger should distinguish `transport_outcome`, `provider_receipt`, `external_observation`, and `authority_lineage` rather than collapsing them into one status enum.
- GC compact joint certificates must bind transition index/term and both configuration sets; snapshot index ordering alone is insufficient.
- Negative tests must assert fail-closed behavior before destructive/provider/SQL mutation wherever possible.

## Audit

This slice is intentionally architecture/evidence only. It extends prior frozen contracts only for failure modes introduced by partial failure-domain overlap, mutually exclusive revocation provenance, remigration after ancestry compaction, concurrent residual-budget reuse, delayed external observations, and cross-boundary compact membership reconciliation. No executable correctness claim is made. LAB-086 remains the mandatory first probe next run; exact source execution supersedes further design work immediately if a supported materialization path becomes available.
