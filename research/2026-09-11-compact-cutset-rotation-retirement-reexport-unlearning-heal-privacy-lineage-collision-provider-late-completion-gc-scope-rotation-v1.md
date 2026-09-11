# Compact recovery authority rotation, retirement re-export, invalidation heal, lineage collision, late provider completion, and GC scope succession — v1

Status: `COMPACT_CUTSET_ROTATION_RETIREMENT_REEXPORT_UNLEARNING_HEAL_PRIVACY_LINEAGE_PROVIDER_LATE_COMPLETION_GC_SCOPE_V1_FROZEN`

Date: 2026-09-11

Scope: architecture/evidence freeze only. No executable RED/GREEN is claimed in this run because exact repository materialization remains unavailable.

## Why this slice

`state/CURRENT.md` recorded six unresolved evidence boundaries after the preceding compact-cutset freeze. They share one failure mode: once detailed evidence has been compacted, deleted, partitioned, or moved across an authority transition, a later valid-looking object can accidentally acquire more authority than the retained proof actually supports.

The invariant for this slice is therefore:

> Compaction may reduce retained representation size, but it must never widen authority, erase a monotonic safety floor, convert uncertainty into independence, mint a fresh budget/effect identity, or let an obsolete authority regain control after rotation.

## Re-verified primary donors

1. **The Update Framework root update discipline.** A new trusted root is accepted only through ordered version succession and signatures satisfying thresholds from both the previously trusted root and the candidate new root; rollback to an older version is rejected. Donor mechanism: predecessor+successor authorization and monotonic versioning for authority rotation.
2. **RFC 9162 Certificate Transparency v2.** Signed tree heads authenticate a view, but append-only continuity across views requires consistency evidence; inconsistent views are evidence of log misbehavior. Donor mechanism: compact checkpoint plus explicit continuity proof rather than treating a signed head as sufficient history.
3. **NIST SP 800-226.** Privacy budget is an upper bound on cumulative privacy loss across analyses of the same data. Donor mechanism: split/restore/merge must preserve one cumulative accounting lineage and cannot refund already consumed loss by renaming or restoring physical shards.
4. **Raft joint consensus.** Direct configuration switch is unsafe because old and new configurations can form disjoint majorities; a transition phase that overlaps both configurations is required. Donor mechanism: authority/membership transitions must preserve an overlap that prevents two simultaneously authoritative configurations.
5. **AWS idempotency semantics.** A client token binds one logical mutating request; retries with the same token and same parameters can return the original outcome, changed parameters conflict, and token retention has a finite TTL. Donor mechanism: one immutable external-effect identity plus explicit uncertainty once provider deduplication retention has expired.

## 1. Rotation of compact recovery cut-set authority after detailed evidence deletion

### Problem

A compact recovery certificate may survive after the detailed dependency graph, signer-to-failure-domain mapping, compromise intervals, and exclusion evidence have been deliberately deleted. Later the authority that issued that compact certificate itself needs rotation, or is partially compromised.

A naive design can re-sign the old compact object under the new authority and thereby silently treat its embedded cut-set conclusion as freshly proven.

### Contract

A compact cut-set certificate MUST bind at least:

- `cutset_generation`;
- canonical `graph_generation` and `registry_generation` that were evaluated;
- hash of the exact compacted independence/cut-set statement;
- compromise-evidence cutoff / interval horizon;
- excluded domains and unresolved/unknown domains;
- issuer authority generation and issuer failure-domain set;
- predecessor certificate digest, when part of a succession chain;
- explicit statement of whether detailed evidence is still retained or has crossed a retention boundary.

Authority rotation is valid only if a successor certificate:

1. commits the predecessor certificate digest and generation;
2. is authorized under both the still-valid predecessor policy and the successor policy, unless the recorded emergency-recovery contract already proved why predecessor participation is impossible;
3. preserves all uncertainty/exclusion floors from the predecessor unless new independently authenticated evidence resolves them;
4. does not relabel a previously shared/unknown failure domain as independent merely because detailed evidence was deleted;
5. advances generation monotonically.

If the predecessor issuing authority is later compromised and no independently authenticated evidence survives to re-establish the cut-set conclusion, state becomes `CUTSET_AUTHORITY_UNCERTAIN`. The system MUST NOT reconstruct a stronger conclusion from absence of deleted detail.

Re-signing identical bytes under a new key is **authority migration**, not **re-proof**.

## 2. Re-export/recovery of verifier-retirement floors after destination-store compromise

### Problem

A retirement floor may have been exported from a source store, the source then deleted, and the destination store later compromised or lost. Restoring an old destination backup can present an older but still validly signed retirement export.

### Contract

Each retirement export binds:

- immutable verifier lineage id;
- retirement floor / minimum rejected authority generation;
- export generation and destination lineage id;
- predecessor export digest;
- root/trust generation;
- source retention-boundary acknowledgement;
- destination-side monotonic high-water mark.

Recovery rules:

- older export generation than the authenticated high-water mark => `RETIREMENT_EXPORT_ROLLBACK`;
- same generation with different digest => `RETIREMENT_EXPORT_FORK`;
- loss/compromise of the destination store does not reset the high-water mark if an independent authenticated checkpoint survives;
- if no independent checkpoint survives after source deletion, status is `RETIREMENT_FLOOR_UNRECOVERABLE`, never “fresh/unretired”;
- bridge/root revocation can remove authority from an export but cannot resurrect any verifier below an already accepted retirement floor;
- a new destination lineage may be created only by a recovery record that commits the last surviving floor and predecessor checkpoint.

The non-resurrection floor is therefore logically stronger than any single destination database.

## 3. Partition/heal semantics for compact distributed unlearning invalidation checkpoints

### Problem

Replicas can partition after accepting different invalidation updates and later compact local tombstones into checkpoints. When the partition heals, two individually valid compact checkpoints may summarize incomparable invalidation sets.

### Contract

A compact invalidation checkpoint binds:

- immutable model/dataset/theorem lineage;
- checkpoint generation;
- causal parent checkpoint digest(s);
- invalidation frontier or canonical invalidated-object-set commitment;
- theorem/profile/root generations used to classify validity;
- replica-membership generation;
- evidence cutoff.

Rules:

- invalidation is monotonic authority state; cache eviction is only a storage action;
- concurrent incomparable checkpoints form `INVALIDATION_CHECKPOINT_FORK`;
- merge is conservative union of invalidation authority, not latest-writer-wins;
- a healed replica may serve a positive authority-bearing cached result only after proving its checkpoint descends from or safely joins all required invalidation heads;
- deleting per-object tombstones is allowed only after a compact checkpoint covering them is itself protected by the retained continuity chain;
- new descendants issued during/after partition inherit invalidation dependencies from their actual theorem/profile ancestors and cannot escape via checkpoint lag;
- replica membership changes during an unresolved fork require an overlapping old/new authorization phase; a newly joined replica cannot vote based on an incomplete checkpoint.

## 4. Logical privacy-lineage collisions across independently restored roots

### Problem

Two backups of what was originally one privacy budget root can be restored independently, each believing it owns a live namespace. Later they meet under different physical identifiers or coordinator generations.

### Contract

Budget identity is logical, not physical. A root lineage binds:

- immutable `privacy_root_id` created at original initialization;
- dataset/cohort identity commitment;
- ancestor root digest;
- accounting generation;
- cumulative consumed-loss floor;
- unresolved reservations/analysis ids;
- participant-set generation.

On collision of two restored lineages with the same root identity:

- consumed loss = conservative maximum/union required by the accounting model, never minimum;
- reservations = union by immutable reservation/analysis identity;
- duplicate copies of the same immutable analysis id are deduplicated, not double-charged;
- conflicting payloads under the same immutable analysis id => `PRIVACY_ANALYSIS_ID_FORK` and spending stops;
- independently created descendants of the same parent are a fork requiring reconciliation before new spend;
- renaming shard, namespace, coordinator, or storage root never creates fresh budget;
- if two roots claim different IDs but authenticated ancestry proves they derive from the same original dataset budget, they must be joined under one lineage rather than treated independently.

No recovery action may refund already consumed privacy loss.

## 5. Provider effect ambiguity after idempotency TTL plus late authenticated completion

### Problem

A destructive provider request is dispatched with effect id `E`. The response is lost. Provider deduplication/idempotency TTL expires, so blind retry is unsafe. Later an authenticated completion signal for `E` arrives.

### Contract

Before dispatch, persist an immutable effect record binding:

- logical effect id/idempotency token;
- canonical request parameters/hash;
- provider identity/generation;
- dispatch generation and timestamp/epoch;
- provider idempotency-retention horizon if known;
- local state `PREPARED`.

After dispatch without authoritative result: `EFFECT_UNKNOWN`.

While provider deduplication is known active, retry may use the same effect id and exact same parameters. Parameter drift is a hard conflict.

After the provider's deduplication retention is expired or unknown, **no blind re-dispatch** is allowed. Recovery is read/reconcile only until independent evidence resolves the outcome or a product-specific compensating protocol explicitly authorizes a new logical effect.

A late authenticated completion signal for `E` after TTL:

- may transition `EFFECT_UNKNOWN -> EFFECT_CONFIRMED` only if it cryptographically/authentically binds the same effect id, provider generation, and request identity;
- does not authorize a second dispatch;
- conflicts with an independently authenticated `NO_EFFECT` statement for the same effect id, yielding `EFFECT_EVIDENCE_FORK` until reconciled;
- if a second logical effect was already explicitly authorized after uncertainty, the late completion does not merge the two identities; compensation/reconciliation must reason about both effects.

TTL expiry ends deduplication assurance, not the identity or audit lifetime of the original effect.

## 6. Split/merge succession of compact GC checkpoint scopes across authority rotation and partial retention

### Problem

GC checkpoints may summarize different object scopes. Later scope A and B split, merge, or rotate authority after some detailed proof data has crossed retention boundaries. A newer checkpoint for one scope must not accidentally supersede evidence for another.

### Contract

Every compact GC checkpoint binds:

- checkpoint id/generation;
- explicit canonical object scope;
- scope-generation and parent scope ids;
- authority/root generation;
- predecessor checkpoint digest(s);
- authenticated inventory/graph snapshot generations;
- destructive-GC epoch and commit status;
- retention boundary crossed;
- non-resurrection / minimum-authority floors inherited from predecessors.

Succession is a DAG, not a single global sequence.

Rules:

- a successor supersedes only the scope it explicitly covers;
- split `S -> {A,B}` requires both child checkpoints to commit parent `S` and partition semantics proving coverage/no overlap ambiguity;
- merge `{A,B} -> M` requires `M` to commit both live parents and preserve the union of their safety floors;
- authority rotation during split/merge uses predecessor+successor authorization or an already-proven emergency recovery rule;
- a retained checkpoint whose issuing authority is later revoked loses positive authority but does not resurrect older deleted authority;
- partial retention that leaves a coverage gap yields `GC_SCOPE_PROOF_INCOMPLETE`; destructive GC for affected objects stops;
- post-commit compaction may delete detail only after a successor compact checkpoint proves the exact scope/effect boundary it replaces.

## Cross-cutting fail-closed states

Implementations should converge on explicit durable states rather than boolean “valid/invalid” shortcuts:

- `CUTSET_AUTHORITY_UNCERTAIN`
- `RETIREMENT_EXPORT_ROLLBACK`
- `RETIREMENT_EXPORT_FORK`
- `RETIREMENT_FLOOR_UNRECOVERABLE`
- `INVALIDATION_CHECKPOINT_FORK`
- `PRIVACY_ANALYSIS_ID_FORK`
- `PRIVACY_LINEAGE_FORK`
- `EFFECT_UNKNOWN`
- `EFFECT_EVIDENCE_FORK`
- `GC_SCOPE_PROOF_INCOMPLETE`

None of these states may be converted to success solely by wall-clock age, cache eviction, local database freshness, a newer signature, or absence of detailed evidence after retention.

## RED-first executable matrix (48 cases)

### A. Compact cut-set authority rotation
1. valid predecessor+successor coauthorized rotation preserves cut-set conclusion;
2. successor-only signature rejected when predecessor remains required;
3. older cut-set generation replay rejected;
4. same-generation different compact digest => fork;
5. rotation that drops prior unknown domain rejected;
6. rotation that relabels shared domain independent without new evidence rejected;
7. predecessor authority compromise with surviving independent re-proof accepted only through explicit recovery contract;
8. predecessor compromise after detail deletion and no surviving proof => `CUTSET_AUTHORITY_UNCERTAIN`.

### B. Retirement-floor destination recovery
9. newest export restored successfully;
10. older signed export after high-water mark => rollback;
11. same-generation alternate export => fork;
12. destination root rotation preserves floor;
13. destination compromise + surviving independent checkpoint restores exact floor;
14. source deleted + destination compromised + no checkpoint => unrecoverable, not fresh;
15. revoked bridge cannot resurrect retired verifier;
16. new destination lineage without committing prior floor rejected.

### C. Distributed unlearning invalidation partition/heal
17. one chain catches up monotonically;
18. concurrent incomparable checkpoints => fork;
19. healed merge uses union of invalidations;
20. latest-writer-wins dropping an invalidation rejected;
21. stale replica blocked from positive authority-bearing cached read;
22. compacted tombstones recover from covering checkpoint;
23. descendant issued on partitioned stale theorem/profile is invalidated after heal;
24. membership change during fork rejects new replica vote before catch-up.

### D. Privacy lineage collision
25. duplicate restored copies of same root collide and merge conservatively;
26. consumed-loss floor cannot decrease;
27. unresolved reservation union retained;
28. same analysis id/same payload deduplicated;
29. same analysis id/different payload => fork;
30. coordinator/shard rename does not mint budget;
31. independently created same-parent descendants require reconciliation;
32. different physical root ids with authenticated common budget ancestor join one lineage.

### E. Provider late completion after TTL
33. normal completion before TTL => confirmed;
34. lost response => `EFFECT_UNKNOWN`;
35. same-token/same-parameters retry while dedupe valid allowed;
36. same-token/different-parameters retry rejected;
37. blind retry after dedupe TTL rejected;
38. late authenticated completion after TTL resolves original effect only;
39. late completion conflicting with authenticated no-effect => evidence fork;
40. completion of original effect after separately authorized compensating effect preserves both identities.

### F. GC scope split/merge across authority rotation
41. one-scope successor supersedes only its explicit scope;
42. split children both bind parent and complete coverage;
43. split with gap/ambiguous overlap => incomplete;
44. merge commits both parent checkpoints and union safety floor;
45. authority rotation across split requires valid continuity;
46. revoked newer checkpoint does not revive retired older authority;
47. retained partial checkpoint set with missing covered scope blocks destructive GC;
48. detailed proof deletion allowed only after exact successor compact scope/effect checkpoint is durable.

## Implementation order once exact execution returns

1. Encode state enums and canonical digest payloads before adding mutation paths.
2. Write the 48 negative/positive cases as tests against isolated contract objects first.
3. Implement append-only generation/succession checks.
4. Add conservative merge functions for invalidation/privacy/GC scope DAGs.
5. Add provider effect state machine with explicit dedupe-expired recovery mode.
6. Run focused RED/GREEN, then compose with the relevant LAB-090..100 surfaces only after exact source identity is verified.

## Audit conclusion

This freeze deliberately refuses three tempting shortcuts: re-signing compact evidence as fresh proof, treating restored physical identity as new logical authority/budget, and retrying an unresolved provider mutation after idempotency retention expires. Across all six domains, retained compact evidence is a monotonic lower bound on what must remain unsafe/retired/consumed/unknown, not a license to infer missing detail optimistically.
