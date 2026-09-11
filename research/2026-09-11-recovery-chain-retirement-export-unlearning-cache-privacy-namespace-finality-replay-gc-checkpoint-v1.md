# Recovery-chain compromise, retirement-floor export, unlearning cache invalidation, privacy namespace split/merge, finality replay, and GC checkpoint authority

Date: 2026-09-11
Status: DESIGN FROZEN / RED-FIRST; executable RED/GREEN still pending
Contract: `RECOVERY_CHAIN_RETIREMENT_EXPORT_UNLEARNING_CACHE_PRIVACY_NAMESPACE_FINALITY_REPLAY_GC_CHECKPOINT_V1_FROZEN`

## Scope

This is the next distinct LAB-093 evidence slice while LAB-086 remains blocked on byte-exact source materialization. It does **not** substitute for LAB-086 execution. It freezes six failure-boundary contracts that become relevant after the previously frozen repair/revocation/compaction work:

1. recovery repair-chain trust when an intermediate repaired anchor and a successor assessment authority are both later compromised;
2. export/migration of a compact verifier-retirement non-resurrection floor across a trust-root rotation without resurrecting retired verifier authority;
3. invalidation of unlearning descendant/result caches after ancestor theorem/profile revalidation changes generation;
4. privacy-budget namespace split/merge across participant-set transitions without double-spend or refund;
5. provider/finality effect-ledger replay after membership recovery and cache compaction;
6. authority loss/revocation of a compact GC checkpoint after detailed historical evidence has already crossed its retention boundary.

## Primary-source mechanisms re-verified

### TUF root-transition discipline

The Update Framework requires root N+1 to be validated by the threshold from trusted root N and by the threshold from root N+1, and requires monotonic root versions to detect rollback. This is a useful donor for recovery-chain transitions because a successor cannot simply self-authorize away predecessor trust.

- TUF specification index: https://theupdateframework.github.io/specification/
- Root update workflow: https://theupdateframework.github.io/specification/draft/#update-the-root-role
- Accessed: 2026-09-11.

### RFC 9162 append-only consistency

Certificate Transparency v2 distinguishes inclusion from consistency and uses Merkle consistency proofs to establish that a later authenticated tree extends an earlier tree. A signed head alone is not enough to prove continuity, and inconsistent views must remain detectable.

- RFC 9162: https://www.rfc-editor.org/rfc/rfc9162.html
- Accessed: 2026-09-11.

### NIST SP 800-226 cumulative privacy loss

NIST defines privacy budget as an upper bound on allowable **cumulative** privacy loss across analyses on one dataset. Repartitioning namespaces or participants therefore cannot mint fresh budget or refund already consumed loss.

- NIST SP 800-226 publication page: https://www.nist.gov/publications/guidelines-evaluating-differential-privacy-guarantees
- NIST glossary, privacy budget: https://csrc.nist.gov/glossary/term/privacy_budget
- Accessed: 2026-09-11.

### Raft joint-consensus membership changes

Raft's extended paper rejects direct old-to-new configuration switches because old and new configurations can form disjoint majorities. The safe transition uses a joint configuration before the new configuration becomes authoritative.

- Raft publication index: https://raft.github.io/
- Extended paper: https://raft.github.io/raft.pdf
- Accessed: 2026-09-11.

## Contract A — repair-chain trust after double compromise

### Threat

A recovery chain may contain `A0 -> R1 -> A2`, where `R1` repaired an earlier compromised anchor and `A2` later assessed/authorized the repaired state. If evidence later shows both `R1` and the authority that issued `A2` were compromised for overlapping intervals, naive validation can accidentally treat `A2` as an independent confirmation even though its trust depended on `R1`.

### Frozen rules

1. Every repair/assessment edge commits: predecessor head(s), successor head, policy generation, canonical failure-domain set, evidence cutoff, and compromise interval.
2. Trust is evaluated over the **dependency graph and time intervals**, not by signature count alone.
3. If a successor authority is derived from, provisioned by, or shares a canonical failure domain with the compromised intermediate, it is not independent evidence for that interval.
4. A later recovery generation may restore authority only if it commits every still-live conflicting head, the last undisputed safety floor, and all compromise assessments needed to justify domain filtering.
5. Same-generation alternative repair heads are a fork. Timestamp, arrival order, lexical ID, or lower-cost path never resolves it.
6. A repaired state never lowers previously established non-resurrection, privacy, effect-unknown, or GC-retention safety floors.
7. Unknown dependency/failure-domain edges are treated as potentially correlated until resolved.
8. Historical signatures remain evidence of what was asserted; compromise can invalidate their authority without deleting that history.

## Contract B — compact retirement floor export across root rotation

### Threat

Detailed verifier-retirement continuity evidence may be compacted into a smaller authenticated non-resurrection floor. Later, trust roots rotate or the store is exported. If the compact floor is imported as ordinary live authority under the new root, an old retired verifier can accidentally regain authority because the original detailed bridge is gone.

### Frozen rules

1. A compact retirement floor has an explicit type: `NON_RESURRECTION_FLOOR`, never `LIVE_VERIFIER_CERTIFICATE`.
2. Export commits the old trust-root generation, retirement-set digest, minimum retirement generation, compaction epoch, evidence-retention class, and source checkpoint head.
3. Root rotation authenticates an **export bridge** under both admissible predecessor and successor trust according to the configured transition policy; the successor root does not self-certify imported history.
4. Import preserves the floor monotonically: the successor may retire more authority but cannot unretire any identity contained in the exported floor.
5. If continuity from the compact floor to the export bridge is no longer provable, the result is `RETIREMENT_CONTINUITY_UNCERTAIN`; the system may fail closed but must not resurrect authority.
6. Re-encoding or namespace migration does not change the semantic retirement identity set; canonical identity mapping is committed before deletion of the old representation.
7. A revoked export bridge invalidates its continuity claim but does not reverse the retirement floor already enforced.
8. Detailed evidence can be deleted only after the compact floor and export bridge are durably authenticated and all explicit audit dependencies are closed.

## Contract C — unlearning descendant/result-cache invalidation

### Threat

An unlearning certificate can have cached descendants/results based on theorem/profile generation G. If an ancestor is revalidated under generation G+1, a cache keyed only by model/data/result identity can continue serving conclusions proved under obsolete assumptions.

### Frozen rules

1. Every reusable unlearning result/cache entry commits the exact theorem/profile generation and all ancestor certificate generations on which it depends.
2. Ancestor revalidation creates a new status generation even if the final verdict remains valid.
3. Any generation change invalidates dependent cache entries until they are re-proved or explicitly revalidated against the new dependency vector.
4. Revalidation and descendant issuance are snapshot/CAS linearized: a descendant prepared against G cannot commit after the ancestor advances to G+1.
5. Re-proof of one descendant does not transitively validate siblings.
6. Negative/revoked ancestor status dominates stale positive caches.
7. Cache compaction may summarize invalidation state, but a summary cannot fabricate a positive proof that no retained dependency proves.
8. Unknown ancestor status fails closed for authority-bearing outputs; it may remain visible as historical evidence.

## Contract D — privacy namespace split/merge without double-spend or refund

### Threat

A participant set may split one accounting namespace into multiple shards and later merge them. If each child namespace inherits the parent's remaining budget independently, the system double-spends. If merge chooses a minimum observed spend or drops orphaned reservations, it refunds privacy loss.

### Frozen rules

1. Namespace lineage has one immutable root budget identity; split children carry disjoint allocation entitlements whose union is bounded by the parent's remaining entitlement.
2. Consumed privacy loss remains attached to the root lineage and is never reset by split, merge, coordinator failover, participant removal, or namespace rename.
3. Outstanding reservations are conservatively inherited by all reconciliation paths until uniquely assigned/released under authenticated evidence.
4. Split commits a participant-set generation and an allocation vector whose sum does not exceed available budget after consumed loss and reservations.
5. Merge computes a conservative union/sum according to the accounting mechanism; it never selects the least-spent child view.
6. Concurrent split/merge heads form a namespace fork. No child may spend against both branches.
7. Coordinator failover preserves root lineage, generation, consumed floor, and unresolved reservations.
8. An unreachable/unknown participant blocks refund/release of its potentially live reservation; availability never wins over cumulative-loss safety.

## Contract E — provider/finality effect-ledger replay after recovery

### Threat

After replica-membership recovery and finality-cache compaction, the runtime may replay an effect ledger to reconstruct state. If replay trusts compact cache entries without the membership/finality generation that authorized them, stale `FINAL` or `NO_EFFECT` claims can be reintroduced after authority revocation.

### Frozen rules

1. Every effect-ledger decision commits the effect ID, operation digest, provider generation, finality-authority generation, membership generation, evidence checkpoint, and decision status.
2. Replay is generation-aware and dependency-aware. A compact cache entry is only a performance hint until its authority chain is re-established.
3. Revoked/compromised finality authority invalidates affected cached decisions and reclassifies destructive effects to `EFFECT_UNKNOWN` unless independent evidence re-proves the decision.
4. `NO_EFFECT` is authority-bearing and is invalidated under the same rules as `FINAL`.
5. Membership recovery uses joint-consensus continuity; old-only or new-only quorum cannot independently bless an overlap interval.
6. Duplicate replay is idempotent by immutable effect identity and cannot execute a provider side effect a second time.
7. Missing compacted dependency evidence fails closed; replay must not infer finality from the current provider state alone.
8. Reconciliation may append a new decision generation but cannot rewrite the historical decision that was actually observed.

## Contract F — compact GC checkpoint authority loss after retention boundary

### Threat

Detailed destructive-GC proof evidence may legitimately age out after a compact checkpoint is created. If the checkpoint's signing/authorization authority is later revoked or shown compromised, the system can no longer reconstruct the deleted evidence. Treating the compact checkpoint as permanently authoritative would make retention destroy the ability to react to later compromise.

### Frozen rules

1. A compact GC checkpoint commits the immutable graph snapshot/epoch, SCC/fixed-point result digest, destructive action set, membership generation, authority generation, retention policy, and detailed-evidence cutoff.
2. Crossing the retention boundary is allowed only after the checkpoint is independently authenticated and all then-known dependencies are closed.
3. Later authority compromise/revocation marks the checkpoint `AUTHORITY_UNCERTAIN` for future authority decisions even if detailed evidence is gone.
4. Already-executed physical destruction is a historical fact and cannot be undone; uncertainty changes what may be *claimed/authorized next*, not the past physical event.
5. A checkpoint with lost authority cannot authorize restoration, new destructive GC, verifier resurrection, budget refund, or effect-finality promotion.
6. Recovery requires an independent surviving evidence path or a new higher-generation assessment that explicitly commits the uncertain checkpoint and preserves all monotonic safety floors.
7. If no independent evidence remains, the system records `PROOF_UNRECOVERABLE_AFTER_RETENTION` and fails closed rather than fabricating continuity.
8. Retention policy itself is versioned/authenticated; retroactive policy shortening cannot erase evidence needed by an already-open dependency.

## Cross-contract invariants

- **No resurrection:** revocation/retirement uncertainty may reduce authority but never silently restore an older authority.
- **No refund:** privacy/accounting transitions never reduce already consumed cumulative loss.
- **No finality invention:** replay/cache/compaction cannot promote `UNKNOWN` solely from current-state observation.
- **No self-authenticating repair:** successor authority cannot erase the need to justify predecessor continuity when predecessor state matters.
- **No compaction privilege escalation:** compact evidence may preserve exactly the authority of the evidence it summarizes, never more.
- **Unknown is conservative:** missing dependency, replica, participant, or historical proof blocks irreversible authority decisions.

## 48-case RED-first matrix

The matrix is architecture evidence only until encoded and executed against the real implementation.

### A. Recovery-chain double compromise

A1. Valid `A0 -> R1 -> A2`, independent domains, no compromise -> accept chain.
A2. `R1` later compromised outside the authorization interval -> retain authority if interval proof excludes compromise.
A3. `R1` compromised during transition interval -> invalidate dependent transition.
A4. `A2` signer later compromised during its assessment interval -> invalidate `A2` authority.
A5. `R1` and `A2` share canonical failure domain -> do not count as independent quorum.
A6. Same-generation alternate `A2` heads -> explicit fork; reject last-write-wins.
A7. Higher repair commits only one fork head -> reject incomplete repair.
A8. Higher repair commits all live heads + undisputed floor + sufficient independent quorum -> accept new generation.

### B. Retirement-floor export/root rotation

B1. Valid compact floor + dual-authorized export bridge -> import and preserve retirements.
B2. Successor root self-signs export without predecessor continuity -> reject.
B3. Import maps retired verifier identity to a new namespace alias -> alias remains retired.
B4. Export bridge revoked after import -> continuity uncertain, verifier remains non-authoritative.
B5. Detailed bridge deleted before durable compact floor -> reject compaction/deletion.
B6. Compact floor present but source checkpoint mismatch -> reject export.
B7. New root attempts lower retirement generation -> reject rollback.
B8. New root retires additional verifiers while preserving prior floor -> accept monotonic extension.

### C. Unlearning cache invalidation

C1. Cache dependency vector exactly matches live ancestor generations -> cache usable.
C2. Ancestor theorem generation increments but verdict stays valid -> stale cache invalidated.
C3. Ancestor becomes revoked -> all dependent positive cache entries invalidated.
C4. One descendant re-proved -> sibling cache remains invalid.
C5. Descendant prepared under G, ancestor CAS advances to G+1 before commit -> descendant commit rejected.
C6. Cache key omits theorem/profile generation -> regression must fail.
C7. Compacted invalidation summary says stale while old positive cache remains -> stale dominates.
C8. Ancestor status unknown after storage loss -> authority-bearing cached result rejected.

### D. Privacy namespace split/merge

D1. Split parent remaining budget into disjoint child entitlements whose sum fits -> accept.
D2. Two children each inherit full parent remainder -> reject double-allocation.
D3. Consumed loss before split disappears from children -> reject refund.
D4. Reservation exists on removed participant -> carry conservatively until authenticated release.
D5. Concurrent split heads allocate overlapping entitlement -> namespace fork; block spend on both.
D6. Merge chooses least-spent child instead of conservative aggregate -> reject.
D7. Coordinator failover reuses same root lineage/generation floor -> accept.
D8. Participant unreachable during merge -> no refund/release of potentially live reservation.

### E. Finality/effect replay

E1. Replay exact authorized effect decision with intact generations -> reconstruct without re-executing effect.
E2. Cached `FINAL` depends on revoked authority -> reclassify `EFFECT_UNKNOWN`.
E3. Cached `NO_EFFECT` depends on revoked authority -> reclassify unknown; do not assume absence.
E4. Old-only quorum signs decision during joint membership interval -> reject.
E5. New-only quorum signs before joint transition completes -> reject.
E6. Exact duplicate effect entry replayed twice -> side effect executes at most once.
E7. Compact cache lacks dependency checkpoint -> cannot establish authority from current provider state.
E8. Independent reconciliation proves prior unknown -> append new decision generation; retain history.

### F. GC checkpoint authority after retention

F1. Valid compact checkpoint, authority intact, detailed evidence expired per policy -> checkpoint remains usable within its exact scope.
F2. Checkpoint authority later revoked -> mark future authority uncertain.
F3. After revocation, checkpoint used to authorize new destructive GC -> reject.
F4. After revocation, checkpoint used to resurrect old restore authority -> reject.
F5. Independent surviving witness re-proves checkpoint scope -> allow higher-generation recovery without lowering floors.
F6. No evidence survives after retention and authority compromised -> `PROOF_UNRECOVERABLE_AFTER_RETENTION`, fail closed.
F7. Retention policy shortened retroactively while dependency open -> refuse deletion.
F8. Past physical destruction already completed, later authority loss -> record historical event but do not claim stronger present authority.

## Implementation direction when exact execution becomes available

1. Encode the matrix as regressions before changing production code.
2. Reuse canonical generation/checkpoint/failure-domain primitives already frozen in LAB-090..100; do not create parallel authority systems.
3. Make dependency vectors explicit and serialized canonically for caches, compact checkpoints, privacy lineage, and replay entries.
4. Use immutable generation transitions and compare-and-swap/fencing at commit boundaries.
5. Separate historical fact from present authority in types/status values; late compromise should not rewrite history.
6. Run crash/restart, fork, rollback, stale-cache, and concurrent-transition tests at the same abstraction level as each durable mutation.

## Non-claims

- No real-schema RED/GREEN was executed in this research run.
- No LAB-086 source was manually copied/re-serialized into an executor.
- No merge/readiness conclusion is made for PR #165 or the other draft PRs.
- This contract is a frozen test/design target, not production proof.
