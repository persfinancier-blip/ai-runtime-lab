# Current Lab State

Last updated: 2026-08-30

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165; branch `lab/086-asymmetric-break-glass-history`.
- Exact LAB-086 `strict_fence.py` predecessor remains blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd` (949 lines).
- Retained hidden-rowid patch: `research/2026-08-28-lab086-hidden-rowid-replace.patch`, blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; exact previously derived target `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- LAB-091 / #170 is the allowed fallback while LAB-086 publication/execution is concretely tool-limited; draft PR #173, branch `lab/091-mutable-shared-anchor-writer`.
- Current LAB-091 branch head: `aad64cc350b5fdef44f941d0d2cffd22adf5b0f5`.
- LAB-088 / #167 remains IN_PROGRESS on draft PR #172. LAB-090 / #169 remains READY.

## Last completed step

Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected active issues/PRs. LAB-086 remains first priority. The connector now returns PR #165's complete 949-line `strict_fence.py` per-file patch, but there is still no observed supported byte-preserving operation that directly composes that fetched payload with the retained hidden-rowid patch and transfers the exact result into a normal Contents API write without model/manual whole-file reserialization. No LAB-086 mutation was attempted.

Continued the permitted LAB-091 first-adoption compatibility audit and reproduced a new reachable persisted-schema failure. A legacy process can create `shared_anchor_intents.status TEXT COLLATE LEGACY_ONLY` while registering an application-defined SQLite collation, commit, and close. Reopen through a supported LAB-091 connection does not recreate that collation. An otherwise-valid canonical INSERT then fails while SQLite evaluates a persisted comparison inheriting the column collation: `sqlite3.OperationalError: no such collation sequence: LEGACY_ONLY`.

Published on PR #173 through normal file-scoped Contents API writes:
- `6b700c55eb340c0902600fccb157995874279678` — add `adoption_column_collations.py` with zero-row collation-resolution probes for canonical TEXT columns;
- `fe3b69852b5ab0f00135c409e7bef3a6d6247efe` — wire the validator into the final adoption envelope;
- `aad64cc350b5fdef44f941d0d2cffd22adf5b0f5` — add `test_adoption_column_collation_regression.py` (current PR #173 head).

Re-fetched published files and recomputed Git object identities locally. Exact matches:
- validator blob `19b78a59fe3e8b3eae9f30eab15b00fff5584001`;
- regression blob `39e7246082c89636ad57c01e885f353d38d47927`.

Focused exact-published-byte regression: **2/2 PASS**. Canonical/default BINARY TEXT columns are accepted; the unavailable legacy-only status collation reproduces the pre-fix supported-shape INSERT failure and is rejected before adoption. An unrelated spreadsheet-runtime warmup printed a timeout during Python startup, but unittest returned exit code 0 and both LAB-091 tests completed successfully. This is focused exact-candidate evidence, not whole-branch/full-stack execution.

Durable analysis: `research/2026-08-30-lab091-unavailable-column-collation-adoption-gap.md`, main commit `7d289a7f760beb7b82d847697a6cd5f520e7db7b`; issue #170 comment `5467367050`.

## Evidence retained

- LAB-080 18/18 PASS; LAB-082 28/28 PASS; LAB-083 24/24 PASS; LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS; asymmetric custody 8/8 PASS; public/final 11/11 PASS; unsafe lower baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; unsafe legacy auto-promotion failed as intended.
- LAB-086 hidden-rowid RED→GREEN evidence retained; exact predecessor -> exact candidate target previously byte-rederived and mechanism-tested; publication/full gate pending.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-091 accumulated adoption hardening now includes receipt affinity/collation, identity lookup collation, constructor ordering, restrictive UNIQUE/CHECK, required/generated extra columns, function-valued extra defaults, inherited foreign-key rejection, secondary-index collation/expression/partial rejection, and unavailable persisted canonical-column collation rejection, each with focused reproduced evidence.
- LAB-091 timeout/UNKNOWN and process concurrency/crash regressions remain pending full final-surface execution.

## Known blockers / constraints

- LAB-086 remains first priority. Do not manually/model-reserialize the 949-line security-critical `strict_fence.py`.
- Publish LAB-086 only by conflict-checking exact predecessor `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`, applying only the retained hidden-rowid patch through a byte-preserving supported path, requiring exact target `b78e7c98e35138719f77c482c7f1aab36b702de7`, then re-fetch/hash-verify and run the complete security gate.
- PR #165 remains draft until exact rowid publication/hash verification and full strict/thaw + LAB-080→086 real-ledger + compileall/security audit pass.
- PR #173 remains draft. Exact whole-branch regressions and full timeout/UNKNOWN + process concurrency/crash behavior remain pending executable transport.
- Do not represent focused local reconstruction/mechanism execution as byte-for-byte full-branch execution.
- Do not add speculative SQLite guards without a reproduced reachable supported compatibility/security failure.

## Exact next action

LAB-086 first: if a supported byte-preserving composition/transfer bridge appears, re-fetch predecessor `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`, apply only retained hidden-rowid patch, require exact target `b78e7c98e35138719f77c482c7f1aab36b702de7`, publish through normal Contents API, re-fetch/hash-verify, then run rowid + receipt-NULL + alternate-UNIQUE + complete strict/thaw + compileall + LAB-080→086 real-ledger gates. If that bridge remains unavailable, execute exact PR #173 head `aad64cc350b5fdef44f941d0d2cffd22adf5b0f5` when whole-branch executable transport appears; otherwise continue first-adoption compatibility audit only for newly reproduced reachable supported-write failures. Next useful audit surface: remaining persisted table options/schema expressions that are executed implicitly by canonical writes, but harden only after concrete reproduction.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; draft PR #172.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — IN_PROGRESS fallback; draft PR #173; unavailable canonical-column collation hardening published; exact whole-branch/full behavioral gates pending.
