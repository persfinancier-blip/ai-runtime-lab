# Current Lab State

Last updated: 2026-08-25

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085.
- Active: Issue #163 / LAB-086 — IN_PROGRESS.
- Branch: `lab/086-asymmetric-break-glass-history`.
- Draft PR: #165 `[LAB-086] Asymmetric break-glass proof migration`.
- Current observed branch commit after provider-receipt fix: `19889dab21ef38c3b8517b9d9bd18f5fe45b755d`.
- PR remains draft; full current-head real-ledger gate has not passed.

## Last completed step

Closed the immediate provider-receipt DML blocker. Applied `research/2026-08-25-lab086-provider-receipt-dml-fence.patch` through the supported GitHub Contents API to exact base blob `34ba1db9c5aa04fc55c3842d73d5ceff92964b55`.

Published `strict_fence.py` blob is `4c16161e83781745f9bf7adce34e4d06ca51e192`. Reconstructed that exact runtime blob locally and verified `git hash-object` equality. Reconstructed exact test blobs and executed them:
- `test_strict_fence.py` `4b651db3638c8b9f2341d52b512f075c4b3c31d2`: **10/10 PASS**.
- `test_provider_receipt_dml_fence.py` `a630e0c42923aa160b25cdbf6d0e586549b4305a`: **2/2 PASS**.
- focused compileall: PASS.

The corrected policy blocks UPDATE, DELETE, INSERT OR REPLACE and UPSERT of an existing `asymmetric_provider_receipts.request_id`, while a new distinct receipt remains insertable.

Post-write commit audit found documentation/comment/docstring deletions beyond the intended functional additions, but no functional code deletion. Treat this as maintainability noise to restore/reduce before final ready/merge.

Fresh compare after the fix: branch `ahead 127 / behind 67`; all 47 PR paths remain additions relative to current main, so current divergence is history-only/path-nonoverlapping.

## Evidence produced / reconfirmed

- Exact runtime provider-receipt fence blob: `4c16161e83781745f9bf7adce34e4d06ca51e192`.
- Exact provider-receipt regression gate: **12/12 total unique tests PASS** (10 strict + 2 receipt).
- Focused compileall PASS.
- Cumulative lower-stack evidence remains: LAB-080 18/18, LAB-082 28/28, LAB-083 24/24, LAB-084 17/17, LAB-085 core 12/12, LAB-085 asymmetric-custody 8/8, LAB-085 public/final 11/11; lower unsafe baselines failed as intended.
- Exact standalone LAB-086 corrected suite previously passed 12/12; unsafe legacy-auto-promotion seed failed as intended.

## Known blockers / constraints

- Remaining merge gate: exact current-head real-ledger `migration_guard + suffix + final_supported` suite, unsafe legacy-promotion seed, full compileall, then fresh full security audit.
- The Contents API rewrite removed comments/docstring from `strict_fence.py`; restore/reduce that documentation-only diff before ready/merge unless a newer exact branch rewrite supersedes it.
- Direct shell GitHub transport is unavailable in this run; connector reads/writes work and are the supported fallback.
- LAB-087/#166 owns arbitrary same-privilege SQLite DDL/schema control.
- LAB-088/#167 owns threshold signer-noise robustness.
- LAB-090/#169 owns provider-generation handoff freshness/external-anchor race.
- LAB-091/#170 owns mutable shared-anchor ordinary-DML writer authorization.
- Logical SQL scrubbing is not forensic erasure; whole-store rollback freshness remains delegated to the external monotonic-anchor layer.

## Exact next action

1. Re-fetch PR #165 HEAD and reconstruct exact current LAB-086 `migration_guard.py`, `suffix.py`, `final_supported.py` plus all current real-schema tests against the already proven LAB-080→085 dependency closure.
2. Execute the complete current-head migration/suffix/final-supported suite, including orphan/partial state, v4 root coauthorization/restart, scrubbed-prefix/asymmetric-suffix, full lower/public-history guards, public-rotation cross-binding/history, inherited/direct surfaces, rotation races and final single-snapshot verification.
3. Run unsafe legacy-promotion seed and full compileall.
4. Perform fresh full security audit and branch/main divergence/conflict check. Restore/reduce the documentation-only `strict_fence.py` rewrite noise before ready/merge.
5. Only after a clean current-head gate may PR #165 be marked ready and integrated.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; provider-receipt DML blocker fixed and exact tested; full real-ledger gate remains.
- #166 / LAB-087 — READY; SQLite schema-control trust boundary.
- #167 / LAB-088 — READY; threshold signer-noise robustness.
- #168 / LAB-089 — CLOSED `not_planned`.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — READY; mutable shared-anchor ordinary-DML writer authorization.
- PostgreSQL-specific validation and open-model serving remain deferred until representative runtime/hardware is available.
