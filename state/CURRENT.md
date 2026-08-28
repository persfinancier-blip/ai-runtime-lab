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
- LAB-091 / #170 remains IN_PROGRESS on draft PR #173; current HEAD `c095c08f25ec034614c150b104f75f5b1ecfc707`, mergeable=true, draft. Use only as fallback while LAB-086 exact work is concretely tool-limited.

## Last completed step

Probed LAB-086 first. The connector still exposes exact predecessor `strict_fence.py` blob `d4a6a40f...`, the saved hidden-rowid patch, and PR #165's complete per-file patch representation, but candidate blob `b78e7c98...` is still absent from GitHub (`fetch_blob` returned 404). The normal Contents writer still requires complete replacement UTF-8 text rather than a connector/file reference. No manual 40 KB security-critical reconstruction was attempted and no new LAB-086 PASS was claimed.

Used the allowed LAB-091 fallback and replaced the earlier proposed LAB-082 verifier refactor with a narrower lock-envelope fix. `SupportedHistoryBoundOperationScopedAsymmetricSharedAnchorLedger._install_guards()` now executes `BEGIN IMMEDIATE`, then re-runs the complete inherited LAB-082 `verify_durable()` before any LAB-091 guard DDL, followed by the v2/v3/v4 guard installers, retroactive mutable-state validation, and commit. The inherited verifier uses a sibling read-only transaction; the first connection's SQLite writer reservation prevents competing legacy/lower SQL writers from mutating committed state between the verification and guard commit.

Published runtime commit `1d1a4586832a9cf660c14637a279ce1342641a69`, blob `931bd4ad0585607866ae27fabf5d6fd4af3dc35e`. An exact local reconstruction hashed to that same Git blob and `python -m py_compile` passed. A standalone SQLite probe also confirmed the required lock behavior in this executor: a sibling reader succeeded while a competing writer failed with `database is locked` under `BEGIN IMMEDIATE`.

Added design/evidence note `research/2026-08-28-lab091-adoption-lock-envelope.md`, commit `c095c08f25ec034614c150b104f75f5b1ecfc707`, and Issue #170 comment `5450213417`. PR #173 remains mergeable=true and draft after the runtime change.

No real-stack unittest PASS is claimed for the new fix in this run. The executor still lacks a working GitHub DNS/network checkout path, so the published deterministic regressions have not yet been executed against the full LAB-080/LAB-082 dependency closure here.

## Evidence retained

- LAB-080 18/18 PASS; LAB-082 28/28 PASS; LAB-083 24/24 PASS; LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS; asymmetric custody 8/8 PASS; public/final 11/11 PASS; lower unsafe baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; unsafe legacy auto-promotion failed as intended.
- Previous repinned LAB-086 strict/thaw exact subgate: 31/31 PASS + compileall on pin `1fa85a0e...`; not sufficient for merge because hidden-rowid conflict was not covered.
- Hidden-rowid exact RED→GREEN retained: predecessor RED 3/3, candidate `b78e7c98...` GREEN 3/3 + compileall; runtime publication still pending.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-091 adoption-state/domain gate: 23/23 PASS + compileall.
- LAB-091 alternate lower/legacy connection persistence regression: exact published 2/2 PASS + compileall, blob `365688e0...`.
- LAB-091 prior failed-adoption regression is published as blob `a81c3937...`; it covers corruption before the first inherited verifier.
- LAB-091 adoption-TOCTOU regression is published as blob `262834c3...`; no PASS is claimed yet.
- LAB-091 lock-envelope runtime blob `931bd4ad...`: exact local hash match + `py_compile` PASS; standalone SQLite serialization premise confirmed (sibling read allowed, competing write blocked).

## Known blockers / constraints

- LAB-086 remains first priority. Hidden-rowid fix must be published byte-exact before the full real-ledger gate resumes.
- Direct shell/raw GitHub transport remains unavailable in this runtime; connector reads do not mount repository files into the executor.
- The available Contents write cannot consume the exact local LAB-086 candidate file by filesystem reference; manually transcribing/reformatting the large security-critical file would weaken the exact-blob discipline.
- PR #165 must remain draft until rowid fix publication, repinned strict/thaw subgate, complete real-ledger gate, unsafe seed, compileall and final audit are all clean.
- PR #173 must remain draft. The first-adoption TOCTOU now has a published lock-envelope runtime fix, but its deterministic regressions still need GREEN execution on exact real LAB-080/LAB-082 dependencies before the blocker is closed.
- LAB-090/#169 provider handoff freshness remains separate.

## Exact next action

1. LAB-086 first: obtain a byte-safe supported transfer path for exact candidate `b78e7c98e35138719f77c482c7f1aab36b702de7` into `experiments/asymmetric_break_glass_history/strict_fence.py` on PR #165. Publish only if branch predecessor remains `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd` and GitHub returns exactly `b78e7c98...`.
2. Re-fetch/hash-verify the published LAB-086 runtime, execute exact `test_thaw_rowid_collision_regression.py` plus the complete strict/thaw conflict subgate and compileall, then repin only after green evidence; resume the complete LAB-080→086 real-ledger gate afterward.
3. If LAB-086 publication remains concretely tool-limited, LAB-091 fallback: execute `test_adoption_toctou_guard_persistence_regression.py` and `test_failed_adoption_no_guard_persistence.py` against exact PR #173 HEAD `c095c08f...` and the complete real LAB-080/LAB-082 dependency closure. Require GREEN before claiming the adoption race fixed.
4. After that GREEN evidence, continue LAB-091's two-worker/crash, timeout-after-commit/UNKNOWN, reentrancy, alternate legacy-write, and LAB-087 composition gates. Keep PR #173 draft until the complete real-stack gate is clean.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; hidden-rowid blocker has exact RED→GREEN candidate evidence; byte-exact runtime publication is next.
- #166 / LAB-087 — DONE; merged as `65a44cc8d12cf37d04d9cd59398b456d7429cc31`.
- #167 / LAB-088 — IN_PROGRESS; draft PR #172.
- #168 / LAB-089 — CLOSED `not_planned`.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — IN_PROGRESS; draft PR #173 HEAD `c095c08f...`; first-adoption lock-envelope fix published, exact real-stack regression execution next when LAB-086 remains tool-limited.
