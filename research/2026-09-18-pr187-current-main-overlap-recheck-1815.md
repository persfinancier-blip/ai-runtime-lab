# PR #187 current-main overlap recheck — 2026-09-18 18:15 Europe/Moscow

## LAB-086 first probe

Per `state/CURRENT.md`, LAB-086 was probed first in the current runtime.

Command attempted:

```text
git clone https://github.com/persfinancier-blip/ai-runtime-lab.git /tmp/airuntime
```

Observed result: exit 128 before repository code execution; `Could not resolve host: github.com`.

Therefore the authoritative executable pin `1fa85a0e34c9ae67da57f1e64dadccf211feacc0` was not byte-exact materialized into the executable filesystem and no LAB-086 executable PASS/GREEN is claimed.

## PR #187 control-plane recheck

GitHub reports PR #187 open and draft at unchanged head `5bfdbdbd64d2281206b1c3d1e9a00db8bdbd4057`; current mergeability metadata is `false`. This metadata alone is not treated as proof of a concrete source conflict.

Actual `main` tip before this evidence write was `207d82ceba242ecb984f9971547e0467b744e6f9`.

A fresh full compare from PR-reported base snapshot `2c72b76b2f1ffbee520e3871d4f1e0e878fe7974` to that main tip reports:

- status: ahead;
- ahead_by: 247;
- behind_by: 0;
- complete returned changed-file inventory: only `research/*` additions plus `state/CURRENT.md`.

There is still no main-side `experiments/*` or `tests/*` change in the returned inventory, so no new source/test overlap with PR #187 is evidenced by current main drift.

PR discussion was re-read through the available merged discussion endpoint. No new concrete source/test review defect was observed in the returned discussion material. The retained requirement remains exact repository execution before any executable GREEN claim.

## Decision

Do not rebase, merge, or broaden LAB-094/095/096 merely to refresh GitHub mergeability metadata. Keep PR #187 draft. Continue LAB-086-first. If byte-exact materialization becomes available, verify retained blob/hash identity before executing the full gate. Otherwise react only to concrete source/test overlap, PR head drift, or a new actionable review defect.
