# PR #187 current-main overlap recheck — 2026-09-16 18:17 MSK

## Scope
Mandatory LAB-086 capability probe first, then PR #187 drift/review recheck against the actual `main` tip.

## Observations
- LAB-086 direct `git clone https://github.com/persfinancier-blip/ai-runtime-lab.git` failed before repository execution: `Could not resolve host: github.com`, exit 128. No executable PASS is claimed.
- Actual `main` tip observed via `/branches/main`: `51d35a20b7863691294b3a7e26ab8292fa1c16ef`.
- PR #187 remains open/draft with head `5bfdbdbd64d2281206b1c3d1e9a00db8bdbd4057`.
- PR metadata still carries base snapshot `2c72b76b2f1ffbee520e3871d4f1e0e878fe7974`; compare from that base snapshot to actual main reports 151 commits ahead on main.
- PR #187 inline review comments endpoint returned an empty list.
- No new concrete review defect was observed in this run.

## Decision
Do not claim executable GREEN. Do not rebase/merge or broaden LAB-094/095/096 merely to refresh stale GitHub metadata. The retained executable gates remain the highest-value next action if byte-exact materialization becomes available.

## Exact next action
Probe LAB-086 first. If authoritative pin `1fa85a0e34c9ae67da57f1e64dadccf211feacc0` can be materialized byte-for-byte into an executable filesystem, run the complete LAB-086 gate. Otherwise re-read actual main and PR #187 head/reviews; react only to concrete drift/overlap/review defects. If exact PR #187 materialization becomes available, verify retained hashes then execute the focused/composed/LAB-080/LAB-081 inventory, followed by full pytest and compileall.
