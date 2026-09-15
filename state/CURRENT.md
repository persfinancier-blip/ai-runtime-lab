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

Continued LAB-095 reference/regression closure at exact PR #187 head. Pinned connector-visible reference/regression blobs: `lab095_database_identity_reference.py` `9f02ddf64cff5b245cfa7a58e188ff9792b3eb18`; `lab095_identity_installation_reference.py` `eca968573bd5374239507aec58b015fcd1f18869`; `red_intent_lab095_complete_reauthentication.py` `347eb94d7d2c601095789c9903dbcbbc24099cd8`; `red_intent_lab095_confirmed_finalize_reauthentication.py` `7dcd20dfd24a9439583595bf433f9f696bd870e7`; `red_intent_lab095_database_identity.py` `b1499243e8452daadf97fdb9ff97e29a9ce82e28`; `test_database_path_binding.py` `9aa68be771e251863b228bcc4fadc5486796254e`.

Composition audit found `test_database_path_binding.py` stale relative to the LAB-090/LAB-092 composition on the same PR: it directly constructs the supported ledger on a fresh DB despite the COMPLETE-only startup gate and uses plain `SignedAnchorProvider` for supported rotation despite LAB-090 fenced-provider requirements. This is a test-composition defect; do not weaken production startup or switch the acceptance regression to legacy history. Evidence: `research/2026-09-15-lab095-reference-regression-blob-audit.md`, main commit `38599dd8d2104880a9670a1e81da78dac7b54f0a`; #180 updated.

## Known failures / blockers
- LAB-086 complete real-ledger gate remains unexecuted because shell DNS cannot resolve GitHub and no supported connector-to-filesystem byte-preserving bridge is exposed.
- Exact PR #187 repository pytest/compileall remains unavailable for the same materialization reason; committed/source-reviewed regressions are not a GREEN claim.
- PRs #165/#172/#173/#175/#177/#186/#187 remain draft until retained exact gates execute.
- LAB-095 exact no-stub reconstruction/hash verification and execution remain pending.
- LAB-095 `test_database_path_binding.py` must be adapted to official LAB-101/LAB-092 migration bootstrap + LAB-090 fenced-provider semantics before it can serve as the composed DB-A -> DB-B executable gate.
- LAB-096 source fixes still need exact repository behavioral gates.
- LAB-090 restart recovery source and focused regressions are composed; execution remains pending.
- LAB-101 explicit bootstrap, legacy integration adaptation, failure/concurrency and UNKNOWN retry regressions are source-composed but not exact-executed.

## Exact next action
Probe LAB-086 first. Execute its complete gate only if authoritative pin `1fa85a0e34c9ae67da57f1e64dadccf211feacc0` can be placed byte-for-byte into an executable filesystem.

If LAB-086 remains transport-blocked, update PR #187 `experiments/provider_generation_history/tests/test_database_path_binding.py`: bootstrap DB A through official `migrate_activation_schema_v1()` so the normal supported ledger sees exact COMPLETE provenance; use `FencedActivationProvider` for rotation; adjust candidate provider/current-position assertions for the authenticated migration increment; preserve DB-B corrupted-history, public/private path rebinding rejection, strategy-rebinding rejection, and proof that subsequent supported mutation touches DB A only. Do not manually stamp provenance and do not substitute legacy `HistoricalSharedAnchorLedger`. Then source-audit every expected position in that regression. If exact materialization becomes available, verify retained blob/hash identity first and execute focused/downstream gates. Do not claim executable GREEN from source inspection.

## Backlog
- #163 LAB-086 — IN_PROGRESS; exact executable gate pending.
- #180 LAB-095 — IN_PROGRESS; production/reference/regression blobs source-pinned; DB-binding regression requires composed startup/fencing adaptation + exact/downstream gates.
- #181 LAB-096 — IN_PROGRESS/COMPOSED ON PR #187; exact/downstream validation pending.
- #169 LAB-090 — composed; execution pending.
- #176 LAB-092 — composed; exact execution pending.
- #188 LAB-101 — IN_PROGRESS: explicit bootstrap/confirmation bridge + legacy integration + failure/concurrency + UNKNOWN retry source regressions implemented; exact execution pending.
- #167 LAB-088, #170 LAB-091 — retained draft gates pending.
- #178..185 LAB-093..100 — architecture/security follow-ups.
- #184 LAB-099 — PREPARED authority waits on LAB-095 completion.
