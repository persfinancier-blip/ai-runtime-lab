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
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; re-inspected open issues/PRs; resumed LAB-086 first and re-probed exact materialization.

Current-run capability/evidence:
- Direct `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git` again failed before repository execution with `Could not resolve host: github.com`.
- GitHub connector reads/writes remain available, but no supported byte-exact connector-to-local-executor materialization primitive is exposed.
- Therefore no new LAB-086 behavioral, unsafe-seed, compileall, security-reconciliation or conflict PASS is claimed.

Completed the recorded LAB-099 atomic persistence/recovery ordering slice against actual PR #175 source plus the frozen provenance contracts.

New source-composed finding/decision:
- PR #175 can derive deterministic `activation_id` before provider prepare, but provider-assigned `fence` exists only after `prepare_activation()`. The frozen LAB-099 V2 event must authenticate the exact ticket digest including `fence`.
- Therefore the final V2 transition cannot be frozen before provider prepare, while provider prepare cannot safely happen before all durable authenticated intent: a crash after prepare with no authenticated local precursor leaves an external provider fence that startup cannot prove was authorized without reconstructing intent from mutable rows.
- Freeze a separate authenticated `ytim.provider-activation-reservation.v1` precursor bound to logical DB identity, current provenance parent/epoch, exact old/new generation identities, provider id, exact shared-anchor expected position, deterministic activation id and protocol versions. It authorizes only one reversible/idempotent same-id provider reservation; it does not advance provider history/provenance authority.
- Ordering is now: verify -> Tx R persist authenticated reservation precursor -> idempotent `prepare_activation()` -> Tx A freeze exact ticket + V2 transition event + successor provenance link + exact LAB-080 intent, with no authority-head advance -> execute/reconcile exact LAB-080 anchor -> Tx B atomically advance provider-generation head **and** authenticated provenance-chain head plus activation SQL recovery state -> provider commit/reconcile while fenced -> durable activation acknowledgement -> exact release.
- Tx B must be the single SQLite authority commit. Do not expose a state where `provider_generation_head` is new while authenticated provenance head is old, or vice versa.
- Restart with authenticated precursor but no V2 event may only re-run/reconcile the same deterministic prepare request; provider reservation with no authenticated precursor fails closed. Existing LAB-090 rows without precursor/V2 provenance remain `LEGACY_LAB090_UNATTESTED`; never synthesize provenance from them.
- This composes with LAB-100: provider/verifier authority pairing must be validated before Tx R/provider prepare, and all historical activation/V2 evidence must verify before any restart provider/SQLite recovery mutation.

Durable evidence:
- `research/2026-09-12-lab099-provider-activation-provenance-atomic-state-machine.md`, main commit `6586ff89a86459151d132c5802a263778e86bedc`.
- #184 comment `5643730420` records the LAB-099 precursor + atomic V2 ordering.
- #169 comment `5643730926` records the LAB-090 transaction-boundary correction.

## Known failures / blockers
- LAB-086 remains priority #1. Exact local execution of the complete real-ledger closure is unavailable in this run.
- Direct shell transport cannot resolve `github.com`.
- Connector can read pinned source but cannot byte-exactly materialize the whole pinned closure into the executor in this run.
- Complete real-schema LAB-086 tests, unsafe expected-failure seed, full compileall, security reconciliation and current-main conflict audit remain pending.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-090..100 source/design evidence does not substitute for executable RED/GREEN proof.
- LAB-100 retains two concrete regressions: verify historical activation evidence before restart recovery side effects; validate provider/verifier authority pairing before mutating `prepare_activation()`.
- LAB-098 source-level completeness/order seam is pinned, but exact repository RED/GREEN is pending.
- LAB-099 now has both the separate authenticated V2 transition-provenance storage seam and the provider-specific crash-safe ordering seam. Production implementation remains intentionally blocked on exact RED execution. Do not bolt an unauthenticated digest/self-hash onto PR #175; do not auto-upgrade existing unauthenticated LAB-090 rows; do not call provider prepare from an unauthenticated local recovery row.

## Exact next action
LAB-086 first: probe once for a newly supported non-model materialization path for pinned connector bytes at exact executable snapshot `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`. If available, materialize the exact manifest-listed implementation closure plus all `test_*.py` and the pinned LAB-085 fixture helper; verify every file with `git hash-object` against the pinned blob before import; execute all normal LAB-086 real-schema tests; run `unsafe_legacy_promotion_expected_failure.py` separately and require the intended failure; run full compileall; then perform final security/reconciliation and a fresh current-main conflict audit. Fix every observed blocker before changing draft/merge status.

Do not manually copy connector payloads into the executor. If no supported materialization path exists, continue source-level READY work without inventing contracts. Next inspect the frozen canonical provenance serialization/authenticator contracts and LAB-090/LAB-100 runtime authority model to pin the **exact authenticator and identity rules for `ytim.provider-activation-reservation.v1`**: which old/new authority authenticators must cover the precursor, how successor runtime provider/verifier identity is bound before provider mutation, how a precursor is made one-to-one with a current provenance parent, and how retirement/replay is rejected after the parent/head changes. Persist only source-proved rules and the minimum RED matrix; do not write production precursor code without exact executable REDs.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact complete real-ledger gate + unsafe seed + full compileall + current-main conflict/security audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending; startup mutation-order, provider/verifier precondition, and V2 provider/provenance atomic-head ordering findings recorded.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending; authenticated cutover composed with LAB-099 migration classification.
- #178 / LAB-093 — READY/design-frozen; exact RED/GREEN pending.
- #179..182 / LAB-094..097 — READY/design-frozen; exact executable gates pending.
- #183 / LAB-098 — READY; transition-derived activation presence/order seam and LAB-099 composition pinned; exact RED/GREEN pending.
- #184 / LAB-099 — READY; separate authenticated V2 transition-provenance relation + authenticated reservation precursor/atomic commit ordering frozen; precursor authenticator/runtime-identity rules are the next source-level slice; exact RED/GREEN pending.
- #185 / LAB-100 — READY/design-frozen; exact executable gates pending; restart verify-before-recover and provider/verifier pairing regressions recorded.
