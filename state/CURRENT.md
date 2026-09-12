# Current Lab State

Last updated: 2026-09-12

## Active objective
LAB-086 — finish the exact executable/security gate for asymmetric break-glass history migration, then reconcile/merge only if every real-schema regression and current-main conflict audit passes.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165. Keep draft.
- LAB-092: #176 / draft PR #177, pinned head `81673f8f6e4e0864dfa124735938c40aa28b4f2c`, base LAB-090.
- LAB-099 RED-intent staging: #184 / branch `lab-099-precursor-cutover-red-intent` / draft PR #186, head `9fe1d87b6d1e9740163a529834a9ca36107624df`, based on PR #177 branch.
- Other retained drafts: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175.
- Frozen design follow-up: LAB-093/#178 plus LAB-094..100/#179..185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected open issues/PRs; resumed LAB-086 first and re-probed exact materialization.

Current-run capability/evidence:
- direct `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git /tmp/ai-runtime-lab` failed before repository execution with `Could not resolve host: github.com` (exit 128);
- GitHub connector reads/writes remain available, but no supported byte-exact connector-to-local-executor materialization primitive for the complete pinned LAB-086 closure is exposed;
- therefore no new LAB-086 behavioral/unsafe-seed/compileall/security/conflict PASS and no LAB-099 repository RED/GREEN PASS is claimed.

Completed LAB-099 test-owned PREPARED cross-binding slice on PR #186:
- added `experiments/provider_generation_history/tests/lab099_prepared_cross_binding_reference.py`;
- verifier is side-effect free and imports only test-owned LAB-099 storage/authority reference modules;
- it cross-binds exact materialized PREPARED canonical bytes/digest/semantic fields + confirmation nonce to deterministic shared-anchor intent/payload/request identity;
- it requires the runtime-expected provider ID/generation and predecessor shared-anchor position rather than trusting a mutable local recovery row as authority;
- exact PREPARED status and `receipt_binding IS NULL` are required;
- negative self-checks reject changed nonce, changed PREPARED digest, stale provider generation and stale tail expectation.

Observed validation only, not repository RED/GREEN:
- authored verifier `python -m py_compile` PASS;
- isolated functional self-check PASS with compatible test doubles for the two imported test-owned reference modules, including all four negative cases;
- published verifier blob `1979346f2372f7daf8a0a2dcc31743ab22e50c1a` exactly matched local `git hash-object` of the published text.

PR #186 topology versus pinned PR #177 head:
- ahead 15 / behind 0;
- PR remains open, draft and mergeable;
- all LAB-099 changes remain under `experiments/provider_generation_history/tests/`; no production LAB-099 file changed.

Durable evidence:
- PR #186 head `9fe1d87b6d1e9740163a529834a9ca36107624df`;
- cross-binding verifier blob `1979346f2372f7daf8a0a2dcc31743ab22e50c1a`;
- `research/2026-09-12-lab099-prepared-cross-binding-verifier.md` main commit `380028f66e06123dcfbdeeec14ba08b6078f049f`;
- #184 comment `5648453600`.

## Known failures / blockers
- LAB-086 remains priority #1; exact local execution of the complete real-ledger closure is unavailable in this run.
- Direct shell transport cannot resolve `github.com`.
- Connector can read/write pinned source but cannot byte-exactly materialize the whole LAB-086 closure into the executor in this run.
- Complete LAB-086 real-schema tests, unsafe expected-failure seed, full compileall, security reconciliation and current-main conflict audit remain pending.
- Keep PRs #165/#172/#173/#175/#177/#186 draft until their retained exact gates execute.
- PR #186 remains RED-intent staging only. Test-owned DDL, authority vectors, atomic PREPARED fixture plan and cross-binding verifier exist, but the repository RED-intent suite has not executed and production LAB-099 remains forbidden.
- LAB-090..100 source/design evidence does not substitute for executable RED/GREEN proof.
- Whole-store rollback/deletion is not solved by another local table; LAB-099 composes with LAB-095/LAB-097 logical-database/provenance authority and must not claim SQLite can prove total deletion of its own history.
- Do not auto-upgrade existing unauthenticated LAB-090 rows; do not call provider prepare from an unauthenticated local recovery row; do not treat PR #177's LAB-092 V1 migration marker as proof of precursor governance.

## Exact next action
LAB-086 first: probe once for a newly supported non-model materialization path for pinned connector bytes at exact executable snapshot `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`. If available, materialize the exact manifest-listed implementation closure plus all `test_*.py` and the pinned LAB-085 fixture helper; verify every file with `git hash-object` against pinned blobs before import; execute all normal LAB-086 real-schema tests; run `unsafe_legacy_promotion_expected_failure.py` separately and require the intended failure; run full compileall; then perform final security/reconciliation and a fresh current-main conflict audit. Fix every observed blocker before changing draft/merge status.

If no supported exact materialization path exists, continue only PR #186 test-owned LAB-099 work: wire `lab099_prepared_cross_binding_reference.py` into the crash-after-atomic-PREPARED RED-intent fixture path. Read the actual `provider_activation_reservation_cutovers` row and matching `shared_anchor_intents` PREPARED row produced by `install_atomic_prepared_cutover()` and require the verifier to accept only the exact frozen pair. Add fixture-level negative row mutations for confirmation nonce, PREPARED digest, provider generation, predecessor/position and request ID and prove each fails closed without adding production `activation_reservation_provenance`. Keep the file non-discoverable by default and do not claim repository RED until the exact repository suite can actually execute.

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
- #184 / LAB-099 — READY + isolated RED-intent draft PR #186; physical relation, canonical vectors, schema/storage oracles, atomic PREPARED fixture plan and exact PREPARED cross-binding verifier are frozen/published; next fallback is actual fixture-row verification plus tamper negatives.
- #185 / LAB-100 — READY/design-frozen; exact executable gates pending.
