# PR #187 synthetic merge-ref ephemerality recheck — 2026-09-16 20:18 MSK

## Scope
Follow `state/CURRENT.md`: probe LAB-086 first, then re-read actual `main`, PR #187 head/reviews, and synthetic merge evidence without claiming executable GREEN.

## Observations
1. LAB-086 transport probe: `git ls-remote https://github.com/persfinancier-blip/ai-runtime-lab.git HEAD` failed before repository execution with exit 128 and `Could not resolve host: github.com`. No LAB-086 executable PASS is claimed.
2. Actual `main` tip is `7e3c0c773b986755ee097738618fc406546f48ed`.
3. PR #187 remains open/draft and its head remains `5bfdbdbd64d2281206b1c3d1e9a00db8bdbd4057`; no head drift was observed.
4. PR discussion was re-read. No new concrete requested change or review defect was found in the returned discussion timeline.
5. A direct GET of `git/ref/pulls/187/merge` returned 404 in this run. This shows the synthetic merge ref is ephemeral and must not be treated as durable repository state.
6. The previously generated merge commit object `88470af85668535527e49a6bd35b57ed08093518` remains retrievable and verified. Its parents are `917a8411c8643e82f0a990c2ae84e6b8841df0e4` (then-main) and the unchanged PR head `5bfdbdbd64d2281206b1c3d1e9a00db8bdbd4057`. Therefore the historical fact that GitHub successfully constructed that merge remains durable even though the convenience ref disappeared.

## Decision
Do not infer a new source conflict from the missing synthetic ref. Do not rebase/merge or broaden LAB-094/095/096 merely to regenerate GitHub metadata. Treat synthetic merge refs as ephemeral hints; when available, validate their parent identities before use. Treat the verified merge commit object as historical evidence only, not proof against future `main` tips.

## Exact next action
Probe LAB-086 first. If byte-exact materialization becomes available, verify authoritative pin/blob identities and execute the retained closure inventory, then full pytest + compileall. If transport remains blocked, re-read actual `main`, PR #187 head/reviews, and source/test overlap; react only to concrete drift, overlap, or a new review defect.