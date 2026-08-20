# Current Lab State

Last updated: 2026-08-20

## Active objective

LAB-063 — reclaim crash-created or otherwise unreferenced local archive artifacts without ever deleting an archive still reachable from the authenticated LAB-062 compaction chain.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-062.
- Completed Issue #115 / LAB-062.
- Merged PR #116 / LAB-062 as `88c7de6da45c31e994130dcdcbcd0b42debfccf3`.
- Next: Issue #117 / LAB-063 — READY.
- Active branch: none yet.
- Active PR: none.

## Last completed step

LAB-062 directly integrated LAB-061 pruning/archive semantics with the real LAB-059 threshold-authenticated transition proof stack. Retained suffix and forensic archived rows reuse the existing authority content-ID lookup, `rotation_payload`, `recovery_payload`, `verify_threshold`, payload reconstruction, and transition-digest rules. A signed checkpoint authorizes the compaction boundary; exact archive bytes are written/fsynced first; then one SQLite `BEGIN IMMEDIATE` transaction revalidates inputs, records the archive/base, and deletes only the checkpointed prefix.

A separate audit found and fixed a cross-layer defect: a content-addressed archive manifest could previously authenticate an arbitrary start authority/commitment. The corrected design binds each archive start to the signed checkpoint `(base_sequence, base_archive_id)` and either the exact bootstrap state or the previous authenticated archive's terminal authority IDs/commitment. Explicit forensic audit also requires the selected archive to be reachable from the current authenticated archive chain.

## Evidence produced

- `experiments/signed_history_compaction/core.py`
- `experiments/signed_history_compaction/verify.py`
- `experiments/signed_history_compaction/archive.py`
- `experiments/signed_history_compaction/protocol.py`
- `experiments/signed_history_compaction/tests/test_protocol.py`
- `experiments/signed_history_compaction/tests/unsafe_delete_first_expected_failure.py`
- `experiments/signed_history_compaction/README.md`
- `research/2026-08-20-signed-history-compaction.md`
- Corrected deterministic suite: 15/15 passed.
- Unsafe delete-first seed: failed as expected because restart verification was destroyed.
- Compileall: passed.
- Exact branch/local Git blob identities matched for executable/test sources: core `a872eb82dd8ced697116b58778d8f29b52aa816a`; verify `cca6eef6c140043ad9e74dcb5f4cae8c647ff0a4`; archive `34067078f619a4b2421a784e64dfb1acf3f09e01`; protocol `6e52b601a2aa772899b008bdd6c5fc7d1a29dda6`; corrected tests `8cedb4d6d5c97879e296123a5b677e2263578b93`; unsafe seed `03dd6b95ab075b51770dd0620741041f03450f62`.
- Pre-PR compare: ahead 8 / behind 0; all eight LAB-062 paths were new.
- PR #116 remote patch-audited, mergeable, and squash-merged as `88c7de6da45c31e994130dcdcbcd0b42debfccf3`.

## Known blockers / constraints

- No active blocker.
- Direct shell/git network access to GitHub was unavailable in the LAB-062 run because DNS resolution failed; GitHub connector operations remained available and exact published new-source blob identities were checked against the locally executed bytes. Treat this as a per-run capability observation, not a persistent limitation.
- Archive bytes are not runtime authority; normal restart uses authenticated checkpoint/base/manifest binding plus retained signed suffix. Archive bytes are required for explicit forensic audit.
- LAB-062 intentionally writes archive files before the SQL prune commit. A crash before commit can therefore leave storage orphans; this is the immediate LAB-063 target.
- Whole-store rollback/freshness remains delegated to LAB-034–037 external monotonic anchors.
- SQL/file deletion is storage reclamation, not forensic erasure.
- Local compaction/scavenging is not distributed consensus, backup durability, or remote-object-store lifecycle management.

## Exact next action

Start Issue #117 / LAB-063. Extend LAB-062 rather than creating a separate garbage collector. Reproduce an orphan artifact+manifest via the fail-after-archive path, then build a scavenger that derives the protected archive set from authenticated current compaction state and the complete `previous_archive_id` chain. Require an explicit grace/generation boundary, reconcile UNKNOWN compaction outcomes, and re-check reachability immediately before deletion. Test artifact-only/manifest-only debris, current and historical reachable archives, candidate-becomes-referenced races, restart/idempotency, stale retention generation, and content-address substitution. Keep secure deletion, legal retention, backups, remote stores, and distributed GC out of scope.

## Backlog

- #117 / LAB-063 — crash-safe archive retention and orphan-artifact scavenging conformance — READY.
- Crash-resilient scavenging for named credential-file fallback — candidate follow-up.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
