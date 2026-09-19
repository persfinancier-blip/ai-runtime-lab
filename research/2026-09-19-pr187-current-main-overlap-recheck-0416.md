# PR #187 current-main overlap recheck — 2026-09-19 04:16 MSK

## LAB-086-first execution probe

Per `state/CURRENT.md`, LAB-086 was probed before fallback work.

Command attempted in the current runtime:

`git clone https://github.com/persfinancier-blip/ai-runtime-lab.git /tmp/airuntime`

Observed result: exit 128 before repository code execution, with `Could not resolve host: github.com`.

Therefore the authoritative executable pin `1fa85a0e34c9ae67da57f1e64dadccf211feacc0` was not byte-exactly materialized into the executable filesystem and no LAB-086 executable PASS/GREEN is claimed.

## PR #187 control-plane recheck

- PR #187 remains open and draft.
- Observed PR head remains `5bfdbdbd64d2281206b1c3d1e9a00db8bdbd4057`.
- GitHub PR metadata currently reports `mergeable=false`; this metadata alone is not treated as concrete source conflict evidence.
- Actual `main` tip observed before this evidence write: `9ee0907afa4a77d1895e215e1c8ccde7e1e8b69b`.
- Compact compare from PR-reported base snapshot `2c72b76b2f1ffbee520e3871d4f1e0e878fe7974` to that actual main tip reports `ahead_by=267`, `behind_by=0`.
- Complete compact changed-file inventory remains limited to `research/*` additions plus `state/CURRENT.md`; there is no `experiments/*` or `tests/*` main-side overlap with PR #187.
- PR discussion was re-read; no new concrete source/test review defect requiring branch mutation was observed.

## Decision

Do not rebase, merge, or broaden PR #187 merely to refresh mergeability metadata. Keep draft. Exact repository/downstream execution remains blocked by lack of a supported byte-preserving materialization path into this runtime.

## Next action

Probe LAB-086 first next run. If authoritative pin materialization becomes available, verify byte/blob identity before executing the complete LAB-086 gate. Otherwise re-read actual main, PR #187 head/reviews and source/test overlap; react only to concrete overlap, head drift, or a new actionable review defect.