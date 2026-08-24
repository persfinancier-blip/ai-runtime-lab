# Current Lab State

Last updated: 2026-08-24

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085.
- Active: Issue #163 / LAB-086 — IN_PROGRESS.
- Branch: `lab/086-asymmetric-break-glass-history`.
- Draft PR: #165 `[LAB-086] Asymmetric break-glass proof migration`.
- Current observed PR HEAD: `465d4d398d89398281714a7cdf6476d949328bb6`.
- PR is mergeable but remains draft; full current-head merged-stack exact-source regression gate has not passed.

## Last completed step

A fresh current-head cross-layer audit found and fixed another pre-commit integrity gap. Final consequential writers re-verified LAB-080/LAB-082 committed history and LAB-086 root/public-window semantics, but they did not re-run LAB-085 `AsymmetricRecoveryCustody.verify_durable()` before mutation. A stored `provider_recovery_public_transitions` Ed25519 old/new signature set could therefore be corrupted while its separate LAB-086 root-coauthorization row remained valid; a new root/provider/public-recovery/asymmetric-recovery successor could commit and only a later restart would detect the damaged public-custody history.

The common final-writer pre-verification helper now verifies both the lower LAB-080/082 history and `ledger.public_recovery_custody.verify_durable()` while the outer `BEGIN IMMEDIATE` owns the writer slot. All four consequential final-writer paths inherit the stronger check, and final `verify_durable()` uses the same composition.

Published commits:
- code fix `78489c8789911565aaa1f18d3583d728142edc62`;
- real-schema regression `6991c910ff39ae23d3191dd0fcbda54b9d3fd333`;
- research note / current HEAD `465d4d398d89398281714a7cdf6476d949328bb6`.

The new regression performs a valid post-cutoff public-recovery rotation, corrupts only `provider_recovery_public_transitions.old_signatures_json`, then requires a valid normal-root rotation to fail with root head/authority/transition counts unchanged. The exact helper body was executed in a focused instrumented harness and confirmed that both lower and public-custody verifiers are invoked. That focused execution is not a substitute for the outstanding full real-schema gate.

## Evidence produced / reconfirmed

- Current branch `final_supported.py` blob: `9f0198d2db85d08ec64f614d6288323c1d642383`.
- New `test_public_custody_history_guard.py` blob: `d18fec7d4a22195165a2b06c171cd9ff4269d6e7`.
- Focused helper execution: PASS; lower committed-history verifier and public-custody verifier were both invoked.
- Fresh source audit confirmed `AsymmetricRecoveryCustody.verify_durable()` is the layer that re-verifies persisted Ed25519 old/new transition signatures and orphan transition count; LAB-086 public-window/root-proof verification is distinct and insufficient alone.
- Previous root-head INSERT/REPLACE/DELETE fence fix remains on the branch; focused semantics blocked all three mutation paths and allowed only transaction-scoped final-writer mutation.
- Cumulative exact lower-stack evidence remains: LAB-080 18/18 PASS, LAB-082 28/28 PASS, LAB-083 24/24 PASS, LAB-084 17/17 PASS, LAB-085 core 12/12 PASS, LAB-085 asymmetric-custody 8/8 PASS; lower unsafe baselines failed as expected.
- Exact standalone LAB-086 corrected suite previously passed 12/12; unsafe legacy-auto-promotion seed failed as intended.
- Fresh branch/main compare after the new regression: branch diverged, all LAB-086 paths remain additions with no path-level overlap against current `main`.

## Known blockers / constraints

- Full LAB-086 merge gate remains incomplete after the new public-custody history fix: exact LAB-085 final/public-custody tests and all current-head LAB-086 real-schema tests must be executed together, followed by unsafe seed, compileall and final audit.
- The focused helper run validates the new control-flow guard but is not exact full-module/current-stack evidence; the new real-schema regression has not yet been executed.
- LAB-083/LAB-084 signer-noise issue #167 remains fail-closed DoS/robustness and separate from LAB-086 unless downstream tests invalidate the candidate.
- LAB-089 / #168 remains a verification question; do not add ordering protocol complexity unless real supported-writer tests reproduce it.
- LAB-086 SQLite fences cover stale/alternate supported mutation paths and the audited DML boundary, not arbitrary same-privilege raw SQLite DDL/schema control. That broader trust boundary is LAB-087 / #166.
- Logical SQL scrubbing is not forensic erasure; WAL/filesystem remnants remain outside the claim. Whole-store rollback freshness remains delegated to the external monotonic-anchor layer.
- Direct shell GitHub transport in this runtime is unavailable (`Could not resolve host: github.com`); connector reconstruction remains the supported fallback and is not an owner blocker.

## Exact next action

1. Reconstruct/execute the remaining exact LAB-085 `test_public_custody_supported.py`, `test_final_supported.py` and direct dependencies in one connector-sourced workspace; verify executable files by Git blob identity.
2. Re-fetch PR #165 HEAD (do not assume `465d4d3...` remains current), reconstruct current LAB-086 implementation/tests and execute the complete real-schema suite, explicitly including `test_public_custody_history_guard.py`, root-head REPLACE/DELETE, inherited lower-writer fences, migration v4 root coauthorization/restart, scrubbed-prefix/asymmetric-suffix, forged-proof/stale-writer/direct-surface, strict conflict algorithms, final verification snapshot, public-rotation history guard and rotation races.
3. Execute a real supported-writer check for #168; close #168 as invalid if both valid serial orders restart cleanly.
4. Run unsafe legacy-promotion seed and full compileall over the reconstructed closure.
5. Perform a fresh full security audit of every consequential/restart mutation path and branch/main divergence. Keep PR #165 draft until all current-head tests are clean; only then mark ready and integrate.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; public-custody Ed25519 history pre-commit guard added; full current-head gate remains.
- #166 / LAB-087 — READY; SQLite schema-control trust boundary.
- #167 / LAB-088 — READY; signer-noise robustness in LAB-083/LAB-084 threshold collectors.
- #168 / LAB-089 — VERIFY premise against real supported-writer serializations before implementation.
- PostgreSQL-specific validation and open-model serving remain deferred until representative runtime/hardware is available.
