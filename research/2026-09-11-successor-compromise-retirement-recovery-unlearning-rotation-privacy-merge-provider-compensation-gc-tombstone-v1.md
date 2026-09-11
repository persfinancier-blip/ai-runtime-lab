# Successor-compromise recovery, retirement-store reconciliation, invalidation-root rotation, privacy-branch merge, provider compensation conflict, and GC tombstone compaction — v1

Status: `SUCCESSOR_COMPROMISE_RETIREMENT_RECONCILIATION_UNLEARNING_ROTATION_PRIVACY_MERGE_PROVIDER_COMPENSATION_GC_TOMBSTONE_V1_FROZEN`

Date: 2026-09-11

Scope: architecture/evidence freeze only. No executable RED/GREEN is claimed in this run because exact repository materialization remains unavailable.

## Why this slice

The previous freeze established compact authority rotation, monotonic retirement floors, partition/heal invalidation checkpoints, logical privacy lineages, immutable provider effect identities, and scope-aware GC succession. The next failure mode is what happens after those mechanisms themselves have forked, been independently restored, or crossed retention boundaries.

Cross-cutting invariant:

> Recovery may restore availability, but it must never manufacture a stronger authority statement than surviving authenticated evidence supports, refund already-consumed budget, replay an uncertain external effect, or resurrect retired configuration/proof authority.

## Primary donors re-verified

1. **TUF root succession.** Current root metadata is trusted through an ordered chain in which version N+1 is signed by thresholds from both the previously trusted root and the new root; rollback is rejected. Donor mechanism: predecessor+successor authorization and monotonic version continuity.
2. **RFC 9162 Certificate Transparency.** A signed tree head authenticates one view; append-only continuity across views requires consistency proofs, and inconsistent views are detectable misbehavior. Donor mechanism: compact state needs explicit continuity evidence, not signature-only trust.
3. **NIST SP 800-226.** Interactive differential-privacy queries consume a total privacy budget; each unique query adds privacy loss and must count against that cumulative budget. Donor mechanism: restoration/merge cannot refund spent privacy loss.
4. **AWS idempotency semantics.** A client token binds one logical request; same-token/same-parameters retries can be idempotent only inside the provider retention window, while parameter changes conflict and finite TTL means later reuse can become a new request. Donor mechanism: local effect identity outlives provider deduplication retention.
5. **Raft configuration-change discipline.** Membership transition must preserve overlap rather than permitting disjoint old/new majorities. Donor mechanism: authority rotation during unresolved distributed state uses overlapping authorization/catch-up.

## 1. Successor compromise or fork after compact cut-set authority rotation

### Problem

A compact cut-set certificate has already rotated from authority generation A to successor B after detailed graph/domain evidence crossed retention. Later B is compromised or two different B-successors appear.

### Contract

Every compact cut-set authority generation binds:

- immutable cut-set lineage id;
- authority generation;
- predecessor certificate digest and generation;
- canonical compact cut-set statement digest;
- graph/registry generations and evidence cutoff represented by that statement;
- preserved excluded/unknown/shared failure-domain floor;
- signer failure-domain registry generation;
- recovery-policy generation;
- retained independent checkpoint set.

Rules:

- a successor compromise does not invalidate authenticated predecessor facts, but it invalidates positive authority derived solely from the compromised successor after the compromise horizon;
- same predecessor + same successor generation + different content is `CUTSET_SUCCESSOR_FORK`;
- two later candidates descending from one predecessor remain a fork until a recovery generation explicitly commits both heads and proves why one continuation is authoritative;
- recovery cannot infer signer/failure-domain independence from deleted detail; surviving compact unknown/shared-domain floors remain binding;
- re-signing the latest compact statement under a fresh key without predecessor/fork reconciliation is authority migration, not re-proof;
- if all surviving paths rely on one compromised failure domain, state is `CUTSET_RECOVERY_AUTHORITY_UNCERTAIN` and destructive recovery remains blocked.

## 2. Cross-destination retirement-floor reconciliation after independent store recovery

### Problem

The original retirement source was deleted. Two destination stores are independently restored from different authenticated backups and then reconnect. Each carries a valid-looking retirement floor, possibly with different export generations.

### Contract

Retirement state is a logical lineage, not a database property. Reconciliation compares:

- immutable verifier lineage id;
- export generation;
- retirement/non-resurrection floor;
- predecessor export digest;
- trust-root generation;
- destination lineage id;
- authenticated high-water checkpoint(s).

Rules:

- ancestor/descendant exports reconcile to the descendant only if continuity is proved;
- same-generation distinct digests are `RETIREMENT_EXPORT_FORK`;
- incomparable descendants are a fork even if one has the numerically higher floor;
- recovery resolution MUST preserve the maximum accepted non-resurrection floor from all authenticated branches;
- revoking one branch removes its positive succession authority but cannot lower a retirement floor already accepted through an independent checkpoint;
- loss of all continuity evidence yields `RETIREMENT_FLOOR_UNRECOVERABLE`, never verifier resurrection;
- a newly reconciled destination must commit all resolved branch heads, not merely the winning store.

## 3. Root/authority rotation of compact unlearning invalidation checkpoints during an unresolved partition

### Problem

Replicas are partitioned and hold incomparable invalidation checkpoints. One side rotates the theorem/profile/root authority before the partition heals.

### Contract

A checkpoint rotation binds:

- invalidation lineage id;
- old and new root/profile generations;
- all known partition heads included in the transition;
- invalidation frontier/set commitment;
- replica-membership generation;
- predecessor checkpoint digests;
- evidence cutoff.

Rules:

- root rotation cannot collapse an unresolved checkpoint fork into a single latest-writer-wins head;
- a transition that has not observed every required live partition head is `INVALIDATION_ROTATION_INCOMPLETE`;
- new authority may sign a successor only after overlapping old/new authorization or an already-frozen emergency rule, plus explicit commitment to all known branch heads;
- invalidation merge is conservative union;
- stale replicas cannot serve positive authority-bearing results after learning a newer root/profile generation until they prove checkpoint catch-up;
- descendants issued under the new root still inherit invalidation dependencies from ancestors created under the old root;
- if one partition later reveals an invalidation omitted from the rotated checkpoint, the rotated checkpoint becomes stale and must be superseded; it is not retroactively treated as complete.

## 4. Privacy-lineage merge after both restored branches independently spend budget

### Problem

Two independently restored branches of one logical privacy root both continue serving analyses before collision is detected.

### Contract

Each branch must retain:

- immutable privacy root id and ancestor digest;
- branch generation;
- participant-set generation;
- cumulative consumed-loss accounting state;
- unresolved reservations;
- immutable analysis ids and canonical payload hashes;
- authenticated branch-head checkpoint.

Merge rules:

- the merged lineage includes every unique accepted analysis from both branches;
- the accounting result is recomputed/conservatively composed from the union of accepted analyses according to the configured DP accountant; it is never `min(branch_a, branch_b)` and never a reset;
- same immutable analysis id + same payload/outcome is deduplicated;
- same immutable analysis id + different payload/outcome is `PRIVACY_ANALYSIS_ID_FORK` and new spend stops;
- unresolved reservations union until individually resolved;
- if the union exceeds the configured budget, historical outputs are not magically undone; state becomes `PRIVACY_BUDGET_OVERRUN_RECONCILIATION_REQUIRED` and no new analyses are admitted;
- changing namespace/coordinator/shard ids cannot create a clean budget;
- the reconciled head commits both branch heads and the exact accountant/profile generation used for composition.

## 5. Late provider no-effect/completion conflict after a separately authorized compensating effect

### Problem

Original destructive effect E1 becomes `EFFECT_UNKNOWN` and provider idempotency retention expires. A separate compensation/replacement effect E2 is explicitly authorized and dispatched. Later authenticated evidence arrives claiming both `NO_EFFECT(E1)` and `COMPLETED(E1)` from different sources or provider replicas.

### Contract

E1 and E2 remain distinct immutable logical effects. Evidence for E1 binds exact effect id, request hash, provider generation, and evidence issuer/source.

Rules:

- `NO_EFFECT(E1)` and `COMPLETED(E1)` are mutually inconsistent positive claims and create `EFFECT_EVIDENCE_FORK`;
- presence of E2 does not permit choosing whichever E1 claim is operationally convenient;
- E2 is never reclassified as an idempotent retry of E1;
- downstream state that depends on whether E1 occurred becomes `EFFECT_DEPENDENCY_UNCERTAIN` until independent reconciliation resolves the fork;
- if E1 completion is eventually proven, reconciliation must reason about the combined E1+E2 real-world outcome; it must not silently discard compensation history;
- if E1 no-effect is proven, E2 remains an independently authorized effect with its own audit lifetime;
- blind re-dispatch of E1 after provider TTL remains prohibited regardless of later ambiguous evidence.

## 6. Tombstone/retention compaction for split/merged GC-scope succession

### Problem

Scope succession has formed a DAG through split and merge operations. Detailed predecessor checkpoints and tombstones are expensive, so retention compaction is required without letting an old authority or uncovered scope reappear.

### Contract

A compact GC succession tombstone binds:

- immutable scope lineage id(s);
- compacted predecessor checkpoint digests/range;
- explicit object-scope coverage commitment;
- successor checkpoint digest(s);
- authority/root generations;
- minimum non-resurrection authority generation;
- destructive effect/GC commit epochs covered;
- retention boundary and compaction generation.

Rules:

- compaction may replace detailed predecessor nodes only when retained tombstones prove exact scope coverage and successor continuity;
- split compaction retains proof that every parent object belongs to exactly one retained child coverage class or an explicit overlap/exception class;
- merge compaction retains all live parent heads until the merge successor proves coverage of their union;
- an old checkpoint below the retained non-resurrection generation cannot become authoritative merely because its detailed tombstone was deleted;
- authority rotation after compaction must commit the compact tombstone root and predecessor authority generation;
- loss/revocation of the only compact tombstone authority yields `GC_SCOPE_CONTINUITY_UNRECOVERABLE`; destructive GC stops for affected scope;
- partial coverage yields `GC_SCOPE_PROOF_INCOMPLETE`; the implementation must not infer deleted objects were safe.

## Cross-cutting durable states

- `CUTSET_SUCCESSOR_FORK`
- `CUTSET_RECOVERY_AUTHORITY_UNCERTAIN`
- `RETIREMENT_EXPORT_FORK`
- `RETIREMENT_FLOOR_UNRECOVERABLE`
- `INVALIDATION_ROTATION_INCOMPLETE`
- `PRIVACY_ANALYSIS_ID_FORK`
- `PRIVACY_BUDGET_OVERRUN_RECONCILIATION_REQUIRED`
- `EFFECT_EVIDENCE_FORK`
- `EFFECT_DEPENDENCY_UNCERTAIN`
- `GC_SCOPE_PROOF_INCOMPLETE`
- `GC_SCOPE_CONTINUITY_UNRECOVERABLE`

## 48-case RED-first matrix

### A. Compact cut-set successor compromise/fork
1. Accept clean A->B transition with valid predecessor+successor authorization and preserved uncertainty floor.
2. Reject B-successor that omits predecessor digest.
3. Reject same-generation B fork with different cut-set digest.
4. Preserve shared-domain floor after detailed evidence deletion.
5. Mark post-compromise B-only positive authority uncertain.
6. Resolve two B-successors only through recovery record committing both heads.
7. Reject recovery quorum whose surviving signers collapse into one compromised failure domain.
8. Confirm re-signing identical compact bytes alone does not count as re-proof.

### B. Retirement cross-destination reconciliation
9. Reconcile exact duplicate restored destinations idempotently.
10. Accept proven ancestor->descendant export continuity.
11. Reject older authenticated backup below surviving high-water mark as rollback.
12. Detect same-generation different-digest export fork.
13. Detect incomparable descendant export fork.
14. Preserve maximum non-resurrection floor during reconciliation.
15. Show branch revocation cannot lower an independently checkpointed floor.
16. Return `RETIREMENT_FLOOR_UNRECOVERABLE` when source and all independent continuity checkpoints are gone.

### C. Unlearning invalidation rotation during partition
17. Rotate after all partition heads are present and unioned.
18. Reject root rotation that commits only one live partition head.
19. Detect stale positive cache serve before checkpoint catch-up.
20. Preserve invalidation issued under old root after rotation.
21. Require overlap/emergency recovery rule for old->new authority transition.
22. Reject latest-writer-wins merge of incomparable invalidation heads.
23. Invalidate rotated checkpoint when a previously hidden branch later reveals omitted invalidation.
24. Block new membership voter until exact rotated checkpoint catch-up.

### D. Privacy merge after independent spend
25. Merge branches with disjoint valid analysis ids and compose union accounting.
26. Deduplicate identical immutable analysis id/payload across branches.
27. Detect same analysis id with different payload as fork.
28. Union unresolved reservations.
29. Prove namespace/shard rename does not reset budget.
30. Enter overrun state when unioned accepted analyses exceed configured budget.
31. Refuse new spend while overrun reconciliation is unresolved.
32. Bind merged head to both parents and exact accountant/profile generation.

### E. Provider ambiguity after compensation
33. Keep original E1 and compensation E2 as distinct effect identities.
34. Detect authenticated `NO_EFFECT(E1)` vs `COMPLETED(E1)` fork.
35. Refuse convenience selection based on desired local state.
36. Mark downstream E1-dependent state uncertain.
37. If completion wins, reconcile actual combined E1+E2 outcome.
38. If no-effect wins, retain E2 as independently authorized history.
39. Reject parameter drift attempting to reinterpret E2 as E1 retry.
40. Reject blind E1 redispatch after provider idempotency TTL expiry.

### F. GC split/merge tombstone compaction
41. Compact a linear predecessor chain while preserving scope/non-resurrection floor.
42. Compact split only with complete child coverage proof.
43. Reject split compaction with uncovered parent scope.
44. Compact merge only after successor commits every live parent head.
45. Reject resurrection of pre-floor checkpoint after detailed tombstone deletion.
46. Require authority rotation to commit compact tombstone root.
47. Return `GC_SCOPE_CONTINUITY_UNRECOVERABLE` after sole compact authority loss.
48. Block destructive GC on any retained partial-coverage state.

## Implementation shape for future RED/GREEN

Prefer immutable records and explicit generations over booleans. Tests should create the RED matrices at the persistence/recovery abstraction level that owns each contract, then add the minimum production mechanism. Where compact records replace detailed evidence, tests must delete the detailed source before exercising recovery so the implementation cannot accidentally depend on information the contract says is gone.

Do not treat this freeze as executable proof. LAB-086 remains higher priority until its exact source gate can run.
