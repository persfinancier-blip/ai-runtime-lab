# Current Lab State

Last updated: 2026-09-08

## Active objective
LAB-086 — finish the exact executable/security gate for asymmetric break-glass history migration, then reconcile/merge only if every real-schema regression and conflict audit passes.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165 at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`; keep draft and do not merge without the exact retained gate.
- Other open draft/IN_PROGRESS PRs observed this run: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175; LAB-092/#176 PR #177.
- Frozen design follow-ups: LAB-093/#178; LAB-094..096/#179..181; LAB-097..099/#182..184; LAB-100/#185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected current open PRs/issues; resumed LAB-086 first.

Current-run capability probe:
- `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git /tmp/ai-runtime-lab-auto19` failed before repository execution with `Could not resolve host: github.com` (exit 128);
- GitHub connector reads/writes and web research remain available;
- therefore no new LAB-086 behavioral/compile PASS is claimed and PR #165 remains draft.

Completed the recorded distinct fallback and froze `REBOOTSTRAP_RELYING_PARTY_CONVERGENCE_ECOSYSTEM_SPLIT_BRAIN_LEGACY_CLIENT_QUARANTINE_V1_FROZEN` in `research/2026-09-08-rebootstrap-relying-party-convergence-ecosystem-split-brain-legacy-client-quarantine-v1.md`, commit `711de2f74b2faca464ebcbd71ecd6a04e0cdeea5`; #178 comment `5576175616` records the result.

Key decisions:
- `NEW_LINEAGE_PUBLISHED != NEW_LINEAGE_ACCEPTED != ECOSYSTEM_CONVERGED`;
- a non-continuous rebootstrap must carry a distinct lineage identity and explicit relying-party acceptance; same endpoint/product identity is not continuity evidence;
- dual trust is a bounded compatibility bridge, never cryptographic continuity proof;
- once a verifier accepts the new lineage, it cannot downgrade to unrestricted old-lineage current authority;
- long-offline or partitioned legacy clients may retain bounded historical/read compatibility but fail closed for consequential current authority after explicit staleness allowance expires;
- server-side enforcement must reject old-lineage consequential authority after cutover so stale clients cannot silently produce post-migration effects;
- explicit `RelyingPartyMigrationStateV1`, `EcosystemConvergenceProofV1`, `LineageBridgeAuthorizationV1`, quarantine states and 10 fraud-proof classes were frozen;
- ecosystem completion requires both fresh acceptance across policy-designated critical verifier cohorts and enforcement-point rejection of prohibited old-lineage authority;
- for open/unbounded client populations, universal convergence is not provable; the defensible terminal claim is `ENFORCEMENT_CUTOVER_COMPLETE_WITH_RESIDUAL_LEGACY_CLIENTS`;
- added a 32-case RED-first matrix covering bootstrap acceptance, dual trust, rollback/partition/offline behavior, server admission, convergence evidence and governance forks.

Primary donors: RFC 9718 initial trust versus in-band succession and validator-local acceptance policy; SPIFFE Federation explicit trust-domain/bundle binding, bootstrap-vs-refresh distinction, advance key publication and periodic refresh.

## Known failures / blockers
- LAB-086 remains priority #1. Remaining blocker is exact source execution.
- Direct git transport failed in this run before repository execution with DNS resolution failure.
- PR #165 must remain draft until branch-local dependency-blob verification, retained strict/thaw subgate, real-schema LAB-086 tests, compileall, unsafe expected-failure seed, security reconciliation and branch/main conflict audit execute on exact source.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-088 still needs supported-integration + LAB-084/085/086 downstream execution.
- LAB-091 still needs real LAB-080/LAB-082 integration, two-worker/crash, timeout-after-commit/UNKNOWN, LAB-087 composition and full exact regressions.
- LAB-090/LAB-100, LAB-092 and LAB-097..099 remain design-frozen but require exact executable RED/GREEN before production integration.
- LAB-093 exact implementation must compose all frozen capability/delegation/revocation/lease/handoff/provider-fence/receipt/historical-trust/archive/verifier/conformance/oracle/publication/witness/recovery/freshness/secure-time/rebootstrap/convergence contracts with LAB-087 isolation; none of the design freezes substitute for executable proof.

## Exact next action
LAB-086 first: if exact branch source execution becomes available, check out/reconstruct current PR head `ee210a47221b6df53f3518aa3af74f76c5b0122b`, verify exact branch-local source/blob lineage, then execute the retained strict/thaw subgate (alternate-UNIQUE, primary-key/history/proof replacement, NULL identities, minimal thaw, conflict algorithms), compileall, exact branch-local LAB-080→086 dependency-blob verification, every normal LAB-086 real-schema test, unsafe legacy-promotion expected-failure seed, and final security/reconciliation + branch/main conflict audit. Fix every observed blocker before changing draft/merge status.

If exact execution remains unavailable, next distinct evidence task is **ecosystem convergence evidence authenticity / verifier-cohort inventory / enforcement-cutover attestation and legacy decommission proof**. Define how migration telemetry itself is authenticated and made rollback/equivocation-resistant; how critical verifier cohorts are enumerated without letting missing clients disappear from the denominator; how enforcement points attest rejection of old-lineage consequential operations; how decommission is proven across gateways/caches/offline replicas; and what contradiction state applies when client-side acceptance reports and server-side rejection evidence disagree. Do not let observability data become authority or let absence of telemetry masquerade as migration completion.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact full executable gate + conflict audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178 / LAB-093 — READY; total-loss rebootstrap plus relying-party convergence/legacy quarantine contracts frozen; exact RED/GREEN pending.
- #179..181 / LAB-094..096 — READY; retained-authority graph contracts frozen.
- #182..184 / LAB-097..099 — READY; authenticated provenance/global chain/recovery contracts frozen.
- #185 / LAB-100 — READY; activation implementation/capability authority contracts frozen.
