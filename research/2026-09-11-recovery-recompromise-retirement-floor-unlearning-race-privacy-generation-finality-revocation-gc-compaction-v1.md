# Recovery re-compromise/fork, compacted retirement floor, unlearning revalidation races, privacy generation changes, finality catch-up revocation, and GC evidence compaction — V1

Status: `RECOVERY_RECOMPROMISE_RETIREMENT_FLOOR_UNLEARNING_RACE_PRIVACY_GENERATION_FINALITY_REVOCATION_GC_COMPACTION_V1_FROZEN`

Date: 2026-09-11

Context: LAB-086 remains priority #1. This run first re-read the repository control-plane files, inspected open issues/PRs, and re-probed exact source materialization. `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git` failed before repository code execution with `Could not resolve host: github.com`. GitHub connector reads/writes remain available but no supported connector-to-executor byte-exact materialization primitive is exposed. Therefore this note executes the exact next distinct evidence task recorded in `state/CURRENT.md`; it does **not** claim LAB-086 RED/GREEN, compileall, security, or integration PASS.

## Primary donors re-verified

- TUF specification: authenticated/versioned root transition, threshold authorization, rollback and mix-and-match resistance. Source: https://theupdateframework.io/spec/
- RFC 9162: authenticated log heads need consistency proofs to establish append-only continuity; inconsistent views are a distinct failure mode. Source: https://www.rfc-editor.org/rfc/rfc9162.html
- NIST SP 800-226: privacy budget is an upper bound on cumulative privacy loss; composition is conservative across repeated analyses. Sources: https://csrc.nist.gov/pubs/sp/800/226/final and https://csrc.nist.gov/glossary/term/privacy_budget
- Raft extended paper: direct configuration switching is unsafe because old/new configurations can form disjoint majorities; joint consensus uses overlapping authorization. Source: https://raft.github.io/raft.pdf

## Frozen contracts

### A. Repaired recovery-policy anchor is later compromised or forks

Repairing a lost/equivocal recovery-policy anchor creates a new authority generation; it does not make that generation permanently trustworthy.

Each repaired anchor generation must bind: predecessor/fork heads, canonical policy digest, accepted floor, root/failure-domain registry generation, threshold, issuance/evaluation interval, evidence cutoff, and repair proof digest.

Rules:

- interval-scoped compromise of a repaired anchor invalidates only authority claims whose authorization interval intersects the proven compromise interval, but surviving independent evidence must still satisfy the original threshold/intersection policy;
- same-generation incompatible repaired-anchor heads are `RECOVERY_POLICY_REPAIR_FORK`, regardless of arrival order or local majority;
- a later self-signed generation descending from only one fork head cannot canonize that branch;
- monotonic safety floors independently committed before the fork remain floors, but new recovery/destructive progress blocks while canonical continuity is unresolved;
- repair requires a strictly higher independently authorized generation that commits every live conflicting repair head, the last undisputed predecessor/floor, compromise evidence/cutoff, and the post-filter independent failure-domain set;
- keys sharing one canonical failure domain do not become independent merely because they live in separate keystores/accounts;
- if post-compromise surviving authority cannot meet threshold/intersection, state is `RECOVERY_POLICY_REPAIR_AUTHORITY_UNKNOWN`, not “best available branch”.

### B. Retirement non-resurrection floor after all reconstructed bridge-continuity evidence was compacted

A verifier retirement/non-resurrection floor is distinct from proof of full canonical bridge continuity. Compaction may preserve the former while intentionally deleting detailed bridge material only if a compact authenticated commitment makes that floor independently verifiable.

Rules:

- the compact record must bind retired verifier/profile id, minimum non-resurrectable generation, predecessor checkpoint/root, compaction generation, bridge/revocation summary digest, issuer/root generation, and retained audit dependency digest;
- after all detailed reconstructed bridges are deleted, the compact floor can still forbid resurrection of retired verifier generations;
- the compact floor cannot assert exact canonical branch continuity that it no longer proves;
- later revocation/compromise of the compact-floor issuer makes continuity authority uncertain unless a separately rooted retained commitment still proves the floor;
- absence of deleted detailed bridge evidence cannot be interpreted as absence of historical forks/revocations;
- a stale verifier with a valid signature below the compact non-resurrection floor remains rejected even when no original retirement bridge survives;
- any unresolved audit/destructive-effect dependency naming deleted bridge material must block compaction before deletion;
- re-expanding a compact floor from operator metadata or current state is not cryptographic reconstruction and cannot restore authority.

### C. Unlearning certificate revalidation races with concurrent descendant issuance

Revalidation after a post-close worker/issuer revocation is a state transition over an immutable certificate dependency DAG snapshot. Descendant issuance racing that transition must not observe a half-revalidated ancestor.

Each revalidation binds ancestor certificate id/digest, prior status generation, exact DAG snapshot/root, revocation evidence cutoff, retained valid contribution set, theorem/profile generation, and resulting status generation.

Rules:

- ancestor status transition to `REVALIDATING` is visible before any new descendant can claim the stronger guarantee;
- descendants issued from an ancestor whose status is `REVALIDATING` or `AUTHORITY_UNCERTAIN` inherit uncertainty or are blocked, according to policy; they cannot optimistically assume prior validity;
- if a descendant is concurrently prepared against old ancestor status but commits after the revalidation generation advances, compare-and-swap/status-generation mismatch rejects it;
- successful revalidation may preserve descendants only if their dependency binding includes the revalidated ancestor content/profile and policy permits status carry-forward; otherwise descendant revalidation is explicit;
- failed revalidation invalidates/blockades all descendants that committed to the affected ancestor generation;
- a new proof epoch cannot retroactively alter the membership/result set of the closed epoch it repairs;
- independent sibling branches remain valid only when they do not transitively depend on the revoked authority.

### D. Privacy compensation reconciliation across participant-set generation change and coordinator failover

Changing participant membership while compensation/reconciliation is open creates two independent version dimensions: accounting generation and participant-set generation. Coordinator failover may not collapse them.

Each compensation/reconciliation record binds predecessor accounting head, analysis id, participant-set generation+digest, coordinator generation, all fork heads, reservations, consumed-loss floor, uncertain contribution upper bounds, and transition proof to any successor participant set.

Rules:

- participant removal does not erase its consumed loss or unresolved reservation;
- a new participant cannot be inserted retroactively into a closed predecessor analysis generation;
- changing participant set while a compensation fork is open requires a bridge record committing all old participant-set fork heads before new-set accounting can proceed;
- coordinator failover cannot choose one fork, renumber `analysis_id`, or move the workload into a fresh budget namespace;
- if old and new participant sets overlap only partially, reconciliation preserves the conservative cumulative floor from all still-plausible predecessor branches before allocating new reservations;
- conflicting participant-set transition records form `PRIVACY_PARTICIPANT_TRANSITION_FORK` and block release of uncertainty margins;
- idempotent replay under the same accounting/participant generation may reproduce the same decision, but a second distinct decision is a fork;
- only independently proven-unused reservation can be released; consumed privacy loss is never refunded by membership change or coordinator replacement.

### E. Finality joint-membership recovery when catch-up attestations are later revoked

A new finality replica gains voting authority through authenticated catch-up plus joint-membership transition. If the catch-up attestation authority is later revoked/compromised for the catch-up interval, previously granted new-replica voting authority must be re-evaluated.

Rules:

- catch-up attestation binds replica identity, source checkpoint/evidence root, source replica-set generation, target membership generation, exact log/evidence range, and issuance interval;
- interval-scoped revocation marks affected catch-up proof `CATCHUP_AUTHORITY_UNCERTAIN`;
- a replica whose only proof of safe catch-up becomes uncertain cannot continue contributing authority to transitions/effect finality that rely on that proof;
- previously committed membership history is not silently rolled back; instead affected current authority is quarantined and a successor membership/recovery generation must reconcile it;
- re-attestation by a new signer without independently proving the exact historical range is not repair;
- if enough unaffected old+new members still satisfy the exact joint quorum and can independently re-prove the target checkpoint/range, a higher revalidation record may restore the member;
- if not, finality membership may lose liveness but must not lower threshold or upgrade `EFFECT_UNKNOWN` merely to recover availability;
- any finality cache entry depending transitively on the revoked catch-up proof is invalidated/reconciled before destructive retry decisions.

### F. GC audit-evidence retention/compaction without stale-configuration authority resurrection

After `GC_NEW_CONFIG_COMMITTED`, old configuration evidence may be necessary for audit/reconciliation while old voting authority is permanently retired. Compaction must preserve proof-of-history without creating a credential that can be replayed as current authority.

A compact GC audit record binds old configuration digest/generation, transition/joint/new configuration digests, destructive GC epoch ids, effect-reconciliation dependencies, stale-authority tombstone/floor, evidence Merkle/checkpoint root, compaction generation, and retention policy generation.

Rules:

- compacted old-config signatures are explicitly historical evidence scoped to their original configuration generation;
- no compact record may be accepted by current voting/mutation authorization paths as a live quorum certificate;
- unresolved destructive effects, compromise investigations, or membership forks referencing old evidence block deletion of the necessary leaves/proofs;
- compaction may replace detailed evidence with authenticated inclusion/consistency commitments only when all supported auditors can still prove required history and dependency closure;
- later loss of some compact replicas does not restore old authority and does not lower the stale-authority tombstone/floor;
- same-generation incompatible audit-compaction roots are an explicit `GC_AUDIT_COMPACTION_FORK`; neither branch is selected by freshness;
- old nodes replaying retained signatures after compaction are rejected by configuration generation and tombstone, then recorded as stale-history events only;
- deletion is safe only after an authenticated retention fixed point shows no unresolved effect/recovery/audit dependency can require the detailed evidence; uncertainty is treated as live.

## RED-first matrix (48 cases)

### Recovery anchor re-compromise/fork (1-8)
1. Repaired anchor remains above floor and no compromise evidence exists -> authority stays proven.
2. Repair signer compromised outside issuance/evaluation interval -> do not invalidate unrelated interval automatically.
3. Compromise intersects issuance interval and surviving independent domains still satisfy threshold/intersection -> allow explicit revalidation.
4. Same compromise leaves sub-threshold independent domains -> `REPAIR_AUTHORITY_UNKNOWN`.
5. Two same-generation valid repaired heads commit different fork sets -> `RECOVERY_POLICY_REPAIR_FORK`.
6. Higher head descends from only one repair fork -> reject as canonical repair.
7. Operator selects branch with more signatures from one correlated failure domain -> reject independence inflation.
8. Higher independently rooted generation commits all repair heads + last floor + compromise evidence and satisfies filtered threshold -> accept repaired continuity.

### Compacted retirement floor (9-16)
9. Detailed reconstructed bridges compacted; authenticated floor commitment retained -> retired verifier remains non-resurrectable.
10. Compact floor proves minimum generation but not exact old branch -> forbid resurrection while labeling canonical continuity unproven.
11. Old verifier below floor presents valid historical signature -> reject.
12. Compact-floor issuer later revoked for issuance interval and no independent commitment survives -> floor/continuity status becomes appropriately uncertain; do not fabricate proof.
13. Independent separately rooted floor commitment survives issuer revocation -> preserve floor.
14. Pending audit dependency references bridge leaf proposed for deletion -> block compaction.
15. Operator/current-state metadata recreates deleted bridge story -> reject as authority reconstruction.
16. Same-generation two compact roots disagree on retired set/floor -> compaction fork; no branch selection by timestamp.

### Unlearning revalidation race (17-24)
17. Ancestor enters `REVALIDATING`; new descendant attempts strong issuance -> block/inherit uncertainty.
18. Descendant prepared under status generation g, ancestor revalidates to g+1 before commit -> reject stale CAS.
19. Ancestor revalidation succeeds with exact original quorum/profile -> durable new status generation.
20. Descendant policy explicitly permits carry-forward and exact dependency digest matches -> allow after checking new ancestor generation.
21. Revalidation fails below quorum -> ancestor uncertain; dependent descendants invalid/blocked.
22. Concurrent descendant commits before `REVALIDATING` transition linearization -> remains historical but is subsequently dependency-invalidated if ancestor fails.
23. New worker tries to vote in old closed proof epoch during revalidation -> reject.
24. Independent sibling with no transitive revoked dependency -> remains unaffected.

### Privacy participant-set/coordinator transition (25-32)
25. Old participant removed with consumed loss -> cumulative floor unchanged or higher, never lower.
26. Removed participant has unresolved reservation -> reservation persists.
27. New participant added after predecessor analysis close -> cannot retroactively alter predecessor result set.
28. Compensation fork open and participant transition omits one fork head -> reject transition.
29. Bridge commits every old-set fork head, conservative floor, reservations, and new participant digest -> allow successor accounting generation.
30. Coordinator failover creates new budget namespace for same dataset/analysis lineage -> reject reset.
31. Same predecessor has two incompatible participant transitions -> `PRIVACY_PARTICIPANT_TRANSITION_FORK`.
32. Higher reconciliation commits both transition forks and conservative cumulative bound -> accept; release only independently unused reservation.

### Finality catch-up revocation (33-40)
33. Catch-up signer revoked outside relevant interval -> no automatic invalidation of unaffected proof.
34. Revocation covers attestation interval -> mark catch-up authority uncertain.
35. New replica with uncertain sole catch-up proof votes for destructive finality -> reject vote.
36. New signer merely re-signs claimed checkpoint without exact range proof -> reject repair.
37. Unaffected joint quorum independently re-proves exact range/checkpoint -> allow higher revalidation record.
38. Revalidation cannot meet joint threshold -> lose liveness rather than lower threshold.
39. Cached finality decision transitively depends on revoked catch-up proof -> invalidate/reconcile cache entry.
40. Membership record stays historical while current replica authority is quarantined -> no silent history rewrite.

### GC audit evidence compaction (41-48)
41. `C_old` evidence compacted with explicit original-generation scope -> usable for audit, not voting.
42. Current authorization path receives compact old quorum record -> reject as live authority.
43. Unresolved destructive effect references old receipt leaf -> retain leaf/proof; block deletion.
44. Authenticated checkpoint + consistency/inclusion material preserves every required audit query -> allow detail compaction.
45. Old compact replica loss occurs -> do not restore `C_old` authority or lower tombstone.
46. Two same-generation compaction roots disagree -> `GC_AUDIT_COMPACTION_FORK`.
47. Old node replays retained signature against current epoch -> generation/tombstone rejection, audit-only stale event.
48. Retention fixed point has an `UNKNOWN` dependency edge -> treat live and block destructive evidence deletion.

## Audit

- No later compromise/revocation is allowed to manufacture a cleaner history than the evidence supports.
- Monotonic floors/tombstones are deliberately separated from stronger canonical-continuity claims.
- Every race-sensitive transition has an explicit generation/snapshot/CAS boundary.
- Privacy membership/failover cannot mint budget or refund consumed loss.
- Membership/catch-up authority is distinct from external-effect finality.
- Historical GC evidence is non-authoritative by type/generation, even while retained for audit.
- Compaction is allowed only after proving dependency closure; unknown dependencies fail closed.
- This is architecture/evidence only. Exact executable RED/GREEN remains pending behind the current byte-exact materialization blocker.
