# Current Lab State

Last updated: 2026-09-10

## Active objective
LAB-086 — finish the exact executable/security gate for asymmetric break-glass history migration, then reconcile/merge only if every real-schema regression and conflict audit passes.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165 at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`; current connector read confirms `open`, `draft=true`, `mergeable=false`. Keep draft.
- Other open drafts: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175; LAB-092/#176 PR #177.
- Frozen design follow-up: LAB-093/#178 plus LAB-094..100/#179..185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected open issues/open PRs and resumed LAB-086 first.

Current-run capability observation:
- Direct `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git` failed before repository execution with `Could not resolve host: github.com`.
- GitHub connector reads/writes are available.
- No supported non-model connector-to-local-filesystem materialization primitive is exposed in this run. Manual/model reserialization of the security-critical LAB-086 closure remains prohibited by the retained byte-exact gate.
- Therefore no new LAB-086 behavioral, unsafe-seed, compileall, security-reconciliation or conflict PASS is claimed; PR #165 remains draft.

Completed the recorded distinct fallback and froze `OBSERVER_RECOVERY_REUSABLE_HOLDOUT_PRIVACY_DUAL_CONTROL_RETENTION_REVOCATION_PQ_CROSS_SNI_V1_FROZEN` in `research/2026-09-10-observer-recovery-reusable-holdout-privacy-dual-control-retention-revocation-pq-cross-sni-v1.md`, main commit `a9c07a79020c866728e8fe41e307ec80e99f0f8d`; #178 comment `5614736890` records the result.

Key decisions:
- `CURRENT_OBSERVER_QUORUM_VALID != OBSERVER_HISTORY_UNCOMPROMISED`: a compromised observer epoch never regains current authority merely because signatures still verify. Recovery creates an authenticated successor epoch binding last uncontested checkpoint, known conflict evidence, degraded interval, new membership/failure domains and thresholds. Lowering signer or independent-domain floors requires recovery authority.
- `MECHANISM_SUPPORTS_REUSE != THIS_ANALYSIS_USED_IT_WITHIN_ITS_GUARANTEE`: holdout reuse is mechanism/disclosure-specific. Persist mechanism version, candidate-family/controller identity, allowed disclosure, exposure budget and stopping rule. Family renaming does not reset exposure when analyst state transfers; score/ranking disclosure is not a one-bit contract.
- `NEW_ROOT_SIGNATURE_VALID != SPEND_FLOOR_RECOVERED`: privacy-root compromise recovery needs separate root/recovery quorum and independent spend-continuity witness quorum. Unknown possible disclosures remain charged/fenced; credential/root rotation never resets cumulative privacy loss.
- `CAPABILITY_REVOKED_AT_CONTROL_PLANE != CAPABILITY_UNSPENDABLE_EVERYWHERE`: retention revocation is complete only after every destructive-capable domain acknowledges current revocation floor or is fenced. Queued/offline jobs require execution-time reauthorization; stale rejoining workers enter destructive quarantine.
- `CERTIFICATE_VALID_FOR_BOTH_SNIS != CURRENT_SERVICE_EQUIVALENCE_FOR_RESUMPTION`: cross-SNI ticket use additionally requires current service-equivalence policy. Ticket ancestry retains certificate/DC/PQ/ECH/backend/ticket-key/revocation/replay generations. DC compromise and parent-certificate reissue do not retroactively sanitize old descendants; 1-RTT recovery may precede resumption/0-RTT.
- Frozen 40-case RED-first matrix across observer recovery, reusable holdout accounting, privacy dual-control recovery, retention revocation propagation and PQ/ECH cross-SNI recovery.

Primary donors: RFC 9162; Generic Holdout (arXiv:1809.05596); NIST SP 800-226; RFC 9345; RFC 9846.

## Known failures / blockers
- LAB-086 remains priority #1. Remaining blocker is exact local execution of the complete real-ledger closure.
- Direct shell transport cannot currently resolve `github.com`.
- Connector can read pinned source but this run has no supported non-model connector-to-local-filesystem materialization primitive.
- Complete real-schema LAB-086 tests, unsafe expected-failure seed, full compileall, security reconciliation and branch/main conflict audit remain pending.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-093..100 design freezes do not substitute for executable RED/GREEN proof.

## Exact next action
LAB-086 first: probe once for a newly supported non-model materialization path for pinned connector bytes at exact executable snapshot `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`. If available, materialize the exact manifest-listed implementation closure plus all `test_*.py` and the pinned LAB-085 fixture helper; verify every file with `git hash-object` against the pinned blob before import; execute all normal LAB-086 real-schema tests; run `unsafe_legacy_promotion_expected_failure.py` separately and require the intended failure; run full compileall; then perform final security/reconciliation and branch/main conflict audit. Fix every observed blocker before changing draft/merge status.

Do not manually copy connector payloads into the executor. If no supported materialization path exists, record the per-run observation and move directly to the next distinct evidence task: **observer recovery-root compromise and emergency observer admission without threshold self-reduction + reusable-holdout correlated-dataset/analyst-identity transfer and exposure-ledger rollback + privacy spend-witness compromise/freshness and uncertainty-floor succession + retention revocation-ack equivocation/lease expiry/resource-side fencing + PQ/ECH cross-SNI service-equivalence split-brain, DC expiry during resumed ancestry and regional ticket-admission convergence**.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact complete real-ledger gate + unsafe seed + full compileall + conflict/security audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178 / LAB-093 — READY; architecture now additionally covers observer compromise recovery/threshold evolution, mechanism-specific reusable-holdout accounting, privacy dual-control root recovery, retention revocation propagation/offline-job fencing, and cross-SNI ticket ancestry through DC compromise/certificate reissue/service-equivalence rollover; exact RED/GREEN pending.
- #179..185 / LAB-094..100 — READY/design-frozen; exact executable gates pending.
