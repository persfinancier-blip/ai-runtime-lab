# Current Lab State

Last updated: 2026-09-07

## Active objective
LAB-086 — finish the exact executable/security gate for asymmetric break-glass history migration, then reconcile/merge only if every real-schema regression and conflict audit passes.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165 remains open at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`; GitHub currently reports `mergeable=false`.
- The alternate-UNIQUE `strict_fence.py` fix is already published byte-exact: commit `05d8e75a636818afcb32e085d464c9fa9171dea5`, blob `eb2198354d222ad0ad6b7d751bf5c649157b6b36`. Do not redo that publication task.
- Other open draft/IN_PROGRESS PRs: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175; LAB-092/#176 PR #177.
- Frozen design follow-ups: LAB-093/#178; LAB-094..096/#179..181; LAB-097..099/#182..184; LAB-100/#185.

## Last completed step
Re-read `AGENTS.md`, this handoff, and `prompts/SELF_RESUME.md`; re-inspected open issues and PRs. Current PR #165 is still open/draft, `mergeable=false`, head `ee210a47221b6df53f3518aa3af74f76c5b0122b`.

Current-run capability probe:
- `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git /tmp/ai-runtime-lab-run11` failed before repository execution with `Could not resolve host: github.com` (exit 128);
- connector reads/writes remain available;
- therefore no new LAB-086 test/compile behavioral PASS is claimed and PR #165 remains draft.

Completed the recorded distinct fallback and froze `PROVIDER_FENCE_ATTESTATION_EXTERNAL_PROVIDER_NON_EQUIVOCATION_CROSS_REGION_MONOTONICITY_V1_FROZEN` in `research/2026-09-07-provider-fence-attestation-external-provider-non-equivocation-cross-region-monotonicity-v1.md`, main commit `79b9614b9ef24edac1070658ceba136e1ae1bfdc`; #178 comment `5565408229` records the result.

Key decisions:
- `HANDOFF_CLOSED` requires evidence of one monotonic provider fence across every material consequential path, not generic HA/strong-consistency claims;
- defined `ProviderFenceAttestationV1` with provider/implementation identity, resource scope, fence generation, predecessor, provider-native commit/order token, consistency mode, independent regional readbacks, stale-epoch rejection evidence, resolved/replication frontier, issuer root epoch and adapter semantics digest;
- provider classes: P1 global-linearizable fence; P2 bounded-propagation fence with mechanically enforced finite horizon; P3 session/causal-only; P4 eventual/LWW;
- P3/P4 cannot prove global revocation closure without stronger broker mediation or finite non-renewable expiry;
- readback of the new epoch is positive evidence only; closure also requires negative evidence that old epoch cannot still perform consequential renewal/use, or a proven finite drain horizon;
- cross-region closure requires every material endpoint frontier to include the cutover, or formal drain/disable, or remain `UNKNOWN`/pending;
- failover is safe only through shared monotonic authority, authenticated terminal checkpoint handoff, or complete finite-expiry drain;
- timeout-after-send remains `UNKNOWN_PENDING_RECONCILIATION`;
- froze contradiction proofs for stale-region acceptance, provider equivocation, failover rollback, and consistency-mode downgrade plus an 80-case RED-first matrix.

Primary donors: Google Spanner external consistency/TrueTime as positive globally ordered shape; Azure Cosmos session/strong consistency as a boundary between causal/session evidence and global closure; DynamoDB Global Tables MREC/LWW as negative evidence that convergence is not fencing.

## Known failures / blockers
- LAB-086 remains priority #1. Remaining blocker is exact source execution, not `strict_fence.py` publication.
- Direct git transport failed in this run before repository execution with DNS resolution failure.
- PR #165 reports `mergeable=false`; branch/main conflict audit must run on exact source before ready/merge.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-088 still needs supported-integration + LAB-084/085/086 downstream execution.
- LAB-091 still needs real LAB-080/LAB-082 integration, two-worker/crash, timeout-after-commit/UNKNOWN, LAB-087 composition and full exact regressions.
- LAB-090/LAB-100, LAB-092 and LAB-097..099 remain design-frozen but require exact executable RED/GREEN before production integration.
- LAB-093 implementation must compose capability inventory/delegation/revocation/lease/handoff/provider-fence contracts with LAB-087 isolation and must not treat local leadership, one-region readback, session consistency or eventual convergence as global revocation proof.

## Exact next action
LAB-086 first: if exact branch source execution becomes available, check out/reconstruct current PR head `ee210a47221b6df53f3518aa3af74f76c5b0122b`, verify the expected `strict_fence.py` blob lineage includes `eb2198354d222ad0ad6b7d751bf5c649157b6b36`, then execute the retained strict/thaw subgate (alternate-UNIQUE, primary-key/history/proof replacement, NULL identities, minimal thaw, conflict algorithms), compileall, exact branch-local LAB-080→086 dependency-blob verification, every normal LAB-086 real-schema test, unsafe legacy-promotion expected-failure seed, and final security/reconciliation + branch/main conflict audit. Fix every observed blocker before changing draft/merge status.

If exact execution remains unavailable, next distinct evidence task is **provider-fence proof portability / provider-native receipt authenticity / adapter-verifier independence semantics**. Define when external provider commit/version/readback evidence is independently verifiable rather than merely asserted by the same SDK/adapter that issued the consequential request; specify signed receipts vs TLS/API observations, canonicalization, replay binding, independent verifier domains, SDK/API semantic drift, and what evidence is sufficient to survive later provider/API migration and historical audit.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; publication fixed; exact full executable gate + conflict audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; activation authority + canonical/global provenance/recovery contracts frozen; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; migration/provenance contracts frozen; exact RED/full gate pending.
- #178 / LAB-093 — READY; capability delegation + descendant revocation + D2 lease + issuer handoff + external-provider fence attestation contracts frozen; exact RED/GREEN pending.
- #179..181 / LAB-094..096 — READY; retained-authority graph contracts frozen.
- #182..184 / LAB-097..099 — READY; authenticated provenance/global chain/recovery contracts frozen.
- #185 / LAB-100 — READY; activation implementation/capability authority contracts frozen.
