# Current Lab State

Last updated: 2026-08-23

## Active objective

LAB-086 — migrate historical break-glass verification from durable symmetric/HMAC material to an explicit authenticated legacy cutoff plus Ed25519 public-only proof history, without auto-promoting legacy rows or weakening LAB-084/LAB-085 authority semantics.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085.
- Active: Issue #163 / LAB-086 — IN_PROGRESS.
- Active branch: `lab/086-asymmetric-break-glass-history`.
- Active draft PR: #165 `[LAB-086] Asymmetric break-glass proof migration`.
- Current PR #165 HEAD after this run: `5187375f67de134d22ac559eb4831d11e1b53bc7` at last observation; re-fetch before any test/merge gate because the branch may move after this handoff.
- PR #165 is open, mergeable and intentionally draft.

## Last completed step

This run resumed the exact-source gate and reconstructed the exact standalone LAB-086 `protocol.py`, `test_protocol.py`, and unsafe seed. Their local `git hash-object` values matched the published branch blobs (`cccb531fa13b8f8d4e3a7c3163dd7c7cbeb3ec41`, `b423cf2d78bc75686b0e4e7dea5ea310ca5721ea`, `d92640ba77f7b1b592faf00f7afcea03cf3fbc4a`). The standalone corrected suite passed 12/12, the unsafe auto-promotion seed failed as expected, and compileall passed.

A fresh cross-layer authority audit then found another real fail-open in the real-schema boundary. `migration_guard.verify_locked()` checked public/symmetric historical binding but did not re-run the cryptographic Ed25519 recovery-custody transition verifier. A live DB mutation of an older `provider_recovery_public_transitions` signature set could therefore leave structural binding intact and allow a new migration cutoff to be prepared before a later full restart audit noticed the broken public trust chain.

The branch now fixes this by making `verify_locked()` re-run `public_recovery_custody.verify_durable()` while the caller's outer `BEGIN IMMEDIATE` holds the writer-excluding boundary. A new exact real-schema regression, `test_cutoff_payload_rejects_corrupted_public_custody_rotation_history`, rotates the recovery/public authority, corrupts the persisted old public signatures, and requires cutoff preparation to fail.

## Evidence produced

- Exact standalone LAB-086 gate executed in this run: 12/12 corrected tests passed.
- Unsafe legacy auto-promotion seed failed as expected (`UnsafeLegacyAutoPromotion().promote(...)` returned true, so the negative assertion failed).
- Standalone LAB-086 compileall passed.
- Exact local Git blob matches:
  - `protocol.py` -> `cccb531fa13b8f8d4e3a7c3163dd7c7cbeb3ec41`;
  - `test_protocol.py` -> `b423cf2d78bc75686b0e4e7dea5ea310ca5721ea`;
  - unsafe seed -> `d92640ba77f7b1b592faf00f7afcea03cf3fbc4a`.
- New public-history authority fix commit: `9593d05706fd17d9ceba6c1d0602fc87c8dced60`; published `migration_guard.py` blob after fix: `7286667eb25c42184fec4d11ee69236944b38a75`.
- New regression commit / observed PR HEAD: `5187375f67de134d22ac559eb4831d11e1b53bc7`.
- Fresh remote patch audit of the new fix and regression found no additional blocker in those two changed files.
- Direct shell GitHub access was probed in this run and still fails before checkout with `Could not resolve host: github.com`; GitHub connector remains healthy. This is a runtime capability constraint, not an owner blocker.

## Known blockers / constraints

- The new public-history fix changed the PR head after the 12/12 standalone exact-source run; that run remains valid only for the unchanged standalone files, not for the current real-schema migration/suffix gate.
- The current PR head has not yet passed the complete exact-source migration-guard + suffix + LAB-085/084/083/082/080 regression stack after the new fix.
- The new public-history regression has been published but has not yet been executed against the exact reconstructed merged dependency stack.
- Direct shell GitHub networking is unavailable; exact reconstruction must continue through the GitHub connector unless network capability changes.
- PR #165 remains draft until exact-source regressions, unsafe seed, compileall and a fresh final full patch audit are actually observed.
- Whole-store rollback freshness remains delegated to the external monotonic-anchor layer.
- No live HSM/KMS was exercised; Ed25519 signer objects remain a reference interface.

## Exact next action

1. Re-fetch PR #165 and require a stable current HEAD; if it moved, restart the gate from that HEAD.
2. Continue connector reconstruction of the exact merged dependency stack, beginning with LAB-085 `provider_recovery_authority_lifecycle`, LAB-084 `provider_rotation_recovery`, LAB-083 `provider_threshold_rotation`, LAB-082 `asymmetric_provider_history`, and LAB-080 `shared_anchor_intent_ledger`; verify every executable/test file with `git hash-object`.
3. Execute exact-source:
   - LAB-086 standalone reference tests (12/12 already observed for unchanged blobs; re-run if those blobs move);
   - LAB-086 migration-guard tests including stale historical recovery cutoff rejection and the new corrupted-public-history regression;
   - LAB-086 asymmetric suffix tests;
   - LAB-085, LAB-084, LAB-083, LAB-082 and LAB-080 regression suites;
   - unsafe legacy auto-promotion seed;
   - compileall for the affected experiment tree.
4. Fix any failure and repeat.
5. Perform a fresh full remote patch audit. Only after a clean gate mark PR #165 ready, merge it, close Issue #163 DONE and choose the next highest-value unblocked correctness bottleneck.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; stale-cutoff bypass and public-custody-history fail-open fixed, current-head exact real-schema regression/audit gate remains.
- PostgreSQL-specific validation and open-model serving remain deferred until representative runtime/hardware is available.
