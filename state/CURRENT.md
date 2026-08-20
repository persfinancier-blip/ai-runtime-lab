# Current Lab State

Last updated: 2026-08-20

## Active objective

LAB-063 — reclaim crash-created or otherwise unreferenced local archive artifacts without ever deleting an archive still reachable from the authenticated LAB-062 compaction chain.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-062.
- Issue #117 / LAB-063 — IN_PROGRESS.
- Active branch: `lab/063-archive-scavenging`.
- Active PR: #118.

## Last completed step

A first executable LAB-063 reference scavenger was built and published. It uses durable retention generations, derives protected archive IDs by walking the current archive head through `previous_archive_id`, marks only unreferenced content-addressed filesystem names as candidates, and rechecks reachability under a SQLite `BEGIN IMMEDIATE` write lock immediately before unlink. UNKNOWN outcomes are reconciled by rereading authoritative SQL state. Invalid/substituted content-address pairs fail closed instead of being silently erased.

Local corrected suite passed 9/9; the unsafe eager-delete seed failed as expected because it deleted a reachable archive; compileall passed. Pre-PR compare was ahead 6 / behind 0 with six new paths. PR #118 was opened and its complete remote patch was inspected.

## Audit finding — unresolved

The remote patch audit found a scope/integration weakness: the tests currently execute the scavenger against a compact fake LAB-062-shaped layer rather than the real `SignedPrunableHistory` implementation. That is useful algorithm evidence but does not yet satisfy Issue #117's requirement to extend LAB-062 and reproduce the real `fail_after_archive` orphan path. Therefore LAB-063 is deliberately NOT marked done and PR #118 must not be merged yet.

The next correction should add minimal GC identity helpers/mixin integration to `experiments/signed_history_compaction` (or otherwise adapt the scavenger directly to its existing `ArchiveManifest`, `_verify_manifest_identity`, `_reachable_archive_ids`, and `_archive_paths`) and add real integration tests using `ChainBuilder` + `SignedPrunableHistory.compact(..., fail_after_archive=True)`. The race test must also demonstrate the actual SQL locking interaction with compaction, not only a pre-delete state change.

## Evidence produced

- `experiments/archive_scavenging/protocol.py`
- `experiments/archive_scavenging/tests/test_protocol.py`
- `experiments/archive_scavenging/tests/unsafe_eager_delete_expected_failure.py`
- `experiments/archive_scavenging/README.md`
- `research/2026-08-20-crash-safe-archive-scavenging.md`
- Corrected algorithm suite: 9/9 passed.
- Unsafe eager-delete seed: failed as expected.
- Compileall: passed.
- PR #118 complete remote patch audited.

## Known blockers / constraints

- No external blocker.
- Current implementation is not yet accepted because its executable tests use a fake archive layer instead of the real LAB-062 layer.
- Archive cleanup is storage reclamation, not forensic erasure.
- Whole-store rollback/freshness remains delegated to LAB-034–037 external monotonic anchors.
- Local scavenging is not distributed GC, backup retention, remote-object lifecycle, or consensus.

## Exact next action

Resume PR #118. Integrate the scavenger with real `SignedPrunableHistory`; reproduce a real orphan via `compact(checkpoint, fail_after_archive=True)`; add real tests for reachable current/historical archives, artifact-only/manifest-only debris, UNKNOWN-after-commit reconciliation, stale generation, restart/idempotency, substitution, and a candidate-vs-compaction race. Re-run the full LAB-062 + LAB-063 suites and compileall, then remote patch-audit the corrected PR. Merge/close Issue #117 only if those tests pass and the audit finds no unresolved authority gap.

## Backlog

- #117 / LAB-063 — IN_PROGRESS.
- Crash-resilient scavenging for named credential-file fallback — candidate follow-up.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
