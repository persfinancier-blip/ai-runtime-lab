# PR #187 current-main overlap recheck — 2026-09-16 21:16 MSK

## LAB-086 first

Probed the preferred executable transport first with:

`git ls-remote https://github.com/persfinancier-blip/ai-runtime-lab.git HEAD`

Observed failure before repository code execution: `Could not resolve host: github.com`, exit 128. No LAB-086 executable PASS is claimed.

## Current control-plane observation

- actual `main`: `044aca380b0609b7ed6e171f2d44601d66ff0c18`
- PR #187: open, draft
- PR head: `5bfdbdbd64d2281206b1c3d1e9a00db8bdbd4057` (unchanged)
- PR reported base snapshot: `2c72b76b2f1ffbee520e3871d4f1e0e878fe7974`
- GitHub currently reports `mergeable=false`; this is not treated alone as source-conflict proof.

A fresh compare from the PR base snapshot to actual main reports main ahead by 157 commits. Every returned changed path is either `research/*` or `state/CURRENT.md`. PR #187 remains a 44-file change whose production/test work is under `experiments/*` and `tests/*`; therefore this current-main compare introduces no source/test path overlap with the PR implementation surface.

No rebase, merge, or authority broadening is justified by this observation. Exact repository execution remains blocked by byte-exact materialization/transport, so no pytest/compileall GREEN is claimed.

## Decision / next gate

Keep PR #187 draft. On the next run, probe LAB-086 first. If transport remains blocked, re-read actual main, PR head/reviews, and compare for concrete source/test overlap or head drift. If byte-exact materialization becomes available, verify authoritative hashes and execute the retained focused/composed gates, then full pytest and compileall.