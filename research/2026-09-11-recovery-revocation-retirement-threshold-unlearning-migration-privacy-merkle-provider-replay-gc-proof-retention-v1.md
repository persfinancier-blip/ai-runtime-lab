# Recovery revocation / retirement threshold / unlearning migration / privacy Merkle / provider replay / GC proof retention v1

Date: 2026-09-11
Status: DESIGN FROZEN; RED/GREEN execution pending exact source materialization
Contract id: `RECOVERY_REVOCATION_RETIREMENT_THRESHOLD_UNLEARNING_MIGRATION_PRIVACY_MERKLE_PROVIDER_REPLAY_GC_PROOF_RETENTION_V1_FROZEN`

## Why this slice exists

LAB-086 remains the executable priority, but the current runtime cannot safely materialize its complete pinned source closure into the local executor. Direct `git clone --no-checkout` again failed before repository execution because `github.com` could not be resolved. This note therefore advances only the next distinct architecture/evidence slice recorded in `state/CURRENT.md`; it does not substitute for LAB-086 RED/GREEN evidence.

This slice addresses six retention/recovery boundaries that become security-critical after detailed evidence is compacted or moved:

1. recovery cut-set key/domain revocation after compact-certificate issuance;
2. retirement witness-threshold changes across bridge generations;
3. unlearning closure-proof retention after result-store migration;
4. privacy event-set checkpoint/Merkle compaction across accountant rotation;
5. provider compensation when a provider rolls back or replays receipts;
6. GC membership-proof retention across multiple snapshots and consensus-log truncation.

## Primary donors and transferred mechanisms

### TUF root succession and revocation
TUF root metadata changes the authorized keys/thresholds and requires each successor root to be authenticated by both the predecessor threshold and the successor threshold. Root versions are monotonic and rollback is rejected. Mechanism transferred here: compact recovery authority must preserve an authenticated succession chain; revoking one key/domain after issuance cannot be represented by merely re-signing an old certificate under a new wrapper.

Source: The Update Framework specification, latest index currently advertises v1.0.36; root-update semantics require predecessor+successor threshold verification and rollback rejection.

### RFC 9162 Merkle consistency
RFC 9162 distinguishes an authenticated tree head from a proof that a newer tree is an append-only extension of an older tree. Mechanism transferred here: compact event/witness checkpoints need explicit consistency/succession evidence; equal or larger counters alone do not prove continuity.

### NIST SP 800-226 privacy composition
NIST defines a privacy budget as an upper bound on cumulative privacy loss and explains composition across repeated releases. Mechanism transferred here: compaction/accountant rotation may change representation or produce a tighter reproducible bound, but cannot erase already released events or refund incurred privacy loss.

### Idempotent mutation semantics
AWS guidance uses the same client/idempotency token for retries so repeated mutating requests have the same effect as the original request. Mechanism transferred here: provider original/compensation/repair operations have immutable identities; receipt rollback/replay is evidence conflict, not permission to mint a new effect identity.

### Raft snapshots and membership
Raft snapshots retain the latest configuration as of the last included index so membership semantics survive log truncation; joint consensus requires overlapping old/new majorities. Mechanism transferred here: a compact GC snapshot must retain enough authenticated membership/finality proof to determine which configuration had authority when truncated entries are no longer available.

## Frozen invariants

### A. Recovery cut-set revocation after compact issuance

A1. A compact recovery certificate binds the exact recovery generation, authorized key set, threshold, signer identities, and independence/failure-domain commitment used at issuance.

A2. Later revocation of a signer or failure domain does not retroactively rewrite historical facts, but it can invalidate the certificate as authority for *new* recovery actions when policy says that compromised material must no longer authorize future transitions.

A3. A successor recovery certificate must commit to the predecessor certificate digest plus the current revocation set/policy generation. Re-signing the old payload under surviving keys is not continuity proof.

A4. If compacted evidence no longer proves that the original threshold satisfied the required independence cut-set, positive authorization becomes `RECOVERY_INDEPENDENCE_UNPROVABLE`; historical audit evidence may remain, but new recovery is blocked.

A5. Revocation cannot lower a monotonic recovery generation or select an older competing head.

A6. Same-generation successors with different revocation views are a fork until a later authenticated resolver commits all known competing heads.

### B. Retirement witness-threshold changes across bridge generations

B1. Each retirement bridge binds a monotonic non-resurrection floor plus its witness policy generation and witness-set commitment.

B2. Increasing or decreasing the witness threshold creates a new bridge generation; it does not reinterpret signatures collected under an earlier policy.

B3. A successor bridge must authenticate the predecessor bridge and the exact policy transition. Threshold cardinality alone is insufficient when witness provenance/failure domains matter.

B4. Revoking witnesses after a bridge was accepted never resurrects retired verifiers. At worst, provenance for new retirement advancement becomes uncertain.

B5. Equal numeric floors with incomparable witness-policy lineage are not equivalent and cannot be collapsed during compaction.

B6. If all proof of bridge succession is lost, retain the maximum independently authenticated non-resurrection floor and return `RETIREMENT_PROVENANCE_UNRECOVERABLE` for further positive advancement.

### C. Unlearning closure-proof retention after result-store migration

C1. Unlearning result-store migration preserves immutable result IDs, theorem/profile generation, input lineage, invalidation frontier, and descendant-closure commitment.

C2. A destination-store import receipt is not authority unless it authenticates the exact source checkpoint and proves complete transfer of all authority-relevant closure commitments.

C3. Missing descendants after migration are treated as `UNLEARNING_CLOSURE_INCOMPLETE`, not as evidence that no descendants exist.

C4. A stale replica that rejoins using a pre-migration checkpoint cannot issue positive cache authority until it catches up through the migration checkpoint and every later invalidation generation.

C5. Re-keying/re-sharding the store changes storage identity only; it does not create a fresh theorem/profile generation or detach prior invalidations.

C6. If detailed dependency edges are compacted, a collision-resistant ancestry/closure commitment must survive. Unknown ancestry yields `UNLEARNING_DEPENDENCY_UNKNOWN`.

### D. Privacy event-set checkpoint/Merkle compaction across accountant rotation

D1. The immutable privacy lineage is the released-analysis event set, not the accountant process/database identity.

D2. Each compact checkpoint binds lineage ID, event-set root, event count/range, accounting method/profile, cumulative bound, and accountant-policy generation.

D3. Accountant rotation requires authenticated predecessor→successor continuity and a consistency proof that the successor event set contains the predecessor event set. A newer signed root without consistency is insufficient.

D4. A tighter privacy bound is acceptable only if reproducibly computed for the exact same immutable released-event set under an authorized method transition.

D5. Compaction never refunds privacy loss. Deleted raw events must remain represented in the committed event-set root/range and cumulative accounting floor.

D6. Equal cumulative epsilon/delta values with different event-set roots are incomparable; numeric equality is not lineage equality.

### E. Provider rollback/replayed compensation receipts

E1. Original effect `E1`, compensation `E2`, and any repair `E3` have separate immutable effect IDs and idempotency identities.

E2. A provider receipt is bound to effect ID, request digest, provider generation, provider transaction/version marker when available, and terminal status.

E3. Provider rollback of its visible state does not invalidate a previously authenticated completion receipt; it creates state/evidence divergence requiring reconciliation.

E4. Replayed receipts with the same identity and same terminal outcome are duplicates. Same identity with contradictory terminal outcomes is `PROVIDER_EFFECT_FORK`.

E5. A compensation receipt never rewrites the original effect to `NO_EFFECT`; accounting/audit retains both operations.

E6. After idempotency retention expires, lack of provider memory is `EFFECT_UNKNOWN`, not evidence of no prior effect and not authority for blind redispatch.

### F. GC membership-proof retention across snapshots/log truncation

F1. Every GC-authority snapshot binds the last included consensus index/term, the membership configuration effective at that index, configuration-generation ID, and proof that the configuration entry was committed.

F2. During joint consensus, snapshot authority records both `C_old` and `C_new` plus the joint phase; presence of `C_new` data alone does not prove final `C_new` commit.

F3. A later snapshot that truncates membership log entries must authenticate succession from the prior snapshot and preserve the finality proof needed to establish the current configuration.

F4. If survivors disagree about whether `C_new` committed and truncated history cannot reconstruct the answer, state is `GC_MEMBERSHIP_FINALITY_UNKNOWN`; destructive GC is blocked.

F5. Restoring an older snapshot cannot regain authority merely because its local membership has a majority under an obsolete configuration.

F6. Compacting old snapshots is safe only after a successor checkpoint commits their authority-relevant membership/finality evidence.

## 48-case RED-first matrix

### Recovery revocation (R1-R8)
1. R1 valid compact certificate under current policy -> accept historical authority.
2. R2 revoked signer attempts new recovery using old compact certificate -> reject.
3. R3 revoked failure domain replaced by nominally new key from same compromised domain -> reject independence.
4. R4 successor commits predecessor + revocation generation + valid new threshold -> accept.
5. R5 successor omits predecessor digest -> reject.
6. R6 equal recovery generation, different revocation views -> fork.
7. R7 older generation replayed after revocation -> rollback reject.
8. R8 compact evidence cannot prove cut-set independence -> `RECOVERY_INDEPENDENCE_UNPROVABLE`.

### Retirement threshold evolution (T1-T8)
9. T1 valid bridge under threshold policy p1 -> accept floor.
10. T2 policy p2 threshold increase with authenticated p1→p2 transition -> accept successor bridge.
11. T3 signatures collected under p1 reinterpreted as satisfying p2 -> reject.
12. T4 witness revocation after accepted floor -> floor remains non-resurrection floor.
13. T5 equal floor, incomparable witness lineage -> do not collapse.
14. T6 successor bridge omits predecessor witness-set commitment -> reject.
15. T7 all detailed witnesses compacted but authenticated bridge succession intact -> retain floor.
16. T8 succession lost -> block advancement, never resurrect retired verifier.

### Unlearning migration (U1-U8)
17. U1 complete authenticated source→destination closure transfer -> accept.
18. U2 destination missing one known descendant -> reject positive closure.
19. U3 destination receipt covers rows but not closure commitment -> reject.
20. U4 stale replica rejoins before migration checkpoint -> positive cache blocked.
21. U5 stale replica catches up through migration + invalidations -> revalidation allowed.
22. U6 store re-key/re-shard tries to reset invalidation generation -> reject.
23. U7 compact ancestry commitment proves descendant inclusion -> accept proof.
24. U8 ancestry detail and commitment both missing -> `UNLEARNING_DEPENDENCY_UNKNOWN`.

### Privacy Merkle/accountant rotation (P1-P8)
25. P1 identical event set + authorized tighter method -> accept reproducible tighter bound.
26. P2 successor root has higher event count and valid consistency proof -> accept.
27. P3 successor signed root lacks consistency proof -> reject continuity.
28. P4 equal epsilon, different event-set root -> incomparable/reject lineage substitution.
29. P5 raw events deleted after root checkpoint -> cumulative floor retained.
30. P6 accountant generation rollback -> reject even if numeric bound is larger/conservative.
31. P7 accountant forks two roots at same generation -> fork.
32. P8 merge requires union/consistent lineage proof; duplicate physical copies do not double-refund or create new budget.

### Provider receipts (E1-E8)
33. E1 repeated identical completion receipt -> deduplicate.
34. E2 same effect ID, contradictory terminal receipt -> `PROVIDER_EFFECT_FORK`.
35. E3 provider visible rollback after authenticated completion -> reconciliation required; do not rewrite history.
36. E4 compensation completes -> retain original completed + compensation completed.
37. E5 provider replays old compensation receipt against new request digest -> reject binding.
38. E6 idempotency TTL expired and provider says unknown -> keep `EFFECT_UNKNOWN`, no blind retry.
39. E7 repair E3 uses E1/E2 identity -> reject identity collision.
40. E8 partition heal unions authenticated E1/E2/E3 evidence without last-writer-wins collapse.

### GC snapshot/membership retention (G1-G8)
41. G1 snapshot with committed current config proof -> permit authority evaluation.
42. G2 snapshot contains C_new but no commit proof -> block destructive GC.
43. G3 joint snapshot preserves old+new config and committed joint entry -> valid joint semantics.
44. G4 log truncation removes config entries before successor snapshot commits proof -> reject compaction.
45. G5 older snapshot restore tries old-only majority after C_new committed -> reject stale authority.
46. G6 survivors disagree and proof unavailable -> `GC_MEMBERSHIP_FINALITY_UNKNOWN`.
47. G7 successor snapshot authenticates predecessor and retains membership finality evidence -> prior snapshot may be retired.
48. G8 multiple snapshot generations preserve monotonic last-included index/term and configuration succession; rollback/equivocation rejected.

## Audit conclusions

- Compaction is safe only if the compact artifact retains the authority-relevant *proof lineage*, not merely the latest numeric/state value.
- Revocation affects future authorization without rewriting historical facts; monotonic safety floors such as retirement/non-resurrection and already-incurred privacy loss survive revocation.
- Storage/process identity changes never create a fresh authority lineage by themselves.
- Unknown or contradictory provider/consensus evidence must stay explicit; last-writer-wins reconciliation is unsafe for authority-bearing state.
- No production implementation is justified from this note alone. The matrix is intentionally RED-first and must execute against exact repository bytes before any GREEN claim.

## Next executable step

LAB-086 remains first. On the next run, probe a supported byte-exact materialization path for executable snapshot `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`. If available, hash-verify the manifest closure and run the retained LAB-086 gate. If unavailable, continue with the next distinct retention/recovery slice rather than re-deriving this contract.