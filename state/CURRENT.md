# Current Lab State

Last updated: 2026-08-30

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165; branch `lab/086-asymmetric-break-glass-history`.
- Exact LAB-086 `strict_fence.py` predecessor remains blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; retained hidden-rowid patch `research/2026-08-28-lab086-hidden-rowid-replace.patch`, blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; exact target `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- LAB-090 / #169 is the current allowed fallback while LAB-086 byte-preserving publication is tool-limited. Draft PR #175; branch `lab-090-provider-activation-fencing`; observed head `348b279d979600e4a03333bc6ed729922705ff5b`.
- LAB-091 / #170 remains IN_PROGRESS fallback on draft PR #173.
- LAB-088 / #167 remains IN_PROGRESS on draft PR #172.

## Last completed step

Re-read `AGENTS.md`, this handoff, and `prompts/SELF_RESUME.md`; inspected open issues and active PRs. Explicit compare now confirms PR #175 is diverged from `main`: 13 commits ahead, 8 behind, merge-base `6cc7a04496187075db1c02f3e27c1d394da53026`. This establishes stale-base divergence but does not by itself prove a semantic/file conflict.

Fresh source audit found a concrete LAB-090 fail-open after the `COMMITTED_FENCED -> RELEASED` correction. Current `_commit_or_reconcile_activation()` accepts provider status `RELEASED` before durable SQLite acknowledgement, and `_recover_pending_activation()` likewise accepts `SQLite=SQL_COMMITTED + provider=RELEASED`, then promotes the durable row to `COMMITTED`. That violates the protocol ordering: provider fence must remain installed until the exact ticket is durably acknowledged as `COMMITTED`; therefore `SQL_COMMITTED + RELEASED` is a protocol violation and must fail closed.

Durable evidence: `research/2026-08-30-lab090-premature-release-fail-open-audit.md`, main commit `3548b5c73ccc6246689b7c53fcb4fc02101b6a8c`; issue #169 comment `5469541730`. A minimal state-machine reproduction confirmed the current acceptance predicate admits the invalid state. No whole-branch execution is claimed.

## Evidence retained

- LAB-080 18/18 PASS; LAB-082 28/28 PASS; LAB-083 24/24 PASS; LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS; asymmetric custody 8/8 PASS; public/final 11/11 PASS; unsafe lower baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; hidden-rowid RED→GREEN evidence and exact predecessor/target derivation retained; publication/full gate pending.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-088 exact published signer-noise/core evidence remains 22/22 PASS + compileall; supported/downstream execution pending.
- LAB-091 accumulated adoption hardening/focused reproduced evidence retained; whole-branch timeout/UNKNOWN and process concurrency/crash gates pending.
- LAB-090 prior provider primitive focused mechanism gate 6/6 PASS is retained. Current PR #175 source audit has identified the premature-release fail-open; exact executable validation of the latest branch remains pending.

## Known blockers / constraints

- LAB-086 remains first priority. Do not manually/model-reserialize the 949-line security-critical `strict_fence.py`.
- Publish LAB-086 only by conflict-checking exact predecessor `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`, applying only the retained patch through a byte-preserving supported path, requiring exact target `b78e7c98e35138719f77c482c7f1aab36b702de7`, then re-fetch/hash-verify and run the complete security gate.
- Direct git/network transport has been unavailable due DNS in recent runs; treat this as a per-run observation.
- PR #175 remains draft. It is stale/diverged from main and has a concrete source-level fail-open: `SQL_COMMITTED + provider RELEASED` is currently accepted. Do not mark ready or merge until corrected and executable gates pass.

## Exact next action

LAB-086 first: if a supported byte-preserving composition/transfer bridge appears, publish and full-gate the exact hidden-rowid target. Otherwise resume LAB-090 PR #175 and make the smallest fail-closed correction: `_commit_or_reconcile_activation()` must accept only `COMMITTED_FENCED` before durable acknowledgement; `_recover_pending_activation()` with durable `SQL_COMMITTED` must accept only `PREPARED` or `COMMITTED_FENCED` and reject `RELEASED`; retain `RELEASED` idempotency only for durable `COMMITTED`. Add a regression for premature exact-ticket release before SQLite acknowledgement, then attempt exact published-head `test_activation`, `test_activation_integration`, existing provider-generation integration, and downstream shared-anchor/provider-history suites. Re-check base/head divergence after the fix. Do not mark PR ready or merge until executable gates pass.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending on draft PR #172.
- #169 / LAB-090 — IN_PROGRESS; premature-release fail-open identified on draft PR #175; fail-closed fix + regression + exact execution pending.
- #170 / LAB-091 — IN_PROGRESS fallback; draft PR #173; exact whole-branch/full behavioral gates pending.
