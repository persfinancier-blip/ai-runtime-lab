# PR #187 current-main overlap recheck — 2026-09-18 13:17 Europe/Moscow

## LAB-086 first probe

Per `state/CURRENT.md`, LAB-086 was probed before fallback work.

Command attempted in the current execution container:

`git clone https://github.com/persfinancier-blip/ai-runtime-lab.git /tmp/airuntime`

Observed result: exit 128 before repository code execution, with `Could not resolve host: github.com`. No LAB-086 executable PASS/GREEN is claimed. Connector access remains control-plane access, not a byte-preserving bridge into the executable filesystem for the security-critical authoritative pin.

## PR #187 state

GitHub reports PR #187 open and draft, head `5bfdbdbd64d2281206b1c3d1e9a00db8bdbd4057`, base snapshot `2c72b76b2f1ffbee520e3871d4f1e0e878fe7974`. `mergeable=false` is observed but is not treated alone as concrete conflict evidence.

Actual `main` tip before this evidence write was `85cb4752fe765d885f706f72391b8b0ae78e9c2e`.

A fresh complete compare from PR base snapshot `2c72b76b2f1ffbee520e3871d4f1e0e878fe7974` to actual main reports:

- status: ahead;
- main ahead by 237 commits;
- main behind by 0;
- returned changed-file inventory consists only of `research/*` additions plus `state/CURRENT.md`;
- no `experiments/*` or `tests/*` main-side overlap is present.

PR discussion was re-read through the connector. Returned material contains no new concrete source/test defect requiring mutation. Therefore no rebase/merge/source broadening was performed merely to refresh mergeability metadata.

## Decision

Keep PR #187 draft and unchanged. Exact repository/downstream execution remains pending. On the next run, probe LAB-086 first; only execute its complete gate after byte-exact authoritative materialization. If transport remains blocked, re-read actual main, PR #187 head/reviews and overlap, and react only to concrete source/test overlap, head drift, or a new review defect.