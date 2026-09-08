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
- `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git /tmp/ai-runtime-lab-auto23` failed before repository execution with `Could not resolve host: github.com` (exit 128);
- GitHub connector reads/writes and web research remain available;
- PR #165 remains open/draft at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`, current connector read `mergeable=false`;
- therefore no new LAB-086 behavioral/compile PASS is claimed and no draft/merge state was changed.

Completed the recorded distinct fallback and froze `CONTINUOUS_ASSURANCE_AUTHORITY_LIFECYCLE_INVALIDATION_INDEPENDENCE_EVENT_LOSS_COMPACTION_V1_FROZEN` in `research/2026-09-08-continuous-assurance-authority-lifecycle-invalidation-independence-event-loss-compaction-v1.md`, main commit `4bdefd62496f7edfb61a420013535c46d1a28bfc`; #178 comment `5578099464` records the result.

Key decisions:
- `VALID_INVALIDATION_SIGNATURE != CURRENT_INVALIDATION_ISSUER_AUTHORITY != INDEPENDENT_INVALIDATION_EVIDENCE != APPRAISED_CONTRADICTION != CURRENT_CONVERGENCE_INVALIDATION`;
- invalidation authority is a first-class generation/freshness-governed authority; routine rotation requires predecessor+successor authorization and compromise intervals affect issuance-time trust;
- one strong monitor contradiction may trigger immediate local quarantine/fail-closed, but high-assurance global invalidation requires a threshold of independently appraised failure/control domains; correlated monitors do not count as independent votes;
- an unknown watch/event interval yields `CONVERGENCE_CURRENT_STATUS_UNKNOWN_EVENT_GAP`; event silence is never evidence that no invalidation occurred;
- recovery after a gap requires fresh authenticated authority/verdict/topology/contradiction state, reconciliation, affected-endpoint proof refresh where continuity was lost, then a new event frontier;
- reclosure creates a new verdict generation and must consume every intervening contradiction/invalidation; false-positive adjudication supersedes but never deletes the original evidence;
- compaction is permitted only as a cryptographic checkpoint over an immutable contiguous prefix, chained to prior trusted checkpoints and carrying unresolved contradictions forward; it must never erase invalidations, losing forks, or historical receipts;
- frozen a 48-case RED-first matrix spanning authority lifecycle, independence/local quarantine, event-loss recovery, reclosure and compaction.

Primary donors: RFC 9334 RATS verifier/appraisal/freshness separation; RFC 5280 revocation numbering/freshness/base+delta reconstruction; RFC 9943 SCITT append-only receipts; RFC 9162 CT consistency/split-view evidence; Kubernetes `resourceVersion` list/watch and `410 Gone` recovery semantics.

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

If exact execution remains unavailable, next distinct evidence task is **continuous-assurance checkpoint authority / archive availability and survivability / checkpoint transparency split-view detection / proof-of-prefix completeness**. Define who may issue/rotate/revoke `ContinuousAssuranceCheckpointV1`; how relying parties distinguish an unavailable archive from a maliciously pruned contradiction history; what minimum independently replicated/transparency-backed evidence is needed so checkpoint compaction remains auditable after archive loss; and how conflicting checkpoint roots for the same prefix/generation are detected and adjudicated without LWW. Preserve the rule that current operation may be freshness-bounded while historical contradiction provenance remains independently recoverable/auditable.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact full executable gate + conflict audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178 / LAB-093 — READY; rebootstrap, convergence, authenticated evidence, verifier-independence/topology/negative-probe, continuous-assurance invalidation/reclosure, and assurance-authority/event-loss/compaction contracts frozen; exact RED/GREEN pending.
- #179..181 / LAB-094..096 — READY; retained-authority graph contracts frozen.
- #182..184 / LAB-097..099 — READY; authenticated provenance/global chain/recovery contracts frozen.
- #185 / LAB-100 — READY; activation implementation/capability authority contracts frozen.
