# Current Lab State

Last updated: 2026-09-15

## Active objective
LAB-086 remains priority #1: execute the exact asymmetric break-glass history migration gate from authoritative executable pin `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`. When byte-exact materialization remains unavailable, continue LAB-095/#180 + LAB-096/#181 composition on draft PR #187. LAB-099 PREPARED authority waits on LAB-095 completion.

## Active issue / branch / PR
- #163 / LAB-086: draft PR #165; keep draft.
- #180 LAB-095 + #181 LAB-096: branch `lab-095-database-identity-red-intent`, draft PR #187; keep draft.
- #169 LAB-090: draft PR #175 retained as donor; provider fence, pre-ack SQL transition, durable acknowledgement, supported-ledger rotation wiring, restart/historical recovery, and focused restart regressions are ported to PR #187.
- #176 LAB-092: draft PR #177 retained as donor; shared schema, locked provenance/receipt guard, read-only startup gate, explicit migration writer, focused writer regressions, and supported-constructor startup ordering are adapted onto PR #187.
- #184 LAB-099: draft PR #186; blocked on LAB-095 completion.

## Last completed step
LAB-086 was probed first. Direct clone failed before repository execution with `Could not resolve host: github.com`, exit 128; no LAB-086 PASS is claimed.

Fallback work added `tests/test_activation_restart_recovery.py` to PR #187. Five restart windows are now committed: SQL_COMMITTED+PREPARED, SQL_COMMITTED+COMMITTED_FENCED, premature RELEASED, ABSENT reservation, and historical non-current SQL_COMMITTED. Every fixture installs the exact LAB-092 activation table/trigger plus canonical CONFIRMED marker and explicitly proves the production locked classifier returns `COMPLETE` before recovery. An audit tightened the first fixture version to make that proof explicit. Current PR #187 head: `2510028d442f775617696d02254d02305e902d8a`. Evidence: `research/2026-09-15-lab090-restart-recovery-regressions.md`, main commit `030506a9016497845edf5e981430edf0ee66b0d9`.

## Known failures / blockers
- LAB-086 complete real-ledger gate remains unexecuted because shell DNS cannot resolve GitHub and no supported connector-to-filesystem byte-preserving bridge is exposed.
- Exact PR #187 repository pytest/compileall remains unavailable for the same materialization reason; committed/source-reviewed regressions are not a GREEN claim.
- PRs #165/#172/#173/#175/#177/#186/#187 remain draft until retained exact gates execute.
- LAB-095 complete eight-file no-stub tree still needs same-run reconstruction/hash verification plus execution.
- LAB-096 source fixes still need exact repository behavioral gates.
- LAB-090 restart recovery source and focused regressions are composed; execution remains pending.
- LAB-092 supported startup requires exact COMPLETE provenance before history construction/recovery; callers/tests that previously constructed a fresh supported ledger directly must explicitly run the migration writer first. Compatibility regressions remain to be audited.

## Exact next action
Probe LAB-086 first. Execute its complete gate only if authoritative pin `1fa85a0e34c9ae67da57f1e64dadccf211feacc0` can be placed byte-for-byte into an executable filesystem.

If LAB-086 remains transport-blocked, audit existing supported-ledger constructor tests for the new explicit LAB-092 migration prerequisite. Adapt test setup to install/prove COMPLETE provenance rather than weakening the startup gate. Then inspect the five restart regressions for compatibility issues exposed by that audit. Do not claim GREEN without execution.

## Backlog
- #163 LAB-086 — IN_PROGRESS; exact executable gate pending.
- #180 LAB-095 — IN_PROGRESS; DB binding implemented; exact/downstream gates pending.
- #181 LAB-096 — IN_PROGRESS/COMPOSED ON PR #187; exact/downstream validation pending.
- #169 LAB-090 — restart/historical recovery source + focused regressions composed; execution pending.
- #176 LAB-092 — supported startup-order gate composed; constructor compatibility/exact execution pending.
- #167 LAB-088, #170 LAB-091 — retained draft gates pending.
- #178..185 LAB-093..100 — architecture/security follow-ups.
- #184 LAB-099 — PREPARED authority waits on LAB-095 completion.
