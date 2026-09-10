# Current Lab State

Last updated: 2026-09-10

## Active objective
LAB-086 — finish the exact executable/security gate for asymmetric break-glass history migration, then reconcile/merge only if every real-schema regression and conflict audit passes.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165 at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`; current inspection shows open/draft. Keep draft.
- Other open drafts: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175; LAB-092/#176 PR #177.
- Frozen design follow-up: LAB-093/#178 plus LAB-094..100/#179..185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected current open issues and active PRs; resumed LAB-086 first and re-probed exact source materialization.

Current-run capability observation:
- Direct `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git` failed before repository execution with `Could not resolve host: github.com`.
- GitHub connector reads/writes are available.
- No supported non-model connector-to-local-filesystem byte-exact materialization primitive is exposed in this run. Manual/model reserialization of the security-critical LAB-086 closure remains prohibited by the retained exact-byte gate.
- Therefore no new LAB-086 behavioral, unsafe-seed, compileall, security-reconciliation or conflict PASS is claimed; PR #165 remains draft.

Completed the recorded distinct fallback and froze `TRANSPARENCY_WITNESS_HOLDOUT_THRESHOLD_PRIVACY_DUAL_RESOLVER_EXTERNAL_EFFECT_TICKET_EMERGENCY_ROTATION_V1_FROZEN` in `research/2026-09-10-transparency-witness-holdout-threshold-privacy-dual-resolver-external-effects-ticket-emergency-rotation-v1.md`, main commit `8389640952a2617247e8eae943199f6c21d78aa6`; #178 comment `5620157496` records the result.

Key decisions:
- `SIGNED_RECOVERY_ROOT != RECOVERY_HISTORY_COMPLETE`: transparency-log recovery roots must commit predecessor root, recovery epoch, witness policy and all known conflict evidence at the declared cutoff; inclusion/authenticity alone does not prove completeness or global canonicality.
- `NEW_HOLDOUT_WITNESS_THRESHOLD != FRESH_HOLDOUT`: witness/threshold/key rotation carries dataset/controller/disclosure ancestry and maximum prior exposure; compromise uncertainty adds an `UNKNOWN` floor rather than resetting exposure.
- `ONE_RESOLVER_SAYS_DISTINCT != SUBJECTS_DISJOINT`: dual-resolver evidence counts only when resolver implementation/data/failure domains are actually independent; disagreement conservatively composes privacy spend/reservations/unknown overlap.
- `LOCAL_TX_COMMITTED != EXTERNAL_EFFECT_EXACTLY_ONCE`: exactly-once guarantees are scoped to the atomic/deduplicated boundary; external destructive effects require their own authenticated receipt plus semantic idempotency/fencing/reconciliation contract, and timeout-after-send is `EFFECT_UNKNOWN`.
- `NEW_CERT_CHAIN_VALID != OLD_TICKETS_AUTHORIZED`: emergency root/intermediate/end-entity/DC/PQ/ECH rotation does not clear predecessor ticket ancestry; full-auth, PSK 1-RTT and 0-RTT recover under separate convergence gates, with replay-state loss specifically quarantining 0-RTT.
- Frozen 40-case RED-first matrix across those five domains.

Primary donors: RFC 9162; Dwork et al. 2015; Generic Holdout 2018; NIST SP 800-226; Apache Kafka design/Kafka Streams exactly-once boundary; RFC 9345; RFC 9849; RFC 8446/RFC 9001.

## Known failures / blockers
- LAB-086 remains priority #1. Remaining blocker is exact local execution of the complete real-ledger closure.
- Direct shell transport cannot currently resolve `github.com`.
- Connector can read pinned source but this run has no supported non-model connector-to-local-filesystem materialization primitive.
- Complete real-schema LAB-086 tests, unsafe expected-failure seed, full compileall, security reconciliation and branch/main conflict audit remain pending.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-093..100 design freezes do not substitute for executable RED/GREEN proof.

## Exact next action
LAB-086 first: probe once for a newly supported non-model materialization path for pinned connector bytes at exact executable snapshot `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`. If available, materialize the exact manifest-listed implementation closure plus all `test_*.py` and the pinned LAB-085 fixture helper; verify every file with `git hash-object` against the pinned blob before import; execute all normal LAB-086 real-schema tests; run `unsafe_legacy_promotion_expected_failure.py` separately and require the intended failure; run full compileall; then perform final security/reconciliation and branch/main conflict audit. Fix every observed blocker before changing draft/merge status.

Do not manually copy connector payloads into the executor. If no supported materialization path exists, record the per-run observation and move directly to the next distinct evidence task: **transparency witness-set membership rollback and cross-log consistency after recovery + reusable-holdout witness independence under correlated operators/data planes + privacy identity-proof freshness/expiry and negative-disjointness evidence + external-effect receipt key rotation, compensation vs reversal, and multi-provider reconciliation + ticket-cutoff proof after KMS/backup restore with stale regional admission caches and replay-window epoch rollover**.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact complete real-ledger gate + unsafe seed + full compileall + conflict/security audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178 / LAB-093 — READY; architecture now additionally covers transparency witness equivocation/recovery inclusion, holdout witness compromise/threshold changes, dual-resolver privacy reconciliation, external exactly-once boundaries, and emergency TLS/PQ/ECH ticket ancestry/replay-state recovery; exact RED/GREEN pending.
- #179..185 / LAB-094..100 — READY/design-frozen; exact executable gates pending.
