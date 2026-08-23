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
- PR remains draft; full current-head regression/audit gate has not passed.

## Last completed step

A fresh upgrade-path audit found a durable fence bypass in the current candidate: LAB-086 used `CREATE TRIGGER IF NOT EXISTS`, so an older/weaker same-name security trigger already stored in SQLite survived code upgrade unchanged. A deterministic pre-fix SQLite reproduction installed a weak `lab086_public_head_requires_root_proof` with `WHEN 0`; the former installer retained it and an unproved public recovery head change succeeded.

The branch now treats trigger definitions as executable policy. `AuthenticatedBreakGlassMigrationGuard._ensure_schema_locked()` runs under the caller's `BEGIN IMMEDIATE`, drops every LAB-086-owned migration/public-fence trigger name, then recreates the exact current definitions before writers can proceed. An executable repository regression was added for the stale-trigger upgrade case.

## Evidence produced

- Regression file commit: `2957e6d066d7870c9d4177056ea7ec2dc7ec2bab`.
- Trigger replacement implementation commit: `f74095980759c08810be09061138018c8e8ba2a4`.
- Published `migration_guard.py` Git blob: `dd95f2604b9986002578592b91fb8e255f359b0a`.
- Research note commit / current observed PR HEAD: `96c436f4571dc5149cf127b23334245fd18a1f59`.
- Actually executed pre-fix SQLite probe: same-name weak trigger remained installed and an unproved head update succeeded.
- Actually executed post-fix focused SQLite probe using the updated trigger predicates: weak `WHEN 0` definition was absent, unproved head update raised `IntegrityError`, authoritative head remained `old`.
- Earlier LAB-086 standalone reference evidence remains 12/12 plus expected unsafe legacy-auto-promotion failure, but is not current-head full-stack evidence.
- Current branch/main comparison after this run: diverged, ahead 50 / behind 12; all 17 PR paths are additions and do not overlap `main` paths.
- Direct GitHub shell transport was probed in this run and failed with `Could not resolve host: github.com`; GitHub connector remained healthy.

## Known blockers / constraints

- Stale public-writer/direct-suffix fence bypasses are fixed in the candidate.
- Stale same-name trigger upgrade bypass is fixed in the candidate.
- Remaining merge gate: exact current-head LAB-086 + LAB-085/084/083/082/080 regression stack has not yet been executed after the trigger-upgrade fix.
- The focused SQLite probe proves the schema-upgrade/fence predicates, not the whole cross-layer stack.
- Logical SQLite scrubbing is not forensic erasure; WAL/filesystem remnants remain outside the claim.
- Whole-store rollback freshness remains delegated to the external monotonic-anchor layer. No live HSM/KMS is claimed.

## Exact next action

1. Reconstruct the exact current PR #165 executable dependency closure through the GitHub connector, including `migration_guard.py` blob `dd95f260...` and `test_stale_trigger_upgrade_regression.py`.
2. Execute all current-head LAB-086 tests: protocol, migration guard, public-history boundary, scrubbed legacy prefix, suffix, stale LAB-085 writer, direct-suffix bypass, stale-trigger upgrade, unsafe legacy-promotion seed, plus compileall.
3. Execute merged LAB-085/084/083/082/080 regressions against the same source tree.
4. Fix every failure and repeat until clean.
5. Perform a fresh complete PR audit focused on alternate mutation entry points, trigger upgrade/replacement, proof-first ordering, fake/orphan proofs, predecessor/root binding, restart and rotation races.
6. Re-check branch/main divergence. Integrate only after the clean gate; prefer normal ready/squash merge and use the AGENTS.md conflict-checked Contents API fallback only if the normal merge path is unavailable and the audited file-scoped change remains conflict-independent.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; current candidate has an additional upgrade-path hardening fix, full exact-source gate remains.
- PostgreSQL-specific validation and open-model serving remain deferred until representative runtime/hardware is available.
