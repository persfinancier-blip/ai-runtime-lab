# PR #187 current-main overlap recheck — 2026-09-16 14:16 MSK

## Observations

- LAB-086 was probed first in the current runtime with direct `git clone https://github.com/persfinancier-blip/ai-runtime-lab.git`.
- The clone failed before repository code execution: `Could not resolve host: github.com`, exit 128. No executable LAB-086 PASS is claimed.
- Direct branch read reports actual `main` tip `1c6f698bd86775c7428d6ba45ccd67234376a612`.
- PR #187 remains open/draft with unchanged head `5bfdbdbd64d2281206b1c3d1e9a00db8bdbd4057`; `get_pr_info` still exposes stale base snapshot `2c72b76b2f1ffbee520e3871d4f1e0e878fe7974` and `mergeable=false`.
- Compare from merge base/base snapshot `2c72b76b...` to actual main `1c6f698b...` reports 143 commits ahead. Every returned changed path is under `research/*` or `state/CURRENT.md`.
- PR #187's previously audited 44 changed files remain under `experiments/*` and `tests/*`; head did not drift.
- PR #187 inline review comments remain empty in this run.

## Decision

The actual-main post-base changes remain path-disjoint from PR #187 source/test changes. There is still no concrete source-level conflict or review defect supporting a rebase, merge, or expansion of LAB-094/095/096. Treat `mergeable=false` as insufficient by itself while PR metadata/merge ref remain stale.

Do not claim executable GREEN. If byte-exact repository materialization becomes available, verify retained hashes first and execute the recorded focused/composed/LAB-080/LAB-081 inventory followed by full pytest and compileall.
