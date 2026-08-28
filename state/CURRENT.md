# Current Lab State

Last updated: 2026-08-29

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Active priority: #163 / LAB-086 — IN_PROGRESS; draft PR #165, branch `lab/086-asymmetric-break-glass-history`.
- Live `strict_fence.py` blob: `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`.
- Exact hidden-rowid candidate: `b78e7c98e35138719f77c482c7f1aab36b702de7` (re-derived and freshly mechanism-tested in this run; still unpublished).
- LAB-088 / #167 remains IN_PROGRESS on draft PR #172.
- LAB-091 / #170 remains IN_PROGRESS on draft PR #173; fallback only while LAB-086 exact publication/execution is concretely tool-limited.

## Last completed step

Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected open issues and active PRs. LAB-086 remains first priority.

Removed the previous executable-materialization uncertainty for `strict_fence.py`: fetched the live branch file via exact connector line ranges, concatenated them in the executable filesystem, and independently authenticated the result as 949 lines / 37,513 bytes / Git blob `d4a6a40f...`, exactly matching the live branch.

Re-read `research/2026-08-28-lab086-hidden-rowid-replace.patch`. It is a semantic research diff with bare `@@` markers, not directly consumable by GNU `patch`; GNU patch failure was therefore not counted as an implementation failure. Applied the same delta as nine exact-string replacements, each required to match exactly once. Result: 1,007 lines / 39,854 bytes / Git blob `b78e7c98e35138719f77c482c7f1aab36b702de7`, exactly matching the retained previously tested candidate. `py_compile` PASS.

Fresh focused SQLite execution on the exact candidate PASS: explicit hidden-rowid replacement blocked for provider-generation history, post-cutoff evidence, and provider receipts; explicit `rowid=-1` rejected for provider-generation and provider-receipt history; required rowid-sentinel triggers were present.

Durable note: `research/2026-08-29-lab086-byte-exact-reconstruction-and-rowid-gate.md`, main commit `a996f00e881fda6233c17618aa48375f00efcabf`. Issue #163 comment `5458762704`; PR #165 comment `5458770023`.

## Evidence retained

- LAB-080 18/18 PASS; LAB-082 28/28 PASS; LAB-083 24/24 PASS; LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS; asymmetric custody 8/8 PASS; public/final 11/11 PASS; lower unsafe baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; unsafe legacy auto-promotion failed as intended.
- Alternate-UNIQUE and provider-receipt NULL protections are present in live `d4a6a40f...`.
- Hidden-rowid RED->GREEN evidence retained; exact predecessor `d4a6a40f...` -> candidate `b78e7c98...` now freshly re-derived from byte-authenticated source. Fresh focused mechanism gate PASS + py_compile PASS.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-091 exact published expression/partial/missing-constraint adoption-index suites: 4/4 PASS + compileall on pinned published blobs. Do not repeat unless a pin changes.

## Known blockers / constraints

- LAB-086 remains first priority.
- Current LAB-086 live security delta is rowid-only hardening. Do not reapply alternate-UNIQUE or provider-receipt NULL patches.
- Read-side/executable reconstruction for the ~40 KB runtime is no longer a blocker: exact predecessor and candidate hashes can be reproduced in the executable filesystem.
- Publication remains blocked by data-plane separation: the supported GitHub Contents `update_file` action requires the complete UTF-8 replacement body and does not accept a mounted-file/file-reference argument; shell/raw GitHub still fails DNS. Do not bridge with low-level blob/tree/ref manipulation, force updates, or manual unauthenticated rewrites.
- PR #165 remains draft until candidate publication/hash verification, four focused regressions, complete strict/thaw subgate, LAB-080->086 real-ledger gate, unsafe seed, compileall and final security/reconciliation audit are clean.
- PR #173 remains draft pending its complete real-stack gate.
- LAB-090/#169 provider handoff freshness remains separate.

## Exact next action

1. LAB-086 first: conflict-check branch `strict_fence.py` is still `d4a6a40f...`. If any newly available supported byte-preserving Contents-API path can accept the exact local candidate, publish `b78e7c98...`, require returned and re-fetched blob equality, then run the four focused regressions + strict/thaw subgate + compileall and resume the LAB-080->086 real-ledger gate.
2. Do not repeat predecessor reconstruction unless the live blob changes; exact materialization is now proven.
3. If publication remains concretely tool-limited, continue LAB-091 with the full `SupportedHistoryBoundOperationScopedAsymmetricSharedAnchorLedger` real LAB-080/LAB-082 dependency closure: two-worker/concurrency/crash, timeout-after-commit/UNKNOWN, LAB-087 composition, and reentrancy/legacy/alternate write-surface audit.
4. Keep PRs #165/#173 draft until their complete gates are clean.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact rowid candidate re-derived + focused mechanism PASS, publication/full gate pending.
- #166 / LAB-087 — DONE; merged as `65a44cc8d12cf37d04d9cd59398b456d7429cc31`.
- #167 / LAB-088 — IN_PROGRESS; draft PR #172.
- #168 / LAB-089 — CLOSED `not_planned`.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — IN_PROGRESS; draft PR #173; adoption-index focused gate GREEN, full supported real-stack gate open.
