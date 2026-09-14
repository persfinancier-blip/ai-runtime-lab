# Current Lab State

Last updated: 2026-09-14

## Active objective
LAB-086 remains priority #1: finish the exact executable/security gate for asymmetric break-glass history migration. When byte-exact LAB-086 execution cannot be materialized safely, LAB-095/#180 is the permitted fallback prerequisite. LAB-099 PREPARED authority waits on LAB-095 authenticated logical database/history identity plus lifetime physical DB binding.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165. Keep draft.
- LAB-095: #180 / branch `lab-095-database-identity-red-intent` / draft PR #187, head `835a81914c5234e68ef436e30c9837331d262432`. Keep draft; retained exact/downstream gates still pending.
- LAB-099: #184 / draft PR #186; PREPARED authority remains blocked on LAB-095.
- Retained drafts: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175; LAB-092/#176 PR #177.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected open issues and active PRs, then resumed the exact next LAB-095 fallback task after the mandatory LAB-086 probe.

LAB-086 was probed first. Shell GitHub access still fails before repository execution with `Could not resolve host: github.com`, exit 128. GitHub connector reads/writes remain available, but no supported byte-preserving connector -> executable-filesystem bridge was established for the complete pinned closure. No byte-exact requirement was weakened and no new LAB-086 PASS is claimed.

### LAB-095 cross-generation COMPLETE reauthentication regression — committed
Added `experiments/provider_generation_history/tests/test_database_identity_rotation_reauthentication.py` on draft PR #187, branch commit `835a81914c5234e68ef436e30c9837331d262432`, published blob `c46914e435a1edbcf234265718976a89eb7a7108`.

The regression uses the real `SupportedHistoricalSharedAnchorLedger`, real signed providers, real generation descriptors and real `rotate_provider()` path. It installs/confirms LAB-095 identity at provider generation 1, proves the exact identity request has a persisted historical receipt, rotates legitimately to generation 2, makes generation 1 unavailable, and requires repeated `migrate_database_identity()` to return the same logical identity digest through historical signed evidence. It then deletes the exact historical receipt and requires fail-closed `HistoricalVerificationError`; local COMPLETE custody alone cannot authorize the identity.

The committed source was re-read after write and passed Python syntax compilation. Full behavioral GREEN is intentionally not claimed because the complete byte-exact dependency closure remains unavailable to the executable runtime.

Durable report: `research/2026-09-14-lab095-cross-generation-complete-reauth-regression.md`, main commit `174b37b20297ac5275c2beed232fea3acc30d12f`; #180 comment `5658108094`; PR #187 comment `5658108665`.

Earlier LAB-095 production remains on PR #187: logical identity/custody classifier; explicit CSPRNG/BEGIN IMMEDIATE migration/recovery; same-request reconciliation; under-lock full provider-history verification; construction-bound physical path binding; DB-A -> DB-B regression; crash/concurrent/legacy recovery regressions; public/locked orphan and custody-payload tamper hardening; confirmed-finalize authenticated-snapshot binding; COMPLETE-state external reauthentication.

## Known failures / blockers
- LAB-086 exact complete real-ledger gate remains unexecuted. Connector can read exact repository data, but shell/raw GitHub DNS remains unavailable and a complete byte-preserving executable materialization path has not been established.
- PRs #165/#172/#173/#175/#177/#186/#187 remain draft until retained exact gates execute.
- LAB-095 COMPLETE/confirmed-finalize/recovery/tamper suite, DB-A/B regression, cross-generation historical-receipt regression, and downstream LAB-080/LAB-081/LAB-090/LAB-092 gates remain unexecuted against a complete byte-exact closure.
- LAB-090/LAB-095 `supported.py` conflict resolution is security-sensitive: preserve `CanonicalDatabaseBinding` on both supported ledger/history MROs.
- LAB-094 bootstrap authority and LAB-096 provider-history strategy authority remain distinct follow-ups.

## Exact next action
LAB-086 first: probe again for a supported byte-preserving path that can materialize connector-read exact blobs into the executable filesystem. If such a path appears, reconstruct only executable pin `1f90830fca21e2f43fc241012cdd34fd187ba96d`, verify every file with `git hash-object`, and run the retained full LAB-086 exact gate.

If that remains unavailable, continue LAB-095 on PR #187:
1. materialize the smallest safe byte-exact dependency closure sufficient to execute `test_database_identity_rotation_reauthentication.py` plus the committed COMPLETE-reauthentication and confirmed-finalize regressions; verify every materialized file against its Git blob SHA before execution;
2. execute crash-before-commit + orphan/partial + concurrent-installer + legacy-prefix + locked-custody-tamper regressions on that verified closure;
3. execute the committed DB-A -> DB-B lifetime-binding regression;
4. run LAB-080/LAB-081/LAB-090/LAB-092 focused/downstream gates and a fresh conflict/security audit;
5. keep PR #187 draft until those gates are actual GREEN evidence.

Never replace external authenticated authority with deterministic test vectors, caller-supplied nonce/digest, path hashes, or same-DB self-asserted identifiers.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact executable gate pending.
- #180 / LAB-095 — IN_PROGRESS; cross-generation COMPLETE reauthentication regression committed; exact/downstream execution next.
- #167 / LAB-088, #169 / LAB-090, #170 / LAB-091, #176 / LAB-092 — retained draft gates pending.
- #178..185 / LAB-093..100 — remaining architecture/security follow-ups.
- #184 / LAB-099 — PREPARED authority waits on LAB-095 completion.
