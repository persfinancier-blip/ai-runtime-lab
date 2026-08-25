# Current Lab State

Last updated: 2026-08-25

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085.
- Active: Issue #163 / LAB-086 — IN_PROGRESS.
- Branch: `lab/086-asymmetric-break-glass-history`.
- Draft PR: #165 `[LAB-086] Asymmetric break-glass proof migration`.
- Current observed branch HEAD after this run: `1f10269617911bb5e24447b5285e3b5cdb6d1ea8`.
- PR remains draft/mergeable; full current-head real-ledger gate has not passed.

## Last completed step

Applied the previously tested migration-metadata ordinary-DML fence to the exact branch runtime through the normal GitHub Contents API.

The original branch `strict_fence.py` was reconstructed line-for-line in the execution runtime and verified with `git hash-object` as `1422f4435913cd95c37a38a0a62c2116f8e80476`. The durable patch `research/2026-08-25-lab086-migration-metadata-dml-fence.patch` was applied locally; the patched candidate compiled and hashed to the expected `7c8387f050bf44894ae02a0a9b90f3bfe09dc003`.

Published the full exact candidate to branch commit `1f10269617911bb5e24447b5285e3b5cdb6d1ea8`; the Contents API returned content blob exactly `7c8387f050bf44894ae02a0a9b90f3bfe09dc003`.

Reconstructed the exact published regressions by connector and verified their Git blobs:
- `test_strict_fence.py` `4b651db3638c8b9f2341d52b512f075c4b3c31d2`;
- `test_migration_metadata_dml_fence.py` `fb7680efffebc8abf17e1a203c0d523e500fa528`.

Executed both against the exact published runtime file: **13/13 PASS**. Compileall for the exact focused LAB-086 package passed. ResourceWarnings were unclosed in-memory SQLite test fixtures only; unittest returned rc=0 and all assertions passed.

## Evidence produced / reconfirmed

- Exact branch runtime `strict_fence.py`: `7c8387f050bf44894ae02a0a9b90f3bfe09dc003`.
- Contents API fix commit: `1f10269617911bb5e24447b5285e3b5cdb6d1ea8`.
- Exact focused branch gate: **13/13 PASS** (`test_strict_fence` 10 + migration metadata DML fence 3).
- Metadata matrix covers UPDATE/DELETE/`INSERT OR REPLACE`/UPSERT across boundary, legacy projection, and root-proof singletons; all blocked after complete cutoff.
- Initial migration order `projection -> boundary -> root proof` remains allowed.
- Final-writer thaw does not remove migration-metadata fences.
- Issue #163 evidence comment: `5409634376`.
- Lower-stack exact gate remains complete from prior observed runs: LAB-080 18/18, LAB-082 28/28, LAB-083 24/24, LAB-084 17/17, LAB-085 core 12/12, LAB-085 asymmetric-custody 8/8, LAB-085 public/final 11/11.
- Current branch/main compare after the fix: diverged, ahead 114 / behind 61; all 42 PR paths remain additions, so no path-level overlap with current `main` was observed.
- Direct shell GitHub transport is still unavailable; connector and Contents API remain functional safe fallbacks.

## Known blockers / constraints

- Full current-head real-ledger migration/suffix/final-supported suite, unsafe legacy-promotion seed, complete compileall, and final security audit remain mandatory before merge.
- Focused strict-fence evidence is now branch-exact but is not a substitute for real LAB-085-backed migration/suffix execution.
- LAB-086 SQLite fences cover audited ordinary DML/stale supported paths, not arbitrary same-privilege SQLite schema/DDL authority. LAB-087/#166 owns that stronger boundary.
- LAB-083/LAB-084 signer-noise robustness remains LAB-088/#167 and is fail-closed availability work unless downstream current-head tests show otherwise.
- Logical SQL scrubbing is not forensic erasure; whole-store rollback freshness remains delegated to the external monotonic-anchor layer.

## Exact next action

1. Reconstruct current PR HEAD `migration_guard.py`, `suffix.py`, `final_supported.py` and the real-ledger LAB-086 tests into a connector-sourced workspace using the already proven LAB-080→085 implementation closure; verify every executable/test file by Git blob identity.
2. Execute the complete current-head real-schema migration/suffix/final-supported regressions, including migration v4 root coauthorization/restart, scrubbed-prefix/asymmetric-suffix, orphan/partial state, full lower/public-history guards, public-rotation cross-binding, inherited/direct surfaces, final verification snapshot, and rotation races.
3. Execute unsafe legacy-promotion seed and full compileall across the reconstructed closure.
4. Perform a fresh full security audit of every consequential/restart mutation path and re-check branch/main divergence. Fix every failure; only then mark PR #165 ready and integrate.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; migration-metadata DML blocker is now applied and branch-exact 13/13 focused gate is clean; full real-ledger gate remains.
- #166 / LAB-087 — READY; SQLite schema-control trust boundary.
- #167 / LAB-088 — READY; threshold signer-noise robustness.
- #168 / LAB-089 — CLOSED `not_planned`.
- PostgreSQL-specific validation and open-model serving remain deferred until representative runtime/hardware is available.
