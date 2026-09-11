# Recovery-of-recovery, revoked reconciliation, rejoining descendants, privacy overrun, compensation ambiguity, and GC root rotation — v1

Date: 2026-09-11
Status: DESIGN FROZEN / RED-FIRST CONTRACT; executable RED/GREEN pending
Related: #163 (LAB-086), #178 (LAB-093 umbrella/follow-up), #179..#185

## Why this slice exists

LAB-086 remains the highest-priority executable gate, but current-run direct materialization is unavailable before repository execution (`git clone --no-checkout` cannot resolve `github.com`). The GitHub connector can read/write repository state, but there is still no supported byte-exact connector-to-local-executor materialization primitive for the pinned security-critical closure. This note therefore advances the next distinct evidence task recorded in `state/CURRENT.md` without claiming executable proof.

This slice freezes six failure/recovery contracts that arise only after an earlier recovery or compaction step has already succeeded once. The core rule is monotonic safety: a later rollback, revocation, partition heal, provider ambiguity, or retention event may reduce liveness or move authority to `UNKNOWN`, but must never synthesize fresh authority, refund already-accounted privacy loss, resurrect retired state, or permit a destructive replay.

## Primary donors re-checked

1. **TUF root update continuity / rollback rejection.** A successor root must be authenticated by both the predecessor threshold and the successor threshold, and versions advance monotonically. This is a useful donor for recovery-of-recovery authority succession and same-generation fork rejection.
   - https://theupdateframework.github.io/specification/
   - Current index exposes v1.0.36; root-update semantics require predecessor+successor threshold continuity and rollback detection.

2. **RFC 9162 Certificate Transparency consistency proofs.** A signed tree head authenticates a head; a Merkle consistency proof is what proves append-only continuity between heads. This is a donor for reconciliation/tombstone/checkpoint continuity after detail has been compacted.
   - https://www.rfc-editor.org/rfc/rfc9162.html

3. **NIST SP 800-226 differential privacy budgeting.** Privacy budget is an upper bound on cumulative privacy loss across analyses. Composition adds privacy loss; invalidating/retracting a result does not imply the already-released information becomes secret again.
   - https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-226.pdf
   - https://csrc.nist.gov/glossary/term/privacy_budget

4. **AWS idempotency guidance.** Retrying a mutating operation with the same idempotency token and same parameters should not create an additional effect; changing parameters under the same token is a conflict. This is a donor for keeping E1 and E2 identities immutable through unknown outcomes.
   - https://docs.aws.amazon.com/ebs/latest/userguide/ebs-direct-api-idempotency.html

5. **Raft joint consensus.** Membership changes require overlapping authority during transition; old and new configurations must not both make unilateral decisions. New replicas should catch up before voting. This is a donor for authority/checkpoint transitions when replicas rejoin or GC authority rotates.
   - https://raft.github.io/raft.pdf

## Frozen contract

`RECOVERY_OF_RECOVERY_RETIREMENT_REVOKE_UNLEARNING_REJOIN_PRIVACY_OVERRUN_PROVIDER_COMPENSATION_GC_ROOT_V1_FROZEN`

The six subcontracts below are normative for future RED tests.

---

## A. Recovery-of-recovery generation rollback/equivocation after a resolved compact cut-set fork

### Model

A compact cut-set authority fork at generation `g` was previously reconciled by accepted recovery generation `g+1`. Later, the recovery-of-recovery authority itself is rolled back, compromised, or presents an alternate same-generation `g+1'` head.

### Required rules

- Acceptance of `g+1` establishes a monotonic minimum accepted recovery generation and commits the complete competing-head set it resolved.
- A later presentation of `<= g` is rollback and cannot regain authority even if correctly signed by historically valid keys.
- A different `g+1'` is equivocation, not a newer recovery. It enters `RECOVERY_AUTHORITY_FORK`.
- `g+2` may resolve the fork only if its recovery policy is independently authorized and explicitly commits all known `g+1` heads plus the retained uncertainty/shared-failure-domain floor.
- Re-signing one old compact certificate with current keys is not re-proof of the deleted detailed evidence.
- If all surviving resolution authorities share a compromised failure domain, state becomes `RECOVERY_AUTHORITY_UNCERTAIN`; destructive decisions are blocked.

### Non-resurrection property

No rollback or fork resolution may lower any previously accepted compromise, revocation, retirement, or non-restorable floor inherited from generations `<= g+1`.

---

## B. Retirement-floor reconciliation when an accepted reconciliation checkpoint is later revoked

### Model

Multiple destination stores were reconciled into checkpoint `R_k`, and old detailed retirement evidence may already have crossed retention. Later, the signer/root/attestation that authorized `R_k` is revoked or retroactively classified compromised.

### Required rules

- Revocation of `R_k` authority invalidates `R_k` as positive continuity evidence; it does **not** resurrect any verifier or reduce the highest previously accepted retirement floor.
- If an earlier independently authenticated checkpoint and a later independently authenticated successor can bridge across `R_k`, continuity may be reconstructed through a new reconciliation generation.
- If the only bridge depended on revoked authority and source detail is gone, state is `RETIREMENT_CONTINUITY_UNRECOVERABLE`.
- `RETIREMENT_CONTINUITY_UNRECOVERABLE` is fail-closed for verifier resurrection and for further destructive retirement-evidence compaction.
- Same-generation alternate reconciliation checkpoints are forks and must be jointly committed by a later recovery generation; latest-writer-wins is forbidden.
- A store restored from backup behind the accepted floor may catch up but may never lower the global non-resurrection floor.

---

## C. Unlearning invalidation root rotation with a replica rejoining carrying pre-rotation descendants

### Model

During a partition, invalidation root `U_g` rotates to `U_g+1`. A replica later rejoins with descendants/caches derived from the pre-rotation root that were issued while isolated.

### Required rules

- Root rotation commits an immutable invalidation generation and the set/digest of required partition heads known at rotation.
- A rejoining replica must present its last authenticated invalidation checkpoint and descendant issuance frontier before its positive results can be used.
- Any descendant issued after the replica's stale checkpoint but before exact catch-up is `REVALIDATION_REQUIRED`; it is not grandfathered merely because issuance predates reconnect.
- If the descendant depends on an ancestor invalidated by `U_g+1`, it remains invalid even if signed by a previously valid worker.
- Cache/result eviction is transitive over the dependency DAG. Sibling revalidation does not repair another branch.
- If the rejoining replica reveals a previously unknown branch that should have participated in the rotation cut, the current root becomes `UNLEARNING_ROTATION_INCOMPLETE`; positive authority-bearing results are blocked until a successor root commits the union.

---

## D. Privacy overrun recovery when one branch later retracts/invalidates an analysis result

### Model

Two independently operating privacy-accounting branches are merged. Their conservative union exceeds the configured privacy budget. Later, one analysis is retracted, declared wrong, or its result is deleted.

### Required rules

- Released privacy loss is accounted when the analysis/result became observable under the configured threat model; later logical invalidation does not refund it.
- Retraction may alter utility/product semantics, but accounting remains at least the cumulative composed loss of all released analyses.
- A branch-local accounting rollback after merge is ignored unless it proves the analysis never executed and never released information; absence of a retained result is insufficient.
- If evidence cannot distinguish `never released` from `released then deleted`, use the conservative released interpretation.
- Budget overrun therefore blocks new analyses until policy explicitly provisions additional budget or a mathematically valid tighter accountant proves a lower bound from the same immutable event set. It is not repaired by deleting outputs.
- Namespace split/merge lineage remains one logical budget identity; restore/rename does not create fresh budget.

---

## E. Provider compensation chain where E2 is unknown and E1 late completion arrives

### Model

Original destructive effect `E1` times out and becomes `UNKNOWN`. A separately authorized compensation `E2` is dispatched and itself becomes `UNKNOWN`. Later, authenticated evidence arrives that `E1` completed.

### Required rules

- `E1` and `E2` have distinct immutable effect identities, payload digests, and idempotency identities.
- Unknown `E2` does not authorize redispatch of `E1`; late completion of `E1` does not imply whether `E2` executed.
- The state becomes a two-effect reconciliation problem: `{E1=COMPLETED, E2=UNKNOWN}`.
- No synthesized "net no-op" may be recorded unless authenticated evidence establishes `E2=COMPLETED` with compensation semantics that are actually inverse for the exact completed `E1` payload/version.
- If provider idempotency retention for either effect has expired, blind retry is forbidden. Use read/reconcile evidence or operator/product policy; do not mint a new token for the same logical mutation and call it a retry.
- Conflicting authenticated status for either effect yields `EFFECT_EVIDENCE_FORK` scoped to that effect identity.
- A later `NO_EFFECT(E2)` plus `COMPLETED(E1)` leaves the original effect in force; a later `COMPLETED(E2)` may establish compensated state only after payload/version cross-binding verifies the intended inverse relationship.

---

## F. GC tombstone root rotation/compaction after parent-scope metadata fully crosses retention

### Model

A destructive-GC scope was split/merged and represented by compact tombstones. Parent-scope metadata and detailed proof have now fully crossed retention. The compact tombstone root itself must rotate or be compacted again.

### Required rules

- The old compact root is an authority checkpoint, not merely a cache. Successor rotation must prove predecessor continuity and exact scope coverage before the predecessor is discarded.
- Scope coverage is set-based/DAG-based, not inferred from naming. Split children and merged successors must exactly cover the parent authority domain with no gap and no unauthorized overlap.
- If parent metadata is gone, the retained tombstone must carry enough authenticated commitment to prove parent identifier, scope digest, terminal destructive floor, predecessor generation, and successor coverage.
- Same-generation alternate successor tombstone roots are forks; both must be committed by a later resolution generation.
- Loss/revocation of the sole compact authority after detail has crossed retention yields `GC_AUTHORITY_UNRECOVERABLE`. It blocks future destructive GC for affected scopes; it does not revive old configuration authority or mark deleted data restorable.
- Historical old configurations remain non-authoritative even when their detailed metadata has expired. A compact non-resurrection floor must survive every tombstone-root rotation.
- Membership/root rotation that changes the replica authority set uses overlapping old/new authorization semantics; a new replica catches up the exact retained compact checkpoint before voting for destructive succession.

---

## RED-first matrix — 48 cases

### A — recovery-of-recovery (8)
1. Accept `g+1`, replay valid `g` -> reject rollback.
2. Accept `g+1`, present alternate same-generation `g+1'` -> `RECOVERY_AUTHORITY_FORK`.
3. Resolve `g+1/g+1'` with `g+2` committing only one head -> reject incomplete resolution.
4. Resolve with `g+2` committing both heads and independent authority -> accept.
5. Re-sign old compact proof with fresh keys but no deleted detail -> reject as re-proof.
6. Surviving authorities all share compromised failure domain -> `RECOVERY_AUTHORITY_UNCERTAIN`.
7. Recovery preserves higher historical revocation floor despite rollback attempt -> pass non-resurrection.
8. Post-resolution stale replica presents pre-fork authority -> cannot make destructive decision.

### B — retirement reconciliation revocation (8)
9. Revoke accepted `R_k` while full detail retained -> rebuild via independent evidence, no resurrection.
10. Revoke `R_k` after source detail deleted, no alternate bridge -> `RETIREMENT_CONTINUITY_UNRECOVERABLE`.
11. Restore destination behind accepted floor -> catch-up required; floor cannot decrease.
12. Same-generation alternate reconciliation checkpoint -> fork.
13. Later successor commits both alternates with valid bridge -> accept successor.
14. Revoked checkpoint was sole evidence for one interval -> further compaction blocked.
15. Attempt to mark retired verifier live because bridge is missing -> reject.
16. Independent pre/post checkpoints bridge revoked interval cryptographically -> allow reconstructed continuity only after proof verification.

### C — unlearning rejoin (8)
17. Replica rejoins exactly caught up, no extra descendants -> accept.
18. Replica rejoins with pre-rotation descendant depending on newly invalid ancestor -> invalidate descendant.
19. Stale positive cache hit before catch-up -> block.
20. Replica reveals previously unknown issuance branch omitted from root rotation -> `UNLEARNING_ROTATION_INCOMPLETE`.
21. Successor root commits union including rejoined branch -> allow revalidation workflow.
22. Revalidate one sibling only -> other sibling remains invalid/stale.
23. Root generation rollback from rejoined replica -> reject.
24. Descendant issued after stale checkpoint but before reconnect -> `REVALIDATION_REQUIRED` even if signature valid.

### D — privacy overrun / retraction (8)
25. Merge two branches under budget -> union/composition accepted.
26. Merge branches over budget -> block new analyses.
27. Delete/retract one already released result -> budget remains overrun/no refund.
28. Prove an analysis never executed and never released -> may remove reservation/unused allocation, not consumed loss.
29. Evidence ambiguous between never-released and released-then-deleted -> conservative consumed interpretation.
30. Restore renamed shard with same lineage -> no fresh budget.
31. Same analysis id, conflicting payload across branches -> accounting fork; do not choose cheaper branch.
32. Apply mathematically tighter accountant to same immutable event set -> may reduce bound only if proof/policy explicitly permits and is reproducible; never by event deletion.

### E — provider E1/E2 ambiguity (8)
33. `E1=UNKNOWN`, dispatch authorized `E2`, then `E1=COMPLETED`, `E2=UNKNOWN` -> explicit two-effect unresolved state.
34. Later `E2=NO_EFFECT` -> E1 remains effective.
35. Later `E2=COMPLETED` with exact inverse cross-binding -> compensated finality may be established.
36. `E2=COMPLETED` but payload/version mismatch -> reject compensation interpretation.
37. Conflicting authenticated `COMPLETED/NO_EFFECT` for E1 -> `EFFECT_EVIDENCE_FORK`.
38. Idempotency TTL expired for E2, status unknown -> blind retry forbidden.
39. New idempotency token for same logical E2 after TTL -> treated as new mutation, not safe retry; requires fresh authorization.
40. Late E1 completion after a previously assumed timeout must invalidate any cached `NO_EFFECT(E1)` conclusion.

### F — GC tombstone root rotation (8)
41. Rotate root with exact predecessor+scope commitments -> accept.
42. Successor omits one split child -> reject coverage gap.
43. Successor double-claims overlapping scope without explicit merge semantics -> reject.
44. Parent detail expired but compact commitment proves parent/scope/floor -> continuity can survive.
45. Sole compact authority revoked after detail expiry -> `GC_AUTHORITY_UNRECOVERABLE`.
46. Same-generation alternate tombstone root -> fork, no latest-writer-wins.
47. New replica votes before exact checkpoint catch-up -> reject destructive succession.
48. Old configuration presents valid historical tombstone after new root committed -> retain audit evidence but deny current authority.

## Implementation consequences

Future code/tests should model each domain with explicit immutable identities and monotonic generations rather than booleans such as `recovered`, `retired`, `invalidated`, `refunded`, `compensated`, or `compacted`. Required state machines must distinguish at least:

- authoritative / forked / uncertain / unrecoverable;
- current generation vs same-generation alternate vs rollback;
- evidence identity vs effect identity;
- logical budget lineage vs physical shard/storage identity;
- audit retention vs live mutation authority.

Compaction may replace detail only when the compact artifact carries enough authenticated commitments for future continuity/fork detection. Once detail is deleted, a compact artifact cannot later be strengthened by re-signing alone.

## Audit pass

Checked this contract for the main recurring failure modes:

- **No resurrection:** every unavailable-proof state fails closed rather than reviving retired/old authority.
- **No refund by deletion:** privacy consumption is tied to release/execution evidence, not result-file existence.
- **No retry aliasing:** original effect and compensation remain distinct identities through ambiguity and TTL expiry.
- **No LWW forks:** same-generation alternates are explicit forks in recovery, retirement, invalidation and GC roots.
- **No compaction magic:** compact evidence preserves commitments but cannot recreate deleted proof detail.
- **No disjoint membership authority:** transitions that change voters require overlap/catch-up before destructive decisions.

No implementation or executable PASS is claimed by this note. The next executable step remains the LAB-086 byte-exact materialization gate when a supported path becomes available.
