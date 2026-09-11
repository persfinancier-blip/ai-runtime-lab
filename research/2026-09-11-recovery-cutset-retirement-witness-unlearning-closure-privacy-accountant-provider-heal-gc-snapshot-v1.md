# Recovery cut-set, retirement witness compaction, propagated unlearning closure, privacy-accountant rollback, provider-ledger heal, and GC snapshot recovery — v1

Date: 2026-09-11
Status: `RECOVERY_CUTSET_RETIREMENT_WITNESS_UNLEARNING_CLOSURE_PRIVACY_ACCOUNTANT_PROVIDER_HEAL_GC_SNAPSHOT_V1_FROZEN`
Scope: architecture/evidence freeze only. Exact executable RED/GREEN remains pending.

## Why this slice exists

LAB-086 remains the highest-priority executable task, but the current runtime cannot byte-exactly materialize its pinned source closure into the local executor. The direct clone probe failed before repository execution with `Could not resolve host: github.com`. Per `AGENTS.md`, this run therefore advances the next distinct unblocked evidence task without claiming executable proof.

This note extends the already-frozen recovery/retirement/unlearning/privacy/provider/GC contracts into six failure modes that appear only after earlier evidence has been compacted, replicated, or partially healed.

## Primary donors re-verified

1. **The Update Framework (TUF)** — root succession is not self-authenticating merely because a newer root signs itself. The transition requires authorization under both predecessor and successor trust and rejects rollback. Donor: https://theupdateframework.github.io/specification/
2. **RFC 9162 / Certificate Transparency v2** — a signed tree head authenticates one view, while append-only continuity between views requires consistency evidence; inconsistent views must not be selected by freshness alone. Donor: https://www.rfc-editor.org/rfc/rfc9162.html
3. **NIST SP 800-226** — privacy budget is an upper bound on cumulative privacy loss over analyses of the same protected data. Re-coordination/version changes therefore cannot mint a fresh budget lineage. Donor: https://doi.org/10.6028/NIST.SP.800-226
4. **Raft joint consensus** — direct `C_old -> C_new` switching is unsafe because disjoint majorities can exist; the transition requires overlapping/joint authority until the new configuration is committed. Donor: https://raft.github.io/raft.pdf

These donors are mechanisms, not claims that the lab implements TUF, CT, differential privacy, or Raft verbatim.

## Contract A — successor recovery authority independence and cut-set validation

### Threat
A recovery-of-recovery rotation creates successor authority `R(n+1)`. Later, compact evidence says only that threshold members signed the successor certificate. If the successor signers share a compromise/failure domain with the predecessor path they are supposed to replace, apparent threshold diversity is not independent recovery authority.

### Frozen rules

- A recovery successor MUST bind a canonical `authority_cutset_descriptor`: signer identities, authority generations, declared independence domains, predecessor head(s), competing/forked heads known at issuance, and compromise/revocation floor inherited from all accepted ancestors.
- Threshold cardinality and cut-set independence are separate predicates. `k-of-n` is insufficient when all `k` members collapse to one compromised domain.
- A compact successor certificate MAY replace detailed compromise evidence only if its authenticated descriptor commits a conservative cut-set summary from which the required independence predicate remains decidable.
- Rotation cannot erase a previously known shared-failure edge. If compaction removes the only proof needed to establish independence, state becomes `RECOVERY_INDEPENDENCE_UNPROVABLE`; positive recovery authorization is blocked.
- A later successor cannot bootstrap from its own signature when predecessor continuity is missing. Missing continuity is not equivalent to predecessor revocation.
- Same-generation competing successors are a fork, not a last-writer-wins race. A resolving successor must commit all known competing heads and the deterministic resolution rule.

### Security consequence
Recovery remains fail-closed when detailed evidence is compacted: compact evidence may preserve authority, but cannot create stronger independence than the retained proof supports.

## Contract B — retirement bridge witness-set compaction after multiple revocations

### Threat
Verifier-retirement checkpoints `T1 -> T2 -> T3` are partially revoked or compacted. A compact bridge may preserve only the maximum retired-generation floor while deleting which authenticated witnesses proved continuity across revoked checkpoints. An attacker can then replay an older bridge with the same numeric floor but a different/untrusted lineage.

### Frozen rules

- A retirement bridge MUST commit both a monotonic `retirement_floor` and a `witness_set_commitment` covering the authenticated continuity segments it replaces.
- Numeric floor equality is not bridge equivalence. Two bridges with the same floor but incomparable witness commitments are distinct heads until reconciled.
- Compaction across revoked checkpoints requires surviving authenticated witnesses that cover every bypassed continuity segment. Revocation may remove a witness from future authority but cannot lower the inherited non-resurrection floor.
- If a bridge witness later becomes compromised/revoked, descendants remain usable only if another surviving authenticated path proves the same or stronger floor without relying on the compromised witness.
- Export/re-import between stores must preserve source bridge identity and witness commitment. Destination re-signing alone is not continuity proof.
- Losing every surviving bridge witness yields `RETIREMENT_CONTINUITY_UNRECOVERABLE`; verifier resurrection remains forbidden even though positive provenance cannot be reconstructed.

### Security consequence
Compaction preserves the one-way safety property: proof loss can stop progress, but cannot make a retired verifier live again.

## Contract C — propagated-descendant closure after one partition compacts unlearning dependency detail

### Threat
Partition A learns that ancestor result `U7` is invalid and propagates descendants `U8..U12` before compacting local dependency detail. Partition B later rejoins with additional descendants built from `U9`, but A no longer retains the full edge list needed to enumerate transitive invalidation.

### Frozen rules

- Every unlearning result/cache artifact MUST carry an immutable dependency-root or ancestry commitment sufficient to prove whether it descends from an invalidation frontier after local edge compaction.
- Invalidation checkpoints are monotonic sets/frontiers, not replaceable scalar versions. Concurrent incomparable checkpoints merge by conservative union of affected ancestry, not by max timestamp/version.
- A replica that cannot prove an artifact is outside the invalidated closure MUST return `UNLEARNING_DEPENDENCY_UNKNOWN`, never a positive authority-bearing cache hit.
- Rejoin requires exchange of invalidation heads plus compact ancestry commitments before accepting remote positive results.
- A partition that propagated stale descendants before learning the invalidation creates transitive revalidation obligations in every downstream partition that accepted those descendants.
- Compaction is permitted only after the retained summary can answer membership/ancestry queries required by the frozen invalidation contract; otherwise the detailed dependency evidence remains retention-critical.

### Security consequence
Local storage compaction cannot convert unknown ancestry into valid ancestry.

## Contract D — privacy accountant-version rollback/equivocation after tighter-bound transition

### Threat
Accountant version `A2` reproducibly computes a tighter bound than `A1` over the same immutable released-analysis event set. After failover, one coordinator presents an older `A1` state while another presents an `A2` state or a same-version result over a different event set.

### Frozen rules

- Privacy lineage identity is independent of accountant/coordinator version.
- An accountant transition MUST commit `(lineage_id, predecessor_accountant_head, method_id, immutable_event_set_commitment, resulting_bound)`.
- A numerically tighter bound is admissible only when it is reproducibly derived from the exact same released-analysis event set under an authorized method transition. Deleting/retracting outputs is not a refund of already incurred privacy loss.
- Rollback to an older accountant head is rejected even if its numeric bound is more conservative; rollback and bound conservatism are distinct properties.
- Same-generation accountant heads over different event-set commitments are equivocation. The reconciled state must include the union/authoritative event closure before any remaining-budget decision.
- Coordinator failover, namespace split/merge, or restored shard identity never creates a second lineage budget.

### Security consequence
Version changes can improve accounting precision but cannot rewrite history or double-spend privacy budget.

## Contract E — provider compensation-ledger partition/heal with delayed E1/E2/E3 evidence

### Threat
An original provider mutation `E1`, compensation `E2`, and repair/re-compensation `E3` execute across a network partition. Each side sees a different subset of late authenticated completion/no-effect evidence. Blindly selecting the freshest ledger can double-apply compensation or erase an already completed effect.

### Frozen rules

- `E1`, `E2`, and `E3` each have independent immutable effect identities and immutable request parameters. Compensation is never reuse of the original idempotency identity.
- Local statuses (`UNKNOWN`, `NO_EFFECT`, `COMPLETED`, provider-specific terminal states) are observations attached to an effect identity; they are not globally final unless backed by the contract's authenticated provider evidence.
- Partition healing performs monotonic evidence union per effect identity before deriving net business state.
- Contradictory authenticated terminal evidence for one identity produces `PROVIDER_EFFECT_FORK`; freshness does not resolve it.
- A confirmed `E2` does not permit deletion of `E1` evidence. Net-state derivation must preserve the ordered causal chain.
- Provider idempotency-retention expiry is not evidence of no prior effect. After TTL expiry, a destructive retry requires reconciliation/proof, not blind redispatch.
- If `E1=COMPLETED`, `E2=UNKNOWN`, `E3=COMPLETED` after heal, the system must not infer a clean net state unless the compensation semantics make that conclusion provable from the complete causal chain.

### Security consequence
Healing is evidence reconciliation, not status overwrite.

## Contract F — GC joint-configuration recovery from snapshot when survivors disagree whether `C_new` committed

### Threat
A GC system snapshots during `C_old,new` joint consensus. After replica loss, one survivor set has evidence that `C_new` committed; another has only the joint snapshot and an uncommitted/new-config proposal. Destructive GC after recovery would be unsafe if either side can independently declare membership finality.

### Frozen rules

- Snapshot authority and membership-finality authority are separate authenticated facts.
- A snapshot taken under joint consensus MUST commit `C_old`, `C_new`, joint configuration identity, last committed membership entry known to the snapshot, and the GC scope/root it authorizes.
- Recovery may restore application/GC state from a snapshot without thereby proving that `C_new` committed.
- While `C_new` commit status is disputed/unprovable, neither old-only nor new-only survivors can authorize new destructive GC: state is `GC_MEMBERSHIP_FINALITY_UNKNOWN`.
- A proof that `C_new` committed must be anchored in the consensus history/commit evidence required by the membership protocol, not inferred merely from presence of `C_new` in the snapshot.
- If the joint state is the last provable committed configuration, authority remains joint; if neither a valid joint quorum nor a valid final new configuration can be proven/reconstituted, destructive progress stops.
- Scope split/merge compaction cannot remove the parent membership-finality commitment while descendant GC tombstones still depend on it.

### Security consequence
Snapshot recovery can restore data without fabricating configuration finality.

## RED-first matrix — 48 cases

The following matrix is frozen as regression intent. `RED` means the pre-fix/unsafe model should accept or remain ambiguous where the frozen contract requires rejection/uncertainty; `GREEN` is the eventual desired executable behavior.

### A. Recovery cut-set (8)
1. successor threshold with all signers in one compromised domain -> reject independence;
2. threshold count valid and domains independent -> accept if continuity also valid;
3. compact descriptor omits known shared-failure edge -> reject;
4. predecessor continuity missing but successor self-signs -> reject self-bootstrap;
5. same-generation competing successor heads -> fork;
6. resolution commits only one known competing head -> reject incomplete resolution;
7. rotation preserves all heads and conservative compromise floor -> accept;
8. sole compact independence proof revoked/lost -> `RECOVERY_INDEPENDENCE_UNPROVABLE`.

### B. Retirement witness compaction (8)
9. same floor, different incomparable witness commitments -> do not collapse;
10. compact bridge covers every revoked segment with surviving witnesses -> accept;
11. bridge skips a revoked segment without witness -> reject;
12. later witness compromise with alternate surviving path -> remain valid at same/higher floor;
13. later witness compromise with no alternate path -> continuity unrecoverable;
14. destination store re-signs imported floor without source witness commitment -> reject;
15. replay older bridge with equal numeric floor but stale witness set -> reject rollback/equivocation;
16. proof loss -> block positive claim but retain non-resurrection floor.

### C. Unlearning propagated closure (8)
17. stale descendant directly names invalid ancestor -> reject;
18. stale descendant reaches invalid ancestor only through compact ancestry commitment -> reject;
19. ancestry proof unavailable after compaction -> `UNLEARNING_DEPENDENCY_UNKNOWN`;
20. incomparable invalidation frontiers -> union, not freshness selection;
21. rejoining replica serves positive cache before checkpoint exchange -> reject;
22. downstream partition received descendant before invalidation -> require transitive revalidation;
23. remote artifact proves outside invalidated closure -> permit normal validation path;
24. compaction removes information needed for closure membership -> compaction itself invalid.

### D. Privacy accountant transition (8)
25. A2 tighter bound over identical immutable event set -> accept authorized transition;
26. A2 tighter bound after omitting an already released event -> reject;
27. rollback A2 -> A1 even when A1 is numerically more conservative -> reject rollback;
28. same accountant generation, different event commitments -> equivocation;
29. failover merges branches with disjoint released events -> account union before remaining-budget decision;
30. deleted/retracted result attempts refund -> reject refund;
31. namespace/shard rename presents fresh budget -> map to existing lineage, reject double-spend;
32. method transition cannot be reproduced -> keep conservative prior floor / block tighter claim.

### E. Provider compensation heal (8)
33. E1 COMPLETED on A, UNKNOWN on B -> heal to authenticated completion if evidence valid;
34. E1 conflicting authenticated terminal evidence -> `PROVIDER_EFFECT_FORK`;
35. E2 compensation uses E1 idempotency identity -> reject identity reuse;
36. E1 completion evidence arrives after E2 dispatch -> retain both, derive ordered net state;
37. E2 UNKNOWN and TTL expired -> no blind redispatch;
38. E3 completes while E2 remains unknown -> do not infer clean net state without proof;
39. one partition drops E1 history after E2 -> reject healed ledger as incomplete;
40. evidence union yields unambiguous causal chain -> allow deterministic reconciliation.

### F. GC snapshot / joint configuration (8)
41. snapshot contains C_new proposal but no commit proof -> membership finality unknown;
42. old-only survivors claim destructive authority during joint state -> reject;
43. new-only survivors claim destructive authority without C_new commit proof -> reject;
44. valid proof C_new committed before snapshot -> recover under C_new after verifying proof;
45. valid proof joint config is last committed state -> retain joint authority requirements;
46. snapshot restores GC state but membership proof unavailable -> data recovery allowed, destructive GC blocked;
47. compaction drops parent membership commitment still needed by child tombstones -> reject compaction;
48. survivors cannot reconstitute any provable authorized quorum/configuration -> halt destructive progress, preserve evidence.

## Audit

### Unsupported assumptions deliberately rejected

- "more signatures" does not imply independent recovery authority;
- equal numeric retirement floors do not imply equal provenance;
- local compaction does not make missing unlearning dependencies valid;
- tighter privacy number does not authorize event omission or lineage reset;
- compensation does not erase original provider effects;
- snapshot presence of `C_new` does not prove `C_new` committed.

### Composition boundaries

- These contracts do not supersede LAB-086, LAB-088, LAB-090, LAB-091, or LAB-092 exact execution gates.
- They are architecture/evidence extensions for LAB-093 and subsequent frozen work.
- No new production code is justified until the corresponding RED cases can execute against exact repository bytes.

## Next distinct slice if exact execution remains blocked

After re-probing LAB-086 exact materialization, continue with: recovery cut-set key/domain revocation after compact certificate issuance; retirement witness threshold changes across bridge generations; unlearning closure proofs after result-store migration; privacy event-set Merkle/checkpoint compaction across accountant rotation; provider compensation semantics when provider itself rolls back/replays receipts; and GC membership proof retention after multiple snapshot generations and log truncation.
