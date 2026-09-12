# Current Lab State

Last updated: 2026-09-12

## Active objective
LAB-086 — finish the exact executable/security gate for asymmetric break-glass history migration, then reconcile/merge only if every real-schema regression and current-main conflict audit passes.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165 at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`. Keep draft.
- LAB-092: #176 / draft PR #177, pinned head `81673f8f6e4e0864dfa124735938c40aa28b4f2c`, base LAB-090.
- LAB-099 RED-intent staging: #184 / branch `lab-099-precursor-cutover-red-intent` / draft PR #186, head `41f50a4293e78b83b541cac017027d6cd6cf818a`, base PR #177 branch.
- Other retained drafts: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175.
- Frozen design follow-up: LAB-093/#178 plus LAB-094..100/#179..185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected open PRs/issues; resumed LAB-086 first and re-probed exact materialization.

Current-run capability/evidence:
- Direct `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git /tmp/ai-runtime-lab` again failed before repository execution with `Could not resolve host: github.com` (exit 128).
- GitHub connector reads/writes remain available, but no supported byte-exact connector-to-local-executor materialization primitive is exposed.
- Therefore no new LAB-086 behavioral, unsafe-seed, compileall, security-reconciliation, conflict, LAB-099 RED, or LAB-099 GREEN PASS is claimed.

Completed the recorded LAB-099 physical-schema audit without production changes:
- source-audited PR #175 LAB-090 conventions and PR #177 LAB-092 migration/schema verification conventions;
- PR #175 provider-generation history already persists transition authority as semantic scalar fields plus dual predecessor/successor HMAC-SHA256 values, reconstructing canonical semantic content rather than storing serialized canonical bytes;
- PR #175 activation schema and PR #177 migration verify literal normalized SQLite DDL through `sqlite_master`; PR #177 explicitly owns DDL+PREPARED in one `BEGIN IMMEDIATE`, with ordinary startup read-only for migration state;
- frozen `LAB099_PRECURSOR_PHYSICAL_RELATION_V1_FROZEN` in `research/2026-09-12-lab099-precursor-physical-relation-v1.md`;
- exact V1 table is `provider_activation_reservation_precursors` with semantic precursor columns, `activation_id TEXT PRIMARY KEY`, dual MAC columns, and `UNIQUE(logical_database_identity_digest,parent_chain_link_digest,parent_epoch)`;
- canonical precursor bytes are reconstructed from row semantics; canonical serialization/digest are not separately persisted;
- predecessor/successor authenticators are now frozen as HMAC-SHA256 over the identical `ytim.provider-activation-reservation.v1` canonical bytes, verified with `hmac.compare_digest` under predecessor/successor generation keys;
- digest/key/MAC identities use lowercase hex TEXT at rest; strict canonical DIGEST32 conversion remains application-verified;
- relation-definition digest is `SHA256(UTF8(_normalized_sql(EXACT_V1_DDL)))` = `696c54d1afdef52c05c120ce7d09a7a2eeb567daafb3a378b7dc4ca64f80e3bb`;
- explicit LAB-099 migration remains sole DDL owner: exact DDL + authenticated PREPARED atomically, separate exact CONFIRMED; startup never auto-repairs or auto-adopts;
- existing synthetic `REFERENCE_ONLY_RELATION_DEFINITION_DIGEST` in PR #186 is still test-only and must be explicitly replaced in a future test-only vector update; no fixture mutation plan was enabled.

Durable evidence:
- research note commit `563698be62660fa132750a3a389ff9d23e307a50`;
- #184 comment `5646771262`;
- PR #186 remains draft/test-only; no production LAB-099 files changed in this slice.

## Known failures / blockers
- LAB-086 remains priority #1. Exact local execution of the complete real-ledger closure is unavailable in this run.
- Direct shell transport cannot resolve `github.com`.
- Connector can read/write pinned source but cannot byte-exactly materialize the whole pinned closure into the executor in this run.
- Complete real-schema LAB-086 tests, unsafe expected-failure seed, full compileall, security reconciliation and current-main conflict audit remain pending.
- Keep PRs #165/#172/#173/#175/#177/#186 draft until their retained exact gates execute.
- PR #186 is RED-intent staging only. Test-owned fixture adapter, independent authority vectors, schema-identity oracle and vector/oracle compatibility layer exist; exact physical V1 DDL is now frozen but not wired into fixture mutation plans or production behavior; no repository RED execution has been observed.
- The fixture adapter must not invent PREPARED/CONFIRMED evidence, provenance-parent advancement, or authenticator bytes. Missing/incomplete exact vectors remain fail-closed.
- The synthetic `REFERENCE_ONLY_RELATION_DEFINITION_DIGEST` is superseded for future V1 schema-identity vectors by the real frozen digest but remains historical test-only data until an explicit PR #186 update changes it.
- LAB-090..100 source/design evidence does not substitute for executable RED/GREEN proof.
- LAB-100 retains concrete regressions: verify historical activation evidence before restart recovery side effects; validate provider/verifier authority pairing before mutating `prepare_activation()`; bind activation state/anchor CAS/idempotency/identity under one provider authority; reject mutable caller-owned/fake subclass authority.
- Do not auto-upgrade existing unauthenticated LAB-090 rows; do not call provider prepare from an unauthenticated local recovery row; do not treat PR #177's LAB-092 V1 migration marker as proof of precursor governance.

## Exact next action
LAB-086 first: probe once for a newly supported non-model materialization path for pinned connector bytes at exact executable snapshot `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`. If available, materialize the exact manifest-listed implementation closure plus all `test_*.py` and the pinned LAB-085 fixture helper; verify every file with `git hash-object` against the pinned blob before import; execute all normal LAB-086 real-schema tests; run `unsafe_legacy_promotion_expected_failure.py` separately and require the intended failure; run full compileall; then perform final security/reconciliation and a fresh current-main conflict audit. Fix every observed blocker before changing draft/merge status.

If no supported exact materialization path exists, continue only PR #186 test-owned LAB-099 work: replace the synthetic relation-definition digest in the independent reference/oracle layers with the frozen real V1 digest `696c54d1afdef52c05c120ce7d09a7a2eeb567daafb3a378b7dc4ca64f80e3bb`, add a test-only literal V1 DDL/schema-identity reference that recomputes that digest using the repository `_normalized_sql` rule without importing production LAB-099 code, and bind the existing non-SQL compatibility check to it. Do not enable fixture mutation plans and do not write production LAB-099 behavior in that same slice. Execute only standalone test-owned checks that can actually be materialized locally, `py_compile` them, and verify local `git hash-object` against the published GitHub blobs. If exact repository source execution becomes available, observe the staged LAB-099 cases RED before any production implementation.

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
- #184 / LAB-099 — READY + isolated RED-intent draft PR #186; physical V1 precursor relation, relation digest and dual-HMAC persistence contract now frozen; next fallback is test-only vector/schema identity update, still no mutation plans/production behavior until executable RED.
- #185 / LAB-100 — READY/design-frozen; exact executable gates pending.
