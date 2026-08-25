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

Closed the exact-source evidence gap for the latest current-authority DML fence. The post-cutoff policy now separates thawable final-writer operations from historical trust state: the verified final writer may create the next root/provider rows and move provider head, while existing root/provider rows and threshold-enablement remain immutable even during transaction-scoped thaw.

Published implementation commit `4f5bf750a0978616fe6b48b0bc683744ad2ad97a`; regression hardening `8b52d732f3640ebf657b3ea5048eb670526d6471`; research note/current branch HEAD `c156d1145dc977dc0cc3c044f556d61b87613730`.

## Evidence produced / reconfirmed

- Pre-fix focused current-authority regression: 0/2; direct successor-root INSERT and historical root UPDATE during thaw were both reproduced.
- Exact connector-reconstructed published implementation blob: `strict_fence.py` `1422f4435913cd95c37a38a0a62c2116f8e80476`; local `git hash-object` matched exactly.
- Exact connector-reconstructed published regression blob: `test_current_authority_dml_fence.py` `b285b082eb1085f592481fd8751d82c79e7cc00f`; local `git hash-object` matched exactly.
- Exact published current-authority regression: **3/3 PASS**.
- Exact cases cover ordinary INSERT/UPDATE/DELETE, `INSERT OR REPLACE`/UPSERT conflict algorithms, and final-writer thaw while historical root/provider rows + threshold-enablement remain frozen.
- Focused compileall of the exact reconstructed LAB-086 package: PASS.
- Implementation compare against prior branch HEAD was one file, +138/-4; fresh commit patch audit found only the intended current-authority split/fence changes.
- Issue #163 exact-evidence comment: `5408586992`.
- Lower-stack exact gate remains complete from prior observed runs: LAB-080 18/18, LAB-082 28/28, LAB-083 24/24, LAB-084 17/17, LAB-085 core 12/12, LAB-085 asymmetric-custody 8/8, LAB-085 public/final 11/11; lower unsafe baselines failed as expected.
- Existing LAB-086 evidence remains relevant: standalone 12/12; legacy projection DML freeze 4/4 exact; prior strict/inherited/root-head fence slices; orphan/pre-cutoff regressions; final single-snapshot contract; public-rotation cross-binding focused checks; unsafe legacy auto-promotion failed as intended.
- Direct shell GitHub transport remains unavailable; GitHub connector + Contents API are healthy and remain the supported control-plane path.

## Known blockers / constraints

- Full current-head real-ledger gate remains mandatory: migration/root-coauthorization, scrubbed-prefix/asymmetric-suffix, orphan/partial-state, full lower/public-history guards, public-rotation cross-binding, direct-surface/fence cases and rotation races must execute together on the supported ledger.
- The latest current-authority fix no longer has an exact-byte evidence gap; remaining blockers are only the broader current-head real-ledger suite + unsafe seed + full compileall + final audit.
- LAB-086 SQLite fences cover audited ordinary DML/stale supported paths, not arbitrary same-privilege SQLite schema/DDL authority. That stronger trust boundary remains LAB-087/#166.
- LAB-083/LAB-084 signer-noise issue #167 remains separate fail-closed DoS/robustness work.
- Logical SQL scrubbing is not forensic erasure. Whole-store rollback freshness remains delegated to the external monotonic-anchor layer.

## Exact next action

1. Continue the existing connector-reconstructed dependency closure with all current-head LAB-086 real-ledger migration/suffix/final-supported tests, prioritizing migration v4 root coauthorization/restart, scrubbed-prefix + asymmetric suffix, orphan/partial state, full lower/public-history guards, public-rotation cross-binding, inherited/direct surfaces and rotation races.
2. Run unsafe legacy-promotion expected-failure seed and full `python -m compileall` over the complete closure.
3. Perform a fresh full security audit of all post-cutoff DML mutation points, consequential writers, restart verification and branch/main divergence.
4. Keep PR #165 draft until every current-head real-ledger test is clean; only then mark ready and integrate.
5. Carry unrestricted SQL/DDL/schema-control work into LAB-087/#166 rather than overstating LAB-086's guarantee.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; current-authority DML fix now has exact 3/3 evidence; full current-head real-ledger gate remains.
- #166 / LAB-087 — READY; SQLite schema-control trust boundary.
- #167 / LAB-088 — READY; threshold signer-noise robustness.
- #168 / LAB-089 — CLOSED `not_planned`.
- PostgreSQL-specific validation and open-model serving remain deferred until representative runtime/hardware is available.
