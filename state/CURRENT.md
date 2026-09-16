# Current Lab State

Last updated: 2026-09-16

## Active objective
LAB-086 remains priority #1: execute the exact asymmetric break-glass history migration gate from authoritative executable pin `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`. When byte-exact materialization remains unavailable, finish executable-readiness closure for LAB-094/#179 + LAB-095/#180 + LAB-096/#181 on draft PR #187. LAB-099 PREPARED authority waits on LAB-095 completion.

## Active issue / branch / PR
- #163 / LAB-086: draft PR #165; keep draft.
- #179 LAB-094 + #180 LAB-095 + #181 LAB-096: branch `lab-095-database-identity-red-intent`, draft PR #187; observed head `5bfdbdbd64d2281206b1c3d1e9a00db8bdbd4057`; keep draft. GitHub currently reports `mergeable=false`; current main is `70467347c924e9ca21a21bcee4cf07ad6b907a2a`, branch is 84 ahead / 137 behind. A retained GitHub synthetic merge commit proves this unchanged head merged cleanly into prior main `6e29f6d3eca2ab8be37938cf388ea5b191a0ac7f`; subsequent main-side paths are only `research/*` and `state/CURRENT.md`, disjoint from PR #187's `experiments/*` and `tests/*` delta. No source conflict is inferred from the boolean alone.
- #169 LAB-090: draft PR #175 retained as donor; composed on PR #187.
- #176 LAB-092: draft PR #177 retained as donor; composed/adapted on PR #187.
- #188 LAB-101: explicit bootstrap + authenticated confirmation bridge and composition regressions are on PR #187; exact execution remains.
- #184 LAB-099: draft PR #186; blocked on LAB-095 completion.

## Last completed step
LAB-086 was probed first in the current run. Direct clone failed before repository execution with `Could not resolve host: github.com`, exit 128; no LAB-086 PASS is claimed.

Triangulated PR #187 mergeability rather than treating `mergeable=false` as a source-conflict diagnosis. Head remains `5bfdbdbd64d2281206b1c3d1e9a00db8bdbd4057`; current main is `70467347c924e9ca21a21bcee4cf07ad6b907a2a`; compare reports 84 ahead / 137 behind. GitHub still exposes synthetic merge commit `d01d446fc5fae68dbf030b8d5bf4a379be83db75`, whose parents are prior main `6e29f6d3eca2ab8be37938cf388ea5b191a0ac7f` and the unchanged PR head. This proves the head was mechanically mergeable at that prior main. Main changes since the common merge base remain confined to `research/*` and `state/CURRENT.md`; PR #187 changes only `experiments/*` and `tests/*`. Thus available evidence does not identify a same-path textual conflict. No speculative rebase/merge/source edit was performed. Evidence: `research/2026-09-16-pr187-mergeability-causal-triangulation-1119.md`, main commit `085386c6824e15999cc142d906c73d0ffb7a9fec`. Exact execution is not claimed.

## Known failures / blockers
- LAB-086 complete real-ledger gate remains unexecuted because shell DNS cannot resolve GitHub and no supported connector-to-filesystem byte-preserving bridge is exposed.
- Exact PR #187 repository pytest/compileall remains unavailable for the same materialization reason; committed/source-reviewed regressions are not a GREEN claim.
- PRs #165/#172/#173/#175/#177/#186/#187 remain draft until retained exact gates execute.
- LAB-095 exact no-stub reconstruction/hash verification and execution remain pending.
- LAB-094/095/096 construction-bound authority graph is source-closed for bootstrap root, canonical path, and provider-history strategy; exact behavioral/downstream gates remain pending.
- LAB-090/LAB-092/LAB-101 composed gates remain source-audited but not exact-executed.
- PR #187 currently reports `mergeable=false`; retained synthetic-merge and disjoint-path evidence do not support a source-conflict diagnosis, so obtain a stronger supported conflict-state signal before integration.

## Exact next action
Probe LAB-086 first. Execute its complete gate only if authoritative pin `1fa85a0e34c9ae67da57f1e64dadccf211feacc0` can be placed byte-for-byte into an executable filesystem.

If LAB-086 remains transport-blocked, re-check PR #187 head/mergeability and seek an explicit supported conflict/merge-state signal if `mergeable=false` persists; do not rebase/merge from the boolean alone. Do not broaden LAB-094/095/096 speculatively. If exact materialization becomes available, verify retained blob/hash identity first, execute the focused/composed/LAB-080/LAB-081 inventory in `research/2026-09-16-lab094-096-closure-inventory.md`, then full pytest and compileall. Otherwise react only to newly reported concrete defects, source drift, or a confirmed conflict. Do not claim executable GREEN from source inspection.

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
