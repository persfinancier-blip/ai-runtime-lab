# Current Lab State

Last updated: 2026-08-30

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165; branch `lab/086-asymmetric-break-glass-history`.
- Authoritative LAB-086 `strict_fence.py` predecessor: `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`.
- Retained hidden-rowid patch: `research/2026-08-28-lab086-hidden-rowid-replace.patch`, blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; exact previously derived target `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- LAB-091 / #170 is the allowed fallback while LAB-086 publication/execution is concretely tool-limited; draft PR #173, branch `lab/091-mutable-shared-anchor-writer`.
- Current LAB-091 PR head: `bb2b3cb49bb2ac05e55a261b26b33f0db3166fc5`.
- LAB-088 / #167 remains IN_PROGRESS on draft PR #172. LAB-090 / #169 remains READY.

## Last completed step

Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected open issues/PRs. LAB-086 remains first priority, but no supported machine-to-machine byte-preserving composition path for the exact 949-line `strict_fence.py` predecessor plus retained patch was observed, so no LAB-086 mutation was attempted.

Continued the allowed LAB-091 first-adoption compatibility audit and reproduced another reachable write-domain defect: an otherwise canonical legacy `shared_anchor_intents` table with an additional `CHECK(component_id='component-a')` passes the previous affinity/NOT NULL/UNIQUE gate but rejects a supported-shape PREPARED insert for `component-b`. Extra legacy CHECK constraints can therefore narrow the normal supported writer contract after adoption.

Published on PR #173 through conflict-checked normal Contents API writes:
- `38df1258a3dc17d59efcc66f11db0e48bde05668` — `adoption_schema_domains.py` now extracts/normalizes legacy CHECK expressions and rejects any outside the canonical set; missing canonical CHECKs remain allowed because LAB-091 persisted guards re-impose those protected predicates;
- `bb2b3cb49bb2ac05e55a261b26b33f0db3166fc5` — added `test_adoption_restrictive_check_regression.py`; re-fetch confirms this is the current draft PR #173 head.

Executed focused local unittest against the exact prepared update/test payload before Contents API publication: **3/3 PASS** — canonical CHECK accepted, omitted canonical CHECK accepted for guard-compatible legacy adoption, restrictive extra CHECK reproduced a normal insert failure and was rejected by the hardened gate. This is focused payload/mechanism evidence, not an exact branch checkout/full pytest claim.

Durable analysis: `research/2026-08-30-lab091-restrictive-check-adoption-gap.md`, main commit `a6a7d050c798ad9f866513429d1174b07b0cdb0f`; issue #170 comment `5465716237`.

## Evidence retained

- LAB-080 18/18 PASS; LAB-082 28/28 PASS; LAB-083 24/24 PASS; LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS; asymmetric custody 8/8 PASS; public/final 11/11 PASS; unsafe lower baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; unsafe legacy auto-promotion failed as intended.
- LAB-086 hidden-rowid RED→GREEN evidence retained; exact predecessor `d4a6a40f...` -> candidate `b78e7c98...` previously byte-rederived and mechanism-tested; publication/full gate pending.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-091 earlier adoption hardening combined focused gate 17/17 PASS before later affinity/collation fixes.
- LAB-091 receipt affinity, receipt collation, identity lookup, constructor ordering, receipt-orphan collation, restrictive-UNIQUE and restrictive-CHECK defects now have published fixes with focused local semantic/mechanism evidence; latest exact branch regressions remain pending executable transport.
- LAB-091 timeout/UNKNOWN regression blob `92133cdc54fd8b95eb9e3270b5e69d4b85a4b05` and process concurrency/crash regression blob `938877479d4c4b997ea52e8b5857bf89e5c3e246` remain pending full final-surface execution.

## Known blockers / constraints

- LAB-086 remains first priority. Do not manually/model-reserialize the 949-line security-critical `strict_fence.py`.
- Publish LAB-086 only by conflict-checking exact predecessor `d4a6a40f...`, applying only the retained hidden-rowid patch through a byte-preserving supported path, requiring exact target `b78e7c98...`, then re-fetch/hash-verify and run the complete security gate.
- PR #165 remains draft until exact rowid publication/hash verification and full strict/thaw + LAB-080→086 real-ledger + compileall/security audit pass.
- PR #173 remains draft. Exact branch regressions, timeout/UNKNOWN, process concurrency/crash, receipt-affinity and receipt-collation final-surface gates remain pending executable transport.
- Do not represent focused local payload/mechanism execution as byte-for-byte branch execution.
- Do not add speculative SQLite guards without a reproduced reachable supported compatibility/security failure.

## Exact next action

LAB-086 first: if a supported byte-preserving composition/transfer bridge appears, re-fetch predecessor `d4a6a40f...`, apply only retained hidden-rowid patch, require exact target `b78e7c98...`, publish through normal Contents API, re-fetch/hash-verify, then run rowid + receipt-NULL + alternate-UNIQUE + complete strict/thaw + compileall + LAB-080→086 real-ledger gates. If that bridge is still unavailable, execute exact PR #173 head `bb2b3cb49bb2ac05e55a261b26b33f0db3166fc5` when executable transport appears, beginning with `test_adoption_restrictive_check_regression.py`; if exact execution remains unavailable, continue first-adoption compatibility audit only for reproduced reachable supported-write failures.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; draft PR #172.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — IN_PROGRESS fallback; draft PR #173; restrictive-CHECK hardening published; exact branch/full behavioral gates pending.
