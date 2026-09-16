# PR #187 current-main overlap proof — 2026-09-16 13:18 MSK

## Observation

LAB-086 was probed first in this run. Direct `git clone https://github.com/persfinancier-blip/ai-runtime-lab.git` failed before repository execution with `Could not resolve host: github.com`, exit 128. No executable PASS is claimed.

PR #187 remains open/draft at head `5bfdbdbd64d2281206b1c3d1e9a00db8bdbd4057`; `get_pr_info` still reports `mergeable=false` and a stale base snapshot `2c72b76b2f1ffbee520e3871d4f1e0e878fe7974`.

The actual `main` branch tip read directly from `/branches/main` is `7f2defd5224c7337cb689d203fcc120b47a1857b`.

A current compare from PR head `5bfdbdbd...` to actual main `7f2defd...` reports `diverged`, with merge base `2c72b76b...`, main ahead by 141 commits and PR head ahead by 84 commits. Crucially, every file changed on main since that merge base is under `research/*` or `state/CURRENT.md`.

The PR's own 44 changed files are all under `experiments/*` or `tests/*`. Therefore the current branch histories have **zero path overlap** between PR #187's source/test patch and main's post-base changes.

## Decision

This is stronger evidence than the stale synthetic merge ref: there is no current path-level overlap capable of producing an ordinary textual source conflict between PR #187 and main. `mergeable=false` remains unexplained GitHub control-plane state, but it is not supported by the current compare as a source-conflict signal.

Do not rebase/merge merely to refresh GitHub metadata. PR #187 must remain draft because its retained exact executable gates are still unavailable, independent of mechanical mergeability.

## Next action

Probe LAB-086 first next run. If transport remains blocked, re-read actual `main` tip and PR #187 head, compare them against their merge base, and react only to new overlap/drift/review defects. If byte-exact materialization becomes available, verify retained hashes and execute the closure inventory before any integration.
