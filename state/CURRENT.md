# Current Lab State

Last updated: 2026-09-12

## Active objective
LAB-086 — finish the exact executable/security gate for asymmetric break-glass history migration, then reconcile/merge only if every real-schema regression and current-main conflict audit passes.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165. Keep draft.
- LAB-092: #176 / draft PR #177, pinned head `81673f8f6e4e0864dfa124735938c40aa28b4f2c`, base LAB-090.
- LAB-099 RED-intent staging: #184 / branch `lab-099-precursor-cutover-red-intent` / draft PR #186, head `f6c0ebeaaed6e0e34156a8c78b5804eedf5db0ab`, based on PR #177 branch.
- Other retained drafts: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175.
- Frozen design follow-up: LAB-093/#178 plus LAB-094..100/#179..185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected open issues/PRs; resumed LAB-086 first and re-probed exact materialization.

Current-run capability/evidence:
- direct `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git /tmp/ai-runtime-lab` failed before repository execution with `Could not resolve host: github.com` (exit 128);
- GitHub connector reads/writes remain available, but no supported byte-exact connector-to-local-executor materialization primitive for the complete pinned LAB-086 closure is exposed;
- therefore no new LAB-086 behavioral/unsafe-seed/compileall/security/conflict PASS and no LAB-099 repository RED/GREEN PASS is claimed.

Completed LAB-099 durable cutover-evidence storage freeze without production changes:
- source-audited `shared_anchor_intents` and provider-history persistence on PR #177;
- froze `LAB099_DURABLE_CUTOVER_EVIDENCE_STORAGE_V1_FROZEN` in `research/2026-09-12-lab099-durable-cutover-evidence-storage-v1.md`;
- selected a small materialization relation `provider_activation_reservation_cutovers` for exact PREPARED bytes/nonce/indexable lineage, while retaining the existing `shared_anchor_intents` PREPARED/CONFIRMED row + externally reauthenticated `receipt_binding` as the authority-bearing phase transition;
- exact normalized materialization-relation definition digest: `0db2587bae8861d0233d939b4283a58b438b947c5336f7af9d0f1687856c860e`;
- deterministic anchor intent identity: `migration:provider-activation-reservation-precursor-cutover:v1:<prepared_digest>`; component `provider-activation-reservation-precursor`; type `migration`; payload commits exact PREPARED digest + exact 32-byte confirmation nonce;
- CONFIRMED is reconstructed deterministically from the verified PREPARED + confirmed shared-anchor `LedgerEntry`; no second phase row, key, signer, receipt mechanism or provenance ledger is introduced;
- migration ownership is explicit-only: ordinary startup verifies but never creates/repairs/adopts/backfills the precursor or cutover materialization relations.

PR #186 test-owned progress:
- added `experiments/provider_generation_history/tests/lab099_cutover_storage_reference.py` at branch commit `f6c0ebeaaed6e0e34156a8c78b5804eedf5db0ab`, blob `89c796b6dd59d5ca9490cfa0b8e7803a76cf7b1f`;
- oracle freezes exact cutover materialization DDL, definition digest, deterministic anchor ID/payload digest and confirmed-head digest adapter;
- compare versus pinned PR #177 head: ahead 11 / behind 0, exactly seven changed files, all under `experiments/provider_generation_history/tests/`; no production file changed.

Durable evidence:
- main research commit `0df2d0ff562a9d4e96e188f2cdae7929dcb93b62`;
- PR #186 branch commit `f6c0ebeaaed6e0e34156a8c78b5804eedf5db0ab`;
- #184 comment `5647785396`.

## Known failures / blockers
- LAB-086 remains priority #1; exact local execution of the complete real-ledger closure is unavailable in this run.
- Direct shell transport cannot resolve `github.com`.
- Connector can read/write pinned source but cannot byte-exactly materialize the whole LAB-086 closure into the executor in this run.
- Complete LAB-086 real-schema tests, unsafe expected-failure seed, full compileall, security reconciliation and current-main conflict audit remain pending.
- Keep PRs #165/#172/#173/#175/#177/#186 draft until their retained exact gates execute.
- PR #186 remains RED-intent staging only. Durable cutover storage identity/reuse/authentication/idempotence/migration ownership are now frozen, but `lab099_precursor_fixture_vectors.py` and an executable `atomic_prepared_plan()` do not yet exist.
- LAB-090..100 source/design evidence does not substitute for executable RED/GREEN proof.
- Whole-store rollback/deletion is not solved by another local table; LAB-099 composes with LAB-095/LAB-097 logical-database/provenance authority and must not claim SQLite can prove total deletion of its own history.
- Do not auto-upgrade existing unauthenticated LAB-090 rows; do not call provider prepare from an unauthenticated local recovery row; do not treat PR #177's LAB-092 V1 migration marker as proof of precursor governance.

## Exact next action
LAB-086 first: probe once for a newly supported non-model materialization path for pinned connector bytes at exact executable snapshot `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`. If available, materialize the exact manifest-listed implementation closure plus all `test_*.py` and the pinned LAB-085 fixture helper; verify every file with `git hash-object` against pinned blobs before import; execute all normal LAB-086 real-schema tests; run `unsafe_legacy_promotion_expected_failure.py` separately and require the intended failure; run full compileall; then perform final security/reconciliation and a fresh current-main conflict audit. Fix every observed blocker before changing draft/merge status.

If no supported exact materialization path exists, continue only PR #186 test-owned LAB-099 work: add `lab099_precursor_fixture_vectors.py` from the already-frozen canonical PREPARED bytes plus the new cutover-storage oracle, then wire `lab099_precursor_fixture_adapter.atomic_prepared_plan()` so one SQLite `BEGIN IMMEDIATE` mechanically installs exact precursor DDL + exact cutover materialization DDL + exact materialization row + exact matching shared-anchor PREPARED row/meta CAS. Add/activate the two minimum RED scenarios: orphan precursor DDL without PREPARED fails closed; crash after atomic DDL+materialization+exact PREPARED resumes only that exact PREPARED. Do not add production LAB-099 behavior before an observable repository RED.

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
- #184 / LAB-099 — READY + isolated RED-intent draft PR #186; precursor physical relation, canonical vectors, schema oracles and durable cutover-evidence storage contract are frozen; next fallback is fixture vectors + executable atomic PREPARED plan/test-only REDs.
- #185 / LAB-100 — READY/design-frozen; exact executable gates pending.
