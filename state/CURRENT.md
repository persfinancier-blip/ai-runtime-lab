# Current Lab State

Last updated: 2026-09-16

## Active objective
LAB-086 remains priority #1: execute the exact asymmetric break-glass history migration gate from authoritative executable pin `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`. When byte-exact materialization remains unavailable, finish executable-readiness closure for LAB-094/#179 + LAB-095/#180 + LAB-096/#181 on draft PR #187. LAB-099 PREPARED authority waits on LAB-095 completion.

## Active issue / branch / PR
- #163 / LAB-086: draft PR #165; keep draft.
- #179 LAB-094 + #180 LAB-095 + #181 LAB-096: branch `lab-095-database-identity-red-intent`, draft PR #187; observed head `5bfdbdbd64d2281206b1c3d1e9a00db8bdbd4057`; keep draft. `get_pr_info` reports base snapshot `2c72b76b2f1ffbee520e3871d4f1e0e878fe7974`, while direct `/branches/main` read in the latest run reports actual main tip `7f2defd5224c7337cb689d203fcc120b47a1857b`. The synthetic merge ref remains stale and is not current mergeability evidence.
- #169 LAB-090: draft PR #175 retained as donor; composed on PR #187.
- #176 LAB-092: draft PR #177 retained as donor; composed/adapted on PR #187.
- #188 LAB-101: explicit bootstrap + authenticated confirmation bridge and composition regressions are on PR #187; exact execution remains.
- #184 LAB-099: draft PR #186; blocked on LAB-095 completion.

## Last completed step
LAB-086 was probed first. Direct clone failed before repository execution with `Could not resolve host: github.com`, exit 128; no LAB-086 PASS is claimed.

Strengthened PR #187 merge-state diagnosis against the actual current main tip. Compare of PR head `5bfdbdbd...` with actual main `7f2defd...` reports divergence from merge base `2c72b76b...`: main has 141 post-base commits and PR has 84. Every current-main post-base changed file is under `research/*` or `state/CURRENT.md`; all 44 PR #187 changed files are under `experiments/*` or `tests/*`. Therefore current histories have zero path overlap between PR source/test changes and main post-base changes. `mergeable=false` remains unexplained control-plane state, but current compare does not support an ordinary source conflict. Evidence: `research/2026-09-16-pr187-current-main-overlap-proof-1318.md`, main commit `ea3a89574b5567af4f61c2ec590d4ec9a88a6d93`. Exact execution is not claimed.

## Known failures / blockers
- LAB-086 complete real-ledger gate remains unexecuted because shell DNS cannot resolve GitHub and no supported connector-to-filesystem byte-preserving bridge is exposed.
- Exact PR #187 repository pytest/compileall remains unavailable for the same materialization reason; committed/source-reviewed regressions are not a GREEN claim.
- PRs #165/#172/#173/#175/#177/#186/#187 remain draft until retained exact gates execute.
- LAB-095 exact no-stub reconstruction/hash verification and execution remain pending.
- LAB-094/095/096 construction-bound authority graph is source-closed for bootstrap root, canonical path, and provider-history strategy; exact behavioral/downstream gates remain pending.
- LAB-090/LAB-092/LAB-101 composed gates remain source-audited but not exact-executed.
- PR #187's synthetic merge ref and `get_pr_info` base snapshot are stale relative to actual main. Do not use them alone as current conflict/mergeability signals.

## Exact next action
Probe LAB-086 first. Execute its complete gate only if authoritative pin `1fa85a0e34c9ae67da57f1e64dadccf211feacc0` can be placed byte-for-byte into an executable filesystem.

If LAB-086 remains transport-blocked, read actual `main` tip directly and re-read PR #187 head. Compare both against their merge base. If the current-main post-base changes remain disjoint from PR source/test paths and there are no new review defects, do not rebase/merge or broaden LAB-094/095/096 merely to refresh GitHub metadata. If byte-exact materialization becomes available, verify retained blob/hash identity first, execute the focused/composed/LAB-080/LAB-081 inventory in `research/2026-09-16-lab094-096-closure-inventory.md`, then full pytest and compileall. Do not claim executable GREEN from source inspection.

## Backlog
- #163 LAB-086 — IN_PROGRESS; exact executable gate pending.
- #179 LAB-094 — source closure composed on PR #187; exact regression/downstream execution pending.
- #180 LAB-095 — IN_PROGRESS; source closure/hash inventory reconciled; exact/downstream gates pending.
- #181 LAB-096 — IN_PROGRESS/COMPOSED ON PR #187; source closure reconciled; exact/downstream validation pending.
- #169 LAB-090 — composed; execution pending.
- #176 LAB-092 — composed; exact execution pending.
- #188 LAB-101 — IN_PROGRESS; source-composed; exact execution pending.
- #167 LAB-088, #170 LAB-091 — retained draft gates pending.
- #178..185 LAB-093..100 — architecture/security follow-ups.
- #184 LAB-099 — PREPARED authority waits on LAB-095 completion.
