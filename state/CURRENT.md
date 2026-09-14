# Current Lab State

Last updated: 2026-09-14

## Active objective
LAB-086 remains priority #1: finish the exact executable/security gate for asymmetric break-glass history migration. When byte-exact LAB-086 execution cannot be materialized safely, LAB-095/#180 is the permitted fallback prerequisite. LAB-099 PREPARED authority waits on LAB-095 authenticated logical database/history identity plus lifetime physical DB binding.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165. Keep draft.
- LAB-095: #180 / branch `lab-095-database-identity-red-intent` / draft PR #187, head `835a81914c5234e68ef436e30c9837331d262432`. Keep draft.
- LAB-099: #184 / draft PR #186; PREPARED authority remains blocked on LAB-095.
- Retained drafts: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175; LAB-092/#176 PR #177.

## Last completed step
Mandatory LAB-086 probe was executed first. Direct shell Git materialization again failed before repository execution with `Could not resolve host: github.com`, exit 128. No byte-exact LAB-086 requirement was weakened and no new complete-gate PASS is claimed. The authoritative complete-gate pin remains `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`.

Permitted LAB-095 fallback then performed a fresh static audit of the exact recovery/tamper target on PR #187. The recovery suite still explicitly covers crash-before-commit rollback, orphan CONFIRMED rejection before nonce generation, concurrent-installer convergence, and exact next-position reservation after legacy CONFIRMED history. The confirmed-finalize regression still requires the authenticated 11-field ledger tuple to remain unchanged through the final `BEGIN IMMEDIATE`, and `_classify_locked()` still recomputes canonical custody payload identity before accepting PREPARED/CONFIRMED state. No new production defect was identified by this static pass; no behavioral PASS is claimed from inspection alone.

An exact eight-file materialization manifest was recorded for the next focused executable gate. Durable report: `research/2026-09-14-lab095-recovery-suite-static-audit-and-materialization-manifest.md`, main commit `566903ecbf407494b805ba6e3cbb14f8e2eb8eaa`.

Previously established exact evidence remains valid: the 10-file closure for `test_database_identity_rotation_reauthentication.py` was verified 10/10 by Git blob SHA, compileall passed, and the regression passed 1/1; the exact `CanonicalDatabaseBinding` object.__new__ regression passed 1/1.

## Known failures / blockers
- LAB-086 complete real-ledger gate remains unexecuted because shell/raw GitHub transport cannot resolve GitHub and no safe automatic byte-preserving bulk connector -> executable-filesystem mount is exposed in this run.
- SQLite tests in this runtime must use a journal-capable filesystem; `/dev/shm` is observed working while ordinary temp paths previously failed default journaling.
- PRs #165/#172/#173/#175/#177/#186/#187 remain draft until retained exact gates execute.
- LAB-095 COMPLETE cross-generation reauth and object.__new__ binding are GREEN, but confirmed-finalize/recovery/tamper suite, full DB-A/B regression, and downstream LAB-080/LAB-081/LAB-090/LAB-092 gates remain incomplete.
- LAB-090/LAB-095 `supported.py` conflict resolution is security-sensitive: preserve `CanonicalDatabaseBinding` on both supported ledger/history MROs.
- LAB-094 bootstrap authority and LAB-096 provider-history strategy authority remain distinct follow-ups.

## Exact next action
LAB-086 first: attempt the complete gate only from authoritative executable pin `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`. Use connector exact content -> isolated filesystem -> `git hash-object` only if every required file can be reconstructed without truncation/manual reserialization risk. If a safe byte-preserving bulk materialization path becomes available, reconstruct/hash-verify the full closure and execute every LAB-086 real-schema `test_*.py`, the unsafe legacy-promotion expected-failure seed and compileall.

If the complete LAB-086 closure remains impractical, reconstruct the eight-file LAB-095 recovery/tamper closure recorded in `research/2026-09-14-lab095-recovery-suite-static-audit-and-materialization-manifest.md`; verify every file by Git blob SHA, run compileall, then execute `test_database_identity_migration_recovery.py`, `red_intent_lab095_confirmed_finalize_reauthentication.py`, and `red_intent_lab095_locked_custody_payload_tamper.py` with `TMPDIR=/dev/shm`. After actual GREEN evidence, execute the full DB-A -> DB-B lifetime-binding regression, LAB-080/LAB-081/LAB-090/LAB-092 focused/downstream gates, and a fresh conflict/security audit. Keep PR #187 draft until those gates are actual GREEN evidence.

Never replace external authenticated authority with deterministic test vectors, caller-supplied nonce/digest, path hashes, or same-DB self-asserted identifiers.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; authoritative complete-gate pin `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`; exact executable gate pending.
- #180 / LAB-095 — IN_PROGRESS; cross-generation COMPLETE reauth 1/1 PASS and object.__new__ binding 1/1 PASS; eight-file recovery/tamper exact execution next.
- #167 / LAB-088, #169 / LAB-090, #170 / LAB-091, #176 / LAB-092 — retained draft gates pending.
- #178..185 / LAB-093..100 — remaining architecture/security follow-ups.
- #184 / LAB-099 — PREPARED authority waits on LAB-095 completion.
