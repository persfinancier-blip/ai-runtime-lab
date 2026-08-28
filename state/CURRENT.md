# Current Lab State

Last updated: 2026-08-28

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085 and LAB-087.
- Active priority: #163 / LAB-086 — IN_PROGRESS; draft PR #165, branch `lab/086-asymmetric-break-glass-history`.
- Current PR #165 HEAD: `3cc63c2133507fd8d468471e1fe0fe5b3680e12c`; GitHub currently reports draft/mergeable=true. Mergeability is not a security/test result.
- Last fully executed published runtime/test pin before the hidden-rowid blocker: `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`.
- Published runtime at that pin: `strict_fence.py` blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`.
- LAB-088 / #167 remains IN_PROGRESS on draft PR #172.
- LAB-091 / #170 remains IN_PROGRESS on draft PR #173; fallback only while LAB-086 exact work is concretely tool-limited.

## Last completed step

Revalidated the hidden SQLite `rowid` fix from exact branch bytes in a fresh runtime.

The preferred checkout path was probed first and remains unavailable: direct `git clone https://github.com/...` fails with `Could not resolve host: github.com`. Connector reconstruction was therefore used rather than assuming shell/raw network access.

Exact predecessor `strict_fence.py` was reconstructed from connector line ranges and accepted only after `git hash-object` returned exactly:

`d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`

`py_compile` passed. The durable patch `research/2026-08-28-lab086-hidden-rowid-replace.patch` was then applied programmatically to those exact bytes. The result again hashes exactly to the retained candidate:

`b78e7c98e35138719f77c482c7f1aab36b702de7`

`py_compile` also passed on the candidate. This independently reproduces the previously recorded exact `d4a6a40f... -> b78e7c98...` transition.

Fresh source audit found no new candidate blocker: rowid sentinel triggers are included in reinstall/assert trigger sets, transaction-scoped thaw does not remove them, explicit existing-rowid collisions are rejected before insert, and the reserved SQLite `NEW.rowid == -1` ambiguity is fail-closed by AFTER INSERT sentinels. Existing alternate `(provider_id,generation)` collision protection remains present for provider generations.

Runtime is intentionally still unpatched. The normal Contents API update available in this runtime accepts a complete UTF-8 text payload but not a local file reference, while direct GitHub network transport is unavailable. Low-level ref/tree manipulation and manual reserialization of the ~40 KB security-critical payload were not used.

Issue #163 comment `5447258459` records this fresh revalidation and tool observation.

## Evidence retained

- LAB-080 18/18 PASS; LAB-082 28/28 PASS; LAB-083 24/24 PASS; LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS; asymmetric custody 8/8 PASS; public/final 11/11 PASS; lower unsafe baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; unsafe legacy auto-promotion failed as intended.
- Previous repinned LAB-086 strict/thaw exact subgate: **31/31 PASS + compileall** on pin `1fa85a0e...`; it is not sufficient for merge because hidden-rowid conflict was not covered.
- Hidden-rowid exact RED→GREEN retained: predecessor **RED 3/3**, candidate `b78e7c98...` **GREEN 3/3 + compileall**.
- This run independently hash-reconstructed predecessor `d4a6a40f...` and candidate `b78e7c98...`; both compiled successfully. This is byte-transition/audit evidence, not publication evidence.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-091 adoption validator exact published-source 5/5 PASS + compileall; PR #173 remains draft and still requires full real LAB-080/LAB-082 supported-surface integration tests.

## Known blockers / constraints

- LAB-086 remains first priority. Hidden-rowid fix must be published byte-exact before the full real-ledger gate resumes.
- Affected policy includes INSERT-thawed authenticated-history tables, post-cutoff proof creation surfaces and `asymmetric_provider_receipts` append-only history.
- Direct shell/raw GitHub transport remains unavailable. Connector reads are byte-exact but file-by-file and do not mount ordinary repository files into the local executor.
- The available Contents write cannot consume the exact local candidate file by reference; manually transcribing/reformatting the large security-critical file would weaken the established exact-blob discipline.
- A reconstructed file counts as execution evidence only if `git hash-object` equals the GitHub blob.
- PR #165 must remain draft until rowid fix publication, repinned strict/thaw subgate, complete real-ledger gate, unsafe seed, compileall and final audit are all clean.
- LAB-090/#169 provider handoff freshness remains separate.

## Exact next action

1. Obtain a byte-safe supported transfer path for exact candidate `b78e7c98e35138719f77c482c7f1aab36b702de7` into `experiments/asymmetric_break_glass_history/strict_fence.py` on PR #165.
2. Publish only if the branch still has predecessor blob `d4a6a40f...` and GitHub returns exactly candidate blob `b78e7c98...`; otherwise stop and reconcile bytes before counting evidence.
3. Re-fetch/hash-verify published runtime, execute exact `test_thaw_rowid_collision_regression.py` plus the complete strict/thaw conflict subgate and compileall, and repin only after green evidence.
4. Resume the complete branch-local LAB-080→086 real-ledger modules, unsafe legacy-promotion expected-failure seed, full compileall and final security/reconciliation audit.
5. While publication is concretely tool-limited, LAB-091 fallback may continue with the full real LAB-080/LAB-082 two-worker/crash/UNKNOWN supported-surface execution; focused stub tests do not satisfy that gate.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; hidden-rowid blocker has exact RED→GREEN candidate evidence and fresh independent byte-transition revalidation; byte-exact runtime publication is next.
- #166 / LAB-087 — DONE; merged as `65a44cc8d12cf37d04d9cd59398b456d7429cc31`.
- #167 / LAB-088 — IN_PROGRESS; draft PR #172.
- #168 / LAB-089 — CLOSED `not_planned`.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — IN_PROGRESS; draft PR #173; fallback only while LAB-086 is tool-limited.
