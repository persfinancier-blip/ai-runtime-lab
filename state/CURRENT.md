# Current Lab State

Last updated: 2026-09-10

## Active objective
LAB-086 — finish the exact executable/security gate for asymmetric break-glass history migration, then reconcile/merge only if every real-schema regression and conflict audit passes.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165 at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`; current connector read confirms `open`, `draft=true`, `mergeable=false`. Keep draft.
- Other open drafts: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175; LAB-092/#176 PR #177.
- Frozen design follow-up: LAB-093/#178 plus LAB-094..100/#179..185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected current open issues and PRs; resumed LAB-086 first.

Current-run capability observation:
- Direct `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git` again failed before repository execution with `Could not resolve host: github.com`.
- GitHub connector reads/writes are available.
- No supported non-model connector-to-local-filesystem byte-exact materialization primitive is exposed in this run. Manual/model reserialization of the security-critical LAB-086 closure remains prohibited by the retained exact-byte gate.
- Therefore no new LAB-086 behavioral, unsafe-seed, compileall, security-reconciliation or conflict PASS is claimed; PR #165 remains draft.

Completed the recorded distinct fallback and froze `OBSERVER_EMERGENCY_HOLDOUT_IDENTITY_PRIVACY_WITNESS_RETENTION_LEASE_PQ_SPLITBRAIN_V1_FROZEN` in `research/2026-09-10-observer-emergency-holdout-identity-privacy-witness-retention-lease-pq-splitbrain-v1.md`, main commit `3cca12b0fb21227cf2441a3174f1b337aba5cca0`; #178 comment `5615421985` records the result.

Key decisions:
- `EMERGENCY_ADMISSION != THRESHOLD_SELF_REDUCTION`: observer recovery-root compromise cannot be repaired by the same compromised epoch silently reducing signer or independent-domain floors. Emergency admission is a bounded authenticated successor transition carrying predecessor epoch, last uncontested checkpoint, known conflicts, degraded interval, reason/expiry and successor threshold policy; emergency observers are not retroactive witnesses.
- `NEW_DATASET_ID != INDEPENDENT_HOLDOUT` and `NEW_ANALYST_ID != FRESH_ADAPTIVITY_BUDGET`: reusable-holdout accounting follows semantic dataset provenance and analyst/controller state transfer. Exposure-ledger rollback becomes `EXPOSURE_UNKNOWN`, not zero; mechanism/disclosure type remains part of the guarantee.
- `SPEND_WITNESS_SIGNATURE_VALID != SPEND_WITNESS_CURRENT`: privacy spend-continuity witnesses require generation/freshness and monotonic cumulative + uncertainty floors. Compromise/key rotation cannot reduce established or possibly disclosed spend; conflicting same-generation witness statements are equivocation evidence.
- `REVOCATION_ACK_RECEIVED != CAPABILITY_UNSPENDABLE`: retention revocation requires bounded execution leases and resource-side enforcement of capability/revocation/hold/policy floors. Conflicting ACKs or stale rejoining workers enter destructive quarantine; queued/offline jobs reauthorize at execution time.
- `CERTIFICATE_COVERS_BOTH_SNIS != SERVICES_CURRENTLY_EQUIVALENT`: cross-SNI ticket use requires current authenticated service-equivalence policy and regional admission-floor convergence. DC/certificate/PQ/ECH/backend/revocation/replay ancestry remains binding; full-auth 1-RTT may recover before resumption/0-RTT.
- Frozen 40-case RED-first matrix across observer emergency/recovery, holdout identity/exposure, privacy spend witnesses, retention lease fencing, and PQ/ECH cross-SNI split-brain recovery.

Primary donors: RFC 9162; Dwork et al. 2015 reusable holdout; Generic Holdout; NIST SP 800-226; RFC 9345; RFC 9846.

## Known failures / blockers
- LAB-086 remains priority #1. Remaining blocker is exact local execution of the complete real-ledger closure.
- Direct shell transport cannot currently resolve `github.com`.
- Connector can read pinned source but this run has no supported non-model connector-to-local-filesystem materialization primitive.
- Complete real-schema LAB-086 tests, unsafe expected-failure seed, full compileall, security reconciliation and branch/main conflict audit remain pending.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-093..100 design freezes do not substitute for executable RED/GREEN proof.

## Exact next action
LAB-086 first: probe once for a newly supported non-model materialization path for pinned connector bytes at exact executable snapshot `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`. If available, materialize the exact manifest-listed implementation closure plus all `test_*.py` and the pinned LAB-085 fixture helper; verify every file with `git hash-object` against the pinned blob before import; execute all normal LAB-086 real-schema tests; run `unsafe_legacy_promotion_expected_failure.py` separately and require the intended failure; run full compileall; then perform final security/reconciliation and branch/main conflict audit. Fix every observed blocker before changing draft/merge status.

Do not manually copy connector payloads into the executor. If no supported materialization path exists, record the per-run observation and move directly to the next distinct evidence task: **observer emergency-admission expiry/replacement under partial recovery-authority compromise + correlated holdout provenance through derived/synthetic datasets and disclosure-budget composition + privacy spend-witness quorum overlap/rotation and stale-witness eviction + retention resource-fence generation rollback/recovery and offline destructive-job replay + PQ/ECH cross-SNI equivalence-policy rollback, DC replacement ancestry, and ticket admission after asymmetric regional recovery**.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact complete real-ledger gate + unsafe seed + full compileall + conflict/security audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178 / LAB-093 — READY; architecture now additionally covers compromised recovery-root emergency observer admission, semantic holdout/analyst identity and rollback-safe exposure accounting, privacy spend-witness continuity/equivocation, retention lease + resource-side revocation fencing, and PQ/ECH cross-SNI split-brain/DC-expiry/regional admission convergence; exact RED/GREEN pending.
- #179..185 / LAB-094..100 — READY/design-frozen; exact executable gates pending.
