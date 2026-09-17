# PR #187 current-main overlap recheck — 2026-09-17 18:15 Europe/Moscow

## Purpose
Continue the retained closure gate while LAB-086 exact execution remains transport-blocked. This note records only observations made in this run; it is not executable GREEN evidence.

## LAB-086 first probe
Command attempted directly in the current runtime:

`git ls-remote https://github.com/persfinancier-blip/ai-runtime-lab.git HEAD`

Result: exit 128 before repository execution: `Could not resolve host: github.com`.

Therefore the authoritative executable pin `1fa85a0e34c9ae67da57f1e64dadccf211feacc0` was not materialized and the LAB-086 complete gate was not executed. No PASS is claimed.

## Control-plane observations
- Actual `main` tip before this evidence write: `4967e1245c0829c2483f27c170435a66cb50560f`.
- PR #187 remains open and draft.
- PR #187 head remains `5bfdbdbd64d2281206b1c3d1e9a00db8bdbd4057`.
- GitHub currently reports `mergeable=false`; retained contract treats that metadata as non-causal unless backed by concrete file/source conflict evidence.
- PR discussion was inspected; no newly observed concrete review defect requiring source mutation was identified in the returned material.

## Fresh current-main overlap proof
Compared PR #187 reported base snapshot `2c72b76b2f1ffbee520e3871d4f1e0e878fe7974` to actual main `4967e1245c0829c2483f27c170435a66cb50560f`.

Observed compare metadata:
- status: `ahead`
- main ahead by: 199 commits
- main behind by: 0
- merge base: the same PR base snapshot

The complete returned changed-file inventory contains only `research/*` additions and `state/CURRENT.md`. No `experiments/*` or `tests/*` file appears in current-main drift from that base snapshot.

This is concrete evidence that the continuing main drift does not itself introduce source/test overlap with PR #187's retained implementation surface. It does not prove PR #187 executable correctness and does not justify merge/rebase while exact gates remain unavailable.

## Decision
Do not mutate, rebase, or merge PR #187 merely to refresh GitHub mergeability metadata. Keep draft. React only to concrete source/test overlap, head drift, or a new review defect.

## Exact next action
Probe LAB-086 first next run. If authoritative pin materialization becomes available byte-for-byte, verify identity and execute the complete LAB-086 gate. Otherwise re-read actual main, PR #187 head/reviews, and source/test overlap. If byte-exact PR #187 materialization becomes available, verify retained blob/hash identity first, execute the focused/composed/LAB-080/LAB-081 inventory in `research/2026-09-16-lab094-096-closure-inventory.md`, then full pytest and compileall. Do not claim executable GREEN from source/control-plane inspection.
