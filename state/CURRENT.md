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
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected live open issues and PRs. GitHub connector remains healthy.

Re-probed LAB-086 direct transport in this runtime: `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git /tmp/ai-runtime-lab` failed before repository access with `Could not resolve host: github.com` (exit 128). Connector exposes repository bytes and normal Contents writes but no supported machine operation that consumes exact predecessor bytes + retained unified patch and emits transformed bytes. `strict_fence.py` was not model-reserialized/mutated; no new LAB-086 behavioral PASS is claimed.

Completed the recorded distinct fallback: froze `DR_HUMAN_SECURITY_CEREMONY_REROOT_AUTHORIZATION_V1_FROZEN` in `research/2026-09-05-dr-human-security-ceremony-reroot-authorization-v1.md`, main commit `d9183aad785fe05f6781a8d83e2c531352c7119b`; #178 comment `5549004201` records the result.

Key decisions: automatic DR must stop for compromised escrow threshold, no surviving authenticated quorum, irreconcilable split view, or unprovable root continuity. Human re-root is an exceptional governance transition, not a cryptographic proof that disputed/missing history was correct. Before new root generation the system seals an immutable evidence package. Four logical roles are separated by default: Evidence Custodian, Independent Verifier, Re-root Authorizer and Root Key Custodian. Production re-root requires a pre-disaster ceremony policy, an explicit authorization threshold and at least two independent human/organizational failure domains. New private root material is fresh; durable history receives only public verification material and no reusable symmetric break-glass master secret.

The transition is one-way and permanently typed `HUMAN_REROOT`, never normalized to ordinary root rotation. Split-view choice retains every competing root and the common authenticated prefix as evidence. If exact historical consumed-key/idempotency epochs are unavailable or irrecoverable, human signatures cannot manufacture non-reuse evidence: lookup remains fail-closed and the affected effect namespace stays sealed absent a separate product/security migration. Root commit alone does not reactivate effects; archive/idempotency/startup re-verification plus a DR drill and fresh activation transition are mandatory. A 60-case RED-first matrix is frozen.

Primary donors: TUF root continuity/threshold rotation; Sigstore offline/distributed threshold roots; C2SP witness/cosignature/quorum policy and split-view consistency; NIST SP 800-57 key lifecycle/recovery/trust-anchor guidance.

## Known failures / blockers
- LAB-086 remains priority #1. Do not manually/model-reserialize security-critical `strict_fence.py`.
- Exact predecessor and retained patch bytes are observable through the connector, but no supported byte-preserving transform/materialization bridge to a Contents API replacement has been observed.
- Normal Contents API requires complete replacement text and is not a predecessor+patch transform.
- Authoritative lineage remains `d4a6a40f...` + `61841b58...` -> `b78e7c98...`.
- Keep PRs #165/#172/#173/#175/#177 draft until retained exact gates execute.
- LAB-088 still needs supported integration + LAB-084/085/086 downstream execution.
- LAB-091 still needs real LAB-080/LAB-082 integration, two-worker/crash, timeout-after-commit/UNKNOWN, LAB-087 composition and full exact regressions.
- LAB-090/LAB-100, LAB-092 and LAB-097..099 must use the frozen shared canonical V1 encoding, parent-linked chain, atomic append/recovery protocol, durable SQL storage, verifier/planner, external evidence continuity, recovery executor and finite broker startup machine; no independent locally-valid provenance islands.
- LAB-093 must implement the frozen least-capability façade, session revocation/re-entry, request/effect boundary, durable request/effect registry, application idempotency/result delivery, authenticated install/retention, bounded-growth/resource-exhaustion, consumed-key archival/checkpoint, authenticated archive retrieval, archive manifest/index/replica lifecycle, archive-loss/DR authority, DR checkpoint-escrow/root recovery, DR escrow issuance/rotation/policy lifecycle and human re-root ceremony contracts; production implementation waits for executable RED/GREEN.
- LAB-093..100 production implementation waits for exact executable RED/GREEN.

## Exact next action
LAB-086 first: probe only for a genuinely supported machine transform/materialization path that can consume the exact connector-returned predecessor blob plus retained patch bytes without model reserialization.

If such a bridge appears: mechanically reconstruct predecessor and require Git blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; apply only patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; require candidate blob `b78e7c98e35138719f77c482c7f1aab36b702de7`; publish through normal Contents API; re-fetch/hash-verify; then execute hidden-rowid + receipt-NULL + alternate-UNIQUE regressions, strict/thaw subgate, LAB-080→086 real-ledger gate, unsafe legacy-promotion seed, compileall and final audit.

If exact source execution becomes available first: run LAB-088 supported/downstream gates, LAB-091 full supported-surface gates, then implement tests first for the frozen canonical encoder/chain/atomic-append/storage/verifier/evidence/recovery/broker/session/request/registry/application-idempotency/install-retention/capacity/archive/retrieval/lifecycle/DR/escrow/human-re-root contracts and execute LAB-090/LAB-100, LAB-092, LAB-094..096 and LAB-097..099 RED matrices before production refactors.

If neither capability appears: next distinct evidence task is to freeze a **post-re-root trust-epoch / namespace migration contract** for the case where future operation must resume but some historical application-idempotency epoch is provably irrecoverable. Define a one-way new effect namespace/epoch that cannot reinterpret any historical application key as `MISS`; bind external side-effect cutover evidence, principal/namespace identity, old sealed namespace identity, selected historical boundary, product/security authorization, rollback prevention and migration crash semantics. Preserve the rule that ordinary admin/provider/worker authority cannot unseal or reuse the historical namespace. This task may define the mechanics and safety conditions, but any actual decision to abandon unavailable historical non-reuse evidence and resume side effects is a genuine product/security decision requiring human owner authorization.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; activation authority + canonical/global provenance/recovery contracts frozen; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; migration bound to retained authority graph + global provenance/recovery contracts; exact RED/full gate pending.
- #178 / LAB-093 — READY; façade/session/request/effect/registry/application-idempotency/install-retention/bounded-capacity/archive/checkpoint/retrieval/lifecycle/archive-loss-DR/escrow-root-recovery/escrow-lifecycle/human-reroot contracts frozen; exact RED/GREEN pending.
- #179..181 / LAB-094..096 — READY; unified retained-authority graph + RED matrix frozen.
- #182..184 / LAB-097..099 — READY; authenticated provenance/global chain/recovery contracts frozen.
- #185 / LAB-100 — READY; sealed/registered activation authority + construction/restart/upgrade/global provenance/recovery contracts frozen.
