# Current Lab State

Last updated: 2026-08-25

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085.
- Active: Issue #163 / LAB-086 — IN_PROGRESS.
- Branch: `lab/086-asymmetric-break-glass-history`.
- Draft PR: #165 `[LAB-086] Asymmetric break-glass proof migration`.
- Current observed branch HEAD after this run: `a1bcd89bb8b7fd0f6d981673afc8b25e13816e66`.
- PR remains draft; full current-head real-ledger migration/suffix/final-supported regression gate has not passed.

## Last completed step

Applied the previously staged post-cutoff evidence-DML fence to the real branch runtime through the supported GitHub Contents API. The write produced branch commit `a1bcd89bb8b7fd0f6d981673afc8b25e13816e66` and runtime `strict_fence.py` blob `34ba1db9c5aa04fc55c3842d73d5ceff92964b55`.

The published blob did not initially equal the locally pre-tested candidate `6992a55a1dcc61f4b2f066ff1844f68a7c9610be`. Investigation showed exactly one byte-layout difference: the published file omits one blank line immediately before `_install_post_cutoff_evidence_freeze_locked()`. No semantic/code-token difference was found. Rather than rewriting again or reusing the prior test evidence, the published branch bytes were reconstructed and executed directly.

Exact published `strict_fence.py` plus exact branch `test_strict_fence.py` (`4b651db3638c8b9f2341d52b512f075c4b3c31d2`) and `test_post_cutoff_evidence_dml_fence.py` (`a8509be97bd1f10ae87d7a733827f3475e8ee9e6`) passed **12/12**. Focused compileall also passed. These tests cover UPDATE, DELETE, `INSERT OR REPLACE`, and UPSERT corruption attempts against committed `provider_asymmetric_break_glass_proofs` and `provider_asymmetric_recovery_public_root_proofs`; original evidence remains unchanged.

Fresh source audit of current `migration_guard.py` (`5a5bb928b39a96f93f019b103b483dfb9bf43c6d`), `suffix.py` (`44847bde53b9f7b0e2fbcbab37d36dc992f497b2`) and `final_supported.py` (`9f0198d2db85d08ec64f614d6288323c1d642383`) found no new privilege-escalation path. Public-recovery root proof is cross-bound to the actual Ed25519 transition by exact predecessor/root/intent, and final consequential writers retain full preverification -> transaction-scoped thaw -> mutation -> refreeze/assert -> postverification before commit.

Started rebuilding the current-run real dependency workspace using connector-sourced implementation bytes. LAB-036/080 and LAB-082 implementation files reconstructed so far are checked by Git blob where complete; direct shell GitHub transport is still unavailable. The complete LAB-080→085 local closure was not finished in this run, so no new full real-ledger PASS is claimed.

## Evidence produced / reconfirmed

- Branch runtime post-fix: `strict_fence.py` blob `34ba1db9c5aa04fc55c3842d73d5ceff92964b55`.
- Branch-exact focused regression: **12/12 PASS**; focused compileall PASS.
- Issue #163 current-run evidence comment: `5411243840`.
- Fresh branch/main compare after branch write: `ahead 118 / behind 63`; all 45 PR paths remain additions, so no path-level content collision with current `main` is observed.
- Lower-stack exact evidence remains complete from prior runs: LAB-080 18/18, LAB-082 28/28, LAB-083 24/24, LAB-084 17/17, LAB-085 core 12/12, LAB-085 asymmetric-custody 8/8, LAB-085 public/final 11/11; lower unsafe baselines failed as intended.
- Exact standalone LAB-086 corrected suite remains 12/12 PASS; unsafe legacy-auto-promotion seed failed as intended.
- Direct shell GitHub transport was probed again and is unavailable; GitHub connector/Contents API are working supported fallbacks and are not owner blockers.

## Known blockers / constraints

- The post-cutoff evidence-DML blocker itself is now fixed and branch-exact tested; do not repeat that work unless a later regression invalidates it.
- Remaining merge gate is the full current-head real-ledger `migration_guard + suffix + final_supported` suite on the proven LAB-080→085 implementation closure, then unsafe seed, full compileall, and final security audit.
- Local dependency reconstruction is per-run and not durable. Connector reconstruction works but is slower than a normal checkout.
- SQLite fences cover audited ordinary DML/stale supported paths, not arbitrary same-privilege SQLite schema/DDL authority; LAB-087/#166 owns that stronger boundary.
- LAB-083/LAB-084 signer-noise robustness remains LAB-088/#167 and is fail-closed availability work.
- Logical SQL scrubbing is not forensic erasure; whole-store rollback freshness remains delegated to the external monotonic-anchor layer.

## Exact next action

1. Continue the connector-sourced local dependency closure from the already reconstructed LAB-036/080/082 implementation: add exact LAB-083/084/085 implementation bytes and verify every completed file by Git blob identity.
2. Re-fetch PR #165 HEAD before execution. Reconstruct exact current `migration_guard.py`, `suffix.py`, `final_supported.py` and all real-ledger tests. Execute migration v4/root coauthorization/restart, scrubbed-prefix/asymmetric-suffix, orphan/partial state, full lower/public-history guards, public-rotation cross-binding, inherited/direct surfaces, final verification snapshot and rotation races.
3. Execute unsafe legacy-promotion seed + full compileall over the reconstructed closure.
4. Perform a fresh full security audit of every consequential/restart path and a new branch/main divergence check. Fix every blocking failure. Only after a clean current-head gate may PR #165 be marked ready and integrated.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; post-cutoff evidence-DML fix is now in branch runtime and branch-exact 12/12 PASS; full real-ledger gate remains.
- #166 / LAB-087 — READY; SQLite schema-control trust boundary.
- #167 / LAB-088 — READY; threshold signer-noise robustness.
- #168 / LAB-089 — CLOSED `not_planned`.
- PostgreSQL-specific validation and open-model serving remain deferred until representative runtime/hardware is available.
