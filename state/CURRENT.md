# Current Lab State

Last updated: 2026-09-12

## Active objective
LAB-086 — finish the exact executable/security gate for asymmetric break-glass history migration, then reconcile/merge only if every real-schema regression and current-main conflict audit passes.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165 at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`. Keep draft.
- LAB-092: #176 / draft PR #177, head `81673f8f6e4e0864dfa124735938c40aa28b4f2c`, base LAB-090.
- LAB-099 RED-intent staging: #184 / branch `lab-099-precursor-cutover-red-intent` / draft PR #186, head `41f50a4293e78b83b541cac017027d6cd6cf818a`, base PR #177 branch.
- Other open drafts retained: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175.
- Frozen design follow-up: LAB-093/#178 plus LAB-094..100/#179..185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected current open issues and active PRs; resumed LAB-086 first and re-probed exact materialization.

Current-run capability/evidence:
- Direct `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git /tmp/ai-runtime-lab` again failed before repository execution with `Could not resolve host: github.com` (exit 128).
- GitHub connector reads/writes remain available, but no supported byte-exact connector-to-local-executor materialization primitive is exposed.
- Therefore no new LAB-086 behavioral, unsafe-seed, compileall, security-reconciliation, conflict, LAB-099 RED, or LAB-099 GREEN PASS is claimed.

Completed the recorded LAB-099 fallback slice:
- added `experiments/provider_generation_history/tests/lab099_schema_vector_compatibility.py` to PR #186;
- it composes the independent byte-exact PREPARED/CONFIRMED reference vectors with the side-effect-free schema-identity oracle;
- the check maps only already-frozen fields: logical DB identity, LAB-092 completion, predecessor/resulting provenance head+epoch, exact relation-definition digest, exact PREPARED event digest, and CONFIRMED -> exact PREPARED binding;
- it contains no SQL, no mutation plan, no production API selection and is not named `test_*`;
- local `python -m py_compile` PASS;
- local `git hash-object` = `7a03017ea06cf5b0e4b3393ec4669209736bd465`, exactly matching the post-publication GitHub blob;
- the imported compatibility function itself was not executed because its exact imported PR modules cannot be materialized into the local executor through a supported path in this run;
- PR #186 remains `open`, `draft`, `mergeable=true`, ahead 6 / behind 0 against pinned PR #177 head, with exactly five changed files and all five under `experiments/provider_generation_history/tests/`.

Durable evidence:
- `research/2026-09-12-lab099-schema-vector-compatibility-boundary.md`, main commit `20309512e131360c6757db35f3d0054bf074d79d`;
- #184 comment `5646457194`;
- PR #186 body updated with the compatibility boundary and exact execution caveat.

## Known failures / blockers
- LAB-086 remains priority #1. Exact local execution of the complete real-ledger closure is unavailable in this run.
- Direct shell transport cannot resolve `github.com`.
- Connector can read/write pinned source but cannot byte-exactly materialize the whole pinned closure into the executor in this run.
- Complete real-schema LAB-086 tests, unsafe expected-failure seed, full compileall, security reconciliation and current-main conflict audit remain pending.
- Keep PRs #165/#172/#173/#175/#177/#186 draft until their retained exact gates execute.
- PR #186 is RED-intent staging only. Test-owned fixture adapter, independent authority vectors, schema-identity oracle and vector/oracle compatibility layer exist, but exact precursor DDL/mutation plans and LAB-099 production behavior do not; no repository RED execution has been observed.
- The fixture adapter must not invent precursor relation DDL, PREPARED/CONFIRMED evidence, provenance-parent advancement, or dual authenticator bytes. Missing/incomplete exact vectors must remain fail-closed.
- The synthetic `REFERENCE_ONLY_RELATION_DEFINITION_DIGEST` is not SQL authority and must never be promoted into production or treated as a schema-definition commitment.
- Exact precursor DDL remains an explicit protocol decision: frozen semantics do not uniquely determine physical SQLite spelling. No production LAB-099 behavior may be written until executable RED exists and the physical schema decision is independently frozen.
- The compatibility module's `py_compile`/blob match does not substitute for executing its imports, production RED/GREEN, or whole-repository tests.
- LAB-090..100 source/design evidence does not substitute for executable RED/GREEN proof.
- LAB-100 retains concrete regressions: verify historical activation evidence before restart recovery side effects; validate provider/verifier authority pairing before mutating `prepare_activation()`; bind activation state/anchor CAS/idempotency/identity under one provider authority; reject mutable caller-owned/fake subclass authority.
- LAB-098 source-level completeness/order seam is pinned, but exact repository RED/GREEN is pending.
- Do not bolt an unauthenticated digest/self-hash onto PR #175; do not auto-upgrade existing unauthenticated LAB-090 rows; do not call provider prepare from an unauthenticated local recovery row; do not treat PR #177's LAB-092 V1 migration marker as proof of precursor governance.

## Exact next action
LAB-086 first: probe once for a newly supported non-model materialization path for pinned connector bytes at exact executable snapshot `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`. If available, materialize the exact manifest-listed implementation closure plus all `test_*.py` and the pinned LAB-085 fixture helper; verify every file with `git hash-object` against the pinned blob before import; execute all normal LAB-086 real-schema tests; run `unsafe_legacy_promotion_expected_failure.py` separately and require the intended failure; run full compileall; then perform final security/reconciliation and a fresh current-main conflict audit. Fix every observed blocker before changing draft/merge status.

If no supported exact materialization path exists, continue LAB-099 without production changes. Next smallest safe slice: source-audit the exact LAB-090/LAB-092 SQLite schema/verification conventions on PRs #175/#177 and independently freeze a single explicit physical precursor relation identity only if one design can be justified from existing repository conventions and the already-frozen LAB-099 authority contract. Record column semantics, exact uniqueness requirements, canonical-body/authenticator persistence choice, relation-definition digest derivation, schema verification rule, and migration ownership. Do not wire the DDL into fixture mutation plans or production code in the same slice. If more than one materially different security-equivalent schema remains after the audit, record the ambiguity instead of guessing.

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
- #184 / LAB-099 — READY + isolated RED-intent draft PR #186; strict test-only fixture adapter, independent authority vectors, schema-identity oracle, and non-SQL vector/oracle compatibility check staged; exact physical DDL remains independently decision-gated; physical-schema audit is next if LAB-086 remains unexecutable.
- #185 / LAB-100 — READY/design-frozen; exact executable gates pending.
