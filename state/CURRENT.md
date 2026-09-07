# Current Lab State

Last updated: 2026-09-07

## Active objective
LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to authenticated cutoff + Ed25519 public-only history without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165; recorded head `ee210a47221b6df53f3518aa3af74f76c5b0122b`.
- Authoritative pending hidden-rowid lineage: predecessor blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; retained patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; required composed target blob `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- Other open draft/IN_PROGRESS PRs: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175; LAB-092/#176 PR #177.
- Frozen design follow-ups: LAB-093/#178; LAB-094..096/#179..181; LAB-097..099/#182..184; LAB-100/#185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; re-inspected open issues and PRs. LAB-086 remains the highest-priority unfinished task.

Re-probed LAB-086 in this run:
- direct `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git /tmp/ai-runtime-lab` failed before repository execution with `Could not resolve host: github.com` (exit 128);
- GitHub connector successfully returned the complete exact predecessor blob `d4a6a40f...` and complete retained patch blob `61841b58...`;
- supported normal Contents writes still require a complete UTF-8 payload, and no supported byte-preserving machine transform/materialization action was observed that consumes exact predecessor+patch bytes and feeds the result directly into Contents API;
- low-level blob/tree/ref construction is forbidden by owner contract, and manual/model reserialization of security-critical `strict_fence.py` remains prohibited;
- therefore `strict_fence.py` was not mutated and no new LAB-086 behavioral PASS is claimed.

Completed the recorded distinct fallback and froze `DESCENDANT_DISCOVERY_REVOCATION_SET_CLOSURE_OFFLINE_RESURRECTION_V1_FROZEN` in `research/2026-09-07-descendant-discovery-revocation-set-closure-offline-resurrection-v1.md`, main commit `df79f8ff5ecc9b6b77cdd42bd7fba71d9c1c058a`; #178 comment `5564164106` records the result.

Key decisions:
- revocation completion is closure over every potentially usable descendant, not every row currently known to a registry;
- descendant authority is classified D1 mechanically enumerable/mediated, D2 logically discoverable with bounded server-enforced lease, D3 independently observable but incomplete, D4 unmediated/non-clawback;
- D1 may reach `CLOSED_LOGICAL` through authenticated complete enumeration + no-new-delegation barrier + mediated-use rejection; D2 only after an authenticated no-renew frontier plus finite maximum lease/uncertainty horizon;
- D3/D4 cannot treat absence of observation as completeness and remain `UNKNOWN` unless stronger physical containment proves otherwise;
- offline workers, retry/dead-letter queues, duplicated/transferred OS handles, provider sessions, broker epochs and recovery checkpoints are first-class revocation descendants/frontiers;
- `CLOSED_LOGICAL` is distinct from `CLOSED_PHYSICAL`; logical revocation does not imply physical clawback;
- froze `RevocationCampaignV1`, `RevocationClosureProofV1`, omitted-descendant/post-close-use/stale-queue/old-broker-epoch fraud proofs, GC interlocks and an 80-case RED-first matrix;
- LAB-093 production architecture should prefer revocable brokered indirection or short server-validated leases over handing consequential raw authority to arbitrary descendants.

Primary donors: FreeBSD Capsicum delegation/attenuation; Linux `SCM_RIGHTS`; Fuchsia handle/object visibility; distributed lease semantics/reconfiguration; Macaroons attenuation with verifier enforcement.

## Known failures / blockers
- LAB-086 remains priority #1. Do not manually/model-reserialize security-critical `strict_fence.py`.
- Direct git transport failed in this run before repository execution with DNS resolution failure.
- Exact predecessor + retained patch are fully readable via connector, but no supported byte-preserving composition-to-Contents bridge has been observed.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-088 still needs supported-integration + LAB-084/085/086 downstream execution.
- LAB-091 still needs real LAB-080/LAB-082 integration, two-worker/crash, timeout-after-commit/UNKNOWN, LAB-087 composition and full exact regressions.
- LAB-090/LAB-100, LAB-092 and LAB-097..099 remain design-frozen but require exact executable RED/GREEN before production integration.
- LAB-093 implementation must compose the frozen authority/evidence/schema/inventory/delegation/revocation contracts with LAB-087 isolation rather than create locally valid authority islands.

## Exact next action
LAB-086 first: probe only for a genuinely supported byte-preserving machine transform/materialization path that consumes exact connector-returned predecessor blob `d4a6a40f...` + retained patch blob `61841b58...` without model reserialization and emits the complete candidate for normal Contents API publication.

If such a bridge appears: mechanically reconstruct predecessor and require Git blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; apply only retained patch `61841b58be42b01b97ca223567cbf9f428f7f0ce`; require candidate blob `b78e7c98e35138719f77c482c7f1aab36b702de7`; conflict-check the live target; publish through normal Contents API; re-fetch/hash-verify; execute hidden-rowid + receipt-NULL + alternate-UNIQUE regressions, strict/thaw subgate, LAB-080→086 real-ledger gate, unsafe legacy-promotion seed, compileall and final security audit.

If exact source execution becomes available first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

If neither capability appears: next distinct evidence task is **revocation-aware lease issuance / renewal linearization / clock-and-partition safety semantics**. Define the exact D2 protocol that makes a bounded revocation horizon trustworthy: authoritative server time vs monotonic epochs, renewal-vs-revoke races, maximum lease enforcement, partition behavior, crash recovery, provider-side expiry, clock rollback/skew, fencing of stale issuers, and proof that no hidden renewal path can extend old authority beyond the declared horizon.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; activation authority + canonical/global provenance/recovery contracts frozen; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; migration/provenance contracts frozen; exact RED/full gate pending.
- #178 / LAB-093 — READY; capability delegation + descendant revocation-set closure contracts frozen; exact RED/GREEN pending.
- #179..181 / LAB-094..096 — READY; retained-authority graph contracts frozen.
- #182..184 / LAB-097..099 — READY; authenticated provenance/global chain/recovery contracts frozen.
- #185 / LAB-100 — READY; activation implementation/capability authority contracts frozen.
