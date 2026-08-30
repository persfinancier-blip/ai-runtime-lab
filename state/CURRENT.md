# Current Lab State

Last updated: 2026-08-30

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165; branch `lab/086-asymmetric-break-glass-history`.
- Exact LAB-086 `strict_fence.py` predecessor remains blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; retained hidden-rowid patch `research/2026-08-28-lab086-hidden-rowid-replace.patch`, blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; exact target `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- LAB-090 / #169 is the current allowed fallback while LAB-086 byte-preserving publication is tool-limited. Draft PR #175; branch `lab-090-provider-activation-fencing`; latest hardening commits `3eb49db6f732d21da34a8b783dd603a62aa38a41` and `50e85e2eaa37fc0787cde48721363e46578c3051`.
- LAB-091 / #170 remains IN_PROGRESS fallback on draft PR #173.
- LAB-088 / #167 remains IN_PROGRESS on draft PR #172.

## Last completed step

Re-read `AGENTS.md`, this handoff, and `prompts/SELF_RESUME.md`; inspected open issues and active PRs. Direct git transport was probed again and failed before repository-code execution with `Could not resolve host: github.com`.

Resumed LAB-090 PR #175 and performed the requested narrow source audit. Found a historical existing-activation retry state-poisoning path: after later generation G3 became current, retrying a durable historical G2 activation could enter the existing-row reconciliation branch, assign `self.attested = new_attested`, and only then fail `_require_runtime_matches_durable_head()`. Authority remained fail-closed, but the live ledger object was left on stale runtime state and could cause avoidable persistent availability fallout.

Published minimal guard commit `3eb49db6f732d21da34a8b783dd603a62aa38a41`: an existing activation retry now checks `new.generation_id` against `provider_history.current().generation_id` before ticket reconciliation or runtime mutation. Historical activation retries fail with `InvalidTransition` while preserving the current runtime.

Published regression commit `50e85e2eaa37fc0787cde48721363e46578c3051`: `test_activation_historical_retry.py` performs G1→G2→G3, retries historical G2, requires failure, and asserts the live runtime remains G3.

A narrow provider-activation mechanism reconstruction executed 8/8 PASS locally. The reconstruction was semantically equivalent but not byte-verified against the published Git blobs, so it is not counted as an exact-head branch gate. The new historical-retry regression itself was not executed in this runtime.

Issue #169 updated in comment `5471029788`. Durable analysis: `research/2026-08-30-lab090-historical-activation-retry-state-poisoning.md`, main commit `b5ce32d62743424c4036d1cec9ba8d397e239b0c`.

## Evidence retained

- LAB-080 18/18 PASS; LAB-082 28/28 PASS; LAB-083 24/24 PASS; LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS; asymmetric custody 8/8 PASS; public/final 11/11 PASS; unsafe lower baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; hidden-rowid RED→GREEN evidence and exact predecessor/target derivation retained; publication/full gate pending.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-088 exact published signer-noise/core evidence remains 22/22 PASS + compileall; supported/downstream execution pending.
- LAB-091 accumulated adoption hardening/focused reproduced evidence retained; whole-branch timeout/UNKNOWN and process concurrency/crash gates pending.
- LAB-090 prior provider primitive focused mechanism evidence is retained; premature-release and overlapping-rotation hardening are published. Historical-retry state-poisoning guard and regression are now published. No new exact-head branch PASS is claimed in this run.

## Known blockers / constraints

- LAB-086 remains first priority. Do not manually/model-reserialize the 949-line security-critical `strict_fence.py`.
- Publish LAB-086 only by conflict-checking exact predecessor `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`, applying only the retained patch through a byte-preserving supported path, requiring exact target `b78e7c98e35138719f77c482c7f1aab36b702de7`, then re-fetch/hash-verify and run the complete security gate.
- Direct git/network transport remains unavailable due DNS in this run; treat this as a per-run observation.
- PR #175 remains draft. Exact-head focused/integration/downstream execution remains pending, including `test_activation_historical_retry.py`.

## Exact next action

LAB-086 first: if a supported byte-preserving composition/transfer bridge appears, publish and full-gate the exact hidden-rowid target. Otherwise resume LAB-090 PR #175 and attempt exact-head execution of `test_activation_historical_retry.py`, `test_activation_overlapping_rotation.py`, `test_activation.py`, `test_activation_integration.py`, `test_activation_premature_release.py`, provider-generation integration, and downstream shared-anchor/provider-history suites. If direct execution remains unavailable, perform one narrow fresh audit of constructor/restart recovery ordering and existing-activation retry idempotence; make no speculative protocol expansion and do not merge from source audit alone.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending on draft PR #172.
- #169 / LAB-090 — IN_PROGRESS; historical activation retry now fails before stale runtime mutation; exact-head executable gate pending on draft PR #175.
- #170 / LAB-091 — IN_PROGRESS fallback; draft PR #173; exact whole-branch/full behavioral gates pending.
