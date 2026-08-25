# Current Lab State

Last updated: 2026-08-25

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085.
- Active: Issue #163 / LAB-086 — IN_PROGRESS.
- Branch: `lab/086-asymmetric-break-glass-history`.
- Draft PR: #165 `[LAB-086] Asymmetric break-glass proof migration`.
- Current observed PR HEAD: `c156d1145dc977dc0cc3c044f556d61b87613730`.
- PR remains draft/mergeable; full current-head real-ledger regression gate has not passed.

## Last completed step

Found and fixed another post-cutoff DML-boundary gap. The branch already contained `test_current_authority_dml_fence.py`, but `strict_fence.py` did not fence direct ordinary DML against current trust-state tables `provider_rotation_authorities`, `asymmetric_provider_generations`, `asymmetric_provider_head`, or `provider_rotation_threshold_enablement`.

A focused pre-fix execution reproduced both failures: direct successor-root INSERT succeeded, and an already authenticated root row remained UPDATE-mutable during the final-writer thaw.

The corrected policy splits current authority state:

- thawable only for the verified final writer: create next root authority, create next provider generation, move provider head;
- never thawed historical state: existing root authority rows, existing provider-generation rows, and threshold-enablement.

Published implementation commit `4f5bf750a0978616fe6b48b0bc683744ad2ad97a`; regression hardening commit `8b52d732f3640ebf657b3ea5048eb670526d6471`; research note commit/current HEAD `c156d1145dc977dc0cc3c044f556d61b87613730`.

## Evidence produced / reconfirmed

- Pre-fix focused current-authority regression: 0/2, both missing protections reproduced.
- Corrected local semantic-equivalent fence candidate: existing strict-fence + current-authority tests 12/12 PASS; compileall PASS.
- Additional conflict-algorithm probe: root authority/provider generation UPSERT and INSERT OR REPLACE, provider-head INSERT OR REPLACE, and threshold-enablement INSERT OR REPLACE were all blocked with original heads unchanged.
- Published `strict_fence.py` blob after fix: `1422f4435913cd95c37a38a0a62c2116f8e80476`.
- Published `test_current_authority_dml_fence.py` blob after conflict-algorithm additions: `b285b082eb1085f592481fd8751d82c79e7cc00f`.
- Implementation compare against prior branch HEAD: one file, +138/-4; fresh commit patch audit showed only the intended current-authority split/fence changes.
- Evidence boundary: the 12/12 focused run used a locally reconstructed semantic-equivalent copy; exact published current-head bytes still require execution in the full connector-reconstructed closure before merge.
- Lower-stack exact gate remains complete from prior observed runs: LAB-080 18/18, LAB-082 28/28, LAB-083 24/24, LAB-084 17/17, LAB-085 core 12/12, LAB-085 asymmetric-custody 8/8, LAB-085 public/final 11/11; lower unsafe baselines failed as expected.
- Existing LAB-086 evidence remains relevant: standalone 12/12; legacy projection DML freeze 4/4 exact; prior strict/inherited/root-head fence slices; orphan/pre-cutoff regressions; final single-snapshot contract; public-rotation cross-binding focused checks; unsafe legacy auto-promotion failed as intended.
- Issue #163 current-authority audit comment: `5408527364`.
- Direct shell GitHub transport remains unavailable; GitHub connector + Contents API are healthy and are the supported control-plane path.

## Known blockers / constraints

- Full current-head real-ledger gate is still mandatory after the new current-authority fence: execute exact published current-authority regression plus migration/root-coauthorization, scrubbed-prefix/asymmetric-suffix, orphan/partial-state, full lower/public-history guards, public-rotation cross-binding, direct-surface/fence cases and rotation races together.
- Focused semantic-equivalent evidence is not exact branch-byte execution and is not a merge gate substitute.
- LAB-086 SQLite fences cover audited ordinary DML/stale supported paths, not arbitrary same-privilege SQLite schema/DDL authority. That stronger trust boundary remains LAB-087/#166.
- LAB-083/LAB-084 signer-noise issue #167 remains separate fail-closed DoS/robustness work.
- Logical SQL scrubbing is not forensic erasure. Whole-store rollback freshness remains delegated to the external monotonic-anchor layer.

## Exact next action

1. Re-fetch PR #165 current HEAD and connector-reconstruct exact published `strict_fence.py` + `test_current_authority_dml_fence.py`; verify blob identities and execute that exact regression first.
2. Continue in the same dependency closure with all current-head LAB-086 real-ledger migration/suffix/final-supported tests, prioritizing migration v4 root coauthorization/restart, scrubbed-prefix + asymmetric suffix, orphan/partial state, full lower/public-history guards, public-rotation cross-binding, inherited/direct surfaces and rotation races.
3. Run unsafe legacy-promotion expected-failure seed and full `python -m compileall` over the complete closure.
4. Perform a fresh full security audit of all post-cutoff DML mutation points, consequential writers, restart verification and branch/main divergence. Keep PR #165 draft until all current-head tests are clean; only then mark ready and integrate.
5. Carry unrestricted SQL/DDL/schema-control work into LAB-087/#166 rather than overstating LAB-086's guarantee.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; current-authority DML gap fixed/published, full exact current-head real-ledger gate remains.
- #166 / LAB-087 — READY; SQLite schema-control trust boundary.
- #167 / LAB-088 — READY; threshold signer-noise robustness.
- #168 / LAB-089 — CLOSED `not_planned`.
- PostgreSQL-specific validation and open-model serving remain deferred until representative runtime/hardware is available.
