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
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected open issues and active PRs; resumed the mandatory LAB-086 probe before LAB-095 fallback work.

LAB-086 direct shell Git materialization still fails before repository execution with `Could not resolve host: github.com`, exit 128. No byte-exact LAB-086 requirement was weakened and no new complete-gate PASS is claimed.

### LAB-086 durable pin reconciliation
The authoritative exact-gate manifest was re-read and the durable control-plane drift was corrected. The remaining complete branch-local LAB-086 gate is pinned to:

`1fa85a0e34c9ae67da57f1e64dadccf211feacc0`

This supersedes old executable pin `1f90830fca21e2f43fc241012cdd34fd187ba96d` because exact execution exposed a stale test-only schema in `test_thaw_history_key_collision_regression.py`; the LAB-086 runtime hardening in `strict_fence.py` is unchanged from the old pin.

The connector can read the recursive tree and exact UTF-8 blobs for `1fa85a0e...`, but the complete gate requires the full branch-local LAB-080 -> LAB-086 real-ledger dependency chain plus every `test_*.py` under `experiments/asymmetric_break_glass_history/tests`, the unsafe expected-failure seed and compileall. This run exposes no automatic byte-preserving connector-blob -> executable-filesystem mount. Manual reconstruction of that large closure would introduce truncation/reserialization risk, so no partial execution was represented as the complete LAB-086 gate.

Durable report: `research/2026-09-14-lab086-pin-control-plane-reconciliation.md`, main commit `aa110b1fcee9dcf24c60cded124b4d324313274c`.

### LAB-095 retained recovery suite audit
PR #187 head remains `835a81914c5234e68ef436e30c9837331d262432`. The committed recovery suite was re-read and contains the retained crash-before-commit rollback, orphan CONFIRMED-before-nonce rejection, concurrent installer convergence, and legacy-prefix next-position reservation cases. Their committed presence is not behavioral PASS evidence; exact execution remains pending.

A fresh GitHub PR metadata read reported #187 open/draft and currently mergeable/clean. Keep draft until retained exact/downstream gates and a fresh security/conflict audit are complete.

Previously established exact evidence remains valid: for PR #187 head `835a81914c5234e68ef436e30c9837331d262432`, the 10-file closure for `test_database_identity_rotation_reauthentication.py` was verified 10/10 by Git blob SHA, compileall passed, and `TMPDIR=/dev/shm python -m unittest -v experiments.provider_generation_history.tests.test_database_identity_rotation_reauthentication` passed 1/1.

## Known failures / blockers
- LAB-086 complete real-ledger gate remains unexecuted because shell/raw GitHub transport cannot resolve GitHub and the connector does not provide an automatic byte-preserving executable-filesystem mount for the large pinned closure.
- SQLite tests in this runtime must use a journal-capable filesystem; `/dev/shm` is observed working while `/tmp`, `/mnt/data`, and `/home/oai/share` fail default journaling.
- PRs #165/#172/#173/#175/#177/#186/#187 remain draft until their retained exact gates execute.
- LAB-095 COMPLETE cross-generation reauth gate is GREEN, but confirmed-finalize/recovery/tamper suite, DB-A/B regression, and downstream LAB-080/LAB-081/LAB-090/LAB-092 gates remain unexecuted against verified closures.
- LAB-090/LAB-095 `supported.py` conflict resolution is security-sensitive: preserve `CanonicalDatabaseBinding` on both supported ledger/history MROs.
- LAB-094 bootstrap authority and LAB-096 provider-history strategy authority remain distinct follow-ups.

## Exact next action
LAB-086 first: attempt the complete gate only from authoritative executable pin `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`. Use connector exact content -> isolated filesystem -> `git hash-object` only if every required file can be reconstructed without truncation/manual reserialization risk. If a safe byte-preserving bulk materialization path becomes available, reconstruct and hash-verify the complete pinned closure, then execute every `test_*.py` under `experiments/asymmetric_break_glass_history/tests`, the unsafe expected-failure seed and compileall (using `/dev/shm` for SQLite temp state where needed).

If the complete LAB-086 closure remains impractical in one safe run, continue LAB-095 on PR #187 using verified small closures:
1. materialize and hash-verify the committed COMPLETE-reauthentication and confirmed-finalize/tamper/recovery regression closure(s);
2. execute crash-before-commit + orphan/partial + concurrent-installer + legacy-prefix + locked-custody/confirmed-finalize tamper regressions with `TMPDIR=/dev/shm`;
3. execute the committed DB-A -> DB-B lifetime-binding regression;
4. run LAB-080/LAB-081/LAB-090/LAB-092 focused/downstream gates and a fresh conflict/security audit;
5. keep PR #187 draft until those gates are actual GREEN evidence.

Never replace external authenticated authority with deterministic test vectors, caller-supplied nonce/digest, path hashes, or same-DB self-asserted identifiers.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; authoritative complete-gate pin `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`; exact executable gate pending.
- #180 / LAB-095 — IN_PROGRESS; cross-generation COMPLETE reauthentication exact gate 1/1 PASS; recovery/tamper/DB-A-B/downstream execution next.
- #167 / LAB-088, #169 / LAB-090, #170 / LAB-091, #176 / LAB-092 — retained draft gates pending.
- #178..185 / LAB-093..100 — remaining architecture/security follow-ups.
- #184 / LAB-099 — PREPARED authority waits on LAB-095 completion.
