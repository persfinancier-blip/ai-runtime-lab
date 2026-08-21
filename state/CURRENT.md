# Current Lab State

Last updated: 2026-08-21

## Active objective

LAB-066 — reconstruct archive namespace authority after process restart without silently trusting pathname, recycled inode/mount identifiers, or byte-identical replacement; support explicit generation-bound relocation and fail-closed detached-artifact handling.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-065.
- Active Issue #123 / LAB-066 — IN_PROGRESS.
- Active branch: `lab/066-namespace-reacquisition`.
- Draft PR #124 / LAB-066 — HEAD `ca9ab795757e155e61b7b295f54ca1b8bd838656`.

## Last completed step

Published the first executable LAB-066 slice. It persists an authenticated namespace continuity record containing lexical absolute archive path, namespace generation, boot ID, `st_dev/st_ino` observations, and Linux opaque file-handle evidence when `name_to_handle_at` is supported. Restart reacquisition reopens the configured directory without following symlinks and compares same-boot opaque handle identity. Byte-identical replacement and symlink replacement are rejected. A boot change or unavailable strong handle path fails closed as `UNSUPPORTED_STRONG_REACQUISITION` rather than degrading to pathname authority. Intentional relocation requires an authenticated migration permit that advances namespace generation by exactly one.

The current runtime can capture opaque file handles but still cannot demonstrate `open_by_handle_at` because `CAP_DAC_READ_SEARCH` is absent. Therefore missing/renamed-object recovery cannot be claimed as strong reacquisition in this environment.

## Evidence produced

- `experiments/namespace_reacquisition/protocol.py`
- `experiments/namespace_reacquisition/tests/test_protocol.py`
- `experiments/namespace_reacquisition/tests/unsafe_path_bytes_expected_failure.py`
- `experiments/namespace_reacquisition/README.md`
- `research/2026-08-21-namespace-reacquisition.md`
- Corrected local suite: 10/10 passed.
- Unsafe path+bytes baseline: failed as expected because byte-identical replacement was trusted.
- Relevant compileall passed.
- Draft PR #124 created; issue #123 updated with evidence and remaining gate.

## Known blockers / constraints

- No owner-level blocker.
- Direct shell GitHub DNS remains unreliable; GitHub connector reconstruction is the supported exact-source fallback.
- `open_by_handle_at` is not usable in the observed runtime without `CAP_DAC_READ_SEARCH`; do not silently weaken detached recovery to pathname trust.
- Opaque handles are filesystem-dependent and can become stale; mount IDs and `st_dev/st_ino` are not universal persistent cross-boot identities.
- Whole-store rollback/freshness remains LAB-034–037.
- Local cleanup is not forensic secure erasure.
- LAB-066 is not DONE until the continuity record is integrated with real SignedPrunableHistory and LAB-063 cleanup/reconciliation.

## Exact next action

Resume draft PR #124. Integrate the authenticated continuity record into real `SignedPrunableHistory`: persist the record alongside archive authority, require successful reacquisition before consequential archive read/write/compaction/scavenge after restart, bind namespace generation into receipts/evidence, and make migration fence stale generation. Add real integration tests for unchanged restart, copied-byte path replacement, symlink replacement, missing/detached directory, authenticated relocation, and LAB-063 refusing cleanup without reacquired namespace authority. Then reconstruct exact PR HEAD source if direct checkout remains unavailable, run LAB-066 plus LAB-065/LAB-062/LAB-063 regressions and compileall, perform a separate remote patch audit, and merge only if clean.

## Backlog

- #123 / LAB-066 — restart namespace reacquisition and detached-artifact reconciliation — IN_PROGRESS.
- Crash-resilient scavenging for named credential-file fallback — candidate follow-up.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
