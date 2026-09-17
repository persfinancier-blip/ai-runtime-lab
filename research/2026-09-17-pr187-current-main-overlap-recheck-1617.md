# PR #187 current-main overlap recheck — 2026-09-17 16:17 MSK

## Purpose
Maintain executable-readiness closure while LAB-086 exact execution remains transport-blocked. This note records only observations actually made in this run; it is not executable GREEN evidence.

## LAB-086 first probe
Command attempted directly in the current execution filesystem:

`git ls-remote https://github.com/persfinancier-blip/ai-runtime-lab.git HEAD`

Result: exit 128 before repository code execution, `Could not resolve host: github.com`.

Therefore authoritative executable pin materialization remains unavailable through shell Git transport and no LAB-086 PASS is claimed.

## PR #187 observation
GitHub reports PR #187 open and draft, head branch `lab-095-database-identity-red-intent`, head SHA `5bfdbdbd64d2281206b1c3d1e9a00db8bdbd4057`. Inline review-thread query returned no threads. GitHub currently reports `mergeable=false`; per retained repository policy this metadata alone is not conflict evidence.

Actual `main` observed before this evidence write: `56abf73c677c5bfc687f62ca2176f0319f2820aa`.

Fresh compare from PR-reported base snapshot `2c72b76b2f1ffbee520e3871d4f1e0e878fe7974` to actual main reports `ahead_by=195`, `behind_by=0`. The compare response is large/truncated by the connector; no concrete new `experiments/*` or `tests/*` overlap was demonstrated by the returned material. No new review defect was observed.

## Decision
Do not rebase, merge, or broaden PR #187 merely to refresh metadata. Keep it draft. LAB-086 remains priority #1. If byte-exact executable materialization becomes available, verify pin/blob identity first and execute the retained exact gate. Otherwise react only to concrete source/test overlap, head drift, or a new review defect.
