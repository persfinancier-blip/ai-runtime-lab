# Current Lab State

Last updated: 2026-08-25

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085.
- Active: Issue #163 / LAB-086 — IN_PROGRESS.
- Branch: `lab/086-asymmetric-break-glass-history`.
- Draft PR: #165 `[LAB-086] Asymmetric break-glass proof migration`.
- Current observed branch HEAD: `6085a9a01c9d895833c4964d777d412a4f795478`.
- PR remains draft; the post-cutoff proof-row creation blocker is now fixed and exact-tested, but the full real-ledger gate is still pending.

## Last completed step

Applied the saved LAB-086 proof-INSERT authorization patch to the exact branch `strict_fence.py` blob `4c16161e83781745f9bf7adce34e4d06ca51e192` using the Contents API after reconstructing the complete file byte-for-byte locally. The local pre-patch hash matched the GitHub blob exactly.

The patched runtime changes closed both unseen-key insertion paths after cutoff:
- `provider_asymmetric_break_glass_proofs`;
- `provider_asymmetric_recovery_public_root_proofs`.

`remove_public_mutation_fence_locked()` now removes only the proof-creation triggers transactionally for the final verified writer. UPDATE/DELETE history guards remain installed. `_install_post_cutoff_evidence_freeze_locked()` now rejects every direct post-cutoff proof INSERT, not only replacement of an existing key.

Published runtime commit: `ab73edec1d67f0e0b731ee38aa210aefeb6dc150`; exact published `strict_fence.py` blob: `02128fb866d7b4a3382622356f33e7b1739ff167`, identical to the locally executed candidate.

The old forged-proof test harness was also corrected: ordinary DML now fails earlier by design, so the test explicitly drops only the proof-creation trigger to model out-of-band DDL corruption, reinstalls the complete fence, and proves the forged row still does not become mutation authority. Test-only commit/current HEAD: `6085a9a01c9d895833c4964d777d412a4f795478`; exact `test_strict_fence.py` blob `97048a325c4cc1ed78612bdbb4cfec42146a43f6`.

## Evidence produced / reconfirmed

- Exact post-fix runtime blob: `strict_fence.py` `02128fb866d7b4a3382622356f33e7b1739ff167`.
- Exact updated `test_strict_fence.py` blob: `97048a325c4cc1ed78612bdbb4cfec42146a43f6`.
- Exact existing `test_post_cutoff_evidence_insert_authorization.py` blob: `60ab3e1b4df369e90ce3a4f44a077ff3f3c2a33b`.
- Published-source local execution against byte-identical files: **12/12 PASS** (`test_strict_fence` 10 + proof-creation authorization 2).
- `py_compile`/focused compile passed. ResourceWarning noise in the strict suite is unrelated to assertions.
- Cumulative lower-stack exact evidence remains: LAB-080 18/18, LAB-082 28/28, LAB-083 24/24, LAB-084 17/17, LAB-085 core 12/12, asymmetric-custody 8/8, public/final 11/11; lower unsafe baselines failed as intended.
- Exact standalone LAB-086 corrected suite previously passed 12/12; unsafe legacy-auto-promotion seed failed as intended.
- Fresh branch/main compare after the fix: `ahead 133 / behind 71`; all 50 PR paths remain additions relative to current main.

## Known blockers / constraints

- Remaining merge gate: exact current-head real-ledger `migration_guard + suffix + final_supported` suite on the proven LAB-080→085 dependency closure, then unsafe legacy-promotion seed, full compileall and a fresh final security audit.
- Direct shell GitHub transport remains unavailable; GitHub connector/Contents API is the supported fallback.
- LAB-087/#166 owns arbitrary same-privilege SQLite DDL/schema control.
- LAB-088/#167 owns threshold signer-noise robustness.
- LAB-090/#169 owns provider-generation handoff freshness/external-anchor race.
- LAB-091/#170 owns mutable shared-anchor ordinary-DML writer authorization and authorization of new provider-receipt INSERTs.
- Logical SQL scrubbing is not forensic erasure; whole-store rollback freshness remains delegated to the external monotonic-anchor layer.

## Exact next action

1. Reconstruct exact current HEAD `migration_guard.py`, `suffix.py`, `final_supported.py` and all current real-ledger LAB-086 tests into the already proven LAB-080→085 dependency closure; verify executable/test blobs.
2. Execute migration v4/root coauthorization/restart, scrubbed-prefix/asymmetric-suffix, orphan/partial state, public-rotation cross-binding/history, inherited/direct surfaces, rotation races, final single-snapshot verification, and all corruption-harness regressions updated for the stronger DML fence.
3. Run unsafe legacy-promotion seed and full compileall over the complete closure.
4. Perform a fresh full security audit of consequential/restart mutation paths and re-check branch/main divergence. Keep PR #165 draft until the complete current-head gate is clean; only then mark ready and integrate.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; proof-row creation blocker fixed and exact-tested 12/12; full real-ledger gate remains.
- #166 / LAB-087 — READY; SQLite schema-control trust boundary.
- #167 / LAB-088 — READY; threshold signer-noise robustness.
- #168 / LAB-089 — CLOSED `not_planned`.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — READY; mutable/shared-ledger plus new provider-receipt ordinary-DML writer authorization.
- PostgreSQL-specific validation and open-model serving remain deferred until representative runtime/hardware is available.
