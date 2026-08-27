# Current Lab State

Last updated: 2026-08-27

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085 and LAB-087.
- Active priority: #163 / LAB-086 — IN_PROGRESS; draft PR #165, branch `lab/086-asymmetric-break-glass-history`.
- Current observed PR #165 HEAD: `968fc36f3423964786f8b9e44ded838bbd55c9c1`; draft=true, mergeable=true.
- Current LAB-086 runtime `strict_fence.py` remains blob `5da01e28a9f813a136d138637f855940f04aab46`; thaw/REPLACE blocker is not yet fixed in runtime.
- LAB-088 / #167 remains IN_PROGRESS on draft PR #172.
- LAB-091 / #170 remains IN_PROGRESS on draft PR #173; latest branch commit in this run `d8ed5ea12d705d10f9b2de16ab78bf82eabcae27` adds focused UNKNOWN/retry coverage.

## Last completed step

Resumed LAB-086 first. Reconfirmed the current thaw/REPLACE blocker and exact staged artifacts: RED regression `test_thaw_proof_replace_regression.py` blob `c511ccfc4b88b050910561b3b8f7e99be5f33e93`, research note, and staged patch `research/2026-08-27-lab086-thaw-proof-replace-bypass.patch` blob `d55ded03d8a73f51caf84f1d5085e56b31172a5a`. The required fix keeps a permanent existing-key collision trigger for both post-cutoff proof tables while only the blanket new-key creation deny is removed during verified thaw.

Tried an additional safe bulk-reconstruction path before falling back: container download of a GitHub commit archive and the GitHub REST zipball endpoint. Both are unavailable in this runtime. The connector still returns exact blobs/files, but no archive/mount or line-patch endpoint exists; the only runtime write path for the ~34 KB `strict_fence.py` remains whole-file Contents replacement. No risky manual rewrite was performed and no LAB-086 PASS was claimed.

Per the recorded fallback, advanced LAB-091 UNKNOWN semantics. Added `test_timeout_unknown_convergence.py` to PR #173. Its published blob `0111e30eb73c91c0a0d91e942556a8f718df5bd8` exactly matches the locally executed test bytes. The harness uses exact branch LAB-036 `anchor_attestation/protocol.py` blob `15d8b7cf8ff093490ccb75679030d3a0fe41e401` and exact `convergent_operation_scoped.py` blob `7fe0d682c0be4c6388799dd6b8a6ba87f65dda3`; only the lower SQL parent/confirmation persistence is stubbed.

Focused executed result: 1/1 PASS + compileall PASS. Scenario: provider increment commits, the first post-timeout reconciliation path is unavailable, execute returns `PendingIntent`, provider position remains advanced exactly once, and retry converges the same request to CONFIRMED without a second increment (`increment_calls == 1`). This is focused exact-source evidence, not the remaining full LAB-080/LAB-082 supported-surface gate.

## Evidence retained

- LAB-086 lower-stack exact evidence: LAB-080 18/18, LAB-082 28/28, LAB-083 24/24, LAB-084 17/17, LAB-085 core 12/12, asymmetric custody 8/8, public/final 11/11; lower unsafe baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; unsafe legacy auto-promotion failed as intended.
- New LAB-086 thaw/REPLACE RED regression exact blob `c511ccfc...`; runtime fix still pending.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-091 retained exact evidence: one-shot primitive 6/6; mutable-row guards + legacy persistence 12/12; v3 state-machine; v4 deterministic/history binding 9/9; restart 3/3; single-pending 2/2; process concurrency/crash 2/2; LAB-087 composition 2/2.
- New LAB-091 focused UNKNOWN/retry regression: exact published test blob `0111e30e...`, exact LAB-036 + exact convergent source, 1/1 PASS + compileall; retry after commit-then-lost-reconcile does not re-increment.

## Known blockers / constraints

- **LAB-086 merge blocker:** during transaction-scoped proof-creation thaw, SQLite `INSERT OR REPLACE` can overwrite an existing authenticated proof key because the blanket proof INSERT deny is temporarily removed and default `recursive_triggers=OFF` does not reliably route REPLACE through DELETE triggers.
- PR #165 must remain draft until permanent no-replace collision triggers are installed for both proof tables, the new regression is green on exact published runtime, and the complete post-fix real-ledger gate is clean.
- Connector exact reads work, but no repository archive/mount or patch-application write endpoint is exposed. Whole-file security-critical rewrites require exact source reconstruction and post-write diff/hash audit.
- Never count manually reformatted/transcribed files as exact evidence.
- LAB-091 still needs the full real LAB-080/LAB-082 supported-surface two-worker same-request and timeout/UNKNOWN gate; the new 1/1 test is focused evidence only.
- LAB-090/#169 provider handoff freshness remains separate.
- Logical SQL scrubbing is not forensic erasure; whole-store rollback freshness remains delegated to the external monotonic-anchor layer.

## Exact next action

1. LAB-086 first: obtain/reconstruct exact `strict_fence.py` blob `5da01e28a9f813a136d138637f855940f04aab46`, apply staged patch `d55ded03...`, and publish only via a byte/diff-auditable Contents update. Re-fetch and verify that the file diff contains only permanent proof-key collision triggers plus fence assertion requirements.
2. Execute exact `test_thaw_proof_replace_regression.py`, `test_transaction_scoped_thaw_minimality.py`, `test_post_cutoff_evidence_dml_fence.py`, `test_post_cutoff_evidence_insert_authorization.py`, and `test_strict_fence.py` on the published runtime.
3. Repin the executable snapshot, regenerate the full LAB-086 test inventory, run the complete branch-local LAB-080→086 normal suite, unsafe seed, compileall and final security audit; only then reconcile/merge #165.
4. If byte-safe LAB-086 publication is still tool-limited, continue LAB-091 with the full real supported surface: two workers sharing one request and timeout-after-commit/UNKNOWN reconciliation with actual LAB-080/LAB-082 persistence, then re-audit restart/reentrancy.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; thaw `INSERT OR REPLACE` blocker remains RED; runtime fix pending.
- #166 / LAB-087 — DONE; merged as `65a44cc8d12cf37d04d9cd59398b456d7429cc31`.
- #167 / LAB-088 — IN_PROGRESS; draft PR #172.
- #168 / LAB-089 — CLOSED `not_planned`.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — IN_PROGRESS; focused UNKNOWN retry convergence now proven, full real supported-surface gate remains.
