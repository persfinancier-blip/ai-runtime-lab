# Current Lab State

Last updated: 2026-08-23

## Active objective

LAB-086 — migrate historical break-glass verification from durable symmetric/HMAC material to an explicit authenticated legacy cutoff plus Ed25519 public-only proof history, without auto-promoting legacy rows or weakening LAB-084/LAB-085 authority semantics.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085.
- Active: Issue #163 / LAB-086 — IN_PROGRESS.
- Active branch: `lab/086-asymmetric-break-glass-history`.
- Active draft PR: #165 `[LAB-086] Asymmetric break-glass proof migration`.
- Current PR #165 HEAD: `9e1169eb1a00f7dafbdbd4558959e8b0983ae230`.
- PR #165 is open, mergeable and intentionally draft.

## Last completed step

LAB-086 moved beyond the standalone reference store and published the first integration slice against the real LAB-084/LAB-085 SQLite authority.

`experiments/asymmetric_break_glass_history/migration_guard.py` now derives the legacy-prefix commitment from the actual `provider_rotation_recovery_transitions` plus corresponding `provider_rotation_recovery_custody_proofs` rows. The cutoff is signed by the exact historically-bound current LAB-085 Ed25519 recovery authority; no caller-supplied legacy digest is trusted.

The migration guard uses one outer `BEGIN IMMEDIATE` writer-excluding interval while it re-runs the inherited LAB-085 recovery lifecycle verifier, public-custody verifier, custody bindings and break-glass custody checks, then authenticates the cutoff. A persistent SQLite trigger blocks insertion into `provider_rotation_recovery_transitions` once the authenticated cutoff exists, so even an old LAB-085 worker cannot append a new HMAC break-glass row after migration.

New real-schema regressions were published in `tests/test_migration_guard.py` for valid legacy migration/restart, insufficient threshold, legacy-history tamper, old-writer SQL blocking and the pre-cutoff compatibility path.

## Audit findings corrected this run

1. A Python pre-check followed by inherited HMAC recovery would have created migration-vs-recovery TOCTOU. The cutoff is now also enforced in SQL.
2. The first published guard called LAB-085 `verify_durable()` while holding `BEGIN IMMEDIATE`, which could self-lock on a nested write transaction. It was replaced with inherited internal verification under the existing writer fence.
3. The first correction did not re-run the complete public-custody transition verifier. The current code follows the LAB-085 final-verifier pattern: lifecycle verification + public-custody verification + exact cross-binding under one outer writer-excluding interval.
4. The designed asymmetric suffix must enforce historical LAB-085 recovery-generation activation windows, so a valid old Ed25519 key cannot authorize a new break-glass edge after recovery-authority rotation.

## Evidence produced

- Existing standalone LAB-086 reference evidence remains: corrected 12/12, unsafe auto-promotion seed failed as expected, compileall passed.
- New real-schema files published on PR #165:
  - `experiments/asymmetric_break_glass_history/migration_guard.py` — current blob `17c19859f06d8b9bbea21e93b783fbfd0f784baa`.
  - `experiments/asymmetric_break_glass_history/tests/test_migration_guard.py`.
- Integration commits this run include `672abbb69cb12267ad17f7a8e9c9588d940e351c`, `f9c35fef1501e4f162f05ae536dcf470a1553a20`, `da99a6389b917a26d9568892bc4687aebdb08ee2`, and current HEAD `9e1169eb1a00f7dafbdbd4558959e8b0983ae230`.
- PR #165 patch was re-inspected after the integration changes; no merge is claimed.

## Known blockers / constraints

- The new real-schema migration guard and its regressions are published but have **not** yet been executed as exact current PR-head source in this runtime. Do not reuse the earlier standalone 12/12 as evidence for these new bytes.
- Direct shell GitHub networking still fails DNS resolution for `github.com`; GitHub connector operations are healthy. This is a capability constraint, not an owner blocker.
- The real-schema asymmetric suffix is not published yet. Current work establishes and fences the migration boundary only.
- New asymmetric recovery must update the existing `provider_rotation_authorities` / `provider_rotation_authority_head` and persist public proof rows in the same transaction; it must not create another root/recovery authority store.
- Historical public recovery authorities may verify old proof rows only within their actual LAB-085 activation window; stale generations must not authorize new recovery.
- Whole-store rollback freshness remains delegated to the external monotonic-anchor layer.
- No live HSM/KMS was exercised; Ed25519 signer objects remain a reference interface.

## Exact next action

Continue Issue #163 / PR #165 by implementing the asymmetric suffix directly on the existing LAB-084/LAB-085 authority tables. Add a content-bound Ed25519 proof row for each post-cutoff break-glass successor, verify the current public recovery generation before commit, enforce the historical recovery-generation activation/deactivation window during restart, count exactly one proof type per root-history edge, and update the existing root head in the same `BEGIN IMMEDIATE` transaction. Keep the SQL trigger blocking all new HMAC recovery rows after cutoff.

Then reconstruct exact PR-head bytes through the GitHub connector and execute: LAB-086 standalone + migration guard + asymmetric suffix tests, LAB-085/084/083/082/080 regressions, unsafe legacy-promotion seed and compileall. Perform a fresh full remote patch audit before marking PR #165 ready or merging.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; real authenticated cutoff integrated, asymmetric real-schema suffix next.
- PostgreSQL-specific validation and open-model serving remain deferred until representative runtime/hardware is available.
