# Current Lab State

Last updated: 2026-08-31

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165; branch `lab/086-asymmetric-break-glass-history`.
- Exact LAB-086 `strict_fence.py` predecessor remains blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; retained hidden-rowid patch `research/2026-08-28-lab086-hidden-rowid-replace.patch`, blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; exact target `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- LAB-090 / #169 remains the current allowed fallback while LAB-086 byte-preserving publication/execution is tool-limited. Draft PR #175; branch `lab-090-provider-activation-fencing`; current head `d6c9306d7df5ef106be1bfaca85eefe8236b7b6a`.
- LAB-091 / #170 remains IN_PROGRESS fallback on draft PR #173.
- LAB-088 / #167 remains IN_PROGRESS on draft PR #172.

## Last completed step

Re-read `AGENTS.md`, this handoff, and `prompts/SELF_RESUME.md`; inspected open issues and active PRs. LAB-086 remained first priority. The GitHub connector successfully returned the exact predecessor blob `d4a6a40f...`, but no supported operation in this run could compose that fetched 949-line security-critical blob with the retained unified patch and publish the exact target without model/manual reserialization. Direct `git ls-remote` was probed and still failed on DNS before repository-code execution (`Could not resolve host: github.com`). No LAB-086 branch mutation was attempted.

Resumed the exact LAB-090 next action. Confirmed on PR #175 head `0cbbfd2477db1774b0cadc5294cd85c2b5495d17` that `_recover_pending_activation()` reconciles only the durable current generation while `_verify_activation_records()` accepted historical `SQL_COMMITTED`. Published the minimal fail-closed fix in commit `d6c9306d7df5ef106be1bfaca85eefe8236b7b6a`: `_verify_activation_records()` now reads the durable current head and rejects any remaining `SQL_COMMITTED` activation whose `new_generation_id` is not current. It does not auto-clear or infer historical provider state. GitHub commit diff confirms only this guard changed.

The previously published regression `test_activation_historical_unresolved_restart.py` remains the focused executable requirement. Exact-head execution was not possible because direct git transport is still DNS-blocked; no unittest/compileall PASS is claimed.

Issue #169 updated in comment `5471594844`. Durable evidence: `research/2026-08-31-lab090-historical-unresolved-restart-fail-closed-fix.md`, main commit `63ae677f972a864486a4fee5030666d30436f41e`.

## Evidence retained

- LAB-080 18/18 PASS; LAB-082 28/28 PASS; LAB-083 24/24 PASS; LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS; asymmetric custody 8/8 PASS; public/final 11/11 PASS; unsafe lower baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; hidden-rowid RED→GREEN evidence and exact predecessor/target derivation retained; publication/full gate pending.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-088 exact published signer-noise/core evidence remains 22/22 PASS + compileall; supported/downstream execution pending.
- LAB-091 accumulated adoption hardening/focused reproduced evidence retained; whole-branch timeout/UNKNOWN and process concurrency/crash gates pending.
- LAB-090 provider primitive, premature-release, overlapping-rotation, historical-retry, and historical-unresolved restart hardening are published. The latest historical-unresolved verifier fix has an audited minimal GitHub diff but has not been executed from exact PR-head bytes.

## Known blockers / constraints

- LAB-086 remains first priority. Do not manually/model-reserialize the 949-line security-critical `strict_fence.py`.
- Publish LAB-086 only by conflict-checking exact predecessor `d4a6a40f...`, applying only the retained patch through a byte-preserving supported path, requiring exact target `b78e7c98...`, then re-fetch/hash-verify and run the complete security gate.
- Direct git/raw network transport remains unavailable due DNS in this run; treat this as a per-run observation. GitHub connector can read exact blob content and perform Contents writes, but no connector-to-local or connector-side patch-composition bridge was observed.
- PR #175 remains draft. Exact-head focused/integration/downstream execution remains pending.

## Exact next action

LAB-086 first: probe for a supported byte-preserving composition/transfer bridge; if one exists, conflict-check predecessor `d4a6a40f...`, compose only retained patch `61841b58...`, require target blob `b78e7c98...`, publish/re-fetch/hash-verify, then run the full LAB-086 security gate. Otherwise resume LAB-090 PR #175: execute `test_activation_historical_unresolved_restart.py` plus historical-retry, overlapping-rotation, activation primitive/integration/premature-release, provider-generation integration, and downstream shared-anchor/provider-history suites from exact published bytes. If exact execution is still blocked, perform a narrow source audit for another concrete restart/concurrency defect only; do not expand the protocol speculatively.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending on draft PR #172.
- #169 / LAB-090 — IN_PROGRESS; historical unresolved activation restart fail-closed verifier fix published on draft PR #175; exact executable gate pending.
- #170 / LAB-091 — IN_PROGRESS fallback; draft PR #173; exact whole-branch/full behavioral gates pending.
