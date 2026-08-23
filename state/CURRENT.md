# Current Lab State

Last updated: 2026-08-23

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085.
- Active: Issue #163 / LAB-086 — IN_PROGRESS.
- Branch: `lab/086-asymmetric-break-glass-history`.
- Draft PR: #165 `[LAB-086] Asymmetric break-glass proof migration`.
- Current observed PR HEAD: `ae67ec4f6afc79db746e8903077a8d9bea8542ac`.
- PR is currently mergeable but must remain draft until the full current-head regression/audit gate passes.

## Last completed step

The alternate directly usable `suffix.SupportedAsymmetricBreakGlassLedger` public-rotation bypass was fixed at the durable migration boundary rather than by disabling only one Python method. `AuthenticatedBreakGlassMigrationGuard._ensure_schema_locked()` now creates the exact public root-proof table and installs cutoff-conditional SQLite fences on public recovery authority/transition/head mutations. Before cutoff the triggers are dormant. After cutoff a mutation-first LAB-085 custody writer or direct LAB-086 suffix writer cannot commit a successor unless the exact predecessor/successor + current normal/root proof already exists.

The legitimate final path remains proof-first under one `BEGIN IMMEDIATE`: validate old/new public quorums + current root quorum, persist the exact root proof, mutate authority/transition/head, re-verify, commit. The existing suffix test that intentionally performs a successful public recovery rotation now routes that consequential operation through `final_supported.SupportedFencedAsymmetricBreakGlassLedger`. The direct-suffix regression was strengthened to require no change to head, authority count, transition count, or root-proof count on rejection.

## Evidence produced

- Exact pre-change branch `migration_guard.py` was reconstructed through the GitHub connector and matched Git blob `605f40490a431226164e7ab3966d8aa1a1d1dc8d` before modification.
- Migration-boundary fence commit: `031c8b7dc39d7ccfaae14052f11445e79028d5b7`; current `migration_guard.py` blob `611b79bc37a0bdf1fcb2eef2315d72d9a891038c`.
- Supported public-rotation test routing commit: `1f2fd4b22a0c265fb56e58fc315a94166ad09e3a`; `test_suffix.py` blob `04134a2a1bd9cce74d006b97c9ce701121930c92`.
- Strengthened direct-suffix regression commit: `0c1100a21f3847a464f9a22f365257a2f60c5993`; test blob `b0625ee6507ce7d7cf0d08579698f9a20feb05d2`.
- Research note updated in commit `ae67ec4f6afc79db746e8903077a8d9bea8542ac`.
- Actually executed focused SQLite evidence using the exact updated migration schema predicates:
  - mutation-first successor authority insert after cutoff raised `IntegrityError` and rollback preserved old state;
  - exact proof-first authority + transition + head committed successfully;
  - post-cutoff public authority/transition UPDATE attempts were rejected.
- Earlier standalone LAB-086 reference evidence remains 12/12 plus expected unsafe legacy-auto-promotion failure, but is not claimed as current-head full-stack evidence.
- Current branch/main comparison: diverged, ahead 46 / behind 11; all 15 LAB-086 paths are additions and do not overlap `main` paths.
- Shell/direct GitHub transport remains unavailable in this runtime; the GitHub connector is healthy and was used for exact source/control-plane work.

## Known blockers / constraints

- The alternate-surface design blocker is fixed in the current candidate.
- Remaining merge gate: full current-head exact-source LAB-086 + LAB-085/084/083/082/080 regression stack has not yet been executed after these latest changes.
- Focused SQLite execution proves the fence ordering/predicates, not all cross-layer behavior.
- Logical SQLite-state scrubbing is not forensic erasure; WAL/filesystem remnants remain outside the claim.
- Whole-store rollback freshness remains delegated to the external monotonic-anchor layer. No live HSM/KMS is claimed.

## Exact next action

1. Reconstruct exact current-head executable bytes for PR #165 through the GitHub connector, including the latest `migration_guard.py`, `test_suffix.py`, direct-suffix regression and their LAB-086 dependencies.
2. Execute all LAB-086 tests: protocol, migration guard, public-history boundary, scrubbed legacy prefix, suffix, stale LAB-085 writer, direct-suffix bypass, and unsafe legacy-promotion seed; run compileall.
3. Execute merged LAB-085/084/083/082/080 regressions against the same source tree.
4. Fix every failure and repeat until clean.
5. Perform a fresh complete patch audit focused on every alternate mutation entry point, migration-time trigger installation, proof-first ordering, predecessor/root binding, fake/orphan proofs, restart and root/public rotation races.
6. Re-check branch/main divergence and integrate only after a clean gate. Prefer normal ready/squash merge; use only the AGENTS.md conflict-checked Contents API fallback if the normal merge path is unavailable and the audited file-scoped change remains conflict-independent.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; design blocker fixed, exact current-head regression/audit gate remains.
- PostgreSQL-specific validation and open-model serving remain deferred until representative runtime/hardware is available.
