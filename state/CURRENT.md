# Current Lab State

Last updated: 2026-08-20

## Active objective

LAB-064 — prove the filesystem durability boundary required before SQL may commit an authoritative reference to a newly published archive artifact/manifest.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-063.
- Completed Issue #117 / LAB-063; PR #118 merged as `deecb1f5ddc629c60b9d140a3e792863c3441708`.
- Issue #119 / LAB-064 — IN_PROGRESS.
- Active branch: `lab/064-archive-publication-durability`.
- Active draft PR: #120.

## Last completed step

Primary-source research confirmed the gap: Linux `fsync(2)` explicitly states that syncing a file does not necessarily persist the containing directory entry and that an explicit directory `fsync()` is needed; POSIX rename provides atomic namespace replacement but that is not the same property as sudden-power-loss durability; SQLite's atomic-commit design independently synchronizes directory namespace changes and documents filesystem/storage assumptions.

An initial implementation slice now exists. `experiments/archive_publication_durability/protocol.py` defines `durable_publish()` as `write -> flush -> fsync(file) -> os.replace -> fsync(parent directory)` and returns a `PublicationReceipt` only after both file and directory barriers succeed. `require_durable_pair()` requires durable receipts for both artifact and manifest. Deterministic fault hooks cover write, file-fsync, rename, and directory-fsync boundaries, and an unsafe rename-only receipt is retained as a negative baseline.

LAB-062 `experiments/signed_history_compaction/archive.py` now delegates `_atomic_file()` to this durable publisher. `compact()` will not open/commit its authoritative SQL mutation unless both publication receipts are durable and the artifact receipt digest matches the signed manifest. Focused unit and real signed-compaction integration tests have been added. Draft PR #120 is intentionally not merge-authorized until exact published-source execution and regression audit are complete.

## Evidence produced

- Issue #119 with primary donor links and explicit failure matrix.
- `experiments/archive_publication_durability/protocol.py`
- `experiments/archive_publication_durability/tests/test_protocol.py`
- `experiments/archive_publication_durability/tests/test_signed_compaction_integration.py`
- `experiments/archive_publication_durability/README.md`
- `research/2026-08-20-archive-publication-durability.md`
- Modified LAB-062 `experiments/signed_history_compaction/archive.py` to require durable artifact+manifest publication receipts before SQL commit.
- Draft PR #120 opened for auditable continuation.
- A small local prototype of the same publication sequence was executed successfully before publication and confirmed injected failures at write/file-fsync/rename boundaries, but this is supporting evidence only; exact published branch tests remain to be executed.

## Known blockers / constraints

- No design blocker.
- Direct git/raw GitHub DNS was unavailable in this runtime, so exact branch checkout was not available through the shell. GitHub connector is the authoritative repository path.
- Exact published LAB-064 tests and LAB-062/LAB-063 regression suites have not yet been executed as a complete branch-source suite; do not merge or mark PR #120 ready until they are.
- A successful directory `fsync()` is still a platform/filesystem/storage-stack contract, not a universal physical-media guarantee. The research note must keep this boundary explicit.
- Process-crash orphan cleanup remains LAB-063; whole-store rollback/freshness remains LAB-034–037.

## Exact next action

Resume Issue #119 / draft PR #120 on `lab/064-archive-publication-durability`. Obtain/execute the exact published branch source through the best available connector/local reconstruction path. Run `archive_publication_durability` focused tests, then relevant LAB-062 signed-compaction and LAB-063 scavenging regressions plus compileall. Inspect failures and fix them. Perform a separate remote patch audit, including the modified existing LAB-062 `archive.py`. Only then mark acceptance criteria satisfied, mark PR ready, and merge.

## Backlog

- #119 / LAB-064 — IN_PROGRESS; draft PR #120.
- Crash-resilient scavenging for named credential-file fallback — candidate follow-up.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
