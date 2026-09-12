# Current Lab State

Last updated: 2026-09-12

## Active objective
LAB-086 — finish the exact executable/security gate for asymmetric break-glass history migration, then reconcile/merge only if every real-schema regression and current-main conflict audit passes.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165 at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`. Keep draft.
- LAB-092: #176 / draft PR #177, head `81673f8f6e4e0864dfa124735938c40aa28b4f2c`, base LAB-090.
- LAB-099 RED-intent staging: #184 / branch `lab-099-precursor-cutover-red-intent` / draft PR #186, head `339a0122b4e93add6eb6962fde92aaf4ea183356`, base PR #177 branch.
- Other open drafts retained: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175.
- Frozen design follow-up: LAB-093/#178 plus LAB-094..100/#179..185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected open PRs/issues; resumed LAB-086 first and re-probed exact materialization.

Current-run capability/evidence:
- Direct `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git /tmp/ai-runtime-lab` again failed before repository execution with `Could not resolve host: github.com` (exit 128).
- GitHub connector reads/writes remain available, but no supported byte-exact connector-to-local-executor materialization primitive is exposed.
- Therefore no new LAB-086 behavioral, unsafe-seed, compileall, security-reconciliation, conflict, LAB-099 RED, or LAB-099 GREEN PASS is claimed.

Completed the recorded LAB-099 fallback slice:
- froze a RED-owned, side-effect-free schema-identity reference boundary without choosing literal precursor DDL or a production API;
- published `experiments/provider_generation_history/tests/lab099_schema_identity_reference.py` on PR #186 at commit `339a0122b4e93add6eb6962fde92aaf4ea183356`;
- exact Git blob is `06f80aeb5a3203036a3964448d1c0dad266a8a30`;
- the reference freezes only already-decided authority relations: LAB-092-only is not precursor authority; PREPARED binds logical DB + LAB-092 completion + predecessor provenance head/epoch + exact relation-definition digest; CONFIRMED binds exact PREPARED + same relation digest + resulting head/epoch; missing/different schema, stale/forked lineage, and post-CONFIRMED downgrade fail closed;
- the reference contains no SQL, no migration mutations, no authenticator persistence layout and no production class/function contract;
- standalone reference self-check PASS and `python -m py_compile` PASS were actually executed before publication;
- post-publication local `git hash-object` returned exactly the GitHub blob above;
- PR #186 is ahead 5 / behind 0 against pinned PR #177 head and changes exactly four files, all under `experiments/provider_generation_history/tests/`.

Durable evidence:
- `research/2026-09-12-lab099-schema-identity-verifier-boundary.md`, main commit `9c1763dbcd9e887626fa32ed8da2fcbd6a7f0eb5`;
- #184 comment `5646150744`;
- PR #186 body updated with the new reference boundary and exact execution caveat.

## Known failures / blockers
- LAB-086 remains priority #1. Exact local execution of the complete real-ledger closure is unavailable in this run.
- Direct shell transport cannot resolve `github.com`.
- Connector can read/write pinned source but cannot byte-exactly materialize the whole pinned closure into the executor in this run.
- Complete real-schema LAB-086 tests, unsafe expected-failure seed, full compileall, security reconciliation and current-main conflict audit remain pending.
- Keep PRs #165/#172/#173/#175/#177/#186 draft until their retained exact gates execute.
- PR #186 is RED-intent staging only. The test-owned schema oracle and independent authority vectors exist, but exact precursor DDL/mutation plans and LAB-099 production behavior do not; no repository RED execution has been observed.
- The fixture adapter must not invent precursor relation DDL, PREPARED/CONFIRMED evidence, provenance-parent advancement, or dual authenticator bytes. Missing/incomplete exact vectors must remain fail-closed.
- The synthetic `REFERENCE_ONLY_RELATION_DEFINITION_DIGEST` is not SQL authority and must never be promoted into production or treated as a schema-definition commitment.
- Exact precursor DDL is implementation-gated: frozen semantics do not select one physical SQL identity. Choosing a literal DDL requires a separate explicit protocol decision plus RED coverage.
- The new schema-identity reference is an oracle only; its local PASS does not substitute for production RED/GREEN or whole-repository execution.
- LAB-090..100 source/design evidence does not substitute for executable RED/GREEN proof.
- LAB-100 retains concrete regressions: verify historical activation evidence before restart recovery side effects; validate provider/verifier authority pairing before mutating `prepare_activation()`; bind activation state/anchor CAS/idempotency/identity under one provider authority; reject mutable caller-owned/fake subclass authority.
- LAB-098 source-level completeness/order seam is pinned, but exact repository RED/GREEN is pending.
- Do not bolt an unauthenticated digest/self-hash onto PR #175; do not auto-upgrade existing unauthenticated LAB-090 rows; do not call provider prepare from an unauthenticated local recovery row; do not treat PR #177's LAB-092 V1 migration marker as proof of precursor governance.

## Exact next action
LAB-086 first: probe once for a newly supported non-model materialization path for pinned connector bytes at exact executable snapshot `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`. If available, materialize the exact manifest-listed implementation closure plus all `test_*.py` and the pinned LAB-085 fixture helper; verify every file with `git hash-object` against the pinned blob before import; execute all normal LAB-086 real-schema tests; run `unsafe_legacy_promotion_expected_failure.py` separately and require the intended failure; run full compileall; then perform final security/reconciliation and a fresh current-main conflict audit. Fix every observed blocker before changing draft/merge status.

If no supported exact materialization path exists, continue only PR #186 without production behavior changes. Next smallest safe slice: compose `lab099_schema_identity_reference.py` with the existing byte-exact `lab099_precursor_reference_vectors.py` and freeze one non-SQL RED-owned compatibility check proving that the PREPARED/CONFIRMED vector fields map exactly onto the schema-identity oracle (logical DB identity, LAB-092 completion, predecessor/resulting head+epoch, relation-definition digest, and exact PREPARED binding). The check may be test-only and side-effect free; it must not define literal DDL, enable fixture mutation plans, make RED-intent tests discoverable, or select production APIs. Execute and byte-verify only this isolated reference check if possible. Do not write LAB-099 production code until real RED execution is available and an explicit physical DDL decision is independently frozen.

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
- #184 / LAB-099 — READY + isolated RED-intent draft PR #186; strict test-only fixture adapter, independent authority vectors, and schema-identity reference oracle staged; exact physical DDL remains implementation-gated; vector/oracle non-SQL compatibility check is next.
- #185 / LAB-100 — READY/design-frozen; exact executable gates pending.
