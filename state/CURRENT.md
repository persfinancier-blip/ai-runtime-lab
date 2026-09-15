# Current Lab State

Last updated: 2026-09-15

## Active objective
LAB-086 remains priority #1: execute the exact asymmetric break-glass history migration gate from authoritative executable pin `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`. When byte-exact materialization remains unavailable, continue LAB-095/#180 + LAB-096/#181 composition on draft PR #187. LAB-099 PREPARED authority waits on LAB-095 completion.

## Active issue / branch / PR
- #163 / LAB-086: draft PR #165; keep draft.
- #180 LAB-095 + #181 LAB-096: branch `lab-095-database-identity-red-intent`, draft PR #187; keep draft.
- #169 LAB-090: draft PR #175 retained as donor; composed on PR #187.
- #176 LAB-092: draft PR #177 retained as donor; composed/adapted on PR #187.
- #188 LAB-101: explicit bootstrap + authenticated confirmation bridge, legacy integration adaptation, and source-level failure/concurrency regressions are on PR #187; exact execution remains.
- #184 LAB-099: draft PR #186; blocked on LAB-095 completion.

## Last completed step
LAB-086 was probed first. Direct clone failed before repository execution with `Could not resolve host: github.com`, exit 128; no LAB-086 PASS is claimed.

On PR #187 added LAB-101 failure/retry regressions for partial activation DDL, unrelated PREPARED intent, stale runtime, and failed authenticated confirmation followed by deterministic retry. Audited the tests and corrected setup to use the real `Intent` API and transaction-internal historical rotation for stale-runtime construction. Then audited the adapted LAB-081 reserve-vs-rotation fixture against LAB-090 prepare/abort ordering: fixed the candidate position so PREPARED-vs-rotation actually reaches provider prepare before SQL rejection, requires exact ticket cleanup, and broadened the concurrent safe outcomes to include pre-ticket `AnchorMismatch` and legitimate generation-2 reservation after successful rotation. Branch head `ab2a5cba273ad8b04b5ee866665acea20291c66c`. Evidence: `research/2026-09-15-lab101-bootstrap-failure-and-concurrency-audit.md`, main commit `f2b933dd181eb15198806d51be5eb2d489d0326d`.

## Known failures / blockers
- LAB-086 complete real-ledger gate remains unexecuted because shell DNS cannot resolve GitHub and no supported connector-to-filesystem byte-preserving bridge is exposed.
- Exact PR #187 repository pytest/compileall remains unavailable for the same materialization reason; committed/source-reviewed regressions are not a GREEN claim.
- PRs #165/#172/#173/#175/#177/#186/#187 remain draft until retained exact gates execute.
- LAB-095 complete eight-file no-stub tree still needs same-run reconstruction/hash verification plus execution.
- LAB-096 source fixes still need exact repository behavioral gates.
- LAB-090 restart recovery source and focused regressions are composed; execution remains pending.
- LAB-101 explicit bootstrap, legacy integration adaptation, and failure/concurrency regressions are source-composed but not exact-executed.

## Exact next action
Probe LAB-086 first. Execute its complete gate only if authoritative pin `1fa85a0e34c9ae67da57f1e64dadccf211feacc0` can be placed byte-for-byte into an executable filesystem.

If LAB-086 remains transport-blocked, source-audit the new LAB-101 failure regressions against exact LAB-092 provenance classifier states, especially partial DDL and PREPARED. Inspect confirmation failure/unknown-outcome retry semantics for any normalization gap without weakening ordinary read-only COMPLETE startup. Then resume LAB-095 eight-file reconstruction/hash verification using connector-visible authoritative content where possible; do not claim executable GREEN without exact materialization.

## Backlog
- #163 LAB-086 — IN_PROGRESS; exact executable gate pending.
- #180 LAB-095 — IN_PROGRESS; DB binding implemented; exact/downstream gates pending.
- #181 LAB-096 — IN_PROGRESS/COMPOSED ON PR #187; exact/downstream validation pending.
- #169 LAB-090 — composed; execution pending.
- #176 LAB-092 — composed; exact execution pending.
- #188 LAB-101 — IN_PROGRESS: explicit bootstrap/confirmation bridge + legacy integration + failure/concurrency source regressions implemented; exact execution pending.
- #167 LAB-088, #170 LAB-091 — retained draft gates pending.
- #178..185 LAB-093..100 — architecture/security follow-ups.
- #184 LAB-099 — PREPARED authority waits on LAB-095 completion.
