# Current Lab State

Last updated: 2026-08-30

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165; branch `lab/086-asymmetric-break-glass-history`.
- Exact LAB-086 `strict_fence.py` predecessor remains blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd` (949 lines).
- Retained hidden-rowid patch: `research/2026-08-28-lab086-hidden-rowid-replace.patch`, blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; exact previously derived target `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- LAB-091 / #170 is the allowed fallback while LAB-086 publication/execution is concretely tool-limited; draft PR #173, branch `lab/091-mutable-shared-anchor-writer`.
- Current LAB-091 branch head after this run: `eb832145e7e33021b9d03b3269da04d15ca0eae1`.
- LAB-088 / #167 remains IN_PROGRESS on draft PR #172. LAB-090 / #169 remains READY.

## Last completed step

Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected active PRs. PR #165 still exposes `strict_fence.py` as an addition relative to `main`, and the per-file PR patch returns the complete current 949-line source. Branch re-fetch confirms the exact predecessor blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; the retained hidden-rowid patch re-fetch confirms blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`. However, no supported bridge in this run can automatically transfer the connector-returned full source into local patch application and back into the Contents API without model/manual reserialization. Because this is security-critical, no LAB-086 mutation was attempted.

Continued the permitted LAB-091 first-adoption compatibility audit. Reproduced a reachable defect: a canonical-shaped legacy protected table can add a FOREIGN KEY on a canonical column. With `PRAGMA foreign_keys=ON`, `shared_anchor_intents.component_id REFERENCES legacy_components(component_id)` makes the next otherwise-valid supported INSERT fail with `sqlite3.IntegrityError: FOREIGN KEY constraint failed`, while the previous adoption envelope did not inspect `PRAGMA foreign_key_list`.

Published on PR #173 through normal conflict-scoped Contents API writes:
- `26c2ab079d1b316d0c067782f94c147842b0c5ff` — new `adoption_foreign_keys.py`, rejecting inherited foreign keys on all protected mutable tables fail-closed;
- `0d7166550d7744c37f5262e0948c41f073f7fe3f` — wire the validator into the final `BEGIN IMMEDIATE` adoption/restart envelope;
- `eb832145e7e33021b9d03b3269da04d15ca0eae1` — add `test_adoption_foreign_key_regression.py` (current branch head at publication time).

Re-fetched published blobs: validator `18cbb38e23b027618b0abec74f1f824ee26faf6a`, regression `6c76d91b389afde1338d86b906313ac58a435fe6`. Reconstructed those exact contents in an isolated temporary package and executed focused unittest: **2/2 PASS**. Canonical no-FK schema accepted; restrictive legacy FK reproduced the pre-fix supported-write failure and is now rejected. Python emitted an unrelated spreadsheet-runtime warmup traceback, but unittest returned 0 and both tests were `ok`. This is focused exact-content evidence, not whole-branch/full-stack execution.

Durable analysis: `research/2026-08-30-lab091-foreign-key-adoption-gap.md`, main commit `253f0aff41f8499d2e2b478d007b4b90f1be2ede`; issue #170 comment `5466446078`.

## Evidence retained

- LAB-080 18/18 PASS; LAB-082 28/28 PASS; LAB-083 24/24 PASS; LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS; asymmetric custody 8/8 PASS; public/final 11/11 PASS; unsafe lower baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; unsafe legacy auto-promotion failed as intended.
- LAB-086 hidden-rowid RED→GREEN evidence retained; exact predecessor -> exact candidate target previously byte-rederived and mechanism-tested; publication/full gate pending.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-091 accumulated adoption hardening now includes receipt affinity/collation, identity lookup collation, constructor ordering, restrictive UNIQUE/CHECK, required/generated extra columns, and inherited foreign-key rejection, each with focused reproduced evidence.
- LAB-091 timeout/UNKNOWN and process concurrency/crash regressions remain pending full final-surface execution.

## Known blockers / constraints

- LAB-086 remains first priority. Do not manually/model-reserialize the 949-line security-critical `strict_fence.py`.
- Publish LAB-086 only by conflict-checking exact predecessor `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`, applying only the retained hidden-rowid patch through a byte-preserving supported path, requiring exact target `b78e7c98e35138719f77c482c7f1aab36b702de7`, then re-fetch/hash-verify and run the complete security gate.
- PR #165 remains draft until exact rowid publication/hash verification and full strict/thaw + LAB-080→086 real-ledger + compileall/security audit pass.
- PR #173 remains draft. Exact whole-branch regressions and full timeout/UNKNOWN + process concurrency/crash behavior remain pending executable transport.
- Do not represent focused local reconstruction/mechanism execution as byte-for-byte full-branch execution.
- Do not add speculative SQLite guards without a reproduced reachable supported compatibility/security failure.

## Exact next action

LAB-086 first: if a supported byte-preserving composition/transfer bridge appears, re-fetch predecessor `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`, apply only retained hidden-rowid patch, require exact target `b78e7c98e35138719f77c482c7f1aab36b702de7`, publish through normal Contents API, re-fetch/hash-verify, then run rowid + receipt-NULL + alternate-UNIQUE + complete strict/thaw + compileall + LAB-080→086 real-ledger gates. If that bridge remains unavailable, execute exact PR #173 head `eb832145e7e33021b9d03b3269da04d15ca0eae1` when whole-branch executable transport appears; otherwise continue first-adoption compatibility audit only for newly reproduced reachable supported-write failures.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; draft PR #172.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — IN_PROGRESS fallback; draft PR #173; foreign-key adoption hardening published; exact whole-branch/full behavioral gates pending.
