# Current Lab State

Last updated: 2026-09-12

## Active objective
LAB-086 — finish the exact executable/security gate for asymmetric break-glass history migration, then reconcile/merge only if every real-schema regression and current-main conflict audit passes.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165 at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`. Keep draft.
- Other open drafts inspected: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175; LAB-092/#176 PR #177.
- Frozen design follow-up: LAB-093/#178 plus LAB-094..100/#179..185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected active PRs; resumed LAB-086 first and re-probed exact materialization.

Current-run capability/evidence:
- Direct `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git` again failed before repository execution with `Could not resolve host: github.com`.
- GitHub connector reads/writes remain available, but no supported byte-exact connector-to-local-executor materialization primitive is exposed. Manual/model reserialization of the security-critical LAB-086 closure remains prohibited.
- Therefore no new LAB-086 behavioral, unsafe-seed, compileall, security-reconciliation or conflict PASS is claimed.
- Fresh PR #165 metadata: open, draft, mergeable=false, head `ee210a47221b6df53f3518aa3af74f76c5b0122b`, 195 commits, 86 changed files.

Completed the recorded LAB-100/#185 fallback cleanup/retry audit on actual PR #175 source. No additional exact-provider mutation-without-durable-row path was source-proved beyond the already recorded restart verify-before-recover and provider/verifier pairing findings. Post-SQL-commit failure paths retain a durable activation row for restart reconciliation; do not manufacture another LAB-100 contract from speculative external races.

Moved to the next READY source-level issue, LAB-098/#183, and pinned a concrete implementation seam:
- authenticated `provider_generation_transitions.new_generation_id` is the required-record index for LAB-090 activation presence;
- verify transition->activation anti-join is empty and activation->transition anti-join is empty before any recovery mutation;
- this establishes one-to-one presence for each governed non-bootstrap transition without reconstructing deleted ticket state;
- verify durable generation history first, then transition-derived activation completeness, then LAB-099 activation-content provenance, and only then `_recover_pending_activation()`;
- this is presence/omission only; it does not substitute for LAB-099 exact ticket authentication.

Durable evidence:
- `research/2026-09-12-lab098-transition-derived-activation-presence-ordering.md`, main commit `553fd2a2ce29d01015007ef265436c430386fbaa`.
- #183 comment `5642807072` records the implementation ordering and RED/GREEN consequences.

## Known failures / blockers
- LAB-086 remains priority #1. Exact local execution of the complete real-ledger closure is unavailable in this run.
- Direct shell transport cannot resolve `github.com`.
- Connector can read pinned source but cannot byte-exactly materialize the whole pinned closure into the executor in this run.
- Complete real-schema LAB-086 tests, unsafe expected-failure seed, full compileall, security reconciliation and current-main conflict audit remain pending.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-090..100 source/design evidence does not substitute for executable RED/GREEN proof.
- LAB-100 retains two concrete regressions: verify historical activation evidence before restart recovery side effects; validate provider/verifier authority pairing before mutating `prepare_activation()`.
- LAB-098 now has a source-level minimal completeness seam, but exact repository RED/GREEN is still pending.

## Exact next action
LAB-086 first: probe once for a newly supported non-model materialization path for pinned connector bytes at exact executable snapshot `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`. If available, materialize the exact manifest-listed implementation closure plus all `test_*.py` and the pinned LAB-085 fixture helper; verify every file with `git hash-object` against the pinned blob before import; execute all normal LAB-086 real-schema tests; run `unsafe_legacy_promotion_expected_failure.py` separately and require the intended failure; run full compileall; then perform final security/reconciliation and a fresh current-main conflict audit. Fix every observed blocker before changing draft/merge status.

Do not manually copy connector payloads into the executor. If no supported materialization path exists, continue source-level READY work without inventing contracts. Next inspect LAB-098/#183 and LAB-099/#184 composition against PR #175 transition/history schemas to determine the smallest regression-first patch shape that simultaneously enforces transition-derived activation presence and authenticated ticket-content binding before recovery. Prefer a concrete test/implementation seam; if exact execution is still unavailable, persist only source-proved design/evidence and then move to the next READY issue.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact complete real-ledger gate + unsafe seed + full compileall + current-main conflict/security audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending; startup mutation-order and provider/verifier precondition audits have concrete findings.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178 / LAB-093 — READY/design-frozen; exact RED/GREEN pending.
- #179..182 / LAB-094..097 — READY/design-frozen; exact executable gates pending.
- #183 / LAB-098 — READY; transition-derived activation presence/order seam pinned; exact RED/GREEN pending.
- #184 / LAB-099 — READY; authenticated ticket-content provenance contract frozen; exact RED/GREEN pending.
- #185 / LAB-100 — READY/design-frozen; exact executable gates pending; restart verify-before-recover and provider/verifier pairing regressions recorded.
