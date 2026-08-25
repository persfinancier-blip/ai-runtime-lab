# Current Lab State

Last updated: 2026-08-25

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085.
- Active: Issue #163 / LAB-086 — IN_PROGRESS.
- Branch: `lab/086-asymmetric-break-glass-history`.
- Draft PR: #165 `[LAB-086] Asymmetric break-glass proof migration`.
- Current observed PR HEAD: `ced3d62304a8ac6164834fbcc54d276f30dd8a07`.
- PR remains draft. The new provider-receipt DML regression/patch is durable, but runtime `strict_fence.py` has not yet received that patch and the full current-head real-ledger gate has not passed.

## Last completed step

Fresh table-by-table lower-history audit found one additional ordinary-DML omission in LAB-086. LAB-082 `asymmetric_provider_receipts` is append-only Ed25519 evidence and is mandatory during `IntegratedAsymmetricProviderHistory._verify_durable_locked`: every stored receipt is re-authenticated and its `stable_binding` is checked, while CONFIRMED shared-anchor rows bind to the exact receipt. Current LAB-086 `strict_fence.py` does not protect this table, so raw UPDATE/DELETE/INSERT OR REPLACE/UPSERT of an existing receipt can turn a valid database into persistent fail-closed state on the next final writer/restart.

A focused executable SQLite policy probe established the intended minimal rule: existing receipt UPDATE/DELETE/REPLACE/UPSERT are blocked, while INSERT of a new distinct request_id remains allowed. This preserves normal post-cutoff receipt creation.

Durable branch artifacts now exist:
- red regression `experiments/asymmetric_break_glass_history/tests/test_provider_receipt_dml_fence.py`, commit `d63babb9e0bb49d5f72c17c330ecc15ee0b4840f`;
- exact intended patch `research/2026-08-25-lab086-provider-receipt-dml-fence.patch`, commit/current branch HEAD `ced3d62304a8ac6164834fbcc54d276f30dd8a07`.

Important evidence boundary: branch runtime `strict_fence.py` is still blob `34ba1db9c5aa04fc55c3842d73d5ceff92964b55`; the saved patch is not yet applied. Do not count the new regression as passing until the runtime blob changes and exact-source tests are executed.

The audit also confirmed that the broader mutable `shared_anchor_meta`, `shared_anchor_intents`, and `component_anchor_watermarks` problem cannot be solved by blanket immutability because supported runtime must continue reserve/confirm/watermark transitions. That narrower ordinary-DML writer-authorization problem is now LAB-091 / Issue #170. Arbitrary same-privilege DDL/schema control remains LAB-087 / #166.

## Evidence produced / reconfirmed

- Focused SQLite provider-receipt fence probe: UPDATE BLOCKED; DELETE BLOCKED; INSERT OR REPLACE BLOCKED; UPSERT-existing BLOCKED; new distinct request INSERT PASS.
- Issue #170 / LAB-091 created for mutable shared-anchor SQL writer authorization.
- Issue #163 and PR #165 updated with the provider-receipt finding and exact evidence boundary.
- Current PR HEAD observed after durable artifacts: `ced3d62304a8ac6164834fbcc54d276f30dd8a07`; draft=true, mergeable=true at last read.
- Fresh branch/main compare before the two new branch commits: `ahead 124 / behind 66`; all then-existing LAB-086 paths were additions with no path-level overlap with main. Re-check after applying the runtime patch.
- Existing exact lower-stack evidence remains: LAB-080 18/18, LAB-082 28/28, LAB-083 24/24, LAB-084 17/17, LAB-085 core 12/12, LAB-085 asymmetric-custody 8/8, LAB-085 public/final 11/11; lower unsafe baselines failed as intended.
- Exact standalone LAB-086 corrected suite remains 12/12 PASS; unsafe legacy-auto-promotion seed failed as intended.

## Known blockers / constraints

- Immediate blocker: provider-receipt DML patch is durable but not applied to runtime `strict_fence.py`; the new real regression is therefore expected to fail on current branch code.
- Remaining merge gate after that fix: full exact current-head real-ledger execution of `migration_guard + suffix + final_supported`, then unsafe seed, full compileall and final security audit.
- Direct shell GitHub transport is unavailable in this run; connector reads/writes work and remain the supported fallback.
- LAB-090/#169 is separate fail-closed external-provider handoff freshness work, not a LAB-086 privilege escalation.
- LAB-088/#167 is separate fail-closed threshold signer-noise robustness.
- LAB-087/#166 owns arbitrary same-privilege SQLite DDL/schema control.
- LAB-091/#170 owns mutable shared-anchor ordinary-DML writer authorization; do not claim LAB-086 immutable history fences solve that runtime ledger boundary.
- Logical SQL scrubbing is not forensic erasure; whole-store rollback freshness remains delegated to the external monotonic-anchor layer.

## Exact next action

1. Fetch exact current branch `strict_fence.py` and require base blob `34ba1db9c5aa04fc55c3842d73d5ceff92964b55`; apply `research/2026-08-25-lab086-provider-receipt-dml-fence.patch` through a byte-controlled supported path. Verify the published result by Git blob identity.
2. Execute exact `test_strict_fence.py + test_provider_receipt_dml_fence.py`; fix every failure. The corrected policy must keep a new distinct receipt insertable while making an existing receipt immutable/non-deletable/non-replaceable.
3. Reconstruct/execute all remaining current-head LAB-086 real-schema migration/suffix/final-supported tests on the exact LAB-080→085 dependency closure.
4. Run unsafe legacy-promotion seed and full compileall.
5. Perform final security audit plus fresh branch/main divergence/conflict check. Only after a clean current-head gate may PR #165 be marked ready and integrated.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; provider-receipt DML blocker found; regression+patch durable, runtime fix pending.
- #166 / LAB-087 — READY; SQLite schema-control trust boundary.
- #167 / LAB-088 — READY; threshold signer-noise robustness.
- #168 / LAB-089 — CLOSED `not_planned`.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — READY; mutable shared-anchor ordinary-DML writer authorization.
- PostgreSQL-specific validation and open-model serving remain deferred until representative runtime/hardware is available.
