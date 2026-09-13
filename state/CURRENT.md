# Current Lab State

Last updated: 2026-09-13

## Active objective
LAB-086 remains priority #1: finish the exact executable/security gate for asymmetric break-glass history migration. When byte-exact LAB-086 execution cannot be materialized safely, LAB-095/#180 is the permitted fallback prerequisite. LAB-099 PREPARED authority waits on LAB-095 authenticated logical database/history identity.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165. Keep draft.
- LAB-095 prerequisite: #180 / branch `lab-095-database-identity-red-intent` / draft PR #187, head `092ebf04fef20558256af80dff0bfd117ca79ab8`; mergeable, still draft.
- LAB-099: #184 / draft PR #186; PREPARED authority remains blocked on LAB-095.
- Retained drafts: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175; LAB-092/#176 PR #177.

## Last completed step
Re-read `AGENTS.md`, this handoff, `prompts/SELF_RESUME.md`, issue #180, and active PR state. Re-probed LAB-086 first; direct clone again failed before repository execution with `Could not resolve host: github.com` / exit 128. No LAB-086 gate was weakened and no new LAB-086 PASS is claimed.

### LAB-095 explicit migration/recovery slice
PR #187 now contains production `experiments/provider_generation_history/database_identity_migration.py`:
- production commit `5f0e2576798f069eeadeedc2ca808439c613750b`;
- published/audited blob `9f3d3a9c31ffa45939393df67e624cd003b09475`;
- regression commit/head `092ebf04fef20558256af80dff0bfd117ca79ab8`;
- regression blob `be85be6534b24f24d3a664332377ade6696019ac`.

Implemented behavior:
- ledger/history paths must resolve to the same DB at migration time;
- existing provider history is verified and current provider/generation checked;
- `BEGIN IMMEDIATE` is acquired before deciding installation is absent;
- bootstrap/current provider-history head are re-read under the same writer lock, closing the supported rotation TOCTOU window found during audit;
- exactly 32 random bytes are generated internally via `secrets.token_bytes(32)` only for a true absent state;
- custody + deterministic PREPARED shared-anchor identity intent + reserved-tail advance commit atomically;
- PREPARED retry reuses the persisted nonce/request and never creates a second identity request;
- external increment/reconciliation/CONFIRMED authentication remains delegated to existing `SharedAnchorLedger.execute()`;
- confirmed restart reconstructs the same Intent from persisted custody, allowing existing shared-anchor logic to reauthenticate before local finalization;
- local identity digest finalization uses only persisted CONFIRMED provider generation, position, request ID, and receipt binding.

Focused file-backed SQLite execution of the exact published migration source with narrow stand-ins for already-inspected interfaces: fresh/retry/finalize PASS; confirmed-restart same-custody PASS; path-divergence rejection PASS; provider-head TOCTOU rejection PASS. Production and regression `py_compile` PASS. The local production and test blobs matched the published Git blobs after exact-text verification.

Durable evidence:
- `research/2026-09-13-lab095-explicit-identity-migration-recovery.md`, main commit `c4173fa15204ea49e81dc5f67c861913c68c8b8a`;
- issue #180 comment `5653830937`;
- issue #163 comment `5653831459`;
- PR #187 description updated to current production state.

This is not a full exact-repository LAB-095 GREEN. Complete repository closure and LAB-080/081/090/092 downstream gates were not materialized in this runtime.

## Known failures / blockers
- LAB-086 exact complete real-ledger gate remains unexecuted because direct git transport cannot resolve `github.com`; do not manually reconstruct the 50+ file closure or weaken byte-exact evidence requirements.
- PRs #165/#172/#173/#175/#177/#186/#187 remain draft until their retained exact gates execute.
- LAB-095 original lifetime-binding acceptance criterion is still open: `DurableProviderHistory.path` and `SharedAnchorLedger.path` remain public/mutable after construction.
- PR #187 now has explicit identity installation/recovery, but exact repository crash/concurrency/legacy regressions and downstream gates remain pending.
- LAB-099 migration/resume must not derive authority from `tests/lab095_*` or LAB-099 fixtures.

## Exact next action
LAB-086 first: re-probe for a supported byte-preserving materialization path. If available, reconstruct only executable pin `1f90830fca21e2f43fc241012cdd34fd187ba96d`, require local `git hash-object` match for every manifest/test/helper/transitive file, then run the full retained LAB-086 gate including unsafe expected-failure separately, compileall, security/reconciliation, and current-main conflict audit.

If exact LAB-086 materialization is still unavailable, continue LAB-095 on PR #187 with the original lifetime DB-binding acceptance criterion:
1. inspect all `self.path` consumers across `SharedAnchorLedger`, `DurableProviderHistory`, historical integration, LAB-090 activation fencing, and LAB-092 provenance;
2. design the smallest non-rebindable/private canonical DB reference shared by composed ledger/history objects without breaking inheritance/restart semantics;
3. add DB-A -> DB-B regressions proving public-state rebinding cannot redirect reserve/execute/rotate/verify, including DB B with superficially matching current head but invalid full history;
4. add remaining exact crash-before-commit/partial-state/concurrent-installer/legacy-history regressions for the migration slice where the real stack exposes gaps;
5. run LAB-080/LAB-081/LAB-090/LAB-092 focused/downstream gates before integration;
6. only after LAB-095 is complete, return to LAB-099 authenticated PREPARED authority.

Never use deterministic test vectors, caller-supplied nonce/digest, filesystem path hashes, or a same-DB self-asserted UUID as production authority.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact executable gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #180 / LAB-095 — IN_PROGRESS on draft PR #187; custody/classifier + explicit migration/recovery published; immutable physical binding + full retained gates next.
- #178..185 / LAB-093..100 — remaining architecture/security follow-ups with executable gates pending.
- #184 / LAB-099 — classifier/startup slice published; PREPARED authority waits on LAB-095 completion.
