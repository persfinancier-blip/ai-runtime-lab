# PR #187 current-main overlap recheck — 2026-09-17 17:13 MSK

## Capability probe
LAB-086 was probed first as required. Direct shell command:

`git ls-remote https://github.com/persfinancier-blip/ai-runtime-lab.git HEAD`

failed before repository execution with `Could not resolve host: github.com`, exit 128. No LAB-086 executable PASS is claimed.

## Control-plane observations
- Actual `main` tip before this evidence write: `43a4b6d88d2f8fd3c5faa147d34d087a2a87d82a`.
- PR #187 remains open and draft.
- PR #187 head remains `5bfdbdbd64d2281206b1c3d1e9a00db8bdbd4057`.
- GitHub currently reports `mergeable=false`; per retained contract this metadata alone is not conflict evidence.
- PR discussion was re-read; no newly observed concrete review defect requiring source mutation was identified.

## Fresh overlap check
A fresh compare from PR #187's reported base snapshot `2c72b76b2f1ffbee520e3871d4f1e0e878fe7974` to actual `main` `43a4b6d88d2f8fd3c5faa147d34d087a2a87d82a` reports:
- status: ahead;
- main ahead by 197 commits;
- main behind by 0;
- returned changed-file inventory contains only `research/*` additions and `state/CURRENT.md` modification;
- no `experiments/*` or `tests/*` path is present in the complete returned file inventory.

Therefore this run has concrete evidence that current-main drift since PR #187's base snapshot still does not overlap PR source/test surfaces. No rebase/merge/source mutation is justified merely to refresh mergeability metadata.

## Decision / next action
Keep PR #187 draft and unchanged. LAB-086 remains priority #1. On the next run, probe LAB-086 first; execute its complete gate only if authoritative pin `1fa85a0e34c9ae67da57f1e64dadccf211feacc0` can be materialized byte-for-byte into an executable filesystem. If transport remains blocked, re-read actual main tip, PR #187 head/reviews, and source/test overlap; react only to concrete overlap, head drift, or a new review defect. Do not claim executable GREEN from source/control-plane inspection.
