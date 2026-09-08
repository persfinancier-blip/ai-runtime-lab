# Current Lab State

Last updated: 2026-09-08

## Active objective
LAB-086 — finish the exact executable/security gate for asymmetric break-glass history migration, then reconcile/merge only if every real-schema regression and conflict audit passes.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165 at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`; keep draft and do not merge without the exact retained gate.
- Other open draft/IN_PROGRESS PRs: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175; LAB-092/#176 PR #177.
- Frozen design follow-ups: LAB-093/#178; LAB-094..096/#179..181; LAB-097..099/#182..184; LAB-100/#185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected open issues and PR #165; resumed LAB-086 first.

Current-run capability probe:
- `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git /tmp/ai-runtime-lab-auto30` failed before repository execution with `Could not resolve host: github.com` (exit 128);
- GitHub connector reads/writes and web research remain available;
- PR #165 remains open/draft at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`, connector read `mergeable=false`;
- therefore no new LAB-086 behavioral/compile PASS is claimed and no draft/merge state was changed.

Completed the recorded distinct fallback and froze `ADJUDICATION_RECOVERY_AUTHORITY_FRESHNESS_DISTRIBUTION_OFFLINE_CATCHUP_WITNESS_ROTATION_V1_FROZEN` in `research/2026-09-08-adjudication-recovery-authority-freshness-distribution-offline-catchup-witness-rotation-v1.md`, main commit `7565aec0b5e6d233c3df8e69c97e8f86c72517a7`; #178 comment `5582562009` records the result.

Key decisions:
- `VALID_SIGNATURE != CURRENT_AUTHORITY != CURRENT_QUORUM_POLICY != CURRENT_WITNESS_MEMBERSHIP`; witness consistency remains distinct from semantic adjudication truth;
- `WitnessSetAuthorityV1` and `WitnessQuorumPolicyV1` are separately versioned authority objects; witness key rotation does not create a new independent witness identity;
- offline relying parties persist `TrustedAdjudicationRecoveryFrontierV1` and MUST reconstruct missing recovery/adjudication authority, witness-set, quorum-policy and witness-key generations sequentially before appraising newest current state;
- normal rotations use TUF-style predecessor+successor authorization and monotonic generation persistence; intermediate generations cannot be skipped;
- checkpoint consistency must chain from the relying party's own retained checkpoint/frontier, not merely from a freshly downloaded local root;
- selectively served healthy-looking newest state is insufficient when intervening compromise/recovery generations may be omitted; e.g. retained g10 cannot jump to g13 if g11 compromise and g12 recovery are absent;
- same-generation/different-digest authority, witness-set, quorum-policy or checkpoint artifacts are conflicts/equivocation, never LWW/newest timestamp/majority-CDN resolution;
- witness signatures count only after membership/key validity and control-domain independence appraisal; post-facto witness compromise may reduce current quorum while preserving historical receipts/cosignatures;
- cross-log anchoring improves survivability and split-view detection but does not manufacture semantic truth or independence;
- frozen a 48-case RED-first matrix spanning offline catch-up, witness membership/key lifecycle, quorum rotation, checkpoint consistency, selective truncation, post-facto compromise/recovery recursion and crash-safe frontier persistence.

Primary donors: TUF sequential root update/rollback/freeze semantics; RFC 9162 monitor/checkpoint consistency; RFC 9943 SCITT statement/receipt/multi-TS separation; transparency.dev witness consistency/cosigning model.

## Known failures / blockers
- LAB-086 remains priority #1. Remaining blocker is exact source execution.
- Direct git transport failed in this run before repository execution with DNS resolution failure.
- PR #165 must remain draft until branch-local dependency-blob verification, retained strict/thaw subgate, real-schema LAB-086 tests, compileall, unsafe expected-failure seed, security reconciliation and branch/main conflict audit execute on exact source.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-088 still needs supported-integration + LAB-084/085/086 downstream execution.
- LAB-091 still needs real LAB-080/LAB-082 integration, two-worker/crash, timeout-after-commit/UNKNOWN, LAB-087 composition and full exact regressions.
- LAB-090/LAB-100, LAB-092 and LAB-097..099 remain design-frozen but require exact executable RED/GREEN before production integration.
- LAB-093 exact implementation must compose all frozen capability/delegation/revocation/lease/handoff/provider-fence/receipt/historical-trust/archive/verifier/conformance/oracle/publication/witness/recovery/freshness/secure-time/rebootstrap/convergence/evidence/continuous-assurance/checkpoint/source-ingestion/source-authority/source-transparency/compromise-adjudication/adjudicator-recovery-recursion/offline-catchup contracts with LAB-087 isolation; none of the design freezes substitute for executable proof.

## Exact next action
LAB-086 first: if exact branch source execution becomes available, check out/reconstruct current PR head `ee210a47221b6df53f3518aa3af74f76c5b0122b`, verify exact branch-local source/blob lineage, then execute the retained strict/thaw subgate (alternate-UNIQUE, primary-key/history/proof replacement, NULL identities, minimal thaw, conflict algorithms), compileall, exact branch-local LAB-080→086 dependency-blob verification, every normal LAB-086 real-schema test, unsafe legacy-promotion expected-failure seed, and final security/reconciliation + branch/main conflict audit. Fix every observed blocker before changing draft/merge status.

If exact execution remains unavailable, next distinct evidence task is **authoritative latest-generation discovery / anti-freeze dissemination / mirror and witness availability under offline catch-up**. Define how an offline relying party learns that newer authority/witness/quorum generations exist without trusting one mirror, how freshness behaves when secure time is weak/unavailable, how independent discovery channels and cross-log checkpoints distinguish ordinary outage from selective withholding, and when inability to prove latestness must yield `CURRENT_AUTHORITY_LATESTNESS_UNKNOWN` instead of trusting a stale-but-valid chain. Preserve the frozen rule that availability/discovery evidence is not semantic authority truth and compose with recovery-root compromise/rebootstrap semantics.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact full executable gate + conflict audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178 / LAB-093 — READY; offline authority/witness/quorum catch-up plus prior adjudication transparency/recovery recursion/compromise provenance/source/transparency/checkpoint/convergence/capability contracts frozen; exact RED/GREEN pending.
- #179..181 / LAB-094..096 — READY; retained-authority graph contracts frozen.
- #182..184 / LAB-097..099 — READY; authenticated provenance/global chain/recovery contracts frozen.
- #185 / LAB-100 — READY; activation implementation/capability authority contracts frozen.
