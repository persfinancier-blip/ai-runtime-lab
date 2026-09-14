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
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected open issues and active PRs; resumed LAB-095 after the mandatory LAB-086 probe.

LAB-086 was probed first. Direct shell Git materialization still fails before repository execution with `Could not resolve host: github.com`, exit 128. No byte-exact LAB-086 requirement was weakened and no new LAB-086 PASS is claimed.

### LAB-095 safe byte-preserving fallback + cross-generation gate — EXECUTED
A safe small-closure connector -> executable-filesystem fallback was established in this runtime:

`connector exact UTF-8 content + published blob SHA -> isolated write -> git hash-object equality -> execution only after every required file matches`.

For PR #187 head `835a81914c5234e68ef436e30c9837331d262432`, the 10-file dependency closure required by `test_database_identity_rotation_reauthentication.py` was materialized and verified **10/10 Git blob SHA PASS**. `python -m compileall -q experiments` also PASS.

A first execution failed before LAB-095 semantics because this runtime's filesystem does not support SQLite default journaling on `/tmp`, `/mnt/data`, or `/home/oai/share` (`sqlite3.OperationalError: disk I/O error`). An independent minimal SQLite probe showed `/dev/shm` supports normal create/insert/commit. No source or SQLite behavior was monkeypatched; the unchanged test was rerun only with `TMPDIR=/dev/shm` so `tempfile.TemporaryDirectory()` used the journal-capable filesystem.

Exact focused result: `TMPDIR=/dev/shm python -m unittest -v experiments.provider_generation_history.tests.test_database_identity_rotation_reauthentication` -> **1/1 PASS**.

This proves on the verified focused closure that COMPLETE identity reauthentication survives legitimate g1->g2 provider rotation through persisted signed historical receipt evidence and fails closed with `HistoricalVerificationError` after that exact receipt is deleted.

Durable report: `research/2026-09-14-lab095-byte-exact-rotation-regression-execution.md`, main commit `13a8ca92735d4d9686a83423ba5223178a3c4ca5`; #180 comment `5658546428`; PR #187 comment `5658547010`.

PR #187 metadata observed after this run: open, draft, head unchanged; connector currently reports `mergeable=false`. Do not integrate until the retained gates and a fresh conflict/security audit are complete.

## Known failures / blockers
- LAB-086 exact complete real-ledger gate remains unexecuted because shell/raw GitHub transport cannot resolve GitHub. The new connector->filesystem fallback is proven only for small UTF-8 closures; applying it to LAB-086 requires reconstructing and hash-verifying the complete pinned closure before execution.
- SQLite tests in this runtime must use a journal-capable filesystem; `/dev/shm` is currently observed working while `/tmp`, `/mnt/data`, and `/home/oai/share` fail default journaling.
- PRs #165/#172/#173/#175/#177/#186/#187 remain draft until their retained exact gates execute.
- LAB-095 COMPLETE cross-generation reauth gate is now GREEN, but confirmed-finalize/recovery/tamper suite, DB-A/B regression, and downstream LAB-080/LAB-081/LAB-090/LAB-092 gates remain unexecuted against verified closures.
- LAB-090/LAB-095 `supported.py` conflict resolution is security-sensitive: preserve `CanonicalDatabaseBinding` on both supported ledger/history MROs.
- LAB-094 bootstrap authority and LAB-096 provider-history strategy authority remain distinct follow-ups.

## Exact next action
LAB-086 first: use the now-proven connector exact-content -> isolated filesystem -> `git hash-object` method to determine whether the complete executable pin `1f90830fca21e2f43fc241012cdd34fd187ba96d` closure can be reconstructed without truncation/manual reserialization risk. If every required file can be obtained exactly and hash-verified, run the retained full LAB-086 gate (using `/dev/shm` for SQLite temp state where needed).

If the complete LAB-086 closure is still impractical in one safe run, continue LAB-095 on PR #187 using the same verified materialization method:
1. materialize and hash-verify the committed COMPLETE-reauthentication and confirmed-finalize/tamper/recovery regression closure(s);
2. execute crash-before-commit + orphan/partial + concurrent-installer + legacy-prefix + locked-custody/confirmed-finalize tamper regressions with `TMPDIR=/dev/shm`;
3. execute the committed DB-A -> DB-B lifetime-binding regression;
4. run LAB-080/LAB-081/LAB-090/LAB-092 focused/downstream gates and a fresh conflict/security audit;
5. keep PR #187 draft until those gates are actual GREEN evidence.

Never replace external authenticated authority with deterministic test vectors, caller-supplied nonce/digest, path hashes, or same-DB self-asserted identifiers.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact executable gate pending.
- #180 / LAB-095 — IN_PROGRESS; cross-generation COMPLETE reauthentication exact gate 1/1 PASS; recovery/tamper/DB-A-B/downstream execution next.
- #167 / LAB-088, #169 / LAB-090, #170 / LAB-091, #176 / LAB-092 — retained draft gates pending.
- #178..185 / LAB-093..100 — remaining architecture/security follow-ups.
- #184 / LAB-099 — PREPARED authority waits on LAB-095 completion.
