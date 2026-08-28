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
- LAB-091 / #170 remains IN_PROGRESS on draft PR #173; current HEAD `936f3430810e587a6033cfabe77047feb0563082`, mergeable=true, draft. Use only as fallback while LAB-086 exact work is concretely tool-limited.

## Last completed step

Probed LAB-086 first. Local DNS for `github.com`, `raw.githubusercontent.com`, and `api.github.com` still fails, so the executor cannot directly clone/fetch the branch. The GitHub connector can return the complete PR patch for the 949-line `strict_fence.py`, but it still does not mount that payload into the local executor. Manually reserializing the ~40 KB security-critical runtime would weaken the established exact-blob gate, so the hidden-rowid candidate was not published and no LAB-086 PASS was fabricated.

Used the allowed LAB-091 fallback and re-audited the complete constructor MRO. This invalidated the previous adoption-ordering conclusion. `SupportedMutableAsymmetricSharedAnchorLedger.__init__()` does call `super().__init__() -> self._install_guards() -> self.verify_durable()`, but the inherited `super().__init__()` path itself reaches `SupportedSharedAnchorLedger.__init__()`, which calls `self.verify_durable()` before returning. No LAB-091 subclass overrides that method, so dynamic dispatch resolves to the full `AsymmetricHistoricalSharedAnchorLedger.verify_durable()` LAB-082 history/receipt verifier. Therefore corrupt lower history fails before LAB-091 guard installation.

The earlier dynamic hook is `SharedAnchorLedger.__init__() -> self._init()`, which reaches final LAB-091 `_init()`. Audited `restart_safe_schema.initialize_shared_anchor_schema()` creates/observes only the historical LAB-080 tables and singleton and installs no LAB-091 guard triggers. The prior focused SQLite reproduction modeled a different ordering and is not evidence about the real final constructor.

Recorded the correction in `research/2026-08-28-lab091-constructor-ordering-correction.md` (commit `cbcdb58893a63295da9ac354b201dae215cc0d06`) and Issue #170 comment `5449176852`. Added `test_failed_adoption_no_guard_persistence.py`, which seeds a valid LAB-082 confirmed receipt, corrupts its Ed25519 signature, requires first final LAB-091 open to raise `HistoricalVerificationError`, then asserts zero persisted `lab091_%` triggers. Local authored test passed `py_compile`; local `git hash-object` and published GitHub blob both equal `a81c393766df571770962bab1714d34a062b03d5` (commit `936f3430810e587a6033cfabe77047feb0563082`). Full branch-local execution remains pending.

## Evidence retained

- LAB-080 18/18 PASS; LAB-082 28/28 PASS; LAB-083 24/24 PASS; LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS; asymmetric custody 8/8 PASS; public/final 11/11 PASS; lower unsafe baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; unsafe legacy auto-promotion failed as intended.
- Previous repinned LAB-086 strict/thaw exact subgate: 31/31 PASS + compileall on pin `1fa85a0e...`; not sufficient for merge because hidden-rowid conflict was not covered.
- Hidden-rowid exact RED→GREEN retained: predecessor RED 3/3, candidate `b78e7c98...` GREEN 3/3 + compileall; runtime publication still pending.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-091 adoption-state/domain gate: 23/23 PASS + compileall.
- LAB-091 alternate lower/legacy connection persistence regression: exact published 2/2 PASS + compileall, blob `365688e0...`.
- LAB-091 constructor-ordering correction is source/MRO evidence: complete LAB-082 `verify_durable()` runs before final LAB-091 `_install_guards()` on first construction.
- New LAB-091 failed-adoption regression is authored, `py_compile` PASS and byte-exact published as blob `a81c3937...`; do not count it as a test PASS until the real branch-local dependency closure is executed.

## Known blockers / constraints

- LAB-086 remains first priority. Hidden-rowid fix must be published byte-exact before the full real-ledger gate resumes.
- Direct shell/raw GitHub transport remains unavailable in this run; connector reads do not directly mount repository files into the executor.
- The available Contents write cannot consume the exact local LAB-086 candidate file by filesystem reference; manually transcribing/reformatting the large security-critical file would weaken the exact-blob discipline.
- A reconstructed file counts as execution evidence only if `git hash-object` equals the GitHub blob.
- PR #165 must remain draft until rowid fix publication, repinned strict/thaw subgate, complete real-ledger gate, unsafe seed, compileall and final audit are all clean.
- PR #173 remains draft. The previous proposed constructor reorder is superseded and must not be published on that rationale. Its remaining gate is the full real LAB-080/LAB-082 class-level failed-adoption regression plus two-worker/crash/timeout-UNKNOWN/reentrancy/legacy-surface execution.
- LAB-090/#169 provider handoff freshness remains separate.

## Exact next action

1. LAB-086 first: obtain a byte-safe supported transfer path for exact candidate `b78e7c98e35138719f77c482c7f1aab36b702de7` into `experiments/asymmetric_break_glass_history/strict_fence.py` on PR #165. Publish only if branch predecessor remains `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd` and GitHub returns exactly `b78e7c98...`.
2. Re-fetch/hash-verify the published LAB-086 runtime, execute exact `test_thaw_rowid_collision_regression.py` plus the complete strict/thaw conflict subgate and compileall, then repin only after green evidence.
3. Resume complete branch-local LAB-080→086 real-ledger modules, unsafe legacy-promotion expected-failure seed, full compileall and final security/reconciliation audit.
4. If LAB-086 publication remains concretely tool-limited, LAB-091 fallback next action is to execute exact published `test_failed_adoption_no_guard_persistence.py` through `SupportedHistoryBoundOperationScopedAsymmetricSharedAnchorLedger` with the real LAB-080/LAB-082 dependency closure; then continue the full supported-surface two-worker/crash/timeout-UNKNOWN/reentrancy/legacy-write gate. No constructor-order runtime change is currently justified.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; hidden-rowid blocker has exact RED→GREEN candidate evidence; byte-exact runtime publication is next.
- #166 / LAB-087 — DONE; merged as `65a44cc8d12cf37d04d9cd59398b456d7429cc31`.
- #167 / LAB-088 — IN_PROGRESS; draft PR #172.
- #168 / LAB-089 — CLOSED `not_planned`.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — IN_PROGRESS; draft PR #173 HEAD `936f3430...`; failed-adoption ordering finding corrected, regression published byte-exact but not yet real-stack executed; full real-stack gate remains.
