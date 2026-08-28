# Current Lab State

Last updated: 2026-08-28

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085 and LAB-087.
- Active priority: #163 / LAB-086 — IN_PROGRESS; draft PR #165, branch `lab/086-asymmetric-break-glass-history`.
- Current PR #165 HEAD after the latest evidence-only commit: `3cc63c2133507fd8d468471e1fe0fe5b3680e12c`.
- Last fully executed published runtime/test pin before the hidden-rowid blocker: `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`.
- Published runtime at that pin: `strict_fence.py` blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`.
- GitHub currently reports PR #165 draft/mergeable=true. Mergeability is not a security/test result.
- LAB-088 / #167 remains IN_PROGRESS on draft PR #172.
- LAB-091 / #170 remains IN_PROGRESS on draft PR #173; fallback only while LAB-086 exact work is concretely tool-limited.

## Last completed step

The hidden SQLite `rowid` REPLACE blocker now has exact executable RED→GREEN evidence.

Exact inputs were reconstructed locally and accepted only after `git hash-object` matched GitHub:
- predecessor `strict_fence.py`: `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`;
- regression `test_thaw_rowid_collision_regression.py`: `9773536e5c1627f2a01f13d45fcdcb7016aa7d08`.

Execution against the exact predecessor produced **RED 3/3**: all three tests failed because `IntegrityError` was not raised. This reproduces hidden-rowid replacement on:
1. INSERT-thawed authenticated public history;
2. transaction-thawed post-cutoff proof history;
3. append-only provider-receipt history.

The durable patch `research/2026-08-28-lab086-hidden-rowid-replace.patch` was applied programmatically to the exact predecessor bytes. The resulting candidate Git blob is:

`b78e7c98e35138719f77c482c7f1aab36b702de7`

The unchanged exact regression then produced **GREEN 3/3**, and focused compileall/py_compile passed. Positive append semantics remain intact: genuinely new history/proof/receipt identities are still insertable where the verified writer requires them.

Durable verification note:
- `research/2026-08-28-lab086-hidden-rowid-red-green-verification.md`;
- PR-branch evidence commit `3cc63c2133507fd8d468471e1fe0fe5b3680e12c`.

Runtime is intentionally still unpatched. The available GitHub Contents write requires resupplying the complete ~40 KB UTF-8 file and does not accept a local file reference. Direct local-file→connector byte transfer is unavailable. Manually reserializing the security-critical payload would weaken the established exact-blob discipline.

## Evidence retained

- LAB-080 18/18 PASS; LAB-082 28/28 PASS; LAB-083 24/24 PASS; LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS; asymmetric custody 8/8 PASS; public/final 11/11 PASS; lower unsafe baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; unsafe legacy auto-promotion failed as intended.
- Previous repinned LAB-086 strict/thaw exact subgate: **31/31 PASS + compileall** on pin `1fa85a0e...`; it is not sufficient for merge because hidden-rowid conflict was not covered.
- Hidden-rowid exact RED→GREEN: predecessor **RED 3/3**, candidate `b78e7c98...` **GREEN 3/3 + compileall**.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-091 adoption validator exact published-source 5/5 PASS + compileall; PR #173 remains draft and still requires full real LAB-080/LAB-082 supported-surface integration tests.

## Known blockers / constraints

- LAB-086 remains first priority. Hidden-rowid fix must be published byte-exact before the full real-ledger gate resumes.
- Affected policy includes INSERT-thawed authenticated-history tables, post-cutoff proof creation surfaces and `asymmetric_provider_receipts` append-only history.
- Direct shell/raw GitHub transport remains unavailable. Connector reads are byte-exact but file-by-file and do not mount ordinary repository files into the local executor.
- A reconstructed file counts as execution evidence only if `git hash-object` equals the GitHub blob.
- Do not manually transcribe/rewrite the large security-critical `strict_fence.py` without a byte-identity checkpoint.
- PR #165 must remain draft until rowid fix publication, repinned strict/thaw subgate, complete real-ledger gate, unsafe seed, compileall and final audit are all clean.
- LAB-090/#169 provider handoff freshness remains separate.

## Exact next action

1. Obtain a byte-safe transfer path for the exact candidate `b78e7c98e35138719f77c482c7f1aab36b702de7` into `experiments/asymmetric_break_glass_history/strict_fence.py` on PR #165.
2. Publish only if the branch still has predecessor blob `d4a6a40f...` and GitHub returns exactly candidate blob `b78e7c98...`; otherwise stop and reconcile bytes before counting evidence.
3. Re-fetch/hash-verify the published runtime, execute exact `test_thaw_rowid_collision_regression.py` plus the complete strict/thaw conflict subgate and compileall, and repin only after green evidence.
4. Resume the complete branch-local LAB-080→086 real-ledger modules, unsafe legacy-promotion expected-failure seed, full compileall and final security/reconciliation audit.
5. Use LAB-091 fallback only if exact LAB-086 publication/execution is concretely tool-limited again; next LAB-091 gate is full real LAB-080/LAB-082 two-worker/crash/UNKNOWN supported-surface execution.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; hidden-rowid blocker has exact RED→GREEN candidate evidence; byte-exact runtime publication is next.
- #166 / LAB-087 — DONE; merged as `65a44cc8d12cf37d04d9cd59398b456d7429cc31`.
- #167 / LAB-088 — IN_PROGRESS; draft PR #172.
- #168 / LAB-089 — CLOSED `not_planned`.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — IN_PROGRESS; draft PR #173; fallback only while LAB-086 is tool-limited.
