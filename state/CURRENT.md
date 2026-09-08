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
- `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git /tmp/ai-runtime-lab-auto27` failed before repository execution with `Could not resolve host: github.com` (exit 128);
- GitHub connector reads/writes and web research remain available;
- PR #165 remains open/draft at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`, current connector read `mergeable=false`;
- therefore no new LAB-086 behavioral/compile PASS is claimed and no draft/merge state was changed.

Completed the recorded distinct fallback and froze `SOURCE_PROMISE_AUTHORITY_TRANSPARENCY_COMPROMISE_PROPAGATION_POST_FACTO_INVALIDATION_V1_FROZEN` in `research/2026-09-08-source-promise-authority-transparency-compromise-propagation-post-facto-invalidation-v1.md`, main commit `8e479b93cbb7402555dfc98873d3438f55b2e02b`; #178 comment `5580251165` records the result.

Key decisions:
- `AUTHENTICATED_AUTHORITY_STATEMENT != CURRENT_AUTHORITY_VIEW`; transparency receipts prove registration, not semantic authority truth;
- source-inventory/source-identity/promise-authority views use retained monotonic `TrustedAuthorityFrontierV1`; lower generation is rollback, same generation/different digest is equivocation/conflict, and higher generation still requires predecessor continuity and authorization;
- same-generation conflicting authenticated authority statements become `AUTHORITY_EQUIVOCATION_CONFLICT_NO_CURRENT_POSITIVE_RELIANCE`; LWW/newest timestamp/first-seen/majority-CDN resolution is forbidden;
- offline monitors must reconstruct missing authority/revocation intervals or valid proof-of-prefix/checkpoint continuity and reconcile transparency views; latest-only metadata is insufficient;
- late compromise notices re-appraise current reliance on earlier completeness verdicts; known intervals affect dependent evidence in the interval, while unknown onset yields `CURRENT_RELIANCE_UNKNOWN_COMPROMISE_ONSET` rather than assuming notice publication time;
- historical verdicts and transparency receipts remain immutable: post-facto invalidation/reclosure is an append-only new generation, never a rewrite;
- compromise notices require separate authorization; a compromised ordinary source key cannot unilaterally redefine its own compromise/validity interval;
- frozen a 48-case RED-first matrix spanning authority lifecycle/transparency, compromise propagation, offline catch-up, post-facto verdict semantics, crash/conflict and control-domain independence.

Primary donors: TUF sequential root continuity + rollback/freeze protection; RFC 9943 SCITT Issuer/Transparency Service separation and equivocation accountability; RFC 9162 Certificate Transparency append-only checkpoints/consistency evidence.

## Known failures / blockers
- LAB-086 remains priority #1. Remaining blocker is exact source execution.
- Direct git transport failed in this run before repository execution with DNS resolution failure.
- PR #165 must remain draft until branch-local dependency-blob verification, retained strict/thaw subgate, real-schema LAB-086 tests, compileall, unsafe expected-failure seed, security reconciliation and branch/main conflict audit execute on exact source.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-088 still needs supported-integration + LAB-084/085/086 downstream execution.
- LAB-091 still needs real LAB-080/LAB-082 integration, two-worker/crash, timeout-after-commit/UNKNOWN, LAB-087 composition and full exact regressions.
- LAB-090/LAB-100, LAB-092 and LAB-097..099 remain design-frozen but require exact executable RED/GREEN before production integration.
- LAB-093 exact implementation must compose all frozen capability/delegation/revocation/lease/handoff/provider-fence/receipt/historical-trust/archive/verifier/conformance/oracle/publication/witness/recovery/freshness/secure-time/rebootstrap/convergence/evidence/continuous-assurance/checkpoint/source-ingestion/source-authority/source-transparency contracts with LAB-087 isolation; none of the design freezes substitute for executable proof.

## Exact next action
LAB-086 first: if exact branch source execution becomes available, check out/reconstruct current PR head `ee210a47221b6df53f3518aa3af74f76c5b0122b`, verify exact branch-local source/blob lineage, then execute the retained strict/thaw subgate (alternate-UNIQUE, primary-key/history/proof replacement, NULL identities, minimal thaw, conflict algorithms), compileall, exact branch-local LAB-080→086 dependency-blob verification, every normal LAB-086 real-schema test, unsafe legacy-promotion expected-failure seed, and final security/reconciliation + branch/main conflict audit. Fix every observed blocker before changing draft/merge status.

If exact execution remains unavailable, next distinct evidence task is **authority-compromise evidence provenance / compromise-onset adjudication / false-revocation resistance / recovery-key independence**. Define who is authorized to assert/prove compromise, how conflicting or uncertain compromise-onset claims are appraised, how a malicious monitor/operator is prevented from weaponizing revocation as permanent denial of service, and how recovery/replacement authority remains independent from both the compromised source key and the evidence producer alleging compromise. Preserve append-only historical receipts and compose with the newly frozen source/promise authority transparency contract.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact full executable gate + conflict audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178 / LAB-093 — READY; source/promise authority transparency + compromise propagation plus prior source-authority/checkpoint/source-ingestion/capability/recovery/convergence/continuous-assurance contracts frozen; exact RED/GREEN pending.
- #179..181 / LAB-094..096 — READY; retained-authority graph contracts frozen.
- #182..184 / LAB-097..099 — READY; authenticated provenance/global chain/recovery contracts frozen.
- #185 / LAB-100 — READY; activation implementation/capability authority contracts frozen.
