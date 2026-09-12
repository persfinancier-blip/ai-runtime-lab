# Current Lab State

Last updated: 2026-09-12

## Active objective
LAB-086 — finish the exact executable/security gate for asymmetric break-glass history migration, then reconcile/merge only if every real-schema regression and current-main conflict audit passes.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165 at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`. Keep draft.
- LAB-092: #176 / draft PR #177, head `81673f8f6e4e0864dfa124735938c40aa28b4f2c`, base LAB-090.
- LAB-099 RED-intent staging: #184 / branch `lab-099-precursor-cutover-red-intent` / draft PR #186, head `96f0b9c9fa28142e1379e2a1c0932c808d4941d3`, base PR #177 branch.
- Other open drafts retained: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175.
- Frozen design follow-up: LAB-093/#178 plus LAB-094..100/#179..185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected active PR state; resumed LAB-086 first and re-probed exact materialization.

Current-run capability/evidence:
- Direct `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git /tmp/ai-runtime-lab` again failed before repository execution with `Could not resolve host: github.com` (exit 128).
- GitHub connector reads/writes remain available, but no supported byte-exact connector-to-local-executor materialization primitive is exposed.
- Therefore no new LAB-086 behavioral, unsafe-seed, compileall, security-reconciliation, conflict, LAB-099 RED, or LAB-099 GREEN PASS is claimed.

Completed the recorded LAB-099 fallback slice:
- source-audited pinned PR #177 physical-schema verification at head `81673f8f6e4e0864dfa124735938c40aa28b4f2c`;
- confirmed LAB-090 `_init_activation_schema()` compares normalized literal `_ACTIVATION_TABLE_SQL` and `_ACTIVATION_TRIGGER_SQL` against `sqlite_master.sql`, so physical SQL choice is security/correctness-visible rather than a semantics-free implementation detail;
- determined that the frozen LAB-099 semantic requirements do not uniquely determine one byte-exact SQLite DDL: table/column names and order, declared types, canonical-body vs decomposed storage, constraint/index spelling, authenticator layout, FK/rowid choices and related schema objects remain genuine protocol choices;
- froze `LAB099_EXACT_PRECURSOR_DDL_NOT_DERIVABLE_FROM_FROZEN_CONTRACTS_V1`;
- kept PR #186 unchanged and test-only; no mutation plans, literal precursor DDL or production LAB-099 behavior were added;
- kept `REFERENCE_ONLY_RELATION_DEFINITION_DIGEST` explicitly synthetic test data, not schema authority.

Durable evidence:
- `research/2026-09-12-lab099-exact-precursor-ddl-derivability-audit.md`, main commit `c8e6633a3ce245bc5687ade68a971926a9247a17`;
- #184 comment `5645836665`;
- pinned PR #177 source shows normalized literal SQL versus `sqlite_master.sql` schema verification.

## Known failures / blockers
- LAB-086 remains priority #1. Exact local execution of the complete real-ledger closure is unavailable in this run.
- Direct shell transport cannot resolve `github.com`.
- Connector can read/write pinned source but cannot byte-exactly materialize the whole pinned closure into the executor in this run.
- Complete real-schema LAB-086 tests, unsafe expected-failure seed, full compileall, security reconciliation and current-main conflict audit remain pending.
- Keep PRs #165/#172/#173/#175/#177/#186 draft until their retained exact gates execute.
- PR #186 is RED-intent staging only. Independent authority vectors exist, but exact precursor DDL/mutation plans and LAB-099 production behavior do not; no RED execution has been observed.
- The fixture adapter must not invent precursor relation DDL, PREPARED/CONFIRMED evidence, provenance-parent advancement, or dual authenticator bytes. Missing/incomplete exact vectors must remain fail-closed.
- The synthetic `REFERENCE_ONLY_RELATION_DEFINITION_DIGEST` is not SQL authority and must never be promoted into production or treated as a schema-definition commitment.
- Exact precursor DDL is now explicitly implementation-gated: the frozen semantics do not select one physical SQL identity. Choosing a literal DDL requires a separate explicit protocol decision plus RED coverage; it must not be smuggled in as an implied consequence of prior freezes.
- LAB-090..100 source/design evidence does not substitute for executable RED/GREEN proof.
- LAB-100 retains concrete regressions: verify historical activation evidence before restart recovery side effects; validate provider/verifier authority pairing before mutating `prepare_activation()`; bind activation state/anchor CAS/idempotency/identity under one provider authority; reject mutable caller-owned/fake subclass authority.
- LAB-098 source-level completeness/order seam is pinned, but exact repository RED/GREEN is pending.
- Do not bolt an unauthenticated digest/self-hash onto PR #175; do not auto-upgrade existing unauthenticated LAB-090 rows; do not call provider prepare from an unauthenticated local recovery row; do not treat PR #177's LAB-092 V1 migration marker as proof of precursor governance.

## Exact next action
LAB-086 first: probe once for a newly supported non-model materialization path for pinned connector bytes at exact executable snapshot `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`. If available, materialize the exact manifest-listed implementation closure plus all `test_*.py` and the pinned LAB-085 fixture helper; verify every file with `git hash-object` against the pinned blob before import; execute all normal LAB-086 real-schema tests; run `unsafe_legacy_promotion_expected_failure.py` separately and require the intended failure; run full compileall; then perform final security/reconciliation and a fresh current-main conflict audit. Fix every observed blocker before changing draft/merge status.

If no supported exact materialization path exists, continue only PR #186 without production behavior changes. Next smallest safe slice: derive and freeze the RED-owned **schema-identity verifier boundary** without choosing literal precursor DDL. Extend the isolated test intent/reference contract only as far as already-frozen semantics require: (1) LAB-092 V1 marker alone cannot authorize precursor schema; (2) PREPARED binds exactly one relation-definition digest plus current logical-DB/provenance-parent/epoch identity; (3) CONFIRMED binds the exact PREPARED digest; (4) missing or different physical-schema digest after PREPARED/CONFIRMED fails closed; (5) stale/forked parent+epoch cannot gain mutation authority; (6) post-CONFIRMED absence cannot downgrade to LAB-090 legacy semantics. Keep adapter DDL/mutation plans disabled and do not make RED-intent tests discoverable or write production LAB-099 behavior until byte-exact source execution is available and an explicit exact physical DDL decision is independently frozen.

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
- #184 / LAB-099 — READY + isolated RED-intent draft PR #186; strict test-only fixture adapter and independent authority vectors staged; exact physical DDL intentionally implementation-gated after derivability audit; schema-identity verifier RED contract is next.
- #185 / LAB-100 — READY/design-frozen; exact executable gates pending.
