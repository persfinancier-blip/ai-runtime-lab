# PR #187 current-main overlap recheck — 2026-09-18 23:15 Europe/Moscow

## LAB-086 first probe

Per durable priority, direct executable materialization was probed first:

`git clone https://github.com/persfinancier-blip/ai-runtime-lab.git /tmp/airuntime`

Observed result: exit 128 before repository execution, `Could not resolve host: github.com`. No LAB-086 executable PASS/GREEN is claimed. The authoritative executable pin remains `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`; no non-byte-preserving reconstruction was attempted.

## Repository control-plane recheck

Actual `main` tip before this evidence commit: `ae4e3a11036ae753ecb5bd1143a7a79f6528f0b3`.

PR #187 remains open and draft. Head remains `5bfdbdbd64d2281206b1c3d1e9a00db8bdbd4057`; reported base snapshot remains `2c72b76b2f1ffbee520e3871d4f1e0e878fe7974`. GitHub currently reports `mergeable=false`; this metadata is not treated as proof of a source conflict.

A fresh complete compact compare from the PR-reported base snapshot to actual main reports main `ahead_by=257`, `behind_by=0`. The complete changed-file inventory remains restricted to `research/*` additions and `state/CURRENT.md`; there is no main-side `experiments/*` or `tests/*` change in that interval. Therefore no new concrete source/test overlap with PR #187 was observed.

The PR review collection is empty. No new actionable review defect was observed.

## Decision

Do not rebase, merge, broaden scope, or claim executable GREEN. Keep PR #187 draft. On the next run probe LAB-086 first; only execute the complete gate if authoritative pin `1fa85a0e34c9ae67da57f1e64dadccf211feacc0` can be materialized byte-for-byte into an executable filesystem. If transport remains blocked, refresh actual main, PR #187 head/reviews, and source/test overlap and react only to concrete drift/defects.
