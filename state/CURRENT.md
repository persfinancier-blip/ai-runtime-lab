# Current Lab State

Last updated: 2026-08-25

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085.
- Active: Issue #163 / LAB-086 — IN_PROGRESS.
- Branch: `lab/086-asymmetric-break-glass-history`.
- Draft PR: #165 `[LAB-086] Asymmetric break-glass proof migration`.
- Current observed branch HEAD: `984147026697114ae4f9a973e82ba64d64794673`.
- PR remains draft; post-cutoff proof-creation authorization is only partially fixed.

## Last completed step

Fresh security audit found that the two LAB-086-only post-cutoff proof tables still allow ordinary SQL INSERT of a previously unseen primary key:
- `provider_asymmetric_break_glass_proofs`;
- `provider_asymmetric_recovery_public_root_proofs`.

Current `strict_fence.py` only rejects replacement of an existing key plus UPDATE/DELETE. A focused SQLite counterexample confirmed a brand-new bogus proof key is accepted after cutoff. This is persistent fail-closed DoS/correctness damage because LAB-086 restart verification expects exact proof cardinality and binding.

Durable branch evidence:
- red real regression `experiments/asymmetric_break_glass_history/tests/test_post_cutoff_evidence_insert_authorization.py`, commit `ec588c60002124ec2fe95ce067d4e869036838ef`;
- exact patch plan `research/2026-08-25-lab086-post-cutoff-proof-insert-authorization.patch`, commit `313ead57c10c606759cc988e2d6f3ecd43a7ec3a`;
- research note commit `f76f29a222752133aeda1656b971de2682f959d7`.

Applied the small writer-ordering half of that patch to runtime `final_supported.py` through Contents API:
- commit/current HEAD `984147026697114ae4f9a973e82ba64d64794673`;
- published `final_supported.py` blob `ceb7f48a55a931ba9923cac77d4ebf6c4cd2cfec`.

`rotate_public_recovery_authority()` now inserts a missing verified public-root proof only inside the existing transaction-scoped thaw, after all quorum checks and existing-proof substitution checks. This remains compatible with the current permissive trigger and prepares the writer for the strict creation gate.

The main runtime blocker is intentionally still open: `strict_fence.py` remains blob `4c16161e83781745f9bf7adce34e4d06ca51e192`, so direct new proof-key INSERT is still possible. No passing result is claimed for the new real regression yet.

## Evidence produced / reconfirmed

- Executed semantic counterexample: unseen proof key currently inserts successfully after cutoff in both LAB-086 proof tables.
- Executed design probe: direct post-cutoff proof INSERT is denied under the proposed creation gate, while `BEGIN IMMEDIATE -> remove creation gate -> INSERT verified proof -> reinstall gate -> COMMIT` succeeds. Existing UPDATE/DELETE history guards stay active.
- Existing exact provider-receipt fence gate remains: 10/10 strict + 2/2 receipt PASS; focused compileall PASS.
- Cumulative exact lower-stack evidence remains: LAB-080 18/18, LAB-082 28/28, LAB-083 24/24, LAB-084 17/17, LAB-085 core 12/12, asymmetric-custody 8/8, public/final 11/11; lower unsafe baselines failed as intended.
- Exact standalone LAB-086 corrected suite previously passed 12/12; unsafe legacy-auto-promotion seed failed as intended.

## Known blockers / constraints

- Immediate blocker: apply the saved proof-INSERT authorization patch to exact runtime `strict_fence.py` and make the new real regression green. The final-writer ordering half is already published.
- Remaining merge gate after that: complete current-head real-ledger `migration_guard + suffix + final_supported` suite, unsafe legacy-promotion seed, full compileall, then fresh full security audit.
- Direct shell GitHub transport is unavailable in this run; GitHub connector/Contents API is the supported fallback. Avoid full-file rewrites without byte-level reconstruction/verification.
- LAB-087/#166 owns arbitrary same-privilege SQLite DDL/schema control.
- LAB-088/#167 owns threshold signer-noise robustness.
- LAB-090/#169 owns provider-generation handoff freshness/external-anchor race.
- LAB-091/#170 owns mutable shared-anchor ordinary-DML writer authorization and authorization of new provider-receipt INSERTs. It does not own the two closed-set LAB-086 proof tables above.
- Logical SQL scrubbing is not forensic erasure; whole-store rollback freshness remains delegated to the external monotonic-anchor layer.

## Exact next action

1. Reconstruct exact branch `strict_fence.py` blob `4c16161e83781745f9bf7adce34e4d06ca51e192`, apply `research/2026-08-25-lab086-post-cutoff-proof-insert-authorization.patch` locally, verify source hash/compile, and execute the new regression before/after patch.
2. Publish only the byte-verified patched `strict_fence.py` through Contents API; re-fetch and verify resulting Git blob; run `test_post_cutoff_evidence_insert_authorization.py` plus existing strict/post-cutoff evidence regressions against current `final_supported.py` blob `ceb7f48a...`.
3. Reconstruct/execute all remaining current-head real-ledger migration/suffix/final-supported tests on the already proven LAB-080→085 closure.
4. Run unsafe legacy-promotion seed and full compileall.
5. Perform fresh full security audit and branch/main conflict check; restore/reduce documentation-only `strict_fence.py` rewrite noise. Only after a clean gate may PR #165 be marked ready and integrated.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; proof-row creation blocker reproduced; red regression + exact patch persisted; writer-ordering half applied; strict runtime creation gate still pending.
- #166 / LAB-087 — READY; SQLite schema-control trust boundary.
- #167 / LAB-088 — READY; threshold signer-noise robustness.
- #168 / LAB-089 — CLOSED `not_planned`.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — READY; mutable/shared-ledger plus new provider-receipt ordinary-DML writer authorization.
- PostgreSQL-specific validation and open-model serving remain deferred until representative runtime/hardware is available.
