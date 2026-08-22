# Current Lab State

Last updated: 2026-08-22

## Active objective

LAB-075 — remove the remaining trusted `sink_id -> runtime adapter/endpoint` mapping behind LAB-074 by binding each new broker reservation to an authenticated/versioned registry entry and enforcing safe rotation/reconciliation semantics.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-074.
- Active: Issue #141 / LAB-075 — IN_PROGRESS.
- Active branch: `lab/075-sink-registry-binding-v2`.
- Active draft PR: #142 at HEAD `181feb0c963731202af64419ba6d7e8aa1b57cb8`.

## Last completed step

LAB-075 now has an explicit audited supported surface (`experiments/sink_registry_binding/supported.py`) and a published real-integration suite importing the merged LAB-074/LAB-072 classes rather than only interface-compatible doubles.

A fresh audit found another split check/use bug in the first audit overlay: stored content-address registry-row validation occurred before `super().observe()` opened its write transaction. The corrected `observe()` now authenticates/rechecks the stored row, validates predecessor/head continuity, re-reads the authoritative row, and activates the new head inside one `BEGIN IMMEDIATE` transaction with a CAS-style head update. A regression proves a pre-existing row with a valid content digest but invalid signature cannot become head.

Normal draft PR creation now succeeds; PR #142 is intentionally left draft pending exact-source execution.

## Evidence produced

- Initial LAB-075 protocol + failure matrix remain on branch.
- `experiments/sink_registry_binding/audit_fixes.py` now contains atomic registry activation.
- `experiments/sink_registry_binding/supported.py` is the documented audited surface.
- `experiments/sink_registry_binding/tests/test_audit_fixes.py` includes corrupt-preexisting-row activation regression.
- `experiments/sink_registry_binding/tests/test_real_integration.py` imports real `TransactionalJournal`, `CapabilityBoundJournal`, `ProbeAuthority`, `Request`, and `IdempotentSink` from merged main.
- Prior local interface-compatible matrix: 14/14 passed.
- Prior audit-fix + inherited matrix: 30/30 passed.
- Unsafe string-only baseline: failed as expected because attacker adapter executed a side effect.
- Direct `git clone` probe in this run failed with DNS resolution for github.com; connector remains functional.
- `compare_commits(main, branch)` before PR creation: only nine new LAB-075 files; branch diverged because main has newer state commits, not overlapping LAB-075 code paths.

## Known blockers / constraints

- No owner/product blocker.
- Direct GitHub clone is unavailable in this runtime due DNS.
- PR #142 is draft because exact published HEAD execution has not yet been observed after the new atomic-activation fix and real-integration tests.
- Do not count prior interface-compatible test runs as exact-source evidence for current HEAD.
- LAB-075 must reuse LAB-022–025 transport/destination enforcement; adapter digest is a reference profile identity, not a claim that Python object identity is production code identity.

## Exact next action

Reconstruct exact executable bytes for PR #142 through the GitHub connector, including the current LAB-075 supported/audit/integration files and merged LAB-074/LAB-073/LAB-072 dependencies. Verify each reconstructed file with local `git hash-object` against the GitHub blob SHA, then run LAB-075 supported + real integration tests, LAB-074/LAB-073/LAB-072 regressions, unsafe baseline, and compileall. Perform a fresh remote patch audit after those results. If all gates are clean and PR HEAD is unchanged, mark #142 ready, squash-merge it, close Issue #141 DONE, and select the next highest-value unblocked correctness gap.

## Backlog

- #141 / LAB-075 — authenticated sink-adapter and endpoint registry binding — IN_PROGRESS.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
