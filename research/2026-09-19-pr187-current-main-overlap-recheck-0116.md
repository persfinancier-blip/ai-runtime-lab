# PR #187 current-main overlap recheck — 2026-09-19 01:16 MSK

## Purpose
Maintain executable-readiness closure while LAB-086 remains transport-blocked, without treating GitHub mergeability metadata as executable evidence.

## LAB-086-first probe
Direct execution attempted:

`git clone https://github.com/persfinancier-blip/ai-runtime-lab.git /tmp/airuntime`

Observed result: exit 128 before repository code execution, `Could not resolve host: github.com`. Therefore the authoritative pin `1fa85a0e34c9ae67da57f1e64dadccf211feacc0` was not byte-exact materialized into the executable filesystem and no LAB-086 PASS/GREEN is claimed.

## PR #187 observation
- PR #187: open, draft.
- Head: `5bfdbdbd64d2281206b1c3d1e9a00db8bdbd4057` (unchanged).
- GitHub reports `mergeable=false`; this metadata alone is not treated as concrete conflict evidence.
- Actual main before this evidence commit: `bda69893524a23a93c3e1053bed859122cad9cf4`.
- Compare from PR-reported base snapshot `2c72b76b2f1ffbee520e3871d4f1e0e878fe7974` to actual main: main ahead 261, behind 0.
- Complete compact changed-file inventory remains only `research/*` additions plus `state/CURRENT.md` modification. There is no `experiments/*` or `tests/*` main-side overlap with PR #187.
- PR discussion was re-read; no new concrete source/test review defect requiring branch mutation was observed.

## Decision
Do not rebase, merge, or broaden LAB-094/095/096 merely to refresh mergeability metadata. Keep PR #187 draft. React only to concrete source/test overlap, head drift, or a new actionable review defect.

## Next action
Probe LAB-086 first next run. If authoritative pin `1fa85a0e34c9ae67da57f1e64dadccf211feacc0` becomes byte-exact executable, verify retained blob/hash identity before running its complete gate. Otherwise repeat a current-main/head/review overlap check and preserve exact-execution honesty.