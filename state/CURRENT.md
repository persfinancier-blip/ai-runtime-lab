# Current Lab State

Last updated: 2026-08-25

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085.
- Active: Issue #163 / LAB-086 — IN_PROGRESS.
- Branch: `lab/086-asymmetric-break-glass-history`.
- Draft PR: #165 `[LAB-086] Asymmetric break-glass proof migration`.
- Current observed PR HEAD: `58aa166b499281559390ba78a472dc6c328b9325`.
- PR remains draft/mergeable; full current-head real-ledger regression gate has not passed.

## Last completed step

A fresh DML-boundary audit found and fixed another LAB-086 post-cutoff integrity gap. The authenticated migration projection commits legacy compatibility/lifecycle/custody semantics, but the prior SQL policy only blocked some new INSERTs. Ordinary UPDATE/DELETE could still alter projected rows such as `provider_rotation_recovery_transitions`, lifecycle state, custody bindings and custody proof/enablement rows, creating persistent fail-closed state that would only be detected by the next verifier.

Focused pre-fix SQLite reproduction actually executed: new legacy INSERT was blocked, while semantic UPDATE/DELETE and custody-binding UPDATE/DELETE committed successfully.

The branch now freezes every SQL row represented by the signed legacy projection. Four tables intentionally scrubbed during the cutoff transaction have scrub-aware UPDATE guards: every semantic column must stay identical and only canonical HMAC key/signature fields may become `{}` / `[]`. All other projected rows reject INSERT/UPDATE/DELETE after cutoff. These legacy-projection triggers are deliberately not removed by the final writer's transaction-scoped thaw because no supported post-cutoff operation needs to mutate the frozen prefix.

Published branch changes:
- new regression commit `d725266c69118f2786c4ccb51bd8730b5eb252d5`;
- fence implementation/current HEAD `58aa166b499281559390ba78a472dc6c328b9325`.

## Evidence produced / reconfirmed

- Published `strict_fence.py` blob: `0b9e4dfea254723e65ffb33ccb5c082e1d0c09ad`; exactly equal to the locally executed candidate.
- Published `test_legacy_projection_dml_fence.py` blob: `e1df33304cb9808dd099cf8342770f879084d8bb`; exactly equal to the locally executed test.
- Exact new regression: **4/4 PASS**.
- Focused compileall for the patched LAB-086 fence package: PASS.
- Correct semantics observed: pre-cutoff projected rows remain live; cutoff permits the exact HMAC scrub; post-cutoff semantic INSERT/UPDATE/DELETE is denied; final-writer current-authority thaw does not thaw legacy projection state.
- Issue #163 evidence comment: `5408029646`; PR #165 evidence comment: `5408031684`.
- Lower-stack exact gate remains complete from prior observed runs: LAB-080 18/18, LAB-082 28/28, LAB-083 24/24, LAB-084 17/17, LAB-085 core 12/12, LAB-085 asymmetric-custody 8/8, LAB-085 public/final 11/11; lower unsafe baselines failed as expected.
- Existing LAB-086 evidence remains relevant: standalone 12/12; current strict/inherited/root-head fence slices; orphan/pre-cutoff regressions; final single-snapshot contract PASS; public-rotation cross-binding focused checks; unsafe legacy auto-promotion failed as intended.
- Direct shell GitHub transport remains unavailable; GitHub connector + Contents API are healthy and are the supported control-plane path.

## Known blockers / constraints

- Full current-head real-ledger gate remains mandatory after the new fence change: migration/root-coauthorization, scrubbed-prefix/asymmetric-suffix, orphan/partial-state, public/lower-history guards, public-rotation cross-binding, direct-surface/fence cases and rotation races must execute together on the supported ledger.
- New 4/4 focused DML-fence evidence is exact current-head evidence for the new policy but is not a substitute for the full real-schema stack.
- The migration projection still relies on SQL/schema-control integrity for enforcement against mutation of committed rows. Arbitrary same-privilege DDL/schema control remains explicitly outside the LAB-086 claim and is LAB-087/#166.
- LAB-083/LAB-084 signer-noise issue #167 remains separate fail-closed DoS/robustness work.
- Logical SQL scrubbing is not forensic erasure. Whole-store rollback freshness remains delegated to the external monotonic-anchor layer.

## Exact next action

1. Reconstruct the exact current PR HEAD dependency closure via GitHub connector and execute the current-head LAB-086 real-ledger suite, starting with `test_legacy_projection_dml_fence.py`, `test_public_rotation_cross_binding.py`, migration/root-coauthorization and scrubbed-prefix/asymmetric-suffix tests.
2. Execute the remaining final-supported/public-history/lower-history/direct-surface/rotation-race regressions with the published `strict_fence.py` blob `0b9e4d...`.
3. Run unsafe legacy-promotion expected-failure seed and full `python -m compileall` over the complete reconstructed closure.
4. Perform a fresh full security audit of all post-cutoff DML mutation points, consequential writers, restart verification and branch/main divergence. Keep PR #165 draft until all current-head tests are clean; only then mark ready and integrate.
5. Carry the broader unrestricted SQL/DDL trust-boundary question into LAB-087/#166 rather than weakening LAB-086's stated claim.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; legacy projection DML freeze blocker fixed and exact 4/4 focused regression passed; full real-ledger gate remains.
- #166 / LAB-087 — READY; SQLite schema-control trust boundary.
- #167 / LAB-088 — READY; threshold signer-noise robustness.
- #168 / LAB-089 — CLOSED `not_planned`.
- PostgreSQL-specific validation and open-model serving remain deferred until representative runtime/hardware is available.
