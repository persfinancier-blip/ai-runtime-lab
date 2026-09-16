# PR #187 regenerated merge-ref evidence — 2026-09-16 19:14 MSK

## Runtime probe
LAB-086 was probed first as required. Direct `git clone https://github.com/persfinancier-blip/ai-runtime-lab.git` failed before repository code execution with `Could not resolve host: github.com`, exit 128. No LAB-086 executable PASS is claimed.

## New control-plane evidence
PR #187 remains open/draft at head `5bfdbdbd64d2281206b1c3d1e9a00db8bdbd4057`.

GitHub now exposes synthetic merge commit `88470af85668535527e49a6bd35b57ed08093518`. Its verified commit payload has exactly these parents:

1. `917a8411c8643e82f0a990c2ae84e6b8841df0e4` (then-current main)
2. `5bfdbdbd64d2281206b1c3d1e9a00db8bdbd4057` (PR #187 head)

and message `Merge 5bfdbdbd... into 917a8411...`.

This is stronger evidence than the previously stale synthetic merge ref: GitHub successfully constructed the exact PR head against a substantially newer main tip without a source merge conflict. The current actual main tip is now `51b6055079267f506e3062fe6cdacbe9cd0f70bf`; commits after `917a8411...` are this lab's research/state handoff commits, not PR production/test edits.

`get_pr_info` nevertheless currently reports `mergeable=false`. Given the successfully regenerated merge commit against `917a8411...`, that boolean must not be treated as proof of a source-level conflict. No rebase/merge is justified merely to refresh metadata.

PR discussion was re-read; no new concrete requested change/review defect was observed in this run.

## Decision
Keep PR #187 draft. Do not broaden LAB-094/095/096 or mutate branch history based only on `mergeable=false`. The acceptance blocker remains exact byte-identical executable materialization and retained gates.

## Exact next action
Probe LAB-086 first next run. If byte-exact materialization becomes available, verify retained hashes and execute the closure inventory, then full pytest + compileall. If transport remains blocked, re-read actual main, PR head, merge-ref parents, and reviews; react only to head drift, production/test overlap, or a concrete defect.
