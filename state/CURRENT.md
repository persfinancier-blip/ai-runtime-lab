# Current Lab State

Last updated: 2026-08-31

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165; branch `lab/086-asymmetric-break-glass-history`.
- LAB-086 exact predecessor `strict_fence.py` blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; retained patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; required target `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- LAB-090 / #169 is the allowed fallback while LAB-086 exact byte-preserving publication/execution is tool-limited. Draft PR #175; branch `lab-090-provider-activation-fencing`; current head `82d15ca21543ba2c70d1a11b7df0633e5cc387f1`.
- LAB-091 / #170 remains IN_PROGRESS on draft PR #173.
- LAB-088 / #167 remains IN_PROGRESS on draft PR #172.

## Last completed step

Re-read `AGENTS.md`, this handoff, `prompts/SELF_RESUME.md`, open issues and active PRs. Direct `git ls-remote` again failed before repository-code execution with `Could not resolve host: github.com`; no LAB-086 mutation was attempted because the required byte-preserving predecessor+retained-patch composition path is still unavailable.

Resumed LAB-090 source audit. Found a stale-current-provider read bug after a lost activation release: provider history/head can be durably G2 and activation `COMMITTED` while `release_activation()` raises before `self.attested` swaps, leaving the live ledger on G1. The earlier fix blocks stale `reserve()`, but inherited LAB-080 `verify_component()` performed an authenticated read via stale `self.attested` and compared it with inherited `_provider()`, which also described stale G1. Current-provider freshness could therefore succeed against historical G1 after durable cutover.

Published regression in PR #175 commit `17f504176cdcffe8c9304807d169a31d02d07326`: `test_activation_stale_verify_component.py`, blob `b1f3e06b0b67da5ee892c5e0b35650dd3567b71f`. Exact test bytes were independently reconstructed and Git-blob hashed to the same SHA; `py_compile` PASS. Behavioral unittest execution is not claimed.

Published minimal fix in PR #175 commit/head `82d15ca21543ba2c70d1a11b7df0633e5cc387f1`: `SupportedHistoricalSharedAnchorLedger._provider()` now calls `_require_runtime_matches_durable_head()` before exposing provider identity to inherited current-provider read surfaces. `supported.py` blob `6aee4eaec6d34563ea82c2a3216a82fb1d157c00`. GitHub commit diff confirms exactly four added lines.

Issue #169 comment `5472915907`. Durable note: `research/2026-08-31-lab090-stale-runtime-verify-component.md`, main commit `cc2328beb9aa86c9e23c2d143ee7ad4550e71bf1`.

PR #175 is now 27 commits ahead / 30 behind main. Merge-base-to-main comparison shows main-side changes since the merge base touch only `research/*` and `state/CURRENT.md`, not LAB-090 source/test paths. GitHub currently reports the draft PR as non-mergeable; treat this as unresolved control-plane state until rechecked, not as a proven source conflict.

## Evidence retained

- LAB-080 18/18 PASS; LAB-082 28/28 PASS; LAB-083 24/24 PASS; LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS; asymmetric custody 8/8 PASS; public/final 11/11 PASS; unsafe lower baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; hidden-rowid RED→GREEN evidence and exact predecessor/target derivation retained; publication/full gate pending.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-088 exact signer-noise/core evidence 22/22 PASS + compileall; supported/downstream gate pending.
- LAB-091 focused/adoption evidence retained; full real-stack gate pending.
- LAB-090 provider primitive/concurrency exact-byte slice remains 10/10 PASS + compileall. Subsequent activation integration/restart/stale-runtime hardening is published but broader exact execution remains pending.

## Known blockers / constraints

- LAB-086 remains first priority. Do not manually/model-reserialize the 949-line security-critical `strict_fence.py`.
- Publish LAB-086 only from exact predecessor `d4a6a40f...` plus retained patch `61841b58...`, requiring exact target `b78e7c98...`, then re-fetch/hash-verify and run the complete security gate.
- Direct git/raw network transport is unavailable due DNS in this run; treat this as a per-run observation.
- PR #175 stays draft. New stale-runtime `verify_component` regression has exact-byte syntax evidence only, not behavioral unittest evidence.

## Exact next action

LAB-086 first: probe for a supported byte-preserving composition/transfer bridge; if available, conflict-check predecessor `d4a6a40f...`, apply only retained patch `61841b58...`, require target `b78e7c98...`, publish/re-fetch/hash-verify, then run the full LAB-086 security gate.

If still unavailable, resume LAB-090 PR #175. First audit and reproduce the remaining `verify_component` concurrency window: generation head may change after the initial current-runtime/provider check but before final watermark commit. Require any fix to prevent stale-generation evidence from durably advancing a watermark, not merely raise after mutation. Then reconstruct/hash-verify the exact dependency closure and run activation integration/restart/downstream tests as soon as a safe byte-transfer execution path is available.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; stale `verify_component` stable-state fix/regression published; concurrency window + exact integration/restart/downstream gate pending.
- #170 / LAB-091 — IN_PROGRESS fallback; full behavioral gates pending.
