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

Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected active issues/PRs. LAB-086 remains first priority. Re-probed the preferred executable transport: local `git ls-remote https://github.com/persfinancier-blip/ai-runtime-lab.git HEAD` still fails with `Could not resolve host: github.com`. The GitHub connector remains readable/writable, but no supported byte-preserving operation appeared that composes the exact fetched 949-line predecessor with the retained hidden-rowid patch and transfers the exact result into a Contents API write without model/manual whole-file reserialization. No LAB-086 mutation was attempted.

Continued the permitted LAB-091 first-adoption compatibility audit at exact PR #173 head `aad64cc350b5fdef44f941d0d2cffd22adf5b0f5`, focusing on remaining table-level/schema-expression surfaces. Re-read the canonical schema, adoption validators and v2/v3/v4 guards, then locally probed canonical write shape against: canonical tables, `STRICT`, `WITHOUT ROWID`, built-in `NOCASE` on `status`, and `PRIMARY KEY ON CONFLICT REPLACE` on `intent_id`. Every variant completed canonical singleton insert -> PREPARED intent insert -> tail advance -> PREPARED->CONFIRMED update with final row `('CONFIRMED', 'b')`.

No reachable supported-write failure or permit/security bypass was reproduced, so no speculative schema guard was added. This negative result is deliberate evidence under the repository rule not to harden arbitrary SQLite variants without a concrete failure.

Durable analysis: `research/2026-08-30-lab091-table-options-negative-audit.md`, main commit `05ae280499edf2e61f714f873f8f27de96e3c6a8`; issue #170 comment `5467604263`.

## Evidence retained

- LAB-080 18/18 PASS; LAB-082 28/28 PASS; LAB-083 24/24 PASS; LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS; asymmetric custody 8/8 PASS; public/final 11/11 PASS; unsafe lower baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; unsafe legacy auto-promotion failed as intended.
- LAB-086 hidden-rowid RED→GREEN evidence retained; exact predecessor -> exact candidate target previously byte-rederived and mechanism-tested; publication/full gate pending.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-091 accumulated adoption hardening includes receipt affinity/collation, identity lookup collation, constructor ordering, restrictive UNIQUE/CHECK, required/generated extra columns, function-valued extra defaults, inherited foreign-key rejection, secondary-index collation/expression/partial rejection, and unavailable persisted canonical-column collation rejection, each with focused reproduced evidence.
- LAB-091 table-options negative audit: canonical, STRICT, WITHOUT ROWID, status NOCASE, and PK ON CONFLICT REPLACE all preserved the tested canonical supported write shape; no hardening added.
- LAB-091 timeout/UNKNOWN and process concurrency/crash regressions remain pending full final-surface execution.

## Known blockers / constraints

- LAB-086 remains first priority. Do not manually/model-reserialize the 949-line security-critical `strict_fence.py`.
- Publish LAB-086 only by conflict-checking exact predecessor `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`, applying only the retained hidden-rowid patch through a byte-preserving supported path, requiring exact target `b78e7c98e35138719f77c482c7f1aab36b702de7`, then re-fetch/hash-verify and run the complete security gate.
- PR #165 remains draft until exact rowid publication/hash verification and full strict/thaw + LAB-080→086 real-ledger + compileall/security audit pass.
- PR #173 remains draft. Exact whole-branch regressions and full timeout/UNKNOWN + process concurrency/crash behavior remain pending executable transport.
- Do not represent focused local mechanism execution as byte-for-byte full-branch execution.
- Do not add speculative SQLite guards without a reproduced reachable supported compatibility/security failure.

## Exact next action

LAB-086 first: if a supported byte-preserving composition/transfer bridge appears, re-fetch predecessor `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`, apply only retained hidden-rowid patch, require exact target `b78e7c98e35138719f77c482c7f1aab36b702de7`, publish through normal Contents API, re-fetch/hash-verify, then run rowid + receipt-NULL + alternate-UNIQUE + complete strict/thaw + compileall + LAB-080→086 real-ledger gates. If that bridge remains unavailable, execute exact PR #173 head `aad64cc350b5fdef44f941d0d2cffd22adf5b0f5` when whole-branch executable transport appears; otherwise continue the first-adoption audit only when a persisted schema expression/table feature can be concretely reproduced as either a canonical supported-write failure after adoption or an exact LAB-091 invariant bypass.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; draft PR #172.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — IN_PROGRESS fallback; draft PR #173; no new patch this run because table-option probes were negative; exact whole-branch/full behavioral gates pending.
