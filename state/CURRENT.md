# Current Lab State

Last updated: 2026-08-30

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165; branch `lab/086-asymmetric-break-glass-history`.
- Exact LAB-086 `strict_fence.py` predecessor remains blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd` (949 lines); retained hidden-rowid patch `research/2026-08-28-lab086-hidden-rowid-replace.patch`, blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; exact target `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- LAB-090 / #169 is the current allowed fallback while LAB-086 byte-preserving publication is tool-limited. Draft PR #175; branch `lab-090-provider-activation-fencing`; current head `5f680da36733a54b6d79d554a083276a1643a0ce`.
- LAB-091 / #170 remains IN_PROGRESS fallback on draft PR #173, branch `lab/091-mutable-shared-anchor-writer`, head last verified `aad64cc350b5fdef44f941d0d2cffd22adf5b0f5`.
- LAB-088 / #167 remains IN_PROGRESS on draft PR #172; source audit clean, downstream execution pending.

## Last completed step

Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected #169, PR #175 and the exact provider-generation/shared-anchor code. Direct branch transport was probed again with `git clone --depth 1 --branch lab-090-provider-activation-fencing ...` and failed before repository execution with `Could not resolve host: github.com`. LAB-086 therefore remains blocked by the same byte-preserving composition/transfer constraint and was not mutated.

Advanced LAB-090 on PR #175. The earlier provider-owned activation primitive is now wired into `SupportedHistoricalSharedAnchorLedger.rotate_provider()`: provider `prepare_activation(expected_position, activation_id)` occurs before SQL rotation; the exact activation ticket/fence is persisted in the same SQLite commit as provider generation history/head; SQL-side failure, changed tail or existing PREPARED intent aborts the provider reservation; provider commit UNKNOWN reconciles by exact ticket status; `SQL_COMMITTED` activation survives restart and is reconciled before normal work resumes.

Audit found a post-SQL/pre-provider-commit writer window. Fixed it with a SQLite trigger that rejects inserts into `shared_anchor_intents` while any activation remains `SQL_COMMITTED`, translated to `PendingRotationBlocked` on the supported API. Independent local SQLite mechanism check passed: unresolved activation blocked insert; changing status to COMMITTED released it. Audit also removed an over-strong global fence-uniqueness assumption across generations; fence validity is now scoped to the exact provider-generation ticket.

Added `experiments/provider_generation_history/tests/test_activation_integration.py` covering attempted external advance, stale candidate, SQL failure/abort, UNKNOWN-after-provider-commit, unresolved writer block and restart reconciliation. Existing provider-generation integration rotations on the branch now use `FencedActivationProvider`. Exact published-branch unittest execution is still NOT claimed because direct git transport is unavailable.

Durable evidence: `research/2026-08-30-lab090-durable-activation-ticket-integration.md`, main commit `fbac6de0de48552583decc95383a483bc333d0bd`; issue #169 comment `5468671747`. PR #175 remains draft.

## Evidence retained

- LAB-080 18/18 PASS; LAB-082 28/28 PASS; LAB-083 24/24 PASS; LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS; asymmetric custody 8/8 PASS; public/final 11/11 PASS; unsafe lower baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; hidden-rowid RED→GREEN evidence and exact predecessor/target derivation retained; publication/full gate pending.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-088 exact published signer-noise/core evidence remains 22/22 PASS + compileall; fresh PR-diff semantic audit CLEAN; supported/downstream execution pending.
- LAB-091 accumulated adoption hardening and focused reproduced evidence remain retained; whole-branch timeout/UNKNOWN and process concurrency/crash gates pending.
- LAB-090 provider primitive focused mechanism gate remains 6/6 PASS from the prior run. New coordinator integration is source-audited and has a focused SQLite trigger mechanism PASS, but no exact whole-branch execution yet.

## Known blockers / constraints

- LAB-086 remains first priority. Do not manually/model-reserialize the 949-line security-critical `strict_fence.py`.
- Publish LAB-086 only by conflict-checking exact predecessor `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`, applying only the retained patch through a byte-preserving supported path, requiring exact target `b78e7c98e35138719f77c482c7f1aab36b702de7`, then re-fetch/hash-verify and run the complete security gate.
- Direct git/network transport is currently unavailable due DNS; treat this as a per-run observation.
- PR #175 remains draft until the exact published branch and relevant downstream suites can execute. Do not represent focused mechanism checks or source audit as byte-for-byte branch behavioral execution.
- LAB-090 cannot be solved by SQLite locking or a second external read alone. The provider owns the external position precondition/reservation/fence; SQLite durably binds the exact ticket to generation rotation and blocks coordinator writers while provider commit is unresolved.

## Exact next action

LAB-086 first: if a supported byte-preserving composition/transfer bridge appears, publish and full-gate the exact hidden-rowid target as already specified. Otherwise resume LAB-090 PR #175 by probing direct branch transport; if available, run the exact provider-generation history suite plus relevant shared-anchor/downstream suites and compile checks, fix any failures, then perform a fresh semantic/security audit. If direct branch execution is still unavailable, inspect the current PR #175 source for one additional concrete restart/concurrency defect only; do not add speculative guards. Keep PR #175 draft until exact behavioral evidence exists.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending on draft PR #172.
- #169 / LAB-090 — IN_PROGRESS; durable activation-ticket coordinator integration implemented on draft PR #175; exact branch/downstream execution pending.
- #170 / LAB-091 — IN_PROGRESS fallback; draft PR #173; exact whole-branch/full behavioral gates pending.
