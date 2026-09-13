# Current Lab State

Last updated: 2026-09-13

## Active objective
LAB-086 remains priority #1: finish the exact executable/security gate for asymmetric break-glass history migration. When byte-exact LAB-086 execution cannot be materialized safely, LAB-095/#180 is the permitted fallback prerequisite. LAB-099 PREPARED authority waits on LAB-095 authenticated logical database/history identity plus lifetime physical DB binding.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165. Keep draft.
- LAB-095: #180 / branch `lab-095-database-identity-red-intent` / draft PR #187, current head `ac16e417cea6bfb930cb38e1755d205926c083a9`, mergeable=true at last check. Keep draft.
- LAB-099: #184 / draft PR #186; PREPARED authority remains blocked on LAB-095.
- Retained drafts: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175; LAB-092/#176 PR #177.

## Last completed step
Re-read `AGENTS.md`, this handoff, `prompts/SELF_RESUME.md`, and inspected open issues/PR #187. LAB-086 was re-probed first: direct clone again failed before repository execution with `Could not resolve host: github.com` / exit 128. No LAB-086 gate was weakened and no new LAB-086 PASS is claimed.

### LAB-095 recovery regression + orphan-intent fix
Added `test_database_identity_migration_recovery.py` to PR #187 with contracts for:
1. crash-before-commit rollback of custody DDL/intent/tail;
2. orphan CONFIRMED identity intent without custody failing before nonce generation;
3. two concurrent installers converging on one nonce/request/PREPARED reservation;
4. legacy shared-anchor prefix reserving exactly the next position.

Regression commit: `884d7ea40d60cf5e5f8c2cb8a25a730240aff3ac`.

Audit found a production fail-closed gap: migration `_classify_locked()` treated zero custody rows as `ABSENT` without checking for an already-existing reserved LAB-095 identity intent. An orphan CONFIRMED identity intent could therefore trigger a fresh CSPRNG nonce before duplicate-intent failure.

Fixed on PR #187: zero custody + existing `IDENTITY_INTENT_ID` now classifies `CORRUPT`; zero custody + no identity intent remains `ABSENT`. Production fix commit `ac16e417cea6bfb930cb38e1755d205926c083a9`, blob `816afb8c3e6bd96ee5ba30061f304fd104dc7a5b`.

Executed focused SQLite semantic evidence:
- empty custody/no identity intent -> ABSENT;
- empty custody/orphan CONFIRMED identity intent -> CORRUPT;
- custody DDL created after `BEGIN IMMEDIATE` disappears after rollback.

This is narrow semantic evidence only. The new repository recovery regression file has not been claimed GREEN because the exact dependency closure remains unavailable.

Durable report: `research/2026-09-13-lab095-recovery-regression-and-orphan-intent-fix.md`, main commit `11ad9b45f0a41483b4d573301e95462551d20c5c`; #180 comment `5655151115`.

Earlier LAB-095 production remains on PR #187: logical identity/custody classifier, explicit CSPRNG/BEGIN IMMEDIATE migration/recovery, same-request reconciliation, under-lock full provider-history verification, local confirmed finalization, and construction-bound physical path binding with DB-A -> DB-B regression committed.

## Known failures / blockers
- LAB-086 exact complete real-ledger gate remains unexecuted because shell git transport cannot resolve `github.com`; do not manually reconstruct the 50+ file closure or weaken byte-exact evidence requirements.
- PRs #165/#172/#173/#175/#177/#186/#187 remain draft until retained exact gates execute.
- LAB-095 full DB-A/B regression and downstream LAB-080/LAB-081/LAB-090/LAB-092 gates remain unexecuted.
- New LAB-095 crash/concurrent/legacy repository regressions are committed but not exact-closure executed.
- `database_identity.classify_identity_custody()` still returns ABSENT on zero custody rows before checking whether an orphan LAB-095 identity intent exists; this is inconsistent with the now-fixed locked migration classifier and is the next correctness fix.
- LAB-090/LAB-095 supported.py conflict resolution is security-sensitive: binding MRO must not be dropped.
- LAB-094 bootstrap authority and LAB-096 provider-history strategy authority remain distinct follow-ups.
- LAB-099 migration/resume must not derive authority from `tests/lab095_*` or LAB-099 fixtures.

## Exact next action
LAB-086 first: re-probe for a supported byte-preserving materialization path. If available, reconstruct only executable pin `1f90830fca21e2f43fc241012cdd34fd187ba96d`, require local `git hash-object` match for every manifest/test/helper/transitive file, then run the full retained LAB-086 gate including unsafe expected-failure separately, compileall, security/reconciliation, and current-main conflict audit.

If exact LAB-086 materialization is still unavailable, continue LAB-095 on PR #187:
1. add a public-classifier regression for orphan PREPARED/CONFIRMED `IDENTITY_INTENT_ID` with zero custody rows and change `classify_identity_custody()` to return CORRUPT consistently before any authority decision;
2. execute the committed crash-before-commit, partial-state, concurrent-installer, and legacy-history regressions on the smallest exact closure that can be safely materialized; require one nonce/request and deterministic same-request recovery;
3. execute `test_database_path_binding.py` and LAB-080/LAB-081/LAB-090/LAB-092 focused/downstream gates when exact closure is available;
4. run a fresh compare/conflict audit against current main and retained LAB-090 PR #175 before any integration; preserve `CanonicalDatabaseBinding` on both supported ledger/history MROs;
5. only after LAB-095 completion return to LAB-099 authenticated PREPARED authority.

Never use deterministic test vectors, caller-supplied nonce/digest, filesystem path hashes, or a same-DB self-asserted UUID as production authority.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact executable gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #180 / LAB-095 — IN_PROGRESS on draft PR #187; recovery regressions committed, orphan-intent migration classifier fixed; next is public classifier consistency then exact execution closure.
- #178..185 / LAB-093..100 — remaining architecture/security follow-ups with executable gates pending.
- #184 / LAB-099 — classifier/startup slice published; PREPARED authority waits on LAB-095 completion.
