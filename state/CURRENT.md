# Current Lab State

Last updated: 2026-09-12

## Active objective
LAB-086 — finish the exact executable/security gate for asymmetric break-glass history migration, then reconcile/merge only if every real-schema regression and current-main conflict audit passes.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165 at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`. Keep draft.
- LAB-092 PR #177 freshly re-read this run: open, draft, mergeable=true, head `81673f8f6e4e0864dfa124735938c40aa28b4f2c`, base LAB-090.
- Other open drafts retained: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175.
- Frozen design follow-up: LAB-093/#178 plus LAB-094..100/#179..185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; re-inspected open issues/PRs; resumed LAB-086 first and re-probed exact materialization.

Current-run capability/evidence:
- Direct `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git` failed before repository execution with `Could not resolve host: github.com` (exit 128).
- GitHub connector reads/writes remain available, but no supported byte-exact connector-to-local-executor materialization primitive is exposed.
- Therefore no new LAB-086 behavioral, unsafe-seed, compileall, security-reconciliation or conflict PASS is claimed.

Completed the recorded LAB-099 precursor cutover identity/one-way-upgrade slice against the frozen provenance canonical encoding, LAB-097 authenticated initialization/provenance rules, and the real PR #177 migration implementation.

New frozen contract:
- `PROVIDER_ACTIVATION_RESERVATION_PRECURSOR_CUTOVER_IDENTITY_ONE_WAY_UPGRADE_V1_FROZEN`
- Evidence: `research/2026-09-12-lab099-precursor-cutover-identity-one-way-upgrade.md`.
- Main research commit: `656b31dd78695a075b13ab5e0a38d3c65104c9b3`.
- #184 comment `5644691292`; #176 comment `5644692414`.

Source-proved/versioning decisions:
- PR #177's existing marker remains exactly the LAB-092 V1 activation-schema migration fact; it cannot be reinterpreted as precursor governance.
- The provenance V1 framing requires new domain/version identities for schema evolution, so precursor cutover uses distinct phase-specific authenticated objects rather than extra fields on the old marker.
- Freeze strict one-way state `ABSENT -> PREPARED -> CONFIRMED`; no downgrade/relabel edge exists.
- PREPARED consumes exact logical DB identity, exact authenticated LAB-092 completion digest, exact predecessor provenance head and epoch, exact precursor schema-definition digest/version, enabled transition-provenance protocol version, and nonce.
- CONFIRMED authenticates the exact PREPARED digest and resulting provenance head/epoch; a generic local status bit/version is insufficient.
- Crash before the atomic DDL+PREPARED transaction commits remains ABSENT and may retry only after fresh authenticated predecessor verification.
- Crash after atomic DDL+PREPARED commit but before CONFIRMED is `PREPARED_INCOMPLETE`; recovery may only finish that exact PREPARED, never create/adopt a sibling.
- Physical precursor DDL without PREPARED is `ORPHAN_UNAUTHENTICATED_SCHEMA`; PREPARED with missing/mismatched DDL is `AUTHENTICATED_CUTOVER_STORAGE_CORRUPTION`; CONFIRMED without exact PREPARED is `BROKEN_CUTOVER_PROVENANCE`. All fail closed with no ordinary-startup repair/adoption.
- A PREPARED built for parent P/epoch E cannot authorize a fresh cutover after parent/head advance. If that exact PREPARED was already durably linked, later recovery may recognize it only by authenticated ancestry through the event; wall-clock age/current-head equality is not authority.
- Once CONFIRMED, relation loss or operational-history deletion cannot fall back to LAB-092/LAB-090 semantics. The highest authenticated one-way cutover lineage defines the minimum accepted protocol generation.
- Existing `LEGACY_LAB090_UNATTESTED` rows remain non-upgradeable by hashing/backfilling mutable state.
- Frozen minimum 26-case RED-first matrix; no production precursor code written and no behavioral PASS claimed.

Relevant retained frozen LAB-099 contracts from prior runs:
- canonical activation-ticket digest and shared provenance encoding;
- separate authenticated V2 transition-provenance storage;
- authenticated reservation precursor before provider mutation;
- atomic V2 provider/provenance ordering;
- dual predecessor+successor precursor authentication;
- fresh runtime provider/verifier preflight and parent/head replay retirement;
- explicit precursor relation/DDL cutover ownership;
- separate versioned precursor cutover marker;
- new one-way PREPARED/CONFIRMED cutover identity and crash semantics above.

## Known failures / blockers
- LAB-086 remains priority #1. Exact local execution of the complete real-ledger closure is unavailable in this run.
- Direct shell transport cannot resolve `github.com`.
- Connector can read pinned source but cannot byte-exactly materialize the whole pinned closure into the executor in this run.
- Complete real-schema LAB-086 tests, unsafe expected-failure seed, full compileall, security reconciliation and current-main conflict audit remain pending.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-090..100 source/design evidence does not substitute for executable RED/GREEN proof.
- LAB-100 retains concrete regressions: verify historical activation evidence before restart recovery side effects; validate provider/verifier authority pairing before mutating `prepare_activation()`; bind activation state/anchor CAS/idempotency/identity under one provider authority; reject mutable caller-owned/fake subclass authority.
- LAB-098 source-level completeness/order seam is pinned, but exact repository RED/GREEN is pending.
- Do not bolt an unauthenticated digest/self-hash onto PR #175; do not auto-upgrade existing unauthenticated LAB-090 rows; do not call provider prepare from an unauthenticated local recovery row; do not treat PR #177's LAB-092 V1 migration marker as proof of later precursor DDL.

## Exact next action
LAB-086 first: probe once for a newly supported non-model materialization path for pinned connector bytes at exact executable snapshot `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`. If available, materialize the exact manifest-listed implementation closure plus all `test_*.py` and the pinned LAB-085 fixture helper; verify every file with `git hash-object` against the pinned blob before import; execute all normal LAB-086 real-schema tests; run `unsafe_legacy_promotion_expected_failure.py` separately and require the intended failure; run full compileall; then perform final security/reconciliation and a fresh current-main conflict audit. Fix every observed blocker before changing draft/merge status.

Do not manually copy connector payloads into the executor. If no supported exact materialization path exists, continue LAB-099 only by converting the frozen precursor cutover contract into repository RED-first tests on the real LAB-092/LAB-090 surfaces, without production behavior changes. Start with the smallest source-proved cases: (1) LAB-092 V1 completion alone does not authorize precursor governance; (2) orphan precursor DDL without PREPARED fails closed; (3) atomic DDL+PREPARED crash resumes only the exact PREPARED; (4) stale/forked predecessor parent+epoch replay is rejected; (5) CONFIRMED must bind the exact PREPARED digest; (6) valid CONFIRMED forbids downgrade/fallback after precursor relation deletion. If tests can be authored safely through the connector but cannot be executed, keep them isolated/RED-intent-only and do not modify production code or claim RED/GREEN execution.

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
- #184 / LAB-099 — READY; V2 transition provenance + authenticated reservation precursor/atomic ordering + dual authenticator/runtime pairing/parent replay + explicit relation/DDL cutover + distinct versioned marker + one-way PREPARED/CONFIRMED cutover identity frozen; exact RED/GREEN pending.
- #185 / LAB-100 — READY/design-frozen; exact executable gates pending; restart verify-before-recover and provider/verifier pairing regressions recorded and composed with fresh authenticated-read preflight.
