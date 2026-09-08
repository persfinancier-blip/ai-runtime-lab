# Current Lab State

Last updated: 2026-09-08

## Active objective
LAB-086 — finish the exact executable/security gate for asymmetric break-glass history migration, then reconcile/merge only if every real-schema regression and conflict audit passes.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165 at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`; keep draft and do not merge without the exact retained gate.
- Other open draft/IN_PROGRESS PRs: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175; LAB-092/#176 PR #177.
- Frozen design follow-ups: LAB-093/#178; LAB-094..096/#179..181; LAB-097..099/#182..184; LAB-100/#185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected current open issues and PR #165; resumed LAB-086 first.

Current-run capability probe:
- `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git /tmp/ai-runtime-lab-auto25` failed before repository execution with `Could not resolve host: github.com` (exit 128);
- GitHub connector reads/writes and web research remain available;
- PR #165 remains open/draft at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`, current connector read `mergeable=false`;
- therefore no new LAB-086 behavioral/compile PASS is claimed and no draft/merge state was changed.

Completed the recorded distinct fallback and froze `SEMANTIC_EVENT_INGESTION_COMPLETENESS_SOURCE_INVENTORY_OMISSION_MONITOR_CATCHUP_V1_FROZEN` in `research/2026-09-08-semantic-event-ingestion-completeness-source-inventory-omission-detection-monitor-catchup-v1.md`, main commit `1d1ea146fa7809e5588a231b9ee7bb4d69c8b540`; #178 comment `5579140264` records the result.

Key decisions:
- `APPEND_ONLY_LOG != COMPLETE_EVENT_INGESTION`; log consistency/inclusion cannot prove that required events were never suppressed before admission;
- `EventSourceInventoryV1` is the authenticated monotonic denominator; currently reporting sources are not the required source set, and a producer cannot silently shrink it;
- source retirement requires an authenticated final/drain frontier with zero unresolved obligations; timeout, DNS/CMDB disappearance or telemetry silence do not retire a required source;
- governed sources use authenticated event/frontier semantics; sequence-gap evidence is valid only when the source contract declares contiguous issuance;
- `IngestionPromiseV1` creates a CT-like pre-inclusion obligation: after its deadline, a retained valid promise plus a covered checkpoint lacking the event is positive omission evidence;
- independent monitors reconcile source inventory/frontiers/promises against checkpoint coverage; log self-attestation is insufficient for source completeness;
- monitor loss creates an unknown interval until inventory continuity, per-source frontiers, promises, log checkpoints and unresolved contradictions are reconstructed;
- partitions/timeouts alone yield UNKNOWN unless independent evidence proves omission; fraud attribution must distinguish producer omission from source failure/misbehavior;
- late omitted events discovered after `PREFIX_COMPLETE_PROVEN` invalidate/reopen through the existing continuous-assurance generation chain instead of rewriting history;
- frozen a 60-case RED-first matrix spanning inventory authority, promise/inclusion, source chains, partitions/delay, catch-up, anti-steering challenges, retirement/resurrection and crash atomicity.

Primary donors: RFC 9162 CT signed inclusion promise/MMD and monitors; RFC 9943 SCITT issuer-vs-registration separation; NIST SP 800-53 Rev.5 AU-12 component/event-source audit denominator; Apache Kafka producer sequence/idempotence semantics.

## Known failures / blockers
- LAB-086 remains priority #1. Remaining blocker is exact source execution.
- Direct git transport failed in this run before repository execution with DNS resolution failure.
- PR #165 must remain draft until branch-local dependency-blob verification, retained strict/thaw subgate, real-schema LAB-086 tests, compileall, unsafe expected-failure seed, security reconciliation and branch/main conflict audit execute on exact source.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-088 still needs supported-integration + LAB-084/085/086 downstream execution.
- LAB-091 still needs real LAB-080/LAB-082 integration, two-worker/crash, timeout-after-commit/UNKNOWN, LAB-087 composition and full exact regressions.
- LAB-090/LAB-100, LAB-092 and LAB-097..099 remain design-frozen but require exact executable RED/GREEN before production integration.
- LAB-093 exact implementation must compose all frozen capability/delegation/revocation/lease/handoff/provider-fence/receipt/historical-trust/archive/verifier/conformance/oracle/publication/witness/recovery/freshness/secure-time/rebootstrap/convergence/evidence/continuous-assurance/checkpoint/source-ingestion contracts with LAB-087 isolation; none of the design freezes substitute for executable proof.

## Exact next action
LAB-086 first: if exact branch source execution becomes available, check out/reconstruct current PR head `ee210a47221b6df53f3518aa3af74f76c5b0122b`, verify exact branch-local source/blob lineage, then execute the retained strict/thaw subgate (alternate-UNIQUE, primary-key/history/proof replacement, NULL identities, minimal thaw, conflict algorithms), compileall, exact branch-local LAB-080→086 dependency-blob verification, every normal LAB-086 real-schema test, unsafe legacy-promotion expected-failure seed, and final security/reconciliation + branch/main conflict audit. Fix every observed blocker before changing draft/merge status.

If exact execution remains unavailable, next distinct evidence task is **source-inventory authority key lifecycle / event-source identity rotation / source-frontier freshness and rollback / ingestion-promise issuer independence**. Define how source inventory and per-source identity keys rotate/revoke without retroactively invalidating safe history; how source epoch/key replacement binds to the same logical source instead of creating denominator laundering; how stale/replayed source frontiers are rejected after monitor catch-up; and how ingestion-promise signing authority is kept independent enough from the log producer that a compromised producer cannot forge, suppress, or selectively repudiate its own completeness obligations.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact full executable gate + conflict audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178 / LAB-093 — READY; checkpoint/source-ingestion and prior capability/recovery/convergence/continuous-assurance contracts frozen; exact RED/GREEN pending.
- #179..181 / LAB-094..096 — READY; retained-authority graph contracts frozen.
- #182..184 / LAB-097..099 — READY; authenticated provenance/global chain/recovery contracts frozen.
- #185 / LAB-100 — READY; activation implementation/capability authority contracts frozen.
