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

Permitted LAB-095 fallback then reconstructed and `git hash-object` verified 6/8 files from the focused recovery/tamper manifest at PR #187 head `835a819...`: exact production `database_identity.py` and `database_identity_migration.py`, exact helper migration test, exact recovery test, exact confirmed-finalize reauthentication test, and exact locked-custody tamper test. A controlled minimal local `shared_anchor_intent_ledger.protocol` stub supplied only `Intent`, `LedgerEntry`, and `_request_id`; `anchor_attestation.protocol` was not exercised through that stubbed import path.

`compileall` passed and the three focused target modules executed on `/dev/shm`: **6/6 PASS**. Covered crash-before-commit rollback, orphan CONFIRMED rejection before nonce generation, concurrent installer convergence, exact legacy-tail next-position reservation, post-reauthentication 11-field tuple tamper rejection, and PREPARED custody nonce-tamper rejection. This is behavioral evidence but **not** the complete 8/8 byte-exact closure because the two protocol dependencies were not reconstructed exactly.

Durable report: `research/2026-09-14-lab095-recovery-tamper-partial-exact-execution.md`, main commit `0bd890192922d69b39eb01882f1e8c46b259612d`. #180 and PR #187 were updated.

Previously established exact evidence remains valid: the 10-file closure for `test_database_identity_rotation_reauthentication.py` was verified 10/10 by Git blob SHA, compileall passed, and the regression passed 1/1; the exact `CanonicalDatabaseBinding` object.__new__ regression passed 1/1.

## Known failures / blockers
- LAB-086 complete real-ledger gate remains unexecuted because shell/raw GitHub transport cannot resolve GitHub and no safe automatic byte-preserving bulk connector -> executable-filesystem mount is exposed in this run.
- SQLite tests in this runtime must use a journal-capable filesystem; `/dev/shm` is observed working while ordinary temp paths previously failed default journaling.
- PRs #165/#172/#173/#175/#177/#186/#187 remain draft until retained exact gates execute.
- LAB-095 COMPLETE cross-generation reauth and object.__new__ binding are GREEN; recovery/tamper behaviors are 6/6 PASS with exact LAB-095 production/test blobs but two protocol dependencies were stubbed. Complete 8/8 no-stub closure, full DB-A/B regression, and downstream LAB-080/LAB-081/LAB-090/LAB-092 gates remain incomplete.
- LAB-090/LAB-095 `supported.py` conflict resolution is security-sensitive: preserve `CanonicalDatabaseBinding` on both supported ledger/history MROs.
- LAB-094 bootstrap authority and LAB-096 provider-history strategy authority remain distinct follow-ups.

## Exact next action
LAB-086 first: attempt the complete gate only from authoritative executable pin `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`. Use connector exact content -> isolated filesystem -> `git hash-object` only if every required file can be reconstructed without truncation/manual reserialization risk. If a safe byte-preserving bulk materialization path becomes available, reconstruct/hash-verify the full closure and execute every LAB-086 real-schema `test_*.py`, the unsafe legacy-promotion expected-failure seed and compileall.

If the complete LAB-086 closure remains impractical, finish the focused LAB-095 manifest by reconstructing exact `experiments/shared_anchor_intent_ledger/protocol.py` blob `68834409363c93eee4e9a9a7b9ec076098af0acf` and exact `experiments/anchor_attestation/protocol.py` blob `15d8b7cf8ff093490ccb75679030d3a0fe41e401`; require 8/8 `git hash-object` matches and rerun the same six recovery/tamper tests with no stubs under `TMPDIR=/dev/shm`. After actual no-stub GREEN evidence, execute the full DB-A -> DB-B lifetime-binding regression, LAB-080/LAB-081/LAB-090/LAB-092 focused/downstream gates, and a fresh conflict/security audit. Keep PR #187 draft until those gates are actual GREEN evidence.

Never replace external authenticated authority with deterministic test vectors, caller-supplied nonce/digest, path hashes, or same-DB self-asserted identifiers.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; authoritative complete-gate pin `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`; exact executable gate pending.
- #180 / LAB-095 — IN_PROGRESS; cross-generation COMPLETE reauth 1/1 PASS, object.__new__ binding 1/1 PASS, recovery/tamper 6/6 PASS on exact LAB-095 production/test blobs with two protocol stubs; complete 8/8 no-stub rerun next.
- #167 / LAB-088, #169 / LAB-090, #170 / LAB-091, #176 / LAB-092 — retained draft gates pending.
- #178..185 / LAB-093..100 — remaining architecture/security follow-ups.
- #184 / LAB-099 — PREPARED authority waits on LAB-095 completion.
