# Current Lab State

Last updated: 2026-09-16

## Active objective
LAB-086 remains priority #1: execute the exact asymmetric break-glass history migration gate from authoritative executable pin `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`. When byte-exact materialization remains unavailable, continue LAB-095/#180 + LAB-096/#181 retained-authority closure on draft PR #187. LAB-099 PREPARED authority waits on LAB-095 completion.

## Active issue / branch / PR
- #163 / LAB-086: draft PR #165; keep draft.
- #179 LAB-094 + #180 LAB-095 + #181 LAB-096: branch `lab-095-database-identity-red-intent`, draft PR #187; latest branch commit `5bfdbdbd64d2281206b1c3d1e9a00db8bdbd4057`; keep draft.
- #169 LAB-090: draft PR #175 retained as donor; composed on PR #187.
- #176 LAB-092: draft PR #177 retained as donor; composed/adapted on PR #187.
- #188 LAB-101: explicit bootstrap + authenticated confirmation bridge and composition regressions are on PR #187; exact execution remains.
- #184 LAB-099: draft PR #186; blocked on LAB-095 completion.

## Last completed step
LAB-086 was probed first. Direct clone failed before repository execution with `Could not resolve host: github.com`, exit 128; no LAB-086 PASS is claimed.

Continued LAB-095/LAB-096 retained-authority closure and found a remaining LAB-094 prerequisite in the supported graph: `CoordinatorOnlyProviderHistory` still inherited mutable public `bootstrap`, while `_verify_durable_locked()` consumes that value as the authenticated history root. PR #187 now binds the first bootstrap assignment to private construction-bound state and rejects later public/private-slot rebinding (`40f97cbcdc46fbe54ac4c2bc0015071902bb9e05`). The capability-surface regression now proves both rebinding attempts fail and verification retains the original g1 root (`5bfdbdbd64d2281206b1c3d1e9a00db8bdbd4057`). Evidence: `research/2026-09-16-lab094-supported-bootstrap-authority-closure.md`, main commit `ed53092bb8cd6817594fd77867c70b2c558f3cb2`. Exact execution is not claimed.

## Known failures / blockers
- LAB-086 complete real-ledger gate remains unexecuted because shell DNS cannot resolve GitHub and no supported connector-to-filesystem byte-preserving bridge is exposed.
- Exact PR #187 repository pytest/compileall remains unavailable for the same materialization reason; committed/source-reviewed regressions are not a GREEN claim.
- PRs #165/#172/#173/#175/#177/#186/#187 remain draft until retained exact gates execute.
- LAB-095 exact no-stub reconstruction/hash verification and execution remain pending.
- LAB-094/095/096 construction-bound authority graph is now source-composed for bootstrap root, canonical path, and provider-history strategy; exact behavioral gates remain pending.
- LAB-090/LAB-092/LAB-101 composed gates remain source-audited but not exact-executed.

## Exact next action
Probe LAB-086 first. Execute its complete gate only if authoritative pin `1fa85a0e34c9ae67da57f1e64dadccf211feacc0` can be placed byte-for-byte into an executable filesystem.

If LAB-086 remains transport-blocked, reconcile the LAB-095 closure/hash inventory after the new `supported.py` and capability-surface blobs. Enumerate the exact focused/downstream executable gates required for #179/#180/#181, and inspect whether any remaining supported production surface consumes a mutable retained authority outside the now-bound bootstrap/path/history-strategy graph. If exact materialization becomes available, verify retained blob/hash identity first and execute focused/downstream gates. Do not claim executable GREEN from source inspection.

## Backlog
- #163 LAB-086 — IN_PROGRESS; exact executable gate pending.
- #179 LAB-094 — source fix composed on PR #187; exact regression/downstream execution pending.
- #180 LAB-095 — IN_PROGRESS; DB-binding/identity and composed regressions source-audited; exact/downstream gates pending.
- #181 LAB-096 — IN_PROGRESS/COMPOSED ON PR #187; exact/downstream validation pending.
- #169 LAB-090 — composed; execution pending.
- #176 LAB-092 — composed; exact execution pending.
- #188 LAB-101 — IN_PROGRESS; source-composed; exact execution pending.
- #167 LAB-088, #170 LAB-091 — retained draft gates pending.
- #178..185 LAB-093..100 — architecture/security follow-ups.
- #184 LAB-099 — PREPARED authority waits on LAB-095 completion.
