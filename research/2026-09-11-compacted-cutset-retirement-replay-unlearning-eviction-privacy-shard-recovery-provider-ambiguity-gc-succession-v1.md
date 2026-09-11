# Compacted cut-set validation, retirement-floor replay, distributed unlearning eviction, privacy shard recovery, ambiguous provider outcomes, and GC checkpoint succession

Date: 2026-09-11
Status: DESIGN FROZEN / RED-FIRST; executable RED/GREEN still pending
Contract: `COMPACTED_CUTSET_RETIREMENT_REPLAY_UNLEARNING_EVICTION_PRIVACY_SHARD_RECOVERY_PROVIDER_AMBIGUITY_GC_SUCCESSION_V1_FROZEN`

## Scope

This is the next distinct LAB-093 evidence slice while LAB-086 remains blocked on byte-exact executable materialization. It does **not** substitute for LAB-086 execution. It freezes six failure-boundary contracts:

1. recovery-chain cut-set validation when compromise evidence itself has been pruned or compacted;
2. rollback/replay protection for exported verifier-retirement floors after the source store is deleted;
3. distributed unlearning result-cache invalidation and eviction across stale replicas/readers;
4. privacy namespace split/merge reconciliation after shard loss/recovery and duplicate namespace identities;
5. effect-ledger replay when the external provider transaction outcome remains ambiguous;
6. succession/recovery of overlapping compact GC checkpoints when one checkpoint authority is later revoked.

## Current-run capability observation

LAB-086 was re-probed first. Direct `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git` failed before repository code execution with `Could not resolve host: github.com`. GitHub connector reads/writes remain available, but this run still exposes no supported connector-to-local-filesystem primitive that materializes the pinned executable closure byte-for-byte without model reserialization. No LAB-086 behavioral/unsafe-seed/compileall/security PASS is claimed.

PR #165 remains draft/open at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`. Fresh compare before this research commit: `diverged`, ahead 195 / behind 833, merge base `d2c9781f5a60dc9b8b94fc8dba651f804a73e509`.

## Primary-source mechanisms re-verified

### TUF root continuity and rollback resistance

TUF root update semantics require each successor root to be authorized by thresholds from both the trusted predecessor root and the successor root, while root versions advance monotonically. This is the donor for exported-floor and recovery-policy succession: a new authority cannot self-certify away predecessor continuity or safely accept an older authenticated generation simply because it is still signed.

- TUF specification index: https://theupdateframework.github.io/specification/
- Current index exposes v1.0.36; root update workflow in the current draft requires predecessor + successor thresholds and rejects rollback.
- Accessed: 2026-09-11.

### RFC 9162 append-only continuity and inconsistent views

Certificate Transparency v2 distinguishes an authenticated tree head from proof that a newer view extends an older one. Merkle consistency proofs establish append-only continuity; inconsistent views remain detectable only if sufficient authenticated heads/proofs survive or are compared by independent observers.

- RFC 9162: https://www.rfc-editor.org/rfc/rfc9162.html
- Accessed: 2026-09-11.

### NIST SP 800-226 cumulative privacy accounting

NIST defines privacy budget as an upper bound on allowable cumulative privacy loss across analyses on one dataset. Namespace repair, shard recovery, identity deduplication, split, merge, or failover therefore cannot mint fresh budget or erase already consumed loss.

- NIST SP 800-226: https://doi.org/10.6028/NIST.SP.800-226
- NIST glossary, privacy budget: https://csrc.nist.gov/glossary/term/privacy_budget
- Accessed: 2026-09-11.

### Raft joint configuration changes

Raft's membership-change mechanism uses overlapping/joint configurations because a direct old-to-new switch can permit disjoint majorities. This is the donor for authority-set/checkpoint succession while destructive GC epochs or recovery checkpoints overlap.

- Raft publication index: https://raft.github.io/
- Extended paper: https://raft.github.io/raft.pdf
- Accessed: 2026-09-11.

### Idempotent mutation under ambiguous external outcomes

AWS documents client-token idempotency specifically to make retries safe when timeouts or server errors leave clients uncertain whether a mutation occurred. Reusing the same token and same parameters returns the original result without another side effect; reusing the token with different parameters is rejected. This is a useful donor for provider effect-ledger replay: an ambiguous external outcome must retain the original immutable effect identity, not generate a new mutation identity on retry.

- AWS ECS idempotency: https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ECS_Idempotency.html
- AWS Well-Architected, idempotent mutations: https://docs.aws.amazon.com/wellarchitected/latest/framework/rel_prevent_interaction_failure_idempotent.html
- Accessed: 2026-09-11.

## Contract A — cut-set validation when compromise evidence is compacted

### Threat

A recovery decision may previously have been justified by a detailed dependency/failure-domain graph. After retention, only a compact compromise summary or cut-set certificate may survive. If that summary omits which original domains, intervals, unknown edges, and excluded authorities produced the cut, a later recovery can incorrectly count correlated or previously excluded authorities as independent.

### Frozen rules

1. A compact cut-set certificate commits the graph snapshot/checkpoint, policy generation, evidence cutoff, canonical failure-domain registry generation, compromise intervals, excluded authority IDs, and the exact surviving independent-domain set.
2. Compaction preserves a **lower bound on dependency/correlation uncertainty**. Unknown or unresolved dependency edges cannot be compacted into "independent".
3. A later authority is admissible only if its domain identity can be mapped into the compacted registry lineage without rollback or ambiguity.
4. If the domain registry or compromise assessment used by the compact cut is later revoked/equivocated, the compact result becomes `CUTSET_AUTHORITY_UNCERTAIN`; it does not silently recompute from incomplete retained evidence.
5. Two same-generation compact cut certificates with different surviving domain sets are an explicit fork, even if both individually satisfy a numeric threshold.
6. Recovery may advance past a compacted cut only through a higher generation that commits every live conflicting cut head plus the last undisputed safety floor.
7. Missing historical detail may reduce availability but cannot be interpreted as proof that a removed dependency never existed.
8. Compaction cannot lower established non-resurrection, privacy-loss, effect-unknown, or destructive-GC uncertainty floors.

## Contract B — exported retirement-floor replay after source deletion

### Threat

A compact verifier-retirement floor may be exported to another store/root and the source store later deleted. An attacker can then replay an older, correctly signed export bundle or a different branch of the export history because the original source evidence no longer exists locally for comparison.

### Frozen rules

1. Every export bundle commits source store identity, source retirement checkpoint, export generation, predecessor export digest, retirement-set digest, canonical identity-map generation, destination trust-root generation, and monotonic minimum retirement generation.
2. Destination import retains a durable **export high-water mark** independent of the deleted source store.
3. An older validly signed export generation is rollback and is rejected after a newer generation has been accepted.
4. A same-generation export with different bundle digest is equivocation/fork, not "another copy".
5. Source deletion is permitted only after destination durability of both the retirement floor and export high-water mark is established.
6. Replay under a new filename, transport envelope, destination namespace, or trust-root encoding does not reset export generation.
7. A later revocation of the export bridge can make continuity uncertain, but already-retired verifier identities remain non-authoritative.
8. If all bridge detail has been deleted and the surviving export cannot prove succession from the destination high-water mark, fail closed with `RETIREMENT_EXPORT_CONTINUITY_UNCERTAIN`; never resurrect.

## Contract C — distributed unlearning cache invalidation/eviction

### Threat

An ancestor theorem/profile/certificate generation can change while result caches are replicated. Some replicas/readers may miss the invalidation and continue serving a positive authority-bearing result after another replica has already observed revocation or revalidation.

### Frozen rules

1. Every cache entry includes an immutable dependency vector: model/data identity, theorem/profile generation, ancestor certificate generations, proof-result generation, and cache epoch.
2. Invalidation creates a monotonic invalidation generation/floor for the affected dependency cone; eviction is storage reclamation only and is not the authority event itself.
3. Readers must prove their observed invalidation generation is at least the floor required by the result's dependency vector before returning authority-bearing cached output.
4. A stale replica may serve historical/non-authoritative diagnostics but cannot serve a positive authority-bearing result after it is known to be below the invalidation floor.
5. Replica recovery/catch-up must transfer invalidation tombstones/floors before positive cache entries become serveable.
6. Evicting the invalidation tombstone while retaining/reconstructing a positive cache entry is forbidden until a compact non-resurrection/invalidation checkpoint supersedes it.
7. Concurrent descendant issuance and ancestor invalidation are CAS/snapshot-linearized: a descendant prepared under the old generation cannot commit after the invalidation floor advances.
8. Replica disagreement about the latest invalidation generation is conservative: authority-bearing output is blocked until quorum/continuity proves an admissible view.

## Contract D — privacy split/merge after shard loss/recovery and duplicate identities

### Threat

A privacy namespace may be split across shards, one shard may be lost and later recovered from stale media, or the same logical namespace may appear under duplicate physical IDs after failover. Naive merge can count one budget lineage twice, drop reservations from the missing shard, or choose the least-spent copy.

### Frozen rules

1. Every physical namespace/shard maps to one immutable logical root-budget lineage ID plus participant-set/allocation generation.
2. Duplicate physical namespace identities that map to the same logical lineage are aliases/copies, not independent budget grants.
3. Recovered stale shards cannot spend until they catch up to the current lineage generation and consumed/reserved accounting floor.
4. Lost/unreachable shard reservations remain conservatively live until authenticated evidence releases or uniquely transfers them.
5. Split entitlements remain disjoint and bounded by the parent's remaining entitlement after consumed loss and all unresolved reservations.
6. Merge deduplicates by immutable analysis/reservation identity before summing; it never deduplicates by choosing the lower-spend shard view.
7. Conflicting same-generation allocation/participant heads are a privacy-accounting fork; spending halts for overlapping entitlement until reconciled by a higher generation.
8. Namespace rename, shard replacement, coordinator failover, or restore from backup cannot reduce cumulative consumed loss or recreate released entitlement.

## Contract E — provider transaction outcome externally ambiguous

### Threat

The coordinator sends a destructive provider mutation and loses the response. The provider may have committed, rejected, or still be processing it. Replaying with a fresh identity risks duplicate side effects; assuming success or no-effect invents finality.

### Frozen rules

1. Every external mutation uses an immutable effect/request identity bound to canonical parameters, provider generation, and authority generation before the first provider call.
2. Timeout/transport failure after dispatch records `EFFECT_UNKNOWN`; it is neither `FINAL` nor `NO_EFFECT`.
3. Retry, when provider semantics support it, must reuse the same immutable idempotency/effect identity and identical authority-relevant parameters.
4. Same identity with changed parameters is a conflict and must fail closed; a new identity is a new effect and cannot be used to "retry" the old ambiguous operation.
5. If provider idempotency retention/TTL expires before outcome is reconciled, blind retry is forbidden; independent provider evidence or human/product policy may be required depending on consequence.
6. A provider status query is evidence only if it authenticates the exact immutable effect identity; current aggregate provider state is insufficient to infer the historical effect.
7. Effect-ledger replay never executes an ambiguous destructive effect again merely because local finality cache was lost or revoked.
8. Later reconciliation appends a new decision generation (`FINAL`, `NO_EFFECT`, or still `UNKNOWN`) while retaining the original ambiguous dispatch history.

## Contract F — overlapping compact GC checkpoint succession/recovery

### Threat

Two compact GC checkpoints may cover overlapping graph/evidence ranges under different authority generations. If one checkpoint authority is later revoked, a runtime might incorrectly fall back to an older overlapping checkpoint, combine incompatible partial scopes, or treat the newer checkpoint as superseding evidence that it never actually covered.

### Frozen rules

1. Each compact GC checkpoint commits graph snapshot/epoch, covered object/action set, predecessor checkpoint digest(s), authority generation, membership generation, evidence cutoff, retention class, and destructive commit status.
2. Succession is scope-aware: checkpoint `C2` supersedes `C1` only for the exact scope explicitly covered and only if continuity from `C1` is authenticated.
3. Overlap without full coverage produces a checkpoint DAG, not a scalar "latest checkpoint".
4. Revocation of `C2` authority invalidates its future authorization claims; it does not automatically revive `C1` for scope that crossed a retention boundary or was explicitly retired.
5. Recovery may combine multiple surviving checkpoints only when their scopes are non-conflicting and a higher-generation recovery record commits the exact set and preserves all monotonic floors.
6. Same-scope/same-generation checkpoints with different destructive action/result digests are an explicit fork.
7. A checkpoint that records `COMMIT_GC` is historical evidence that destruction was recorded; authority revocation changes present/future claims, not the physical fact. If commit itself cannot be independently authenticated after revocation, status becomes `GC_COMMIT_AUTHORITY_UNCERTAIN`.
8. If overlapping retained checkpoints cannot prove a complete admissible cover after one authority is revoked, future destructive GC and restoration claims fail closed; no checkpoint is selected merely by timestamp.

## Cross-contract invariants

- **Monotonic safety floors survive compaction.** Deleting detail never grants more authority than the detail possessed.
- **Identity survives relocation.** Export, shard replacement, namespace rename, cache replication, and checkpoint succession preserve immutable logical identity.
- **Unknown is not no-effect.** Ambiguous provider outcomes, missing cut-set detail, stale invalidation state, and revoked checkpoint authority stay conservative.
- **Replay is generation-aware.** A valid historical signature does not defeat a newer high-water mark, revocation, retirement, or invalidation floor.
- **Forks remain forks.** Same-generation conflicting authenticated state is not resolved by timestamp, arrival order, lexical ID, lower spend, or smaller scope.
- **Historical fact and current authority are separate.** Late compromise/revocation does not rewrite what occurred, but may remove the authority to rely on it for new irreversible decisions.

## 48-case RED-first matrix

The matrix is architecture evidence only until encoded and executed against the real implementation.

### A. Compacted recovery cut-set

A1. Compact cut commits full snapshot/registry/cut-set metadata and all surviving domains are independently admissible -> accept.
A2. Unknown dependency edge was dropped during compaction and two domains appear independent -> reject.
A3. Domain-registry generation rolls back after cut creation -> reject reuse under older registry.
A4. Same-generation compact cuts disagree on surviving domains -> explicit fork.
A5. Cut authority later revoked -> mark `CUTSET_AUTHORITY_UNCERTAIN`.
A6. Detailed evidence gone, but independently authenticated compact cut + registry continuity survive -> use exact compact scope only.
A7. Higher recovery commits only one live conflicting cut head -> reject incomplete repair.
A8. Higher recovery commits all live cut heads + undisputed floor + sufficient independent domains -> accept successor.

### B. Retirement export replay/rollback

B1. Export generation N imported and high-water mark persisted -> accept.
B2. Replay generation N-1 after N -> reject rollback.
B3. Same generation N with different digest -> explicit export fork.
B4. Replay N under new filename/transport wrapper -> still duplicate/replay, no new authority.
B5. Source deleted before destination high-water mark durability -> deletion precondition fails.
B6. Destination root rotates, export generation preserved through authenticated bridge -> accept.
B7. Export bridge later revoked -> continuity uncertain, retirement remains enforced.
B8. Source gone and surviving export cannot connect to destination high-water mark -> fail closed, no resurrection.

### C. Distributed unlearning cache

C1. Reader cache dependency vector and invalidation generation both current -> serve result.
C2. Ancestor invalidated on replica A; stale replica B serves positive result without floor check -> regression must fail.
C3. Replica B catches up tombstone before cache entries -> positive cache remains blocked until dependency revalidation.
C4. Tombstone evicted while stale positive cache retained and no compact invalidation checkpoint exists -> reject.
C5. Compact invalidation checkpoint supersedes detailed tombstones -> safe eviction within exact scope.
C6. Descendant prepared before ancestor invalidation, commits after floor advances -> reject CAS.
C7. Replica restored from old backup with stale positive entries -> cannot serve before invalidation-floor catch-up.
C8. Replicas disagree on latest invalidation generation -> block authority-bearing output until admissible continuity resolved.

### D. Privacy shard loss/recovery

D1. Lost shard restored at current lineage generation with all consumed/reserved IDs -> reconcile without refund.
D2. Restored stale shard attempts spend before catch-up -> reject.
D3. Two physical namespace IDs map to same logical lineage and same analyses -> deduplicate identities, do not grant two budgets.
D4. Duplicate namespace copies disagree on consumed loss -> conservative union / fork handling, never choose lower spend.
D5. Missing shard owns unresolved reservation -> reservation remains live.
D6. Split allocations overlap after shard recovery -> accounting fork; block overlapping spend.
D7. Merge deduplicates immutable analysis IDs then conservatively composes unique loss -> accept.
D8. Backup restore uses old namespace name/generation and appears "fresh" -> reject lineage rollback.

### E. Ambiguous provider outcome

E1. Mutation returns success -> record `FINAL` bound to immutable effect identity.
E2. Transport timeout after dispatch -> record `EFFECT_UNKNOWN`, not no-effect.
E3. Retry same effect identity + same canonical parameters on idempotent provider -> safe retry / recover original result.
E4. Retry same identity with changed parameters -> reject conflict.
E5. Retry ambiguous operation with a new identity -> reject as duplicate-risk unless explicitly creating a distinct new effect.
E6. Provider idempotency TTL expired while outcome unknown -> do not blind retry.
E7. Aggregate provider state happens to match expected postcondition but exact effect identity is not authenticated -> remain unknown.
E8. Independent exact-effect reconciliation later proves success/no-effect -> append new decision generation, preserve ambiguous history.

### F. GC checkpoint succession

F1. `C2` explicitly supersedes full scope of `C1` with authenticated continuity -> use C2 for that scope.
F2. `C2` overlaps only part of C1 -> retain checkpoint DAG; do not erase uncovered C1 scope.
F3. Same-scope same-generation C2 variants disagree -> checkpoint fork.
F4. C2 authority revoked after C1 detailed evidence expired -> do not silently fall back to C1 for retired/superseded scope.
F5. Independent surviving C1 scope plus other non-conflicting checkpoints form complete authenticated cover -> higher recovery may commit exact cover.
F6. Overlapping checkpoints conflict and no higher recovery resolves them -> fail closed for destructive/restore authority.
F7. C2 records physical `COMMIT_GC`; later authority revocation -> historical commit retained, future authority uncertain.
F8. Commit evidence itself loses admissible authentication after retention -> `GC_COMMIT_AUTHORITY_UNCERTAIN`; no fabricated finality.

## Implementation direction when exact execution becomes available

1. Encode these 48 cases as regressions before production refactors.
2. Reuse existing generation/checkpoint/failure-domain/effect identity primitives; do not create parallel authority systems.
3. Give every compact artifact explicit type, predecessor digest(s), scope, generation, authority generation, registry/identity generation, and retention/evidence cutoff.
4. Persist high-water marks and invalidation/non-resurrection floors separately from reclaimable detailed evidence.
5. For external effects, bind immutable request identity before dispatch and preserve it across retry/reconciliation; never infer an exact historical effect from aggregate provider state.
6. Model overlapping compact checkpoints and dependency summaries as DAGs where scalar "latest" is unsafe.
7. Exercise crash/restart, backup restore, stale replica, fork, TTL expiry, replay, and retention-boundary schedules at the same abstraction level as the durable transitions.

## Non-claims

- No real-schema RED/GREEN was executed in this research run.
- No LAB-086 source was manually copied/re-serialized into an executor.
- No branch/PR readiness or merge-safety conclusion is made.
- The current compare is observational only and must be refreshed after this main-branch research/state work.
- This document is a frozen regression/design target, not production proof.
