# PR #187 current-main overlap recheck — 2026-09-17 11:17 Europe/Moscow

## LAB-086-first capability probe

Executed in this run:

`git ls-remote https://github.com/persfinancier-blip/ai-runtime-lab.git HEAD`

Observed result: exit 128 before repository code execution with `Could not resolve host: github.com`.

Therefore the authoritative LAB-086 executable pin cannot be byte-exact materialized through shell Git transport in this runtime, and no LAB-086 executable PASS/GREEN is claimed.

## GitHub control-plane observations

- Actual `main` before this evidence commit: `da90e51a10980626b1b44e4354009755bad19175`.
- PR #187 remains open and draft.
- PR #187 head remains `5bfdbdbd64d2281206b1c3d1e9a00db8bdbd4057`.
- Inline review-thread query returned none.
- GitHub PR metadata currently reports `mergeable=false`; this is not treated alone as source-conflict evidence.
- Fresh compare from PR-reported base snapshot `2c72b76b2f1ffbee520e3871d4f1e0e878fe7974` to actual main reports `ahead_by=185`, `behind_by=0`.
- The compare drift continues the established main-side research/state churn; no concrete new review defect, PR-head drift, or demonstrated `experiments/*` / `tests/*` source overlap was observed that justifies mutating PR #187 in this run.

## Decision

Keep PR #187 draft and unchanged. Do not rebase/merge merely to refresh mergeability metadata. LAB-086 remains priority #1. If byte-exact materialization becomes available, verify the authoritative pin/blob identities first and execute the retained exact gates before claiming GREEN.
