# PR #187 current-main overlap recheck — 2026-09-18 16:16 MSK

## LAB-086-first probe

Per repository priority, direct byte-preserving materialization was probed first:

`git clone https://github.com/persfinancier-blip/ai-runtime-lab.git /tmp/airuntime`

Observed result: exit 128 before repository execution, `Could not resolve host: github.com`. No LAB-086 executable PASS/GREEN is claimed.

## Control-plane state

- actual main tip observed before this evidence write: `507c6688e9e2942c21778f29607a5708d8acd5bd`;
- PR #187 remains open/draft;
- PR #187 head remains `5bfdbdbd64d2281206b1c3d1e9a00db8bdbd4057`;
- GitHub reports `mergeable=false`; this is not treated as standalone conflict evidence.

## Main-side overlap check

Fresh compare `2c72b76b2f1ffbee520e3871d4f1e0e878fe7974..507c6688e9e2942c21778f29607a5708d8acd5bd` reports:

- status: ahead;
- ahead_by: 243;
- behind_by: 0;
- complete returned changed-file inventory: only `research/*` additions and `state/CURRENT.md` modification.

No `experiments/*` or `tests/*` main-side overlap is present. Therefore no concrete source/test conflict or drift was found that justifies rebasing, merging, or broadening PR #187.

## Decision

Keep PR #187 draft and unchanged. Preserve the exact-execution gate. Next run probes LAB-086 byte-exact materialization first; if still blocked, refresh actual main/head/reviews and react only to concrete source/test overlap, head drift, or actionable review defects.
