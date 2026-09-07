# Current Lab State

Last updated: 2026-09-07

## Active objective
LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to authenticated cutoff + Ed25519 public-only history without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165 remains open at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`.
- PR #165 currently reports `mergeable=false`; do not merge/ready it before retained exact gates and conflict audit execute.
- Authoritative pending hidden-rowid lineage remains: predecessor blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; retained patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; required composed target blob `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- Other open draft/IN_PROGRESS PRs: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175; LAB-092/#176 PR #177.
- Frozen design follow-ups: LAB-093/#178; LAB-094..096/#179..181; LAB-097..099/#182..184; LAB-100/#185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; re-inspected open issues, PRs and branches. LAB-086 remains the highest-priority unfinished task.

Re-probed LAB-086 in this run:
- direct `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git /tmp/ai-runtime-lab` failed before repository execution with `Could not resolve host: github.com` (exit 128);
- connector read surfaces remain available, but supported Contents writes accept complete UTF-8 replacement payloads and no supported byte-preserving machine transform/materialization bridge was observed for exact predecessor+patch composition;
- low-level blob/tree/ref construction remains forbidden and manual/model reserialization of security-critical `strict_fence.py` remains prohibited;
- therefore `strict_fence.py` was not mutated and no new LAB-086 behavioral PASS is claimed.

Completed the recorded distinct fallback and froze `REVOCATION_AWARE_LEASE_RENEWAL_LINEARIZATION_CLOCK_PARTITION_SAFETY_V1_FROZEN` in `research/2026-09-07-revocation-aware-lease-renewal-linearization-clock-partition-safety-v1.md`, main commit `a74db556cd250fffb14e2911c41fb07c6c41e176`; #178 comment `5564545790` records the result.

Key decisions:
- D2 is valid only when renewal, revocation and consequential use-time enforcement are bound to one authenticated monotonic lease/root generation;
- prefer online-mediated D2: each consequential use checks current server-side generation/state, so partitions fail closed and holder wall clock is irrelevant;
- provider-expiring D2 is allowed only when the provider itself enforces finite maximum expiry and stale issuers cannot extend it;
- `RENEW` and `REVOKE` linearize in one authority domain; revoke-before-renew must reject, renew-before-revoke remains bounded by an immutable maximum horizon;
- holder wall-clock/NTP/token `exp` checked only by the holder cannot prove closure; use logical epochs for ordering and explicit provider/authority time uncertainty for finite horizons;
- freeze issuer epochs, crash-safe idempotent request IDs, `RenewalPathInventoryV1`, `LeaseIssuanceProofV1`, `LeaseRevocationBarrierV1`, `LeaseClosureProofV1`, fraud proofs and an 80-case RED-first matrix;
- any unknown material refresh path (SDK/provider/session refresh, queue extension, plugin/child renew authority, manual/admin renewal, recovery recreation) prevents D2 closure.

Primary donors: etcd Lease API, Kubernetes Lease API, Spanner/TrueTime uncertainty semantics.

## Known failures / blockers
- LAB-086 remains priority #1. Do not manually/model-reserialize security-critical `strict_fence.py`.
- Direct git transport failed in this run before repository execution with DNS resolution failure.
- Exact predecessor + retained patch are connector-readable, but no supported byte-preserving composition-to-Contents bridge has been observed.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-088 still needs supported-integration + LAB-084/085/086 downstream execution.
- LAB-091 still needs real LAB-080/LAB-082 integration, two-worker/crash, timeout-after-commit/UNKNOWN, LAB-087 composition and full exact regressions.
- LAB-090/LAB-100, LAB-092 and LAB-097..099 remain design-frozen but require exact executable RED/GREEN before production integration.
- LAB-093 implementation must compose frozen capability inventory/delegation/revocation/lease contracts with LAB-087 isolation and must not treat client-local TTL as revocation authority.

## Exact next action
LAB-086 first: probe only for a genuinely supported byte-preserving machine transform/materialization path that consumes exact connector-returned predecessor blob `d4a6a40f...` + retained patch blob `61841b58...` without model reserialization and emits the complete candidate for normal Contents API publication.

If such a bridge appears: mechanically reconstruct predecessor and require Git blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; apply only retained patch `61841b58be42b01b97ca223567cbf9f428f7f0ce`; require candidate blob `b78e7c98e35138719f77c482c7f1aab36b702de7`; conflict-check the live target; publish through normal Contents API; re-fetch/hash-verify; execute hidden-rowid + receipt-NULL + alternate-UNIQUE regressions, strict/thaw subgate, LAB-080→086 real-ledger gate, unsafe legacy-promotion seed, compileall and final security audit.

If exact source execution becomes available first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

If neither capability appears: next distinct evidence task is **lease/enforcement quorum handoff / issuer-epoch transition / provider-fence continuity semantics**. Define how a D2 authority changes replica membership, consensus generation, broker/provider implementation or signing root without a gap where old and new issuers can both renew; specify joint/overlap handoff, stale-issuer fencing, provider-side epoch continuity, crash/partition behavior, and historical proof verification after old issuers are retired.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; activation authority + canonical/global provenance/recovery contracts frozen; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; migration/provenance contracts frozen; exact RED/full gate pending.
- #178 / LAB-093 — READY; capability delegation + descendant revocation + D2 lease protocol contracts frozen; exact RED/GREEN pending.
- #179..181 / LAB-094..096 — READY; retained-authority graph contracts frozen.
- #182..184 / LAB-097..099 — READY; authenticated provenance/global chain/recovery contracts frozen.
- #185 / LAB-100 — READY; activation implementation/capability authority contracts frozen.
