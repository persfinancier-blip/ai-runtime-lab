# Current Lab State

Last updated: 2026-09-07

## Active objective
LAB-086 — finish the exact executable/security gate for asymmetric break-glass history migration, then reconcile/merge only if every real-schema regression and conflict audit passes.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165 at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`; keep draft and do not merge without the exact retained gate.
- Other open draft/IN_PROGRESS PRs observed this run: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175; LAB-092/#176 PR #177.
- Frozen design follow-ups: LAB-093/#178; LAB-094..096/#179..181; LAB-097..099/#182..184; LAB-100/#185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected current open issues/PRs; resumed LAB-086 first.

Current-run capability probe:
- `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git /tmp/ai-runtime-lab-auto16` failed before repository execution with `Could not resolve host: github.com` (exit 128);
- GitHub connector reads/writes and web research remain available;
- therefore no new LAB-086 behavioral/compile PASS is claimed and PR #165 remains draft.

Completed the recorded distinct fallback and froze `SECURE_TIME_SOURCE_KEY_LIFECYCLE_QUORUM_INDEPENDENCE_FAR_FUTURE_POISON_RECOVERY_V1_FROZEN` in `research/2026-09-07-secure-time-source-key-lifecycle-quorum-independence-far-future-poisoning-recovery-v1.md`, commit `5135e9a99fae6b8e511e0fcd3496a1ccd1e460d1`; #178 comment `5574820709` records the result.

Key decisions:
- `AUTHENTICATED_TIME_SAMPLE != CORRECT_TIME_SAMPLE != INDEPENDENT_TIME_SAMPLE != QUORUM_TIME_DECISION != TRUSTED_TIME_FLOOR`;
- authenticated time servers can still be falsetickers; advance freshness authority only from a bounded, uncertainty-aware quorum decision;
- count independence by failure/control domains (operator/control, key custody, hosting/provider, network/AS path, DNS/discovery, jurisdiction, implementation/build, upstream reference-clock lineage), not raw IP/hostname/server count;
- retain append-only `TimeSourceKeyStatusV1` history with effective compromise/calibration-loss boundaries; unknown compromise onset yields `UNKNOWN_HISTORICAL_TIME_TRUST` where safety depends on that source;
- ordinary source-key rotation must preserve lineage, activation boundary and historical public verification/status evidence;
- a far-future poisoned `TrustedTimeFloorV1` cannot be lowered by routine time samples, wall-clock reset, VM rollback, cache deletion or ordinary resynchronization;
- poison recovery requires a distinct higher-order, independently authorized `TimeFloorPoisonRecoveryV1`, changes generation, preserves the poisoned decision as evidence, and sets only a conservative independently supported replacement interval/floor;
- recovery authority must not be wholly controlled by the same domains that satisfied the poisoned routine time quorum;
- added a 64-case RED-first matrix across key lifecycle, source correlation, robust selection, far-future poisoning, recovery authorization, crash/replay and governance.

Primary donors: RFC 8915 NTS; RFC 5905 authentication-vs-correctness and falseticker selection; RFC 8633 multiple-source/anycast guidance; RFC 9523 Khronos adversarial multi-source sampling/trimming; RFC 3628 TSA compromise/calibration-loss history; TUF fast-forward attack recovery.

## Known failures / blockers
- LAB-086 remains priority #1. Remaining blocker is exact source execution.
- Direct git transport failed in this run before repository execution with DNS resolution failure.
- PR #165 must remain draft until branch-local dependency-blob verification, retained strict/thaw subgate, real-schema LAB-086 tests, compileall, unsafe expected-failure seed, security reconciliation and branch/main conflict audit execute on exact source.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-088 still needs supported-integration + LAB-084/085/086 downstream execution.
- LAB-091 still needs real LAB-080/LAB-082 integration, two-worker/crash, timeout-after-commit/UNKNOWN, LAB-087 composition and full exact regressions.
- LAB-090/LAB-100, LAB-092 and LAB-097..099 remain design-frozen but require exact executable RED/GREEN before production integration.
- LAB-093 exact implementation must compose all frozen capability/delegation/revocation/lease/handoff/provider-fence/receipt/historical-trust/archive/verifier/conformance/oracle/publication/witness/recovery/freshness/secure-time contracts with LAB-087 isolation; none of the design freezes substitute for executable proof.

## Exact next action
LAB-086 first: if exact branch source execution becomes available, check out/reconstruct current PR head `ee210a47221b6df53f3518aa3af74f76c5b0122b`, verify exact branch-local source/blob lineage, then execute the retained strict/thaw subgate (alternate-UNIQUE, primary-key/history/proof replacement, NULL identities, minimal thaw, conflict algorithms), compileall, exact branch-local LAB-080→086 dependency-blob verification, every normal LAB-086 real-schema test, unsafe legacy-promotion expected-failure seed, and final security/reconciliation + branch/main conflict audit. Fix every observed blocker before changing draft/merge status.

If exact execution remains unavailable, next distinct evidence task is **time-floor recovery-authority key lifecycle / recovery-policy rotation / poison-evidence adjudication and emergency-quorum governance semantics**. Define how `TimeFloorRecoveryAuthorityV1` keys are bootstrapped, rotated, compromised and retired; how old+new recovery-policy generations authorize transition without self-authorization; what evidence threshold is sufficient to classify a trusted floor as poisoned versus merely surprising; how emergency recovery avoids governance capture and correlated approvers; and how conflicting valid recovery artifacts are published, appealed and reconciled without silently choosing the lower clock.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact full executable gate + conflict audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178 / LAB-093 — READY; secure-time source lifecycle/quorum/far-future poison-recovery contract now also frozen; exact RED/GREEN pending.
- #179..181 / LAB-094..096 — READY; retained-authority graph contracts frozen.
- #182..184 / LAB-097..099 — READY; authenticated provenance/global chain/recovery contracts frozen.
- #185 / LAB-100 — READY; activation implementation/capability authority contracts frozen.
