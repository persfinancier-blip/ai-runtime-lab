# Current Lab State

Last updated: 2026-09-16

## Active objective
LAB-086 remains priority #1: execute the exact asymmetric break-glass history migration gate from authoritative executable pin `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`. When byte-exact materialization remains unavailable, finish executable-readiness closure for LAB-094/#179 + LAB-095/#180 + LAB-096/#181 on draft PR #187. LAB-099 PREPARED authority waits on LAB-095 completion.

## Active issue / branch / PR
- #163 / LAB-086: draft PR #165; keep draft.
- #179 LAB-094 + #180 LAB-095 + #181 LAB-096: branch `lab-095-database-identity-red-intent`, draft PR #187; observed head `5bfdbdbd64d2281206b1c3d1e9a00db8bdbd4057`; keep draft.
- #169 LAB-090: draft PR #175 retained as donor; composed on PR #187.
- #176 LAB-092: draft PR #177 retained as donor; composed/adapted on PR #187.
- #188 LAB-101: explicit bootstrap + authenticated confirmation bridge and composition regressions are on PR #187; exact execution remains.
- #184 LAB-099: draft PR #186; blocked on LAB-095 completion.

## Last completed step
LAB-086 was probed first. Direct clone failed before repository execution with `Could not resolve host: github.com`, exit 128; no LAB-086 PASS is claimed.

Re-checked PR #187 through the GitHub control plane: observed head remains `5bfdbdbd64d2281206b1c3d1e9a00db8bdbd4057`, so no head drift was observed relative to the prior closure inventory. Completed the previously implicit downstream-gate audit. LAB-080 merged evidence (#152) plus current main-tree discovery pins `experiments/shared_anchor_intent_ledger/tests/test_protocol.py`, `test_restart_rollback.py`, and `test_supported.py`, with `unsafe_monotonic_expected_failure.py` retained as an expected-failure control. LAB-081 merged evidence (#154) plus current main-tree discovery pins provider-history `test_protocol.py`, `test_standalone_audit.py`, `test_audit_regressions.py`, and `test_integration.py`; the latter two overlap existing focused/composed gates and need only one observed execution result. Updated `research/2026-09-16-lab094-096-closure-inventory.md` in main commit `6bc60d82a90455192dcae84075221f60e068803b`. Exact execution is not claimed.

## Known failures / blockers
- LAB-086 complete real-ledger gate remains unexecuted because shell DNS cannot resolve GitHub and no supported connector-to-filesystem byte-preserving bridge is exposed.
- Exact PR #187 repository pytest/compileall remains unavailable for the same materialization reason; committed/source-reviewed regressions are not a GREEN claim.
- PRs #165/#172/#173/#175/#177/#186/#187 remain draft until retained exact gates execute.
- LAB-095 exact no-stub reconstruction/hash verification and execution remain pending.
- LAB-094/095/096 construction-bound authority graph is source-closed for bootstrap root, canonical path, and provider-history strategy; exact behavioral/downstream gates remain pending.
- LAB-090/LAB-092/LAB-101 composed gates remain source-audited but not exact-executed.

## Exact next action
Probe LAB-086 first. Execute its complete gate only if authoritative pin `1fa85a0e34c9ae67da57f1e64dadccf211feacc0` can be placed byte-for-byte into an executable filesystem.

If LAB-086 remains transport-blocked, re-check PR #187 head/blob identities for drift. Do not broaden LAB-094/095/096 speculatively: the focused, composed, LAB-080, and LAB-081 executable gate inventory is now explicit in `research/2026-09-16-lab094-096-closure-inventory.md`. If exact materialization becomes available, verify retained blob/hash identity first, execute that inventory, then full pytest and compileall. If materialization remains unavailable and hashes remain stable, audit whether PR #187's current diff contains any files outside the recorded closure/gate inventory that can affect supported startup/rotation/database identity; record only concrete omissions. Do not claim executable GREEN from source inspection.

## Backlog
- #163 LAB-086 — IN_PROGRESS; exact executable gate pending.
- #179 LAB-094 — source closure composed on PR #187; exact regression/downstream execution pending.
- #180 LAB-095 — IN_PROGRESS; source closure/hash inventory reconciled; exact/downstream gates pending.
- #181 LAB-096 — IN_PROGRESS/COMPOSED ON PR #187; source closure reconciled; exact/downstream validation pending.
- #169 LAB-090 — composed; execution pending.
- #176 LAB-092 — composed; exact execution pending.
- #188 LAB-101 — IN_PROGRESS; source-composed; exact execution pending.
- #167 LAB-088, #170 LAB-091 — retained draft gates pending.
- #178..185 LAB-093..100 — architecture/security follow-ups.
- #184 LAB-099 — PREPARED authority waits on LAB-095 completion.
