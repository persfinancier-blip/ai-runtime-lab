# Current Lab State

Last updated: 2026-08-28

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085 and LAB-087.
- Active priority: #163 / LAB-086 — IN_PROGRESS; draft PR #165, branch `lab/086-asymmetric-break-glass-history`.
- Exact live `strict_fence.py` blob: `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`.
- Exact retained hidden-rowid candidate: `b78e7c98e35138719f77c482c7f1aab36b702de7` (tested previously, not published).
- LAB-088 / #167 remains IN_PROGRESS on draft PR #172.
- LAB-091 / #170 remains IN_PROGRESS on draft PR #173; fallback only while LAB-086 exact publication/execution is concretely tool-limited.

## Last completed step

Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected open PRs. LAB-086 remains blocked on a byte-preserving publication path for the exact hidden-rowid candidate, and direct shell GitHub access still fails DNS resolution, so the ~40 KB security-critical runtime was not manually reserialized.

Under the allowed LAB-091 fallback, audited the remaining SQLite UNIQUE-index semantics. Found a reproduced expression-index false guarantee in `_unique_key_sets()`: `PRAGMA index_info()` reports expression terms as `cid=-2/name=NULL`, while the current collector silently drops NULL names. Therefore `UNIQUE(id, lower(scope))` is incorrectly reduced to `('id',)` even though SQLite admits duplicate `id` rows when the expression differs.

Executed an in-memory SQLite counterexample: the current collector returned `{('id',)}` for `UNIQUE(id, lower(scope))`; inserts `('same','A')` and `('same','B')` both committed; assertions proving the false identity guarantee passed.

Durable LAB-091 branch artifacts:
- red regression `experiments/mutable_shared_anchor_writer/tests/test_adoption_expression_unique_regression.py`, commit `db5b81375f19c7d0e06cc4cc98e992a0f849f1c0`;
- staged minimal fix `research/2026-08-28-lab091-expression-unique-adoption.patch`, commit `b93eb4b733d2cdf6a6f4b644c0186215f607135c`;
- current validator remains exact blob `bab8366438f266342ab461307c9191c9328653bd` until the staged fix is applied byte-safely.

Research note: `research/2026-08-28-lab091-expression-unique-adoption-gap.md`, main commit `7b568c997cf15c6fe194deceb650f82c01301709`. Issue #170 comment `5457349339` and PR #173 comment `5457350290` record the finding.

Adjacent audit result: ASC/DESC does not weaken equality uniqueness for the same named column; built-in `NOCASE` is not a reproduced weaker identity guarantee; do not broaden rejection to collation/NOT NULL/CHECK without a concrete future-ambiguity counterexample.

## Evidence retained

- LAB-080 18/18 PASS; LAB-082 28/28 PASS; LAB-083 24/24 PASS; LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS; asymmetric custody 8/8 PASS; public/final 11/11 PASS; lower unsafe baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; unsafe legacy auto-promotion failed as intended.
- Alternate-UNIQUE and provider-receipt NULL protections are present in live `d4a6a40f...`.
- Hidden-rowid RED→GREEN evidence retained: exact predecessor `d4a6a40f...` -> candidate `b78e7c98...`; candidate remains unpublished. Rowid collision and explicit `rowid=-1` sentinel regressions are durable on PR #165.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-091 focused evidence covers adoption lock/WAL behavior, existing-row identity ambiguity, missing canonical identity constraints, partial-UNIQUE false guarantees, and now expression-UNIQUE false guarantees.

## Known blockers / constraints

- LAB-086 remains first priority.
- Current LAB-086 live security delta is rowid-only hardening. Do not reapply alternate-UNIQUE or provider-receipt NULL patches.
- Direct shell/raw GitHub transport remains unavailable in this executor.
- Connector reads are exact but do not mount the complete LAB-086 candidate into the execution filesystem; publication through Contents API is allowed only after exact candidate bytes are materialized and tested. Do not hand-rewrite the security-critical runtime.
- PR #165 remains draft until candidate publication/hash verification, complete strict/thaw gate, LAB-080→086 real-ledger gate, unsafe seed, compileall and final security/reconciliation audit are clean.
- PR #173 remains draft pending complete real-stack gate. The new expression-UNIQUE regression is durable RED evidence; the staged validator fix is not yet applied.
- Do not broaden legacy schema rejection merely for structural similarity. Require a reproduced ambiguity or unsupported transition that survives current row validation.
- LAB-090/#169 provider handoff freshness remains separate.

## Exact next action

1. LAB-086 first: if a supported byte-preserving path exists, publish exact candidate `b78e7c98e35138719f77c482c7f1aab36b702de7` over predecessor `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; require returned/re-fetched Git blob equality, then run the four focused regressions + strict/thaw subgate + compileall and resume the LAB-080→086 real-ledger gate.
2. If LAB-086 remains concretely transport-limited, LAB-091: apply `research/2026-08-28-lab091-expression-unique-adoption.patch` byte-safely to exact validator blob `bab8366438f266342ab461307c9191c9328653bd`.
3. Execute the expression-UNIQUE regression together with the earlier missing-constraint and partial-UNIQUE regressions; require exact published blobs before promoting evidence.
4. Then resume the complete LAB-080/LAB-082 supported-surface concurrency/restart/crash/UNKNOWN gate and reentrancy audit. Do not expand to NOT NULL/CHECK rejection without a reproduced future-ambiguity gap.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid candidate tested but unpublished; publication/execution transport remains blocker.
- #166 / LAB-087 — DONE; merged as `65a44cc8d12cf37d04d9cd59398b456d7429cc31`.
- #167 / LAB-088 — IN_PROGRESS; draft PR #172.
- #168 / LAB-089 — CLOSED `not_planned`.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — IN_PROGRESS; draft PR #173; expression-UNIQUE false identity guarantee newly reproduced and staged for fix; full real-stack gate still open.
