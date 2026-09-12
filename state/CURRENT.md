# Current Lab State

Last updated: 2026-09-12

## Active objective
LAB-086 — finish the exact executable/security gate for asymmetric break-glass history migration, then reconcile/merge only if every real-schema regression and current-main conflict audit passes.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165 at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`. Keep draft.
- Fresh PR read this run: #165 remains open, draft, `mergeable=false`.
- Other open drafts retained: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175; LAB-092/#176 PR #177.
- Frozen design follow-up: LAB-093/#178 plus LAB-094..100/#179..185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; re-inspected open PRs; resumed LAB-086 first and re-probed exact materialization.

Current-run capability/evidence:
- Direct `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git` again failed before repository execution with `Could not resolve host: github.com`.
- GitHub connector reads/writes remain available, but no supported byte-exact connector-to-local-executor materialization primitive is exposed.
- Therefore no new LAB-086 behavioral, unsafe-seed, compileall, security-reconciliation or conflict PASS is claimed.

Completed the recorded LAB-099 precursor authenticator/runtime-identity slice against actual provider-history source, PR #175 source and the frozen canonical provenance/chain contracts.

New source-composed decision:
- Freeze `PROVIDER_ACTIVATION_RESERVATION_AUTHENTICATOR_IDENTITY_V1_FROZEN` in `research/2026-09-12-lab099-activation-reservation-authenticator-identity-contract.md`.
- `ytim.provider-activation-reservation.v1` binds logical DB identity, exact current provenance parent/epoch, old/new generation ids, successor provider id/generation/key-id, exact shared-anchor position, deterministic activation id and protocol version. `fence` is intentionally absent because it exists only after provider prepare; the final V2 event authenticates the exact returned ticket/fence.
- The precursor must be authenticated by BOTH the current predecessor and candidate successor provider-generation authorities. This is the source-compatible extension of current `TransitionProof.old_mac/new_mac`; successor-only or predecessor-only authorization is invalid.
- Stored descriptors alone do not prove that the concrete runtime provider is the successor. Before Tx R/provider mutation, require a fresh side-effect-free successor provider read verified through the exact successor verifier. Existing `AttestedCatchup.authenticated_read()` already proves provider id/generation/challenge/kind/MAC pairing; this closes the LAB-100 provider/verifier split before `prepare_activation()`.
- Tx R must recheck logical DB identity, exact provenance parent/epoch, old provider-generation head and shared-anchor tail, persist one unique precursor for that parent/activation id, and MUST NOT advance provider/provenance authority heads.
- Retry is authorized only while the exact precursor parent/head is still current and only for byte-identical same-id prepare. After head/epoch/provider-head change, the historical authenticator remains evidence only and carries no mutation authority.
- Provider reservation with no valid precursor fails closed. Existing LAB-090 rows without precursor/V2 provenance remain `LEGACY_LAB090_UNATTESTED`; never synthesize authorization from current mutable rows.
- Minimum 20-case RED matrix frozen, including one-sided authentication, provider/verifier mismatch, parent/head replay, forked precursor, restart after Tx R/pre-prepare and after prepare/pre-V2, legacy/unattested rows, and verify-before-recover composition.

Durable evidence:
- `research/2026-09-12-lab099-activation-reservation-authenticator-identity-contract.md`, main commit `427debbf7d3c12e97b5f4f612ebe17ac94209166`.
- #184 comment `5644155945` records the LAB-099 dual-authenticator + parent/head rules.
- #185 comment `5644156733` records the LAB-100 fresh provider/verifier preflight composition.

## Known failures / blockers
- LAB-086 remains priority #1. Exact local execution of the complete real-ledger closure is unavailable in this run.
- Direct shell transport cannot resolve `github.com`.
- Connector can read pinned source but cannot byte-exactly materialize the whole pinned closure into the executor in this run.
- Complete real-schema LAB-086 tests, unsafe expected-failure seed, full compileall, security reconciliation and current-main conflict audit remain pending.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-090..100 source/design evidence does not substitute for executable RED/GREEN proof.
- LAB-100 retains concrete regressions: verify historical activation evidence before restart recovery side effects; validate provider/verifier authority pairing before mutating `prepare_activation()`; bind activation state/anchor CAS/idempotency/identity under one provider authority; reject mutable caller-owned/fake subclass authority.
- LAB-098 source-level completeness/order seam is pinned, but exact repository RED/GREEN is pending.
- LAB-099 now has: canonical ticket digest; authenticated V2 transition-provenance storage seam; authenticated reservation precursor; atomic V2 ordering; dual predecessor+successor precursor authentication; fresh runtime provider/verifier preflight; parent/head replay retirement. Production implementation remains intentionally blocked on exact RED execution.
- Do not bolt an unauthenticated digest/self-hash onto PR #175; do not auto-upgrade existing unauthenticated LAB-090 rows; do not call provider prepare from an unauthenticated local recovery row; do not treat a successor descriptor/verifier alone as proof that the supplied provider object is paired to it.

## Exact next action
LAB-086 first: probe once for a newly supported non-model materialization path for pinned connector bytes at exact executable snapshot `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`. If available, materialize the exact manifest-listed implementation closure plus all `test_*.py` and the pinned LAB-085 fixture helper; verify every file with `git hash-object` against the pinned blob before import; execute all normal LAB-086 real-schema tests; run `unsafe_legacy_promotion_expected_failure.py` separately and require the intended failure; run full compileall; then perform final security/reconciliation and a fresh current-main conflict audit. Fix every observed blocker before changing draft/merge status.

Do not manually copy connector payloads into the executor. If no supported materialization path exists, continue source-level READY work without inventing contracts. Next inspect LAB-092 schema-migration provenance and LAB-097 initialization/cutover contracts plus the current PR #175 schema initialization path to pin the **minimum persisted relation/DDL ownership and migration rules for the precursor**: how `provider_activation_reservations` (or equivalent) is installed without ordinary-startup auto-DDL, how uniqueness over `(logical DB identity, parent link/epoch)` and `activation_id` is enforced, how authenticated old/new precursor tags are stored, and how legacy LAB-090 DBs are classified when the precursor relation is absent. Persist only source-proved schema/cutover rules and a minimum RED matrix; do not write production precursor code without exact executable REDs.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact complete real-ledger gate + unsafe seed + full compileall + current-main conflict/security audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending; startup mutation-order, provider/verifier precondition, authenticated reservation precursor and V2 provider/provenance atomic-head ordering findings recorded.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending; authenticated cutover composed with LAB-099 migration classification.
- #178 / LAB-093 — READY/design-frozen; exact RED/GREEN pending.
- #179..182 / LAB-094..097 — READY/design-frozen; exact executable gates pending.
- #183 / LAB-098 — READY; transition-derived activation presence/order seam and LAB-099 composition pinned; exact RED/GREEN pending.
- #184 / LAB-099 — READY; V2 transition provenance + reservation precursor/atomic ordering + dual authenticator/runtime pairing/parent replay contract frozen; next source-level slice is precursor relation/DDL migration ownership; exact RED/GREEN pending.
- #185 / LAB-100 — READY/design-frozen; exact executable gates pending; restart verify-before-recover and provider/verifier pairing regressions recorded and now composed with fresh authenticated-read preflight.
