# Current Lab State

Last updated: 2026-08-30

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165; branch `lab/086-asymmetric-break-glass-history`.
- Exact LAB-086 `strict_fence.py` predecessor remains blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd` (949 lines).
- Retained hidden-rowid patch: `research/2026-08-28-lab086-hidden-rowid-replace.patch`, blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; exact previously derived target `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- LAB-091 / #170 is the allowed fallback while LAB-086 publication/execution is concretely tool-limited; draft PR #173, branch `lab/091-mutable-shared-anchor-writer`.
- Current LAB-091 branch head after this run: `7551a6e80c677512da0093bd7ddd083f5189a516`.
- LAB-088 / #167 remains IN_PROGRESS on draft PR #172. LAB-090 / #169 remains READY.

## Last completed step

Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected active issues/PRs. LAB-086 remains first priority. This run newly confirmed the GitHub connector can return PR #165's complete 949-line `strict_fence.py` per-file patch, but no observed supported operation composes that exact fetched payload with the retained hidden-rowid unified patch and transfers the result into a normal Contents API update without model/manual whole-file reserialization. No LAB-086 mutation was attempted.

Continued the permitted LAB-091 first-adoption compatibility audit and reproduced a new reachable supported-write defect: an additive legacy column with `DEFAULT (legacy_only())` can be created while a legacy deterministic UDF is registered; after reopen on the supported LAB-091 connection, which does not register that UDF, the next otherwise-valid canonical INSERT that omits the extra column fails with `sqlite3.OperationalError: unknown function: legacy_only()`.

Published on PR #173 through normal conflict-scoped Contents API writes:
- `5b9ce523611193120212a0d335edf33054bf8ece` — extend `adoption_extra_columns.py` to reject function-call defaults on non-canonical ordinary columns while retaining literal/default-keyword extras;
- `7551a6e80c677512da0093bd7ddd083f5189a516` — add `test_adoption_extra_default_regression.py` (current PR #173 head).

Re-fetched published files. Validator blob is `c5e6617bd7abf73864e31ec191451af0c281842b`; regression blob is `3c613366fdcb2f626d4d1c39af8060fb58bca760`. Locally recomputed Git object hashes exactly match those published identities.

Focused regression: **2/2 PASS**. Literal string, numeric, and `CURRENT_TIMESTAMP` defaults remain accepted; the legacy-only function default reproduces the pre-fix reopen failure and is now rejected before adoption. An unrelated spreadsheet-runtime warmup printed a timeout during Python startup, but unittest returned exit code 0 and both LAB-091 tests completed successfully. This is focused exact-candidate evidence, not whole-branch/full-stack execution.

Durable analysis: `research/2026-08-30-lab091-function-valued-extra-default-adoption-gap.md`, main commit `26bf7d0abeba60526f825e13486853cab43b5049`; issue #170 comment `5467112396`.

## Evidence retained

- LAB-080 18/18 PASS; LAB-082 28/28 PASS; LAB-083 24/24 PASS; LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS; asymmetric custody 8/8 PASS; public/final 11/11 PASS; unsafe lower baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; unsafe legacy auto-promotion failed as intended.
- LAB-086 hidden-rowid RED→GREEN evidence retained; exact predecessor -> exact candidate target previously byte-rederived and mechanism-tested; publication/full gate pending.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-091 accumulated adoption hardening now includes receipt affinity/collation, identity lookup collation, constructor ordering, restrictive UNIQUE/CHECK, required/generated extra columns, function-valued extra defaults, inherited foreign-key rejection, secondary-index collation rejection, and expression/partial secondary-index rejection, each with focused reproduced evidence.
- LAB-091 timeout/UNKNOWN and process concurrency/crash regressions remain pending full final-surface execution.

## Known blockers / constraints

- LAB-086 remains first priority. Do not manually/model-reserialize the 949-line security-critical `strict_fence.py`.
- Publish LAB-086 only by conflict-checking exact predecessor `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`, applying only the retained hidden-rowid patch through a byte-preserving supported path, requiring exact target `b78e7c98e35138719f77c482c7f1aab36b702de7`, then re-fetch/hash-verify and run the complete security gate.
- PR #165 remains draft until exact rowid publication/hash verification and full strict/thaw + LAB-080→086 real-ledger + compileall/security audit pass.
- PR #173 remains draft. Exact whole-branch regressions and full timeout/UNKNOWN + process concurrency/crash behavior remain pending executable transport.
- Do not represent focused local reconstruction/mechanism execution as byte-for-byte full-branch execution.
- Do not add speculative SQLite guards without a reproduced reachable supported compatibility/security failure.

## Exact next action

LAB-086 first: if a supported byte-preserving composition/transfer bridge appears, re-fetch predecessor `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`, apply only retained hidden-rowid patch, require exact target `b78e7c98e35138719f77c482c7f1aab36b702de7`, publish through normal Contents API, re-fetch/hash-verify, then run rowid + receipt-NULL + alternate-UNIQUE + complete strict/thaw + compileall + LAB-080→086 real-ledger gates. If that bridge remains unavailable, execute exact PR #173 head `7551a6e80c677512da0093bd7ddd083f5189a516` when whole-branch executable transport appears; otherwise continue first-adoption compatibility audit only for newly reproduced reachable supported-write failures. Next useful audit surface: other persisted schema expressions that execute on canonical writes, but harden only after a concrete supported-path reproduction.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; draft PR #172.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — IN_PROGRESS fallback; draft PR #173; function-valued extra-default hardening published; exact whole-branch/full behavioral gates pending.
