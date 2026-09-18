# PR #187 current-main overlap recheck — 2026-09-18 15:19 Europe/Moscow

## LAB-086-first execution probe

A direct clone was attempted first in the current execution container:

`git clone https://github.com/persfinancier-blip/ai-runtime-lab.git /tmp/airuntime`

Observed result: exit 128 before repository code execution, with `Could not resolve host: github.com`.

Therefore the authoritative executable pin `1fa85a0e34c9ae67da57f1e64dadccf211feacc0` was not byte-exactly materialized into the executable filesystem and no LAB-086 PASS/GREEN is claimed.

## PR #187 state

GitHub reports PR #187 open and draft, head `5bfdbdbd64d2281206b1c3d1e9a00db8bdbd4057`, base snapshot `2c72b76b2f1ffbee520e3871d4f1e0e878fe7974`, and `mergeable=false`. Mergeability metadata is not treated as standalone source-conflict evidence.

Actual main before this evidence commit was `5d3c87bf4a0234f50a523e2e4b203dd41c400781`.

A fresh complete compare from PR base snapshot to actual main reports:
- status: ahead
- main ahead by 241 commits
- main behind by 0
- merge base remains the PR base snapshot
- returned changed-file inventory contains only `research/*` additions and `state/CURRENT.md`
- no `experiments/*` or `tests/*` overlap is present

No PR-head drift was observed. No source/test mutation is justified solely to refresh mergeability metadata.

## Decision

Keep PR #187 draft and unchanged. Do not claim exact repository execution. On the next run, probe LAB-086 first; if byte-exact materialization remains unavailable, refresh actual main/PR head/reviews and react only to concrete source/test overlap, head drift, or an actionable review defect.