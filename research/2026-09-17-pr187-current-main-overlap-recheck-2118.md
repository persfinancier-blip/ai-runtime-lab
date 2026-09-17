# PR #187 current-main overlap recheck — 2026-09-17 21:18 MSK

## LAB-086-first capability probe

Attempted direct executable transport first with:

`git ls-remote https://github.com/persfinancier-blip/ai-runtime-lab.git HEAD`

The container operation did not reach git/repository execution; the runtime returned `GatewaySelectionError`. This is a per-run transport/runtime failure, not evidence about repository correctness. No LAB-086 executable PASS/GREEN is claimed.

## Control-plane observations

- Actual `main` tip observed through GitHub REST: `3d5d9b423373c42f981bedbd09ac2f526a18a059`.
- PR #187 remains open and draft.
- PR #187 head remains `5bfdbdbd64d2281206b1c3d1e9a00db8bdbd4057`.
- GitHub reports `mergeable=false`; this metadata alone is not treated as concrete conflict evidence.
- Fresh compare from PR-reported base snapshot `2c72b76b2f1ffbee520e3871d4f1e0e878fe7974` to actual main reports `ahead_by=205`, `behind_by=0`.
- The complete returned changed-file inventory consists only of `research/*` additions plus `state/CURRENT.md`; no `experiments/*` or `tests/*` overlap is present.
- PR discussion was inspected; no newly observed concrete inline/actionable review defect requiring source mutation was found in the returned material.

## Decision

Do not rebase, merge, or mutate PR #187 merely to refresh mergeability metadata. The observed main drift remains durable evidence/state churn outside the PR source/test surfaces. Keep PR #187 draft because exact repository execution remains unavailable.

## Exact next action

Probe LAB-086 first on the next run. If authoritative pin `1fa85a0e34c9ae67da57f1e64dadccf211feacc0` becomes byte-exactly materializable in an executable filesystem, verify identity and run the complete retained LAB-086 gate. Otherwise re-read actual main, PR #187 head/reviews, and source/test overlap, reacting only to concrete source/test overlap, head drift, or a new review defect. If exact PR #187 materialization becomes available, verify retained blob/hash identity first and execute the closure inventory in `research/2026-09-16-lab094-096-closure-inventory.md`, then full pytest and compileall.