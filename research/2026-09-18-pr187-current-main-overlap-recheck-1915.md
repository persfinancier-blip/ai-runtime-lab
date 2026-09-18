# PR #187 current-main overlap recheck — 2026-09-18 19:15 Europe/Moscow

## LAB-086 first probe

Per the durable priority, the exact direct materialization path was probed before fallback work:

```text
git clone https://github.com/persfinancier-blip/ai-runtime-lab.git /tmp/airuntime
fatal: unable to access 'https://github.com/persfinancier-blip/ai-runtime-lab.git/': Could not resolve host: github.com
exit 128
```

The failure occurred before repository code execution. No LAB-086 executable PASS/GREEN is claimed. Connector reads remain control-plane evidence, not a substitute for byte-exact executable materialization of the authoritative pin `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`.

## PR #187 state

- open: yes
- draft: yes
- head: `5bfdbdbd64d2281206b1c3d1e9a00db8bdbd4057` (unchanged)
- reported base snapshot: `2c72b76b2f1ffbee520e3871d4f1e0e878fe7974`
- GitHub mergeable metadata: `false`; not treated alone as proof of a concrete source/test conflict.

## Current main / overlap proof

Actual `main` observed before this evidence write: `6e738b765568173d30eec64dcc8b104f0c4945ee`.

Fresh full compare `2c72b76b... -> 6e738b765...` reports:

- status: ahead
- ahead_by: 249
- behind_by: 0
- merge base remains the PR base snapshot
- complete returned main-side changed-file inventory contains only `research/*` additions plus `state/CURRENT.md`
- no `experiments/*` or `tests/*` path appears on the main side

Therefore there is still no concrete main-side source/test overlap requiring a rebase, merge, or manual conflict rewrite of PR #187.

## Review recheck

PR discussion was re-read. No new concrete source/test review defect requiring a branch mutation was observed. Existing discussion continues to require exact repository/downstream execution before GREEN/integration.

## Decision

Keep PR #187 draft and unchanged. Do not churn the branch merely to refresh mergeability metadata. React only to concrete source/test overlap, PR head drift, or a new actionable review defect.

## Exact next action

Probe LAB-086 first next run. Execute its complete gate only if authoritative pin `1fa85a0e34c9ae67da57f1e64dadccf211feacc0` can be materialized byte-for-byte into an executable filesystem. If transport remains blocked, re-read actual main, PR #187 head/reviews and source/test overlap. If exact materialization becomes available for #187, verify retained blob/hash identity before executing the focused/composed/LAB-080/LAB-081 inventory, then full pytest and compileall.
