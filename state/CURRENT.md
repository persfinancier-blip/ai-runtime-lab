# Current Lab State

Last updated: 2026-09-06

## Active objective
LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to authenticated cutoff + Ed25519 public-only history without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165; live head `ee210a47221b6df53f3518aa3af74f76c5b0122b`.
- Authoritative pending lineage retained from prior handoff: predecessor blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; retained hidden-rowid patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; required composed target blob `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- Draft/IN_PROGRESS stack remains open: LAB-088/#167 PR #172; LAB-090/#169 PR #175; LAB-091/#170 PR #173; LAB-092/#176 PR #177.
- Frozen design follow-ups: LAB-093/#178; LAB-094..096/#179..181; LAB-097..099/#182..184; LAB-100/#185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected open issues and PR #165. PR #165 remains open/draft at `ee210a47221b6df53f3518aa3af74f76c5b0122b`; its published body still requires strict/thaw, exact LAB-080→086 dependency closure, real LAB-086/unsafe-seed/compileall execution and final audit before ready/merge.

Re-probed direct source execution with:

`git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git /tmp/ai-runtime-lab-probe`

It failed before repository execution with `Could not resolve host: github.com` (exit 128). No security-critical source mutation was attempted and no new LAB-086 behavioral PASS is claimed.

Completed the recorded distinct fallback: froze `MONITOR_OBSERVATION_RECEIPT_PUBLICATION_PROMISE_OMISSION_CHALLENGE_RESPONSE_V1_FROZEN` in `research/2026-09-06-monitor-observation-receipt-publication-promise-omission-challenge-response-v1.md`, main commit `98f5cbeafcdfa3bf0cfe84d74273a26671f835de`; #178 comment `5558292629` records the result.

Key decisions:
- a publication promise is an authenticated, externally durable statement binding subject, origin generation, baseline/frontier, deadline/skew/time-source, publication surfaces, policy and key generation;
- observation receipts bind the exact challenge, requester/monitor/origin generations, baseline, returned checkpoint/proof digests, response class, channel, time source and policy;
- challenge transcripts are nonce-bound/replay-resistant and survive restart;
- timeout or HTTP absence alone can produce `STALE`/degraded coverage but never `OMISSION_PROVEN`;
- `OMISSION_SUSPECTED` requires stronger independent evidence such as a newer authenticated mirror/archive/witness checkpoint, an expired signed publication promise, or overlapping independent challenger evidence;
- `OMISSION_PROVEN` requires a violated authenticated statement or prior authenticated knowledge plus contradictory post-condition evidence (e.g. stale-after-knowledge, selective contradictory service, acknowledged-storage downgrade);
- challenger/monitor diversity collapses across common operator/network/DNS/CDN/clock/collector domains;
- clock uncertainty fails closed rather than manufacturing a deadline violation;
- explicit 80-case RED-first matrix is frozen across promises, replay resistance, receipt semantics, stale/suspected/proven boundaries, clock/partition/selective-service and recovery/auditability.

Primary donors: RFC 9162 SCT/MMD promise semantics and later signed-frontier/inclusion auditing; C2SP checkpoint/witness mechanisms for persistable authenticated frontier state. Donor mechanisms only; no production monitor/prover network or behavioral compatibility PASS is claimed.

## Known failures / blockers
- LAB-086 remains priority #1. Do not manually/model-reserialize security-critical `strict_fence.py`.
- Exact predecessor/patch identities are known, but no supported byte-preserving connector-resource→machine transform/materialization bridge has been observed; large blob connector responses truncate and line-chunk reconstruction would be model-mediated.
- Direct git transport currently fails before repository execution with DNS resolution failure.
- Keep PRs #165/#172/#173/#175/#177 draft until retained exact gates execute.
- LAB-088 still needs supported integration + LAB-084/085/086 downstream execution.
- LAB-091 still needs real LAB-080/LAB-082 integration, two-worker/crash, timeout-after-commit/UNKNOWN, LAB-087 composition and full exact regressions.
- LAB-090/LAB-100, LAB-092 and LAB-097..099 remain design-frozen but require exact executable RED/GREEN before production integration.
- LAB-093 production implementation must compose all frozen evidence/privacy/policy/schema/model/proof/adjudicator/trust-frontier/monitoring contracts rather than creating independent locally-valid authority islands.
- No production omission verdict may treat silence alone as cryptographic proof.

## Exact next action
LAB-086 first: probe only for a genuinely supported machine transform/materialization path that can consume exact connector-returned predecessor + retained patch bytes without model reserialization.

If such a bridge appears: mechanically reconstruct predecessor and require Git blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; apply only patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; require candidate blob `b78e7c98e35138719f77c482c7f1aab36b702de7`; publish through normal Contents API; re-fetch/hash-verify; then execute hidden-rowid + receipt-NULL + alternate-UNIQUE regressions, strict/thaw subgate, LAB-080→086 real-ledger gate, unsafe legacy-promotion seed, compileall and final audit.

If exact source execution becomes available first: run LAB-088 supported/downstream gates, LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

If neither capability appears: next distinct evidence task is to freeze **publication-promise fulfillment / verifiable non-inclusion / subject-index completeness semantics**. Determine exactly when an append-only Merkle frontier can prove that promised subject X was not incorporated by deadline (ordinary inclusion trees generally do not prove arbitrary non-membership); compare indexed transparency maps/sparse-Merkle or commitment-to-ordered-subject-set mechanisms; define canonical subject keys, duplicate/retry semantics, promise→leaf binding, completeness/range proofs, migration/rehash behavior, and RED cases that prevent an invalid `OMISSION_PROVEN` verdict from a merely missing inclusion proof.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; activation authority + canonical/global provenance/recovery contracts frozen; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; migration bound to retained authority graph + global provenance/recovery contracts; exact RED/full gate pending.
- #178 / LAB-093 — READY; evidence/privacy/policy/schema/model/proof/adjudicator/trust-frontier/monitor-completeness/challenge-response contracts frozen; exact RED/GREEN pending.
- #179..181 / LAB-094..096 — READY; unified retained-authority graph + RED matrix frozen.
- #182..184 / LAB-097..099 — READY; authenticated provenance/global chain/recovery contracts frozen.
- #185 / LAB-100 — READY; sealed/registered activation authority + construction/restart/upgrade/global provenance/recovery contracts frozen.
