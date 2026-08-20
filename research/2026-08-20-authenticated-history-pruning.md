# LAB-061 — Authenticated history pruning and archival boundary

Date: 2026-08-20  
Issue: #113

## Question

Can a verified/checkpointed transition prefix be removed from the live SQL store without changing restart correctness, while preserving a separately auditable exact archive?

## Donors and transferable mechanisms

- SQLite transactions provide an atomic commit boundary: live `compaction_base`, archive-manifest registration, and prefix deletion belong in one write transaction. An interrupted transaction must expose either the old or committed new database state, not a half-pruned logical state.
- Git's content-addressed object model is the useful archive-identity donor: immutable archive bytes are named by a digest of canonical content, so substitution is detected by recomputing identity rather than trusting a filename.
- LAB-060's authenticated checkpoint remains the authorization boundary. Compaction is not allowed from caller-supplied derived state.

Primary sources:
- https://www.sqlite.org/atomiccommit.html
- https://www.sqlite.org/lang_transaction.html
- https://git-scm.com/book/en/v2/Git-Internals-Git-Objects.html

## Protocol

The live authoritative state after compaction is:

`(base_sequence, root_id, recovery_id, cumulative_prefix_commitment, latest_archive_id, checkpoint_id) + retained transition suffix`.

Compaction has two phases:

1. Under a consistent read snapshot, authenticate the current checkpoint, derive exact canonical archive bytes for `(old_base, checkpoint]`, and write/fsync the content-addressed archive and manifest.
2. Start one SQLite `BEGIN IMMEDIATE`, re-authenticate the same checkpoint and reproduce the same archive digest, verify archive files, atomically register the manifest, advance `compaction_base`, and delete the checkpointed transition rows.

A crash after archive export but before SQL commit can leave an orphan archive file, but the live DB is still the pre-prune state. A crash during the SQL transaction rolls back. A timeout after COMMIT is an unknown outcome; restart resolves it from durable `compaction_base`.

## Archive semantics

Archive bytes are deliberately **not required for normal restart**. Runtime correctness uses the authenticated compacted base plus the retained suffix. Forensic audit is a separate operation that reads the archive artifact, recomputes its SHA-256, replays its rolling commitment, and compares exact history/archive identity.

The SQL manifest referenced by the current base is required. Missing/tampered archive files fail closed when forensic audit is requested. The base itself is re-bound to the authenticated checkpoint after restart; neither `compaction_base` nor an archive manifest is accepted as an unauthenticated replacement authority.

## Failure matrix

The corrected experiment covers:
- unsafe delete-before-archive/checkpoint;
- crash after archive export before live-store commit;
- crash inside prune transaction;
- timeout after committed prune;
- stale/substituted checkpoint;
- tampered base checkpoint;
- missing/substituted archive manifest;
- wrong history identity in archive metadata;
- tampered archive artifact;
- retained suffix gap;
- head mismatch;
- successful restart after prune;
- new transitions after prune;
- second compaction;
- storage bounded by retained suffix.

## Audit finding

The first implementation allowed a SQL archive manifest with a substituted `history_id` to survive normal restart because restart compared only the base fields. This was fixed by recomputing the archive manifest content identity and binding it to the current history identity. A second audit tightened the boundary further: the compacted base now re-verifies the exact persisted checkpoint signature/content after restart, so compaction metadata cannot silently replace checkpoint authority.

## Boundaries / non-goals

- Deleting SQLite rows is not forensic erasure.
- This does not build remote archival storage or backup durability.
- A fully rolled-back but internally consistent DB snapshot is not detectable locally; LAB-034–037 external monotonic anchors remain authoritative for whole-store freshness.
- Local compaction is not distributed consensus or fork prevention.
- The reference experiment isolates compaction/archival semantics; production integration must retain LAB-059/060 threshold-signature verification rather than weakening transition-proof semantics.
