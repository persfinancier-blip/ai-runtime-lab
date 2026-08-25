# Current Lab State

Last updated: 2026-08-25

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085.
- Active: Issue #163 / LAB-086 — IN_PROGRESS.
- Branch: `lab/086-asymmetric-break-glass-history`.
- Draft PR: #165 `[LAB-086] Asymmetric break-glass proof migration`.
- Current observed PR HEAD: `6404c7f471588e196728a34938f50a41936fbf3f`.
- PR remains draft; a public-rotation cross-binding blocker is regression-backed and the exact fix diff is now durable on the PR branch, but the implementation file has not yet been rewritten/published.

## Last completed step

A fresh current-head audit found a cross-layer mix-and-match gap in post-cutoff public recovery rotation.

LAB-085 `provider_recovery_public_transitions` authenticates old+new Ed25519 signatures over a custody rotation payload containing its own `root_authority_id`. LAB-086 separately authenticates `provider_asymmetric_recovery_public_root_proofs` with the normal/root threshold. `_verify_public_recovery_rotations_locked()` verifies the root-proof row but does not load the corresponding public-transition row under the same locked verifier or require both rows to bind the same root/payload.

Therefore two independently valid proof sets can be combined: a public transition valid under root1 plus a LAB-086 root-threshold proof valid under root2. This violates the intended old-public + new-public + current-root authorization over one exact canonical transition and means the post-mutation q-verifier does not re-check the newly uncommitted public transition.

Published regression commit: `264d7ad13e305d966d11b5cc8bde2b84034bab7e`, file `experiments/asymmetric_break_glass_history/tests/test_public_rotation_cross_binding.py`. It creates a valid P1→P2 rotation under root1, then a valid root1→root2 rotation, then rebinds only the LAB-086 root proof to root2 with a valid root2 quorum. Correct behavior is rejection as mix-and-match.

The exact implementation fix is now also durable as `research/2026-08-25-lab086-public-rotation-cross-binding.patch`, commit/current HEAD `6404c7f471588e196728a34938f50a41936fbf3f`. The patch is generated from an exact byte reconstruction of current `suffix.py`: unmodified local hash matched branch blob `bb9f8e55fb03424ac19c152ae2d8aceaf2e1c078`; applying the patch locally produced candidate blob `44847bde53b9f7b0e2fbcbab37d36dc992f497b2`; candidate `py_compile` passed. The patch has not yet been applied to `suffix.py`, so no fixed regression PASS is claimed.

## Evidence produced / reconfirmed

- Current PR HEAD: `6404c7f471588e196728a34938f50a41936fbf3f`.
- Regression commit: `264d7ad13e305d966d11b5cc8bde2b84034bab7e`.
- Exact fix patch commit: `6404c7f471588e196728a34938f50a41936fbf3f`.
- Exact current `suffix.py` reconstruction matched branch blob `bb9f8e55fb03424ac19c152ae2d8aceaf2e1c078` before editing.
- Local patched candidate `py_compile`: PASS; candidate blob `44847bde53b9f7b0e2fbcbab37d36dc992f497b2`.
- New regression has not yet been executed against the full dependency closure; no PASS is claimed.
- Issue #163 audit report comment: `5407017732`; PR #165 report comment: `5407020953`.
- Lower-stack exact gate remains complete from prior observed runs: LAB-080 18/18, LAB-082 28/28, LAB-083 24/24, LAB-084 17/17, LAB-085 core 12/12, LAB-085 asymmetric-custody 8/8, LAB-085 public/final 11/11.
- Earlier unchanged LAB-086 evidence remains: standalone 12/12, strict/inherited/root-head fence slices, orphan/pre-cutoff evidence focused regressions, and final single-snapshot contract PASS; unsafe legacy auto-promotion failed as intended.
- Direct shell GitHub transport was re-probed and still fails DNS; GitHub connector remains healthy.

## Known blockers / constraints

- Immediate blocker: apply the durable exact patch to `suffix.py` through the Contents API and make `test_public_rotation_cross_binding.py` pass on the real supported ledger.
- After that, remaining LAB-086 merge gate is exact current-head real-ledger migration/suffix/final-supported execution, unsafe seed, full compileall and final audit.
- Do not weaken the fix to wrapper-only validation: direct `SupportedAsymmetricBreakGlassLedger` restart verification must reject mix-and-match.
- LAB-083/LAB-084 signer-noise issue #167 remains separate fail-closed DoS/robustness work.
- LAB-086 SQLite fences cover stale/alternate supported mutation paths and audited DML, not arbitrary same-privilege raw SQLite DDL/schema control; that broader boundary is LAB-087/#166.
- Logical SQL scrubbing is not forensic erasure. Whole-store rollback freshness remains delegated to the external monotonic-anchor layer.

## Exact next action

1. Apply `research/2026-08-25-lab086-public-rotation-cross-binding.patch` exactly to current `suffix.py` blob `bb9f8e55fb03424ac19c152ae2d8aceaf2e1c078` through the normal Contents API. After publication, verify the resulting Git blob matches the expected local candidate `44847bde53b9f7b0e2fbcbab37d36dc992f497b2` before counting it as the audited fix.
2. Reconstruct the exact updated PR dependency closure and execute `test_public_rotation_cross_binding.py` first. It must PASS only after the verifier cross-binds predecessor/root ID/intent digest and re-verifies both Ed25519 quorums on the same payload.
3. Execute remaining current-head migration/suffix/final-supported real-schema modules, unsafe legacy-promotion expected-failure seed, and full `python -m compileall`.
4. Perform one final security audit of every consequential/restart writer plus branch/main divergence. Fix every failure before changing PR #165 out of draft.
5. Only after a clean gate, mark PR #165 ready and integrate by normal merge when available; use only the documented audited file-scoped Contents API fallback if normal merge is unavailable and conflicts are rechecked.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; public-transition/root-proof cross-binding blocker explicit, regression and exact fix patch durable.
- #166 / LAB-087 — READY; SQLite schema-control trust boundary.
- #167 / LAB-088 — READY; threshold signer-noise robustness.
- #168 / LAB-089 — CLOSED `not_planned`.
- PostgreSQL-specific validation and open-model serving remain deferred until representative runtime/hardware is available.
