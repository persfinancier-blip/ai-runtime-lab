# Current Lab State

Last updated: 2026-08-20

## Active objective

Finish integrating LAB-063, then investigate the newly exposed archive-publication durability boundary between filesystem rename durability and the SQL commit that makes an archive authoritative.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-062.
- Issue #117 / LAB-063 — acceptance criteria satisfied; pending integration.
- Active branch: `lab/063-archive-scavenging`.
- Active PR: #118, remote-audited and mergeable at corrected HEAD.

## Last completed step

The first LAB-063 slice was deliberately rejected after audit because its executable tests used only a fake LAB-062-shaped layer. The corrected implementation now interoperates with the real `SignedPrunableHistory`: real `ArchiveManifest.parse`, `_verify_manifest_identity`, authenticated `_reachable_archive_ids`, real archive paths, real `fail_after_archive=True`, committed-UNKNOWN handling, multi-archive chaining, and a concurrent compaction-vs-GC race.

The final destructive boundary is `authenticated mark -> durable grace -> BEGIN IMMEDIATE -> authenticated reachability recheck -> content-address verification -> unlink`. Because LAB-062's final compaction commit also requires a SQLite write transaction, a candidate cannot become authoritative between the final reachability check and unlink. If GC wins first, compaction fails closed or republishes/revalidates before commit; if compaction wins first, GC observes the archive as reachable and retains it.

## Evidence produced

- `experiments/archive_scavenging/protocol.py`
- `experiments/archive_scavenging/tests/test_protocol.py`
- `experiments/archive_scavenging/tests/test_signed_integration.py`
- `experiments/archive_scavenging/tests/unsafe_eager_delete_expected_failure.py`
- `experiments/archive_scavenging/README.md`
- `research/2026-08-20-crash-safe-archive-scavenging.md`
- Earlier isolated algorithm suite: 9/9 passed; unsafe eager-delete seed failed as expected; compileall passed.
- Corrected real integration observed in this run: `fail_after_archive=True` orphan reclaimed after grace while five signed live transitions remained restartable; `timeout_after_commit=True` committed archive was never a candidate; two sequential real compactions preserved both current and historical reachable archives.
- Real compaction-vs-GC race repeated 20 times with no committed compaction base referencing missing archive files.
- Remote PR audit confirms branch is ahead of `main` with no behind commits; LAB-063 adds seven new files and updates only this durable state file.
- Direct GitHub DNS/checkout is unavailable in this runtime, so the corrected integration execution used connector-retrieved authoritative source/interfaces rather than claiming an unavailable full git checkout. No GitHub Actions/workers were used.

## Known blockers / constraints

- No active repository blocker.
- Archive cleanup is storage reclamation, not forensic erasure, backup retention, secure deletion, remote-object lifecycle, or distributed garbage collection.
- Whole-store rollback/freshness remains delegated to LAB-034–037 external monotonic anchors.
- LAB-062 `_atomic_file()` fsyncs file contents before `os.replace`, but does not fsync the parent directory. LAB-063 therefore proves process-crash/SQL-race safety, not sudden host/power-loss durability of archive publication.
- SQLite is the current reference locking boundary; PostgreSQL-specific validation remains deferred until a representative runtime exists.

## Exact next action

Integrate PR #118 and close Issue #117 as DONE. Then create the next issue for filesystem archive-publication durability: verify the exact durability ordering needed before SQL may commit an archive reference (`write -> fsync(file) -> atomic rename -> fsync(parent directory) -> verify publication -> SQL commit`), inject failures around every boundary, and distinguish process-crash guarantees from sudden power-loss/filesystem guarantees. Do not overclaim universal durability across filesystems; record platform/filesystem assumptions explicitly.

## Backlog

- Next: archive publication fsync / power-loss durability conformance (LAB-064 candidate).
- Crash-resilient scavenging for named credential-file fallback — candidate follow-up.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
