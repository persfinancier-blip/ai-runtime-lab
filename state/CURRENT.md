# Current Lab State

Last updated: 2026-08-29

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Active priority: #163 / LAB-086 — IN_PROGRESS; draft PR #165, branch `lab/086-asymmetric-break-glass-history`.
- Live LAB-086 `strict_fence.py` blob remains `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`.
- Exact unpublished hidden-rowid candidate remains `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- LAB-088 / #167 remains IN_PROGRESS on draft PR #172.
- LAB-091 / #170 remains IN_PROGRESS on draft PR #173, branch head `715bebe7172e738b15ce126bb2f132645010e9d5`; fallback only while LAB-086 exact publication/execution is concretely tool-limited.

## Last completed step

Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected open issues and active PRs. LAB-086 remains first priority. Conflict-check confirmed branch `strict_fence.py` is still exact predecessor blob `d4a6a40f...`. Shell/raw GitHub DNS remains unavailable in this runtime, so the exact ~39.8 KB candidate still cannot be published from the executable filesystem through a byte-preserving supported path.

Used the allowed LAB-091 fallback to continue the first-adoption schema audit. Found that `_unique_key_sets()` accepted identity UNIQUE/PRIMARY KEY constraints solely by column names and therefore treated `UNIQUE(... COLLATE NOCASE)` as canonical. Executed SQLite reproduction confirmed this is not equivalent to the LAB-080/LAB-082 exact-string identity contract: `Intent-A` and `intent-a` are byte-distinct protocol identities but the NOCASE unique constraint rejects the second insert.

Published the minimal fix on `lab/091-mutable-shared-anchor-writer`: use `PRAGMA index_xinfo` key terms and require BINARY collation for text/composite identity indexes while retaining partial/expression rejection; bare `INTEGER PRIMARY KEY` remains directly accepted because it is the rowid identity and has no backing index. Validator commit `4d509c028c8b32f36011674cb868374223538069`, blob `1731648b4e65b1c5984d4f93b78c45d5a066dd95`. Added regression commit `715bebe7172e738b15ce126bb2f132645010e9d5`, blob `ad2b3b80bf848f874e300acf6304cb57997f5bca`.

Focused executed mechanism gate PASS: canonical BINARY schema accepted; NOCASE intent ID, intent request ID, watermark component ID, and receipt request ID constraints all rejected; behavioral NOCASE incompatibility reproduced; focused probe compile PASS. This is not the complete PR #173 real-stack gate.

Durable note: `research/2026-08-29-lab091-nonbinary-identity-collation-adoption.md`, main commit `e7e58dcab84f889227c0d2901bac105281716a29`. Issue #170 comment `5459117184`; PR #173 comment `5459117825`.

## Evidence retained

- LAB-080 18/18 PASS; LAB-082 28/28 PASS; LAB-083 24/24 PASS; LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS; asymmetric custody 8/8 PASS; public/final 11/11 PASS; lower unsafe baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; unsafe legacy auto-promotion failed as intended.
- Alternate-UNIQUE and provider-receipt NULL protections are present in live LAB-086 predecessor `d4a6a40f...`.
- LAB-086 hidden-rowid RED->GREEN evidence retained; exact predecessor `d4a6a40f...` -> candidate `b78e7c98...` was byte-rederived and focused mechanism-tested in the prior run.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-091 exact published expression/partial/missing-constraint adoption-index suites: 4/4 PASS + compileall on their prior pinned blobs.
- LAB-091 non-BINARY identity collation: focused executed mechanism gate PASS; published validator blob now `1731648b...`, regression blob `ad2b3b80...`.

## Known blockers / constraints

- LAB-086 remains first priority.
- Current LAB-086 live security delta is rowid-only hardening. Do not reapply alternate-UNIQUE or provider-receipt NULL patches.
- Read-side/executable reconstruction for the ~40 KB runtime is no longer a blocker; exact predecessor and candidate hashes are reproducible.
- Publication remains blocked by data-plane separation: supported GitHub Contents `update_file` requires the complete UTF-8 replacement body and does not accept a mounted-file/file-reference; shell/raw GitHub DNS still fails. Do not bridge with low-level blob/tree/ref manipulation, force updates, or manual unauthenticated rewrites.
- PR #165 remains draft until candidate publication/hash verification, four focused regressions, complete strict/thaw subgate, LAB-080->086 real-ledger gate, unsafe seed, compileall and final security/reconciliation audit are clean.
- PR #173 remains draft pending its complete real-stack gate. Existing timeout-after-commit and process concurrency/crash tests use stubs; they do not yet prove the final supported class against exact real LAB-080/LAB-082 dependencies.
- LAB-090/#169 provider handoff freshness remains separate.

## Exact next action

1. LAB-086 first: conflict-check branch `strict_fence.py` is still `d4a6a40f...`. If a newly available supported byte-preserving Contents path can accept the exact local candidate, publish `b78e7c98...`, require returned and re-fetched blob equality, then run the four focused regressions + strict/thaw subgate + compileall and resume the LAB-080->086 real-ledger gate.
2. Do not repeat LAB-086 predecessor reconstruction unless the live blob changes.
3. If LAB-086 publication remains concretely tool-limited, continue LAB-091 by replacing the stub-only proof gap with a real-stack regression around `SupportedHistoryBoundOperationScopedAsymmetricSharedAnchorLedger`: first timeout-after-commit/UNKNOWN retry convergence, then two-worker confirmation/crash semantics, using exact real LAB-080/LAB-082 dependencies.
4. Re-run the prior LAB-091 adoption-index suites against the new validator blob `1731648b...` before counting the collation change as branch-wide regression-safe.
5. Keep PRs #165/#173 draft until their complete gates are clean.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact rowid candidate re-derived + focused mechanism PASS, publication/full gate pending.
- #166 / LAB-087 — DONE; merged as `65a44cc8d12cf37d04d9cd59398b456d7429cc31`.
- #167 / LAB-088 — IN_PROGRESS; draft PR #172.
- #168 / LAB-089 — CLOSED `not_planned`.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — IN_PROGRESS; draft PR #173; collation schema-contract fix published; exact prior adoption-index regressions need re-run on new validator, then full supported real-stack gate.
