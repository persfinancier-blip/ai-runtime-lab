# PR #187 current-main overlap recheck — 2026-09-19 03:14 MSK

## LAB-086-first capability probe

Attempted direct clone into `/tmp/airuntime` before any fallback work:

`git clone https://github.com/persfinancier-blip/ai-runtime-lab.git /tmp/airuntime`

Observed result: exit 128, `Could not resolve host: github.com`. Failure occurred before repository code execution. No LAB-086 executable PASS/GREEN is claimed. The GitHub connector remains control-plane access, not a demonstrated byte-preserving executable materialization path for authoritative pin `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`.

## PR #187 / main drift

Observed PR #187 remains open/draft at head `5bfdbdbd64d2281206b1c3d1e9a00db8bdbd4057`; GitHub metadata currently reports `mergeable=false`.

Actual `main` tip before this evidence write: `449ca4863cea7e54e4b96cacd466548b03ff2575`.

Compact compare from PR-reported base snapshot `2c72b76b2f1ffbee520e3871d4f1e0e878fe7974` to that main tip reports:
- status: ahead;
- main ahead by 265 commits;
- main behind by 0;
- complete changed-file inventory remains additions under `research/*` plus `state/CURRENT.md` only;
- no `experiments/*` or `tests/*` overlap is present.

PR discussion was re-read. No new concrete source/test review defect requiring branch mutation was observed. `mergeable=false` alone remains metadata, not concrete source/test conflict evidence.

## Decision

Do not rebase/merge/broaden PR #187 merely to refresh mergeability metadata. Keep draft. Exact repository execution remains the retained gate. Next run must probe LAB-086 first; if byte-exact authoritative materialization becomes available, verify identity before executing the retained gate inventory.