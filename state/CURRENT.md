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

Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected open PRs and resumed LAB-086 first. The LAB-086 byte-preserving publication blocker remains unchanged, so no manual reserialization of the ~40 KB security-critical `strict_fence.py` was attempted.

Per fallback policy, audited LAB-091 first-adoption schema semantics. Found a concrete gap in `_unique_key_sets()`: SQLite partial UNIQUE indexes (`PRAGMA index_list(...)[4] == 1`) were counted as table-wide identity guarantees even though uniqueness applies only to rows satisfying the index predicate. A clean weakened legacy schema could therefore pass adoption and later admit duplicate identities outside the predicate.

Fixed on branch `lab/091-mutable-shared-anchor-writer`:
- validator commit `7198487c306077724d3d8721e1d1e2b28004288c`, blob `bab8366438f266342ab461307c9191c9328653bd`;
- regression introduced then syntax-corrected; final commit `affb299bf9810c2bffcde0d6060ebf3e49b9975a`, blob `e77521d839510490a2bea4d92d68d9071241ff35`.

Executed local SQLite mechanism probe: `UNIQUE(id) WHERE status='CONFIRMED'` accepted two duplicate `PREPARED` rows; the pre-fix collector falsely returned `('id',)`, while the corrected collector ignored the partial index; assertions PASS. This is focused mechanism evidence only, not full PR #173 acceptance.

Durable note: `research/2026-08-28-lab091-partial-unique-adoption-gap.md`, main commit `03093fb5d7816c4ae886d44082354167bfae4702`. Issue #170 comment `5456771737` and PR #173 comment `5456772697` record the same result.

## Evidence retained

- LAB-080 18/18 PASS; LAB-082 28/28 PASS; LAB-083 24/24 PASS; LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS; asymmetric custody 8/8 PASS; public/final 11/11 PASS; lower unsafe baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; unsafe legacy auto-promotion failed as intended.
- Alternate-UNIQUE and provider-receipt NULL protections are present in live `d4a6a40f...`.
- Hidden-rowid RED→GREEN evidence retained: exact predecessor `d4a6a40f...` -> candidate `b78e7c98...`; candidate remains unpublished. Rowid collision regression and explicit `rowid=-1` sentinel regression are durable on PR #165.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-091 focused evidence now covers adoption lock/WAL behavior, existing-row identity ambiguity, missing canonical identity constraints, and partial-UNIQUE false identity guarantees.

## Known blockers / constraints

- LAB-086 remains first priority.
- The current live security delta is rowid-only hardening. Do not reapply alternate-UNIQUE or provider-receipt NULL patches.
- Direct shell/raw GitHub transport remains unavailable in this executor.
- Connector reads are exact but do not mount the complete LAB-086 candidate into the execution filesystem; large responses are truncated. Publication through Contents API is allowed only after exact candidate bytes are materialized and tested; do not hand-rewrite the security-critical runtime.
- PR #165 must remain draft until candidate publication/hash verification, complete strict/thaw gate, LAB-080→086 real-ledger gate, unsafe seed, compileall and final security/reconciliation audit are clean.
- PR #173 remains draft pending complete real-stack gate. Current partial-UNIQUE change has mechanism-level evidence; the repository regression itself has not been executed in a complete checkout in this run.
- Remaining DDL audit should distinguish constraints that merely duplicate supported-writer validation from constraints whose absence permits future ambiguity under otherwise canonical transitions. Do not broaden schema rejection without a reproduced failure.
- LAB-090/#169 provider handoff freshness remains separate.

## Exact next action

1. LAB-086 first: obtain a supported byte-preserving publication path for exact candidate `b78e7c98e35138719f77c482c7f1aab36b702de7` over predecessor `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; do not manually reserialize the file.
2. Require GitHub returned blob == `b78e7c98...`, then re-fetch/hash-verify and execute the four focused regressions plus strict/thaw subgate + compileall.
3. Resume complete LAB-080→086 real-ledger gate, unsafe legacy-promotion expected-failure seed, full compileall, security/reconciliation audit and branch/main conflict check.
4. If LAB-086 remains concretely transport-limited, continue LAB-091 complete real-stack integration. Execute the partial-UNIQUE regression together with both earlier weakened-schema regressions and audit remaining index semantics (collation/expression/order) before considering NOT NULL/CHECK structural rejection.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid candidate tested but unpublished; publication/execution transport remains blocker.
- #166 / LAB-087 — DONE; merged as `65a44cc8d12cf37d04d9cd59398b456d7429cc31`.
- #167 / LAB-088 — IN_PROGRESS; draft PR #172.
- #168 / LAB-089 — CLOSED `not_planned`.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — IN_PROGRESS; draft PR #173; adoption lock + weakened-schema row/cardinality + canonical identity + partial-UNIQUE hardening have focused evidence, full real-stack gate still open.
