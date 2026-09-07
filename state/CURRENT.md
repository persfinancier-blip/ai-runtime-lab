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
- `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git /tmp/ai-runtime-lab-auto20` failed before repository execution with `Could not resolve host: github.com` (exit 128);
- GitHub connector reads/writes and web research remain available;
- PR #165 remains open/draft at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`, with current connector read `mergeable=false`;
- therefore no new LAB-086 behavioral/compile PASS is claimed and no draft/merge state was changed.

Completed the recorded distinct fallback and froze `ECOSYSTEM_CONVERGENCE_EVIDENCE_AUTHENTICITY_COHORT_INVENTORY_ENFORCEMENT_CUTOVER_DECOMMISSION_V1_FROZEN` in `research/2026-09-08-ecosystem-convergence-evidence-authenticity-cohort-inventory-enforcement-cutover-decommission-v1.md`, commit `2c5dea6c25d1e12f6e88900d63401ab80fcbe8a2`; #178 comment `5576589220` records the result.

Key decisions:
- `TELEMETRY_OBSERVED != TELEMETRY_AUTHENTICATED != CLAIM_APPRAISED != AUTHORITY_PROVEN`;
- `REPORTING_CLIENTS != REQUIRED_COHORT_DENOMINATOR`; governed inventory membership, not a recent-heartbeat query, defines the denominator;
- a missing required cohort remains in the denominator as stale/offline and blocks any completion claim that requires it;
- raw telemetry cannot satisfy convergence policy until subject binding, authenticity, freshness and appraisal-policy identity are established;
- cutover proof requires both configuration/running identity and effective-path behavior, including a policy-designated negative old-lineage consequential admission probe;
- topology coverage must include every authority-bearing gateway/region/cache/worker/failover/DR path designated by policy;
- `NO_LEGACY_TRAFFIC_OBSERVED != LEGACY_AUTHORITY_DECOMMISSIONED`; silence is not retirement evidence;
- decommission requires an authenticated lifecycle transition plus evidence that old authority is fenced/rejected downstream, while historical public verification material remains archived;
- credible contradictions between client/control-plane/data-plane evidence yield `CONVERGENCE_EVIDENCE_CONFLICT_NO_COMPLETION`, never LWW/majority telemetry reconciliation;
- a closed governed fleet may reach `CONVERGENCE_PROVEN_FOR_BOUNDED_INVENTORY`; an open/unbounded population can only claim `ENFORCEMENT_CUTOVER_COMPLETE_WITH_RESIDUAL_LEGACY_CLIENTS` after all critical enforcement paths reject prohibited old-lineage authority;
- frozen `VerifierCohortInventoryV1`, `MigrationEvidenceEnvelopeV1`, `EnforcementCutoverAttestationV1`, `LegacyDecommissionProofV1`, `EcosystemConvergenceEvidenceSetV1`, 12 fraud/contradiction classes and a 50-case RED-first matrix.

Primary donors: RFC 9334 RATS for telemetry-as-Evidence, subject binding, appraisal and nonce/epoch freshness; RFC 9943 SCITT for signed statements plus transparency receipts; NIST SP 800-53 CM-8 for accurate/non-duplicative governed component inventory; SPIFFE Federation for domain-bound trust distribution and refresh semantics.

## Known failures / blockers
- LAB-086 remains priority #1. Remaining blocker is exact source execution.
- Direct git transport failed in this run before repository execution with DNS resolution failure.
- PR #165 must remain draft until branch-local dependency-blob verification, retained strict/thaw subgate, real-schema LAB-086 tests, compileall, unsafe expected-failure seed, security reconciliation and branch/main conflict audit execute on exact source.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-088 still needs supported-integration + LAB-084/085/086 downstream execution.
- LAB-091 still needs real LAB-080/LAB-082 integration, two-worker/crash, timeout-after-commit/UNKNOWN, LAB-087 composition and full exact regressions.
- LAB-090/LAB-100, LAB-092 and LAB-097..099 remain design-frozen but require exact executable RED/GREEN before production integration.
- LAB-093 exact implementation must compose all frozen capability/delegation/revocation/lease/handoff/provider-fence/receipt/historical-trust/archive/verifier/conformance/oracle/publication/witness/recovery/freshness/secure-time/rebootstrap/convergence/evidence contracts with LAB-087 isolation; none of the design freezes substitute for executable proof.

## Exact next action
LAB-086 first: if exact branch source execution becomes available, check out/reconstruct current PR head `ee210a47221b6df53f3518aa3af74f76c5b0122b`, verify exact branch-local source/blob lineage, then execute the retained strict/thaw subgate (alternate-UNIQUE, primary-key/history/proof replacement, NULL identities, minimal thaw, conflict algorithms), compileall, exact branch-local LAB-080→086 dependency-blob verification, every normal LAB-086 real-schema test, unsafe legacy-promotion expected-failure seed, and final security/reconciliation + branch/main conflict audit. Fix every observed blocker before changing draft/merge status.

If exact execution remains unavailable, next distinct evidence task is **convergence-evidence issuer/verifier key lifecycle, attestation-verifier independence, topology-discovery completeness and negative-proof sampling semantics**. Define how migration evidence signing/verification keys rotate/revoke without invalidating historical cutover statements; how multiple attestation verifiers are proven independent rather than correlated aliases; how the authority-bearing topology inventory proves discovery coverage for ephemeral autoscaled workers, caches, DR/failover and shadow endpoints; how negative `L0` probes are sampled/challenged so a load balancer cannot route probes only to migrated replicas while stale replicas still serve real traffic; and what fail-closed state applies when topology discovery and observed routing disagree. Do not let the evidence system's own keys, verifier quorum or service-discovery feed become an unaudited root of truth.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact full executable gate + conflict audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178 / LAB-093 — READY; total-loss rebootstrap, relying-party convergence/legacy quarantine, and authenticated convergence-evidence/cutover/decommission contracts frozen; exact RED/GREEN pending.
- #179..181 / LAB-094..096 — READY; retained-authority graph contracts frozen.
- #182..184 / LAB-097..099 — READY; authenticated provenance/global chain/recovery contracts frozen.
- #185 / LAB-100 — READY; activation implementation/capability authority contracts frozen.
