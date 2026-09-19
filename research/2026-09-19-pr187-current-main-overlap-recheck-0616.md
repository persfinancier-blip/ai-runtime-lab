# PR #187 current-main overlap recheck — 2026-09-19 06:16 MSK

## LAB-086-first execution probe

Attempted direct clone into `/tmp/airuntime` before any fallback work:

```text
git clone https://github.com/persfinancier-blip/ai-runtime-lab.git /tmp/airuntime
fatal: unable to access 'https://github.com/persfinancier-blip/ai-runtime-lab.git/': Could not resolve host: github.com
exit 128
```

Failure occurred before repository code execution. No LAB-086 executable PASS/GREEN is claimed and the authoritative-pin byte-exact gate remains blocked in this runtime.

## Control-plane observations

- actual `main` tip before this evidence write: `45d9dc6f2a35aab108c3280f5087b9a5f199bc4a`;
- PR #187: open, draft, head `5bfdbdbd64d2281206b1c3d1e9a00db8bdbd4057`, unchanged;
- GitHub currently reports `mergeable=false`; this metadata alone is not concrete source-conflict evidence;
- submitted review collection is empty;
- compare from PR-reported base snapshot `2c72b76b2f1ffbee520e3871d4f1e0e878fe7974` to actual main: `ahead_by=271`, `behind_by=0`;
- complete compact changed-file inventory remains only `research/*` additions plus `state/CURRENT.md`; there is no `experiments/*` or `tests/*` main-side overlap.

## Decision

Do not rebase, merge, broaden scope, or claim executable validation merely to refresh mergeability metadata. Keep PR #187 draft. React only to concrete source/test overlap, head drift, or a new actionable review defect. Next run probes LAB-086 first; if byte-exact materialization becomes available, verify authoritative identity before executing the retained full gate.
