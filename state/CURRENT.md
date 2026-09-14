# Current Lab State

Last updated: 2026-09-14

## Active objective
LAB-086 remains priority #1: finish the exact executable/security gate for asymmetric break-glass history migration. When byte-exact LAB-086 execution cannot be materialized safely, LAB-095/#180 is the permitted fallback prerequisite. LAB-099 PREPARED authority waits on LAB-095 authenticated logical database/history identity plus lifetime physical DB binding.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165. Keep draft.
- LAB-095: #180 / branch `lab-095-database-identity-red-intent` / draft PR #187, head `473185a0278a3ff3777dfe578be018c33018e415`, mergeable=true. Keep draft.
- LAB-099: #184 / draft PR #186; PREPARED authority remains blocked on LAB-095.
- Retained drafts: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175; LAB-092/#176 PR #177.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected open issues plus PR #187 and its committed LAB-095 recovery/authentication regressions.

LAB-086 was probed first. Shell/Python network access to GitHub/raw GitHub still fails DNS resolution. The GitHub connector can read exact files/tree metadata but no supported connector-byte -> executable-filesystem bridge was observed. The raw-download helper requires a web-opened URL while web access to the exact raw GitHub URL is disabled. No byte-exact requirement was weakened and no new LAB-086 PASS is claimed.

### LAB-095 COMPLETE-state external reauthentication bypass — production fixed
A fresh audit found that the prior authenticated-finalize fix was bypassed when local custody was already `COMPLETE`: `migrate_database_identity()` returned `logical_database_identity_digest` immediately after `prepare_database_identity()` and never called `SharedAnchorLedger.execute()`. Therefore repeated migration/startup verification could trust same-DB local state without reauthenticating the external CONFIRMED receipt.

Regression-first commit `86766045eceddc754bc495a345d371a0edbee227` adds `red_intent_lab095_complete_reauthentication.py`: first migration succeeds; every later `ledger.execute()` fails; a second migration must surface that failure rather than returning the local digest.

Production commit `473185a0278a3ff3777dfe578be018c33018e415` removes the COMPLETE early return. All installed non-corrupt states now reload custody, reconstruct the exact identity intent, call `ledger.execute()`, and pass the returned authenticated CONFIRMED entry into `_finalize_confirmed()`. Under its final `BEGIN IMMEDIATE`, exact durable-row equality with that authenticated snapshot remains mandatory before returning/finalizing identity. Published production blob: `c4d1db46b8b64fec116dcfef8bb05e1e7a7b875e`.

Executed evidence this run:
- focused semantic control-flow probe proved the pre-fix COMPLETE path made zero execute calls and the corrected flow makes one — PASS;
- re-fetched PR #187 production lines after commit and verified the COMPLETE early return is absent and `ledger.execute()` is unconditional after custody reconstruction — PASS;
- PR #187 re-fetched at head `473185a...`, draft, mergeable=true.

Durable report: `research/2026-09-14-lab095-complete-state-reauthentication-fix.md`, main commit `a114771a80a398949c36b0822e2e19f24c821273`; #180 comment `5657335683`; PR #187 comment `5657336223`.

Earlier LAB-095 production remains on PR #187: logical identity/custody classifier; explicit CSPRNG/BEGIN IMMEDIATE migration/recovery; same-request reconciliation; under-lock full provider-history verification; construction-bound physical path binding; DB-A -> DB-B regression; crash/concurrent/legacy recovery regressions; public/locked orphan and custody-payload tamper hardening; confirmed-finalize authenticated-snapshot binding.

## Known failures / blockers
- LAB-086 exact complete real-ledger gate remains unexecuted. Connector can read exact repository data, but no observed supported path transfers the complete pinned byte set into the executable filesystem; shell/raw GitHub DNS remains unavailable.
- PRs #165/#172/#173/#175/#177/#186/#187 remain draft until retained exact gates execute.
- The new COMPLETE-state regression plus LAB-095 confirmed-finalize/recovery/tamper suite, DB-A/B regression and downstream LAB-080/LAB-081/LAB-090/LAB-092 gates remain unexecuted against a complete byte-exact closure.
- LAB-090/LAB-095 `supported.py` conflict resolution is security-sensitive: preserve `CanonicalDatabaseBinding` on both supported ledger/history MROs.
- LAB-094 bootstrap authority and LAB-096 provider-history strategy authority remain distinct follow-ups.

## Exact next action
LAB-086 first: probe again for a supported byte-preserving path that can materialize connector-read exact blobs into the executable filesystem. If such a path appears, reconstruct only executable pin `1f90830fca21e2f43fc241012cdd34fd187ba96d`, verify every file with `git hash-object`, and run the retained full LAB-086 exact gate.

If that remains unavailable, continue LAB-095 on PR #187:
1. execute the committed COMPLETE-reauthentication + confirmed-finalize + crash-before-commit + orphan/partial + concurrent-installer + legacy-prefix + locked-custody-tamper regressions on the smallest safe byte-exact closure available;
2. execute the committed DB-A -> DB-B lifetime-binding regression;
3. run LAB-080/LAB-081/LAB-090/LAB-092 focused/downstream gates and a fresh conflict/security audit;
4. keep PR #187 draft until those gates are actual GREEN evidence.

Never replace external authenticated authority with deterministic test vectors, caller-supplied nonce/digest, path hashes, or same-DB self-asserted identifiers.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact executable gate pending.
- #180 / LAB-095 — IN_PROGRESS; COMPLETE-state and confirmed-finalize external-authentication bypasses fixed; exact/downstream gates next.
- #167 / LAB-088, #169 / LAB-090, #170 / LAB-091, #176 / LAB-092 — retained draft gates pending.
- #178..185 / LAB-093..100 — remaining architecture/security follow-ups.
- #184 / LAB-099 — PREPARED authority waits on LAB-095 completion.
