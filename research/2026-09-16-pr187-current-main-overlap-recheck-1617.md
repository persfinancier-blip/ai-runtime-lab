# PR #187 current-main overlap recheck — 2026-09-16 16:17 MSK

## Runtime observation
LAB-086 was probed first as required. Direct `git clone https://github.com/persfinancier-blip/ai-runtime-lab.git` failed before repository code execution with exit 128 and `Could not resolve host: github.com`. No LAB-086 executable PASS is claimed.

## Control-plane state
- actual `main` tip from `/branches/main`: `0d1e410a6824e2a5d8f2654216eb78385627c9fa`;
- PR #187 remains open/draft;
- PR #187 head remains `5bfdbdbd64d2281206b1c3d1e9a00db8bdbd4057`;
- PR metadata still reports base snapshot / merge base `2c72b76b2f1ffbee520e3871d4f1e0e878fe7974` and `mergeable=false`;
- inline review threads remain empty.

## Current-main comparison
Compare `2c72b76b... -> 0d1e410a...` reports 147 post-base commits. Every returned changed path is still under `research/*` or `state/CURRENT.md`.

PR #187 still reports 44 changed files and its previously audited source/test set is under `experiments/*` and `tests/*`. No new current-main source/test overlap or concrete review defect is observed in this run.

## Decision
Do not rebase, merge, or broaden LAB-094/095/096 merely to refresh stale GitHub mergeability metadata. Exact repository execution remains the closure gate. If byte-exact materialization becomes available, verify retained hashes first and execute the retained focused/composed/LAB-080/LAB-081 inventory, then full pytest and compileall.
