# Current Lab State

Last updated: 2026-08-30

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165; branch `lab/086-asymmetric-break-glass-history`.
- Exact LAB-086 `strict_fence.py` predecessor remains blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd` (949 lines).
- Retained hidden-rowid patch: `research/2026-08-28-lab086-hidden-rowid-replace.patch`, blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; exact previously derived target `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- LAB-091 / #170 is the allowed fallback while LAB-086 publication/execution is concretely tool-limited; draft PR #173, branch `lab/091-mutable-shared-anchor-writer`.
- Current LAB-091 branch head after this run: `7c815210730c7d04be039eea9766115821e68781`.
- LAB-088 / #167 remains IN_PROGRESS on draft PR #172. LAB-090 / #169 remains READY.

## Last completed step

Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected active PR #165 and fallback PR #173. LAB-086 remains first priority, but this run still exposed no supported byte-preserving composition/transfer bridge that can apply the retained hidden-rowid patch to the exact 949-line security-critical predecessor and publish the exact expected target without model/manual reserialization. No LAB-086 mutation was attempted.

Continued the permitted LAB-091 first-adoption compatibility audit and reproduced a new reachable supported-write defect: a legacy protected table may contain a non-UNIQUE secondary index using a legacy-only custom collation. SQLite maintains that index during INSERT/UPDATE; after reopen on a LAB-091 connection where the custom collation is not registered, the next otherwise-valid supported INSERT fails with `sqlite3.OperationalError: no such collation sequence: LEGACY_ONLY`. Earlier adoption checks covered UNIQUE/PK identity indexes but not non-UNIQUE secondary indexes.

Published on PR #173 through normal conflict-scoped Contents API writes:
- `7e575ec5c14d9184661f4acdba9fdb6b9161bd8e` — add `adoption_secondary_indexes.py`, rejecting inherited non-BINARY collations on non-UNIQUE indexes for protected mutable tables;
- `b909c6ff52014f65d797fde19d6aa0ce55ae7004` — wire the validator into the final `BEGIN IMMEDIATE` adoption/restart envelope;
- `7c815210730c7d04be039eea9766115821e68781` — add `test_adoption_secondary_index_collation_regression.py` (current PR #173 head).

Re-fetched published blobs and verified exact Git object identities before execution:
- validator `fa74904a6264a5eb3d888b02d398b27959321fff`;
- regression `1924e25bde8c20e502686b9e5b309c45327287e6`.
Focused exact-content unittest: **2/2 PASS**. Canonical schema plus ordinary BINARY secondary index is accepted; custom-collation secondary index reproduces the pre-fix supported-write failure and is now rejected at adoption. Python emitted the known unrelated spreadsheet-runtime warmup timeout, but unittest returned 0 and both tests were `ok`. This is focused exact-content evidence, not whole-branch/full-stack execution.

Durable analysis: `research/2026-08-30-lab091-secondary-index-collation-adoption-gap.md`, main commit `438a7e956eb27729e39e4c8b65604b458652a686`; issue #170 comment `5466667342`.

## Evidence retained

- LAB-080 18/18 PASS; LAB-082 28/28 PASS; LAB-083 24/24 PASS; LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS; asymmetric custody 8/8 PASS; public/final 11/11 PASS; unsafe lower baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; unsafe legacy auto-promotion failed as intended.
- LAB-086 hidden-rowid RED→GREEN evidence retained; exact predecessor -> exact candidate target previously byte-rederived and mechanism-tested; publication/full gate pending.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-091 accumulated adoption hardening now includes receipt affinity/collation, identity lookup collation, constructor ordering, restrictive UNIQUE/CHECK, required/generated extra columns, inherited foreign-key rejection, and non-UNIQUE secondary-index collation rejection, each with focused reproduced evidence.
- LAB-091 timeout/UNKNOWN and process concurrency/crash regressions remain pending full final-surface execution.

## Known blockers / constraints

- LAB-086 remains first priority. Do not manually/model-reserialize the 949-line security-critical `strict_fence.py`.
- Publish LAB-086 only by conflict-checking exact predecessor `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`, applying only the retained hidden-rowid patch through a byte-preserving supported path, requiring exact target `b78e7c98e35138719f77c482c7f1aab36b702de7`, then re-fetch/hash-verify and run the complete security gate.
- PR #165 remains draft until exact rowid publication/hash verification and full strict/thaw + LAB-080→086 real-ledger + compileall/security audit pass.
- PR #173 remains draft. Exact whole-branch regressions and full timeout/UNKNOWN + process concurrency/crash behavior remain pending executable transport.
- Do not represent focused local reconstruction/mechanism execution as byte-for-byte full-branch execution.
- Do not add speculative SQLite guards without a reproduced reachable supported compatibility/security failure.

## Exact next action

LAB-086 first: if a supported byte-preserving composition/transfer bridge appears, re-fetch predecessor `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`, apply only retained hidden-rowid patch, require exact target `b78e7c98e35138719f77c482c7f1aab36b702de7`, publish through normal Contents API, re-fetch/hash-verify, then run rowid + receipt-NULL + alternate-UNIQUE + complete strict/thaw + compileall + LAB-080→086 real-ledger gates. If that bridge remains unavailable, execute exact PR #173 head `7c815210730c7d04be039eea9766115821e68781` when whole-branch executable transport appears; otherwise continue first-adoption compatibility audit only for newly reproduced reachable supported-write failures. Candidate next audit surface: non-UNIQUE expression/partial indexes, but harden only after reproducing a supported-write failure.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; draft PR #172.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — IN_PROGRESS fallback; draft PR #173; secondary-index collation adoption hardening published; exact whole-branch/full behavioral gates pending.
