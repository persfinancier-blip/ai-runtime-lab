# PR #187 current-main overlap recheck — 2026-09-18 11:17 MSK

## LAB-086-first capability probe

Direct executable transport was probed first with:

`git clone https://github.com/persfinancier-blip/ai-runtime-lab.git /tmp/airuntime`

Observed result: exit 128 before repository execution; `Could not resolve host: github.com`. Therefore the authoritative LAB-086 pin could not be byte-exactly materialized into the executable filesystem in this run, and no LAB-086 executable PASS/GREEN is claimed.

## PR #187 control-plane state

- PR #187 remains open and draft.
- Observed head remains `5bfdbdbd64d2281206b1c3d1e9a00db8bdbd4057`.
- GitHub reports `mergeable=false`; this metadata alone is not treated as concrete conflict evidence.
- Actual `main` tip before this evidence write: `1069b0c51669e5e3a4daca4aff226a52cd89d654`.
- Fresh compare from PR-reported base snapshot `2c72b76b2f1ffbee520e3871d4f1e0e878fe7974` to actual main reports main ahead by 233 commits and behind by 0.
- Complete returned changed-file inventory remains `research/*` additions plus `state/CURRENT.md`; no `experiments/*` or `tests/*` overlap is present.
- PR discussion was re-read; no new concrete source/test defect requiring branch mutation was identified from returned material.

## Decision

Do not rebase, merge, or mutate PR #187 merely to refresh mergeability metadata. Keep it draft. Exact repository/downstream execution remains pending byte-preserving materialization.

## Exact next action

Probe LAB-086 first again. If authoritative pin `1fa85a0e34c9ae67da57f1e64dadccf211feacc0` can be placed byte-for-byte into an executable filesystem, verify identity before executing the complete gate. Otherwise re-read actual main, PR #187 head/reviews, and source/test overlap and react only to concrete drift or defects.
