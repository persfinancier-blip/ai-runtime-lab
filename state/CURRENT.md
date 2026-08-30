# Current Lab State

Last updated: 2026-08-30

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165; branch `lab/086-asymmetric-break-glass-history`.
- Exact LAB-086 `strict_fence.py` predecessor remains blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; retained hidden-rowid patch `research/2026-08-28-lab086-hidden-rowid-replace.patch`, blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; exact target `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- LAB-090 / #169 is the current allowed fallback while LAB-086 byte-preserving publication is tool-limited. Draft PR #175; branch `lab-090-provider-activation-fencing`; head `348b279d979600e4a03333bc6ed729922705ff5b`.
- LAB-091 / #170 remains IN_PROGRESS fallback on draft PR #173.
- LAB-088 / #167 remains IN_PROGRESS on draft PR #172.

## Last completed step

Re-read `AGENTS.md`, this handoff, and `prompts/SELF_RESUME.md`; inspected open issues and active PRs. LAB-086 still has no supported byte-preserving composition path for its 949-line security-critical file, so resumed the exact LAB-090 next action.

Fixed the concrete PR #175 post-provider-commit race. Provider activation now has explicit `PREPARED -> COMMITTED_FENCED -> RELEASED` semantics: `commit_activation()` durably records provider commitment but keeps the exact activation ticket installed as the external increment fence. Coordinator `_mark_activation_committed()` durably acknowledges the exact ticket in SQLite first; only then does exact-ticket `release_activation()` remove the provider fence. Restart reconciliation now also handles durable SQLite `COMMITTED` with provider still `COMMITTED_FENCED`, completing a lost release.

Added provider and integration regressions for external advance immediately after provider commit/before SQL acknowledgement, stale/different release ticket, committed-fenced state across coordinator restart, and outage after durable SQL acknowledgement but before provider release. Fresh PR diff audit confirmed the intended ordering in published source.

Published LAB-090 head: `348b279d979600e4a03333bc6ed729922705ff5b`. Durable evidence: `research/2026-08-30-lab090-committed-fenced-release-protocol.md`, main commit `22ca89fdff401e8e4d9c24ed00020642cb9fef38`; issue #169 comment `5469216388`.

Direct exact-branch execution was probed again with a fresh shallow clone and failed before repository code execution with `Could not resolve host: github.com`. No whole-branch unittest result is claimed.

## Evidence retained

- LAB-080 18/18 PASS; LAB-082 28/28 PASS; LAB-083 24/24 PASS; LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS; asymmetric custody 8/8 PASS; public/final 11/11 PASS; unsafe lower baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; hidden-rowid RED→GREEN evidence and exact predecessor/target derivation retained; publication/full gate pending.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-088 exact published signer-noise/core evidence remains 22/22 PASS + compileall; supported/downstream execution pending.
- LAB-091 accumulated adoption hardening/focused reproduced evidence retained; whole-branch timeout/UNKNOWN and process concurrency/crash gates pending.
- LAB-090 prior provider primitive focused mechanism gate 6/6 PASS is retained. New committed-fenced/release code and regressions are published and source-audited, but exact executable validation of this new head remains pending.

## Known blockers / constraints

- LAB-086 remains first priority. Do not manually/model-reserialize the 949-line security-critical `strict_fence.py`.
- Publish LAB-086 only by conflict-checking exact predecessor `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`, applying only the retained patch through a byte-preserving supported path, requiring exact target `b78e7c98e35138719f77c482c7f1aab36b702de7`, then re-fetch/hash-verify and run the complete security gate.
- Direct git/network transport is currently unavailable due DNS; treat this as a per-run observation.
- PR #175 remains draft until exact published-branch and downstream tests execute and a fresh concurrency/restart audit is clean.
- PR metadata after the latest update reported `mergeable: false`; do not infer a semantic conflict without an explicit compare/conflict check. No merge is attempted while the PR is draft and ungated.

## Exact next action

LAB-086 first: if a supported byte-preserving composition/transfer bridge appears, publish and full-gate the exact hidden-rowid target. Otherwise resume LAB-090 PR #175: attempt exact published-head execution of `test_activation`, `test_activation_integration`, existing provider-generation integration, and downstream shared-anchor/provider-history suites. If direct transport remains unavailable, perform a supported explicit base/head conflict check and source-level audit of the new `COMMITTED_FENCED -> RELEASED` restart/idempotency paths; fix only concrete defects. Do not mark PR ready or merge until executable gates pass.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending on draft PR #172.
- #169 / LAB-090 — IN_PROGRESS; post-provider-commit race corrected on draft PR #175; exact new-head execution/downstream gate pending.
- #170 / LAB-091 — IN_PROGRESS fallback; draft PR #173; exact whole-branch/full behavioral gates pending.
