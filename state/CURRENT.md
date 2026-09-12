# Current Lab State

Last updated: 2026-09-12

## Active objective
LAB-086 — finish the exact executable/security gate for asymmetric break-glass history migration, then reconcile/merge only if every real-schema regression and current-main conflict audit passes.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165 at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`. Keep draft.
- LAB-092: #176 / draft PR #177, head `81673f8f6e4e0864dfa124735938c40aa28b4f2c`, base LAB-090.
- LAB-099 RED-intent staging: #184 / branch `lab-099-precursor-cutover-red-intent` / draft PR #186, head `fc4456690b732b3e111379200bba58cf21af9ec8`, base PR #177 branch.
- Other open drafts retained: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175.
- Frozen design follow-up: LAB-093/#178 plus LAB-094..100/#179..185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected current open issues and active PRs; resumed LAB-086 first and re-probed exact materialization.

Current-run capability/evidence:
- Direct `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git /tmp/ai-runtime-lab` again failed before repository execution with `Could not resolve host: github.com` (exit 128).
- GitHub connector reads/writes remain available, but no supported byte-exact connector-to-local-executor materialization primitive is exposed.
- Therefore no new LAB-086 behavioral, unsafe-seed, compileall, security-reconciliation, conflict, LAB-099 RED, or LAB-099 GREEN PASS is claimed.

Completed the recorded LAB-099 fallback slice on PR #186:
- re-read the frozen precursor relation/DDL, canonical provenance-chain, logical-DB/history identity and PREPARED/CONFIRMED contracts;
- found that exact precursor SQL spelling is intentionally still implementation-gated, while PREPARED/CONFIRMED and precursor authorization require canonical authenticated bytes and parent/head/epoch lineage;
- therefore rejected a helper design that would guess DDL or synthesize self-asserted phase rows/digests/authenticators;
- added test-only `experiments/provider_generation_history/tests/lab099_precursor_fixture_adapter.py` at branch commit `fc4456690b732b3e111379200bba58cf21af9ec8`;
- adapter owns only mechanical SQLite mutation and fails closed unless a future independent byte-exact fixture-vector module supplies the exact authority-bearing plans/bytes;
- no production `*_for_test_only` hooks and no production files were added or changed.

Post-write topology against pinned PR #177 head `81673f8f6e4e0864dfa124735938c40aa28b4f2c`:
- ahead 3 / behind 0;
- exactly two changed files, both under `experiments/provider_generation_history/tests/`;
- PR #186 remains open, draft and mergeable.

Durable evidence:
- `research/2026-09-12-lab099-test-fixture-adapter-vector-boundary.md`, main commit `386d2ef29a48245d4e5f2d90697ebbf4ee593205`;
- decision `LAB099_TEST_FIXTURE_INDEPENDENT_VECTOR_BOUNDARY_V1_FROZEN`;
- #184 comment `5645318427`;
- PR #186 body updated with current adapter/vector boundary and execution caveat.

## Known failures / blockers
- LAB-086 remains priority #1. Exact local execution of the complete real-ledger closure is unavailable in this run.
- Direct shell transport cannot resolve `github.com`.
- Connector can read pinned source but cannot byte-exactly materialize the whole pinned closure into the executor in this run.
- Complete real-schema LAB-086 tests, unsafe expected-failure seed, full compileall, security reconciliation and current-main conflict audit remain pending.
- Keep PRs #165/#172/#173/#175/#177/#186 draft until their retained exact gates execute.
- PR #186 is RED-intent staging only. The test-only adapter now exists, but the independent byte-exact fixture-vector bundle and LAB-099 production module do not; no RED execution has been observed.
- The adapter must not invent precursor relation DDL, PREPARED/CONFIRMED evidence, provenance-parent advancement, or dual authenticator bytes. Missing/incomplete exact vectors must remain fail-closed.
- LAB-090..100 source/design evidence does not substitute for executable RED/GREEN proof.
- LAB-100 retains concrete regressions: verify historical activation evidence before restart recovery side effects; validate provider/verifier authority pairing before mutating `prepare_activation()`; bind activation state/anchor CAS/idempotency/identity under one provider authority; reject mutable caller-owned/fake subclass authority.
- LAB-098 source-level completeness/order seam is pinned, but exact repository RED/GREEN is pending.
- Do not bolt an unauthenticated digest/self-hash onto PR #175; do not auto-upgrade existing unauthenticated LAB-090 rows; do not call provider prepare from an unauthenticated local recovery row; do not treat PR #177's LAB-092 V1 migration marker as proof of precursor governance.

## Exact next action
LAB-086 first: probe once for a newly supported non-model materialization path for pinned connector bytes at exact executable snapshot `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`. If available, materialize the exact manifest-listed implementation closure plus all `test_*.py` and the pinned LAB-085 fixture helper; verify every file with `git hash-object` against the pinned blob before import; execute all normal LAB-086 real-schema tests; run `unsafe_legacy_promotion_expected_failure.py` separately and require the intended failure; run full compileall; then perform final security/reconciliation and a fresh current-main conflict audit. Fix every observed blocker before changing draft/merge status.

If no supported exact materialization path exists, continue only PR #186 without production behavior changes. Next smallest safe slice: source-audit the frozen canonical provenance encoder and add an **independent test-vector contract/module** for authority bytes that are already fully specified (precursor canonical fields/domain, dual predecessor/successor authenticator reference inputs, PREPARED domain/fields, CONFIRMED exact-PREPARED binding, parent/head/epoch reference values). Do not guess the still implementation-gated exact precursor SQL spelling; leave DDL mutation plans unavailable/fail-closed until an exact RED-owned DDL identity is legitimately frozen. Keep vector generation independent from future production LAB-099 behavior. If exact execution is still unavailable, persist only source-audited reference vectors/contracts and do not claim RED.

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
- #184 / LAB-099 — READY + isolated RED-intent draft PR #186; strict test-only fixture adapter staged; independent exact vectors and observed REDs pending before production behavior.
- #185 / LAB-100 — READY/design-frozen; exact executable gates pending.
