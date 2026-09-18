# PR #187 current-main overlap recheck — 2026-09-18 10:18 MSK

## LAB-086 first probe

Per `state/CURRENT.md`, LAB-086 was probed before fallback work.

Command executed in the current runtime:

```text
git clone https://github.com/persfinancier-blip/ai-runtime-lab.git /tmp/airuntime
```

Observed result: exit 128 before repository execution with `Could not resolve host: github.com`.

Therefore the authoritative LAB-086 pin `1fa85a0e34c9ae67da57f1e64dadccf211feacc0` was not byte-exact materialized into the executable filesystem and no LAB-086 executable PASS/GREEN is claimed.

## PR #187 control-plane recheck

GitHub control-plane reads remain available.

- actual `main` before this evidence write: `00e12204225a67b3ecad32864d795a55db46fcb4`;
- PR #187: open, draft;
- PR head: `5bfdbdbd64d2281206b1c3d1e9a00db8bdbd4057` (unchanged);
- reported PR base snapshot: `2c72b76b2f1ffbee520e3871d4f1e0e878fe7974`;
- fresh compare base snapshot -> actual main: main ahead 231, behind 0;
- complete returned changed-file inventory contains only `research/*` additions and `state/CURRENT.md` modification;
- no `experiments/*` or `tests/*` main-side overlap is present.

GitHub currently reports `mergeable=false`; this remains metadata, not by itself proof of a concrete source/test conflict. PR discussion was re-read and no new concrete review defect requiring branch mutation was identified in returned material.

## Decision

Do not rebase/merge or mutate PR #187 merely to refresh mergeability metadata. Exact repository/downstream execution remains transport-blocked. Continue to require byte-exact identity before any executable GREEN claim.

## Exact next action

Probe LAB-086 first next run. If byte-exact materialization becomes available, verify authoritative pin identity and execute the complete retained LAB-086 gate. Otherwise re-read actual main, PR #187 head/reviews and source/test overlap, reacting only to concrete overlap, head drift, or a new actionable defect.