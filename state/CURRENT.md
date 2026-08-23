# Current Lab State

Last updated: 2026-08-23

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085.
- Active: Issue #163 / LAB-086 — IN_PROGRESS.
- Branch: `lab/086-asymmetric-break-glass-history`.
- Draft PR: #165 `[LAB-086] Asymmetric break-glass proof migration`.
- Previous observed PR HEAD was `1039e9268a666409d0f072a31ae758a51deef069`; branch advanced in this run with regression commit `436459b01744cbdf14bfc9302a7fbee168cea303`.
- Do not merge until the new alternate-surface blocker is fixed and the full exact-source gate passes.

## Last completed step

A fresh current-head audit found an authority bypass not covered by the prior stale LAB-085 custody-writer fence. `final_supported.SupportedFencedAsymmetricBreakGlassLedger` correctly installs proof-first SQL fencing, but `suffix.SupportedAsymmetricBreakGlassLedger` remains directly importable/constructible and still exposes its older mutation-first `rotate_public_recovery_authority()` method. A caller can therefore use the still-named supported suffix surface directly after cutoff and avoid installation of the final fence.

An executable regression was added at `experiments/asymmetric_break_glass_history/tests/test_unfenced_supported_surface_regression.py`. It constructs the suffix surface directly, establishes the migration cutoff, and requires direct public-recovery rotation to fail closed. This is expected to fail on the current implementation from source inspection.

## Evidence produced

- Regression commit: `436459b01744cbdf14bfc9302a7fbee168cea303`.
- Issue #163 comment records the bypass and required fix.
- Current exact source inspection confirmed:
  - `final_supported.py` installs the proof-first public authority/transition/head fence;
  - `suffix.py` still contains a separate mutation-first `rotate_public_recovery_authority()` implementation;
  - migration-guard triggers currently fence legacy symmetric/HMAC writes, not this direct public-custody rotation path.
- Shell GitHub transport was probed again and remains unavailable; GitHub connector is healthy. No test execution is claimed for the new regression.
- Earlier evidence remains valid only for the earlier source states: standalone LAB-086 12/12, unsafe legacy auto-promotion expected failure, and deterministic SQLite proof-first fence probe.

## Known blockers / constraints

- NEW merge blocker: alternate directly usable `SupportedAsymmetricBreakGlassLedger` can bypass the final post-cutoff public-rotation fence.
- Full current-head exact-source regression stack has not run after the fence/regression changes.
- Logical SQLite-state scrubbing is not forensic erasure; WAL/filesystem remnants remain outside the claim.
- Whole-store rollback freshness remains delegated to the external monotonic-anchor layer. No live HSM/KMS is claimed.

## Exact next action

1. Fix the alternate supported-surface bypass. Preferred minimal shape: make `suffix.SupportedAsymmetricBreakGlassLedger.rotate_public_recovery_authority()` fail closed after cutoff and require `final_supported.SupportedFencedAsymmetricBreakGlassLedger` for consequential public recovery rotation; alternatively install the exact same durable proof-first fence at migration boundary if that preserves all acceptance invariants.
2. Make `test_unfenced_supported_surface_regression.py` pass and update any older suffix tests that intentionally exercised the now-unsupported consequential method to use the final supported surface.
3. Re-fetch PR #165 and reconstruct exact current-head executable bytes through the GitHub connector.
4. Execute all LAB-086 tests (including stale LAB-085 writer and new direct-suffix bypass), unsafe seed, and compileall.
5. Execute merged LAB-085/084/083/082/080 regressions against the same source tree.
6. Fix every failure, then perform a fresh full PR patch audit focused on every alternate mutation entry point, trigger/proof ordering, predecessor/root binding, orphan proofs and restart.
7. Re-check branch/main divergence and integrate only after a clean gate. Use only normal merge or the AGENTS.md conflict-checked Contents API fallback for a small audited file-scoped change if normal merge is unavailable.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; alternate supported-surface authority bypass is the current blocker.
- PostgreSQL-specific validation and open-model serving remain deferred until representative runtime/hardware is available.
