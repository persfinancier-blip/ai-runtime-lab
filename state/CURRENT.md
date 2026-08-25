# Current Lab State

Last updated: 2026-08-25

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085.
- Active: Issue #163 / LAB-086 — IN_PROGRESS.
- Branch: `lab/086-asymmetric-break-glass-history`.
- Draft PR: #165 `[LAB-086] Asymmetric break-glass proof migration`.
- Current observed PR HEAD: `264d7ad13e305d966d11b5cc8bde2b84034bab7e`.
- PR remains draft; a new public-rotation cross-binding blocker is now covered by an expected-failing real-ledger regression and must be fixed before the full merge gate resumes.

## Last completed step

A fresh current-head audit found a cross-layer mix-and-match gap in post-cutoff public recovery rotation.

LAB-085 `provider_recovery_public_transitions` authenticates old+new Ed25519 signatures over a custody rotation payload containing its own `root_authority_id`. LAB-086 separately authenticates `provider_asymmetric_recovery_public_root_proofs` with the normal/root threshold. `_verify_public_recovery_rotations_locked()` verifies the root-proof row but does not load the corresponding public-transition row under the same locked verifier or require both rows to bind the same root/payload.

Therefore two independently valid proof sets can be combined: a public transition valid under root1 plus a LAB-086 root-threshold proof valid under root2. This violates the intended old-public + new-public + current-root authorization over one exact canonical transition and also means the post-mutation q-verifier does not re-check the newly uncommitted public transition.

Published regression commit: `264d7ad13e305d966d11b5cc8bde2b84034bab7e`, file `experiments/asymmetric_break_glass_history/tests/test_public_rotation_cross_binding.py`. It creates a valid P1→P2 rotation under root1, then a valid root1→root2 rotation, then rebinds only the LAB-086 root proof to root2 with a valid root2 quorum. Correct behavior is rejection as mix-and-match.

A minimal verifier fix was prepared locally against an exact byte reconstruction of current `suffix.py`: the unmodified reconstruction matched Git blob `bb9f8e55fb03424ac19c152ae2d8aceaf2e1c078`; the local fixed candidate compiles and has Git blob `44847bde53b9f7b0e2fbcbab37d36dc992f497b2`. It is not yet published because the Contents API requires a full-file replacement and no non-exact rewrite is allowed.

## Evidence produced / reconfirmed

- Current PR HEAD after regression: `264d7ad13e305d966d11b5cc8bde2b84034bab7e`.
- New regression is durable on the PR branch; it has not yet been executed against the full dependency closure and no PASS is claimed.
- Exact current `suffix.py` reconstruction matched branch blob `bb9f8e55fb03424ac19c152ae2d8aceaf2e1c078` before editing.
- Local candidate verifier fix `py_compile`: PASS; local candidate blob `44847bde53b9f7b0e2fbcbab37d36dc992f497b2`.
- Issue #163 audit report comment: `5407017732`; PR #165 report comment: `5407020953`.
- Lower-stack exact gate remains complete from prior observed runs: LAB-080 18/18, LAB-082 28/28, LAB-083 24/24, LAB-084 17/17, LAB-085 core 12/12, LAB-085 asymmetric-custody 8/8, LAB-085 public/final 11/11.
- Earlier unchanged LAB-086 evidence remains: standalone 12/12, strict/inherited/root-head fence slices, orphan/pre-cutoff evidence focused regressions, and final single-snapshot contract PASS; unsafe legacy auto-promotion failed as intended.
- Direct shell GitHub transport was re-probed and still fails DNS; GitHub connector remains healthy.

## Known blockers / constraints

- Immediate blocker: publish the exact `suffix.py` cross-binding verifier fix and make `test_public_rotation_cross_binding.py` pass on the real supported ledger.
- After that, the remaining LAB-086 merge gate is exact current-head real-ledger migration/suffix/final-supported execution, unsafe seed, full compileall and final audit.
- Do not weaken the fix to wrapper-only validation: direct `SupportedAsymmetricBreakGlassLedger` restart verification must also reject mix-and-match.
- LAB-083/LAB-084 signer-noise issue #167 remains separate fail-closed DoS/robustness work.
- LAB-086 SQLite fences cover stale/alternate supported mutation paths and audited DML, not arbitrary same-privilege raw SQLite DDL/schema control; that broader boundary is LAB-087/#166.
- Logical SQL scrubbing is not forensic erasure. Whole-store rollback freshness remains delegated to the external monotonic-anchor layer.

## Exact next action

1. Publish the prepared minimal `suffix.py` fix from the exact current blob: inside `_verify_public_recovery_rotations_locked`, load `provider_recovery_public_transitions` for each successor; require exact predecessor, `root_authority_id`, and `intent_digest` equality with the LAB-086 root-proof row; reconstruct one `custody_rotation_payload`; verify old+new Ed25519 thresholds and root threshold over that same payload; require canonical stored signature encodings.
2. Reconstruct the exact updated PR dependency closure and execute `test_public_rotation_cross_binding.py` first. The pre-fix scenario must fail verification and the post-fix test must PASS.
3. Execute the remaining current-head migration/suffix/final-supported real-schema modules, unsafe legacy-promotion expected-failure seed, and full `python -m compileall`.
4. Perform one final security audit of every consequential/restart writer plus branch/main divergence. Fix every failure before changing PR #165 out of draft.
5. Only after a clean gate, mark PR #165 ready and integrate by normal merge when available; use only the documented audited file-scoped Contents API fallback if normal merge is unavailable and conflicts are rechecked.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; public-transition/root-proof cross-binding blocker now explicit and regression-backed.
- #166 / LAB-087 — READY; SQLite schema-control trust boundary.
- #167 / LAB-088 — READY; threshold signer-noise robustness.
- #168 / LAB-089 — CLOSED `not_planned`.
- PostgreSQL-specific validation and open-model serving remain deferred until representative runtime/hardware is available.
