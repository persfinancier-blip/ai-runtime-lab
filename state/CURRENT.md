# Current Lab State

Last updated: 2026-09-12

## Active objective
LAB-086 — finish the exact executable/security gate for asymmetric break-glass history migration, then reconcile/merge only if every real-schema regression and current-main conflict audit passes.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165 at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`. Keep draft.
- Fresh PR read this run: #165 remains open, draft, `mergeable=false`.
- Current compare after this run's main commits: LAB-086 branch is diverged, ahead 195 / behind 876, merge-base `d2c9781f5a60dc9b8b94fc8dba651f804a73e509`.
- Other open drafts retained: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175; LAB-092/#176 PR #177.
- Frozen design follow-up: LAB-093/#178 plus LAB-094..100/#179..185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; re-inspected open issues/PRs; resumed LAB-086 first and re-probed exact materialization.

Current-run capability/evidence:
- Direct `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git` again failed before repository execution with `Could not resolve host: github.com`.
- GitHub connector reads/writes remain available, but no supported byte-exact connector-to-local-executor materialization primitive is exposed.
- Therefore no new LAB-086 behavioral, unsafe-seed, compileall, security-reconciliation or conflict PASS is claimed.

Completed the recorded LAB-099 precursor relation/DDL ownership slice against PR #175 source, PR #177 LAB-092 migration source, LAB-097 deletion-provenance evidence and the frozen LAB-094..096 retained-authority graph.

New source/schema decisions:
- Freeze `PROVIDER_ACTIVATION_RESERVATION_RELATION_DDL_CUTOVER_V1_FROZEN` in `research/2026-09-12-lab099-reservation-precursor-relation-ddl-cutover.md`.
- The precursor is a distinct pre-transition authenticated authority object. Its dedicated relation is unique by `activation_id` and by `(logical DB identity, provenance parent link, parent epoch)` so sibling reservations fail at the DB boundary.
- The precursor cannot require an already-existing `provider_generation_transitions` row at insertion: Tx R must exist before provider `prepare_activation()` and before the generation transition/V2 ticket event. Later V2 verification composes precursor -> governed transition -> exact activation ticket one-to-one.
- Ordinary startup must never auto-create/repair the governed precursor relation. Explicit migration follows LAB-092: verify eligibility/history, `BEGIN IMMEDIATE`, install exact DDL + deterministic PREPARED cutover evidence atomically, then externally/authentically confirm. Confirmed cutover + missing/mismatched DDL fails closed.
- Existing LAB-090 activation rows without independently authenticated precursor/V2 ticket evidence are `LEGACY_LAB090_UNATTESTED` and are not migration-eligible; never hash/backfill current mutable rows into authority.
- Relation absence is not freshness. Complete provider-history deletion + missing precursor DDL remains LAB-097 fail-closed, not a fresh-install signal.
- Minimum 20-case RED-first matrix frozen; no production code written without exact executable REDs.

Additional source-proved versioning boundary:
- PR #177's existing CONFIRMED marker is exactly `migration:provider-generation-activation-schema:v1` with payload `{schema: provider-generation-activation, version: 1}`. It does not authenticate precursor relation/protocol semantics.
- Freeze `LAB099_PRECURSOR_CUTOVER_MARKER_VERSIONING_V1_FROZEN` in `research/2026-09-12-lab099-precursor-cutover-marker-versioning-addendum.md`.
- Do not reinterpret the historical LAB-092 V1 marker. Precursor governance requires a new authenticated versioned cutover event committing to logical history identity, precursor schema/protocol version, enabled transition-provenance version, predecessor cutover/head and exact schema-set/DDL identity.

Durable evidence:
- main commit `1b510762f42151d922aeb06277ae548aa411f54e` — precursor relation/DDL cutover contract.
- main commit `58f6f7b65483fe5f9f6967c059b2d2d10e7fe9bb` — precursor cutover marker versioning addendum.
- #184 comments `5644413908`, `5644418779`.
- #176 comment `5644414428`.
- #182 comment `5644415216`.

## Known failures / blockers
- LAB-086 remains priority #1. Exact local execution of the complete real-ledger closure is unavailable in this run.
- Direct shell transport cannot resolve `github.com`.
- Connector can read pinned source but cannot byte-exactly materialize the whole pinned closure into the executor in this run.
- Complete real-schema LAB-086 tests, unsafe expected-failure seed, full compileall, security reconciliation and current-main conflict audit remain pending.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-090..100 source/design evidence does not substitute for executable RED/GREEN proof.
- LAB-100 retains concrete regressions: verify historical activation evidence before restart recovery side effects; validate provider/verifier authority pairing before mutating `prepare_activation()`; bind activation state/anchor CAS/idempotency/identity under one provider authority; reject mutable caller-owned/fake subclass authority.
- LAB-098 source-level completeness/order seam is pinned, but exact repository RED/GREEN is pending.
- LAB-099 now has: canonical ticket digest; separate authenticated V2 transition-provenance storage; authenticated reservation precursor; atomic V2 ordering; dual predecessor+successor precursor authentication; fresh runtime provider/verifier preflight; parent/head replay retirement; explicit precursor relation/DDL cutover ownership; separate versioned precursor cutover marker. Production implementation remains intentionally blocked on exact RED execution.
- Do not bolt an unauthenticated digest/self-hash onto PR #175; do not auto-upgrade existing unauthenticated LAB-090 rows; do not call provider prepare from an unauthenticated local recovery row; do not treat PR #177's LAB-092 V1 migration marker as proof of later precursor DDL.

## Exact next action
LAB-086 first: probe once for a newly supported non-model materialization path for pinned connector bytes at exact executable snapshot `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`. If available, materialize the exact manifest-listed implementation closure plus all `test_*.py` and the pinned LAB-085 fixture helper; verify every file with `git hash-object` against the pinned blob before import; execute all normal LAB-086 real-schema tests; run `unsafe_legacy_promotion_expected_failure.py` separately and require the intended failure; run full compileall; then perform final security/reconciliation and a fresh current-main conflict audit. Fix every observed blocker before changing draft/merge status.

Do not manually copy connector payloads into the executor. If no supported materialization path exists, continue source-level READY work without inventing contracts. Next inspect the frozen global provenance-chain event/epoch rules plus PR #177 migration implementation and LAB-099 V2 transition-provenance seam to pin the **minimum new precursor cutover event identity and one-way upgrade ordering**: whether it is a separate deterministic migration intent or a new schema-set version, how it binds the existing LAB-092 V1 completion without reinterpreting it, what exact predecessor head/epoch it consumes, and how crash after PREPARED / before CONFIRMED is classified. Persist only source-proved/versioning rules and a minimum RED matrix; do not write production precursor code without exact executable REDs.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact complete real-ledger gate + unsafe seed + full compileall + current-main conflict/security audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending; startup mutation-order, provider/verifier precondition, authenticated reservation precursor and V2 provider/provenance atomic-head ordering findings recorded.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending; existing V1 migration marker explicitly does not cover future precursor relation semantics.
- #178 / LAB-093 — READY/design-frozen; exact RED/GREEN pending.
- #179..182 / LAB-094..097 — READY/design-frozen; exact executable gates pending.
- #183 / LAB-098 — READY; transition-derived activation presence/order seam and LAB-099 composition pinned; exact RED/GREEN pending.
- #184 / LAB-099 — READY; V2 transition provenance + authenticated reservation precursor/atomic ordering + dual authenticator/runtime pairing/parent replay + explicit relation/DDL cutover + versioned new cutover-marker requirement frozen; exact RED/GREEN pending.
- #185 / LAB-100 — READY/design-frozen; exact executable gates pending; restart verify-before-recover and provider/verifier pairing regressions recorded and composed with fresh authenticated-read preflight.
