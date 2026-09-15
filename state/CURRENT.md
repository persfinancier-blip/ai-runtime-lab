# Current Lab State

Last updated: 2026-09-15

## Active objective
LAB-086 remains priority #1: execute the exact asymmetric break-glass history migration gate from authoritative executable pin `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`. When byte-exact materialization remains unavailable, continue LAB-095/#180 + LAB-096/#181 composition/audit on draft PR #187. LAB-099 PREPARED authority waits on LAB-095 completion.

## Active issue / branch / PR
- #163 / LAB-086: draft PR #165; keep draft.
- #180 LAB-095 + #181 LAB-096: branch `lab-095-database-identity-red-intent`, draft PR #187 at `c69eb116e78ac85b4983ddb0499131210ddcacc9`; keep draft.
- #169 LAB-090: draft PR #175 retained as donor; composed on PR #187.
- #176 LAB-092: draft PR #177 retained as donor; composed/adapted on PR #187.
- #188 LAB-101: explicit bootstrap + authenticated confirmation bridge, legacy integration adaptation, failure/concurrency regressions, and unknown-outcome retry regression are on PR #187; exact execution remains.
- #184 LAB-099: draft PR #186; blocked on LAB-095 completion.

## Last completed step
LAB-086 was probed first. Direct clone failed before repository execution with `Could not resolve host: github.com`, exit 128; no LAB-086 PASS is claimed.

Resumed LAB-095 production reconstruction/authority audit at exact PR #187 head. Connector-visible branch blobs are now pinned for five production files: `experiments/database_binding.py` `c6bf05b3a5579e076142300aefbc9d785cc6354a`; `database_identity.py` `bac58a48c576001370144cc10cfab8e0cfd129e3`; `database_identity_migration.py` `c4d1db46b8b64fec116dcfef8bb05e1e7a7b875e`; `integration.py` `83399d3d184ae61bcfb50a749c11a348e835f428`; `supported.py` `a1615cb7b793d6602db4406f0bdccb31ef5fba45`. Audited supported path/strategy authority: construction-bound canonical path remains enforced at supported ledger/history boundaries; `_provider_history` and public `provider_history` rebinding are rejected; inspection view exposes no rotation/path mutation; coordinator-only history rejects direct rotate. Legacy `HistoricalSharedAnchorLedger` remains intentionally broader but its constructor is bypassed by the supported concrete class. No new production path/strategy authority defect was found in this slice. Evidence: `research/2026-09-15-lab095-production-authority-blob-audit.md`, main commit `57d365f13902f268faa5da47432606f629f27b10`.

## Known failures / blockers
- LAB-086 complete real-ledger gate remains unexecuted because shell DNS cannot resolve GitHub and no supported connector-to-filesystem byte-preserving bridge is exposed.
- Exact PR #187 repository pytest/compileall remains unavailable for the same materialization reason; committed/source-reviewed regressions are not a GREEN claim.
- PRs #165/#172/#173/#175/#177/#186/#187 remain draft until retained exact gates execute.
- LAB-095 complete eight-file no-stub tree still needs remaining reference/regression blob pins, same-run reconstruction/hash verification, and execution.
- LAB-096 source fixes still need exact repository behavioral gates.
- LAB-090 restart recovery source and focused regressions are composed; execution remains pending.
- LAB-101 explicit bootstrap, legacy integration adaptation, failure/concurrency and UNKNOWN retry regressions are source-composed but not exact-executed.

## Exact next action
Probe LAB-086 first. Execute its complete gate only if authoritative pin `1fa85a0e34c9ae67da57f1e64dadccf211feacc0` can be placed byte-for-byte into an executable filesystem.

If LAB-086 remains transport-blocked, continue LAB-095 eight-file closure at PR #187 head: identify and pin the remaining reference/regression file blob identities, audit their imports and assumptions against the five pinned production blobs, and check specifically for any test/reference path that silently instantiates legacy `HistoricalSharedAnchorLedger` where supported LAB-095/LAB-096 guarantees are expected. If exact materialization becomes available, reconstruct all retained files, verify byte/hash identity first, then execute focused/downstream gates. Do not claim executable GREEN from source inspection.

## Backlog
- #163 LAB-086 — IN_PROGRESS; exact executable gate pending.
- #180 LAB-095 — IN_PROGRESS; five production blobs pinned and supported path/strategy authority source-audited; remaining reference/regression pins + exact/downstream gates pending.
- #181 LAB-096 — IN_PROGRESS/COMPOSED ON PR #187; exact/downstream validation pending.
- #169 LAB-090 — composed; execution pending.
- #176 LAB-092 — composed; exact execution pending.
- #188 LAB-101 — IN_PROGRESS: explicit bootstrap/confirmation bridge + legacy integration + failure/concurrency + UNKNOWN retry source regressions implemented; exact execution pending.
- #167 LAB-088, #170 LAB-091 — retained draft gates pending.
- #178..185 LAB-093..100 — architecture/security follow-ups.
- #184 LAB-099 — PREPARED authority waits on LAB-095 completion.
