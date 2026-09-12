# Current Lab State

Last updated: 2026-09-12

## Active objective
LAB-086 — finish the exact executable/security gate for asymmetric break-glass history migration, then reconcile/merge only if every real-schema regression and current-main conflict audit passes.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165 at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`. Keep draft.
- LAB-092: #176 / draft PR #177, pinned head `81673f8f6e4e0864dfa124735938c40aa28b4f2c`, base LAB-090.
- LAB-099 RED-intent staging: #184 / branch `lab-099-precursor-cutover-red-intent` / draft PR #186, head `4d77115ccc3cffe2c2b320886329422717fb76d9`, base PR #177 branch.
- Other retained drafts: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175.
- Frozen design follow-up: LAB-093/#178 plus LAB-094..100/#179..185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected open PRs/issues; resumed LAB-086 first and re-probed exact materialization.

Current-run capability/evidence:
- Direct `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git /tmp/ai-runtime-lab` again failed before repository execution with `Could not resolve host: github.com` (exit 128).
- GitHub connector reads/writes remain available, but no supported byte-exact connector-to-local-executor materialization primitive is exposed.
- Therefore no new LAB-086 behavioral, unsafe-seed, compileall, security-reconciliation, conflict, LAB-099 RED, or LAB-099 GREEN PASS is claimed.

Completed the recorded LAB-099 test-owned DDL/vector integration without production changes:
- added side-effect-free `experiments/provider_generation_history/tests/lab099_precursor_relation_reference.py` with the exact frozen V1 `provider_activation_reservation_precursors` literal DDL and repository normalization rule;
- its normalized DDL recomputes frozen relation-definition digest `696c54d1afdef52c05c120ce7d09a7a2eeb567daafb3a378b7dc4ca64f80e3bb`;
- explicitly replaced the historical synthetic relation digest in current PREPARED/CONFIRMED reference vectors rather than reinterpreting it;
- precursor canonical bytes, precursor digest, and dual predecessor/successor HMAC reference vectors remain unchanged;
- re-frozen PREPARED digest is `77ffdf5f657510a285d75e866d3418a85d1aeb0ca0f2c830617c850a5277b53e`;
- CONFIRMED binds that exact PREPARED; re-frozen CONFIRMED digest is `caeb7b1cac2ff7b990ca54377fa2bd83b639a0af6e86478760de3ee27d5e6406`;
- updated `lab099_schema_vector_compatibility.py` to compose literal DDL -> frozen relation digest -> PREPARED/CONFIRMED vectors -> schema-identity oracle;
- PR #186 remains draft/test-only and mergeable, head `4d77115ccc3cffe2c2b320886329422717fb76d9`, ahead 9 / behind 0 versus pinned PR #177 head, with exactly six changed files, all under `experiments/provider_generation_history/tests/`;
- fixture mutation plans remain disabled/fail-closed; no production LAB-099 file changed.

Actually executed local test-owned evidence:
- `python3 -m py_compile` PASS for the new DDL oracle, updated authority-vector module, and compatibility module;
- standalone DDL-oracle self-check PASS;
- standalone authority-vector self-check PASS;
- local `git hash-object` exactly matched published GitHub blobs: DDL oracle `41f1fa650fa4554d44710fc1e717090e620e533b`, authority vectors `d1757fa667b8ab7ce4ea1b6ae27136f594716511`, compatibility module `b121c77a731d7b2aac0846eaffb18d72bcb4f59e`;
- composed compatibility function itself was not claimed executed because the exact imported schema-oracle module was not byte-exactly materialized into the executor through a supported path.

Durable evidence:
- `research/2026-09-12-lab099-ddl-vector-test-oracle-integration.md`, commit `25305516826224db6e9b5beebbd3ea05ed44d266`;
- #184 comment `5647156592`;
- PR #186 body updated to current V1 digest/vector state.

## Known failures / blockers
- LAB-086 remains priority #1. Exact local execution of the complete real-ledger closure is unavailable in this run.
- Direct shell transport cannot resolve `github.com`.
- Connector can read/write pinned source but cannot byte-exactly materialize the whole pinned closure into the executor in this run.
- Complete real-schema LAB-086 tests, unsafe expected-failure seed, full compileall, security reconciliation and current-main conflict audit remain pending.
- Keep PRs #165/#172/#173/#175/#177/#186 draft until their retained exact gates execute.
- PR #186 is RED-intent staging only. Exact physical V1 DDL, real relation digest, authority vectors and schema-identity oracle are now test-owned and mutually bound, but fixture mutation plans and production behavior remain disabled; no repository RED execution has been observed.
- The fixture adapter must not invent PREPARED/CONFIRMED evidence, provenance-parent advancement, or authenticator bytes.
- LAB-090..100 source/design evidence does not substitute for executable RED/GREEN proof.
- LAB-100 retains concrete regressions: verify historical activation evidence before restart recovery side effects; validate provider/verifier authority pairing before mutating `prepare_activation()`; bind activation state/anchor CAS/idempotency/identity under one provider authority; reject mutable caller-owned/fake subclass authority.
- Do not auto-upgrade existing unauthenticated LAB-090 rows; do not call provider prepare from an unauthenticated local recovery row; do not treat PR #177's LAB-092 V1 migration marker as proof of precursor governance.

## Exact next action
LAB-086 first: probe once for a newly supported non-model materialization path for pinned connector bytes at exact executable snapshot `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`. If available, materialize the exact manifest-listed implementation closure plus all `test_*.py` and the pinned LAB-085 fixture helper; verify every file with `git hash-object` against the pinned blob before import; execute all normal LAB-086 real-schema tests; run `unsafe_legacy_promotion_expected_failure.py` separately and require the intended failure; run full compileall; then perform final security/reconciliation and a fresh current-main conflict audit. Fix every observed blocker before changing draft/merge status.

If no supported exact materialization path exists, continue only PR #186 test-owned LAB-099 work: wire the now-frozen literal V1 DDL into `lab099_precursor_fixture_adapter.py` as explicit test-only mutation-plan input without adding production behavior. Make the smallest staged SQLite cases executable first: (1) orphan literal DDL without authenticated PREPARED must fail closed; (2) crash after atomic literal DDL + exact PREPARED must resume only that exact PREPARED. Preserve independently supplied canonical PREPARED/CONFIRMED bytes/authenticator inputs; the fixture must not fabricate authority. If the exact PR #186 test closure can be byte-exactly materialized, execute those cases and require observable RED before production implementation. If it still cannot be materialized, publish only the auditable adapter/test wiring and standalone checks that can genuinely execute; do not claim repository RED/GREEN.

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
- #184 / LAB-099 — READY + isolated RED-intent draft PR #186; physical V1 precursor relation, real relation digest, dual-HMAC persistence contract, byte-exact cutover vectors and test-owned DDL/schema oracles are now mutually bound; next fallback is test-only fixture mutation wiring, still no production behavior until executable RED.
- #185 / LAB-100 — READY/design-frozen; exact executable gates pending.
