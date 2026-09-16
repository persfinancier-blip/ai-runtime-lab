# PR #187 current-main overlap recheck — 2026-09-16 17:16 MSK

## Observations

- Mandatory LAB-086 execution probe was performed first in this run.
- `git clone https://github.com/persfinancier-blip/ai-runtime-lab.git /tmp/ai-runtime-lab` failed before repository code execution with `Could not resolve host: github.com`, exit 128. No LAB-086 executable PASS is claimed.
- Actual `main` tip read directly from `/branches/main`: `0f7ae99138281ab5200095038a5e04dde2e6fc1a`.
- Draft PR #187 head remains `5bfdbdbd64d2281206b1c3d1e9a00db8bdbd4057`; GitHub PR metadata still reports base snapshot / merge base `2c72b76b2f1ffbee520e3871d4f1e0e878fe7974` and `mergeable=false`.
- Direct compare `2c72b76b... -> 0f7ae991...` reports 149 post-base commits on current main.
- Every changed path returned for current main remains under `research/*` or `state/CURRENT.md`.
- PR #187 remains a 44-file `experiments/*` / `tests/*` change set from the retained closure inventory; no current-main source/test path overlap is evidenced.
- PR discussion was re-read; no new concrete requested change or review defect was observed that supersedes the retained exact-execution gate.

## Decision

Do not rebase/merge PR #187 merely to refresh stale GitHub merge metadata, and do not broaden LAB-094/095/096 without a concrete defect. The highest-value unresolved work remains exact execution when byte-preserving repository materialization becomes available.

## Exact next action

Probe LAB-086 first. If authoritative pin `1fa85a0e34c9ae67da57f1e64dadccf211feacc0` can be materialized byte-for-byte, execute its complete retained gate. Otherwise re-read actual main and PR #187 head; react only to source/test overlap, head drift, or a concrete review defect. If PR #187 byte-exact materialization becomes available, verify retained hashes first, execute the focused/composed/LAB-080/LAB-081 inventory, then full pytest and compileall. Do not claim executable GREEN from source/control-plane inspection.