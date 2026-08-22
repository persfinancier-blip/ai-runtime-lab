# Current Lab State

Last updated: 2026-08-22

## Active objective

LAB-075 — remove the remaining trusted `sink_id -> runtime adapter/endpoint` mapping behind LAB-074 by binding each new broker reservation to an authenticated/versioned registry entry and enforcing safe rotation/reconciliation semantics.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-074.
- Active: Issue #141 / LAB-075 — IN_PROGRESS.
- Active branch: `lab/075-sink-registry-binding-v2`.
- Active draft PR: #142; latest branch commit observed after this run's fix/regression is `4e56aad9ade8f8bbf1e9757a92e3d1b675d01c9e`.

## Last completed step

The historical-UNKNOWN fail-open found in the prior audit was fixed. `CorrectedRegistryBrokerWorker.process()` now authorizes reconciliation only when `reconcile_by_key is True`; dict/legacy claims with the field omitted no longer receive authority by default. A dedicated regression, `test_unknown_missing_reconcile_capability_fails_closed`, was added. The fix and regression were committed to the active branch as `63aba8d27a7c712accbfcc7e8eff281c4c93bf20` and `4e56aad9ade8f8bbf1e9757a92e3d1b675d01c9e`.

Direct `git clone` was re-probed in this run and still fails DNS resolution for github.com. The GitHub connector remains functional. PR #142 remains draft; no exact-source full-suite execution is claimed for the new HEAD.

## Evidence produced

- Re-read `AGENTS.md`, this state, `prompts/SELF_RESUME.md`, PR #142, and the exact supported audit-fix/test paths before editing.
- Confirmed the fail-open expression was `claim.get("reconcile_by_key", True)` and changed it to a missing-value-denies lookup.
- Added a regression that creates a real historical UNKNOWN, rotates to a direct successor, supplies a dict capability with no `reconcile_by_key`, requires `HistoricalExecutionBlocked`, and proves the sink effect count remains one.
- Branch commits: fix `63aba8d27a7c712accbfcc7e8eff281c4c93bf20`; regression `4e56aad9ade8f8bbf1e9757a92e3d1b675d01c9e`.
- Issue #141 comment records the fix, regression, and remaining validation gate.
- Direct shell clone probe failed with `Could not resolve host: github.com`; no test execution is claimed in this run.
- Prior evidence remains: interface-compatible matrix 14/14, audit-fix + inherited matrix 30/30, unsafe string-only baseline failed as expected. These are not exact-source evidence for the corrected HEAD.

## Known blockers / constraints

- No owner/product blocker.
- The known reconciliation-authority code blocker is fixed, but validation is incomplete for the new published HEAD.
- Direct GitHub clone is unavailable in this runtime due DNS; connector reconstruction is the supported fallback.
- Do not mark LAB-075 DONE until exact published-source execution and final remote patch audit are clean.
- LAB-075 must reuse LAB-022–025 transport/destination enforcement; adapter digest is a reference profile identity, not a claim that Python object identity is production code identity.

## Exact next action

Reconstruct the exact executable bytes of PR #142 HEAD through the GitHub connector, verify Git blob identities locally, and execute LAB-075 supported/audit-fix + real integration tests, LAB-074/LAB-073/LAB-072 regressions, unsafe baseline, and compileall. Perform a fresh remote patch audit of all changed executable paths. If all gates are clean and PR HEAD is unchanged after validation, mark #142 ready, squash-merge it, close Issue #141 DONE, and select the next highest-value unblocked correctness gap.

## Backlog

- #141 / LAB-075 — authenticated sink-adapter and endpoint registry binding — IN_PROGRESS.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
