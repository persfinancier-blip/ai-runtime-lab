# Current Lab State

Last updated: 2026-08-24

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085.
- Active: Issue #163 / LAB-086 — IN_PROGRESS.
- Branch: `lab/086-asymmetric-break-glass-history`.
- Draft PR: #165 `[LAB-086] Asymmetric break-glass proof migration`.
- Current observed PR HEAD: `4b78693910658156bfacd7460e5d6cb1edf61500`.
- PR is open/draft/mergeable; full current-head merged-stack exact-source regression gate has not passed.

## Last completed step

A fresh cross-layer audit found and fixed a mixed-SQL-snapshot regression in the final LAB-086 supported verifier. The previous `SupportedFencedAsymmetricBreakGlassLedger.verify_durable()` completed `ledger.verify_durable()` first, released that write-excluding verification interval, and only then opened a second `BEGIN IMMEDIATE` for LAB-086 boundary/fence checks. Lower durable state could therefore change after being verified but before the final surface returned success. This regressed the single-serialization-boundary pattern already established in LAB-085.

The final verifier now opens one `BEGIN IMMEDIATE` first, installs/asserts the public mutation fence, runs `SupportedAsymmetricHistoricalSharedAnchorLedger.verify_durable(ledger)` while that write guard is held, re-verifies public recovery history, runs `_verify_lab086_locked(q)` in the same guarded interval, reasserts the fence, then commits. A focused regression verifies both that the old split public `ledger.verify_durable()` path is not called and that a second SQLite writer cannot acquire `BEGIN IMMEDIATE` during either lower or LAB-086 verification.

## Evidence produced / reconfirmed

- New PR HEAD: `4b78693910658156bfacd7460e5d6cb1edf61500`.
- Exact published `final_supported.py` Git blob: `fa0dd30bf1b34b7e140c3244807e30bedf84ea28`; locally reconstructed bytes matched exactly.
- Exact published `test_final_verification_snapshot.py` Git blob: `0426dcfe61bef665bcbc5c21b937d805f223da64`; locally reconstructed bytes matched exactly.
- Focused final-verification serialization regression: 1/1 PASS.
- The focused test observed `database is locked` for a competing `BEGIN IMMEDIATE` during both lower verification and LAB-086 locked verification.
- A separate old-algorithm harness confirmed the previous final flow called a lower public verifier before acquiring the final transaction, demonstrating the split-verification structure being removed.
- Exact current-head standalone LAB-086 protocol suite from the previous pass remains 12/12 PASS; unsafe legacy-auto-promotion seed failed as expected. These unchanged results do not substitute for the new full current-head gate.
- `migration_guard.py` remains blob `332995323d8d74fcc0f377d0e74bb0f30b8735c1`; `strict_fence.py` remains blob `eb9f3d60f9bda56de9d71aa3aa406a7d6a99ae78`.
- Fresh branch/main compare after the fix: ahead 74 / behind 25; all 23 PR paths are additions with no path overlap against main.
- Direct shell GitHub DNS remains unavailable; GitHub connector is healthy and remains the supported durable source/control-plane path.

## Known blockers / constraints

- Remaining LAB-086 merge gate: exact current-head real-schema LAB-086 tests plus LAB-085/084/083/082/080 regressions still need to be executed together from one connector-reconstructed exact dependency closure after the v4 cutoff/root-coauthorization and the new final-verification snapshot fix.
- The new 1/1 focused result and prior 12/12 standalone result are real evidence but are not substitutes for the combined gate.
- File-by-file exact reconstruction is slower because shell GitHub transport is unavailable; this is a runtime limitation, not an owner blocker.
- LAB-086 SQL fences protect against stale/alternate supported mutation paths, not arbitrary same-privilege raw SQLite DDL. That broader trust boundary is LAB-087 / #166.
- Logical SQL scrubbing is not forensic erasure; WAL/filesystem remnants remain outside the claim.
- Whole-store rollback freshness remains delegated to the external monotonic-anchor layer. No live HSM/KMS is claimed.

## Exact next action

1. Continue connector reconstruction of the exact PR HEAD dependency closure. Verify every reconstructed executable file with local `git hash-object` against the GitHub blob before counting any test.
2. Execute all current LAB-086 real-schema tests, now including `test_final_verification_snapshot.py`, migration v4/root coauthorization, scrubbed-prefix/asymmetric-suffix, public-history boundary, forged/stale/direct-surface fences, strict-fence conflict algorithms, trigger upgrade and final-supported rotation.
3. Execute exact LAB-085/084/083/082/080 regressions from the same closure, then unsafe seed and `python -m compileall`.
4. Perform a fresh full audit focused on final single-snapshot verification, cutoff/root/public proof substitution, alternate supported mutation entry points, transaction-scoped fence removal/restoration, predecessor/root binding, restart snapshots and rotation races.
5. Re-check PR/head and branch/main divergence. Keep PR #165 draft until the full gate is clean; only then mark ready and prefer normal squash merge. Use file-scoped Contents API fallback only after a fresh conflict/path audit if normal merge is unavailable and no safety gate is bypassed.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; new final mixed-snapshot verifier defect fixed with exact focused 1/1 evidence; full merged-stack gate remains.
- #166 / LAB-087 — READY; establish/enforce the SQLite schema-control trust boundary behind post-cutoff authority fences.
- PostgreSQL-specific validation and open-model serving remain deferred until representative runtime/hardware is available.
