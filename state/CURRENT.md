# Current Lab State

Last updated: 2026-08-24

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085.
- Active: Issue #163 / LAB-086 — IN_PROGRESS.
- Branch: `lab/086-asymmetric-break-glass-history`.
- Draft PR: #165 `[LAB-086] Asymmetric break-glass proof migration`.
- Current observed PR HEAD: `96c436f4571dc5149cf127b23334245fd18a1f59`.
- PR remains draft; full current-head merged-stack regression gate has not passed.

## Last completed step

The current PR-head was re-audited after the stale-trigger upgrade fix. The final migration boundary now treats SQLite trigger definitions as executable policy: `_ensure_schema_locked()` drops and recreates every LAB-086-owned trigger under the caller's `BEGIN IMMEDIATE`. The public-recovery underlying suffix remains mutation-first, but after cutoff its first authority/transition/head mutation is SQL-fenced unless the exact current-root proof was already persisted by the final proof-first surface.

This run reconstructed exact current-branch `protocol.py`, `migration_guard.py`, `test_protocol.py`, and `test_stale_trigger_upgrade_regression.py` through the GitHub connector and verified their Git blob identities locally. The standalone protocol suite and the exact stale-trigger regression were actually executed. No new fail-open was found in the fresh migration-guard/suffix/final-surface audit.

## Evidence produced

- Exact `protocol.py` Git blob: `cccb531fa13b8f8d4e3a7c3163dd7c7cbeb3ec41`; local `git hash-object` matched.
- Exact `test_protocol.py` Git blob: `b423cf2d78bc75686b0e4e7dea5ea310ca5721ea`; local `git hash-object` matched.
- Current exact standalone LAB-086 suite: **12/12 passed**.
- Exact unsafe legacy-promotion seed still **fails as expected** because the unsafe baseline auto-promotes a legacy HMAC proof.
- Exact `migration_guard.py` Git blob: `dd95f2604b9986002578592b91fb8e255f359b0a`; local `git hash-object` matched.
- Exact stale-trigger regression Git blob: `e136dd636e4d9c0483595f3f4051c1c07080c5ea`; local `git hash-object` matched.
- Exact stale-trigger upgrade regression: **1/1 passed**. For this focused test only, unrelated imported dependency classes were import-only stubs; the executed migration-guard file and regression file themselves were exact published bytes, and the exercised `_ensure_schema_locked()` path does not call those stubs.
- Focused compileall over the reconstructed exact protocol/migration-guard/regression files passed.
- Fresh branch/main comparison: `diverged`, ahead 50 / behind 13. All 17 PR paths are additions; there is still no path overlap with `main`.
- Direct shell GitHub transport remains unavailable; the GitHub connector is healthy and was used as the auditable source path.

## Known blockers / constraints

- Stale public-writer/direct-suffix fence bypasses remain fixed in the candidate.
- Stale same-name trigger upgrade bypass is now exact-regression-tested and fixed.
- Remaining merge gate: the exact current-head real-schema LAB-086 integration tests and merged LAB-085/084/083/082/080 regressions still must be executed together after the trigger-upgrade fix.
- The focused exact trigger test uses import-only dependency stubs and therefore is not a substitute for the real cross-layer stack.
- Logical SQLite scrubbing is not forensic erasure; WAL/filesystem remnants remain outside the claim.
- Whole-store rollback freshness remains delegated to the external monotonic-anchor layer. No live HSM/KMS is claimed.

## Exact next action

1. Continue reconstructing the exact merged dependency closure through the GitHub connector, replacing the focused import stubs with the real LAB-085/084/083/082/080 modules.
2. Execute all current-head real-schema LAB-086 tests: migration guard, public-history boundary, scrubbed legacy prefix, suffix, stale LAB-085 writer, direct-suffix bypass, stale-trigger upgrade, plus the already-clean protocol suite and unsafe seed.
3. Execute merged LAB-085/084/083/082/080 regressions against that same source tree and compileall.
4. Fix every failure and repeat until clean.
5. Perform a final complete PR audit focused on alternate mutation entry points, trigger upgrade/replacement, proof-first ordering, fake/orphan proofs, predecessor/root binding, restart and rotation races.
6. Re-check divergence. Integrate only after the clean gate; prefer normal ready/squash merge and use the AGENTS.md conflict-checked Contents API fallback only if the normal merge path is unavailable and the audited file-scoped change remains conflict-independent.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; current candidate has exact standalone + exact stale-trigger evidence, but the real merged-stack gate remains.
- PostgreSQL-specific validation and open-model serving remain deferred until representative runtime/hardware is available.
