# Current Lab State

Last updated: 2026-08-30

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165; branch `lab/086-asymmetric-break-glass-history`.
- Exact LAB-086 `strict_fence.py` predecessor remains blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; retained hidden-rowid patch `research/2026-08-28-lab086-hidden-rowid-replace.patch`, blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; exact target `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- LAB-090 / #169 is the current allowed fallback while LAB-086 byte-preserving publication is tool-limited. Draft PR #175; branch `lab-090-provider-activation-fencing`; observed head `9e53c6ed0340c8a3c77c22b23eb7c0340240294e`.
- LAB-091 / #170 remains IN_PROGRESS fallback on draft PR #173.
- LAB-088 / #167 remains IN_PROGRESS on draft PR #172.

## Last completed step

Re-read `AGENTS.md`, this handoff, and `prompts/SELF_RESUME.md`; inspected open issues and active PRs. LAB-086 remains blocked on the same byte-preserving publication requirement, and direct git checkout again failed before repository code execution because `github.com` could not be resolved.

Resumed LAB-090 PR #175 and fixed the previously audited premature-release fail-open. `_commit_or_reconcile_activation()` now accepts only provider `COMMITTED_FENCED` before durable SQLite acknowledgement. `_recover_pending_activation()` with durable `SQL_COMMITTED` now accepts only `PREPARED` or `COMMITTED_FENCED`; provider `RELEASED` at that stage raises `HistoricalVerificationError` instead of being promoted to durable `COMMITTED`. `RELEASED` remains idempotently accepted only when SQLite already says `COMMITTED`.

Added dedicated regression `experiments/provider_generation_history/tests/test_activation_premature_release.py`, modeling a faulty provider that commits and immediately releases before coordinator acknowledgement. Published fix commit `3f6c7a32e12ee57d82fca87abab27dbe1d3fe2dc`; regression/head commit `9e53c6ed0340c8a3c77c22b23eb7c0340240294e`. Durable evidence: `research/2026-08-30-lab090-premature-release-fail-closed-fix.md`, main commit `150c7799474c8564d4b6cdf693a1104c7fc360a6`; issue #169 comment `5469837124`.

Fresh GitHub metadata reports PR #175 `mergeable=true`, but explicit compare against current main still reports divergence: 15 commits ahead, 10 behind, merge-base `6cc7a04496187075db1c02f3e27c1d394da53026`. No exact-head unittest PASS is claimed because direct checkout remained DNS-blocked.

## Evidence retained

- LAB-080 18/18 PASS; LAB-082 28/28 PASS; LAB-083 24/24 PASS; LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS; asymmetric custody 8/8 PASS; public/final 11/11 PASS; unsafe lower baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; hidden-rowid RED→GREEN evidence and exact predecessor/target derivation retained; publication/full gate pending.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-088 exact published signer-noise/core evidence remains 22/22 PASS + compileall; supported/downstream execution pending.
- LAB-091 accumulated adoption hardening/focused reproduced evidence retained; whole-branch timeout/UNKNOWN and process concurrency/crash gates pending.
- LAB-090 prior provider primitive focused mechanism gate 6/6 PASS is retained. Latest premature-release fail-closed source correction and regression are published, but exact-head executable validation remains pending.

## Known blockers / constraints

- LAB-086 remains first priority. Do not manually/model-reserialize the 949-line security-critical `strict_fence.py`.
- Publish LAB-086 only by conflict-checking exact predecessor `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`, applying only the retained patch through a byte-preserving supported path, requiring exact target `b78e7c98e35138719f77c482c7f1aab36b702de7`, then re-fetch/hash-verify and run the complete security gate.
- Direct git/network transport remains unavailable due DNS in this run; treat this as a per-run observation.
- PR #175 remains draft. The premature-release predicate is fixed in source, but exact-head tests and downstream suites have not executed; branch remains diverged from main despite GitHub currently reporting mergeable=true.

## Exact next action

LAB-086 first: if a supported byte-preserving composition/transfer bridge appears, publish and full-gate the exact hidden-rowid target. Otherwise resume LAB-090 PR #175 and retry exact-head execution of `test_activation.py`, `test_activation_integration.py`, `test_activation_premature_release.py`, existing provider-generation integration, and downstream shared-anchor/provider-history suites. If direct git transport remains blocked, perform a fresh source audit of the newly fixed head and inspect the 10 main-side commits since merge-base for semantic/file conflicts with the five LAB-090 touched paths; do not mark PR ready or merge without executable gates.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending on draft PR #172.
- #169 / LAB-090 — IN_PROGRESS; premature-release fail-open fixed and regression published on draft PR #175; exact-head/downstream execution + divergence audit pending.
- #170 / LAB-091 — IN_PROGRESS fallback; draft PR #173; exact whole-branch/full behavioral gates pending.
