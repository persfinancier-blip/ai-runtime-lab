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
- `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git /tmp/ai-runtime-lab-auto22` failed before repository execution with `Could not resolve host: github.com` (exit 128);
- GitHub connector reads/writes and web research remain available;
- PR #165 remains open/draft at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`, current connector read `mergeable=false`;
- therefore no new LAB-086 behavioral/compile PASS is claimed and no draft/merge state was changed.

Completed the recorded distinct fallback and froze `CONVERGENCE_EVIDENCE_REVOCATION_PROPAGATION_POST_COMPLETION_INVALIDATION_CONTINUOUS_ASSURANCE_V1_FROZEN` in `research/2026-09-08-convergence-evidence-revocation-propagation-post-completion-invalidation-continuous-assurance-v1.md`, main commit `b662954e6b99f49f26bce3c9ab248c2ced8005b5`; #178 comment `5577643158` records the result.

Key decisions:
- `HISTORICALLY_PROVEN_CONVERGENCE != CURRENTLY_VALID_CONVERGENCE`; a close is a freshness-bounded verdict over a specific evidence/topology frontier, not a permanent certificate;
- later authenticated contradictions create a new monotonic `ConvergenceInvalidationV1`; the old convergence artifact and transparency receipt remain historical evidence but lose current authority where superseded;
- mandatory reopen triggers include evidence/verifier key compromise intersecting relied-on issuance intervals, verifier-policy supersession, topology omission, resurrected endpoints, stale DR/failover activation, negative-probe steering, effective L0 acceptance, topology-watch continuity loss, freshness expiry and verifier-independence collapse;
- relying parties persist `TrustedConvergenceFrontierV1`; lower invalidation generations are rollback and equal-generation/different-content is equivocation;
- topology continuity after close requires authenticated version/watch continuity or a fresh consistent snapshot plus reconciliation; a watch gap degrades current status to `CONVERGENCE_CURRENT_STATUS_UNKNOWN_STALE` until repaired;
- new/resurrected endpoints do not inherit convergence from service membership and must pass post-close admission before consequential routing;
- reclosure requires a new verdict generation consuming every contradiction/invalidation since the prior close; failure intervals and losing branches remain append-only history;
- conflicting same-generation invalidations/reclosures yield `CONVERGENCE_EVIDENCE_CONFLICT_NO_COMPLETION`;
- frozen a 48-case RED-first matrix spanning key authority, topology resurrection/DR, effective-path contradictions/probe steering, propagation/freshness, reclosure/history and crash/governance semantics.

Primary donors: RFC 9334 RATS freshness/appraisal semantics; RFC 9943 SCITT receipt/history semantics; TUF monotonic version/expiration/recovery semantics; Kubernetes `resourceVersion` list/watch and EndpointSlice topology aggregation.

## Known failures / blockers
- LAB-086 remains priority #1. Remaining blocker is exact source execution.
- Direct git transport failed in this run before repository execution with DNS resolution failure.
- PR #165 must remain draft until branch-local dependency-blob verification, retained strict/thaw subgate, real-schema LAB-086 tests, compileall, unsafe expected-failure seed, security reconciliation and branch/main conflict audit execute on exact source.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-088 still needs supported-integration + LAB-084/085/086 downstream execution.
- LAB-091 still needs real LAB-080/LAB-082 integration, two-worker/crash, timeout-after-commit/UNKNOWN, LAB-087 composition and full exact regressions.
- LAB-090/LAB-100, LAB-092 and LAB-097..099 remain design-frozen but require exact executable RED/GREEN before production integration.
- LAB-093 exact implementation must compose all frozen capability/delegation/revocation/lease/handoff/provider-fence/receipt/historical-trust/archive/verifier/conformance/oracle/publication/witness/recovery/freshness/secure-time/rebootstrap/convergence/evidence/continuous-assurance contracts with LAB-087 isolation; none of the design freezes substitute for executable proof.

## Exact next action
LAB-086 first: if exact branch source execution becomes available, check out/reconstruct current PR head `ee210a47221b6df53f3518aa3af74f76c5b0122b`, verify exact branch-local source/blob lineage, then execute the retained strict/thaw subgate (alternate-UNIQUE, primary-key/history/proof replacement, NULL identities, minimal thaw, conflict algorithms), compileall, exact branch-local LAB-080→086 dependency-blob verification, every normal LAB-086 real-schema test, unsafe legacy-promotion expected-failure seed, and final security/reconciliation + branch/main conflict audit. Fix every observed blocker before changing draft/merge status.

If exact execution remains unavailable, next distinct evidence task is **continuous-assurance authority lifecycle / invalidation-issuer independence / event-loss recovery / reclosure freshness compaction semantics**. Define how the authority that issues `ConvergenceInvalidationV1` is itself rotated/revoked and appraised; how independent invalidation sources avoid one compromised monitor becoming unilateral revocation authority; how relying parties recover safely after missing an unknown interval of invalidation/topology events; and whether old verdict/invalidation chains may be compacted into checkpoints without losing contradiction provenance or enabling rollback. Preserve the rule that historical receipts remain verifiable while current authority is monotonic and freshness-bounded.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact full executable gate + conflict audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178 / LAB-093 — READY; rebootstrap, convergence, authenticated evidence, verifier-independence/topology/negative-probe and continuous-assurance invalidation/reclosure contracts frozen; exact RED/GREEN pending.
- #179..181 / LAB-094..096 — READY; retained-authority graph contracts frozen.
- #182..184 / LAB-097..099 — READY; authenticated provenance/global chain/recovery contracts frozen.
- #185 / LAB-100 — READY; activation implementation/capability authority contracts frozen.
