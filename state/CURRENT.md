# Current Lab State

Last updated: 2026-08-26

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085 and LAB-087.
- Active priority: Issue #163 / LAB-086 — IN_PROGRESS.
- Branch: `lab/086-asymmetric-break-glass-history`; draft PR #165.
- Current observed PR HEAD: `95fa5da3c457e3431cd596ec969d5939b0a1d925`.
- Current published `migration_guard.py` blob: `1a9209b16fdb2c3dcae8e4690658a030040f6ca2`.
- LAB-088 / #167 remains IN_PROGRESS on draft PR #172.
- LAB-091 / #170 remains IN_PROGRESS on draft PR #173.

## Last completed step

Reconciled stale durable state with the actual PR branch. The pre-cutoff own-proof cardinality fix is already published in commit `95fa5da3c457e3431cd596ec969d5939b0a1d925`; the commit has exactly +20 lines and its patch is byte-for-byte the saved `research/2026-08-26-lab086-pre-cutoff-own-proof-cardinality.patch`. The prior handoff claim that the runtime still used blob `2ae3df...` and that candidate `7db4b53...` remained unpublished was stale and is superseded.

The published runtime now explicitly rejects any pre-cutoff rows in `provider_asymmetric_break_glass_proofs` or `provider_asymmetric_recovery_public_root_proofs`. A focused executable SQLite harness using the exact published method logic accepted a clean pre-cutoff state and rejected each orphan-proof table independently. This is focused semantic evidence only, not the full exact real-ledger regression.

A fresh branch/main compare reports `ahead 154 / behind 98`; all 59 PR paths are still additions relative to current main, so the observed divergence remains history/path-nonoverlapping rather than a demonstrated content conflict. PR #165 remains draft.

## Evidence retained

- Current published own-proof cardinality commit: `95fa5da3c457e3431cd596ec969d5939b0a1d925`.
- Commit patch stats: exactly 20 additions / 0 deletions to `migration_guard.py`; patch content matches the saved 20-line research patch.
- Current published `migration_guard.py` blob: `1a9209b16fdb2c3dcae8e4690658a030040f6ca2`.
- Focused semantic harness: clean state PASS; orphan break-glass proof BLOCKED; orphan public-recovery root proof BLOCKED.
- Exact lower-stack evidence remains LAB-080 18/18, LAB-082 28/28, LAB-083 24/24, LAB-084 17/17, LAB-085 core 12/12, asymmetric custody 8/8, public/final 11/11; lower unsafe baselines failed as expected.
- Standalone LAB-086 previously passed 12/12; unsafe legacy auto-promotion failed as intended.
- LAB-087 remains merged/DONE with exact 14/14 PASS + compileall.
- LAB-091 reference layer remains exact 11/11 PASS + compileall; published real integration still needs exact execution.

## Known blockers / constraints

- The LAB-086 publication blocker recorded in the previous handoff is resolved; do not attempt to republish `7db4b53...` over the current runtime.
- Remaining LAB-086 merge gate is execution, not publication: reconstruct exact current HEAD with LAB-080→085 dependencies and run the real-ledger cardinality, migration, suffix and final-supported/security suites together, then unsafe seed and compileall.
- Direct shell GitHub transport may be unavailable; GitHub connector exact reads remain the supported control-plane path.
- LAB-086 SQLite fences cover audited ordinary-DML/stale supported paths, not arbitrary same-privilege DDL/schema authority; LAB-087 owns that external boundary.
- LAB-090/#169 provider handoff freshness and LAB-091/#170 mutable shared-ledger writer authorization remain separate follow-ups.
- Logical SQL scrubbing is not forensic erasure; whole-store rollback freshness remains delegated to the external monotonic-anchor layer.

## Exact next action

1. Reconstruct the exact current PR #165 `migration_guard.py`, `suffix.py`, `final_supported.py` and their current tests on the already-proven LAB-080→085 dependency closure, verifying executable blobs by Git identity.
2. Execute `test_pre_cutoff_lab086_proof_cardinality.py`, lower-evidence cardinality, migration-guard, suffix, final-supported, cross-binding/history, inherited/direct-surface, strict-fence/thaw and restart/concurrency regressions from the same closure.
3. Run unsafe legacy-promotion seed and full compileall.
4. Perform one fresh final security audit and branch/main reconciliation; fix every blocking failure before ready/merge.
5. If exact closure reconstruction remains tool-limited, continue LAB-091 exact published-source execution and real restart/concurrency/UNKNOWN composition work without weakening the LAB-086 gate.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; own-proof cardinality fix is published; full current-head real-ledger execution gate remains.
- #166 / LAB-087 — DONE; merged as `65a44cc8d12cf37d04d9cd59398b456d7429cc31`.
- #167 / LAB-088 — IN_PROGRESS; draft PR #172.
- #168 / LAB-089 — CLOSED `not_planned`.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — IN_PROGRESS; draft PR #173 contains real supported-stack integration work.
