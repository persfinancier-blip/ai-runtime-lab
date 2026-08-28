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

Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected open PRs and resumed LAB-086 first.

Current-run transport probe reconfirmed the LAB-086 blocker: direct `git clone` fails before transfer with `Could not resolve host: github.com`; system download cannot use the raw GitHub URL because prerequisite web-open is disabled for that URL. No manual reserialization of the ~40 KB security-critical `strict_fence.py` was attempted and no new LAB-086 PASS is claimed.

Per the allowed fallback policy, advanced LAB-091 and found a first-adoption identity-cardinality gap. `initialize_shared_anchor_schema()` uses `CREATE TABLE IF NOT EXISTS`, so a preexisting legacy DB cannot be assumed to retain LAB-080 PK/UNIQUE constraints. The prior row validator could accept two contiguous confirmed rows sharing one `intent_id`; such state is impossible under the supported schema but makes later identity lookups ambiguous.

Fixed on branch `lab/091-mutable-shared-anchor-writer`:
- validator commit `bc2f95d4ca6815383fe30fe856369c5ef1251d29`, blob `c7fff2c6c492ea470a2f495e112c72246aee3258`;
- regression commit `80f84da5338706ab11666e1c5f561ff8bfc510fa`, blob `ac2d6f5f23545a6871a04c589937213a579e3f9e`.

First adoption now fail-closes on duplicate/ambiguous existing intent identity, metadata singleton, receipt request identity, or watermark component identity. Exact target validator/test bytes were hash-matched to GitHub and the focused weakened-schema regression executed **4/4 PASS**. The import harness was minimal, so this is exact target-file evidence, not a complete LAB-080/LAB-082/LAB-091 dependency-closure PASS.

Durable note: `research/2026-08-28-lab091-weakened-schema-identity-adoption.md`, main commit `3b86cd63c4ed9a5c3ebfc98efb40d4d9c7fe23fe`. Issue #170 comment `5455565277` records the same result.

## Evidence retained

- LAB-080 18/18 PASS; LAB-082 28/28 PASS; LAB-083 24/24 PASS; LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS; asymmetric custody 8/8 PASS; public/final 11/11 PASS; lower unsafe baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; unsafe legacy auto-promotion failed as intended.
- Alternate-UNIQUE and provider-receipt NULL protections are present in live `d4a6a40f...`.
- Hidden-rowid RED→GREEN evidence retained: exact predecessor `d4a6a40f...` -> candidate `b78e7c98...`; candidate remains unpublished. Rowid collision regression and explicit `rowid=-1` sentinel regression are durable on PR #165.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-091 one-shot/state-machine/restart/concurrency focused evidence remains retained; WAL adoption-lock mechanism is verified; weakened-schema first-adoption identity ambiguity is now fixed with 4/4 focused PASS.

## Known blockers / constraints

- LAB-086 remains first priority.
- The current live security delta is rowid-only hardening. Do not reapply alternate-UNIQUE or provider-receipt NULL patches.
- Direct shell/raw GitHub transport remains unavailable in this executor.
- Connector reads are exact but do not mount the complete candidate into the execution filesystem; large responses are truncated. Publication through Contents API is allowed only after exact candidate bytes are materialized and tested; do not hand-rewrite the security-critical runtime.
- PR #165 must remain draft until candidate publication/hash verification, complete strict/thaw gate, LAB-080→086 real-ledger gate, unsafe seed, compileall and final security/reconciliation audit are clean.
- LAB-091 focused identity fix is target-file verified only; PR #173 remains draft pending its complete real-stack gate.
- LAB-090/#169 provider handoff freshness remains separate.

## Exact next action

1. LAB-086 first: obtain a supported byte-preserving publication path for exact candidate `b78e7c98e35138719f77c482c7f1aab36b702de7` over predecessor `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; do not manually reserialize the file.
2. Require GitHub returned blob == `b78e7c98...`, then re-fetch/hash-verify.
3. Execute unchanged focused regressions: provider-receipt NULL identity, alternate UNIQUE, hidden-rowid collision, and explicit `rowid=-1` sentinel; then full strict/thaw conflict subgate + compileall and repin.
4. Resume complete LAB-080→086 real-ledger gate, unsafe legacy-promotion expected-failure seed, full compileall, security/reconciliation audit and branch/main conflict check.
5. If LAB-086 remains concretely transport-limited, continue LAB-091 complete real-stack integration. Include the new weakened-schema identity regression in the adoption gate and audit whether any additional legacy schema property is assumed rather than semantically revalidated.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid candidate tested but unpublished; publication/execution transport remains blocker.
- #166 / LAB-087 — DONE; merged as `65a44cc8d12cf37d04d9cd59398b456d7429cc31`.
- #167 / LAB-088 — IN_PROGRESS; draft PR #172.
- #168 / LAB-089 — CLOSED `not_planned`.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — IN_PROGRESS; draft PR #173; adoption lock + weakened-schema identity hardening have focused evidence, full real-stack gate still open.
