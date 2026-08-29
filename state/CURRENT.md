# Current Lab State

Last updated: 2026-08-29

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Active priority: #163 / LAB-086 — IN_PROGRESS; draft PR #165, branch `lab/086-asymmetric-break-glass-history`.
- Live LAB-086 `strict_fence.py` blob remains `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`.
- Exact unpublished hidden-rowid candidate remains `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- LAB-088 / #167 remains IN_PROGRESS on draft PR #172.
- LAB-091 / #170 remains IN_PROGRESS on draft PR #173; fallback only while LAB-086 exact publication/execution is concretely tool-limited.

## Last completed step

Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected open PRs/issues. LAB-086 predecessor is still `d4a6a40f...`. This run has a normal Contents API writer, but the exact 40 KB candidate body is still separated from the executable filesystem; shell/raw GitHub DNS remains unavailable. The LAB-086 candidate was therefore not approximated or manually lossy-reserialized.

Used the permitted LAB-091 fallback to audit CHECK/type-affinity only for demonstrated reachable-state gaps. Found one: canonical LAB-080 creates `component_anchor_watermarks.position INTEGER NOT NULL CHECK(position>=0)`, but a legacy table missing only that CHECK can accept `position=-1` under the current v2/v4 guard stack when an exact one-shot `watermark-insert` permit is supplied. v4 confirmed-prefix logic runs only for `NEW.position>0`, and v2 previously did not reject negative positions.

Executed a local SQLite RED reproduction: weakened watermark table + current v2/v4 semantics + exact permit admitted `('component-a', -1)`. Published the minimal trigger-level fix on `lab/091-mutable-shared-anchor-writer`: v2 watermark insert now rejects `NEW.position<0` before permit consumption. Runtime commit `568011740f743208314ff2e5c464e1b48bcd4781`; `full_operation_guards.py` blob `529ee8094d04b0cc9bb208f3fce8f85b2bc6db0f`. Added regression commit `210d51dd15ebfcaf4858bb927e2b729765c176b3`, `tests/test_weakened_watermark_check_regression.py`.

Focused supported-path execution after the fix used `PermitConnection`, the one-shot permit UDF/context, and the corrected watermark trigger: negative exact-permit insert rejected; zero exact-permit insert accepted; 2/2 PASS; focused compileall PASS. An initial temporary local harness run had an unterminated triple-quoted string; the harness typo was corrected and rerun. Published branch source did not contain that typo.

Durable note: `research/2026-08-29-lab091-watermark-check-gap.md`, main commit `8e0f5eff31788bc595e30a021314baa83deee4d0`. Issue #170 comment `5459739722`; PR #173 comment `5459740124`.

## Evidence retained

- LAB-080 18/18 PASS; LAB-082 28/28 PASS; LAB-083 24/24 PASS; LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS; asymmetric custody 8/8 PASS; public/final 11/11 PASS; lower unsafe baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; unsafe legacy auto-promotion failed as intended.
- LAB-086 hidden-rowid RED->GREEN evidence retained; exact predecessor `d4a6a40f...` -> candidate `b78e7c98...` was byte-rederived and focused mechanism-tested.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-091 expression/partial/missing-constraint adoption-index suites previously 4/4 PASS + compileall; non-BINARY collation focused gate PASS.
- LAB-091 weakened NOT NULL schema-domain regression 2/2 PASS; NULL-component pre-fix mechanism reproduced.
- LAB-091 weakened watermark CHECK regression now RED reproduced -> fix published -> focused 2/2 PASS + compileall.

## Known blockers / constraints

- LAB-086 remains first priority. Current live security delta is rowid-only hardening; do not reapply alternate-UNIQUE or provider-receipt NULL patches.
- LAB-086 publication remains blocked by byte-preserving data-plane separation for the exact 40 KB candidate. Do not use low-level blob/tree/ref manipulation, force updates, or manual lossy rewrites.
- PR #165 remains draft until exact candidate publication/hash verification, four focused regressions, complete strict/thaw subgate, LAB-080->086 real-ledger gate, unsafe seed, compileall and final security/reconciliation audit are clean.
- PR #173 remains draft. Existing timeout-after-commit and process concurrency/crash tests still use stubs and do not prove the final supported class against exact real LAB-080/LAB-082 dependencies.
- CHECK/type-affinity equivalence is not globally claimed. Only demonstrated behavior gaps should add constraints/guards.
- LAB-090/#169 provider handoff freshness remains separate.

## Exact next action

1. LAB-086 first: re-check `strict_fence.py` remains `d4a6a40f...`. If a byte-preserving bridge to the Contents writer becomes available, publish only exact candidate `b78e7c98...`, require returned/re-fetched blob equality, then run four focused regressions + strict/thaw subgate + compileall + LAB-080->086 real-ledger gate.
2. If LAB-086 publication remains tool-limited, LAB-091: run the combined adoption identity/index/collation + NOT NULL + weakened-watermark-CHECK focused suites against branch head after `210d51dd...`.
3. Then close the stub-only proof gap with real-stack `SupportedHistoryBoundOperationScopedAsymmetricSharedAnchorLedger`: timeout-after-commit/UNKNOWN retry convergence first, then two-worker confirmation/crash semantics, using exact real LAB-080/LAB-082 dependencies.
4. Continue CHECK/type-affinity audit only where a concrete future reachable-state counterexample can be reproduced.
5. Keep PRs #165/#173 draft until complete gates are clean.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact rowid candidate re-derived + focused mechanism PASS, publication/full gate pending.
- #166 / LAB-087 — DONE; merged as `65a44cc8d12cf37d04d9cd59398b456d7429cc31`.
- #167 / LAB-088 — IN_PROGRESS; draft PR #172.
- #168 / LAB-089 — CLOSED `not_planned`.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — IN_PROGRESS; draft PR #173; identity/index/collation, NOT NULL, and demonstrated watermark-CHECK hardening published; combined regression re-run and full supported real-stack gate pending.
