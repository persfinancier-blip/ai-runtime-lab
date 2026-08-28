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
- LAB-091 / #170 remains IN_PROGRESS on draft PR #173; current HEAD `db514d4ffab8f831ac60dfb09a449584b2282360`, mergeable=true, draft. Use only as fallback while LAB-086 exact work is concretely tool-limited.

## Last completed step

Probed LAB-086 first. Direct `git clone`/raw GitHub transport still fails in this runtime because `github.com` cannot resolve. Connector reads remain byte-exact but ordinary repository blobs are not mounted into the local executor, so the ~40 KB security-critical `strict_fence.py` hidden-rowid candidate was not manually reserialized and no LAB-086 PASS was fabricated.

Used the allowed LAB-091 fallback to close the alternate lower-write-surface acceptance gap. Reconstructed and hash-verified the exact published dependencies:
- `operation_permit.py` `637784a5cb61a024a1df3e0e983887b6d0a838be`;
- `row_tokens.py` `801eb0fbdb915bb31f40069d087bf3ce56d659a8`;
- `full_operation_guards.py` `8e409d61d3d813dbf3a564ea8ea5f4d3015106fb`.

Added `experiments/mutable_shared_anchor_writer/tests/test_alternate_lower_surface_persistence.py`. The locally executed test blob was `365688e001f56276f397d46458adc9eb24f45f4f`; GitHub returned the same blob after publication in commit `db514d4ffab8f831ac60dfb09a449584b2282360`.

Focused exact result: **2/2 PASS + compileall PASS**. After v2 one-shot guards are persisted, both a plain LAB-080-style/raw SQLite connection and a legacy connection carrying only the old broad `lab091_writer_authorized()==1` predicate fail closed on consequential meta/intent/watermark/receipt writes. Durable rows remain unchanged. PR #173 and Issue #170 comments record the evidence.

## Evidence retained

- LAB-080 18/18 PASS; LAB-082 28/28 PASS; LAB-083 24/24 PASS; LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS; asymmetric custody 8/8 PASS; public/final 11/11 PASS; lower unsafe baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; unsafe legacy auto-promotion failed as intended.
- Previous repinned LAB-086 strict/thaw exact subgate: 31/31 PASS + compileall on pin `1fa85a0e...`; not sufficient for merge because hidden-rowid conflict was not covered.
- Hidden-rowid exact RED→GREEN retained: predecessor RED 3/3, candidate `b78e7c98...` GREEN 3/3 + compileall; runtime publication still pending.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-091 adoption-state/domain gate: 23/23 PASS + compileall.
- LAB-091 alternate lower/legacy connection persistence regression: exact published **2/2 PASS + compileall**, blob `365688e0...`.

## Known blockers / constraints

- LAB-086 remains first priority. Hidden-rowid fix must be published byte-exact before the full real-ledger gate resumes.
- Direct shell/raw GitHub transport remains unavailable in this run; connector reads do not directly mount repository files into the executor.
- The available Contents write cannot consume the exact local candidate file by filesystem reference; manually transcribing/reformatting the large security-critical file would weaken the established exact-blob discipline.
- A reconstructed file counts as execution evidence only if `git hash-object` equals the GitHub blob.
- PR #165 must remain draft until rowid fix publication, repinned strict/thaw subgate, complete real-ledger gate, unsafe seed, compileall and final audit are all clean.
- PR #173 remains draft. Its remaining gate is the full real LAB-080/LAB-082 class-level two-worker/crash/UNKNOWN supported-surface execution plus reentrancy audit; focused alternate-surface coverage is now closed.
- LAB-090/#169 provider handoff freshness remains separate.

## Exact next action

1. LAB-086 first: obtain a byte-safe supported transfer path for exact candidate `b78e7c98e35138719f77c482c7f1aab36b702de7` into `experiments/asymmetric_break_glass_history/strict_fence.py` on PR #165. Publish only if branch predecessor remains `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd` and GitHub returns exactly `b78e7c98...`.
2. Re-fetch/hash-verify the published runtime, execute exact `test_thaw_rowid_collision_regression.py` plus the complete strict/thaw conflict subgate and compileall, then repin only after green evidence.
3. Resume complete branch-local LAB-080→086 real-ledger modules, unsafe legacy-promotion expected-failure seed, full compileall and final security/reconciliation audit.
4. If LAB-086 publication remains concretely tool-limited, continue LAB-091 with the full real `SupportedHistoryBoundOperationScopedAsymmetricSharedAnchorLedger` two-worker/crash/timeout-UNKNOWN execution and reentrancy audit. Do not substitute focused stubs unless a new executable blocker is first reproduced.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; hidden-rowid blocker has exact RED→GREEN candidate evidence; byte-exact runtime publication is next.
- #166 / LAB-087 — DONE; merged as `65a44cc8d12cf37d04d9cd59398b456d7429cc31`.
- #167 / LAB-088 — IN_PROGRESS; draft PR #172.
- #168 / LAB-089 — CLOSED `not_planned`.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — IN_PROGRESS; draft PR #173; alternate lower/legacy connection coverage now exact 2/2 PASS; full real-stack gate remains.
