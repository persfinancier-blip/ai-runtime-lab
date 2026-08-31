# Current Lab State

Last updated: 2026-08-31

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165; branch `lab/086-asymmetric-break-glass-history`.
- LAB-086 exact predecessor `strict_fence.py` blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; retained patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; required target `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- LAB-090 / #169 is the allowed fallback while LAB-086 exact byte-preserving publication/execution is tool-limited. Draft PR #175; branch `lab-090-provider-activation-fencing`; latest production-fix commit `9cefa27a285b292e9699505a3b10e580c69a38e1`.
- LAB-091 / #170 remains IN_PROGRESS on draft PR #173.
- LAB-088 / #167 remains IN_PROGRESS on draft PR #172.

## Last completed step

Re-read `AGENTS.md`, this handoff, `prompts/SELF_RESUME.md`, open issues and active PRs. LAB-086 remains first priority. Direct Git transport was re-probed and again failed before repository execution with `Could not resolve host: github.com`. The available GitHub connector still exposes complete-file Contents writes but no safe server-side exact-blob-plus-retained-patch composition operation for the 949-line security-critical LAB-086 `strict_fence.py`; no LAB-086 mutation was attempted.

Resumed the exact LAB-090 fallback target: `verify_component()` generation concurrency. The previously published deterministic race regression remains `experiments/provider_generation_history/tests/test_activation_verify_component_rotation_race.py`, blob `359288e32e7df0ffd60bd359e326398b0bec276a`.

Published the production fix in PR #175 commit `9cefa27a285b292e9699505a3b10e580c69a38e1`. It changes only `experiments/shared_anchor_intent_ledger/protocol.py`: immediately after final `BEGIN IMMEDIATE`, before any watermark DML, `verify_component()` dynamically re-checks `_provider()` and requires the same `(provider_id,generation)` authenticated earlier. For `SupportedHistoricalSharedAnchorLedger`, `_provider()` verifies live runtime against the durable provider-generation head. Therefore rotation either commits first and stale evidence is rejected, or verification obtains SQLite's writer reservation first and rotation serializes behind the watermark transaction.

Post-publication GitHub commit inspection confirms exactly six inserted lines and no unrelated diff. Resulting `protocol.py` blob: `fd22bc30f6aacdfd157557c8b458d9f7b0b3bda8`.

Executed a local file-backed two-thread SQLite mechanism check for the specific implementation assumption: while one connection holds `BEGIN IMMEDIATE`, a second connection can read the committed generation head, while a competing writer waits until the first transaction commits. Observed generation order `1 -> 2`; mechanism PASS.

Exact PR-head behavioral regression/full-suite PASS is not claimed because repository execution transport remains unavailable. Issue #169 comment `5473667375`. Durable note: `research/2026-08-31-lab090-verify-component-commit-boundary-fix.md`, main commit `dc1981fc9d49295423a6140419041d694630fd19`.

PR #175 is currently open/draft and GitHub reports `mergeable=false`; branch comparison is diverged 31 ahead / 36 behind main. A merge-base→main comparison shows main-side divergence only in `research/*` and `state/CURRENT.md`, with no LAB-090 source/test path overlap. Treat non-mergeable as a control-plane/integration condition to resolve before ready/merge, not evidence of a source-level conflict in the LAB-090 files.

## Evidence retained

- LAB-080 18/18 PASS; LAB-082 28/28 PASS; LAB-083 24/24 PASS; LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS; asymmetric custody 8/8 PASS; public/final 11/11 PASS; unsafe lower baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; hidden-rowid RED->GREEN evidence and exact predecessor/target derivation retained; publication/full gate pending.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-088 exact signer-noise/core evidence 22/22 PASS + compileall; supported/downstream gate pending.
- LAB-091 focused/adoption evidence retained; full real-stack gate pending.
- LAB-090 provider primitive/concurrency exact-byte slice remains 10/10 PASS + compileall. Subsequent activation integration/restart/stale-runtime hardening is published but broader exact execution remains pending.
- LAB-090 `verify_component` rotation-race regression blob `359288e3...` is byte-verified and `py_compile` PASS from the prior run; production commit-boundary fix is now published as exact six-line diff, with separate SQLite serialization mechanism PASS. Behavioral GREEN execution remains pending.

## Known blockers / constraints

- LAB-086 remains first priority. Do not manually/model-reserialize the 949-line security-critical `strict_fence.py`.
- Publish LAB-086 only from exact predecessor `d4a6a40f...` plus retained patch `61841b58...`, requiring exact target `b78e7c98...`, then re-fetch/hash-verify and run the complete security gate.
- Current GitHub connector provides normal complete-file Contents writes but no observed safe server-side patch/composition primitive for the LAB-086 exact predecessor+retained-patch operation.
- PR #175 stays draft. The generation-commit race production fix is published and diff-audited, but the new behavioral regression/full downstream gate has not executed on exact PR-head bytes in this run.
- PR #175 is currently 31 commits ahead / 36 behind main and GitHub reports non-mergeable; main-side changes since merge-base do not overlap LAB-090 source/test paths.
- Direct Git transport currently fails DNS resolution before repository code execution.

## Exact next action

LAB-086 first: probe again for a supported byte-preserving composition/transfer bridge; if available, conflict-check predecessor `d4a6a40f...`, apply only retained patch `61841b58...`, require target `b78e7c98...`, publish/re-fetch/hash-verify, then run the full LAB-086 security gate.

If still unavailable, resume LAB-090 PR #175. First execute the published rotation-race regression against exact PR-head bytes and run the activation integration/restart/downstream gate. If execution transport remains unavailable, resolve or safely refresh the PR's diverged/non-mergeable integration state using only supported high-level operations after conflict-checking; do not use low-level ref/tree manipulation or force updates. Then continue only with a narrow correctness audit; do not broaden authority semantics or claim behavioral GREEN without execution.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; provider activation hardening and verify_component commit-boundary guard published; exact behavioral integration/restart/downstream gate pending.
- #170 / LAB-091 — IN_PROGRESS fallback; full behavioral gates pending.
