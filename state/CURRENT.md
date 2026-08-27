# Current Lab State

Last updated: 2026-08-27

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085 and LAB-087.
- Active priority: #163 / LAB-086 — IN_PROGRESS; draft PR #165, branch `lab/086-asymmetric-break-glass-history`.
- Pinned executable/runtime/test snapshot for the remaining LAB-086 gate: `95fa5da3c457e3431cd596ec969d5939b0a1d925`.
- Current PR #165 branch HEAD: `5a1709fbe11f1a8e162280c393ba66d778c7f3b0`; post-snapshot change is the non-executable exact-gate manifest.
- PR #165 remains draft; full exact LAB-080→086 real-ledger execution gate remains outstanding.
- LAB-088 / #167 remains IN_PROGRESS on draft PR #172.
- LAB-091 / #170 remains IN_PROGRESS on draft PR #173; current observed HEAD `a380ada41494807cf4a30a3594cc314b4f3072ce`, draft.

## Last completed step

Resumed LAB-086 first. Re-read the pinned exact-gate manifest and current exact `migration_guard.py`, `strict_fence.py`, `suffix.py` and `final_supported.py`. No new confirmed LAB-086 privilege-escalation/stale-supported-writer blocker was established in this audit. The full execution gate is still tool-limited because connector reads exact blobs but no safe repository archive/export exists, while direct shell/raw GitHub transport remains unavailable. No manual/nonmatching reconstruction was counted as evidence.

Used the documented fallback on LAB-091 and found a real state-machine gap. The v3 SQL intent guard required exact-next tail/current provider but did not enforce the LAB-080 single-pending invariant. A focused executable counterexample committed `intent-1` PREPARED at position 1, advanced the durable tail to 1, then successfully committed `intent-2` PREPARED at position 2 while the first request was unresolved. The supported `reserve()` API explicitly rejects this state.

Fixed `cross_table_guards.py` so a new intent INSERT is denied whenever any existing `shared_anchor_intents.status='PREPARED'` row exists. Added `test_single_prepared_guard.py` proving the second PREPARED is blocked at the exact next tail while a new reservation becomes legal after the prior intent is CONFIRMED.

Published exact blobs:
- `operation_permit.py` `637784a5cb61a024a1df3e0e983887b6d0a838be`;
- updated `cross_table_guards.py` `fe7696e27ba29a1f1fd090279ebd1082810de78b`;
- `test_single_prepared_guard.py` `78fc440552855c900a6aa633e7bcdb16546ea154`.

All three locally reconstructed files matched `git hash-object` exactly. Exact published-source regression: **2/2 PASS**; compileall PASS. Research note `research/2026-08-27-lab091-single-pending-invariant.md` and Issue #170/PR #173 were updated.

## Evidence retained

- LAB-086 lower-stack exact evidence: LAB-080 18/18, LAB-082 28/28, LAB-083 24/24, LAB-084 17/17, LAB-085 core 12/12, asymmetric custody 8/8, public/final 11/11; lower unsafe baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; unsafe legacy auto-promotion failed as intended.
- Current LAB-086 exact test inventory: 29 normal modules + one unsafe seed from the pinned executable tree; no new full-stack PASS claimed in this run.
- Key LAB-086 blobs remain `migration_guard.py` `1a9209b...`, `strict_fence.py` `5da01e28...`, `suffix.py` `44847bde...`, `final_supported.py` `ceb7f48a...`.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-091 retained exact evidence: one-shot primitive 6/6; full mutable-row guards + legacy persistence 12/12; v3 state-machine 8/8; v4 deterministic/history binding 9/9; v4 restart persistence 3/3; latest single-pending SQL invariant **2/2 PASS + compileall** on exact published blobs.

## Known blockers / constraints

- LAB-086 remains first priority. Merge gate is exact execution on one coherent branch-local LAB-080→086 closure: all 29 normal LAB-086 modules, unsafe seed, compileall and final audit. Do not reconcile/integrate before that gate is clean.
- Direct shell/raw GitHub transport cannot establish a connection; connector exact blob reads remain healthy but expose no repository archive/export. Reconstruction is file-by-file unless a later runtime exposes byte-safe bulk transport.
- Never count manually reformatted/transcribed files as exact evidence; hash mismatch means discard the run.
- LAB-091 final candidate still needs execution against real LAB-080/LAB-082 for two actual concurrent workers sharing one request, crash rollback, timeout/UNKNOWN reconciliation and LAB-087 restricted-worker composition. The SQL trigger layer now additionally preserves the single-PREPARED invariant.
- LAB-090/#169 provider handoff freshness remains separate.
- Logical SQL scrubbing is not forensic erasure; whole-store rollback freshness remains delegated to the external monotonic-anchor layer.

## Exact next action

1. LAB-086 first: use `research/2026-08-27-lab086-exact-gate-manifest.md` and connector exact blob reads to reconstruct the pinned executable snapshot byte-for-byte; verify every file with `git hash-object` before import.
2. Execute all 29 normal LAB-086 real-schema modules, then unsafe legacy-promotion seed separately, full compileall and fresh security audit; only then reconcile/merge PR #165.
3. If exact LAB-086 reconstruction remains tool-limited, continue LAB-091 real-stack execution. Next fallback target: two actual workers sharing one request and crash rollback on `SupportedHistoryBoundOperationScopedAsymmetricSharedAnchorLedger`, then timeout/UNKNOWN and LAB-087 composition.
4. Keep PR #165 and PR #173 draft until their complete real-stack gates are clean.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact gate manifest durable, full branch-local execution gate remains.
- #166 / LAB-087 — DONE; merged as `65a44cc8d12cf37d04d9cd59398b456d7429cc31`.
- #167 / LAB-088 — IN_PROGRESS; draft PR #172.
- #168 / LAB-089 — CLOSED `not_planned`.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — IN_PROGRESS; single-pending SQL invariant fixed/exact-tested, real LAB-080/LAB-082 integration gate remains.
