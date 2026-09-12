# Current Lab State

Last updated: 2026-09-12

## Active objective
LAB-086 — finish the exact executable/security gate for asymmetric break-glass history migration, then reconcile/merge only if every real-schema regression and current-main conflict audit passes.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165 at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`. Keep draft.
- Other open drafts inspected: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175; LAB-092/#176 PR #177.
- Frozen design follow-up: LAB-093/#178 plus LAB-094..100/#179..185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected open issues and active PRs; resumed LAB-086 first and re-probed exact materialization.

Current-run capability/evidence:
- Direct `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git` failed before repository execution with `Could not resolve host: github.com`.
- GitHub connector reads/writes remain available, but no supported byte-exact connector-to-local-executor materialization primitive is exposed. Manual/model reserialization of the security-critical LAB-086 closure remains prohibited.
- Therefore no new LAB-086 behavioral, unsafe-seed, compileall, security-reconciliation or conflict PASS is claimed.
- Open issues and PRs were re-inspected; PR #175 is still open/draft at `d9a381dd4607a928cd1315adef6431e239995bc1`.

Executed the recorded distinct fallback for LAB-100/#185 by auditing the actual PR #175 construction/restart source against the already frozen ActivationAuthority model.

Fresh finding:
- `SupportedHistoricalSharedAnchorLedger.__init__()` calls `_recover_pending_activation()` before `_verify_activation_records()`.
- For a current `SQL_COMMITTED` activation, `_recover_pending_activation()` can call provider `commit_activation()`, mutate coordinator SQLite to `COMMITTED`, and release the provider fence before all historical activation rows are checked.
- A separately tampered historical activation row can therefore be rejected only after current recovery side effects occurred.
- This violates the frozen LAB-090/LAB-100 restart ordering and composes directly with LAB-099/#184's fail-before-mutation requirement.
- Merely moving the current structural verifier earlier is necessary but not sufficient: final LAB-097..099 retained-authority and authenticated activation-ticket provenance checks must all precede recovery mutation.

Durable evidence:
- `research/2026-09-12-lab100-restart-verification-before-recovery-side-effects.md`, main commit `d2a03016f70eafe6ef5054d5c1316725d243928d`.
- #185 comment `5642126893` records the LAB-100 restart-ordering regression requirement.
- #184 comment `5642127689` records the LAB-099 composition.
- Verdict: `LAB100_RESTART_VERIFY_BEFORE_RECOVER_SIDE_EFFECTS_REQUIRED`.
- Python official typing documentation was rechecked: `typing.final` has no runtime enforcement, so the trusted/sealed authority boundary cannot be type-hint-only.

## Known failures / blockers
- LAB-086 remains priority #1. Exact local execution of the complete real-ledger closure is unavailable in this run.
- Direct shell transport cannot resolve `github.com`.
- Connector can read pinned source but cannot byte-exactly materialize the whole pinned closure into the executor in this run.
- Complete real-schema LAB-086 tests, unsafe expected-failure seed, full compileall, security reconciliation and current-main conflict audit remain pending.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-090..100 source/design evidence does not substitute for executable RED/GREEN proof.
- LAB-100 now has a concrete restart mutation-order RED case in addition to its already frozen authority-construction model.

## Exact next action
LAB-086 first: probe once for a newly supported non-model materialization path for pinned connector bytes at exact executable snapshot `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`. If available, materialize the exact manifest-listed implementation closure plus all `test_*.py` and the pinned LAB-085 fixture helper; verify every file with `git hash-object` against the pinned blob before import; execute all normal LAB-086 real-schema tests; run `unsafe_legacy_promotion_expected_failure.py` separately and require the intended failure; run full compileall; then perform final security/reconciliation and a fresh current-main conflict audit. Fix every observed blocker before changing draft/merge status.

Do not manually copy connector payloads into the executor. If no supported materialization path exists, continue the highest-value distinct source audit rather than extending frozen contracts by repetition. Preferred next fallback: audit PR #175/LAB-090 startup and rotation paths for **any additional mutation-before-provenance-verification ordering** beyond the newly recorded `_recover_pending_activation()` before `_verify_activation_records()` case; specifically trace `_init_activation_schema()`, `_require_runtime_matches_durable_head()`, rotation retry handling, and provider abort/release cleanup against LAB-097..100 fail-before-mutation requirements. Record only genuinely distinct findings; if none exist, move to the next READY source-level issue rather than manufacturing a new contract.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact complete real-ledger gate + unsafe seed + full compileall + current-main conflict/security audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending; startup mutation-order audit now has a concrete pre-verification side-effect finding.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178 / LAB-093 — READY/design-frozen; exact RED/GREEN pending.
- #179..185 / LAB-094..100 — READY/design-frozen; exact executable gates pending. LAB-100 additionally requires the restart verify-before-recover regression recorded on 2026-09-12.
