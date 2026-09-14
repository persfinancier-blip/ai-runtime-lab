# Current Lab State

Last updated: 2026-09-14

## Active objective
LAB-086 remains priority #1: finish the exact executable/security gate for asymmetric break-glass history migration. When byte-exact LAB-086 execution cannot be materialized safely, LAB-095/#180 is the permitted fallback prerequisite. LAB-099 PREPARED authority waits on LAB-095 authenticated logical database/history identity plus lifetime physical DB binding.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165. Keep draft.
- LAB-095: #180 / branch `lab-095-database-identity-red-intent` / draft PR #187, head `473185a0278a3ff3777dfe578be018c33018e415`. Direct PR REST recheck this run: mergeable=true, rebaseable=true, mergeable_state=clean. Keep draft.
- LAB-099: #184 / draft PR #186; PREPARED authority remains blocked on LAB-095.
- Retained drafts: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175; LAB-092/#176 PR #177.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected open issues, PR #187, LAB-095 migration production, recovery regressions, shared-ledger reauthentication, supported historical reauthentication, and provider-history integration.

LAB-086 was probed first. Shell GitHub access still fails before repository execution with `Could not resolve host: github.com`, exit 128. GitHub connector reads remain available, but no supported byte-preserving connector -> executable-filesystem bridge was established for the complete pinned closure. No byte-exact requirement was weakened and no new LAB-086 PASS is claimed.

### LAB-095 COMPLETE reauthentication across provider rotation — audited
The prior COMPLETE-state fix requires repeated `migrate_database_identity()` calls to drive the existing identity intent through `ledger.execute()` before trusting local COMPLETE custody. A fresh audit checked whether this would permanently fail after a legitimate provider-generation rotation.

Plain `SharedAnchorLedger._reauthenticate()` is current-generation-only, so that concern is real for the plain ledger. However the supported historical surface deliberately overrides it: `SupportedHistoricalSharedAnchorLedger._reauthenticate()` first loads persisted `HistoricalReceipt` evidence, verifies its provider id, generation, position and request id against the old ledger entry, and returns the historical stable binding. Only when no historical receipt exists does it require the entry to belong to the current generation and authenticate against the live provider. Therefore a generation-1 LAB-095 identity intent can remain externally authenticated after a legitimate move to generation 2 when used through the supported historical composition.

Decision: do not revert or weaken COMPLETE-state external reauthentication. Add/execute a retained cross-generation regression on the supported historical closure: install/confirm identity at g1, prove historical receipt persisted, rotate legitimately to g2, re-run identity verification and require the same logical identity digest; then corrupt/remove the historical receipt and require fail-closed behavior.

Durable report: `research/2026-09-14-lab095-complete-reauth-provider-rotation-audit.md`, main commit `7a35c49745920fafa7d7081f0eeac885a1c59bf3`; #180 comment `5657713093`.

PR #187 state note: one higher-level connector summary transiently reported `mergeable=false`, but direct GitHub PR REST returned `mergeable=true`, `rebaseable=true`, `mergeable_state=clean`; compare shows main advanced only through LAB-095 research/state commits and the PR remains 32 commits ahead / 29 behind from merge base `2c72b76b...`.

Earlier LAB-095 production remains on PR #187: logical identity/custody classifier; explicit CSPRNG/BEGIN IMMEDIATE migration/recovery; same-request reconciliation; under-lock full provider-history verification; construction-bound physical path binding; DB-A -> DB-B regression; crash/concurrent/legacy recovery regressions; public/locked orphan and custody-payload tamper hardening; confirmed-finalize authenticated-snapshot binding; COMPLETE-state external reauthentication.

## Known failures / blockers
- LAB-086 exact complete real-ledger gate remains unexecuted. Connector can read exact repository data, but shell/raw GitHub DNS remains unavailable and a complete byte-preserving executable materialization path has not been established.
- PRs #165/#172/#173/#175/#177/#186/#187 remain draft until retained exact gates execute.
- LAB-095 COMPLETE/confirmed-finalize/recovery/tamper suite, DB-A/B regression, new cross-generation historical-receipt regression, and downstream LAB-080/LAB-081/LAB-090/LAB-092 gates remain unexecuted against a complete byte-exact closure.
- LAB-090/LAB-095 `supported.py` conflict resolution is security-sensitive: preserve `CanonicalDatabaseBinding` on both supported ledger/history MROs.
- LAB-094 bootstrap authority and LAB-096 provider-history strategy authority remain distinct follow-ups.

## Exact next action
LAB-086 first: probe again for a supported byte-preserving path that can materialize connector-read exact blobs into the executable filesystem. If such a path appears, reconstruct only executable pin `1f90830fca21e2f43fc241012cdd34fd187ba96d`, verify every file with `git hash-object`, and run the retained full LAB-086 exact gate.

If that remains unavailable, continue LAB-095 on PR #187:
1. add the supported cross-generation COMPLETE-reauthentication regression described above, using persisted historical receipt evidence rather than a fake current-generation ledger;
2. execute the committed COMPLETE-reauthentication + confirmed-finalize + crash-before-commit + orphan/partial + concurrent-installer + legacy-prefix + locked-custody-tamper regressions on the smallest safe byte-exact closure available;
3. execute the committed DB-A -> DB-B lifetime-binding regression;
4. run LAB-080/LAB-081/LAB-090/LAB-092 focused/downstream gates and a fresh conflict/security audit;
5. keep PR #187 draft until those gates are actual GREEN evidence.

Never replace external authenticated authority with deterministic test vectors, caller-supplied nonce/digest, path hashes, or same-DB self-asserted identifiers.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact executable gate pending.
- #180 / LAB-095 — IN_PROGRESS; COMPLETE-state and confirmed-finalize external-authentication bypasses fixed; provider-rotation compatibility audited; exact/downstream gates next.
- #167 / LAB-088, #169 / LAB-090, #170 / LAB-091, #176 / LAB-092 — retained draft gates pending.
- #178..185 / LAB-093..100 — remaining architecture/security follow-ups.
- #184 / LAB-099 — PREPARED authority waits on LAB-095 completion.
