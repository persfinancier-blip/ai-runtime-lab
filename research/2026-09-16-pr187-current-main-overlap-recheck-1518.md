# PR #187 current-main overlap recheck — 2026-09-16 15:18 MSK

## Execution observation
LAB-086 was probed first as required. A direct `git clone https://github.com/persfinancier-blip/ai-runtime-lab.git` failed before repository execution with `Could not resolve host: github.com`, exit 128. No LAB-086 executable PASS is claimed.

## Current control-plane observations
- Direct `/branches/main` read: actual `main` tip `917a8411c8643e82f0a990c2ae84e6b8841df0e4`.
- PR #187 remains open/draft, head `5bfdbdbd64d2281206b1c3d1e9a00db8bdbd4057`, 44 changed files.
- `get_pr_info` still reports stale base SHA `2c72b76b2f1ffbee520e3871d4f1e0e878fe7974` and `mergeable=false`; this metadata is not treated alone as source-conflict evidence.
- Compare `2c72b76b... -> 917a8411...` reports 145 post-base commits on current main.
- Every returned current-main changed path remains under `research/*` or `state/CURRENT.md`.
- PR #187 changed paths remain under `experiments/*` or `tests/*`.
- Inline review threads are empty.

## Decision
There is still zero observed path overlap between current-main post-base changes and PR #187 source/test paths, and no concrete review defect. Do not rebase/merge or broaden LAB-094/095/096 merely to refresh stale GitHub mergeability metadata. Exact repository execution remains blocked by byte-exact materialization/transport, so no executable GREEN is claimed.

## Next action
Probe LAB-086 first next run. If transport remains blocked, read actual main tip and PR #187 head again, compare current-main post-base paths against PR changed paths, and inspect review threads. Only act on real drift/overlap/review defects. If byte-exact materialization becomes available, verify retained blob/hash identity and execute the closure inventory gates, then full pytest and compileall.
