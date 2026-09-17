# PR #187 current-main overlap recheck — 2026-09-17 15:18 MSK

## LAB-086 first probe

Executed directly in this runtime:

`git ls-remote https://github.com/persfinancier-blip/ai-runtime-lab.git HEAD`

Result: exit 128 before repository execution, `Could not resolve host: github.com`.

No LAB-086 executable PASS/GREEN is claimed.

## Control-plane observations

- Actual `main` before this evidence commit: `410e277ac7349a2e270d345b004a84000d411503`.
- PR #187 remains open and draft.
- PR #187 head remains `5bfdbdbd64d2281206b1c3d1e9a00db8bdbd4057`.
- GitHub currently reports `mergeable=false`; per retained contract this metadata alone is not treated as proof of a concrete source conflict.
- PR discussion was re-read; no newly observed concrete review defect requiring source mutation was identified.
- Fresh compare from PR-reported base snapshot `2c72b76b2f1ffbee520e3871d4f1e0e878fe7974` to actual main reports `ahead_by=193`, `behind_by=0`.
- Returned changed paths are research records plus `state/CURRENT.md`; no new `experiments/*` or `tests/*` overlap is demonstrated by this compare.

## Decision

Do not rebase, merge, or mutate PR #187 merely to refresh mergeability metadata. Preserve LAB-086 as priority #1. If byte-exact executable materialization becomes available, verify authoritative pin/blob identity before running the complete LAB-086 gate. Otherwise continue reacting only to concrete PR head drift, source/test overlap, or review defects.

Exact PR #187 repository pytest/compileall remains unexecuted in this runtime; source/control-plane inspection is not an executable GREEN claim.
