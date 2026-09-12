# Current Lab State

Last updated: 2026-09-12

## Active objective
LAB-086 — finish the exact executable/security gate for asymmetric break-glass history migration, then reconcile/merge only if every real-schema regression and current-main conflict audit passes.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165 at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`. Keep draft.
- LAB-092: #176 / draft PR #177, pinned head `81673f8f6e4e0864dfa124735938c40aa28b4f2c`, base LAB-090.
- LAB-099 RED-intent staging: #184 / branch `lab-099-precursor-cutover-red-intent` / draft PR #186, head `1bea1eb519f07ce6eb32388eb923ed53d0f99e86`, base PR #177 branch.
- Other retained drafts: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175.
- Frozen design follow-up: LAB-093/#178 plus LAB-094..100/#179..185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected open PRs/issues; resumed LAB-086 first and re-probed exact materialization.

Current-run capability/evidence:
- Direct `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git /tmp/ai-runtime-lab` again failed before repository execution with `Could not resolve host: github.com` (exit 128).
- GitHub connector reads/writes remain available, but no supported byte-exact connector-to-local-executor materialization primitive for the complete pinned LAB-086 closure is exposed.
- Therefore no new LAB-086 behavioral, unsafe-seed, compileall, security-reconciliation, conflict, LAB-099 repository RED, or LAB-099 GREEN PASS is claimed.

Completed the recorded LAB-099 test-owned fixture-DDL wiring without production changes:
- PR #186 commit `1bea1eb519f07ce6eb32388eb923ed53d0f99e86` updates only `experiments/provider_generation_history/tests/lab099_precursor_fixture_adapter.py`;
- `install_precursor_relation_without_prepared()` now installs the exact frozen V1 literal DDL directly from `lab099_precursor_relation_reference.py`, so the orphan-schema fixture no longer depends on fabricated or absent authority vectors;
- `delete_precursor_relation()` resolves the exact frozen relation name from the same oracle;
- the adapter validates relation name, literal DDL, exact 32-byte frozen definition digest and the relation-oracle self-check before mutation;
- authority-bearing PREPARED/CONFIRMED/provenance helpers remain fail-closed on the absent `lab099_precursor_fixture_vectors` module;
- any future `atomic_prepared_plan()` is additionally required to begin with the exact frozen precursor DDL;
- PR #186 remains draft/test-only and mergeable, now ahead 10 / behind 0 versus pinned PR #177 head, with exactly six changed files, all under `experiments/provider_generation_history/tests/`; no production file changed.

Actually executed local evidence:
- direct LAB-086 clone probe failed as above before repository execution;
- standalone file-backed SQLite probe executed the exact frozen precursor V1 DDL inside `BEGIN IMMEDIATE`, committed, read `sqlite_master`, and verified normalized stored SQL equals the frozen literal definition;
- the same probe recomputed frozen relation-definition digest `696c54d1afdef52c05c120ce7d09a7a2eeb567daafb3a378b7dc4ca64f80e3bb`; result PASS;
- this is schema-fixture evidence only, not repository RED/GREEN and not a full PR #186 import/compile pass.

Durable evidence:
- branch commit `1bea1eb519f07ce6eb32388eb923ed53d0f99e86`, adapter blob `6419a2bde9a13b88d4b3718ce4dab19e67ba145b`;
- `research/2026-09-12-lab099-fixture-ddl-wiring-and-authority-storage-boundary.md`, main commit `daf7aa1f862bc19dd5c6ef10f7a3a33288984e34`;
- #184 comment `5647448158`.

## Known failures / blockers
- LAB-086 remains priority #1. Exact local execution of the complete real-ledger closure is unavailable in this run.
- Direct shell transport cannot resolve `github.com`.
- Connector can read/write pinned source but cannot byte-exactly materialize the whole LAB-086 closure into the executor in this run.
- Complete real-schema LAB-086 tests, unsafe expected-failure seed, full compileall, security reconciliation and current-main conflict audit remain pending.
- Keep PRs #165/#172/#173/#175/#177/#186 draft until their retained exact gates execute.
- PR #186 is RED-intent staging only. The orphan literal-DDL fixture is now mechanically wired, but authenticated PREPARED/CONFIRMED persistence still lacks one frozen concrete SQLite storage representation; fixture vectors must not invent it.
- Canonical PREPARED/CONFIRMED bytes/digests are frozen, but the durable relation/reuse strategy, persisted fields, authenticator storage/verification, uniqueness/idempotence and lineage reconstruction for cutover evidence must be frozen before `atomic_prepared_plan()` can safely exist.
- LAB-090..100 source/design evidence does not substitute for executable RED/GREEN proof.
- LAB-100 retains concrete regressions: verify historical activation evidence before restart recovery side effects; validate provider/verifier authority pairing before mutating `prepare_activation()`; bind activation state/anchor CAS/idempotency/identity under one provider authority; reject mutable caller-owned/fake subclass authority.
- Do not auto-upgrade existing unauthenticated LAB-090 rows; do not call provider prepare from an unauthenticated local recovery row; do not treat PR #177's LAB-092 V1 migration marker as proof of precursor governance.

## Exact next action
LAB-086 first: probe once for a newly supported non-model materialization path for pinned connector bytes at exact executable snapshot `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`. If available, materialize the exact manifest-listed implementation closure plus all `test_*.py` and the pinned LAB-085 fixture helper; verify every file with `git hash-object` against the pinned blob before import; execute all normal LAB-086 real-schema tests; run `unsafe_legacy_promotion_expected_failure.py` separately and require the intended failure; run full compileall; then perform final security/reconciliation and a fresh current-main conflict audit. Fix every observed blocker before changing draft/merge status.

If no supported exact materialization path exists, continue only PR #186 test-owned LAB-099 work: source-audit the existing authenticated provenance/shared-anchor persistence surfaces and freeze the smallest concrete durable PREPARED/CONFIRMED cutover-evidence representation that reuses an existing authority mechanism rather than creating a duplicate subsystem. Freeze exact storage identity/fields, authenticator persistence and verification, PREPARED->CONFIRMED binding, logical-DB/LAB-092/parent+epoch lineage, idempotence/sibling uniqueness and migration ownership. Only after that storage contract is frozen may `lab099_precursor_fixture_vectors.py` be added and `atomic_prepared_plan()` made mechanically executable. Do not add production LAB-099 behavior before an observable repository RED.

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
- #184 / LAB-099 — READY + isolated RED-intent draft PR #186; physical V1 precursor relation, real relation digest, dual-HMAC precursor persistence contract, byte-exact cutover vectors and test-owned DDL/schema oracles are frozen; orphan DDL fixture now uses the frozen DDL directly; next fallback is freeze durable authenticated cutover-evidence persistence before fixture-vector mutation plans.
- #185 / LAB-100 — READY/design-frozen; exact executable gates pending.
