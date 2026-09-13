# Current Lab State

Last updated: 2026-09-14

## Active objective
LAB-086 remains priority #1: finish the exact executable/security gate for asymmetric break-glass history migration. When byte-exact LAB-086 execution cannot be materialized safely, LAB-095/#180 is the permitted fallback prerequisite. LAB-099 PREPARED authority waits on LAB-095 authenticated logical database/history identity plus lifetime physical DB binding.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165. Keep draft.
- LAB-095: #180 / branch `lab-095-database-identity-red-intent` / draft PR #187, head `d022656ceac70700009d302de9d26ad47190b0f6`, mergeable=true. Keep draft.
- LAB-099: #184 / draft PR #186; PREPARED authority remains blocked on LAB-095.
- Retained drafts: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175; LAB-092/#176 PR #177.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected LAB-086 #163/PR #165 and LAB-095 #180/PR #187.

LAB-086 was probed first. The GitHub connector can now read the recursive tree for exact executable commit `1f90830fca21e2f43fc241012cdd34fd187ba96d`, but the shell execution environment still cannot resolve `github.com`; direct clone again failed before repository execution with `Could not resolve host: github.com`, exit 128. The connector does not provide a supported byte-stream/materialize operation into the executable filesystem for the full 50+ file closure, so the full exact gate remains unexecuted. No byte-exact requirement was weakened and no new LAB-086 PASS is claimed.

### LAB-095 confirmed-finalize authentication binding — production fixed
The previously committed RED showed that `SharedAnchorLedger.execute()` externally reauthenticates and returns a CONFIRMED `LedgerEntry`, but LAB-095 discarded it and later finalized from a fresh SQLite read. A same-host writer could replace authority-bearing fields after reauthentication but before local custody finalization.

PR #187 now retains the exact CONFIRMED entry and passes it into `_finalize_confirmed()`. Under the final `BEGIN IMMEDIATE`, the implementation rereads and compares all 11 durable intent fields (intent/component/type/payload/provider/generation/predecessor/position/request/status/receipt) against that authenticated snapshot before any custody mutation. Any drift raises `DatabaseIdentityMigrationError("confirmed identity intent changed after authentication")`. COMPLETE state also requires the same snapshot equality and cannot bypass this binding.

Production commit: `f958719e9108b9d2011fcebfd5500edead854494`; test-helper API alignment commit/head: `d022656ceac70700009d302de9d26ad47190b0f6`; production blob after re-fetch: `3292c0aacaf564416cb336a95ccf9229963dd738`.

Executed evidence this run:
- focused file-backed SQLite guard accepted an unchanged authenticated tuple;
- after changing provider id/generation/position/receipt, the same guard rejected finalization with the required error — PASS;
- GitHub compare from prior head `e3d4821f...` to `d022656c...` shows only production migration code plus its migration-test helper changed.

Durable report: `research/2026-09-14-lab095-authenticated-finalize-binding-fix.md`, main commit `66b53a907f8aa66e4b923706153d145c87bb2dca`; #180 comment `5656944532`; PR #187 comment `5656946512`.

Earlier LAB-095 production remains on PR #187: logical identity/custody classifier; explicit CSPRNG/BEGIN IMMEDIATE migration/recovery; same-request reconciliation; under-lock full provider-history verification; construction-bound physical path binding; DB-A -> DB-B regression; crash/concurrent/legacy recovery regressions; public/locked orphan and custody-payload tamper hardening.

## Known failures / blockers
- LAB-086 exact complete real-ledger gate remains unexecuted. Connector can read the exact tree, but no observed supported path transfers the complete pinned byte set into the executable filesystem; shell/raw GitHub DNS remains unavailable.
- PRs #165/#172/#173/#175/#177/#186/#187 remain draft until retained exact gates execute.
- LAB-095 full exact recovery/tamper suite, DB-A/B regression and downstream LAB-080/LAB-081/LAB-090/LAB-092 gates remain unexecuted.
- LAB-090/LAB-095 `supported.py` conflict resolution is security-sensitive: preserve `CanonicalDatabaseBinding` on both supported ledger/history MROs.
- LAB-094 bootstrap authority and LAB-096 provider-history strategy authority remain distinct follow-ups.

## Exact next action
LAB-086 first: probe for a supported byte-preserving path that can materialize connector-read exact blobs into the executable filesystem. If such a path appears, reconstruct only executable pin `1f90830fca21e2f43fc241012cdd34fd187ba96d`, verify every file with `git hash-object`, and run the retained full LAB-086 exact gate.

If that remains unavailable, continue LAB-095 on PR #187:
1. execute the committed confirmed-finalize regression plus crash-before-commit, partial-state, concurrent-installer, legacy-prefix and locked-custody tamper regressions on the smallest safe byte-exact closure available;
2. execute the committed DB-A -> DB-B lifetime-binding regression;
3. run LAB-080/LAB-081/LAB-090/LAB-092 focused/downstream gates and a fresh conflict/security audit;
4. keep PR #187 draft until those gates are actual GREEN evidence.

Never replace external authenticated authority with deterministic test vectors, caller-supplied nonce/digest, path hashes, or same-DB self-asserted identifiers.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact executable gate pending.
- #180 / LAB-095 — IN_PROGRESS; confirmed-finalize TOCTOU production fix committed; full exact/downstream gates next.
- #167 / LAB-088, #169 / LAB-090, #170 / LAB-091, #176 / LAB-092 — retained draft gates pending.
- #178..185 / LAB-093..100 — remaining architecture/security follow-ups.
- #184 / LAB-099 — PREPARED authority waits on LAB-095 completion.
