# PR #187 mergeability causal triangulation — 2026-09-16 11:19 MSK

## Observation

LAB-086 was probed first. Direct `git clone https://github.com/persfinancier-blip/ai-runtime-lab.git` failed before repository execution with `Could not resolve host: github.com`, exit 128. No executable PASS is claimed.

PR #187 remains open/draft at head `5bfdbdbd64d2281206b1c3d1e9a00db8bdbd4057`; GitHub currently reports `mergeable=false`.

Current `main` is `70467347c924e9ca21a21bcee4cf07ad6b907a2a`. Comparing current main to the PR head reports divergence of 84 commits ahead / 137 behind with merge base `2c72b76b2f1ffbee520e3871d4f1e0e878fe7974`.

## Stronger causal evidence

GitHub still exposes synthetic merge commit `d01d446fc5fae68dbf030b8d5bf4a379be83db75`, created when PR head `5bfdbdbd...` was merged by GitHub into then-main `6e29f6d3eca2ab8be37938cf388ea5b191a0ac7f`. Its two parents are exactly `6e29f6d...` and `5bfdbdbd...`. This proves the unchanged PR head was mechanically mergeable against main at `6e29f6d...`.

Current main is a descendant of that prior main. The compare from the PR merge base through current main shows only `research/*` additions and `state/CURRENT.md` modification. The PR's current 44-file delta contains only `experiments/*` and `tests/*`; it does not modify `research/*` or `state/CURRENT.md`.

Therefore the commits added to main after the last known-good synthetic merge do not create a same-path textual overlap with PR #187. The available control-plane evidence does not support diagnosing a source-level merge conflict. `mergeable=false` is retained as an observed GitHub state whose exact internal cause is unresolved; no rebase, merge, low-level ref operation, or speculative source edit is justified from this signal alone.

## Decision

Keep PR #187 draft and unchanged. Do not broaden LAB-094/095/096. Re-check mergeability on the next run. If byte-exact materialization becomes available, verify retained hashes and execute the recorded focused/composed/downstream gates before any integration. If `mergeable=false` persists, seek an explicit supported conflict/merge-state signal; do not infer a conflict from the boolean alone.
