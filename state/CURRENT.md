# Current Lab State

Last updated: 2026-09-08

## Active objective
LAB-086 — finish the exact executable/security gate for asymmetric break-glass history migration, then reconcile/merge only if every real-schema regression and conflict audit passes.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165 at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`; keep draft and do not merge without the exact retained gate.
- Other open draft/IN_PROGRESS PRs: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175; LAB-092/#176 PR #177.
- Frozen design follow-ups: LAB-093/#178; LAB-094..096/#179..181; LAB-097..099/#182..184; LAB-100/#185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected current open issues/PRs; resumed LAB-086 first.

Current-run capability probe:
- `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git /tmp/ai-runtime-lab-auto21` failed before repository execution with `Could not resolve host: github.com` (exit 128);
- GitHub connector reads/writes and web research remain available;
- PR #165 remains open/draft at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`, current connector read `mergeable=false`;
- therefore no new LAB-086 behavioral/compile PASS is claimed and no draft/merge state was changed.

Completed the recorded distinct fallback and froze `CONVERGENCE_EVIDENCE_KEY_LIFECYCLE_VERIFIER_INDEPENDENCE_TOPOLOGY_COMPLETENESS_NEGATIVE_PROBE_SAMPLING_V1_FROZEN` in `research/2026-09-08-convergence-evidence-key-lifecycle-verifier-independence-topology-completeness-negative-probe-sampling-v1.md`, main commit `bd6b45b1d04de58747b62ac9b49c9260e705d5de`; #178 comment `5577151220` records the result.

Key decisions:
- `VALID_EVIDENCE_SIGNATURE != CURRENT_EVIDENCE_ISSUER_AUTHORITY`; evidence/verifier authority is generation- and policy-bound, with explicit retirement/compromise history and historical-verification semantics;
- `DISTINCT_VERIFIER_IDENTITIES != INDEPENDENT_VERIFIERS`; verifier quorum counting requires an independence appraisal across operator, key custody, implementation/build, runtime/deployment, appraisal-policy, evidence-source and supply-chain failure domains;
- `SERVICE_DISCOVERY_SNAPSHOT != COMPLETE_AUTHORITY_TOPOLOGY`; high-assurance cutover reconciles differently controlled desired/control-plane and observed/effective data-plane topology views;
- authority topology is versioned; autoscaled/new endpoints enter coverage before completion, and lost watch continuity forces a fresh snapshot/reconciliation;
- `NEGATIVE_PROBE_PASS != UNIVERSAL_L0_REJECTION`; bounded critical fleets prefer exhaustive backend-pinned probes, while randomized production-path probes require post-snapshot unpredictable challenges, backend/responder identity, anti-steering conditions and declared statistical bounds;
- target topology is committed before challenge generation so inconvenient replicas cannot be removed after sampling is known;
- transparency receipts prove statement registration/history, not semantic truth;
- frozen `ConvergenceEvidenceAuthorityV1`, `AttestationVerifierIndependenceProfileV1`, `AuthorityTopologySnapshotV1`, `TopologyCoverageLedgerV1`, `NegativeCutoverChallengeV1`, `NegativeCutoverProbeResultV1`, 12 fraud/contradiction proof classes and a 60-case RED-first matrix.

Primary donors: RFC 9334 RATS; NIST SP 800-57 Pt.1 Rev.5; RFC 9943 SCITT; Kubernetes EndpointSlice and `resourceVersion` list/watch semantics; SPIRE node/workload attestation.

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

If exact execution remains unavailable, next distinct evidence task is **convergence-evidence revocation propagation / post-completion invalidation / continuous assurance and re-open semantics**. Define how a previously `CONVERGENCE_PROVEN_*` frontier is invalidated when a verifier/evidence key compromise, resurrected endpoint, stale DR/failover activation, topology omission, probe-steering proof or contradictory evidence is discovered later; how relying parties learn and authenticate that invalidation; how historical receipts remain verifiable without being treated as current authority; what states replace a previously closed convergence verdict; and what evidence/quorum is required to re-close convergence without deleting or rewriting the original failure history. Do not allow completion to become a permanent one-time certificate when the evidence authority or topology can later be disproven.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact full executable gate + conflict audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178 / LAB-093 — READY; rebootstrap, convergence, authenticated evidence, verifier-independence/topology/negative-probe contracts frozen; exact RED/GREEN pending.
- #179..181 / LAB-094..096 — READY; retained-authority graph contracts frozen.
- #182..184 / LAB-097..099 — READY; authenticated provenance/global chain/recovery contracts frozen.
- #185 / LAB-100 — READY; activation implementation/capability authority contracts frozen.
