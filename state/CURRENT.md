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

Continued the remaining PR #187 supported integration/wiring call-site audit. `experiments/provider_generation_history/tests/test_integration.py` is already correctly composed through LAB-101 bootstrap with `FencedActivationProvider`, migration position accounting, and post-COMPLETE restart. `tests/test_supported_activation_wiring.py` is source-structure validation only. `test_activation_schema_startup.py` and `test_activation_restart_recovery.py` intentionally isolate lower-level startup/recovery semantics and should retain manual/fake state. LAB-101 explicit-bootstrap tests use `SignedAnchorProvider` intentionally because they authenticate an ordinary migration intent and perform no provider rotation; LAB-090 fencing is a rotation requirement, not a blanket increment requirement. No additional stale supported-runtime call site was found in this slice. Evidence: `research/2026-09-16-lab095-integration-wiring-callsite-audit.md`, main commit `17f41fceafb21e8086c2388023b04f9dd55a81f2`.

## Known failures / blockers
- LAB-086 complete real-ledger gate remains unexecuted because shell DNS cannot resolve GitHub and no supported connector-to-filesystem byte-preserving bridge is exposed.
- Exact PR #187 repository pytest/compileall remains unavailable for the same materialization reason; committed/source-reviewed regressions are not a GREEN claim.
- PRs #165/#172/#173/#175/#177/#186/#187 remain draft until retained exact gates execute.
- LAB-095 exact no-stub reconstruction/hash verification and execution remain pending.
- LAB-095 DB-binding, identity-rotation, capability-surface, corrupt-receipt restart, and integration/wiring regressions are source-composed/audited with LAB-101/LAB-092 bootstrap and LAB-090 fencing; exact execution remains required.
- LAB-096 migration-only strategy audit found no defect; exact repository behavioral gates remain pending.
- LAB-090 restart recovery source and focused regressions are composed; execution remains pending.
- LAB-101 explicit bootstrap, legacy integration adaptation, failure/concurrency, UNKNOWN retry, and LAB-095 composition are source-composed but not exact-executed.

## Exact next action
Probe LAB-086 first. Execute its complete gate only if authoritative pin `1fa85a0e34c9ae67da57f1e64dadccf211feacc0` can be placed byte-for-byte into an executable filesystem.

If LAB-086 remains transport-blocked, stop mechanically adapting lower-level fixtures and continue LAB-095/LAB-096 authority closure: inspect any remaining production/supported-runtime surfaces for mutable canonical path or provider-history strategy authority. If none remain, reconcile the LAB-095 eight-file closure/hash inventory and enumerate the exact focused/downstream executable gates required before #180/#181 can leave draft status. If exact materialization becomes available, verify retained blob/hash identity first and execute focused/downstream gates. Do not claim executable GREEN from source inspection.

## Backlog
- #163 LAB-086 — IN_PROGRESS; exact executable gate pending.
- #180 LAB-095 — IN_PROGRESS; DB-binding + identity-rotation + capability-surface + corrupt-receipt restart regressions source-composed; integration/wiring and migration/recovery/classifier/store-receipt slices audited; exact/downstream gates pending.
- #181 LAB-096 — IN_PROGRESS/COMPOSED ON PR #187; migration-only strategy audit PASS by source inspection; exact/downstream validation pending.
- #169 LAB-090 — composed; execution pending.
- #176 LAB-092 — composed; exact execution pending.
- #188 LAB-101 — IN_PROGRESS: explicit bootstrap/confirmation bridge + legacy integration + failure/concurrency + UNKNOWN retry + LAB-095 composition implemented; exact execution pending.
- #167 LAB-088, #170 LAB-091 — retained draft gates pending.
- #178..185 LAB-093..100 — architecture/security follow-ups.
- #184 LAB-099 — PREPARED authority waits on LAB-095 completion.
