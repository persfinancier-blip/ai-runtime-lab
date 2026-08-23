# Current Lab State

Last updated: 2026-08-23

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085.
- Active: Issue #163 / LAB-086 — IN_PROGRESS.
- Branch: `lab/086-asymmetric-break-glass-history`.
- Draft PR: #165 `[LAB-086] Asymmetric break-glass proof migration`.
- Current observed PR HEAD: `1039e9268a666409d0f072a31ae758a51deef069`.
- PR is open/draft/mergeable; do not merge until the full exact-source gate below is observed.

## Last completed step

The previous stale post-cutoff LAB-085 public-custody writer blocker has been corrected in the candidate without hiding the old primitive.

A new final supported surface, `experiments/asymmetric_break_glass_history/final_supported.py`, wraps the real LAB-086 ledger and installs cutoff-conditional SQLite fences on public recovery authority/transition/head mutation. After the migration boundary exists, the old LAB-085 `AsymmetricRecoveryCustody.rotate()` path cannot commit a successor unless an exact LAB-086 root-coauthorization proof already binds the proposed successor to the currently active public predecessor and current normal/root `(id, version, generation)`.

The final supported rotation path is proof-first inside one `BEGIN IMMEDIATE`: validate old/new public Ed25519 thresholds + current root threshold, persist/check the exact `provider_asymmetric_recovery_public_root_proofs` row, call the existing custody `rotate_locked()` primitive, verify resulting history, then commit. Any failure rolls back proof + authority + transition + head together.

`tests/test_stale_public_writer_regression.py` now targets the final fenced surface and contains both the stale underlying-writer rejection and the legitimate proof-first supported rotation success path.

## Evidence produced

- Final fenced surface blob: `23bc6bdc614ff3158e05f4d22cbac0e426d8197b`.
- Updated stale-writer regression blob: `381b1c4a1c82f819e83b520eb628ca004d0efcbb`.
- Durable research/evidence note: `research/2026-08-23-lab086-stale-public-writer-fence.md`.
- An actually executed deterministic SQLite probe using the same trigger predicates observed:
  - stale writer without root proof -> `IntegrityError`; rollback preserved the old public head and authority count;
  - exact root proof first -> successor authority + transition + head committed with exactly one proof row.
- Earlier exact standalone LAB-086 reference suite remains 12/12 passed on the unchanged reference layer; unsafe legacy auto-promotion failed as expected.
- Earlier exact `migration_guard.py` source compiled successfully.
- Direct shell GitHub DNS remains unavailable; GitHub connector is healthy and remains the supported source/control-plane path.
- Current branch/main compare: diverged, ahead 42 / behind 9; all 14 LAB-086 paths are additions relative to the merge base. Re-check before any integration.

## Known blockers / constraints

- The stale-writer design/implementation blocker is fixed in the current candidate.
- The current HEAD has not yet passed the required repository-wide exact-source regression stack after the fence change. The deterministic SQL probe is not a substitute for this gate.
- Logical SQLite-state scrubbing is not forensic erasure; WAL/filesystem remnants remain outside the claim.
- Whole-store rollback freshness remains delegated to the external monotonic-anchor layer. No live HSM/KMS is claimed.
- `suffix.SupportedAsymmetricBreakGlassLedger` is now an underlying implementation primitive; the final supported authority boundary is `final_supported.SupportedFencedAsymmetricBreakGlassLedger`. The database fence still blocks stale low-level custody mutation when the final surface owns the store.

## Exact next action

1. Re-fetch PR #165 and require HEAD `1039e9268a666409d0f072a31ae758a51deef069` or restart the gate if it moved.
2. Reconstruct exact current-head executable bytes through the GitHub connector, including the new final surface and updated stale-writer regression.
3. Execute current-head LAB-086 tests: stale-writer/final-supported rotation, migration guard, suffix, public-history boundary, scrubbed legacy-prefix + asymmetric-suffix restart, protocol and unsafe seed; run compileall.
4. Execute merged LAB-085/084/083/082/080 regression suites against the same reconstructed source tree.
5. Fix every failure. Then perform a fresh full PR patch audit, with special attention to trigger/proof ordering, exact predecessor/root binding, orphan proof behavior, restart, and whether any alternate supported entry point can mutate public recovery state without the fence.
6. Re-check branch/main divergence and integrate only after a clean gate. If normal merge is unavailable and the final audited change remains file-scoped/conflict-free, the AGENTS.md Contents API fallback may be used after an explicit conflict check.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; implementation blocker fixed, exact current-head regression/audit gate remains.
- PostgreSQL-specific validation and open-model serving remain deferred until representative runtime/hardware is available.
