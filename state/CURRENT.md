# Current Lab State

Last updated: 2026-09-10

## Active objective
LAB-086 — finish the exact executable/security gate for asymmetric break-glass history migration, then reconcile/merge only if every real-schema regression and conflict audit passes.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165 at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`; current connector read confirms `open`, `draft=true`. Keep draft.
- Other open drafts remain LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175; LAB-092/#176 PR #177.
- Frozen design follow-up: LAB-093/#178 plus LAB-094..100/#179..185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected open issues, active PRs and repository branches; resumed LAB-086 first.

Current-run capability observation:
- Direct `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git` failed before repository execution with `Could not resolve host: github.com`.
- GitHub connector reads/writes are available.
- No supported non-model connector-to-local-filesystem materialization primitive is exposed in this run. Manual/model reserialization of the security-critical LAB-086 closure remains prohibited by the retained byte-exact gate.
- Therefore no new LAB-086 behavioral, unsafe-seed, compileall, security-reconciliation or conflict PASS is claimed; PR #165 remains draft.

Completed the recorded distinct fallback and froze `CONFLICT_GOSSIP_HOLDOUT_PRIVACY_REPLAY_RETENTION_INVENTORY_PQ_TICKET_ROTATION_V1_FROZEN` in `research/2026-09-10-conflict-gossip-holdout-privacy-replay-retention-inventory-pq-ticket-rotation-v1.md`, main commit `6c211774b665de48d4ef8f3ed403e7821dec31ad`; #178 comment `5613602421` records the result.

Key decisions:
- `CONFLICT_NOT_GOSSIPED != CONFLICT_DID_NOT_EXIST`: adjudication commits to the canonical known conflict set, observation cutoff, observer/failure-domain inventory and missing observers. A successor quorum proves agreement on that package, not universal absence of censored/partition-hidden heads. Late authenticated conflicts append evidence and can reopen finality without rewriting the earlier truthful cutoff package.
- `HOLDOUT_WAS_UNUSED_ONCE != HOLDOUT_REMAINS_INDEPENDENT_AFTER_REUSE`: adaptive reducer search is ranking evidence only. A selected candidate gets a fresh predeclared confirmation budget. If confirmation data is used to modify/rank another candidate, that holdout generation is burned for independent inference unless an explicitly justified reusable-validation mechanism applies.
- `RECONCILIATION_ROOT_VALID != ORPHAN_RECLAMATION_AUTHORITY_CURRENT`: privacy escrow reclamation requires current destination non-credit proof or fencing of every destination credit authority. Timeout or an old valid reconciliation signature cannot mint budget; cumulative charged/unknown spend remains monotonic.
- `WRITER_NOT_IN_INVENTORY != WRITER_COULD_NOT_MUTATE`: retention completeness requires a canonical destructive-writer inventory per membership epoch. Every writer needs gap-free receipts or authenticated fencing evidence for uncovered intervals; discovery of an omitted writer downgrades affected reconciliation to `INVENTORY_INCOMPLETE`.
- `NEW_CERT_OR_PQ_POLICY_ACTIVE != OLD_TICKET_ANCESTRY_REAUTHORIZED`: ticket descendants inherit certificate/identity, PQ/hybrid, ECH-source, backend, ticket-key, revocation and replay ancestry floors plus an absolute ancestry expiry. Descendant issuance after rotation does not reset stale ancestry.
- `REGION_LOCAL_REVOCATION_FLOOR_CURRENT != GLOBAL_RESUMPTION_FLOOR_CONVERGED`: late/stale regions remain resumption-quarantined unless current or independently fenced. Tickets issued while a region was below the revocation floor remain tainted after later convergence. 1-RTT/full handshake recovery remains separate from 0-RTT re-enable.
- Frozen 40-case RED-first matrix across censored conflict discovery, post-selection inference, orphan privacy reconciliation, retention writer inventory, and PQ/ECH ticket ancestry/regional divergence.

Primary donors: RFC 9162; NIST SP 800-226; RFC 8446; RFC 9846; RFC 9849; RFC 9813.

## Known failures / blockers
- LAB-086 remains priority #1. Remaining blocker is exact local execution of the complete real-ledger closure.
- Direct shell transport cannot currently resolve `github.com`.
- Connector can read exact pinned blobs but this run has no supported non-model connector-to-local-filesystem materialization primitive.
- Complete real-schema LAB-086 tests, unsafe expected-failure seed, full compileall, security reconciliation and branch/main conflict audit remain pending.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-093..100 design freezes do not substitute for executable RED/GREEN proof.

## Exact next action
LAB-086 first: probe once for a newly supported non-model materialization path for pinned connector bytes at exact executable snapshot `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`. If available, materialize the exact manifest-listed implementation closure plus all `test_*.py` and the pinned LAB-085 fixture helper; verify every file with `git hash-object` against the pinned blob before import; execute all normal LAB-086 real-schema tests; run `unsafe_legacy_promotion_expected_failure.py` separately and require the intended failure; run full compileall; then perform final security/reconciliation and branch/main conflict audit. Fix every observed blocker before changing draft/merge status.

Do not manually copy connector payloads into the executor. If no supported materialization path exists, record the per-run observation and move directly to the next distinct evidence task: **conflict-observer admission/removal and eclipse-resistant coverage thresholds + reusable-holdout privacy/accounting style guarantees for repeated flaky-candidate confirmation + privacy reconciliation-root compromise recovery with successor anti-rollback + retention writer-capability delegation/subdelegation inventory closure + PQ/ECH ticket ancestry across delegated credentials/certificate revocation, cross-SNI resumption and regional stale-issuer fencing**.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact complete real-ledger gate + unsafe seed + full compileall + conflict/security audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178 / LAB-093 — READY; capability/evidence architecture now also covers censored conflict discovery and qualified observer completeness, post-selection holdout independence, compromise-safe orphan privacy reclamation, writer-inventory-based retention completeness, and PQ/ECH ticket ancestry floors through certificate/PQ rotation and regional revocation divergence; exact RED/GREEN pending.
- #179..185 / LAB-094..100 — READY/design-frozen; exact executable gates pending.
