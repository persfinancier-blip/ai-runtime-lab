# PR #187 current-main overlap recheck — 2026-09-17 01:16 Europe/Moscow

## Purpose
Continue the executable-readiness fallback required by `state/CURRENT.md` while LAB-086 exact execution remains transport-blocked.

## LAB-086 first probe
Executed in the current runtime:

```text
git ls-remote https://github.com/persfinancier-blip/ai-runtime-lab.git HEAD
fatal: unable to access 'https://github.com/persfinancier-blip/ai-runtime-lab.git/': Could not resolve host: github.com
exit 128
```

Failure occurred before repository code execution. No LAB-086 executable PASS/GREEN is claimed.

## Control-plane observations
- actual `main` tip before this evidence commit: `80bb503783f0620939dccd7d00e57175d6db0cbf`;
- draft PR #187 remains open at head `5bfdbdbd64d2281206b1c3d1e9a00db8bdbd4057`;
- PR discussion was re-read; no new concrete requested change/source-level defect requiring branch mutation was observed;
- compare from PR-reported base snapshot `2c72b76b2f1ffbee520e3871d4f1e0e878fe7974` to actual main reports `ahead_by=165`, `behind_by=0`;
- returned changed-file surface remains control-plane/evidence only (`research/*`, `state/CURRENT.md`), with no new overlap against PR #187 implementation surface (`experiments/*`, `tests/*`).

GitHub PR metadata remains unsuitable as sole source-conflict evidence. In particular, synthetic merge refs/mergeability observations are ephemeral; react only to concrete path/source overlap, head drift, or a specific review defect.

## Decision
Do not rebase, merge, or broaden LAB-094/095/096 solely to refresh GitHub metadata. Keep PR #187 draft. Exact repository pytest/compileall remains unexecuted because byte-exact repository materialization is unavailable in this runtime.

## Next action
Probe LAB-086 first next run. If authoritative pin `1fa85a0e34c9ae67da57f1e64dadccf211feacc0` becomes byte-exact executable, verify hashes and execute the complete LAB-086 gate. Otherwise re-read actual main, PR #187 head/reviews, and source/test overlap. If byte-exact PR #187 closure becomes executable, run the retained focused/composed/LAB-080/LAB-081 inventory, then full pytest and compileall; do not infer GREEN from source inspection.
