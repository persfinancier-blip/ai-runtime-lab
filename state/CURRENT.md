# Current Lab State

Last updated: 2026-09-15

## Active objective
LAB-086 remains priority #1: execute the exact asymmetric break-glass history migration gate from authoritative executable pin `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`. When byte-exact materialization remains unavailable, continue LAB-095/#180 + LAB-096/#181 composition on draft PR #187. LAB-099 PREPARED authority waits on LAB-095 completion.

## Active issue / branch / PR
- #163 / LAB-086: draft PR #165; keep draft.
- #180 LAB-095 + #181 LAB-096: branch `lab-095-database-identity-red-intent`, draft PR #187; keep draft.
- #169 LAB-090: draft PR #175 retained as donor; provider fence, pre-ack SQL transition, durable acknowledgement, supported-ledger rotation wiring, and restart/historical recovery are ported to PR #187.
- #176 LAB-092: draft PR #177 retained as donor; shared schema, locked provenance/receipt guard, read-only startup gate, explicit migration writer, focused writer regressions, and supported-constructor startup ordering are adapted onto PR #187.
- #184 LAB-099: draft PR #186; blocked on LAB-095 completion.

## Last completed step
LAB-086 was probed first. Direct clone failed before repository execution with `Could not resolve host: github.com`, exit 128; no LAB-086 PASS is claimed.

Fallback work audited PR #187 startup ordering after LAB-090 restart recovery composition. The audit found that the concrete supported constructor could reach `_recover_pending_activation()` without first proving LAB-092 activation-schema provenance COMPLETE. PR #187 now explicitly calls `require_complete_activation_schema_provenance_for_startup(path)` before `CoordinatorOnlyProviderHistory` construction, supported-ledger initialization, or recovery. An initial MRO-only mixin attempt was caught as ineffective because the concrete class owns `__init__` and was superseded in the same run. Current production commit: `f67eec5e274767e38c58d70bcc0c172980e3e81b`. Evidence: `research/2026-09-15-lab092-supported-startup-ordering-audit.md`, main commit `1c9e402e69c55a22dddbeec23087b77158098935`.

## Known failures / blockers
- LAB-086 complete real-ledger gate remains unexecuted because shell DNS cannot resolve GitHub and no supported connector-to-filesystem byte-preserving bridge is exposed.
- Exact PR #187 repository pytest/compileall remains unavailable for the same materialization reason; committed/source-reviewed regressions are not a GREEN claim.
- PRs #165/#172/#173/#175/#177/#186/#187 remain draft until retained exact gates execute.
- LAB-095 complete eight-file no-stub tree still needs same-run reconstruction/hash verification plus execution.
- LAB-096 source fixes still need exact repository behavioral gates.
- LAB-090 restart recovery is source-composed but focused regressions for restart windows/premature release/ABSENT/historical unresolved remain to be added and executed when possible.
- LAB-092 supported startup now requires exact COMPLETE provenance before history construction/recovery; callers/tests that previously constructed a fresh supported ledger directly must explicitly run the migration writer first. Compatibility regressions remain to be audited.

## Exact next action
Probe LAB-086 first. Execute its complete gate only if authoritative pin `1fa85a0e34c9ae67da57f1e64dadccf211feacc0` can be placed byte-for-byte into an executable filesystem.

If LAB-086 remains transport-blocked, add focused PR #187 restart regressions seeded with exact COMPLETE LAB-092 provenance for: SQL_COMMITTED+PREPARED, SQL_COMMITTED+COMMITTED_FENCED, premature RELEASED, ABSENT reservation, and historical non-current SQL_COMMITTED. Audit existing supported-ledger tests/constructors for the new explicit migration prerequisite and adapt setup rather than weakening the startup gate. Do not claim GREEN without execution.

## Backlog
- #163 LAB-086 — IN_PROGRESS; exact executable gate pending.
- #180 LAB-095 — IN_PROGRESS; DB binding implemented; exact/downstream gates pending.
- #181 LAB-096 — IN_PROGRESS/COMPOSED ON PR #187; exact/downstream validation pending.
- #169 LAB-090 — restart/historical recovery source-composed; focused recovery regressions next.
- #176 LAB-092 — supported startup-order gate composed; compatibility/exact execution pending.
- #167 LAB-088, #170 LAB-091 — retained draft gates pending.
- #178..185 LAB-093..100 — architecture/security follow-ups.
- #184 LAB-099 — PREPARED authority waits on LAB-095 completion.
