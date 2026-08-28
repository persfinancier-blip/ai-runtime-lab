# Current Lab State

Last updated: 2026-08-28

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085 and LAB-087.
- Active priority: #163 / LAB-086 — IN_PROGRESS; draft PR #165, branch `lab/086-asymmetric-break-glass-history`.
- Current PR #165 HEAD: `3cc63c2133507fd8d468471e1fe0fe5b3680e12c`; GitHub reports mergeable=false.
- Last fully executed published LAB-086 runtime/test pin before the hidden-rowid blocker: `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`; published `strict_fence.py` blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`.
- Hidden-rowid candidate remains `b78e7c98e35138719f77c482c7f1aab36b702de7`; runtime is intentionally still unpatched until byte-safe publication is possible.
- LAB-088 / #167 remains IN_PROGRESS on draft PR #172.
- LAB-091 / #170 remains IN_PROGRESS on draft PR #173; current HEAD `5c1a3487cb53b7abbdb601e65b97e9b9724717f5`, mergeable=true, draft. Use only as fallback while LAB-086 exact work is concretely tool-limited.

## Last completed step

Probed LAB-086 first. Direct shell/raw GitHub transport still fails in this runtime because GitHub hostnames cannot resolve. Connector reads remain exact but ordinary repository blobs are not mounted into the local executor, so the ~40 KB security-critical `strict_fence.py` hidden-rowid candidate was not manually reserialized and no LAB-086 PASS was fabricated.

Used the allowed LAB-091 fallback for a fresh constructor/adoption audit. The final `SupportedHistoryBoundOperationScopedAsymmetricSharedAnchorLedger` inherits `SupportedMutableAsymmetricSharedAnchorLedger.__init__()`, whose order is lower construction -> dynamic `self._install_guards()` -> `self.verify_durable()`. Therefore final v2/v3/v4 persistent guards are committed before the complete lower LAB-082 cryptographic/history verifier runs.

A focused file-backed SQLite mechanism reproduction confirmed the side effect: install/commit persistent guard -> verification failure left the guard present after reopen; verify-before-install rejected the same invalid state with no trigger persisted. This is mechanism/source evidence, not an exact real-stack regression.

Recorded the finding in `research/2026-08-28-lab091-adoption-verification-ordering.md`, PR #173 commit `5c1a3487cb53b7abbdb601e65b97e9b9724717f5`, and Issue #170 comment `5448755103`. Runtime was intentionally not reordered without an exact real LAB-080/LAB-082 regression.

## Evidence retained

- LAB-080 18/18 PASS; LAB-082 28/28 PASS; LAB-083 24/24 PASS; LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS; asymmetric custody 8/8 PASS; public/final 11/11 PASS; lower unsafe baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; unsafe legacy auto-promotion failed as intended.
- Previous repinned LAB-086 strict/thaw exact subgate: 31/31 PASS + compileall on pin `1fa85a0e...`; not sufficient for merge because hidden-rowid conflict was not covered.
- Hidden-rowid exact RED→GREEN retained: predecessor RED 3/3, candidate `b78e7c98...` GREEN 3/3 + compileall; runtime publication still pending.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-091 adoption-state/domain gate: 23/23 PASS + compileall.
- LAB-091 alternate lower/legacy connection persistence regression: exact published 2/2 PASS + compileall, blob `365688e0...`.
- LAB-091 adoption-verification ordering: source audit + focused file-backed SQLite reproduction establishes non-atomic failed-adoption side effect; exact real-stack regression still required before runtime change.

## Known blockers / constraints

- LAB-086 remains first priority. Hidden-rowid fix must be published byte-exact before the full real-ledger gate resumes.
- Direct shell/raw GitHub transport remains unavailable in this run; connector reads do not directly mount repository files into the executor.
- The available Contents write cannot consume the exact local candidate file by filesystem reference; manually transcribing/reformatting the large security-critical file would weaken the established exact-blob discipline.
- A reconstructed file counts as execution evidence only if `git hash-object` equals the GitHub blob.
- PR #165 must remain draft until rowid fix publication, repinned strict/thaw subgate, complete real-ledger gate, unsafe seed, compileall and final audit are all clean.
- PR #173 remains draft. In addition to its full real LAB-080/LAB-082 class-level two-worker/crash/UNKNOWN gate, failed first adoption must be tested for zero persistent LAB-091 schema/trigger side effects before any constructor-ordering fix is published.
- LAB-090/#169 provider handoff freshness remains separate.

## Exact next action

1. LAB-086 first: obtain a byte-safe supported transfer path for exact candidate `b78e7c98e35138719f77c482c7f1aab36b702de7` into `experiments/asymmetric_break_glass_history/strict_fence.py` on PR #165. Publish only if branch predecessor remains `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd` and GitHub returns exactly `b78e7c98...`.
2. Re-fetch/hash-verify the published runtime, execute exact `test_thaw_rowid_collision_regression.py` plus the complete strict/thaw conflict subgate and compileall, then repin only after green evidence.
3. Resume complete branch-local LAB-080→086 real-ledger modules, unsafe legacy-promotion expected-failure seed, full compileall and final security/reconciliation audit.
4. If LAB-086 publication remains concretely tool-limited, LAB-091 fallback next action is an exact real-stack regression through `SupportedHistoryBoundOperationScopedAsymmetricSharedAnchorLedger` proving that a lower `verify_durable()` failure during first adoption leaves no LAB-091 triggers/schema side effects. Only after RED reproduction consider minimal `verify_durable() -> _install_guards() -> verify_durable()` constructor ordering, then continue the full two-worker/crash/timeout-UNKNOWN/reentrancy gate.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; hidden-rowid blocker has exact RED→GREEN candidate evidence; byte-exact runtime publication is next.
- #166 / LAB-087 — DONE; merged as `65a44cc8d12cf37d04d9cd59398b456d7429cc31`.
- #167 / LAB-088 — IN_PROGRESS; draft PR #172.
- #168 / LAB-089 — CLOSED `not_planned`.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — IN_PROGRESS; draft PR #173; new failed-adoption atomicity regression required before constructor-ordering change; full real-stack gate remains.
