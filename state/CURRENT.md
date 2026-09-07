# Current Lab State

Last updated: 2026-09-07

## Active objective
LAB-086 — finish the exact executable/security gate for asymmetric break-glass history migration, then reconcile/merge only if every real-schema regression and conflict audit passes.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165 remains open at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`; GitHub currently reports `mergeable=false`.
- Important correction to older handoff text: the alternate-UNIQUE `strict_fence.py` fix is already published byte-exact. Commit `05d8e75a636818afcb32e085d464c9fa9171dea5` contains blob `eb2198354d222ad0ad6b7d751bf5c649157b6b36`; compare evidence shows `05d8e75a...` is an ancestor of current PR head (`ee210a4...` is 16 commits ahead). Do **not** redo the obsolete predecessor+patch publication task.
- Other open draft/IN_PROGRESS PRs: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175; LAB-092/#176 PR #177.
- Frozen design follow-ups: LAB-093/#178; LAB-094..096/#179..181; LAB-097..099/#182..184; LAB-100/#185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; re-inspected PR #165 and #178 evidence. Detected and corrected stale state: PR #165 already records the byte-exact alternate-UNIQUE publication, and GitHub commit/compare data confirms `05d8e75a...` is in the current PR ancestry.

Current-run capability probe:
- direct `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git /tmp/ai-runtime-lab` failed before repository execution with `Could not resolve host: github.com` (exit 128);
- connector reads/writes remain available, but there is still no supported way in this runtime to materialize the full branch source tree into an executable local checkout without model/manual reserialization;
- therefore no new LAB-086 test/compile behavioral PASS is claimed and PR #165 remains draft.

Completed the recorded distinct fallback and froze `LEASE_ENFORCEMENT_QUORUM_HANDOFF_ISSUER_EPOCH_PROVIDER_FENCE_CONTINUITY_V1_FROZEN` in `research/2026-09-07-lease-enforcement-quorum-handoff-issuer-epoch-provider-fence-continuity-v1.md`, main commit `399efa08d170a1806011a5e5f0b6fab7d9f43ece`; #178 comment `5564987021` records the result.

Key decisions:
- every accepted D2 renewal/use must bind to one authenticated monotonic `IssuerEpochV1`; retired epochs remain historical-verify-only and cannot issue;
- handoff is three-state: `PREPARED` -> `CUTOVER_COMMITTED` -> `OLD_EPOCH_FENCED`; cutover alone is not closure;
- old+new authority/root overlap authenticates the handoff record but never grants simultaneous post-cutover renewal authority;
- consensus/leader election alone is insufficient: stale issuers must be fenced at the provider/broker enforcement point;
- provider A->B migration is safe only through shared monotonic fencing, authenticated final checkpoint handoff, or complete finite-expiry drain;
- timeout-after-send is `UNKNOWN_PENDING_RECONCILIATION`; partitions do not become success by timeout;
- root rotation is separate from issuer-epoch rotation; a valid signature from a retired root may verify history but cannot authorize fresh renewal;
- froze `IssuerHandoffClosureProofV1`, contradiction/fraud proofs, and an 80-case RED-first matrix.

Primary donors: current etcd runtime reconfiguration/learner mechanics, TUF dual-threshold root continuity, Kubernetes Lease/coordinated leader election, SPIFFE short-lived credential rotation.

## Known failures / blockers
- LAB-086 remains priority #1. The remaining blocker is exact source execution, not publication of `strict_fence.py`.
- Direct git transport failed in this run before repository execution with DNS resolution failure.
- PR #165 reports `mergeable=false`; branch/main conflict audit must run on exact source before ready/merge.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-088 still needs supported-integration + LAB-084/085/086 downstream execution.
- LAB-091 still needs real LAB-080/LAB-082 integration, two-worker/crash, timeout-after-commit/UNKNOWN, LAB-087 composition and full exact regressions.
- LAB-090/LAB-100, LAB-092 and LAB-097..099 remain design-frozen but require exact executable RED/GREEN before production integration.
- LAB-093 implementation must compose frozen capability inventory/delegation/revocation/lease/handoff contracts with LAB-087 isolation and must not treat client-local TTL or leader election alone as revocation authority.

## Exact next action
LAB-086 first: if exact branch source execution becomes available, check out/reconstruct current PR head `ee210a47221b6df53f3518aa3af74f76c5b0122b`, verify the expected `strict_fence.py` blob lineage includes `eb2198354d222ad0ad6b7d751bf5c649157b6b36`, then execute the retained strict/thaw subgate (alternate-UNIQUE, primary-key/history/proof replacement, NULL identities, minimal thaw, conflict algorithms), compileall, exact branch-local LAB-080→086 dependency-blob verification, every normal LAB-086 real-schema test, unsafe legacy-promotion expected-failure seed, and final security/reconciliation + branch/main conflict audit. Fix every observed blocker before changing draft/merge status.

If exact execution remains unavailable, next distinct evidence task is **provider-fence attestation / external-provider non-equivocation / cross-region monotonicity semantics**. Define how a third-party or multi-region provider proves it enforces one monotonic fence outside the local consensus domain; specify attested readback/checkpoints, stale-region behavior, replication lag, equivocation detection, failover continuity, and the evidence threshold required before `HANDOFF_CLOSED` is trustworthy.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; publication fixed; exact full executable gate + conflict audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; activation authority + canonical/global provenance/recovery contracts frozen; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; migration/provenance contracts frozen; exact RED/full gate pending.
- #178 / LAB-093 — READY; capability delegation + descendant revocation + D2 lease + issuer-handoff contracts frozen; exact RED/GREEN pending.
- #179..181 / LAB-094..096 — READY; retained-authority graph contracts frozen.
- #182..184 / LAB-097..099 — READY; authenticated provenance/global chain/recovery contracts frozen.
- #185 / LAB-100 — READY; activation implementation/capability authority contracts frozen.
