# Current Lab State

Last updated: 2026-09-07

## Active objective
LAB-086 — finish the exact executable/security gate for asymmetric break-glass history migration, then reconcile/merge only if every real-schema regression and conflict audit passes.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165 remains open at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`; GitHub currently reports `mergeable=false`; do not change draft/merge status without the exact retained gate.
- The alternate-UNIQUE `strict_fence.py` fix is already published byte-exact: commit `05d8e75a636818afcb32e085d464c9fa9171dea5`, blob `eb2198354d222ad0ad6b7d751bf5c649157b6b36`. Do not redo that publication task.
- Other open draft/IN_PROGRESS PRs observed: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175; LAB-092/#176 PR #177.
- Frozen design follow-ups: LAB-093/#178; LAB-094..096/#179..181; LAB-097..099/#182..184; LAB-100/#185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; directly re-inspected open PRs, PR #165 and issue #178. PR #165 remains open/draft at head `ee210a47221b6df53f3518aa3af74f76c5b0122b` and still retains the full exact branch execution gate before ready/merge.

Current-run capability probe:
- `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git /tmp/ai-runtime-lab-run14` failed before repository execution with `Could not resolve host: github.com` (exit 128);
- GitHub connector reads/writes remain available;
- therefore no new LAB-086 behavioral/compile PASS is claimed and PR #165 remains draft.

Completed the recorded distinct fallback and froze `HISTORICAL_TRUST_BUNDLE_CAPTURE_ATOMICITY_PRE_DECOMMISSION_FREEZE_COMPLETENESS_PROOF_V1_FROZEN` in `research/2026-09-07-historical-trust-bundle-capture-atomicity-pre-decommission-freeze-completeness-proof-v1.md`, main commit `9bd8115f10c4e3f99636f90d05f5d038ffea719d`; #178 comment `5567592081` records the result.

Key decisions:
- `FINAL_ARCHIVE_CLOSED` requires four distinct properties: object authenticity, archive integrity, semantic completeness and causal closure; none substitutes for another;
- decommission safety is protocol-atomic, not cross-provider ACID: one immutable campaign generation must bind causal freeze, exact requirement universe, captured exact-byte root, positive closure of async evidence frontiers, independent completeness verdict and final archive seal;
- introduced `ArchiveCaptureCampaignV1`, `PreDecommissionFreezeV1`, `EvidenceRequirementManifestV1`, `CapturedEvidenceObjectV1`, `ArchiveCaptureManifestV1`, `ArchiveSealV1`, `ArchiveCompletenessProofV1` and `DecommissionAuthorizationV1`;
- archive requirements are derived from the frozen semantic inventory/schema/policy, not from whatever object list the archive builder happened to copy;
- every required slot discharges only as `PRESENT_AUTHENTIC`, independently justified `NOT_APPLICABLE_AUTHENTIC`, `UNKNOWN_MISSING`, or `CONTRADICTORY`; only the first two permit closure;
- freeze must mechanically prevent new target-generation consequential roots, while already-accepted asynchronous evidence delivery is positively drained to a provider/log/status closure frontier; a quiet period is never a completeness proof;
- exact provider-origin bytes are retained and sealed; normalized adapter/model views are indexing aids, not authority evidence;
- an independent checker recomputes required slots/source frontiers; the archive builder cannot self-attest consequential absence;
- any crash before final `CLOSED` leaves decommission unauthorized; partial capture resumes against the same frozen generation and may not redefine the universe to make the archive pass;
- source disappearance or permanently missing required evidence before closure yields `UNKNOWN_PARTIAL_CAPTURE`, potentially permanently;
- decommission before archive closure and later-discovered omitted required material have explicit fraud/contradiction semantics; repair is additive and dependent finalization/GC proofs become stale;
- added an 80-case RED-first matrix for freeze, requirement-universe completeness, async drain, exact capture, checker independence, seal/storage, crash recovery and decommission/fraud repair.

Primary donors: RFC 4998 Evidence Record Syntax; RFC 3161 time stamping; AWS CloudTrail signed digest chaining/final digest behavior; Sigstore self-contained bundle/offline verification material.

## Known failures / blockers
- LAB-086 remains priority #1. Remaining blocker is exact source execution, not `strict_fence.py` publication.
- Direct git transport failed in this run before repository execution with DNS resolution failure.
- PR #165 must remain draft until branch-local dependency-blob verification, retained strict/thaw subgate, real-schema LAB-086 tests, compileall, unsafe expected-failure seed, security reconciliation and branch/main conflict audit execute on exact source.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-088 still needs supported-integration + LAB-084/085/086 downstream execution.
- LAB-091 still needs real LAB-080/LAB-082 integration, two-worker/crash, timeout-after-commit/UNKNOWN, LAB-087 composition and full exact regressions.
- LAB-090/LAB-100, LAB-092 and LAB-097..099 remain design-frozen but require exact executable RED/GREEN before production integration.
- LAB-093 implementation must compose capability inventory/delegation/revocation/lease/handoff/provider-fence/portable-receipt/historical-trust/archive-capture contracts with LAB-087 isolation. It must not treat current trust state, adapter assertions, one-region readback, session consistency, eventual convergence, timestamps alone, a single authentic receipt, a quiet period, or an archive-builder-selected Merkle root as global completeness proof.

## Exact next action
LAB-086 first: if exact branch source execution becomes available, check out/reconstruct current PR head `ee210a47221b6df53f3518aa3af74f76c5b0122b`, verify expected `strict_fence.py` blob lineage includes `eb2198354d222ad0ad6b7d751bf5c649157b6b36`, then execute the retained strict/thaw subgate (alternate-UNIQUE, primary-key/history/proof replacement, NULL identities, minimal thaw, conflict algorithms), compileall, exact branch-local LAB-080→086 dependency-blob verification, every normal LAB-086 real-schema test, unsafe legacy-promotion expected-failure seed, and final security/reconciliation + branch/main conflict audit. Fix every observed blocker before changing draft/merge status.

If exact execution remains unavailable, next distinct evidence task is **archive replica durability / independent custody / correlated-loss and restore-verifiability semantics**. Define minimum independent archive custody/failure domains, whether physical replication/erasure coding is sufficient or logically independent administration/key custody is required, anti-rollback/anti-equivocation across archive replicas, periodic restore/proof-of-retrievability drills, immutable replica manifests and renewal propagation, failure/recovery states, and the conditions under which destructive GC may safely depend on archived historical evidence.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; publication fixed; exact full executable gate + conflict audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; activation authority + canonical/global provenance/recovery contracts frozen; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; migration/provenance contracts frozen; exact RED/full gate pending.
- #178 / LAB-093 — READY; capability delegation + descendant revocation + D2 lease + issuer handoff + external-provider fence + portable receipt + historical trust + archival capture/completeness contracts frozen; exact RED/GREEN pending.
- #179..181 / LAB-094..096 — READY; retained-authority graph contracts frozen.
- #182..184 / LAB-097..099 — READY; authenticated provenance/global chain/recovery contracts frozen.
- #185 / LAB-100 — READY; activation implementation/capability authority contracts frozen.
