# Current Lab State

Last updated: 2026-09-12

## Active objective
LAB-086 — finish the exact executable/security gate for asymmetric break-glass history migration, then reconcile/merge only if every real-schema regression and current-main conflict audit passes.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165 at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`. Keep draft.
- Other open drafts inspected: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175; LAB-092/#176 PR #177.
- Frozen design follow-up: LAB-093/#178 plus LAB-094..100/#179..185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected active PRs; resumed LAB-086 first and re-probed exact materialization.

Current-run capability/evidence:
- Direct `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git` again failed before repository execution with `Could not resolve host: github.com`.
- GitHub connector reads/writes remain available, but no supported byte-exact connector-to-local-executor materialization primitive is exposed. Manual/model reserialization of the security-critical LAB-086 closure remains prohibited.
- Therefore no new LAB-086 behavioral, unsafe-seed, compileall, security-reconciliation or conflict PASS is claimed.

Completed the recorded LAB-098/#183 + LAB-099/#184 composition audit against actual PR #175 transition/history schemas.

Source-proved result:
- LAB-098 can be enforced on the current relational shape with two read-only anti-joins after provider-generation transition authenticity is established: transition->activation must have no missing row and activation->transition must have no extra row; the existing PK/UNIQUE constraints then establish one-to-one presence for every governed non-bootstrap transition.
- These checks must complete before `_recover_pending_activation()` so deleted/tampered provenance cannot trigger provider or SQLite recovery mutation.
- LAB-099 cannot be closed by a local `_verify_activation_records()` patch or a self-hash in the mutable activation row. PR #175 `provider_generation_transitions` has no authenticated activation-ticket commitment, so the original historical `expected_position`/`activation_id`/`fence` is otherwise unrecoverable after coherent rewrite.
- A sound LAB-099 GREEN therefore requires a versioned authenticated transition/provenance delta carrying the frozen V1 `activation_ticket_digest`; merely adding an unauthenticated SQL column is insufficient.
- Because `expected_position` and provider-assigned `fence` exist only after `prepare_activation()`, the new protocol must prepare the exact reservation before constructing/signing the activation-aware transition, or cryptographically bind an equivalent authenticated handoff record into that transition.
- Regression composition must include a tampered historical activation plus a recoverable current pending activation and assert constructor failure occurs before any current provider commit/release or SQLite mutation. This composes directly with LAB-100 verify-before-recover.

Durable evidence:
- `research/2026-09-12-lab098-lab099-minimal-regression-first-composition.md`, main commit `a8044355201d843846702e2514b0add543ed6238`.
- #183 comment `5643117814` records the anti-join/order seam.
- #184 comment `5643118351` records the authenticated transition/schema boundary and rotation-order implication.

## Known failures / blockers
- LAB-086 remains priority #1. Exact local execution of the complete real-ledger closure is unavailable in this run.
- Direct shell transport cannot resolve `github.com`.
- Connector can read pinned source but cannot byte-exactly materialize the whole pinned closure into the executor in this run.
- Complete real-schema LAB-086 tests, unsafe expected-failure seed, full compileall, security reconciliation and current-main conflict audit remain pending.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-090..100 source/design evidence does not substitute for executable RED/GREEN proof.
- LAB-100 retains two concrete regressions: verify historical activation evidence before restart recovery side effects; validate provider/verifier authority pairing before mutating `prepare_activation()`.
- LAB-098 source-level completeness/order seam is pinned, but exact repository RED/GREEN is pending.
- LAB-099 necessarily crosses authenticated transition/schema versioning; do not bolt an unauthenticated digest or self-hash onto PR #175.

## Exact next action
LAB-086 first: probe once for a newly supported non-model materialization path for pinned connector bytes at exact executable snapshot `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`. If available, materialize the exact manifest-listed implementation closure plus all `test_*.py` and the pinned LAB-085 fixture helper; verify every file with `git hash-object` against the pinned blob before import; execute all normal LAB-086 real-schema tests; run `unsafe_legacy_promotion_expected_failure.py` separately and require the intended failure; run full compileall; then perform final security/reconciliation and a fresh current-main conflict audit. Fix every observed blocker before changing draft/merge status.

Do not manually copy connector payloads into the executor. If no supported materialization path exists, continue source-level READY work without inventing contracts. Next inspect LAB-092 PR #177 plus LAB-097/#182 frozen provenance/schema contracts and determine the smallest versioned storage seam for authenticated `activation_ticket_digest`: whether to version `provider_generation_transitions` directly or add a new authenticated provenance relation, how explicit migration classifies pre-LAB-099 histories, and how constructor ordering verifies that version before recovery. Persist only source-proved schema/ordering evidence; do not write partial production provenance code without executable REDs.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact complete real-ledger gate + unsafe seed + full compileall + current-main conflict/security audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending; startup mutation-order and provider/verifier precondition audits have concrete findings.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178 / LAB-093 — READY/design-frozen; exact RED/GREEN pending.
- #179..182 / LAB-094..097 — READY/design-frozen; exact executable gates pending.
- #183 / LAB-098 — READY; transition-derived activation presence/order seam and LAB-099 composition pinned; exact RED/GREEN pending.
- #184 / LAB-099 — READY; authenticated ticket-content provenance requires versioned transition/schema composition; exact RED/GREEN pending.
- #185 / LAB-100 — READY/design-frozen; exact executable gates pending; restart verify-before-recover and provider/verifier pairing regressions recorded.
