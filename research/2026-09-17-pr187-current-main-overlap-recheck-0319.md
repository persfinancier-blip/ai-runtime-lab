# PR #187 current-main overlap recheck — 2026-09-17 03:19 MSK

## LAB-086 first probe

Executed in this runtime:

```text
git ls-remote https://github.com/persfinancier-blip/ai-runtime-lab.git HEAD
fatal: unable to access 'https://github.com/persfinancier-blip/ai-runtime-lab.git/': Could not resolve host: github.com
exit 128
```

The failure occurred before repository code execution. No LAB-086 executable PASS/GREEN is claimed.

## Control-plane observations

- Actual `main` tip before this evidence write: `60716ee37faad2a3a6a82a70589fc2753896b2a8`.
- Draft PR #187 remains open/draft.
- PR #187 head remains `5bfdbdbd64d2281206b1c3d1e9a00db8bdbd4057`.
- GitHub currently reports `mergeable=false`; this metadata alone is not treated as source-level conflict proof.
- Fresh compare from PR-reported base snapshot `2c72b76b2f1ffbee520e3871d4f1e0e878fe7974` to actual main reports `ahead_by=169`, `behind_by=0`.
- Every returned changed path remains under `research/*` or `state/CURRENT.md`; there is still no new source/test path overlap with PR #187's `experiments/*` + `tests/*` implementation surface.
- Fresh PR discussion inspection exposed no new concrete review defect/requested source change requiring branch mutation.

## Decision

Do not rebase, merge, or broaden LAB-094/095/096 merely to refresh GitHub mergeability metadata. Keep PR #187 draft. Exact repository execution remains the retained gate.

## Next action

Probe LAB-086 first next run. If byte-exact executable materialization becomes available, verify authoritative pin/blob identity before executing its complete gate. Otherwise re-read actual main tip, PR #187 head/reviews, and source/test overlap; react only to concrete source/test drift or a new review defect. If PR #187 can be materialized byte-exactly, run the retained focused/composed/LAB-080/LAB-081 inventory, then full pytest and compileall; do not infer GREEN from source inspection.
