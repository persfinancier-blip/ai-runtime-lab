# Current Lab State

Last updated: 2026-09-13

## Active objective
LAB-086 remains priority #1: finish the exact executable/security gate for asymmetric break-glass history migration. When byte-exact LAB-086 execution cannot be materialized safely, LAB-095/#180 is the permitted fallback prerequisite. LAB-099 PREPARED authority waits on LAB-095 authenticated logical database/history identity plus lifetime physical DB binding.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165. Keep draft.
- LAB-095 prerequisite: #180 / branch `lab-095-database-identity-red-intent` / draft PR #187, head `fd6d75ea35decdb719632802a538427cf51d71c7`; mergeable, still draft.
- LAB-099: #184 / draft PR #186; PREPARED authority remains blocked on LAB-095.
- Retained drafts: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175; LAB-092/#176 PR #177.

## Last completed step
Re-read `AGENTS.md`, this handoff, `prompts/SELF_RESUME.md`, open issues, PR #187, and relevant LAB-080/LAB-081 supported sources. Re-probed LAB-086 first; direct clone again failed before repository execution with `Could not resolve host: github.com` / exit 128. No LAB-086 gate was weakened and no new LAB-086 PASS is claimed.

### LAB-095 construction-bound physical DB path slice
PR #187 now additionally contains:
- `experiments/database_binding.py`, blob `c6bf05b3a5579e076142300aefbc9d785cc6354a`;
- `experiments/shared_anchor_intent_ledger/supported.py`, blob `b16fda1fd1f47ab3f333af6ac94190d6135dcf64`;
- `experiments/provider_generation_history/supported.py`, blob `7808753d7fb27c979e93f342eaf05d1e9f3f7c41`;
- `experiments/provider_generation_history/tests/test_database_path_binding.py`, blob `a7671276b4c8f6b7b3b1de507fe1ed405ee3be97`.

Implemented behavior:
- first supported-object path assignment is canonicalized with `Path.resolve(strict=False)`;
- public `path` remains readable but becomes construction-bound after that first assignment;
- direct later rebinding of the private `_canonical_database_path` source of truth is also rejected;
- `SupportedSharedAnchorLedger` now receives this binding at the supported LAB-080 boundary;
- `CoordinatorOnlyProviderHistory` receives the same binding at the supported LAB-081 provider-history boundary;
- inherited `_con()` methods therefore still consume `self.path`, but on supported objects it resolves to the immutable canonical source of truth rather than a mutable public slot.

New DB-A -> DB-B regression contract:
- construct supported historical ledger on A and rotate to generation 2;
- copy A to B;
- corrupt B's provider-transition MAC while retaining a superficially matching generation-2 head;
- attempts to reassign both ledger and provider-history paths to B must fail;
- private canonical-slot reassignment must fail;
- verify/execute must continue against A;
- B must receive no new intent and its reserved tail must remain unchanged.

Executed evidence in this runtime:
- exact published `CanonicalDatabaseBinding` source was executed independently against an inherited base whose constructor assigns and later consumes `self.path`;
- canonical first binding PASS;
- public path rebinding rejection PASS;
- private canonical-slot rebinding rejection PASS;
- continued DB-A selection PASS.

The full exact repository DB-A/B regression has NOT yet executed because the exact dependency closure was not safely materialized in this runtime. Do not count the committed regression as GREEN yet.

Durable evidence:
- `research/2026-09-13-lab095-construction-bound-database-path.md`, main commit `c09083e26228900053acd2642a3a1a220cc53c21`;
- issue #180 comment `5654177156`;
- issue #163 comment `5654177832`;
- PR #187 description updated to current state.

Earlier LAB-095 production remains on the same draft: canonical logical identity/custody classifier plus explicit migration/recovery with internal CSPRNG nonce, `BEGIN IMMEDIATE`, atomic PREPARED reservation, same-request reconciliation, under-lock provider-history recheck, and authenticated local finalization.

## Known failures / blockers
- LAB-086 exact complete real-ledger gate remains unexecuted because direct git transport cannot resolve `github.com`; do not manually reconstruct the 50+ file closure or weaken byte-exact evidence requirements.
- PRs #165/#172/#173/#175/#177/#186/#187 remain draft until their retained exact gates execute.
- LAB-095 physical binding implementation is published, but its exact repository DB-A/B regression and downstream compatibility gates remain unexecuted.
- LAB-095 migration still needs exact crash-before-commit/partial-state/concurrent-installer/legacy-history regressions.
- LAB-094 bootstrap authority and LAB-096 provider-history strategy authority remain distinct follow-ups; this path slice does not claim to close them.
- LAB-099 migration/resume must not derive authority from `tests/lab095_*` or LAB-099 fixtures.

## Exact next action
LAB-086 first: re-probe for a supported byte-preserving materialization path. If available, reconstruct only executable pin `1f90830fca21e2f43fc241012cdd34fd187ba96d`, require local `git hash-object` match for every manifest/test/helper/transitive file, then run the full retained LAB-086 gate including unsafe expected-failure separately, compileall, security/reconciliation, and current-main conflict audit.

If exact LAB-086 materialization is still unavailable, continue LAB-095 on PR #187:
1. inspect LAB-090 and LAB-092 supported constructors/MRO for repeated `path` assignment or any bypass around `SupportedSharedAnchorLedger` / `CoordinatorOnlyProviderHistory` binding;
2. execute `test_database_path_binding.py` on the exact repository closure if a safe materialization path becomes available; otherwise source-audit downstream consumers and add only narrowly justified regressions;
3. add exact crash-before-commit, partial-state, concurrent-installer, and legacy-history migration regressions where the real stack exposes gaps;
4. run LAB-080/LAB-081/LAB-090/LAB-092 focused/downstream gates before integration;
5. perform final current-main conflict/security audit;
6. only after LAB-095 is complete, return to LAB-099 authenticated PREPARED authority.

Never use deterministic test vectors, caller-supplied nonce/digest, filesystem path hashes, or a same-DB self-asserted UUID as production authority.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact executable gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #180 / LAB-095 — IN_PROGRESS on draft PR #187; custody/classifier + explicit migration/recovery + supported physical path binding published; exact DB-binding/downstream gates next.
- #178..185 / LAB-093..100 — remaining architecture/security follow-ups with executable gates pending.
- #184 / LAB-099 — classifier/startup slice published; PREPARED authority waits on LAB-095 completion.
