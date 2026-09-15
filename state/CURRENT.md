# Current Lab State

Last updated: 2026-09-15

## Active objective
LAB-086 remains priority #1: execute the exact asymmetric break-glass history migration gate from authoritative executable pin `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`. When byte-exact materialization remains unavailable, continue LAB-095/#180 + LAB-096/#181 composition on draft PR #187. LAB-099 PREPARED authority waits on LAB-095 completion.

## Active issue / branch / PR
- #163 / LAB-086: draft PR #165; keep draft.
- #180 LAB-095 + #181 LAB-096: branch `lab-095-database-identity-red-intent`, draft PR #187; keep draft.
- #169 LAB-090: draft PR #175 retained as donor; provider fence, pre-ack SQL transition, durable acknowledgement, supported-ledger rotation wiring, restart/historical recovery, and focused restart regressions are ported to PR #187.
- #176 LAB-092: draft PR #177 retained as donor; shared schema, locked provenance/receipt guard, read-only startup gate, explicit PREPARED migration writer, focused writer regressions, and supported-constructor startup ordering are adapted onto PR #187.
- #188 LAB-101: explicit end-to-end LAB-092 fresh/legacy bootstrap + authenticated confirmation bridge is now implemented on PR #187; legacy integration adaptation and exact execution remain.
- #184 LAB-099: draft PR #186; blocked on LAB-095 completion.

## Last completed step
LAB-086 was probed first. Direct clone failed before repository execution with `Could not resolve host: github.com`, exit 128; no LAB-086 PASS is claimed.

Implemented the smallest LAB-101 explicit bootstrap/migration bridge on PR #187. `migrate_activation_schema_v1()` now constructs one construction-bound `CoordinatorOnlyProviderHistory`, initializes legitimate fresh/pre-LAB-090 shared-ledger state without invoking ordinary COMPLETE-only startup, verifies historical durable state/runtime authority, atomically installs exact LAB-090 DDL + deterministic PREPARED marker, re-verifies authority, authenticates/confirms the exact migration intent through ordinary execution, and only then invokes normal `SupportedHistoricalSharedAnchorLedger` startup. Audit caught an initial use of LAB-080 `SupportedSharedAnchorLedger.verify_durable()` that would reject legitimate historical-generation rows; corrected before handoff to initialize only `SharedAnchorLedger` and verify through the historical ledger abstraction. Branch head `6aec2aec3e7877c8d6c1594cb88a5b4225e139a5`. Added focused fresh + COMPLETE-idempotence regressions. Evidence: `research/2026-09-15-lab101-explicit-activation-bootstrap-bridge.md`, main commit `657b006f6f85293cdbafc7298d342ec9d3a35223`.

## Known failures / blockers
- LAB-086 complete real-ledger gate remains unexecuted because shell DNS cannot resolve GitHub and no supported connector-to-filesystem byte-preserving bridge is exposed.
- Exact PR #187 repository pytest/compileall remains unavailable for the same materialization reason; committed/source-reviewed regressions are not a GREEN claim.
- PRs #165/#172/#173/#175/#177/#186/#187 remain draft until retained exact gates execute.
- LAB-095 complete eight-file no-stub tree still needs same-run reconstruction/hash verification plus execution.
- LAB-096 source fixes still need exact repository behavioral gates.
- LAB-090 restart recovery source and focused regressions are composed; execution remains pending.
- LAB-101 explicit bootstrap bridge is source-composed but not exact-executed. Existing LAB-081 integration tests still instantiate the COMPLETE-only constructor directly, and their provider-rotation fixtures use `SignedAnchorProvider`; composed LAB-090 rotation now requires `FencedActivationProvider`, so compatibility adaptation must address both migration and fencing semantics.

## Exact next action
Probe LAB-086 first. Execute its complete gate only if authoritative pin `1fa85a0e34c9ae67da57f1e64dadccf211feacc0` can be placed byte-for-byte into an executable filesystem.

If LAB-086 remains transport-blocked, adapt `experiments/provider_generation_history/tests/test_integration.py` on PR #187 through the new explicit `migrate_activation_schema_v1()` entrypoint. Do not mechanically replace only the constructor helper: rotation tests must use the composed LAB-090 fenced-provider semantics while preserving their historical receipt/restart assertions. Then add end-to-end LAB-101 failure regressions for stale runtime, unrelated PREPARED, partial DDL, and failed confirmation/retry. Preserve ordinary read-only COMPLETE startup, private construction-bound `_history()`, canonical DB binding, and no post-construction history replacement. Do not claim GREEN without execution.

## Backlog
- #163 LAB-086 — IN_PROGRESS; exact executable gate pending.
- #180 LAB-095 — IN_PROGRESS; DB binding implemented; exact/downstream gates pending.
- #181 LAB-096 — IN_PROGRESS/COMPOSED ON PR #187; exact/downstream validation pending.
- #169 LAB-090 — restart/historical recovery source + focused regressions composed; execution pending.
- #176 LAB-092 — startup-order gate + explicit writer composed; exact execution pending.
- #188 LAB-101 — IN_PROGRESS: explicit bootstrap/confirmation bridge implemented; integration adaptation + failure regressions + exact execution pending.
- #167 LAB-088, #170 LAB-091 — retained draft gates pending.
- #178..185 LAB-093..100 — architecture/security follow-ups.
- #184 LAB-099 — PREPARED authority waits on LAB-095 completion.
