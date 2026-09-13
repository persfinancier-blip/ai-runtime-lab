# Current Lab State

Last updated: 2026-09-14

## Active objective
LAB-086 remains priority #1: finish the exact executable/security gate for asymmetric break-glass history migration. When byte-exact LAB-086 execution cannot be materialized safely, LAB-095/#180 is the permitted fallback prerequisite. LAB-099 PREPARED authority waits on LAB-095 authenticated logical database/history identity plus lifetime physical DB binding.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165. Keep draft.
- LAB-095: #180 / branch `lab-095-database-identity-red-intent` / draft PR #187, current head at least `e3d4821f4c53349eff8f96614ef0c36b4c5e8230`. Keep draft.
- LAB-099: #184 / draft PR #186; PREPARED authority remains blocked on LAB-095.
- Retained drafts: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175; LAB-092/#176 PR #177.

## Last completed step
Re-read `AGENTS.md`, this handoff, `prompts/SELF_RESUME.md`, open PRs and LAB-095 issue #180. LAB-086 was re-probed first. Shell Git transport still failed before repository execution with `Could not resolve host: github.com`; raw GitHub `curl` DNS also failed. No LAB-086 gate was weakened and no new PASS is claimed.

### LAB-095 confirmed-finalize reauthentication race
Source audit found a new TOCTOU in `database_identity_migration.py`: real `SharedAnchorLedger.execute()` reauthenticates a CONFIRMED ledger entry against the external provider and returns that authenticated `LedgerEntry`, but `migrate_database_identity()` discards the return value. `_finalize_confirmed()` then opens a later `BEGIN IMMEDIATE`, rereads SQLite, and derives/persists logical identity from whichever CONFIRMED row exists at that later moment.

A same-host SQLite writer can therefore change authority-bearing provider id/generation/position/receipt after external reauthentication but before local finalization. The locked custody classifier protects payload/custody coherence but does not bind finalization to the exact externally authenticated CONFIRMED tuple.

Executed evidence this run:
- a narrow file-backed SQLite semantic probe captured an authenticated `(provider-alpha, generation 1, position 1, receipt d...)` tuple, changed the durable row to `(attacker-provider, generation 99, position 99, receipt e...)` while retaining request/payload, and reproduced the current finalization shape accepting the tampered tuple into CONFIRMED custody;
- regression-first branch commit `e3d4821f4c53349eff8f96614ef0c36b4c5e8230` added `red_intent_lab095_confirmed_finalize_reauthentication.py`;
- the regression requires `DatabaseIdentityMigrationError("confirmed identity intent changed after authentication")` and custody remaining PREPARED/unfinalized after post-auth row replacement.

Durable report: `research/2026-09-14-lab095-confirmed-finalize-reauthentication-race.md`, main commit `1bed4560ca09cc8519a397dba215492204831b94`; #180 comment `5656557496`; PR #187 comment `5656558077`.

Earlier LAB-095 production remains on PR #187: logical identity/custody classifier; explicit CSPRNG/BEGIN IMMEDIATE migration/recovery; same-request reconciliation; under-lock full provider-history verification; construction-bound physical path binding; DB-A -> DB-B regression; crash/concurrent/legacy recovery regressions; public/locked orphan and tamper hardening.

## Known failures / blockers
- LAB-086 exact complete real-ledger gate remains unexecuted because shell Git/raw GitHub transport cannot resolve GitHub hosts; do not manually reconstruct the 50+ file closure or weaken byte-exact evidence requirements.
- PRs #165/#172/#173/#175/#177/#186/#187 remain draft until retained exact gates execute.
- LAB-095 newly discovered confirmed-finalize race is RED-intent only; production fix is not yet committed.
- LAB-095 full DB-A/B regression and downstream LAB-080/LAB-081/LAB-090/LAB-092 gates remain unexecuted.
- LAB-090/LAB-095 `supported.py` conflict resolution is security-sensitive: preserve `CanonicalDatabaseBinding` on both supported ledger/history MROs.
- LAB-094 bootstrap authority and LAB-096 provider-history strategy authority remain distinct follow-ups.

## Exact next action
LAB-086 first: re-probe for a supported byte-preserving materialization path. If available, reconstruct only executable pin `1f90830fca21e2f43fc241012cdd34fd187ba96d`, verify every file by Git blob identity, and run the retained LAB-086 exact gate.

If exact LAB-086 materialization is still unavailable, continue LAB-095 on PR #187:
1. fix the new confirmed-finalize race by retaining the exact CONFIRMED `LedgerEntry` returned by `ledger.execute()` and passing it into `_finalize_confirmed()`;
2. under the final `BEGIN IMMEDIATE`, compare the complete current identity-intent tuple (component/type/payload/provider/generation/predecessor/position/request/status/receipt) with that authenticated snapshot; any drift must fail closed before custody mutation;
3. run the new RED plus crash-before-commit, partial-state, concurrent-installer, legacy-prefix, locked-custody tamper and DB-A/B regressions on the smallest safe byte-exact closure available;
4. then run LAB-080/LAB-081/LAB-090/LAB-092 focused/downstream gates and fresh conflict audit before integration.

Never replace external authenticated authority with deterministic test vectors, caller-supplied nonce/digest, path hashes, or same-DB self-asserted identifiers.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact executable gate pending.
- #180 / LAB-095 — IN_PROGRESS; confirmed-finalize external-authentication TOCTOU now has committed RED intent; production fix next.
- #167 / LAB-088, #169 / LAB-090, #170 / LAB-091, #176 / LAB-092 — retained draft gates pending.
- #178..185 / LAB-093..100 — remaining architecture/security follow-ups.
- #184 / LAB-099 — PREPARED authority waits on LAB-095 completion.
