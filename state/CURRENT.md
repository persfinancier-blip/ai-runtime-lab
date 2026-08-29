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

Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; re-inspected active PRs. LAB-086 predecessor was re-fetched and is still exact blob `d4a6a40f...`. Shell `git clone` again failed before byte transfer because `github.com` DNS could not resolve, so the exact 40 KB candidate was not approximated or manually lossy-reserialized.

Used the permitted LAB-091 fallback and executed the combined adoption hardening surface against current branch logic after head `210d51dd15ebfcaf4858bb927e2b729765c176b3`. Exact fetched runtime blobs: `adoption_validation.py` `1731648b4e65b1c5984d4f93b78c45d5a066dd95`, `adoption_schema_domains.py` `1abef5360fc57f5a863e8665556cbdb9dee6f012`, `full_operation_guards.py` `529ee8094d04b0cc9bb208f3fce8f85b2bc6db0f`.

A local SQLite mechanism harness reproduced the exact fetched branch logic for identity/index admission, required-NOT-NULL admission, deterministic request identity and the current v2 watermark insert predicate. Combined result: **17/17 PASS**. Canonical identity + NOT NULL accepted; six missing identity constraints rejected; four NOCASE identity variants rejected; expression and partial UNIQUE do not collapse to false global identity; weakened `component_id` NOT NULL rejected; weakened watermark CHECK still rejects `position=-1` through exact permit while `position=0` remains valid.

This is explicitly a focused mechanism gate over exact fetched branch logic, not execution of every published unittest file and not the full LAB-080/LAB-082 real-stack acceptance gate. Durable note: `research/2026-08-29-lab091-combined-adoption-focused-gate.md`, main commit `ccc1c6ef49f0288cf9fc085710faad94493dc583`; Issue #170 comment `5460010387`; PR #173 comment `5460010753`.

## Evidence retained

- LAB-080 18/18 PASS; LAB-082 28/28 PASS; LAB-083 24/24 PASS; LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS; asymmetric custody 8/8 PASS; public/final 11/11 PASS; lower unsafe baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; unsafe legacy auto-promotion failed as intended.
- LAB-086 hidden-rowid RED->GREEN evidence retained; exact predecessor `d4a6a40f...` -> candidate `b78e7c98...` was byte-rederived and focused mechanism-tested.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-091 adoption hardening now has a combined focused 17/17 PASS over current identity/index/collation + NOT NULL + weakened-watermark-CHECK logic.

## Known blockers / constraints

- LAB-086 remains first priority. Current live security delta is rowid-only hardening; do not reapply alternate-UNIQUE or provider-receipt NULL patches.
- LAB-086 publication remains blocked by byte-preserving data-plane separation for the exact 40 KB candidate. Do not use low-level blob/tree/ref manipulation, force updates, or manual lossy rewrites.
- PR #165 remains draft until exact candidate publication/hash verification, four focused regressions, complete strict/thaw subgate, LAB-080->086 real-ledger gate, unsafe seed, compileall and final security/reconciliation audit are clean.
- PR #173 remains draft. Existing timeout-after-commit and process concurrency/crash tests still use stubs and do not prove the final supported class against exact real LAB-080/LAB-082 dependencies.
- Do not repeat the narrow LAB-091 combined adoption gate unless one of the pinned source blobs changes.
- CHECK/type-affinity equivalence is not globally claimed. Only demonstrated behavior gaps should add constraints/guards.
- LAB-090/#169 provider handoff freshness remains separate.

## Exact next action

1. LAB-086 first: re-check `strict_fence.py` remains `d4a6a40f...`. If a byte-preserving bridge to the normal Contents writer becomes available, publish only exact candidate `b78e7c98...`, require returned/re-fetched blob equality, then run four focused regressions + strict/thaw subgate + compileall + LAB-080->086 real-ledger gate.
2. If LAB-086 publication remains tool-limited, LAB-091: close the highest-value remaining proof gap with the final `SupportedHistoryBoundOperationScopedAsymmetricSharedAnchorLedger` against exact real LAB-080/LAB-082 dependencies. First prove timeout-after-commit/UNKNOWN retry convergence; then prove two-worker confirmation/crash semantics.
3. Retain/reconfirm LAB-087 restricted-worker composition and audit alternate write surfaces/reentrancy before PR #173 can leave draft.
4. Continue CHECK/type-affinity audit only where a concrete future reachable-state counterexample can be reproduced.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact rowid candidate re-derived + focused mechanism PASS, publication/full gate pending.
- #166 / LAB-087 — DONE; merged as `65a44cc8d12cf37d04d9cd59398b456d7429cc31`.
- #167 / LAB-088 — IN_PROGRESS; draft PR #172.
- #168 / LAB-089 — CLOSED `not_planned`.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — IN_PROGRESS; draft PR #173; combined adoption hardening focused gate 17/17 PASS; real-stack timeout/UNKNOWN + two-worker/crash gates pending.
