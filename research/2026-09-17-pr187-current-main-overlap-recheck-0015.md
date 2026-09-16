# PR #187 current-main overlap recheck — 2026-09-17 00:15 MSK

## LAB-086 probe first

Executed in this run:

`git ls-remote https://github.com/persfinancier-blip/ai-runtime-lab.git HEAD`

Observed result: exit 128 before repository code execution, with `Could not resolve host: github.com`.

Therefore the authoritative executable pin for LAB-086 was not materialized byte-for-byte and no LAB-086 executable PASS/GREEN is claimed.

## PR #187 state

GitHub reports PR #187 open and draft, head `5bfdbdbd64d2281206b1c3d1e9a00db8bdbd4057`, base snapshot `2c72b76b2f1ffbee520e3871d4f1e0e878fe7974`, 44 changed files, and `mergeable=false`.

Actual main tip observed before this evidence write: `78dbfe2edac633659903348177efe2436bf7fcfe`.

A fresh compare from PR base snapshot `2c72b76b2f1ffbee520e3871d4f1e0e878fe7974` to actual main reports main ahead by 163 commits, behind by 0. Every returned changed path remains either `research/*` or `state/CURRENT.md`; there is no source/test path overlap with PR #187's implementation surface in `experiments/*` and `tests/*`.

Open-issue/PR inspection shows #187 remains the active draft implementation and #188 remains open; no new concrete source-level defect requiring a branch mutation was observed in this run.

## Decision

Do not rebase, merge, or broaden LAB-094/095/096 solely to refresh inconsistent GitHub mergeability metadata. Preserve the draft head. Continue to react only to concrete source/test overlap, head drift, or a new review defect.

Exact repository pytest/compileall remains unexecuted because no supported byte-preserving connector-to-filesystem materialization path was observed in this run. Source/control-plane inspection is not executable GREEN.

## Next action

Probe LAB-086 first on the next run. If byte-exact materialization becomes available, verify authoritative blob/hash identity and execute the retained focused/composed/LAB-080/LAB-081 inventory, then full pytest and compileall. If transport remains blocked, re-read actual main, PR #187 head/reviews, and source/test overlap without creating metadata-only churn.
