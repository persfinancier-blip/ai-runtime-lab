# Current Lab State

Last updated: 2026-08-25

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085.
- Active: Issue #163 / LAB-086 — IN_PROGRESS.
- Branch: `lab/086-asymmetric-break-glass-history`.
- Draft PR: #165 `[LAB-086] Asymmetric break-glass proof migration`.
- Current observed PR HEAD: `d96be88b27a5945eecf70d66d9b9b964a729bc9e`.
- PR remains draft; cross-binding implementation is now published and focused-verified, but the full real-supported-ledger current-head gate has not passed.

## Last completed step

Applied the durable public-rotation cross-binding patch to the actual branch `suffix.py` via the normal Contents API. GitHub returned content blob `44847bde53b9f7b0e2fbcbab37d36dc992f497b2`, exactly matching the previously audited local candidate recorded before publication.

The published `_verify_public_recovery_rotations_locked()` now loads the matching LAB-085 `provider_recovery_public_transitions` row under the same locked verifier and requires exact predecessor, root authority and intent digest binding. It re-verifies old/new Ed25519 quorums on that same canonical custody-rotation payload, requires canonical public signature encodings, then verifies the root threshold proof on the same payload. A valid public transition under root1 can no longer be combined with an independently valid root-threshold proof under root2.

Executed a focused exact-method SQLite check against the exact published `suffix.py` blob: valid same-root state accepted; root1 public transition + root2 root proof rejected; same-root transition with rebound intent digest rejected. Result: **3/3 PASS**. Exact published `suffix.py` `py_compile` also passed. This is focused evidence only, not a substitute for `test_public_rotation_cross_binding.py` on the real supported ledger.

## Evidence produced / reconfirmed

- Cross-binding fix commit: `d96be88b27a5945eecf70d66d9b9b964a729bc9e`.
- Published `suffix.py` blob: `44847bde53b9f7b0e2fbcbab37d36dc992f497b2`, equal to the pre-publication audited candidate.
- Exact published verifier focused SQLite checks: 3/3 PASS.
- Exact published `suffix.py` py_compile: PASS.
- Regression remains `experiments/asymmetric_break_glass_history/tests/test_public_rotation_cross_binding.py`, blob `a871b80c3f651ba49cbb5b603353b0ca7d4d94d7`; full real-ledger execution is still pending.
- Issue #163 evidence comment: `5407582403`; PR #165 evidence comment: `5407583819`.
- Lower-stack exact gate remains complete from prior observed runs: LAB-080 18/18, LAB-082 28/28, LAB-083 24/24, LAB-084 17/17, LAB-085 core 12/12, LAB-085 asymmetric-custody 8/8, LAB-085 public/final 11/11; lower unsafe baselines failed as expected.
- Earlier unchanged LAB-086 evidence remains: standalone 12/12; current strict/inherited/root-head fence slices; orphan/pre-cutoff focused regressions; final single-snapshot contract PASS; unsafe legacy auto-promotion failed as intended.
- Fresh branch/main compare after publication: ahead 104 / behind 56. All 36 PR files are additions in the compare response; no path-level overlap with current main was reported.
- Direct shell GitHub transport remains unavailable; GitHub connector + Contents API are healthy and remain the supported control-plane path.

## Known blockers / constraints

- Immediate remaining gate: execute exact `test_public_rotation_cross_binding.py` against the real LAB-085/LAB-086 supported-ledger dependency closure. The focused 3/3 method check does not replace it.
- Then execute the remaining current-head migration/root-coauthorization, scrubbed-prefix/asymmetric-suffix, full lower/public-history guard, orphan-partial-state and rotation-race regressions; unsafe seed + full compileall + final audit remain mandatory.
- Do not weaken verification to wrapper-only validation: direct `SupportedAsymmetricBreakGlassLedger` restart verification must reject mix-and-match.
- LAB-083/LAB-084 signer-noise issue #167 remains separate fail-closed DoS/robustness work.
- LAB-086 SQLite fences cover stale/alternate supported mutation paths and audited DML, not arbitrary same-privilege raw SQLite DDL/schema control; that broader boundary is LAB-087/#166.
- Logical SQL scrubbing is not forensic erasure. Whole-store rollback freshness remains delegated to the external monotonic-anchor layer.

## Exact next action

1. Reconstruct the exact current-head dependency closure needed by `test_public_rotation_cross_binding.py`: branch LAB-086 implementation/tests plus merged LAB-085/083/082/080 direct dependencies. Verify executable files by Git blob identity where reconstructed.
2. Execute `test_public_rotation_cross_binding.py` first on the real supported ledger. It must pass with the published `suffix.py` blob `44847bde...`.
3. Execute remaining current-head migration/suffix/final-supported real-schema modules, including orphan/partial-state, migration v4 root coauthorization/restart, scrubbed-prefix/asymmetric-suffix, public/lower-history guards, direct-surface/fence cases and rotation races.
4. Run unsafe legacy-promotion expected-failure seed and full `python -m compileall` over the reconstructed closure.
5. Perform a fresh full security audit of every consequential/restart writer and branch/main divergence. Keep PR #165 draft until all current-head tests are clean; only then mark ready and integrate.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; cross-binding implementation published and focused-verified; full real-ledger gate remains.
- #166 / LAB-087 — READY; SQLite schema-control trust boundary.
- #167 / LAB-088 — READY; threshold signer-noise robustness.
- #168 / LAB-089 — CLOSED `not_planned`.
- PostgreSQL-specific validation and open-model serving remain deferred until representative runtime/hardware is available.
