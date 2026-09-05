# Current Lab State

Last updated: 2026-09-05

## Active objective
LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to authenticated cutoff + Ed25519 public-only history without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165; branch `lab/086-asymmetric-break-glass-history`; observed head `ee210a47221b6df53f3518aa3af74f76c5b0122b`.
- Authoritative pending lineage: predecessor blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; retained hidden-rowid patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; required composed target blob `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- Draft/IN_PROGRESS stack: LAB-088/#167 PR #172; LAB-090/#169 PR #175; LAB-091/#170 PR #173; LAB-092/#176 PR #177.
- Frozen design follow-ups: LAB-093/#178; LAB-094..096/#179..181; LAB-097..099/#182..184; LAB-100/#185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected live open issues and PRs. GitHub connector is healthy.

Re-probed LAB-086 direct transport in this runtime: `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git /tmp/ai-runtime-lab` failed before repository access with `Could not resolve host: github.com` (exit 128). Connector exposes repository bytes and normal Contents writes but no supported machine operation that consumes exact predecessor bytes + retained unified patch and emits transformed bytes. `strict_fence.py` was not model-reserialized/mutated; no new LAB-086 behavioral PASS is claimed.

Completed the recorded distinct fallback: froze `POST_REROOT_TRUST_EPOCH_EFFECT_NAMESPACE_MIGRATION_V1_FROZEN` in `research/2026-09-05-post-reroot-trust-epoch-effect-namespace-migration-v1.md`, main commit `a4868a53e4f76b094ad532c808875482c7ba7957`; #178 comment `5549278450` records the result.

Key decisions: human re-root does not recreate missing application-idempotency evidence. An old effect namespace with irrecoverable historical coverage transitions one-way to `SEALED_HISTORY_INCOMPLETE` and never becomes MISS-capable again. Any technically possible future resumption must use fresh `trust_epoch_id` + `effect_namespace_id` in canonical operation/effect identity, with explicit external provider/broker request-domain cutover evidence preventing collisions with the historical epoch. Migration is staged `PROPOSED -> SECURITY_AUTHORIZED -> CUTOVER_PREPARED -> EXTERNAL_CUTOVER_ANCHORED -> PROVENANCE_COMMITTED -> VERIFIED -> ACTIVE`; crashes cannot roll back into the old namespace. Legacy clients may not silently inherit the new epoch after a discontinuity. Ordinary admin/provider/worker/DR-recovery authority cannot authorize the cutover. Actual production activation that abandons unavailable historical non-reuse evidence remains a genuine product/security owner decision. A 35-case RED-first minimum matrix is frozen.

Research rationale: RFC 6962 append-only/consistency semantics for preserving authenticated history rather than rewriting it; NIST SP 800-57 lifecycle separation for deactivating future authority without erasing historical verification meaning; existing LAB TUF-derived root-continuity contracts for authenticated one-way transitions.

## Known failures / blockers
- LAB-086 remains priority #1. Do not manually/model-reserialize security-critical `strict_fence.py`.
- Exact predecessor and retained patch bytes are observable through the connector, but no supported byte-preserving transform/materialization bridge to a Contents API replacement has been observed.
- Normal Contents API requires complete replacement text and is not a predecessor+patch transform.
- Authoritative lineage remains `d4a6a40f...` + `61841b58...` -> `b78e7c98...`.
- Keep PRs #165/#172/#173/#175/#177 draft until retained exact gates execute.
- LAB-088 still needs supported integration + LAB-084/085/086 downstream execution.
- LAB-091 still needs real LAB-080/LAB-082 integration, two-worker/crash, timeout-after-commit/UNKNOWN, LAB-087 composition and full exact regressions.
- LAB-090/LAB-100, LAB-092 and LAB-097..099 must use the frozen shared canonical V1 encoding, parent-linked chain, atomic append/recovery protocol, durable SQL storage, verifier/planner, external evidence continuity, recovery executor and finite broker startup machine; no independent locally-valid provenance islands.
- LAB-093 must implement the frozen least-capability façade, session revocation/re-entry, request/effect boundary, durable request/effect registry, application idempotency/result delivery, authenticated install/retention, bounded-growth/resource-exhaustion, consumed-key archival/checkpoint, authenticated archive retrieval, archive manifest/index/replica lifecycle, archive-loss/DR authority, DR checkpoint-escrow/root recovery, DR escrow issuance/rotation/policy lifecycle, human re-root ceremony and post-re-root trust/effect epoch migration contracts; production implementation waits for executable RED/GREEN.
- LAB-093..100 production implementation waits for exact executable RED/GREEN.
- No production post-re-root cutover may be activated without explicit human-owner product/security authorization bound to the exact loss/cutover payload.

## Exact next action
LAB-086 first: probe only for a genuinely supported machine transform/materialization path that can consume the exact connector-returned predecessor blob plus retained patch bytes without model reserialization.

If such a bridge appears: mechanically reconstruct predecessor and require Git blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; apply only patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; require candidate blob `b78e7c98e35138719f77c482c7f1aab36b702de7`; publish through normal Contents API; re-fetch/hash-verify; then execute hidden-rowid + receipt-NULL + alternate-UNIQUE regressions, strict/thaw subgate, LAB-080→086 real-ledger gate, unsafe legacy-promotion seed, compileall and final audit.

If exact source execution becomes available first: run LAB-088 supported/downstream gates, LAB-091 full supported-surface gates, then implement tests first for the frozen canonical encoder/chain/atomic-append/storage/verifier/evidence/recovery/broker/session/request/registry/application-idempotency/install-retention/capacity/archive/retrieval/lifecycle/DR/escrow/human-reroot/post-reroot-epoch contracts and execute LAB-090/LAB-100, LAB-092, LAB-094..096 and LAB-097..099 RED matrices before production refactors.

If neither capability appears: next distinct evidence task is to freeze an **epoch-aware client/API negotiation and external cutover adapter contract**. Define how legacy callers are rejected rather than silently defaulted after a trust discontinuity; canonical wire/request versioning; explicit epoch acknowledgement; provider request-ID construction; adapter capability attestation; mixed old/new client behavior; retry semantics across cutover; rollback/replay protection; and how an external provider that cannot domain-separate idempotency keys permanently blocks activation for that effect class. This may define mechanics/tests only and must not authorize an actual production cutover.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; activation authority + canonical/global provenance/recovery contracts frozen; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; migration bound to retained authority graph + global provenance/recovery contracts; exact RED/full gate pending.
- #178 / LAB-093 — READY; façade/session/request/effect/registry/application-idempotency/install-retention/bounded-capacity/archive/checkpoint/retrieval/lifecycle/archive-loss-DR/escrow-root-recovery/escrow-lifecycle/human-reroot/post-reroot-epoch contracts frozen; exact RED/GREEN pending.
- #179..181 / LAB-094..096 — READY; unified retained-authority graph + RED matrix frozen.
- #182..184 / LAB-097..099 — READY; authenticated provenance/global chain/recovery contracts frozen.
- #185 / LAB-100 — READY; sealed/registered activation authority + construction/restart/upgrade/global provenance/recovery contracts frozen.
