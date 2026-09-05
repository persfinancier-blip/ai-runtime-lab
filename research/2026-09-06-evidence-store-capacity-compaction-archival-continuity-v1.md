# Durable evidence-store capacity reservation / compaction / archival continuity contract v1

Status: `EVIDENCE_STORE_CAPACITY_COMPACTION_ARCHIVAL_CONTINUITY_V1_FROZEN`

Date: 2026-09-06

Scope: LAB-093 follow-up under #178. Design/evidence contract only. No production compactor/archiver implementation or behavioral PASS is claimed.

## Problem

The prior observer-durability contract requires a synchronous durable `SINK_ENTERED` barrier before consequential I/O and requires post-I/O evidence loss to move only toward `UNKNOWN`. That contract is incomplete if the evidence store can later exhaust disk, checkpoint/truncate away the only recoverable state, compact unresolved attempts, or restore an older archive that is internally valid but globally stale.

Capacity management is therefore part of authority, not housekeeping. A store may reclaim physical space only when it can prove that the reclaimed bytes are no longer the sole carrier of any evidence needed for replay, ambiguity classification, audit, authority continuity, or manual resolution.

## Frozen invariants

### I1. Reserve is measured in durable writable bytes, not reported free space alone

The runtime maintains a conservative `evidence_reserve_bytes` budget sufficient for a bounded emergency envelope containing at least:

- one new `SINK_ENTERED` barrier per admitted in-flight consequential slot;
- one terminal/ambiguity observation per admitted slot;
- one quarantine/shutdown marker;
- one compaction/archive manifest transition;
- one recovery-journal segment footer/rollover record;
- WAL/checkpoint amplification and filesystem metadata margin.

`statvfs`-style free bytes are advisory input only. Admission also accounts for configured filesystem quota, SQLite `page_size/page_count/max_page_count`, WAL/journal size, archive staging requirements, and worst-case copy/checkpoint amplification.

When the reserve would be crossed, new consequential `SEND/MUTATE/RESUME/TOKEN_MINT` authority is removed before ENOSPC. Read-only reconciliation may continue if it does not consume the protected reserve.

### I2. Capacity has explicit watermarks and hysteresis

Define at minimum:

- `NORMAL`: reserve comfortably satisfied;
- `HIGH_WATER`: new high-volume/nonessential evidence producers throttled;
- `QUARANTINE_WATER`: no new consequential provider attempts admitted;
- `EMERGENCY_RESERVE`: bytes protected for safety markers/recovery only.

Returning from quarantine requires both recovered capacity above a separate lower watermark and successful continuity verification; it is not triggered merely by a transient increase in free-space counters.

### I3. WAL checkpoint is not evidence deletion

Checkpointing copies committed WAL frames into the database; it does not authorize deletion of logical evidence rows. WAL truncation is allowed only after SQLite reports a completed checkpoint appropriate for the admitted mode and the database-level evidence invariants have been re-verified.

A PASSIVE checkpoint may be incomplete under concurrent readers/writers and therefore cannot be treated as proof that truncation/reclamation succeeded. `TRUNCATE` or equivalent aggressive checkpointing is a storage operation, not a semantic compaction decision.

Long-lived readers/checkpoint starvation are capacity hazards: if WAL growth threatens reserve, admission is reduced/quarantined rather than assuming a future checkpoint will succeed.

### I4. Logical compaction is append-only at the authority layer

Compaction must create a new authenticated `CompactionManifestV1`; it must never silently rewrite history in place.

The manifest binds:

- source authority/global-provenance generation;
- source evidence range/segment IDs and digests;
- exact retained records or retained canonical summary commitments;
- pin-set digest;
- destination/archive object digests;
- compactor implementation/profile version;
- prior compaction-manifest digest;
- resulting logical frontier/root;
- deletion eligibility proof.

Only after the manifest is durable and independently verified may source bytes become deletion candidates.

### I5. `UNKNOWN` and manual-resolution evidence is pinned

Any attempt in `UNKNOWN`, `EVIDENCE_GAP_UNKNOWN`, unresolved provider-recovery, pending challenge/quarantine, manual reconciliation, disputed audit, or active incident state is pinned.

Pinned means:

- all identity/authority/replay-capsule records required to reconstruct the attempt remain online or in an immediately verifiable archive tier;
- no summary-only compaction may destroy provider request identity, semantic request digest, `SINK_ENTERED`, observation chain, retry history, or protocol-certified non-processing proof;
- retention expiry alone cannot unpin an unresolved consequential attempt.

Unpin requires a durable terminal resolution whose authorization is bound to the exact attempt/effect and, where required by parent contracts, explicit product/security/business approval.

### I6. Safe deletion requires two independent proofs

A source segment/row range is deletion-eligible only when both are true:

1. **semantic proof**: no unresolved/pinned attempt, active authority dependency, challenge, audit hold, or replay window requires the original material;
2. **continuity proof**: an authenticated replacement/archive commitment exists and verifies as a descendant of the currently trusted global evidence frontier.

Neither `age > retention_days` nor `archive upload returned 200` is sufficient.

### I7. Archive is content-addressed and authenticated before source deletion

Every archive object is written under an immutable content identity and accompanied by an authenticated `ArchiveManifestV1` containing object digest, byte length, format/version, logical evidence range, authority/provenance generation, previous archive-manifest link, and restore prerequisites.

Deletion requires a read-after-write verification from the archive destination that recomputes the complete object digest/length from retrieved bytes, not merely provider metadata or ETag semantics.

If remote object-lock/WORM semantics are available they are useful defense-in-depth, but they do not replace cryptographic continuity and restore verification.

### I8. Restore is rollback-sensitive

A cryptographically valid archive may still be stale. Restore therefore requires:

- verifying every object digest and archive-manifest chain;
- verifying inclusion/continuity to the expected trusted evidence frontier;
- verifying the restored frontier is not older than the externally retained monotonic/global provenance anchor;
- replaying compaction/archive manifests in order;
- refusing to auto-admit consequential authority until all pinned/unresolved attempt state is reconstructed and classified.

An older self-consistent snapshot is a rollback, not a valid restore.

### I9. Backup snapshots are staging artifacts until continuity is sealed

SQLite Online Backup or `VACUUM INTO` may create a consistent database image, but that image is not an authoritative archive by itself. It becomes admissible only after the archive manifest binds its digest to the trusted logical frontier and restore checks prove the same authority/provenance state.

Online backup may restart internally when the source changes; the resulting completed image is consistent, but the system must bind the exact completed image, not assumptions about which intermediate source pages were copied.

### I10. Compaction cannot synthesize negative evidence

A compacted summary may preserve authenticated positive facts, terminal classifications, and chain commitments. It may not infer `FAILED_BEFORE_IO` from absence of older low-level records.

If deleting detailed transport observations would make a future classifier unable to distinguish `UNKNOWN` from a stronger terminal state, the records remain pinned or the summary must contain the already-authenticated terminal proof sufficient to reproduce the classification.

### I11. Retention is class-specific

Evidence classes have separate minimum retention/pinning rules:

- authority/provenance roots, generation transitions, compaction/archive manifests: retained for the lifetime of descendants or externally anchored beyond local deletion;
- unresolved consequential attempts: retained until explicit terminal resolution plus downstream retention window;
- terminal provider-confirmed/certified-not-processed attempts: eligible only after replay/idempotency/provider-retention windows close and audit policy permits;
- diagnostic/non-authority telemetry: separately reclaimable and may never share the emergency reserve budget with authority evidence.

A single global TTL is not admitted.

### I12. Physical SQLite reclamation follows semantic deletion, never precedes it

`DELETE`, freelist growth, incremental vacuum, full VACUUM, page compaction, or database rewrite are physical storage operations after logical deletion eligibility has been proven.

`VACUUM`/auto-vacuum behavior must not be used as the authority decision for what may be removed. Physical reclamation may be deferred; lack of immediate file shrink is not evidence loss.

### I13. Compaction and archive jobs are authority-visible maintenance operations

A compactor/archiver runs with least capability. It can read admitted ranges, create immutable archive objects/manifests, and request deletion of ranges that already carry a valid deletion proof. It cannot mint provider-effect authority, resolve `UNKNOWN`, alter evidence payloads, rewrite parent manifests, or unpin attempts.

Crash/restart is idempotent: repeated upload of the same content identity must verify equality; repeated deletion of an already-deleted eligible segment is a no-op; same identity/different bytes is corruption.

### I14. Segment rotation preserves a continuous digest chain

For append-only recovery journals, every sealed segment has a footer containing segment ID, first/last record identity, record count, complete segment digest, previous sealed-segment digest, authority/provenance generation, and next-segment handoff nonce/digest.

The next segment header binds the previous footer. Missing middle segments, duplicate divergent segment IDs, or a broken chain fail closed. Segment deletion requires an archive/compaction manifest that commits to the exact sealed digest.

### I15. Space amplification is included in admission proofs

Capacity planning uses worst-case, not steady-state, storage cost. At minimum model:

`live_db + wal_peak + recovery_journal_open_segment + archive_staging_copy + compaction_output + filesystem_overhead + emergency_reserve`.

If the selected operation may temporarily duplicate the whole DB (for example a rewrite/backup/vacuum profile), it is prohibited unless that temporary amplification fits without consuming emergency reserve.

### I16. `max_page_count` is a guardrail, not reserve management

SQLite `max_page_count` can force `SQLITE_FULL` when the database reaches a configured page bound. It may be used as an outer safety bound, but setting it does not reserve filesystem bytes for WAL, journals, archive staging, or other processes. Therefore it cannot substitute for cross-file reserve accounting.

### I17. Checkpoint/compaction scheduling cannot run on the consequential critical path by default

The pre-I/O evidence barrier must remain small and bounded. Heavy checkpoint, archive upload, backup, vacuum, digest scans, and compaction run outside provider/pool locks and outside the provider send critical path.

If background maintenance cannot keep up and reserve drops, the correct response is admission throttling/quarantine, not making the provider send path wait indefinitely for compaction.

### I18. Startup verifies continuity before admitting new consequential authority

Startup/recovery order:

1. verify filesystem/storage profile and reserve inputs;
2. recover SQLite/WAL/journal according to the admitted durability profile;
3. validate open and sealed segment chains;
4. validate compaction and archive manifest chains;
5. restore/materialize any required pinned evidence;
6. verify no deletion precedes its deletion proof;
7. verify global provenance/external monotonic frontier against local/restored frontier;
8. classify all incomplete/pinned attempts conservatively;
9. only then admit the authority otherwise allowed by parent contracts.

## Suggested data contracts

### `CapacityStateV1`

- filesystem/device identity;
- measured free bytes and quota headroom;
- SQLite page size/page count/max page count;
- DB/WAL/journal/staging byte counts;
- configured worst-case amplification;
- emergency reserve bytes;
- admitted concurrent consequential slots;
- watermark state;
- measurement timestamp/sequence;
- profile/version digest.

### `EvidencePinV1`

- evidence/attempt identity;
- pin reason enum;
- authority/effect/replay identities;
- minimum required record set or range;
- creation generation;
- optional release authorization reference;
- terminal resolution reference when released.

### `ArchiveManifestV1`

- domain/version;
- archive object content digest + byte length;
- covered evidence range/segment list;
- logical frontier/root before and after archival;
- authority/global-provenance generation;
- previous archive-manifest digest;
- storage-class/provider/location identifier as metadata only;
- read-after-write verification evidence;
- restore profile/version.

### `CompactionManifestV1`

- source range/segment digests;
- retained canonical commitments/summaries;
- pin-set digest;
- archive-manifest references;
- previous compaction-manifest digest;
- resulting frontier/root;
- exact deletion-eligible identities;
- implementation/profile digest;
- authenticated approval/quorum required by parent authority contract.

## RED-first fault matrix

Freeze at least the following 72 cases before implementation is admitted.

### A. Capacity accounting and reserve (9)
1. normal reserve with no in-flight attempts;
2. reserve scales with admitted concurrent attempts;
3. filesystem quota lower than nominal free space wins;
4. WAL/journal/staging bytes included;
5. worst-case backup/compaction amplification included;
6. high-water throttles nonessential producers;
7. quarantine occurs before emergency reserve is consumed;
8. transient free-space recovery does not bypass hysteresis/continuity check;
9. `max_page_count` alone cannot satisfy reserve proof.

### B. WAL/checkpoint behavior (9)
10. PASSIVE checkpoint incomplete under reader does not authorize truncation claim;
11. successful FULL/RESTART/TRUNCATE profile reports expected frame state;
12. checkpoint starvation grows WAL and triggers admission reduction;
13. checkpoint SQLITE_BUSY is bounded;
14. crash during checkpoint preserves committed evidence semantics;
15. WAL truncation never deletes logical rows;
16. long reader cannot force emergency reserve exhaustion before quarantine;
17. checkpoint runs outside provider locks;
18. startup verifies recovered DB/WAL frontier before sends.

### C. Pinning and retention (9)
19. `UNKNOWN` attempt pinned;
20. `EVIDENCE_GAP_UNKNOWN` pinned;
21. active manual reconciliation pinned;
22. open challenge/quarantine evidence pinned;
23. TTL expiry cannot unpin unresolved attempt;
24. terminal provider-confirmed attempt remains until provider replay window closes;
25. terminal certified-not-processed proof retained sufficiently to reproduce classification;
26. diagnostic telemetry may expire independently;
27. authorized terminal resolution releases only the exact pin.

### D. Archive creation and verification (9)
28. immutable content-addressed upload succeeds;
29. read-after-write digest/length match required;
30. provider metadata match with wrong retrieved bytes fails;
31. upload timeout with unknown object state reconciles by content identity;
32. duplicate same-content upload is idempotent;
33. same archive identity/different content fails closed;
34. manifest links exact object and evidence range;
35. source deletion forbidden before verified manifest durability;
36. archive destination unavailable triggers capacity quarantine before reserve exhaustion.

### E. Compaction/deletion proof (9)
37. compaction manifest preserves parent chain;
38. pinned record included in delete set is rejected;
39. unresolved attempt summarized without required raw identities is rejected;
40. age/TTL-only deletion is rejected;
41. valid semantic proof without archive continuity is rejected;
42. valid archive continuity without semantic eligibility is rejected;
43. exact delete set succeeds only after both proofs;
44. compactor crash after manifest/before deletion resumes idempotently;
45. crash mid-deletion cannot make remaining state look like a fresh store.

### F. Journal segment rotation (9)
46. clean segment seal and next-header linkage;
47. torn footer leaves segment unsealed/not deletable;
48. missing middle sealed segment fails closed;
49. divergent duplicate segment ID fails closed;
50. archive binds exact sealed segment digest;
51. source segment deletion before archive proof rejected;
52. restore preserves record order and previous-digest chain;
53. wrong authority epoch segment rejected;
54. open segment has reserved rollover/footer space.

### G. Backup/restore/rollback (9)
55. online backup completes to a consistent snapshot;
56. snapshot not authoritative until digest/frontier manifest sealed;
57. restore of bit-valid but older snapshot fails external/global frontier check;
58. missing newest archive manifest fails closed;
59. corrupted archive object fails digest check;
60. restored pin set equals authenticated expected set;
61. unresolved attempts reconstruct to UNKNOWN, not terminal-by-absence;
62. compaction manifests replay in order;
63. authority remains withheld until full restore verification completes.

### H. Physical reclamation and operations (9)
64. logical deletion can occur without immediate file shrink;
65. incremental/full vacuum runs only after semantic deletion proof;
66. insufficient temporary space rejects VACUUM/backup profile before starting;
67. ENOSPC during staging leaves source authoritative and intact;
68. compactor cannot resolve UNKNOWN or mint SEND authority;
69. archive worker cannot mutate provider request/effect state;
70. maintenance backlog lowers admission rather than blocking provider path indefinitely;
71. profile/version drift invalidates deletion/restore admission until reverified;
72. clean compaction+archive+restore roundtrip preserves exact authenticated logical frontier.

## Donors / evidence

Primary sources consulted 2026-09-06:

1. SQLite WAL documentation: checkpoints transfer committed WAL content into the database; default auto-checkpoint is 1000 pages; PASSIVE checkpoints may remain incomplete under concurrent use; long-lived readers can cause checkpoint starvation and unbounded WAL growth. https://sqlite.org/wal.html
2. SQLite `sqlite3_wal_checkpoint_v2`: exposes total WAL/checkpointed frames; PASSIVE does not wait, and successful TRUNCATE reports the log truncated to zero bytes. https://sqlite.org/c3ref/wal_checkpoint_v2.html
3. SQLite Online Backup API: completed backup is a consistent snapshot; incremental backup can release locks between steps and may restart when the source changes. https://sqlite.org/backup.html
4. SQLite PRAGMAs/limits: `page_count`, `max_page_count`, auto/incremental vacuum. `max_page_count` causes SQLITE_FULL at the database-file bound but does not reserve capacity for WAL/journals/staging. https://sqlite.org/pragma.html and https://sqlite.org/limits.html
5. RFC 9162 / Certificate Transparency v2 Merkle-tree construction: append-only log states can be committed by tree roots with inclusion/consistency proofs. This is a donor for authenticated archive/compaction frontier continuity, not a claim that CT itself supplies the runtime archive format. https://www.rfc-editor.org/rfc/rfc9162.html

## Decision

Freeze `EVIDENCE_STORE_CAPACITY_COMPACTION_ARCHIVAL_CONTINUITY_V1_FROZEN`.

The critical rule is: **space reclamation is permitted only after a durable authenticated replacement/continuity proof and a separate semantic proof that the source bytes are no longer needed.** `UNKNOWN`, manual-resolution, active challenge/quarantine, replay identities, and global provenance remain pinned. Capacity pressure removes future consequential authority before it is allowed to consume the emergency evidence reserve.

This keeps checkpointing, backup, vacuum, compaction, archive, and restore subordinate to the same authority/evidence chain rather than allowing storage maintenance to create an independent rollback or evidence-erasure path.

## Next distinct evidence task

If LAB-086 exact execution remains unavailable, freeze an **evidence retention / cryptographic-erasure / privacy minimization versus auditability contract**: define which provider payload/body/header fields must never enter durable evidence, redaction/tokenization before the pre-I/O barrier, digest commitments for later proof, key separation and key-destruction semantics, legal/privacy retention holds versus unresolved-security pinning, and a RED-first matrix proving that minimization cannot destroy retry/UNKNOWN/manual-resolution evidence required by the authority contracts.