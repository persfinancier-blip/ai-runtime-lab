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

Re-read `AGENTS.md`, this handoff, and `prompts/SELF_RESUME.md`; inspected open issues and active PR state. Direct git transport was probed again and failed before repository-code execution with `Could not resolve host: github.com`, so no exact-head unittest/downstream PASS is claimed.

Resumed LAB-090 PR #175 according to the prior handoff and performed the explicit divergence/conflict audit. Current refs observed: PR head `9e53c6ed0340c8a3c77c22b23eb7c0340240294e`, main before the audit note `df316786015eb5abcc0d285b6ae13ce9ba0bf210`, merge-base `6cc7a04496187075db1c02f3e27c1d394da53026`. The PR is 15 commits ahead and 12 behind current main.

Compared merge-base -> current main. All 12 main-side commits touch only LAB-090 `research/*` notes and `state/CURRENT.md`; none touches the six PR #175 implementation/test paths. Therefore there is no direct file-content overlap/conflict introduced by those main-side commits. GitHub currently reports PR #175 `mergeable=false`, but that signal is not evidence of a semantic LAB-090 code conflict.

Fresh source audit of branch `activation.py` and `supported.py` reconfirmed the required protocol ordering: provider `PREPARED` fence -> durable SQL `SQL_COMMITTED` exact ticket -> provider `COMMITTED_FENCED` -> durable exact-ticket `COMMITTED` -> release. Restart rejects `SQL_COMMITTED + RELEASED` and completes `COMMITTED + COMMITTED_FENCED` idempotently. No new source-level defect was established in this pass; executable validation remains required.

Durable evidence: `research/2026-08-30-lab090-main-divergence-conflict-audit.md`, main commit `aae5be540b29ffa0f4a3a19684c481b8e33fdf74`; issue #169 comment `5470130013`.

## Evidence retained

- LAB-080 18/18 PASS; LAB-082 28/28 PASS; LAB-083 24/24 PASS; LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS; asymmetric custody 8/8 PASS; public/final 11/11 PASS; unsafe lower baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; hidden-rowid RED→GREEN evidence and exact predecessor/target derivation retained; publication/full gate pending.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-088 exact published signer-noise/core evidence remains 22/22 PASS + compileall; supported/downstream execution pending.
- LAB-091 accumulated adoption hardening/focused reproduced evidence retained; whole-branch timeout/UNKNOWN and process concurrency/crash gates pending.
- LAB-090 prior provider primitive focused mechanism gate 6/6 PASS is retained. Premature-release fail-closed source correction/regression is published. Fresh divergence audit proves no post-merge-base main-side file overlap with PR #175; exact-head executable validation is still pending.

## Known blockers / constraints

- LAB-086 remains first priority. Do not manually/model-reserialize the 949-line security-critical `strict_fence.py`.
- Publish LAB-086 only by conflict-checking exact predecessor `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`, applying only the retained patch through a byte-preserving supported path, requiring exact target `b78e7c98e35138719f77c482c7f1aab36b702de7`, then re-fetch/hash-verify and run the complete security gate.
- Direct git/network transport remains unavailable due DNS in this run; treat this as a per-run observation.
- PR #175 remains draft. Main-side divergence has no direct path overlap with the PR implementation/test files, but exact-head tests and downstream suites have not executed; do not mark ready or merge from source audit alone.

## Exact next action

LAB-086 first: if a supported byte-preserving composition/transfer bridge appears, publish and full-gate the exact hidden-rowid target. Otherwise resume LAB-090 PR #175 and retry exact-head execution of `test_activation.py`, `test_activation_integration.py`, `test_activation_premature_release.py`, existing provider-generation integration, and downstream shared-anchor/provider-history suites. If direct git transport remains blocked, continue a narrowly scoped source audit for a concretely reproducible restart/concurrency defect; do not speculatively expand the protocol and do not attempt low-level ref/tree or force-update operations merely to remove branch divergence.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending on draft PR #172.
- #169 / LAB-090 — IN_PROGRESS; premature-release fail-open fixed; current-main divergence has no direct file overlap; exact-head/downstream execution pending on draft PR #175.
- #170 / LAB-091 — IN_PROGRESS fallback; draft PR #173; exact whole-branch/full behavioral gates pending.
