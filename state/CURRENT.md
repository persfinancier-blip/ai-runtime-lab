# Current Lab State

Last updated: 2026-09-13

## Active objective
LAB-086 remains priority #1: finish the exact executable/security gate for asymmetric break-glass history migration. When byte-exact LAB-086 execution cannot be materialized safely, LAB-095/#180 is the permitted fallback prerequisite. LAB-099 PREPARED authority waits on LAB-095 authenticated logical database/history identity plus lifetime physical DB binding.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165. Keep draft.
- LAB-095: #180 / branch `lab-095-database-identity-red-intent` / draft PR #187, current head `37d93619ecca9af20c935cc6b1dcd60f37cece72`. Keep draft.
- LAB-099: #184 / draft PR #186; PREPARED authority remains blocked on LAB-095.
- Retained drafts: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175; LAB-092/#176 PR #177.

## Last completed step
Re-read `AGENTS.md`, this handoff, `prompts/SELF_RESUME.md`, open issues/PRs, and re-probed LAB-086 first. Direct clone again failed before repository execution with `Could not resolve host: github.com` / exit 128. No LAB-086 gate was weakened and no new LAB-086 PASS is claimed.

### LAB-095 constructor/MRO integration audit
Source-audited retained LAB-090 PR #175 and LAB-092 PR #177 against PR #187's `CanonicalDatabaseBinding`.

Findings:
- LAB-090 rewrites `experiments/provider_generation_history/supported.py`, the same supported surface modified by LAB-095. Eventual conflict resolution MUST preserve `CanonicalDatabaseBinding` in both supported ledger/provider-history MROs or the mutable-path finding reopens.
- LAB-092 deliberately uses `object.__new__` followed by the first manual `path` assignment in `_reservation_surface()` and `_bind_live_provider_history_provenance()`. This is compatible with the one-assignment binding contract only when that MRO is preserved.
- Added `test_database_binding_object_new_surface.py`, blob `25cd1d53fece40ab71a78ff4838381950505ce0d`, to freeze this construction idiom.
- Exact published binding blob `c6bf05b3a5579e076142300aefbc9d785cc6354a` + exact test blob were locally reconstructed and verified with `git hash-object`; focused unittest PASS 1/1.
- Full LAB-090/LAB-092/downstream GREEN is NOT claimed.

Durable report: `research/2026-09-13-lab095-lab090-lab092-binding-integration-audit.md`, main commit `d284388ed9349ba305d3ad16b5130391408e3f2c`; #180 comment `5654496396`; PR #187 comment `5654497076`.

### LAB-095 under-lock durable-history gap
Audited `database_identity_migration.py` and found a TOCTOU trust gap: full `history.verify_durable()` runs before the writer lock, but inside `BEGIN IMMEDIATE` production rechecks only bootstrap generation id plus head generation/provider. Historical transition/verification material could change after the precheck while those shallow fields remain unchanged.

Added RED-intent `red_intent_lab095_under_lock_history_verification.py`, blob `42f7ea0c8d00ce01d68db27f2d93b7d50ddc31cd`. Required fix: before nonce generation or reservation, invoke the existing full integrated durable-history verifier on the SAME locked SQLite connection and cross-check its verified current descriptor against runtime/pre-lock authority. Any failure must roll back with zero shared-anchor/custody mutation.

The RED test is committed but not claimed behaviorally executed because the exact repository dependency closure was not safely materialized. Source audit confirms current production does not call `_verify_durable_locked`.

Durable report: `research/2026-09-13-lab095-under-lock-full-history-reverification-gap.md`, main commit `06ce5dc4fafdd27904b7f549aabe880b30713432`; #180 comment `5654506073`.

Earlier LAB-095 production remains on PR #187: logical identity/custody classifier, explicit CSPRNG/BEGIN IMMEDIATE migration/recovery, same-request reconciliation, local confirmed finalization, and construction-bound physical path binding with DB-A -> DB-B regression committed.

## Known failures / blockers
- LAB-086 exact complete real-ledger gate remains unexecuted because shell git transport cannot resolve `github.com`; do not manually reconstruct the 50+ file closure or weaken byte-exact evidence requirements.
- PRs #165/#172/#173/#175/#177/#186/#187 remain draft until retained exact gates execute.
- LAB-095 full DB-A/B regression and downstream LAB-080/LAB-081/LAB-090/LAB-092 gates remain unexecuted.
- LAB-095 migration still needs production fix + GREEN for the under-lock full-history recheck, then crash-before-commit/partial-state/concurrent-installer/legacy-history regressions.
- LAB-090/LAB-095 supported.py conflict resolution is security-sensitive: binding MRO must not be dropped.
- LAB-094 bootstrap authority and LAB-096 provider-history strategy authority remain distinct follow-ups.
- LAB-099 migration/resume must not derive authority from `tests/lab095_*` or LAB-099 fixtures.

## Exact next action
LAB-086 first: re-probe for a supported byte-preserving materialization path. If available, reconstruct only executable pin `1f90830fca21e2f43fc241012cdd34fd187ba96d`, require local `git hash-object` match for every manifest/test/helper/transitive file, then run the full retained LAB-086 gate including unsafe expected-failure separately, compileall, security/reconciliation, and current-main conflict audit.

If exact LAB-086 materialization is still unavailable, continue LAB-095 on PR #187:
1. fix `prepare_database_identity()` so the existing full integrated provider-history verifier runs inside the SAME `BEGIN IMMEDIATE` transaction before nonce generation/reservation; compare the locked verified current descriptor with runtime/pre-lock authority;
2. execute the new under-lock RED plus existing migration focused regressions on the smallest exact closure that can be safely materialized; do not claim broader GREEN;
3. add crash-before-commit, partial-state, concurrent-installer, and legacy-history migration regressions;
4. execute `test_database_path_binding.py` and LAB-080/LAB-081/LAB-090/LAB-092 focused/downstream gates when exact closure is available;
5. during eventual LAB-090/LAB-095 conflict resolution, preserve `CanonicalDatabaseBinding` on both supported ledger/history MROs;
6. only after LAB-095 completion return to LAB-099 authenticated PREPARED authority.

Never use deterministic test vectors, caller-supplied nonce/digest, filesystem path hashes, or a same-DB self-asserted UUID as production authority.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact executable gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #180 / LAB-095 — IN_PROGRESS on draft PR #187; current next fix is under-lock full durable-history reverification.
- #178..185 / LAB-093..100 — remaining architecture/security follow-ups with executable gates pending.
- #184 / LAB-099 — classifier/startup slice published; PREPARED authority waits on LAB-095 completion.
