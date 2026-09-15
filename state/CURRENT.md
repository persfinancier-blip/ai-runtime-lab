# Current Lab State

Last updated: 2026-09-15

## Active objective
LAB-086 remains priority #1: execute the exact asymmetric break-glass history migration gate from authoritative executable pin `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`. When byte-exact materialization remains unavailable, continue LAB-095/#180 + LAB-096/#181 composition on draft PR #187. LAB-099 PREPARED authority waits on LAB-095 completion.

## Active issue / branch / PR
- #163 / LAB-086: draft PR #165; keep draft.
- #180 LAB-095 + #181 LAB-096: branch `lab-095-database-identity-red-intent`, draft PR #187; keep draft.
- #169 LAB-090: draft PR #175 retained as donor; provider fence, pre-ack SQL transition, durable acknowledgement, supported-ledger rotation wiring, restart/historical recovery, and focused restart regressions are ported to PR #187.
- #176 LAB-092: draft PR #177 retained as donor; shared schema, locked provenance/receipt guard, read-only startup gate, explicit PREPARED migration writer, focused writer regressions, and supported-constructor startup ordering are adapted onto PR #187.
- #188 LAB-101: explicit end-to-end LAB-092 fresh/legacy bootstrap + authenticated confirmation bridge; discovered by constructor-compatibility audit and now blocks safe adaptation of legacy fresh-constructor tests.
- #184 LAB-099: draft PR #186; blocked on LAB-095 completion.

## Last completed step
LAB-086 was probed first. Direct clone failed before repository execution with `Could not resolve host: github.com`, exit 128; no LAB-086 PASS is claimed.

Audited the existing main LAB-081 supported integration suite against PR #187's new LAB-092 startup prerequisite. The suite's fresh `SupportedHistoricalSharedAnchorLedger` constructor calls cannot be mechanically adapted to the current migration writer: ordinary startup now correctly requires exact `COMPLETE` before any provider-history/shared-ledger construction, while `install_and_reserve_activation_schema_v1()` requires an already-existing ledger/history and stops at deterministic `PREPARED`. PR #187 therefore lacks a supported end-to-end fresh/legacy bootstrap + authenticated confirmation entrypoint. Weakening startup or stamping CONFIRMED in tests would violate LAB-092. Created #188 LAB-101 and recorded `research/2026-09-15-lab092-constructor-compatibility-bootstrap-gap.md`, main commit `ce3b03c2cf512c21a7237d6759bb8d5b251f058f`. PR #187 remains at `2510028d442f775617696d02254d02305e902d8a`; no branch code was changed in this audit.

## Known failures / blockers
- LAB-086 complete real-ledger gate remains unexecuted because shell DNS cannot resolve GitHub and no supported connector-to-filesystem byte-preserving bridge is exposed.
- Exact PR #187 repository pytest/compileall remains unavailable for the same materialization reason; committed/source-reviewed regressions are not a GREEN claim.
- PRs #165/#172/#173/#175/#177/#186/#187 remain draft until retained exact gates execute.
- LAB-095 complete eight-file no-stub tree still needs same-run reconstruction/hash verification plus execution.
- LAB-096 source fixes still need exact repository behavioral gates.
- LAB-090 restart recovery source and focused regressions are composed; execution remains pending.
- LAB-092 ordinary startup correctly requires exact COMPLETE provenance before history construction/recovery, but PR #187 has no supported end-to-end path from a legitimate fresh/pre-LAB-090 DB through PREPARED to authenticated CONFIRMED. #188 tracks this gap; legacy constructor tests must not be weakened around it.

## Exact next action
Probe LAB-086 first. Execute its complete gate only if authoritative pin `1fa85a0e34c9ae67da57f1e64dadccf211feacc0` can be placed byte-for-byte into an executable filesystem.

If LAB-086 remains transport-blocked, implement the smallest LAB-101/#188 explicit bootstrap/migration surface on PR #187. Preserve the ordinary read-only COMPLETE startup gate, private construction-bound `_history()`, canonical DB binding, and no post-construction history replacement. The explicit path must establish legitimate fresh/legacy ledger+history state, atomically install exact LAB-090 DDL + deterministic PREPARED marker, re-verify history/runtime authority, authenticate/confirm the exact completion intent, and only then return the normal supported ledger. After that, adapt `experiments/provider_generation_history/tests/test_integration.py` fresh-constructor setup through the explicit entrypoint. Do not claim GREEN without execution.

## Backlog
- #163 LAB-086 — IN_PROGRESS; exact executable gate pending.
- #180 LAB-095 — IN_PROGRESS; DB binding implemented; exact/downstream gates pending.
- #181 LAB-096 — IN_PROGRESS/COMPOSED ON PR #187; exact/downstream validation pending.
- #169 LAB-090 — restart/historical recovery source + focused regressions composed; execution pending.
- #176 LAB-092 — startup-order gate composed; end-to-end explicit migration entrypoint gap moved to #188.
- #188 LAB-101 — READY/HIGH: restore fresh/legacy explicit bootstrap + authenticated LAB-092 confirmation without weakening startup.
- #167 LAB-088, #170 LAB-091 — retained draft gates pending.
- #178..185 LAB-093..100 — architecture/security follow-ups.
- #184 LAB-099 — PREPARED authority waits on LAB-095 completion.
