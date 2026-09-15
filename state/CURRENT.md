# Current Lab State

Last updated: 2026-09-15

## Active objective
LAB-086 remains priority #1: execute the exact asymmetric break-glass history migration gate from authoritative executable pin `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`. When byte-exact materialization remains unavailable, continue LAB-095/#180 + LAB-096/#181 composition/audit on draft PR #187. LAB-099 PREPARED authority waits on LAB-095 completion.

## Active issue / branch / PR
- #163 / LAB-086: draft PR #165; keep draft.
- #180 LAB-095 + #181 LAB-096: branch `lab-095-database-identity-red-intent`, draft PR #187; latest file-scoped adaptation commit `925a1e2587f1a0685b8fb15e040ebe67100cb703`; keep draft.
- #169 LAB-090: draft PR #175 retained as donor; composed on PR #187.
- #176 LAB-092: draft PR #177 retained as donor; composed/adapted on PR #187.
- #188 LAB-101: explicit bootstrap + authenticated confirmation bridge, legacy integration adaptation, failure/concurrency regressions, UNKNOWN retry, and LAB-095 DB-binding test composition are on PR #187; exact execution remains.
- #184 LAB-099: draft PR #186; blocked on LAB-095 completion.

## Last completed step
LAB-086 was probed first. Direct clone failed before repository execution with `Could not resolve host: github.com`, exit 128; no LAB-086 PASS is claimed.

Audited PR #187 `activation_schema_migration.py` migration-only `object.__new__` paths against LAB-095 canonical DB binding and LAB-096 construction-bound provider-history strategy. No concrete defect was found. `_migration_reservation_surface()` first-binds both `CoordinatorOnlyProviderHistory.path` and supported-ledger `path` through `CanonicalDatabaseBinding`, then first-binds exact `CoordinatorOnlyProviderHistory` through the supported `provider_history` setter into immutable `_provider_history`. `_explicit_bootstrap_surface()` constructs the same canonical history first, binds it through the same setter, and the subsequent `SharedAnchorLedger.__init__` first ledger-path assignment is intercepted by the supported MRO's canonical binding. `_history()` then prefers `_provider_history`. No DB-A -> DB-B or strategy replacement authority path is introduced by these migration-only surfaces. Evidence: `research/2026-09-15-lab095-lab096-migration-only-construction-audit.md`, main commit `e7c3efc7d40048c8e811dd615a5da5d8e53cb82f`.

## Known failures / blockers
- LAB-086 complete real-ledger gate remains unexecuted because shell DNS cannot resolve GitHub and no supported connector-to-filesystem byte-preserving bridge is exposed.
- Exact PR #187 repository pytest/compileall remains unavailable for the same materialization reason; committed/source-reviewed regressions are not a GREEN claim.
- PRs #165/#172/#173/#175/#177/#186/#187 remain draft until retained exact gates execute.
- LAB-095 exact no-stub reconstruction/hash verification and execution remain pending.
- LAB-095 DB-binding regression is source-composed with LAB-101/LAB-092 bootstrap and LAB-090 fencing; migration-only canonical-binding audit found no defect, but exact execution remains required.
- LAB-096 migration-only strategy audit found no defect; exact repository behavioral gates remain pending.
- LAB-090 restart recovery source and focused regressions are composed; execution remains pending.
- LAB-101 explicit bootstrap, legacy integration adaptation, failure/concurrency, UNKNOWN retry, and DB-binding composition are source-composed but not exact-executed.

## Exact next action
Probe LAB-086 first. Execute its complete gate only if authoritative pin `1fa85a0e34c9ae67da57f1e64dadccf211feacc0` can be placed byte-for-byte into an executable filesystem.

If LAB-086 remains transport-blocked, re-fetch PR #187 `experiments/provider_generation_history/tests/test_database_path_binding.py` and source-audit every expected provider position against the composed semantics: authenticated LAB-092 migration completion consumes position 1; first ordinary DB-A intent is position 2; generation-2 candidate must start at durable tail 2; post-rotation DB-A-only mutation is position 3; independently migrated DB B remains at tail 1 before corruption/rebinding attempts. Fix only a concrete mismatch. If exact materialization becomes available, verify retained blob/hash identity first and execute focused/downstream gates. Do not claim executable GREEN from source inspection.

## Backlog
- #163 LAB-086 — IN_PROGRESS; exact executable gate pending.
- #180 LAB-095 — IN_PROGRESS; DB-binding regression source-composed; migration-only canonical-binding audit PASS by source inspection; position audit + exact/downstream gates pending.
- #181 LAB-096 — IN_PROGRESS/COMPOSED ON PR #187; migration-only strategy audit PASS by source inspection; exact/downstream validation pending.
- #169 LAB-090 — composed; execution pending.
- #176 LAB-092 — composed; exact execution pending.
- #188 LAB-101 — IN_PROGRESS: explicit bootstrap/confirmation bridge + legacy integration + failure/concurrency + UNKNOWN retry + DB-binding composition implemented; exact execution pending.
- #167 LAB-088, #170 LAB-091 — retained draft gates pending.
- #178..185 LAB-093..100 — architecture/security follow-ups.
- #184 LAB-099 — PREPARED authority waits on LAB-095 completion.
