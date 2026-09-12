# Current Lab State

Last updated: 2026-09-13

## Active objective
LAB-086 — finish the exact executable/security gate for asymmetric break-glass history migration, then reconcile/merge only if every real-schema regression and current-main conflict audit passes.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165. Keep draft.
- LAB-092: #176 / draft PR #177, pinned head `81673f8f6e4e0864dfa124735938c40aa28b4f2c`, base LAB-090.
- LAB-099 RED-intent staging: #184 / branch `lab-099-precursor-cutover-red-intent` / draft PR #186, head `c62cc02397c9e80383d95808ff4de71461c98b5e`, based on PR #177 branch.
- Other retained drafts: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175.
- Frozen design follow-up: LAB-093/#178 plus LAB-094..100/#179..185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected open issues/PRs; resumed LAB-086 first and re-probed exact materialization.

Current-run capability/evidence:
- direct `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git /tmp/ai-runtime-lab` failed before repository execution with `Could not resolve host: github.com` (exit 128);
- GitHub connector reads/writes remain available, but no supported byte-exact connector-to-local-executor materialization primitive for the complete pinned LAB-086 closure is exposed;
- therefore no new LAB-086 behavioral/unsafe-seed/compileall/security/conflict PASS and no LAB-099 repository RED/GREEN PASS is claimed.

Completed LAB-099 test-owned persisted PREPARED row cross-binding slice on PR #186:
- added `experiments/provider_generation_history/tests/lab099_prepared_fixture_row_verifier.py`;
- it reads exactly one actual cutover materialization row by the expected frozen PREPARED digest and exactly one matching shared-anchor PREPARED row by materialized anchor intent ID;
- it requires the persisted PREPARED position to equal the durable `shared_anchor_meta.reserved_position` and derives predecessor only as `reserved_position - 1`;
- provider ID/generation remain external runtime-attestation expectations, not values trusted from the mutable recovery row;
- exact semantic/byte binding delegates to `lab099_prepared_cross_binding_reference.verify_prepared_cross_binding()`;
- added narrow test-only durable tamper support for confirmation nonce, PREPARED digest, provider generation, predecessor position, position and request ID;
- added non-discoverable `red_intent_lab099_prepared_row_cross_binding.py` to require one positive persisted-pair check and fail-closed behavior for all six isolated row mutations.

Observed validation only, not repository RED/GREEN:
- standalone local SQLite read-back/tail mechanics PASS;
- incrementing persisted PREPARED `position` while leaving durable reserved tail unchanged was rejected by the explicit tail/position cross-check;
- both new published files were fetched back through GitHub after write.

PR #186 topology versus pinned PR #177 head:
- ahead 17 / behind 0;
- PR remains open and draft;
- PR file list remains entirely under `experiments/provider_generation_history/tests/`; no production LAB-099 file changed.

Durable evidence:
- PR #186 head `c62cc02397c9e80383d95808ff4de71461c98b5e`;
- persisted-row verifier blob `b21341bfe986a06fb0a91f18423383f6344dfc4e`;
- persisted-row RED-intent blob `c67180993d7a766180bb17f68382b978f9efdfef`;
- `research/2026-09-13-lab099-persisted-prepared-row-cross-binding.md` main commit `f07570dca1ae0601a5567f28e945dc657b3c6412`;
- #184 comment `5648751979`.

## Known failures / blockers
- LAB-086 remains priority #1; exact local execution of the complete real-ledger closure is unavailable in this run.
- Direct shell transport cannot resolve `github.com`.
- Connector can read/write pinned source but cannot byte-exactly materialize the whole LAB-086 closure into the executor in this run.
- Complete LAB-086 real-schema tests, unsafe expected-failure seed, full compileall, security reconciliation and current-main conflict audit remain pending.
- Keep PRs #165/#172/#173/#175/#177/#186 draft until their retained exact gates execute.
- PR #186 remains RED-intent staging only. Test-owned DDL, authority vectors, schema/storage oracles, atomic PREPARED fixture plan, side-effect-free cross-binding oracle and actual persisted-row verifier exist, but the exact repository RED-intent suite has not executed and production LAB-099 remains forbidden.
- LAB-090..100 source/design evidence does not substitute for executable RED/GREEN proof.
- Whole-store rollback/deletion is not solved by another local table; LAB-099 composes with LAB-095/LAB-097 logical-database/provenance authority and must not claim SQLite can prove total deletion of its own history.
- Do not auto-upgrade existing unauthenticated LAB-090 rows; do not call provider prepare from an unauthenticated local recovery row; do not treat PR #177's LAB-092 V1 migration marker as proof of precursor governance.

## Exact next action
LAB-086 first: probe once for a newly supported non-model materialization path for pinned connector bytes at exact executable snapshot `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`. If available, materialize the exact manifest-listed implementation closure plus all `test_*.py` and the pinned LAB-085 fixture helper; verify every file with `git hash-object` against pinned blobs before import; execute all normal LAB-086 real-schema tests; run `unsafe_legacy_promotion_expected_failure.py` separately and require the intended failure; run full compileall; then perform final security/reconciliation and a fresh current-main conflict audit. Fix every observed blocker before changing draft/merge status.

If no supported exact materialization path exists, continue only PR #186 test-owned LAB-099 work: source-audit the existing frozen CONFIRMED vector and shared-anchor receipt/re-authentication surfaces, then add a side-effect-free persisted CONFIRMED read-back verifier that cross-binds the exact PREPARED materialization ancestry to one CONFIRMED shared-anchor entry, requires externally reauthenticated `receipt_binding`, and reproduces the frozen CONFIRMED head/event binding. Add isolated non-discoverable durable mutations for receipt binding, confirmed position/head binding and exact PREPARED digest ancestry and require each to fail closed. Do not add production `activation_reservation_provenance` until the exact repository RED-intent suite can actually execute and an actual RED is observed.

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
- #184 / LAB-099 — READY + isolated RED-intent draft PR #186; physical relation, canonical vectors, schema/storage oracles, atomic PREPARED fixture plan, exact PREPARED cross-binding oracle and actual persisted-row/tamper verifier are frozen/published; next fallback is persisted CONFIRMED read-back cross-binding.
- #185 / LAB-100 — READY/design-frozen; exact executable gates pending.
