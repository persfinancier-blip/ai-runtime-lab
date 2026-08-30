# Current Lab State

Last updated: 2026-08-30

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165; branch `lab/086-asymmetric-break-glass-history`.
- Authoritative LAB-086 `strict_fence.py` predecessor: `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`.
- Retained hidden-rowid patch: `research/2026-08-28-lab086-hidden-rowid-replace.patch`, blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; exact previously derived target `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- LAB-091 / #170 is the allowed fallback while LAB-086 publication/execution is concretely tool-limited; draft PR #173, branch `lab/091-mutable-shared-anchor-writer`.
- Current LAB-091 PR head: `9f999dd9704742d5f929c4d340494d02322b044e` (connector re-fetch confirmed open, mergeable, draft).
- LAB-088 / #167 remains IN_PROGRESS on draft PR #172. LAB-090 / #169 remains READY.

## Last completed step

Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected active PRs/issues. No supported byte-preserving composition writer for the exact 949-line LAB-086 `strict_fence.py` predecessor plus retained patch appeared in this run, so no LAB-086 mutation was attempted.

Continued the allowed LAB-091 first-adoption compatibility audit and reproduced a reachable defect in the prior extra-column validator. An otherwise canonical empty legacy `shared_anchor_intents` table can add a nullable generated column such as `legacy_json TEXT GENERATED ALWAYS AS (json_extract(component_id,'$.x')) STORED`. `PRAGMA table_xinfo` reports the column as hidden/generated, so the prior validator ignored it. Adoption could succeed, but the canonical supported INSERT for a valid ordinary identity such as `component-b` evaluates the inherited expression and fails with `sqlite3.OperationalError: malformed JSON`. A separate mechanism probe also showed that generated `NOT NULL` expressions can reject otherwise valid supported rows, so generated-column nullability alone is insufficient.

Published on PR #173 through normal conflict-scoped Contents API writes:
- `b713c735eca2e8d57115c328088fd16cf3b828d8` — `adoption_extra_columns.py` now rejects non-canonical generated extras (`table_xinfo hidden=2/3`) fail-closed while still accepting ordinary nullable/defaulted extras;
- `9f999dd9704742d5f929c4d340494d02322b044e` — regression added to `test_adoption_required_extra_column_regression.py`; connector re-fetch confirms this is current draft PR #173 head.

Re-fetched both published files and locally reconstructed/executed their focused unittest surface: **4/4 PASS**. Canonical schema accepted; ordinary nullable/defaulted extras accepted; required ordinary extra rejected with the pre-fix supported INSERT failure reproduced; generated nullable JSON extra rejected with the pre-fix `malformed JSON` supported INSERT failure reproduced. Python emitted an unrelated spreadsheet-runtime warmup traceback before discovery, but unittest completed return code 0 with all four named tests `ok`. This is focused exact-content reconstruction evidence for the two published files, not full PR/full-stack execution.

Durable analysis: `research/2026-08-30-lab091-generated-extra-column-adoption-gap.md`, main commit `83f4ea03c3b6a4e1999bf0f50e436f552a8aaf7f`; issue #170 comment `5466205957`.

## Evidence retained

- LAB-080 18/18 PASS; LAB-082 28/28 PASS; LAB-083 24/24 PASS; LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS; asymmetric custody 8/8 PASS; public/final 11/11 PASS; unsafe lower baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; unsafe legacy auto-promotion failed as intended.
- LAB-086 hidden-rowid RED→GREEN evidence retained; exact predecessor `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd` -> candidate `b78e7c98e35138719f77c482c7f1aab36b702de7` previously byte-rederived and mechanism-tested; publication/full gate pending.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-091 earlier adoption hardening combined focused gate 17/17 PASS before later affinity/collation fixes.
- LAB-091 receipt affinity, receipt collation, identity lookup, constructor ordering, receipt-orphan collation, restrictive-UNIQUE, restrictive-CHECK, required-extra-column and generated-extra-column defects now have published fixes with focused local semantic/mechanism evidence; latest exact whole-branch regressions remain pending executable transport.
- LAB-091 generated-extra focused re-fetched-content gate: 4/4 PASS on current validator/regression pair.
- LAB-091 timeout/UNKNOWN regression blob `92133cdc54fd8b95eb9e3270b5e69d4b85a4b05` and process concurrency/crash regression blob `938877479d4c4b997ea52e8b5857bf89e5c3e246` remain pending full final-surface execution.

## Known blockers / constraints

- LAB-086 remains first priority. Do not manually/model-reserialize the 949-line security-critical `strict_fence.py`.
- Publish LAB-086 only by conflict-checking exact predecessor `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`, applying only the retained hidden-rowid patch through a byte-preserving supported path, requiring exact target `b78e7c98e35138719f77c482c7f1aab36b702de7`, then re-fetch/hash-verify and run the complete security gate.
- PR #165 remains draft until exact rowid publication/hash verification and full strict/thaw + LAB-080→086 real-ledger + compileall/security audit pass.
- PR #173 remains draft. Exact whole-branch regressions, timeout/UNKNOWN, process concurrency/crash, receipt-affinity, receipt-collation and accumulated adoption regressions remain pending executable transport.
- Do not represent focused local reconstruction/mechanism execution as byte-for-byte full-branch execution.
- Do not add speculative SQLite guards without a reproduced reachable supported compatibility/security failure.

## Exact next action

LAB-086 first: if a supported byte-preserving composition/transfer bridge appears, re-fetch predecessor `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`, apply only retained hidden-rowid patch, require exact target `b78e7c98e35138719f77c482c7f1aab36b702de7`, publish through normal Contents API, re-fetch/hash-verify, then run rowid + receipt-NULL + alternate-UNIQUE + complete strict/thaw + compileall + LAB-080→086 real-ledger gates. If that bridge is still unavailable, execute exact PR #173 head `9f999dd9704742d5f929c4d340494d02322b044e` when whole-branch executable transport appears, beginning with the accumulated adoption regressions including generated-extra-column coverage; if exact execution remains unavailable, continue first-adoption compatibility audit only for newly reproduced reachable supported-write failures.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; draft PR #172.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — IN_PROGRESS fallback; draft PR #173; generated-extra-column hardening published; exact whole-branch/full behavioral gates pending.
