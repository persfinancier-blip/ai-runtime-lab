# Current Lab State

Last updated: 2026-09-12

## Active objective
LAB-086 — finish the exact executable/security gate for asymmetric break-glass history migration, then reconcile/merge only if every real-schema regression and current-main conflict audit passes.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165 at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`. Keep draft.
- LAB-092: #176 / draft PR #177, head `81673f8f6e4e0864dfa124735938c40aa28b4f2c`, base LAB-090.
- LAB-099 RED-intent staging: #184 / branch `lab-099-precursor-cutover-red-intent` / draft PR #186, current head `7695b28733b2c6bdf3f0dfb384a82d0bf095f7b1`, base PR #177 branch.
- Other open drafts retained: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175.
- Frozen design follow-up: LAB-093/#178 plus LAB-094..100/#179..185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; re-inspected open issues/PRs; resumed LAB-086 first and re-probed exact materialization.

Current-run capability/evidence:
- Direct `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git /tmp/ai-runtime-lab` failed before repository execution with `Could not resolve host: github.com` (exit 128).
- GitHub connector reads/writes remain available, but no supported byte-exact connector-to-local-executor materialization primitive is exposed.
- Therefore no new LAB-086 behavioral, unsafe-seed, compileall, security-reconciliation, conflict, LAB-099 RED, or LAB-099 GREEN PASS is claimed.

Completed the exact fallback recorded by the previous handoff: converted the first LAB-099 precursor-cutover cases into an isolated repository RED-intent scaffold without production changes.

Durable outputs:
- branch `lab-099-precursor-cutover-red-intent` created from exact PR #177 head `81673f8f6e4e0864dfa124735938c40aa28b4f2c`;
- final scaffold head `7695b28733b2c6bdf3f0dfb384a82d0bf095f7b1`;
- compare against pinned PR #177 head: ahead 2 / behind 0 / one changed file;
- draft PR #186 opened against `lab-092-activation-schema-provenance`;
- isolated explicit-run file: `experiments/provider_generation_history/tests/red_intent_lab099_precursor_cutover.py` (intentionally not `test_*.py`);
- durable note: `research/2026-09-12-lab099-first-red-intent-scaffold.md`, main commit `c37ac655f24dfb87f2439baa7cd8a1ff7703a83a`;
- #184 comment `5644977008`; #176 comment `5644977414`.

RED-intent cases now staged:
1. LAB-092 V1 completion alone is not LAB-099 precursor authority.
2. Orphan precursor DDL without PREPARED fails closed.
3. Atomic DDL+PREPARED crash resumes only exact PREPARED digest.
4. Stale/forked predecessor parent+epoch replay rejects.
5. CONFIRMED binds the exact PREPARED digest.
6. CONFIRMED forbids downgrade/fallback after precursor relation deletion.

Audit correction before PR creation:
- initial scaffold draft incorrectly put corruption/crash `*_for_test_only` hooks on the future production module;
- final scaffold moves those responsibilities to a future sibling test-only fixture adapter under the tests package;
- production LAB-099 surface must not expose test mutation hooks.

## Known failures / blockers
- LAB-086 remains priority #1. Exact local execution of the complete real-ledger closure is unavailable in this run.
- Direct shell transport cannot resolve `github.com`.
- Connector can read pinned source but cannot byte-exactly materialize the whole pinned closure into the executor in this run.
- Complete real-schema LAB-086 tests, unsafe expected-failure seed, full compileall, security reconciliation and current-main conflict audit remain pending.
- Keep PRs #165/#172/#173/#175/#177/#186 draft until their retained exact gates execute.
- PR #186 is RED-intent staging only. The future LAB-099 production module and test-only fixture adapter intentionally do not exist yet, so no RED execution has been observed.
- LAB-090..100 source/design evidence does not substitute for executable RED/GREEN proof.
- LAB-100 retains concrete regressions: verify historical activation evidence before restart recovery side effects; validate provider/verifier authority pairing before mutating `prepare_activation()`; bind activation state/anchor CAS/idempotency/identity under one provider authority; reject mutable caller-owned/fake subclass authority.
- LAB-098 source-level completeness/order seam is pinned, but exact repository RED/GREEN is pending.
- Do not bolt an unauthenticated digest/self-hash onto PR #175; do not auto-upgrade existing unauthenticated LAB-090 rows; do not call provider prepare from an unauthenticated local recovery row; do not treat PR #177's LAB-092 V1 migration marker as proof of precursor governance.

## Exact next action
LAB-086 first: probe once for a newly supported non-model materialization path for pinned connector bytes at exact executable snapshot `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`. If available, materialize the exact manifest-listed implementation closure plus all `test_*.py` and the pinned LAB-085 fixture helper; verify every file with `git hash-object` against the pinned blob before import; execute all normal LAB-086 real-schema tests; run `unsafe_legacy_promotion_expected_failure.py` separately and require the intended failure; run full compileall; then perform final security/reconciliation and a fresh current-main conflict audit. Fix every observed blocker before changing draft/merge status.

If no supported exact materialization path exists, continue LAB-099 on draft PR #186 without production behavior changes. Next smallest safe slice: define and add the **test-only** `lab099_precursor_fixture_adapter` contract needed by cases 2-6 using only already-frozen precursor relation/provenance DDL identities; do not invent unauthenticated fixture semantics. Before writing it, re-read the frozen relation-DDL, canonical provenance, LAB-097 logical-DB identity, and PREPARED/CONFIRMED contracts and pin every fixture mutation to those bytes/columns. Keep the adapter isolated under tests and non-discovered. If exact execution is still unavailable, do not claim RED; persist the adapter/source audit and stop before production code.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement/execute frozen LAB-090..100 RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact complete real-ledger gate + unsafe seed + full compileall + current-main conflict/security audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending; startup mutation-order, provider/verifier precondition, authenticated reservation precursor and V2 provider/provenance atomic-head ordering findings recorded.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending; V1 migration marker does not cover precursor semantics.
- #178 / LAB-093 — READY/design-frozen; exact RED/GREEN pending.
- #179..182 / LAB-094..097 — READY/design-frozen; exact executable gates pending.
- #183 / LAB-098 — READY; exact RED/GREEN pending.
- #184 / LAB-099 — READY + isolated RED-intent draft PR #186; fixture adapter and observed REDs pending before production behavior.
- #185 / LAB-100 — READY/design-frozen; exact executable gates pending.
