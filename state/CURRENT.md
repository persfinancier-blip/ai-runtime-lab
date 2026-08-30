# Current Lab State

Last updated: 2026-08-30

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165; branch `lab/086-asymmetric-break-glass-history`.
- Exact LAB-086 `strict_fence.py` predecessor remains blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd` (949 lines).
- Retained hidden-rowid patch: `research/2026-08-28-lab086-hidden-rowid-replace.patch`, blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; exact previously derived target `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- LAB-091 / #170 is the allowed fallback while LAB-086 publication/execution is concretely tool-limited; draft PR #173, branch `lab/091-mutable-shared-anchor-writer`.
- Current LAB-091 branch head after this run: `ff6abe5893b203ebdc978b3db08a1dc8bd950c26`.
- LAB-088 / #167 remains IN_PROGRESS on draft PR #172. LAB-090 / #169 remains READY.

## Last completed step

Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected active PRs. LAB-086 remains first priority, but this run still exposed no supported byte-preserving composition/transfer bridge that can apply the retained hidden-rowid patch to the exact 949-line security-critical predecessor and publish the exact expected target without model/manual reserialization. No LAB-086 mutation was attempted.

Continued the permitted LAB-091 first-adoption compatibility audit. Reproduced two new reachable supported-write defects from inherited non-UNIQUE secondary indexes:

- expression index using a deterministic legacy-only UDF, e.g. `ON shared_anchor_intents(legacy_only(component_id))`;
- partial index whose predicate uses the same legacy-only UDF.

Both can be created by a legacy connection while the deterministic function is registered. After reopen on the supported LAB-091 connection, which does not register that legacy-only function, the next otherwise-valid supported INSERT fails while SQLite maintains the inherited index with `sqlite3.OperationalError: unknown function: legacy_only()`.

Published on PR #173 through normal conflict-scoped Contents API writes:
- `7971901b949884e5218a91f0ce4472584f432822` — extend `adoption_secondary_indexes.py` to reject non-UNIQUE expression and partial indexes on protected mutable tables while retaining ordinary column-only/BINARY secondary indexes;
- `ff6abe5893b203ebdc978b3db08a1dc8bd950c26` — add `test_adoption_secondary_index_expression_partial_regression.py` (current PR #173 head).

Re-fetched published validator/test. Published validator blob is `593a018da8471070e6b0c7606a32623c585b00d4`; regression blob is `b50a92555a0df86c7b589a2123d9d94fd7c411a1`. The validator text was reconstructed locally and its Git object identity recomputed exactly as `593a018da8471070e6b0c7606a32623c585b00d4` before execution.

Focused mechanism gate:
- expression index: pre-fix supported-shape INSERT -> `OperationalError: unknown function: legacy_only()`; adoption -> rejected;
- partial index: same pre-fix failure; adoption -> rejected;
- ordinary BINARY column-only secondary index -> accepted.

This is focused exact-validator/mechanism evidence, not whole-branch/full-stack execution.

Durable analysis: `research/2026-08-30-lab091-expression-partial-secondary-index-adoption-gap.md`, main commit `e8aff16a1f54eb08ed8b5b13e2755db887361666`; issue #170 comment `5466893347`.

## Evidence retained

- LAB-080 18/18 PASS; LAB-082 28/28 PASS; LAB-083 24/24 PASS; LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS; asymmetric custody 8/8 PASS; public/final 11/11 PASS; unsafe lower baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; unsafe legacy auto-promotion failed as intended.
- LAB-086 hidden-rowid RED→GREEN evidence retained; exact predecessor -> exact candidate target previously byte-rederived and mechanism-tested; publication/full gate pending.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-091 accumulated adoption hardening now includes receipt affinity/collation, identity lookup collation, constructor ordering, restrictive UNIQUE/CHECK, required/generated extra columns, inherited foreign-key rejection, secondary-index collation rejection, and expression/partial secondary-index rejection, each with focused reproduced evidence.
- LAB-091 timeout/UNKNOWN and process concurrency/crash regressions remain pending full final-surface execution.

## Known blockers / constraints

- LAB-086 remains first priority. Do not manually/model-reserialize the 949-line security-critical `strict_fence.py`.
- Publish LAB-086 only by conflict-checking exact predecessor `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`, applying only the retained hidden-rowid patch through a byte-preserving supported path, requiring exact target `b78e7c98e35138719f77c482c7f1aab36b702de7`, then re-fetch/hash-verify and run the complete security gate.
- PR #165 remains draft until exact rowid publication/hash verification and full strict/thaw + LAB-080→086 real-ledger + compileall/security audit pass.
- PR #173 remains draft. Exact whole-branch regressions and full timeout/UNKNOWN + process concurrency/crash behavior remain pending executable transport.
- Do not represent focused local reconstruction/mechanism execution as byte-for-byte full-branch execution.
- Do not add speculative SQLite guards without a reproduced reachable supported compatibility/security failure.

## Exact next action

LAB-086 first: if a supported byte-preserving composition/transfer bridge appears, re-fetch predecessor `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`, apply only retained hidden-rowid patch, require exact target `b78e7c98e35138719f77c482c7f1aab36b702de7`, publish through normal Contents API, re-fetch/hash-verify, then run rowid + receipt-NULL + alternate-UNIQUE + complete strict/thaw + compileall + LAB-080→086 real-ledger gates. If that bridge remains unavailable, execute exact PR #173 head `ff6abe5893b203ebdc978b3db08a1dc8bd950c26` when whole-branch executable transport appears; otherwise continue first-adoption compatibility audit only for newly reproduced reachable supported-write failures. Next useful audit surface: inherited views/triggers or index SQL dependencies not already covered, but harden only after a concrete supported-path reproduction.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; draft PR #172.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — IN_PROGRESS fallback; draft PR #173; secondary-index expression/partial hardening published; exact whole-branch/full behavioral gates pending.
