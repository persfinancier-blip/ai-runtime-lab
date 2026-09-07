# Current Lab State

Last updated: 2026-09-08

## Active objective
LAB-086 — finish the exact executable/security gate for asymmetric break-glass history migration, then reconcile/merge only if every real-schema regression and conflict audit passes.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165 at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`; keep draft and do not merge without the exact retained gate.
- Other open draft/IN_PROGRESS PRs observed: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175; LAB-092/#176 PR #177.
- Frozen design follow-ups: LAB-093/#178; LAB-094..096/#179..181; LAB-097..099/#182..184; LAB-100/#185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected current open PRs and #178; resumed LAB-086 first.

Current-run capability probe:
- `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git /tmp/ai-runtime-lab-auto18` failed before repository execution with `Could not resolve host: github.com` (exit 128);
- GitHub connector reads/writes and web research remain available;
- therefore no new LAB-086 behavioral/compile PASS is claimed and PR #165 remains draft.

Completed the recorded distinct fallback and froze `RECOVERY_POLICY_TRANSPARENCY_BOOTSTRAP_OFFLINE_ROOT_CUSTODY_TOTAL_LOSS_RECONSTITUTION_V1_FROZEN` in `research/2026-09-08-recovery-policy-transparency-bootstrap-offline-root-custody-total-loss-reconstitution-v1.md`, commit `e2e0c2af7decfb5437521c2d420cab0ff21f0cb0`; #178 comment `5575739311` records the result.

Key decisions:
- total loss/compromise of all current recovery signers plus all previously authenticated independent continuity authority is **not** an ordinary cryptographic rotation;
- the old trust domain must fail closed as `RECOVERY_AUTHORITY_UNAVAILABLE_NO_CONTINUITY_PROOF` rather than accept a self-authorized replacement root;
- continuous disaster recovery is allowed only through a pre-disaster authenticated, independently controlled `RecoveryContinuityRootV1`/policy;
- if that continuity root is also lost, restoration is an explicit external rebootstrap/new trust lineage with relying-party/governance acceptance; reusing the old lineage would launder false continuity;
- external rebootstrap cannot retroactively erase historical compromise uncertainty;
- offline root custody must preserve threshold and control-domain separation in both primary and backup material; one archive containing every share is not independent custody;
- `RootCustodyManifestV1`, `GovernanceReconstitutionEvidenceV1`, `TrustDomainRebootstrapV1`, transparency/ceremony requirements and dispute states were frozen;
- conflicting independently credible reconstitution packages produce `REBOOTSTRAP_GOVERNANCE_DISPUTE_NO_AUTOMATIC_ACCEPT`;
- added a 40-case RED-first matrix across continuity loss, offline custody, lineage laundering, governance forks, external-channel correlation and historical-trust behavior.

Primary donors: RFC 9718 initial trust-anchor establishment versus RFC 5011 in-band succession; TUF out-of-band Root recovery after threshold compromise; Sigstore distributed root keyholders/signing events; NIST SP 800-57 Part 1 Rev. 5 key lifecycle/custody/recovery.

## Known failures / blockers
- LAB-086 remains priority #1. Remaining blocker is exact source execution.
- Direct git transport failed in this run before repository execution with DNS resolution failure.
- PR #165 must remain draft until branch-local dependency-blob verification, retained strict/thaw subgate, real-schema LAB-086 tests, compileall, unsafe expected-failure seed, security reconciliation and branch/main conflict audit execute on exact source.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-088 still needs supported-integration + LAB-084/085/086 downstream execution.
- LAB-091 still needs real LAB-080/LAB-082 integration, two-worker/crash, timeout-after-commit/UNKNOWN, LAB-087 composition and full exact regressions.
- LAB-090/LAB-100, LAB-092 and LAB-097..099 remain design-frozen but require exact executable RED/GREEN before production integration.
- LAB-093 exact implementation must compose all frozen capability/delegation/revocation/lease/handoff/provider-fence/receipt/historical-trust/archive/verifier/conformance/oracle/publication/witness/recovery/freshness/secure-time/rebootstrap contracts with LAB-087 isolation; none of the design freezes substitute for executable proof.

## Exact next action
LAB-086 first: if exact branch source execution becomes available, check out/reconstruct current PR head `ee210a47221b6df53f3518aa3af74f76c5b0122b`, verify exact branch-local source/blob lineage, then execute the retained strict/thaw subgate (alternate-UNIQUE, primary-key/history/proof replacement, NULL identities, minimal thaw, conflict algorithms), compileall, exact branch-local LAB-080→086 dependency-blob verification, every normal LAB-086 real-schema test, unsafe legacy-promotion expected-failure seed, and final security/reconciliation + branch/main conflict audit. Fix every observed blocker before changing draft/merge status.

If exact execution remains unavailable, next distinct evidence task is **rebootstrap relying-party convergence / ecosystem split-brain / legacy-client quarantine and migration semantics**. Define how a non-continuous new trust lineage is distributed to heterogeneous verifiers without silent stale-client acceptance; how old-lineage and new-lineage operations coexist, quarantine or bridge; what acceptance/freshness evidence each verifier must retain; how rollback/partition/long-offline clients behave; and what evidence is required before declaring ecosystem migration complete. Do not reinterpret local acceptance as universal continuity.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact full executable gate + conflict audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178 / LAB-093 — READY; total-loss recovery reconstitution/offline-root/bootstrap contract now also frozen; exact RED/GREEN pending.
- #179..181 / LAB-094..096 — READY; retained-authority graph contracts frozen.
- #182..184 / LAB-097..099 — READY; authenticated provenance/global chain/recovery contracts frozen.
- #185 / LAB-100 — READY; activation implementation/capability authority contracts frozen.
