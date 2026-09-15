# Current Lab State

Last updated: 2026-09-16

## Active objective
LAB-086 remains priority #1: execute the exact asymmetric break-glass history migration gate from authoritative executable pin `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`. When byte-exact materialization remains unavailable, continue LAB-095/#180 + LAB-096/#181 composition/audit on draft PR #187. LAB-099 PREPARED authority waits on LAB-095 completion.

## Active issue / branch / PR
- #163 / LAB-086: draft PR #165; keep draft.
- #180 LAB-095 + #181 LAB-096: branch `lab-095-database-identity-red-intent`, draft PR #187; latest file-scoped adaptation commit `efaa96eeade6e3e6bebc8ad0fd66c3c8af098ecc`; keep draft.
- #169 LAB-090: draft PR #175 retained as donor; composed on PR #187.
- #176 LAB-092: draft PR #177 retained as donor; composed/adapted on PR #187.
- #188 LAB-101: explicit bootstrap + authenticated confirmation bridge, legacy integration adaptation, failure/concurrency regressions, UNKNOWN retry, and LAB-095 test composition are on PR #187; exact execution remains.
- #184 LAB-099: draft PR #186; blocked on LAB-095 completion.

## Last completed step
LAB-086 was probed first. Direct clone failed before repository execution with `Could not resolve host: github.com`, exit 128; no LAB-086 PASS is claimed.

Continued the actual supported-runtime call-site scan on PR #187. Found and adapted two stale fresh-DB constructors: `test_provider_history_capability_surface.py` and `test_audit_regressions.py` now bootstrap through LAB-101 `migrate_activation_schema_v1()` with `FencedActivationProvider` and assert the authenticated migration consumes provider position 1. The original capability-surface and corrupt-receipt restart fail-closed assertions remain intact. `test_store_receipt_guard_hook.py` was audited and intentionally left unchanged because its `object.__new__`/fake objects isolate `_store_receipt()` transaction/guard ordering below supported startup and perform no rotation. Branch commits: `41f559c3daf0b9c670943fd2ff1855d418f6ba9c`, `efaa96eeade6e3e6bebc8ad0fd66c3c8af098ecc`. Evidence: `research/2026-09-16-lab095-supported-runtime-scan.md`, main commit `eaaafd8b2fb169d0058c14ea258b9e1316a2f22e`.

## Known failures / blockers
- LAB-086 complete real-ledger gate remains unexecuted because shell DNS cannot resolve GitHub and no supported connector-to-filesystem byte-preserving bridge is exposed.
- Exact PR #187 repository pytest/compileall remains unavailable for the same materialization reason; committed/source-reviewed regressions are not a GREEN claim.
- PRs #165/#172/#173/#175/#177/#186/#187 remain draft until retained exact gates execute.
- LAB-095 exact no-stub reconstruction/hash verification and execution remain pending.
- LAB-095 DB-binding, identity-rotation, capability-surface, and corrupt-receipt restart regressions are source-composed with LAB-101/LAB-092 bootstrap and LAB-090 fencing; exact execution remains required.
- LAB-096 migration-only strategy audit found no defect; exact repository behavioral gates remain pending.
- LAB-090 restart recovery source and focused regressions are composed; execution remains pending.
- LAB-101 explicit bootstrap, legacy integration adaptation, failure/concurrency, UNKNOWN retry, and LAB-095 composition are source-composed but not exact-executed.

## Exact next action
Probe LAB-086 first. Execute its complete gate only if authoritative pin `1fa85a0e34c9ae67da57f1e64dadccf211feacc0` can be placed byte-for-byte into an executable filesystem.

If LAB-086 remains transport-blocked, continue scanning remaining PR #187 actual supported integration call sites for direct fresh/pre-LAB-092 `SupportedHistoricalSharedAnchorLedger` construction or non-fenced `rotate_provider()` usage. Preserve lower-level `object.__new__`, fake, migration, and classifier fixtures when they intentionally test below supported startup. Prioritize remaining integration/wiring tests after the now-adapted capability-surface and audit regressions. If none remain, continue LAB-095/LAB-096 authority audit. If exact materialization becomes available, verify retained blob/hash identity first and execute focused/downstream gates. Do not claim executable GREEN from source inspection.

## Backlog
- #163 LAB-086 — IN_PROGRESS; exact executable gate pending.
- #180 LAB-095 — IN_PROGRESS; DB-binding + identity-rotation + capability-surface + corrupt-receipt restart regressions source-composed; migration/recovery/classifier and store-receipt unit slices audited; exact/downstream gates pending.
- #181 LAB-096 — IN_PROGRESS/COMPOSED ON PR #187; migration-only strategy audit PASS by source inspection; exact/downstream validation pending.
- #169 LAB-090 — composed; execution pending.
- #176 LAB-092 — composed; exact execution pending.
- #188 LAB-101 — IN_PROGRESS: explicit bootstrap/confirmation bridge + legacy integration + failure/concurrency + UNKNOWN retry + LAB-095 composition implemented; exact execution pending.
- #167 LAB-088, #170 LAB-091 — retained draft gates pending.
- #178..185 LAB-093..100 — architecture/security follow-ups.
- #184 LAB-099 — PREPARED authority waits on LAB-095 completion.
