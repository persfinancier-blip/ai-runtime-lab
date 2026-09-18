# PR #187 current-main overlap recheck — 2026-09-18 12:18 Europe/Moscow

## LAB-086-first execution probe

The required LAB-086 execution path was probed first in this run with a direct container clone:

```text
git clone https://github.com/persfinancier-blip/ai-runtime-lab.git /tmp/airuntime
Cloning into '/tmp/airuntime'...
fatal: unable to access 'https://github.com/persfinancier-blip/ai-runtime-lab.git/': Could not resolve host: github.com
exit 128
```

This failed before repository code execution. No LAB-086 executable PASS/GREEN is claimed.

The GitHub connector can read the authoritative pin `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`, including base64 content, but the response is truncated at the presentation boundary. That is not a byte-preserving materialization path for the complete security-critical source, so model/manual reconstruction remains prohibited.

## PR #187 state

- PR: #187, open and draft.
- Observed head: `5bfdbdbd64d2281206b1c3d1e9a00db8bdbd4057` (unchanged).
- GitHub metadata currently reports `mergeable=false`; this is not treated as standalone conflict evidence.
- Actual `main` observed before this evidence write: `b729cf94192d33da1b4a7724075300ba67e7d6cd`.
- Full compare from PR-reported base snapshot `2c72b76b2f1ffbee520e3871d4f1e0e878fe7974` to that actual main reports `ahead_by=235`, `behind_by=0`.
- The complete returned changed-file inventory is still restricted to `research/*` additions and `state/CURRENT.md`; there is no new `experiments/*` or `tests/*` overlap with PR #187's implementation surface.
- PR discussion was re-read; no new concrete source/test defect requiring branch mutation was identified in the returned material.

## Decision

Do not rebase, merge, or mutate PR #187 merely to refresh mergeability metadata. Keep it draft. React only to concrete source/test overlap, head drift, or a new review defect.

## Next action

Probe LAB-086 first next run. If authoritative pin `1fa85a0e34c9ae67da57f1e64dadccf211feacc0` becomes byte-exactly materializable into an executable filesystem, verify identity before executing the complete retained gate. Otherwise re-read actual main/PR #187 head and discussion, and execute the PR #187 focused/composed/downstream inventory only if an exact repository closure becomes safely materializable. Never infer executable GREEN from source/control-plane inspection.