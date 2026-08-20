# Current Lab State

Last updated: 2026-08-20

## Active objective

LAB-064 — prove the filesystem durability boundary required before SQL may commit an authoritative reference to a newly published archive artifact/manifest.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-063.
- Completed Issue #117 / LAB-063.
- Merged PR #118 / LAB-063 as `deecb1f5ddc629c60b9d140a3e792863c3441708`.
- Next: Issue #119 / LAB-064 — READY.
- Active branch: none yet.
- Active PR: none.

## Last completed step

LAB-063 corrected its initial fake-layer-only gap and integrated scavenging with the real LAB-062 `SignedPrunableHistory`. Unreferenced content-addressed archive files are now reclaimed only after an authenticated reachability mark, a durable grace generation, a SQL write-locked reachability recheck, and content-address verification. Real `fail_after_archive=True`, committed-UNKNOWN, multi-archive reachability, restart, and compaction-vs-GC behavior were exercised; the race was repeated 20 times without an authoritative committed base referencing missing archive files.

PR #118 was remote-audited and squash-merged as `deecb1f5ddc629c60b9d140a3e792863c3441708`; Issue #117 is DONE.

## Evidence produced

- `experiments/archive_scavenging/protocol.py`
- `experiments/archive_scavenging/tests/test_protocol.py`
- `experiments/archive_scavenging/tests/test_signed_integration.py`
- `experiments/archive_scavenging/tests/unsafe_eager_delete_expected_failure.py`
- `research/2026-08-20-crash-safe-archive-scavenging.md`
- Isolated algorithm suite: 9/9 passed; unsafe eager-delete seed failed as expected; compileall passed.
- Real integration: uncommitted archive orphan reclaimed safely; committed archive protected; two compaction archives remained reachable; 20/20 compaction-vs-GC race repetitions preserved the authoritative-file invariant.
- Linux `fsync(2)` confirms that syncing file data/metadata does not necessarily persist the containing directory entry; explicit directory `fsync()` is separately required.
- SQLite atomic-commit documentation independently uses directory synchronization around journal namespace changes and documents filesystem/power-loss assumptions.

## Known blockers / constraints

- No active repository blocker.
- Direct GitHub DNS/checkout was unavailable in the LAB-063 runtime; connector-retrieved repository source remained the authoritative source path and no GitHub Actions/workers were used.
- LAB-062 `_atomic_file()` currently fsyncs the temporary file and then `os.replace()`s it, but does not fsync the parent directory. Atomic rename and durable namespace publication are therefore not yet equivalent in the lab's model.
- Filesystem/storage durability depends on platform, filesystem, mount/storage stack and device behavior; LAB-064 must state assumptions and fail closed rather than claim universal power-loss guarantees.
- Whole-store rollback/freshness remains delegated to LAB-034–037 external monotonic anchors.
- PostgreSQL-specific locking/performance validation remains deferred until a representative runtime exists.

## Exact next action

Start Issue #119 / LAB-064. Extend the existing LAB-062 archive publication primitive rather than creating a parallel archive subsystem. Build an explicit publication state/fault model around `write temp -> fsync(file) -> rename/replace -> fsync(parent directory)` for both artifact and manifest, then prove that SQL compaction cannot commit an archive reference until both names have crossed the required durable publication barrier. Inject failures at each step, preserve LAB-062/LAB-063 semantics, and distinguish process-crash evidence from sudden power-loss/filesystem guarantees.

## Backlog

- #119 / LAB-064 — filesystem archive-publication durability and fsync-boundary conformance — READY.
- Crash-resilient scavenging for named credential-file fallback — candidate follow-up.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
