# Current Lab State

Last updated: 2026-08-26

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085 and LAB-087.
- Active priority: Issue #163 / LAB-086 — IN_PROGRESS; draft PR #165, branch `lab/086-asymmetric-break-glass-history`.
- Current observed PR #165 HEAD: `95fa5da3c457e3431cd596ec969d5939b0a1d925`; mergeable=false; 59 changed files.
- Current published `migration_guard.py` blob: `1a9209b16fdb2c3dcae8e4690658a030040f6ca2`.
- LAB-088 / #167 remains IN_PROGRESS on draft PR #172.
- LAB-091 / #170 remains IN_PROGRESS on draft PR #173.

## Last completed step

Re-read AGENTS.md, this state and SELF_RESUME.md; inspected current PR #165. LAB-086 remains draft and its required exact current-head real-ledger closure is still not fully reconstructed in this runtime. Exact connector reads confirm the published own-proof cardinality guard is present and `test_pre_cutoff_lab086_proof_cardinality.py` targets both LAB-086 proof tables. No test result was fabricated from source inspection.

Per the recorded fallback, advanced LAB-091's known RED merge blocker. Added a standalone connection-local one-shot operation permit primitive to PR #173. The permit binds `(operation kind, identity, expected old value, expected new value)`, requires an active SQL transaction, is consumed by the guarding trigger before row mutation, cannot authorize a second statement, and is cleared on unused/error paths.

Published exact artifacts:
- `experiments/mutable_shared_anchor_writer/operation_permit.py`: commit `2024407d350ea9b0c7d07bcdba814e2bada70bc3`, blob `637784a5cb61a024a1df3e0e983887b6d0a838be`;
- `experiments/mutable_shared_anchor_writer/tests/test_operation_permit_primitive.py`: commit `570112b4ce5b3340e8ee639350011d47dd509851`, blob `b410a5111542db23a80fcb2645a65c6b4e96c80d`.

Exact-source local reconstruction matched both published Git blobs via `git hash-object`. The primitive suite ran 6/6 PASS and compileall PASS. Tests prove: unpermitted DML blocked; exact transition allowed; different new value blocked; permit consumed after one statement; failed statement does not leave authority; permit cannot exist outside an active transaction.

This closes only the permit primitive. PR #173 remains DRAFT because `real_integration.py` still uses transaction-wide `lab091_writer_authorized()` and must be migrated to one-shot permits for actual reserve/confirm/watermark/receipt statements.

## Evidence retained

- LAB-086 published own-proof cardinality commit: `95fa5da3c457e3431cd596ec969d5939b0a1d925`; current blob `1a9209b16fdb2c3dcae8e4690658a030040f6ca2`.
- Focused LAB-086 cardinality semantics retained: clean PASS; orphan break-glass proof BLOCKED; orphan public-root proof BLOCKED. Full real-ledger gate still outstanding.
- Exact lower-stack evidence remains LAB-080 18/18, LAB-082 28/28, LAB-083 24/24, LAB-084 17/17, LAB-085 core 12/12, asymmetric custody 8/8, public/final 11/11; lower unsafe baselines failed as expected.
- Standalone LAB-086 previously 12/12 PASS; unsafe legacy auto-promotion failed as intended.
- LAB-087 remains merged/DONE with exact 14/14 PASS + compileall.
- LAB-091 reference layer remains exact 11/11 PASS + compileall; unsafe raw-DML seed failed as intended.
- LAB-091 one-shot permit primitive exact published-source gate: 6/6 PASS + compileall; blobs `637784a5...` and `b410a511...` matched local execution exactly.
- Prior LAB-091 counterexample remains relevant to old integration: transaction-wide boolean authority allowed meta and watermark jumps to 999.

## Known blockers / constraints

- Remaining LAB-086 merge gate is exact execution: reconstruct current HEAD with LAB-080→085 dependencies and run real-ledger cardinality + migration + suffix + final-supported/security suites, unsafe seed and compileall.
- PR #165 currently reports mergeable=false; do not reconcile/integrate until the complete current-head security/test gate is clean.
- LAB-091 real integration still has transaction-wide boolean writer authority. The new one-shot primitive is proven but not yet wired into real reserve/confirm/watermark/receipt DML; PR #173 must remain draft.
- LAB-091 exact published integration execution and restart/concurrency/crash/UNKNOWN/LAB-087 composition gates remain outstanding.
- Direct shell GitHub may remain unavailable; connector exact reads/writes are the control-plane fallback.
- LAB-086 SQLite fences cover audited ordinary-DML/stale supported paths, not arbitrary same-privilege DDL/schema authority; LAB-087 owns that boundary.
- LAB-090/#169 provider handoff freshness remains separate.
- Logical SQL scrubbing is not forensic erasure; whole-store rollback freshness remains delegated to the external monotonic-anchor layer.

## Exact next action

1. LAB-086 remains first priority: connector-reconstruct exact current PR #165 `migration_guard.py`, `suffix.py`, `final_supported.py` and tests on the proven LAB-080→085 closure; execute own/lower cardinality, migration, suffix, final-supported, cross-binding/history, inherited/direct-surface, strict-fence/thaw, restart/concurrency tests; then unsafe seed + full compileall + final audit.
2. If exact closure reconstruction remains tool-limited, wire LAB-091 `operation_permit.py` into `real_integration.py`: replace transaction-wide boolean guards with operation-specific trigger calls and install a one-shot permit immediately around each reserve intent INSERT, meta CAS, receipt INSERT, confirmation UPDATE, and watermark INSERT/UPDATE. Make the existing RED operation-scoped regression green.
3. Then run exact published LAB-091 real-stack restart/concurrency/crash/UNKNOWN and LAB-087 composition tests. Keep PR #165 and PR #173 draft until their complete gates are clean.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; own-proof cardinality fix published; full current-head real-ledger execution gate remains.
- #166 / LAB-087 — DONE; merged as `65a44cc8d12cf37d04d9cd59398b456d7429cc31`.
- #167 / LAB-088 — IN_PROGRESS; draft PR #172.
- #168 / LAB-089 — CLOSED `not_planned`.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — IN_PROGRESS; one-shot permit primitive exact 6/6 PASS, but real integration still uses broad boolean authority; draft PR #173.
