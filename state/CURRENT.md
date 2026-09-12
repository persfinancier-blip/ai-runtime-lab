# Current Lab State

Last updated: 2026-09-12

## Active objective
LAB-086 — finish the exact executable/security gate for asymmetric break-glass history migration, then reconcile/merge only if every real-schema regression and current-main conflict audit passes.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165 at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`. Keep draft.
- Other open drafts inspected: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175; LAB-092/#176 PR #177.
- Frozen design follow-up: LAB-093/#178 plus LAB-094..100/#179..185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; re-inspected the active PR set; resumed LAB-086 first and re-probed exact materialization.

Current-run capability/evidence:
- Direct `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git` again failed before repository execution with `Could not resolve host: github.com`.
- GitHub connector reads/writes remain available, but no supported byte-exact connector-to-local-executor materialization primitive is exposed. Manual/model reserialization of the security-critical LAB-086 closure remains prohibited.
- Therefore no new LAB-086 behavioral, unsafe-seed, compileall, security-reconciliation or conflict PASS is claimed.

Completed the recorded LAB-092/LAB-097/LAB-099 storage/versioning audit against actual PR #175/#177 source plus the frozen provenance-chain contracts.

Source-proved decision:
- Do not ALTER legacy `provider_generation_transitions` into a mixed V1/V2 proof row. Current V1 `old_mac/new_mac` authenticate only provider id + old generation id + new generation id; adding a digest column beside those MACs would leave the LAB-099 digest unauthenticated unless the proof meaning is replaced.
- The smallest sound seam is a separate one-to-one authenticated provider-transition provenance event keyed by `new_generation_id`. Its V2 authenticators must cover the frozen `activation_ticket_digest`, activation/transition protocol versions and provenance-chain parent; the legacy transition row remains a compatibility/structural projection.
- This matches `AUTHENTICATED_PROVENANCE_CHAIN_LINK_V1_FROZEN`, which already requires domain-specific event payloads to be stored separately from global chain links.
- LAB-098 presence and LAB-099 content checks then share one authority source: every governed post-cutover transition must have exactly one authenticated provenance event and exactly one activation row, and the canonical ticket digest must match before recovery.
- Pre-LAB-090 transitions may remain explicitly legacy before an authenticated LAB-092/provenance cutover; do not fabricate historical tickets for them.
- Existing LAB-090 activation rows that were created without authenticated ticket commitments cannot be silently upgraded by hashing current mutable rows. That would bless coherent tampering. Classify such state as legacy/unattested and fail closed under the V2 supported surface unless a future explicit re-attestation/import protocol has independently authenticated original ticket evidence.
- Constructor order remains verify-only through initialization/migration provenance, provider history, V2 transition provenance, LAB-098 cardinality and LAB-099 ticket digest before `_recover_pending_activation()` or any provider/SQLite mutation.

Durable evidence:
- `research/2026-09-12-lab099-versioned-transition-provenance-storage-seam.md`, main commit `3642bd484c6dfb6b36e4dd21cf85aa2239376729`.
- #184 comment `5643413886` records the separate V2 provenance relation and no-hash-and-bless migration rule.
- #176 comment `5643414268` records the LAB-092 cutover interaction.

## Known failures / blockers
- LAB-086 remains priority #1. Exact local execution of the complete real-ledger closure is unavailable in this run.
- Direct shell transport cannot resolve `github.com`.
- Connector can read pinned source but cannot byte-exactly materialize the whole pinned closure into the executor in this run.
- Complete real-schema LAB-086 tests, unsafe expected-failure seed, full compileall, security reconciliation and current-main conflict audit remain pending.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-090..100 source/design evidence does not substitute for executable RED/GREEN proof.
- LAB-100 retains two concrete regressions: verify historical activation evidence before restart recovery side effects; validate provider/verifier authority pairing before mutating `prepare_activation()`.
- LAB-098 source-level completeness/order seam is pinned, but exact repository RED/GREEN is pending.
- LAB-099 now has a pinned storage/versioning seam, but production implementation remains intentionally blocked on exact RED execution. Do not bolt an unauthenticated digest/self-hash onto PR #175 and do not auto-upgrade existing unauthenticated LAB-090 rows.

## Exact next action
LAB-086 first: probe once for a newly supported non-model materialization path for pinned connector bytes at exact executable snapshot `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`. If available, materialize the exact manifest-listed implementation closure plus all `test_*.py` and the pinned LAB-085 fixture helper; verify every file with `git hash-object` against the pinned blob before import; execute all normal LAB-086 real-schema tests; run `unsafe_legacy_promotion_expected_failure.py` separately and require the intended failure; run full compileall; then perform final security/reconciliation and a fresh current-main conflict audit. Fix every observed blocker before changing draft/merge status.

Do not manually copy connector payloads into the executor. If no supported materialization path exists, continue source-level READY work without inventing contracts. Next inspect the frozen canonical transition/event encoding plus PR #175 `rotate_provider()` transaction boundaries and pin the minimal atomic persistence/recovery state machine for the separate V2 provider-transition provenance event: exact ordering of `prepare_activation()` -> V2 event authentication -> SQLite transition/activation/event persistence -> provenance-chain append -> provider commit/release, including UNKNOWN/crash states and the rule for a V2 event/activation/legacy-transition partial commit. Persist only source-proved ordering/recovery evidence; do not write production provenance code without executable REDs.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact complete real-ledger gate + unsafe seed + full compileall + current-main conflict/security audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending; startup mutation-order and provider/verifier precondition audits have concrete findings.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending; authenticated cutover now composed with LAB-099 migration classification.
- #178 / LAB-093 — READY/design-frozen; exact RED/GREEN pending.
- #179..182 / LAB-094..097 — READY/design-frozen; exact executable gates pending.
- #183 / LAB-098 — READY; transition-derived activation presence/order seam and LAB-099 composition pinned; exact RED/GREEN pending.
- #184 / LAB-099 — READY; separate authenticated V2 transition-provenance relation frozen; migration classification pinned; atomic persistence/recovery ordering is the next source-level slice; exact RED/GREEN pending.
- #185 / LAB-100 — READY/design-frozen; exact executable gates pending; restart verify-before-recover and provider/verifier pairing regressions recorded.
