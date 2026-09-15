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

Adapted PR #187 `experiments/provider_generation_history/tests/test_database_path_binding.py` to the current LAB-090/LAB-092/LAB-101 composition. Fresh DB A now enters through official `migrate_activation_schema_v1()` with `FencedActivationProvider`; authenticated migration completion consumes position 1, first ordinary intent is position 2, generation-2 candidate starts at the durable tail 2, and post-rotation DB-A-only mutation is expected at position 3. The split-authority DB-B case now independently migrates DB B through the official entrypoint, leaving tail 1, so it remains a legitimate-history strategy replacement regression rather than a malformed/fresh DB test. Public/private path rebinding rejection, private strategy rebinding rejection, corrupted matching-head DB B, and DB-B no-mutation assertions are preserved. Initial branch commit `c8cc55cee579204f91e0dadef504f93be6ac0e74`; source-audit correction `925a1e2587f1a0685b8fb15e040ebe67100cb703`. Evidence: `research/2026-09-15-lab095-db-binding-composed-bootstrap-adaptation.md`, main commit `55e517624d1636175c97ec1dc6547ffda2af0245`; #180 updated.

## Known failures / blockers
- LAB-086 complete real-ledger gate remains unexecuted because shell DNS cannot resolve GitHub and no supported connector-to-filesystem byte-preserving bridge is exposed.
- Exact PR #187 repository pytest/compileall remains unavailable for the same materialization reason; committed/source-reviewed regressions are not a GREEN claim.
- PRs #165/#172/#173/#175/#177/#186/#187 remain draft until retained exact gates execute.
- LAB-095 exact no-stub reconstruction/hash verification and execution remain pending.
- LAB-095 DB-binding regression is now source-composed with LAB-101/LAB-092 bootstrap and LAB-090 fencing, but still requires exact execution and a fresh audit of migration-only object construction against canonical DB binding.
- LAB-096 source fixes still need exact repository behavioral gates.
- LAB-090 restart recovery source and focused regressions are composed; execution remains pending.
- LAB-101 explicit bootstrap, legacy integration adaptation, failure/concurrency, UNKNOWN retry, and DB-binding composition are source-composed but not exact-executed.

## Exact next action
Probe LAB-086 first. Execute its complete gate only if authoritative pin `1fa85a0e34c9ae67da57f1e64dadccf211feacc0` can be placed byte-for-byte into an executable filesystem.

If LAB-086 remains transport-blocked, re-fetch the adapted PR #187 DB-binding regression and audit `activation_schema_migration.py` migration-only construction paths (`_migration_reservation_surface` and `_explicit_bootstrap_surface`) against LAB-095 canonical database binding and LAB-096 construction-bound provider-history strategy. Determine whether their deliberate `object.__new__` + first assignment preserves the same canonical DB source of truth without creating a rebindable migration authority path. Fix only if a concrete supported/migration authority defect is proven. Then source-audit every expected position in the DB-binding regression. If exact materialization becomes available, verify retained blob/hash identity first and execute focused/downstream gates. Do not claim executable GREEN from source inspection.

## Backlog
- #163 LAB-086 — IN_PROGRESS; exact executable gate pending.
- #180 LAB-095 — IN_PROGRESS; DB-binding regression source-composed with LAB-090/092/101; migration-only canonical-binding audit + exact/downstream gates pending.
- #181 LAB-096 — IN_PROGRESS/COMPOSED ON PR #187; migration-only strategy audit + exact/downstream validation pending.
- #169 LAB-090 — composed; execution pending.
- #176 LAB-092 — composed; exact execution pending.
- #188 LAB-101 — IN_PROGRESS: explicit bootstrap/confirmation bridge + legacy integration + failure/concurrency + UNKNOWN retry + DB-binding composition implemented; exact execution pending.
- #167 LAB-088, #170 LAB-091 — retained draft gates pending.
- #178..185 LAB-093..100 — architecture/security follow-ups.
- #184 LAB-099 — PREPARED authority waits on LAB-095 completion.
