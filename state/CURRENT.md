# Current Lab State

Last updated: 2026-09-07

## Active objective
LAB-086 — finish the exact executable/security gate for asymmetric break-glass history migration, then reconcile/merge only if every real-schema regression and conflict audit passes.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165 at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`; current `get_pr_info` reports open/draft, `mergeable=false`; do not change draft/merge status without the exact retained gate.
- Other open draft/IN_PROGRESS PRs observed: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175; LAB-092/#176 PR #177.
- Frozen design follow-ups: LAB-093/#178; LAB-094..096/#179..181; LAB-097..099/#182..184; LAB-100/#185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected current open PRs and PR #165.

Current-run capability probe:
- `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git /tmp/ai-runtime-lab-auto14` failed before repository execution with `Could not resolve host: github.com` (exit 128);
- GitHub connector reads/writes and web research remain available;
- therefore no new LAB-086 behavioral/compile PASS is claimed and PR #165 remains draft.

Completed the recorded distinct fallback and froze `WITNESS_ACTIVATION_EPOCH_DISTRIBUTION_VERIFIER_FRESHNESS_STALE_POLICY_CACHE_INVALIDATION_V1_FROZEN` in `research/2026-09-07-witness-activation-epoch-distribution-verifier-freshness-stale-policy-cache-invalidation-v1.md`, commit `e8afcc33a633302f5ddd4b88c554d1579f29f5a6`; #178 comment `5573880885` records the result.

Key decisions:
- `VALID_WITNESS_SIGNATURE(E) != CURRENT_WITNESS_AUTHORITY(E)`;
- cache TTL/refetch behavior cannot revoke or extend authority;
- each verifier persists monotonic `TrustedActivationFrontierV1`; lower epoch is rollback and same-epoch divergent content is equivocation;
- activation transition is append-only authority data binding predecessor/successor, recovery authorization, policy/key digests and predecessor fencing;
- current-authority decisions require positive authenticated freshness evidence; wall-clock age alone is not sufficient;
- offline verification can prove historical authority at a bundled frontier, but after freshness expiry returns `CURRENT_AUTHORITY_UNKNOWN_OFFLINE` rather than current validity;
- during partition, a verifier that knows E+1 never accepts E again; an E-only verifier may use E only within an explicitly signed operation-class bounded-staleness allowance, then consequential mutation fails closed as `CURRENT_AUTHORITY_UNKNOWN_PARTITIONED`;
- recovery closure includes representative distribution audits proving relying boundaries reject E; unreachable boundaries remain explicitly unknown;
- added `WitnessActivationEpochPublicationV1`, `TrustedActivationFrontierV1`, `ActivationFreshnessProofV1`, `VerifierEpochDecisionV1`, `EpochDistributionAuditV1` and a 40-case RED-first matrix.

Primary donors: TUF monotonic metadata/rollback/freeze/expiry semantics; RFC 6960 `thisUpdate`/`nextUpdate`; RFC 9162 split-view consistency; C2SP witness/cosignature checkpoint semantics.

## Known failures / blockers
- LAB-086 remains priority #1. Remaining blocker is exact source execution.
- Direct git transport failed in this run before repository execution with DNS resolution failure.
- PR #165 must remain draft until branch-local dependency-blob verification, retained strict/thaw subgate, real-schema LAB-086 tests, compileall, unsafe expected-failure seed, security reconciliation and branch/main conflict audit execute on exact source.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-088 still needs supported-integration + LAB-084/085/086 downstream execution.
- LAB-091 still needs real LAB-080/LAB-082 integration, two-worker/crash, timeout-after-commit/UNKNOWN, LAB-087 composition and full exact regressions.
- LAB-090/LAB-100, LAB-092 and LAB-097..099 remain design-frozen but require exact executable RED/GREEN before production integration.
- LAB-093 exact implementation must compose all frozen capability/delegation/revocation/lease/handoff/provider-fence/receipt/historical-trust/archive/verifier/conformance/oracle/publication/witness/recovery/freshness contracts with LAB-087 isolation; none of the design freezes substitute for executable proof.

## Exact next action
LAB-086 first: if exact branch source execution becomes available, check out/reconstruct current PR head `ee210a47221b6df53f3518aa3af74f76c5b0122b`, verify exact branch-local source/blob lineage, then execute the retained strict/thaw subgate (alternate-UNIQUE, primary-key/history/proof replacement, NULL identities, minimal thaw, conflict algorithms), compileall, exact branch-local LAB-080→086 dependency-blob verification, every normal LAB-086 real-schema test, unsafe legacy-promotion expected-failure seed, and final security/reconciliation + branch/main conflict audit. Fix every observed blocker before changing draft/merge status.

If exact execution remains unavailable, next distinct evidence task is **freshness clock authority / secure-time rollback / suspend-resume and long-offline verifier semantics**. Define what time source may validate `thisUpdate`/`nextUpdate`-style epoch freshness; how monotonic elapsed time, secure wall time and externally witnessed checkpoints compose; what happens after VM snapshot rollback, device suspend, clock reset, RTC loss or years-long offline operation; and how to prevent a stale verifier from regaining authority merely because its local clock was rolled backward or unavailable.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact full executable gate + conflict audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178 / LAB-093 — READY; witness activation-epoch distribution/freshness contract now also frozen; exact RED/GREEN pending.
- #179..181 / LAB-094..096 — READY; retained-authority graph contracts frozen.
- #182..184 / LAB-097..099 — READY; authenticated provenance/global chain/recovery contracts frozen.
- #185 / LAB-100 — READY; activation implementation/capability authority contracts frozen.
