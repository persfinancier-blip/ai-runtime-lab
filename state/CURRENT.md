# Current Lab State

Last updated: 2026-09-12

## Active objective
LAB-086 — finish the exact executable/security gate for asymmetric break-glass history migration, then reconcile/merge only if every real-schema regression and current-main conflict audit passes.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165 at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`. Keep draft.
- Other open drafts inspected: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175; LAB-092/#176 PR #177.
- Frozen design follow-up: LAB-093/#178 plus LAB-094..100/#179..185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected open issues and active PRs; resumed LAB-086 first and re-probed exact materialization.

Current-run capability/evidence:
- Direct `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git` again failed before repository execution with `Could not resolve host: github.com`.
- GitHub connector reads/writes remain available, but no supported byte-exact connector-to-local-executor materialization primitive is exposed. Manual/model reserialization of the security-critical LAB-086 closure remains prohibited.
- Therefore no new LAB-086 behavioral, unsafe-seed, compileall, security-reconciliation or conflict PASS is claimed.
- Fresh compare after the research commit: PR #165 remains `diverged`, ahead 195 / behind 864, merge-base `d2c9781f5a60dc9b8b94fc8dba651f804a73e509`.

Executed the recorded LAB-100/#185 fallback audit against actual PR #175 source.

Fresh distinct finding:
- `AttestedCatchup` stores arbitrary `provider` + `verifier` without proving they describe the same provider authority.
- `rotate_provider()` validates requested successor identity from `new_attested.verifier`, accepts the separately supplied provider via `isinstance(FencedActivationProvider)`, then calls `provider.prepare_activation()` before proving the provider object's identity/generation/key matches the verifier-derived successor.
- Exact `FencedActivationProvider.prepare_activation()` mutates provider-owned `next_fence` and `pending` before returning its ticket.
- If an exact provider for a different generation is paired with a verifier describing the requested successor, ticket validation rejects only after the provider reservation exists, and the rejection occurs before the SQL cleanup scope that calls `abort_activation()`.
- Result: no malicious subclass is required; a rejected rotation can leave a live provider reservation with no durable activation row from which restart can reconcile it.
- Required regression: exact classes only, mismatched provider/verifier pair; post-fix must reject before `prepare_activation()` and leave provider + SQLite state unchanged.

Durable evidence:
- `research/2026-09-12-lab100-provider-verifier-pairing-precondition.md`, main commit `71493a254da518b179302cc95137c35755c018b4`.
- #185 comment `5642480285` records the regression-first extension.
- This strengthens the trusted construction boundary and the earlier rejected-ticket cleanup finding; no duplicate issue was opened.

## Known failures / blockers
- LAB-086 remains priority #1. Exact local execution of the complete real-ledger closure is unavailable in this run.
- Direct shell transport cannot resolve `github.com`.
- Connector can read pinned source but cannot byte-exactly materialize the whole pinned closure into the executor in this run.
- Complete real-schema LAB-086 tests, unsafe expected-failure seed, full compileall, security reconciliation and current-main conflict audit remain pending.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-090..100 source/design evidence does not substitute for executable RED/GREEN proof.
- LAB-100 now additionally requires provider/verifier authority pairing to be validated before any mutating activation prepare.

## Exact next action
LAB-086 first: probe once for a newly supported non-model materialization path for pinned connector bytes at exact executable snapshot `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`. If available, materialize the exact manifest-listed implementation closure plus all `test_*.py` and the pinned LAB-085 fixture helper; verify every file with `git hash-object` against the pinned blob before import; execute all normal LAB-086 real-schema tests; run `unsafe_legacy_promotion_expected_failure.py` separately and require the intended failure; run full compileall; then perform final security/reconciliation and a fresh current-main conflict audit. Fix every observed blocker before changing draft/merge status.

Do not manually copy connector payloads into the executor. If no supported materialization path exists, continue the highest-value distinct PR #175 source audit, focusing next on provider abort/release cleanup and retry exception ordering after a reservation exists: determine whether any exact-provider path can leave provider-side committed/fenced state without a durable activation row, or mutate/release provider state before retained ticket/provenance checks. Record only genuinely distinct findings. If none exist, stop extending LAB-100 and move to the next READY source-level issue rather than manufacturing a new contract.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact complete real-ledger gate + unsafe seed + full compileall + current-main conflict/security audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending; startup mutation-order and provider/verifier precondition audits have concrete findings.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178 / LAB-093 — READY/design-frozen; exact RED/GREEN pending.
- #179..185 / LAB-094..100 — READY/design-frozen; exact executable gates pending. LAB-100 additionally requires restart verify-before-recover and provider/verifier precondition regressions recorded on 2026-09-12.
