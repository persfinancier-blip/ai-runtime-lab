# Current Lab State

Last updated: 2026-08-31

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165; branch `lab/086-asymmetric-break-glass-history`.
- Exact LAB-086 `strict_fence.py` predecessor remains blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; retained hidden-rowid patch `research/2026-08-28-lab086-hidden-rowid-replace.patch`, blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; exact target `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- LAB-090 / #169 is the current allowed fallback while LAB-086 byte-preserving publication is tool-limited. Draft PR #175; branch `lab-090-provider-activation-fencing`; current head now includes regression commit `0cbbfd2477db1774b0cadc5294cd85c2b5495d17`.
- LAB-091 / #170 remains IN_PROGRESS fallback on draft PR #173.
- LAB-088 / #167 remains IN_PROGRESS on draft PR #172.

## Last completed step

Re-read `AGENTS.md`, this handoff, and `prompts/SELF_RESUME.md`; inspected open issues and active PRs. GitHub connector confirmed PR #175 head before this run's regression was `50e85e2eaa37fc0787cde48721363e46578c3051`, draft and mergeable. Direct raw/git filesystem transport was probed again and still failed on DNS before repository-code execution.

Resumed the exact requested LAB-090 narrow constructor/restart audit. Found a legacy/upgrade state that the prospective overlapping-rotation guard does not repair: a DB produced by the older vulnerable scheduler can already have historical G2 activation `SQL_COMMITTED` while provider-generation head is G3. The current constructor recovers only the durable current generation; `_verify_activation_records()` accepts historical `SQL_COMMITTED`; the persisted global activation trigger then blocks all new shared-anchor intents and the overlapping-rotation guard blocks new rotations. Because the current runtime is G3, ordinary recovery cannot reconcile the historical G2 provider reservation. Construction can therefore succeed into a permanently unavailable state.

Published expected-RED regression `experiments/provider_generation_history/tests/test_activation_historical_unresolved_restart.py` on PR #175, commit `0cbbfd2477db1774b0cadc5294cd85c2b5495d17`. It creates valid G1→G2→G3 history, seeds the pre-fix durable shape by restoring G2 activation status to `SQL_COMMITTED`, and requires restart with valid current G3 runtime to raise `HistoricalVerificationError` rather than silently construct an indefinitely blocked ledger.

Issue #169 updated in comment `5471311412`. Durable analysis: `research/2026-08-31-lab090-historical-unresolved-activation-restart.md`, main commit `b01dba382e9ad036dfec7ef212c1dbc66f4cde29`.

## Evidence retained

- LAB-080 18/18 PASS; LAB-082 28/28 PASS; LAB-083 24/24 PASS; LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS; asymmetric custody 8/8 PASS; public/final 11/11 PASS; unsafe lower baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; hidden-rowid RED→GREEN evidence and exact predecessor/target derivation retained; publication/full gate pending.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-088 exact published signer-noise/core evidence remains 22/22 PASS + compileall; supported/downstream execution pending.
- LAB-091 accumulated adoption hardening/focused reproduced evidence retained; whole-branch timeout/UNKNOWN and process concurrency/crash gates pending.
- LAB-090 provider primitive, premature-release, overlapping-rotation, and historical-retry hardening remain published. New historical-unresolved restart regression is published but not executed; no exact-head PASS is claimed.

## Known blockers / constraints

- LAB-086 remains first priority. Do not manually/model-reserialize the 949-line security-critical `strict_fence.py`.
- Publish LAB-086 only by conflict-checking exact predecessor `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`, applying only the retained patch through a byte-preserving supported path, requiring exact target `b78e7c98e35138719f77c482c7f1aab36b702de7`, then re-fetch/hash-verify and run the complete security gate.
- Direct git/raw network transport remains unavailable due DNS in this run; treat this as a per-run observation. GitHub connector can read exact commit/tree/blob metadata, but no connector-to-local byte materialization bridge was available for executing the repository without manual reserialization.
- PR #175 remains draft. The newly found historical unresolved activation restart defect is open; exact-head focused/integration/downstream execution remains pending.

## Exact next action

LAB-086 first: if a supported byte-preserving composition/transfer bridge appears, publish and full-gate the exact hidden-rowid target. Otherwise resume LAB-090 PR #175: minimally harden `_verify_activation_records()` so that, after current-generation recovery, any `status='SQL_COMMITTED'` activation whose `new_generation_id` is not the durable current generation fails restart with `HistoricalVerificationError`; do not auto-clear or auto-reconcile historical provider activation state. Then execute `test_activation_historical_unresolved_restart.py` plus historical-retry, overlapping-rotation, activation primitive/integration/premature-release, provider-generation integration, and downstream shared-anchor/provider-history suites from exact published bytes before considering PR #175 ready.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending on draft PR #172.
- #169 / LAB-090 — IN_PROGRESS; historical unresolved activation restart defect now has expected-RED regression on draft PR #175; minimal fail-closed verifier fix and exact executable gate pending.
- #170 / LAB-091 — IN_PROGRESS fallback; draft PR #173; exact whole-branch/full behavioral gates pending.
