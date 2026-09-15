# Current Lab State

Last updated: 2026-09-15

## Active objective
LAB-086 remains priority #1: execute the exact asymmetric break-glass history migration gate from authoritative executable pin `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`. When byte-exact materialization remains unavailable, continue LAB-095/#180 + LAB-096/#181 composition on draft PR #187. LAB-099 PREPARED authority waits on LAB-095 completion.

## Active issue / branch / PR
- #163 / LAB-086: draft PR #165; keep draft.
- #180 LAB-095 + #181 LAB-096: branch `lab-095-database-identity-red-intent`, draft PR #187; keep draft.
- #169 LAB-090: draft PR #175 retained as donor; composed on PR #187.
- #176 LAB-092: draft PR #177 retained as donor; composed/adapted on PR #187.
- #188 LAB-101: explicit bootstrap + authenticated confirmation bridge, legacy integration adaptation, failure/concurrency regressions, and unknown-outcome retry regression are on PR #187; exact execution remains.
- #184 LAB-099: draft PR #186; blocked on LAB-095 completion.

## Last completed step
LAB-086 was probed first. Direct clone failed before repository execution with `Could not resolve host: github.com`, exit 128; no LAB-086 PASS is claimed.

Source-audited LAB-101 failure regressions against the exact LAB-092 classifier. Confirmed that exact table+trigger+PREPARED maps to `DDL_INSTALLED_PREPARED`, exact CONFIRMED maps to `COMPLETE`, corrupt marker content fails closed, and partial/mismatched DDL is not normalized. Found that the existing confirmation-failure regression covered only failure before the external effect, not the timeout/UNKNOWN window after provider commit. Added a regression that drives the real `execute(..., timeout_after_commit=True)` path, requires provider position 1 + PREPARED after the first failure, then retries the deterministic migration request and requires COMPLETE with provider still exactly at 1. PR #187 branch commit `c69eb116e78ac85b4983ddb0499131210ddcacc9`. Evidence: `research/2026-09-15-lab101-unknown-outcome-retry-audit.md`, main commit `8a2e64b15f048fb5333b576a2ce23597fd9d0164`.

## Known failures / blockers
- LAB-086 complete real-ledger gate remains unexecuted because shell DNS cannot resolve GitHub and no supported connector-to-filesystem byte-preserving bridge is exposed.
- Exact PR #187 repository pytest/compileall remains unavailable for the same materialization reason; committed/source-reviewed regressions are not a GREEN claim.
- PRs #165/#172/#173/#175/#177/#186/#187 remain draft until retained exact gates execute.
- LAB-095 complete eight-file no-stub tree still needs same-run reconstruction/hash verification plus execution.
- LAB-096 source fixes still need exact repository behavioral gates.
- LAB-090 restart recovery source and focused regressions are composed; execution remains pending.
- LAB-101 explicit bootstrap, legacy integration adaptation, failure/concurrency and UNKNOWN retry regressions are source-composed but not exact-executed.

## Exact next action
Probe LAB-086 first. Execute its complete gate only if authoritative pin `1fa85a0e34c9ae67da57f1e64dadccf211feacc0` can be placed byte-for-byte into an executable filesystem.

If LAB-086 remains transport-blocked, resume LAB-095 eight-file reconstruction/hash verification from connector-visible authoritative PR #187 content. Prioritize production database-binding/identity files before reference tests, verify exact branch blob identities where the connector exposes them, and audit for remaining public/rebindable path or strategy authority. Do not claim executable GREEN without exact materialization.

## Backlog
- #163 LAB-086 — IN_PROGRESS; exact executable gate pending.
- #180 LAB-095 — IN_PROGRESS; DB binding implemented; exact/downstream gates pending.
- #181 LAB-096 — IN_PROGRESS/COMPOSED ON PR #187; exact/downstream validation pending.
- #169 LAB-090 — composed; execution pending.
- #176 LAB-092 — composed; exact execution pending.
- #188 LAB-101 — IN_PROGRESS: explicit bootstrap/confirmation bridge + legacy integration + failure/concurrency + UNKNOWN retry source regressions implemented; exact execution pending.
- #167 LAB-088, #170 LAB-091 — retained draft gates pending.
- #178..185 LAB-093..100 — architecture/security follow-ups.
- #184 LAB-099 — PREPARED authority waits on LAB-095 completion.
