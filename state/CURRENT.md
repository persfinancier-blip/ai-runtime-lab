# Current Lab State

Last updated: 2026-09-15

## Active objective
LAB-086 remains priority #1: execute the exact asymmetric break-glass history migration gate from authoritative executable pin `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`. When byte-exact materialization remains unavailable, continue LAB-095/#180 + LAB-096/#181 composition on draft PR #187. LAB-099 PREPARED authority waits on LAB-095 completion.

## Active issue / branch / PR
- #163 / LAB-086: draft PR #165; keep draft.
- #180 LAB-095 + #181 LAB-096: branch `lab-095-database-identity-red-intent`, draft PR #187; keep draft.
- #169 LAB-090: draft PR #175 retained as donor; provider fence, pre-ack SQL transition, durable acknowledgement, supported-ledger rotation wiring, restart/historical recovery, and focused restart regressions are ported to PR #187.
- #176 LAB-092: draft PR #177 retained as donor; shared schema, locked provenance/receipt guard, read-only startup gate, explicit PREPARED migration writer, focused writer regressions, and supported-constructor startup ordering are adapted onto PR #187.
- #188 LAB-101: explicit end-to-end LAB-092 fresh/legacy bootstrap + authenticated confirmation bridge is implemented on PR #187; legacy LAB-081 integration tests are now adapted to that entrypoint and LAB-090 fencing; failure regressions and exact execution remain.
- #184 LAB-099: draft PR #186; blocked on LAB-095 completion.

## Last completed step
LAB-086 was probed first. Direct clone failed before repository execution with `Could not resolve host: github.com`, exit 128; no LAB-086 PASS is claimed.

Adapted `experiments/provider_generation_history/tests/test_integration.py` on PR #187 to the composed LAB-101/LAB-090 contract. Fresh test setup now enters through `migrate_activation_schema_v1()` while restart assertions continue through the ordinary COMPLETE-only `SupportedHistoricalSharedAnchorLedger` constructor. Rotation fixtures now use `FencedActivationProvider`, candidate providers start at the exact current position required by activation fencing, and position assertions account for the deterministic LAB-092 completion intent consuming position 1. Historical receipt/restart, direct-history-rotation blocking, PREPARED-vs-rotation, and reserve-vs-rotation coverage are retained. Branch commit `0e8e47631a5e4ee40fa1e99ffc10e258ca47c827`. Evidence: `research/2026-09-15-lab101-legacy-integration-adaptation.md`, main commit `f2ea18062887791f593fe3bc9ee9bd7d58d24fdc`.

## Known failures / blockers
- LAB-086 complete real-ledger gate remains unexecuted because shell DNS cannot resolve GitHub and no supported connector-to-filesystem byte-preserving bridge is exposed.
- Exact PR #187 repository pytest/compileall remains unavailable for the same materialization reason; committed/source-reviewed regressions are not a GREEN claim.
- PRs #165/#172/#173/#175/#177/#186/#187 remain draft until retained exact gates execute.
- LAB-095 complete eight-file no-stub tree still needs same-run reconstruction/hash verification plus execution.
- LAB-096 source fixes still need exact repository behavioral gates.
- LAB-090 restart recovery source and focused regressions are composed; execution remains pending.
- LAB-101 explicit bootstrap and legacy integration adaptation are source-composed but not exact-executed. End-to-end failure/retry coverage for stale runtime, unrelated PREPARED, partial DDL, and failed confirmation is still missing.

## Exact next action
Probe LAB-086 first. Execute its complete gate only if authoritative pin `1fa85a0e34c9ae67da57f1e64dadccf211feacc0` can be placed byte-for-byte into an executable filesystem.

If LAB-086 remains transport-blocked, add end-to-end LAB-101 failure regressions on PR #187 for stale runtime, unrelated PREPARED, partial LAB-090 DDL, and failed confirmation/retry. Each scenario must enter through the explicit migration surface, prove fail-closed durable state and deterministic resumability where intended, and preserve ordinary read-only COMPLETE startup, private construction-bound `_history()`, canonical DB binding, and no post-construction history replacement. Audit the newly adapted concurrency fixture against activation prepare/abort ordering. Do not claim GREEN without execution.

## Backlog
- #163 LAB-086 — IN_PROGRESS; exact executable gate pending.
- #180 LAB-095 — IN_PROGRESS; DB binding implemented; exact/downstream gates pending.
- #181 LAB-096 — IN_PROGRESS/COMPOSED ON PR #187; exact/downstream validation pending.
- #169 LAB-090 — restart/historical recovery source + focused regressions composed; execution pending.
- #176 LAB-092 — startup-order gate + explicit writer composed; exact execution pending.
- #188 LAB-101 — IN_PROGRESS: explicit bootstrap/confirmation bridge + legacy integration adaptation implemented; failure regressions + exact execution pending.
- #167 LAB-088, #170 LAB-091 — retained draft gates pending.
- #178..185 LAB-093..100 — architecture/security follow-ups.
- #184 LAB-099 — PREPARED authority waits on LAB-095 completion.
