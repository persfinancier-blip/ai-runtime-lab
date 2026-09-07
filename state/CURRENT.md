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
Re-read `AGENTS.md`, this handoff, and `prompts/SELF_RESUME.md`; re-inspected open PRs and PR #165 directly. PR #165 is still open/draft, `mergeable=false`, base `main`, head `ee210a47221b6df53f3518aa3af74f76c5b0122b`.

Current-run capability probe:
- `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git /tmp/ai-runtime-lab-run12` failed before repository execution with `Could not resolve host: github.com` (exit 128);
- connector reads/writes remain available;
- therefore no new LAB-086 test/compile behavioral PASS is claimed and PR #165 remains draft.

Completed the recorded distinct fallback and froze `PROVIDER_FENCE_PROOF_PORTABILITY_PROVIDER_NATIVE_RECEIPT_AUTHENTICITY_ADAPTER_VERIFIER_INDEPENDENCE_V1_FROZEN` in `research/2026-09-07-provider-fence-proof-portability-provider-native-receipt-authenticity-adapter-verifier-independence-v1.md`, main commit `5fcf078c3900ca3ecf33944e8b69717a5fdf1db7`; #178 comment `5566006621` records the result.

Key decisions:
- R0 adapter-generated assertions are telemetry/debug evidence, never provider authority;
- R1 authenticated transport observations help reconciliation but do not automatically survive historical key/API drift as proof;
- R2 provider-signed/native receipts are the preferred minimum provider-origin evidence for positive/negative claims when available;
- R3 transparency/digest-chain and R4 quorum/multi-witness receipts are required when the security claim additionally depends on historical non-equivocation/global order;
- `AUTHENTIC(receipt) != NON_EQUIVOCATING(provider)`; contradictory authentic receipts invalidate dependent closure rather than resolving latest-wins;
- defined `PortableProviderReceiptV1` binding provider/API semantic generation, resource, operation ID/class, request digest, fence generation, provider order token, result, failure domain, issuer/key epoch, trust bundle, verifier policy and optional transparency/timestamp/quorum material;
- exact raw provider-origin evidence, historical trust bundle, frozen semantic schema and verifier policy must be retained before provider/API migration or destructive GC;
- issuer adapter and historical verifier must be independently checkable for E2/E3/E4 consequences;
- unknown semantic revision, missing historical trust evidence, timeout-after-send or absence of a receipt remain `UNKNOWN`/invalid according to policy, never success;
- frozen contradiction/fraud proofs cover adapter fabrication, request-binding mismatch, provider equivocation, semantic drift misverification and trust rollback;
- added an 80-case RED-first matrix for authenticity, historical trust, verifier independence, schema/API migration, transparency/non-equivocation, crash/replay/recovery and GC.

Primary donors: AWS CloudTrail signed digest-chain validation; Sigstore bundle/Rekor offline verification material; DSSE typed envelopes; RFC3161 as trusted-time-only evidence; Google Cloud HSM independently verifiable signed attestation + certificate chains.

## Known failures / blockers
- LAB-086 remains priority #1. Remaining blocker is exact source execution, not `strict_fence.py` publication.
- Direct git transport failed in this run before repository execution with DNS resolution failure.
- PR #165 reports `mergeable=false`; branch/main conflict audit must run on exact source before ready/merge.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-088 still needs supported-integration + LAB-084/085/086 downstream execution.
- LAB-091 still needs real LAB-080/LAB-082 integration, two-worker/crash, timeout-after-commit/UNKNOWN, LAB-087 composition and full exact regressions.
- LAB-090/LAB-100, LAB-092 and LAB-097..099 remain design-frozen but require exact executable RED/GREEN before production integration.
- LAB-093 implementation must compose capability inventory/delegation/revocation/lease/handoff/provider-fence/portable-receipt contracts with LAB-087 isolation. It must not treat adapter assertions, one-region readback, session consistency, eventual convergence, timestamps, or a single authentic receipt as global non-equivocation proof.

## Exact next action
LAB-086 first: if exact branch source execution becomes available, check out/reconstruct current PR head `ee210a47221b6df53f3518aa3af74f76c5b0122b`, verify expected `strict_fence.py` blob lineage includes `eb2198354d222ad0ad6b7d751bf5c649157b6b36`, then execute the retained strict/thaw subgate (alternate-UNIQUE, primary-key/history/proof replacement, NULL identities, minimal thaw, conflict algorithms), compileall, exact branch-local LAB-080→086 dependency-blob verification, every normal LAB-086 real-schema test, unsafe legacy-promotion expected-failure seed, and final security/reconciliation + branch/main conflict audit. Fix every observed blocker before changing draft/merge status.

If exact execution remains unavailable, next distinct evidence task is **portable receipt key-lifecycle / historical trust-status / transparency-root rotation and archival survivability semantics**. Define how a receipt remains verifiable after provider signing-key expiry/revocation, CA/root rotation, transparency-log key rotation or retirement, account/provider decommission and offline archival; distinguish "key compromised after event" from "key untrusted at event", define retained OCSP/CRL/status/timestamp/checkpoint evidence, and specify when historical verification must become `UNKNOWN` rather than silently applying current trust state.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; publication fixed; exact full executable gate + conflict audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; activation authority + canonical/global provenance/recovery contracts frozen; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; migration/provenance contracts frozen; exact RED/full gate pending.
- #178 / LAB-093 — READY; capability delegation + descendant revocation + D2 lease + issuer handoff + external-provider fence + portable provider-receipt contracts frozen; exact RED/GREEN pending.
- #179..181 / LAB-094..096 — READY; retained-authority graph contracts frozen.
- #182..184 / LAB-097..099 — READY; authenticated provenance/global chain/recovery contracts frozen.
- #185 / LAB-100 — READY; activation implementation/capability authority contracts frozen.
