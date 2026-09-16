# Current Lab State

Last updated: 2026-09-17

## Active objective
LAB-086 remains priority #1: execute the exact asymmetric break-glass history migration gate from authoritative executable pin `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`. When byte-exact materialization remains unavailable, maintain executable-readiness closure for LAB-094/#179 + LAB-095/#180 + LAB-096/#181 on draft PR #187. LAB-099 PREPARED authority waits on LAB-095 completion.

## Active issue / branch / PR
- #163 / LAB-086: draft PR #165; keep draft.
- #179 LAB-094 + #180 LAB-095 + #181 LAB-096: branch `lab-095-database-identity-red-intent`, draft PR #187; observed head `5bfdbdbd64d2281206b1c3d1e9a00db8bdbd4057`; keep draft.
- #169 LAB-090: draft PR #175 retained as donor; composed on PR #187.
- #176 LAB-092: draft PR #177 retained as donor; composed/adapted on PR #187.
- #188 LAB-101: bootstrap + authenticated confirmation bridge/composition regressions on PR #187; exact execution remains.
- #184 LAB-099: draft PR #186; blocked on LAB-095 completion.

## Last completed step
LAB-086 was probed first. `git ls-remote https://github.com/persfinancier-blip/ai-runtime-lab.git HEAD` failed before repository execution with `Could not resolve host: github.com`, exit 128; no LAB-086 PASS is claimed.

PR #187 was rechecked against actual main `78dbfe2edac633659903348177efe2436bf7fcfe`. PR remains open/draft at unchanged head `5bfdbdbd64d2281206b1c3d1e9a00db8bdbd4057`; open issue/PR inspection exposed no new concrete source-level defect requiring branch mutation. Fresh compare from reported base snapshot `2c72b76b2f1ffbee520e3871d4f1e0e878fe7974` to actual main reports main ahead by 163 commits and behind by 0; every returned changed path is `research/*` or `state/CURRENT.md`, so there is still no new source/test path overlap with PR #187's `experiments/*` + `tests/*` implementation surface. GitHub still reports `mergeable=false`; that boolean alone is not treated as source-conflict proof. Evidence: `research/2026-09-17-pr187-current-main-overlap-recheck-0015.md`, evidence commit `e4b5d449d73e131ad20a6839a1f10488d93b820e`. Exact execution is not claimed.

## Known failures / blockers
- LAB-086 complete real-ledger gate remains unexecuted because shell DNS cannot resolve GitHub and no supported connector-to-filesystem byte-preserving bridge is exposed.
- Exact PR #187 repository pytest/compileall remains unavailable for the same materialization reason; committed/source-reviewed regressions are not a GREEN claim.
- PRs #165/#172/#173/#175/#177/#186/#187 remain draft until retained exact gates execute.
- LAB-095 exact no-stub reconstruction/hash verification and execution remain pending.
- LAB-094/095/096 construction-bound authority graph is source-closed; exact behavioral/downstream gates remain pending.
- LAB-090/LAB-092/LAB-101 composed gates remain source-audited but not exact-executed.
- PR #187 mergeability metadata has been inconsistent across observations. Synthetic `refs/pull/*/merge` is ephemeral; never use its absence alone as conflict evidence, and validate parent identities whenever it exists.

## Exact next action
Probe LAB-086 first. Execute its complete gate only if authoritative pin `1fa85a0e34c9ae67da57f1e64dadccf211feacc0` can be placed byte-for-byte into an executable filesystem.

If LAB-086 remains transport-blocked, re-read actual `main` tip, PR #187 head/reviews, and source/test overlap. Treat a synthetic merge ref as optional/ephemeral; if present, validate both parents before using it. React only to concrete source/test overlap, head drift, or a new review defect; do not rebase/merge or broaden LAB-094/095/096 merely to refresh GitHub metadata. If byte-exact materialization becomes available, verify retained blob/hash identity first, execute the focused/composed/LAB-080/LAB-081 inventory in `research/2026-09-16-lab094-096-closure-inventory.md`, then full pytest and compileall. Do not claim executable GREEN from source inspection.

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
