# Current Lab State

Last updated: 2026-09-10

## Active objective
LAB-086 — finish the exact executable/security gate for asymmetric break-glass history migration, then reconcile/merge only if every real-schema regression and conflict audit passes.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165 at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`; current connector read confirms `open`, `draft=true`, `mergeable=false`. Keep draft.
- Other open drafts: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175; LAB-092/#176 PR #177.
- Frozen design follow-up: LAB-093/#178 plus LAB-094..100/#179..185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected current open issues and draft PRs; resumed LAB-086 first.

Current-run capability observation:
- Direct `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git` failed before repository execution with `Could not resolve host: github.com`.
- GitHub connector reads/writes are available.
- No supported non-model connector-to-local-filesystem materialization primitive is exposed in this run. Manual/model reserialization of the security-critical LAB-086 closure remains prohibited by the retained byte-exact gate.
- Therefore no new LAB-086 behavioral, unsafe-seed, compileall, security-reconciliation or conflict PASS is claimed; PR #165 remains draft.

Completed the recorded distinct fallback and froze `CHECKPOINT_ADJUDICATION_SEQUENTIAL_REDUCER_PRIVACY_ESCROW_RETENTION_RECEIPTS_PQ_TICKET_LIFETIME_V1_FROZEN` in `research/2026-09-10-checkpoint-adjudication-sequential-reducer-privacy-escrow-retention-receipts-pq-ticket-lifetime-v1.md`, main commit `5d93b621d68a082fc0baf6132468072b62b2d753`; #178 comment `5612117072` records the result.

Key decisions:
- `EQUIVOCATION_DETECTED != WINNER_SELECTED`: an equivocating checkpoint generation is terminally `EQUIVOCATED`. Resolution is a successor `ADJUDICATED_RECOVERY` transition committing to every known conflict and the last common floor; later signatures on one old head cannot rehabilitate the accused generation.
- `ZERO_FAILURES_OBSERVED != ZERO_FAILURE_PROBABILITY`: flaky/security reducers must predeclare stopping/sequential rules, preserve the same security predicate plus event-order/environment envelope, and classify finite clean samples as `NOT_OBSERVED_UNDER_BUDGET`, not predicate absence. Rare-event reproduction class is part of the witness.
- `ESCROW_TRANSFER_REQUESTED != ESCROW_AVAILABLE_AT_DESTINATION`: privacy-budget transfer uses one immutable transfer id with source-debit-before-destination-credit semantics. Timeout after irrevocable source debit is `TRANSFER_UNKNOWN`; reconciliation may finish/retire that slice but cannot mint a second allocation.
- `DEGRADED_INTERVAL != AUTOMATICALLY_INVALID_HISTORY`: retention compromise is reconciled event-by-event. A receipt upgrades confidence only when signer, storage/log path and operator/control plane are outside the compromised failure domain; missing evidence for destructive events remains `UNRESOLVED_DEGRADED`.
- `PARTIAL_ERASURE_ATTESTED != TICKET_GENERATION_SAFE`: TLS/PQ incident recovery separates ticket revocation generation, erasure coverage, replay-state recovery and late-edge admission. RFC 8446's 7-day ticket lifetime is a protocol maximum, not incident authorization; policy may be shorter, descendant ticket authority cannot cross a revocation generation, and successful old-ticket decryption never overrides revocation.
- Frozen 40-case RED-first matrix across checkpoint adjudication, sequential flaky reduction, privacy escrow transfer, retention receipt reconciliation and PQ/ECH late-edge/ticket-lifetime recovery.

Primary donors: RFC 9162; RFC 5011; NIST event-sequence/combinatorial testing guidance; NIST SP 800-226; NIST SP 800-88 Rev. 2; RFC 8446; RFC 9849.

## Known failures / blockers
- LAB-086 remains priority #1. Remaining blocker is exact local execution of the complete real-ledger closure.
- Direct shell transport cannot currently resolve `github.com`.
- Connector can read exact pinned blobs but this run has no supported non-model connector-to-local-filesystem materialization primitive.
- Complete real-schema LAB-086 tests, unsafe expected-failure seed, full compileall, security reconciliation and branch/main conflict audit remain pending.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-093..100 design freezes do not substitute for executable RED/GREEN proof.

## Exact next action
LAB-086 first: probe once for a newly supported non-model materialization path for pinned connector bytes at exact executable snapshot `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`. If available, materialize the exact manifest-listed implementation closure plus all `test_*.py` and the pinned LAB-085 fixture helper; verify every file with `git hash-object` against the pinned blob before import; execute all normal LAB-086 real-schema tests; run `unsafe_legacy_promotion_expected_failure.py` separately and require the intended failure; run full compileall; then perform final security/reconciliation and branch/main conflict audit. Fix every observed blocker before changing draft/merge status.

Do not manually copy connector payloads into the executor. If no supported materialization path exists, record the per-run observation and move directly to the next distinct evidence task: **checkpoint adjudication conflict-set completeness and successor-root compromise/replay + multiple-candidate/sequential-selection bias in flaky reducers + orphaned privacy escrow transfer reclamation without double ownership + omission-proof/coverage guarantees for independent retention receipts + PQ/ECH ticket-ancestry lifetime enforcement, admission fencing for late edges, and descendant-ticket revocation propagation**.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact complete real-ledger gate + unsafe seed + full compileall + conflict/security audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178 / LAB-093 — READY; capability/evidence architecture now also covers successor adjudication after equivocation, rare-event-safe sequential reduction, partition-safe escrow transfer, degraded-interval receipt reconciliation and bounded TLS/PQ ticket ancestry/late-edge recovery; exact RED/GREEN pending.
- #179..185 / LAB-094..100 — READY/design-frozen; exact executable gates pending.
