# Current Lab State

Last updated: 2026-08-27

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085 and LAB-087.
- Active priority: #163 / LAB-086 — IN_PROGRESS; draft PR #165, branch `lab/086-asymmetric-break-glass-history`.
- Current observed PR #165 HEAD: `bc2cd0fa80eae042cbab93e0f6fd02ad92521318`; draft=true; mergeable=true.
- Executable LAB-086 gate snapshot is pinned to `4570a19fb92f1222db64cb07f7e4ce6312630879`.
- LAB-088 / #167 remains IN_PROGRESS on draft PR #172.
- LAB-091 / #170 remains IN_PROGRESS on draft PR #173; fallback only while LAB-086 exact execution is concretely tool-limited.

## Last completed step

Corrected stale durable state after verifying the current PR and branch manifest.

The combined thaw identity hardening is already published in runtime `strict_fence.py` with Git blob `080eb9454437932a8ab419d66a4f2a69ed17c7ce` at executable commit `4570a19fb92f1222db64cb07f7e4ce6312630879`. Exact published regressions previously reconstructed and executed after publication:

- `test_strict_fence.py` `97048a325c4cc1ed78612bdbb4cfec42146a43f6`;
- `test_thaw_null_proof_key_regression.py` `fce5c57c8cfaa18f6761ae9b47c211813801aae0`;
- `test_thaw_history_key_collision_regression.py` `88ba35e933c123d10af65597d6bb51f4f11068ec`;
- `test_thaw_proof_replace_regression.py` `c511ccfc4b88b050910561b3b8f7e99be5f33e93`.

Result retained: **14/14 PASS + focused compileall PASS**. Existing and NULL identities are denied on every INSERT-thawed authenticated-history/proof surface; legitimate new unique non-NULL successor keys remain creatable by the verified final writer.

Compared executable pin `4570a19f...` to current branch HEAD `bc2cd0fa...`: the three later commits touch only research/manifest/staging cleanup. No executable or test bytes changed after the pin. Therefore the full gate may safely remain pinned to `4570a19f...`.

Direct shell GitHub transport was re-probed in this run and still fails DNS resolution. Connector exact reads/writes remain healthy. Issue #163 received a verification comment recording the corrected state.

## Evidence retained

- LAB-080 18/18 PASS.
- LAB-082 28/28 PASS.
- LAB-083 24/24 PASS.
- LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS.
- LAB-085 asymmetric custody 8/8 PASS.
- LAB-085 public/final 11/11 PASS.
- Lower unsafe baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; unsafe legacy auto-promotion failed as intended.
- Current published thaw/fence exact subgate: 14/14 PASS + compileall.
- Exact-gate manifest is `research/2026-08-27-lab086-exact-gate-manifest.md`, pinned to executable snapshot `4570a19f...`.
- PR #165 current HEAD `bc2cd0fa...` is three note/manifest-cleanup commits ahead of the executable pin only.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-091 retained evidence remains fallback only.

## Known blockers / constraints

- PR #165 must remain draft until the complete branch-local LAB-080→086 real-ledger execution gate is clean.
- Remaining gate: every normal LAB-086 real-schema test module from pinned snapshot, unsafe legacy-promotion seed separately, full compileall, then one fresh security/reconciliation audit and branch/main integration check.
- Direct shell/raw GitHub transport is unavailable; connector provides exact UTF-8 blobs but no repository archive/mount into the local executor. Reconstruction therefore remains file-by-file and expensive.
- Do not mix current `main` lower-layer files with the long-lived PR branch; use only exact blobs from executable snapshot `4570a19f...` and verify each local file with `git hash-object` before counting tests.
- LAB-090/#169 provider handoff freshness remains separate. Logical SQL scrubbing is not forensic erasure; whole-store rollback freshness remains delegated to the external monotonic-anchor layer.

## Exact next action

1. Reconstruct the minimal LAB-080→086 import/test closure from executable snapshot `4570a19fb92f1222db64cb07f7e4ce6312630879` using the exact blob identities in `research/2026-08-27-lab086-exact-gate-manifest.md`; verify every local file with `git hash-object`.
2. Execute every `test_*.py` under `experiments/asymmetric_break_glass_history/tests` from that pinned snapshot, including cardinality, migration/root-coauthorization/restart, scrubbed-prefix/suffix, orphan/partial-state, public-rotation cross-binding/history, inherited/direct-surface, final single-snapshot, thaw/collision and concurrency/rotation-race regressions.
3. Execute `unsafe_legacy_promotion_expected_failure.py` separately and require the intended failure; run full compileall over the reconstructed closure.
4. Perform one fresh security/reconciliation audit and branch/main compare. Fix every blocking failure before marking PR #165 ready or integrating it.
5. If exact reconstruction is concretely tool-limited in a run, continue LAB-091 real-stack fallback rather than weakening LAB-086 byte-integrity requirements.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; runtime combined thaw fix published and exact 14/14 subgate green; full pinned real-ledger gate remains.
- #166 / LAB-087 — DONE; merged as `65a44cc8d12cf37d04d9cd59398b456d7429cc31`.
- #167 / LAB-088 — IN_PROGRESS; draft PR #172.
- #168 / LAB-089 — CLOSED `not_planned`.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — IN_PROGRESS; fallback only while LAB-086 exact gate is tool-limited.
