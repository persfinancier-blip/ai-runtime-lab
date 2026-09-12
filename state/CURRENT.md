# Current Lab State

Last updated: 2026-09-12

## Active objective
LAB-086 — finish the exact executable/security gate for asymmetric break-glass history migration, then reconcile/merge only if every real-schema regression and current-main conflict audit passes.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165. Keep draft.
- LAB-092: #176 / draft PR #177, pinned head `81673f8f6e4e0864dfa124735938c40aa28b4f2c`, base LAB-090.
- LAB-099 RED-intent staging: #184 / branch `lab-099-precursor-cutover-red-intent` / draft PR #186, head `3ce932e1e20813644b14c0916b5802e5f96cfa85`, based on PR #177 branch.
- Other retained drafts: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175.
- Frozen design follow-up: LAB-093/#178 plus LAB-094..100/#179..185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected open issues/PRs; resumed LAB-086 first and re-probed exact materialization.

Current-run capability/evidence:
- direct `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git /tmp/ai-runtime-lab` failed before repository execution with `Could not resolve host: github.com` (exit 128);
- GitHub connector reads/writes remain available, but no supported byte-exact connector-to-local-executor materialization primitive for the complete pinned LAB-086 closure is exposed;
- therefore no new LAB-086 behavioral/unsafe-seed/compileall/security/conflict PASS and no LAB-099 repository RED/GREEN PASS is claimed.

Completed LAB-099 test-owned PREPARED fixture slice on PR #186:
- added `experiments/provider_generation_history/tests/lab099_precursor_fixture_vectors.py`;
- `atomic_prepared_plan()` now composes exact frozen precursor DDL + exact cutover materialization DDL + exact materialization row + matching shared-anchor PREPARED + `shared_anchor_meta` CAS;
- updated `lab099_precursor_fixture_adapter.py` so plan entries may require exact rowcounts and any mismatch rolls back the same `BEGIN IMMEDIATE` transaction;
- audit caught a provider-generation-head race in the first draft: the published shared-anchor PREPARED insertion now uses `INSERT ... SELECT` from the current durable provider head constrained to the preflight provider/generation and requires rowcount 1;
- stale provider head or stale reserved-position CAS therefore fails closed and rolls back earlier fixture DDL/materialization/PREPARED mutations;
- frozen PREPARED digest remains `77ffdf5f657510a285d75e866d3418a85d1aeb0ca0f2c830617c850a5277b53e`;
- frozen anchor payload digest remains `8aee140ac30142fac83fe03f95f36e56be94583b4ef100060610bb9ec59089e9`.

Observed scratch validation only, not repository RED/GREEN:
- initially authored fixture-vector module `py_compile` PASS and static self-check PASS before publication;
- semantically equivalent SQLite success path installed cutover materialization + PREPARED and advanced reserved position exactly once;
- stale tail CAS simulation rolled back DDL/materialization/PREPARED completely;
- stale provider-generation-head simulation produced PREPARED insert rowcount 0 and rolled back.

PR #186 topology versus pinned PR #177 head:
- ahead 14 / behind 0;
- exactly eight changed files;
- all changed files under `experiments/provider_generation_history/tests/`;
- PR remains open, draft and mergeable; no production LAB-099 file changed.

Durable evidence:
- PR #186 head `3ce932e1e20813644b14c0916b5802e5f96cfa85`;
- fixture-vector blob `8ca5f2fb508500758a5129d75a29c2406169b361`;
- fixture-adapter blob `671ace9ed879a0a1d0c06786b11d2e46fb746de3`;
- `research/2026-09-12-lab099-executable-prepared-fixture-plan.md` main commit `e7c6df4df6ef437f072e68099ff142902e55f06c`;
- #184 comment `5648133496`.

## Known failures / blockers
- LAB-086 remains priority #1; exact local execution of the complete real-ledger closure is unavailable in this run.
- Direct shell transport cannot resolve `github.com`.
- Connector can read/write pinned source but cannot byte-exactly materialize the whole LAB-086 closure into the executor in this run.
- Complete LAB-086 real-schema tests, unsafe expected-failure seed, full compileall, security reconciliation and current-main conflict audit remain pending.
- Keep PRs #165/#172/#173/#175/#177/#186 draft until their retained exact gates execute.
- PR #186 remains RED-intent staging only. Its first atomic PREPARED fixture plan now exists, but the repository RED-intent suite has not been executed and production LAB-099 remains forbidden.
- LAB-090..100 source/design evidence does not substitute for executable RED/GREEN proof.
- Whole-store rollback/deletion is not solved by another local table; LAB-099 composes with LAB-095/LAB-097 logical-database/provenance authority and must not claim SQLite can prove total deletion of its own history.
- Do not auto-upgrade existing unauthenticated LAB-090 rows; do not call provider prepare from an unauthenticated local recovery row; do not treat PR #177's LAB-092 V1 migration marker as proof of precursor governance.

## Exact next action
LAB-086 first: probe once for a newly supported non-model materialization path for pinned connector bytes at exact executable snapshot `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`. If available, materialize the exact manifest-listed implementation closure plus all `test_*.py` and the pinned LAB-085 fixture helper; verify every file with `git hash-object` against pinned blobs before import; execute all normal LAB-086 real-schema tests; run `unsafe_legacy_promotion_expected_failure.py` separately and require the intended failure; run full compileall; then perform final security/reconciliation and a fresh current-main conflict audit. Fix every observed blocker before changing draft/merge status.

If no supported exact materialization path exists, continue only PR #186 test-owned LAB-099 work: add one side-effect-free verifier for the exact `provider_activation_reservation_cutovers` materialization row + matching shared-anchor PREPARED cross-binding, then use it to make the crash-after-atomic-PREPARED fixture self-check prove that only the exact frozen PREPARED digest, confirmation nonce, intent identity/payload digest, provider generation, predecessor/position and request ID are resumable. Include negative checks for changed nonce, changed PREPARED digest and stale provider/tail bindings. Do not add production `activation_reservation_provenance` before an observable repository RED.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement/execute frozen LAB-090..100 RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact complete real-ledger gate + unsafe seed + full compileall + current-main conflict/security audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending; V1 migration marker does not cover precursor semantics.
- #178 / LAB-093 — READY/design-frozen; exact RED/GREEN pending.
- #179..182 / LAB-094..097 — READY/design-frozen; exact executable gates pending.
- #183 / LAB-098 — READY; exact RED/GREEN pending.
- #184 / LAB-099 — READY + isolated RED-intent draft PR #186; precursor physical relation, canonical vectors, schema oracles, durable cutover storage and first atomic PREPARED fixture plan are frozen/published; next fallback is exact PREPARED cross-binding verifier/self-checks.
- #185 / LAB-100 — READY/design-frozen; exact executable gates pending.
