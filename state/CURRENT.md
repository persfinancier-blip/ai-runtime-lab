# Current Lab State

Last updated: 2026-09-13

## Active objective
LAB-086 — finish the exact executable/security gate for asymmetric break-glass history migration, then reconcile/merge only if every real-schema regression and current-main conflict audit passes.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165. Keep draft.
- LAB-092: #176 / draft PR #177, pinned head `81673f8f6e4e0864dfa124735938c40aa28b4f2c`.
- LAB-099 fallback: #184 / branch `lab-099-precursor-cutover-red-intent` / draft PR #186, head `766434563a5ad82a88156687c84de9c9e17b14c6`, based on PR #177.
- Other retained drafts: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175.

## Last completed step
Re-read `AGENTS.md`, this handoff, `prompts/SELF_RESUME.md`, open issues and PR state; resumed LAB-086 first.

Recovered the exact LAB-086 gate manifest from commit `1fa85a0e34c9ae67da57f1e64dadccf211feacc0` and corrected a durable pin ambiguity: `1fa85a0...` is a later notes/evidence commit, while the manifest explicitly pins executable source at `1f90830fca21e2f43fc241012cdd34fd187ba96d`. Do not execute a mixed snapshot.

Current-run LAB-086 evidence:
- fresh direct clone again failed before repository execution with `Could not resolve host: github.com` (exit 128); this is transport evidence only;
- GitHub Git-data/Contents reads at executable pin `1f90830...` succeeded;
- pinned target blobs confirmed: `protocol.py=cccb531fa13b8f8d4e3a7c3163dd7c7cbeb3ec41`, `migration_guard.py=1a9209b16fdb2c3dcae8e4690658a030040f6ca2`, `strict_fence.py=d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`, `suffix.py=44847bde53b9f7b0e2fbcbab37d36dc992f497b2`, `final_supported.py=ceb7f48a55a931ba9923cac77d4ebf6c4cd2cfec`;
- pinned LAB-086 tests tree is `ccd38ad88bd1be94fc78b2929e7938d6fa315b6f`; NULL-receipt regression is `a66d9ddef2d4a41db937222b875f697c7ff74b75`;
- connector `fetch_file` supports bounded line ranges, so large UTF-8 blobs can be reconstructed deterministically and admitted only after local `git hash-object` equals the pinned blob SHA;
- focused SQLite reprobe of the exact pinned provider-receipt predicate denied post-cutoff NULL request ID, allowed a genuinely new non-NULL ID, and denied `INSERT OR REPLACE` collision;
- this is focused semantic evidence only. No new LAB-086 full unittest/security/compile/conflict PASS is claimed because the entire byte-exact closure has not yet been reconstructed and executed.

Durable LAB-086 evidence:
- `research/2026-09-13-lab086-executable-pin-and-focused-receipt-reprobe.md`, main commit `8d4a5d4061db2e3b6f789983f028ff5dc65817b5`;
- #163 comment `5652187603` records the corrected executable pin, exact tree/blob observations, transport failure, and focused semantic reprobe.

Retained LAB-099 evidence from the prior completed fallback slice:
- all 18 frozen orchestration files were previously materialized byte-exact; compileall and fresh file-backed SQLite orchestration were GREEN with the frozen request/receipt/position/head identities and final durable verification;
- exact LAB-099 RED then ran 6 tests / 6 failures solely because production module `experiments.provider_generation_history.activation_reservation_provenance` does not exist;
- production LAB-099 is now allowed by its RED gate, but remains lower priority than LAB-086 and may not derive production authority from test-only vectors/witnesses.

## Known failures / blockers
- LAB-086 exact complete real-ledger gate remains unexecuted.
- Direct clone/network transport remains unavailable in the observed runtime; use the supported GitHub connector as source of exact pinned blobs and verify every reconstructed file locally by Git hash.
- PR #165 remains draft and must not be integrated without the exact gate and fresh conflict audit.
- PRs #172/#173/#175/#177/#186 remain draft until their retained exact gates execute.
- LAB-099 historical synthetic CONFIRMED head `c0..df` remains non-authoritative; exact CONFIRMED bridge and dynamic PREPARED fixture remain intentionally distinct authority layers.

## Exact next action
LAB-086 first. Use executable pin `1f90830fca21e2f43fc241012cdd34fd187ba96d` as the only source snapshot. Reconstruct the manifest-listed implementation closure, every `test_*.py` under `experiments/asymmetric_break_glass_history/tests`, `unsafe_legacy_promotion_expected_failure.py`, the pinned LAB-085 helper used by LAB-086 integration fixtures, and all transitive experiment dependencies reached by those tests. Use connector `fetch_file` line ranges for large files where needed. Write into an isolated local tree and accept **no file** unless local `git hash-object` equals its pinned Git blob SHA.

Only after 100% closure hash match: run all normal LAB-086 tests from the pinned snapshot; run `unsafe_legacy_promotion_expected_failure.py` separately and require its intended failure; run downstream/helper tests and `python -m compileall`; source-audit `*_for_test_only`; then perform final security/reconciliation and current-main conflict audit. Fix every observed blocker before changing PR #165 draft/merge status.

If a specific connector/API inconsistency prevents byte-exact reconstruction after reasonable line-ranged fallbacks, persist the exact missing path/blob and return to LAB-099 rather than weakening the LAB-086 gate. For LAB-099, derive the smallest production `activation_reservation_provenance` authority model independently of `tests/lab099_*` and let the observed six-case RED drive the next minimal implementation.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact executable pin clarified as `1f90830...`, byte-exact complete gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178..185 / LAB-093..100 — design/source follow-ups with executable gates pending.
- #184 / LAB-099 — orchestration GREEN and first production RED observed; production implementation permitted by RED but behind LAB-086 priority.
