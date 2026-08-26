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

Re-read AGENTS.md, this state and SELF_RESUME.md and re-inspected PR #165. LAB-086 remains first priority and draft; its exact current-head LAB-080→086 real-ledger closure is still outstanding, so no merge/readiness claim was made.

Per the recorded fallback, advanced LAB-091's known transaction-wide writer-authority blocker. Added an operation-scoped guard layer on PR #173 using the already-published one-shot permit primitive. `operation_permit_guards.py` replaces broad authorization semantics for the meta-tail and component-watermark surfaces with triggers that consume an exact `(kind, identity, old, new)` permit. A transaction without a permit cannot mutate those rows.

Published exact artifacts:
- `experiments/mutable_shared_anchor_writer/operation_permit_guards.py`: commit `65ee18274dd9f81f505335bbdbdf368f8e70c617`, blob `773dd331f5d7f76cf1a79ef7b80c630a80dfa9b3`;
- `experiments/mutable_shared_anchor_writer/tests/test_operation_permit_guards.py`: commit `7b6134ddc74ba5c3e955647a3cb4c611d248f1e6`, blob `af1823815f2bc73c2b9fb6f94b811fbe7a4e7688`.

Local reconstruction hashes matched both published blobs. Focused exact guard suite ran 6/6 PASS; compileall PASS. It proves: broad transaction cannot jump meta 0→999; exact meta CAS works and does not authorize a second statement; broad transaction cannot jump watermark 1→999; exact watermark insert/update permits work; wrong new values fail and do not leave authority behind.

An attempted combined run also named the prior primitive test module without reconstructing that test file in this runtime, causing one unittest loader error. That missing-module error is recorded and is not counted as a product regression; the newly published guard suite itself is 6/6 green.

## Evidence retained

- LAB-086 published own-proof cardinality commit: `95fa5da3c457e3431cd596ec969d5939b0a1d925`; current blob `1a9209b16fdb2c3dcae8e4690658a030040f6ca2`.
- Focused LAB-086 cardinality semantics retained: clean PASS; orphan break-glass proof BLOCKED; orphan public-root proof BLOCKED. Full real-ledger gate still outstanding.
- Exact lower-stack evidence remains LAB-080 18/18, LAB-082 28/28, LAB-083 24/24, LAB-084 17/17, LAB-085 core 12/12, asymmetric custody 8/8, public/final 11/11; lower unsafe baselines failed as expected.
- Standalone LAB-086 previously 12/12 PASS; unsafe legacy auto-promotion failed as intended.
- LAB-087 remains merged/DONE with exact 14/14 PASS + compileall.
- LAB-091 reference layer remains exact 11/11 PASS + compileall; unsafe raw-DML seed failed as intended.
- LAB-091 one-shot permit primitive exact published-source gate remains 6/6 PASS + compileall; blobs `637784a5...` and `b410a511...`.
- LAB-091 operation-scoped meta/watermark guard layer exact published-source gate: 6/6 PASS + compileall; blobs `773dd331...` and `af182381...`.
- Prior LAB-091 counterexample remains relevant to old `real_integration.py`: transaction-wide boolean authority allowed meta and watermark jumps to 999.

## Known blockers / constraints

- Remaining LAB-086 merge gate is exact execution: reconstruct current HEAD with LAB-080→085 dependencies and run real-ledger cardinality + migration + suffix + final-supported/security suites, unsafe seed and compileall.
- PR #165 currently reports mergeable=false; do not reconcile/integrate until the complete current-head security/test gate is clean.
- LAB-091 `real_integration.py` still uses transaction-wide `lab091_writer_authorized()`. The one-shot primitive and meta/watermark guard layer are proven separately but not yet wired into the actual reserve/confirm/watermark/receipt statements; PR #173 remains draft.
- LAB-091 still needs operation-scoped guards for intent creation/confirmation and provider-receipt creation, followed by exact real-stack restart/concurrency/crash/UNKNOWN and LAB-087 composition gates.
- Direct shell GitHub may remain unavailable; connector exact reads/writes are the control-plane fallback.
- LAB-086 SQLite fences cover audited ordinary-DML/stale supported paths, not arbitrary same-privilege DDL/schema authority; LAB-087 owns that boundary.
- LAB-090/#169 provider handoff freshness remains separate.
- Logical SQL scrubbing is not forensic erasure; whole-store rollback freshness remains delegated to the external monotonic-anchor layer.

## Exact next action

1. LAB-086 remains first priority: connector-reconstruct exact current PR #165 `migration_guard.py`, `suffix.py`, `final_supported.py` and tests on the proven LAB-080→085 closure; execute own/lower cardinality, migration, suffix, final-supported, cross-binding/history, inherited/direct-surface, strict-fence/thaw, restart/concurrency tests; then unsafe seed + full compileall + final audit.
2. If exact closure reconstruction remains tool-limited, continue LAB-091 operation-scoped integration: add exact one-shot triggers for intent INSERT/PREPARED→CONFIRMED and receipt INSERT, then replace `_authorized_txn()`'s boolean authority in `real_integration.py` with transaction-only scope plus `one_shot_permit()` immediately around each actual DML statement (intent INSERT, meta CAS, receipt INSERT, confirmation UPDATE, watermark INSERT/UPDATE). Make `test_operation_scoped_permit_regression.py` green without granting transaction-wide authority.
3. Then run exact published LAB-091 real-stack restart/concurrency/crash/UNKNOWN and LAB-087 composition tests. Keep PR #165 and PR #173 draft until their complete gates are clean.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; own-proof cardinality fix published; full current-head real-ledger execution gate remains.
- #166 / LAB-087 — DONE; merged as `65a44cc8d12cf37d04d9cd59398b456d7429cc31`.
- #167 / LAB-088 — IN_PROGRESS; draft PR #172.
- #168 / LAB-089 — CLOSED `not_planned`.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — IN_PROGRESS; one-shot permit primitive exact 6/6 PASS and meta/watermark guard layer exact 6/6 PASS, but real integration still uses broad boolean authority; draft PR #173.
