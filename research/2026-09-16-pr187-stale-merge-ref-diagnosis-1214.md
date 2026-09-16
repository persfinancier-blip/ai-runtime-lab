# PR #187 stale merge-ref diagnosis — 2026-09-16 12:14 MSK

## Observation

LAB-086 was probed first. A direct `git clone https://github.com/persfinancier-blip/ai-runtime-lab.git` failed before repository execution with `Could not resolve host: github.com` and exit 128. No executable PASS is claimed.

PR #187 remains open/draft with unchanged head `5bfdbdbd64d2281206b1c3d1e9a00db8bdbd4057`. At this observation GitHub reports the PR base SHA as current main `2c72b76b2f1ffbee520e3871d4f1e0e878fe7974`.

The supported Git ref read for `refs/pull/187/merge` still returns `d01d446fc5fae68dbf030b8d5bf4a379be83db75`. Inspecting that commit proves it is an older synthetic merge whose parents are prior main `6e29f6d3eca2ab8be37938cf388ea5b191a0ac7f` and the unchanged PR head `5bfdbdbd64d2281206b1c3d1e9a00db8bdbd4057`.

## Decision

`refs/pull/187/merge` is stale relative to the PR's current base and therefore is not a valid current conflict/mergeability signal. Its continued existence only proves historical mechanical mergeability against prior main. Do not infer current mergeability from it, and do not rebase/merge merely to refresh the synthetic ref.

The stronger supported diagnosis now is: GitHub's merge ref has not been regenerated for current main. Until GitHub supplies a current-base merge commit or another explicit current conflict signal, keep #187 draft and avoid speculative integration/source edits.

## Next action

Probe LAB-086 first. If still transport-blocked, re-read PR #187. Treat a merge ref as current evidence only if its first parent equals the PR's then-current base SHA and its second parent equals the PR head. If the merge ref remains stale, inspect current compare/file overlap or newly reported review defects; do not broaden LAB-094/095/096.