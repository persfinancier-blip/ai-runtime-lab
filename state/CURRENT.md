# Current Lab State

Last updated: 2026-08-27

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085 and LAB-087.
- Active priority: #163 / LAB-086 — IN_PROGRESS; draft PR #165, branch `lab/086-asymmetric-break-glass-history`.
- Current observed PR #165 HEAD: `81ebb8157cae872230e986ec4131384bc62cd137`; draft=true, mergeable=true.
- Pinned executable snapshot for the remaining exact gate: `3d22efc4c562103e8b0bc18fb8f99559411b55fc`.
- Current LAB-086 runtime `strict_fence.py` blob: `cea0ca3b42723790971ba9415b70a7e9fa0c7368`; thaw/REPLACE blocker is fixed in runtime.
- LAB-088 / #167 remains IN_PROGRESS on draft PR #172.
- LAB-091 / #170 remains IN_PROGRESS on draft PR #173; focused UNKNOWN/retry evidence from branch commit `d8ed5ea12d705d10f9b2de16ab78bf82eabcae27` remains retained.

## Last completed step

Resolved the LAB-086 thaw/REPLACE blocker using a byte/diff-auditable whole-file Contents update from exact old blob `5da01e28a9f813a136d138637f855940f04aab46`.

Published runtime commit `3d22efc4c562103e8b0bc18fb8f99559411b55fc` changes only `experiments/asymmetric_break_glass_history/strict_fence.py`; compare against prior HEAD `968fc36...` is exactly +16/-0 lines. The GitHub commit patch exactly matches staged research patch `research/2026-08-27-lab086-thaw-proof-replace-bypass.patch` (`d55ded03...`).

Each post-cutoff proof table now gets a permanent existing-key/no-replace BEFORE INSERT trigger. Verified final writers may still remove the ordinary proof-creation deny trigger to insert a new unique proof key, but the permanent collision trigger is never removed by transaction-scoped thaw. `assert_public_mutation_fence_locked()` requires those permanent triggers.

Focused post-publication SQLite execution confirmed for both `provider_asymmetric_break_glass_proofs` and `provider_asymmetric_recovery_public_root_proofs`: `INSERT OR REPLACE` existing key BLOCKED, UPSERT-existing BLOCKED, original evidence unchanged, and insertion of a new unique proof key succeeds during legitimate thaw. This is focused semantic evidence, not the full exact real-ledger gate.

The exact-gate manifest was repinned to executable snapshot `3d22efc4...` and strict-fence blob `cea0ca3b...`; manifest-only/current branch HEAD is `81ebb815...`. PR #165 description and Issue #163 were updated to the same facts.

## Evidence retained

- LAB-086 lower-stack exact evidence: LAB-080 18/18, LAB-082 28/28, LAB-083 24/24, LAB-084 17/17, LAB-085 core 12/12, asymmetric custody 8/8, public/final 11/11; lower unsafe baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; unsafe legacy auto-promotion failed as intended.
- Thaw/REPLACE RED regression exact blob: `c511ccfc4b88b050910561b3b8f7e99be5f33e93`.
- Published thaw fix: commit `3d22efc4...`, runtime blob `cea0ca3b...`, diff exactly +16/-0 matching staged patch.
- Focused post-publication SQLite semantics: existing proof REPLACE/UPSERT blocked for both proof tables; new unique proof creation during thaw succeeds.
- `research/2026-08-27-lab086-exact-gate-manifest.md` now pins executable snapshot `3d22efc4...`.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-091 retained exact evidence: one-shot primitive 6/6; mutable-row guards + legacy persistence 12/12; v3 state-machine 6/6; v4 deterministic/history binding 9/9; restart 3/3; single-pending 2/2; process concurrency/crash 2/2; LAB-087 composition 2/2.
- LAB-091 focused UNKNOWN/retry regression retained: exact published test blob `0111e30e...`, exact LAB-036 + exact convergent source, 1/1 PASS + compileall; retry after commit-then-lost-reconcile does not re-increment.

## Known blockers / constraints

- LAB-086 remains first priority. The thaw/REPLACE runtime blocker is fixed, but PR #165 must remain draft until the complete post-fix exact branch-local LAB-080→086 execution gate is clean.
- Full gate must use one coherent executable snapshot `3d22efc4...`; every reconstructed local file must match its pinned Git blob via `git hash-object` before execution.
- Connector exact reads work, but no repository archive/mount exists and direct shell/raw GitHub transport remains unavailable; reconstruction remains file-by-file.
- The new thaw run is focused semantic evidence, not yet the exact full-module/closure regression result.
- LAB-091 still needs the full real LAB-080/LAB-082 supported-surface two-worker same-request and timeout/UNKNOWN gate; retained focused evidence is not the final integration gate.
- LAB-090/#169 provider handoff freshness remains separate.
- Logical SQL scrubbing is not forensic erasure; whole-store rollback freshness remains delegated to the external monotonic-anchor layer.

## Exact next action

1. LAB-086 first: reconstruct the minimal branch-local import closure from executable snapshot `3d22efc4...` using exact Git blob SHAs in the updated manifest; verify every local file with `git hash-object` before execution.
2. Execute exact `test_thaw_proof_replace_regression.py` first on published `strict_fence.py`, then `test_transaction_scoped_thaw_minimality.py`, `test_post_cutoff_evidence_dml_fence.py`, `test_post_cutoff_evidence_insert_authorization.py`, `test_strict_fence.py`, and the remainder of every normal LAB-086 real-schema module.
3. Execute the complete current migration/root coauthorization/restart, cardinality, scrubbed-prefix/suffix, orphan/partial-state, public-rotation cross-binding/history, inherited/direct-surface, DML-fence, final single-snapshot and concurrency/rotation-race regressions.
4. Execute `unsafe_legacy_promotion_expected_failure.py` separately and require intended failure; run full `python -m compileall`; perform final security audit plus branch/main reconciliation/conflict check.
5. Keep PR #165 draft until this entire gate is clean; only then mark ready/integrate. If exact reconstruction is concretely tool-limited after progress, fallback to LAB-091 full supported-worker concurrency/UNKNOWN integration without weakening LAB-086 acceptance criteria.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; thaw `INSERT OR REPLACE` blocker fixed in runtime, full exact post-fix gate remains.
- #166 / LAB-087 — DONE; merged as `65a44cc8d12cf37d04d9cd59398b456d7429cc31`.
- #167 / LAB-088 — IN_PROGRESS; draft PR #172.
- #168 / LAB-089 — CLOSED `not_planned`.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — IN_PROGRESS; focused UNKNOWN retry convergence proven, full real supported-surface gate remains.
