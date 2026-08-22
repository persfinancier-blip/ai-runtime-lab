# Current Lab State

Last updated: 2026-08-22

## Active objective

LAB-076 — complete the durable threshold sink-registry authority lifecycle without allowing historical-authority corruption, mixed SQLite snapshots, stale publication authority, or weaker unaudited compositions.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-075.
- Active: Issue #143 / LAB-076 — IN_PROGRESS.
- Active branch: `lab/076-registry-authority-lifecycle-v2`.
- Active draft PR: #144 `[LAB-076] Durable sink-registry authority lifecycle`.
- Current PR HEAD after this run's audit fixes: `3a1ece72e2609d783ca1f465ddded540d67b81e4`.
- PR #144 remains open, draft, and mergeable; 11 changed files.

## Last completed step

Re-read AGENTS.md / SELF_RESUME and re-fetched PR #144. Direct `git clone` was probed again and still fails because the runtime cannot resolve `github.com`, so connector reconstruction remains the supported exact-source fallback.

A fresh source audit found two additional defects before merge:

1. `_LifecycleAuthorityAdapter.verify()` treated a missing historical binding as a reason to retry current publication verification. For an already-published row this could hide deletion/corruption of `registry_authorized_entries`, especially before the first authority rotation.
2. `DurableRegistryAuthority.verify_durable()` performed multiple SELECTs in SQLite autocommit mode without a stable read/write-excluding window. Concurrent rotation/recovery could therefore produce a mixed-snapshot audit (normally fail-closed/spurious failure, but not a deterministic restart verifier).

Both are fixed on the branch through a new audited supported surface:
- `audit_fixes.py` adds `ConsistentDurableRegistryAuthority`, a strict historical-only adapter for inherited read paths, `CorrectedLifecycleRegistryBoundJournal`, and an exact-type-gated worker;
- standalone durable verification holds `BEGIN IMMEDIATE` while the base multi-query verifier runs;
- cross-layer journal verification holds the same write-excluding guard while lifecycle + LAB-075 durable verification execute;
- `supported.py` now exports only these audited classes;
- `test_supported_audit.py` adds regressions for missing historical binding and concurrent rotation fencing.

Issue #143 was updated with these audit fixes and the revised merge gate.

## Evidence produced

- PR #144 current HEAD: `3a1ece72e2609d783ca1f465ddded540d67b81e4`.
- New branch commits this run:
  - `4762659fa55f25057c4d4677141093f292635739` — audited supported lifecycle surface;
  - `897dee58ffcbc28ecd876a3cb7f86b88577fa01a` — route supported exports through audit fixes;
  - `3a1ece72e2609d783ca1f465ddded540d67b81e4` — supported-surface regressions.
- Earlier isolated lifecycle evidence remains 12/12, but it predates the current integrated HEAD and is **not** merge evidence for this HEAD.
- No exact-source test run is claimed for the new HEAD.

## Known blockers / constraints

- No owner/product blocker.
- Direct GitHub clone/raw download is unavailable in this runtime due DNS; connector reconstruction is required.
- Current PR #144 HEAD has not yet been executed as exact published source. Do not mark ready or merge yet.
- Exact-source regressions required: LAB-076 protocol + real integration + integration audit + supported audit, unsafe self-swap seed, merged LAB-075/074/073/072 suites, and compileall.
- Fresh full remote patch audit is required after those tests.
- Historical authority is verification-only and must never become publication authority again.
- Whole-store rollback/freshness remains delegated to LAB-034–037 external monotonic anchors.
- Recovery-authority rotation remains owned by LAB-057; LAB-076 intentionally keeps that subsystem separate.

## Exact next action

Re-fetch PR #144 and confirm HEAD `3a1ece72e2609d783ca1f465ddded540d67b81e4` (or record a newer exact HEAD). Reconstruct every executable/test file at that HEAD through the GitHub connector, plus merged LAB-075/074/073/072 dependencies, and verify Git blob identities. Execute LAB-076 protocol, real-integration, integration-audit and supported-audit suites; run the unsafe self-swap seed and confirm expected failure; run LAB-075/074/073/072 regressions and compileall. Then perform a fresh remote patch audit with special attention to historical-binding deletion/corruption, nested transaction/deadlock behavior of the new SQLite guards, restart reconstruction, and any path that could reinterpret historical authority as current publication authority. If clean, update Issue #143, mark PR #144 ready, squash-merge normally, close LAB-076 DONE, and choose the next highest-value unblocked correctness gap.

## Backlog

- #143 / LAB-076 — sink-registry authority lifecycle — IN_PROGRESS; draft PR #144.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
