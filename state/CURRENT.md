# Current Lab State

Last updated: 2026-08-25

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085.
- Active: Issue #163 / LAB-086 — IN_PROGRESS.
- Branch: `lab/086-asymmetric-break-glass-history`.
- Draft PR: #165 `[LAB-086] Asymmetric break-glass proof migration`.
- Current observed branch HEAD: `76f37534cad26531284442e06d4a170bd4a8cad4`.
- PR is open/draft and currently reported non-mergeable; runtime `strict_fence.py` still has the broad thaw.

## Last completed step

The LAB-086 least-privilege thaw fix remains technically ready but could not be safely published in this runtime. Exact branch `strict_fence.py` was re-read as blob `02128fb866d7b4a3382622356f33e7b1739ff167`; the durable patch `research/2026-08-25-lab086-minimal-thaw.patch` still targets that exact blob and the previously tested candidate hash remains `5da01e28a9f813a136d138637f855940f04aab46`.

Direct shell GitHub transport was probed again and failed DNS resolution. The available GitHub connector can replace an existing file only by supplying the complete UTF-8 file body; `strict_fence.py` is large enough that reconstructing/re-emitting it manually would weaken the byte-exact publication guarantee. No risky rewrite was attempted and no publication/test PASS was fabricated.

Because LAB-086 publication is tool-interface blocked rather than design blocked, useful parallel work advanced LAB-087/#166. Primary SQLite/Python documentation was reviewed and the trust-boundary decision was persisted at `research/2026-08-25-lab087-sqlite-authorizer-boundary.md` (main commit `f004f824ff91820c74e69bdafb060061363dc1d2`). SQLite `set_authorizer` is connection-scoped and replaceable/disableable, so it is defense-in-depth, not a database-file security boundary. The selected outer boundary is broker/process + writable-handle/file ownership; restricted worker connections may additionally use an authorizer to deny DDL and consequential DML.

## Evidence produced / reconfirmed

- Exact current LAB-086 runtime blob: `strict_fence.py` `02128fb866d7b4a3382622356f33e7b1739ff167`.
- Exact durable minimal-thaw patch still present at `research/2026-08-25-lab086-minimal-thaw.patch`.
- Previously tested candidate blob remains `5da01e28a9f813a136d138637f855940f04aab46`, with prior focused 13/13 evidence; it is **not yet published runtime code**.
- Direct `git ls-remote https://github.com/...` in this runtime failed with `Could not resolve host: github.com`; connector reads/writes work.
- LAB-087 primary-source conclusion: SQLite authorizer is per connection, one authorizer replaces another, NULL disables it, and action codes include DROP TRIGGER/INSERT/UPDATE/DELETE/ALTER/ATTACH/DETACH. Therefore arbitrary same-privilege writable connections remain outside what authorizer/triggers alone can secure.
- LAB-087 research note committed on main: `f004f824ff91820c74e69bdafb060061363dc1d2`; Issue #166 updated with the selected design and next implementation slice.
- Cumulative exact lower-stack evidence remains: LAB-080 18/18, LAB-082 28/28, LAB-083 24/24, LAB-084 17/17, LAB-085 core 12/12, asymmetric-custody 8/8, public/final 11/11; lower unsafe baselines failed as intended.

## Known blockers / constraints

- LAB-086 runtime minimal-thaw fix is not yet published. Do not claim candidate blob `5da01e28...` is branch runtime until the repository returns that exact content SHA.
- Current connector exposes whole-file replacement but no line-patch/file-upload operation for an existing UTF-8 file; direct shell GitHub transport is unavailable in this run. Safe publication therefore remains blocked unless a byte-exact whole-file transfer can be performed.
- After publication, exact branch minimal-thaw + strict-fence tests must be rerun before the full real-ledger migration/suffix/final-supported gate.
- LAB-087/#166 design is selected but implementation/regressions remain.
- LAB-088/#167 signer-noise; LAB-090/#169 provider handoff freshness; LAB-091/#170 mutable shared-anchor/new-receipt DML authorization remain READY.
- Logical SQL scrubbing is not forensic erasure; whole-store rollback freshness remains delegated to the external monotonic-anchor layer.

## Exact next action

1. On the next runtime that offers a safe byte-exact write path, apply `research/2026-08-25-lab086-minimal-thaw.patch` to exact blob `02128fb8...`; accept publication only if returned blob is exactly `5da01e28a9f813a136d138637f855940f04aab46`.
2. Run exact `test_transaction_scoped_thaw_minimality.py` plus the complete strict-fence regression set.
3. Resume exact current-head real-ledger LAB-086 migration/suffix/final-supported suite, unsafe legacy-promotion seed, full compileall and final security audit; only then ready/merge PR #165.
4. If LAB-086 publication remains tool-blocked, continue LAB-087 implementation: restricted-connection authorizer regressions + explicit unrestricted-connection negative control + broker-owned writable-handle contract.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; minimal-thaw candidate tested but runtime publication remains safely blocked by current write interface.
- #166 / LAB-087 — READY; primary-source design decision now recorded: broker/process/file ownership is the outer boundary, SQLite authorizer is defense-in-depth.
- #167 / LAB-088 — READY; threshold signer-noise robustness.
- #168 / LAB-089 — CLOSED `not_planned`.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — READY; mutable/shared-ledger plus new provider-receipt ordinary-DML writer authorization.
- PostgreSQL-specific validation and open-model serving remain deferred until representative runtime/hardware is available.
