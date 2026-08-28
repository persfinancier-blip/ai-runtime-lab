# Current Lab State

Last updated: 2026-08-28

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085 and LAB-087.
- Active priority: #163 / LAB-086 — IN_PROGRESS; draft PR #165, branch `lab/086-asymmetric-break-glass-history`.
- Current PR #165 HEAD: `5887eb79da5a13d2beb03ee8b846d64efb9328bd`.
- Last fully executed runtime/test pin before the new blocker: `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`.
- Published runtime at that pin: `strict_fence.py` blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`.
- GitHub reports PR #165 draft/mergeable=true. Mergeability is not a test/security result.
- LAB-088 / #167 remains IN_PROGRESS on draft PR #172.
- LAB-091 / #170 remains IN_PROGRESS on draft PR #173, current HEAD `9bee235bb65efaae6feaa971518b27405bf85151`; fallback only while LAB-086 exact work is concretely tool-limited.

## Last completed step

LAB-086 remains blocked by the hidden SQLite `rowid` REPLACE class found after the previously clean 31/31 strict/thaw subgate.

The permanent collision fences protect declared PK/UNIQUE identities, but affected tables are ordinary SQLite rowid tables. During transaction-scoped thaw, `INSERT OR REPLACE` can target an existing hidden `rowid` while presenting a fresh declared key. With default `recursive_triggers=OFF`, the implicit REPLACE delete is not stopped by the ordinary DELETE trigger.

Durable RED regression:
- `experiments/asymmetric_break_glass_history/tests/test_thaw_rowid_collision_regression.py`, blob `9773536e5c1627f2a01f13d45fcdcb7016aa7d08`;
- it covers public history during thaw, post-cutoff proof history during thaw, and append-only provider receipts.

Durable fix artifacts:
- `research/2026-08-28-lab086-hidden-rowid-replace.md`;
- `research/2026-08-28-lab086-hidden-rowid-replace.patch`, staged in current HEAD `5887eb79da5a13d2beb03ee8b846d64efb9328bd`.

Fresh source/lifecycle audit of that staged patch found no additional omission:
- rowid collision/sentinel triggers remain installed during transaction-scoped thaw;
- full reinstall cleanup enumerates the new sentinels and install paths recreate them;
- post-cutoff proof sentinels remain during trusted proof-creation thaw;
- provider-receipt sentinel is part of the receipt trigger set;
- `assert_public_mutation_fence_locked()` will require all rowid sentinels;
- exact asymmetric-provider schemas confirm generation/transition/receipt tables are ordinary rowid tables and do not declare a `rowid` column that would shadow SQLite's hidden rowid.

This is source/lifecycle audit evidence only. Runtime `strict_fence.py` remains unpatched at blob `d4a6a40f...`; the RED regression and repinned execution gate are still required.

While exact LAB-086 connector-to-local reconstruction remained concretely tool-limited, fallback LAB-091 advanced. A fresh adoption audit found that v2/v3/v4 triggers constrain only future DML: preexisting non-deterministic LAB-080 request IDs or authenticated receipts orphaned from all shared-anchor intents could otherwise be grandfathered on first LAB-091 adoption. The final candidate now validates those LAB-091-only invariants inside the same `BEGIN IMMEDIATE` transaction that installs persistent guards.

LAB-091 exact published-source evidence from this run:
- `operation_permit.py` `637784a5cb61a024a1df3e0e983887b6d0a838be`;
- `state_machine_udfs.py` `8c1d6d0cd075285aed3a90ac337b60b60c1d608b`;
- `adoption_validation.py` `d96c5656273cdfd42250ccd55456c10110eb4a20`;
- `test_adoption_validation.py` `1a5b397a05d61845ca183cf476ee32db5e8def3c`;
- final wiring `history_bound_operation_scoped.py` `4bdf64fa714cbe0d5598ac9a702dd60edd97a112`;
- focused adoption suite **5/5 PASS + compileall PASS** after local `git hash-object` matched all executed published files.
- Research: `research/2026-08-28-lab091-adoption-state-validation.md`.

## Evidence retained

- LAB-080 18/18 PASS; LAB-082 28/28 PASS; LAB-083 24/24 PASS; LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS; asymmetric custody 8/8 PASS; public/final 11/11 PASS; lower unsafe baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; unsafe legacy auto-promotion failed as intended.
- Previous repinned LAB-086 strict/thaw exact subgate: 31/31 PASS + compileall on pin `1fa85a0e...`; it is no longer sufficient for merge because hidden-rowid conflict was not covered.
- Focused hidden-rowid RED counterexample executed and reproduced replacement; focused rowid-safe mechanism produced the desired block/allow behavior.
- LAB-086 staged rowid patch lifecycle/source audit found no new blocker, but runtime remains unpatched.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-091 adoption validator exact published-source 5/5 PASS + compileall; PR #173 remains draft and still requires full real LAB-080/LAB-082 supported-surface integration tests.

## Known blockers / constraints

- LAB-086 remains first priority. Hidden-rowid REPLACE bypass must be fixed before full real-ledger gate resumes.
- Affected policy includes INSERT-thawed authenticated-history tables, post-cutoff proof creation surfaces and `asymmetric_provider_receipts` append-only history.
- Direct shell/raw GitHub transport remains unavailable. Connector reconstruction is byte-exact but file-by-file and does not mount ordinary repository files into the local executor.
- A reconstructed file counts as execution evidence only if `git hash-object` equals the pinned Git blob.
- Do not manually transcribe/rewrite the large security-critical `strict_fence.py` without byte identity checks.
- PR #165 must remain draft until rowid fix, repinned strict/thaw subgate, complete real-ledger gate, unsafe seed, compileall and final audit are all clean.
- LAB-090/#169 provider handoff freshness remains separate.

## Exact next action

1. Reconstruct/hash-verify current `strict_fence.py` and apply staged rowid-safe patch from exact bytes to:
   - thawed authenticated-history collision fences;
   - post-cutoff proof no-replace fences;
   - provider-receipt append-only no-replace fence.
2. Publish only if the resulting Git blob matches the locally tested candidate bytes.
3. Execute/hash-verify `test_thaw_rowid_collision_regression.py` plus the complete strict/thaw conflict subgate and compileall; repin the executable snapshot only after green evidence.
4. Then resume complete branch-local LAB-080→086 real-ledger modules, unsafe legacy-promotion expected-failure seed, full compileall and final security/reconciliation audit.
5. Use LAB-091 fallback only if exact LAB-086 reconstruction/execution is concretely tool-limited again; next LAB-091 gate is the full real LAB-080/LAB-082 two-worker/crash/UNKNOWN supported-surface execution.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; hidden-rowid REPLACE blocker RED and durable; staged rowid patch lifecycle audited; exact runtime patch next.
- #166 / LAB-087 — DONE; merged as `65a44cc8d12cf37d04d9cd59398b456d7429cc31`.
- #167 / LAB-088 — IN_PROGRESS; draft PR #172.
- #168 / LAB-089 — CLOSED `not_planned`.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — IN_PROGRESS; draft PR #173; adoption grandfathering fixed with exact 5/5 + compileall; full real-stack concurrency/UNKNOWN gate remains; fallback only while LAB-086 is tool-limited.
